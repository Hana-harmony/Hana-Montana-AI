import importlib.util
from pathlib import Path
from types import ModuleType

from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
)
from hannah_montana_ai.training.collector import ProviderCollectionStatus, RawCollectionResult
from hannah_montana_ai.training.live_news_quality_audit import (
    LIVE_NEWS_QUALITY_AUDIT_REPORT_SCHEMA_VERSION,
    LIVE_NEWS_QUALITY_AUDIT_ROW_SCHEMA_VERSION,
    ArticleContent,
    _contains_translated_content_hallucinated_surface,
    _has_financial_context,
    _stock_text_matched,
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


class SummaryOnlyConfidentAnalyzer(FakeAnalyzer):
    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        response = super().analyze(request)
        return response.model_copy(
            update={
                "content_availability": "SUMMARY_ONLY",
                "event_confidence": 0.55,
                "sentiment_confidence": 0.55,
                "importance_confidence": 0.55,
            }
        )


class RiskyTranslationEventBuilder:
    def build_response(self, request: IntelligenceEventRequest) -> IntelligenceEventResponse:
        return IntelligenceEventResponse(
            alert_id="fake-alert",
            duplicate_key="fake-translation",
            stock_code="086790",
            stock_name="하나금융지주",
            news_disclosure_type=request.source_type,
            original_title=request.title,
            translated_title="Hana Securities said bank stocks had solid second-quarter earnings.",
            summary="",
            summary_lines={
                "what": "Korean bank stocks moved around solid second-quarter earnings.",
                "why": "The article cites rate momentum and preferred bank-stock picks.",
                "impact": "Investors should track bank earnings and rate sensitivity.",
            },
            translated_summary=(
                "Korean bank stocks moved around solid second-quarter earnings.\n"
                "The article cites rate momentum and preferred bank-stock picks.\n"
                "Investors should track bank earnings and rate sensitivity."
            ),
            original_content=request.content,
            translated_content=(
                "KB semaphore and Newhan bank's 2-month earnings improved, while "
                "Korean exporters were treated as the highest bidder."
            ),
            original_body=request.content,
            translated_body=(
                "KB semaphore and Newhan bank's 2-month earnings improved, while "
                "Korean exporters were treated as the highest bidder."
            ),
            body_source_type="FULL_TEXT",
            image_urls=[],
            content_availability="FULL_TEXT",
            sentiment="POSITIVE",
            importance="HIGH",
            event_tag="EARNINGS",
            event_tags=["EARNINGS", "MACRO"],
            related_stocks=["086790"],
            is_holder_target=True,
            is_watchlist_target=True,
            glossary_terms=[],
            translation_quality_flags=["QWEN_TRANSLATION_SEMANTIC_MISMATCH:KB_FINANCIAL"],
            original_url=request.original_url,
            provider=request.provider or "naver-news",
            published_at=request.published_at,
            translation_provider="local-open-source-qwen3-translation",
            translation_model_version="fake-qwen3-translation",
            translation_status="TRANSLATED",
            model_version="fake-quality-model",
            event_confidence=0.82,
            sentiment_confidence=0.8,
            importance_confidence=0.75,
            stock_match_confidence=1.0,
            data_source="test",
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

    def fake_content_fetcher(url: str, _title: str) -> ArticleContent:
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


def test_live_news_quality_audit_marks_summary_only_confidence_cap() -> None:
    universe = [StockUniverseEntry(stock_code="005930", stock_name="삼성전자")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(provider="naver-news", collected_count=1)
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title="삼성전자 반도체 실적 개선 기대",
                    snippet="HBM 공급 확대가 주목된다.",
                    original_url="https://example.com/news/summary-only",
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
        analyzer=SummaryOnlyConfidentAnalyzer(),
        news_collector=fake_collector,
        content_fetcher=lambda *_: None,
    )

    row = batch.rows[0]
    assert "MISSING_FULL_CONTENT" in row["quality_findings"]
    assert "SUMMARY_ONLY_CONFIDENCE_CAPPED" in row["quality_findings"]


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
        content_fetcher=lambda *_: None,
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

    def fake_content_fetcher(url: str, _title: str) -> ArticleContent:
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

    def fake_content_fetcher(url: str, _title: str) -> ArticleContent:
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


def test_live_news_quality_audit_fails_critical_translation_flags() -> None:
    universe = [StockUniverseEntry(stock_code="086790", stock_name="하나금융지주")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(provider="naver-news", collected_count=1)
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title='하나증권 "은행주 2분기 실적 양호"',
                    snippet="KB금융지주와 신한금융지주가 최선호주로 제시됐다.",
                    original_url="https://example.com/news/bank-translation-risk",
                    published_at="Mon, 06 Jul 2026 09:29:16 +0900",
                    provider="naver-news",
                )
            ],
            status=status,
        )

    def fake_content_fetcher(url: str, _title: str) -> ArticleContent:
        return ArticleContent(
            content=(
                "하나증권은 은행주 2분기 실적이 양호하고 최선호주는 "
                "KB금융지주와 신한금융지주라고 밝혔다."
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
        intents=("주가",),
        analyzer=FakeAnalyzer(),
        event_builder=RiskyTranslationEventBuilder(),
        news_collector=fake_collector,
        content_fetcher=fake_content_fetcher,
    )

    row = batch.rows[0]
    assert row["quality_status"] == "fail"
    assert "TRANSLATED_CONTENT_HALLUCINATED_SURFACE" in row["quality_findings"]
    assert "TRANSLATION_CRITICAL_REVIEW_FLAG" in row["quality_findings"]
    assert batch.report["quality_pass_rate"] == 0.0


def test_live_news_quality_audit_does_not_flag_shinhan_bank_as_nhan_bank() -> None:
    assert not _contains_translated_content_hallucinated_surface(
        "Jin later held senior management roles at Shinhan Bank and Shinhan Financial Group."
    )
    assert _contains_translated_content_hallucinated_surface(
        "KB Financial and Nhan bank were treated as the highest bidder."
    )


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


def test_python_full_content_extractor_handles_newdaily_article_conent_container() -> None:
    html = """
    <html>
      <body>
        <div>많이 본 뉴스 로그인 검색</div>
        <div id="article_conent">
          <p>상반기 내내 정책 부담의 시험대에 올랐던 은행들이 반등했다.</p>
          <p>4대 금융지주는 500조원 정책금융 부담에도 주주환원 기대를 받았다.</p>
          <p>투자자는 저평가 해소와 자본효율 개선 여부를 확인해야 한다.</p>
        </div>
        <ul><li>관련기사</li></ul>
        <footer>저작권자 개인정보처리방침</footer>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="정책 부담 견딘 은행들 … 남은 과제는 저평가 해소",
    )

    assert "정책 부담의 시험대" in text
    assert "500조원 정책금융" in text
    assert "많이 본 뉴스" not in text
    assert "저작권자" not in text


def test_python_full_content_extractor_handles_imaeil_articlebody_container() -> None:
    html = """
    <html>
      <body>
        <div>최신기사 오피니언 정치 경제 사회 국제 문화 스포츠 라이프</div>
        <div class="article_view v2">
          <div class="article_content">
            <div id="articlebody" itemprop="articleBody">
              <figure><img src="/photo.jpg" alt="동전주"><figcaption>연합뉴스</figcaption></figure>
              <p>오는 7월부터 주가 1천원 미만인 이른바 동전주가 상장폐지 관리 대상에 포함된다.</p>
              <p>금융당국과 한국거래소는 부실기업 퇴출을 위한 상장폐지 제도 개편안을 시행한다.</p>
              <p>대구경북 상장사 가운데 이월드 등 일부 기업은 주가 기준을 확인해야 한다.</p>
            </div>
            <div class="chn_box">네이버TV 구독 유튜브 구독</div>
          </div>
        </div>
        <footer>RSS 개인정보처리방침</footer>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="국내 증시 동전주 퇴출 칼바람",
    )

    assert "상장폐지 관리 대상" in text
    assert "이월드" in text
    assert "최신기사 오피니언" not in text
    assert "네이버TV 구독" not in text


