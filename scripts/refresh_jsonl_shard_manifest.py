from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.training.dataset import (
    JSONL_SHARD_MANIFEST_SCHEMA_VERSION,
    build_jsonl_file_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="JSONL shard manifest에 파일 크기와 SHA-256을 기록한다."
    )
    parser.add_argument("manifest", type=Path, nargs="+")
    args = parser.parse_args()
    for manifest_path in args.manifest:
        refresh_manifest(manifest_path)


def refresh_manifest(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON 객체 manifest가 필요합니다: {path}")
    manifest = cast(dict[str, Any], payload)
    if manifest.get("schema_version") != JSONL_SHARD_MANIFEST_SCHEMA_VERSION:
        raise SystemExit(f"지원하지 않는 manifest schema입니다: {path}")
    shard_names = manifest.get("dataset_shards")
    if not isinstance(shard_names, list) or not all(isinstance(name, str) for name in shard_names):
        raise SystemExit(f"dataset_shards가 올바르지 않습니다: {path}")
    if len(set(shard_names)) != len(shard_names):
        raise SystemExit(f"dataset_shards 경로가 중복되었습니다: {path}")
    parent = path.parent.resolve()
    shard_paths: list[Path] = []
    for shard_name in shard_names:
        unresolved = path.parent / str(shard_name)
        resolved = unresolved.resolve()
        if (
            Path(str(shard_name)).is_absolute()
            or not resolved.is_relative_to(parent)
            or unresolved.is_symlink()
            or not resolved.is_file()
        ):
            raise SystemExit(f"안전하지 않은 shard 경로입니다: {shard_name}")
        shard_paths.append(resolved)
    manifest["files"] = [
        build_jsonl_file_manifest(shard_path, str(shard_name))
        for shard_name, shard_path in zip(shard_names, shard_paths, strict=True)
    ]
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)
    print(f"refreshed={path} shards={len(shard_paths)}")


if __name__ == "__main__":
    main()
