from __future__ import annotations

import hmac
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, cast

from hannah_montana_ai.services.source_hierarchical_sentiment import (
    ANCHOR_DOMAIN,
    DOMAIN_ORDER,
    HEAD_ARCHITECTURE_VERSION,
    HEAD_ARTIFACT_FILENAME,
    INPUT_FEATURE_VERSION,
    LABEL_ORDER,
    RESIDUAL_DOMAINS,
    DomainCalibration,
    SentimentDomain,
    validate_domain_calibration,
)

BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
BASE_MODEL_WEIGHT_FILENAME = "pytorch_model.bin"
BASE_MODEL_WEIGHT_SHA256 = "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
ARTIFACT_SCHEMA_VERSION = "kf-deberta-shared-residual-sentiment-artifact/v2"
ARTIFACT_MANIFEST_SCHEMA_VERSION = "kf-deberta-shared-residual-sentiment-manifest/v2"
TRAINING_SCHEMA_VERSION = "kf-deberta-shared-residual-sentiment-training/v2"
RUNTIME_LOADER_SCHEMA_VERSION = "kf-deberta-shared-residual-runtime-loader/v2"
BENCHMARK_SCHEMA_VERSION = "korean-finance-sentiment-benchmark/v5"
LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v2"
MODEL_FAMILY = "kf-deberta-shared-residual-hierarchical/v2"
CANDIDATE_MODEL = "kf_deberta_shared_residual_hierarchical_locked"

MAX_ARTIFACT_FILES = 512
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_ADAPTER_BYTES = 2 * 1024 * 1024 * 1024
MAX_HEAD_BYTES = 64 * 1024 * 1024
REQUIRED_ARTIFACT_FILES = frozenset(
    {
        "adapter/adapter_config.json",
        "adapter/adapter_model.safetensors",
        "hannah_metadata.json",
        HEAD_ARTIFACT_FILENAME,
        "tokenizer.json",
        "tokenizer_config.json",
    }
)
UNSAFE_ARTIFACT_SUFFIXES = frozenset(
    {".bin", ".ckpt", ".dylib", ".joblib", ".pickle", ".pkl", ".pt", ".pth", ".py", ".so"}
)
METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "version",
        "base_model",
        "base_model_revision",
        "base_source_kind",
        "label_order",
        "runtime_loader_contract",
        "prepared_partition_commitments",
        "selected_stage",
        "trained_at",
    }
)
ALLOWED_ARTIFACT_SUFFIXES = frozenset({".json", ".md", ".model", ".safetensors", ".txt"})
RUNTIME_FIELDS = frozenset(
    {
        "schema_version",
        "base_source",
        "adapter_path",
        "heads_path",
        "tokenizer_source",
        "domain_order",
        "domain_required",
        "unknown_domain_behavior",
        "pooling",
        "head_tensor_contract",
        "head_architecture",
        "composition",
        "calibration",
        "input_feature_version",
        "max_length",
    }
)
EXPECTED_COMPOSITION = {
    "NEGATIVE": "log_sigmoid(boundary)+log_softmax(direction)[0]",
    "NEUTRAL": "log_sigmoid(-boundary)",
    "POSITIVE": "log_sigmoid(boundary)+log_softmax(direction)[1]",
}
EXPECTED_HEAD_TENSOR_CONTRACT = {
    "shared": {
        "neutral_vs_directional": 1,
        "negative_vs_positive": 2,
    },
    "residual": {
        "neutral_vs_directional": 1,
        "negative_vs_positive": 2,
    },
}
EXPECTED_HEAD_ARCHITECTURE = {
    "version": HEAD_ARCHITECTURE_VERSION,
    "anchor_domain": ANCHOR_DOMAIN,
    "residual_domains": list(RESIDUAL_DOMAINS),
    "residual_initialization": "EXACT_ZERO",
    "known_untrained_domain_fallback": "SHARED_HEAD_ZERO_RESIDUAL",
    "unknown_domain_behavior": "FAIL_CLOSED",
}


class SentimentArtifactContractError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SourceHierarchicalArtifactContract:
    artifact_dir: Path
    version: str
    max_length: int
    base_source_kind: str
    base_source: dict[str, Any]
    calibration_by_domain: dict[SentimentDomain, DomainCalibration]
    metadata: dict[str, Any]
    manifest: dict[str, dict[str, int | str]]
    locked_manifest: dict[str, dict[str, int | str]]
    locked_manifest_sha256: str


