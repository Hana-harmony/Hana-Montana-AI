from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import time
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
from http.client import IncompleteRead
from io import BytesIO
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

import certifi

from hannah_montana_ai.training.collector import load_local_env, read_raw_alerts
from hannah_montana_ai.training.dataset import (
    JSONL_SHARD_MANIFEST_SCHEMA_VERSION,
    build_jsonl_file_manifest,
    resolve_jsonl_paths,
)
from hannah_montana_ai.training.stock_universe import (
    StockUniverseMatcher,
    attach_stock_metadata,
    load_stock_universe,
)
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert, normalize_text, weak_label

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ALERTS_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
OUTPUT_PATH = PROJECT_ROOT / "data/training/financial_alert_full_content_gold.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/real-full-content-training-dataset-report.json"
STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
OPEN_DART_DOCUMENT_URL = "https://opendart.fss.or.kr/api/document.xml"
DART_MAIN_URL = "https://dart.fss.or.kr/dsaf001/main.do"
DART_VIEWER_URL = "https://dart.fss.or.kr/report/viewer.do"
NEWS_POLICY = "licensed_naver_original_full_text_v1"
DART_POLICY = "opendart_public_disclosure_text_v1"
REUSABLE_FULL_CONTENT_POLICIES = {
    "internal_rights_safe_disclosure_text_v1",
    "internal_rights_safe_full_article_v1",
    NEWS_POLICY,
    DART_POLICY,
}
MIN_CONTENT_CHARS = 180
MAX_CONTENT_CHARS = 20_000
MAX_FETCH_BYTES = 1_500_000
MAX_DART_FETCH_BYTES = 32_000_000
REQUEST_TIMEOUT_SECONDS = 4.0
FETCH_RETRY_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}
MAX_OUTPUT_SHARD_BYTES = 48_000_000
CONTENT_SELECTOR_PATTERN = re.compile(
    r"""(?is)<(?P<tag>article|section|div)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)>"""
)
CONTENT_ATTRIBUTE_TERMS = (
    "article",
    "articlebody",
    "article_body",
    "article-body",
    "article_txt",
    "articletext",
    "articlecontent",
    "article_content",
    "article_conent",
    "article-view-content",
    "article_view",
    "articlecont",
    "news_body",
    "news-view",
    "view_content",
    "view_cont",
    "view-article",
    "view_con_wrap",
    "contents_view",
    "content",
    "content-area",
)
EXCLUDED_CONTENT_ATTRIBUTE_TERMS = (
    "popular_news",
    "popularnews",
    "related_news",
    "relatednews",
    "comment",
    "reply",
    "latest",
    "recommend",
)
BALANCED_CONTENT_ELEMENT_IDS = (
    "articlebody",
    "article-view-content-div",
    "articleViewCon",
)
BALANCED_CONTENT_CLASS_TERM_GROUPS = (
    ("article-view-content",),
    ("view_con_wrap",),
    ("article-veiw-body",),
    ("article_body",),
    ("article-body",),
    ("news_body",),
    ("content-area",),
    ("news_home_list", "section_2"),
)
FINANCIAL_CONTEXT_TERMS = (
    "주가",
    "시총",
    "증시",
    "시장",
    "매출",
    "영업이익",
    "실적",
    "계약",
    "수주",
    "투자",
    "반도체",
    "배터리",
    "공시",
    "거래",
    "외국인",
    "환율",
    "금리",
    "전망",
    "리스크",
    "상승",
    "하락",
    "급등",
    "급락",
)
BOILERPLATE_TERMS = (
    "로그인",
    "회원가입",
    "전체 메뉴",
    "메뉴 열기",
    "메뉴 닫기",
    "본문 바로가기",
    "주메뉴 바로가기",
    "하단메뉴 바로가기",
    "검색 열기",
    "검색 닫기",
    "뉴스스탠드",
    "구독설정",
    "지면PDF",
    "운세",
    "이용약관",
    "개인정보",
    "저작권",
    "복사하기",
    "스크롤 이동 상태바",
    "관련태그",
    "관련기사",
    "많이 본 뉴스",
    "실시간 속보 랭킹뉴스",
    "K-Artprice",
    "프라임뉴시스",
    "위클리뉴시스",
    "제휴 콘텐츠",
    "월드컵24시",
    "더중앙플러스",
    "최신 기사",
    "최신뉴스",
    "인스타그램",
    "유튜브",
    "share flutter_dash",
    "format_size",
    "사진 확대",
    "기자 입력",
    "회원용",
    "나만의 AI 비서",
    "증권 홈",
    "오늘 나온 보고서",
)
PRIMARY_LABEL_PRIORITY = (
    "RISK",
    "CAPITAL_ACTION",
    "CONTRACT",
    "CORPORATE_ACTION",
    "EARNINGS",
    "MACRO",
    "GENERAL_MARKET",
    "DISCLOSURE",
)


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "iframe", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "iframe", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        text = normalize_text(unescape(data))
        if len(text) >= 2:
            self.parts.append(text)

    def text(self) -> str:
        return normalize_text(" ".join(self.parts))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a real full-content news/disclosure training dataset."
    )
    parser.add_argument("--raw-path", type=Path, default=RAW_ALERTS_PATH)
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    parser.add_argument("--stock-universe-path", type=Path, default=STOCK_UNIVERSE_PATH)
    parser.add_argument("--max-news", type=int, default=600)
    parser.add_argument("--max-disclosures", type=int, default=200)
    parser.add_argument("--per-label-limit", type=int, default=70)
    parser.add_argument("--target-row-count", type=int, default=0)
    parser.add_argument("--target-disclosure-count", type=int, default=0)
    parser.add_argument("--news-worker-count", type=int, default=1)
    parser.add_argument("--news-batch-size", type=int, default=0)
    parser.add_argument("--disclosure-worker-count", type=int, default=4)
    parser.add_argument("--disclosure-batch-size", type=int, default=200)
    parser.add_argument(
        "--dart-fetch-mode",
        choices=("api_with_public_viewer_fallback", "public_viewer"),
        default="api_with_public_viewer_fallback",
    )
    parser.add_argument("--sleep-seconds", type=float, default=0.05)
    parser.add_argument("--timeout-seconds", type=float, default=4.0)
    parser.add_argument("--append-existing", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    global REQUEST_TIMEOUT_SECONDS
    REQUEST_TIMEOUT_SECONDS = max(args.timeout_seconds, 1.0)

    load_local_env(PROJECT_ROOT / "secrets.local.env")
    matcher = StockUniverseMatcher(load_stock_universe(args.stock_universe_path))
    raw_alerts = read_raw_alerts(args.raw_path)
    existing_rows = read_existing_rows(args.output_path) if args.append_existing else []
    rows: dict[str, dict[str, Any]] = {
        row["content_hash"]: row
        for row in existing_rows
        if row.get("content_hash")
        and is_reusable_full_content_policy(str(row.get("source_license_policy", "")))
        and is_valid_full_content(str(row.get("full_content", "")))
    }
    existing_source_urls = {
        str(row.get("source_url", "")) for row in rows.values() if row.get("source_url")
    }
    status = Counter[str]()
    errors: list[str] = []

    collect_news_rows(
        raw_alerts=raw_alerts,
        rows=rows,
        existing_source_urls=existing_source_urls,
        matcher=matcher,
        status=status,
        max_news=args.max_news,
        per_label_limit=args.per_label_limit,
        target_row_count=args.target_row_count,
        sleep_seconds=args.sleep_seconds,
        worker_count=args.news_worker_count,
        batch_size=args.news_batch_size,
    )

    collect_disclosure_rows(
        raw_alerts=raw_alerts,
        rows=rows,
        existing_source_urls=existing_source_urls,
        matcher=matcher,
        status=status,
        max_disclosures=args.max_disclosures,
        per_label_limit=args.per_label_limit,
        target_row_count=args.target_row_count,
        target_disclosure_count=args.target_disclosure_count,
        sleep_seconds=args.sleep_seconds,
        worker_count=args.disclosure_worker_count,
        batch_size=args.disclosure_batch_size,
        dart_fetch_mode=args.dart_fetch_mode,
    )

    sorted_rows = sorted(
        rows.values(),
        key=lambda row: (row["source_type"], row["content_hash"]),
    )
    write_sharded_jsonl(args.output_path, sorted_rows)
    if args.append_existing and args.report_path.exists():
        previous_report = json.loads(args.report_path.read_text(encoding="utf-8"))
        status = merge_collection_status(
            previous_report.get("collection_status", {}),
            status,
        )
    report = build_report(args.output_path, sorted_rows, status, errors)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def merge_collection_status(
    previous: dict[str, Any],
    current: Counter[str],
) -> Counter[str]:
    """누적 수집 시도는 합산하고 현재 데이터 스냅샷 수치는 최신 값으로 유지한다."""
    merged = Counter[str]()
    cumulative_markers = ("_added", "_attempted", "_failed")
    keys = set(previous) | set(current)
    for key in keys:
        previous_value = int(previous.get(key, 0))
        current_value = int(current.get(key, 0))
        if any(marker in key for marker in cumulative_markers):
            merged[key] = previous_value + current_value
        elif key in current:
            merged[key] = current_value
        else:
            merged[key] = previous_value
    return merged


def read_existing_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for jsonl_path in resolve_jsonl_paths(path):
        with jsonl_path.open(encoding="utf-8") as file:
            rows.extend(json.loads(line) for line in file if line.strip())
    return rows


def write_sharded_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(row, ensure_ascii=False) + "\n" for row in rows]
    if sum(len(line.encode("utf-8")) for line in lines) <= MAX_OUTPUT_SHARD_BYTES:
        path.write_text("".join(lines), encoding="utf-8")
        return

    shard_dir = path.with_name(f"{path.stem}_shards")
    shard_dir.mkdir(parents=True, exist_ok=True)
    for old_shard in shard_dir.glob("*.jsonl"):
        old_shard.unlink()

    shard_paths: list[str] = []
    current_lines: list[str] = []
    current_bytes = 0
    for line in lines:
        line_bytes = len(line.encode("utf-8"))
        if current_lines and current_bytes + line_bytes > MAX_OUTPUT_SHARD_BYTES:
            shard_paths.append(write_shard(path, shard_dir, len(shard_paths) + 1, current_lines))
            current_lines = []
            current_bytes = 0
        current_lines.append(line)
        current_bytes += line_bytes
    if current_lines:
        shard_paths.append(write_shard(path, shard_dir, len(shard_paths) + 1, current_lines))

    manifest = {
        "schema_version": JSONL_SHARD_MANIFEST_SCHEMA_VERSION,
        "row_count": len(rows),
        "dataset_shards": shard_paths,
        "files": [
            build_jsonl_file_manifest(path.parent / shard_path, shard_path)
            for shard_path in shard_paths
        ],
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_shard(path: Path, shard_dir: Path, index: int, lines: list[str]) -> str:
    shard_path = shard_dir / f"part-{index:04d}.jsonl"
    shard_path.write_text("".join(lines), encoding="utf-8")
    return str(shard_path.relative_to(path.parent))


def fetch_news_content(url: str, expected_title: str = "") -> FullContent | None:
    safe_url = safe_http_url(url)
    if not safe_url:
        return None
    html = fetch_html_with_retry(safe_url)
    if not html:
        return None
    text = extract_article_text(html, expected_title=expected_title)
    content_html = html
    content_url = safe_url
    primary_image_urls = image_urls(html, safe_url)
    if len(text) < MIN_CONTENT_CHARS:
        next_amp_url = amp_url(html, safe_url)
        if next_amp_url and next_amp_url != safe_url:
            amp_html = fetch_html_with_retry(next_amp_url)
            if amp_html:
                amp_text = extract_article_text(amp_html, expected_title=expected_title)
                if len(amp_text) > len(text):
                    text = amp_text
                    content_html = amp_html
                    content_url = next_amp_url
    if len(text) < MIN_CONTENT_CHARS:
        return None
    merged_image_urls = [
        image_url
        for image_url in [*image_urls(content_html, content_url), *primary_image_urls]
        if image_url
    ]
    deduplicated_image_urls = list(dict.fromkeys(merged_image_urls))[:10]
    return FullContent(
        content=text[:MAX_CONTENT_CHARS],
        canonical_url=canonical_url(content_html, content_url),
        image_urls=deduplicated_image_urls,
    )


def collect_news_rows(
    *,
    raw_alerts: list[RawCollectedAlert],
    rows: dict[str, dict[str, Any]],
    existing_source_urls: set[str],
    matcher: StockUniverseMatcher,
    status: Counter[str],
    max_news: int,
    per_label_limit: int,
    target_row_count: int,
    sleep_seconds: float,
    worker_count: int,
    batch_size: int,
) -> None:
    if worker_count <= 1:
        collect_news_rows_sequential(
            raw_alerts=raw_alerts,
            rows=rows,
            existing_source_urls=existing_source_urls,
            matcher=matcher,
            status=status,
            max_news=max_news,
            per_label_limit=per_label_limit,
            target_row_count=target_row_count,
            sleep_seconds=sleep_seconds,
        )
        return

    candidates = select_news_candidates(
        raw_alerts=raw_alerts,
        existing_source_urls=existing_source_urls,
        status=status,
        max_news=max_news,
        per_label_limit=per_label_limit,
    )
    if not candidates:
        return

    accepted_news_labels: Counter[str] = Counter()
    max_workers = min(max(worker_count, 1), 16)
    actual_batch_size = max(batch_size, max_workers * 16)
    for batch in chunked(candidates, actual_batch_size):
        if target_reached(rows, target_row_count):
            status["target_row_count_reached"] += 1
            break
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(fetch_news_content, alert.original_url): (alert, label)
                for alert, label in batch
            }
            for future in as_completed(future_map):
                alert, label = future_map[future]
                if target_reached(rows, target_row_count):
                    status["target_row_count_reached"] += 1
                    break
                full_content = future.result()
                if not full_content:
                    status["news_failed"] += 1
                    continue
                if accepted_news_labels[label] >= per_label_limit:
                    status["news_label_limit_after_fetch"] += 1
                    continue
                candidate_row = to_labeled_row(
                    alert,
                    full_content.content,
                    full_content.canonical_url,
                    NEWS_POLICY,
                    matcher,
                )
                if candidate_row is None:
                    status["news_unlabeled"] += 1
                    continue
                rows[candidate_row["content_hash"]] = candidate_row | {
                    "image_urls": full_content.image_urls
                }
                existing_source_urls.add(str(candidate_row["source_url"]))
                accepted_news_labels[label] += 1
                status["news_added"] += 1
                sleep(sleep_seconds)


