from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine


def test_summary_ignores_news_site_navigation_noise() -> None:
    engine = FinancialRuleEngine()
    content = (
        "SK하이닉스, 삼성전자 시총 맹추격 로그인 회원가입 전체 메뉴 열기 검색 열기 "
        "머니 증권 은행 보험 카드 부동산 경제일반 산업 재계 자동차 전기전자. "
        "22일 한국거래소에 따르면 이날 오전 11시 기준 SK하이닉스의 주가는 "
        "전 거래일 대비 4.59% 상승한 289만1000원에 거래되고 있다. "
        "이는 연초 대비 삼성전자는 195.25% 오른 반면 SK하이닉스는 324.58% "
        "급등한 영향이다. "
        "시장에서는 HBM 수요와 반도체 업황 개선이 시가총액 격차를 좁히는 "
        "핵심 배경으로 거론된다. "
        "오늘의 NEWS STAND 30대 교사 부부 대박 주식 이야기와 소름 돋는 폭탄 발언."
    )

    summary = engine.summarize_what_why_impact(
        "SK하이닉스, 삼성전자 시총 맹추격",
        "",
        content,
        "HIGH",
        "POSITIVE",
    )

    assert "로그인" not in summary.what
    assert "전체 메뉴" not in summary.what
    assert "NEWS STAND" not in summary.impact
    assert "SK하이닉스" in summary.what
    assert "급등" in summary.why or "HBM" in summary.why
    assert "사용자" in summary.impact or "시장" in summary.impact


def test_clean_article_text_keeps_financial_sentences_in_original_order() -> None:
    engine = FinancialRuleEngine()
    content = (
        "본문 바로가기 로그인 회원가입 전체 메뉴 열기 검색 열기. "
        "삼성전자는 AI 서버 투자 확대로 반도체 실적 개선 기대가 커졌다. "
        "메모리 가격 반등과 HBM 공급 확대가 주요 배경이다. "
        "투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다. "
        "이용약관 개인정보 처리방침 저작권 안내."
    )

    cleaned = engine.clean_article_text(content, "삼성전자 실적 개선")

    assert "본문 바로가기" not in cleaned
    assert "이용약관" not in cleaned
    assert cleaned.index("삼성전자는") < cleaned.index("메모리 가격")
    assert "영업이익" in cleaned


def test_clean_article_text_removes_market_widget_tail() -> None:
    engine = FinancialRuleEngine()
    content = (
        "한화에어로스페이스는 중동 방산 수요 확대에 따라 수주 기회가 늘고 있다. "
        "유럽 안보 협력 균열과 국방 예산 증액이 주요 배경으로 거론된다. "
        "투자자는 수주 잔고와 영업이익 기여 시점을 확인해야 한다. "
        "최신 영상 오늘의 증시일정 뉴로메카 카카오게임즈 동양 등 "
        "마켓 최신 뉴스 특징주 제주반도체 반도체 수출 호조 속 급등."
    )

    cleaned = engine.clean_article_text(content, "한화에어로스페이스 방산 수주 확대")

    assert "중동 방산 수요" in cleaned
    assert "최신 영상" not in cleaned
    assert "오늘의 증시일정" not in cleaned
    assert "마켓 최신 뉴스" not in cleaned


def test_summary_prefers_title_context_over_unrelated_market_tail() -> None:
    engine = FinancialRuleEngine()
    content = (
        "감마누는 대규모 자금조달을 추진하며 재무구조 개선 기대가 커졌다. "
        "이번 자금조달은 운영자금 확보와 상장 유지 리스크 완화가 주요 배경이다. "
        "투자자는 신주 발행 조건과 기존 주주 지분 희석 가능성을 확인해야 한다. "
        "배터리·우주항공·희토류·수소 등 미래 산업 금융주는 상반기 순익이 늘었다. "
        "오늘의 증시일정 뉴로메카 카카오게임즈 동양 등 최신 영상."
    )

    summary = engine.summarize_what_why_impact(
        "[되살아난 감마누] 대규모 자금조달 성공할까",
        "",
        content,
        "HIGH",
        "NEUTRAL",
    )

    joined = " ".join([summary.what, summary.why, summary.impact])
    assert "감마누" in joined
    assert "자금조달" in joined
    assert "상반기 순익" not in joined
    assert "오늘의 증시일정" not in joined


