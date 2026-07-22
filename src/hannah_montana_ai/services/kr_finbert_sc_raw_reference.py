from __future__ import annotations

import hmac
import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.services.kr_finbert_sc_v6_baseline import (
    BASE_MODEL,
    BASE_MODEL_FILES_SHA256,
    BASE_MODEL_REVISION,
)

__all__ = [
    "BASE_MODEL",
    "BASE_MODEL_FILES_SHA256",
    "BASE_MODEL_REVISION",
    "MANIFEST_FILENAME",
    "RawReferenceArtifact",
    "RawReferenceArtifactError",
    "canonical_raw_reference_manifest",
    "load_raw_reference_model",
    "validate_raw_reference_artifact",
]

SCHEMA_VERSION = "kr-finbert-sc-raw-reference-artifact/v1"
MANIFEST_FILENAME = "raw_reference_manifest.json"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
MAX_FILE_COUNT = 16
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024


class RawReferenceArtifactError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RawReferenceArtifact:
    artifact_dir: Path
    manifest_sha256: str
    max_length: int


def canonical_raw_reference_manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "files_sha256": dict(sorted(BASE_MODEL_FILES_SHA256.items())),
        "label_order": list(LABEL_ORDER),
        "inference_contract": {
            "input": "raw article text only",
            "target_conditioning": False,
            "truncation": "first_tokens",
            "max_length": 256,
            "trust_remote_code": False,
            "local_files_only": True,
            "safe_serialization_only": True,
        },
    }


def validate_raw_reference_artifact(artifact_dir: Path) -> RawReferenceArtifact:
    root = _regular_directory(artifact_dir, "raw KR-FinBERT-SC artifact")
    expected_files = set(BASE_MODEL_FILES_SHA256) | {MANIFEST_FILENAME}
    actual_files: set[str] = set()
    total_bytes = 0
    for path in sorted(root.iterdir()):
        if path.is_symlink() or not path.is_file():
            raise RawReferenceArtifactError(
                "raw KR-FinBERT-SC artifact에는 symlink나 비정규 파일을 허용하지 않습니다."
            )
        actual_files.add(path.name)
        total_bytes += path.stat().st_size
    if (
        actual_files != expected_files
        or len(actual_files) > MAX_FILE_COUNT
        or total_bytes > MAX_TOTAL_BYTES
    ):
        raise RawReferenceArtifactError(
            "raw KR-FinBERT-SC artifact 파일 집합 또는 크기가 고정 계약과 다릅니다."
        )

    manifest = _read_json(root / MANIFEST_FILENAME, "raw reference manifest")
    expected_manifest = canonical_raw_reference_manifest()
    if _canonical_json(manifest) != _canonical_json(expected_manifest):
        raise RawReferenceArtifactError("raw reference manifest가 canonical 계약과 다릅니다.")
    for filename, expected_digest in BASE_MODEL_FILES_SHA256.items():
        actual_digest = _file_sha256(root / filename)
        if not hmac.compare_digest(actual_digest, expected_digest):
            raise RawReferenceArtifactError(
                f"raw KR-FinBERT-SC 파일 바이트가 pinned hash와 다릅니다: {filename}"
            )
    _validate_label_mapping(root / "config.json")
    inference = cast(dict[str, Any], expected_manifest["inference_contract"])
    return RawReferenceArtifact(
        artifact_dir=root,
        manifest_sha256=sha256(_canonical_json(manifest).encode("utf-8")).hexdigest(),
        max_length=int(inference["max_length"]),
    )


def load_raw_reference_model(artifact_dir: Path) -> tuple[Any, Any, RawReferenceArtifact]:
    contract = validate_raw_reference_artifact(artifact_dir)
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
            contract.artifact_dir,
            revision="local-verified-raw-kr-finbert-sc",
            trust_remote_code=False,
            local_files_only=True,
        )
        model = AutoModelForSequenceClassification.from_pretrained(  # nosec B615
            contract.artifact_dir,
            revision="local-verified-raw-kr-finbert-sc",
            trust_remote_code=False,
            local_files_only=True,
            use_safetensors=True,
            weights_only=True,
        )
    except Exception as exception:
        raise RawReferenceArtifactError(
            "raw KR-FinBERT-SC를 검증된 로컬 artifact에서 load할 수 없습니다."
        ) from exception
    return tokenizer, model, contract


def _validate_label_mapping(config_path: Path) -> None:
    config = _read_json(config_path, "raw KR-FinBERT-SC config")
    if config.get("id2label") != {
        "0": "negative",
        "1": "neutral",
        "2": "positive",
    } or config.get("label2id") != {
        "negative": 0,
        "neutral": 1,
        "positive": 2,
    }:
        raise RawReferenceArtifactError("raw KR-FinBERT-SC label mapping이 다릅니다.")


def _regular_directory(path: Path, label: str) -> Path:
    absolute = path.absolute()
    if any(component.is_symlink() for component in (absolute, *absolute.parents)):
        raise RawReferenceArtifactError(f"{label} 경로에 symlink가 있습니다.")
    if not path.is_dir():
        raise RawReferenceArtifactError(f"{label}가 일반 디렉터리가 아닙니다.")
    return path.resolve(strict=True)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        raise RawReferenceArtifactError(f"{label} 파일이 올바르지 않습니다.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise RawReferenceArtifactError(f"{label} JSON을 읽을 수 없습니다.") from exception
    if not isinstance(value, dict):
        raise RawReferenceArtifactError(f"{label}가 JSON 객체가 아닙니다.")
    return value


def _file_sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RawReferenceArtifactError("raw reference commitment 파일이 없습니다.")
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exception:
        raise RawReferenceArtifactError(
            "raw reference JSON이 canonical하지 않습니다."
        ) from exception
