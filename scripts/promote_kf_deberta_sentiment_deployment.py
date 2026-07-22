from __future__ import annotations

import argparse
import fcntl
import hmac
import json
import math
import os
import shutil
import stat
import subprocess  # nosec B404
import tempfile
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, NoReturn, cast

from hannah_montana_ai.services.sentiment_artifact_contract import (
    CANDIDATE_MODEL as V6_CANDIDATE_MODEL,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    LOCK_SCHEMA_VERSION as V6_LOCK_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    validate_source_hierarchical_activation,
    validate_source_hierarchical_artifact,
    validate_source_hierarchical_base_directory,
)
from hannah_montana_ai.services.sentiment_input import (
    SENTIMENT_LOGIT_BIAS_DOMAINS,
    validated_sentiment_logit_biases,
)
from hannah_montana_ai.services.sentiment_release import (
    AUXILIARY_TRAINING_INPUTS,
    CANDIDATE_TRAINING_STRATEGY,
    CURRENT_SCHEMA_VERSION,
    FAIR_BASELINE_TRAINING_STRATEGY,
    LOCAL_ATTESTATION_MODE,
    RELEASE_SCHEMA_VERSION,
    REQUIRED_EVIDENCE_ROLES,
    REQUIRED_RUNTIME_CODE,
    V6_CURRENT_SCHEMA_VERSION,
    V6_RELEASE_SCHEMA_VERSION,
    V6_REQUIRED_RUNTIME_CODE,
    SentimentReleaseError,
    expected_sentiment_gate_checks,
    validate_strict_sentiment_gate,
    verify_sentiment_release,
)
from hannah_montana_ai.services.sentiment_runtime_parity import (
    validate_cpu_serving_parity_evidence,
    validate_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
    validate_confirmatory_baseline_commitments,
)
from hannah_montana_ai.training.sentiment_git_attestation import (
    validate_candidate_git_attestation,
)
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    validate_v6_confirmatory_baseline_commitments,
    validate_v6_statistical_analysis_plan,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK_MANIFEST = PROJECT_ROOT / "reports/sentiment-candidate-lock.json"
DEFAULT_LOCKED_ARTIFACT = PROJECT_ROOT / "artifacts/sentiment/locked"
DEFAULT_BENCHMARK_REPORT = PROJECT_ROOT / "reports/korean-finance-sentiment-benchmark-v4.json"
DEFAULT_TARGET_ARTIFACT = PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment_v2"
DEFAULT_TARGET_REPORT = PROJECT_ROOT / "reports/kf-deberta-sentiment-training-report.json"
DEFAULT_TARGET_BENCHMARK = PROJECT_ROOT / "reports/korean-finance-sentiment-benchmark.json"
DEFAULT_RELEASES_ROOT = PROJECT_ROOT / "releases/sentiment"
DEFAULT_CURRENT_POINTER = DEFAULT_RELEASES_ROOT / "current.json"
DEFAULT_RUNTIME_BASE_MODEL = Path("/app/models/kf-deberta-base")
DEFAULT_GIT_ATTESTATION = PROJECT_ROOT / "reports/sentiment-candidate-git-attestation.json"
DEFAULT_CONSUMPTION_RECEIPT = PROJECT_ROOT / "reports/sentiment-sealed-evaluation-consumption.json"

LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v1"
TRAINING_SCHEMA_VERSION = "kf-deberta-sentiment-training/v2"
ARTIFACT_SCHEMA_VERSION = "kf-deberta-sentiment-artifact/v2"
BENCHMARK_SCHEMA_VERSION = "korean-finance-sentiment-benchmark/v4"
INPUT_FEATURE_VERSION = "source-target-prefix-head-tail/v2"
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
CANDIDATE_MODEL = "kf_deberta_lora_locked"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
TRAINING_SCRIPT = "scripts/train_kf_deberta_sentiment_v2.py"
LOCKED_ARTIFACT_DIRECTORY = "artifacts/sentiment/locked"
TARGET_ARTIFACT_DIRECTORY = "src/hannah_montana_ai/model_store/kf_deberta_sentiment_v2"
TARGET_REPORT_PATH = "reports/kf-deberta-sentiment-training-report.json"
IMMUTABLE_BENCHMARK_PATH = "reports/korean-finance-sentiment-benchmark-v4.json"
TARGET_BENCHMARK_PATH = "reports/korean-finance-sentiment-benchmark.json"
CONSUMPTION_RECEIPT_PATH = "reports/sentiment-sealed-evaluation-consumption.json"
TRAINING_ARTIFACTS = frozenset(
    {
        "adapter_config.json",
        "adapter_model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    }
)
LOCKED_ARTIFACTS = TRAINING_ARTIFACTS | {"hannah_metadata.json"}
EXPECTED_LORA_LAYERS = tuple(range(6, 12))
EXPECTED_TARGET_MODULES = frozenset({"query_proj", "key_proj", "value_proj", "dense"})
MAX_JSON_BYTES = 64 * 1024 * 1024


class PromotionError(RuntimeError):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="봉인 평가 gate를 통과한 KF-DeBERTa 후보를 배포 경로에 승격한다."
    )
    parser.add_argument("--candidate-report", type=Path, required=True)
    parser.add_argument("--lock-manifest", type=Path, default=DEFAULT_LOCK_MANIFEST)
    parser.add_argument("--locked-artifact", type=Path, default=DEFAULT_LOCKED_ARTIFACT)
    parser.add_argument("--benchmark-report", type=Path, default=DEFAULT_BENCHMARK_REPORT)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--runtime-base-model", type=Path, default=DEFAULT_RUNTIME_BASE_MODEL)
    parser.add_argument("--releases-root", type=Path, default=DEFAULT_RELEASES_ROOT)
    parser.add_argument("--current-pointer", type=Path, default=DEFAULT_CURRENT_POINTER)
    parser.add_argument(
        "--candidate-git-attestation",
        type=Path,
        default=DEFAULT_GIT_ATTESTATION,
    )
    parser.add_argument(
        "--consumption-receipt",
        type=Path,
        default=DEFAULT_CONSUMPTION_RECEIPT,
    )
    parser.add_argument(
        "--synthetic-fixture",
        action="store_true",
        help="test/local contract fixture만 허용하며 production eligibility는 생성하지 않는다.",
    )
    args = parser.parse_args()
    source_git_commit, source_dirty = _git_source(PROJECT_ROOT)
    try:
        result = promote_candidate(
            project_root=PROJECT_ROOT,
            lock_manifest=args.lock_manifest,
            locked_artifact=args.locked_artifact,
            candidate_report=args.candidate_report,
            benchmark_report=args.benchmark_report,
            base_model_path=args.base_model,
            runtime_base_model_path=args.runtime_base_model,
            releases_root=args.releases_root,
            current_pointer=args.current_pointer,
            source_git_commit=source_git_commit,
            source_dirty=source_dirty,
            candidate_git_attestation=args.candidate_git_attestation,
            consumption_receipt=args.consumption_receipt,
            synthetic_fixture=args.synthetic_fixture,
        )
    except PromotionError as exception:
        raise SystemExit(str(exception)) from exception
    print(json.dumps(result, ensure_ascii=False))


def promote_candidate(
    *,
    project_root: Path,
    lock_manifest: Path,
    locked_artifact: Path,
    candidate_report: Path,
    benchmark_report: Path,
    base_model_path: Path,
    runtime_base_model_path: Path,
    releases_root: Path,
    current_pointer: Path,
    source_git_commit: str,
    source_dirty: bool,
    candidate_git_attestation: Path | None = None,
    consumption_receipt: Path | None = None,
    synthetic_fixture: bool = False,
) -> dict[str, Any]:
    root = _existing_project_root(project_root)
    lock_path = _existing_project_path(lock_manifest, root, "후보 lock manifest", directory=False)
    artifact_dir = _existing_project_path(
        locked_artifact, root, "잠긴 후보 artifact", directory=True
    )
    report_path = _existing_project_path(
        candidate_report, root, "후보 학습 report", directory=False
    )
    benchmark_path = _existing_project_path(
        benchmark_report, root, "v4 benchmark report", directory=False
    )
    base_model = _existing_directory(base_model_path, "base model")
    release_root = _release_root_path(releases_root, root)
    pointer_path = _current_pointer_path(current_pointer, release_root)
    if not _is_git_commit(source_git_commit) or not isinstance(source_dirty, bool):
        raise PromotionError("release source Git 계약이 올바르지 않습니다.")

    lock = _load_json_object(lock_path, "후보 lock manifest")
    training = _load_json_object(report_path, "후보 학습 report")
    benchmark = _load_json_object(benchmark_path, "v4 benchmark report")
    if lock.get("schema_version") == V6_LOCK_SCHEMA_VERSION:
        return promote_v6_candidate(
            root=root,
            lock_path=lock_path,
            artifact_dir=artifact_dir,
            report_path=report_path,
            benchmark_path=benchmark_path,
            base_model_path=base_model,
            release_root=release_root,
            current_pointer=pointer_path,
            source_git_commit=source_git_commit,
            source_dirty=source_dirty,
            candidate_git_attestation=candidate_git_attestation,
            consumption_receipt=consumption_receipt,
            synthetic_fixture=synthetic_fixture,
        )
    if not runtime_base_model_path.is_absolute():
        raise PromotionError("runtime base model 경로는 절대경로여야 합니다.")
    verified = _validate_release_contract(
        root=root,
        lock_path=lock_path,
        artifact_dir=artifact_dir,
        report_path=report_path,
        benchmark_path=benchmark_path,
        lock=lock,
        training=training,
        benchmark=benchmark,
    )
    try:
        release = _create_immutable_release(
            root=root,
            release_root=release_root,
            current_pointer=pointer_path,
            artifact_dir=artifact_dir,
            report_path=report_path,
            benchmark_path=benchmark_path,
            lock_path=lock_path,
            lock=lock,
            benchmark=benchmark,
            base_model_path=base_model,
            runtime_base_model_path=runtime_base_model_path,
            source_git_commit=source_git_commit,
            source_dirty=source_dirty,
            verified=verified,
        )
    except PromotionError:
        raise
    except Exception as exception:
        raise PromotionError("immutable sentiment release 활성화에 실패했습니다.") from exception
    return {
        "schema_version": "kf-deberta-sentiment-deployment-promotion/v2",
        "version": verified["version"],
        "candidate_report_sha256": verified["candidate_report_sha256"],
        "benchmark_report_sha256": _file_sha256(benchmark_path),
        "candidate_lock_sha256": _file_sha256(lock_path),
        "artifact_manifest_sha256": verified["artifact_manifest_sha256"],
        "release_id": release["release_id"],
        "release_manifest": release["release_manifest"],
        "current_pointer": release["current_pointer"],
        "attestation_mode": LOCAL_ATTESTATION_MODE,
        "production_eligible": False,
    }