def test_summary_uses_snippet_context_for_roundup_disclosure_title() -> None:
    engine = FinancialRuleEngine()
    content = (
        "삼성전자는 14조5800억원 규모 자사주 소각을 결정했다. "
        "레드우즈는 상장폐지 사유 발생으로 주권 매매거래정지 기간이 변경됐다. "
        "투자자는 정리매매 가능성과 거래정지 해제 조건을 확인해야 한다."
    )

    summary = engine.summarize_what_why_impact(
        "[오늘의 주요공시·31일] 삼성전자, 14조5800억 자사주 소각",
        "레드우즈 주권 매매거래정지 기간 변경 및 상장폐지 사유 발생",
        content,
        "CRITICAL",
        "NEGATIVE",
    )

    joined = " ".join([summary.what, summary.why, summary.impact])
    assert "레드우즈" in summary.what
    assert "상장폐지" in joined or "거래정지" in joined
    assert "오늘의 주요공시" not in joined


def test_summary_uses_distinct_article_lines_before_fallback() -> None:
    engine = FinancialRuleEngine()
    content = (
        "신한투자증권은 신한 SOL증권 이용 고객을 대상으로 하반기 증시 전망 "
        "설문조사 결과를 발표했다고 밝혔다. "
        "응답자 다수는 고위험·고수익 투자 상품 선호가 커졌다고 답했다. "
        "증권사는 시장 변동성 확대에 따라 투자자별 위험 관리가 중요하다고 설명했다."
    )

    summary = engine.summarize_what_why_impact(
        "신한투자증권, 증시 전망 설문 결과 발표",
        "",
        content,
        "HIGH",
        "POSITIVE",
    )

    lines = {summary.what, summary.why, summary.impact}
    assert len(lines) == 3
    assert "설문조사" in summary.what
    assert any("고위험" in line for line in lines)
    assert any("시장 변동성" in line or "투자자" in line for line in lines)


def test_summary_removes_ad_and_related_article_tail() -> None:
    engine = FinancialRuleEngine()
    content = (
        "파이낸셜뉴스 광고 구독하기 공유하기 글자크기 설정. "
        "삼성전자는 AI 서버 투자 확대로 HBM과 메모리 수요가 늘며 반도체 실적 회복 기대가 커졌다. "
        "메모리 가격 반등과 주요 고객사의 데이터센터 투자가 이번 회복의 배경으로 거론된다. "
        "투자자는 영업이익 회복 속도와 고부가 제품 비중 확대 여부를 확인해야 한다. "
        "관련기사 인텔의 반격 파운드리 삼국 시대 최신 기사 오늘의 주요공시."
    )

    summary = engine.summarize_what_why_impact(
        "삼성전자, AI 서버 투자 확대에 반도체 실적 회복 기대",
        "",
        content,
        "HIGH",
        "POSITIVE",
    )

    joined = " ".join([summary.what, summary.why, summary.impact])
    assert "광고" not in joined
    assert "관련기사" not in joined
    assert "최신 기사" not in joined
    assert "삼성전자" in joined
    assert "영업이익" in joined or "메모리 가격" in joined


