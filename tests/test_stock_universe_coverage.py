import json
from pathlib import Path

from hannah_montana_ai.training.dataset import LabeledAlert
from hannah_montana_ai.training.stock_collection_plan import (
    build_stock_collection_shard_plan,
    load_stock_collection_plan_queries,
    write_stock_collection_shard_plan,
)
from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    StockUniverseMatcher,
    attach_stock_metadata,
    build_stock_coverage_report,
    build_stock_news_queries,
    load_stock_universe,
    write_stock_universe,
)


def test_stock_universe_file_covers_thousands_of_korean_stocks() -> None:
    entries = load_stock_universe(Path("data/reference/korea_stock_universe.csv"))

    assert len(entries) >= 3_000
    assert any(stock.stock_code == "005930" and stock.stock_name == "삼성전자" for stock in entries)
    assert all(len(stock.stock_code) == 6 for stock in entries)


def test_stock_coverage_report_tracks_event_model_pseudo_training_coverage() -> None:
    report = json.loads(Path("reports/stock-coverage-report.json").read_text())
    pseudo_coverage = report["event_model_pseudo_training_coverage"]

    assert report["coverage_gates"]["overall_status"] == "fail"
    assert pseudo_coverage["status"] == "promoted_to_event_student_training"
    assert pseudo_coverage["source_path"] == "reports/ml-training-report.json"
    assert pseudo_coverage["stock_candidate_event_training_sample_count"] == 704
    assert pseudo_coverage["stock_candidate_event_training_stock_count"] == 704
    assert pseudo_coverage["stock_candidate_per_stock_quota"] == 1
    assert pseudo_coverage["effective_event_training_stock_count_lower_bound"] == 704
    assert pseudo_coverage["stock_candidate_label_distribution"]["RISK"] == 258
    assert pseudo_coverage["stock_candidate_label_distribution"]["CONTRACT"] == 239
    assert pseudo_coverage["stock_candidate_label_distribution"]["CAPITAL_ACTION"] == 120


def test_stock_collection_shard_plan_targets_missing_candidate_coverage() -> None:
    report = json.loads(Path("reports/stock-collection-shard-plan.json").read_text())
    rows = _read_jsonl(Path("data/curation/stock_collection_shard_plan.jsonl"))

    assert report["schema_version"] == "stock-collection-shard-report/v1"
    assert report["row_schema_version"] == "stock-collection-shard-row/v1"
    assert report["planned_stock_count"] == len(rows)
    assert report["planned_stock_count"] == 877
    assert report["shard_size"] == 100
    assert report["shard_count"] == 9
    assert report["planned_query_count"] == report["planned_stock_count"] * len(
        report["intents"]
    )
    assert report["priority_distribution"]["no_raw_no_candidate"] == 702
    assert report["priority_distribution"]["raw_without_candidate"] == 175
    assert all(row["candidate_count"] == 0 for row in rows)
    assert all(row["training_gold_count"] == 0 for row in rows)
    assert all(row["evaluation_gold_count"] == 0 for row in rows)
    assert all(len(row["naver_queries"]) == len(report["intents"]) for row in rows)
    assert "human_review_approved" in report["collection_policy"]


def test_build_stock_collection_shard_plan_prioritizes_no_raw_stocks(
    tmp_path: Path,
) -> None:
    universe_path = tmp_path / "universe.csv"
    raw_path = tmp_path / "raw.jsonl"
    candidate_path = tmp_path / "candidate.jsonl"
    training_path = tmp_path / "training.jsonl"
    evaluation_path = tmp_path / "evaluation.jsonl"
    write_stock_universe(
        universe_path,
        [
            StockUniverseEntry("000001", "후보없음"),
            StockUniverseEntry("000002", "원시있음"),
            StockUniverseEntry("000003", "검수후보"),
            StockUniverseEntry("000004", "학습골드"),
            StockUniverseEntry("000005", "평가골드"),
        ],
    )
    _write_jsonl(raw_path, [_raw_alert("원시있음 실적 개선")])
    _write_jsonl(candidate_path, [{"stock_code": "000003"}])
    _write_jsonl(training_path, [_labeled_alert("000004", "학습골드")])
    _write_jsonl(evaluation_path, [_labeled_alert("000005", "평가골드")])

    result = build_stock_collection_shard_plan(
        stock_universe_path=universe_path,
        raw_alert_path=raw_path,
        candidate_path=candidate_path,
        training_paths=[training_path],
        evaluation_paths=[evaluation_path],
        shard_size=1,
        intents=("실적", "공시"),
    )

    assert [row.stock_code for row in result.rows] == ["000001", "000002"]
    assert [row.priority_bucket for row in result.rows] == [
        "no_raw_no_candidate",
        "raw_without_candidate",
    ]
    assert [row.shard_index for row in result.rows] == [0, 1]
    assert result.rows[0].naver_queries == ["후보없음 실적", "후보없음 공시"]
    assert result.report["planned_query_count"] == 4
    assert result.report["next_collection_commands"][0].endswith(
        "--stock-collection-plan-shard-index 0"
    )


