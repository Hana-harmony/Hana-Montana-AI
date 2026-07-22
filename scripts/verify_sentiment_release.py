from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from hannah_montana_ai.services.sentiment_release import (
    LOCAL_ATTESTATION_MODE,
    SentimentReleaseError,
    verify_sentiment_release,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="활성 Hana Montana AI sentiment release의 전체 공급망을 검증한다."
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=PROJECT_ROOT / "releases/sentiment/current.json",
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--base-model-runtime-path", type=Path, required=True)
    parser.add_argument("--base-model-verification-path", type=Path)
    parser.add_argument(
        "--runtime-environment",
        choices=("local", "test", "production"),
        default=os.getenv("HANNAH_RUNTIME_ENVIRONMENT", "local"),
    )
    parser.add_argument(
        "--attestation-mode",
        default=os.getenv(
            "HANNAH_SENTIMENT_RELEASE_ATTESTATION_MODE",
            LOCAL_ATTESTATION_MODE,
        ),
    )
    parser.add_argument("--public-key", type=Path)
    parser.add_argument(
        "--signer-key-id",
        default=os.getenv("HANNAH_SENTIMENT_RELEASE_SIGNER_KEY_ID", ""),
    )
    parser.add_argument(
        "--expected-release-id",
        default=os.getenv("HANNAH_SENTIMENT_RELEASE_EXPECTED_ID", ""),
    )
    parser.add_argument(
        "--expected-git-commit",
        default=os.getenv("HANNAH_SENTIMENT_RELEASE_EXPECTED_GIT_COMMIT", ""),
    )
    args = parser.parse_args()
    try:
        release = verify_sentiment_release(
            args.current,
            args.base_model_runtime_path,
            project_root=args.project_root,
            runtime_environment=args.runtime_environment,
            attestation_mode=args.attestation_mode,
            public_key_path=args.public_key,
            signer_key_id=args.signer_key_id,
            expected_release_id=args.expected_release_id,
            expected_git_commit=args.expected_git_commit,
            base_model_verification_path=args.base_model_verification_path,
        )
    except SentimentReleaseError as exception:
        raise SystemExit(f"sentiment release 검증 실패: {exception}") from exception
    print(
        json.dumps(
            {
                "status": "verified",
                "release_id": release.release_id,
                "version": release.version,
                "artifact_path": str(release.artifact_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