def collect_disclosure_rows(
    *,
    raw_alerts: list[RawCollectedAlert],
    rows: dict[str, dict[str, Any]],
    existing_source_urls: set[str],
    matcher: StockUniverseMatcher,
    status: Counter[str],
    max_disclosures: int,
    per_label_limit: int,
    target_row_count: int,
    target_disclosure_count: int,
    sleep_seconds: float,
    worker_count: int,
    batch_size: int,
    dart_fetch_mode: str,
) -> None:
    if max_disclosures <= 0:
        return
    dart_api_key = os.environ.get("OPEN_DART_API_KEY", "")
    if not dart_api_key and dart_fetch_mode != "public_viewer":
        status["disclosure_skipped_missing_key"] += 1
        return
    status[f"disclosure_fetch_mode_{dart_fetch_mode}"] += 1

    accepted_labels = Counter[str]()
    disclosure_count = 0
    for row in rows.values():
        if row.get("source_type") != "DISCLOSURE":
            continue
        disclosure_count += 1
        tags = {str(tag) for tag in row.get("tags", [])}
        label = next((name for name in PRIMARY_LABEL_PRIORITY if name in tags), None)
        if label:
            accepted_labels[label] += 1

    candidates = select_disclosure_candidates(
        raw_alerts=raw_alerts,
        existing_source_urls=existing_source_urls,
        status=status,
        max_disclosures=max_disclosures,
    )
    max_workers = min(max(worker_count, 1), 8)
    actual_batch_size = max(batch_size, max_workers * 8)
    for batch in chunked(candidates, actual_batch_size):
        if target_reached(rows, target_row_count):
            status["target_row_count_reached"] += 1
            break
        if target_disclosure_count > 0 and disclosure_count >= target_disclosure_count:
            status["target_disclosure_count_reached"] += 1
            break
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(
                    fetch_dart_document_with_status,
                    dart_api_key,
                    receipt_number,
                    fetch_mode=dart_fetch_mode,
                ): (
                    alert,
                    label,
                )
                for alert, label, receipt_number in batch
                if accepted_labels[label] < per_label_limit
            }
            for future in as_completed(future_map):
                alert, label = future_map[future]
                if target_reached(rows, target_row_count) or (
                    target_disclosure_count > 0 and disclosure_count >= target_disclosure_count
                ):
                    break
                status["disclosure_attempted"] += 1
                content, fetch_status = future.result()
                if not content:
                    status["disclosure_failed"] += 1
                    status[f"disclosure_failed_{fetch_status}"] += 1
                    continue
                if accepted_labels[label] >= per_label_limit:
                    status["disclosure_label_limit_after_fetch"] += 1
                    continue
                candidate_row = to_labeled_row(
                    alert,
                    content,
                    alert.original_url,
                    DART_POLICY,
                    matcher,
                )
                if candidate_row is None:
                    status["disclosure_unlabeled"] += 1
                    continue
                rows[candidate_row["content_hash"]] = candidate_row
                existing_source_urls.add(str(candidate_row["source_url"]))
                accepted_labels[label] += 1
                disclosure_count += 1
                status["disclosure_added"] += 1
        print(
            json.dumps(
                {
                    "stage": "open_dart_full_text",
                    "attempted": status["disclosure_attempted"],
                    "added": status["disclosure_added"],
                    "failed": status["disclosure_failed"],
                    "total_disclosure_rows": disclosure_count,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        sleep(sleep_seconds)


def select_disclosure_candidates(
    *,
    raw_alerts: list[RawCollectedAlert],
    existing_source_urls: set[str],
    status: Counter[str],
    max_disclosures: int,
) -> list[tuple[RawCollectedAlert, str, str]]:
    buckets: dict[tuple[str, str], list[tuple[RawCollectedAlert, str, str]]] = {}
    for alert in raw_alerts:
        if alert.source_type != "DISCLOSURE" or not is_training_disclosure_candidate(alert):
            continue
        if alert.original_url in existing_source_urls:
            status["disclosure_reused_existing_url"] += 1
            continue
        receipt_number = receipt_number_from_url(alert.original_url)
        if not receipt_number:
            status["disclosure_missing_receipt"] += 1
            continue
        label = pre_label(alert)
        if label is None:
            status["disclosure_unlabeled"] += 1
            continue
        year = re.sub(r"\D", "", alert.published_at)[:4] or "UNKNOWN"
        buckets.setdefault((year, label), []).append((alert, label, receipt_number))

    for values in buckets.values():
        values.sort(key=lambda value: value[0].content_hash)
    selected: list[tuple[RawCollectedAlert, str, str]] = []
    bucket_keys = sorted(buckets)
    while len(selected) < max_disclosures and bucket_keys:
        next_keys: list[tuple[str, str]] = []
        for key in bucket_keys:
            values = buckets[key]
            if values:
                selected.append(values.pop())
            if values:
                next_keys.append(key)
            if len(selected) >= max_disclosures:
                break
        bucket_keys = next_keys
    return selected


def chunked[T](
    values: list[T],
    size: int,
) -> list[list[T]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def collect_news_rows_sequential(
    *,
    raw_alerts: list[RawCollectedAlert],
    rows: dict[str, dict[str, Any]],
    existing_source_urls: set[str],
    matcher: StockUniverseMatcher,
    status: Counter[str],
    max_news: int,
    per_label_limit: int,
    target_row_count: int,
    sleep_seconds: float,
) -> None:
    accepted_news_labels: Counter[str] = Counter()
    for alert, label in select_news_candidates(
        raw_alerts=raw_alerts,
        existing_source_urls=existing_source_urls,
        status=status,
        max_news=max_news,
        per_label_limit=per_label_limit,
    ):
        if target_reached(rows, target_row_count):
            status["target_row_count_reached"] += 1
            break
        if accepted_news_labels[label] >= per_label_limit:
            continue
        full_content = fetch_news_content(alert.original_url)
        if not full_content:
            status["news_failed"] += 1
            continue
        row = to_labeled_row(
            alert,
            full_content.content,
            full_content.canonical_url,
            NEWS_POLICY,
            matcher,
        )
        if row is None:
            status["news_unlabeled"] += 1
            continue
        rows[row["content_hash"]] = row | {"image_urls": full_content.image_urls}
        existing_source_urls.add(str(row["source_url"]))
        accepted_news_labels[label] += 1
        status["news_added"] += 1
        sleep(sleep_seconds)


def select_news_candidates(
    *,
    raw_alerts: list[RawCollectedAlert],
    existing_source_urls: set[str],
    status: Counter[str],
    max_news: int,
    per_label_limit: int,
) -> list[tuple[RawCollectedAlert, str]]:
    candidates: list[tuple[RawCollectedAlert, str]] = []
    candidate_labels: Counter[str] = Counter()
    for alert in [alert for alert in raw_alerts if alert.source_type == "NEWS"]:
        if len(candidates) >= max_news:
            break
        label = pre_label(alert)
        if label is None:
            status["news_unlabeled"] += 1
            continue
        if candidate_labels[label] >= max(per_label_limit * 4, per_label_limit):
            continue
        if alert.original_url in existing_source_urls:
            status["news_reused_existing_url"] += 1
            continue
        candidates.append((alert, label))
        candidate_labels[label] += 1
        status["news_attempted"] += 1
    return candidates


def fetch_dart_document(api_key: str, receipt_number: str, max_attempts: int = 3) -> str:
    return fetch_dart_document_with_status(api_key, receipt_number, max_attempts)[0]


def fetch_dart_document_with_status(
    api_key: str,
    receipt_number: str,
    max_attempts: int = 3,
    *,
    fetch_mode: str = "api_with_public_viewer_fallback",
) -> tuple[str, str]:
    if fetch_mode == "public_viewer":
        return fetch_dart_public_viewer_with_status(receipt_number, "public_viewer")
    if fetch_mode != "api_with_public_viewer_fallback":
        raise ValueError("지원하지 않는 DART 원문 수집 모드입니다.")
    params = urlencode({"crtfc_key": api_key, "rcept_no": receipt_number})
    payload = b""
    failure_status = "transport_error"
    for attempt in range(max_attempts):
        try:
            payload = fetch_bytes(
                f"{OPEN_DART_DOCUMENT_URL}?{params}",
                max_bytes=MAX_DART_FETCH_BYTES,
            )
            break
        except HTTPError as exception:
            failure_status = f"http_{exception.code}"
            if exception.code not in FETCH_RETRY_HTTP_CODES or attempt == max_attempts - 1:
                return fetch_dart_public_viewer_with_status(receipt_number, failure_status)
        except ValueError:
            failure_status = "oversize"
            if attempt == max_attempts - 1:
                return fetch_dart_public_viewer_with_status(receipt_number, failure_status)
        except (IncompleteRead, OSError, TimeoutError, URLError):
            if attempt == max_attempts - 1:
                return fetch_dart_public_viewer_with_status(receipt_number, failure_status)
        time.sleep(min(0.25 * (2**attempt), 1.0))
    if not payload:
        return fetch_dart_public_viewer_with_status(receipt_number, failure_status)
    if payload.startswith(b"PK"):
        try:
            text = extract_zip_text(payload)
        except zipfile.BadZipFile:
            return fetch_dart_public_viewer_with_status(receipt_number, "malformed_zip")
    else:
        text = payload.decode("utf-8", errors="replace")
        status_match = re.search(r"<status>([^<]+)</status>", text)
        if status_match and status_match.group(1) != "000":
            return fetch_dart_public_viewer_with_status(
                receipt_number,
                f"dart_status_{status_match.group(1)}",
            )
    content = extract_text(text)[:MAX_CONTENT_CHARS]
    if not is_valid_full_content(content):
        return "", "content_too_short"
    return content, "accepted"


def fetch_dart_public_viewer_with_status(
    receipt_number: str,
    upstream_status: str,
) -> tuple[str, str]:
    if not re.fullmatch(r"\d{14}", receipt_number):
        return "", "invalid_receipt_number"
    main_url = f"{DART_MAIN_URL}?{urlencode({'rcpNo': receipt_number})}"
    main_html = fetch_html_with_retry(main_url)
    view_match = re.search(
        rf'''viewDoc\(\s*["']{re.escape(receipt_number)}["']\s*,\s*["'](?P<dcm_no>\d+)["']\s*,\s*["']0["']\s*,\s*["']0["']\s*,\s*["']0["']\s*,\s*["'](?P<dtd>dart\d+\.xsd)["']''',
        main_html,
    )
    if not view_match:
        return "", f"{upstream_status}_viewer_metadata_missing"
    viewer_url = f"{DART_VIEWER_URL}?{urlencode({
        'rcpNo': receipt_number,
        'dcmNo': view_match.group('dcm_no'),
        'eleId': '0',
        'offset': '0',
        'length': '0',
        'dtd': view_match.group('dtd'),
    })}"
    viewer_html = fetch_html_with_retry(viewer_url)
    content = extract_text(viewer_html)[:MAX_CONTENT_CHARS]
    if not is_valid_full_content(content):
        return "", f"{upstream_status}_viewer_content_too_short"
    return content, "accepted_public_viewer"


def fetch_html_with_retry(url: str, max_attempts: int = 3) -> str:
    for attempt in range(max_attempts):
        try:
            return fetch_bytes(url).decode("utf-8", errors="replace")
        except HTTPError as exception:
            if exception.code not in FETCH_RETRY_HTTP_CODES:
                return ""
            if attempt == max_attempts - 1:
                return ""
        except (IncompleteRead, OSError, TimeoutError, URLError, UnicodeError):
            if attempt == max_attempts - 1:
                return ""
        time.sleep(min(0.2 * (2**attempt), 1.0))
    return ""


def fetch_bytes(url: str, max_bytes: int = MAX_FETCH_BYTES) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("unsupported URL scheme")
    context = (
        ssl.create_default_context(cafile=certifi.where()) if parsed.scheme == "https" else None
    )
    request = Request(  # noqa: S310
        url,
        headers={"User-Agent": ("Hana-Omni-ConnectTrainingBot/1.0 (+https://github.com/Hana-harmony)")},
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS, context=context) as response:  # noqa: S310
        payload = cast(bytes, response.read(max_bytes + 1))
    if len(payload) > max_bytes:
        raise ValueError("response exceeds configured byte limit")
    return payload


def extract_zip_text(payload: bytes) -> str:
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        for name in archive.namelist():
            if not name.lower().endswith((".xml", ".html", ".htm", ".txt")):
                continue
            with archive.open(name) as entry:
                return entry.read(MAX_FETCH_BYTES + 1)[:MAX_FETCH_BYTES].decode(
                    "utf-8", errors="replace"
                )
    return ""


def extract_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style|noscript|iframe|svg).*?</\1>", " ", html)
    parser = TextExtractor()
    parser.feed(cleaned)
    return parser.text()