def validate_source_hierarchical_artifact(
    artifact_dir: Path,
    training_report: Mapping[str, Any] | None = None,
) -> SourceHierarchicalArtifactContract:
    root = _regular_directory(artifact_dir, "v6 감성 artifact")
    manifest_path = _contained_regular_file(root, "manifest.json")
    manifest_document = _read_json_object(manifest_path, "v6 감성 artifact manifest")
    if (
        set(manifest_document)
        != {
            "schema_version",
            "status",
            "generated_at",
            "artifact_files",
            "safe_serialization_only",
            "symlinks_allowed",
            "overwrite_allowed",
        }
        or manifest_document.get("schema_version") != ARTIFACT_MANIFEST_SCHEMA_VERSION
        or manifest_document.get("status") != "ATOMIC_COMPLETE"
        or manifest_document.get("safe_serialization_only") is not True
        or manifest_document.get("symlinks_allowed") is not False
        or manifest_document.get("overwrite_allowed") is not False
        or not _timezone_datetime(manifest_document.get("generated_at"))
    ):
        raise SentimentArtifactContractError("v6 감성 artifact manifest 계약이 다릅니다.")

    declared_manifest = _validate_manifest_records(
        manifest_document.get("artifact_files"),
        "v6 감성 artifact manifest",
    )
    if not REQUIRED_ARTIFACT_FILES.issubset(declared_manifest):
        raise SentimentArtifactContractError("v6 감성 artifact 필수 파일이 없습니다.")
    if (
        cast(int, declared_manifest["adapter/adapter_model.safetensors"]["bytes"])
        > MAX_ADAPTER_BYTES
        or cast(
            int,
            declared_manifest[HEAD_ARTIFACT_FILENAME]["bytes"],
        )
        > MAX_HEAD_BYTES
    ):
        raise SentimentArtifactContractError("v6 감성 tensor artifact 크기 제한을 초과했습니다.")
    _verify_directory_tree(root, declared_manifest)

    metadata = _read_json_object(
        _contained_regular_file(root, "hannah_metadata.json"),
        "v6 감성 metadata",
    )
    runtime = _validate_metadata(metadata)
    _validate_adapter_config(
        _read_json_object(
            _contained_regular_file(root, "adapter/adapter_config.json"),
            "v6 감성 LoRA config",
        )
    )
    calibration = validate_domain_calibration(runtime["calibration"])
    base_source = _mapping(runtime["base_source"], "v6 base source provenance")
    _validate_base_source(metadata["base_source_kind"], base_source)

    if training_report is not None:
        _validate_training_report(
            training_report,
            metadata=metadata,
            runtime=runtime,
            artifact_manifest=declared_manifest,
        )

    locked_manifest = dict(declared_manifest)
    locked_manifest["manifest.json"] = _file_record(manifest_path)
    return SourceHierarchicalArtifactContract(
        artifact_dir=root,
        version=cast(str, metadata["version"]),
        max_length=cast(int, runtime["max_length"]),
        base_source_kind=cast(str, metadata["base_source_kind"]),
        base_source=base_source,
        calibration_by_domain=calibration,
        metadata=metadata,
        manifest=declared_manifest,
        locked_manifest=locked_manifest,
        locked_manifest_sha256=canonical_manifest_sha256(locked_manifest),
    )


