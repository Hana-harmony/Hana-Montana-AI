from __future__ import annotations

import sys
from pathlib import Path

from huggingface_hub import hf_hub_download

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import train_k_fnspid_dapt as dapt  # noqa: E402


def main() -> None:
    for filename, expected_sha256 in sorted(dapt.BASE_FILE_HASHES.items()):
        path = Path(
            hf_hub_download(
                repo_id=dapt.BASE_MODEL,
                filename=filename,
                revision=dapt.BASE_REVISION,
                local_files_only=False,
            )
        )
        if dapt.sha256_file(path) != expected_sha256:
            raise SystemExit(f"DAPT 기준 모델 SHA-256 검증 실패: {filename}")
    print(
        "DAPT 기준 모델 고정본 복원 완료: "
        f"{dapt.BASE_MODEL}@{dapt.BASE_REVISION} ({len(dapt.BASE_FILE_HASHES)}개 파일)"
    )


if __name__ == "__main__":
    main()
