from __future__ import annotations

import hmac
import json
from collections.abc import Mapping
from dataclasses import dataclass
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
    SourceHierarchicalSentimentRuntime,
    build_source_hierarchical_classifier,
    load_source_hierarchical_heads,
    validate_domain_calibration,
)

BASE_MODEL = "snunlp/KR-FinBert-SC"
BASE_MODEL_REVISION = "36b3d36898bc9925ca58c3508b1048e4449f1370"
BASE_MODEL_FILES_SHA256 = {
    "config.json": "cb7c00d3e6dfe46beacec2e0c7b98bfa519bed9949093fc06086f961e0020544",
    "model.safetensors": "fc073b39aa12271fc67c878de86e150a021f07a426e3e7e42705511d35e27b9a",
    "special_tokens_map.json": (
        "303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3"
    ),
    "tokenizer.json": "896789eab76ff9b984d5a91342ca7bf58adf14cfe9027da888a0c228078d7dcf",
    "tokenizer_config.json": (
        "5d5692ce35199e06e258b858a5741807c2c9b0555b93cc352d72fe5b72e3873e"
    ),
    "vocab.txt": "a6fb3bad008ed486cf553d7585251a6cb0d72be8fd88386f3646c592876d195c",
}

ARTIFACT_SCHEMA_VERSION = "k-fnspid-v6-fair-shared-residual-baseline-artifact/v2"
MANIFEST_SCHEMA_VERSION = (
    "kr-finbert-sc-shared-residual-sentiment-artifact-manifest/v2"
)
RUNTIME_SCHEMA_VERSION = "kr-finbert-sc-shared-residual-runtime-loader/v2"
MODEL_FAMILY = "kr-finbert-sc-shared-residual-same-data-schedule/v2"
MAX_ARTIFACT_FILES = 128
MAX_ARTIFACT_BYTES = 2 * 1024 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024
UNSAFE_SUFFIXES = frozenset(
    {".bin", ".ckpt", ".joblib", ".pickle", ".pkl", ".pt", ".pth"}
)
ALLOWED_SUFFIXES = frozenset({".json", ".safetensors", ".txt"})
REQUIRED_FILES = frozenset(
    {
        "encoder/config.json",
        "encoder/model.safetensors",
        "hannah_metadata.json",
        "manifest.json",
        HEAD_ARTIFACT_FILENAME,
        "tokenizer.json",
        "tokenizer_config.json",
    }
)


class KrFinBertBaselineArtifactError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class KrFinBertBaselineArtifact:
    artifact_dir: Path
    version: str
    max_length: int
    calibration_by_domain: dict[SentimentDomain, DomainCalibration]
    prepared_partition_commitments: dict[str, Any]
    candidate_matching_contract: dict[str, Any]
    artifact_manifest_sha256: str


