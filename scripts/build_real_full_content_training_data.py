from __future__ import annotations

import argparse
import json
import os
import re
import time
import zipfile
from collections import Counter
from dataclasses import asdict
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from hannah_montana_ai.training.collector import load_local_env, read_raw_alerts
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
MIN_CONTENT_CHARS = 180
MAX_CONTENT_CHARS = 20_000
MAX_FETCH_BYTES = 1_500_000
REQUEST_TIMEOUT_SECONDS = 4.0
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
    "많이 본 뉴스",
    "실시간 속보 랭킹뉴스",
    "K-Artprice",
    "프라임뉴시스",
    "위클리뉴시스",
    "제휴 콘텐츠",
    "월드컵24시",
    "더중앙플러스",
    "최신 기사",
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
        and is_seed_policy(str(row.get("source_license_policy", "")))
        and is_valid_full_content(str(row.get("full_content", "")))
    }
    status = Counter[str]()
    errors: list[str] = []

    accepted_news_labels: Counter[str] = Counter()
    for alert in [alert for alert in raw_alerts if alert.source_type == "NEWS"]:
        if status["news_attempted"] >= args.max_news:
            break
        label = pre_label(alert)
        if label is None:
            status["news_unlabeled"] += 1
            continue
        if accepted_news_labels[label] >= args.per_label_limit:
            continue
        status["news_attempted"] += 1
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
        accepted_news_labels[label] += 1
        status["news_added"] += 1
        sleep(args.sleep_seconds)

    dart_api_key = os.environ.get("OPEN_DART_API_KEY", "")
    accepted_disclosure_labels: Counter[str] = Counter()
    for alert in [
        alert
        for alert in raw_alerts
        if alert.source_type == "DISCLOSURE" and is_training_disclosure_candidate(alert)
    ]:
        if status["disclosure_attempted"] >= args.max_disclosures:
            break
        if not dart_api_key:
            status["disclosure_skipped_missing_key"] += 1
            break
        receipt_number = receipt_number_from_url(alert.original_url)
        if not receipt_number:
            status["disclosure_missing_receipt"] += 1
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
        accepted_disclosure_labels[label] += 1
        status["disclosure_added"] += 1
        sleep(args.sleep_seconds)

    sorted_rows = sorted(
        rows.values(),
        key=lambda row: (row["source_type"], row["content_hash"]),
    )
    write_jsonl(args.output_path, sorted_rows)
    report = build_report(args.output_path, sorted_rows, status, errors)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def read_existing_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def fetch_news_content(url: str) -> FullContent | None:
    safe_url = safe_http_url(url)
    if not safe_url:
        return None
    try:
        html = fetch_bytes(safe_url).decode("utf-8", errors="replace")
    except (HTTPError, OSError, TimeoutError, URLError, UnicodeError):
        return None
    text = extract_article_text(html)
    if len(text) < MIN_CONTENT_CHARS:
        return None
    return FullContent(
        content=text[:MAX_CONTENT_CHARS],
        canonical_url=canonical_url(html, safe_url),
        image_urls=image_urls(html, safe_url),
    )


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


def extract_article_text(html: str) -> str:
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

    best = max(candidates, key=content_score)
    return best if content_score(best) > 0 else extract_text(cleaned)


def content_score(text: str) -> int:
    normalized = normalize_text(text)
    if len(normalized) < 90:
        return 0
    financial_score = sum(1 for term in FINANCIAL_CONTEXT_TERMS if term in normalized) * 80
    boilerplate_penalty = sum(1 for term in BOILERPLATE_TERMS if term in normalized) * 180
    sentence_score = len(re.split(r"[.!?。]|다\.", normalized)) * 25
    return max(
        0,
        min(len(normalized), 2_000) + financial_score + sentence_score - boilerplate_penalty,
    )


def is_valid_full_content(content: str) -> bool:
    if len(content) < MIN_CONTENT_CHARS:
        return False
    provider_error_markers = (
        "파일이 존재하지 않습니다",
        "정상적인 접근이 아닙니다",
        "조회된 자료가 없습니다",
    )
    return not any(marker in content for marker in provider_error_markers)


def is_seed_policy(policy: str) -> bool:
    return policy.startswith("internal_")


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