def test_python_full_content_extractor_prefers_herald_article_body_over_popular_news() -> None:
    html = """
    <html>
      <body>
        <article class="popular_news">
          <p>많이 본 기사 부동산 연예 사회 국제 unrelated popular content.</p>
          <p>김흥국이 16억에 낙찰받은 그집 관련 인기기사 내용이다.</p>
        </article>
        <section class="section_view">
          <article class="article-view article-body" id="articleText" itemprop="articleBody">
            <p>원/달러 외환 거래가 6일 오전 6시부터 24시간 무중단 체제로 전환됐다.</p>
            <p>이날 오전 6시 원/달러 환율은 1527.6원으로 거래를 시작했다.</p>
            <p>하나은행 딜링룸에서 외환시장 24시간 개장 상황을 점검했다.</p>
          </article>
        </section>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="첫 외환 24시간 개장 1527.6원 출발",
    )

    assert "24시간 무중단" in text
    assert "1527.6원" in text
    assert "많이 본 기사" not in text


def test_python_full_content_extractor_reads_news1_content_arrange_json() -> None:
    arrange_json = (
        '{"contentArrange":['
        '{"type":"image","content":"사진 설명"},'
        '{"type":"text","content":"양 씨 남편 일당은 코스닥 상장사 듀오백 주식에 '
        '대한 시세조종성 주문을 제출한 혐의를 받는다."},'
        '{"type":"text","content":"검찰은 듀오백 주식을 최소 289억 원 상당 거래해 '
        '주가를 인위적으로 상승시켰다고 봤다."}'
        "]}"
    )
    html = f"""
    <html>
      <body>
        <script>{arrange_json}</script>
        <div class="article">관련 키워드 법원 사회 인기기사</div>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="경찰에 룸살롱 제공한 양정원 남편",
    )

    assert "듀오백 주식" in text
    assert "289억 원" in text
    assert "인기기사" not in text


