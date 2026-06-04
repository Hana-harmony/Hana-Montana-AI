import json
from pathlib import Path

from hannah_montana_ai.training.dataset import LabeledAlert
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
    assert pseudo_coverage["stock_candidate_event_training_sample_count"] == 400
    assert pseudo_coverage["stock_candidate_event_training_stock_count"] == 400
    assert pseudo_coverage["stock_candidate_per_stock_quota"] == 1
    assert pseudo_coverage["effective_event_training_stock_count_lower_bound"] == 400
    assert pseudo_coverage["stock_candidate_label_distribution"]["RISK"] == 200
    assert pseudo_coverage["stock_candidate_label_distribution"]["CONTRACT"] == 200


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


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
