import json
from pathlib import Path

from hannah_montana_ai.training.active_review import (
    build_stock_gold_active_review_report,
    build_stock_gold_coverage_active_review_packet,
    build_stock_gold_coverage_active_review_report,
)
from hannah_montana_ai.training.coverage_planner import build_stock_gold_coverage_plan
from hannah_montana_ai.training.stock_curation import (
    build_stock_gold_review_batches,
    build_stock_training_candidates,
    candidate_review_key,
    promote_approved_stock_gold_coverage_reviews,
    promote_approved_stock_gold_reviews,
    validate_stock_gold_review_batches,
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
    assert all("reviewer_id" in row for row in training_rows)
    assert all("final_tags" in row for row in evaluation_rows)
    assert report["review_approval_requirements"]["required_status"] == (
        "human_review_approved"
    )
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
    assert "reviewer metadata and final labels" in result.report["promotion_policy"]
    assert (tmp_path / "training_gold.jsonl").read_text(encoding="utf-8") == ""
    assert (tmp_path / "evaluation_gold.jsonl").read_text(encoding="utf-8") == ""


def test_stock_gold_promotion_report_tracks_zero_approved_committed_batch() -> None:
    report = json.loads(Path("reports/stock-gold-promotion-report.json").read_text())

    assert report["schema_version"] == "stock-gold-promotion-report/v1"
    assert report["training_promotion"]["review_row_count"] == 300
    assert report["training_promotion"]["approved_row_count"] == 0
    assert report["training_promotion"]["promoted_row_count"] == 0
    assert report["evaluation_promotion"]["review_row_count"] == 100
    assert report["evaluation_promotion"]["approved_row_count"] == 0
    assert "reviewer metadata and final labels" in report["promotion_policy"]


def test_stock_gold_coverage_promotion_report_tracks_zero_approved_packet() -> None:
    report = json.loads(Path("reports/stock-gold-coverage-promotion-report.json").read_text())

    assert report["schema_version"] == "stock-gold-coverage-promotion-report/v1"
    assert report["training_promotion"]["review_row_count"] == 1_500
    assert report["training_promotion"]["approved_row_count"] == 0
    assert report["training_promotion"]["promoted_row_count"] == 0
    assert report["training_promotion"]["review_wave_distribution"]["0"] == 300
    assert report["training_promotion"]["review_wave_distribution"]["12"] == 100
    assert report["evaluation_promotion"]["review_row_count"] == 500
    assert report["evaluation_promotion"]["review_wave_distribution"]["4"] == 100
    assert report["disjoint_stock_check"]["status"] == "pass"
    assert "human_review_approved" in report["promotion_policy"]


def test_stock_gold_review_validation_report_tracks_current_blocker() -> None:
    report = json.loads(
        Path("reports/stock-gold-review-validation-report.json").read_text()
    )

    assert report["schema_version"] == "stock-gold-review-validation-report/v1"
    assert report["overall_status"] == "fail"
    assert report["training_validation"]["review_row_count"] == 300
    assert report["training_validation"]["eligible_stock_count"] == 0
    assert report["training_validation"]["remaining_stock_count_to_target"] == 300
    assert report["evaluation_validation"]["review_row_count"] == 100
    assert report["evaluation_validation"]["remaining_stock_count_to_target"] == 100
    assert report["approval_requirements"]["required_status"] == (
        "human_review_approved"
    )


def test_stock_gold_active_review_report_prioritizes_model_disagreement() -> None:
    report = json.loads(Path("reports/stock-gold-active-review-report.json").read_text())
    top_training_rows = report["training_review"]["top_priority_rows"]
    top_evaluation_rows = report["evaluation_review"]["top_priority_rows"]

    assert report["schema_version"] == "stock-gold-active-review-report/v1"
    assert report["training_review"]["review_row_count"] == 300
    assert report["evaluation_review"]["review_row_count"] == 100
    assert len(top_training_rows) == 50
    assert len(top_evaluation_rows) == 50
    assert top_training_rows[0]["review_priority_score"] >= top_training_rows[-1][
        "review_priority_score"
    ]
    assert top_training_rows[0]["suggested_tags"]
    assert "reviewer assistance only" in report["review_policy"]


def test_stock_gold_coverage_plan_expands_reviewable_stock_coverage() -> None:
    report = json.loads(Path("reports/stock-gold-coverage-plan-report.json").read_text())
    rows = _read_jsonl(Path("data/curation/stock_gold_coverage_review_plan.jsonl"))
    training_stocks = {
        row["stock_code"] for row in rows if row["intended_split"] == "training"
    }
    evaluation_stocks = {
        row["stock_code"] for row in rows if row["intended_split"] == "evaluation"
    }

    assert report["schema_version"] == "stock-gold-coverage-plan/v1"
    assert len(rows) == 2_000
    assert report["training_plan"]["status"] == "pass"
    assert report["training_plan"]["planned_stock_count"] == 1_500
    assert report["training_plan"]["stage_distribution"] == {
        "additional_coverage_plan": 1_200,
        "current_review_batch": 300,
    }
    assert report["evaluation_plan"]["status"] == "pass"
    assert report["evaluation_plan"]["planned_stock_count"] == 500
    assert report["candidate_coverage_after_full_plan"]["covered_candidate_stock_count"] >= 2_000
    assert report["disjoint_stock_check"]["status"] == "pass"
    assert training_stocks.isdisjoint(evaluation_stocks)
    assert {row["review_status"] for row in rows} == {"needs_human_review"}
    assert all(row["reviewer_id"] == "" for row in rows)
    assert "human_review_approved" in report["review_policy"]


def test_stock_gold_coverage_active_review_packet_enriches_all_plan_rows() -> None:
    report = json.loads(
        Path("reports/stock-gold-coverage-active-review-report.json").read_text()
    )
    packet_rows = _read_jsonl(
        Path("data/curation/stock_gold_coverage_active_review_packet.jsonl")
    )
    training_rows = [
        row for row in packet_rows if row["intended_split"] == "training"
    ]
    evaluation_rows = [
        row for row in packet_rows if row["intended_split"] == "evaluation"
    ]

    assert report["schema_version"] == "stock-gold-coverage-active-review-report/v1"
    assert len(packet_rows) == 2_000
    assert len(training_rows) == 1_500
    assert len(evaluation_rows) == 500
    assert report["training_review"]["review_row_count"] == 1_500
    assert report["training_review"]["review_wave_count"] == 13
    assert report["evaluation_review"]["review_row_count"] == 500
    assert report["evaluation_review"]["review_wave_count"] == 5
    assert len(report["training_review"]["top_priority_rows"]) == 100
    assert set(report["training_review"]["wave_priority_rows"]) == {
        str(wave) for wave in range(13)
    }
    assert {row["review_status"] for row in packet_rows} == {"needs_human_review"}
    assert all(row["suggested_tags"] for row in packet_rows)
    assert all("review_priority_score" in row for row in packet_rows)
    assert all(row["reviewer_id"] == "" for row in packet_rows)
    assert "human_review_approved" in report["review_policy"]


def test_build_stock_gold_coverage_active_review_packet_can_score_small_plan(
    tmp_path: Path,
) -> None:
    coverage_plan_path = tmp_path / "coverage_plan.jsonl"
    _write_jsonl(
        coverage_plan_path,
        [
            _coverage_plan_row("000001", "학습후보", "CONTRACT", "training", 0),
            _coverage_plan_row("000002", "평가후보", "RISK", "evaluation", 1),
        ],
    )

    packet_rows = build_stock_gold_coverage_active_review_packet(
        coverage_plan_path=coverage_plan_path,
        model_path=Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"),
    )
    report = build_stock_gold_coverage_active_review_report(
        coverage_plan_path=coverage_plan_path,
        model_path=Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"),
        top_n_per_split=1,
        top_n_per_wave=1,
    )

    assert len(packet_rows) == 2
    assert {row["review_status"] for row in packet_rows} == {"needs_human_review"}
    assert all(row["suggested_tags"] for row in packet_rows)
    assert packet_rows[0]["schema_version"] == (
        "stock-gold-coverage-active-review-packet/v1"
    )
    assert report["training_review"]["review_row_count"] == 1
    assert report["evaluation_review"]["review_row_count"] == 1
    assert len(report["training_review"]["top_priority_rows"]) == 1
    assert report["training_review"]["top_priority_rows"][0]["review_wave"] == 0


def test_build_stock_gold_coverage_plan_excludes_supervised_and_current_review_stocks(
    tmp_path: Path,
) -> None:
    candidate_path = tmp_path / "candidates.jsonl"
    training_review_path = tmp_path / "training_review.jsonl"
    evaluation_review_path = tmp_path / "evaluation_review.jsonl"
    training_path = tmp_path / "training.jsonl"
    evaluation_path = tmp_path / "evaluation.jsonl"
    _write_jsonl(
        candidate_path,
        [
            _candidate("000001", "기존학습", "CONTRACT"),
            _candidate("000002", "현재학습검수", "RISK"),
            _candidate("000003", "현재평가검수", "EARNINGS"),
            _candidate("000004", "추가학습", "MACRO"),
            _candidate("000005", "추가평가", "CAPITAL_ACTION"),
        ],
    )
    _write_jsonl(training_path, [{"stock_code": "000001"}])
    _write_jsonl(evaluation_path, [])
    _write_jsonl(
        training_review_path,
        [_review_row("000002", "현재학습검수", "RISK", "training", "needs_human_review")],
    )
    _write_jsonl(
        evaluation_review_path,
        [_review_row("000003", "현재평가검수", "EARNINGS", "evaluation", "needs_human_review")],
    )

    result = build_stock_gold_coverage_plan(
        candidate_path=candidate_path,
        training_review_path=training_review_path,
        evaluation_review_path=evaluation_review_path,
        training_paths=[training_path],
        evaluation_paths=[evaluation_path],
        training_stock_target=2,
        evaluation_stock_target=2,
        review_wave_size=1,
    )
    rows = [row.to_dict() for row in result.rows]
    training_stocks = {
        row["stock_code"] for row in rows if row["intended_split"] == "training"
    }
    evaluation_stocks = {
        row["stock_code"] for row in rows if row["intended_split"] == "evaluation"
    }

    assert "000001" not in training_stocks
    assert "000001" not in evaluation_stocks
    assert "000002" in training_stocks
    assert "000003" in evaluation_stocks
    assert len(training_stocks) == 2
    assert len(evaluation_stocks) == 2
    assert training_stocks | evaluation_stocks == {"000002", "000003", "000004", "000005"}
    assert result.report["disjoint_stock_check"]["status"] == "pass"
    assert {row["review_status"] for row in rows} == {"needs_human_review"}


def test_build_stock_gold_active_review_report_can_limit_top_rows() -> None:
    report = build_stock_gold_active_review_report(
        training_review_path=Path("data/curation/stock_gold_training_review_batch.jsonl"),
        evaluation_review_path=Path(
            "data/curation/stock_gold_evaluation_review_batch.jsonl"
        ),
        model_path=Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"),
        top_n_per_split=3,
    )

    assert len(report["training_review"]["top_priority_rows"]) == 3
    assert len(report["evaluation_review"]["top_priority_rows"]) == 3
    assert report["training_review"]["disagreement_count_by_reason"]
    assert report["model_version"].startswith("financial-ml-tfidf-logreg-")


def test_validate_stock_gold_review_batches_passes_when_targets_are_eligible(
    tmp_path: Path,
) -> None:
    training_review_path = tmp_path / "training_review.jsonl"
    evaluation_review_path = tmp_path / "evaluation_review.jsonl"
    _write_jsonl(
        training_review_path,
        [
            _review_row("000001", "학습승인", "CONTRACT", "training", "human_review_approved"),
        ],
    )
    _write_jsonl(
        evaluation_review_path,
        [
            _review_row("000002", "평가승인", "RISK", "evaluation", "human_review_approved"),
        ],
    )

    result = validate_stock_gold_review_batches(
        training_review_path=training_review_path,
        evaluation_review_path=evaluation_review_path,
        training_stock_target=1,
        evaluation_stock_target=1,
    )

    assert result.report["overall_status"] == "pass"
    assert result.report["training_validation"]["eligible_stock_count"] == 1
    assert result.report["evaluation_validation"]["eligible_stock_count"] == 1
    assert result.report["disjoint_stock_check"]["status"] == "pass"


def test_validate_stock_gold_review_batches_reports_invalid_approved_rows(
    tmp_path: Path,
) -> None:
    training_review_path = tmp_path / "training_review.jsonl"
    evaluation_review_path = tmp_path / "evaluation_review.jsonl"
    _write_jsonl(
        training_review_path,
        [
            _review_row(
                "000001",
                "검수시각오류",
                "CONTRACT",
                "training",
                "human_review_approved",
                reviewed_at="bad-time",
            ),
        ],
    )
    _write_jsonl(evaluation_review_path, [])

    result = validate_stock_gold_review_batches(
        training_review_path=training_review_path,
        evaluation_review_path=evaluation_review_path,
        training_stock_target=1,
        evaluation_stock_target=1,
    )

    assert result.report["overall_status"] == "fail"
    assert result.report["training_validation"]["eligible_row_count"] == 0
    assert result.report["training_validation"]["blocked_approved_count_by_reason"] == {
        "invalid_reviewed_at": 1
    }


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
    assert training_rows[0]["tags"] == ["CONTRACT"]
    assert training_rows[0]["sentiment"] == "NEUTRAL"
    assert training_rows[0]["importance"] == "HIGH"
    assert training_rows[0]["reviewer_id"] == "analyst-001"
    assert training_rows[0]["source_review_status"] == "human_review_approved"
    assert evaluation_rows[0]["source_review_split"] == "evaluation"
    assert result.report["training_promotion"]["promoted_stock_count"] == 1
    assert result.report["evaluation_promotion"]["promoted_stock_count"] == 1
    assert result.report["disjoint_stock_check"]["status"] == "pass"


def test_promote_stock_gold_coverage_reviews_preserves_packet_lineage(
    tmp_path: Path,
) -> None:
    coverage_packet_path = tmp_path / "coverage_packet.jsonl"
    training_output_path = tmp_path / "training_gold.jsonl"
    evaluation_output_path = tmp_path / "evaluation_gold.jsonl"
    _write_jsonl(
        coverage_packet_path,
        [
            _coverage_packet_row(
                "000001",
                "학습승인",
                "CONTRACT",
                "training",
                2,
                "human_review_approved",
            ),
            _coverage_packet_row(
                "000002",
                "학습대기",
                "RISK",
                "training",
                3,
                "needs_human_review",
            ),
            _coverage_packet_row(
                "000003",
                "평가승인",
                "EARNINGS",
                "evaluation",
                1,
                "human_review_approved",
            ),
        ],
    )

    result = promote_approved_stock_gold_coverage_reviews(
        coverage_review_packet_path=coverage_packet_path,
        training_output_path=training_output_path,
        evaluation_output_path=evaluation_output_path,
    )
    training_rows = _read_jsonl(training_output_path)
    evaluation_rows = _read_jsonl(evaluation_output_path)

    assert [row["stock_code"] for row in training_rows] == ["000001"]
    assert [row["stock_code"] for row in evaluation_rows] == ["000003"]
    assert training_rows[0]["source_review_wave"] == 2
    assert training_rows[0]["source_review_stage"] == "additional_coverage_plan"
    assert training_rows[0]["source_model_suggested_tags"] == ["CONTRACT"]
    assert training_rows[0]["source_review_priority_score"] == 123.45
    assert result.report["training_promotion"]["promoted_stock_count"] == 1
    assert result.report["training_promotion"]["promoted_wave_distribution"] == {"2": 1}
    assert result.report["evaluation_promotion"]["promoted_wave_distribution"] == {"1": 1}
    assert result.report["disjoint_stock_check"]["status"] == "pass"


def test_promote_stock_gold_reviews_rejects_unattested_approved_rows(
    tmp_path: Path,
) -> None:
    training_review_path = tmp_path / "training_review.jsonl"
    evaluation_review_path = tmp_path / "evaluation_review.jsonl"
    training_output_path = tmp_path / "training_gold.jsonl"
    evaluation_output_path = tmp_path / "evaluation_gold.jsonl"
    _write_jsonl(
        training_review_path,
        [
            _review_row(
                "000001",
                "검수자없음",
                "CONTRACT",
                "training",
                "human_review_approved",
                reviewer_id="",
            ),
            _review_row(
                "000002",
                "최종라벨없음",
                "RISK",
                "training",
                "human_review_approved",
                final_tags=[],
            ),
        ],
    )
    _write_jsonl(evaluation_review_path, [])

    result = promote_approved_stock_gold_reviews(
        training_review_path=training_review_path,
        evaluation_review_path=evaluation_review_path,
        training_output_path=training_output_path,
        evaluation_output_path=evaluation_output_path,
    )

    assert _read_jsonl(training_output_path) == []
    assert result.report["training_promotion"]["approved_row_count"] == 2
    assert result.report["training_promotion"]["promoted_row_count"] == 0
    assert result.report["training_promotion"]["rejected_approved_count_by_reason"] == {
        "missing_final_tags": 1,
        "missing_reviewer_id": 1,
    }


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
    reviewer_id: str = "analyst-001",
    reviewed_at: str = "2026-06-05T00:00:00+09:00",
    final_tags: list[str] | None = None,
) -> dict[str, object]:
    row = _candidate(stock_code, stock_name, primary_label)
    return {
        **row,
        "review_key": f"review-{stock_code}",
        "intended_split": intended_split,
        "review_status": review_status,
        "reviewer_id": reviewer_id,
        "reviewed_at": reviewed_at,
        "review_notes": "테스트 검수",
        "final_tags": final_tags if final_tags is not None else [primary_label],
        "final_sentiment": row["sentiment"],
        "final_importance": row["importance"],
    }