def extract_article_text(html: str, expected_title: str = "") -> str:
    arranged_text = extract_content_arrange_text(html)
    cleaned = re.sub(
        r"(?is)<(script|style|noscript|iframe|svg|nav|header|footer|aside|form).*?</\1>",
        " ",
        html,
    )
    candidates: list[str] = []
    if arranged_text:
        candidates.append(arranged_text)
    article_body_match = re.search(
        r"""(?is)<article[^>]+(?:id=["']articleText["']|itemprop=["']articleBody["'])[^>]*>(?P<body>.*?)</article>""",
        cleaned,
    )
    if article_body_match:
        text = extract_text(article_body_match.group("body"))
        if text:
            candidates.append(text)
    for element_id in BALANCED_CONTENT_ELEMENT_IDS:
        element_html = extract_element_html_by_id(cleaned, element_id)
        if element_html:
            text = extract_text(element_html)
            if text:
                candidates.append(text)
    for class_terms in BALANCED_CONTENT_CLASS_TERM_GROUPS:
        texts = [
            text
            for element_html in extract_elements_html_by_class_terms(cleaned, class_terms)
            if (text := extract_text(element_html))
        ]
        candidates.extend(texts)
        if len(texts) >= 2:
            candidates.append(" ".join(texts))
    newdaily_match = re.search(
        r"""(?is)<div[^>]+id=["']article_conent["'][^>]*>(?P<body>.*?)</ul>""",
        cleaned,
    )
    if newdaily_match:
        text = extract_text(newdaily_match.group("body"))
        if text:
            candidates.append(text)
    for match in CONTENT_SELECTOR_PATTERN.finditer(cleaned):
        attrs = normalize_text(unescape(match.group("attrs"))).lower()
        compact_attrs = re.sub(r"[^a-z0-9가-힣_-]+", "", attrs)
        if is_excluded_content_attrs(compact_attrs):
            continue
        if match.group("tag").lower() == "article" or any(
            term in compact_attrs for term in CONTENT_ATTRIBUTE_TERMS
        ):
            text = extract_text(match.group("body"))
            if text:
                candidates.append(text)

    if not candidates:
        return extract_text(cleaned)

    best = max(candidates, key=lambda text: content_score(text, expected_title))
    return best if content_score(best, expected_title) > 0 else extract_text(cleaned)


