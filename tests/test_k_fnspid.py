from __future__ import annotations

from datetime import date

from hannah_montana_ai.training.k_fnspid.entity_linker import ExactContextEntityLinker
from hannah_montana_ai.training.k_fnspid.impact_labeler import build_market_impacts
from hannah_montana_ai.training.k_fnspid.schema import DailyPrice
from hannah_montana_ai.training.k_fnspid.splitter import temporal_split
from hannah_montana_ai.training.k_fnspid.temporal import (
    effective_trade_date,
    normalize_publication_time,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry


def test_after_close_news_maps_to_next_trading_date() -> None:
    trading_dates = {date(2026, 6, 3), date(2026, 6, 4)}
    publication = normalize_publication_time("2026-06-03T07:00:00+00:00", trading_dates)

    assert publication.published_at_kst.startswith("2026-06-03T16:00:00")
    assert publication.market_session == "AFTER_CLOSE"
    assert effective_trade_date(publication, sorted(trading_dates)) == "2026-06-04"


def test_date_only_disclosure_keeps_precision() -> None:
    publication = normalize_publication_time("20260603", {date(2026, 6, 3)})

    assert publication.precision == "DATE"
    assert publication.market_session == "UNKNOWN"


def test_entity_linker_rejects_english_partial_match() -> None:
    linker = ExactContextEntityLinker(
        [
            StockUniverseEntry(stock_code="365900", stock_name="브이씨", market="KOSDAQ"),
            StockUniverseEntry(stock_code="005930", stock_name="삼성전자", market="KOSPI"),
        ]
    )

    result = linker.link(
        document_id="doc",
        title="CSOP Investments VCC securities report",
        body="Global investment vehicle report",
        source_type="DISCLOSURE",
    )

    assert result.links == ()


def test_entity_linker_marks_exact_title_company_primary() -> None:
    linker = ExactContextEntityLinker(
        [StockUniverseEntry(stock_code="005930", stock_name="삼성전자", market="KOSPI")]
    )

    result = linker.link(
        document_id="doc",
        title="삼성전자 2분기 영업이익 증가",
        body="삼성전자 실적 발표",
        source_type="NEWS",
    )

    assert result.links[0].stock_code == "005930"
    assert result.links[0].relation == "PRIMARY"


def test_market_impact_uses_market_adjusted_return() -> None:
    prices: list[DailyPrice] = []
    for index in range(70):
        trade_date = date.fromordinal(date(2025, 1, 1).toordinal() + index).isoformat()
        prices.extend(
            [
                DailyPrice(
                    "005930",
                    trade_date,
                    "KOSPI",
                    100 + index,
                    102 + index,
                    99 + index,
                    101 + index,
                    101 + index,
                    1_000 + index,
                    100_000,
                ),
                DailyPrice(
                    "000660",
                    trade_date,
                    "KOSPI",
                    200 + index,
                    202 + index,
                    199 + index,
                    201 + index,
                    201 + index,
                    2_000 + index,
                    200_000,
                ),
            ]
        )

    result = build_market_impacts([("doc", "005930", prices[120].trade_date)], prices)[0]

    assert result.abnormal_return_1d is not None
    assert result.materiality_score is not None


def test_temporal_split_applies_embargo() -> None:
    assert (
        temporal_split(
            "2024-12-28",
            validation_start=date(2025, 1, 1),
            test_start=date(2026, 1, 1),
        )
        == "EMBARGO"
    )
