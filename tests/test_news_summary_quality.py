from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine


def test_disclosure_importance_follows_v3_codebook() -> None:
    engine = FinancialRuleEngine()

    assert engine.classify_importance("회생절차개시신청", "DISCLOSURE") == "CRITICAL"
    assert engine.classify_importance("출자법인 부도발생", "DISCLOSURE") == "CRITICAL"
    assert engine.classify_importance("채권자 파산신청", "DISCLOSURE") == "CRITICAL"
    assert engine.classify_importance("불성실공시법인 지정 예고", "DISCLOSURE") == "HIGH"
    assert engine.classify_importance("주권매매거래정지", "DISCLOSURE") == "HIGH"


def test_disclosure_event_tags_follow_v3_codebook() -> None:
    analyzer = AlertAnalyzer()

    assert analyzer._augment_event_tags(
        "매출액또는손익구조30%이상변동",
        "DISCLOSURE",
        ["RISK"],
    ) == ["DISCLOSURE", "EARNINGS"]
    assert analyzer._augment_event_tags(
        "주권매매거래정지 (주식의 병합, 분할 등 전자등록 변경)",
        "DISCLOSURE",
        ["GENERAL_MARKET"],
    ) == ["DISCLOSURE", "RISK"]


def test_stock_name_containing_research_is_not_treated_as_attribution() -> None:
    analyzer = AlertAnalyzer()
    stock = StockCandidate(
        stock_code="359090",
        stock_name="씨엔알리서치",
        stock_name_en="C&R Research",
    )

    match = analyzer._match_primary_stock_from_request_or_internal(
        "씨엔알리서치 주권매매거래정지",
        "씨엔알리서치 주권매매거래정지",
        [stock],
    )

    assert match.stock == stock


def test_clean_article_text_keeps_financial_sentences_and_removes_navigation() -> None:
    engine = FinancialRuleEngine()
    content = (
        "본문 바로가기 로그인 회원가입 전체 메뉴 열기 검색 열기. "
        "삼성전자는 AI 서버 투자 확대로 반도체 실적 개선 기대가 커졌다. "
        "메모리 가격 반등과 HBM 공급 확대가 주요 배경이다. "
        "투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다."
    )

    cleaned = engine.clean_article_text(content, "삼성전자 반도체 실적 개선")

    assert "본문 바로가기" not in cleaned
    assert cleaned.startswith("삼성전자는")
    assert cleaned.index("메모리 가격") < cleaned.index("투자자는")


def test_summary_only_response_caps_model_confidence() -> None:
    response = AlertAnalyzer().analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="SK하이닉스, 삼성전자 제치고 시총 1위 등극",
            snippet="HBM 수요와 반도체 수출 호조가 주가 상승 배경으로 꼽힌다.",
            original_url="https://news.example.com/summary-only",
            stock_universe=[
                StockCandidate(
                    stock_code="000660",
                    stock_name="SK하이닉스",
                    stock_name_en="SK hynix",
                )
            ],
        )
    )

    assert response.content_availability == "SUMMARY_ONLY"
    assert response.event_confidence <= 0.34
    assert response.sentiment_confidence <= 0.34
    assert response.importance_confidence <= 0.34


def test_market_wide_news_does_not_force_primary_stock_from_internal_mentions() -> None:
    response = AlertAnalyzer().analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="한국 증시, 인도 제치고 시총 세계 6위 등극",
            snippet="삼성전자와 SK하이닉스가 코스피 상승을 이끌었다.",
            content=(
                "한국 주식시장 시가총액이 인도를 추월하며 세계 6위로 올라섰다. "
                "인공지능 메모리 반도체 랠리에 올라탄 삼성전자와 SK하이닉스가 "
                "코스피 상승을 이끌었다."
            ),
            original_url="https://news.example.com/korea-market-cap",
        )
    )

    assert response.stock_code is None
    assert response.stock_name is None
    assert "GENERAL_MARKET" in response.event_tags
    assert {"005930", "000660"}.issubset(set(response.related_stocks))
    assert response.summary_lines.what
    assert response.summary_lines.why
    assert response.summary_lines.impact