def test_python_full_content_extractor_prefers_title_matching_candidate() -> None:
    html = """
    <html>
      <body>
        <div class="content">
          <p>사진 '내란 가담' 박성재 1심 징역 25년형.</p>
          <p>서울중앙지법은 내란 중요임무 종사 혐의와 직권남용 혐의를 판단했다.</p>
          <p>정치권은 판결 리스크와 후속 수사 전망을 주목하고 있다.</p>
        </div>
        <article>
          <h1>한투운용, 반도체 AI 전력 ETF 2종 상장</h1>
          <p>한국투자신탁운용은 반도체와 AI 전력 인프라에 투자하는 ETF 2종을 상장했다.</p>
          <p>삼성전자와 SK하이닉스 등 반도체 공급망 투자 수요가 배경이다.</p>
          <p>투자자는 ETF 편입 종목과 시장 변동성을 함께 확인해야 한다.</p>
        </article>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="한투운용, 반도체 AI 전력 ETF 2종 상장",
    )

    assert "ETF 2종을 상장" in text
    assert "내란 가담" not in text


def test_python_full_content_extractor_skips_related_news_container() -> None:
    html = """
    <html>
      <body>
        <div class="related_news cf">
          <p>[관련기사] [N2 모닝 경제 브리핑-7월 1일] 미국 증시 관련기사 목록.</p>
          <p>[N2 모닝 경제 브리핑-7월 2일] 관련기사 목록.</p>
        </div>
        <div class="view_con_wrap">
          <p>[뉴스투데이=김소연 기자] 뉴욕 금융시장은 AI 반도체주 강세로 상승했다.</p>
          <p>나스닥지수와 S&P500지수는 기술주 매수세 속에 반기 마지막 거래일을 마쳤다.</p>
          <p>투자자는 금리 기대와 반도체 업종 쏠림을 함께 점검해야 한다.</p>
        </div>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="[N2 모닝 경제 브리핑-7월 1일] 美 증시",
    )

    assert "뉴욕 금융시장은 AI 반도체주 강세" in text
    assert "[관련기사]" not in text