def extract_content_arrange_text(html: str) -> str:
    chunks: list[str] = []
    for match in re.finditer(
        r'''"type":"text","content":"(?P<content>(?:\\.|[^"\\])*)"''',
        html,
    ):
        try:
            decoded = json.loads(f'"{match.group("content")}"')
        except json.JSONDecodeError:
            continue
        text = normalize_text(unescape(decoded))
        if text:
            chunks.append(text)
    return " ".join(chunks)


def extract_element_html_by_id(html: str, element_id: str) -> str:
    start_match = re.search(
        r"""(?is)<(?P<tag>[a-z0-9]+)\b(?=[^>]*\bid=["']"""
        + re.escape(element_id)
        + r"""["'])(?P<attrs>[^>]*)>""",
        html,
    )
    if not start_match:
        return ""
    return extract_balanced_element_body(html, start_match)


def extract_elements_html_by_class_terms(html: str, class_terms: tuple[str, ...]) -> list[str]:
    parts: list[str] = []
    seen: set[tuple[int, int]] = set()
    start_pattern = re.compile(
        r"""(?is)<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*\bclass=["'][^"']+["'][^>]*)>"""
    )
    for start_match in start_pattern.finditer(html):
        attrs = normalize_text(unescape(start_match.group("attrs"))).lower()
        compact_attrs = re.sub(r"[^a-z0-9가-힣_-]+", "", attrs)
        if is_excluded_content_attrs(compact_attrs):
            continue
        if not all(term.lower() in attrs for term in class_terms):
            continue
        body = extract_balanced_element_body(html, start_match)
        if not body:
            continue
        key = (start_match.start(), start_match.end() + len(body))
        if key in seen:
            continue
        seen.add(key)
        parts.append(body)
    return parts


