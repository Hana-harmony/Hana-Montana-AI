import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

from build_real_full_content_training_data import NEWS_POLICY, fetch_news_content

from hannah_montana_ai.domain.schemas import IntelligenceEventRequest, IntelligenceEventResponse
from hannah_montana_ai.training.collector import load_local_env
from hannah_montana_ai.training.live_news_evaluation import DEFAULT_LIVE_NEWS_INTENTS
from hannah_montana_ai.training.live_news_quality_audit import (
    ArticleContent,
    build_live_news_quality_audit_batch,
    report_to_json,
    rows_to_jsonl,
)
from hannah_montana_ai.training.stock_universe import load_stock_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = PROJECT_ROOT / "secrets.local.env"
DEFAULT_STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/evaluation/live_news_quality_audit.jsonl"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports/live-news-quality-audit-report.json"


def main() -> None:
    args = _parse_args()
    env_path = _project_path(args.env_file)
    stock_universe_path = _project_path(args.stock_universe)
    output_path = _project_path(args.output)
    report_path = _project_path(args.report)

    load_local_env(env_path)
    stock_universe = load_stock_universe(stock_universe_path)
    event_builder = (
        HttpIntelligenceEventClient(
            args.ai_base_url,
            timeout_seconds=args.ai_timeout_seconds,
        )
        if args.ai_base_url.strip()
        else None
    )
    batch = build_live_news_quality_audit_batch(
        stock_universe=stock_universe,
        stock_universe_path=stock_universe_path,
        output_path=output_path,
        stock_sample_size=args.stock_sample_size,
        max_news_per_query=args.max_news_per_query,
        intents=tuple(args.intent or DEFAULT_LIVE_NEWS_INTENTS),
        seed=args.seed,
        sleep_seconds=args.sleep_seconds,
        max_retries=args.max_retries,
        sample_limit=args.sample_limit,
        event_builder=event_builder,
        content_fetcher=_fetch_article_content,
        require_query_stock_match=args.require_query_stock_match,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rows_to_jsonl(batch.rows), encoding="utf-8")
    report_path.write_text(report_to_json(batch.report), encoding="utf-8")
    print(report_to_json(batch.report), end="")


def _fetch_article_content(url: str, title: str) -> ArticleContent | None:
    content = fetch_news_content(url, expected_title=title)
    if content is None:
        return None
    return ArticleContent(
        content=content.content,
        canonical_url=content.canonical_url,
        image_urls=content.image_urls,
        source_license_policy=NEWS_POLICY,
    )


class HttpIntelligenceEventClient:
    def __init__(self, base_url: str, timeout_seconds: float = 90.0) -> None:
        parsed_url = urllib.parse.urlparse(base_url)
        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("--ai-base-url must use http or https")
        self._endpoint = base_url.rstrip("/") + "/api/v1/intelligence/events"
        self._timeout_seconds = timeout_seconds

    def build_response(self, request: IntelligenceEventRequest) -> IntelligenceEventResponse:
        http_request = urllib.request.Request(  # noqa: S310
            self._endpoint,
            data=json.dumps(request.model_dump(mode="json")).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(http_request, timeout=self._timeout_seconds) as response:  # noqa: S310
            envelope = json.loads(response.read().decode("utf-8"))
        data = envelope.get("data")
        if not envelope.get("success") or not isinstance(data, dict):
            raise RuntimeError(f"Hannah AI intelligence event failed: {envelope}")
        return IntelligenceEventResponse.model_validate(data)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a live full-content news AI summary quality audit report."
    )
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--stock-universe", type=Path, default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--stock-sample-size", type=int, default=30)
    parser.add_argument("--max-news-per-query", type=int, default=3)
    parser.add_argument("--intent", action="append")
    parser.add_argument("--seed", type=int, default=20260622)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--sample-limit", type=int)
    parser.add_argument(
        "--ai-base-url",
        default="",
        help="실행 중인 Hannah AI 서버를 통해 /api/v1/intelligence/events를 검증한다.",
    )
    parser.add_argument(
        "--ai-timeout-seconds",
        type=float,
        default=240.0,
        help="AI 이벤트 응답 검증 HTTP timeout.",
    )
    parser.add_argument(
        "--require-query-stock-match",
        action="store_true",
        help=(
            "제목, snippet, 전문에서 query 대상 종목명이 확인된 기사만 품질 감사 row로 남긴다."
        ),
    )
    return parser.parse_args()


def _project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


if __name__ == "__main__":
    main()
