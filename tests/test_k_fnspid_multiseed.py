from __future__ import annotations

import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path("scripts/aggregate_k_fnspid_runs.py")
    spec = importlib.util.spec_from_file_location("aggregate_k_fnspid_runs", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_promotion_script() -> ModuleType:
    path = Path("scripts/promote_k_fnspid_transformer.py")
    spec = importlib.util.spec_from_file_location("promote_k_fnspid_transformer", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _report(seed: int, validation_f1: float, test_f1: float) -> dict:
    metrics = {"accuracy": 0.5, "macro_f1": test_f1, "quadratic_kappa": 0.4}
    return {
        "seed": seed,
        "version": f"run-{seed}",
        "artifact_dir": f"artifacts/seed-{seed}",
        "dataset_dir": "data/k_fnspid/v3",
        "dataset_manifest": {"sha256": "frozen-dataset"},
        "partition_count": {"TRAIN": 100, "VALIDATION": 20, "TEST": 20},
        "training_objective": {"name": "ordinal"},
        "training_hyperparameters": {"effective_batch_size": 32, "learning_rate": 2e-4},
        "postprocessing": {
            "method": "validation-selected-log-prior-correction/v1",
            "selection_partition": "VALIDATION",
            "selection_objective": "macro_f1",
            "strength_grid": {"minimum": 0.0, "maximum": 2.0, "step": 0.05},
        },
        "base_model": "kf-deberta",
        "base_model_revision": "frozen-revision",
        "max_length": 256,
        "validation": {**metrics, "macro_f1": validation_f1},
        "test": metrics,
        "test_predictions": {"path": f"reports/seed-{seed}.jsonl"},
    }


def test_multiseed_selection_uses_validation_only(tmp_path: Path) -> None:
    module = _load_script()
    reports = [
        _report(17, 0.41, 0.60),
        _report(42, 0.45, 0.40),
        _report(73, 0.43, 0.70),
    ]

    result = module.aggregate_reports(
        reports,
        [tmp_path / f"seed-{seed}.json" for seed in (17, 42, 73)],
    )

    assert result["selected_seed_by_validation"] == 42
    assert result["test"]["macro_f1"]["mean"] == pytest.approx(0.5666667)
    assert result["test"]["macro_f1"]["sample_std"] == pytest.approx(0.1527525)


def test_multiseed_rejects_mismatched_protocol(tmp_path: Path) -> None:
    module = _load_script()
    reports = [_report(17, 0.41, 0.42), _report(42, 0.43, 0.44), _report(73, 0.45, 0.46)]
    reports[2]["max_length"] = 128

    with pytest.raises(ValueError, match="일치하지 않습니다"):
        module.aggregate_reports(reports, [tmp_path / f"{index}.json" for index in range(3)])


def test_multiseed_rejects_changed_dataset_manifest(tmp_path: Path) -> None:
    module = _load_script()
    reports = [_report(17, 0.41, 0.42), _report(42, 0.43, 0.44), _report(73, 0.45, 0.46)]
    reports[2]["dataset_manifest"]["sha256"] = "changed-dataset"

    with pytest.raises(ValueError, match="일치하지 않습니다"):
        module.aggregate_reports(reports, [tmp_path / f"{index}.json" for index in range(3)])


def test_multiseed_rejects_changed_training_hyperparameters(tmp_path: Path) -> None:
    module = _load_script()
    reports = [_report(17, 0.41, 0.42), _report(42, 0.43, 0.44), _report(73, 0.45, 0.46)]
    reports[2]["training_hyperparameters"]["learning_rate"] = 3e-4

    with pytest.raises(ValueError, match="일치하지 않습니다"):
        module.aggregate_reports(reports, [tmp_path / f"{index}.json" for index in range(3)])


def test_multiseed_rejects_changed_postprocessing_protocol(tmp_path: Path) -> None:
    module = _load_script()
    reports = [_report(17, 0.41, 0.42), _report(42, 0.43, 0.44), _report(73, 0.45, 0.46)]
    reports[2]["postprocessing"]["selection_partition"] = "TEST"

    with pytest.raises(ValueError, match="일치하지 않습니다"):
        module.aggregate_reports(reports, [tmp_path / f"{index}.json" for index in range(3)])


def test_promotion_rejects_tampered_prediction_manifest(tmp_path: Path) -> None:
    module = _load_promotion_script()
    prediction = tmp_path / "prediction.jsonl"
    prediction.write_text('{"document_id":"1"}\n', encoding="utf-8")
    manifest = {
        "bytes": prediction.stat().st_size,
        "sha256": sha256(prediction.read_bytes()).hexdigest(),
    }

    assert module._matches_manifest(prediction, manifest)

    prediction.write_text('{"document_id":"tampered"}\n', encoding="utf-8")
    assert not module._matches_manifest(prediction, manifest)


def test_artifact_replacement_is_verified_and_atomic(tmp_path: Path) -> None:
    module = _load_promotion_script()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    artifact = source / "adapter_model.safetensors"
    artifact.write_bytes(b"new-verified-model")
    (target / "adapter_model.safetensors").write_bytes(b"old-model")
    report = {
        "artifact_files": {
            artifact.name: {
                "bytes": artifact.stat().st_size,
                "sha256": sha256(artifact.read_bytes()).hexdigest(),
            }
        }
    }

    module._replace_artifact_directory(source, target, report)

    assert (target / artifact.name).read_bytes() == b"new-verified-model"
    assert not (tmp_path / ".target-backup").exists()


def test_selected_report_path_matches_validation_selected_seed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_promotion_script()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    paths = []
    for seed in (17, 42, 73):
        path = tmp_path / f"seed-{seed}.json"
        path.write_text(json.dumps({"seed": seed}), encoding="utf-8")
        paths.append(path.name)

    selected = module._selected_report_path({"report_paths": paths}, 73)

    assert selected == tmp_path / "seed-73.json"
