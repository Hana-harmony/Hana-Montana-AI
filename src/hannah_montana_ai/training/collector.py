from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
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

NAVER_NEWS_CREDENTIAL_NAMES = ("NAVER_NEWS_CLIENT_ID", "NAVER_NEWS_CLIENT_SECRET")
OPEN_DART_CREDENTIAL_NAMES = ("OPEN_DART_API_KEY",)


@dataclass
class ProviderCollectionStatus:
    provider: str
    attempted_requests: int = 0
    successful_requests: int = 0
    rate_limited_requests: int = 0
    failed_requests: int = 0
    collected_count: int = 0
    completed: bool = True
    errors: list[str] = field(default_factory=list)

    def record_error(self, message: str) -> None:
        self.completed = False
        self.errors.append(message)

    def to_dict(self) -> dict[str, int | bool | str | list[str]]:
        return {
            "provider": self.provider,
            "attempted_requests": self.attempted_requests,
            "successful_requests": self.successful_requests,
            "rate_limited_requests": self.rate_limited_requests,
            "failed_requests": self.failed_requests,
            "collected_count": self.collected_count,
            "completed": self.completed,
            "errors": self.errors,
        }


@dataclass(frozen=True)
class RawCollectionResult:
    alerts: list[RawCollectedAlert]
    status: ProviderCollectionStatus


class ProviderCredentialError(RuntimeError):
    pass


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def collect_naver_news(
    max_per_query: int = 200,
    sleep_seconds: float = 0.4,
    max_retries: int = 3,
) -> RawCollectionResult:
    credentials = _required_credentials(NAVER_NEWS_CREDENTIAL_NAMES)
    client_id = credentials["NAVER_NEWS_CLIENT_ID"]
    client_secret = credentials["NAVER_NEWS_CLIENT_SECRET"]
    collected: dict[str, RawCollectedAlert] = {}
    status = ProviderCollectionStatus(provider="naver-news")

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
            payload = _json_request_with_retry(
                request,
                status=status,
                max_retries=max_retries,
                base_sleep_seconds=sleep_seconds,
            )
            if payload is None:
                status.record_error(f"news query stopped: query={query} start={start}")
                break
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
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    status.collected_count = len(collected)
    return RawCollectionResult(alerts=list(collected.values()), status=status)


def collect_naver_news_legacy(max_per_query: int = 200) -> list[RawCollectedAlert]:
    return collect_naver_news(max_per_query=max_per_query).alerts


def collect_open_dart(
    days: int = 30,
    pages: int = 3,
    end_date: date | None = None,
    window_days: int = 30,
    sleep_seconds: float = 0.1,
) -> RawCollectionResult:
    credentials = _required_credentials(OPEN_DART_CREDENTIAL_NAMES)
    api_key = credentials["OPEN_DART_API_KEY"]
    effective_end_date = end_date or date.today()
    collected: dict[str, RawCollectedAlert] = {}
    status = ProviderCollectionStatus(provider="open-dart")

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
            payload = _json_request_with_retry(
                request,
                status=status,
                max_retries=2,
                base_sleep_seconds=sleep_seconds,
            )
            if payload is None:
                status.record_error(
                    f"dart window stopped: begin={window_begin} end={window_end} page={page_no}"
                )
                continue
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
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    status.collected_count = len(collected)
    return RawCollectionResult(alerts=list(collected.values()), status=status)


def collect_open_dart_legacy(
    days: int = 30,
    pages: int = 3,
    end_date: date | None = None,
    window_days: int = 30,
) -> list[RawCollectedAlert]:
    return collect_open_dart(
        days=days,
        pages=pages,
        end_date=end_date,
        window_days=window_days,
    ).alerts


def merge_raw_alerts(alerts: list[RawCollectedAlert]) -> list[RawCollectedAlert]:
    return list({alert.content_hash: alert for alert in alerts}.values())


def should_write_raw_alerts(existing_count: int, next_count: int, force: bool = False) -> bool:
    # 수집 실패로 기존 코퍼스를 빈 파일이나 축소된 파일로 덮어쓰지 않는다.
    return force or next_count >= existing_count


def collection_status_to_dict(statuses: list[ProviderCollectionStatus]) -> list[dict[str, Any]]:
    return [status.to_dict() for status in statuses]


def _required_credentials(names: tuple[str, ...]) -> dict[str, str]:
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise ProviderCredentialError(
            "Missing provider credential environment variables: " + ", ".join(missing)
        )
    return {name: os.environ[name] for name in names}


def _json_request_with_retry(
    request: Request,
    status: ProviderCollectionStatus,
    max_retries: int,
    base_sleep_seconds: float,
) -> dict[str, Any] | None:
    for attempt in range(max_retries + 1):
        status.attempted_requests += 1
        try:
            payload = _json_request(request)
            status.successful_requests += 1
            return payload
        except HTTPError as exception:
            if exception.code == 429:
                status.rate_limited_requests += 1
                if attempt < max_retries:
                    time.sleep(_retry_sleep(base_sleep_seconds, attempt))
                    continue
                status.record_error("rate limit exceeded")
                return None
            if exception.code in {500, 502, 503, 504} and attempt < max_retries:
                status.failed_requests += 1
                time.sleep(_retry_sleep(base_sleep_seconds, attempt))
                continue
            status.failed_requests += 1
            raise

    return None


def _retry_sleep(base_sleep_seconds: float, attempt: int) -> float:
    return float(max(base_sleep_seconds, 0.1) * (2**attempt))


def _json_request(request: Request) -> dict[str, Any]:
    # 공급자 URL은 코드에서 고정하고 사용자 입력을 받지 않는다.
    with urlopen(request, timeout=10) as response:  # noqa: S310  # nosec B310
        return cast(dict[str, Any], json.loads(response.read().decode("utf-8")))


def _parse_naver_date(value: str) -> str:
    if not value:
        return datetime.now(UTC).isoformat()
    return parsedate_to_datetime(value).astimezone(UTC).isoformat()


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