def validate_kr_finbert_sc_v6_artifact(
    artifact_dir: Path,
) -> KrFinBertBaselineArtifact:
    root = _regular_directory(artifact_dir, "KR-FinBERT-SC v6 artifact")
    actual_files = _verify_tree(root)
    if not REQUIRED_FILES.issubset(actual_files):
        missing = ", ".join(sorted(REQUIRED_FILES - actual_files))
        raise KrFinBertBaselineArtifactError(
            f"기준선 artifact 필수 파일이 없습니다: {missing}"
        )

    manifest = _read_json(root / "manifest.json", "기준선 artifact manifest")
    if (
        set(manifest)
        != {
            "schema_version",
            "status",
            "generated_at",
            "artifact_files",
            "artifact_manifest_sha256",
            "safe_serialization_only",
            "symlinks_allowed",
            "overwrite_allowed",
        }
        or manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION
        or manifest.get("status") != "ATOMIC_COMPLETE"
        or manifest.get("safe_serialization_only") is not True
        or manifest.get("symlinks_allowed") is not False
        or manifest.get("overwrite_allowed") is not False
    ):
        raise KrFinBertBaselineArtifactError("기준선 artifact manifest 계약이 다릅니다.")
    declared_files = _manifest_records(manifest.get("artifact_files"))
    expected_paths = set(actual_files) - {"manifest.json"}
    if set(declared_files) != expected_paths:
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact manifest 파일 집합이 다릅니다."
        )
    for relative, record in declared_files.items():
        if _file_record(root / relative) != record:
            raise KrFinBertBaselineArtifactError(
                f"기준선 artifact 파일 commitment가 다릅니다: {relative}"
            )
    manifest_digest = _canonical_sha256(declared_files)
    if not hmac.compare_digest(
        str(manifest.get("artifact_manifest_sha256", "")),
        manifest_digest,
    ):
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact manifest digest가 다릅니다."
        )

    metadata = _read_json(root / "hannah_metadata.json", "기준선 artifact metadata")
    runtime = metadata.get("runtime_loader_contract")
    commitments = metadata.get("prepared_partition_commitments")
    matching = metadata.get("candidate_matching_contract")
    if (
        metadata.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or metadata.get("model_family") != MODEL_FAMILY
        or metadata.get("base_model") != BASE_MODEL
        or metadata.get("base_model_revision") != BASE_MODEL_REVISION
        or metadata.get("label_order") != list(LABEL_ORDER)
        or not isinstance(commitments, dict)
        or not isinstance(matching, dict)
        or not isinstance(runtime, dict)
    ):
        raise KrFinBertBaselineArtifactError("기준선 artifact metadata 계약이 다릅니다.")
    planned_steps = matching.get("planned_optimizer_steps")
    executed_steps = matching.get("executed_optimizer_steps")
    matching_semantics = matching.get("matching_semantics")
    expected_schedule = {
        "stage1_epochs": 2,
        "stage2_epochs": 4,
        "batch_size": 8,
        "eval_batch_size": 16,
        "gradient_accumulation_steps": 2,
        "optimizer": "AdamW",
        "scheduler": "cosine-with-8pct-warmup",
        "checkpoint_and_stopping_rule": (
            "fixed-full-epoch; best-in-stage-checkpoint-selected"
        ),
    }
    expected_semantics = {
        "same_raw_source_rows": True,
        "same_group_disjoint_partitions": True,
        "same_data_selection_seed": True,
        "same_model_seed_set": True,
        "same_target_aware_input": True,
        "same_source_hierarchical_task_loss_calibration_selection": True,
        "same_schedule_implementation_and_configured_rule": True,
        "planned_equals_executed_optimizer_steps": True,
    }
    configured_schedule = matching.get("configured_schedule")
    if not isinstance(configured_schedule, dict):
        raise KrFinBertBaselineArtifactError(
            "기준선 configured schedule 계약이 없습니다."
        )
    gradient_checkpointing = configured_schedule.get("gradient_checkpointing")
    configured_schedule_without_gradient = {
        key: value
        for key, value in configured_schedule.items()
        if key != "gradient_checkpointing"
    }
    if (
        matching.get("schema_version")
        != "kr-finbert-sc-v6-candidate-matching-contract/v1"
        or matching.get("prepared_partition_commitments") != commitments
        or not _is_sha256(matching.get("input_artifacts_sha256"))
        or not isinstance(gradient_checkpointing, bool)
        or configured_schedule_without_gradient != expected_schedule
        or not isinstance(planned_steps, dict)
        or not isinstance(executed_steps, dict)
        or planned_steps != executed_steps
        or set(planned_steps) != {"stage1", "stage2", "total"}
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in planned_steps.values()
        )
        or planned_steps["total"]
        != planned_steps["stage1"] + planned_steps["stage2"]
        or matching_semantics != expected_semantics
    ):
        raise KrFinBertBaselineArtifactError(
            "기준선 candidate matching 계약이 다릅니다."
        )
    if (
        runtime.get("schema_version") != RUNTIME_SCHEMA_VERSION
        or runtime.get("encoder_path") != "encoder"
        or runtime.get("heads_path") != HEAD_ARTIFACT_FILENAME
        or runtime.get("tokenizer_source") != "artifact-root"
        or runtime.get("input_feature_version") != INPUT_FEATURE_VERSION
        or runtime.get("domain_order") != list(DOMAIN_ORDER)
        or runtime.get("label_order") != list(LABEL_ORDER)
        or runtime.get("domain_required") is not True
        or runtime.get("unknown_domain_behavior") != "FAIL_CLOSED"
        or runtime.get("head_architecture")
        != {
            "version": HEAD_ARCHITECTURE_VERSION,
            "anchor_domain": ANCHOR_DOMAIN,
            "residual_domains": list(RESIDUAL_DOMAINS),
            "residual_initialization": "EXACT_ZERO",
            "known_untrained_domain_fallback": "SHARED_HEAD_ZERO_RESIDUAL",
            "unknown_domain_behavior": "FAIL_CLOSED",
        }
    ):
        raise KrFinBertBaselineArtifactError(
            "기준선 runtime loader 계약이 다릅니다."
        )
    max_length = runtime.get("max_length")
    if (
        isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not 16 <= max_length <= 512
    ):
        raise KrFinBertBaselineArtifactError(
            "기준선 runtime max_length가 올바르지 않습니다."
        )
    try:
        calibration = validate_domain_calibration(runtime.get("calibration"))
    except (TypeError, ValueError) as exception:
        raise KrFinBertBaselineArtifactError(
            "기준선 calibration 계약이 다릅니다."
        ) from exception
    version = metadata.get("version")
    if not isinstance(version, str) or not version.strip():
        raise KrFinBertBaselineArtifactError("기준선 artifact version이 없습니다.")
    return KrFinBertBaselineArtifact(
        artifact_dir=root,
        version=version,
        max_length=max_length,
        calibration_by_domain=calibration,
        prepared_partition_commitments=cast(dict[str, Any], commitments),
        candidate_matching_contract=cast(dict[str, Any], matching),
        artifact_manifest_sha256=manifest_digest,
    )