def promote_v6_candidate(
    *,
    root: Path,
    lock_path: Path,
    artifact_dir: Path,
    report_path: Path,
    benchmark_path: Path,
    base_model_path: Path,
    release_root: Path,
    current_pointer: Path,
    source_git_commit: str,
    source_dirty: bool,
    candidate_git_attestation: Path | None,
    consumption_receipt: Path | None,
    synthetic_fixture: bool,
) -> dict[str, Any]:
    lock = _load_json_object(lock_path, "v6 후보 lock")
    training = _load_json_object(report_path, "v6 후보 학습 report")
    benchmark = _load_json_object(benchmark_path, "v6 benchmark report")
    try:
        contract = validate_source_hierarchical_artifact(artifact_dir, training)
        base = validate_source_hierarchical_base_directory(base_model_path)
    except RuntimeError as exception:
        raise PromotionError(str(exception)) from exception
    winner = _mapping(lock.get("winner"), "v6 lock winner")
    if (
        lock.get("schema_version") != V6_LOCK_SCHEMA_VERSION
        or lock.get("selection_only") is not True
        or lock.get("public_test_evaluated_before_lock") is not False
        or lock.get("operational_sealed_gold_evaluated_before_lock") is not False
        or winner.get("model_family") != V6_MODEL_FAMILY
        or winner.get("version") != contract.version
        or winner.get("artifact_files") != contract.locked_manifest
        or winner.get("artifact_manifest_sha256") != contract.locked_manifest_sha256
        or winner.get("base_source_kind") != contract.base_source_kind
        or winner.get("base_source") != contract.base_source
        or winner.get("report_sha256") != _file_sha256(report_path)
    ):
        raise PromotionError("v6 lock/report/artifact 연결이 다릅니다.")
    if contract.base_source_kind == "DAPT_MERGED_FP32":
        declared = contract.base_source.get("merged_directory")
        if (
            base.name != "merged_fp32"
            or not isinstance(declared, str)
            or base != Path(declared).resolve(strict=True)
        ):
            raise PromotionError("DAPT 승격은 잠긴 학습 provenance의 merged_fp32만 허용합니다.")
    parity_record = _mapping(lock.get("runtime_parity"), "v6 runtime parity lock")
    parity_source = _manifest_project_path(
        root,
        parity_record.get("evidence"),
        "v6 runtime parity evidence",
    )
    parity = validate_cpu_serving_parity_evidence(
        _load_json_object(parity_source, "v6 runtime parity evidence")
    )
    parity_candidate = _mapping(parity.get("candidate"), "v6 parity candidate")
    if (
        parity_candidate.get("model_family") != V6_MODEL_FAMILY
        or parity_candidate.get("version") != contract.version
        or parity_candidate.get("artifact_manifest_sha256")
        != contract.locked_manifest_sha256
        or parity_candidate.get("base_source_kind") != contract.base_source_kind
    ):
        raise PromotionError("v6 runtime parity가 승격 후보와 다릅니다.")

    evidence_sources: dict[str, Path] = {
        "training_report": report_path,
        "benchmark_report": benchmark_path,
        "candidate_lock": lock_path,
        "cpu_runtime_parity": parity_source,
    }
    candidate_lock_git_commit: str | None = None
    release_mode = (
        "SYNTHETIC_CONTRACT_FIXTURE" if synthetic_fixture else "PRODUCTION_CANDIDATE"
    )
    if synthetic_fixture:
        fixture = _mapping(benchmark.get("fixture_contract"), "v6 fixture contract")
        if fixture.get("production_eligible") is not False:
            raise PromotionError("synthetic fixture는 production eligible일 수 없습니다.")
    else:
        try:
            validate_v6_statistical_analysis_plan(lock.get("statistical_analysis_plan"))
            v6_baselines = validate_v6_confirmatory_baseline_commitments(
                lock.get("baseline_commitments"),
                root,
                candidate_training_report=training,
            )
        except ValueError as exception:
            raise PromotionError(str(exception)) from exception
        if lock.get("baseline_commitments_sha256") != baseline_commitments_sha256(
            v6_baselines
        ):
            raise PromotionError("v6 baseline commitment digest가 lock과 다릅니다.")
        try:
            validate_source_hierarchical_activation(benchmark, contract)
        except RuntimeError as exception:
            raise PromotionError(str(exception)) from exception
        if candidate_git_attestation is None or consumption_receipt is None:
            raise PromotionError(
                "v6 production candidate에는 Git attestation/receipt가 필요합니다."
            )
        attestation_path = _existing_project_path(
            candidate_git_attestation,
            root,
            "v6 candidate Git attestation",
            directory=False,
        )
        receipt_path = _existing_project_path(
            consumption_receipt,
            root,
            "v6 consumption receipt",
            directory=False,
        )
        try:
            normalized_attestation = validate_candidate_git_attestation(
                attestation_path,
                lock_path,
                project_root=root,
            )
        except ValueError as exception:
            raise PromotionError(str(exception)) from exception
        candidate_lock_git_commit = str(normalized_attestation["commit_sha"])
        receipt = _load_json_object(receipt_path, "v6 consumption receipt")
        if (
            receipt.get("candidate_version") != contract.version
            or receipt.get("candidate_lock_manifest_sha256") != _file_sha256(lock_path)
            or receipt.get("candidate_artifact_manifest_sha256")
            != contract.locked_manifest_sha256
            or receipt.get("cpu_runtime_parity") != lock.get("runtime_parity")
            or receipt.get("labels_loaded_before_receipt") is not False
        ):
            raise PromotionError("v6 consumption receipt가 승격 후보와 다릅니다.")
        evidence_sources["candidate_git_attestation"] = attestation_path
        evidence_sources["consumption_receipt"] = receipt_path
    release = _create_v6_immutable_release(
        root=root,
        release_root=release_root,
        current_pointer=current_pointer,
        artifact_dir=artifact_dir,
        base_model_path=base,
        contract=contract,
        evidence_sources=evidence_sources,
        release_mode=release_mode,
        source_git_commit=source_git_commit,
        source_dirty=source_dirty,
        candidate_lock_git_commit=candidate_lock_git_commit,
    )
    return {
        "schema_version": "kf-deberta-source-hierarchical-deployment-promotion/v1",
        "model_family": V6_MODEL_FAMILY,
        "version": contract.version,
        "candidate_report_sha256": _file_sha256(report_path),
        "benchmark_report_sha256": _file_sha256(benchmark_path),
        "candidate_lock_sha256": _file_sha256(lock_path),
        "artifact_manifest_sha256": contract.locked_manifest_sha256,
        "base_source_kind": contract.base_source_kind,
        "release_mode": release_mode,
        "release_id": release["release_id"],
        "release_manifest": release["release_manifest"],
        "current_pointer": release["current_pointer"],
        "attestation_mode": LOCAL_ATTESTATION_MODE,
        "production_eligible": False,
    }


def _create_v6_immutable_release(
    *,
    root: Path,
    release_root: Path,
    current_pointer: Path,
    artifact_dir: Path,
    base_model_path: Path,
    contract: Any,
    evidence_sources: dict[str, Path],
    release_mode: str,
    source_git_commit: str,
    source_dirty: bool,
    candidate_lock_git_commit: str | None,
) -> dict[str, str]:
    artifact_manifest = contract.locked_manifest
    base_manifest = _manifest_from_tree(base_model_path, "v6 release base")
    runtime_code = {
        relative: _project_file_commitment(root, relative)
        for relative in sorted(V6_REQUIRED_RUNTIME_CODE)
    }
    release_root.mkdir(parents=True, exist_ok=True, mode=0o755)
    _reject_symlink_components(release_root, root)
    with _release_lock(release_root):
        created_at = datetime.now(UTC)
        release_id = (
            f"{created_at.strftime('%Y%m%dT%H%M%S%fZ')}-v6-"
            f"{contract.locked_manifest_sha256[:16]}"
        )
        staging = Path(tempfile.mkdtemp(prefix=".v6-release-staging-", dir=release_root))
        final = release_root / release_id
        try:
            artifact_target = staging / "artifact"
            base_relative = (
                Path("base/merged_fp32")
                if contract.base_source_kind == "DAPT_MERGED_FP32"
                else Path("base/pinned_raw")
            )
            base_target = staging / base_relative
            evidence_target = staging / "evidence"
            artifact_target.mkdir(mode=0o755)
            base_target.mkdir(parents=True, mode=0o755)
            evidence_target.mkdir(mode=0o755)
            _copy_regular_tree(artifact_dir, artifact_target, artifact_manifest)
            _copy_regular_tree(base_model_path, base_target, base_manifest)
            evidence: dict[str, dict[str, int | str]] = {}
            for role, source in sorted(evidence_sources.items()):
                target = evidence_target / f"{role}.json"
                _copy_regular_file(source, target)
                evidence[role] = _release_file_commitment(
                    target,
                    f"evidence/{role}.json",
                )
            source_manifest: dict[str, int | str] | None = None
            if contract.base_source_kind == "DAPT_MERGED_FP32":
                provenance_record = _mapping(
                    contract.base_source.get("manifest"),
                    "v6 DAPT manifest provenance",
                )
                provenance_path = _provenance_regular_file(
                    provenance_record,
                    root=root,
                    description="v6 DAPT source manifest",
                )
                source_target = staging / "base/dapt-source-manifest.json"
                _copy_regular_file(provenance_path, source_target)
                source_manifest = _release_file_commitment(
                    source_target,
                    "base/dapt-source-manifest.json",
                )
            manifest = {
                "schema_version": V6_RELEASE_SCHEMA_VERSION,
                "release_id": release_id,
                "created_at": created_at.isoformat(),
                "release_mode": release_mode,
                "source": {
                    "git_commit": source_git_commit,
                    "dirty": source_dirty,
                    "candidate_lock_git_commit": candidate_lock_git_commit,
                },
                "candidate": {
                    "name": V6_CANDIDATE_MODEL,
                    "model_family": V6_MODEL_FAMILY,
                    "version": contract.version,
                    "input_feature_version": INPUT_FEATURE_VERSION,
                    "label_order": list(LABEL_ORDER),
                    "max_length": contract.max_length,
                    "base_source_kind": contract.base_source_kind,
                },
                "artifact": {
                    "path": "artifact",
                    "files": artifact_manifest,
                    "manifest_sha256": contract.locked_manifest_sha256,
                },
                "base_model": {
                    "kind": contract.base_source_kind,
                    "path": base_relative.as_posix(),
                    "files": base_manifest,
                    "manifest_sha256": _canonical_json_sha256(base_manifest),
                    "training_provenance": contract.base_source,
                    "source_manifest": source_manifest,
                },
                "evidence": evidence,
                "runtime_code": runtime_code,
                "dependency_lock": runtime_code["uv.lock"],
            }
            manifest_path = staging / "release.json"
            _write_json_exclusive(manifest_path, manifest)
            for directory in (artifact_target, base_target, evidence_target, staging / "base"):
                _fsync_directory(directory)
            _fsync_directory(staging)
            if final.exists() or final.is_symlink():
                raise PromotionError("같은 v6 release ID가 이미 존재합니다.")
            os.replace(staging, final)
            _fsync_directory(release_root)
            installed_manifest = final / "release.json"
            pointer = {
                "schema_version": V6_CURRENT_SCHEMA_VERSION,
                "release_id": release_id,
                "release_manifest_path": f"{release_id}/release.json",
                "release_manifest": _release_file_commitment(
                    installed_manifest,
                    f"{release_id}/release.json",
                ),
                "attestation": {
                    "mode": LOCAL_ATTESTATION_MODE,
                    "production_eligible": False,
                },
            }
            _verify_v6_release_before_activation(
                release_root=release_root,
                pointer=pointer,
                project_root=root,
                base_model_path=final / base_relative,
            )
            _replace_json_atomically(current_pointer, pointer)
        except Exception:
            _remove_path(staging)
            raise
    return {
        "release_id": release_id,
        "release_manifest": _relative_path(final / "release.json", root),
        "current_pointer": _relative_path(current_pointer, root),
    }


