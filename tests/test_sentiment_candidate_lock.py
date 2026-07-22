from __future__ import annotations

import importlib.util
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import pytest


def _module() -> ModuleType:
    path = Path("scripts/lock_kf_deberta_sentiment_candidate.py")
    spec = importlib.util.spec_from_file_location("lock_sentiment_candidate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_candidate_lock_uses_selection_score_and_deterministic_tie_break() -> None:
    module = _module()
    candidates = [
        {
            "seed": 42,
            "selection_score": 0.84,
            "report": {"selection": {"macro_f1": 0.90}},
        },
        {
            "seed": 17,
            "selection_score": 0.86,
            "report": {"selection": {"macro_f1": 0.88}},
        },
        {
            "seed": 73,
            "selection_score": 0.86,
            "report": {"selection": {"macro_f1": 0.87}},
        },
    ]

    assert module.select_candidate(candidates)["seed"] == 17


def test_selection_score_is_recomputed_from_weakest_partition() -> None:
    module = _module()
    report = {
        "candidate_selection": {"selection_score": 0.84},
        "selection_breakdown": {
            "PUBLIC_SELECTION": {"sample_count": 400, "macro_f1": 0.91},
            "K_FNSPID_DEVELOPMENT_SELECTION": {
                "sample_count": 220,
                "macro_f1": 0.84,
            },
            "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION": {
                "sample_count": 220,
                "macro_f1": 0.88,
            },
        },
    }

    assert module._validated_selection_score(report) == 0.84
    report["candidate_selection"]["selection_score"] = 0.90
    with pytest.raises(SystemExit, match="재현"):
        module._validated_selection_score(report)


def test_candidate_protocol_signature_excludes_only_seed() -> None:
    module = _module()
    base = {
        "dataset_revision": "revision",
        "input_artifacts": {"gold": {"sha256": "a" * 64}},
        "training_code": {"trainer": {"sha256": "b" * 64}},
        "training_arguments": {"seed": 17, "epochs": 1.5, "max_train_rows": None},
        "training_strategy": "strategy",
        "lora_layers": [6, 7, 8, 9, 10, 11],
        "loss": {"method": "loss"},
        "partition_count": {"TRAIN": 100},
        "prepared_partition_commitments": {
            "TRAIN": {"row_count": 100, "sha256": "c" * 64}
        },
    }
    other_seed = {
        **base,
        "training_arguments": {**base["training_arguments"], "seed": 42},
    }

    assert module._candidate_protocol_signature(base) == (
        module._candidate_protocol_signature(other_seed)
    )
    other_seed["training_arguments"]["epochs"] = 2.0
    assert module._candidate_protocol_signature(base) != (
        module._candidate_protocol_signature(other_seed)
    )
    different_rows = {
        **base,
        "prepared_partition_commitments": {
            "TRAIN": {"row_count": 100, "sha256": "d" * 64}
        },
    }
    assert module._candidate_protocol_signature(base) != module._candidate_protocol_signature(
        different_rows
    )


def test_candidate_lock_manifest_is_write_once(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "lock.json"
    module._write_json_atomic(path, {"locked": True})

    with pytest.raises(SystemExit, match="이미 존재"):
        module._write_json_atomic(path, {"locked": False})


def test_candidate_lock_commits_every_training_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    artifact = tmp_path / "input.jsonl"
    artifact.write_text("{}\n", encoding="utf-8")
    raw = artifact.read_bytes()
    record = {
        "path": artifact.name,
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }
    report = {"input_artifacts": {name: dict(record) for name in module.REQUIRED_TRAINING_INPUTS}}

    module._validate_training_inputs(report)
    assert "news_auxiliary_training_report" in report["input_artifacts"]
    assert "disclosure_auxiliary_training_report" in report["input_artifacts"]

    artifact.write_text('{"changed":true}\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="변경"):
        module._validate_training_inputs(report)


def test_candidate_lock_freezes_every_recipe_blob_and_statistical_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    expected_paths = dict(module.RECIPE_RELATIVE_PATHS)
    for name, relative_path in expected_paths.items():
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n", encoding="utf-8")

    commitments = module._recipe_commitments()
    plan = module.canonical_statistical_analysis_plan()

    assert set(commitments) == set(expected_paths)
    assert all(
        set(commitment) == {"path", "bytes", "sha256"}
        and commitment["path"] == expected_paths[name]
        for name, commitment in commitments.items()
    )
    assert len(plan["holm_hypotheses"]) == 8
    assert plan["familywise_alpha"] == 0.05
    assert plan["evaluation_batch_size"] == 16
    assert plan["paired_design_inference"]["finite_population_correction"] is True
    assert plan["claim_scope"]["global_sota_claim_allowed"] is False
