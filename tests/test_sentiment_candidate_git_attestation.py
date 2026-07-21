from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from hannah_montana_ai.services.sentiment_runtime_parity import (
    base_encoder_evidence,
    build_cpu_serving_parity_evidence,
    build_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
    build_confirmatory_baseline_commitments,
    canonical_json_sha256,
    directory_commitment,
    file_commitment,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import (
    RECIPE_RELATIVE_PATHS,
    canonical_statistical_analysis_plan,
)
from hannah_montana_ai.training.sentiment_git_attestation import (
    validate_candidate_git_attestation,
)


def _module() -> ModuleType:
    path = Path("scripts/attest_sentiment_candidate_git_commit.py")
    spec = importlib.util.spec_from_file_location("attest_sentiment_candidate_git", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repository: Path, *arguments: str) -> str:
    executable = shutil.which("git")
    assert executable is not None
    result = subprocess.run(  # noqa: S603
        [executable, *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _manifest(root: Path, relative_path: str) -> dict[str, int | str]:
    raw = (root / relative_path).read_bytes()
    return {
        "path": relative_path,
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }


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


def _repository_fixture(
    tmp_path: Path,
    *,
    external_git_commitment_required: bool | None = True,
) -> tuple[Path, Path, str]:
    remote = tmp_path / "remote.git"
    root = tmp_path / "repository"
    remote.mkdir()
    root.mkdir()
    _git(remote, "init", "--bare")
    _git(root, "init", "-b", "feature")
    _git(root, "config", "user.name", "Attestation Test")
    _git(root, "config", "user.email", "attestation@example.invalid")
    _git(root, "remote", "add", "origin", str(remote))

    news_row = {"source_type": "NEWS", "document_id": "news-1", "stock_code": "000001"}
    disclosure_row = {
        "source_type": "DISCLOSURE",
        "document_id": "disclosure-1",
        "stock_code": "000002",
    }
    files = {
        "data/gold/news-confirmatory.jsonl": json.dumps(news_row) + "\n",
        "data/gold/disclosure-confirmatory.jsonl": json.dumps(disclosure_row) + "\n",
        "docs/datasets/k-fnspid-sentiment-codebook.md": "# codebook\n",
        "src/hannah_montana_ai/training/sentiment_sampling.py": "SEED = 17\n",
        "reports/k-fnspid-sentiment-dataset-report.json": '{"source":"NEWS"}\n',
        "reports/k-fnspid-disclosure-sentiment-dataset-report.json": (
            '{"source":"DISCLOSURE"}\n'
        ),
        "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json": (
            '{"design":"stratified_probability"}\n'
        ),
        "scripts/train_kf_deberta_sentiment_v2.py": "def train():\n    return None\n",
    }
    for name, relative_path in RECIPE_RELATIVE_PATHS:
        files.setdefault(relative_path, f"# {name}\n")
    for relative_path, content in files.items():
        _write(root / relative_path, content)

    recipe_blobs = {
        name: _manifest(root, relative_path) for name, relative_path in RECIPE_RELATIVE_PATHS
    }

    reservations: dict[str, dict[str, Any]] = {}
    for source, relative_path, row in (
        ("NEWS", "data/gold/news-confirmatory.jsonl", news_row),
        ("DISCLOSURE", "data/gold/disclosure-confirmatory.jsonl", disclosure_row),
    ):
        item_id = f"{row['document_id']}::{row['stock_code']}"
        reservations[source] = {
            **_manifest(root, relative_path),
            "sample_count": 1,
            "item_id_set_sha256": canonical_json_sha256([item_id]),
            "source_record_set_sha256": canonical_json_sha256(
                [{"item_id": item_id, "source_record_sha256": canonical_json_sha256(row)}]
            ),
        }
    candidate_files = {"adapter_model.safetensors": {"bytes": 1, "sha256": "a" * 64}}
    baseline_commitments, runtime_parity = _baseline_and_parity(
        root,
        reservations=reservations,
        candidate_files=candidate_files,
    )
    lock: dict[str, Any] = {
        "schema_version": "sentiment-candidate-lock/v1",
        "sealed_reservations": reservations,
        "dataset_provenance": {
            "codebook": _manifest(root, "docs/datasets/k-fnspid-sentiment-codebook.md"),
            "sampling_implementation": _manifest(
                root,
                "src/hannah_montana_ai/training/sentiment_sampling.py",
            ),
            "dataset_reports": {
                "NEWS": _manifest(root, "reports/k-fnspid-sentiment-dataset-report.json"),
                "DISCLOSURE": _manifest(
                    root,
                    "reports/k-fnspid-disclosure-sentiment-dataset-report.json",
                ),
                "SAMPLING_DESIGN": _manifest(
                    root,
                    "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json",
                ),
            },
        },
        "recipe": {
            "schema_version": "sentiment-candidate-recipe/v2",
            "training_script": recipe_blobs["candidate_trainer"]["path"],
            "training_script_sha256": recipe_blobs["candidate_trainer"]["sha256"],
            "auxiliary_training_gold_promoter": recipe_blobs[
                "historical_auxiliary_promoter"
            ]["path"],
            "auxiliary_training_gold_promoter_sha256": recipe_blobs[
                "historical_auxiliary_promoter"
            ]["sha256"],
            "blobs": recipe_blobs,
        },
        "statistical_analysis_plan": canonical_statistical_analysis_plan(),
        "winner": {
            "version": "candidate-v1",
            "artifact_files": candidate_files,
        },
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_commitments_sha256(
            baseline_commitments
        ),
        "runtime_parity": runtime_parity,
    }
    if external_git_commitment_required is not None:
        lock["external_git_commitment_required"] = external_git_commitment_required
    lock_path = root / "reports/sentiment-candidate-lock.json"
    _write(lock_path, json.dumps(lock, ensure_ascii=False, indent=2) + "\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "Lock candidate and unlabeled reservations")
    commit_sha = _git(root, "rev-parse", "HEAD")
    _git(root, "push", "-u", "origin", "feature")
    _git(root, "fetch", "origin", "feature:refs/remotes/origin/feature")
    return root, lock_path, commit_sha


def _baseline_and_parity(
    root: Path,
    *,
    reservations: dict[str, dict[str, Any]],
    candidate_files: dict[str, dict[str, int | str]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    tfidf = root / "models/tfidf.joblib"
    _write(tfidf, "tfidf")
    pre_k = root / "models/pre-k"
    _write(pre_k / "adapter_model.safetensors", "pre-k")
    pre_k_report = root / "reports/pre-k.json"
    _write(pre_k_report, '{"schema_version":"pre-k/v1"}\n')

    fair_root = root / "artifacts/fair"
    fair_report_dir = root / "reports/fair"
    fair_runs = []
    for seed in (17, 42, 73):
        report = fair_report_dir / f"seed{seed}.json"
        _write(
            report,
            json.dumps(
                {"schema_version": "k-fnspid-fair-baseline-training/v1", "seed": seed}
            ),
        )
        fair_runs.append({"seed": seed, "report": file_commitment(report, root)})
    _write(fair_root / "seed42/model.safetensors", "fair")
    fair_selection = fair_report_dir / "selection.json"
    _write(
        fair_selection,
        json.dumps(
            {
                "schema_version": "k-fnspid-fair-baseline-selection/v1",
                "selected_seed": 42,
                "runs": fair_runs,
            }
        ),
    )

    no_k_reports: dict[str, dict[str, int | str]] = {}
    no_k_report_dir = root / "reports/ablations"
    for seed in (17, 42, 73):
        report = no_k_report_dir / f"seed{seed}.json"
        _write(
            report,
            json.dumps(
                {
                    "schema_version": "k-fnspid-sentiment-ablation-training/v1",
                    "ablation_mode": "NO_K",
                    "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                    "seed": seed,
                    "public_test_opened": False,
                    "test": {
                        "sample_count": 0,
                        "status": "NOT_AVAILABLE_TO_ABLATION_RUNNER",
                    },
                    "training_strategy": (
                        "group-purged-three-way-ablation-target-swap-rdrop-"
                        "hierarchical-upper6-lora/v1"
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
                }
            ),
        )
        no_k_reports[str(seed)] = file_commitment(report, root)
    no_k_artifact = root / "artifacts/no-k/seed42"
    _write(no_k_artifact / "adapter_model.safetensors", "no-k")
    _write(
        no_k_artifact / "hannah_metadata.json",
        json.dumps(
            {
                "schema_version": "kf-deberta-sentiment-ablation-artifact/v1",
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "ablation_mode": "NO_K",
                "seed": 42,
            }
        ),
    )
    winner = root / "artifacts/no-k/selection/winner.json"
    _write(
        winner,
        json.dumps(
            {
                "schema_version": "k-fnspid-sentiment-ablation-winner-manifest/v1",
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "ablation_mode": "NO_K",
                "selected_seed": 42,
                "selected_training_report": no_k_reports["42"],
                "artifact_directory": str(no_k_artifact.relative_to(root)),
                "artifact_files": directory_commitment(no_k_artifact, root)["files"],
                "confirmatory_or_public_test_used": False,
                "deployment_eligible": False,
            }
        ),
    )
    no_k_selection = no_k_report_dir / "selection.json"
    _write(
        no_k_selection,
        json.dumps(
            {
                "schema_version": "k-fnspid-sentiment-ablation-selection/v1",
                "ablation_mode": "NO_K",
                "candidate_reports": no_k_reports,
                "winner": {"seed": 42},
                "winner_artifact_manifest": file_commitment(winner, root),
                "deployment_eligible": False,
            }
        ),
    )
    baselines = build_confirmatory_baseline_commitments(
        project_root=root,
        tfidf_model=tfidf,
        pre_k_artifact=pre_k,
        pre_k_training_report=pre_k_report,
        fair_artifact_root=fair_root,
        fair_selection_report=fair_selection,
        no_k_selection_report=no_k_selection,
        no_k_winner_manifest=winner,
    )

    evaluator_base = root / "models/evaluator-base"
    runtime_base = root / "models/runtime-base"
    _write(evaluator_base / "model.safetensors", "base")
    _write(runtime_base / "model.safetensors", "base")
    inputs = {
        source: [
            {
                "item_id": ("news-1::000001" if source == "NEWS" else "disclosure-1::000002"),
                "source_record_sha256": (
                    canonical_json_sha256(
                        {
                            "source_type": source,
                            "document_id": "news-1" if source == "NEWS" else "disclosure-1",
                            "stock_code": "000001" if source == "NEWS" else "000002",
                        }
                    )
                ),
            }
        ]
        for source in ("NEWS", "DISCLOSURE")
    }
    outputs = [
        {"item_id": row["item_id"], "label": "POSITIVE", "logits": [-1.0, 0.0, 1.0]}
        for source in ("NEWS", "DISCLOSURE")
        for row in inputs[source]
    ]
    evidence = build_cpu_serving_parity_evidence(
        candidate_version="candidate-v1",
        candidate_artifact_manifest_sha256=canonical_json_sha256(candidate_files),
        reservation_inputs=inputs,
        evaluator_outputs=outputs,
        packaged_runtime_outputs=outputs,
        evaluator_base_model=base_encoder_evidence(evaluator_base, root),
        packaged_runtime_base_model=base_encoder_evidence(runtime_base, root),
        generated_at="2026-07-16T00:00:00+00:00",
    )
    evidence_path = root / "reports/runtime-parity.json"
    _write(evidence_path, json.dumps(evidence))
    parity = build_runtime_parity_lock_commitment(
        evidence_path=evidence_path,
        project_root=root,
        expected_candidate_version="candidate-v1",
        expected_candidate_artifact_manifest_sha256=canonical_json_sha256(candidate_files),
        sealed_reservations=reservations,
    )
    return baselines, parity


def _create(
    module: ModuleType,
    root: Path,
    lock_path: Path,
    commit_sha: str,
    *,
    output: Path | None = None,
) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        module.create_attestation(
            project_root=root,
            candidate_lock_path=lock_path,
            commit_sha=commit_sha,
            remote_name="origin",
            remote_ref="feature",
            output_path=output or root / "reports/sentiment-candidate-git-attestation.json",
        ),
    )


def test_attests_exact_pushed_commit_and_all_required_manifests(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)

    result = _create(module, root, lock_path, commit_sha)

    output = root / "reports/sentiment-candidate-git-attestation.json"
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert result == persisted
    assert result["schema_version"] == "sentiment-candidate-git-attestation/v1"
    assert result["role"] == "REMOTE_GIT_HISTORY_COMMITMENT_NOT_INDEPENDENT_TIMESTAMP"
    assert result["git"]["commit_sha"] == commit_sha
    assert len(result["git"]["tree_sha"]) == 40
    assert result["git"]["remote_tracking_ref"] == "refs/remotes/origin/feature"
    assert set(result["committed_artifact_manifests"]["sealed_reservations"]) == {
        "NEWS",
        "DISCLOSURE",
    }
    assert set(
        result["committed_artifact_manifests"]["dataset_provenance"]["dataset_reports"]
    ) == {"NEWS", "DISCLOSURE", "SAMPLING_DESIGN"}
    assert set(result["committed_artifact_manifests"]["recipe_blobs"]) == {
        name for name, _ in RECIPE_RELATIVE_PATHS
    }
    assert stat_mode(output) == 0o600
    validated = validate_candidate_git_attestation(
        output,
        lock_path,
        project_root=root,
    )
    assert validated["commit_sha"] == commit_sha
    assert validated["candidate_lock_sha256"] == sha256(lock_path.read_bytes()).hexdigest()


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def test_rejects_commit_not_pushed_to_fetched_remote_ref(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, _ = _repository_fixture(tmp_path)
    _write(root / "local-only.txt", "not pushed\n")
    _git(root, "add", "local-only.txt")
    _git(root, "commit", "-m", "Local only commit")
    local_commit = _git(root, "rev-parse", "HEAD")

    with pytest.raises(module.AttestationError, match="ancestor"):
        _create(module, root, lock_path, local_commit)


def test_rejects_local_lock_that_differs_from_committed_bytes(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    payload = json.loads(lock_path.read_text(encoding="utf-8"))
    payload["tampered"] = True
    lock_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(module.AttestationError, match="lock bytes"):
        _create(module, root, lock_path, commit_sha)


def test_rejects_committed_artifact_that_breaks_lock_commitment(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, _ = _repository_fixture(tmp_path)
    codebook = root / "docs/datasets/k-fnspid-sentiment-codebook.md"
    codebook.write_text("# changed after lock\n", encoding="utf-8")
    _git(root, "add", str(codebook.relative_to(root)))
    _git(root, "commit", "-m", "Break codebook commitment")
    commit_sha = _git(root, "rev-parse", "HEAD")
    _git(root, "push", "origin", "feature")
    _git(root, "fetch", "origin", "feature:refs/remotes/origin/feature")

    with pytest.raises(module.AttestationError, match="codebook.*commitment"):
        _create(module, root, lock_path, commit_sha)


def test_rejects_any_committed_recipe_blob_that_breaks_lock_commitment(
    tmp_path: Path,
) -> None:
    module = _module()
    root, lock_path, _ = _repository_fixture(tmp_path)
    evaluator = root / "scripts/evaluate_locked_kf_deberta_sentiment.py"
    evaluator.write_text("# changed after lock\n", encoding="utf-8")
    _git(root, "add", str(evaluator.relative_to(root)))
    _git(root, "commit", "-m", "Break evaluator commitment")
    commit_sha = _git(root, "rev-parse", "HEAD")
    _git(root, "push", "origin", "feature")
    _git(root, "fetch", "origin", "feature:refs/remotes/origin/feature")

    with pytest.raises(module.AttestationError, match="recipe blob evaluator.*commitment"):
        _create(module, root, lock_path, commit_sha)


def test_v6_recipe_contract_includes_raw_reference_reproduction() -> None:
    module = _module()

    assert module.V6_RECIPE_RELATIVE_PATHS["v6_raw_reference_runtime"] == (
        "src/hannah_montana_ai/services/kr_finbert_sc_raw_reference.py"
    )
    assert module.V6_RECIPE_RELATIVE_PATHS["v6_raw_reference_materializer"] == (
        "scripts/materialize_kr_finbert_sc_raw_reference.py"
    )


def test_rejects_incomplete_recipe_blob_set(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, _ = _repository_fixture(tmp_path)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    del lock["recipe"]["blobs"]["evaluator"]
    lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _git(root, "add", str(lock_path.relative_to(root)))
    _git(root, "commit", "-m", "Remove evaluator commitment")
    commit_sha = _git(root, "rev-parse", "HEAD")
    _git(root, "push", "origin", "feature")
    _git(root, "fetch", "origin", "feature:refs/remotes/origin/feature")

    with pytest.raises(module.AttestationError, match="집합이 완전하지"):
        _create(module, root, lock_path, commit_sha)


def test_rejects_symlink_and_path_escape(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    symlink = root / "reports/lock-link.json"
    symlink.symlink_to(lock_path)

    with pytest.raises(module.AttestationError, match="symlink"):
        _create(module, root, symlink, commit_sha)
    with pytest.raises(module.AttestationError, match="밖"):
        module.create_attestation(
            project_root=root,
            candidate_lock_path=lock_path,
            commit_sha=commit_sha,
            remote_name="origin",
            remote_ref="feature",
            output_path=root / "../escaped-attestation.json",
        )


def test_attestation_output_is_write_once(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    output = root / "reports/sentiment-candidate-git-attestation.json"
    _create(module, root, lock_path, commit_sha, output=output)

    with pytest.raises(module.AttestationError, match="write-once"):
        _create(module, root, lock_path, commit_sha, output=output)


@pytest.mark.parametrize("required", [None, False])
def test_requires_external_git_commitment_flag(
    tmp_path: Path,
    required: bool | None,
) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(
        tmp_path,
        external_git_commitment_required=required,
    )

    with pytest.raises(module.AttestationError, match="external_git_commitment_required=true"):
        _create(module, root, lock_path, commit_sha)


def test_requires_full_commit_sha(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)

    with pytest.raises(module.AttestationError, match="전체 40/64자리"):
        _create(module, root, lock_path, commit_sha[:12])


def test_rejects_symlink_output(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("{}\n", encoding="utf-8")
    output = root / "reports/attestation-link.json"
    os.symlink(outside, output)

    with pytest.raises(module.AttestationError, match="symlink"):
        _create(module, root, lock_path, commit_sha, output=output)


def test_consumer_revalidates_working_tree_evidence(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    output = root / "reports/sentiment-candidate-git-attestation.json"
    _create(module, root, lock_path, commit_sha, output=output)
    codebook = root / "docs/datasets/k-fnspid-sentiment-codebook.md"
    codebook.write_text("# post-attestation mutation\n", encoding="utf-8")

    with pytest.raises(ValueError, match="codebook working-tree"):
        validate_candidate_git_attestation(output, lock_path, project_root=root)


def test_consumer_revalidates_every_working_tree_recipe_blob(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    output = root / "reports/sentiment-candidate-git-attestation.json"
    _create(module, root, lock_path, commit_sha, output=output)
    evaluator = root / "scripts/evaluate_locked_kf_deberta_sentiment.py"
    evaluator.write_text("# post-attestation mutation\n", encoding="utf-8")

    with pytest.raises(ValueError, match="recipe blob evaluator working-tree"):
        validate_candidate_git_attestation(output, lock_path, project_root=root)


def test_consumer_revalidates_current_remote_tracking_ref(tmp_path: Path) -> None:
    module = _module()
    root, lock_path, commit_sha = _repository_fixture(tmp_path)
    output = root / "reports/sentiment-candidate-git-attestation.json"
    _create(module, root, lock_path, commit_sha, output=output)
    _git(root, "checkout", "--orphan", "rewritten")
    _git(root, "rm", "-rf", ".")
    _write(root / "rewritten.txt", "unrelated history\n")
    _git(root, "add", "rewritten.txt")
    _git(root, "commit", "-m", "Rewrite remote history")
    _git(root, "push", "--force", "origin", "HEAD:feature")
    _git(root, "fetch", "origin", "feature:refs/remotes/origin/feature")
    _git(root, "checkout", "feature")

    with pytest.raises(ValueError, match="ancestor"):
        validate_candidate_git_attestation(output, lock_path, project_root=root)