def extract_balanced_element_body(html: str, start_match: re.Match[str]) -> str:
    tag = start_match.group("tag")
    tag_pattern = re.compile(rf"(?is)</?{re.escape(tag)}\b[^>]*>")
    depth = 0
    for match in tag_pattern.finditer(html, start_match.start()):
        token = match.group(0)
        is_end = token.startswith("</")
        is_self_closing = token.rstrip().endswith("/>")
        if is_end:
            depth -= 1
            if depth == 0:
                return html[start_match.end() : match.start()]
        elif not is_self_closing:
            depth += 1
    return ""


def is_excluded_content_attrs(compact_attrs: str) -> bool:
    return any(term in compact_attrs for term in EXCLUDED_CONTENT_ATTRIBUTE_TERMS)


def content_score(text: str, expected_title: str = "") -> int:
    normalized = normalize_text(text)
    if len(normalized) < 90:
        return 0
    title_terms = title_match_terms(expected_title)
    title_match_score = sum(1 for term in title_terms if term in normalized) * 220
    title_absent_penalty = (
        600 if title_terms and not any(term in normalized for term in title_terms) else 0
    )
    financial_score = sum(1 for term in FINANCIAL_CONTEXT_TERMS if term in normalized) * 80
    boilerplate_penalty = sum(1 for term in BOILERPLATE_TERMS if term in normalized) * 180
    sentence_score = len(re.split(r"[.!?。]|다\.", normalized)) * 25
    return max(
        0,
        min(len(normalized), 2_000)
        + title_match_score
        + financial_score
        + sentence_score
        - boilerplate_penalty
        - title_absent_penalty,
    )