def _verify_v6_release_before_activation(
    *,
    release_root: Path,
    pointer: dict[str, Any],
    project_root: Path,
    base_model_path: Path,
) -> None:
    descriptor, raw_path = tempfile.mkstemp(
        prefix=".v6-current-verification-",
        suffix=".json",
        dir=release_root,
    )
    verification_pointer = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as file:
            file.write(_canonical_json_bytes(pointer))
            file.flush()
            os.fsync(file.fileno())
        verify_sentiment_release(
            verification_pointer,
            base_model_path,
            project_root=project_root,
            runtime_environment="test",
            attestation_mode=LOCAL_ATTESTATION_MODE,
        )
    except SentimentReleaseError as exception:
        raise PromotionError(f"생성된 v6 immutable release 검증 실패: {exception}") from exception
    finally:
        verification_pointer.unlink(missing_ok=True)


def _provenance_regular_file(
    record: dict[str, Any],
    *,
    root: Path,
    description: str,
) -> Path:
    raw_path = record.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise PromotionError(f"{description} 경로가 없습니다.")
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink() or not _is_regular_file(candidate):
        raise PromotionError(f"{description}는 symlink가 아닌 일반 파일이어야 합니다.")
    resolved = candidate.resolve(strict=True)
    if (
        record.get("bytes") != resolved.stat().st_size
        or record.get("sha256") != _file_sha256(resolved)
    ):
        raise PromotionError(f"{description} hash가 학습 provenance와 다릅니다.")
    return resolved


