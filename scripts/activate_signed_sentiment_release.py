from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.sentiment_release import (
    PRODUCTION_ATTESTATION_MODE,
    V6_CURRENT_SCHEMA_VERSION,
    V6_DSSE_PAYLOAD_TYPE,
    V6_RELEASE_SCHEMA_VERSION,
    SentimentReleaseError,
    verify_external_dsse_envelope,
    verify_sentiment_release,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASES_ROOT = PROJECT_ROOT / "releases/sentiment"
DEFAULT_CURRENT_POINTER = DEFAULT_RELEASES_ROOT / "current.json"
RELEASE_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,239}\Z")
GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


class ActivationError(RuntimeError):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="외부에서 서명된 v6 DSSE envelope를 검증한 뒤 pointer를 원자 활성화한다."
    )
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--signer-key-id", required=True)
    parser.add_argument("--expected-git-commit", required=True)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--releases-root", type=Path, default=DEFAULT_RELEASES_ROOT)
    parser.add_argument("--current-pointer", type=Path, default=DEFAULT_CURRENT_POINTER)
    args = parser.parse_args()
    try:
        result = activate_signed_release(
            project_root=args.project_root,
            releases_root=args.releases_root,
            current_pointer=args.current_pointer,
            release_id=args.release_id,
            external_envelope=args.envelope,
            public_key_path=args.public_key,
            signer_key_id=args.signer_key_id,
            expected_git_commit=args.expected_git_commit,
        )
    except (ActivationError, SentimentReleaseError) as exception:
        raise SystemExit(str(exception)) from exception
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def activate_signed_release(
    *,
    project_root: Path,
    releases_root: Path,
    current_pointer: Path,
    release_id: str,
    external_envelope: Path,
    public_key_path: Path,
    signer_key_id: str,
    expected_git_commit: str,
) -> dict[str, Any]:
    if RELEASE_ID_PATTERN.fullmatch(release_id) is None:
        raise ActivationError("release ID 형식이 올바르지 않습니다.")
    if SHA256_PATTERN.fullmatch(signer_key_id) is None:
        raise ActivationError("signer key ID는 lowercase SHA-256이어야 합니다.")
    if GIT_COMMIT_PATTERN.fullmatch(expected_git_commit) is None:
        raise ActivationError("expected Git commit 형식이 올바르지 않습니다.")
    root = _directory(project_root, "project root")
    release_root = _contained_directory(root, releases_root, "release root")
    release_dir = _contained_directory(release_root, release_root / release_id, "release")
    manifest_path = _regular_file(release_dir / "release.json", "release manifest")
    manifest = _load_json(manifest_path, "release manifest")
    source = manifest.get("source")
    if (
        manifest.get("schema_version") != V6_RELEASE_SCHEMA_VERSION
        or manifest.get("release_id") != release_id
        or manifest.get("release_mode") != "PRODUCTION_CANDIDATE"
        or not isinstance(source, dict)
        or source.get("git_commit") != expected_git_commit
        or source.get("dirty") is not False
    ):
        raise ActivationError("서명 활성화 대상은 clean v6 production candidate여야 합니다.")
    envelope_source = _regular_file(external_envelope, "external DSSE envelope")
    public_key = _regular_file(public_key_path, "DSSE public key")
    verify_external_dsse_envelope(
        envelope_path=envelope_source,
        release_manifest_path=manifest_path,
        public_key_path=public_key,
        signer_key_id=signer_key_id,
        payload_type=V6_DSSE_PAYLOAD_TYPE,
    )

    envelope_target = release_dir / "attestation.dsse.json"
    with _activation_lock(release_root):
        _install_envelope_write_once(envelope_source, envelope_target)
        pointer = {
            "schema_version": V6_CURRENT_SCHEMA_VERSION,
            "release_id": release_id,
            "release_manifest_path": f"{release_id}/release.json",
            "release_manifest": _file_commitment(
                manifest_path,
                f"{release_id}/release.json",
            ),
            "attestation": {
                "mode": PRODUCTION_ATTESTATION_MODE,
                "production_eligible": True,
                "envelope": _file_commitment(
                    envelope_target,
                    f"{release_id}/attestation.dsse.json",
                ),
            },
        }
        verification_pointer = _write_temporary_json(release_root, pointer)
        try:
            verified = verify_sentiment_release(
                verification_pointer,
                release_dir / "base",
                project_root=root,
                runtime_environment="production",
                attestation_mode=PRODUCTION_ATTESTATION_MODE,
                public_key_path=public_key,
                signer_key_id=signer_key_id,
                expected_release_id=release_id,
                expected_git_commit=expected_git_commit,
            )
            if verified.release_id != release_id:
                raise ActivationError("검증 결과의 release ID가 활성화 대상과 다릅니다.")
            _replace_json_atomically(current_pointer, release_root, pointer)
        finally:
            verification_pointer.unlink(missing_ok=True)
    return {
        "schema_version": "hana-sentiment-release-dsse-activation/v1",
        "release_id": release_id,
        "release_manifest_sha256": _sha256_file(manifest_path),
        "envelope_sha256": _sha256_file(envelope_target),
        "signer_key_id": signer_key_id,
        "current_pointer": str(current_pointer),
        "private_key_material_handled": False,
    }


