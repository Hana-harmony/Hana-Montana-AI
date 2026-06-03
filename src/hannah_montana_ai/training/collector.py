from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import UTC, date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from hannah_montana_ai.training.weak_labeler import RawCollectedAlert, normalize_text

NAVER_QUERIES = (
    "삼성전자 실적",
    "SK하이닉스 반도체",
    "현대차 수출",
    "NAVER 실적",
    "카카오 공시",
    "코스피 외국인",
    "한국 증시 금리",
    "유상증자 공시",
    "공급계약 수주",
    "상장폐지 거래정지",
    "자사주 배당",
    "환율 수출 기업",
)


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def collect_naver_news(max_per_query: int = 200) -> list[RawCollectedAlert]:
    client_id = os.environ["NAVER_NEWS_CLIENT_ID"]
    client_secret = os.environ["NAVER_NEWS_CLIENT_SECRET"]
    collected: dict[str, RawCollectedAlert] = {}

    for query in NAVER_QUERIES:
        for start in range(1, max_per_query + 1, 100):
            params = urlencode(
                {
                    "query": query,
                    "display": min(100, max_per_query - start + 1),
                    "start": start,
                    "sort": "date",
                }
            )
            request = Request(
                f"https://openapi.naver.com/v1/search/news.json?{params}",
                headers={
                    "X-Naver-Client-Id": client_id,
                    "X-Naver-Client-Secret": client_secret,
                },
            )
            try:
                payload = _json_request(request)
            except HTTPError as exception:
                if exception.code == 429:
                    break
                raise
            for item in payload.get("items", []):
                alert = RawCollectedAlert(
                    source_type="NEWS",
                    title=normalize_text(str(item.get("title", ""))),
                    snippet=normalize_text(str(item.get("description", ""))),
                    original_url=str(item.get("originallink") or item.get("link") or ""),
                    published_at=_parse_naver_date(str(item.get("pubDate", ""))),
                    provider="naver-news",
                )
                if alert.title and alert.original_url:
                    collected[alert.content_hash] = alert

    return list(collected.values())


def collect_open_dart(
    days: int = 30,
    pages: int = 3,
    end_date: date | None = None,
    window_days: int = 30,
) -> list[RawCollectedAlert]:
    api_key = os.environ["OPEN_DART_API_KEY"]
    effective_end_date = end_date or date.today()
    collected: dict[str, RawCollectedAlert] = {}

    for offset in range(0, days, window_days):
        window_end = effective_end_date - timedelta(days=offset)
        window_begin = window_end - timedelta(days=min(window_days, days - offset))
        for page_no in range(1, pages + 1):
            params = urlencode(
                {
                    "crtfc_key": api_key,
                    "bgn_de": window_begin.strftime("%Y%m%d"),
                    "end_de": window_end.strftime("%Y%m%d"),
                    "page_no": page_no,
                    "page_count": 100,
                }
            )
            request = Request(f"https://opendart.fss.or.kr/api/list.json?{params}")
            payload = _json_request(request)
            for item in payload.get("list", []):
                receipt_number = str(item.get("rcept_no", ""))
                report_name = normalize_text(str(item.get("report_nm", "")))
                corp_name = normalize_text(str(item.get("corp_name", "")))
                if not receipt_number or not report_name:
                    continue
                alert = RawCollectedAlert(
                    source_type="DISCLOSURE",
                    title=f"{corp_name} {report_name}".strip(),
                    snippet=report_name,
                    original_url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt_number}",
                    published_at=str(item.get("rcept_dt", "")),
                    provider="open-dart",
                )
                collected[alert.content_hash] = alert

    return list(collected.values())


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def read_raw_alerts(path: Path) -> list[RawCollectedAlert]:
    if not path.exists():
        return []
    alerts: list[RawCollectedAlert] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        alerts.append(
            RawCollectedAlert(
                source_type=payload["source_type"],
                title=payload["title"],
                snippet=payload["snippet"],
                original_url=payload["original_url"],
                published_at=payload["published_at"],
                provider=payload["provider"],
            )
        )
    return alerts


def raw_alert_to_dict(alert: RawCollectedAlert) -> dict[str, Any]:
    return asdict(alert) | {"content_hash": alert.content_hash}


def _json_request(request: Request) -> dict[str, Any]:
    # 공급자 URL은 코드에서 고정하고 사용자 입력을 받지 않는다.
    with urlopen(request, timeout=10) as response:  # noqa: S310  # nosec B310
        return cast(dict[str, Any], json.loads(response.read().decode("utf-8")))


def _parse_naver_date(value: str) -> str:
    if not value:
        return datetime.now(UTC).isoformat()
    return parsedate_to_datetime(value).astimezone(UTC).isoformat()
