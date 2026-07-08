from pathlib import Path

import pytest

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate, SummaryLines
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model import ModelArtifactNotFoundError
from hannah_montana_ai.services.news_summary_generator import (
    MlxQwenNewsSummaryClient,
    NewsSummaryContext,
    NewsSummaryGenerator,
    OpenAiCompatibleNewsSummaryClient,
)


class FakeNewsSummaryClient:
    def __init__(self, raw_output: str) -> None:
        self.raw_output = raw_output
        self.messages: list[dict[str, str]] = []

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        self.messages = messages
        return self.raw_output


class CapturingNewsSummaryGenerator(NewsSummaryGenerator):
    def __init__(self, summary: SummaryLines) -> None:
        super().__init__()
        self.summary = summary
        self.context: NewsSummaryContext | None = None

    def generate(self, context: NewsSummaryContext) -> SummaryLines:
        self.context = context
        return self.summary


def test_news_summary_local_llm_settings_without_endpoint_use_direct_qwen3_mlx_client() -> None:
    settings = Settings(
        news_summary_generation_mode="local_llm",
        news_summary_llm_endpoint="",
        news_summary_mlx_model="mlx-community/Qwen3-0.6B-4bit",
        news_summary_mlx_adapter_path=Path(
            "src/hannah_montana_ai/model_store/news_summary_qwen3_lora"
        ),
    )

    generator = NewsSummaryGenerator.from_settings(settings)

    assert generator._enabled is True
    assert isinstance(generator._client, MlxQwenNewsSummaryClient)
    assert generator._model_name == "mlx-community/Qwen3-0.6B-4bit"


def test_news_summary_local_llm_requires_trained_adapter(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactNotFoundError):
        NewsSummaryGenerator.from_settings(
            Settings(
                news_summary_generation_mode="local_llm",
                news_summary_llm_endpoint="",
                news_summary_mlx_adapter_path=tmp_path / "missing-summary-lora",
            )
        )


def test_news_summary_local_llm_settings_with_endpoint_use_openai_compatible_client() -> None:
    settings = Settings(
        news_summary_generation_mode="local_llm",
        news_summary_llm_endpoint="http://127.0.0.1:8089",
        news_summary_llm_model="Qwen3-0.6B-GGUF-Q4",
    )

    generator = NewsSummaryGenerator.from_settings(settings)

    assert generator._enabled is True
    assert isinstance(generator._client, OpenAiCompatibleNewsSummaryClient)
    assert generator._model_name == "Qwen3-0.6B-GGUF-Q4"


def test_news_summary_qwen_output_replaces_rule_fallback_for_full_text() -> None:
    fallback = SummaryLines(
        what="삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다.",
        why="메모리 가격 반등과 HBM 공급 확대가 주요 배경이다.",
        impact="투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다.",
    )
    context = _sample_context(fallback=fallback)
    client = FakeNewsSummaryClient(
        '{"what":"Samsung Electronics said AI-server investment is lifting '
        'semiconductor earnings expectations.",'
        '"why":"The article cites stronger HBM demand and a rebound in memory '
        'prices as the main drivers.",'
        '"impact":"The investor impact is to track operating-profit recovery '
        'speed and the mix of high-value memory products."}'
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=client,
    )

    summary = generator.generate(context)

    assert summary != fallback
    assert summary.what.startswith("Samsung Electronics")
    assert "HBM" in summary.why
    assert "operating-profit recovery" in summary.impact
    assert "article_text" in client.messages[1]["content"]


def test_news_summary_rule_mode_returns_english_fallback() -> None:
    fallback = SummaryLines(
        what="삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다.",
        why="메모리 가격 반등과 HBM 공급 확대가 주요 배경이다.",
        impact="투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다.",
    )
    generator = NewsSummaryGenerator(enabled=False)

    summary = generator.generate(_sample_context(fallback=fallback))

    assert summary != fallback
    assert "Samsung Electronics" in summary.what
    assert "HBM" in summary.why
    assert "Investors should track" in summary.impact
    assert not _has_korean(summary)


