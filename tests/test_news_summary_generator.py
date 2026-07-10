from hannah_montana_ai.domain.schemas import SummaryLines
from hannah_montana_ai.services.news_summary_generator import (
    NewsSummaryContext,
    NewsSummaryGenerator,
)


def _context(**overrides: object) -> NewsSummaryContext:
    values: dict[str, object] = {
        "title": "삼성전자, 반도체 수요 회복에 실적 개선",
        "snippet": "메모리 가격 반등과 AI 수요가 실적을 끌어올렸다.",
        "content": "삼성전자의 영업이익이 반도체 수요 회복과 메모리 가격 반등으로 증가했다.",
        "source_type": "NEWS",
        "importance": "HIGH",
        "sentiment": "POSITIVE",
        "event_tags": ["EARNINGS"],
        "stock_code": "005930",
        "stock_name": "삼성전자",
        "stock_name_en": "Samsung Electronics",
        "fallback": SummaryLines(what="fallback", why="fallback", impact="fallback"),
    }
    values.update(overrides)
    return NewsSummaryContext(**values)  # type: ignore[arg-type]


def test_news_summary_always_uses_rule_output() -> None:
    result = NewsSummaryGenerator().generate(_context())

    assert result.what != "fallback"
    assert result.why != "fallback"
    assert result.impact != "fallback"
    assert all(not any("가" <= char <= "힣" for char in line) for line in result)


def test_rule_summary_has_three_distinct_complete_lines() -> None:
    result = NewsSummaryGenerator().generate(_context())
    lines = (result.what, result.why, result.impact)

    assert len(set(lines)) == 3
    assert all(line.endswith((".", "!", "?")) for line in lines)


def test_rule_summary_handles_kospi_volatility() -> None:
    result = NewsSummaryGenerator().generate(
        _context(
            title="코스피 롤러코스터 장세",
            snippet="외국인 순매도로 코스피가 장중 급락 후 반등했다.",
            content="코스피는 외국인 순매도 영향으로 큰 변동성을 보이며 급락 후 반등했다.",
            stock_code=None,
            stock_name=None,
            stock_name_en="Korean market",
            event_tags=["MARKET_MOVE", "FOREIGN_FLOW"],
        )
    )

    combined = f"{result.what} {result.why} {result.impact}".lower()
    assert "kospi" in combined
    assert "volatil" in combined or "foreign" in combined


def test_rule_summary_handles_bank_earnings() -> None:
    result = NewsSummaryGenerator().generate(
        _context(
            title="은행권 순이익 증가",
            snippet="이자이익과 비이자이익이 개선됐다.",
            content="국내 은행의 순이익은 이자이익과 수수료 수익 증가로 개선됐다.",
            stock_name_en="Korean banks",
            stock_code=None,
        )
    )

    combined = f"{result.what} {result.why} {result.impact}".lower()
    assert "bank" in combined


def test_rule_summary_does_not_emit_advice() -> None:
    result = NewsSummaryGenerator().generate(_context())
    combined = f"{result.what} {result.why} {result.impact}".lower()

    assert "must buy" not in combined
    assert "price target" not in combined
    assert "guaranteed" not in combined


def test_rule_summary_preserves_ant_localism() -> None:
    result = NewsSummaryGenerator().generate(
        _context(
            title="개미 순매수 확대",
            snippet="개미가 상반기 국내 주식을 순매수했다.",
            content="개미 투자자는 상반기 반도체주를 중심으로 큰 규모의 순매수를 기록했다.",
        )
    )

    combined = f"{result.what} {result.why} {result.impact}"
    assert "Ant" in combined
    assert "retail investor" not in combined.lower()
