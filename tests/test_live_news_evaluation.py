from pathlib import Path

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, AlertAnalysisResponse
from hannah_montana_ai.training.collector import ProviderCollectionStatus, RawCollectionResult
from hannah_montana_ai.training.live_news_evaluation import (
    LIVE_NEWS_EVALUATION_REPORT_SCHEMA_VERSION,
    LIVE_NEWS_EVALUATION_ROW_SCHEMA_VERSION,
    build_live_news_evaluation_batch,
    build_live_news_queries,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert


class FakeModel:
    version = "fake-live-model"

    def event_tag_probabilities(self, text: str, source_type: str) -> dict[str, float]:
        return {"CONTRACT": 0.82, "GENERAL_MARKET": 0.18}

    def sentiment_probabilities(self, text: str) -> dict[str, float]:
        return {"NEGATIVE": 0.05, "NEUTRAL": 0.15, "POSITIVE": 0.8}

    def importance_probabilities(self, text: str, source_type: str) -> dict[str, float]:
        return {"LOW": 0.02, "MEDIUM": 0.08, "HIGH": 0.85, "CRITICAL": 0.05}


class FakeAnalyzer:
    model = FakeModel()

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        return AlertAnalysisResponse(
            stock_code="005930",
            stock_name="삼성전자",
            source_type=request.source_type,
            original_title=request.title,
            summary=request.title,
            event_tags=["CONTRACT"],
            sentiment="POSITIVE",
            importance="HIGH",
            related_stocks=["005930"],
            holder_target=True,
            watchlist_target=True,
            duplicate_key="fake",
            model_version=self.model.version,
        )


def test_build_live_news_queries_is_seeded_and_stock_intent_expanded() -> None:
    universe = [
        StockUniverseEntry(stock_code="005930", stock_name="삼성전자"),
        StockUniverseEntry(stock_code="000660", stock_name="SK하이닉스"),
        StockUniverseEntry(stock_code="035420", stock_name="NAVER"),
    ]

    first = build_live_news_queries(
        universe,
        stock_sample_size=2,
        intents=("주가", "실적"),
        seed=7,
    )
    second = build_live_news_queries(
        universe,
        stock_sample_size=2,
        intents=("주가", "실적"),
        seed=7,
    )

    assert first == second
    assert len(first) == 4
    assert {query.intent for query in first} == {"주가", "실적"}


def test_live_news_evaluation_batch_records_unlabeled_model_review_rows() -> None:
    universe = [StockUniverseEntry(stock_code="005930", stock_name="삼성전자")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(
            provider="naver-news",
            attempted_requests=1,
            successful_requests=1,
            collected_count=1,
        )
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title="삼성전자 대규모 공급계약 체결",
                    snippet="실적 개선 기대가 커졌다",
                    original_url="https://example.com/news/1",
                    published_at="Sat, 13 Jun 2026 10:00:00 +0900",
                    provider="naver-news",
                )
            ],
            status=status,
        )

    batch = build_live_news_evaluation_batch(
        stock_universe=universe,
        stock_universe_path=Path("data/reference/korea_stock_universe.csv"),
        output_path=Path("data/evaluation/live_news_evaluation_batch.jsonl"),
        stock_sample_size=1,
        max_news_per_query=1,
        intents=("주가",),
        analyzer=FakeAnalyzer(),
        news_collector=fake_collector,
    )

    assert len(batch.rows) == 1
    row = batch.rows[0]
    assert row["schema_version"] == LIVE_NEWS_EVALUATION_ROW_SCHEMA_VERSION
    assert row["review_status"] == "needs_review"
    assert row["sampled_stock_code"] == "005930"
    assert row["sampled_stock_primary_matched"] is True
    assert row["sampled_stock_related_matched"] is True
    assert row["sampled_stock_model_matched"] is True
    assert row["sampled_stock_text_matched"] is True
    assert row["event_top_label"] == "CONTRACT"
    assert row["sentiment_top_confidence"] == 0.8
    assert row["final_tags"] == []
    assert row["final_sentiment"] == ""

    assert batch.report["schema_version"] == LIVE_NEWS_EVALUATION_REPORT_SCHEMA_VERSION
    assert batch.report["evaluation_policy"]["f1_available"] is False
    assert batch.report["sampled_stock_primary_match_count"] == 1
    assert batch.report["sampled_stock_related_match_count"] == 1
    assert batch.report["sampled_stock_model_match_rate"] == 1.0
    assert batch.report["provider_status_totals"]["attempted_requests"] == 1
