from __future__ import annotations

import json
from pathlib import Path

import pytest

from hannah_montana_ai.training.sentiment_baseline_commitments import (
    build_confirmatory_baseline_commitments,
    directory_commitment,
    file_commitment,
    validate_confirmatory_baseline_commitments,
)


def test_confirmatory_baselines_require_three_seed_reports_and_full_winners(
    tmp_path: Path,
) -> None:
    paths = _baseline_fixture(tmp_path)
    locked = build_confirmatory_baseline_commitments(project_root=tmp_path, **paths)

    baselines = locked["baselines"]
    assert set(baselines["kr_finbert_sc_same_data_fair"]["seed_reports"]) == {
        "17",
        "42",
        "73",
    }
    assert set(baselines["kf_deberta_no_k_ablation"]["seed_reports"]) == {
        "17",
        "42",
        "73",
    }
    assert baselines["pre_k_fnspid_kf_deberta"]["winner_artifact"]["files"]
    assert validate_confirmatory_baseline_commitments(locked, tmp_path) == locked

    no_k_winner = Path(
        tmp_path
        / baselines["kf_deberta_no_k_ablation"]["winner_artifact"]["path"]
        / "adapter_model.safetensors"
    )
    no_k_winner.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="artifact 바이트"):
        validate_confirmatory_baseline_commitments(locked, tmp_path)


def test_confirmatory_baseline_lock_fails_without_no_k_selection(tmp_path: Path) -> None:
    paths = _baseline_fixture(tmp_path)
    paths["no_k_selection_report"].unlink()

    with pytest.raises((FileNotFoundError, ValueError)):
        build_confirmatory_baseline_commitments(project_root=tmp_path, **paths)


def test_no_k_baseline_rejects_k_fnspid_training_source(tmp_path: Path) -> None:
    paths = _baseline_fixture(tmp_path)
    report_path = tmp_path / "reports/ablations/no-k-seed17.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["training_source_distribution"]["K_FNSPID_CODEX_GOLD"] = 1
    report["source_selection_provenance"]["K_FNSPID_CODEX_GOLD"] = {
        "decision": "INCLUDED",
        "pre_dedup_selected_count": 1,
    }
    _write_json(report_path, report)
    selection_path = paths["no_k_selection_report"]
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selection["candidate_reports"]["17"] = file_commitment(report_path, tmp_path)
    _write_json(selection_path, selection)

    with pytest.raises(ValueError, match="K-FNSPID"):
        build_confirmatory_baseline_commitments(project_root=tmp_path, **paths)


def _baseline_fixture(root: Path) -> dict[str, Path]:
    tfidf = _write(root / "models/tfidf.joblib", b"tfidf")
    pre_k = root / "models/pre-k"
    _write(pre_k / "adapter_model.safetensors", b"pre-k")
    _write(pre_k / "hannah_metadata.json", b"{}")
    pre_k_report = _write_json(root / "reports/pre-k.json", {"schema_version": "pre-k/v1"})

    fair_root = root / "artifacts/fair"
    fair_report_dir = root / "reports/fair"
    fair_runs: list[dict[str, object]] = []
    for seed in (17, 42, 73):
        report_path = _write_json(
            fair_report_dir / f"seed{seed}.json",
            {"schema_version": "k-fnspid-fair-baseline-training/v1", "seed": seed},
        )
        fair_runs.append({"seed": seed, "report": file_commitment(report_path, root)})
    _write(fair_root / "seed42/model.safetensors", b"fair")
    _write(fair_root / "seed42/hannah_metadata.json", b"{}")
    fair_selection = _write_json(
        fair_report_dir / "selection.json",
        {
            "schema_version": "k-fnspid-fair-baseline-selection/v1",
            "selected_seed": 42,
            "runs": fair_runs,
        },
    )

    no_k_root = root / "artifacts/no-k"
    no_k_report_dir = root / "reports/ablations"
    no_k_reports: dict[str, dict[str, int | str]] = {}
    for seed in (17, 42, 73):
        report_path = _write_json(
            no_k_report_dir / f"no-k-seed{seed}.json",
            {
                "schema_version": "k-fnspid-sentiment-ablation-training/v1",
                "ablation_mode": "NO_K",
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "public_test_opened": False,
                "test": {
                    "sample_count": 0,
                    "status": "NOT_AVAILABLE_TO_ABLATION_RUNNER",
                },
                "seed": seed,
                "training_strategy": (
                    "group-purged-three-way-ablation-target-swap-rdrop-hierarchical-"
                    "upper6-lora/v1"
                ),
                "training_source_distribution": {"PUBLIC_TRAIN": 7413},
                "source_selection_provenance": _no_k_source_provenance(),
                "target_swap_count": 0,
                "target_swap_source_distribution": {},
                "partition_count": {"PUBLIC_TEST_NOT_LOADED": 0},
                "decision_calibration": {
                    "public_test_used_for_fit": False,
                    "sealed_gold_used_for_fit": False,
                },
            },
        )
        no_k_reports[str(seed)] = file_commitment(report_path, root)
    no_k_winner_dir = no_k_root / "seed42"
    _write(no_k_winner_dir / "adapter_model.safetensors", b"no-k")
    _write_json(
        no_k_winner_dir / "hannah_metadata.json",
        {
            "schema_version": "kf-deberta-sentiment-ablation-artifact/v1",
            "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
            "ablation_mode": "NO_K",
            "seed": 42,
        },
    )
    winner_files = directory_commitment(no_k_winner_dir, root)["files"]
    winner_manifest = _write_json(
        no_k_root / "selection/winner-artifact-manifest.json",
        {
            "schema_version": "k-fnspid-sentiment-ablation-winner-manifest/v1",
            "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
            "ablation_mode": "NO_K",
            "selected_seed": 42,
            "selected_training_report": no_k_reports["42"],
            "artifact_directory": no_k_winner_dir.relative_to(root).as_posix(),
            "artifact_files": winner_files,
            "confirmatory_or_public_test_used": False,
            "deployment_eligible": False,
        },
    )
    no_k_selection = _write_json(
        no_k_report_dir / "no-k-selection.json",
        {
            "schema_version": "k-fnspid-sentiment-ablation-selection/v1",
            "artifact_role": "PAPER_ABLATION_EVIDENCE_NOT_DEPLOYMENT_SELECTION",
            "ablation_mode": "NO_K",
            "required_seed_runs": [17, 42, 73],
            "candidate_reports": no_k_reports,
            "winner": {"seed": 42},
            "winner_artifact_manifest": file_commitment(winner_manifest, root),
            "deployment_eligible": False,
        },
    )
    return {
        "tfidf_model": tfidf,
        "pre_k_artifact": pre_k,
        "pre_k_training_report": pre_k_report,
        "fair_artifact_root": fair_root,
        "fair_selection_report": fair_selection,
        "no_k_selection_report": no_k_selection,
        "no_k_winner_manifest": winner_manifest,
    }


def _write(path: Path, payload: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def _no_k_source_provenance() -> dict[str, dict[str, int | str]]:
    excluded = (
        "K_FNSPID_CODEX_GOLD",
        "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_RULE_SILVER",
        "K_FNSPID_DISCLOSURE_RULE_SILVER",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE",
    )
    return {
        "PUBLIC_TRAIN": {"decision": "INCLUDED", "pre_dedup_selected_count": 7413},
        **{
            source: {"decision": "EXCLUDED", "pre_dedup_selected_count": 0}
            for source in excluded
        },
    }


def _write_json(path: Path, payload: object) -> Path:
    return _write(
        path,
        (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"),
    )
