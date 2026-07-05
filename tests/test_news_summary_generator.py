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


def test_news_summary_qwen_output_falls_back_to_english_lines_on_korean_fragment_or_meta() -> None:
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
    assert summary.what == (
        "Samsung Electronics drew attention in the article around earnings recovery expectations."
    )
    assert "HBM demand" in summary.why
    assert "operating-profit recovery" in summary.impact
    assert not any(
        any("가" <= char <= "힣" for char in line)
        for line in (summary.what, summary.why, summary.impact)
    )


def test_news_summary_enabled_short_content_falls_back_to_english_lines() -> None:
    fallback = SummaryLines(
        what="삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다.",
        why="메모리 가격 반등과 HBM 공급 확대가 주요 배경이다.",
        impact="투자자는 영업이익 회복 속도와 수요 지속성을 확인해야 한다.",
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

    assert summary.what == "KOSPI drew attention in the article around foreign-investor net buying."
    assert summary.why == "The article links the move to foreign-investor flow."
    assert (
        summary.impact
        == "Investors should track whether investor flows continue as the story develops."
    )


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
