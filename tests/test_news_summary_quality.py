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


def test_market_summary_prefers_lead_index_recovery_over_later_index_tail() -> None:
    engine = FinancialRuleEngine()
    content = (
        "코스피가 3일 장중 기관의 대규모 매수세에 힘입어 상승 전환하며 7800선을 회복했다. "
        "장 초반 미국 기술주 약세 영향으로 밀렸지만 반도체주를 중심으로 기관 자금이 "
        "유입되면서 분위기가 반전됐다. "
        "유가증권시장에서 기관은 1조3941억원을 순매수하며 지수 반등을 이끌었다. "
        "반면 외국인은 1조3941억원을 순매도했고 개인도 5896억원어치를 순매도했다. "
        "코스닥지수는 코스피와 다른 흐름을 보이며 전 거래일보다 22.23포인트 내렸다. "
        "시가총액 상위 종목 가운데 알테오젠과 에코프로비엠 등은 하락세다."
    )

    summary = engine.summarize_what_why_impact(
        "코스피, 기관 매수세에 장중 7800선 회복",
        "",
        content,
        "MEDIUM",
        "POSITIVE",
    )

    assert "코스피가 3일 장중 기관" in summary.what
    assert "기관 자금" in summary.why or "기관은 1조3941억원" in summary.why
    assert "positive" not in summary.impact.lower()
    assert "중요도" not in summary.impact


def test_market_wide_mixed_index_article_is_neutral() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="코스피, 기관 매수세에 장중 7800선 회복",
            snippet="반도체주를 중심으로 기관 자금이 유입되며 지수가 반등했다.",
            content=(
                "코스피가 3일 장중 기관의 대규모 매수세에 힘입어 상승 전환하며 "
                "7800선을 회복했다. "
                "장 초반 미국 기술주 약세 영향으로 밀렸지만 반도체주를 중심으로 "
                "기관 자금이 유입되면서 분위기가 반전됐다. "
                "유가증권시장에서 기관은 1조3941억원을 순매수하며 지수 반등을 이끌었다. "
                "반면 외국인은 1조3941억원을 순매도했고 개인도 5896억원어치를 순매도했다. "
                "코스닥지수는 코스피와 다른 흐름을 보이며 전 거래일보다 22.23포인트 내렸다."
            ),
            original_url="https://news.example.com/market-recovery",
        )
    )

    assert response.sentiment == "NEUTRAL"
    assert response.stock_code is None
    assert "코스피가 3일 장중 기관" in response.summary_lines.what


def test_summary_fallback_impact_does_not_expose_model_labels() -> None:
    engine = FinancialRuleEngine()
    summary = engine.summarize_what_why_impact(
        "반도체 수요 둔화 우려 확산",
        "AI 투자 속도 조절 가능성이 제기됐다.",
        "반도체 수요 둔화 우려가 다시 제기됐다. AI 투자 속도 조절 가능성이 배경이다.",
        "MEDIUM",
        "NEGATIVE",
    )

    assert "negative" not in summary.impact.lower()
    assert "medium" not in summary.impact.lower()
    assert "감성" not in summary.impact
    assert "중요도" not in summary.impact


def test_summary_rejects_snippet_ellipsis_lines() -> None:
    engine = FinancialRuleEngine()
    summary = engine.summarize_what_why_impact(
        "삼성전자 실적 개선 기대",
        "반도체 수요 회복으로 영업이익 전망이 상향...",
        "",
        "MEDIUM",
        "POSITIVE",
    )

    lines = [summary.what, summary.why, summary.impact]
    assert all("..." not in line and "…" not in line for line in lines)
    assert all(line.strip() for line in lines)


def test_full_content_summary_beats_snippet_only_ellipsis() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="삼성전자 실적 개선 기대",
            snippet="반도체 수요 회복으로 영업이익 전망이 상향...",
            content=(
                "삼성전자는 AI 서버 투자 확대로 HBM과 메모리 수요가 늘며 "
                "반도체 실적 회복 기대가 커졌다. "
                "메모리 가격 반등과 주요 고객사의 데이터센터 투자가 이번 회복의 "
                "핵심 배경으로 거론된다. "
                "투자자는 영업이익 회복 속도와 고부가 제품 비중 확대 여부를 확인해야 한다."
            ),
            original_url="https://news.example.com/full-content-summary",
            stock_universe=[
                StockCandidate(
                    stock_code="005930",
                    stock_name="삼성전자",
                    stock_name_en="Samsung Electronics",
                )
            ],
        )
    )

    joined = " ".join(
        [
            response.summary_lines.what,
            response.summary_lines.why,
            response.summary_lines.impact,
        ]
    )
    assert response.content_availability == "FULL_TEXT"
    assert "..." not in joined
    assert "HBM" in joined
    assert "데이터센터" in joined
    assert "영업이익 회복 속도" in joined


