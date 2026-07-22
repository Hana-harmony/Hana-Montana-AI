from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pytest

from hannah_montana_ai.services import kr_finbert_sc_raw_reference as module


def _artifact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "raw-reference"
    root.mkdir()
    config = {
        "id2label": {"0": "negative", "1": "neutral", "2": "positive"},
        "label2id": {"negative": 0, "neutral": 1, "positive": 2},
    }
    config_payload = json.dumps(config, sort_keys=True).encode("utf-8")
    model_payload = b"safe-test-weight-bytes"
    files = {
        "config.json": config_payload,
        "model.safetensors": model_payload,
    }
    monkeypatch.setattr(
        module,
        "BASE_MODEL_FILES_SHA256",
        {name: sha256(payload).hexdigest() for name, payload in files.items()},
    )
    for name, payload in files.items():
        (root / name).write_bytes(payload)
    (root / module.MANIFEST_FILENAME).write_text(
        json.dumps(
            module.canonical_raw_reference_manifest(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    return root


def test_raw_reference_artifact_validates_exact_bytes_and_label_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _artifact(tmp_path, monkeypatch)

    contract = module.validate_raw_reference_artifact(root)

    assert contract.artifact_dir == root.resolve()
    assert contract.max_length == 256
    assert len(contract.manifest_sha256) == 64


def test_raw_reference_artifact_rejects_weight_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _artifact(tmp_path, monkeypatch)
    (root / "model.safetensors").write_bytes(b"mutated")

    with pytest.raises(module.RawReferenceArtifactError, match="pinned hash"):
        module.validate_raw_reference_artifact(root)


def test_raw_reference_artifact_rejects_symlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _artifact(tmp_path, monkeypatch)
    extra = tmp_path / "extra"
    extra.write_text("x", encoding="utf-8")
    (root / "unexpected.json").symlink_to(extra)

    with pytest.raises(module.RawReferenceArtifactError, match="symlink"):
        module.validate_raw_reference_artifact(root)


def test_raw_reference_artifact_rejects_label_mapping_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _artifact(tmp_path, monkeypatch)
    mutated = {
        "id2label": {"0": "positive", "1": "neutral", "2": "negative"},
        "label2id": {"positive": 0, "neutral": 1, "negative": 2},
    }
    payload = json.dumps(mutated, sort_keys=True).encode("utf-8")
    (root / "config.json").write_bytes(payload)
    monkeypatch.setitem(
        module.BASE_MODEL_FILES_SHA256,
        "config.json",
        sha256(payload).hexdigest(),
    )
    (root / module.MANIFEST_FILENAME).write_text(
        json.dumps(
            module.canonical_raw_reference_manifest(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    with pytest.raises(module.RawReferenceArtifactError, match="label mapping"):
        module.validate_raw_reference_artifact(root)