def validate_source_hierarchical_activation(
    benchmark_report: Mapping[str, Any],
    contract: SourceHierarchicalArtifactContract,
) -> None:
    gate = _mapping(benchmark_report.get("deployment_gate"), "v6 deployment gate")
    candidate_lock = _mapping(benchmark_report.get("candidate_lock"), "v6 candidate lock")
    source_gold = _mapping(
        benchmark_report.get("source_sealed_gold"),
        "v6 source sealed gold",
    )
    if (
        benchmark_report.get("schema_version") != BENCHMARK_SCHEMA_VERSION
        or benchmark_report.get("input_feature_version") != INPUT_FEATURE_VERSION
        or gate.get("eligible") is not True
        or gate.get("candidate_model") != CANDIDATE_MODEL
        or gate.get("candidate_model_family") != MODEL_FAMILY
        or gate.get("candidate_version") != contract.version
        or candidate_lock.get("schema_version") != LOCK_SCHEMA_VERSION
        or candidate_lock.get("selection_only") is not True
    ):
        raise SentimentArtifactContractError("v6 감성 활성화 gate 계약이 다릅니다.")

    locked_version = _candidate_lock_value(candidate_lock, "version")
    locked_family = _candidate_lock_value(candidate_lock, "model_family")
    locked_manifest = _validate_manifest_records(
        _candidate_lock_value(candidate_lock, "artifact_files"),
        "v6 candidate lock artifact",
    )
    declared_lock_hash = _candidate_lock_value(candidate_lock, "artifact_manifest_sha256")
    gate_hash = gate.get("candidate_artifact_manifest_sha256")
    if (
        locked_version != contract.version
        or locked_family != MODEL_FAMILY
        or locked_manifest != contract.locked_manifest
        or not isinstance(declared_lock_hash, str)
        or not isinstance(gate_hash, str)
        or not hmac.compare_digest(contract.locked_manifest_sha256, declared_lock_hash)
        or not hmac.compare_digest(contract.locked_manifest_sha256, gate_hash)
    ):
        raise SentimentArtifactContractError("v6 감성 candidate lock 연결이 다릅니다.")
    for source in ("NEWS", "DISCLOSURE"):
        _validate_source_gate(source_gold.get(source), source)


def validate_source_hierarchical_base_directory(base_model_dir: Path) -> Path:
    root = _regular_directory(base_model_dir, "v6 감성 base model")
    found_config = False
    found_safetensors = False
    file_count = 0
    total_bytes = 0
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SentimentArtifactContractError("v6 감성 base model에 symlink가 있습니다.")
        if not path.is_file():
            continue
        file_count += 1
        total_bytes += path.stat().st_size
        relative = path.relative_to(root).as_posix()
        if Path(relative).suffix.casefold() in UNSAFE_ARTIFACT_SUFFIXES:
            raise SentimentArtifactContractError("v6 감성 base model에 unsafe 파일이 있습니다.")
        found_config = found_config or relative == "config.json"
        found_safetensors = found_safetensors or relative.endswith(".safetensors")
    if (
        not found_config
        or not found_safetensors
        or file_count > MAX_ARTIFACT_FILES
        or total_bytes > MAX_ARTIFACT_BYTES
    ):
        raise SentimentArtifactContractError("v6 감성 base model 파일 계약이 다릅니다.")
    return root