def load_kr_finbert_sc_v6_runtime(
    artifact_dir: Path,
) -> SourceHierarchicalSentimentRuntime:
    contract = validate_kr_finbert_sc_v6_artifact(artifact_dir)
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
            contract.artifact_dir,
            revision="local-verified-kr-finbert-sc-v6-baseline",
            local_files_only=True,
            trust_remote_code=False,
        )
        encoder = AutoModel.from_pretrained(  # nosec B615
            contract.artifact_dir / "encoder",
            revision="local-verified-kr-finbert-sc-v6-baseline",
            local_files_only=True,
            trust_remote_code=False,
            use_safetensors=True,
            weights_only=True,
        )
        hidden_size = int(cast(Any, encoder.config).hidden_size)
        model = build_source_hierarchical_classifier(encoder, hidden_size)
        load_source_hierarchical_heads(
            model,
            contract.artifact_dir / HEAD_ARTIFACT_FILENAME,
        )
        model.to(torch.device("cpu"))
        model.eval()
    except KrFinBertBaselineArtifactError:
        raise
    except Exception as exception:
        raise KrFinBertBaselineArtifactError(
            "KR-FinBERT-SC v6 기준선 runtime을 안전하게 load할 수 없습니다."
        ) from exception
    return SourceHierarchicalSentimentRuntime(
        model=model,
        tokenizer=tokenizer,
        torch_module=torch,
        max_length=contract.max_length,
        calibration_by_domain=contract.calibration_by_domain,
    )


def _verify_tree(root: Path) -> set[str]:
    files: set[str] = set()
    total_bytes = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise KrFinBertBaselineArtifactError(
                "기준선 artifact에 symlink를 허용하지 않습니다."
            )
        if path.is_dir():
            continue
        if not path.is_file():
            raise KrFinBertBaselineArtifactError(
                "기준선 artifact에 일반 파일이 아닌 항목이 있습니다."
            )
        relative = path.relative_to(root).as_posix()
        _safe_relative_path(relative)
        suffix = path.suffix.casefold()
        if suffix in UNSAFE_SUFFIXES or suffix not in ALLOWED_SUFFIXES:
            raise KrFinBertBaselineArtifactError(
                f"기준선 artifact에 허용되지 않은 파일이 있습니다: {relative}"
            )
        if suffix == ".json" and path.stat().st_size > MAX_JSON_BYTES:
            raise KrFinBertBaselineArtifactError(
                "기준선 artifact JSON 크기 제한을 초과했습니다."
            )
        total_bytes += path.stat().st_size
        files.add(relative)
    if len(files) > MAX_ARTIFACT_FILES or total_bytes > MAX_ARTIFACT_BYTES:
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact 전체 제한을 초과했습니다."
        )
    return files


def _regular_directory(path: Path, description: str) -> Path:
    absolute = path.absolute()
    if any(component.is_symlink() for component in (absolute, *absolute.parents)):
        raise KrFinBertBaselineArtifactError(f"{description} 경로에 symlink가 있습니다.")
    if not path.is_dir():
        raise KrFinBertBaselineArtifactError(
            f"{description} 경로가 일반 디렉터리가 아닙니다."
        )
    return path.resolve(strict=True)


def _safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact 상대 경로가 안전하지 않습니다."
        )
    return path


def _manifest_records(value: object) -> dict[str, dict[str, int | str]]:
    if not isinstance(value, dict) or len(value) > MAX_ARTIFACT_FILES:
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact manifest record가 잘못되었습니다."
        )
    result: dict[str, dict[str, int | str]] = {}
    for raw_path, raw_record in value.items():
        if not isinstance(raw_path, str) or not isinstance(raw_record, dict):
            raise KrFinBertBaselineArtifactError(
                "기준선 artifact manifest 항목이 잘못되었습니다."
            )
        relative = _safe_relative_path(raw_path).as_posix()
        if set(raw_record) != {"bytes", "sha256"}:
            raise KrFinBertBaselineArtifactError(
                "기준선 artifact manifest 필드가 잘못되었습니다."
            )
        size = raw_record.get("bytes")
        digest = raw_record.get("sha256")
        if (
            isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
            or not _is_sha256(digest)
        ):
            raise KrFinBertBaselineArtifactError(
                "기준선 artifact manifest 값이 잘못되었습니다."
            )
        result[relative] = {"bytes": size, "sha256": cast(str, digest)}
    return result


def _read_json(path: Path, description: str) -> dict[str, Any]:
    if (
        path.is_symlink()
        or not path.is_file()
        or path.stat().st_size > MAX_JSON_BYTES
    ):
        raise KrFinBertBaselineArtifactError(
            f"{description} 파일이 올바르지 않습니다."
        )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise KrFinBertBaselineArtifactError(
            f"{description} JSON을 읽을 수 없습니다."
        ) from exception
    if not isinstance(value, dict):
        raise KrFinBertBaselineArtifactError(f"{description} JSON 객체가 아닙니다.")
    return value


def _file_record(path: Path) -> dict[str, int | str]:
    if path.is_symlink() or not path.is_file():
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact commitment 파일이 없습니다."
        )
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exception:
        raise KrFinBertBaselineArtifactError(
            "기준선 artifact manifest가 canonical JSON이 아닙니다."
        ) from exception
    return sha256(encoded).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
