from __future__ import annotations

import importlib.util
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path("scripts/verify_k_fnspid_dataset.py")
    spec = importlib.util.spec_from_file_location("verify_k_fnspid_dataset", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_verify_dataset_rejects_tampering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_script()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    files = []
    for name in module.REQUIRED_FILES:
        artifact = tmp_path / name
        artifact.write_bytes(b"verified")
        files.append(
            {
                "path": artifact.name,
                "bytes": artifact.stat().st_size,
                "sha256": sha256(artifact.read_bytes()).hexdigest(),
            }
        )
    manifest = {
        "schema_version": "k-fnspid-quality/v1",
        "status": "pass",
        "files": files,
    }
    _add_source_manifests(manifest, tmp_path, module.SOURCE_MANIFEST_KEYS)

    assert module.verify_dataset(tmp_path, manifest) == []
    artifact = tmp_path / "documents.parquet"
    artifact.write_bytes(b"tampered")
    assert module.verify_dataset(tmp_path, manifest) == ["SHA-256이 다릅니다: documents.parquet"]


def test_verify_dataset_rejects_path_traversal(tmp_path: Path) -> None:
    module = _load_script()
    manifest = {
        "schema_version": "k-fnspid-quality/v1",
        "status": "pass",
        "files": [{"path": "../secret", "bytes": 1, "sha256": "invalid"}],
    }

    errors = module.verify_dataset(tmp_path, manifest)

    assert errors[0].startswith("필수 파일이 manifest에 없습니다:")
    assert errors[1] == "허용되지 않은 파일 경로: ../secret"


def test_verify_dataset_rejects_omitted_and_duplicate_files(tmp_path: Path) -> None:
    module = _load_script()
    manifest = {
        "schema_version": "k-fnspid-quality/v1",
        "status": "pass",
        "files": [
            {"path": "documents.parquet", "bytes": 0, "sha256": ""},
            {"path": "documents.parquet", "bytes": 0, "sha256": ""},
        ],
    }

    errors = module.verify_dataset(tmp_path, manifest)

    assert errors[0].startswith("필수 파일이 manifest에 없습니다:")
    assert errors[1] == "manifest 파일 경로가 중복되었습니다: documents.parquet"


def test_verify_source_manifest_rejects_stale_shard_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_script()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    shard = tmp_path / "data/raw/part-0001.jsonl"
    shard.parent.mkdir(parents=True)
    shard.write_text('{"id":1}\n', encoding="utf-8")
    source = {
        "files": [
            {
                "path": "data/raw/part-0001.jsonl",
                "bytes": shard.stat().st_size,
                "sha256": "0" * 64,
            }
        ],
        "bytes": shard.stat().st_size,
        "sha256": "0" * 64,
    }

    errors = module._verify_source_manifest("raw_source", source)

    assert any("원천 파일 SHA-256" in error for error in errors)
    assert any("원천 복합 SHA-256" in error for error in errors)


def test_verify_source_manifest_rejects_internal_symlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_script()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    actual = tmp_path / "data/actual.jsonl"
    linked = tmp_path / "data/linked.jsonl"
    actual.parent.mkdir(parents=True)
    actual.write_text('{"id":1}\n', encoding="utf-8")
    linked.symlink_to(actual)
    source = {
        "files": [{"path": "data/linked.jsonl", "bytes": actual.stat().st_size, "sha256": ""}],
        "bytes": actual.stat().st_size,
        "sha256": "",
    }

    errors = module._verify_source_manifest("raw_source", source)

    assert any("안전하지 않습니다" in error for error in errors)


def _add_source_manifests(
    manifest: dict,
    root: Path,
    source_keys: tuple[str, ...],
) -> None:
    source_file = root / "data/source.jsonl"
    source_file.parent.mkdir(parents=True)
    source_file.write_text('{"verified":true}\n', encoding="utf-8")
    entry = {
        "path": "data/source.jsonl",
        "bytes": source_file.stat().st_size,
        "sha256": sha256(source_file.read_bytes()).hexdigest(),
    }
    source = {"files": [entry], "bytes": entry["bytes"], "sha256": entry["sha256"]}
    for key in source_keys:
        manifest[key] = source
    manifest["gold_sources"] = [source]