def title_match_terms(title: str) -> set[str]:
    generic_terms = {
        "단독",
        "종합",
        "속보",
        "특징주",
        "공시",
        "오늘뉴스",
        "이슈",
    }
    return {
        token
        for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", normalize_text(unescape(title)))
        if token not in generic_terms
    }


def is_valid_full_content(content: str) -> bool:
    if len(content) < MIN_CONTENT_CHARS:
        return False
    provider_error_markers = (
        "파일이 존재하지 않습니다",
        "정상적인 접근이 아닙니다",
        "조회된 자료가 없습니다",
    )
    return not any(marker in content for marker in provider_error_markers)


def target_reached(rows: dict[str, dict[str, Any]], target_row_count: int) -> bool:
    return target_row_count > 0 and len(rows) >= target_row_count


def disclosure_target_reached(
    rows: dict[str, dict[str, Any]], target_disclosure_count: int
) -> bool:
    if target_disclosure_count <= 0:
        return False
    disclosure_count = sum(
        str(row.get("source_type")) == "DISCLOSURE" for row in rows.values()
    )
    return disclosure_count >= target_disclosure_count


def is_reusable_full_content_policy(policy: str) -> bool:
    return policy in REUSABLE_FULL_CONTENT_POLICIES


def is_training_disclosure_candidate(alert: RawCollectedAlert) -> bool:
    text = f"{alert.title} {alert.snippet}"
    excluded = ("집합투자증권", "투자설명서", "일괄신고서", "증권발행실적보고서")
    if any(keyword in text for keyword in excluded):
        return False
    included = (
        "주요사항",
        "단일판매",
        "공급계약",
        "자기주식",
        "유상증자",
        "무상증자",
        "타법인",
        "합병",
        "분할",
        "영업",
        "잠정",
        "거래정지",
        "상장폐지",
        "소송",
        "임원ㆍ주요주주",
        "주식등의대량보유",
        "주주총회",
        "기업설명회",
        "감사보고서",
        "사업보고서",
        "분기보고서",
        "반기보고서",
        "최대주주등소유주식변동",
        "조회공시",
        "대표이사변경",
    )
    return any(keyword in text for keyword in included)


