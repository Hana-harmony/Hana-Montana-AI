import importlib.util
from pathlib import Path
from types import ModuleType

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, AlertAnalysisResponse
from hannah_montana_ai.training.collector import ProviderCollectionStatus, RawCollectionResult
from hannah_montana_ai.training.live_news_quality_audit import (
    LIVE_NEWS_QUALITY_AUDIT_REPORT_SCHEMA_VERSION,
    LIVE_NEWS_QUALITY_AUDIT_ROW_SCHEMA_VERSION,
    ArticleContent,
    build_live_news_quality_audit_batch,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert


def _load_full_content_script() -> ModuleType:
    script_path = Path("scripts/build_real_full_content_training_data.py")
    spec = importlib.util.spec_from_file_location(
        "build_real_full_content_training_data",
        script_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeModel:
    version = "fake-quality-model"


class FakeAnalyzer:
    model = FakeModel()

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        return AlertAnalysisResponse(
            stock_code="005930",
            stock_name="삼성전자",
            source_type=request.source_type,
            original_title=request.title,
            summary="",
            summary_lines={
                "what": "삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다.",
                "why": "메모리 가격 반등과 HBM 공급 확대가 주요 배경이다.",
                "impact": "투자자는 영업이익 회복 속도와 시장 수요를 확인해야 한다.",
            },
            content_availability="FULL_TEXT",
            event_tags=["EARNINGS", "MACRO"],
            sentiment="POSITIVE",
            importance="HIGH",
            related_stocks=["005930"],
            holder_target=True,
            watchlist_target=True,
            duplicate_key="fake",
            model_version=self.model.version,
            event_confidence=0.82,
            sentiment_confidence=0.74,
            importance_confidence=0.76,
            stock_match_confidence=1.0,
        )


def test_live_news_quality_audit_scores_full_content_summary() -> None:
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
                    title="삼성전자 반도체 실적 개선 기대",
                    snippet="HBM 공급 확대가 주목된다.",
                    original_url="https://example.com/news/1",
                    published_at="Mon, 22 Jun 2026 10:00:00 +0900",
                    provider="naver-news",
                )
            ],
            status=status,
        )

    def fake_content_fetcher(url: str) -> ArticleContent:
        return ArticleContent(
            content=(
                "삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다. "
                "메모리 가격 반등과 HBM 공급 확대가 주요 배경이다. "
                "투자자는 영업이익 회복 속도와 시장 수요를 확인해야 한다."
            ),
            canonical_url=url,
            image_urls=[],
            source_license_policy="licensed_naver_original_full_text_v1",
        )

    batch = build_live_news_quality_audit_batch(
        stock_universe=universe,
        stock_universe_path=Path("data/reference/korea_stock_universe.csv"),
        output_path=Path("data/evaluation/live_news_quality_audit.jsonl"),
        stock_sample_size=1,
        max_news_per_query=1,
        intents=("실적",),
        analyzer=FakeAnalyzer(),
        news_collector=fake_collector,
        content_fetcher=fake_content_fetcher,
    )

    assert len(batch.rows) == 1
    row = batch.rows[0]
    assert row["schema_version"] == LIVE_NEWS_QUALITY_AUDIT_ROW_SCHEMA_VERSION
    assert row["quality_status"] == "pass"
    assert row["quality_score"] == 100
    assert row["quality_findings"] == []
    assert row["content_availability"] == "FULL_TEXT"
    assert row["sampled_stock_model_matched"] is True

    assert batch.report["schema_version"] == LIVE_NEWS_QUALITY_AUDIT_REPORT_SCHEMA_VERSION
    assert batch.report["quality_pass_rate"] == 1.0
    assert batch.report["full_content_rate"] == 1.0
    assert batch.report["sampled_stock_model_match_rate"] == 1.0


class NoisyAnalyzer(FakeAnalyzer):
    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        return AlertAnalysisResponse(
            stock_code=None,
            stock_name=None,
            source_type=request.source_type,
            original_title=request.title,
            summary="",
            summary_lines={
                "what": "로그인 회원가입 전체 메뉴",
                "why": "로그인 회원가입 전체 메뉴",
                "impact": "로그인 회원가입 전체 메뉴",
            },
            event_tags=["GENERAL_MARKET"],
            sentiment="NEUTRAL",
            importance="MEDIUM",
            related_stocks=[],
            holder_target=False,
            watchlist_target=True,
            duplicate_key="fake",
            model_version=self.model.version,
            event_confidence=0.2,
            sentiment_confidence=0.3,
            importance_confidence=0.3,
            stock_match_confidence=0.0,
        )


def test_live_news_quality_audit_flags_noisy_summary() -> None:
    universe = [StockUniverseEntry(stock_code="005930", stock_name="삼성전자")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(provider="naver-news", collected_count=1)
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title="삼성전자 반도체 실적 개선 기대",
                    snippet="HBM 공급 확대가 주목된다.",
                    original_url="https://example.com/news/1",
                    published_at="Mon, 22 Jun 2026 10:00:00 +0900",
                    provider="naver-news",
                )
            ],
            status=status,
        )

    batch = build_live_news_quality_audit_batch(
        stock_universe=universe,
        stock_universe_path=Path("data/reference/korea_stock_universe.csv"),
        output_path=Path("data/evaluation/live_news_quality_audit.jsonl"),
        stock_sample_size=1,
        max_news_per_query=1,
        intents=("실적",),
        analyzer=NoisyAnalyzer(),
        news_collector=fake_collector,
        content_fetcher=lambda _: None,
    )

    row = batch.rows[0]
    assert row["quality_status"] == "fail"
    assert "SUMMARY_BOILERPLATE" in row["quality_findings"]
    assert "SUMMARY_LINE_DUPLICATED" in row["quality_findings"]
    assert "PREDICTED_STOCK_NULL" in row["quality_findings"]
    assert batch.report["quality_pass_rate"] == 0.0
    assert batch.report["quality_finding_counts"]["SUMMARY_BOILERPLATE"] == 1