def canonical_manifest_sha256(manifest: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        manifest,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def _validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if (
        set(metadata) != METADATA_FIELDS
        or metadata.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or metadata.get("base_model") != BASE_MODEL
        or metadata.get("base_model_revision") != BASE_MODEL_REVISION
        or metadata.get("label_order") != list(LABEL_ORDER)
        or metadata.get("base_source_kind") not in {"PINNED_RAW", "DAPT_MERGED_FP32"}
        or metadata.get("selected_stage")
        not in {"STAGE1_DOMAIN_BALANCED_FULL", "STAGE2_GOLD_CLEAN_HEADS_ONLY"}
        or not _timezone_datetime(metadata.get("trained_at"))
        or not _version(metadata.get("version"))
    ):
        raise SentimentArtifactContractError("v6 감성 metadata 계약이 다릅니다.")
    _validate_partition_commitments(metadata.get("prepared_partition_commitments"))
    runtime = _mapping(metadata.get("runtime_loader_contract"), "v6 runtime loader")
    max_length = runtime.get("max_length")
    if (
        set(runtime) != RUNTIME_FIELDS
        or runtime.get("schema_version") != RUNTIME_LOADER_SCHEMA_VERSION
        or runtime.get("adapter_path") != "adapter"
        or runtime.get("heads_path") != HEAD_ARTIFACT_FILENAME
        or runtime.get("tokenizer_source") != "artifact-root"
        or runtime.get("domain_order") != list(DOMAIN_ORDER)
        or runtime.get("domain_required") is not True
        or runtime.get("unknown_domain_behavior") != "FAIL_CLOSED"
        or runtime.get("pooling") != "last_hidden_state_cls"
        or runtime.get("head_tensor_contract") != EXPECTED_HEAD_TENSOR_CONTRACT
        or runtime.get("head_architecture") != EXPECTED_HEAD_ARCHITECTURE
        or runtime.get("composition") != EXPECTED_COMPOSITION
        or runtime.get("input_feature_version") != INPUT_FEATURE_VERSION
        or isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not 16 <= max_length <= 512
    ):
        raise SentimentArtifactContractError("v6 감성 runtime loader 계약이 다릅니다.")
    validate_domain_calibration(runtime.get("calibration"))
    return runtime


def _validate_training_report(
    training_report: Mapping[str, Any],
    *,
    metadata: Mapping[str, Any],
    runtime: Mapping[str, Any],
    artifact_manifest: Mapping[str, Any],
) -> None:
    if (
        training_report.get("schema_version") != TRAINING_SCHEMA_VERSION
        or training_report.get("version") != metadata.get("version")
        or training_report.get("base_model") != BASE_MODEL
        or training_report.get("base_model_revision") != BASE_MODEL_REVISION
        or training_report.get("base_source_kind") != metadata.get("base_source_kind")
        or training_report.get("label_order") != list(LABEL_ORDER)
        or training_report.get("runtime_loader_contract") != runtime
        or training_report.get("prepared_partition_commitments")
        != metadata.get("prepared_partition_commitments")
        or training_report.get("selected_stage") != metadata.get("selected_stage")
        or training_report.get("base_source") != runtime.get("base_source")
        or training_report.get("artifact_files") != artifact_manifest
        or training_report.get("public_test_opened") is not False
        or training_report.get("confirmatory_labels_opened") is not False
    ):
        raise SentimentArtifactContractError("v6 감성 training report 연결이 다릅니다.")


def _validate_adapter_config(config: Mapping[str, Any]) -> None:
    layers = config.get("layers_to_transform")
    modules_to_save = config.get("modules_to_save")
    target_modules = config.get("target_modules")
    if (
        str(config.get("peft_type", "")).upper() != "LORA"
        or str(config.get("task_type", "")).upper() != "FEATURE_EXTRACTION"
        or config.get("inference_mode") is not True
        or config.get("r") != 16
        or config.get("lora_alpha") != 32
        or not _numbers_equal(config.get("lora_dropout"), 0.08)
        or not isinstance(target_modules, list)
        or not all(isinstance(module, str) for module in target_modules)
        or set(target_modules) != {"query_proj", "key_proj", "value_proj", "dense"}
        or not isinstance(layers, list)
        or layers != list(range(12))
        or config.get("layers_pattern") != "layer"
        or modules_to_save not in (None, [])
        or config.get("auto_mapping") is not None
    ):
        raise SentimentArtifactContractError("v6 감성 LoRA config 계약이 다릅니다.")


def _validate_base_source(kind: object, value: Mapping[str, Any]) -> None:
    if kind == "PINNED_RAW":
        if (
            value.get("repository") != BASE_MODEL
            or value.get("revision") != BASE_MODEL_REVISION
            or value.get("source_weight_filename") != BASE_MODEL_WEIGHT_FILENAME
            or value.get("source_weight_sha256") != BASE_MODEL_WEIGHT_SHA256
            or value.get("weights_only") is not True
            or value.get("trust_remote_code") is not False
        ):
            raise SentimentArtifactContractError("v6 감성 pinned base provenance가 다릅니다.")
        return
    if kind == "DAPT_MERGED_FP32":
        expected_fields = {
            "schema_version",
            "artifact_manifest",
            "merged_fp32_artifact_files",
            "training_report",
            "prepared_manifest",
            "pilot_report",
            "inventory_oracle",
            "pack_oracle",
            "base_model",
            "base_revision",
            "precision",
            "validation_nll",
        }
        manifest = _mapping(value.get("artifact_manifest"), "v6 DAPT manifest provenance")
        merged_files = _mapping(
            value.get("merged_fp32_artifact_files"),
            "v6 DAPT merged artifact provenance",
        )
        training_report = _mapping(value.get("training_report"), "v6 DAPT training report")
        prepared_manifest = _mapping(value.get("prepared_manifest"), "v6 DAPT prepared manifest")
        pilot_report = _mapping(value.get("pilot_report"), "v6 DAPT pilot report")
        inventory_oracle = _mapping(value.get("inventory_oracle"), "v6 DAPT inventory oracle")
        pack_oracle = _mapping(value.get("pack_oracle"), "v6 DAPT pack oracle")
        validation_nll = _mapping(value.get("validation_nll"), "v6 DAPT validation NLL")
        frozen_nll = validation_nll.get("frozen_base")
        final_nll = validation_nll.get("end_of_epoch")
        if (
            set(value) != expected_fields
            or value.get("schema_version") != "kf-deberta-dapt-base-source/v2"
            or value.get("base_model") != BASE_MODEL
            or value.get("base_revision") != BASE_MODEL_REVISION
            or not _regular_record(manifest, require_path=True)
            or set(merged_files)
            != {"merged_fp32/config.json", "merged_fp32/model.safetensors"}
            or not all(
                _regular_record(_mapping(record, "v6 DAPT merged file"), require_path=False)
                for record in merged_files.values()
            )
            or not _regular_record(training_report, require_path=False)
            or not _regular_record(prepared_manifest, require_path=True)
            or not _regular_record(pilot_report, require_path=True)
            or inventory_oracle.get("status") != "LOCKED"
            or pack_oracle.get("status") != "LOCKED"
            or not isinstance(inventory_oracle.get("candidate_sha256"), str)
            or not isinstance(pack_oracle.get("candidate_sha256"), str)
            or value.get("precision") != "FP32"
            or set(validation_nll) != {"frozen_base", "end_of_epoch"}
            or isinstance(frozen_nll, bool)
            or not isinstance(frozen_nll, (int, float))
            or isinstance(final_nll, bool)
            or not isinstance(final_nll, (int, float))
            or not math.isfinite(float(frozen_nll))
            or not math.isfinite(float(final_nll))
            or float(final_nll) >= float(frozen_nll)
        ):
            raise SentimentArtifactContractError("v6 감성 DAPT base provenance가 다릅니다.")
        return
    raise SentimentArtifactContractError("지원하지 않는 v6 감성 base source입니다.")


def _validate_partition_commitments(value: object) -> None:
    commitments = _mapping(value, "v6 partition commitment")
    required = {
        "TRAIN",
        "CHECKPOINT",
        "CALIBRATION",
        "SELECTION",
        "NEWS_CONFIRMATORY_RESERVATION",
        "DISCLOSURE_CONFIRMATORY_RESERVATION",
    }
    if set(commitments) != required:
        raise SentimentArtifactContractError("v6 partition commitment 집합이 다릅니다.")
    for name, record in commitments.items():
        details = _mapping(record, f"v6 partition commitment/{name}")
        if not _regular_record(details, require_path=False, count_key="row_count"):
            raise SentimentArtifactContractError("v6 partition commitment가 올바르지 않습니다.")


def _validate_source_gate(value: object, source: str) -> None:
    metrics = _mapping(value, f"v6 {source} sealed gold")
    sample_count = metrics.get("sample_count")
    accuracy = _score(metrics.get("accuracy"))
    macro_f1 = _score(metrics.get("macro_f1"))
    if (
        isinstance(sample_count, bool)
        or not isinstance(sample_count, int)
        or sample_count < 500
        or accuracy is None
        or macro_f1 is None
        or accuracy < 0.90
        or macro_f1 < 0.85
    ):
        raise SentimentArtifactContractError(f"v6 {source} sealed gold gate가 부족합니다.")


def _validate_manifest_records(
    value: object,
    description: str,
) -> dict[str, dict[str, int | str]]:
    raw = _mapping(value, description)
    if not raw or len(raw) > MAX_ARTIFACT_FILES:
        raise SentimentArtifactContractError(f"{description} 파일 수가 올바르지 않습니다.")
    result: dict[str, dict[str, int | str]] = {}
    total_bytes = 0
    for name, record in raw.items():
        if not isinstance(name, str):
            raise SentimentArtifactContractError(f"{description} 경로가 문자열이 아닙니다.")
        relative = _safe_relative_path(name, description)
        details = _mapping(record, f"{description}/{name}")
        if set(details) != {"bytes", "sha256"} or not _regular_record(details):
            raise SentimentArtifactContractError(f"{description}/{name} record가 다릅니다.")
        total_bytes += cast(int, details["bytes"])
        if total_bytes > MAX_ARTIFACT_BYTES:
            raise SentimentArtifactContractError(f"{description} 크기 제한을 초과했습니다.")
        result[relative.as_posix()] = {
            "bytes": cast(int, details["bytes"]),
            "sha256": cast(str, details["sha256"]),
        }
    return result


def _verify_directory_tree(
    root: Path,
    manifest: Mapping[str, Mapping[str, Any]],
) -> None:
    actual: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SentimentArtifactContractError("v6 감성 artifact에 symlink가 있습니다.")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    if actual != {*manifest, "manifest.json"}:
        raise SentimentArtifactContractError("v6 감성 artifact 파일 트리가 다릅니다.")
    for relative, expected in manifest.items():
        path = _contained_regular_file(root, relative)
        suffix = Path(relative).suffix.casefold()
        if suffix in UNSAFE_ARTIFACT_SUFFIXES or suffix not in ALLOWED_ARTIFACT_SUFFIXES:
            raise SentimentArtifactContractError("v6 감성 artifact에 unsafe 파일이 있습니다.")
        actual_record = _file_record(path)
        if actual_record != expected:
            raise SentimentArtifactContractError(f"v6 감성 artifact hash가 다릅니다: {relative}")


def _regular_directory(path: Path, description: str) -> Path:
    if _has_symlink_component(path) or not path.is_dir():
        raise SentimentArtifactContractError(f"{description} 디렉터리가 올바르지 않습니다.")
    try:
        return path.resolve(strict=True)
    except OSError as exception:
        raise SentimentArtifactContractError(
            f"{description} 경로를 확인할 수 없습니다."
        ) from exception


def _has_symlink_component(path: Path) -> bool:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _contained_regular_file(root: Path, relative: str) -> Path:
    safe_relative = _safe_relative_path(relative, "v6 artifact 경로")
    current = root
    for part in safe_relative.parts:
        current = current / part
        if current.is_symlink():
            raise SentimentArtifactContractError("v6 artifact 경로에 symlink가 있습니다.")
    if not current.is_file():
        raise SentimentArtifactContractError(f"v6 artifact 파일이 없습니다: {relative}")
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exception:
        raise SentimentArtifactContractError(
            "v6 artifact 경로가 root 밖을 가리킵니다."
        ) from exception
    return resolved


def _safe_relative_path(value: str, description: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or len(value) > 512
        or "\\" in value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise SentimentArtifactContractError(f"{description} 상대 경로가 올바르지 않습니다.")
    return path


def _file_record(path: Path) -> dict[str, int | str]:
    digest = sha256()
    try:
        with path.open("rb") as file:
            while chunk := file.read(1024 * 1024):
                digest.update(chunk)
    except OSError as exception:
        raise SentimentArtifactContractError(
            "v6 artifact hash를 계산할 수 없습니다."
        ) from exception
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def _read_json_object(path: Path, description: str) -> dict[str, Any]:
    if path.stat().st_size > MAX_JSON_BYTES:
        raise SentimentArtifactContractError(f"{description} 크기 제한을 초과했습니다.")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, UnicodeDecodeError, ValueError) as exception:
        raise SentimentArtifactContractError(
            f"{description} JSON이 올바르지 않습니다."
        ) from exception
    return _mapping(value, description)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"중복 JSON key는 허용하지 않습니다: {key}")
        result[key] = value
    return result