def pre_label(alert: RawCollectedAlert) -> str | None:
    labeled = weak_label(alert)
    if labeled is None:
        return None
    for label in PRIMARY_LABEL_PRIORITY:
        if label in labeled.tags:
            return label
    return labeled.tags[0] if labeled.tags else None


def canonical_url(html: str, source_url: str) -> str:
    match = re.search(r"""<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']+)["']""", html, re.I)
    if not match:
        return source_url
    return safe_http_url(urljoin(source_url, unescape(match.group(1)))) or source_url


def amp_url(html: str, source_url: str) -> str:
    match = re.search(r"""<link[^>]+rel=["']amphtml["'][^>]+href=["']([^"']+)["']""", html, re.I)
    if not match:
        return ""
    return safe_http_url(urljoin(source_url, unescape(match.group(1))))


def image_urls(html: str, source_url: str) -> list[str]:
    urls: list[str] = []
    patterns = [
        r"""<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']""",
        r"""<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']""",
        r"""<amp-img[^>]+src=["']([^"']+)["']""",
        r"""<img[^>]+src=["']([^"']+)["']""",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, html, re.I):
            image_url = safe_http_url(urljoin(source_url, unescape(match.group(1))))
            if image_url and image_url not in urls:
                urls.append(image_url)
            if len(urls) >= 10:
                return urls
    return urls