def test_news_summary_rule_mode_handles_korean_market_plunge_context() -> None:
    context = NewsSummaryContext(
        title="KOSPI 5% plunge... KOSDAQ breaks below 800",
        snippet="반도체 고점 논란과 중동 지정학 리스크로 매도 사이드카가 발동됐다.",
        content=(
            "코스피가 8일 5% 넘게 급락하며 7200선까지 밀려났다. "
            "코스피와 코스닥 모두 프로그램 매도 호가 효력을 정지하는 매도 사이드카가 발동됐다. "
            "반도체 투자심리 위축과 중동 지정학적 긴장 고조가 겹치면서 국내 증시 변동성이 커졌다. "
            "코스닥도 46.23포인트(5.56%) 내린 785.00에 마감하며 800선이 붕괴됐다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code="000660",
        stock_name="SK하이닉스",
        stock_name_en="SK hynix",
        fallback=SummaryLines(
            what="코스피와 코스닥이 급락했다.",
            why="반도체 투자심리와 중동 리스크가 부담이다.",
            impact="투자자는 수급과 변동성을 확인해야 한다.",
        ),
    )
    generator = NewsSummaryGenerator(enabled=False)

    summary = generator.generate(context)
    joined = " ".join((summary.what, summary.why, summary.impact))

    assert "KOSPI and KOSDAQ sold off sharply" in summary.what
    assert "sell-side circuit breakers" in summary.what
    assert "semiconductor weakness" in summary.why
    assert "Middle East risk" in summary.why
    assert "46." not in joined
    assert "785." not in joined
    assert not _has_korean(summary)


def test_news_summary_rule_mode_expands_single_market_plunge_driver() -> None:
    context = NewsSummaryContext(
        title="KOSPI and KOSDAQ plunge as sidecars triggered",
        snippet="코스피와 코스닥이 5%대 급락했고 코스닥은 800선 아래로 내려갔다.",
        content=(
            "반도체 수출 호조에 힘입어 5월 우리나라 경상수지가 역대 최대 흑자를 기록했다. "
            "코스피와 코스닥 모두 프로그램 매도 호가 효력을 정지하는 매도 사이드카가 발동됐다. "
            "코스피와 코스닥은 5%대 급락하며 마감했고 코스닥은 800선 아래로 떨어졌다. "
            "SK하이닉스의 ADR 상장이 국내 투자 심리 회복으로 이어질 거란 기대와 "
            "외국인 투자자의 이탈을 가속화할 수 있단 우려도 나왔다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code="000660",
        stock_name="SK하이닉스",
        stock_name_en="SK hynix",
        fallback=SummaryLines(
            what="코스피와 코스닥이 급락했다.",
            why="반도체 투자심리가 부담이다.",
            impact="투자자는 수급을 확인해야 한다.",
        ),
    )
    generator = NewsSummaryGenerator(enabled=False)

    summary = generator.generate(context)

    assert summary.why != "The article cites semiconductor weakness."
    assert "semiconductor weakness" in summary.why
    assert "sell-side program selling pressure" in summary.why
    assert "SK hynix ADR demand" in summary.impact
    assert not _has_korean(summary)


def test_news_summary_qwen_output_falls_back_to_source_lines_on_korean_fragment_or_meta() -> None:
    fallback = SummaryLines(
        what="삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다.",
        why="메모리 가격 반등과 HBM 공급 확대가 주요 배경이다.",
        impact="투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다.",
    )
    context = _sample_context(fallback=fallback)
    client = FakeNewsSummaryClient(
        '{"what":"삼성전자는 AI 서버 투자 확대로 실적 개선 기대가 커졌다.",'
        '"why":"The reason is classified as high importance and positive sentiment.",'
        '"impact":"Investors should track operating profit..."}'
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=client,
    )

    summary = generator.generate(context)

    assert summary != fallback
    assert "Samsung Electronics" in summary.what
    assert "semiconductor" in summary.what
    assert "HBM" in summary.why
    assert "Investors should track" in summary.impact
    assert not _has_korean(summary)


def test_news_summary_qwen_output_rejects_fragmentary_market_lines() -> None:
    fallback = SummaryLines(
        what="코스피는 장중 급락 후 7,200선에서 마감했다.",
        why="반도체주 조정과 중동 지정학 리스크가 투자심리를 압박했다.",
        impact="투자자는 외국인 수급과 반도체 대형주 변동성을 확인해야 한다.",
    )
    context = _sample_context(fallback=fallback)
    client = FakeNewsSummaryClient(
        '{"what":"() crisis intraday Korean stock market.",'
        '"why":".",'
        '"impact":"(WTI) 72.69 3% surge (-4.60%), (-3.43%) stock price, '
        'SK (-6.34%), (-10.25%) IT· ·."}'
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=client,
    )

    summary = generator.generate(context)

    assert summary.what != "() crisis intraday Korean stock market."
    assert summary.why != "."
    assert "WTI) 72.69 3% surge" not in summary.impact
    assert not _has_korean(summary)


def test_news_summary_rejects_unsupported_hallucinated_hyphenated_terms() -> None:
    fallback = SummaryLines(
        what="LG화학은 반도체 스트리퍼 공급을 확대한다고 밝혔다.",
        why="AI와 HBM 수요 증가로 고성능 공정 소재 중요성이 커지고 있다.",
        impact="투자자는 전자소재 성장 속도와 신규 고객 공급 확대를 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="LG화학, 고부가가치 미래 전략사업 영역 확대",
        snippet="반도체 스트리퍼 공급과 전자소재 포트폴리오 확대가 핵심이다.",
        content=(
            "LG화학은 AI 투자 확대와 고대역폭 메모리(HBM) 수요 증가로 "
            "고성능 공정 소재 중요성이 커지는 상황에서 반도체 스트리퍼 사업을 "
            "확대하고 있다. LG화학은 앰코에 반도체용 스트리퍼를 양산 공급하고 "
            "전자소재 사업을 2030년까지 약 2조원 규모로 성장시킨다는 방침이다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="POSITIVE",
        event_tags=["CONTRACT"],
        stock_code="051910",
        stock_name="LG화학",
        stock_name_en="LG Chem",
        fallback=fallback,
    )
    client = FakeNewsSummaryClient(
        '{"what":"LG Chem expanded its high-value future strategy field.",'
        '"why":"The article cites the need for better memory-hazard shielding technology.",'
        '"impact":"The investor impact is to track the pace of memory-hazard '
        'shielding technology improvement."}'
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=client,
    )

    summary = generator.generate(context)

    assert summary != fallback
    assert summary.what.startswith("LG Chem")
    assert "semiconductor" in summary.what
    assert "memory-hazard" not in " ".join(
        [summary.what, summary.why, summary.impact]
    )
    assert not _has_korean(summary)


def test_news_summary_enabled_short_content_returns_english_grounded_fallback() -> None:
    fallback = SummaryLines(
        what="외국인 순매수에 코스피가 장중 반등했다.",
        why="원문은 외국인 자금 유입을 주요 배경으로 제시했다.",
        impact="투자자는 수급 지속성과 지수 확산 여부를 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="코스피, 외국인 순매수에 반등",
        snippet="외국인 자금 유입으로 코스피가 장중 반등했다.",
        content="외국인 순매수에 코스피가 반등했다.",
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient("{}"),
    )

    summary = generator.generate(context)

    assert summary != fallback
    assert summary.what.startswith("KOSPI")
    assert "drew attention" not in summary.what
    assert "foreign-investor" in summary.why
    assert "Investors should track" in summary.impact
    assert not _has_korean(summary)


def test_news_summary_fallback_handles_single_stock_leverage_etf_context() -> None:
    fallback = SummaryLines(
        what="단일종목 레버리지 ETF가 변동성을 키웠다.",
        why="개미 매수와 리밸런싱 물량이 영향을 줬다.",
        impact="투자자는 장 막판 변동성과 규제 변화를 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title='삼닉 레버리지로 손실 입은 개미들 … "이제라도 팔까" 전전긍긍',
        snippet="단일종목 레버리지 ETF가 한국 증시의 변동성을 키우고 있다.",
        content=(
            "단일종목 레버리지 상장지수펀드(ETF)가 출시 한 달 만에 한국 증시의 "
            "게임 체인저로 부상했다. 개미 매수가 몰리고 외국인 순매도발 낙폭이 "
            "커지면 레버리지 리밸런싱 물량이 장 막판 변동성을 키운다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"The Korean stock market faced trading by Samjeon Nix as a key issue.",'
            '"why":"The core background is market and business events confirmed in the source.",'
            '"impact":"Investors should monitor the spread of the story."}'
        ),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Single-stock leveraged ETFs")
    assert "ETF rebalancing" in summary.why
    assert "late-session volatility" in summary.impact
    assert "trading by Samjeon Nix" not in " ".join([summary.what, summary.why, summary.impact])
    assert not _has_korean(summary)


def test_news_summary_fallback_handles_securities_overseas_expansion_context() -> None:
    fallback = SummaryLines(
        what="국내 금융투자회사들이 해외 사업을 확대했다.",
        why="뉴욕 법인과 미들마켓론, 유럽 로드쇼가 주요 배경이다.",
        impact="투자자는 해외 수익원 다변화와 신용 리스크를 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="美서 중견·중소기업 자금줄 역할…유럽 로드쇼엔 투자자들 북적",
        snippet="국내 금융투자회사들이 뉴욕과 유럽에서 새 먹거리 확보에 나섰다.",
        content=(
            "한국투자증권의 뉴욕 법인 KIS US는 중견·중소기업 직접 대출인 "
            "미들마켓론에 공을 들이고 있다. 국내 금융투자회사들은 유럽 "
            "로드쇼에서도 투자자 수요를 확인했다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient("{}"),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Korean securities firms expanded overseas")
    assert "mid-market loan" in summary.why
    assert "credit risk controls" in summary.impact


def test_news_summary_fallback_handles_semiconductor_cluster_policy_context() -> None:
    context = NewsSummaryContext(
        title="이 대통령, 오늘 반도체 클러스터 점검회의…메가프로젝트 지원",
        snippet="반도체 클러스터 점검회의에서 메가프로젝트 후속 지원 방안이 논의된다.",
        content="반도체 클러스터 점검회의와 메가프로젝트 지원 방안이 핵심이다. ...",
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["POLICY"],
        stock_code="000660",
        stock_name="SK하이닉스",
        stock_name_en="SK하이닉스",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient("{}"),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Korea's semiconductor cluster support plan")
    assert "semiconductor megaprojects" in summary.why
    assert "chip supply-chain beneficiaries" in summary.impact
    assert not _has_korean(summary)


def test_news_summary_rejects_recent_market_word_salad_and_uses_retail_fallback() -> None:
    context = NewsSummaryContext(
        title="AI 신의 탄생과 인간의 종말",
        snippet="한국증시는 반도체 호황과 삼전닉스 빚투 우려를 함께 다뤘다.",
        content=(
            "지금 한국증시는 반도체 호황에 따른 투자 광풍이 불고 있다. "
            "개미투자자의 빚투와 삼전닉스 쏠림에 대한 우려가 제기됐다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"The Korean stock market faced Samjeon Nix trading as a key market issue.",'
            '"why":"The core backdrop is the latest market and corporate events '
            'confirmed in the original.",'
            '"impact":"Investors should track whether investor flows continue as the '
            'story develops."}'
        ),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Korean retail speculation around Samjeon Nix")
    assert "debt-funded retail speculation" in summary.why
    assert "margin exposure" in summary.impact


def test_news_summary_rejects_recent_numeric_word_salad_and_uses_regional_fallback() -> None:
    context = NewsSummaryContext(
        title="대구 상장사 시총 2조원 증발…5분기 상승세 꺾였다",
        snippet="대구 상장사 시총이 5분기 만에 감소세로 전환했다.",
        content="대구 상장사 시총이 2조원 줄었고 코스닥 약세가 부담으로 작용했다.",
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Large company ISeutasi stock price rose on KOSPI.",'
            '"why":"The total company share price decreased only 6.9% in the second quarter.",'
            '"impact":"The sheriff rifle exploded near par."}'
        ),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Daegu-listed companies")
    assert "KRW 2 trillion" in summary.why
    assert "regional market-cap trends" in summary.impact


def test_news_summary_rejects_broken_samjeon_leverage_surfaces() -> None:
    context = NewsSummaryContext(
        title="한은의 경고 “삼전닉스 레버리지, 개미들 죽여”",
        snippet="삼전닉스 레버리지 상품이 개미 투자자 손실과 시장 변동성을 키운다는 경고다.",
        content="삼전닉스 레버리지 상품에 개미 투자자가 몰리며 변동성 우려가 커졌다.",
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Korean entrepreneurhan warned that SKhinky and SinErlwyk prices may move.",'
            '"why":"The article cites exchange-rate volatility tied to company stock prices.",'
            '"impact":"The investor impact is greater focus on company stock prices."}'
        ),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Single-stock leveraged ETFs")
    assert "retail investors" in summary.why
    assert "risk controls" in summary.impact


def test_news_summary_rejects_live_honam_semiconductor_hallucination_surface() -> None:
    fallback = SummaryLines(
        what="금호건설 등 여러 종목이 호남 반도체 메가 프로젝트 기대감에 상한가를 기록했다.",
        why="정부 프로젝트 수혜 기대와 반도체 투자 뉴스가 매수세를 자극했다.",
        impact="투자자는 테마 수급 지속성과 관련주 변동성을 함께 확인해야 한다.",
    )
    context = _sample_context(fallback=fallback)
    client = FakeNewsSummaryClient(
        '{"what":"Golden Electric Group became Korea\'s largest semiconductor company '
        'on a Korean basis on a Korean scale.",'
        '"why":"The article cites high-value PER ratios, stronger AI demand, and '
        'larger plant sizes.",'
        '"impact":"The investor impact is better than expected with more orders '
        'placed on the market."}'
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=client,
    )

    summary = generator.generate(context)
    joined = " ".join((summary.what, summary.why, summary.impact))

    assert "Golden Electric Group" not in joined
    assert "investor impact is better than expected" not in joined.lower()


@pytest.mark.parametrize(
    ("title", "content", "expected"),
    [
        (
            "[Who Is ?] 진옥동 신한 금융지주 대표이사 회장",
            (
                "진옥동 신한금융지주 대표이사 회장의 생애와 경영전략을 다룬다. "
                "생산적 금융과 포용금융, 일본 금융 경험이 핵심이다."
            ),
            ("Shinhan Financial Group leadership", "Jin Ok-dong", "governance"),
        ),
        (
            "KB증권, 7월 첫째주 대한전선 등 14종목 매수 추천",
            (
                "KB증권은 7월 첫째주 14종목 매수 추천 목록을 제시했다. "
                "대한전선과 HD건설기계에 대해 Buy 유지 의견을 냈다."
            ),
            ("KB Securities highlighted 14 Korean stocks", "Taihan Cable", "target-price"),
        ),
        (
            "[특징주] 방산주, 나토 정상회의 기대감에 강세",
            (
                "방산주가 나토 정상회의 기대감에 상승했다. 엠앤씨솔루션, "
                "한화시스템, 한국항공우주가 동반 강세를 보였다."
            ),
            ("Korean defense stocks rallied", "NATO annual summit", "order expectations"),
        ),
        (
            "정책 부담 견딘 은행들 … 남은 과제는 저평가 해소",
            (
                "정책 부담 견딘 은행들 남은 과제는 저평가 해소다. "
                "금융지주와 은행주는 500조원 정책금융 부담에도 주주환원 기대를 받았다."
            ),
            (
                "Korean financial holding companies rebounded",
                "policy-finance obligations",
                "shareholder returns",
            ),
        ),
        (
            "한국항공우주·한화에어로스페이스 주가 기세등등…방산 슈퍼사이클 본격화",
            (
                "우주항공과국방 업종이 방산 수출 확대와 우주산업 투자 확대 정책에 "
                "상승했다. 한국항공우주와 한화에어로스페이스, 한화시스템이 강세다."
            ),
            ("aerospace and defense stocks rallied", "defense-export", "export orders"),
        ),
        (
            "국민연금, IT·뷰티 담고 코스닥 소부장·바이오 덜었다",
            (
                "국민연금이 2분기 국내 주식시장에서 IT·전자부품과 뷰티 비중을 "
                "늘리고 코스닥 소부장·바이오 지분을 줄였다."
            ),
            ("National Pension Service", "IT and electronics-parts", "valuation pressure"),
        ),
        (
            "'견미리家' 투자했던 '보타바이오' 주가의 타임라인",
            (
                "견미리 가족 투자 이후 보타바이오 주가는 급등했고 주가조작 "
                "사건은 대법원 판단을 기다린다."
            ),
            ("Botabio", "stock manipulation", "litigation"),
        ),
        (
            "생성형 AI 확산에도 딥페이크 테마 조정… 옥석 가리기 본격화",
            (
                "생성형 AI 확산에도 딥페이크 테마가 차익실현으로 조정됐다. "
                "라온시큐어와 파수AI 등 AI 보안 관련주의 선별 투자가 중요해졌다."
            ),
            ("Deepfake-related", "generative-AI", "commercialized AI security"),
        ),
        (
            "보안 시장 성장 기대 지속…AI·제로트러스트 관련주 주목",
            (
                "정보보안 테마가 글로벌 사이버 공격 증가와 제로트러스트 보안 투자 "
                "기대 속에 움직였고 핀텔과 라온시큐어가 주목받았다."
            ),
            ("information-security stocks", "zero-trust", "customer wins"),
        ),
        (
            "코위버, 테라급 광전송 장비 부각…보안 시장 핵심 공급자로 부상",
            (
                "코위버가 테라급 광전송 장비와 양자암호 QKD, PQA 인프라 공급 "
                "기대 속에 주목받았다."
            ),
            ("Quantum-security infrastructure", "Cowaver", "public-sector demand"),
        ),
        (
            "[뉴스줌인] '수백만 큐비트' 통념 깨졌다…양자컴퓨터가 흔드는 암호 방패",
            (
                "Q-데이 도래 우려가 커졌다. 양자컴퓨터의 암호 해독 큐비트 "
                "요구량이 줄면서 RSA와 ECC 공개키 암호가 위협받을 수 있다."
            ),
            ("Quantum-computing progress", "RSA", "post-quantum cryptography"),
        ),
        (
            "듀오백 , 투자경고종목 해제→재지정 예고",
            (
                "듀오백은 투자경고종목에서 해제돼 투자주의종목으로 지정됐지만 "
                "조건 충족 시 투자경고종목으로 재지정될 수 있다."
            ),
            ("Duoback", "investment-warning", "trading-halt"),
        ),
        (
            "6월 18일 주식시장 주요공시",
            (
                "주식시장 주요공시에는 전환사채 만기전 취득, 공급계약, 자사주 "
                "취득 신탁계약, 유상증자 등 여러 공시가 포함됐다."
            ),
            ("daily disclosure roundup", "convertible-bond", "dilution"),
        ),
        (
            "'5조 시장' 상반기 ECM, SKC·한화솔루션 유증이 순위 갈랐다",
            (
                "상반기 ECM 리그테이블에서 SKC와 한화솔루션 유상증자가 순위를 "
                "갈랐고 NH투자증권과 KB증권 실적이 주목받았다."
            ),
            ("ECM league-table", "SKC", "underwriting"),
        ),
        (
            "'코스닥 상폐 강화' D-데이…10곳 중 1곳 퇴출 위기",
            (
                "코스닥 상장폐지 기준 강화로 듀오백과 SHD 등 시총 미달 "
                "관리종목의 퇴출 위험이 커졌다."
            ),
            ("KOSDAQ delisting", "market-cap", "small caps"),
        ),
        (
            "첫 외환 24시간 개장 1527.6원 출발",
            (
                "원/달러 외환거래가 24시간 무중단 방식으로 바뀌었고 환율은 "
                "1527.6원으로 출발했다. 하나은행 딜링룸에서 당국자들이 점검했다."
            ),
            ("won-dollar FX market", "KRW 1,527.6", "overnight volatility"),
        ),
        (
            "이순형 라온시큐어 대표, 2억 규모 자사주 장내매수",
            (
                "라온시큐어 이순형 대표는 지난 22일부터 이틀간 약 2억136만원 "
                "규모의 회사 주식을 매입했다."
            ),
            ("RaonSecure", "KRW 200 million", "insider-confidence"),
        ),
        (
            "조아 제약 , 신규 헬스케어 원료 유통 계약 확보…수익 다각화 시동",
            (
                "조아제약은 신규 헬스케어 원료 유통 계약과 신약 물질 기대감으로 "
                "상한가에 올랐다."
            ),
            ("Cho-A Pharm", "healthcare raw-material", "contract revenue"),
        ),
        (
            "경찰에 룸살롱 제공한 양정원 남편",
            (
                "자본시장법 위반 사건에서 듀오백 주식 시세조종과 차명계좌, "
                "부당이득 혐의가 재판에서 다뤄졌다."
            ),
            ("Duoback", "share-price manipulation", "court findings"),
        ),
    ],
)
def test_news_summary_fallback_handles_recent_live_market_contexts(
    title: str,
    content: str,
    expected: tuple[str, str, str],
) -> None:
    context = NewsSummaryContext(
        title=title,
        snippet=content,
        content=content,
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient("{}"),
    )

    summary = generator.generate(context)
    joined = " ".join((summary.what, summary.why, summary.impact))

    for fragment in expected:
        assert fragment in joined
    assert summary.what.endswith(".")
    assert summary.why.endswith(".")
    assert summary.impact.endswith(".")
    assert not _has_korean(summary)


def test_news_summary_rejects_broken_samnik_leverage_hynix_surface() -> None:
    context = NewsSummaryContext(
        title='삼닉 레버리지로 손실 입은 개미들 … "이제라도 팔까" 전전긍긍',
        snippet="단일종목 레버리지 ETF가 한국 증시의 변동성을 키우고 있다.",
        content=(
            "단일종목 레버리지 상장지수펀드(ETF)에 개미 투자자가 몰리고 "
            "외국인 순매도발 낙폭이 커지면 리밸런싱 물량이 장 막판 변동성을 키운다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            "{\"what\":\"SK Hallinkyos Semiconductor's investor impact is higher on "
            "regular market cap.\","
            "\"why\":\"The article cites global exposure to US NVDL's market cap and "
            "Korean exchange volatility.\","
            "\"impact\":\"The investor impact is greater on regular market cap and "
            "larger exposure to US ETFs.\"}"
        ),
    )

    summary = generator.generate(context)

    assert summary.what.startswith("Single-stock leveraged ETFs")
    assert "ETF rebalancing" in summary.why
    assert "late-session volatility" in summary.impact
    assert "Hallinkyos" not in " ".join([summary.what, summary.why, summary.impact])


def test_news_summary_fallback_handles_coupang_trade_tension_context() -> None:
    context = NewsSummaryContext(
        title="트럼프, 재임 중 쿠팡株 18회 거래… 한미 통상 갈등 심화 우려",
        snippet="쿠팡 사태가 한미 통상 갈등과 무역 보복 우려로 번지고 있다.",
        content=(
            "트럼프 대통령이 재임 중 쿠팡 주식을 18차례 거래한 사실이 확인됐다. "
            "미국 측은 한국 정부의 쿠팡 조사와 규제를 미국 기업 차별로 비판했고, "
            "무역법 301조와 반도체·자동차 수출 압박 가능성이 거론됐다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET", "RISK"],
        stock_code="000660",
        stock_name="SK하이닉스",
        stock_name_en="SK hynix",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"SK hynix faced the reported event as a key market issue.",'
            '"why":"The article links the move to policy expectations.",'
            '"impact":"Investors should track policy execution as the story develops."}'
        ),
    )

    summary = generator.generate(context)

    assert "Coupang" in summary.what
    assert "Trump" in summary.what
    assert "Section 301" in summary.why
    assert "Korea-U.S. trade talks" in summary.impact
    assert "reported event" not in " ".join([summary.what, summary.why, summary.impact])


def test_news_summary_fallback_handles_pension_alternative_investment_context() -> None:
    context = NewsSummaryContext(
        title="연기금, 주식 수익률 날았는데 대체투자는 '고전'… 하반기 개선 기대",
        snippet="연기금의 주식 수익률은 높았지만 대체투자는 부진했다.",
        content=(
            "연기금은 상장주식에서 높은 수익률을 냈지만 대체투자 성과는 고전했고 "
            "하반기 개선이 기대된다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"The Korean stock market faced interest-rate pressure as a key market issue.",'
            '"why":"The article links the move to interest-rate expectations.",'
            '"impact":"Investors should track rate expectations and valuation pressure."}'
        ),
    )

    summary = generator.generate(context)

    assert "pension funds" in summary.what
    assert "alternative" in summary.what
    assert "second-half improvement" in summary.why
    assert "asset-allocation" in summary.impact


def test_news_summary_fallback_handles_samsung_two_track_esg_context() -> None:
    context = NewsSummaryContext(
        title="실상은 다른 회사(?)…삼성전자 DX·DS '투트랙 ESG' 속사정",
        snippet="삼성전자 DX와 DS가 서로 다른 ESG 전략을 추진한다.",
        content=(
            "삼성전자 DX와 DS 부문은 사업 구조가 달라 ESG 우선순위와 실행 방식도 "
            "다르며 투트랙 ESG 전략을 택하고 있다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["ESG", "GENERAL_MARKET"],
        stock_code="005930",
        stock_name="삼성전자",
        stock_name_en="Samsung Electronics",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Samsung Electronics faced semiconductor and HBM demand as a key '
            'market issue.",'
            '"why":"The article links the move to HBM demand and memory-market conditions.",'
            '"impact":"Investors should track operating-profit recovery."}'
        ),
    )

    summary = generator.generate(context)

    assert "DX and DS" in summary.what
    assert "ESG strategies" in summary.what
    assert "two-track ESG" in summary.why
    assert "ESG disclosure" in summary.impact


def test_news_summary_fallback_handles_hyundai_usmca_parts_context() -> None:
    context = NewsSummaryContext(
        title="현대차·기아·모비스 초비상…美 부품 82% 유지",
        snippet="USMCA 원산지 규정 강화와 멕시코 생산망 재편 부담이 커졌다.",
        content=(
            "미국은 USMCA 연장을 현재 형태로 동의하지 않았고, 북미산 부품 조달 "
            "비율을 82%까지 높이는 방안이 유지됐다. 현대차·기아·현대모비스는 "
            "멕시코 생산망과 무관세 수출 구조를 다시 점검해야 한다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET", "RISK"],
        stock_code="005380",
        stock_name="현대차",
        stock_name_en="Hyundai Motor",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Hyundai Motor faced the KOSPI market move as a key market issue.",'
            '"why":"The article links the move to currency moves and supply changes.",'
            '"impact":"Investors should track currency sensitivity and foreign flow."}'
        ),
    )

    summary = generator.generate(context)

    assert "Hyundai Motor, Kia, and Hyundai Mobis" in summary.what
    assert "82% North American parts threshold" in summary.why
    assert "USMCA talks" in summary.impact
    assert "KOSPI market move" not in " ".join([summary.what, summary.why, summary.impact])


def test_news_summary_fallback_handles_bank_deposit_inflow_context() -> None:
    context = NewsSummaryContext(
        title="“증시 때문에 머리가 다 빠지네요”…결국 은행으로 다시 돈 몰린다",
        snippet="증시 변동성에 차익 실현 자금이 은행 수신으로 돌아왔다.",
        content=(
            "5대 은행 총수신이 90조원 가까이 늘었다. 증시가 출렁이며 안전선호 "
            "현상이 커졌고 차익 실현 후 은행 예치가 늘었다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"KOSPI faced the KOSPI market move as a key market issue.",'
            '"why":"The article links the move to interest-rate expectations.",'
            '"impact":"Investors should track rate expectations."}'
        ),
    )

    summary = generator.generate(context)

    assert "Money flowed back into major Korean banks" in summary.what
    assert "KRW 90 trillion" in summary.why
    assert "bank deposit growth" in summary.impact


def test_news_summary_fallback_handles_bank_earnings_without_data_center_driver() -> None:
    context = NewsSummaryContext(
        title='하나증권 "은행주 2분기 실적 양호, 최선호주 KB금융지주 신한금융지주"',
        snippet=(
            "2분기 환율 상승에 따른 부정적 영향이 크지 않아 은행들 실적은 "
            "예상대로 양호할 가능성이 높다."
        ),
        content=(
            "은행주 주가가 2분기 양호한 실적과 금리 모멘텀을 바탕으로 추가 "
            "상승세를 이어갈 것으로 전망됐다. KB금융과 신한지주, 하나금융은 "
            "직전 주가 고점 돌파를 눈앞에 두고 있다. 반도체 업종이 고점 "
            "논란으로 데이터센터 투자 우려를 받는 동안 은행주는 강세를 보였다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="POSITIVE",
        event_tags=["EARNINGS", "MACRO"],
        stock_code="086790",
        stock_name="하나금융지주",
        stock_name_en="Hana Financial",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"KOSPI moved around earnings recovery expectations.",'
            '"why":"The article links the move to data-center investment, '
            'foreign-investor net buying, institutional net buying.",'
            '"impact":"Investors should track operating-profit recovery and earnings guidance."}'
        ),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert summary.what.startswith("Korean bank stocks")
    assert "second-quarter bank earnings" in summary.why
    assert "KB Financial" in summary.impact
    assert "data-center investment" not in joined
    assert not _has_korean(summary)


def test_news_summary_catch_all_uses_evidence_instead_of_generic_reported_event() -> None:
    context = NewsSummaryContext(
        title="[대호에이엘 톺아보기] 쪼개기 매각된 반품 CB",
        snippet="반품 CB와 최대주주 지분 변화가 투자자 관심을 받고 있다.",
        content=(
            "전환사채 물량이 여러 투자자에게 쪼개기 매각됐고, 최대주주 변경과 "
            "지분 희석 가능성이 함께 거론됐다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEGATIVE",
        event_tags=["CAPITAL_ACTION", "RISK"],
        stock_code="000000",
        stock_name="대호에이엘",
        stock_name_en="Daeho AL",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"The company moved around the reported event.",'
            '"why":"The article links the move to market sentiment and investor positioning.",'
            '"impact":"Investors should track the next disclosure and market reaction '
            'as the story develops."}'
        ),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert "reported event" not in joined
    assert "market sentiment and investor positioning" not in joined
    assert "convertible-bond" in joined
    assert "dilution risk" in joined


def test_news_summary_rejects_kospi_hallucinated_company_name() -> None:
    context = NewsSummaryContext(
        title="오늘도 '롤러코스피'…등락 거듭 끝 8000선 지켜",
        snippet=(
            "실적 발표를 앞둔 삼성전자는 등락을 보였고 외국인은 "
            "유가증권시장에서 순매도했다."
        ),
        content=(
            "지난주 급격한 등락을 보였던 코스피가 장중 크게 출렁였다. "
            "코스피는 외국인과 기관 순매도 속에 8000선을 아슬아슬하게 지켰다. "
            "삼성전자와 SK하이닉스 흐름이 지수 변동성을 키웠고 환율도 흔들렸다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET", "MACRO"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Samsung Exosphate rose on a small day only to fall back to '
            'the level of KRW 8,000.",'
            '"why":"The article cites exchange data from KRW 8,000.",'
            '"impact":"The investor impact is a market rebound still dependent on '
            'smaller daily volatility levels."}'
        ),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert "KOSPI" in joined
    assert "Samsung Exosphate" not in joined
    assert "foreign" in summary.why.lower()


def test_news_summary_fallback_handles_limit_up_ai_infra_context() -> None:
    context = NewsSummaryContext(
        title="[주식마감] 삼전닉스 '호남 메가 프로젝트'에 금호건설 3거래일 연속 상한가",
        snippet="금호건설, 미래산업, 삼화전자, 에브리봇 등 상한가 종목이 주목받았다.",
        content=(
            "금호건설, 미래산업, 삼화전자, 에브리봇이 상한가를 기록했다. "
            "삼성전자와 SK그룹의 AI 인프라 투자 기대와 MLCC 수요 확대, "
            "로봇 자동화 테마가 투자심리를 자극했다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="POSITIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"KOSPI and KOSDAQ moved around Samjeon Nix trading.",'
            '"why":"The article links the move to attention on Samjeon Nix.",'
            '"impact":"Investors should track whether investor flows continue."}'
        ),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert summary.what.startswith("Korean limit-up stocks")
    assert "AI infrastructure" in summary.why
    assert "MLCC demand" in summary.why
    assert "Samjeon Nix trading" not in joined
    assert not _has_korean(summary)


def test_news_summary_fallback_handles_semiconductor_earnings_adr_context() -> None:
    context = NewsSummaryContext(
        title="외국인 20조 던진 반도체…이번 주 '삼전 실적·하이닉스 ADR'이 승부 가...",
        snippet="삼성전자 실적과 SK하이닉스 ADR 상장이 반도체 투자심리의 분수령이다.",
        content=(
            "외국인이 반도체주를 20조원 가까이 순매도했다. 이번 주 삼성전자 "
            "잠정실적과 SK하이닉스 ADR 상장이 외국인 수급 회복의 시험대다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["EARNINGS", "GENERAL_MARKET"],
        stock_code="452400",
        stock_name="한화인더스트리얼솔루션즈",
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"KOSPI faced earnings recovery expectations as a key market issue.",'
            '"why":"The article links the move to memory-market conditions.",'
            '"impact":"Investors should track earnings guidance."}'
        ),
    )

    summary = generator.generate(context)

    assert "SK hynix's ADR listing" in summary.what
    assert "Samsung Electronics' upcoming earnings" in summary.why
    assert "foreign flows" in summary.impact


def test_news_summary_fallback_handles_weekly_semiconductor_flow_report() -> None:
    context = NewsSummaryContext(
        title="[주간수급리포트] 외인 20兆 매도 폭탄에 국장 하락...개인·기관 반도체...",
        snippet="외국인이 코스피와 코스닥에서 매도하고 개인과 기관이 반도체주를 받아냈다.",
        content=(
            "지난 한 주간 국내 증시는 외국인의 거센 매도세에 밀려 코스피와 코스닥 "
            "지수 모두 하락했다. 외국인은 19조8374억원을 순매도했고 개인과 기관은 "
            "삼성전자와 SK하이닉스 등 반도체주를 매수했다. 메타와 애플발 쇼크도 "
            "반도체 업종 약세의 배경으로 지목됐다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="NEGATIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"KOSPI and KOSDAQ faced earnings recovery expectations as a key '
            'market issue.",'
            '"why":"The article links the move to memory-market conditions.",'
            '"impact":"Investors should track earnings guidance."}'
        ),
    )

    summary = generator.generate(context)

    assert "nearly KRW 20 trillion sell-off" in summary.what
    assert "major semiconductor stocks" in summary.why
    assert "semiconductor bargain buying" in summary.impact


def test_news_summary_fallback_handles_hyundai_rv_hev_profit_context() -> None:
    context = NewsSummaryContext(
        title="신차 가격 떨어지는 美 시장…현대차·기아, 'RV·HEV' 투트랙으로 수익...",
        snippet="현대차와 기아가 RV와 HEV로 미국 시장 수익성을 방어하고 있다.",
        content=(
            "미국 신차 가격이 떨어지고 인센티브가 늘었지만 현대차와 기아는 RV와 "
            "HEV 판매를 앞세워 상반기 역대 최대 판매를 기록했다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["EARNINGS", "GENERAL_MARKET"],
        stock_code="005380",
        stock_name="현대차",
        stock_name_en="Hyundai Motor",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Hyundai Motor Group became stronger on the US market with EV '
            'and HEV vehicles.",'
            '"why":"The article cites the investor impact on the flow of earnings.",'
            '"impact":"The investor impact is higher on EV and HEV markets."}'
        ),
    )

    summary = generator.generate(context)

    assert "RV and HEV sales" in summary.what
    assert "falling U.S. new-car prices" in summary.why
    assert "U.S. margin resilience" in summary.impact


def test_news_summary_enabled_fallback_does_not_use_bare_stock_code_subject() -> None:
    fallback = SummaryLines(
        what="두산에너빌리티 주가 흐름이 시장 관심을 받았다.",
        why="외국인과 기관 수급이 영향을 줬다.",
        impact="투자자는 수급 지속성을 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="두산에너빌리티 지난장 소폭 강세로, 새주장 주가 흐름 이목",
        snippet="코스피 시장에서 주가 흐름과 외국인 수급이 주목됐다.",
        content="두산에너빌리티 주가는 코스피 시장에서 수급 변화와 함께 움직였다.",
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code="034020",
        stock_name=None,
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"034020 drew attention in the article around the KOSPI market move.",'
            '"why":"The story links the shift to supply.",'
            '"impact":"Investors should follow the next disclosure and watch the '
            'market reaction as the story develops."}'
        ),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert "034020" not in joined
    assert "drew attention" not in joined
    assert "article-backed" not in joined
    assert summary.what.startswith("KOSPI")


def test_news_summary_enabled_fallback_handles_nvidia_robotics_context() -> None:
    fallback = SummaryLines(
        what="엔비디아 로봇 매출과 액추에이터 수혜주가 부각됐다.",
        why="부품 공급망으로 관심이 이동했다.",
        impact="투자자는 액추에이터 수주와 실적 반영 여부를 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="엔비디아 로봇매출 1%대…액추에이터 수혜주 급부상",
        snippet="엔비디아 피지컬 AI 매출과 부품 공급망 관련 액추에이터 기업이 주목받았다.",
        content=(
            "엔비디아의 로봇매출 기여도는 아직 1%대에 머물렀고 국내 투자자 "
            "관심은 완제품보다 부품 공급망과 액추에이터 수혜주로 이동했다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="POSITIVE",
        event_tags=["GENERAL_MARKET"],
        stock_code="454910",
        stock_name=None,
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient('{"what":"한글 조각", "why":"bad", "impact":"bad"}'),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert "Nvidia-linked robotics and actuator stocks" in summary.what
    assert "small direct robotics revenue contribution" in summary.why
    assert "parts supply chain" in summary.why
    assert "454910" not in joined
    assert not _has_korean(summary)


def test_news_summary_enabled_fallback_handles_corporate_rehabilitation_terms() -> None:
    fallback = SummaryLines(
        what="기업회생 신청이 3년 새 급증했다.",
        why="한계기업과 좀비기업 정리가 늦어지고 있다.",
        impact="투자자는 구조조정 속도와 금융기관 부실 위험을 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="[박근종 칼럼] 3년 새 기업회생 신청 2배 급증",
        snippet="한계기업은 신속 정리하는 게 최선이라는 지적이다.",
        content=(
            "최근 증시 활황의 착시 속에 재무구조가 취약한 기업들의 기업회생 "
            "신청이 급증했다. 한계기업과 좀비기업을 시장에서 신속히 정리해야 "
            "생산성과 자본 배분의 효율성을 높일 수 있다는 지적이 나온다. "
            "구조조정이 늦어질수록 금융기관 부실과 투자자 손실이 커질 수 있다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["GENERAL_MARKET", "RISK"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient('{"what":"한글 조각", "why":"bad", "impact":"bad"}'),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert "corporate rehabilitation" in joined
    assert "marginal-company" in joined
    assert "restructuring" in joined
    assert "credit risk" in joined
    assert "key market issue" not in joined
    assert "institutional flow" not in joined
    assert "currency moves" not in joined
    assert "interest-rate expectations" not in joined
    assert not _has_korean(summary)


def test_news_summary_enabled_fallback_prioritizes_ipo_market_context() -> None:
    fallback = SummaryLines(
        what="IPO 시장이 위축됐다.",
        why="공모금액과 상장기업 수가 줄었다.",
        impact="투자자는 신규상장 종목 수요를 확인해야 한다.",
    )
    context = NewsSummaryContext(
        title="IPO시장 칼바람… 상장기업 수·공모금액 절반 싹둑",
        snippet="올해 상반기 IPO 시장은 공모금액이 반토막 났다.",
        content=(
            "올해 상반기 IPO 시장은 공모금액이 반토막 났고 신규상장 기업은 "
            "상장 첫날 주가를 유지하지 못했다. 대부분 코스닥 시장으로 진입한 "
            "신규상장 기업의 주가는 공모가를 밑돌았다. 기관 수요예측과 "
            "중복상장 규제 이슈도 관망세를 키웠다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["GENERAL_MARKET"],
        stock_code="279570",
        stock_name="",
        stock_name_en="",
        fallback=fallback,
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient('{"what":"한글 조각", "why":"bad", "impact":"bad"}'),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert summary.what == (
        "The Korean IPO market cooled as listing counts and offering proceeds fell sharply."
    )
    assert "new listings traded below their offering prices" in summary.why
    assert "weak KOSDAQ demand" in summary.why
    assert "listing-rule uncertainty" in summary.why
    assert "major listings revive demand" in summary.impact
    assert "279570" not in joined
    assert "institutional flow" not in joined
    assert not _has_korean(summary)


def test_news_summary_fallback_handles_kospi_trillion_club_context() -> None:
    context = NewsSummaryContext(
        title="코스피 8천선에도 '1조클럽' 감소⋯대형주 쏠림 심화",
        snippet="시가총액 1조원 이상 종목 수가 줄며 대형주 쏠림이 심화됐다.",
        content=(
            "코스피가 8000선을 회복했지만 국내 증시 1조클럽 종목 수는 "
            "314개로 감소했다. 삼성전자와 SK하이닉스 등 대형주 중심으로 "
            "시가총액이 쏠렸고 코스닥 1조클럽도 줄었다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient('{"what":"한글 조각", "why":"bad", "impact":"bad"}'),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert summary.what.startswith("KOSPI recovered the 8,000 level")
    assert "KRW 1 trillion club" in joined
    assert "large-cap concentration" in joined
    assert "key market issue" not in joined
    assert not _has_korean(summary)


def test_news_summary_fallback_handles_won_dollar_rate_forecast_context() -> None:
    context = NewsSummaryContext(
        title='"연말 환율고점 1575원… 내년에도 안 꺾인다"',
        snippet="전문가들은 원·달러 환율이 내년까지 1500원 안팎에 머물 것으로 봤다.",
        content=(
            "원·달러 환율 전망치는 평균 1484원, 고점은 1575원으로 집계됐다. "
            "대미투자 압력과 엔저가 변수로 남았고 일부 전문가는 연내 1600원 "
            "돌파 가능성도 제기했다."
        ),
        source_type="NEWS",
        importance="MEDIUM",
        sentiment="NEUTRAL",
        event_tags=["GENERAL_MARKET"],
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        fallback=SummaryLines(what="", why="", impact=""),
    )
    generator = NewsSummaryGenerator(
        enabled=True,
        model_name="Qwen3-0.6B-test",
        client=FakeNewsSummaryClient(
            '{"what":"Korean exporters face stronger currency risk as exchange rates weaken.",'
            '"why":"The investor impact is higher on exchange rates.",'
            '"impact":"The investor impact is greater on exchange rates."}'
        ),
    )

    summary = generator.generate(context)
    joined = " ".join([summary.what, summary.why, summary.impact])

    assert summary.what.startswith("Market experts expected the won-dollar rate")
    assert "KRW 1,575" in summary.what
    assert "yen weakness" in summary.why
    assert "investor impact is greater" not in joined.lower()
    assert not _has_korean(summary)


def test_alert_analyzer_passes_full_context_to_news_summary_generator() -> None:
    generated = SummaryLines(
        what="Samsung Electronics said AI-server investment is lifting chip earnings.",
        why="The article links the move to HBM demand and stronger memory prices.",
        impact="The investor impact is a need to track operating-profit recovery speed.",
    )
    summary_generator = CapturingNewsSummaryGenerator(generated)
    analyzer = AlertAnalyzer(summary_generator=summary_generator)

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

    assert response.summary_lines == generated
    assert summary_generator.context is not None
    assert summary_generator.context.stock_code == "005930"
    assert summary_generator.context.stock_name_en == "Samsung Electronics"
    assert "HBM" in summary_generator.context.content


def _sample_context(*, fallback: SummaryLines) -> NewsSummaryContext:
    return NewsSummaryContext(
        title="삼성전자, AI 서버 투자 확대에 반도체 실적 회복 기대",
        snippet="HBM 수요와 메모리 가격 반등이 실적 회복의 배경으로 꼽힌다.",
        content=(
            "삼성전자는 AI 서버 투자 확대로 HBM과 메모리 수요가 늘며 "
            "반도체 실적 회복 기대가 커졌다. "
            "메모리 가격 반등과 주요 고객사의 데이터센터 투자가 이번 회복의 "
            "핵심 배경으로 거론된다. "
            "투자자는 영업이익 회복 속도와 고부가 제품 비중 확대 여부를 확인해야 한다."
        ),
        source_type="NEWS",
        importance="HIGH",
        sentiment="POSITIVE",
        event_tags=["EARNINGS"],
        stock_code="005930",
        stock_name="삼성전자",
        stock_name_en="Samsung Electronics",
        fallback=fallback,
    )


def _has_korean(summary: SummaryLines) -> bool:
    return any("가" <= char <= "힣" for char in f"{summary.what}{summary.why}{summary.impact}")