def _mapping(value: object, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SentimentArtifactContractError(f"{description} 객체가 올바르지 않습니다.")
    return value


def _candidate_lock_value(candidate_lock: Mapping[str, Any], name: str) -> object:
    if name in candidate_lock:
        return candidate_lock[name]
    winner = candidate_lock.get("winner")
    return winner.get(name) if isinstance(winner, Mapping) else None


def _regular_record(
    value: Mapping[str, Any],
    *,
    require_path: bool = False,
    count_key: str = "bytes",
) -> bool:
    count = value.get(count_key)
    digest = value.get("sha256")
    path_valid = not require_path or (
        isinstance(value.get("path"), str) and bool(cast(str, value["path"]).strip())
    )
    return (
        not isinstance(count, bool)
        and isinstance(count, int)
        and count >= 0
        and _is_sha256(digest)
        and path_valid
    )


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _version(value: object) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= 240
        and all(character.isalnum() or character in "._-" for character in value)
    )


def _timezone_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _numbers_equal(value: object, expected: float) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, int | float)
        and math.isfinite(float(value))
        and math.isclose(float(value), expected, rel_tol=0.0, abs_tol=1e-12)
    )


def _score(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    score = float(value)
    return score if math.isfinite(score) and 0.0 <= score <= 1.0 else None
