from __future__ import annotations

import base64
import binascii
import hmac
import json
import math
import os
import re
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, NoReturn, cast

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from hannah_montana_ai.services.sentiment_artifact_contract import (
    BENCHMARK_SCHEMA_VERSION as V6_BENCHMARK_SCHEMA_VERSION,
)
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
from hannah_montana_ai.services.sentiment_runtime_parity import (
    LOGITS_MAX_ABS_ERROR_TOLERANCE,
    validate_cpu_serving_parity_evidence,
)
from hannah_montana_ai.services.sentiment_runtime_parity import (
    V6_SCHEMA_VERSION as V6_PARITY_SCHEMA_VERSION,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import RECIPE_RELATIVE_PATHS
from hannah_montana_ai.training.sentiment_git_attestation import (
    LIMITATIONS as GIT_ATTESTATION_LIMITATIONS,
)
from hannah_montana_ai.training.sentiment_git_attestation import (
    ROLE as GIT_ATTESTATION_ROLE,
)
from hannah_montana_ai.training.sentiment_git_attestation import (
    SCHEMA_VERSION as GIT_ATTESTATION_SCHEMA_VERSION,
)
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    validate_v6_confirmatory_baseline_commitments,
    validate_v6_statistical_analysis_plan,
)

CURRENT_SCHEMA_VERSION = "hana-sentiment-release-pointer/v1"
RELEASE_SCHEMA_VERSION = "hana-sentiment-release/v1"
V6_CURRENT_SCHEMA_VERSION = "hana-sentiment-release-pointer/v2"
V6_RELEASE_SCHEMA_VERSION = "hana-sentiment-release/v2"
BENCHMARK_SCHEMA_VERSION = "korean-finance-sentiment-benchmark/v4"
TRAINING_SCHEMA_VERSION = "kf-deberta-sentiment-training/v2"
LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v1"
RECEIPT_SCHEMA_VERSION = "sentiment-sealed-evaluation-consumption/v1"
ARTIFACT_SCHEMA_VERSION = "kf-deberta-sentiment-artifact/v2"
INPUT_FEATURE_VERSION = "source-target-prefix-head-tail/v2"
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
CANDIDATE_MODEL = "kf_deberta_lora_locked"
PRE_K_FNSPID_MODEL = "pre_k_fnspid_kf_deberta"
FAIR_BASELINE_MODEL = "kr_finbert_sc_same_data_fair"
NO_K_ABLATION_MODEL = "kf_deberta_no_k_ablation"
CANDIDATE_TRAINING_STRATEGY = (
    "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
)
FAIR_BASELINE_TRAINING_STRATEGY = (
    "full-finetune-same-three-way-dual-gold-target-swap-rdrop-hierarchical/v4"
)
AUXILIARY_TRAINING_INPUTS = {
    "news_auxiliary_training_gold": (
        "data/training/k_fnspid_news_sentiment_auxiliary_gold_v2.jsonl"
    ),
    "disclosure_auxiliary_training_gold": (
        "data/training/k_fnspid_disclosure_sentiment_auxiliary_gold_v2.jsonl"
    ),
    "news_auxiliary_training_report": (
        "reports/k-fnspid-news-sentiment-training-reclassification-v2.json"
    ),
    "disclosure_auxiliary_training_report": (
        "reports/k-fnspid-disclosure-sentiment-training-reclassification-v2.json"
    ),
}
AUXILIARY_TRAINING_PAIRS = (
    ("NEWS", "news_auxiliary_training_gold", "news_auxiliary_training_report"),
    (
        "DISCLOSURE",
        "disclosure_auxiliary_training_gold",
        "disclosure_auxiliary_training_report",
    ),
)
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
SUPPORTED_SOURCES = ("NEWS", "DISCLOSURE")
REFERENCE_BASELINES = (
    "kr_finbert_sc_raw_off_the_shelf",
    PRE_K_FNSPID_MODEL,
    FAIR_BASELINE_MODEL,
    NO_K_ABLATION_MODEL,
)
CONFIRMATORY_METHOD = (
    "stratified SRSWOR delete-1 jackknife with finite-population correction; "
    "Holm-adjusted paired normal tests"
)
NORMAL_95_Z = 1.959963984540054
LOCAL_ATTESTATION_MODE = "local-untrusted"
PRODUCTION_ATTESTATION_MODE = "dsse-ed25519-v1"
DSSE_PAYLOAD_TYPE = "application/vnd.hana.sentiment.release.v1+json"
V6_DSSE_PAYLOAD_TYPE = "application/vnd.hana.sentiment.release.v2+json"
MAX_JSON_BYTES = 64 * 1024 * 1024
MAX_RELEASE_FILES = 100_000
RELEASE_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,239}\Z")
GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
TRAINING_ARTIFACT_FILES = frozenset(
    {
        "adapter_config.json",
        "adapter_model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    }
)
LOCKED_ARTIFACT_FILES = TRAINING_ARTIFACT_FILES | {"hannah_metadata.json"}
REQUIRED_EVIDENCE_ROLES = frozenset(
    {
        "candidate_git_attestation",
        "news_auxiliary_training_gold",
        "disclosure_auxiliary_training_gold",
        "news_auxiliary_training_report",
        "disclosure_auxiliary_training_report",
        "fair_baseline_selection_report",
        "fair_baseline_training_report",
        "training_report",
        "benchmark_report",
        "candidate_lock",
        "consumption_receipt",
        "sampling_design",
        "reservation_news",
        "reservation_disclosure",
        "sealed_gold_news",
        "sealed_gold_disclosure",
        "gold_promotion_news",
        "gold_promotion_disclosure",
        "tfidf_baseline",
        "pre_k_fnspid_metadata",
        "pre_k_fnspid_training_report",
        "cpu_runtime_parity",
    }
)
REQUIRED_RUNTIME_CODE = frozenset(
    {
        "scripts/train_kf_deberta_sentiment_v2.py",
        "scripts/evaluate_locked_kf_deberta_sentiment.py",
        "scripts/promote_kf_deberta_sentiment_deployment.py",
        "scripts/attest_sentiment_candidate_git_commit.py",
        "scripts/generate_sentiment_cpu_runtime_parity.py",
        "src/hannah_montana_ai/services/sentiment_input.py",
        "src/hannah_montana_ai/services/sentiment_release.py",
        "src/hannah_montana_ai/services/transformer_sentiment_model.py",
        "src/hannah_montana_ai/training/sentiment_protocol.py",
        "src/hannah_montana_ai/training/sentiment_git_attestation.py",
        "src/hannah_montana_ai/training/sentiment_sampling.py",
        "src/hannah_montana_ai/training/sentiment_baseline_commitments.py",
        "src/hannah_montana_ai/services/sentiment_runtime_parity.py",
        "pyproject.toml",
        "uv.lock",
    }
)
V6_REQUIRED_RUNTIME_CODE = frozenset(
    {
        "scripts/train_kf_deberta_sentiment_v6.py",
        "scripts/train_kf_deberta_sentiment_v6_ablation.py",
        "scripts/train_kr_finbert_sc_sentiment_v6.py",
        "scripts/lock_kf_deberta_sentiment_candidate.py",
        "scripts/evaluate_locked_kf_deberta_sentiment.py",
        "scripts/generate_sentiment_cpu_runtime_parity.py",
        "scripts/promote_kf_deberta_sentiment_deployment.py",
        "scripts/attest_sentiment_candidate_git_commit.py",
        "scripts/verify_sentiment_release.py",
        "scripts/activate_signed_sentiment_release.py",
        "src/hannah_montana_ai/services/sentiment_artifact_contract.py",
        "src/hannah_montana_ai/services/source_hierarchical_sentiment.py",
        "src/hannah_montana_ai/services/kr_finbert_sc_v6_baseline.py",
        "src/hannah_montana_ai/services/sentiment_release.py",
        "src/hannah_montana_ai/services/sentiment_runtime_parity.py",
        "src/hannah_montana_ai/services/transformer_sentiment_model.py",
        "src/hannah_montana_ai/services/sentiment_input.py",
        "src/hannah_montana_ai/training/sentiment_protocol.py",
        "src/hannah_montana_ai/training/sentiment_git_attestation.py",
        "src/hannah_montana_ai/training/sentiment_v6_evaluation_contract.py",
        "src/hannah_montana_ai/training/sentiment_v6_baseline_commitment.py",
        "pyproject.toml",
        "uv.lock",
    }
)
V6_PRODUCTION_EVIDENCE_ROLES = frozenset(
    {
        "training_report",
        "benchmark_report",
        "candidate_lock",
        "candidate_git_attestation",
        "consumption_receipt",
        "cpu_runtime_parity",
    }
)
V6_FIXTURE_EVIDENCE_ROLES = frozenset(
    {"training_report", "benchmark_report", "candidate_lock", "cpu_runtime_parity"}
)


class SentimentReleaseError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class VerifiedSentimentRelease:
    release_id: str
    version: str
    artifact_path: Path
    training_report_path: Path
    benchmark_report_path: Path
    candidate_lock_path: Path
    receipt_path: Path
    base_model_path: Path
    release_manifest: dict[str, Any]
    training_report: dict[str, Any]
    benchmark_report: dict[str, Any]


def verify_sentiment_release(
    current_path: Path,
    base_model_path: Path,
    *,
    project_root: Path,
    runtime_environment: str,
    attestation_mode: str,
    public_key_path: Path | None = None,
    signer_key_id: str = "",
    expected_release_id: str = "",
    expected_git_commit: str = "",
    base_model_verification_path: Path | None = None,
) -> VerifiedSentimentRelease:
    if runtime_environment not in {"local", "test", "production"}:
        raise SentimentReleaseError("지원하지 않는 runtime environment입니다.")
    if runtime_environment == "production" and not expected_release_id:
        raise SentimentReleaseError("production에는 예상 release ID가 필요합니다.")
    root = _existing_directory(project_root, "프로젝트 root")
    pointer_path = _safe_regular_path(current_path, "release 포인터")
    pointer = _load_json(pointer_path, "release 포인터")
    if pointer.get("schema_version") == V6_CURRENT_SCHEMA_VERSION:
        return _verify_v6_sentiment_release(
            pointer_path=pointer_path,
            pointer=pointer,
            project_root=root,
            runtime_environment=runtime_environment,
            attestation_mode=attestation_mode,
            public_key_path=public_key_path,
            signer_key_id=signer_key_id,
            expected_release_id=expected_release_id,
            expected_git_commit=expected_git_commit,
        )
    release_id = _release_id(pointer.get("release_id"))
    manifest_relative = _safe_relative_path(
        pointer.get("release_manifest_path"), "release manifest 경로"
    )
    expected_relative = Path(release_id) / "release.json"
    if (
        pointer.get("schema_version") != CURRENT_SCHEMA_VERSION
        or manifest_relative != expected_relative
    ):
        raise SentimentReleaseError("release 포인터 계약이 올바르지 않습니다.")
    if expected_release_id and release_id != expected_release_id:
        raise SentimentReleaseError("활성 release ID가 배포 계약과 다릅니다.")

    release_root = _existing_directory(pointer_path.parent, "sentiment release root")
    manifest_path = _contained_regular_path(
        release_root,
        manifest_relative,
        "release manifest",
    )
    manifest_commitment = _file_commitment(pointer.get("release_manifest"), "release manifest")
    _verify_file_commitment(manifest_path, manifest_commitment, "release manifest")
    manifest_bytes = _read_regular_bytes(manifest_path, MAX_JSON_BYTES, "release manifest")
    manifest = _decode_json(manifest_bytes, "release manifest")
    if (
        manifest.get("schema_version") != RELEASE_SCHEMA_VERSION
        or manifest.get("release_id") != release_id
    ):
        raise SentimentReleaseError("release manifest 식별자가 포인터와 다릅니다.")

    _verify_attestation(
        pointer,
        release_root=release_root,
        release_manifest_bytes=manifest_bytes,
        runtime_environment=runtime_environment,
        configured_mode=attestation_mode,
        public_key_path=public_key_path,
        signer_key_id=signer_key_id,
    )
    source = _mapping(manifest.get("source"), "release source")
    git_commit = source.get("git_commit")
    if not isinstance(git_commit, str) or GIT_COMMIT_PATTERN.fullmatch(git_commit) is None:
        raise SentimentReleaseError("release Git commit 형식이 올바르지 않습니다.")
    if runtime_environment == "production" and source.get("dirty") is not False:
        raise SentimentReleaseError("production release는 dirty source에서 생성할 수 없습니다.")
    if expected_git_commit and not hmac.compare_digest(git_commit, expected_git_commit):
        raise SentimentReleaseError("release Git commit이 배포 환경과 다릅니다.")
    if runtime_environment == "production" and not expected_git_commit:
        raise SentimentReleaseError("production에는 예상 Git commit이 필요합니다.")

    release_dir = _existing_directory(manifest_path.parent, "release 디렉터리")
    artifact_path = _verify_artifact(release_dir, manifest.get("artifact"))
    _verify_base_model(
        base_model_path,
        manifest.get("base_model"),
        verification_path=base_model_verification_path,
    )
    reference_artifacts = _verify_reference_artifacts(
        release_dir, manifest.get("reference_artifacts")
    )
    evidence_paths = _verify_evidence(release_dir, manifest.get("evidence"))
    _verify_runtime_code(root, manifest.get("runtime_code"))
    dependency_lock = _file_commitment(
        manifest.get("dependency_lock"), "dependency lock"
    )
    runtime_lock = _file_commitment(
        _mapping(manifest.get("runtime_code"), "runtime code").get("uv.lock"),
        "runtime uv.lock",
    )
    if dependency_lock != runtime_lock:
        raise SentimentReleaseError("dependency lock commitment가 runtime code와 다릅니다.")

    training_path = evidence_paths["training_report"]
    benchmark_path = evidence_paths["benchmark_report"]
    lock_path = evidence_paths["candidate_lock"]
    receipt_path = evidence_paths["consumption_receipt"]
    training = _load_json(training_path, "release 학습 report")
    benchmark = _load_json(benchmark_path, "release benchmark")
    lock = _load_json(lock_path, "release candidate lock")
    receipt = _load_json(receipt_path, "release consumption receipt")
    version = _validate_release_linkage(
        manifest,
        artifact_path=artifact_path,
        training_path=training_path,
        benchmark_path=benchmark_path,
        lock_path=lock_path,
        receipt_path=receipt_path,
        training=training,
        benchmark=benchmark,
        lock=lock,
        receipt=receipt,
        evidence_paths=evidence_paths,
        reference_artifacts=reference_artifacts,
    )
    validate_strict_sentiment_gate(benchmark)
    return VerifiedSentimentRelease(
        release_id=release_id,
        version=version,
        artifact_path=artifact_path,
        training_report_path=training_path,
        benchmark_report_path=benchmark_path,
        candidate_lock_path=lock_path,
        receipt_path=receipt_path,
        base_model_path=base_model_path,
        release_manifest=manifest,
        training_report=training,
        benchmark_report=benchmark,
    )


def _verify_v6_sentiment_release(
    *,
    pointer_path: Path,
    pointer: dict[str, Any],
    project_root: Path,
    runtime_environment: str,
    attestation_mode: str,
    public_key_path: Path | None,
    signer_key_id: str,
    expected_release_id: str,
    expected_git_commit: str,
) -> VerifiedSentimentRelease:
    release_id = _release_id(pointer.get("release_id"))
    manifest_relative = _safe_relative_path(
        pointer.get("release_manifest_path"),
        "v6 release manifest 경로",
    )
    if (
        set(pointer) != {
            "schema_version",
            "release_id",
            "release_manifest_path",
            "release_manifest",
            "attestation",
        }
        or manifest_relative != Path(release_id) / "release.json"
    ):
        raise SentimentReleaseError("v6 release 포인터 계약이 올바르지 않습니다.")
    if expected_release_id and release_id != expected_release_id:
        raise SentimentReleaseError("활성 v6 release ID가 배포 계약과 다릅니다.")
    release_root = _existing_directory(pointer_path.parent, "v6 sentiment release root")
    manifest_path = _contained_regular_path(
        release_root,
        manifest_relative,
        "v6 release manifest",
    )
    manifest_commitment = _file_commitment(
        pointer.get("release_manifest"),
        "v6 release manifest",
    )
    _verify_file_commitment(manifest_path, manifest_commitment, "v6 release manifest")
    manifest_bytes = _read_regular_bytes(
        manifest_path,
        MAX_JSON_BYTES,
        "v6 release manifest",
    )
    manifest = _decode_json(manifest_bytes, "v6 release manifest")
    if (
        set(manifest)
        != {
            "schema_version",
            "release_id",
            "created_at",
            "release_mode",
            "source",
            "candidate",
            "artifact",
            "base_model",
            "evidence",
            "runtime_code",
            "dependency_lock",
        }
        or manifest.get("schema_version") != V6_RELEASE_SCHEMA_VERSION
        or manifest.get("release_id") != release_id
    ):
        raise SentimentReleaseError("v6 release manifest 식별자 또는 필드가 다릅니다.")
    _aware_iso_datetime(manifest.get("created_at"), "v6 release created_at")
    release_mode = manifest.get("release_mode")
    if release_mode not in {"PRODUCTION_CANDIDATE", "SYNTHETIC_CONTRACT_FIXTURE"}:
        raise SentimentReleaseError("지원하지 않는 v6 release mode입니다.")
    if release_mode == "SYNTHETIC_CONTRACT_FIXTURE" and (
        runtime_environment == "production" or attestation_mode != LOCAL_ATTESTATION_MODE
    ):
        raise SentimentReleaseError("synthetic v6 release는 production/DSSE에 사용할 수 없습니다.")
    _verify_attestation(
        pointer,
        release_root=release_root,
        release_manifest_bytes=manifest_bytes,
        runtime_environment=runtime_environment,
        configured_mode=attestation_mode,
        public_key_path=public_key_path,
        signer_key_id=signer_key_id,
        payload_type=V6_DSSE_PAYLOAD_TYPE,
    )

    source = _mapping(manifest.get("source"), "v6 release source")
    if set(source) != {"git_commit", "dirty", "candidate_lock_git_commit"}:
        raise SentimentReleaseError("v6 release source 계약이 올바르지 않습니다.")
    git_commit = source.get("git_commit")
    if not isinstance(git_commit, str) or GIT_COMMIT_PATTERN.fullmatch(git_commit) is None:
        raise SentimentReleaseError("v6 release Git commit 형식이 올바르지 않습니다.")
    if expected_git_commit and not hmac.compare_digest(git_commit, expected_git_commit):
        raise SentimentReleaseError("v6 release Git commit이 배포 환경과 다릅니다.")
    if runtime_environment == "production" and (
        source.get("dirty") is not False or not expected_git_commit
    ):
        raise SentimentReleaseError(
            "production v6 release는 clean/expected Git commit이 필요합니다."
        )

    release_dir = _existing_directory(manifest_path.parent, "v6 release 디렉터리")
    artifact_path = _verify_v6_artifact(release_dir, manifest.get("artifact"))
    base_path, base_descriptor = _verify_v6_release_base(
        release_dir,
        manifest.get("base_model"),
    )
    evidence_paths = _verify_v6_evidence(
        release_dir,
        manifest.get("evidence"),
        release_mode=cast(str, release_mode),
    )
    _verify_v6_runtime_code(project_root, manifest.get("runtime_code"))
    dependency = _file_commitment(manifest.get("dependency_lock"), "v6 dependency lock")
    runtime_code = _mapping(manifest.get("runtime_code"), "v6 runtime code")
    if dependency != _file_commitment(runtime_code.get("uv.lock"), "v6 runtime uv.lock"):
        raise SentimentReleaseError("v6 dependency lock이 runtime code와 다릅니다.")

    training_path = evidence_paths["training_report"]
    benchmark_path = evidence_paths["benchmark_report"]
    lock_path = evidence_paths["candidate_lock"]
    parity_path = evidence_paths["cpu_runtime_parity"]
    training = _load_json(training_path, "v6 release 학습 report")
    benchmark = _load_json(benchmark_path, "v6 release benchmark")
    lock = _load_json(lock_path, "v6 release candidate lock")
    parity = validate_cpu_serving_parity_evidence(
        _load_json(parity_path, "v6 release runtime parity")
    )
    try:
        contract = validate_source_hierarchical_artifact(artifact_path, training)
    except RuntimeError as exception:
        raise SentimentReleaseError(str(exception)) from exception
    candidate = _mapping(manifest.get("candidate"), "v6 release candidate")
    if (
        set(candidate)
        != {
            "name",
            "model_family",
            "version",
            "input_feature_version",
            "label_order",
            "max_length",
            "base_source_kind",
        }
        or candidate.get("name") != V6_CANDIDATE_MODEL
        or candidate.get("model_family") != V6_MODEL_FAMILY
        or candidate.get("version") != contract.version
        or candidate.get("input_feature_version") != INPUT_FEATURE_VERSION
        or tuple(candidate.get("label_order", ())) != LABEL_ORDER
        or candidate.get("max_length") != contract.max_length
        or candidate.get("base_source_kind") != contract.base_source_kind
    ):
        raise SentimentReleaseError("v6 release candidate가 artifact 계약과 다릅니다.")
    if (
        base_descriptor["kind"] != contract.base_source_kind
        or base_descriptor["training_provenance"] != contract.base_source
    ):
        raise SentimentReleaseError("v6 release base와 학습 provenance가 다릅니다.")
    _validate_v6_lock_linkage(lock, lock_path=lock_path, contract=contract)
    _validate_v6_parity_linkage(
        parity,
        parity_path=parity_path,
        lock=lock,
        contract=contract,
        base_descriptor=base_descriptor,
    )
    if release_mode == "PRODUCTION_CANDIDATE":
        try:
            validate_v6_statistical_analysis_plan(lock.get("statistical_analysis_plan"))
            v6_baselines = validate_v6_confirmatory_baseline_commitments(
                lock.get("baseline_commitments"),
                project_root,
                candidate_training_report=training,
            )
        except ValueError as exception:
            raise SentimentReleaseError(str(exception)) from exception
        if lock.get("baseline_commitments_sha256") != baseline_commitments_sha256(
            v6_baselines
        ):
            raise SentimentReleaseError("v6 baseline commitment digest가 다릅니다.")
        _validate_v6_production_evidence_linkage(
            source=source,
            lock_path=lock_path,
            evidence_paths=evidence_paths,
            contract=contract,
            lock=lock,
        )
        try:
            validate_source_hierarchical_activation(benchmark, contract)
        except RuntimeError as exception:
            raise SentimentReleaseError(str(exception)) from exception
    else:
        _validate_v6_fixture_benchmark(benchmark, contract)
    return VerifiedSentimentRelease(
        release_id=release_id,
        version=contract.version,
        artifact_path=artifact_path,
        training_report_path=training_path,
        benchmark_report_path=benchmark_path,
        candidate_lock_path=lock_path,
        receipt_path=evidence_paths.get("consumption_receipt", lock_path),
        base_model_path=base_path,
        release_manifest=manifest,
        training_report=training,
        benchmark_report=benchmark,
    )


def _verify_v6_artifact(release_dir: Path, value: object) -> Path:
    artifact = _mapping(value, "v6 release artifact")
    if set(artifact) != {"path", "files", "manifest_sha256"}:
        raise SentimentReleaseError("v6 release artifact descriptor가 올바르지 않습니다.")
    relative = _safe_relative_path(artifact.get("path"), "v6 release artifact 경로")
    if relative != Path("artifact"):
        raise SentimentReleaseError("v6 release artifact 경로는 artifact여야 합니다.")
    artifact_path = _contained_directory(release_dir, relative, "v6 release artifact")
    manifest = _directory_manifest(artifact.get("files"), "v6 release artifact manifest")
    _verify_directory_tree(artifact_path, manifest, "v6 release artifact")
    if artifact.get("manifest_sha256") != _canonical_json_sha256(manifest):
        raise SentimentReleaseError("v6 release artifact manifest hash가 다릅니다.")
    return artifact_path


def _verify_v6_release_base(
    release_dir: Path,
    value: object,
) -> tuple[Path, dict[str, Any]]:
    base = _mapping(value, "v6 release base")
    if set(base) != {
        "kind",
        "path",
        "files",
        "manifest_sha256",
        "training_provenance",
        "source_manifest",
    }:
        raise SentimentReleaseError("v6 release base descriptor가 올바르지 않습니다.")
    kind = base.get("kind")
    expected_path = (
        Path("base/merged_fp32")
        if kind == "DAPT_MERGED_FP32"
        else Path("base/pinned_raw")
        if kind == "PINNED_RAW"
        else None
    )
    relative = _safe_relative_path(base.get("path"), "v6 release base 경로")
    if expected_path is None or relative != expected_path:
        raise SentimentReleaseError("v6 release base kind/path가 다릅니다.")
    directory = _contained_directory(release_dir, relative, "v6 release base")
    manifest = _directory_manifest(base.get("files"), "v6 release base manifest")
    _verify_directory_tree(directory, manifest, "v6 release base")
    if base.get("manifest_sha256") != _canonical_json_sha256(manifest):
        raise SentimentReleaseError("v6 release base manifest hash가 다릅니다.")
    try:
        validate_source_hierarchical_base_directory(directory)
    except RuntimeError as exception:
        raise SentimentReleaseError(str(exception)) from exception
    provenance = _mapping(base.get("training_provenance"), "v6 training base provenance")
    source_manifest = base.get("source_manifest")
    if kind == "DAPT_MERGED_FP32":
        commitment = _file_commitment(source_manifest, "v6 DAPT source manifest")
        source_relative = _safe_relative_path(
            commitment["path"],
            "v6 DAPT source manifest 경로",
        )
        if source_relative != Path("base/dapt-source-manifest.json"):
            raise SentimentReleaseError("v6 DAPT source manifest 경로가 다릅니다.")
        source_path = _contained_regular_path(
            release_dir,
            source_relative,
            "v6 DAPT source manifest",
        )
        _verify_file_commitment(source_path, commitment, "v6 DAPT source manifest")
        training_record = _mapping(provenance.get("manifest"), "v6 DAPT provenance manifest")
        if (
            training_record.get("bytes") != commitment["bytes"]
            or training_record.get("sha256") != commitment["sha256"]
        ):
            raise SentimentReleaseError("v6 DAPT source manifest가 학습 provenance와 다릅니다.")
    elif source_manifest is not None:
        raise SentimentReleaseError("PINNED_RAW release에는 DAPT source manifest가 없어야 합니다.")
    return directory, {
        "kind": kind,
        "files": manifest,
        "manifest_sha256": _canonical_json_sha256(manifest),
        "training_provenance": provenance,
    }


def _verify_v6_evidence(
    release_dir: Path,
    value: object,
    *,
    release_mode: str,
) -> dict[str, Path]:
    evidence = _mapping(value, "v6 release evidence")
    required = (
        V6_PRODUCTION_EVIDENCE_ROLES
        if release_mode == "PRODUCTION_CANDIDATE"
        else V6_FIXTURE_EVIDENCE_ROLES
    )
    if set(evidence) != set(required):
        raise SentimentReleaseError("v6 release evidence role 집합이 다릅니다.")
    paths: dict[str, Path] = {}
    for role in sorted(required):
        commitment = _file_commitment(evidence[role], f"v6 evidence {role}")
        relative = _safe_relative_path(commitment["path"], f"v6 evidence {role} 경로")
        if relative != Path("evidence") / f"{role}.json":
            raise SentimentReleaseError(f"v6 evidence {role} 경로가 고정 계약과 다릅니다.")
        path = _contained_regular_path(release_dir, relative, f"v6 evidence {role}")
        _verify_file_commitment(path, commitment, f"v6 evidence {role}")
        paths[role] = path
    evidence_dir = _contained_directory(release_dir, Path("evidence"), "v6 release evidence")
    actual = {
        path
        for path in evidence_dir.iterdir()
        if _is_regular_file(path) and not path.is_symlink()
    }
    if actual != set(paths.values()) or any(path.is_dir() for path in evidence_dir.iterdir()):
        raise SentimentReleaseError("v6 release evidence에 선언되지 않은 항목이 있습니다.")
    return paths


def _verify_v6_runtime_code(project_root: Path, value: object) -> None:
    runtime_code = _mapping(value, "v6 runtime code")
    if set(runtime_code) != set(V6_REQUIRED_RUNTIME_CODE):
        raise SentimentReleaseError("v6 runtime code commitment 집합이 다릅니다.")
    for relative_text in sorted(V6_REQUIRED_RUNTIME_CODE):
        relative = _safe_relative_path(relative_text, "v6 runtime code 경로")
        commitment = _file_commitment(runtime_code[relative_text], f"v6 runtime {relative}")
        if commitment["path"] != relative_text:
            raise SentimentReleaseError("v6 runtime code key와 경로가 다릅니다.")
        path = _contained_regular_path(project_root, relative, f"v6 runtime {relative}")
        _verify_file_commitment(path, commitment, f"v6 runtime {relative}")


def _v6_lock_value(lock: dict[str, Any], name: str) -> object:
    if name in lock:
        return lock[name]
    winner = lock.get("winner")
    return winner.get(name) if isinstance(winner, dict) else None


def _validate_v6_lock_linkage(
    lock: dict[str, Any],
    *,
    lock_path: Path,
    contract: Any,
) -> None:
    if (
        lock.get("schema_version") != V6_LOCK_SCHEMA_VERSION
        or lock.get("selection_only") is not True
        or lock.get("public_test_evaluated_before_lock") is not False
        or lock.get("operational_sealed_gold_evaluated_before_lock") is not False
        or _v6_lock_value(lock, "model_family") != V6_MODEL_FAMILY
        or _v6_lock_value(lock, "version") != contract.version
        or _v6_lock_value(lock, "artifact_files") != contract.locked_manifest
        or _v6_lock_value(lock, "artifact_manifest_sha256")
        != contract.locked_manifest_sha256
        or _v6_lock_value(lock, "base_source_kind") != contract.base_source_kind
        or _v6_lock_value(lock, "base_source") != contract.base_source
        or lock_path.stat().st_size < 1
    ):
        raise SentimentReleaseError("v6 candidate lock과 release artifact가 다릅니다.")


def _validate_v6_parity_linkage(
    parity: dict[str, Any],
    *,
    parity_path: Path,
    lock: dict[str, Any],
    contract: Any,
    base_descriptor: dict[str, Any],
) -> None:
    candidate = _mapping(parity.get("candidate"), "v6 parity candidate")
    lock_parity = _mapping(lock.get("runtime_parity"), "v6 lock runtime parity")
    evidence = _file_commitment(lock_parity.get("evidence"), "v6 parity evidence")
    release_base_safetensors = {
        name: record
        for name, record in base_descriptor["files"].items()
        if name.endswith(".safetensors")
    }
    evaluator_base = _mapping(
        _mapping(parity.get("evaluator"), "v6 parity evaluator").get("base_encoder"),
        "v6 parity evaluator base",
    )
    if (
        parity.get("schema_version") != V6_PARITY_SCHEMA_VERSION
        or candidate.get("model_family") != V6_MODEL_FAMILY
        or candidate.get("version") != contract.version
        or candidate.get("artifact_manifest_sha256") != contract.locked_manifest_sha256
        or candidate.get("base_source_kind") != contract.base_source_kind
        or evidence["bytes"] != parity_path.stat().st_size
        or evidence["sha256"] != _file_sha256(parity_path)
        or evaluator_base.get("safetensors_files") != release_base_safetensors
    ):
        raise SentimentReleaseError("v6 runtime parity와 release 가중치 연결이 다릅니다.")


def _validate_v6_production_evidence_linkage(
    *,
    source: dict[str, Any],
    lock_path: Path,
    evidence_paths: dict[str, Path],
    contract: Any,
    lock: dict[str, Any],
) -> None:
    attestation = _load_json(
        evidence_paths["candidate_git_attestation"],
        "v6 candidate Git attestation",
    )
    git = _mapping(attestation.get("git"), "v6 candidate Git attestation.git")
    lock_record = _mapping(
        attestation.get("candidate_lock"),
        "v6 candidate Git attestation lock",
    )
    commit = git.get("commit_sha")
    if (
        attestation.get("schema_version") != GIT_ATTESTATION_SCHEMA_VERSION
        or git.get("commit_is_ancestor_of_remote_tracking_ref") is not True
        or not isinstance(commit, str)
        or GIT_COMMIT_PATTERN.fullmatch(commit) is None
        or lock_record.get("bytes") != lock_path.stat().st_size
        or lock_record.get("sha256") != _file_sha256(lock_path)
        or source.get("candidate_lock_git_commit") != commit
    ):
        raise SentimentReleaseError("v6 candidate Git attestation 연결이 다릅니다.")
    receipt = _load_json(evidence_paths["consumption_receipt"], "v6 consumption receipt")
    if (
        receipt.get("candidate_version") != contract.version
        or receipt.get("candidate_lock_manifest_sha256") != _file_sha256(lock_path)
        or receipt.get("candidate_artifact_manifest_sha256")
        != contract.locked_manifest_sha256
        or receipt.get("cpu_runtime_parity") != lock.get("runtime_parity")
        or receipt.get("labels_loaded_before_receipt") is not False
        or receipt.get("one_shot") is not True
    ):
        raise SentimentReleaseError("v6 sealed evaluation consumption 연결이 다릅니다.")


def _validate_v6_fixture_benchmark(benchmark: dict[str, Any], contract: Any) -> None:
    fixture = _mapping(benchmark.get("fixture_contract"), "v6 fixture contract")
    gate = _mapping(benchmark.get("deployment_gate"), "v6 fixture deployment gate")
    candidate_lock = _mapping(benchmark.get("candidate_lock"), "v6 fixture candidate lock")
    if (
        benchmark.get("schema_version") != V6_BENCHMARK_SCHEMA_VERSION
        or fixture
        != {
            "schema_version": "sentiment-v6-evaluation-fixture/v1",
            "real_labels_opened": False,
            "mock_labels_only": True,
            "production_eligible": False,
        }
        or candidate_lock.get("schema_version") != V6_LOCK_SCHEMA_VERSION
        or candidate_lock.get("selection_only") is not True
        or _v6_lock_value(candidate_lock, "model_family") != V6_MODEL_FAMILY
        or _v6_lock_value(candidate_lock, "version") != contract.version
        or _v6_lock_value(candidate_lock, "artifact_manifest_sha256")
        != contract.locked_manifest_sha256
        or gate.get("candidate_model") != V6_CANDIDATE_MODEL
        or gate.get("candidate_model_family") != V6_MODEL_FAMILY
        or gate.get("candidate_version") != contract.version
        or gate.get("candidate_artifact_manifest_sha256")
        != contract.locked_manifest_sha256
        or gate.get("eligible") is not False
        or gate.get("decision") != "FIXTURE_ONLY_DO_NOT_DEPLOY"
    ):
        raise SentimentReleaseError("v6 synthetic evaluation fixture 계약이 다릅니다.")


def expected_sentiment_gate_checks(benchmark: dict[str, Any]) -> dict[str, bool]:
    source_gold = _mapping(benchmark.get("source_sealed_gold"), "source sealed Gold")
    news = _mapping(source_gold.get("NEWS"), "뉴스 sealed Gold")
    disclosure = _mapping(source_gold.get("DISCLOSURE"), "공시 sealed Gold")
    inference = _mapping(benchmark.get("confirmatory_inference"), "확증 추론")
    return {
        "news_sample_count": _sample_count(news, 500),
        "news_accuracy": _score(news, "accuracy") >= 0.90,
        "news_macro_f1": _score(news, "macro_f1") >= 0.85,
        "news_tfidf_accuracy_non_regression": _score(news, "accuracy")
        >= _score(news, "baseline_accuracy"),
        "news_tfidf_macro_f1_non_regression": _score(news, "macro_f1")
        >= _score(news, "baseline_macro_f1"),
        "news_kr_finbert_macro_f1_non_regression": _score(news, "macro_f1")
        >= _score(news, "kr_finbert_sc_macro_f1"),
        "news_kr_finbert_accuracy_non_regression": _score(news, "accuracy")
        >= _score(news, "kr_finbert_sc_accuracy"),
        "news_raw_kr_finbert_macro_f1_non_regression": _score(news, "macro_f1")
        >= _score(news, "kr_finbert_sc_raw_macro_f1"),
        "news_raw_kr_finbert_accuracy_non_regression": _score(news, "accuracy")
        >= _score(news, "kr_finbert_sc_raw_accuracy"),
        "news_pre_k_fnspid_macro_f1_improvement": _score(news, "macro_f1")
        > _score(news, "pre_k_fnspid_macro_f1"),
        "news_fair_baseline_macro_f1_non_regression": _score(news, "macro_f1")
        >= _score(news, "fair_baseline_macro_f1"),
        "news_fair_baseline_accuracy_non_regression": _score(news, "accuracy")
        >= _score(news, "fair_baseline_accuracy"),
        "news_no_k_ablation_macro_f1_non_regression": _score(news, "macro_f1")
        >= _score(news, "no_k_ablation_macro_f1"),
        "news_no_k_ablation_accuracy_non_regression": _score(news, "accuracy")
        >= _score(news, "no_k_ablation_accuracy"),
        "disclosure_sample_count": _sample_count(disclosure, 500),
        "disclosure_accuracy": _score(disclosure, "accuracy") >= 0.90,
        "disclosure_macro_f1": _score(disclosure, "macro_f1") >= 0.85,
        "disclosure_tfidf_accuracy_non_regression": _score(disclosure, "accuracy")
        >= _score(disclosure, "baseline_accuracy"),
        "disclosure_tfidf_macro_f1_non_regression": _score(disclosure, "macro_f1")
        >= _score(disclosure, "baseline_macro_f1"),
        "disclosure_kr_finbert_macro_f1_non_regression": _score(disclosure, "macro_f1")
        >= _score(disclosure, "kr_finbert_sc_macro_f1"),
        "disclosure_kr_finbert_accuracy_non_regression": _score(disclosure, "accuracy")
        >= _score(disclosure, "kr_finbert_sc_accuracy"),
        "disclosure_raw_kr_finbert_macro_f1_non_regression": _score(
            disclosure, "macro_f1"
        )
        >= _score(disclosure, "kr_finbert_sc_raw_macro_f1"),
        "disclosure_raw_kr_finbert_accuracy_non_regression": _score(disclosure, "accuracy")
        >= _score(disclosure, "kr_finbert_sc_raw_accuracy"),
        "disclosure_pre_k_fnspid_macro_f1_improvement": _score(disclosure, "macro_f1")
        > _score(disclosure, "pre_k_fnspid_macro_f1"),
        "disclosure_fair_baseline_macro_f1_non_regression": _score(
            disclosure, "macro_f1"
        )
        >= _score(disclosure, "fair_baseline_macro_f1"),
        "disclosure_fair_baseline_accuracy_non_regression": _score(
            disclosure, "accuracy"
        )
        >= _score(disclosure, "fair_baseline_accuracy"),
        "disclosure_no_k_ablation_macro_f1_non_regression": _score(
            disclosure, "macro_f1"
        )
        >= _score(disclosure, "no_k_ablation_macro_f1"),
        "disclosure_no_k_ablation_accuracy_non_regression": _score(
            disclosure, "accuracy"
        )
        >= _score(disclosure, "no_k_ablation_accuracy"),
        "news_and_disclosure_statistically_superior_to_raw_kr_finbert_reference": (
            inference.get("raw_kr_finbert_reference_superiority_claim_allowed") is True
            and inference.get("global_sota_claim_allowed") is False
        ),
        "news_and_disclosure_statistically_superior_to_pre_k_fnspid": (
            inference.get("pre_k_fnspid_superiority_claim_allowed") is True
            and inference.get("global_sota_claim_allowed") is False
        ),
        "news_and_disclosure_statistically_superior_to_fair_baseline": (
            inference.get("fair_baseline_superiority_claim_allowed") is True
            and inference.get("global_sota_claim_allowed") is False
        ),
        "news_and_disclosure_statistically_superior_to_no_k_ablation": (
            inference.get("no_k_ablation_superiority_claim_allowed") is True
            and inference.get("global_sota_claim_allowed") is False
        ),
    }


def validate_strict_sentiment_gate(benchmark: dict[str, Any]) -> None:
    if (
        benchmark.get("schema_version") != BENCHMARK_SCHEMA_VERSION
        or benchmark.get("input_feature_version") != INPUT_FEATURE_VERSION
    ):
        raise SentimentReleaseError("benchmark schema 또는 입력 계약이 다릅니다.")
    public = _mapping(benchmark.get("public_test"), "공개 Test 진단")
    if not isinstance(public.get("sample_count"), int) or isinstance(
        public.get("sample_count"), bool
    ):
        raise SentimentReleaseError("공개 Test 진단 표본 수가 올바르지 않습니다.")
    for field in (
        "accuracy",
        "macro_f1",
        "kr_finbert_sc_accuracy",
        "kr_finbert_sc_macro_f1",
        "kr_finbert_sc_raw_accuracy",
        "kr_finbert_sc_raw_macro_f1",
        "pre_k_fnspid_accuracy",
        "pre_k_fnspid_macro_f1",
        "fair_baseline_accuracy",
        "fair_baseline_macro_f1",
        "no_k_ablation_accuracy",
        "no_k_ablation_macro_f1",
    ):
        _score(public, field)
    diagnostics = _mapping(
        _mapping(benchmark.get("deployment_gate"), "deployment gate").get(
            "secondary_regression_diagnostics"
        ),
        "공개 Test secondary 진단",
    )
    if (
        diagnostics.get("role") != "repeatedly_exposed_secondary_regression_set_non_gating"
        or diagnostics.get("affects_deployment_decision") is not False
    ):
        raise SentimentReleaseError("공개 Test는 비-gating secondary 진단이어야 합니다.")

    _validate_confirmatory_inference(benchmark)
    gate = _mapping(benchmark.get("deployment_gate"), "deployment gate")
    checks = _mapping(gate.get("checks"), "deployment gate checks")
    if any(str(name).startswith("public_") for name in checks):
        raise SentimentReleaseError("공개 Test 진단은 deployment veto에 사용할 수 없습니다.")
    expected_checks = expected_sentiment_gate_checks(benchmark)
    if (
        gate.get("candidate_model") != CANDIDATE_MODEL
        or checks != expected_checks
        or not all(expected_checks.values())
        or gate.get("eligible") is not True
        or gate.get("decision") != "DEPLOY_HANA_MONTANA_AI"
    ):
        raise SentimentReleaseError("deployment gate가 확증 지표와 일치하지 않습니다.")
    thresholds = _mapping(gate.get("thresholds"), "deployment thresholds")
    if (
        thresholds.get("minimum_sealed_sample_count_per_source") != 500
        or _finite_number(
            thresholds.get("minimum_sealed_accuracy_per_source"), "최소 sealed accuracy"
        )
        != 0.90
        or _finite_number(
            thresholds.get("minimum_sealed_macro_f1_per_source"), "최소 sealed Macro-F1"
        )
        != 0.85
        or thresholds.get("sealed_must_match_or_exceed_reference_family")
        != [
            "target-aware snunlp/KR-FinBERT-SC",
            "raw snunlp/KR-FinBERT-SC",
            "same-data/split/selection-budget full-finetuned snunlp/KR-FinBERT-SC",
            "locked KF-DeBERTa no-K-FNSPID ablation",
        ]
        or thresholds.get("blind_teacher_diagnostic_only_not_gating")
        != "Qwen3-4B-GGUF-Q4"
        or any("public" in str(key).lower() for key in thresholds)
        or "delete-1 jackknife" not in str(
            thresholds.get("confirmatory_superiority_requires", "")
        )
    ):
        raise SentimentReleaseError("deployment threshold 계약이 올바르지 않습니다.")


def _validate_confirmatory_inference(benchmark: dict[str, Any]) -> None:
    inference = _mapping(benchmark.get("confirmatory_inference"), "확증 추론")
    sources = _mapping(inference.get("sources"), "확증 출처")
    source_gold = _mapping(benchmark.get("source_sealed_gold"), "source sealed Gold")
    if (
        inference.get("paired_inference") != CONFIRMATORY_METHOD
        or inference.get("global_sota_claim_allowed") is not False
        or inference.get("family")
        != (
            "NEWS/DISCLOSURE x raw KR-FinBERT-SC/pre-K-FNSPID/"
            "same-data KR-FinBERT-SC/no-K ablation"
        )
        or inference.get("family_hypothesis_count") != 8
        or inference.get("multiple_comparison_correction") != "Holm family-wise alpha=0.05"
        or inference.get("primary_metric")
        != "sampling-design-weighted plug-in Macro-F1"
        or _mapping(
            inference.get("qwen_confirmatory_exclusion"), "Qwen 확증 제외 계약"
        ).get("affects_deployment_gate")
        is not False
        or _mapping(
            inference.get("target_aware_kr_finbert_input_ablation"),
            "target-aware KR-FinBERT 진단",
        ).get("role")
        != "candidate_input_format_diagnostic_non_claim"
        or set(sources) != set(SUPPORTED_SOURCES)
    ):
        raise SentimentReleaseError("확증 추론 계약이 올바르지 않습니다.")

    family_rows: list[tuple[dict[str, Any], float]] = []
    for source in SUPPORTED_SOURCES:
        source_inference = _mapping(sources.get(source), f"{source} 확증 추론")
        if set(source_inference) != set(REFERENCE_BASELINES):
            raise SentimentReleaseError(f"{source} 확증 기준선 구성이 다릅니다.")
        source_result = _mapping(source_gold.get(source), f"{source} sealed Gold")
        models = _mapping(source_result.get("models"), f"{source} model 지표")
        if CANDIDATE_MODEL not in models:
            raise SentimentReleaseError(f"{source} 후보 model 지표가 없습니다.")
        for model_name, model_metrics_raw in models.items():
            model_metrics = _mapping(model_metrics_raw, f"{source}/{model_name} 지표")
            _validate_sampling_design_jackknife(
                model_metrics.get("sampling_design_delete_1_jackknife_95_ci"),
                f"{source}/{model_name} 설계 jackknife",
                paired=False,
            )
        comparisons = _mapping(
            source_result.get("statistical_comparisons"), f"{source} paired 비교"
        )
        for baseline in REFERENCE_BASELINES:
            result = _mapping(source_inference.get(baseline), f"{source}/{baseline} 확증")
            comparison = _mapping(
                comparisons.get(f"candidate_vs_{baseline}"),
                f"{source}/{baseline} paired 비교",
            )
            paired = _mapping(
                comparison.get("paired_sampling_design_delete_1_jackknife_95_ci"),
                f"{source}/{baseline} paired jackknife",
            )
            paired_intervals = _validate_sampling_design_jackknife(
                paired,
                f"{source}/{baseline} paired jackknife",
                paired=True,
            )
            comparison_interval = paired_intervals["macro_f1_difference"]
            inference_interval = _validate_jackknife_interval(
                result.get("paired_sampling_design_jackknife_95_ci"),
                f"{source}/{baseline} 확증 Macro-F1 차이",
            )
            if not _numbers_match(comparison_interval, inference_interval):
                raise SentimentReleaseError(
                    f"{source}/{baseline} paired jackknife와 확증 결과가 다릅니다."
                )
            raw_p = _probability(
                result.get("sampling_design_jackknife_normal_p_value"),
                f"{source}/{baseline} paired p-value",
            )
            if not math.isclose(
                raw_p,
                comparison_interval["two_sided_normal_p_value"],
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise SentimentReleaseError(f"{source}/{baseline} 원 p-value가 다릅니다.")
            family_rows.append((result, raw_p))

    adjusted = holm_adjusted_p_values([p_value for _, p_value in family_rows])
    for (result, _), adjusted_p in zip(family_rows, adjusted, strict=True):
        declared_adjusted = _probability(result.get("holm_adjusted_p_value"), "Holm p-value")
        interval = _mapping(
            result.get("paired_sampling_design_jackknife_95_ci"), "paired jackknife"
        )
        expected_superior = (
            _finite_number(interval.get("estimate"), "paired estimate") > 0.0
            and _finite_number(interval.get("low"), "paired lower bound") > 0.0
            and adjusted_p < 0.05
        )
        if (
            not math.isclose(declared_adjusted, adjusted_p, rel_tol=0.0, abs_tol=1e-12)
            or result.get("statistically_superior") is not expected_superior
        ):
            raise SentimentReleaseError("Holm 보정 또는 확증 우월성 판정이 다릅니다.")

    expected_reference = all(
        cast(dict[str, Any], cast(dict[str, Any], sources[source])[
            "kr_finbert_sc_raw_off_the_shelf"
        ]).get("statistically_superior")
        is True
        for source in SUPPORTED_SOURCES
    )
    expected_pre_k = all(
        cast(dict[str, Any], cast(dict[str, Any], sources[source])[PRE_K_FNSPID_MODEL]).get(
            "statistically_superior"
        )
        is True
        for source in SUPPORTED_SOURCES
    )
    expected_fair = all(
        cast(dict[str, Any], cast(dict[str, Any], sources[source])[
            FAIR_BASELINE_MODEL
        ]).get("statistically_superior")
        is True
        for source in SUPPORTED_SOURCES
    )
    expected_no_k = all(
        cast(dict[str, Any], cast(dict[str, Any], sources[source])[
            NO_K_ABLATION_MODEL
        ]).get("statistically_superior")
        is True
        for source in SUPPORTED_SOURCES
    )
    if (
        inference.get("raw_kr_finbert_reference_superiority_claim_allowed")
        is not expected_reference
        or inference.get("pre_k_fnspid_superiority_claim_allowed") is not expected_pre_k
        or inference.get("fair_baseline_superiority_claim_allowed") is not expected_fair
        or inference.get("no_k_ablation_superiority_claim_allowed") is not expected_no_k
    ):
        raise SentimentReleaseError("확증 family 우월성 판정이 원 검정과 다릅니다.")


def holm_adjusted_p_values(p_values: list[float]) -> list[float]:
    if not p_values or any(not 0.0 <= value <= 1.0 for value in p_values):
        raise SentimentReleaseError("Holm 입력 p-value가 올바르지 않습니다.")
    ordered = sorted(enumerate(p_values), key=lambda row: row[1])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, (original_index, value) in enumerate(ordered):
        running = max(running, min(1.0, value * (len(p_values) - rank)))
        adjusted[original_index] = running
    return adjusted


def _validate_jackknife_interval(
    value: object,
    description: str,
    *,
    bounded: bool = False,
    require_p_value: bool = True,
) -> dict[str, float]:
    payload = _mapping(value, description)
    required = {
        "estimate",
        "variance",
        "standard_error",
        "low",
        "high",
    }
    if require_p_value:
        required.add("two_sided_normal_p_value")
    if not required.issubset(payload):
        raise SentimentReleaseError(f"{description} 필드가 부족합니다.")
    result = {name: _finite_number(payload.get(name), f"{description}.{name}") for name in required}
    standard_error = result["standard_error"]
    expected_low = result["estimate"] - NORMAL_95_Z * standard_error
    expected_high = result["estimate"] + NORMAL_95_Z * standard_error
    if bounded:
        expected_low = max(0.0, expected_low)
        expected_high = min(1.0, expected_high)
    expected_p = (
        (0.0 if result["estimate"] != 0.0 else 1.0)
        if standard_error == 0.0
        else math.erfc(abs(result["estimate"] / standard_error) / math.sqrt(2.0))
    )
    if (
        result["variance"] < 0.0
        or standard_error < 0.0
        or not math.isclose(
            standard_error**2,
            result["variance"],
            rel_tol=1e-6,
            abs_tol=1e-12,
        )
        or not math.isclose(result["low"], expected_low, rel_tol=0.0, abs_tol=1e-12)
        or not math.isclose(result["high"], expected_high, rel_tol=0.0, abs_tol=1e-12)
        or (
            require_p_value
            and (
                not 0.0 <= result["two_sided_normal_p_value"] <= 1.0
                or not math.isclose(
                    result["two_sided_normal_p_value"],
                    expected_p,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
            )
        )
    ):
        raise SentimentReleaseError(f"{description} 수치가 올바르지 않습니다.")
    return result


def _validate_sampling_design_jackknife(
    value: object,
    description: str,
    *,
    paired: bool,
) -> dict[str, dict[str, float]]:
    payload = _mapping(value, description)
    expected_method = (
        "paired_stratified_delete_1_jackknife_srswor_fpc/v1"
        if paired
        else "stratified_delete_1_jackknife_srswor_fpc/v1"
    )
    sample_counts = _mapping(payload.get("sample_n_h"), f"{description} sample_n_h")
    population_counts = _mapping(
        payload.get("population_N_h"), f"{description} population_N_h"
    )
    if (
        payload.get("method") != expected_method
        or payload.get("resampling_unit") != "unique_event_cluster"
        or set(sample_counts) != set(LABEL_ORDER)
        or set(population_counts) != set(LABEL_ORDER)
    ):
        raise SentimentReleaseError(f"{description} 설계 계약이 올바르지 않습니다.")
    total = 0
    for label in LABEL_ORDER:
        sample_count = sample_counts[label]
        population_count = population_counts[label]
        if (
            isinstance(sample_count, bool)
            or not isinstance(sample_count, int)
            or sample_count < 2
            or isinstance(population_count, bool)
            or not isinstance(population_count, int)
            or population_count < sample_count
        ):
            raise SentimentReleaseError(f"{description}/{label} 표본 설계가 올바르지 않습니다.")
        total += sample_count
    if payload.get("replicate_count") != total:
        raise SentimentReleaseError(f"{description} replicate 수가 표본 설계와 다릅니다.")
    field_names = (
        ("accuracy_difference", "macro_f1_difference")
        if paired
        else ("accuracy", "macro_f1")
    )
    return {
        field: _validate_jackknife_interval(
            payload.get(field),
            f"{description}.{field}",
            bounded=not paired,
            require_p_value=paired,
        )
        for field in field_names
    }


def _verify_attestation(
    pointer: dict[str, Any],
    *,
    release_root: Path,
    release_manifest_bytes: bytes,
    runtime_environment: str,
    configured_mode: str,
    public_key_path: Path | None,
    signer_key_id: str,
    payload_type: str = DSSE_PAYLOAD_TYPE,
) -> None:
    attestation = _mapping(pointer.get("attestation"), "release attestation")
    declared_mode = attestation.get("mode")
    if configured_mode not in {LOCAL_ATTESTATION_MODE, PRODUCTION_ATTESTATION_MODE}:
        raise SentimentReleaseError("지원하지 않는 release attestation mode입니다.")
    if runtime_environment == "production" and configured_mode != PRODUCTION_ATTESTATION_MODE:
        raise SentimentReleaseError("production은 DSSE attestation이 필수입니다.")
    if declared_mode != configured_mode:
        raise SentimentReleaseError("release 포인터와 설정의 attestation mode가 다릅니다.")
    if configured_mode == LOCAL_ATTESTATION_MODE:
        production_eligible = attestation.get("production_eligible")
        if runtime_environment == "production" or production_eligible is not False:
            raise SentimentReleaseError(
                "local-untrusted release는 production에서 사용할 수 없습니다."
            )
        return
    if public_key_path is None or not signer_key_id:
        raise SentimentReleaseError("DSSE 공개키와 signer key ID가 필요합니다.")
    envelope_commitment = _file_commitment(attestation.get("envelope"), "DSSE envelope")
    envelope_path = _contained_regular_path(
        release_root,
        _safe_relative_path(envelope_commitment["path"], "DSSE envelope 경로"),
        "DSSE envelope",
    )
    _verify_file_commitment(envelope_path, envelope_commitment, "DSSE envelope")
    _verify_dsse_envelope(
        _load_json(envelope_path, "DSSE envelope"),
        release_manifest_bytes,
        public_key_path,
        signer_key_id,
        payload_type=payload_type,
    )


def _verify_dsse_envelope(
    envelope: dict[str, Any],
    payload: bytes,
    public_key_path: Path,
    signer_key_id: str,
    *,
    payload_type: str = DSSE_PAYLOAD_TYPE,
) -> None:
    if envelope.get("payloadType") != payload_type:
        raise SentimentReleaseError("DSSE payload type이 다릅니다.")
    encoded_payload = envelope.get("payload")
    signatures = envelope.get("signatures")
    if not isinstance(encoded_payload, str) or not isinstance(signatures, list):
        raise SentimentReleaseError("DSSE envelope 형식이 올바르지 않습니다.")
    try:
        decoded_payload = base64.b64decode(encoded_payload, validate=True)
    except (ValueError, binascii.Error) as exception:
        raise SentimentReleaseError("DSSE payload가 올바른 base64가 아닙니다.") from exception
    if not hmac.compare_digest(decoded_payload, payload):
        raise SentimentReleaseError("DSSE payload가 release manifest와 다릅니다.")
    public_key_file = _safe_regular_path(public_key_path, "DSSE 공개키")
    try:
        loaded_key = serialization.load_pem_public_key(
            _read_regular_bytes(public_key_file, 64 * 1024, "DSSE 공개키")
        )
    except (TypeError, ValueError) as exception:
        raise SentimentReleaseError("DSSE 공개키를 읽을 수 없습니다.") from exception
    if not isinstance(loaded_key, Ed25519PublicKey):
        raise SentimentReleaseError("DSSE 공개키는 Ed25519여야 합니다.")
    raw_public_key = loaded_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    actual_key_id = sha256(raw_public_key).hexdigest()
    if not hmac.compare_digest(actual_key_id, signer_key_id):
        raise SentimentReleaseError("DSSE signer key ID가 고정 공개키와 다릅니다.")
    signature_row = next(
        (
            row
            for row in signatures
            if isinstance(row, dict) and row.get("keyid") == signer_key_id
        ),
        None,
    )
    if signature_row is None or not isinstance(signature_row.get("sig"), str):
        raise SentimentReleaseError("고정 signer의 DSSE 서명이 없습니다.")
    try:
        signature = base64.b64decode(signature_row["sig"], validate=True)
        loaded_key.verify(signature, _dsse_pae(payload_type, payload))
    except (ValueError, binascii.Error, InvalidSignature) as exception:
        raise SentimentReleaseError("DSSE 서명 검증에 실패했습니다.") from exception


def verify_external_dsse_envelope(
    *,
    envelope_path: Path,
    release_manifest_path: Path,
    public_key_path: Path,
    signer_key_id: str,
    payload_type: str = V6_DSSE_PAYLOAD_TYPE,
) -> dict[str, dict[str, int | str]]:
    envelope_file = _safe_regular_path(envelope_path, "외부 DSSE envelope")
    manifest_file = _safe_regular_path(release_manifest_path, "release manifest")
    payload = _read_regular_bytes(manifest_file, MAX_JSON_BYTES, "release manifest")
    _verify_dsse_envelope(
        _load_json(envelope_file, "외부 DSSE envelope"),
        payload,
        public_key_path,
        signer_key_id,
        payload_type=payload_type,
    )
    return {
        "release_manifest": {
            "path": manifest_file.name,
            "bytes": manifest_file.stat().st_size,
            "sha256": _file_sha256(manifest_file),
        },
        "envelope": {
            "path": envelope_file.name,
            "bytes": envelope_file.stat().st_size,
            "sha256": _file_sha256(envelope_file),
        },
    }


def _dsse_pae(payload_type: str, payload: bytes) -> bytes:
    type_bytes = payload_type.encode("utf-8")
    return b"DSSEv1 %d %s %d %s" % (
        len(type_bytes),
        type_bytes,
        len(payload),
        payload,
    )


def _verify_artifact(release_dir: Path, value: object) -> Path:
    artifact = _mapping(value, "release artifact")
    relative = _safe_relative_path(artifact.get("path"), "release artifact 경로")
    if relative != Path("artifact"):
        raise SentimentReleaseError("release artifact는 artifact 디렉터리여야 합니다.")
    artifact_path = _contained_directory(release_dir, relative, "release artifact")
    manifest = _directory_manifest(artifact.get("files"), "release artifact manifest")
    if set(manifest) != set(LOCKED_ARTIFACT_FILES):
        raise SentimentReleaseError("release artifact 파일 구성이 다릅니다.")
    _verify_directory_tree(artifact_path, manifest, "release artifact")
    if artifact.get("manifest_sha256") != _canonical_json_sha256(manifest):
        raise SentimentReleaseError("release artifact manifest hash가 다릅니다.")
    return artifact_path


def _verify_base_model(
    base_model_path: Path,
    value: object,
    *,
    verification_path: Path | None,
) -> None:
    base = _mapping(value, "base model")
    if base.get("model_id") != BASE_MODEL or base.get("revision") != BASE_MODEL_REVISION:
        raise SentimentReleaseError("base model ID 또는 revision이 다릅니다.")
    expected_runtime_path = base.get("runtime_path")
    if not isinstance(expected_runtime_path, str) or Path(expected_runtime_path) != base_model_path:
        raise SentimentReleaseError("base model runtime 경로가 release 계약과 다릅니다.")
    directory = _existing_directory(
        verification_path if verification_path is not None else base_model_path,
        "base model",
    )
    manifest = _directory_manifest(base.get("files"), "base model manifest")
    _verify_directory_tree(directory, manifest, "base model")
    if base.get("manifest_sha256") != _canonical_json_sha256(manifest):
        raise SentimentReleaseError("base model manifest hash가 다릅니다.")


def _verify_evidence(release_dir: Path, value: object) -> dict[str, Path]:
    evidence = _mapping(value, "release evidence")
    if not REQUIRED_EVIDENCE_ROLES.issubset(evidence):
        missing = sorted(REQUIRED_EVIDENCE_ROLES - set(evidence))
        raise SentimentReleaseError(f"release evidence가 부족합니다: {missing}")
    paths: dict[str, Path] = {}
    seen_paths: set[Path] = set()
    for role, raw_commitment in evidence.items():
        commitment = _file_commitment(raw_commitment, f"evidence {role}")
        relative = _safe_relative_path(commitment["path"], f"evidence {role} 경로")
        if not relative.is_relative_to(Path("evidence")):
            raise SentimentReleaseError(f"evidence {role}가 evidence 디렉터리 밖입니다.")
        path = _contained_regular_path(release_dir, relative, f"evidence {role}")
        if path in seen_paths:
            raise SentimentReleaseError("서로 다른 evidence가 같은 파일을 참조합니다.")
        _verify_file_commitment(path, commitment, f"evidence {role}")
        paths[str(role)] = path
        seen_paths.add(path)
    evidence_dir = _contained_directory(release_dir, Path("evidence"), "release evidence")
    actual_files = {path for path in evidence_dir.iterdir() if _is_regular_file(path)}
    invalid_entry = any(
        path.is_symlink() or path.is_dir() for path in evidence_dir.iterdir()
    )
    if actual_files != seen_paths or invalid_entry:
        raise SentimentReleaseError("release evidence에 선언되지 않은 파일이 있습니다.")
    return paths


def _verify_reference_artifacts(
    release_dir: Path,
    value: object,
) -> dict[str, tuple[Path, dict[str, dict[str, int | str]], dict[str, Any]]]:
    references = _mapping(value, "release reference artifacts")
    if set(references) != {FAIR_BASELINE_MODEL}:
        raise SentimentReleaseError("release 공정 기준선 artifact 구성이 다릅니다.")
    details = _mapping(references[FAIR_BASELINE_MODEL], "공정 기준선 artifact")
    relative = _safe_relative_path(details.get("path"), "공정 기준선 artifact 경로")
    if relative != Path("reference-artifacts/same-data-fair-baseline"):
        raise SentimentReleaseError("공정 기준선 release 경로가 고정 계약과 다릅니다.")
    directory = _contained_directory(release_dir, relative, "공정 기준선 artifact")
    files = _directory_manifest(details.get("files"), "공정 기준선 artifact manifest")
    _verify_directory_tree(directory, files, "공정 기준선 artifact")
    if details.get("manifest_sha256") != _canonical_json_sha256(files):
        raise SentimentReleaseError("공정 기준선 artifact manifest hash가 다릅니다.")
    return {FAIR_BASELINE_MODEL: (directory, files, details)}


def _verify_runtime_code(project_root: Path, value: object) -> None:
    runtime_code = _mapping(value, "runtime code")
    if not REQUIRED_RUNTIME_CODE.issubset(runtime_code):
        missing = sorted(REQUIRED_RUNTIME_CODE - set(runtime_code))
        raise SentimentReleaseError(f"runtime code commitment가 부족합니다: {missing}")
    for relative_value, raw_commitment in runtime_code.items():
        relative = _safe_relative_path(relative_value, "runtime code 경로")
        commitment = _file_commitment(raw_commitment, f"runtime code {relative}")
        if commitment["path"] != relative.as_posix():
            raise SentimentReleaseError("runtime code key와 commitment 경로가 다릅니다.")
        path = _contained_regular_path(project_root, relative, f"runtime code {relative}")
        _verify_file_commitment(path, commitment, f"runtime code {relative}")


def _validate_release_linkage(
    manifest: dict[str, Any],
    *,
    artifact_path: Path,
    training_path: Path,
    benchmark_path: Path,
    lock_path: Path,
    receipt_path: Path,
    training: dict[str, Any],
    benchmark: dict[str, Any],
    lock: dict[str, Any],
    receipt: dict[str, Any],
    evidence_paths: dict[str, Path],
    reference_artifacts: dict[
        str, tuple[Path, dict[str, dict[str, int | str]], dict[str, Any]]
    ],
) -> str:
    candidate = _mapping(manifest.get("candidate"), "release candidate")
    gate = _mapping(benchmark.get("deployment_gate"), "deployment gate")
    benchmark_lock = _mapping(benchmark.get("candidate_lock"), "benchmark candidate lock")
    winner = _mapping(lock.get("winner"), "candidate lock winner")
    benchmark_receipt = _mapping(
        benchmark.get("sealed_evaluation_consumption"), "benchmark consumption receipt"
    )
    version = training.get("version")
    receipt_payload = {
        key: value
        for key, value in benchmark_receipt.items()
        if key not in {"receipt_path", "receipt_sha256"}
    }
    if (
        training.get("schema_version") != TRAINING_SCHEMA_VERSION
        or training.get("training_strategy") != CANDIDATE_TRAINING_STRATEGY
        or lock.get("schema_version") != LOCK_SCHEMA_VERSION
        or lock.get("external_git_commitment_required") is not True
        or receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION
        or not isinstance(version, str)
        or candidate.get("name") != CANDIDATE_MODEL
        or candidate.get("version") != version
        or candidate.get("input_feature_version") != INPUT_FEATURE_VERSION
        or tuple(candidate.get("label_order", ())) != LABEL_ORDER
        or candidate.get("max_length") != training.get("max_length")
        or winner.get("version") != version
        or benchmark_lock.get("version") != version
        or gate.get("candidate_version") != version
        or receipt.get("candidate_version") != version
    ):
        raise SentimentReleaseError("release candidate 버전 연결이 다릅니다.")
    if (
        winner.get("report_sha256") != _file_sha256(training_path)
        or benchmark_lock.get("candidate_report_sha256") != _file_sha256(training_path)
        or benchmark_lock.get("manifest_sha256") != _file_sha256(lock_path)
        or receipt.get("candidate_lock_manifest_sha256") != _file_sha256(lock_path)
        or benchmark_receipt.get("receipt_sha256") != _file_sha256(receipt_path)
        or receipt_payload != receipt
    ):
        raise SentimentReleaseError("release report/lock/receipt hash 연결이 다릅니다.")
    _validate_runtime_parity_linkage(
        manifest=manifest,
        benchmark=benchmark,
        lock=lock,
        receipt=receipt,
        evidence_path=evidence_paths["cpu_runtime_parity"],
    )
    _validate_evidence_linkage(
        benchmark,
        lock,
        receipt,
        evidence_paths,
    )
    _validate_auxiliary_training_linkage(training, benchmark, evidence_paths)
    _validate_fair_baseline_linkage(
        receipt,
        benchmark,
        evidence_paths,
        reference_artifacts,
    )
    normalized_attestation = _normalized_candidate_git_attestation(
        evidence_paths["candidate_git_attestation"],
        _load_json(
            evidence_paths["candidate_git_attestation"],
            "candidate Git attestation",
        ),
        lock,
        lock_size=lock_path.stat().st_size,
        lock_sha256=_file_sha256(lock_path),
    )
    receipt_attestation = _mapping(
        receipt.get("candidate_git_attestation"),
        "consumption receipt candidate Git attestation",
    )
    if receipt_attestation != normalized_attestation:
        raise SentimentReleaseError(
            "consumption receipt의 candidate Git attestation이 release 증거와 다릅니다."
        )
    source = _mapping(manifest.get("source"), "release source")
    if (
        source.get("candidate_lock_git_commit") != normalized_attestation["commit_sha"]
        or source.get("candidate_lock_git_tree") != normalized_attestation["tree_sha"]
        or source.get("candidate_git_attestation_sha256")
        != normalized_attestation["sha256"]
    ):
        raise SentimentReleaseError(
            "release source와 candidate Git attestation commitment가 다릅니다."
        )
    _validate_gold_candidate_commitments(
        evidence_paths,
        candidate_lock_sha256=_file_sha256(lock_path),
        git_attestation_sha256=cast(str, normalized_attestation["sha256"]),
        git_commit_sha=cast(str, normalized_attestation["commit_sha"]),
    )
    artifact_manifest = _directory_manifest(
        _mapping(manifest.get("artifact"), "release artifact").get("files"),
        "release artifact manifest",
    )
    training_manifest = _directory_manifest(
        training.get("artifact_files"), "학습 artifact manifest"
    )
    if (
        set(training_manifest) != set(TRAINING_ARTIFACT_FILES)
        or any(artifact_manifest[name] != training_manifest[name] for name in training_manifest)
        or benchmark_lock.get("artifact_files") != artifact_manifest
        or gate.get("candidate_artifact_manifest_sha256")
        != _canonical_json_sha256(artifact_manifest)
        or receipt.get("candidate_artifact_manifest_sha256")
        != _canonical_json_sha256(artifact_manifest)
    ):
        raise SentimentReleaseError("release artifact manifest 연결이 다릅니다.")
    metadata = _load_json(artifact_path / "hannah_metadata.json", "artifact metadata")
    if (
        metadata.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or metadata.get("version") != version
        or metadata.get("base_model") != BASE_MODEL
        or metadata.get("base_model_revision") != BASE_MODEL_REVISION
        or metadata.get("artifact_files") != training_manifest
        or metadata.get("input_feature_version") != INPUT_FEATURE_VERSION
    ):
        raise SentimentReleaseError("artifact metadata와 release 계약이 다릅니다.")
    benchmark_commitment = _file_commitment(
        _mapping(manifest.get("evidence"), "evidence")["benchmark_report"],
        "benchmark",
    )
    if _file_sha256(benchmark_path) != cast(str, benchmark_commitment["sha256"]):
        raise SentimentReleaseError("benchmark evidence hash가 다릅니다.")
    return version


def _validate_runtime_parity_linkage(
    *,
    manifest: dict[str, Any],
    benchmark: dict[str, Any],
    lock: dict[str, Any],
    receipt: dict[str, Any],
    evidence_path: Path,
) -> None:
    parity_lock = _mapping(lock.get("runtime_parity"), "candidate runtime parity lock")
    evidence_commitment = _file_commitment(
        parity_lock.get("evidence"), "runtime parity evidence commitment"
    )
    evidence_size, evidence_digest = _file_identity(evidence_path)
    if (
        evidence_commitment["bytes"] != evidence_size
        or evidence_commitment["sha256"] != evidence_digest
        or receipt.get("cpu_runtime_parity") != parity_lock
        or benchmark.get("cpu_runtime_parity") != parity_lock
    ):
        raise SentimentReleaseError(
            "runtime parity evidence의 lock·receipt·benchmark 연결이 다릅니다."
        )
    try:
        evidence = validate_cpu_serving_parity_evidence(
            _load_json(evidence_path, "CPU runtime parity evidence")
        )
    except ValueError as exception:
        raise SentimentReleaseError(str(exception)) from exception
    candidate = _mapping(evidence.get("candidate"), "runtime parity candidate")
    release_candidate = _mapping(manifest.get("candidate"), "release candidate")
    release_artifact = _mapping(manifest.get("artifact"), "release artifact")
    if (
        candidate.get("version") != release_candidate.get("version")
        or candidate.get("version") != parity_lock.get("candidate_version")
        or candidate.get("artifact_manifest_sha256")
        != release_artifact.get("manifest_sha256")
        or candidate.get("artifact_manifest_sha256")
        != parity_lock.get("candidate_artifact_manifest_sha256")
    ):
        raise SentimentReleaseError("runtime parity candidate가 immutable release와 다릅니다.")
    comparison = _mapping(evidence.get("comparison"), "runtime parity comparison")
    if (
        comparison.get("passed") is not True
        or comparison.get("exact_label_agreement") is not True
        or _finite_number(
            comparison.get("logits_max_abs_error"), "runtime parity logits error"
        )
        > LOGITS_MAX_ABS_ERROR_TOLERANCE
        or parity_lock.get("exact_label_agreement") is not True
        or _finite_number(
            parity_lock.get("logits_max_abs_error"), "locked runtime parity error"
        )
        > LOGITS_MAX_ABS_ERROR_TOLERANCE
    ):
        raise SentimentReleaseError("runtime parity pass 조건이 release에서 재현되지 않습니다.")
    evaluator = _mapping(evidence.get("evaluator"), "runtime parity evaluator")
    packaged = _mapping(evidence.get("packaged_runtime"), "runtime parity packaged runtime")
    evaluator_base = _mapping(evaluator.get("base_encoder"), "evaluator base encoder")
    runtime_base = _mapping(packaged.get("base_encoder"), "runtime base encoder")
    evaluator_weights = _directory_manifest(
        evaluator_base.get("safetensors_files"), "evaluator safetensors manifest"
    )
    runtime_weights = _directory_manifest(
        runtime_base.get("safetensors_files"), "runtime safetensors manifest"
    )
    release_base = _mapping(manifest.get("base_model"), "release base model")
    release_files = _directory_manifest(release_base.get("files"), "release base model files")
    release_weights = {
        name: record for name, record in release_files.items() if name.endswith(".safetensors")
    }
    if (
        not release_weights
        or evaluator_weights != runtime_weights
        or evaluator_weights != release_weights
        or parity_lock.get("base_encoder_safetensors_manifest_sha256")
        != _canonical_json_sha256(evaluator_weights)
    ):
        raise SentimentReleaseError(
            "release base encoder safetensors가 parity evidence와 다릅니다."
        )


def _validate_auxiliary_training_linkage(
    training: dict[str, Any],
    benchmark: dict[str, Any],
    evidence_paths: dict[str, Path],
) -> None:
    candidate_inputs = _mapping(training.get("input_artifacts"), "후보 학습 입력")
    fair_report = _load_json(
        evidence_paths["fair_baseline_training_report"],
        "same-data 공정 기준선 학습 report",
    )
    fair_inputs = _mapping(fair_report.get("input_artifacts"), "공정 기준선 학습 입력")
    if (
        fair_report.get("schema_version")
        != "k-fnspid-fair-baseline-training/v1"
        or fair_report.get("training_strategy") != FAIR_BASELINE_TRAINING_STRATEGY
    ):
        raise SentimentReleaseError("same-data 공정 기준선 학습 전략이 다릅니다.")

    fair_summary = _mapping(
        benchmark.get("same_data_fair_baseline"),
        "benchmark same-data 공정 기준선",
    )
    same_data_contract = _mapping(
        fair_summary.get("same_data_contract"), "same-data 공정 비교 계약"
    )
    contract_sha256 = _canonical_json_sha256(same_data_contract)
    matched_inputs = _mapping(
        same_data_contract.get("matched_input_artifacts"),
        "same-data 일치 학습 입력",
    )
    if (
        fair_summary.get("same_data_contract_sha256") != contract_sha256
        or fair_summary.get("same_data_split_selection_budget_verified") is not True
        or fair_summary.get("public_test_labels_used_for_training_or_selection")
        is not False
        or fair_summary.get("confirmatory_labels_used_for_training_or_selection")
        is not False
    ):
        raise SentimentReleaseError("same-data 공정 비교 계약이 올바르지 않습니다.")

    for role, expected_path in AUXILIARY_TRAINING_INPUTS.items():
        candidate = _training_input_commitment(
            candidate_inputs.get(role), expected_path, f"후보 {role}"
        )
        fair = _training_input_commitment(
            fair_inputs.get(role), expected_path, f"공정 기준선 {role}"
        )
        matched = _training_input_commitment(
            matched_inputs.get(role), expected_path, f"same-data {role}"
        )
        copied_size, copied_sha256 = _file_identity(evidence_paths[role])
        if (
            candidate != fair
            or candidate != matched
            or candidate["bytes"] != copied_size
            or candidate["sha256"] != copied_sha256
        ):
            raise SentimentReleaseError(f"{role} 학습 입력 commitment가 다릅니다.")
    for source, gold_role, report_role in AUXILIARY_TRAINING_PAIRS:
        _validate_auxiliary_training_report(
            evidence_paths[report_role],
            source=source,
            gold_path=evidence_paths[gold_role],
            gold_commitment=_training_input_commitment(
                candidate_inputs.get(gold_role),
                AUXILIARY_TRAINING_INPUTS[gold_role],
                f"후보 {gold_role}",
            ),
        )


def _validate_auxiliary_training_report(
    report_path: Path,
    *,
    source: str,
    gold_path: Path,
    gold_commitment: dict[str, int | str],
) -> None:
    report = _load_json(report_path, f"{source} auxiliary training report")
    source_record = _mapping(report.get("source"), f"{source} auxiliary source")
    reclassification = _mapping(
        report.get("reclassification"), f"{source} auxiliary reclassification"
    )
    integrity = _mapping(report.get("integrity"), f"{source} auxiliary integrity")
    lineage = _mapping(report.get("lineage"), f"{source} auxiliary lineage")
    output = _mapping(lineage.get("output"), f"{source} auxiliary output")
    gold_count = _validate_auxiliary_gold_rows(gold_path, source)
    sample_count = source_record.get("sample_count")
    count_fields = {"review_sample_count", "excluded_unresolved_count"}
    present_fields = count_fields.intersection(source_record)
    flag_present = "unresolved_rows_excluded" in integrity
    new_contract = present_fields == count_fields and flag_present
    old_disclosure_contract = not present_fields and not flag_present
    if new_contract:
        review_count = source_record.get("review_sample_count")
        excluded_count = source_record.get("excluded_unresolved_count")
        count_contract_valid = (
            isinstance(review_count, int)
            and not isinstance(review_count, bool)
            and isinstance(excluded_count, int)
            and not isinstance(excluded_count, bool)
            and review_count >= 1
            and excluded_count >= 0
            and sample_count == gold_count
            and review_count == gold_count + excluded_count
            and integrity.get("unresolved_rows_excluded") is True
        )
    else:
        count_contract_valid = (
            old_disclosure_contract
            and source == "DISCLOSURE"
            and sample_count == gold_count
        )
    if (
        report.get("schema_version")
        != "k-fnspid-sentiment-training-reclassification/v2"
        or source_record.get("source_type") != source
        or isinstance(sample_count, bool)
        or not isinstance(sample_count, int)
        or sample_count < 1
        or not count_contract_valid
        or reclassification.get("previous_role")
        != "REPEATEDLY_EXPOSED_DIAGNOSTIC_NOT_CLAIM_EVIDENCE"
        or reclassification.get("new_role")
        != "TRAINING_ONLY_NOT_EVALUATION_OR_CLAIM_EVIDENCE"
        or reclassification.get("confirmatory_created_before_reclassification")
        is not True
        or any(
            reclassification.get(field) is not False
            for field in (
                "eligible_for_confirmatory_metrics",
                "eligible_for_evaluation",
                "eligible_for_model_selection",
                "eligible_for_superiority_claims",
            )
        )
        or any(
            integrity.get(field) is not True
            for field in (
                "exact_item_set",
                "independent_dual_review_required",
                "model_blind",
                "market_blind",
                "confirmatory_sampling_commitments_verified",
                "promotion_after_confirmatory_reservation",
                "source_review_protected_at_confirmatory_reservation",
                "write_once",
            )
        )
        or integrity.get("confirmatory_group_overlap_count") != 0
        or output != gold_commitment
    ):
        raise SentimentReleaseError(
            f"{source} auxiliary training report 계약이 올바르지 않습니다."
        )


def _validate_auxiliary_gold_rows(path: Path, source: str) -> int:
    payload = _read_regular_bytes(path, MAX_JSON_BYTES, f"{source} auxiliary training Gold")
    count = 0
    for line_number, raw_line in enumerate(payload.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(
                raw_line,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_json_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exception:
            raise SentimentReleaseError(
                f"{source} auxiliary training Gold JSONL이 올바르지 않습니다: {line_number}"
            ) from exception
        if (
            not isinstance(row, dict)
            or row.get("schema_version")
            != "k-fnspid-sentiment-auxiliary-training-gold/v2"
            or row.get("partition") != "AUXILIARY_TRAINING_GOLD"
            or row.get("source_type") != source
            or row.get("sentiment") not in LABEL_ORDER
            or row.get("final_sentiment") != row.get("sentiment")
        ):
            raise SentimentReleaseError(
                f"{source} auxiliary training Gold 계약이 올바르지 않습니다: {line_number}"
            )
        count += 1
    if count < 1:
        raise SentimentReleaseError(f"{source} auxiliary training Gold가 비어 있습니다.")
    return count


def _training_input_commitment(
    value: object,
    expected_path: str,
    description: str,
) -> dict[str, int | str]:
    raw = _mapping(value, description)
    path = raw.get("path")
    size = raw.get("bytes")
    digest = raw.get("sha256")
    if (
        set(raw) != {"path", "bytes", "sha256"}
        or path != expected_path
        or isinstance(size, bool)
        or not isinstance(size, int)
        or size < 0
        or not _is_sha256(digest)
    ):
        raise SentimentReleaseError(f"{description} commitment가 올바르지 않습니다.")
    return {"path": expected_path, "bytes": size, "sha256": cast(str, digest)}


def _validate_fair_baseline_linkage(
    receipt: dict[str, Any],
    benchmark: dict[str, Any],
    evidence_paths: dict[str, Path],
    reference_artifacts: dict[
        str, tuple[Path, dict[str, dict[str, int | str]], dict[str, Any]]
    ],
) -> None:
    baselines = _mapping(receipt.get("baseline_artifacts"), "receipt baselines")
    fair = _mapping(baselines.get(FAIR_BASELINE_MODEL), "same-data fair baseline")
    benchmark_fair = _mapping(
        benchmark.get("same_data_fair_baseline"),
        "benchmark same-data fair baseline",
    )
    directory, files, release_details = reference_artifacts[FAIR_BASELINE_MODEL]
    metadata_path = directory / "hannah_metadata.json"
    if (
        fair.get("artifact_manifest_sha256") != _canonical_json_sha256(files)
        or fair.get("metadata_sha256") != _file_sha256(metadata_path)
        or release_details.get("metadata_sha256") != _file_sha256(metadata_path)
        or release_details.get("same_data_contract_sha256")
        != fair.get("same_data_contract_sha256")
        or benchmark_fair.get("same_data_contract_sha256")
        != fair.get("same_data_contract_sha256")
        or fair.get("selection_report_sha256")
        != _file_sha256(evidence_paths["fair_baseline_selection_report"])
        or fair.get("training_report_sha256")
        != _file_sha256(evidence_paths["fair_baseline_training_report"])
    ):
        raise SentimentReleaseError("same-data 공정 기준선 release 연결이 다릅니다.")
    for field in (
        "artifact_dir",
        "selection_report_path",
        "training_report_path",
        "same_data_contract_sha256",
    ):
        if not isinstance(fair.get(field), str) or not fair[field]:
            raise SentimentReleaseError(f"same-data 공정 기준선 {field}가 없습니다.")
    if not _is_sha256(fair.get("same_data_contract_sha256")):
        raise SentimentReleaseError("same-data 공정 기준선 계약 hash가 올바르지 않습니다.")


def _normalized_candidate_git_attestation(
    attestation_path: Path,
    attestation: dict[str, Any],
    lock: dict[str, Any],
    *,
    lock_size: int,
    lock_sha256: str,
) -> dict[str, Any]:
    if (
        attestation.get("schema_version") != GIT_ATTESTATION_SCHEMA_VERSION
        or attestation.get("role") != GIT_ATTESTATION_ROLE
        or lock.get("external_git_commitment_required") is not True
    ):
        raise SentimentReleaseError("candidate Git attestation 계약이 올바르지 않습니다.")
    git = _mapping(attestation.get("git"), "candidate Git attestation.git")
    commit_sha = _git_object_id(git.get("commit_sha"), "candidate commit SHA")
    tree_sha = _git_object_id(git.get("tree_sha"), "candidate tree SHA")
    remote_name = git.get("remote_name")
    remote_ref = git.get("remote_tracking_ref")
    if (
        not isinstance(remote_name, str)
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", remote_name) is None
        or remote_name in {".", ".."}
        or not isinstance(remote_ref, str)
        or not remote_ref.startswith(f"refs/remotes/{remote_name}/")
        or remote_ref.endswith("/")
        or "\\" in remote_ref
        or "\x00" in remote_ref
        or ".." in remote_ref
        or "@{" in remote_ref
        or git.get("commit_is_ancestor_of_remote_tracking_ref") is not True
    ):
        raise SentimentReleaseError("candidate Git remote commitment가 올바르지 않습니다.")
    committer_time = _aware_iso_datetime(
        git.get("committer_time_iso"), "candidate committer 시각"
    )
    attested_at = _aware_iso_datetime(
        attestation.get("attested_at"), "candidate attestation 시각"
    )
    if attested_at > datetime.now(UTC) or committer_time > attested_at:
        raise SentimentReleaseError("candidate Git attestation 시각 순서가 올바르지 않습니다.")
    lock_commitment = _mapping(
        attestation.get("candidate_lock"), "candidate Git attestation lock"
    )
    if (
        lock_commitment.get("path") != "reports/sentiment-candidate-lock.json"
        or lock_commitment.get("bytes") != lock_size
        or lock_commitment.get("sha256") != lock_sha256
        or lock_commitment.get("bytes_equal_local_lock") is not True
    ):
        raise SentimentReleaseError("candidate Git attestation lock bytes가 다릅니다.")
    committed = _mapping(
        attestation.get("committed_artifact_manifests"),
        "candidate committed artifact manifests",
    )
    committed_reservations = _mapping(
        committed.get("sealed_reservations"), "committed sealed reservations"
    )
    lock_reservations = _mapping(lock.get("sealed_reservations"), "lock sealed reservations")
    if set(committed_reservations) != set(SUPPORTED_SOURCES):
        raise SentimentReleaseError("committed sealed reservation 구성이 다릅니다.")
    normalized_reservations: dict[str, dict[str, int | str]] = {}
    for source in SUPPORTED_SOURCES:
        normalized_reservations[source] = _require_same_manifest(
            committed_reservations.get(source),
            lock_reservations.get(source),
            f"{source} committed reservation",
        )
    committed_provenance = _mapping(
        committed.get("dataset_provenance"), "committed dataset provenance"
    )
    lock_provenance = _mapping(lock.get("dataset_provenance"), "lock dataset provenance")
    normalized_provenance: dict[str, Any] = {}
    for name in ("codebook", "sampling_implementation"):
        normalized_provenance[name] = _require_same_manifest(
            committed_provenance.get(name),
            lock_provenance.get(name),
            f"committed {name}",
        )
    committed_reports = _mapping(
        committed_provenance.get("dataset_reports"), "committed dataset reports"
    )
    lock_reports = _mapping(lock_provenance.get("dataset_reports"), "lock dataset reports")
    if set(committed_reports) != {"NEWS", "DISCLOSURE", "SAMPLING_DESIGN"}:
        raise SentimentReleaseError("committed dataset report 구성이 다릅니다.")
    normalized_reports: dict[str, dict[str, int | str]] = {}
    for name in ("NEWS", "DISCLOSURE", "SAMPLING_DESIGN"):
        normalized_reports[name] = _require_same_manifest(
            committed_reports.get(name),
            lock_reports.get(name),
            f"committed dataset report {name}",
        )
    code = _mapping(committed.get("code_provenance"), "committed code provenance")
    recipe = _mapping(lock.get("recipe"), "candidate lock recipe")
    committed_recipe_blobs = _mapping(
        committed.get("recipe_blobs"),
        "committed recipe blobs",
    )
    lock_recipe_blobs = _mapping(recipe.get("blobs"), "candidate lock recipe blobs")
    expected_recipe_paths = dict(RECIPE_RELATIVE_PATHS)
    if (
        set(committed_recipe_blobs) != set(expected_recipe_paths)
        or set(lock_recipe_blobs) != set(expected_recipe_paths)
    ):
        raise SentimentReleaseError("committed recipe blob 집합이 완전하지 않습니다.")
    normalized_recipe_blobs: dict[str, dict[str, int | str]] = {}
    for name, expected_path in expected_recipe_paths.items():
        normalized_recipe_blobs[name] = _require_same_manifest(
            committed_recipe_blobs.get(name),
            lock_recipe_blobs.get(name),
            f"committed recipe blob {name}",
        )
        if normalized_recipe_blobs[name]["path"] != expected_path:
            raise SentimentReleaseError(f"committed recipe blob 경로가 다릅니다: {name}")
    training_script = _mapping(code.get("training_script"), "committed training script")
    candidate_trainer = normalized_recipe_blobs["candidate_trainer"]
    historical_promoter = normalized_recipe_blobs["historical_auxiliary_promoter"]
    if (
        dict(training_script) != candidate_trainer
        or recipe.get("training_script") != candidate_trainer["path"]
        or recipe.get("training_script_sha256") != candidate_trainer["sha256"]
        or recipe.get("auxiliary_training_gold_promoter") != historical_promoter["path"]
        or recipe.get("auxiliary_training_gold_promoter_sha256")
        != historical_promoter["sha256"]
    ):
        raise SentimentReleaseError("committed recipe legacy commitment가 다릅니다.")
    lock_baselines = _mapping(
        lock.get("baseline_commitments"), "candidate lock baseline commitments"
    )
    committed_baselines = _mapping(
        committed.get("baseline_commitments"), "committed baseline commitments"
    )
    baseline_digest = baseline_commitments_sha256(lock_baselines)
    if (
        committed_baselines != lock_baselines
        or committed.get("baseline_commitments_sha256") != baseline_digest
        or lock.get("baseline_commitments_sha256") != baseline_digest
    ):
        raise SentimentReleaseError("baseline manifests가 Git attestation과 다릅니다.")
    lock_parity = _mapping(lock.get("runtime_parity"), "candidate lock runtime parity")
    committed_parity = _mapping(
        committed.get("runtime_parity"), "committed runtime parity"
    )
    if committed_parity != lock_parity:
        raise SentimentReleaseError("runtime parity lock이 Git attestation과 다릅니다.")
    parity_evidence = _require_same_manifest(
        committed.get("runtime_parity_evidence"),
        lock_parity.get("evidence"),
        "committed runtime parity evidence",
    )
    limitations = attestation.get("limitations")
    if (
        not isinstance(limitations, list)
        or tuple(limitations) != GIT_ATTESTATION_LIMITATIONS
    ):
        raise SentimentReleaseError("candidate Git attestation 한계가 명시되지 않았습니다.")
    return {
        "schema_version": GIT_ATTESTATION_SCHEMA_VERSION,
        "role": GIT_ATTESTATION_ROLE,
        "path": "reports/sentiment-candidate-git-attestation.json",
        "sha256": _file_sha256(attestation_path),
        "attested_at": attested_at.isoformat(),
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "committer_time_iso": committer_time.isoformat(),
        "remote_name": remote_name,
        "remote_tracking_ref": remote_ref,
        "candidate_lock_path": "reports/sentiment-candidate-lock.json",
        "candidate_lock_sha256": lock_sha256,
        "committed_artifact_manifests": {
            "sealed_reservations": normalized_reservations,
            "dataset_provenance": {
                **normalized_provenance,
                "dataset_reports": normalized_reports,
            },
            "code_provenance": {"training_script": dict(training_script)},
            "recipe_blobs": normalized_recipe_blobs,
            "baseline_commitments": lock_baselines,
            "baseline_commitments_sha256": baseline_digest,
            "runtime_parity": lock_parity,
            "runtime_parity_evidence": parity_evidence,
        },
        "limitations": list(GIT_ATTESTATION_LIMITATIONS),
    }


def _validate_gold_candidate_commitments(
    evidence_paths: dict[str, Path],
    *,
    candidate_lock_sha256: str,
    git_attestation_sha256: str,
    git_commit_sha: str,
) -> None:
    for source, gold_role, promotion_role in (
        ("NEWS", "sealed_gold_news", "gold_promotion_news"),
        ("DISCLOSURE", "sealed_gold_disclosure", "gold_promotion_disclosure"),
    ):
        promotion_report = _load_json(
            evidence_paths[promotion_role],
            f"{source} Gold promotion report",
        )
        provenance = _mapping(
            promotion_report.get("provenance"), f"{source} Gold promotion provenance"
        )
        codex_review = _mapping(
            provenance.get("codex_review"), f"{source} Gold Codex review provenance"
        )
        _require_gold_candidate_commitment(
            codex_review,
            description=f"{source} Gold promotion report",
            candidate_lock_sha256=candidate_lock_sha256,
            git_attestation_sha256=git_attestation_sha256,
            git_commit_sha=git_commit_sha,
        )

        raw = _read_regular_bytes(
            evidence_paths[gold_role], MAX_JSON_BYTES, f"{source} sealed Gold"
        )
        lines = [line for line in raw.splitlines() if line.strip()]
        if not lines:
            raise SentimentReleaseError(f"{source} sealed Gold가 비어 있습니다.")
        for index, line in enumerate(lines, start=1):
            row = _decode_json(line, f"{source} sealed Gold {index}행")
            if str(row.get("source_type", "")).upper() != source:
                raise SentimentReleaseError(
                    f"{source} sealed Gold {index}행의 source_type이 다릅니다."
                )
            _require_gold_candidate_commitment(
                row,
                description=f"{source} sealed Gold {index}행",
                candidate_lock_sha256=candidate_lock_sha256,
                git_attestation_sha256=git_attestation_sha256,
                git_commit_sha=git_commit_sha,
            )


def _require_gold_candidate_commitment(
    value: dict[str, Any],
    *,
    description: str,
    candidate_lock_sha256: str,
    git_attestation_sha256: str,
    git_commit_sha: str,
) -> None:
    if (
        value.get("candidate_manifest_sha256") != candidate_lock_sha256
        or value.get("candidate_git_attestation_sha256")
        != git_attestation_sha256
        or value.get("candidate_git_commit_sha") != git_commit_sha
    ):
        raise SentimentReleaseError(
            f"{description}의 candidate Git commitment가 release와 다릅니다."
        )


def _require_same_manifest(
    source: object,
    expected: object,
    description: str,
) -> dict[str, int | str]:
    source_manifest = _mapping(source, description)
    expected_manifest = _mapping(expected, f"{description} lock")
    normalized = {
        "path": expected_manifest.get("path"),
        "bytes": expected_manifest.get("bytes"),
        "sha256": expected_manifest.get("sha256"),
    }
    if source_manifest != normalized or not _is_sha256(normalized["sha256"]):
        raise SentimentReleaseError(f"{description}가 candidate lock과 다릅니다.")
    if (
        not isinstance(normalized["path"], str)
        or not normalized["path"]
        or isinstance(normalized["bytes"], bool)
        or not isinstance(normalized["bytes"], int)
        or normalized["bytes"] < 0
    ):
        raise SentimentReleaseError(f"{description} commitment가 올바르지 않습니다.")
    _safe_relative_path(normalized["path"], f"{description} 경로")
    return cast(dict[str, int | str], normalized)


def _git_object_id(value: object, description: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) not in {40, 64}
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise SentimentReleaseError(f"{description} 형식이 올바르지 않습니다.")
    return value


def _aware_iso_datetime(value: object, description: str) -> datetime:
    if not isinstance(value, str):
        raise SentimentReleaseError(f"{description} 형식이 올바르지 않습니다.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exception:
        raise SentimentReleaseError(f"{description} 형식이 올바르지 않습니다.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SentimentReleaseError(f"{description}에 시간대가 없습니다.")
    return parsed.astimezone(UTC)


def _validate_evidence_linkage(
    benchmark: dict[str, Any],
    lock: dict[str, Any],
    receipt: dict[str, Any],
    evidence_paths: dict[str, Path],
) -> None:
    sealed_gold = _mapping(receipt.get("sealed_gold"), "receipt sealed Gold")
    promotion = _mapping(receipt.get("promotion_reports"), "receipt promotion reports")
    reservations = _mapping(lock.get("sealed_reservations"), "lock sealed reservations")
    expected_roles = {
        "sealed_gold_news": _mapping(sealed_gold.get("NEWS"), "NEWS sealed Gold"),
        "sealed_gold_disclosure": _mapping(
            sealed_gold.get("DISCLOSURE"), "DISCLOSURE sealed Gold"
        ),
        "gold_promotion_news": _mapping(promotion.get("NEWS"), "NEWS promotion report"),
        "gold_promotion_disclosure": _mapping(
            promotion.get("DISCLOSURE"), "DISCLOSURE promotion report"
        ),
        "sampling_design": _mapping(
            receipt.get("sampling_design_report"), "sampling design"
        ),
        "reservation_news": _mapping(reservations.get("NEWS"), "NEWS reservation"),
        "reservation_disclosure": _mapping(
            reservations.get("DISCLOSURE"), "DISCLOSURE reservation"
        ),
    }
    baseline = _mapping(receipt.get("baseline_artifacts"), "baseline artifacts")
    expected_roles["tfidf_baseline"] = _mapping(
        baseline.get("hana_tfidf_logistic"), "TF-IDF baseline"
    )
    pre_k = _mapping(
        baseline.get("pre_k_fnspid_kf_deberta"), "pre-K-FNSPID baseline"
    )
    metadata_path = pre_k.get("artifact_dir")
    if not isinstance(metadata_path, str):
        raise SentimentReleaseError("pre-K-FNSPID artifact 경로가 없습니다.")
    expected_roles["pre_k_fnspid_metadata"] = {
        "path": f"{metadata_path}/hannah_metadata.json",
        "sha256": pre_k.get("metadata_sha256"),
    }
    expected_roles["pre_k_fnspid_training_report"] = {
        "path": pre_k.get("training_report_path"),
        "sha256": pre_k.get("training_report_sha256"),
    }
    sampling = _mapping(benchmark.get("sampling_design"), "benchmark sampling design")
    if (
        sampling.get("report_path") != expected_roles["sampling_design"].get("path")
        or sampling.get("report_sha256") != expected_roles["sampling_design"].get("sha256")
    ):
        raise SentimentReleaseError("benchmark와 sampling design 증거가 다릅니다.")
    for role, source_commitment in expected_roles.items():
        _safe_relative_path(source_commitment.get("path"), f"{role} 원본 경로")
        digest = source_commitment.get("sha256")
        if not _is_sha256(digest):
            raise SentimentReleaseError(f"{role} 원본 hash가 올바르지 않습니다.")
        if not hmac.compare_digest(_file_sha256(evidence_paths[role]), cast(str, digest)):
            raise SentimentReleaseError(f"{role} release 사본이 원본 증거와 다릅니다.")


def _directory_manifest(value: object, description: str) -> dict[str, dict[str, int | str]]:
    raw = _mapping(value, description)
    if not raw or len(raw) > MAX_RELEASE_FILES:
        raise SentimentReleaseError(f"{description}가 비었거나 너무 큽니다.")
    manifest: dict[str, dict[str, int | str]] = {}
    for relative_value, details in raw.items():
        relative = _safe_relative_path(relative_value, f"{description} 경로")
        commitment = _manifest_entry(details, f"{description}/{relative}")
        manifest[relative.as_posix()] = {
            "bytes": commitment["bytes"],
            "sha256": commitment["sha256"],
        }
    return manifest


def _verify_directory_tree(
    directory: Path,
    manifest: dict[str, dict[str, int | str]],
    description: str,
) -> None:
    actual: set[str] = set()
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise SentimentReleaseError(f"{description}에는 일반 파일만 허용됩니다: {path}")
        if path.is_dir():
            continue
        if not _is_regular_file(path):
            raise SentimentReleaseError(f"{description}에는 일반 파일만 허용됩니다: {path}")
        actual.add(path.relative_to(directory).as_posix())
    if actual != set(manifest):
        raise SentimentReleaseError(f"{description} 파일 트리가 manifest와 다릅니다.")
    for relative, commitment in manifest.items():
        path = _contained_regular_path(directory, Path(relative), f"{description}/{relative}")
        _verify_file_commitment(path, commitment, f"{description}/{relative}")


def _numbers_match(left: dict[str, float], right: dict[str, float]) -> bool:
    return all(
        math.isclose(left[name], right[name], rel_tol=0.0, abs_tol=1e-12) for name in left
    )


def _file_commitment(value: object, description: str) -> dict[str, int | str]:
    raw = _mapping(value, description)
    path = raw.get("path")
    size = raw.get("bytes")
    digest = raw.get("sha256")
    if (
        not isinstance(path, str)
        or isinstance(size, bool)
        or not isinstance(size, int)
        or size < 0
        or not _is_sha256(digest)
    ):
        raise SentimentReleaseError(f"{description} commitment가 올바르지 않습니다.")
    return {"path": path, "bytes": size, "sha256": cast(str, digest)}


def _manifest_entry(value: object, description: str) -> dict[str, int | str]:
    raw = _mapping(value, description)
    size = raw.get("bytes")
    digest = raw.get("sha256")
    if (
        set(raw) != {"bytes", "sha256"}
        or isinstance(size, bool)
        or not isinstance(size, int)
        or size < 0
        or not _is_sha256(digest)
    ):
        raise SentimentReleaseError(f"{description} manifest 항목이 올바르지 않습니다.")
    return {"bytes": size, "sha256": cast(str, digest)}


def _verify_file_commitment(
    path: Path,
    commitment: dict[str, int | str],
    description: str,
) -> None:
    size, digest = _file_identity(path)
    if size != commitment["bytes"] or not hmac.compare_digest(
        digest, cast(str, commitment["sha256"])
    ):
        raise SentimentReleaseError(f"{description} hash가 다릅니다.")


def _contained_regular_path(root: Path, relative: Path, description: str) -> Path:
    path = root / relative
    _reject_symlink_components(path, root)
    try:
        resolved = path.resolve(strict=True)
    except OSError as exception:
        raise SentimentReleaseError(f"{description} 파일이 없습니다.") from exception
    if resolved != path or not _is_regular_file(path):
        raise SentimentReleaseError(f"{description} 경로가 일반 파일이 아닙니다.")
    return path


def _contained_directory(root: Path, relative: Path, description: str) -> Path:
    path = root / relative
    _reject_symlink_components(path, root)
    if not path.is_dir() or path.is_symlink() or path.resolve() != path:
        raise SentimentReleaseError(f"{description} 경로가 실제 디렉터리가 아닙니다.")
    return path


def _safe_regular_path(path: Path, description: str) -> Path:
    absolute = Path(os.path.abspath(path))
    if absolute.is_symlink() or not _is_regular_file(absolute):
        raise SentimentReleaseError(f"{description} 경로가 일반 파일이 아닙니다.")
    return absolute


def _existing_directory(path: Path, description: str) -> Path:
    absolute = Path(os.path.abspath(path))
    if absolute.is_symlink() or not absolute.is_dir():
        raise SentimentReleaseError(f"{description} 경로가 실제 디렉터리가 아닙니다.")
    return absolute.resolve(strict=True)


def _reject_symlink_components(path: Path, root: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exception:
        raise SentimentReleaseError("release 경로가 허용된 root 밖입니다.") from exception
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise SentimentReleaseError(f"release 경로에 symlink가 있습니다: {current}")


def _safe_relative_path(value: object, description: str) -> Path:
    if not isinstance(value, str) or not value:
        raise SentimentReleaseError(f"{description}가 없습니다.")
    path = Path(value)
    if path.is_absolute() or path != Path(*path.parts) or ".." in path.parts or "." in path.parts:
        raise SentimentReleaseError(f"{description}가 안전한 상대경로가 아닙니다.")
    return path


def _release_id(value: object) -> str:
    if not isinstance(value, str) or RELEASE_ID_PATTERN.fullmatch(value) is None:
        raise SentimentReleaseError("release ID 형식이 올바르지 않습니다.")
    return value


def _load_json(path: Path, description: str) -> dict[str, Any]:
    return _decode_json(_read_regular_bytes(path, MAX_JSON_BYTES, description), description)


def _decode_json(payload: bytes, description: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exception:
        raise SentimentReleaseError(f"{description} JSON을 읽을 수 없습니다.") from exception
    if not isinstance(value, dict):
        raise SentimentReleaseError(f"{description}은 JSON 객체여야 합니다.")
    return cast(dict[str, Any], value)


def _read_regular_bytes(path: Path, maximum: int, description: str) -> bytes:
    descriptor = _open_regular_readonly(path)
    with os.fdopen(descriptor, "rb", closefd=True) as file:
        size = os.fstat(file.fileno()).st_size
        if size > maximum:
            raise SentimentReleaseError(f"{description} 크기가 허용 범위를 넘었습니다.")
        return file.read(maximum + 1)


def _file_identity(path: Path) -> tuple[int, str]:
    descriptor = _open_regular_readonly(path)
    digest = sha256()
    with os.fdopen(descriptor, "rb", closefd=True) as file:
        size = os.fstat(file.fileno()).st_size
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return size, digest.hexdigest()


def _file_sha256(path: Path) -> str:
    return _file_identity(path)[1]


def _open_regular_readonly(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exception:
        raise SentimentReleaseError(f"일반 파일을 안전하게 열 수 없습니다: {path}") from exception
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise SentimentReleaseError(f"일반 파일이 아닙니다: {path}")
    return descriptor


def _is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode)
    except OSError:
        return False


def _mapping(value: object, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SentimentReleaseError(f"{description}은 JSON 객체여야 합니다.")
    return cast(dict[str, Any], value)


def _finite_number(value: object, description: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SentimentReleaseError(f"{description} 값이 숫자가 아닙니다.")
    result = float(value)
    if not math.isfinite(result):
        raise SentimentReleaseError(f"{description} 값이 유한하지 않습니다.")
    return result


def _score(metrics: dict[str, Any], field: str) -> float:
    value = _finite_number(metrics.get(field), field)
    if not 0.0 <= value <= 1.0:
        raise SentimentReleaseError(f"{field} 점수가 0과 1 사이가 아닙니다.")
    return value


def _probability(value: object, description: str) -> float:
    probability = _finite_number(value, description)
    if not 0.0 <= probability <= 1.0:
        raise SentimentReleaseError(f"{description}이 0과 1 사이가 아닙니다.")
    return probability


def _sample_count(metrics: dict[str, Any], minimum: int) -> bool:
    value = metrics.get("sample_count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SentimentReleaseError("sample_count가 0 이상의 정수가 아닙니다.")
    return value >= minimum


def _canonical_json_sha256(value: object) -> str:
    return sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SentimentReleaseError(f"중복 JSON key는 허용하지 않습니다: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise SentimentReleaseError(f"비표준 JSON 숫자는 허용하지 않습니다: {value}")