def _validate_release_contract(
    *,
    root: Path,
    lock_path: Path,
    artifact_dir: Path,
    report_path: Path,
    benchmark_path: Path,
    lock: dict[str, Any],
    training: dict[str, Any],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    if _relative_path(lock_path, root) != "reports/sentiment-candidate-lock.json":
        raise PromotionError("후보 lock manifest 경로가 표준 경로와 다릅니다.")
    if _relative_path(artifact_dir, root) != LOCKED_ARTIFACT_DIRECTORY:
        raise PromotionError("잠긴 후보 artifact 경로가 표준 경로와 다릅니다.")
    if _relative_path(benchmark_path, root) != IMMUTABLE_BENCHMARK_PATH:
        raise PromotionError("v4 benchmark report 경로가 표준 경로와 다릅니다.")
    winner = _validate_lock(lock, lock_path, artifact_dir, report_path, root)
    training_manifest, auxiliary_training_paths = _validate_training_report(
        training,
        winner,
        root,
    )
    locked_manifest = _validate_locked_artifact(artifact_dir, training, training_manifest)
    artifact_manifest_sha256 = _canonical_json_sha256(locked_manifest)
    _validate_benchmark(
        benchmark,
        benchmark_path=benchmark_path,
        lock_path=lock_path,
        artifact_dir=artifact_dir,
        report_path=report_path,
        lock=lock,
        winner=winner,
        training=training,
        locked_manifest=locked_manifest,
        artifact_manifest_sha256=artifact_manifest_sha256,
        root=root,
    )
    return {
        "version": training["version"],
        "candidate_report_sha256": _file_sha256(report_path),
        "locked_artifact_files": locked_manifest,
        "artifact_manifest_sha256": artifact_manifest_sha256,
        "auxiliary_training_paths": auxiliary_training_paths,
    }


def _validate_lock(
    lock: dict[str, Any],
    lock_path: Path,
    artifact_dir: Path,
    report_path: Path,
    root: Path,
) -> dict[str, Any]:
    if (
        lock.get("schema_version") != LOCK_SCHEMA_VERSION
        or lock.get("selection_only") is not True
        or lock.get("external_git_commitment_required") is not True
        or lock.get("public_test_evaluated_before_lock") is not False
        or lock.get("operational_sealed_gold_evaluated_before_lock") is not False
    ):
        raise PromotionError("후보 lock이 봉인 평가 계약을 충족하지 않습니다.")
    locked_at = _aware_datetime(lock.get("locked_at"), "locked_at")
    if locked_at > datetime.now(UTC):
        raise PromotionError("후보 lock 시각이 미래입니다.")
    winner = _mapping(lock.get("winner"), "후보 lock winner")
    seed = _integer(winner.get("seed"), "후보 seed", minimum=0)
    expected_report = f"reports/candidates/kf-deberta-sentiment-seed{seed}.json"
    if winner.get("report_path") != expected_report:
        raise PromotionError("후보 lock의 학습 report 경로가 seed 계약과 다릅니다.")
    if _relative_path(report_path, root) != expected_report:
        raise PromotionError("입력 후보 report가 lock winner report와 다릅니다.")
    if winner.get("locked_artifact_dir") != LOCKED_ARTIFACT_DIRECTORY:
        raise PromotionError("후보 lock의 잠긴 artifact 경로가 다릅니다.")
    if _relative_path(artifact_dir, root) != winner["locked_artifact_dir"]:
        raise PromotionError("입력 artifact가 lock winner artifact와 다릅니다.")
    expected_source = f"artifacts/sentiment/candidates/seed{seed}"
    if winner.get("source_artifact_dir") != expected_source:
        raise PromotionError("후보 lock의 원본 artifact 경로가 seed 계약과 다릅니다.")
    report_hash = _sha256_value(winner.get("report_sha256"), "후보 report SHA-256")
    if not hmac.compare_digest(_file_sha256(report_path), report_hash):
        raise PromotionError("후보 report가 lock 이후 변경되었습니다.")
    locked_manifest = _artifact_manifest(
        winner.get("artifact_files"), LOCKED_ARTIFACTS, "후보 lock artifact manifest"
    )
    _verify_directory_manifest(artifact_dir, locked_manifest, exact_files=True)
    try:
        baseline_commitments = validate_confirmatory_baseline_commitments(
            lock.get("baseline_commitments"), root
        )
        if lock.get("baseline_commitments_sha256") != baseline_commitments_sha256(
            baseline_commitments
        ):
            raise PromotionError("후보 lock baseline commitment digest가 다릅니다.")
        reservations = _mapping(lock.get("sealed_reservations"), "봉인 reservations")
        validate_runtime_parity_lock_commitment(
            lock.get("runtime_parity"),
            project_root=root,
            expected_candidate_version=str(winner.get("version", "")),
            expected_candidate_artifact_manifest_sha256=_canonical_json_sha256(
                locked_manifest
            ),
            sealed_reservations={
                source: _mapping(reservations.get(source), f"{source} reservation")
                for source in ("NEWS", "DISCLOSURE")
            },
        )
    except ValueError as exception:
        raise PromotionError(str(exception)) from exception
    recipe = _mapping(lock.get("recipe"), "후보 lock recipe")
    if recipe.get("training_script") != TRAINING_SCRIPT:
        raise PromotionError("후보 lock의 학습 스크립트 계약이 다릅니다.")
    script_path = _existing_project_path(root / TRAINING_SCRIPT, root, "학습 스크립트", False)
    script_hash = _sha256_value(recipe.get("training_script_sha256"), "학습 스크립트 SHA-256")
    if not hmac.compare_digest(_file_sha256(script_path), script_hash):
        raise PromotionError("후보 lock 이후 학습 스크립트가 변경되었습니다.")
    if lock_path.is_symlink():
        raise PromotionError("후보 lock manifest는 심볼릭 링크일 수 없습니다.")
    return winner


def _validate_training_report(
    training: dict[str, Any],
    winner: dict[str, Any],
    root: Path,
) -> tuple[dict[str, dict[str, int | str]], dict[str, Path]]:
    seed = _integer(training.get("seed"), "학습 seed", minimum=0)
    version = training.get("version")
    max_length = training.get("max_length")
    selection = _mapping(training.get("candidate_selection"), "후보 선택 계약")
    test = _mapping(training.get("test"), "Test 봉인 계약")
    if (
        training.get("schema_version") != TRAINING_SCHEMA_VERSION
        or training.get("base_model") != BASE_MODEL
        or training.get("base_model_revision") != BASE_MODEL_REVISION
        or training.get("input_feature_version") != INPUT_FEATURE_VERSION
        or tuple(training.get("label_order", ())) != LABEL_ORDER
        or training.get("training_strategy") != CANDIDATE_TRAINING_STRATEGY
        or tuple(training.get("lora_layers", ())) != EXPECTED_LORA_LAYERS
        or seed != winner.get("seed")
        or not isinstance(version, str)
        or not version.startswith(f"hana-montana-kf-deberta-k-fnspid-sentiment-seed{seed}-")
        or version != winner.get("version")
        or isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not 16 <= max_length <= 512
        or selection.get("locked_candidate") != "kf_deberta_lora"
        or selection.get("test_used_for_selection") is not False
        or selection.get("operational_gold_used_for_selection") is not False
        or selection.get("sealed_test_evaluated") is not False
        or test.get("sample_count") != 0
        or test.get("status") != "SEALED_UNTIL_CANDIDATE_LOCK"
    ):
        raise PromotionError("후보 학습 report의 버전 또는 봉인 계약이 다릅니다.")
    selection_score = _finite_number(selection.get("selection_score"), "selection score")
    if not math.isclose(
        selection_score,
        _finite_number(winner.get("selection_score"), "lock selection score"),
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise PromotionError("후보 report와 lock의 selection score가 다릅니다.")
    training_biases = _validated_biases(training.get("logit_bias_by_domain"), "학습 report")
    calibration = _mapping(training.get("decision_calibration"), "감성 보정 계약")
    if (
        calibration.get("method") != "validation-only-domain-logit-offset-grid/v1"
        or calibration.get("fit_partition") != "CALIBRATION_ONLY"
        or calibration.get("selection_used_for_fit") is not False
        or calibration.get("public_test_used_for_fit") is not False
        or calibration.get("sealed_gold_used_for_fit") is not False
        or _validated_biases(calibration.get("logit_bias_by_domain"), "감성 보정")
        != training_biases
    ):
        raise PromotionError("후보 학습 report의 validation-only 보정 계약이 다릅니다.")
    auxiliary_paths = _validate_auxiliary_training_inputs(training, root)
    return (
        _artifact_manifest(
            training.get("artifact_files"), TRAINING_ARTIFACTS, "학습 artifact manifest"
        ),
        auxiliary_paths,
    )


def _validate_auxiliary_training_inputs(
    training: dict[str, Any], root: Path
) -> dict[str, Path]:
    inputs = _mapping(training.get("input_artifacts"), "후보 학습 입력")
    paths: dict[str, Path] = {}
    for role, expected_path in AUXILIARY_TRAINING_INPUTS.items():
        record = _training_input_record(inputs.get(role), expected_path, f"후보 {role}")
        paths[role] = _manifest_project_path(root, record, f"후보 {role}")
    return paths


def _training_input_record(
    value: object,
    expected_path: str,
    description: str,
) -> dict[str, Any]:
    record = _mapping(value, description)
    size = record.get("bytes")
    if (
        set(record) != {"path", "bytes", "sha256"}
        or record.get("path") != expected_path
        or isinstance(size, bool)
        or not isinstance(size, int)
        or size < 0
        or not _is_sha256(record.get("sha256"))
    ):
        raise PromotionError(f"{description} commitment가 올바르지 않습니다.")
    return record


def _validate_locked_artifact(
    artifact_dir: Path,
    training: dict[str, Any],
    training_manifest: dict[str, dict[str, int | str]],
) -> dict[str, dict[str, int | str]]:
    metadata_path = artifact_dir / "hannah_metadata.json"
    metadata = _load_json_object(metadata_path, "감성 artifact metadata")
    metadata_biases = _validated_biases(metadata.get("logit_bias_by_domain"), "artifact metadata")
    training_biases = _validated_biases(training.get("logit_bias_by_domain"), "학습 report")
    if (
        metadata.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or metadata.get("version") != training.get("version")
        or metadata.get("base_model") != BASE_MODEL
        or metadata.get("base_model_revision") != BASE_MODEL_REVISION
        or metadata.get("input_feature_version") != INPUT_FEATURE_VERSION
        or tuple(metadata.get("label_order", ())) != LABEL_ORDER
        or metadata.get("max_length") != training.get("max_length")
        or metadata.get("trained_at") != training.get("trained_at")
        or metadata.get("artifact_files") != training_manifest
        or metadata_biases != training_biases
    ):
        raise PromotionError("artifact metadata와 후보 학습 report 계약이 다릅니다.")
    adapter_config = _load_json_object(artifact_dir / "adapter_config.json", "LoRA 설정")
    target_modules = adapter_config.get("target_modules")
    modules_to_save = adapter_config.get("modules_to_save")
    if (
        adapter_config.get("base_model_name_or_path") != BASE_MODEL
        or adapter_config.get("peft_type") != "LORA"
        or adapter_config.get("task_type") != "SEQ_CLS"
        or not isinstance(target_modules, list)
        or frozenset(target_modules) != EXPECTED_TARGET_MODULES
        or tuple(adapter_config.get("layers_to_transform", ())) != EXPECTED_LORA_LAYERS
        or adapter_config.get("layers_pattern") != "layer"
        or not isinstance(modules_to_save, list)
        or not {"pooler", "classifier"}.issubset(modules_to_save)
    ):
        raise PromotionError("LoRA adapter 설정이 학습 v2 계약과 다릅니다.")
    locked_manifest = _manifest_from_directory(artifact_dir, LOCKED_ARTIFACTS)
    if any(locked_manifest[name] != training_manifest[name] for name in TRAINING_ARTIFACTS):
        raise PromotionError("잠긴 artifact와 학습 report manifest가 다릅니다.")
    return locked_manifest


def _validate_benchmark(
    benchmark: dict[str, Any],
    *,
    benchmark_path: Path,
    lock_path: Path,
    artifact_dir: Path,
    report_path: Path,
    lock: dict[str, Any],
    winner: dict[str, Any],
    training: dict[str, Any],
    locked_manifest: dict[str, dict[str, int | str]],
    artifact_manifest_sha256: str,
    root: Path,
) -> None:
    if (
        benchmark.get("schema_version") != BENCHMARK_SCHEMA_VERSION
        or benchmark.get("input_feature_version") != INPUT_FEATURE_VERSION
    ):
        raise PromotionError("benchmark report의 v4 입력 계약이 다릅니다.")
    evaluation_contract = _mapping(benchmark.get("evaluation_contract"), "평가 계약")
    if (
        evaluation_contract.get("candidate_selection_completed_before_evaluation_labels_loaded")
        is not True
        or evaluation_contract.get("locked_before_evaluation") is not True
        or evaluation_contract.get("test_used_for_candidate_selection") is not False
        or evaluation_contract.get("sealed_gold_used_for_candidate_selection") is not False
        or evaluation_contract.get("candidate_selection_inputs") != ["CALIBRATION", "SELECTION"]
    ):
        raise PromotionError("benchmark report의 봉인 평가 순서 계약이 다릅니다.")
    benchmark_lock = _mapping(benchmark.get("candidate_lock"), "benchmark 후보 lock")
    lock_biases = _validated_biases(benchmark_lock.get("logit_bias_by_domain"), "benchmark lock")
    training_biases = _validated_biases(training.get("logit_bias_by_domain"), "학습 report")
    expected_lock_path = _relative_path(lock_path, root)
    expected_report_path = _relative_path(report_path, root)
    expected_artifact_path = _relative_path(artifact_dir, root)
    if (
        benchmark_lock.get("schema_version") != LOCK_SCHEMA_VERSION
        or benchmark_lock.get("manifest_path") != expected_lock_path
        or benchmark_lock.get("manifest_sha256") != _file_sha256(lock_path)
        or benchmark_lock.get("locked_before_evaluation") is not True
        or benchmark_lock.get("selection_only") is not True
        or benchmark_lock.get("version") != training.get("version")
        or benchmark_lock.get("candidate_report_path") != expected_report_path
        or benchmark_lock.get("candidate_report_sha256") != _file_sha256(report_path)
        or benchmark_lock.get("artifact_dir") != expected_artifact_path
        or benchmark_lock.get("artifact_files") != locked_manifest
        or benchmark_lock.get("artifact_manifest_sha256") != artifact_manifest_sha256
        or benchmark_lock.get("base_model") != BASE_MODEL
        or benchmark_lock.get("base_model_revision") != BASE_MODEL_REVISION
        or benchmark_lock.get("max_length") != training.get("max_length")
        or benchmark_lock.get("input_feature_version") != INPUT_FEATURE_VERSION
        or lock_biases != training_biases
    ):
        raise PromotionError("benchmark report와 잠긴 후보 계약이 다릅니다.")
    if _aware_datetime(benchmark_lock.get("locked_at"), "benchmark locked_at") != _aware_datetime(
        lock.get("locked_at"), "lock locked_at"
    ):
        raise PromotionError("benchmark와 후보 lock 시각이 다릅니다.")
    generated_at = _aware_datetime(benchmark.get("generated_at"), "benchmark generated_at")
    if generated_at < _aware_datetime(lock.get("locked_at"), "lock locked_at"):
        raise PromotionError("benchmark가 후보 lock 전에 생성되었습니다.")
    _validate_consumption_receipt(
        benchmark,
        benchmark_path=benchmark_path,
        lock_path=lock_path,
        artifact_manifest_sha256=artifact_manifest_sha256,
        candidate_version=str(training["version"]),
        root=root,
    )
    gate = _mapping(benchmark.get("deployment_gate"), "deployment gate")
    try:
        validate_strict_sentiment_gate(benchmark)
    except SentimentReleaseError as exception:
        raise PromotionError(str(exception)) from exception
    if (
        gate.get("candidate_version") != training.get("version")
        or gate.get("candidate_version") != winner.get("version")
        or gate.get("candidate_artifact_manifest_sha256") != artifact_manifest_sha256
    ):
        raise PromotionError("deployment gate와 잠긴 후보 artifact 연결이 다릅니다.")
    if benchmark_path.is_symlink():
        raise PromotionError("benchmark report는 심볼릭 링크일 수 없습니다.")


def _validate_consumption_receipt(
    benchmark: dict[str, Any],
    *,
    benchmark_path: Path,
    lock_path: Path,
    artifact_manifest_sha256: str,
    candidate_version: str,
    root: Path,
) -> None:
    attestation = _mapping(
        benchmark.get("sealed_evaluation_consumption"), "sealed evaluation consumption"
    )
    if attestation.get("receipt_path") != CONSUMPTION_RECEIPT_PATH:
        raise PromotionError("sealed 평가 consumption receipt 경로가 다릅니다.")
    receipt_path = _existing_project_path(
        root / CONSUMPTION_RECEIPT_PATH,
        root,
        "sealed 평가 consumption receipt",
        directory=False,
    )
    receipt = _load_json_object(receipt_path, "sealed 평가 consumption receipt")
    lock = _load_json_object(lock_path, "candidate lock")
    receipt_hash = _file_sha256(receipt_path)
    evaluation_script = _existing_project_path(
        root / "scripts/evaluate_locked_kf_deberta_sentiment.py",
        root,
        "sealed 평가 스크립트",
        directory=False,
    )
    receipt_without_attestation = {
        key: value
        for key, value in attestation.items()
        if key not in {"receipt_path", "receipt_sha256"}
    }
    sealed_gold = _mapping(receipt.get("sealed_gold"), "receipt sealed Gold")
    promotion_reports = _mapping(receipt.get("promotion_reports"), "receipt Gold 승격 report")
    for source_type in ("NEWS", "DISCLOSURE"):
        _validate_receipt_file_manifest(
            sealed_gold.get(source_type), f"receipt {source_type} sealed Gold", root
        )
        _validate_receipt_file_manifest(
            promotion_reports.get(source_type),
            f"receipt {source_type} Gold 승격 report",
            root,
        )
    sampling_manifest = _validate_receipt_file_manifest(
        receipt.get("sampling_design_report"),
        "receipt sampling design report",
        root,
    )
    baseline_artifacts = _mapping(receipt.get("baseline_artifacts"), "receipt baseline artifacts")
    _validate_receipt_file_manifest(
        baseline_artifacts.get("hana_tfidf_logistic"),
        "receipt TF-IDF baseline",
        root,
    )
    pre_k_baseline = _mapping(
        baseline_artifacts.get("pre_k_fnspid_kf_deberta"),
        "receipt pre-K-FNSPID baseline",
    )
    pre_k_artifact_dir = pre_k_baseline.get("artifact_dir")
    if not isinstance(pre_k_artifact_dir, str):
        raise PromotionError("receipt pre-K-FNSPID artifact 경로가 없습니다.")
    pre_k_metadata = _existing_project_path(
        root / pre_k_artifact_dir / "hannah_metadata.json",
        root,
        "receipt pre-K-FNSPID metadata",
        directory=False,
    )
    if (
        _relative_path(pre_k_metadata.parent, root) != pre_k_artifact_dir
        or not _is_sha256(pre_k_baseline.get("metadata_sha256"))
        or not hmac.compare_digest(
            _file_sha256(pre_k_metadata), str(pre_k_baseline["metadata_sha256"])
        )
    ):
        raise PromotionError("receipt pre-K-FNSPID metadata hash가 다릅니다.")
    _validate_receipt_file_manifest(
        {
            "path": pre_k_baseline.get("training_report_path"),
            "sha256": pre_k_baseline.get("training_report_sha256"),
        },
        "receipt pre-K-FNSPID 학습 report",
        root,
    )
    _mapping(
        baseline_artifacts.get("kf_deberta_no_k_ablation"),
        "receipt no-K ablation baseline",
    )
    benchmark_sampling = _mapping(benchmark.get("sampling_design"), "sampling design")
    if (
        receipt.get("schema_version") != "sentiment-sealed-evaluation-consumption/v1"
        or receipt.get("labels_loaded_before_receipt") is not False
        or receipt.get("one_shot") is not True
        or receipt.get("candidate_version") != candidate_version
        or receipt.get("candidate_lock_manifest_sha256") != _file_sha256(lock_path)
        or receipt.get("candidate_artifact_manifest_sha256") != artifact_manifest_sha256
        or receipt.get("locked_baseline_commitments") != lock.get("baseline_commitments")
        or receipt.get("locked_baseline_commitments_sha256")
        != lock.get("baseline_commitments_sha256")
        or receipt.get("cpu_runtime_parity") != lock.get("runtime_parity")
        or benchmark_sampling.get("report_path") != sampling_manifest["path"]
        or benchmark_sampling.get("report_sha256") != sampling_manifest["sha256"]
        or receipt.get("evaluation_script_sha256") != _file_sha256(evaluation_script)
        or receipt.get("planned_report_path") != IMMUTABLE_BENCHMARK_PATH
        or not isinstance(receipt.get("bootstrap_samples"), int)
        or isinstance(receipt.get("bootstrap_samples"), bool)
        or int(receipt["bootstrap_samples"]) < 100
        or not isinstance(receipt.get("bootstrap_seed"), int)
        or isinstance(receipt.get("bootstrap_seed"), bool)
        or _aware_datetime(receipt.get("consumed_at"), "receipt consumed_at")
        > _aware_datetime(benchmark.get("generated_at"), "benchmark generated_at")
        or _aware_datetime(receipt.get("consumed_at"), "receipt consumed_at")
        < _aware_datetime(benchmark["candidate_lock"].get("locked_at"), "lock locked_at")
        or attestation.get("receipt_sha256") != receipt_hash
        or receipt_without_attestation != receipt
        or _relative_path(benchmark_path, root) != receipt.get("planned_report_path")
    ):
        raise PromotionError("sealed 평가 consumption receipt 계약이 다릅니다.")


def _validate_receipt_file_manifest(raw: object, description: str, root: Path) -> dict[str, str]:
    manifest = _mapping(raw, description)
    relative_path = manifest.get("path")
    expected_hash = manifest.get("sha256")
    if not isinstance(relative_path, str) or not _is_sha256(expected_hash):
        raise PromotionError(f"{description} manifest가 올바르지 않습니다.")
    path = _existing_project_path(
        root / relative_path,
        root,
        description,
        directory=False,
    )
    if _relative_path(path, root) != relative_path or not hmac.compare_digest(
        _file_sha256(path), str(expected_hash)
    ):
        raise PromotionError(f"{description} hash가 다릅니다.")
    return {"path": relative_path, "sha256": str(expected_hash)}


def _expected_gate_checks(benchmark: dict[str, Any]) -> dict[str, bool]:
    return expected_sentiment_gate_checks(benchmark)


def _create_immutable_release(
    *,
    root: Path,
    release_root: Path,
    current_pointer: Path,
    artifact_dir: Path,
    report_path: Path,
    benchmark_path: Path,
    lock_path: Path,
    lock: dict[str, Any],
    benchmark: dict[str, Any],
    base_model_path: Path,
    runtime_base_model_path: Path,
    source_git_commit: str,
    source_dirty: bool,
    verified: dict[str, Any],
) -> dict[str, str]:
    artifact_manifest = cast(
        dict[str, dict[str, int | str]], verified["locked_artifact_files"]
    )
    base_manifest = _manifest_from_tree(base_model_path, "base model")
    evidence_sources = _release_evidence_sources(
        root=root,
        report_path=report_path,
        benchmark_path=benchmark_path,
        lock_path=lock_path,
        lock=lock,
        benchmark=benchmark,
        auxiliary_training_paths=cast(dict[str, Path], verified["auxiliary_training_paths"]),
    )
    fair_directory, fair_manifest, fair_receipt = _fair_baseline_source(
        root,
        benchmark,
        training=_load_json_object(report_path, "후보 학습 report"),
    )
    if set(evidence_sources) != set(REQUIRED_EVIDENCE_ROLES):
        raise PromotionError("immutable release evidence role 구성이 다릅니다.")
    try:
        normalized_git_attestation = validate_candidate_git_attestation(
            evidence_sources["candidate_git_attestation"],
            lock_path,
            project_root=root,
        )
    except (OSError, ValueError) as exception:
        raise PromotionError(str(exception)) from exception
    receipt = _load_json_object(
        evidence_sources["consumption_receipt"],
        "consumption receipt",
    )
    if receipt.get("candidate_git_attestation") != normalized_git_attestation:
        raise PromotionError(
            "consumption receipt의 candidate Git attestation이 원격 이력 검증값과 다릅니다."
        )
    candidate_lock_git_commit = str(normalized_git_attestation["commit_sha"])
    runtime_code = {
        relative: _project_file_commitment(root, relative)
        for relative in sorted(REQUIRED_RUNTIME_CODE)
    }
    release_root.mkdir(parents=True, exist_ok=True, mode=0o755)
    _reject_symlink_components(release_root, root)
    with _release_lock(release_root):
        created_at = datetime.now(UTC)
        release_id = (
            f"{created_at.strftime('%Y%m%dT%H%M%S%fZ')}-"
            f"{str(verified['artifact_manifest_sha256'])[:16]}"
        )
        staging = Path(tempfile.mkdtemp(prefix=".release-staging-", dir=release_root))
        final = release_root / release_id
        try:
            artifact_target = staging / "artifact"
            evidence_target = staging / "evidence"
            fair_target = staging / "reference-artifacts/same-data-fair-baseline"
            artifact_target.mkdir(mode=0o755)
            evidence_target.mkdir(mode=0o755)
            fair_target.mkdir(parents=True, mode=0o755)
            for filename in sorted(artifact_manifest):
                _copy_regular_file(artifact_dir / filename, artifact_target / filename)
            _verify_directory_manifest(
                artifact_target,
                artifact_manifest,
                exact_files=True,
            )
            evidence = _copy_release_evidence(
                evidence_sources,
                evidence_target=evidence_target,
            )
            _copy_regular_tree(fair_directory, fair_target, fair_manifest)
            manifest = {
                "schema_version": RELEASE_SCHEMA_VERSION,
                "release_id": release_id,
                "created_at": created_at.isoformat(),
                "source": {
                    "git_commit": source_git_commit,
                    "dirty": source_dirty,
                    "candidate_lock_git_commit": candidate_lock_git_commit,
                    "candidate_lock_git_tree": normalized_git_attestation["tree_sha"],
                    "candidate_git_attestation_sha256": normalized_git_attestation[
                        "sha256"
                    ],
                },
                "candidate": {
                    "name": CANDIDATE_MODEL,
                    "version": verified["version"],
                    "input_feature_version": INPUT_FEATURE_VERSION,
                    "label_order": list(LABEL_ORDER),
                    "max_length": _mapping(
                        _load_json_object(report_path, "후보 학습 report"),
                        "후보 학습 report",
                    )["max_length"],
                },
                "artifact": {
                    "path": "artifact",
                    "files": artifact_manifest,
                    "manifest_sha256": _canonical_json_sha256(artifact_manifest),
                },
                "base_model": {
                    "model_id": BASE_MODEL,
                    "revision": BASE_MODEL_REVISION,
                    "runtime_path": str(runtime_base_model_path),
                    "files": base_manifest,
                    "manifest_sha256": _canonical_json_sha256(base_manifest),
                },
                "evidence": evidence,
                "reference_artifacts": {
                    "kr_finbert_sc_same_data_fair": {
                        "path": "reference-artifacts/same-data-fair-baseline",
                        "files": fair_manifest,
                        "manifest_sha256": _canonical_json_sha256(fair_manifest),
                        "metadata_sha256": fair_receipt["metadata_sha256"],
                        "same_data_contract_sha256": fair_receipt[
                            "same_data_contract_sha256"
                        ],
                    }
                },
                "runtime_code": runtime_code,
                "dependency_lock": runtime_code["uv.lock"],
            }
            manifest_path = staging / "release.json"
            _write_json_exclusive(manifest_path, manifest)
            _fsync_directory(artifact_target)
            _fsync_directory(evidence_target)
            _fsync_directory(fair_target)
            _fsync_directory(fair_target.parent)
            _fsync_directory(staging)
            if final.exists() or final.is_symlink():
                raise PromotionError("같은 release ID가 이미 존재합니다.")
            os.replace(staging, final)
            _fsync_directory(release_root)
            installed_manifest = final / "release.json"
            pointer = {
                "schema_version": CURRENT_SCHEMA_VERSION,
                "release_id": release_id,
                "release_manifest_path": f"{release_id}/release.json",
                "release_manifest": _release_file_commitment(
                    installed_manifest,
                    f"{release_id}/release.json",
                ),
                "attestation": {
                    "mode": LOCAL_ATTESTATION_MODE,
                    "production_eligible": False,
                },
            }
            _verify_release_before_activation(
                release_root=release_root,
                pointer=pointer,
                runtime_base_model_path=runtime_base_model_path,
                base_model_verification_path=base_model_path,
                project_root=root,
            )
            _replace_json_atomically(current_pointer, pointer)
        except Exception:
            _remove_path(staging)
            raise
    return {
        "release_id": release_id,
        "release_manifest": _relative_path(final / "release.json", root),
        "current_pointer": _relative_path(current_pointer, root),
    }


def _verify_release_before_activation(
    *,
    release_root: Path,
    pointer: dict[str, Any],
    runtime_base_model_path: Path,
    base_model_verification_path: Path,
    project_root: Path,
) -> None:
    payload = _canonical_json_bytes(pointer)
    descriptor, raw_path = tempfile.mkstemp(
        prefix=".current-verification-",
        suffix=".json",
        dir=release_root,
    )
    verification_pointer = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        verify_sentiment_release(
            verification_pointer,
            runtime_base_model_path,
            project_root=project_root,
            runtime_environment="test",
            attestation_mode=LOCAL_ATTESTATION_MODE,
            base_model_verification_path=base_model_verification_path,
        )
    except SentimentReleaseError as exception:
        raise PromotionError(f"생성된 immutable release 검증 실패: {exception}") from exception
    finally:
        verification_pointer.unlink(missing_ok=True)


def _release_evidence_sources(
    *,
    root: Path,
    report_path: Path,
    benchmark_path: Path,
    lock_path: Path,
    lock: dict[str, Any],
    benchmark: dict[str, Any],
    auxiliary_training_paths: dict[str, Path],
) -> dict[str, Path]:
    receipt_attestation = _mapping(
        benchmark.get("sealed_evaluation_consumption"),
        "sealed evaluation consumption",
    )
    receipt_path = _manifest_project_path(
        root,
        receipt_attestation,
        "consumption receipt",
        path_key="receipt_path",
        hash_key="receipt_sha256",
    )
    receipt = _load_json_object(receipt_path, "consumption receipt")
    sealed_gold = _mapping(receipt.get("sealed_gold"), "receipt sealed Gold")
    promotion = _mapping(receipt.get("promotion_reports"), "receipt promotion reports")
    reservations = _mapping(lock.get("sealed_reservations"), "lock sealed reservations")
    baselines = _mapping(receipt.get("baseline_artifacts"), "receipt baselines")
    pre_k = _mapping(
        baselines.get("pre_k_fnspid_kf_deberta"),
        "pre-K-FNSPID baseline",
    )
    fair = _mapping(
        baselines.get("kr_finbert_sc_same_data_fair"),
        "same-data fair baseline",
    )
    runtime_parity = _mapping(lock.get("runtime_parity"), "runtime parity lock")
    artifact_dir = pre_k.get("artifact_dir")
    if not isinstance(artifact_dir, str):
        raise PromotionError("pre-K-FNSPID artifact 경로가 없습니다.")
    sources = {
        "candidate_git_attestation": _existing_project_path(
            root / "reports/sentiment-candidate-git-attestation.json",
            root,
            "candidate Git attestation",
            directory=False,
        ),
        **auxiliary_training_paths,
        "training_report": report_path,
        "benchmark_report": benchmark_path,
        "candidate_lock": lock_path,
        "consumption_receipt": receipt_path,
        "sampling_design": _manifest_project_path(
            root, receipt.get("sampling_design_report"), "sampling design"
        ),
        "reservation_news": _manifest_project_path(
            root, reservations.get("NEWS"), "NEWS reservation"
        ),
        "reservation_disclosure": _manifest_project_path(
            root, reservations.get("DISCLOSURE"), "DISCLOSURE reservation"
        ),
        "sealed_gold_news": _manifest_project_path(
            root, sealed_gold.get("NEWS"), "NEWS sealed Gold"
        ),
        "sealed_gold_disclosure": _manifest_project_path(
            root, sealed_gold.get("DISCLOSURE"), "DISCLOSURE sealed Gold"
        ),
        "gold_promotion_news": _manifest_project_path(
            root, promotion.get("NEWS"), "NEWS Gold promotion"
        ),
        "gold_promotion_disclosure": _manifest_project_path(
            root, promotion.get("DISCLOSURE"), "DISCLOSURE Gold promotion"
        ),
        "tfidf_baseline": _manifest_project_path(
            root, baselines.get("hana_tfidf_logistic"), "TF-IDF baseline"
        ),
        "pre_k_fnspid_metadata": _manifest_project_path(
            root,
            {
                "path": f"{artifact_dir}/hannah_metadata.json",
                "sha256": pre_k.get("metadata_sha256"),
            },
            "pre-K-FNSPID metadata",
        ),
        "pre_k_fnspid_training_report": _manifest_project_path(
            root,
            {
                "path": pre_k.get("training_report_path"),
                "sha256": pre_k.get("training_report_sha256"),
            },
            "pre-K-FNSPID training report",
        ),
        "fair_baseline_selection_report": _manifest_project_path(
            root,
            {
                "path": fair.get("selection_report_path"),
                "sha256": fair.get("selection_report_sha256"),
            },
            "same-data fair baseline selection report",
        ),
        "fair_baseline_training_report": _manifest_project_path(
            root,
            {
                "path": fair.get("training_report_path"),
                "sha256": fair.get("training_report_sha256"),
            },
            "same-data fair baseline training report",
        ),
        "cpu_runtime_parity": _manifest_project_path(
            root,
            runtime_parity.get("evidence"),
            "CPU runtime parity evidence",
        ),
    }
    if len(set(sources.values())) != len(sources):
        raise PromotionError("release evidence source 경로가 중복됩니다.")
    return sources


def _fair_baseline_source(
    root: Path,
    benchmark: dict[str, Any],
    *,
    training: dict[str, Any],
) -> tuple[Path, dict[str, dict[str, int | str]], dict[str, Any]]:
    receipt = _mapping(
        benchmark.get("sealed_evaluation_consumption"),
        "sealed evaluation consumption",
    )
    baselines = _mapping(receipt.get("baseline_artifacts"), "receipt baselines")
    fair = _mapping(
        baselines.get("kr_finbert_sc_same_data_fair"),
        "same-data fair baseline",
    )
    artifact_dir = fair.get("artifact_dir")
    if not isinstance(artifact_dir, str):
        raise PromotionError("same-data fair baseline artifact 경로가 없습니다.")
    directory = _existing_project_path(
        root / artifact_dir,
        root,
        "same-data fair baseline artifact",
        directory=True,
    )
    manifest = _manifest_from_tree(directory, "same-data fair baseline artifact")
    metadata_path = directory / "hannah_metadata.json"
    training_report_path = _manifest_project_path(
        root,
        {
            "path": fair.get("training_report_path"),
            "sha256": fair.get("training_report_sha256"),
        },
        "same-data fair baseline training report",
    )
    fair_training = _load_json_object(
        training_report_path,
        "same-data fair baseline training report",
    )
    benchmark_fair = _mapping(
        benchmark.get("same_data_fair_baseline"),
        "benchmark same-data fair baseline",
    )
    same_data_contract = _mapping(
        benchmark_fair.get("same_data_contract"),
        "same-data fair baseline contract",
    )
    if (
        fair.get("artifact_manifest_sha256") != _canonical_json_sha256(manifest)
        or fair.get("metadata_sha256") != _file_sha256(metadata_path)
        or not _is_sha256(fair.get("same_data_contract_sha256"))
        or fair_training.get("schema_version")
        != "k-fnspid-fair-baseline-training/v1"
        or fair_training.get("training_strategy") != FAIR_BASELINE_TRAINING_STRATEGY
        or benchmark_fair.get("same_data_contract_sha256")
        != _canonical_json_sha256(same_data_contract)
        or benchmark_fair.get("same_data_contract_sha256")
        != fair.get("same_data_contract_sha256")
        or benchmark_fair.get("same_data_split_selection_budget_verified") is not True
        or benchmark_fair.get("public_test_labels_used_for_training_or_selection")
        is not False
        or benchmark_fair.get("confirmatory_labels_used_for_training_or_selection")
        is not False
    ):
        raise PromotionError("same-data fair baseline artifact commitment가 다릅니다.")
    candidate_inputs = _mapping(training.get("input_artifacts"), "후보 학습 입력")
    fair_inputs = _mapping(fair_training.get("input_artifacts"), "공정 기준선 학습 입력")
    matched_inputs = _mapping(
        same_data_contract.get("matched_input_artifacts"),
        "same-data 일치 학습 입력",
    )
    for role, expected_path in AUXILIARY_TRAINING_INPUTS.items():
        candidate_record = _training_input_record(
            candidate_inputs.get(role), expected_path, f"후보 {role}"
        )
        fair_record = _training_input_record(
            fair_inputs.get(role), expected_path, f"공정 기준선 {role}"
        )
        matched_record = _training_input_record(
            matched_inputs.get(role), expected_path, f"same-data {role}"
        )
        if candidate_record != fair_record or candidate_record != matched_record:
            raise PromotionError(f"same-data {role} commitment가 다릅니다.")
    return directory, manifest, fair


def _copy_regular_tree(
    source: Path,
    destination: Path,
    manifest: dict[str, dict[str, int | str]],
) -> None:
    for relative in sorted(manifest):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        _copy_regular_file(source / relative, target)
    if _manifest_from_tree(destination, "복사된 same-data fair baseline") != manifest:
        raise PromotionError("복사된 same-data fair baseline hash가 다릅니다.")


def _manifest_project_path(
    root: Path,
    raw: object,
    description: str,
    *,
    path_key: str = "path",
    hash_key: str = "sha256",
) -> Path:
    commitment = _mapping(raw, description)
    relative = commitment.get(path_key)
    digest = commitment.get(hash_key)
    if not isinstance(relative, str) or not _is_sha256(digest):
        raise PromotionError(f"{description} commitment가 올바르지 않습니다.")
    path = _existing_project_path(root / relative, root, description, directory=False)
    if _relative_path(path, root) != relative or not hmac.compare_digest(
        _file_sha256(path), cast(str, digest)
    ):
        raise PromotionError(f"{description} 원본 hash가 다릅니다.")
    size = commitment.get("bytes")
    if size is not None and (
        isinstance(size, bool) or not isinstance(size, int) or size != path.stat().st_size
    ):
        raise PromotionError(f"{description} 원본 byte 수가 다릅니다.")
    return path


def _copy_release_evidence(
    sources: dict[str, Path],
    *,
    evidence_target: Path,
) -> dict[str, dict[str, int | str]]:
    commitments: dict[str, dict[str, int | str]] = {}
    for role, source in sorted(sources.items()):
        suffix = source.suffix if source.suffix else ".bin"
        relative = Path("evidence") / f"{role}{suffix}"
        destination = evidence_target / relative.name
        _copy_regular_file(source, destination)
        commitments[role] = _release_file_commitment(destination, relative.as_posix())
    return commitments


def _manifest_from_tree(
    directory: Path,
    description: str,
) -> dict[str, dict[str, int | str]]:
    result: dict[str, dict[str, int | str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise PromotionError(f"{description}에는 일반 파일만 허용됩니다: {path}")
        if path.is_dir():
            continue
        if not _is_regular_file(path):
            raise PromotionError(f"{description}에는 일반 파일만 허용됩니다: {path}")
        relative = path.relative_to(directory).as_posix()
        size, digest = _file_identity(path)
        result[relative] = {"bytes": size, "sha256": digest}
    if not result:
        raise PromotionError(f"{description} 파일 트리가 비었습니다.")
    return result


def _project_file_commitment(root: Path, relative: str) -> dict[str, int | str]:
    path = _existing_project_path(root / relative, root, relative, directory=False)
    return _release_file_commitment(path, relative)


def _release_file_commitment(path: Path, relative: str) -> dict[str, int | str]:
    size, digest = _file_identity(path)
    return {"path": relative, "bytes": size, "sha256": digest}


def _write_json_exclusive(path: Path, value: object) -> None:
    payload = _canonical_json_bytes(value)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as file:
        file.write(payload)
        file.flush()
        os.fsync(file.fileno())
        os.fchmod(file.fileno(), 0o644)


def _replace_json_atomically(path: Path, value: object) -> None:
    if path.is_symlink() or (path.exists() and not _is_regular_file(path)):
        raise PromotionError("current 포인터는 일반 파일이어야 합니다.")
    descriptor, staging_name = tempfile.mkstemp(prefix=".current-staging-", dir=path.parent)
    staging = Path(staging_name)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as file:
            file.write(_canonical_json_bytes(value))
            file.flush()
            os.fsync(file.fileno())
            os.fchmod(file.fileno(), 0o644)
        os.replace(staging, path)
        _fsync_directory(path.parent)
    finally:
        staging.unlink(missing_ok=True)


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


@contextmanager
def _release_lock(release_root: Path) -> Iterator[None]:
    lock_path = release_root / ".promotion.lock"
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock_path, flags, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _release_root_path(path: Path, root: Path) -> Path:
    candidate = Path(os.path.abspath(path if path.is_absolute() else root / path))
    if candidate != root / "releases/sentiment":
        raise PromotionError("sentiment release root는 releases/sentiment로 고정됩니다.")
    _reject_symlink_components(candidate.parent, root)
    return candidate


def _current_pointer_path(path: Path, release_root: Path) -> Path:
    candidate = Path(os.path.abspath(path if path.is_absolute() else release_root / path))
    if candidate != release_root / "current.json":
        raise PromotionError("sentiment current 포인터 경로가 고정 계약과 다릅니다.")
    return candidate


def _existing_directory(path: Path, description: str) -> Path:
    candidate = Path(os.path.abspath(path))
    if candidate.is_symlink() or not candidate.is_dir():
        raise PromotionError(f"{description} 경로가 실제 디렉터리가 아닙니다.")
    return candidate.resolve(strict=True)


def _git_source(root: Path) -> tuple[str, bool]:
    git = shutil.which("git")
    if git is None:
        raise PromotionError("git 실행 파일이 없습니다.")
    try:
        commit = subprocess.run(  # noqa: S603  # nosec B603
            [git, "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        status = subprocess.run(  # noqa: S603  # nosec B603
            [git, "status", "--porcelain", "--untracked-files=normal"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exception:
        raise PromotionError("release Git source를 확인할 수 없습니다.") from exception
    if not _is_git_commit(commit):
        raise PromotionError("release Git commit 형식이 올바르지 않습니다.")
    return commit, bool(status.strip())


def _is_git_commit(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def _promote_atomically(
    source_artifact: Path,
    source_report: Path,
    target_artifact: Path,
    target_report: Path,
    source_benchmark: Path,
    target_benchmark: Path,
    locked_manifest: dict[str, dict[str, int | str]],
) -> None:
    target_artifact.parent.mkdir(parents=True, exist_ok=True)
    target_report.parent.mkdir(parents=True, exist_ok=True)
    staging_artifact = Path(
        tempfile.mkdtemp(prefix=f".{target_artifact.name}-staging-", dir=target_artifact.parent)
    )
    report_fd, report_staging_name = tempfile.mkstemp(
        prefix=f".{target_report.name}-staging-", dir=target_report.parent
    )
    os.close(report_fd)
    staging_report = Path(report_staging_name)
    benchmark_fd, benchmark_staging_name = tempfile.mkstemp(
        prefix=f".{target_benchmark.name}-staging-", dir=target_benchmark.parent
    )
    os.close(benchmark_fd)
    staging_benchmark = Path(benchmark_staging_name)
    artifact_backup = target_artifact.parent / f".{target_artifact.name}-rollback"
    report_backup = target_report.parent / f".{target_report.name}-rollback"
    benchmark_backup = target_benchmark.parent / f".{target_benchmark.name}-rollback"
    artifact_had_previous = target_artifact.exists()
    report_had_previous = target_report.exists()
    benchmark_had_previous = target_benchmark.exists()
    artifact_installed = False
    report_installed = False
    benchmark_installed = False
    try:
        if artifact_backup.exists() or artifact_backup.is_symlink():
            raise PromotionError("이전 artifact rollback 경로가 남아 있습니다.")
        if report_backup.exists() or report_backup.is_symlink():
            raise PromotionError("이전 report rollback 경로가 남아 있습니다.")
        if benchmark_backup.exists() or benchmark_backup.is_symlink():
            raise PromotionError("이전 benchmark rollback 경로가 남아 있습니다.")
        for filename in sorted(LOCKED_ARTIFACTS):
            _copy_regular_file(source_artifact / filename, staging_artifact / filename)
        _verify_directory_manifest(staging_artifact, locked_manifest, exact_files=True)
        _copy_regular_file(source_report, staging_report, replace_empty=True)
        _copy_regular_file(source_benchmark, staging_benchmark, replace_empty=True)

        if artifact_had_previous:
            os.replace(target_artifact, artifact_backup)
        os.replace(staging_artifact, target_artifact)
        artifact_installed = True
        if report_had_previous:
            os.replace(target_report, report_backup)
        os.replace(staging_report, target_report)
        report_installed = True
        if benchmark_had_previous:
            os.replace(target_benchmark, benchmark_backup)
        os.replace(staging_benchmark, target_benchmark)
        benchmark_installed = True
        _fsync_directory(target_artifact.parent)
        _fsync_directory(target_report.parent)
        _verify_directory_manifest(target_artifact, locked_manifest, exact_files=True)
        if not hmac.compare_digest(_file_sha256(target_report), _file_sha256(source_report)):
            raise PromotionError("승격된 학습 report의 SHA-256이 다릅니다.")
        if not hmac.compare_digest(_file_sha256(target_benchmark), _file_sha256(source_benchmark)):
            raise PromotionError("승격된 benchmark report의 SHA-256이 다릅니다.")
    except Exception as exception:
        _rollback_promotion(
            target_artifact=target_artifact,
            target_report=target_report,
            target_benchmark=target_benchmark,
            artifact_backup=artifact_backup,
            report_backup=report_backup,
            benchmark_backup=benchmark_backup,
            artifact_had_previous=artifact_had_previous,
            report_had_previous=report_had_previous,
            benchmark_had_previous=benchmark_had_previous,
            artifact_installed=artifact_installed,
            report_installed=report_installed,
            benchmark_installed=benchmark_installed,
        )
        if isinstance(exception, PromotionError):
            raise
        raise PromotionError("배포 파일의 원자적 승격에 실패했습니다.") from exception
    else:
        _remove_path(artifact_backup)
        _remove_path(report_backup)
        _remove_path(benchmark_backup)
    finally:
        _remove_path(staging_artifact)
        _remove_path(staging_report)
        _remove_path(staging_benchmark)


def _rollback_promotion(
    *,
    target_artifact: Path,
    target_report: Path,
    target_benchmark: Path,
    artifact_backup: Path,
    report_backup: Path,
    benchmark_backup: Path,
    artifact_had_previous: bool,
    report_had_previous: bool,
    benchmark_had_previous: bool,
    artifact_installed: bool,
    report_installed: bool,
    benchmark_installed: bool,
) -> None:
    if benchmark_installed:
        _remove_path(target_benchmark)
    if benchmark_had_previous and benchmark_backup.exists():
        os.replace(benchmark_backup, target_benchmark)
    if report_installed:
        _remove_path(target_report)
    if report_had_previous and report_backup.exists():
        os.replace(report_backup, target_report)
    if artifact_installed:
        _remove_path(target_artifact)
    if artifact_had_previous and artifact_backup.exists():
        os.replace(artifact_backup, target_artifact)


def _copy_regular_file(source: Path, destination: Path, *, replace_empty: bool = False) -> None:
    source_fd = _open_regular_readonly(source)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if replace_empty else os.O_EXCL)
    try:
        destination_fd = os.open(destination, flags, 0o600)
    except Exception:
        os.close(source_fd)
        raise
    try:
        with os.fdopen(source_fd, "rb", closefd=True) as source_file:
            with os.fdopen(destination_fd, "wb", closefd=True) as destination_file:
                shutil.copyfileobj(source_file, destination_file, length=1024 * 1024)
                destination_file.flush()
                os.fsync(destination_file.fileno())
                os.fchmod(destination_file.fileno(), 0o644)
    except Exception:
        _remove_path(destination)
        raise


def _existing_project_root(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise PromotionError("프로젝트 root가 실제 디렉터리가 아닙니다.")
    return path.resolve(strict=True)


def _existing_project_path(
    path: Path,
    root: Path,
    description: str,
    directory: bool,
) -> Path:
    candidate = path if path.is_absolute() else root / path
    candidate = Path(os.path.abspath(candidate))
    if not candidate.is_relative_to(root):
        raise PromotionError(f"{description} 경로가 프로젝트 밖을 가리킵니다.")
    _reject_symlink_components(candidate, root)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exception:
        raise PromotionError(f"{description} 파일이 없습니다.") from exception
    if resolved != candidate:
        raise PromotionError(f"{description} 경로에 심볼릭 링크가 포함되어 있습니다.")
    if directory and not candidate.is_dir():
        raise PromotionError(f"{description} 경로가 디렉터리가 아닙니다.")
    if not directory and not _is_regular_file(candidate):
        raise PromotionError(f"{description} 경로가 일반 파일이 아닙니다.")
    return candidate


def _deployment_target_path(
    path: Path,
    root: Path,
    expected_relative: str,
    *,
    directory: bool,
) -> Path:
    candidate = path if path.is_absolute() else root / path
    candidate = Path(os.path.abspath(candidate))
    expected = root / expected_relative
    if candidate != expected:
        raise PromotionError("배포 대상 경로가 고정된 v2 경로와 다릅니다.")
    _reject_symlink_components(candidate.parent, root)
    if candidate.exists() or candidate.is_symlink():
        _reject_symlink_components(candidate, root)
        if candidate.is_symlink():
            raise PromotionError("배포 대상은 심볼릭 링크일 수 없습니다.")
        if directory and not candidate.is_dir():
            raise PromotionError("artifact 배포 대상이 디렉터리가 아닙니다.")
        if not directory and not _is_regular_file(candidate):
            raise PromotionError("report 배포 대상이 일반 파일이 아닙니다.")
    return candidate


def _reject_symlink_components(path: Path, root: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exception:
        raise PromotionError("경로가 프로젝트 root 밖을 가리킵니다.") from exception
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise PromotionError(f"심볼릭 링크 경로는 허용하지 않습니다: {current}")


def _verify_directory_manifest(
    directory: Path,
    manifest: dict[str, dict[str, int | str]],
    *,
    exact_files: bool,
) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise PromotionError("artifact 경로가 실제 디렉터리가 아닙니다.")
    entries = list(directory.iterdir())
    if exact_files and {path.name for path in entries} != set(manifest):
        raise PromotionError("artifact 디렉터리에 선언되지 않은 파일이 있습니다.")
    for path in entries:
        if path.is_symlink() or not _is_regular_file(path):
            raise PromotionError("artifact에는 일반 파일만 포함할 수 있습니다.")
    for filename, expected in manifest.items():
        path = directory / filename
        actual_size, actual_hash = _file_identity(path)
        if actual_size != expected["bytes"] or not hmac.compare_digest(
            actual_hash, cast(str, expected["sha256"])
        ):
            raise PromotionError(f"artifact 파일 무결성 검증에 실패했습니다: {filename}")


def _manifest_from_directory(
    directory: Path, filenames: frozenset[str]
) -> dict[str, dict[str, int | str]]:
    return {
        filename: {"bytes": size, "sha256": digest}
        for filename in sorted(filenames)
        for size, digest in [_file_identity(directory / filename)]
    }


def _artifact_manifest(
    value: object,
    required: frozenset[str],
    description: str,
) -> dict[str, dict[str, int | str]]:
    if not isinstance(value, dict) or set(value) != set(required):
        raise PromotionError(f"{description} 파일 구성이 다릅니다.")
    result: dict[str, dict[str, int | str]] = {}
    for filename in sorted(required):
        if Path(filename).name != filename:
            raise PromotionError(f"{description} 파일명이 안전하지 않습니다.")
        details = value.get(filename)
        if not isinstance(details, dict):
            raise PromotionError(f"{description} 항목이 객체가 아닙니다.")
        size = details.get("bytes")
        digest = details.get("sha256")
        if (
            set(details) != {"bytes", "sha256"}
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size <= 0
            or not _is_sha256(digest)
        ):
            raise PromotionError(f"{description} 항목이 올바르지 않습니다: {filename}")
        result[filename] = {"bytes": size, "sha256": cast(str, digest)}
    return result


def _load_json_object(path: Path, description: str) -> dict[str, Any]:
    size, _ = _file_identity(path)
    if size > MAX_JSON_BYTES:
        raise PromotionError(f"{description} 크기가 허용 범위를 넘었습니다.")
    file_descriptor = _open_regular_readonly(path)
    try:
        with os.fdopen(file_descriptor, "r", encoding="utf-8", closefd=True) as file:
            value = json.load(
                file,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_json_constant,
            )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exception:
        raise PromotionError(f"{description} JSON을 읽을 수 없습니다.") from exception
    if not isinstance(value, dict):
        raise PromotionError(f"{description}은 JSON 객체여야 합니다.")
    return cast(dict[str, Any], value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PromotionError(f"중복 JSON key는 허용하지 않습니다: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise PromotionError(f"비표준 JSON 숫자는 허용하지 않습니다: {value}")


def _open_regular_readonly(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        file_descriptor = os.open(path, flags)
    except OSError as exception:
        raise PromotionError(f"일반 파일을 안전하게 열 수 없습니다: {path}") from exception
    file_status = os.fstat(file_descriptor)
    if not stat.S_ISREG(file_status.st_mode):
        os.close(file_descriptor)
        raise PromotionError(f"일반 파일이 아닙니다: {path}")
    return file_descriptor


def _file_identity(path: Path) -> tuple[int, str]:
    file_descriptor = _open_regular_readonly(path)
    digest = sha256()
    with os.fdopen(file_descriptor, "rb", closefd=True) as file:
        file_status = os.fstat(file.fileno())
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return file_status.st_size, digest.hexdigest()


def _file_sha256(path: Path) -> str:
    return _file_identity(path)[1]


def _canonical_json_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _validated_biases(value: object, description: str) -> dict[str, tuple[float, ...]]:
    try:
        biases = validated_sentiment_logit_biases(value)
    except ValueError as exception:
        raise PromotionError(f"{description}의 logit bias 계약이 다릅니다.") from exception
    if tuple(biases) != SENTIMENT_LOGIT_BIAS_DOMAINS:
        raise PromotionError(f"{description}의 logit bias 도메인 순서가 다릅니다.")
    return biases


def _mapping(value: object, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PromotionError(f"{description}은 JSON 객체여야 합니다.")
    return cast(dict[str, Any], value)


def _integer(value: object, description: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise PromotionError(f"{description} 값이 올바르지 않습니다.")
    return value


def _finite_number(value: object, description: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise PromotionError(f"{description} 값이 숫자가 아닙니다.")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise PromotionError(f"{description} 값이 유한하지 않습니다.")
    return numeric


def _score(metrics: dict[str, Any], field: str) -> float:
    score = _finite_number(metrics.get(field), field)
    if not 0.0 <= score <= 1.0:
        raise PromotionError(f"{field} 점수가 0과 1 사이가 아닙니다.")
    return score


def _sample_count(metrics: dict[str, Any], minimum: int) -> bool:
    value = metrics.get("sample_count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromotionError("sample_count가 0 이상의 정수가 아닙니다.")
    return value >= minimum


def _aware_datetime(value: object, description: str) -> datetime:
    if not isinstance(value, str):
        raise PromotionError(f"{description}이 문자열이 아닙니다.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exception:
        raise PromotionError(f"{description} 형식이 올바르지 않습니다.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PromotionError(f"{description}에 시간대가 없습니다.")
    return parsed.astimezone(UTC)


def _sha256_value(value: object, description: str) -> str:
    if not _is_sha256(value):
        raise PromotionError(f"{description} 형식이 올바르지 않습니다.")
    return cast(str, value)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode)
    except OSError:
        return False


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _remove_path(path: Path) -> None:
    if path.is_symlink() or _is_regular_file(path):
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    file_descriptor = os.open(path, flags)
    try:
        os.fsync(file_descriptor)
    finally:
        os.close(file_descriptor)


if __name__ == "__main__":
    main()