def test_python_full_content_extractor_reads_balanced_article_body_id() -> None:
    html = """
    <html>
      <body>
        <div id="user-container">icon PDF보기 기사공유하기 가나다라마바사</div>
        <div id="article-view-content-div" itemprop="articleBody">
          <p><strong>■한국GSK, 자궁체부암 인식의 달 기념 심포지엄 개최</strong></p>
          <div><figure><img src="/photo.jpg"><figcaption>행사 사진</figcaption></figure></div>
          <p>한국GSK는 자궁내막암 최신 치료 지견을 공유했다고 밝혔다.</p>
          <p>제약업계는 신약 공급 일정과 임상 데이터를 함께 확인하고 있다.</p>
        </div>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="[제약업계 소식] 6월 25일",
    )

    assert "자궁내막암 최신 치료 지견" in text
    assert "신약 공급 일정" in text
    assert "기사공유하기" not in text


def test_python_full_content_extractor_prefers_balanced_edaily_news_body() -> None:
    html = """
    <html>
      <body>
        <div class="menu_articlearea">실시간뉴스 로그인 전체 메뉴 경제 사회 연예</div>
        <div class="news_body" itemprop="articleBody">
          [이데일리 김새미 기자] 7월 바이오업계의 주요 이벤트는 HLB 간암 신약
          리보세라닙의 허가 여부와 코오롱티슈진 TG-C 임상 3상 공개로 압축된다.
          <div class="adTarget01"><iframe title="본문"></iframe></div>
          HLB는 FDA 허가 여부 결정을 앞두고 있고 큐로셀은 급여 심사 재도전에 나선다.
          투자자는 허가 일정, 임상 데이터, 급여 심사 결과를 함께 확인해야 한다.
        </div>
        <div class="right_trend">주요뉴스 정치 사회 연예 스포츠</div>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="HLB 운명의 날에 TG-C 설욕전까지",
    )

    assert text.startswith("[이데일리 김새미 기자]")
    assert "큐로셀은 급여 심사 재도전" in text
    assert "실시간뉴스 로그인" not in text
    assert "주요뉴스 정치" not in text


