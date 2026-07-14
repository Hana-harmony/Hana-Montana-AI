from __future__ import annotations

import importlib.util
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path
from types import ModuleType

from hannah_montana_ai.training.k_fnspid.entity_linker import ExactContextEntityLinker
from hannah_montana_ai.training.k_fnspid.event_clusterer import assign_event_clusters
from hannah_montana_ai.training.k_fnspid.impact_labeler import build_market_impacts
from hannah_montana_ai.training.k_fnspid.sampling import (
    select_unconfounded_representatives,
)
from hannah_montana_ai.training.k_fnspid.schema import CanonicalDocument, DailyPrice
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


def test_publication_before_price_history_has_no_effective_trade_date() -> None:
    trading_dates = [date(2021, 1, 4), date(2021, 1, 5)]
    publication = normalize_publication_time("20200102", set(trading_dates))

    assert effective_trade_date(publication, trading_dates) == ""


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


def test_market_impact_one_day_window_starts_at_pre_event_close() -> None:
    prices: list[DailyPrice] = []
    for index in range(30):
        trade_date = date.fromordinal(date(2025, 1, 1).toordinal() + index).isoformat()
        event_close = 120.0 if index >= 21 else 100.0
        prices.extend(
            [
                DailyPrice(
                    "005930",
                    trade_date,
                    "KOSPI",
                    event_close,
                    event_close,
                    event_close,
                    event_close,
                    event_close,
                    1_000,
                    100_000,
                ),
                DailyPrice(
                    "000660",
                    trade_date,
                    "KOSPI",
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    1_000,
                    100_000,
                ),
            ]
        )

    result = build_market_impacts([("doc", "005930", "2025-01-22")], prices)[0]

    assert result.abnormal_return_1d == 0.1


def test_temporal_split_applies_embargo() -> None:
    assert (
        temporal_split(
            "2024-12-28",
            validation_start=date(2025, 1, 1),
            test_start=date(2026, 1, 1),
        )
        == "EMBARGO"
    )


def test_event_cluster_does_not_merge_recurring_title_across_trade_dates() -> None:
    first = _document("first", "2026-01-02", "A사 잠정실적 공시")
    second = replace(first, document_id="second", effective_trade_date="2026-04-02")

    clusters = assign_event_clusters([first, second])

    assert clusters["first"] != clusters["second"]


def test_sampling_excludes_multi_event_stock_days_and_keeps_one_cluster_row() -> None:
    rows = [
        _candidate("a", "cluster-1", "005930", "2026-01-02", "짧은 기사"),
        _candidate("b", "cluster-1", "005930", "2026-01-02", "더 긴 동일 이벤트 기사"),
        _candidate("c", "cluster-2", "000660", "2026-01-02", "첫 번째 이벤트"),
        _candidate("d", "cluster-3", "000660", "2026-01-02", "두 번째 이벤트"),
    ]

    selected = select_unconfounded_representatives(rows)

    assert [row["document_id"] for row in selected] == ["b"]


def _candidate(
    document_id: str,
    cluster_id: str,
    stock_code: str,
    trade_date: str,
    text: str,
) -> dict[str, str]:
    return {
        "document_id": document_id,
        "event_cluster_id": cluster_id,
        "stock_code": stock_code,
        "effective_trade_date": trade_date,
        "text": text,
    }


def _document(document_id: str, trade_date: str, title: str) -> CanonicalDocument:
    return CanonicalDocument(
        document_id=document_id,
        provider="naver-news",
        source_type="NEWS",
        title=title,
        snippet="",
        full_text="",
        source_url=f"https://example.com/{document_id}",
        content_hash=document_id,
        published_at_utc=f"{trade_date}T00:00:00+00:00",
        published_at_kst=f"{trade_date}T09:00:00+09:00",
        published_precision="MINUTE",
        market_session="PRE_MARKET",
        effective_trade_date=trade_date,
    )


def test_source_manifest_uses_logical_path_for_external_symlink_target(
    tmp_path: Path,
    monkeypatch,
) -> None:
    build_k_fnspid = _load_build_script()
    project_root = tmp_path / "worktree"
    source_path = project_root / "data/raw/collected_alerts.jsonl"
    external_file = tmp_path / "main/data/raw/collected_alerts.part-00001.jsonl"
    monkeypatch.setattr(build_k_fnspid, "PROJECT_ROOT", project_root)

    assert build_k_fnspid._source_display_path(external_file, source_path) == (
        "data/raw/collected_alerts.part-00001.jsonl"
    )


def _load_build_script() -> ModuleType:
    path = Path("scripts/build_k_fnspid.py")
    spec = importlib.util.spec_from_file_location("build_k_fnspid_for_test", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_impact_text_ablation_removes_only_selected_features() -> None:
    training = _load_impact_training_script()
    document = {
        "title": "삼성전자 실적",
        "snippet": "영업이익 증가",
        "full_text": "공시 전문",
        "source_type": "DISCLOSURE",
    }
    entity = {"stock_name": "삼성전자"}

    full = training._impact_text(
        document,
        entity,
        include_full_text=True,
        include_source_prefix=True,
    )
    title_only = training._impact_text(
        document,
        entity,
        include_full_text=False,
        include_source_prefix=True,
    )
    no_source = training._impact_text(
        document,
        entity,
        include_full_text=True,
        include_source_prefix=False,
    )

    assert full.startswith("[SOURCE=DISCLOSURE]")
    assert "공시 전문" in full
    assert "공시 전문" not in title_only
    assert not no_source.startswith("[SOURCE=")


def _load_impact_training_script() -> ModuleType:
    path = Path("scripts/train_k_fnspid_impact_model.py")
    spec = importlib.util.spec_from_file_location("train_k_fnspid_impact_model", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
