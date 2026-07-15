#!/usr/bin/env python3
"""논문 PDF가 제출 manifest의 크기·해시·쪽수와 일치하는지 검증한다."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess  # nosec B404
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs/paper/acl/submission-manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _page_count(path: Path) -> int:
    pdfinfo_command = shutil.which("pdfinfo")
    if pdfinfo_command is None:
        raise RuntimeError("pdfinfo 실행 파일을 찾지 못했습니다")
    pdfinfo_path = Path(pdfinfo_command).resolve(strict=True)
    # 절대 실행 경로와 인자 배열을 사용해 shell 해석과 PATH 재탐색을 차단한다.
    result = subprocess.run(  # noqa: S603  # nosec B603
        [str(pdfinfo_path), str(path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", maxsplit=1)[1].strip())
    raise ValueError(f"PDF 쪽수를 찾지 못했습니다: {path}")


def _load_artifacts() -> dict[str, dict[str, Any]]:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise ValueError("submission manifest에 artifacts가 없습니다")
    return artifacts


def main() -> None:
    for name, artifact in _load_artifacts().items():
        relative_path = artifact.get("pdf_path")
        if not isinstance(relative_path, str):
            raise ValueError(f"{name}.pdf_path가 문자열이 아닙니다")
        path = (ROOT / relative_path).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError(f"작업공간 밖 PDF 경로입니다: {relative_path}")
        if not path.is_file():
            raise FileNotFoundError(path)

        expected_bytes = int(artifact["pdf_bytes"])
        expected_pages = int(artifact["total_pages"])
        expected_sha256 = str(artifact["pdf_sha256"])
        actual_bytes = path.stat().st_size
        actual_pages = _page_count(path)
        actual_sha256 = _sha256(path)

        if actual_bytes != expected_bytes:
            raise ValueError(f"{name} 크기 불일치: {actual_bytes} != {expected_bytes}")
        if actual_pages != expected_pages:
            raise ValueError(f"{name} 쪽수 불일치: {actual_pages} != {expected_pages}")
        if actual_sha256 != expected_sha256:
            raise ValueError(f"{name} SHA-256 불일치: {actual_sha256}")

    print("paper artifacts verified against submission manifest")


if __name__ == "__main__":
    main()