def test_load_stock_collection_plan_queries_filters_shard(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.jsonl"
    rows = [
        _plan_row("000001", shard_index=0, queries=["A 실적", "A 공시"]),
        _plan_row("000002", shard_index=1, queries=["B 실적", "A 실적"]),
    ]
    write_stock_collection_shard_plan(plan_path, rows)

    assert load_stock_collection_plan_queries(plan_path, shard_index=0) == [
        "A 실적",
        "A 공시",
    ]
    assert load_stock_collection_plan_queries(plan_path) == [
        "A 실적",
        "A 공시",
        "B 실적",
    ]


def test_stock_universe_news_queries_expand_by_stock_intent() -> None:
    entries = [
        StockUniverseEntry("005930", "삼성전자"),
        StockUniverseEntry("000660", "SK하이닉스"),
    ]

    queries = build_stock_news_queries(entries, intents=("실적", "공시"))

    assert queries == [
        "삼성전자 실적",
        "삼성전자 공시",
        "SK하이닉스 실적",
        "SK하이닉스 공시",
    ]


def test_stock_matcher_ignores_ambiguous_short_names_but_keeps_stock_codes() -> None:
    matcher = StockUniverseMatcher(
        [
            StockUniverseEntry("003600", "SK"),
            StockUniverseEntry("005930", "삼성전자"),
        ]
    )

    assert matcher.match("SK그룹 투자 뉴스") is None
    assert matcher.match("003600 주요사항보고서") is not None
    assert matcher.match("삼성전자 잠정실적 공시").stock_code == "005930"  # type: ignore[union-attr]


def test_attach_stock_metadata_uses_universe_matcher() -> None:
    matcher = StockUniverseMatcher([StockUniverseEntry("005930", "삼성전자")])
    sample = LabeledAlert(
        text="삼성전자 2분기 영업이익 증가",
        tags=["EARNINGS"],
        sentiment="POSITIVE",
        importance="HIGH",
    )

    enriched = attach_stock_metadata(sample, matcher)

    assert enriched.stock_code == "005930"
    assert enriched.stock_name == "삼성전자"


def test_stock_coverage_report_tracks_raw_training_and_evaluation(tmp_path: Path) -> None:
    universe_path = tmp_path / "universe.csv"
    training_path = tmp_path / "training.jsonl"
    evaluation_path = tmp_path / "evaluation.jsonl"
    raw_path = tmp_path / "raw.jsonl"
    write_stock_universe(
        universe_path,
        [
            StockUniverseEntry("005930", "삼성전자"),
            StockUniverseEntry("000660", "SK하이닉스"),
            StockUniverseEntry("035420", "NAVER"),
        ],
    )
    _write_jsonl(
        training_path,
        [
            {
                "text": "삼성전자 실적 개선",
                "tags": ["EARNINGS"],
                "sentiment": "POSITIVE",
                "importance": "HIGH",
                "source_type": "NEWS",
                "stock_code": "005930",
                "stock_name": "삼성전자",
            }
        ],
    )
    _write_jsonl(
        evaluation_path,
        [
            {
                "text": "SK하이닉스 공급계약",
                "tags": ["CONTRACT"],
                "sentiment": "POSITIVE",
                "importance": "HIGH",
                "source_type": "NEWS",
                "stock_code": "000660",
                "stock_name": "SK하이닉스",
            }
        ],
    )
    _write_jsonl(
        raw_path,
        [
            _raw_alert("삼성전자 실적 개선"),
            _raw_alert("NAVER 자사주 매입"),
        ],
    )

    report = build_stock_coverage_report(
        universe_path=universe_path,
        training_paths=[training_path],
        evaluation_paths=[evaluation_path],
        raw_alert_path=raw_path,
        minimum_universe_count=3,
        minimum_real_data_stock_count=1,
    )

    assert report.universe_count == 3
    assert report.training_stock_count == 1
    assert report.evaluation_stock_count == 1
    assert report.raw_matched_stock_count == 2
    assert report.coverage_gates["overall_status"] == "pass"


def _raw_alert(title: str) -> dict[str, str]:
    return {
        "source_type": "NEWS",
        "title": title,
        "snippet": "",
        "original_url": f"https://example.com/{title}",
        "published_at": "2026-06-05T00:00:00+00:00",
        "provider": "test",
    }


def _labeled_alert(stock_code: str, stock_name: str) -> dict[str, object]:
    return {
        "text": f"{stock_name} 실적 개선",
        "tags": ["EARNINGS"],
        "sentiment": "POSITIVE",
        "importance": "HIGH",
        "source_type": "NEWS",
        "stock_code": stock_code,
        "stock_name": stock_name,
    }


def _plan_row(
    stock_code: str,
    shard_index: int,
    queries: list[str],
):
    from hannah_montana_ai.training.stock_collection_plan import (
        STOCK_COLLECTION_SHARD_ROW_SCHEMA_VERSION,
        StockCollectionShardRow,
    )

    return StockCollectionShardRow(
        schema_version=STOCK_COLLECTION_SHARD_ROW_SCHEMA_VERSION,
        stock_code=stock_code,
        stock_name=f"종목{stock_code}",
        stock_name_en="",
        market="",
        dart_corp_code="",
        collection_priority=10,
        priority_bucket="no_raw_no_candidate",
        shard_index=shard_index,
        shard_size=1,
        raw_match_count=0,
        candidate_count=0,
        training_gold_count=0,
        evaluation_gold_count=0,
        naver_queries=queries,
    )


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
