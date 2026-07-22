from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from huggingface_hub import hf_hub_download

from hannah_montana_ai.services.kr_finbert_sc_raw_reference import (
    BASE_MODEL,
    BASE_MODEL_FILES_SHA256,
    BASE_MODEL_REVISION,
    MANIFEST_FILENAME,
    canonical_raw_reference_manifest,
    validate_raw_reference_artifact,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "models/kr-finbert-sc-raw-reference"


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="pinned raw KR-FinBERT-SC를 로컬 immutable 평가 artifact로 만든다."
    )
    value.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return value


def main() -> None:
    args = parser().parse_args()
    output = args.output_dir.absolute()
    try:
        output.relative_to(PROJECT_ROOT)
    except ValueError as exception:
        raise SystemExit(
            "raw reference artifact는 프로젝트 내부에만 만들 수 있습니다."
        ) from exception
    if output.exists() or output.is_symlink():
        raise SystemExit(f"raw reference artifact가 이미 존재합니다: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.", dir=str(output.parent))
    )
    try:
        for filename, expected_digest in sorted(BASE_MODEL_FILES_SHA256.items()):
            source = Path(
                hf_hub_download(
                    repo_id=BASE_MODEL,
                    filename=filename,
                    revision=BASE_MODEL_REVISION,
                )
            )
            if _file_sha256(source) != expected_digest:
                raise RuntimeError(f"Hugging Face pinned 파일 hash가 다릅니다: {filename}")
            _copy_exclusive(source, temporary / filename)
        _write_json_exclusive(
            temporary / MANIFEST_FILENAME,
            canonical_raw_reference_manifest(),
        )
        validate_raw_reference_artifact(temporary)
        os.replace(temporary, output)
        _fsync_directory(output.parent)
        contract = validate_raw_reference_artifact(output)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(
        json.dumps(
            {
                "status": "MATERIALIZED_AND_VERIFIED",
                "artifact_dir": output.relative_to(PROJECT_ROOT).as_posix(),
                "base_model": BASE_MODEL,
                "base_model_revision": BASE_MODEL_REVISION,
                "manifest_sha256": contract.manifest_sha256,
                "max_length": contract.max_length,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def _copy_exclusive(source: Path, destination: Path) -> None:
    if source.is_dir() or not source.exists():
        raise RuntimeError("raw reference 원본 파일이 없습니다.")
    with source.open("rb") as reader, destination.open("xb") as writer:
        shutil.copyfileobj(reader, writer, length=1024 * 1024)
        writer.flush()
        os.fsync(writer.fileno())


def _write_json_exclusive(path: Path, value: object) -> None:
    payload = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    with path.open("xb") as file:
        file.write(payload)
        file.flush()
        os.fsync(file.fileno())


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    main()