def test_live_news_quality_audit_can_filter_query_stock_absent_rows() -> None:
    universe = [StockUniverseEntry(stock_code="005930", stock_name="삼성전자")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(
            provider="naver-news",
            attempted_requests=1,
            successful_requests=1,
            collected_count=2,
        )
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title="브로드컴, AI 반도체 수요 확대로 급등",
                    snippet="미국 기술주 투자 심리가 개선됐다.",
                    original_url="https://example.com/news/foreign-chip",
                    published_at="Mon, 22 Jun 2026 10:00:00 +0900",
                    provider="naver-news",
                ),
                RawCollectedAlert(
                    source_type="NEWS",
                    title="삼성전자, HBM 공급 확대 기대",
                    snippet="삼성전자 반도체 실적 개선 전망이 제기됐다.",
                    original_url="https://example.com/news/samsung-hbm",
                    published_at="Mon, 22 Jun 2026 10:01:00 +0900",
                    provider="naver-news",
                ),
            ],
            status=status,
        )

    def fake_content_fetcher(url: str) -> ArticleContent:
        if "foreign-chip" in url:
            return ArticleContent(
                content="브로드컴은 AI 인프라 투자 확대 영향으로 매출 전망을 높였다.",
                canonical_url=url,
                image_urls=[],
                source_license_policy="licensed_naver_original_full_text_v1",
            )
        return ArticleContent(
            content=(
                "삼성전자는 HBM 공급 확대와 메모리 가격 반등으로 반도체 실적 "
                "개선 기대가 커졌다고 밝혔다."
            ),
            canonical_url=url,
            image_urls=[],
            source_license_policy="licensed_naver_original_full_text_v1",
        )

    batch = build_live_news_quality_audit_batch(
        stock_universe=universe,
        stock_universe_path=Path("data/reference/korea_stock_universe.csv"),
        output_path=Path("data/evaluation/live_news_quality_audit.jsonl"),
        stock_sample_size=1,
        max_news_per_query=2,
        intents=("실적",),
        analyzer=FakeAnalyzer(),
        news_collector=fake_collector,
        content_fetcher=fake_content_fetcher,
        require_query_stock_match=True,
    )

    assert len(batch.rows) == 1
    assert batch.rows[0]["title"] == "삼성전자, HBM 공급 확대 기대"
    assert batch.report["filtered_query_stock_absent_count"] == 1
    assert batch.report["emitted_row_count"] == 1


def test_live_news_quality_audit_filters_broker_research_attribution() -> None:
    universe = [StockUniverseEntry(stock_code="001750", stock_name="한양증권")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(provider="naver-news", collected_count=1)
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title="엘앤씨바이오, 신제품 성장 기대",
                    snippet="한양증권 연구원은 바이오 업종 전망을 제시했다.",
                    original_url="https://example.com/news/broker-report",
                    published_at="Mon, 22 Jun 2026 10:02:00 +0900",
                    provider="naver-news",
                )
            ],
            status=status,
        )

    def fake_content_fetcher(url: str) -> ArticleContent:
        return ArticleContent(
            content=(
                "오병용 한양증권 연구원은 엘앤씨바이오의 신제품 성장세가 "
                "내년 실적 개선을 이끌 수 있다고 평가했다."
            ),
            canonical_url=url,
            image_urls=[],
            source_license_policy="licensed_naver_original_full_text_v1",
        )

    batch = build_live_news_quality_audit_batch(
        stock_universe=universe,
        stock_universe_path=Path("data/reference/korea_stock_universe.csv"),
        output_path=Path("data/evaluation/live_news_quality_audit.jsonl"),
        stock_sample_size=1,
        max_news_per_query=1,
        intents=("실적",),
        analyzer=FakeAnalyzer(),
        news_collector=fake_collector,
        content_fetcher=fake_content_fetcher,
        require_query_stock_match=True,
    )

    assert batch.rows == []
    assert batch.report["filtered_query_stock_absent_count"] == 1


def test_python_full_content_extractor_prefers_article_container() -> None:
    html = """
    <html>
      <body>
        <nav>로그인 회원가입 전체 메뉴 검색 열기</nav>
        <div>복사하기 스크롤 이동 상태바 많이 본 뉴스</div>
        <div class="article_body">
          <p>한미반도체는 TC본더 수요 증가로 반도체 장비 매출 확대가 기대된다.</p>
          <p>HBM 투자 확대와 공급계약 증가가 주요 배경이다.</p>
          <p>투자자는 영업이익 성장과 주가 변동성을 함께 확인해야 한다.</p>
        </div>
        <footer>이용약관 개인정보 저작권</footer>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(html)

    assert "TC본더 수요 증가" in text
    assert "전체 메뉴" not in text
    assert "이용약관" not in text


def test_full_content_builder_reuses_existing_licensed_rows() -> None:
    module = _load_full_content_script()

    assert module.is_reusable_full_content_policy(
        "licensed_naver_original_full_text_v1"
    )
    assert module.is_reusable_full_content_policy("opendart_public_disclosure_text_v1")
    assert module.is_reusable_full_content_policy("internal_rights_safe_full_article_v1")
    assert not module.is_reusable_full_content_policy("NAVER_SEARCH_SNIPPET_ONLY")


def test_full_content_builder_stops_at_target_row_count() -> None:
    module = _load_full_content_script()

    assert module.target_reached({"a": {}, "b": {}}, 2)
    assert not module.target_reached({"a": {}}, 2)
    assert not module.target_reached({"a": {}, "b": {}}, 0)
