from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data/external/kf_deberta_benchmark"
DATASET_REVISION = "7a8dc8cf6548a08e0a5dab3a12ad0fb8dccfd23f"
BASE_URL = (
    f"https://huggingface.co/datasets/mssongit/finance-task/resolve/{DATASET_REVISION}/fnsentiment"
)
FILES = {
    "ratings_train.csv": "aab3329efb94b49828d68ecaa3b9bba795c954d9625950057ab9f9add541bf13",
    "ratings_val.csv": "7bc31a5ae598413cbdac50aa1c78ea1c42561ab4ed7f14fca5d09b36935709d1",
    "ratings_test.csv": "ec2e60f370b711f307683995c7cf02770a53ab1b2e5ec4d5feb00da5ecd38360",
}
MAX_FILE_BYTES = 32 * 1024 * 1024


def main() -> None:
    parser = argparse.ArgumentParser(
        description="고정 리비전의 한국 금융 뉴스 감성 벤치마크를 검증해 받는다."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(
        timeout=httpx.Timeout(60.0),
        follow_redirects=True,
        headers={"User-Agent": "Hannah-Montana-AI-dataset-builder/2"},
    ) as client:
        for filename, expected_hash in FILES.items():
            _download_verified(
                client,
                f"{BASE_URL}/{filename}",
                args.output_dir / filename,
                expected_hash,
            )
    print(f"검증된 벤치마크 {len(FILES)}개 파일을 {args.output_dir}에 저장했습니다.")


def _download_verified(
    client: httpx.Client,
    url: str,
    destination: Path,
    expected_hash: str,
) -> None:
    temporary = destination.with_suffix(f"{destination.suffix}.partial")
    digest = sha256()
    byte_count = 0
    with client.stream("GET", url) as response:
        response.raise_for_status()
        with temporary.open("wb") as file:
            for chunk in response.iter_bytes():
                byte_count += len(chunk)
                if byte_count > MAX_FILE_BYTES:
                    raise RuntimeError(f"다운로드 크기 제한 초과: {destination.name}")
                digest.update(chunk)
                file.write(chunk)
    if digest.hexdigest() != expected_hash:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"SHA-256 검증 실패: {destination.name}")
    temporary.replace(destination)


if __name__ == "__main__":
    main()