def to_labeled_row(
    alert: RawCollectedAlert,
    full_content: str,
    source_url: str,
    policy: str,
    matcher: StockUniverseMatcher,
) -> dict[str, Any] | None:
    labeled = weak_label(alert)
    if labeled is None:
        return None
    labeled = attach_stock_metadata(labeled, matcher)
    content_hash = sha256(f"{alert.source_type}:{source_url}:{full_content}".encode()).hexdigest()
    row = asdict(labeled) | {
        "title": alert.title,
        "snippet": alert.snippet,
        "full_content": full_content,
        "content_availability": "FULL_TEXT",
        "source_license_policy": policy,
        "source_url": source_url,
        "content_hash": content_hash,
        "provider": alert.provider,
        "published_at": alert.published_at,
        "label_provenance": "RULE_WEAK_SUPERVISION_V2",
        "source_review_status": "UNREVIEWED_WEAK_LABEL",
        "reviewer_id": "",
        "review_note": "학습 전용 약한 라벨이며 Gold 평가에는 사용하지 않는다.",
    }
    row["text"] = alert.title
    return row


def receipt_number_from_url(url: str) -> str:
    query = parse_qs(urlparse(url).query)
    value = query.get("rcpNo", [""])[0]
    return value if re.fullmatch(r"\d{14}", value) else ""


def safe_http_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".localhost"):
        return ""
    return parsed.geturl()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_report(
    output_path: Path,
    rows: list[dict[str, Any]],
    status: Counter[str],
    errors: list[str],
) -> dict[str, Any]:
    policy_count = Counter(str(row.get("source_license_policy", "")) for row in rows)
    source_count = Counter(str(row.get("source_type", "")) for row in rows)
    source_types = sorted(source_count)
    return {
        "schema_version": "real-full-content-training-dataset/v1",
        "dataset_path": str(output_path.relative_to(PROJECT_ROOT)),
        "status": "pass" if rows else "fail",
        "row_count": len(rows),
        "source_type_count": dict(sorted(source_count.items())),
        "source_license_policy_count": dict(sorted(policy_count.items())),
        "label_provenance_count": dict(
            sorted(Counter(str(row.get("label_provenance", "")) for row in rows).items())
        ),
        "importance_distribution_by_source": {
            source_type: dict(
                sorted(
                    Counter(
                        str(row.get("importance", ""))
                        for row in rows
                        if row.get("source_type") == source_type
                    ).items()
                )
            )
            for source_type in source_types
        },
        "sentiment_distribution_by_source": {
            source_type: dict(
                sorted(
                    Counter(
                        str(row.get("sentiment", ""))
                        for row in rows
                        if row.get("source_type") == source_type
                    ).items()
                )
            )
            for source_type in source_types
        },
        "publication_year_count": dict(
            sorted(Counter(str(row.get("published_at", ""))[:4] for row in rows).items())
        ),
        "full_text_character_statistics": {
            "ALL": length_summary([len(str(row.get("full_content", ""))) for row in rows]),
            **{
                source_type: length_summary(
                    [
                        len(str(row.get("full_content", "")))
                        for row in rows
                        if row.get("source_type") == source_type
                    ]
                )
                for source_type in source_types
            },
        },
        "minimum_full_text_characters": min(
            (len(row.get("full_content", "")) for row in rows),
            default=0,
        ),
        "collection_status": dict(sorted(status.items())),
        "errors": errors,
    }


def length_summary(values: list[int]) -> dict[str, int | float]:
    if not values:
        return {"minimum": 0, "median": 0, "p95": 0, "maximum": 0, "mean": 0.0}
    ordered = sorted(values)
    return {
        "minimum": ordered[0],
        "median": ordered[(len(ordered) - 1) // 2],
        "p95": ordered[round((len(ordered) - 1) * 0.95)],
        "maximum": ordered[-1],
        "mean": round(sum(ordered) / len(ordered), 2),
    }


def sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


class FullContent:
    def __init__(self, content: str, canonical_url: str, image_urls: list[str]) -> None:
        self.content = content
        self.canonical_url = canonical_url
        self.image_urls = image_urls


if __name__ == "__main__":
    main()
