from __future__ import annotations

import importlib.util
import json
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import pytest


def _load_restore_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts/restore_k_fnspid_release.py"
    spec = importlib.util.spec_from_file_location("restore_k_fnspid_release", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


restore = _load_restore_module()


def _write_release(dataset_dir: Path, price: bytes = b"verified-price") -> None:
    dataset_dir.mkdir(parents=True)
    files = {
        "annotations.parquet": b"annotation",
        "document_entities.parquet": b"entity",
        "documents.parquet": b"document",
        "market_impacts.parquet": b"impact",
        "prices_daily.parquet": price,
        "splits.parquet": b"split",
    }
    entries = []
    for name, content in files.items():
        (dataset_dir / name).write_bytes(content)
        entries.append({"path": name, "bytes": len(content), "sha256": sha256(content).hexdigest()})
    price_entry = next(entry for entry in entries if entry["path"] == "prices_daily.parquet")
    (dataset_dir / "manifest.json").write_text(
        json.dumps(
            {
                "files": entries,
                "price_source": {
                    "path": "data/market/market_daily_price.parquet",
                    "bytes": price_entry["bytes"],
                    "sha256": price_entry["sha256"],
                },
            }
        ),
        encoding="utf-8",
    )


def test_restore_release_verifies_assets_and_restores_market_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(restore, "PROJECT_ROOT", tmp_path)
    dataset_dir = tmp_path / "data/k_fnspid/v3"
    market_price = tmp_path / "data/market/market_daily_price.parquet"
    _write_release(dataset_dir)

    result = restore.restore_release(dataset_dir, market_price)

    assert result["status"] == "pass"
    assert result["market_price_restored"] is True
    assert market_price.read_bytes() == b"verified-price"
    assert len(result["verified_release_assets"]) == 6


def test_restore_release_rejects_tampered_asset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(restore, "PROJECT_ROOT", tmp_path)
    dataset_dir = tmp_path / "data/k_fnspid/v3"
    _write_release(dataset_dir)
    (dataset_dir / "documents.parquet").write_bytes(b"tampered")

    with pytest.raises(ValueError, match="SHA-256"):
        restore.restore_release(
            dataset_dir,
            tmp_path / "data/market/market_daily_price.parquet",
        )


def test_restore_release_rejects_market_price_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(restore, "PROJECT_ROOT", tmp_path)
    dataset_dir = tmp_path / "data/k_fnspid/v3"
    _write_release(dataset_dir)
    market_price = tmp_path / "data/market/market_daily_price.parquet"
    market_price.parent.mkdir(parents=True)
    target = tmp_path / "data/market/other.parquet"
    target.write_bytes(b"old")
    market_price.symlink_to(target)

    with pytest.raises(ValueError, match="symlink"):
        restore.restore_release(dataset_dir, market_price)
