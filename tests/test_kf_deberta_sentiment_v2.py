from __future__ import annotations

import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
import torch


def _module() -> ModuleType:
    path = Path("scripts/train_kf_deberta_sentiment_v2.py")
    spec = importlib.util.spec_from_file_location("train_kf_deberta_sentiment_v2", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_candidate_trainer_never_opens_reused_public_test() -> None:
    source = Path("scripts/train_kf_deberta_sentiment_v2.py").read_text(encoding="utf-8")

    assert "ratings_test.csv" not in source


def test_hierarchical_loss_rewards_correct_neutral_boundary() -> None:
    module = _module()
    labels = torch.tensor([1, 0, 2])
    weights = torch.ones(3)
    class_weights = torch.ones(3)
    correct = torch.tensor([[0.0, 4.0, 0.0], [4.0, 0.0, -1.0], [-1.0, 0.0, 4.0]])
    wrong = torch.tensor([[4.0, 0.0, -1.0], [0.0, 4.0, -1.0], [-1.0, 4.0, 0.0]])

    assert module.hierarchical_focal_loss(
        correct, labels, weights, class_weights
    ) < module.hierarchical_focal_loss(wrong, labels, weights, class_weights)


def test_rdrop_symmetric_kl_is_zero_only_for_identical_predictions() -> None:
    module = _module()
    first = torch.tensor([[2.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
    second = torch.tensor([[1.0, 0.5, -0.5], [0.0, 1.0, 0.0]])
    weights = torch.ones(2)

    identical = module.symmetric_kl_consistency_loss(first, first, weights)
    different = module.symmetric_kl_consistency_loss(first, second, weights)

    assert abs(float(identical)) < 1e-7
    assert float(different) > 0.0


def test_weighted_deduplication_prefers_reviewed_gold() -> None:
    module = _module()
    rows = [
        {
            "text": "같은 뉴스",
            "label": "NEUTRAL",
            "sample_weight": 0.3,
            "dataset": "SILVER",
        },
        {
            "text": "같은뉴스",
            "label": "POSITIVE",
            "sample_weight": 1.5,
            "dataset": "GOLD",
        },
    ]

    selected = module._deduplicate_weighted(rows)

    assert len(selected) == 1
    assert selected[0]["dataset"] == "GOLD"


def test_target_swap_hard_negatives_are_deterministic_and_target_absent() -> None:
    module = _module()
    rows = [
        {
            "text": f"{name}의 영업이익이 증가했다.",
            "label": "POSITIVE" if index % 2 == 0 else "NEGATIVE",
            "source_type": source,
            "stock_code": f"{index:06d}",
            "stock_name": name,
            "stock_aliases": [f"{name}별칭"],
            "sample_weight": 1.0,
            "dataset": "GOLD",
            "document_id": f"doc-{source}-{index}",
            "content_hash": f"hash-{source}-{index}",
            "event_cluster_id": f"event-{source}-{index}",
        }
        for source in ("NEWS", "DISCLOSURE")
        for index, name in enumerate(("하나금융지주", "카카오뱅크", "현대건설"))
    ]

    first = module.build_target_swap_hard_negatives(rows, per_source=2, seed=17)
    second = module.build_target_swap_hard_negatives(rows, per_source=2, seed=17)

    assert first == second
    assert len(first) == 4
    assert {row["source_type"] for row in first} == {"NEWS", "DISCLOSURE"}
    assert all(row["label"] == "NEUTRAL" for row in first)
    assert all(row["sample_weight"] == module.TARGET_SWAP_WEIGHT for row in first)
    assert all(
        module.normalized_sentiment_text(row["stock_name"])
        not in module.normalized_sentiment_text(row["text"])
        for row in first
    )
    assert all(row["dataset"] == "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE" for row in first)
    assert all(row["augmentation_method"] == "ABSENT_TARGET_SWAP_V2" for row in first)
    assert all(row["stock_aliases"] for row in first)
    assert all(
        all(
            token not in module.normalized_sentiment_text(row["text"])
            for token in row["target_swap_absence_tokens"]
        )
        for row in first
    )


@pytest.mark.parametrize("mentioned_field", ["stock_code", "stock_alias"])
def test_target_swap_rejects_donor_code_or_alias_mentioned_in_text(
    mentioned_field: str,
) -> None:
    module = _module()
    donor_code = "999999"
    donor_alias = "숨은별칭"
    mentioned = donor_code if mentioned_field == "stock_code" else donor_alias
    rows = [
        {
            "text": f"하나금융지주 실적 개선. 참고: {mentioned}",
            "label": "POSITIVE",
            "source_type": "NEWS",
            "stock_code": "086790",
            "stock_name": "하나금융지주",
            "stock_aliases": ["하나금융"],
            "document_id": "source",
            "content_hash": "source-hash",
            "event_cluster_id": "source-event",
        },
        {
            "text": "donor pool only",
            "label": "NEUTRAL",
            "source_type": "NEWS",
            "stock_code": donor_code,
            "stock_name": "도너기업",
            "stock_aliases": [donor_alias],
            "document_id": "donor",
            "content_hash": "donor-hash",
            "event_cluster_id": "donor-event",
        },
    ]

    assert module.build_target_swap_hard_negatives(rows, per_source=1, seed=17) == []


def test_effective_number_weights_use_sample_weight_mass_not_raw_count() -> None:
    module = _module()
    rows = [
        {"label": "NEGATIVE", "sample_weight": 0.01}
        for _ in range(100)
    ] + [
        {"label": "NEUTRAL", "sample_weight": 1.0},
        {"label": "POSITIVE", "sample_weight": 1.0},
    ]

    weights = module._effective_number_weights(rows)

    assert torch.allclose(weights, torch.ones(3), atol=1e-6)


def test_effective_number_weights_are_stable_and_reject_non_finite_mass() -> None:
    module = _module()
    rows = [
        {"label": "NEGATIVE", "sample_weight": 1e-9},
        {"label": "NEUTRAL", "sample_weight": 1.0},
        {"label": "POSITIVE", "sample_weight": 1e12},
    ]

    weights = module._effective_number_weights(rows)

    assert bool(torch.isfinite(weights).all())
    assert abs(float(weights.sum()) - 3.0) < 1e-5
    with pytest.raises(ValueError, match="sample_weight"):
        module._effective_number_weights(
            [
                {"label": "NEGATIVE", "sample_weight": float("nan")},
                {"label": "NEUTRAL", "sample_weight": 1.0},
                {"label": "POSITIVE", "sample_weight": 1.0},
            ]
        )


def test_training_weight_audit_exposes_source_label_and_dataset_mass() -> None:
    module = _module()
    rows = [
        {
            "label": "NEGATIVE",
            "sample_weight": 0.25,
            "source_type": "NEWS",
            "dataset": "SILVER",
        },
        {
            "label": "NEGATIVE",
            "sample_weight": 1.5,
            "source_type": "NEWS",
            "dataset": "GOLD",
        },
        {
            "label": "POSITIVE",
            "sample_weight": 1.5,
            "source_type": "DISCLOSURE",
            "dataset": "GOLD",
        },
    ]

    audit = module._training_weight_audit(rows)

    assert audit["by_source_and_label"]["NEWS"]["NEGATIVE"] == {
        "raw_count": 2,
        "effective_weight_sum": 1.75,
    }
    assert audit["by_dataset_source_and_label"]["SILVER"]["NEWS"]["NEGATIVE"] == {
        "raw_count": 1,
        "effective_weight_sum": 0.25,
    }


def test_base_weight_verification_hashes_resolved_cache_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    assert module.BASE_MODEL_WEIGHT_SHA256 == (
        "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
    )
    blob = tmp_path / "blob"
    blob.write_bytes(b"verified base weights")
    link = tmp_path / "pytorch_model.bin"
    link.symlink_to(blob)
    digest = sha256(blob.read_bytes()).hexdigest()
    monkeypatch.setattr(module, "BASE_MODEL_WEIGHT_SHA256", digest)
    monkeypatch.setattr(module, "hf_hub_download", lambda **_kwargs: str(link))

    assert module._verify_base_model_weights() == blob.resolve()

    monkeypatch.setattr(module, "BASE_MODEL_WEIGHT_SHA256", "0" * 64)
    with pytest.raises(RuntimeError, match="SHA-256"):
        module._verify_base_model_weights()


def test_selection_score_uses_weakest_independent_news_partition() -> None:
    module = _module()
    breakdown = {
        "PUBLIC_SELECTION": {"macro_f1": 0.91},
        "K_FNSPID_DEVELOPMENT_SELECTION": {"macro_f1": 0.84},
        "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION": {"macro_f1": 0.88},
    }

    assert module._selection_score(breakdown) == 0.84


def test_reviewed_loader_accepts_promoted_gold_contract(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "gold.jsonl"
    path.write_text(
        json.dumps(
            {
                "schema_version": module.GOLD_SCHEMA_VERSION,
                "partition": "TRAIN_REVIEW",
                "sentiment": "POSITIVE",
                "review_status": "CODEX_REVIEW_APPROVED",
                "reviewer_id": "codex-blind-reviewer",
                "reviewed_at": "2026-07-15T12:30:00+00:00",
                "source_type": "NEWS",
                "text": "영업이익이 증가했다.",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    rows = module._load_reviewed_rows(path, "TRAIN_REVIEW", weight=1.5)

    assert rows[0]["label"] == "POSITIVE"
    assert rows[0]["sample_weight"] == 1.5


def test_auxiliary_loader_reconstructs_v2_lineage() -> None:
    module = _module()

    rows = module._load_auxiliary_training_rows(
        Path("data/training/k_fnspid_disclosure_sentiment_auxiliary_gold_v2.jsonl"),
        Path("reports/k-fnspid-disclosure-sentiment-training-reclassification-v2.json"),
        "DISCLOSURE",
        weight=1.5,
    )

    assert len(rows) == 600
    assert all(row["sentiment"] == row["final_sentiment"] == row["label"] for row in rows)


def test_auxiliary_decision_accepts_unresolved_as_excluded() -> None:
    module = _module()
    decision = next(
        json.loads(line)
        for line in Path(
            "data/curation/k_fnspid_sentiment/"
            "prevalence_aux_training_codex_decisions_dual.jsonl"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if '"final_sentiment":"UNRESOLVED"' in line
    )

    assert module._validate_auxiliary_decision(decision, decision["item_id"]) is False


def test_auxiliary_subset_report_requires_news_exclusion_counts(tmp_path: Path) -> None:
    module = _module()
    integrity = {"unresolved_rows_excluded": True}
    source = {
        "review_sample_count": 600,
        "sample_count": 598,
        "excluded_unresolved_count": 2,
    }

    module._validate_auxiliary_subset_report(
        source,
        integrity,
        source_type="NEWS",
        review_count=600,
        gold_count=598,
        unresolved_count=2,
        report_path=tmp_path / "news-report.json",
    )
    with np.testing.assert_raises_regex(SystemExit, "unresolved exclusion"):
        module._validate_auxiliary_subset_report(
            {"sample_count": 598},
            {},
            source_type="NEWS",
            review_count=600,
            gold_count=598,
            unresolved_count=2,
            report_path=tmp_path / "news-report.json",
        )


def test_auxiliary_loader_rejects_self_consistent_forged_label(tmp_path: Path) -> None:
    module = _module()
    source_path = Path("data/training/k_fnspid_disclosure_sentiment_auxiliary_gold_v2.jsonl")
    rows = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines()]
    rows[0]["sentiment"] = "NEGATIVE"
    rows[0]["final_sentiment"] = "NEGATIVE"
    forged_path = tmp_path / "forged.jsonl"
    forged_path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    report = json.loads(
        Path("reports/k-fnspid-disclosure-sentiment-training-reclassification-v2.json").read_text(
            encoding="utf-8"
        )
    )
    raw = forged_path.read_bytes()
    report["lineage"]["output"] = {
        "path": str(forged_path),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }
    report_path = tmp_path / "forged-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

    with np.testing.assert_raises_regex(SystemExit, "provenance"):
        module._load_auxiliary_training_rows(
            forged_path,
            report_path,
            "DISCLOSURE",
            weight=1.5,
        )


def test_domain_logit_bias_is_fit_only_for_sufficient_calibration_rows() -> None:
    module = _module()
    rows = [
        {
            "text": f"뉴스 {index}",
            "label": ("NEGATIVE" if index < 5 else "NEUTRAL" if index < 25 else "POSITIVE"),
            "source_type": "NEWS",
            "stock_name": "하나금융지주",
        }
        for index in range(30)
    ]
    logits = np.tile(np.asarray([[0.0, 0.0, 0.1]]), (30, 1))

    biases = module._fit_logit_bias_by_domain(logits, rows)
    adjusted = module._apply_logit_bias(logits, rows, biases)

    assert biases["NEWS_TARGETED"] != [0.0, 0.0, 0.0]
    assert biases["NEWS_UNTARGETED"] == [0.0, 0.0, 0.0]
    assert adjusted.argmax(axis=-1).tolist().count(1) >= 20


def test_domain_logit_bias_rejects_incomplete_contract() -> None:
    module = _module()

    with np.testing.assert_raises_regex(ValueError, "구성"):
        module._apply_logit_bias(
            np.asarray([[0.0, 0.0, 0.0]]),
            [{"source_type": "NEWS"}],
            {"NEWS_UNTARGETED": [0.0, 0.0, 0.0]},
        )


def test_sealed_reservation_loader_uses_identity_without_label(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "sealed-review.jsonl"
    rows = [
        {
            "schema_version": "k-fnspid-sentiment-review-row/v1",
            "partition": "SEALED_TEST_REVIEW",
            "source_type": "NEWS",
            "review_status": "NEEDS_BLIND_REVIEW",
            "final_sentiment": "",
            "text": f"뉴스 {index}",
            "source_url": f"https://example.com/{index}",
            "canonical_url": f"https://example.com/{index}",
            "content_hash": f"hash-{index}",
            "event_cluster_id": f"event-{index}",
        }
        for index in range(500)
    ]
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    loaded = module._load_sealed_reservation_rows(path, "SEALED_TEST_REVIEW", "NEWS")

    assert len(loaded) == 500
    assert "label" not in loaded[0]
    assert loaded[0]["event_cluster_id"] == "event-0"
