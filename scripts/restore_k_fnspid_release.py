from __future__ import annotations

import argparse
import json
import os
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = PROJECT_ROOT / "data/k_fnspid/v3"
DEFAULT_MARKET_PRICE = PROJECT_ROOT / "data/market/market_daily_price.parquet"
EXPECTED_RELEASE_ASSETS = {
    "annotations.parquet",
    "document_entities.parquet",
    "documents.parquet",
    "market_impacts.parquet",
    "prices_daily.parquet",
    "splits.parquet",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-FNSPID Release 자산을 검증하고 파일 기반 시세 정본을 복원한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--market-price", type=Path, default=DEFAULT_MARKET_PRICE)
    args = parser.parse_args()

    result = restore_release(args.dataset_dir, args.market_price)
    print(json.dumps(result, ensure_ascii=False))


def restore_release(dataset_dir: Path, market_price: Path) -> dict[str, Any]:
    dataset_dir = _safe_path(dataset_dir)
    market_price = _safe_path(market_price)
    if dataset_dir.is_symlink() or not dataset_dir.is_dir():
        raise ValueError("K-FNSPID Release 디렉터리가 없거나 symlink입니다.")
    manifest_path = dataset_dir / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("K-FNSPID manifest가 없거나 symlink입니다.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("K-FNSPID manifest 파일 목록이 없습니다.")

    verified: list[str] = []
    by_name: dict[str, dict[str, Any]] = {}
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("K-FNSPID manifest 파일 항목이 올바르지 않습니다.")
        name = str(entry.get("path", ""))
        if Path(name).name != name or not name.endswith(".parquet"):
            raise ValueError(f"Release 자산 경로가 올바르지 않습니다: {name}")
        if name in by_name:
            raise ValueError(f"Release 자산 경로가 중복되었습니다: {name}")
        path = dataset_dir / name
        _verify_file(path, entry)
        verified.append(name)
        by_name[name] = entry

    if set(by_name) != EXPECTED_RELEASE_ASSETS:
        raise ValueError("K-FNSPID Release 자산 6개 구성이 manifest와 다릅니다.")

    price_entry = by_name.get("prices_daily.parquet")
    if price_entry is None:
        raise ValueError("Release에 prices_daily.parquet이 없습니다.")
    source = dataset_dir / "prices_daily.parquet"
    price_source = manifest.get("price_source", {})
    if (
        not isinstance(price_source, dict)
        or int(price_source.get("bytes", -1)) != int(price_entry["bytes"])
        or str(price_source.get("sha256", "")) != str(price_entry["sha256"])
    ):
        raise ValueError("Release 시세와 정본 시세 manifest가 일치하지 않습니다.")

    restored = not _file_matches(market_price, price_entry)
    if restored:
        if market_price.is_symlink():
            raise ValueError("시세 정본 경로는 symlink일 수 없습니다.")
        market_price.parent.mkdir(parents=True, exist_ok=True)
        temporary = market_price.with_suffix(market_price.suffix + ".tmp")
        if temporary.exists() or temporary.is_symlink():
            temporary.unlink()
        try:
            shutil.copyfile(source, temporary)
            _verify_file(temporary, price_entry)
            os.replace(temporary, market_price)
        finally:
            if temporary.exists():
                temporary.unlink()

    _verify_file(market_price, price_entry)
    return {
        "status": "pass",
        "verified_release_assets": sorted(verified),
        "market_price_path": str(market_price.relative_to(PROJECT_ROOT)),
        "market_price_restored": restored,
        "sha256": str(price_entry["sha256"]),
    }


def _safe_path(path: Path) -> Path:
    configured = path.expanduser()
    if not configured.is_absolute():
        configured = PROJECT_ROOT / configured
    normalized = Path(os.path.abspath(configured))
    root = PROJECT_ROOT.resolve()
    if not normalized.is_relative_to(root) or not normalized.parent.resolve(
        strict=False
    ).is_relative_to(root):
        raise ValueError(f"프로젝트 밖의 경로는 사용할 수 없습니다: {path}")
    return normalized


def _verify_file(path: Path, manifest: dict[str, Any]) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Release 자산 파일이 없거나 symlink입니다: {path}")
    if not _file_matches(path, manifest):
        raise ValueError(f"Release 자산 SHA-256 또는 크기가 다릅니다: {path}")


def _file_matches(path: Path, manifest: dict[str, Any]) -> bool:
    return (
        path.is_file()
        and not path.is_symlink()
        and path.stat().st_size == int(manifest.get("bytes", -1))
        and _sha256(path) == str(manifest.get("sha256", ""))
    )


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
