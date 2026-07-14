import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path("scripts/evaluate_k_fnspid_research.py")
    spec = importlib.util.spec_from_file_location("evaluate_k_fnspid_research", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_research_evaluation_reports_paired_improvement() -> None:
    module = _load_script()
    rows = []
    labels = module.LABEL_ORDER
    for index in range(120):
        expected = labels[index % len(labels)]
        baseline = labels[(index + 1) % len(labels)] if index % 3 == 0 else expected
        transformer = labels[(index + 1) % len(labels)] if index % 12 == 0 else expected
        rows.append(
            {
                "document_id": str(index),
                "expected": expected,
                "baseline": baseline,
                "transformer": transformer,
                "baseline_probabilities": {
                    label: 0.7 if label == baseline else 0.1 for label in labels
                },
                "transformer_probabilities": {
                    label: 0.7 if label == transformer else 0.1 for label in labels
                },
                "source_type": "NEWS" if index % 2 else "DISCLOSURE",
                "stock_code": f"{index % 12:06d}",
                "effective_trade_date": f"2026-04-{index % 24 + 1:02d}",
            }
        )

    report = module.evaluate_research(rows, bootstrap_samples=100, seed=7)

    assert report["transformer"]["macro_f1"] > report["baseline"]["macro_f1"]
    assert report["mcnemar_exact"]["transformer_only_correct"] > 0
    assert set(report["source_type"]) == {"DISCLOSURE", "NEWS"}
    assert report["clustered_bootstrap"]["cluster_count"] == 24
    assert "macro_f1_difference" in report["clustered_bootstrap"]
    assert set(report["transformer"]["per_class"]) == set(labels)
    assert report["transformer"]["per_class"]["LOW"]["support"] == 30
    assert len(report["transformer"]["confusion_matrix"]) == len(labels)
    assert (
        report["transformer"]["ordinal_mean_absolute_error"]
        < report["baseline"]["ordinal_mean_absolute_error"]
    )
    assert report["research_gate"]["trade_date_clustered_accuracy_ci_excludes_zero"]
    assert report["research_gate"]["trade_date_clustered_macro_f1_ci_excludes_zero"]
    assert report["research_gate"]["trade_date_clustered_quadratic_kappa_ci_excludes_zero"]
    assert report["research_gate"]["mcnemar_exact_p_below_0_05"]


def test_exact_mcnemar_handles_identical_predictions() -> None:
    module = _load_script()

    assert module.exact_mcnemar_p_value(0, 0) == 1.0


def test_clustered_bootstrap_rejects_missing_cluster_key() -> None:
    module = _load_script()

    try:
        module.clustered_paired_bootstrap(
            [{"expected": "LOW", "baseline": "LOW", "transformer": "LOW"}],
            cluster_key="effective_trade_date",
            samples=10,
            seed=7,
        )
    except ValueError as error:
        assert "필드가 없습니다" in str(error)
    else:
        raise AssertionError("누락된 cluster key를 허용했습니다.")


def _prediction(document_id: str) -> dict[str, object]:
    return {
        "document_id": document_id,
        "expected": "LOW",
        "predicted": "LOW",
        "probabilities": {"LOW": 0.7, "MEDIUM": 0.1, "HIGH": 0.1, "CRITICAL": 0.1},
        "source_type": "NEWS",
        "stock_code": "005930",
        "effective_trade_date": "2026-04-01",
    }


def test_align_predictions_rejects_duplicate_document_id() -> None:
    module = _load_script()
    duplicate = [_prediction("doc-1"), _prediction("doc-1")]

    with pytest.raises(ValueError, match="중복"):
        module.align_predictions(duplicate, [_prediction("doc-1")])


def test_align_predictions_rejects_cluster_metadata_mismatch() -> None:
    module = _load_script()
    baseline = _prediction("doc-1")
    transformer = {**_prediction("doc-1"), "effective_trade_date": "2026-04-02"}

    with pytest.raises(ValueError, match="effective_trade_date"):
        module.align_predictions([baseline], [transformer])


def test_align_predictions_rejects_invalid_probability_vector() -> None:
    module = _load_script()
    malformed = {**_prediction("doc-1"), "probabilities": {"LOW": 1.0}}

    with pytest.raises(ValueError, match="확률 라벨"):
        module.align_predictions([malformed], [_prediction("doc-1")])
