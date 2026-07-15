from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v4"
REQUIRED_FILES = {
    "annotations.parquet",
    "document_entities.parquet",
    "documents.parquet",
    "market_impacts.parquet",
    "prices_daily.parquet",
    "splits.parquet",
}
SOURCE_MANIFEST_KEYS = (
    "raw_source",
    "full_content_source",
    "stock_universe_source",
    "price_source",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="K-FNSPID 파일의 크기와 SHA-256을 검증한다.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()

    dataset_dir = args.dataset_dir.resolve()
    manifest_path = dataset_dir / "manifest.json"
    manifest = _load_manifest(manifest_path)
    errors = verify_dataset(dataset_dir, manifest)
    result = {
        "dataset_version": manifest.get("dataset_version"),
        "dataset_dir": str(dataset_dir),
        "file_count": len(manifest.get("files", [])),
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


def verify_dataset(dataset_dir: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != "k-fnspid-quality/v1":
        errors.append("지원하지 않는 manifest schema입니다.")
    if manifest.get("status") != "pass":
        errors.append("dataset build status가 pass가 아닙니다.")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return [*errors, "manifest files가 비어 있습니다."]

    names = [str(entry.get("path", "")) for entry in files if isinstance(entry, dict)]
    missing = sorted(REQUIRED_FILES - set(names))
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if missing:
        errors.append(f"필수 파일이 manifest에 없습니다: {', '.join(missing)}")
    if duplicates:
        errors.append(f"manifest 파일 경로가 중복되었습니다: {', '.join(duplicates)}")

    root = dataset_dir.resolve()
    for entry in files:
        if not isinstance(entry, dict):
            errors.append("manifest file 항목이 객체가 아닙니다.")
            continue
        name = str(entry.get("path", ""))
        candidate = root / name
        path = candidate.resolve()
        if Path(name).name != name or path.parent != root:
            errors.append(f"허용되지 않은 파일 경로: {name}")
            continue
        if not path.is_file() or candidate.is_symlink():
            errors.append(f"파일이 없거나 심볼릭 링크입니다: {name}")
            continue
        if path.stat().st_size != int(entry.get("bytes", -1)):
            errors.append(f"파일 크기가 다릅니다: {name}")
            continue
        if _sha256(path) != str(entry.get("sha256", "")):
            errors.append(f"SHA-256이 다릅니다: {name}")
    for key in SOURCE_MANIFEST_KEYS:
        errors.extend(_verify_source_manifest(key, manifest.get(key)))
    gold_sources = manifest.get("gold_sources")
    if not isinstance(gold_sources, list) or not gold_sources:
        errors.append("gold_sources가 비어 있습니다.")
    else:
        for index, source in enumerate(gold_sources):
            errors.extend(_verify_source_manifest(f"gold_sources[{index}]", source))
    return errors


def _verify_source_manifest(name: str, source: Any) -> list[str]:
    if not isinstance(source, dict):
        return [f"원천 manifest가 객체가 아닙니다: {name}"]
    files = source.get("files")
    if not isinstance(files, list) or not files:
        return [f"원천 manifest files가 비어 있습니다: {name}"]

    errors: list[str] = []
    seen: set[str] = set()
    actual_rows: list[tuple[str, int, str]] = []
    root = PROJECT_ROOT.resolve()
    for entry in files:
        if not isinstance(entry, dict):
            errors.append(f"원천 파일 항목이 객체가 아닙니다: {name}")
            continue
        logical_path = str(entry.get("path", ""))
        candidate = root / logical_path
        path = candidate.resolve()
        if (
            not logical_path
            or logical_path in seen
            or not path.is_relative_to(root)
            or candidate.is_symlink()
            or not path.is_file()
        ):
            errors.append(f"원천 파일 경로가 없거나 안전하지 않습니다: {logical_path}")
            continue
        seen.add(logical_path)
        actual_size = path.stat().st_size
        actual_sha256 = _sha256(path)
        if actual_size != int(entry.get("bytes", -1)):
            errors.append(f"원천 파일 크기가 다릅니다: {logical_path}")
        if actual_sha256 != str(entry.get("sha256", "")):
            errors.append(f"원천 파일 SHA-256이 다릅니다: {logical_path}")
        actual_rows.append((logical_path, actual_size, actual_sha256))

    actual_bytes = sum(row[1] for row in actual_rows)
    if actual_bytes != int(source.get("bytes", -1)):
        errors.append(f"원천 파일 총 크기가 다릅니다: {name}")
    composite = sha256()
    for logical_path, _, actual_sha256 in actual_rows:
        composite.update(f"{logical_path}:{actual_sha256}\n".encode())
    actual_source_sha256 = actual_rows[0][2] if len(actual_rows) == 1 else composite.hexdigest()
    if actual_source_sha256 != str(source.get("sha256", "")):
        errors.append(f"원천 복합 SHA-256이 다릅니다: {name}")
    return errors


def _load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("manifest는 JSON 객체여야 합니다.")
    return cast(dict[str, Any], data)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