def _coverage_plan_row(
    stock_code: str,
    stock_name: str,
    primary_label: str,
    intended_split: str,
    review_wave: int,
) -> dict[str, object]:
    row = _review_row(
        stock_code,
        stock_name,
        primary_label,
        intended_split,
        "needs_human_review",
    )
    return {
        **row,
        "schema_version": "stock-gold-coverage-plan-row/v1",
        "review_wave": review_wave,
        "review_stage": "current_review_batch" if review_wave == 0 else "additional_coverage_plan",
        "review_reason": (
            "already_exported_for_human_review"
            if review_wave == 0
            else "missing_supervised_stock_coverage"
        ),
    }


def _coverage_packet_row(
    stock_code: str,
    stock_name: str,
    primary_label: str,
    intended_split: str,
    review_wave: int,
    review_status: str,
) -> dict[str, object]:
    row = _coverage_plan_row(
        stock_code,
        stock_name,
        primary_label,
        intended_split,
        review_wave,
    )
    return {
        **row,
        "schema_version": "stock-gold-coverage-active-review-packet/v1",
        "review_status": review_status,
        "reviewer_id": "analyst-001",
        "reviewed_at": "2026-06-05T00:00:00+09:00",
        "review_notes": "테스트 검수",
        "final_tags": [primary_label],
        "final_sentiment": "NEUTRAL",
        "final_importance": "HIGH",
        "suggested_tags": [primary_label],
        "suggested_sentiment": "NEUTRAL",
        "suggested_importance": "HIGH",
        "event_top_label": primary_label,
        "event_confidence": 0.91,
        "event_margin": 0.44,
        "sentiment_confidence": 0.82,
        "importance_confidence": 0.78,
        "disagreement_reasons": [],
        "review_priority_score": 123.45,
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
