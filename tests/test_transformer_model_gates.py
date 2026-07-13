from pathlib import Path

from hannah_montana_ai.services.model_artifact_integrity import (
    build_artifact_manifest,
    verify_artifact_manifest,
)
from hannah_montana_ai.services.transformer_impact_model import (
    _deployment_gate_passed as impact_gate_passed,
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


def test_impact_gate_requires_large_temporal_test_and_ordinal_quality() -> None:
    report = {
        "test": {"sample_count": 999, "macro_f1": 0.5, "quadratic_kappa": 0.4},
        "deployment_gate": {"eligible": True},
    }

    assert not impact_gate_passed(report)

    report["test"]["sample_count"] = 1_000
    assert impact_gate_passed(report)


def test_artifact_manifest_rejects_tampered_file(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter_model.safetensors"
    artifact.write_bytes(b"verified")
    manifest = build_artifact_manifest(tmp_path, (artifact.name,))

    assert verify_artifact_manifest(tmp_path, manifest)

    artifact.write_bytes(b"tampered")
    assert not verify_artifact_manifest(tmp_path, manifest)