def test_summary_ignores_related_story_bracket_cluster() -> None:
    engine = FinancialRuleEngine()
    content = (
        "SK하이닉스는 AI 인프라 투자 확대의 최대 수혜 기업으로 평가받으며 "
        "시가총액 1위에 올라섰다. "
        "HBM 공급 우위와 메모리 반도체 수요 증가가 주가 상승의 핵심 배경이다. "
        "투자자는 메모리 가격과 영업이익 전망 변화를 확인해야 한다. "
        "[CEO 위클리] 르망과 바티칸 그리고 데이터센터 "
        "[비즈 인사이트] 삼성은 삼성전자그룹 SK는 하이닉스그룹 "
        "[게임 앤 플랫폼] 신작만으론 부족하다 검찰 압수수색했다는데 왜?"
    )

    summary = engine.summarize_what_why_impact(
        "SK하이닉스, 시총 1위 등극",
        "",
        content,
        "HIGH",
        "POSITIVE",
    )

    joined = " ".join([summary.what, summary.why, summary.impact])
    assert "CEO 위클리" not in joined
    assert "게임 앤 플랫폼" not in joined
    assert "압수수색" not in joined
    assert "HBM" in joined or "메모리" in joined


def test_summary_only_response_caps_model_confidence() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
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
    assert response.event_confidence <= 0.55
    assert response.sentiment_confidence <= 0.55
    assert response.importance_confidence <= 0.55


def test_analyzer_prefers_first_internal_stock_over_limited_request_universe() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="NH-Amundi운용, 반도체 ETF 리밸런싱...SK스퀘어 신규 편입",
            snippet="SK하이닉스와 삼성전자 등 반도체 종목을 담는 ETF가 정기 리밸런싱을 마쳤다.",
            content=(
                "NH-Amundi자산운용은 국내 반도체 산업을 대표하는 ETF에 SK스퀘어를 "
                "신규 편입했다고 밝혔다. SK하이닉스 주가 상승과 HBM 수요 확대가 "
                "반도체 투자 심리를 끌어올리고 있다."
            ),
            original_url="https://news.example.com/article",
            stock_universe=[
                StockCandidate(
                    stock_code="000660",
                    stock_name="SK하이닉스",
                    stock_name_en="SK hynix",
                )
            ],
        )
    )

    assert response.stock_code == "402340"
    assert response.stock_name == "SK스퀘어"


def test_analyzer_allows_short_requested_stock_name() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="세동, 정기주총서 정관 변경·사외이사 선임안 가결",
            snippet="세동은 주주총회에서 사외이사 선임안을 의결했다.",
            original_url="https://news.example.com/saedong",
            stock_universe=[
                StockCandidate(
                    stock_code="053060",
                    stock_name="세동",
                    stock_name_en="Saedong",
                )
            ],
        )
    )

    assert response.stock_code == "053060"
    assert response.stock_name == "세동"


def test_analyzer_ignores_short_english_internal_stock_noise() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="전국 바이오 데이터센터 구축 본격화…new growth 기대",
            snippet="AI 데이터센터와 바이오 연구 인프라 투자 확대가 이어지고 있다.",
            original_url="https://news.example.com/ai-bio",
        )
    )

    assert response.stock_code != "160550"


def test_analyzer_does_not_match_legacy_bank_entity_as_listed_stock() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="환율 변동 대응력 키운다…하나은행, 수출입 아카데미",
            snippet="수출입 기업 실무자를 대상으로 환율 교육을 진행한다.",
            original_url="https://news.example.com/hana-bank-academy",
        )
    )

    assert response.stock_code is None
    assert "002860" not in response.related_stocks
    assert "004940" not in response.related_stocks


def test_news_analysis_does_not_emit_disclosure_tag() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="HLB제약, 1200억 유상증자 결정 공시",
            snippet="신공장 건설과 연구소 확대에 자금을 투입한다.",
            original_url="https://news.example.com/hlb-capital-action",
            stock_universe=[
                StockCandidate(
                    stock_code="047920",
                    stock_name="HLB제약",
                    stock_name_en="HLB Pharmaceutical",
                )
            ],
        )
    )

    assert "CAPITAL_ACTION" in response.event_tags
    assert "DISCLOSURE" not in response.event_tags