def test_python_full_content_extractor_reads_chosun_article_body_class() -> None:
    html = """
    <html>
      <head>
        <meta name="description"
              content="K-바이오 키운 코스닥 기술 수출 꽃 피우고 옥석 가리기 시험대">
      </head>
      <body>
        <section class="article-body" itemProp="articleBody">
          <figure class="article-body__content article-body__content-image">
            <amp-img src="https://img.example.com/kosdaq.jpg"></amp-img>
            <figcaption>코스닥 30주년 기념행사 사진</figcaption>
          </figure>
          <p class="article-body__content article-body__content-text">
            지난 1일 코스닥 시장 출범 30주년을 맞았다.
            코스닥은 국내 제약·바이오 산업의 성장 사다리 역할을 해왔다.
          </p>
          <p class="article-body__content article-body__content-text">
            에이비엘바이오, 알테오젠, 리가켐바이오 등 기술 특례 상장 기업들이
            세계 시장에서 조 단위 기술 수출 성과를 거두며 경쟁력을 입증했다.
          </p>
          <p class="article-body__content article-body__content-text">
            KOSDAQ Connect 2026에는 큐로셀과 여러 바이오 기업이 참가해
            기관 투자자와 임상 데이터, 기술 수출 전략을 논의한다.
          </p>
          <p class="article-body__content article-body__content-text">
            투자자는 상장 유지 기준 강화와 바이오 업종 투자 심리 변화를 함께 확인해야 한다.
          </p>
        </section>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="K-바이오 키운 코스닥",
    )

    assert "성장 사다리 역할" in text
    assert "큐로셀" in text
    assert "상장 유지 기준 강화" in text
    assert "K-바이오 키운 코스닥 기술 수출" not in text


def test_python_full_content_extractor_reads_sentv_section_body() -> None:
    html = """
    <html>
      <body>
        <div class="news_home_list section_2">
          <p>주가 부진에 유증 물량 증가와 대주주 변경이 이어졌다.</p>
          <p>오늘이엔엠의 새 대주주 측 이력과 자금 조달 경로가 확인됐다.</p>
          <p>투자자는 지배구조 변화와 추가 자금 조달 위험을 살펴야 한다.</p>
        </div>
        <div class="news_home_list section_3">
          <p>관련뉴스 태성 신공장 완공 은행권 보안 투자 증가.</p>
        </div>
      </body>
    </html>
    """

    text = _load_full_content_script().extract_article_text(
        html,
        expected_title="오늘이엔엠, 기묘한 손바뀜",
    )

    assert "대주주 변경이 이어졌다" in text
    assert "지배구조 변화" in text
    assert "관련뉴스" not in text


def test_live_news_quality_audit_filters_non_financial_short_stock_name_context() -> None:
    entertainment_alert = RawCollectedAlert(
        source_type="NEWS",
        title="이본, 27년 만에 가수로 복귀",
        snippet="1993년 SBS 공채 탤런트로 데뷔한 배우가 새 앨범을 냈다는 전망이다.",
        original_url="https://example.com/entertainment/sbs",
        published_at="Mon, 06 Jul 2026 10:00:00 +0900",
        provider="naver-news",
    )
    market_alert = RawCollectedAlert(
        source_type="NEWS",
        title="SBS 주가, 실적 전망에 상승",
        snippet="광고 매출과 콘텐츠 계약 기대가 주가에 반영됐다.",
        original_url="https://example.com/market/sbs",
        published_at="Mon, 06 Jul 2026 10:00:00 +0900",
        provider="naver-news",
    )

    assert not _has_financial_context(entertainment_alert)
    assert _has_financial_context(market_alert)


def test_live_news_quality_audit_filters_short_stock_media_source_context() -> None:
    universe = [StockUniverseEntry(stock_code="034120", stock_name="SBS")]

    def fake_collector(**kwargs: object) -> RawCollectionResult:
        status = ProviderCollectionStatus(provider="naver-news", collected_count=2)
        return RawCollectionResult(
            alerts=[
                RawCollectedAlert(
                    source_type="NEWS",
                    title="오늘도 롤러코스피 등락 거듭 끝 8000선 지켜",
                    snippet=(
                        "실적 발표를 앞둔 삼성전자는 등락을 보였다. "
                        "증시 흐름은 SBS Biz 이광호 기자가 전했다."
                    ),
                    original_url="https://biz.sbs.co.kr/article/20000320880",
                    published_at="Mon, 06 Jul 2026 15:25:00 +0900",
                    provider="naver-news",
                ),
                RawCollectedAlert(
                    source_type="NEWS",
                    title="SBS 주가, 광고 매출 회복 기대에 상승",
                    snippet="방송 광고 매출과 콘텐츠 계약 기대가 주가에 반영됐다.",
                    original_url="https://example.com/market/sbs-stock",
                    published_at="Mon, 06 Jul 2026 15:26:00 +0900",
                    provider="naver-news",
                ),
            ],
            status=status,
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
        content_fetcher=lambda *_: None,
        require_query_stock_match=True,
    )

    assert len(batch.rows) == 1
    assert batch.rows[0]["title"] == "SBS 주가, 광고 매출 회복 기대에 상승"
    assert batch.report["filtered_query_stock_absent_count"] == 1


def test_live_news_quality_audit_ignores_sbs_copyright_footer_as_stock_match() -> None:
    alert = RawCollectedAlert(
        source_type="NEWS",
        title="오늘도 롤러코스피 등락 거듭 끝 8000선 지켜",
        snippet="증시 흐름을 SBS Biz 기자가 전했다.",
        original_url="https://biz.sbs.co.kr/article/20000320880",
        published_at="Mon, 06 Jul 2026 15:25:00 +0900",
        provider="naver-news",
    )
    full_content = ArticleContent(
        content=(
            "코스피는 외국인 순매도와 반도체 대형주 등락 속에 8000선을 지켰다. "
            "투자자는 환율과 외국인 수급을 확인해야 한다. "
            "ⓒ SBS Medianet & SBSi 무단복제-재배포 금지."
        ),
        canonical_url=alert.original_url,
        image_urls=[],
        source_license_policy="licensed_naver_original_full_text_v1",
    )

    assert not _stock_text_matched(alert, "SBS", full_content=full_content)


def test_live_news_quality_audit_ignores_sbs_broadcaster_source_context() -> None:
    program_alert = RawCollectedAlert(
        source_type="NEWS",
        title="한탑, 창업주 복귀 논란에 지배구조 리스크 부각",
        snippet="2013년 SBS 그것이 알고싶다 방송 보도로 사건이 재조명됐다.",
        original_url="https://example.com/hantop-governance",
        published_at="Mon, 06 Jul 2026 15:25:00 +0900",
        provider="naver-news",
    )
    source_alert = RawCollectedAlert(
        source_type="NEWS",
        title="여고생 살해범 수사 지휘권 박탈",
        snippet="6일 SBS에 따르면 경찰 수사 지휘 라인이 배제될 전망이다.",
        original_url="https://example.com/sbs-source",
        published_at="Mon, 06 Jul 2026 15:26:00 +0900",
        provider="naver-news",
    )

    assert not _stock_text_matched(program_alert, "SBS")
    assert not _stock_text_matched(source_alert, "SBS")


def test_live_news_quality_audit_ignores_short_stock_technical_acronym_context() -> None:
    alert = RawCollectedAlert(
        source_type="NEWS",
        title="삼성전자 엑시노스 적용 범위 확대",
        snippet=(
            "AP와 D램을 나란히 수평 배치하는 사이드 바이 사이드(SBS) 구조를 도입해 "
            "반도체 실적 개선을 추진한다."
        ),
        original_url="https://example.com/samsung-exynos-side-by-side",
        published_at="Mon, 06 Jul 2026 15:26:00 +0900",
        provider="naver-news",
    )

    assert not _stock_text_matched(alert, "SBS")


def test_full_content_builder_follows_amphtml_when_desktop_page_is_shell(monkeypatch) -> None:
    module = _load_full_content_script()
    desktop_url = "https://biz.sbs.co.kr/article/20000320880"
    amp_page = """
    <html>
      <head><link rel="canonical" href="https://biz.sbs.co.kr/article/20000320880"></head>
          <body>
            <main class="article_content_w">
              <p>지난주 급격한 등락을 보였던 코스피가 오늘도 장중 크게 출렁였다.</p>
              <p>급등과 급락을 오가던 코스피는 전장보다 소폭 하락해 8000선을 지켰다.</p>
              <p>투자자는 외국인 수급과 환율 변동성, 대형주 실적 발표를 함께 확인해야 한다.</p>
              <p>장중 대형주 매매가 반복되며 투자 심리가 흔들렸고,
              원화 흐름도 지수 변동성에 영향을 줬다.</p>
              <p>시장 참가자는 다음 거래일 수급 전환과 반도체 업종의
              실적 가이던스를 점검하고 있다.</p>
            </main>
          </body>
    </html>
    """.encode()
    desktop_page = b"""
    <html>
      <head>
        <link rel="amphtml" href="/amp/article/20000320880">
        <meta property="og:image" content="https://img.biz.sbs.co.kr/upload/news.jpg">
      </head>
      <body><div id="app-cnbc-front"></div></body>
    </html>
    """

    def fake_fetch_bytes(url: str) -> bytes:
        if url == desktop_url:
            return desktop_page
        if url == "https://biz.sbs.co.kr/amp/article/20000320880":
            return amp_page
        raise AssertionError(url)

    monkeypatch.setattr(module, "fetch_bytes", fake_fetch_bytes)

    full_content = module.fetch_news_content(desktop_url, expected_title="롤러코스피")

    assert full_content is not None
    assert "코스피가 오늘도 장중 크게 출렁였다" in full_content.content
    assert full_content.canonical_url == desktop_url
    assert full_content.image_urls == ["https://img.biz.sbs.co.kr/upload/news.jpg"]


def test_full_content_builder_retries_transient_article_fetch(monkeypatch) -> None:
    module = _load_full_content_script()
    url = "https://www.pinpointnews.co.kr/news/articleView.html?idxno=463947"
    call_count = 0
    html = """
    <html>
      <head>
        <meta property="og:image" content="https://img.example.com/battery.jpg">
      </head>
      <body>
        <section class="article-body" itemProp="articleBody">
          <p>폐배터리 관련주가 전기차 보급 확대 기대에 강세를 보였다.</p>
          <p>새빗켐은 폐배터리에서 리튬과 희소금속을 회수하는 기술력이 부각됐다.</p>
          <p>성일하이텍과 에코프로도 배터리 재활용 시장 성장 기대를 받았다.</p>
          <p>투자자는 테마 급등 이후 실적 개선과 신규 수주 지속성을 확인해야 한다.</p>
          <p>글로벌 완성차 업체의 폐배터리 회수 전략과 원재료 내재화 흐름도
          관련 기업의 중장기 매출 기대를 키우는 요인으로 거론됐다.</p>
          <p>단기간 주가가 급등한 만큼 실제 설비 가동률, 수익성, 고객사 확보 여부가
          후속 투자 판단의 핵심 변수로 꼽힌다.</p>
        </section>
      </body>
    </html>
    """.encode()

    def fake_fetch_bytes(fetch_url: str) -> bytes:
        nonlocal call_count
        assert fetch_url == url
        call_count += 1
        if call_count == 1:
            raise TimeoutError("read timed out")
        return html

    monkeypatch.setattr(module, "fetch_bytes", fake_fetch_bytes)
    monkeypatch.setattr(module.time, "sleep", lambda _: None)

    full_content = module.fetch_news_content(url, expected_title="배터리 재활용 시대")

    assert full_content is not None
    assert call_count == 2
    assert "새빗켐은 폐배터리" in full_content.content
    assert full_content.image_urls == ["https://img.example.com/battery.jpg"]


def test_full_content_builder_reuses_existing_licensed_rows() -> None:
    module = _load_full_content_script()

    assert module.is_reusable_full_content_policy("licensed_naver_original_full_text_v1")
    assert module.is_reusable_full_content_policy("opendart_public_disclosure_text_v1")
    assert module.is_reusable_full_content_policy("internal_rights_safe_full_article_v1")
    assert not module.is_reusable_full_content_policy("NAVER_SEARCH_SNIPPET_ONLY")


def test_full_content_builder_stops_at_target_row_count() -> None:
    module = _load_full_content_script()

    assert module.target_reached({"a": {}, "b": {}}, 2)
    assert not module.target_reached({"a": {}}, 2)
    assert not module.target_reached({"a": {}, "b": {}}, 0)


def test_full_content_builder_tracks_disclosure_target_separately() -> None:
    module = _load_full_content_script()
    rows = {
        "news": {"source_type": "NEWS"},
        "disclosure": {"source_type": "DISCLOSURE"},
    }

    assert module.disclosure_target_reached(rows, 1)
    assert not module.disclosure_target_reached(rows, 2)
    assert not module.disclosure_target_reached(rows, 0)


def test_full_content_builder_rejects_truncated_dart_zip(monkeypatch) -> None:
    module = _load_full_content_script()
    monkeypatch.setattr(module, "fetch_bytes", lambda *_args, **_kwargs: b"PKbroken")

    assert module.fetch_dart_document("local-key", "20260617000001") == ""
