from __future__ import annotations

import copy
import importlib.util
import json
import subprocess  # nosec B404 - 고정된 로컬 학습 스크립트만 검증한다.
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path("scripts/train_k_fnspid_sentiment_ablation.py")
CANONICAL_TRAINER = Path("scripts/train_kf_deberta_sentiment_v2.py")


@pytest.fixture(scope="module")
def module() -> ModuleType:
    scripts = str(Path("scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location("train_k_fnspid_sentiment_ablation", SCRIPT)
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def _validate(script: Path, *arguments: str) -> dict[str, Any]:
    completed = subprocess.run(  # noqa: S603  # nosec B603
        [sys.executable, str(script), *arguments, "--validate-only"],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    value = json.loads(completed.stdout)
    assert isinstance(value, dict)
    return value


@pytest.fixture(scope="module")
def no_k_validation() -> dict[str, Any]:
    return _validate(SCRIPT, "--mode", "NO_K", "--seed", "17")


def test_runner_never_names_or_loads_public_test() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "ratings_test.csv" not in source
    assert '"TEST": []' in source


def test_no_k_has_only_public_training_and_no_target_swap(
    no_k_validation: dict[str, Any],
) -> None:
    assert no_k_validation["status"] == "VALIDATED_WITHOUT_TRAINING"
    assert no_k_validation["public_test_opened"] is False
    assert no_k_validation["training_source_distribution"] == {"PUBLIC_TRAIN": 7413}
    assert no_k_validation["target_swap_count"] == 0
    assert no_k_validation["target_swap_source_distribution"] == {}
    provenance = no_k_validation["source_selection_provenance"]
    assert isinstance(provenance, dict)
    assert provenance["PUBLIC_TRAIN"]["decision"] == "INCLUDED"
    assert all(
        details["decision"] == "EXCLUDED" and details["pre_dedup_selected_count"] == 0
        for name, details in provenance.items()
        if name != "PUBLIC_TRAIN"
    )


def test_validation_exposes_labels_partitions_and_all_hashes(
    no_k_validation: dict[str, Any],
) -> None:
    labels = no_k_validation["training_label_distribution"]
    assert isinstance(labels, dict)
    assert set(labels) == {"NEGATIVE", "NEUTRAL", "POSITIVE"}
    commitments = no_k_validation["prepared_partition_commitments"]
    assert isinstance(commitments, dict)
    assert set(commitments) == {
        "TRAIN",
        "CHECKPOINT",
        "CALIBRATION",
        "SELECTION",
        "NEWS_CONFIRMATORY_RESERVATION",
        "DISCLOSURE_CONFIRMATORY_RESERVATION",
    }
    assert all(
        isinstance(record, dict) and record["row_count"] > 0 and len(record["sha256"]) == 64
        for record in commitments.values()
    )
    for field in ("input_artifacts", "recipe_artifacts"):
        artifacts = no_k_validation[field]
        assert isinstance(artifacts, dict) and artifacts
        assert all(
            len(record["sha256"]) == 64 and record["bytes"] > 0 for record in artifacts.values()
        )
    base = no_k_validation["base_model_provenance"]
    assert base["revision"] == "363b171d71443b0874b0bf9cea053eb5b1650633"
    assert base["source_weight_sha256"] == (
        "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
    )


def test_fixed_seed_matrix_uses_identical_data_commitments(
    module: ModuleType,
    no_k_validation: dict[str, Any],
) -> None:
    assert module.MODEL_SEEDS == (17, 42, 73)
    plan = no_k_validation["ablation_validation_plan"]
    assert plan["primary_required"] == {
        "mode": "NO_K",
        "required_seed_runs": [17, 42, 73],
        "comparison": "FULL canonical v5 candidate on the same prepared holdouts and seeds",
        "status": "MANDATORY_BEFORE_PAPER_COMPONENT_CLAIM",
    }
    baseline = no_k_validation["prepared_partition_commitments"]
    synthetic_rows = [
        {"dataset": "PUBLIC_TRAIN", "label": label, "source_type": "NEWS"}
        for label in module.v5.LABEL_ORDER
    ]
    prepared = module.PreparedAblation(
        mode=module.AblationMode.NO_K,
        train_rows=synthetic_rows,
        checkpoint_rows=[],
        calibration_rows=[],
        selection_rows=[],
        news_reservation=[],
        disclosure_reservation=[],
        target_swap_rows=[],
        prepared_partition_commitments=baseline,
        public_audit={},
        news_silver_audit={},
        disclosure_silver_audit={},
        final_overlap_audit={},
        raw_source_counts={"PUBLIC_TRAIN": 3},
    )
    records = [
        module._protocol_record(prepared, seed, {}, {})["prepared_partition_commitments"]
        for seed in module.MODEL_SEEDS
    ]

    assert records[0] == records[1] == records[2] == baseline


@pytest.mark.parametrize(
    ("mode", "datasets", "swap_sources"),
    [
        ("NO_K", ["PUBLIC_TRAIN"], []),
        (
            "NEWS_ONLY",
            ["PUBLIC_TRAIN", "K_FNSPID_CODEX_GOLD", "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE"],
            ["NEWS"],
        ),
        (
            "DISCLOSURE_ONLY",
            [
                "PUBLIC_TRAIN",
                "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
                "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
            ],
            ["DISCLOSURE"],
        ),
        (
            "FULL",
            [
                "PUBLIC_TRAIN",
                "K_FNSPID_CODEX_GOLD",
                "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
                "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
            ],
            ["NEWS", "DISCLOSURE"],
        ),
    ],
)
def test_mode_source_contracts(
    module: ModuleType,
    mode: str,
    datasets: list[str],
    swap_sources: list[str],
) -> None:
    rows = [{"dataset": name} for name in datasets]
    swaps = [
        {"dataset": "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE", "source_type": source}
        for source in swap_sources
    ]

    module._validate_mode_contract(module.AblationMode(mode), rows, swaps)


def test_mode_contract_fails_closed_on_k_data_in_no_k(module: ModuleType) -> None:
    with pytest.raises(RuntimeError, match="source contract"):
        module._validate_mode_contract(
            module.AblationMode.NO_K,
            [{"dataset": "PUBLIC_TRAIN"}, {"dataset": "K_FNSPID_RULE_SILVER"}],
            [],
        )
    with pytest.raises(RuntimeError, match="target-swap contract"):
        module._validate_mode_contract(
            module.AblationMode.NEWS_ONLY,
            [
                {"dataset": "PUBLIC_TRAIN"},
                {"dataset": "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE"},
            ],
            [
                {
                    "dataset": "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
                    "source_type": "DISCLOSURE",
                }
            ],
        )


def test_artifact_guard_fails_closed_when_bytes_change(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    path = tmp_path / "input.jsonl"
    path.write_text('{"value":1}\n', encoding="utf-8")
    paths = {"input": path}
    expected = module._artifact_records(paths)
    path.write_text('{"value":2}\n', encoding="utf-8")

    with pytest.raises(RuntimeError, match="changed"):
        module._assert_records_unchanged(expected, paths, "input")


def test_full_prepared_commitments_equal_canonical_v5() -> None:
    ablation = _validate(SCRIPT, "--mode", "FULL", "--seed", "17")
    canonical = _validate(CANONICAL_TRAINER, "--seed", "17")

    assert ablation["prepared_partition_commitments"] == canonical["prepared_partition_commitments"]
    assert ablation["partition_count"]["TRAIN"] == canonical["train_count"]
    assert ablation["target_swap_count"] == canonical["target_swap_count"]


def test_no_k_aggregate_writes_three_seed_selection_and_full_winner_manifest(
    module: ModuleType,
    no_k_validation: dict[str, Any],
    tmp_path: Path,
) -> None:
    report_dir = tmp_path / "reports"
    artifact_root = tmp_path / "artifacts"
    report_dir.mkdir()
    scores = {17: 0.61, 42: 0.67, 73: 0.63}
    for seed, score in scores.items():
        artifact_dir = artifact_root / f"seed{seed}"
        artifact_dir.mkdir(parents=True)
        for filename in (
            "adapter_config.json",
            "adapter_model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
        ):
            (artifact_dir / filename).write_text(f"seed={seed};file={filename}\n", encoding="utf-8")
        artifact_files = module.build_artifact_manifest(
            artifact_dir,
            (
                "adapter_config.json",
                "adapter_model.safetensors",
                "tokenizer.json",
                "tokenizer_config.json",
            ),
        )
        metadata = {
            "schema_version": "kf-deberta-sentiment-ablation-artifact/v1",
            "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
            "ablation_mode": "NO_K",
            "seed": seed,
            "artifact_files": artifact_files,
            "artifact_directory": module._display_path(artifact_dir),
        }
        (artifact_dir / "hannah_metadata.json").write_text(
            json.dumps(metadata),
            encoding="utf-8",
        )
        report = copy.deepcopy(no_k_validation)
        report.update(
            {
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "seed": seed,
                "artifact_files": artifact_files,
                "artifact_directory": module._display_path(artifact_dir),
                "selection_score": score,
                "selection_breakdown": {
                    "PUBLIC_SELECTION": {"macro_f1": score},
                    "K_FNSPID_DEVELOPMENT_SELECTION": {"macro_f1": score},
                    "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION": {"macro_f1": score},
                },
                "decision_calibration": {"sealed_gold_used_for_fit": False},
                "test": {"sample_count": 0, "status": "NOT_AVAILABLE_TO_ABLATION_RUNNER"},
            }
        )
        report["training_arguments"]["model_seed"] = seed
        (report_dir / f"kf-deberta-sentiment-no-k-seed{seed}.json").write_text(
            json.dumps(report),
            encoding="utf-8",
        )

    selection_path = tmp_path / "selection.json"
    winner_path = tmp_path / "selection/winner-artifact-manifest.json"
    result = module.aggregate_no_k_runs(
        report_dir=report_dir,
        artifact_root=artifact_root,
        selection_report_path=selection_path,
        winner_manifest_path=winner_path,
        validate_only=False,
    )

    assert result["status"] == "NO_K_AGGREGATION_WRITTEN"
    assert result["selected_seed"] == 42
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    winner = json.loads(winner_path.read_text(encoding="utf-8"))
    assert selection["schema_version"] == "k-fnspid-sentiment-ablation-selection/v1"
    assert selection["winner"]["seed"] == 42
    assert selection["deployment_eligible"] is False
    assert winner["schema_version"] == "k-fnspid-sentiment-ablation-winner-manifest/v1"
    assert winner["selected_seed"] == 42
    assert winner["deployment_eligible"] is False
    assert set(winner["artifact_files"]) == {
        "adapter_config.json",
        "adapter_model.safetensors",
        "hannah_metadata.json",
        "tokenizer.json",
        "tokenizer_config.json",
    }

    (artifact_root / "seed42/adapter_model.safetensors").write_text(
        "tampered\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="artifact manifest mismatch"):
        module.aggregate_no_k_runs(
            report_dir=report_dir,
            artifact_root=artifact_root,
            selection_report_path=tmp_path / "second-selection.json",
            winner_manifest_path=tmp_path / "second-winner.json",
            validate_only=True,
        )
