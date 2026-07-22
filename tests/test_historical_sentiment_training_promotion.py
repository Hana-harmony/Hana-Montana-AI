from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from tests.sentiment_review_provenance_fixture import (
    build_verified_dual_review_provenance,
)


def _load_promoter() -> Any:
    path = Path("scripts/promote_historical_sentiment_training_gold.py")
    spec = importlib.util.spec_from_file_location(
        "promote_historical_sentiment_training_gold", path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.promote_historical_training_gold


promote_historical_training_gold = _load_promoter()


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _review(index: int, *, source: str, partition: str) -> dict[str, Any]:
    return {
        "schema_version": "k-fnspid-sentiment-review-row/v1",
        "dataset_version": "K-FNSPID-v4",
        "codebook_version": "k-fnspid-sentiment-codebook/v1",
        "partition": partition,
        "document_id": f"{source.lower()}-{index}",
        "source_type": source,
        "stock_code": f"{index:06d}",
        "stock_name": f"stock-{index}",
        "text": f"{source} unique text {index}",
        "source_url": f"https://example.test/{source.lower()}/{index}",
        "canonical_url": f"https://example.test/{source.lower()}/{index}",
        "content_hash": f"hash-{source}-{index}",
        "event_cluster_id": f"cluster-{source}-{index}",
        "published_at_kst": "2026-07-01T09:00:00+09:00",
        "effective_trade_date": "2026-07-01",
        "review_status": "NEEDS_BLIND_REVIEW",
        "final_sentiment": "",
        "reviewer_id": "",
        "reviewed_at": "",
        "review_note": "",
    }


def _decision(row: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(UTC).isoformat()
    item_id = f"{row['document_id']}::{row['stock_code']}"

    def reviewer(reviewer_id: str) -> dict[str, Any]:
        return {
            "stage_1": "DIRECTIONAL",
            "stage_2": "POSITIVE",
            "final_sentiment": "POSITIVE",
            "label_evidence": "target-specific benefit",
            "decision_path": "NEUTRAL_DIRECTIONAL_THEN_POLARITY",
            "reviewer_id": reviewer_id,
            "reviewed_at": now,
            "reviewer_type": "CODEX_AI",
            "model_blind": True,
            "market_blind": True,
        }

    return {
        "schema_version": "k-fnspid-sentiment-dual-review-decision/v1",
        "item_id": item_id,
        "reviewer_1": reviewer("reviewer-1"),
        "reviewer_2": reviewer("reviewer-2"),
        "independent_reviewer_count": 2,
        "inter_reviewer_agreement": True,
        "decision_path": "INDEPENDENT_REVIEWER_AGREEMENT",
        "adjudication": None,
        "final_sentiment": "POSITIVE",
        "review_note": "independent agreement",
        "reviewer_id": "reviewer-1+reviewer-2",
        "reviewed_at": now,
        "review_status": "CODEX_REVIEW_APPROVED",
        "reviewer_type": "INDEPENDENT_CODEX_AI",
        "model_blind": True,
        "market_blind": True,
    }


def _unresolved_decision(row: dict[str, Any]) -> dict[str, Any]:
    decision = _decision(row)
    decision["reviewer_2"].update(
        {
            "stage_2": "NEGATIVE",
            "final_sentiment": "NEGATIVE",
            "label_evidence": "input is truncated and direction cannot be confirmed",
        }
    )
    adjudication = {
        "item_id": decision["item_id"],
        "final_sentiment": "UNRESOLVED",
        "adjudication_note": "입력 훼손으로 대상 기업의 방향을 확정할 수 없다.",
        "adjudicator_id": "independent-adjudicator",
        "adjudicated_at": decision["reviewed_at"],
        "adjudication_status": "UNRESOLVED",
    }
    decision.update(
        {
            "inter_reviewer_agreement": False,
            "decision_path": "UNRESOLVED_EXCLUDED",
            "adjudication": adjudication,
            "final_sentiment": "UNRESOLVED",
            "review_note": adjudication["adjudication_note"],
            "reviewer_id": adjudication["adjudicator_id"],
            "review_status": "UNRESOLVED",
        }
    )
    return decision


def _fixture_paths(tmp_path: Path, *, include_unresolved: bool = False) -> dict[str, Path]:
    paths = {
        name: tmp_path / filename
        for name, filename in {
            "review": "review.jsonl",
            "decisions": "decisions.jsonl",
            "news": "news-confirmatory.jsonl",
            "disclosure": "disclosure-confirmatory.jsonl",
            "sampling": "sampling.json",
            "output": "gold.jsonl",
            "report": "report.json",
            "provenance": "dual-review-provenance.json",
        }.items()
    }
    source_rows = [_review(9001, source="DISCLOSURE", partition="HISTORICAL_REVIEW")]
    decisions = [_decision(source_rows[0])]
    if include_unresolved:
        unresolved_row = _review(9002, source="DISCLOSURE", partition="HISTORICAL_REVIEW")
        source_rows.append(unresolved_row)
        decisions.append(_unresolved_decision(unresolved_row))
    _write_jsonl(paths["review"], source_rows)
    _write_jsonl(paths["decisions"], decisions)
    paths["provenance"] = build_verified_dual_review_provenance(
        root=tmp_path,
        review_path=paths["review"],
        final_decisions=decisions,
        final_decisions_path=paths["decisions"],
    )
    _write_jsonl(
        paths["news"],
        [
            _review(index, source="NEWS", partition="CONFIRMATORY_SEALED_TEST_REVIEW")
            for index in range(500)
        ],
    )
    _write_jsonl(
        paths["disclosure"],
        [
            _review(
                index,
                source="DISCLOSURE",
                partition="DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
            )
            for index in range(500)
        ],
    )

    def artifact(path: Path) -> dict[str, Any]:
        raw = path.read_bytes()
        return {"path": str(path), "bytes": len(raw), "sha256": sha256(raw).hexdigest()}

    news_artifact = artifact(paths["news"])
    disclosure_artifact = artifact(paths["disclosure"])
    paths["sampling"].write_text(
        json.dumps(
            {
                "schema_version": ("k-fnspid-sentiment-confirmatory-sealed-sampling-design/v2"),
                "report_role": "UNLABELED_CONFIRMATORY_RESERVATION",
                "generated_at": "2026-07-14T00:00:00+00:00",
                "labels_available_at_reservation": False,
                "candidate_predictions_available": False,
                "partitions": {
                    "CONFIRMATORY_SEALED_TEST_REVIEW": {
                        "source_type": "NEWS",
                        "sample_count": 500,
                        "output": news_artifact,
                    },
                    "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW": {
                        "source_type": "DISCLOSURE",
                        "sample_count": 500,
                        "output": disclosure_artifact,
                    },
                },
                "write_once_commitments": {
                    "CONFIRMATORY_SEALED_TEST_REVIEW": news_artifact,
                    "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW": disclosure_artifact,
                },
                "protected_identity_sets": {
                    "categories": {"historical": {"paths": [artifact(paths["review"])]}}
                },
            }
        ),
        encoding="utf-8",
    )
    return paths


def _promote(paths: dict[str, Path], *, purpose: str = "TRAINING") -> dict[str, Any]:
    return promote_historical_training_gold(
        review_path=paths["review"],
        decisions_path=paths["decisions"],
        output_path=paths["output"],
        report_path=paths["report"],
        expected_partition="HISTORICAL_REVIEW",
        expected_source="DISCLOSURE",
        confirmatory_paths=(paths["news"], paths["disclosure"]),
        sampling_design_path=paths["sampling"],
        review_provenance_path=paths["provenance"],
        purpose=purpose,
    )


def test_promotes_training_only_gold_with_confirmatory_disjointness(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    report = _promote(paths)
    row = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["source"]["sample_count"] == 1
    assert report["reclassification"]["eligible_for_superiority_claims"] is False
    assert report["integrity"]["confirmatory_group_overlap_count"] == 0
    assert row["sentiment"] == "POSITIVE"
    assert row["final_sentiment"] == "POSITIVE"
    assert row["training_role"] == "TRAINING_ONLY_NOT_EVALUATION_OR_CLAIM_EVIDENCE"


def test_promotes_development_gold_without_training_role(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    report = _promote(paths, purpose="DEVELOPMENT")
    row = json.loads(paths["output"].read_text(encoding="utf-8"))

    assert report["schema_version"] == "k-fnspid-sentiment-development-promotion/v1"
    assert report["reclassification"]["eligible_for_model_selection"] is True
    assert report["reclassification"]["eligible_for_superiority_claims"] is False
    assert row["partition"] == "HISTORICAL_REVIEW"
    assert row["schema_version"] == "k-fnspid-sentiment-codex-gold/v1"
    assert row["training_role"] == "NOT_TRAINING_DATA"
    assert row["evaluation_role"] == "DEVELOPMENT_MODEL_SELECTION_NOT_CLAIM_EVIDENCE"


def test_promotes_primary_training_gold_with_original_partition(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    report = _promote(paths, purpose="PRIMARY_TRAINING")
    row = json.loads(paths["output"].read_text(encoding="utf-8"))

    assert report["reclassification"]["eligible_for_evaluation"] is False
    assert row["schema_version"] == "k-fnspid-sentiment-codex-gold/v1"
    assert row["partition"] == "HISTORICAL_REVIEW"
    assert row["training_role"] == (
        "PRIMARY_TRAINING_NOT_EVALUATION_OR_CLAIM_EVIDENCE"
    )


def test_excludes_unresolved_from_exact_eligible_gold_subset(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path, include_unresolved=True)
    adjudication_packet = json.loads(
        (tmp_path / "adjudication-packet.jsonl").read_text(encoding="utf-8")
    )
    assert "reviewer_1" not in adjudication_packet
    assert "reviewer_2" not in adjudication_packet

    report = _promote(paths)
    rows = [json.loads(line) for line in paths["output"].read_text().splitlines()]

    assert [row["document_id"] for row in rows] == ["disclosure-9001"]
    assert report["source"]["review_sample_count"] == 2
    assert report["source"]["sample_count"] == 1
    assert report["source"]["excluded_unresolved_count"] == 1
    assert report["integrity"]["unresolved_rows_excluded"] is True


def test_rejects_non_independent_unresolved_adjudication(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path, include_unresolved=True)
    decisions = [json.loads(line) for line in paths["decisions"].read_text().splitlines()]
    decisions[1]["adjudication"]["adjudicator_id"] = decisions[1]["reviewer_1"][
        "reviewer_id"
    ]
    decisions[1]["reviewer_id"] = decisions[1]["adjudication"]["adjudicator_id"]
    _write_jsonl(paths["decisions"], decisions)

    with pytest.raises(ValueError, match="independence"):
        _promote(paths)


def test_rejects_hidden_confirmatory_label(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    rows = [json.loads(line) for line in paths["news"].read_text().splitlines()]
    rows[0]["label"] = "NEGATIVE"
    _write_jsonl(paths["news"], rows)
    with pytest.raises(ValueError, match="reservation contract"):
        _promote(paths)


def test_rejects_confirmatory_overlap(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    review = json.loads(paths["review"].read_text(encoding="utf-8"))
    confirmatory = [json.loads(line) for line in paths["disclosure"].read_text().splitlines()]
    confirmatory[0]["content_hash"] = review["content_hash"]
    _write_jsonl(paths["disclosure"], confirmatory)
    with pytest.raises(ValueError, match="commitment|provenance"):
        _promote(paths)


def test_rejects_non_independent_decisions(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    decision = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    decision["reviewer_2"]["reviewer_id"] = decision["reviewer_1"]["reviewer_id"]
    _write_jsonl(paths["decisions"], [decision])
    with pytest.raises(ValueError, match="Dual-review"):
        _promote(paths)


def test_refuses_overwrite(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _promote(paths)
    with pytest.raises(ValueError, match="already exists"):
        _promote(paths)
