import json
from pathlib import Path

from hannah_montana_ai.training.stock_curation import (
    build_stock_gold_review_batches,
    build_stock_training_candidates,
    candidate_review_key,
    promote_approved_stock_gold_reviews,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, write_stock_universe


def test_stock_training_candidate_queue_is_broad_and_review_gated() -> None:
    report = json.loads(Path("reports/stock-training-candidate-report.json").read_text())
    rows = _read_jsonl(Path("data/curation/stock_training_candidate_queue.jsonl"))
    stock_codes = {row["stock_code"] for row in rows}

    assert report["schema_version"] == "stock-curation-report/v1"
    assert report["candidate_count"] == len(rows)
    assert report["candidate_count"] >= 5_000
    assert report["candidate_stock_count"] >= 2_000
    assert len(stock_codes) == report["candidate_stock_count"]
    assert report["coverage_gate"]["status"] == "pass"
    assert {row["curation_status"] for row in rows} == {"needs_human_review"}
    assert all(row["stock_code"] and row["stock_name"] for row in rows)
    assert all(row["original_url"].startswith("http") for row in rows)


def test_build_stock_training_candidates_balances_by_stock_and_label(tmp_path: Path) -> None:
    universe_path = tmp_path / "universe.csv"
    raw_path = tmp_path / "raw.jsonl"
    write_stock_universe(
        universe_path,
        [
            StockUniverseEntry("005930", "삼성전자"),
            StockUniverseEntry("000660", "SK하이닉스"),
        ],
    )
    _write_jsonl(
        raw_path,
        [
            _raw("삼성전자 대규모 공급계약 체결", "삼성전자 수주 확대"),
            _raw("삼성전자 추가 공급계약 체결", "삼성전자 계약 확대"),
            _raw("삼성전자 세번째 공급계약 체결", "삼성전자 납품 확대"),
            _raw("SK하이닉스 상장폐지 우려", "SK하이닉스 거래정지 가능성"),
            _raw("SK하이닉스 일반 시황", "코스피 상승"),
        ],
    )

    result = build_stock_training_candidates(
        raw_alert_path=raw_path,
        stock_universe_path=universe_path,
        per_stock_label_quota=1,
        minimum_signal_score=3,
        minimum_stock_count=2,
    )

    assert result.report["coverage_gate"]["status"] == "pass"
    assert result.report["candidate_stock_count"] == 2
    assert result.report["label_distribution"] == {"CONTRACT": 1, "RISK": 1}
    assert [candidate.stock_code for candidate in result.candidates] == ["000660", "005930"]


def test_candidate_review_key_is_stable_and_keeps_stock_boundary() -> None:
    rows = _read_jsonl(Path("data/curation/stock_training_candidate_queue.jsonl"))
    first = rows[0]
    first_key = candidate_review_key_from_dict(first)
    second_key = candidate_review_key_from_dict(first | {"stock_code": "999999"})

    assert first_key == candidate_review_key_from_dict(first)
    assert first_key != second_key


def test_stock_gold_review_batches_are_balanced_and_not_promoted() -> None:
    report = json.loads(Path("reports/stock-gold-review-batch-report.json").read_text())
    training_rows = _read_jsonl(
        Path("data/curation/stock_gold_training_review_batch.jsonl")
    )
    evaluation_rows = _read_jsonl(
        Path("data/curation/stock_gold_evaluation_review_batch.jsonl")
    )
    training_stocks = {row["stock_code"] for row in training_rows}
    evaluation_stocks = {row["stock_code"] for row in evaluation_rows}

    assert report["schema_version"] == "stock-gold-review-report/v1"
    assert report["training_review"]["status"] == "pass"
    assert report["evaluation_review"]["status"] == "pass"
    assert report["training_review"]["actual_stock_count"] == 300
    assert report["evaluation_review"]["actual_stock_count"] == 100
    assert report["disjoint_stock_check"]["status"] == "pass"
    assert training_stocks.isdisjoint(evaluation_stocks)
    assert {row["review_status"] for row in training_rows} == {"needs_human_review"}
    assert {row["review_status"] for row in evaluation_rows} == {"needs_human_review"}
    assert len(report["training_review"]["label_distribution"]) >= 7
    assert len(report["evaluation_review"]["label_distribution"]) >= 7
    assert "not supervised or gold" in report["promotion_policy"]


def test_build_stock_gold_review_batches_excludes_existing_and_splits_stocks(
    tmp_path: Path,
) -> None:
    candidate_path = tmp_path / "candidates.jsonl"
    training_path = tmp_path / "training.jsonl"
    evaluation_path = tmp_path / "evaluation.jsonl"
    _write_jsonl(
        candidate_path,
        [
            _candidate("000001", "후보1", "CONTRACT"),
            _candidate("000002", "후보2", "RISK"),
            _candidate("000003", "후보3", "EARNINGS"),
            _candidate("000004", "후보4", "MACRO"),
            _candidate("000005", "후보5", "CAPITAL_ACTION"),
        ],
    )
    _write_jsonl(training_path, [{"stock_code": "000001"}])
    _write_jsonl(evaluation_path, [{"stock_code": "000002"}])

    result = build_stock_gold_review_batches(
        candidate_path=candidate_path,
        training_paths=[training_path],
        evaluation_paths=[evaluation_path],
        training_stock_target=2,
        evaluation_stock_target=1,
    )

    training_stocks = {row.stock_code for row in result.training_rows}
    evaluation_stocks = {row.stock_code for row in result.evaluation_rows}

    assert training_stocks.isdisjoint({"000001", "000002"})
    assert evaluation_stocks.isdisjoint({"000001", "000002"})
    assert training_stocks.isdisjoint(evaluation_stocks)
    assert result.report["training_review"]["status"] == "pass"
    assert result.report["evaluation_review"]["status"] == "pass"
    assert result.report["promotion_policy"].endswith("human_review_approved")


def test_committed_stock_gold_review_batches_do_not_promote_without_approval(
    tmp_path: Path,
) -> None:
    result = promote_approved_stock_gold_reviews(
        training_review_path=Path("data/curation/stock_gold_training_review_batch.jsonl"),
        evaluation_review_path=Path(
            "data/curation/stock_gold_evaluation_review_batch.jsonl"
        ),
        training_output_path=tmp_path / "training_gold.jsonl",
        evaluation_output_path=tmp_path / "evaluation_gold.jsonl",
    )

    assert result.training_rows == []
    assert result.evaluation_rows == []
    assert result.report["training_promotion"]["approved_row_count"] == 0
    assert result.report["evaluation_promotion"]["approved_row_count"] == 0
    assert result.report["promotion_policy"].startswith("only human_review_approved")
    assert (tmp_path / "training_gold.jsonl").read_text(encoding="utf-8") == ""
    assert (tmp_path / "evaluation_gold.jsonl").read_text(encoding="utf-8") == ""


def test_promote_stock_gold_reviews_writes_only_human_approved_rows(
    tmp_path: Path,
) -> None:
    training_review_path = tmp_path / "training_review.jsonl"
    evaluation_review_path = tmp_path / "evaluation_review.jsonl"
    training_output_path = tmp_path / "training_gold.jsonl"
    evaluation_output_path = tmp_path / "evaluation_gold.jsonl"
    _write_jsonl(
        training_review_path,
        [
            _review_row("000001", "학습승인", "CONTRACT", "training", "human_review_approved"),
            _review_row("000002", "학습대기", "RISK", "training", "needs_human_review"),
            _review_row("000003", "분리오류", "MACRO", "evaluation", "human_review_approved"),
        ],
    )
    _write_jsonl(
        evaluation_review_path,
        [
            _review_row("000004", "평가승인", "EARNINGS", "evaluation", "human_review_approved"),
            _review_row("000005", "평가대기", "RISK", "evaluation", "needs_human_review"),
        ],
    )

    result = promote_approved_stock_gold_reviews(
        training_review_path=training_review_path,
        evaluation_review_path=evaluation_review_path,
        training_output_path=training_output_path,
        evaluation_output_path=evaluation_output_path,
    )
    training_rows = _read_jsonl(training_output_path)
    evaluation_rows = _read_jsonl(evaluation_output_path)

    assert [row["stock_code"] for row in training_rows] == ["000001"]
    assert [row["stock_code"] for row in evaluation_rows] == ["000004"]
    assert training_rows[0]["source_review_status"] == "human_review_approved"
    assert evaluation_rows[0]["source_review_split"] == "evaluation"
    assert result.report["training_promotion"]["promoted_stock_count"] == 1
    assert result.report["evaluation_promotion"]["promoted_stock_count"] == 1
    assert result.report["disjoint_stock_check"]["status"] == "pass"


def candidate_review_key_from_dict(row: dict[str, object]) -> str:
    from hannah_montana_ai.training.stock_curation import StockTrainingCandidate

    return candidate_review_key(
        StockTrainingCandidate(
            text=str(row["text"]),
            tags=list(row["tags"]),  # type: ignore[arg-type]
            sentiment=str(row["sentiment"]),
            importance=str(row["importance"]),
            source_type=str(row["source_type"]),
            stock_code=str(row["stock_code"]),
            stock_name=str(row["stock_name"]),
            primary_label=str(row["primary_label"]),
            signal_score=int(row["signal_score"]),
            original_url=str(row["original_url"]),
            provider=str(row["provider"]),
            content_hash=str(row["content_hash"]),
            curation_status=str(row["curation_status"]),
        )
    )


def _raw(title: str, snippet: str) -> dict[str, str]:
    return {
        "source_type": "NEWS",
        "title": title,
        "snippet": snippet,
        "original_url": f"https://example.com/{title}",
        "published_at": "2026-06-05T00:00:00+00:00",
        "provider": "test",
    }


def _candidate(stock_code: str, stock_name: str, primary_label: str) -> dict[str, object]:
    return {
        "text": f"{stock_name} {primary_label} 검수 후보",
        "tags": [primary_label],
        "sentiment": "NEUTRAL",
        "importance": "HIGH",
        "source_type": "NEWS",
        "stock_code": stock_code,
        "stock_name": stock_name,
        "primary_label": primary_label,
        "signal_score": 5,
        "original_url": f"https://example.com/{stock_code}",
        "provider": "test",
        "content_hash": stock_code,
        "curation_status": "needs_human_review",
    }


def _review_row(
    stock_code: str,
    stock_name: str,
    primary_label: str,
    intended_split: str,
    review_status: str,
) -> dict[str, object]:
    row = _candidate(stock_code, stock_name, primary_label)
    return {
        **row,
        "review_key": f"review-{stock_code}",
        "intended_split": intended_split,
        "review_status": review_status,
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