def _install_envelope_write_once(source: Path, target: Path) -> None:
    source_bytes = source.read_bytes()
    if target.exists() or target.is_symlink():
        existing = _regular_file(target, "installed DSSE envelope")
        if existing.read_bytes() != source_bytes:
            raise ActivationError("다른 DSSE envelope가 이미 설치되어 있습니다.")
        return
    descriptor, raw_path = tempfile.mkstemp(
        prefix=".attestation.dsse.",
        suffix=".tmp",
        dir=target.parent,
    )
    temporary = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as file:
            file.write(source_bytes)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o444)
        try:
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError as exception:
            raise ActivationError("DSSE envelope 설치 경합을 감지했습니다.") from exception
        _fsync_directory(target.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _replace_json_atomically(path: Path, release_root: Path, value: object) -> None:
    pointer_parent = path.parent.resolve(strict=True)
    if pointer_parent != release_root or path.is_symlink():
        raise ActivationError("current pointer는 release root의 일반 파일이어야 합니다.")
    payload = _canonical_json(value)
    descriptor, raw_path = tempfile.mkstemp(prefix=".current.", suffix=".tmp", dir=release_root)
    temporary = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o444)
        os.replace(temporary, path)
        _fsync_directory(release_root)
    finally:
        temporary.unlink(missing_ok=True)


def _write_temporary_json(directory: Path, value: object) -> Path:
    descriptor, raw_path = tempfile.mkstemp(
        prefix=".signed-current-verification-",
        suffix=".json",
        dir=directory,
    )
    path = Path(raw_path)
    with os.fdopen(descriptor, "wb", closefd=True) as file:
        file.write(_canonical_json(value))
        file.flush()
        os.fsync(file.fileno())
    return path


@contextmanager
def _activation_lock(release_root: Path) -> Iterator[None]:
    lock_path = release_root / ".activation.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _contained_directory(root: Path, path: Path, label: str) -> Path:
    candidate = path if path.is_absolute() else root / path
    resolved = _directory(candidate, label)
    try:
        resolved.relative_to(root)
    except ValueError as exception:
        raise ActivationError(f"{label} 경로가 허용된 root 밖입니다.") from exception
    return resolved


def _directory(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ActivationError(f"{label}는 symlink가 아닌 디렉터리여야 합니다.")
    resolved = path.resolve(strict=True)
    if resolved != path.absolute():
        raise ActivationError(f"{label} 경로에 symlink component가 있습니다.")
    return resolved


def _regular_file(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ActivationError(f"{label}는 symlink가 아닌 일반 파일이어야 합니다.")
    resolved = path.resolve(strict=True)
    if resolved != path.absolute() or not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
        raise ActivationError(f"{label} 경로에 symlink component가 있습니다.")
    return resolved


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ActivationError(f"{label} JSON을 읽을 수 없습니다.") from exception
    if not isinstance(value, dict):
        raise ActivationError(f"{label}는 JSON 객체여야 합니다.")
    return value


def _file_commitment(path: Path, display_path: str) -> dict[str, int | str]:
    regular = _regular_file(path, display_path)
    return {
        "path": display_path,
        "bytes": regular.stat().st_size,
        "sha256": _sha256_file(regular),
    }


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    main()
