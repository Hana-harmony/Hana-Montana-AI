import json
import sys
from pathlib import Path

import pytest

from hannah_montana_ai.services.model_artifact_integrity import (
    build_artifact_manifest,
    verify_artifact_manifest,
)
from hannah_montana_ai.services.transformer_impact_model import (
    KfDebertaImpactModel,
    _log_prior_offsets,
    _temperature,
)
from hannah_montana_ai.services.transformer_impact_model import (
    _deployment_gate_passed as impact_gate_passed,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    KfDebertaSentimentModel,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    _deployment_gate_passed as sentiment_gate_passed,
)


def test_sentiment_gate_requires_external_benchmark_eligibility() -> None:
    training = {"test": {"sample_count": 933, "macro_f1": 0.91}}
    benchmark = {
        "sample_count": 933,
        "models": {"kf_deberta_lora": {"macro_f1": 0.90}},
        "deployment_gate": {"eligible": False},
    }

    assert not sentiment_gate_passed(training, benchmark)

    benchmark["deployment_gate"]["eligible"] = True
    assert sentiment_gate_passed(training, benchmark)


def test_sentiment_gate_uses_serving_ensemble_result() -> None:
    training = {"test": {"sample_count": 933, "macro_f1": 0.91}}
    benchmark = {
        "sample_count": 933,
        "models": {
            "kf_deberta_lora": {"macro_f1": 0.91},
            "kf_deberta_lora_ensemble": {"macro_f1": 0.84},
        },
        "deployment_gate": {"eligible": True},
    }

    assert not sentiment_gate_passed(training, benchmark)

    benchmark["models"]["kf_deberta_lora_ensemble"]["macro_f1"] = 0.90
    assert sentiment_gate_passed(training, benchmark)


def test_sentiment_gate_uses_declared_stacker_candidate() -> None:
    training = {"test": {"sample_count": 933, "macro_f1": 0.91}}
    benchmark = {
        "sample_count": 933,
        "models": {
            "kf_deberta_lora_ensemble": {"macro_f1": 0.90},
            "kf_deberta_lora_stacker": {"macro_f1": 0.84},
        },
        "deployment_gate": {
            "eligible": True,
            "candidate_model": "kf_deberta_lora_stacker",
        },
    }

    assert not sentiment_gate_passed(training, benchmark)

    benchmark["models"]["kf_deberta_lora_stacker"]["macro_f1"] = 0.90
    assert sentiment_gate_passed(training, benchmark)


def test_impact_gate_requires_large_temporal_test_and_ordinal_quality() -> None:
    report = {
        "test": {"sample_count": 999, "macro_f1": 0.5, "quadratic_kappa": 0.4},
        "deployment_gate": {"eligible": True},
    }

    assert not impact_gate_passed(report)

    report["test"]["sample_count"] = 1_000
    assert impact_gate_passed(report)


def test_impact_gate_requires_matching_source_expert() -> None:
    report = {
        "source_type": "DISCLOSURE",
        "test": {"sample_count": 590, "macro_f1": 0.34, "quadratic_kappa": 0.12},
        "deployment_gate": {
            "minimum_test_sample_count": 500,
            "minimum_macro_f1": 0.30,
            "minimum_quadratic_kappa": 0.08,
            "eligible": True,
        },
    }

    assert impact_gate_passed(report, "DISCLOSURE")
    assert not impact_gate_passed(report, "NEWS")


def test_impact_log_prior_correction_requires_validation_provenance() -> None:
    report = {
        "postprocessing": {
            "method": "validation-selected-log-prior-correction/v1",
            "selection_partition": "VALIDATION",
            "selected_strength": 0.5,
            "training_class_priors": {
                "LOW": 0.7,
                "MEDIUM": 0.2,
                "HIGH": 0.08,
                "CRITICAL": 0.02,
            },
        }
    }

    offsets = _log_prior_offsets(report)
    assert offsets is not None
    assert offsets[0] > offsets[-1]

    report["postprocessing"]["selection_partition"] = "TEST"
    assert _log_prior_offsets(report) is None


def test_impact_log_prior_temperature_v2_uses_validation_provenance() -> None:
    report = {
        "postprocessing": {
            "method": "validation-selected-log-prior-temperature/v2",
            "selection_partition": "VALIDATION",
            "selected_strength": 0.35,
            "selected_temperature": 0.9,
            "training_class_priors": {
                "LOW": 0.7,
                "MEDIUM": 0.2,
                "HIGH": 0.08,
                "CRITICAL": 0.02,
            },
        }
    }

    assert _log_prior_offsets(report) is not None
    assert _temperature(report) == 0.9

    report["postprocessing"]["method"] = "unreviewed-postprocessing/v3"
    assert _log_prior_offsets(report) is None


@pytest.mark.parametrize(
    ("source_type", "artifact_dir", "report_path"),
    (
        (
            "NEWS",
            "src/hannah_montana_ai/model_store/k_fnspid_impact_news_transformer",
            "reports/k-fnspid-impact-news-transformer-training-report.json",
        ),
        (
            "DISCLOSURE",
            "src/hannah_montana_ai/model_store/k_fnspid_impact_disclosure_transformer",
            "reports/k-fnspid-impact-disclosure-transformer-training-report.json",
        ),
    ),
)
def test_promoted_impact_experts_satisfy_runtime_contract(
    source_type: str,
    artifact_dir: str,
    report_path: str,
) -> None:
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))

    assert impact_gate_passed(report, source_type)
    assert verify_artifact_manifest(Path(artifact_dir), report["artifact_files"])
    assert _log_prior_offsets(report) is not None
    assert _temperature(report) is not None


def test_current_impact_feature_requires_postprocessing() -> None:
    assert _log_prior_offsets({"input_feature_version": "k-fnspid-text-v2"}) is None
    assert _log_prior_offsets({"input_feature_version": "k-fnspid-text-v1"}) == [
        0.0,
        0.0,
        0.0,
        0.0,
    ]


def test_impact_temperature_requires_validation_selection() -> None:
    report = {
        "postprocessing": {
            "selection_partition": "VALIDATION",
            "selected_temperature": 1.35,
        }
    }

    assert _temperature(report) == 1.35
    report["postprocessing"]["selection_partition"] = "TEST"
    assert _temperature(report) is None


def test_artifact_manifest_rejects_tampered_file(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter_model.safetensors"
    artifact.write_bytes(b"verified")
    manifest = build_artifact_manifest(tmp_path, (artifact.name,))

    assert verify_artifact_manifest(tmp_path, manifest)

    artifact.write_bytes(b"tampered")
    assert not verify_artifact_manifest(tmp_path, manifest)


def test_transformers_fall_back_when_optional_runtime_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)

    sentiment = KfDebertaSentimentModel(
        Path("src/hannah_montana_ai/model_store/kf_deberta_sentiment"),
        Path("reports/kf-deberta-sentiment-training-report.json"),
        Path("reports/korean-finance-sentiment-benchmark.json"),
        Path("/missing/base-model"),
    )
    impact = KfDebertaImpactModel(
        Path("src/hannah_montana_ai/model_store/k_fnspid_impact_transformer"),
        Path("reports/k-fnspid-transformer-training-report.json"),
        Path("/missing/base-model"),
    )

    assert sentiment.enabled is False
    assert impact.enabled is False
