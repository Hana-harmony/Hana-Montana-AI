from __future__ import annotations

import argparse
import json
import os
import re
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
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from hannah_montana_ai.training.collector import load_local_env, read_raw_alerts
from hannah_montana_ai.training.dataset import JSONL_SHARD_MANIFEST_SCHEMA_VERSION
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
REQUEST_TIMEOUT_SECONDS = 4.0
MAX_OUTPUT_SHARD_BYTES = 95_000_000
CONTENT_SELECTOR_PATTERN = re.compile(
    r"""(?is)<(?P<tag>article|section|div)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)>"""
)
CONTENT_ATTRIBUTE_TERMS = (
    "article",
    "articlebody",
    "article_body",
    "article_txt",
    "articletext",
    "articlecontent",
    "article_content",
    "article-view-content",
    "article_view",
    "articlecont",
    "news_body",
    "news-view",
    "view_content",
    "view_cont",
    "view-article",
    "contents_view",
    "content",
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
    parser.add_argument("--news-worker-count", type=int, default=1)
    parser.add_argument("--news-batch-size", type=int, default=0)
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
        str(row.get("source_url", ""))
        for row in rows.values()
        if row.get("source_url")
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

    dart_api_key = os.environ.get("OPEN_DART_API_KEY", "")
    accepted_disclosure_labels: Counter[str] = Counter()
    for alert in [
        alert
        for alert in raw_alerts
        if alert.source_type == "DISCLOSURE" and is_training_disclosure_candidate(alert)
    ]:
        if target_reached(rows, args.target_row_count):
            status["target_row_count_reached"] += 1
            break
        if status["disclosure_attempted"] >= args.max_disclosures:
            break
        if not dart_api_key:
            status["disclosure_skipped_missing_key"] += 1
            break
        receipt_number = receipt_number_from_url(alert.original_url)
        if not receipt_number:
            status["disclosure_missing_receipt"] += 1
            continue
        if alert.original_url in existing_source_urls:
            status["disclosure_reused_existing_url"] += 1
            continue
        label = pre_label(alert)
        if label is None:
            status["disclosure_unlabeled"] += 1
            continue
        if accepted_disclosure_labels[label] >= args.per_label_limit:
            continue
        status["disclosure_attempted"] += 1
        content = fetch_dart_document(dart_api_key, receipt_number)
        if not content:
            status["disclosure_failed"] += 1
            continue
        row = to_labeled_row(alert, content, alert.original_url, DART_POLICY, matcher)
        if row is None:
            status["disclosure_unlabeled"] += 1
            continue
        rows[row["content_hash"]] = row
        existing_source_urls.add(str(row["source_url"]))
        accepted_disclosure_labels[label] += 1
        status["disclosure_added"] += 1
        sleep(args.sleep_seconds)

    sorted_rows = sorted(
        rows.values(),
        key=lambda row: (row["source_type"], row["content_hash"]),
    )
    write_sharded_jsonl(args.output_path, sorted_rows)
    report = build_report(args.output_path, sorted_rows, status, errors)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def read_existing_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for jsonl_path in resolve_jsonl_paths(path):
        with jsonl_path.open(encoding="utf-8") as file:
            rows.extend(json.loads(line) for line in file if line.strip())
    return rows


def resolve_jsonl_paths(path: Path) -> list[Path]:
    with path.open(encoding="utf-8") as file:
        first_line = file.readline().strip()
    if not first_line:
        return [path]
    try:
        payload = json.loads(first_line)
    except json.JSONDecodeError:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return [path]
    shard_paths = payload.get("dataset_shards") if isinstance(payload, dict) else None
    if not isinstance(shard_paths, list):
        return [path]
    return [
        path.parent / shard_path
        for shard_path in shard_paths
        if isinstance(shard_path, str)
    ]


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
    try:
        html = fetch_bytes(safe_url).decode("utf-8", errors="replace")
    except (HTTPError, IncompleteRead, OSError, TimeoutError, URLError, UnicodeError):
        return None
    text = extract_article_text(html, expected_title=expected_title)
    if len(text) < MIN_CONTENT_CHARS:
        return None
    return FullContent(
        content=text[:MAX_CONTENT_CHARS],
        canonical_url=canonical_url(html, safe_url),
        image_urls=image_urls(html, safe_url),
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


def chunked(
    values: list[tuple[RawCollectedAlert, str]],
    size: int,
) -> list[list[tuple[RawCollectedAlert, str]]]:
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


def fetch_dart_document(api_key: str, receipt_number: str) -> str:
    params = urlencode({"crtfc_key": api_key, "rcept_no": receipt_number})
    try:
        payload = fetch_bytes(f"{OPEN_DART_DOCUMENT_URL}?{params}")
    except (HTTPError, OSError, TimeoutError, URLError):
        return ""
    if payload.startswith(b"PK"):
        text = extract_zip_text(payload)
    else:
        text = payload.decode("utf-8", errors="replace")
    content = extract_text(text)[:MAX_CONTENT_CHARS]
    return content if is_valid_full_content(content) else ""


def fetch_bytes(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("unsupported URL scheme")
    request = Request(  # noqa: S310
        url,
        headers={
            "User-Agent": (
                "Hana-OmniLensTrainingBot/1.0 (+https://github.com/Hana-harmony)"
            )
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:  # noqa: S310
        return response.read(MAX_FETCH_BYTES + 1)[:MAX_FETCH_BYTES]


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
    cleaned = re.sub(
        r"(?is)<(script|style|noscript|iframe|svg|nav|header|footer|aside|form).*?</\1>",
        " ",
        html,
    )
    candidates: list[str] = []
    for match in CONTENT_SELECTOR_PATTERN.finditer(cleaned):
        attrs = normalize_text(unescape(match.group("attrs"))).lower()
        compact_attrs = re.sub(r"[^a-z0-9가-힣_-]+", "", attrs)
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


def image_urls(html: str, source_url: str) -> list[str]:
    urls: list[str] = []
    patterns = [
        r"""<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']""",
        r"""<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']""",
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
    return {
        "schema_version": "real-full-content-training-dataset/v1",
        "dataset_path": str(output_path.relative_to(PROJECT_ROOT)),
        "status": "pass" if rows else "fail",
        "row_count": len(rows),
        "source_type_count": dict(sorted(source_count.items())),
        "source_license_policy_count": dict(sorted(policy_count.items())),
        "minimum_full_text_characters": min(
            (len(row.get("full_content", "")) for row in rows),
            default=0,
        ),
        "collection_status": dict(sorted(status.items())),
        "errors": errors,
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
