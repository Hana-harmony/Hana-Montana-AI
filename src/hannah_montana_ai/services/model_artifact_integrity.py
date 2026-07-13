from __future__ import annotations

from collections.abc import Sequence
from hashlib import sha256
from pathlib import Path
from typing import Any


def build_artifact_manifest(
    directory: Path,
    filenames: Sequence[str],
) -> dict[str, dict[str, int | str]]:
    return {
        filename: {
            "bytes": (directory / filename).stat().st_size,
            "sha256": _file_sha256(directory / filename),
        }
        for filename in filenames
    }


def verify_artifact_manifest(directory: Path, manifest: Any) -> bool:
    if not isinstance(manifest, dict) or not manifest:
        return False
    resolved_directory = directory.resolve()
    for filename, expected in manifest.items():
        if (
            not isinstance(filename, str)
            or Path(filename).name != filename
            or not isinstance(expected, dict)
        ):
            return False
        path = (resolved_directory / filename).resolve()
        # manifest의 상대경로가 artifact 디렉터리 밖을 참조하지 못하게 한다.
        if path.parent != resolved_directory or not path.is_file():
            return False
        if path.stat().st_size != int(expected.get("bytes", -1)):
            return False
        if _file_sha256(path) != str(expected.get("sha256", "")):
            return False
    return True


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