def test_summary_truncates_only_on_sentence_boundary() -> None:
    engine = FinancialRuleEngine()
    long_context = "삼성전자는 " + "반도체 수요 회복과 HBM 공급 확대를 " * 9
    content = (
        f"{long_context}바탕으로 영업이익 개선 기대가 커졌다고 밝혔다."
        f"다만 {'세부 사업부별 수익성 확인이 필요하다는 설명이 이어졌다' * 4}. "
        "메모리 가격 반등과 데이터센터 투자가 핵심 배경이다. "
        "투자자는 영업이익 회복 속도와 고부가 제품 비중을 확인해야 한다."
    )

    summary = engine.summarize_what_why_impact(
        "삼성전자 반도체 실적 개선 기대",
        "",
        content,
        "HIGH",
        "POSITIVE",
    )

    assert len(summary.what) < 300
    assert summary.what.endswith("밝혔다.")
    assert not summary.what.endswith("확대")


def test_impact_rejects_classification_meta_sentence() -> None:
    engine = FinancialRuleEngine()
    summary = engine.summarize_what_why_impact(
        "삼성전자 실적 개선",
        "",
        (
            "삼성전자는 AI 서버 투자 확대로 반도체 실적 개선 기대가 커졌다. "
            "메모리 가격 반등과 HBM 공급 확대가 주요 배경이다. "
            "The impact is classified as high importance and positive sentiment. "
            "투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다."
        ),
        "HIGH",
        "POSITIVE",
    )

    assert "classified" not in summary.impact.lower()
    assert "importance" not in summary.impact.lower()
    assert "sentiment" not in summary.impact.lower()
    assert "투자자는 영업이익" in summary.impact


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


def test_market_wide_news_does_not_force_primary_stock_from_internal_mentions() -> None:
    analyzer = AlertAnalyzer()
    response = analyzer.analyze(
        AlertAnalysisRequest(
            source_type="NEWS",
            title="한국 증시, 인도 제치고 시총 세계 6위 등극",
            snippet="삼성전자와 SK하이닉스가 코스피 상승을 이끌었다.",
            content=(
                "한국 주식시장 시가총액이 인도를 추월하며 세계 6위로 올라섰다. "
                "인공지능 메모리 반도체 랠리에 올라탄 삼성전자와 SK하이닉스가 "
                "코스피 상승을 이끌었다. "
                "시장에서는 반도체 대형주 쏠림과 지수 상승 지속성을 함께 점검해야 "
                "한다는 평가가 나온다."
            ),
            original_url="https://news.example.com/korea-market-cap",
        )
    )

    assert response.stock_code is None
    assert response.stock_name is None
    assert "GENERAL_MARKET" in response.event_tags
    assert {"005930", "000660"}.issubset(set(response.related_stocks))
    assert "시장에서는 반도체 대형주 쏠림" in response.summary_lines.impact


def test_disclosure_summary_separates_reason_from_investor_impact() -> None:
    engine = FinancialRuleEngine()
    summary = engine.summarize_what_why_impact(
        "삼성전자, 14조5800억원 규모 자사주 소각 결정",
        "주주가치 제고를 위해 보유 자기주식 일부를 소각한다고 공시했다.",
        (
            "삼성전자는 주주가치 제고를 위해 14조5800억원 규모의 자기주식을 "
            "소각하기로 결정했다고 공시했다. "
            "이번 결정은 발행주식 수 감소와 주주환원 정책 강화 목적이다. "
            "회사는 이사회 결의 후 관련 절차에 따라 소각을 진행할 예정이다. "
            "투자자는 실제 소각 일정과 향후 배당 정책 변화를 확인해야 한다."
        ),
        "HIGH",
        "POSITIVE",
    )

    assert "주주환원 정책 강화 목적" in summary.why
    assert "투자자는 실제 소각 일정" in summary.impact
