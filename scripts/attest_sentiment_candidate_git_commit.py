from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess  # nosec B404
from collections.abc import Mapping
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from hannah_montana_ai.services.sentiment_runtime_parity import (
    validate_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
    validate_confirmatory_baseline_commitments,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import RECIPE_RELATIVE_PATHS
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    validate_v6_confirmatory_baseline_commitments,
)

SCHEMA_VERSION = "sentiment-candidate-git-attestation/v1"
ROLE = "REMOTE_GIT_HISTORY_COMMITMENT_NOT_INDEPENDENT_TIMESTAMP"
LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v1"
V6_LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v2"
V6_RECIPE_RELATIVE_PATHS = {
    "candidate_trainer": "scripts/train_kf_deberta_sentiment_v6.py",
    "candidate_locker": "scripts/lock_kf_deberta_sentiment_candidate.py",
    "canonical_evaluator": "scripts/evaluate_locked_kf_deberta_sentiment.py",
    "runtime_parity_generator": "scripts/generate_sentiment_cpu_runtime_parity.py",
    "artifact_contract": "src/hannah_montana_ai/services/sentiment_artifact_contract.py",
    "hierarchical_runtime": (
        "src/hannah_montana_ai/services/source_hierarchical_sentiment.py"
    ),
    "serving_loader": "src/hannah_montana_ai/services/transformer_sentiment_model.py",
    "input_contract": "src/hannah_montana_ai/services/sentiment_input.py",
    "protocol": "src/hannah_montana_ai/training/sentiment_protocol.py",
    "v6_ablation_trainer": "scripts/train_kf_deberta_sentiment_v6_ablation.py",
    "v6_evaluation_contract": (
        "src/hannah_montana_ai/training/sentiment_v6_evaluation_contract.py"
    ),
    "v6_fair_baseline_trainer": "scripts/train_kr_finbert_sc_sentiment_v6.py",
    "v6_fair_baseline_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_v6_baseline.py"
    ),
    "v6_raw_reference_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_raw_reference.py"
    ),
    "v6_raw_reference_materializer": (
        "scripts/materialize_kr_finbert_sc_raw_reference.py"
    ),
    "v6_fair_baseline_commitment": (
        "src/hannah_montana_ai/training/sentiment_v6_baseline_commitment.py"
    ),
    "dependency_manifest": "pyproject.toml",
    "dependency_lock": "uv.lock",
}
HEX_OBJECT_RE = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
REMOTE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
MAX_LOCK_BYTES = 8 * 1024 * 1024
MAX_COMMITTED_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_GIT_METADATA_BYTES = 16 * 1024
MAX_GIT_STDERR_BYTES = 16 * 1024
GIT_TIMEOUT_SECONDS = 30


class AttestationError(ValueError):
    """원격 Git 후보 고정 검증 실패."""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="원격 추적 ref에 포함된 감성 후보 lock과 봉인 자료를 검증한다."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--candidate-lock-path", type=Path, required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--remote-name", required=True)
    parser.add_argument("--remote-ref", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        attestation = create_attestation(
            project_root=args.project_root,
            candidate_lock_path=args.candidate_lock_path,
            commit_sha=args.commit_sha,
            remote_name=args.remote_name,
            remote_ref=args.remote_ref,
            output_path=args.output,
        )
    except AttestationError as exception:
        raise SystemExit(str(exception)) from exception
    print(json.dumps(attestation, ensure_ascii=False, sort_keys=True))


def create_attestation(
    *,
    project_root: Path,
    candidate_lock_path: Path,
    commit_sha: str,
    remote_name: str,
    remote_ref: str,
    output_path: Path,
) -> dict[str, Any]:
    root = _validated_project_root(project_root)
    lock_path = _validated_path_inside_root(
        root,
        candidate_lock_path,
        must_exist=True,
        expect_directory=False,
        label="candidate lock",
    )
    output = _validated_path_inside_root(
        root,
        output_path,
        must_exist=False,
        expect_directory=False,
        label="attestation output",
    )
    if output.exists() or output.is_symlink():
        raise AttestationError(f"attestation 출력은 write-once이며 이미 존재합니다: {output}")

    normalized_commit = _validated_object_id(commit_sha, "commit SHA")
    tracking_ref = _validated_remote_tracking_ref(remote_name, remote_ref)
    _validate_repository_root(root)
    _verify_remote_commit(root, normalized_commit, remote_name, tracking_ref)

    canonical_commit = _git_text(
        root,
        ["rev-parse", "--verify", f"{normalized_commit}^{{commit}}"],
        label="commit 정규화",
    )
    canonical_commit = _validated_object_id(canonical_commit, "정규화 commit SHA")
    if canonical_commit != normalized_commit:
        raise AttestationError("입력 commit SHA가 전체 canonical object ID와 일치하지 않습니다.")
    tree_sha = _validated_object_id(
        _git_text(root, ["show", "-s", "--format=%T", canonical_commit], label="tree 조회"),
        "tree SHA",
    )
    committer_time = _git_text(
        root,
        ["show", "-s", "--format=%cI", canonical_commit],
        label="committer 시각 조회",
    )
    _validate_aware_iso_datetime(committer_time, "committer 시각")

    local_lock = _read_regular_file(lock_path, MAX_LOCK_BYTES, "candidate lock")
    lock_relative_path = lock_path.relative_to(root).as_posix()
    committed_lock = _read_committed_blob(
        root,
        canonical_commit,
        lock_relative_path,
        maximum_bytes=MAX_LOCK_BYTES,
        label="candidate lock",
    )
    if committed_lock != local_lock:
        raise AttestationError("로컬 candidate lock이 지정 commit의 lock bytes와 다릅니다.")
    lock = _load_json_object(committed_lock, "candidate lock")
    if lock.get("schema_version") not in {LOCK_SCHEMA_VERSION, V6_LOCK_SCHEMA_VERSION}:
        raise AttestationError("candidate lock schema가 올바르지 않습니다.")
    if lock.get("external_git_commitment_required") is not True:
        raise AttestationError(
            "candidate lock에 external_git_commitment_required=true가 필요합니다."
        )

    committed_manifests = _attest_lock_commitments(root, canonical_commit, lock)
    attestation = {
        "schema_version": SCHEMA_VERSION,
        "role": ROLE,
        "git": {
            "commit_sha": canonical_commit,
            "tree_sha": tree_sha,
            "committer_time_iso": committer_time,
            "remote_name": remote_name,
            "remote_tracking_ref": tracking_ref,
            "commit_is_ancestor_of_remote_tracking_ref": True,
        },
        "candidate_lock": {
            "path": lock_relative_path,
            "bytes": len(committed_lock),
            "sha256": sha256(committed_lock).hexdigest(),
            "bytes_equal_local_lock": True,
        },
        "committed_artifact_manifests": committed_manifests,
        "limitations": [
            "Git object ID는 내용 변경을 탐지하지만 독립된 신뢰 시각 또는 서명을 제공하지 않는다.",
            (
                "원격 ref는 force-push될 수 있으며 이 증명은 검증 시점의 로컬 "
                "fetched remote-tracking ref만 확인한다."
            ),
            (
                "committer 시각은 커밋 작성자가 설정할 수 있으므로 신뢰 가능한 "
                "타임스탬프로 해석할 수 없다."
            ),
        ],
        "attested_at": datetime.now(UTC).isoformat(),
    }
    _write_json_exclusive(output, attestation)
    return attestation


def _attest_lock_commitments(
    root: Path,
    commit_sha: str,
    lock: Mapping[str, Any],
) -> dict[str, Any]:
    reservations = _mapping(lock.get("sealed_reservations"), "sealed_reservations")
    if set(reservations) != {"NEWS", "DISCLOSURE"}:
        raise AttestationError("sealed_reservations는 NEWS와 DISCLOSURE만 포함해야 합니다.")
    reservation_manifests = {
        source: _verify_committed_manifest(
            root,
            commit_sha,
            _mapping(reservations[source], f"sealed_reservations.{source}"),
            label=f"{source} reservation",
        )
        for source in ("NEWS", "DISCLOSURE")
    }

    provenance = _mapping(lock.get("dataset_provenance"), "dataset_provenance")
    codebook = _verify_committed_manifest(
        root,
        commit_sha,
        _mapping(provenance.get("codebook"), "dataset_provenance.codebook"),
        label="sentiment codebook",
    )
    sampling_implementation = _verify_committed_manifest(
        root,
        commit_sha,
        _mapping(
            provenance.get("sampling_implementation"),
            "dataset_provenance.sampling_implementation",
        ),
        label="sealed sampling implementation",
    )
    dataset_reports = _mapping(
        provenance.get("dataset_reports"),
        "dataset_provenance.dataset_reports",
    )
    required_reports = {"NEWS", "DISCLOSURE", "SAMPLING_DESIGN"}
    if set(dataset_reports) != required_reports:
        raise AttestationError(
            "dataset_reports는 NEWS, DISCLOSURE, SAMPLING_DESIGN을 정확히 포함해야 합니다."
        )
    report_manifests = {
        name: _verify_committed_manifest(
            root,
            commit_sha,
            _mapping(dataset_reports[name], f"dataset_reports.{name}"),
            label=f"dataset report {name}",
        )
        for name in sorted(required_reports)
    }

    recipe = _mapping(lock.get("recipe"), "recipe")
    recipe_blobs = _mapping(recipe.get("blobs"), "recipe.blobs")
    is_v6 = lock.get("schema_version") == V6_LOCK_SCHEMA_VERSION
    expected_recipe_paths = (
        V6_RECIPE_RELATIVE_PATHS if is_v6 else dict(RECIPE_RELATIVE_PATHS)
    )
    if set(recipe_blobs) != set(expected_recipe_paths):
        raise AttestationError("candidate recipe blob commitment 집합이 완전하지 않습니다.")
    committed_recipe_blobs: dict[str, dict[str, int | str]] = {}
    for name in sorted(recipe_blobs):
        if not isinstance(name, str) or not name or len(name) > 128:
            raise AttestationError("candidate recipe blob 이름이 올바르지 않습니다.")
        committed_recipe_blobs[name] = _verify_committed_manifest(
            root,
            commit_sha,
            _mapping(recipe_blobs[name], f"recipe.blobs.{name}"),
            label=f"candidate recipe blob {name}",
        )
        if committed_recipe_blobs[name]["path"] != expected_recipe_paths[name]:
            raise AttestationError(f"candidate recipe blob 경로가 고정 계약과 다릅니다: {name}")
    training_script = committed_recipe_blobs.get("candidate_trainer")
    historical_promoter = committed_recipe_blobs.get("historical_auxiliary_promoter")
    legacy_recipe_valid = (
        historical_promoter is not None
        and recipe.get("training_script") == training_script["path"]
        and recipe.get("training_script_sha256") == training_script["sha256"]
        and recipe.get("auxiliary_training_gold_promoter") == historical_promoter["path"]
        and recipe.get("auxiliary_training_gold_promoter_sha256")
        == historical_promoter["sha256"]
    ) if training_script is not None else False
    v6_recipe_valid = (
        recipe.get("schema_version") == "sentiment-candidate-recipe/v3"
        and set(recipe) == {"schema_version", "blobs"}
    )
    if (
        training_script is None
        or (v6_recipe_valid if is_v6 else legacy_recipe_valid) is not True
    ):
        raise AttestationError("candidate recipe legacy commitment가 blob 집합과 다릅니다.")
    winner = _mapping(lock.get("winner"), "winner")
    try:
        if is_v6:
            report_relative = _validated_git_path(
                winner.get("report_path"), "v6 candidate report"
            )
            report_raw = _read_regular_file(
                root / report_relative,
                MAX_LOCK_BYTES,
                "v6 candidate report",
            )
            if sha256(report_raw).hexdigest() != winner.get("report_sha256"):
                raise AttestationError("v6 candidate report hash가 lock과 다릅니다.")
            candidate_report = _load_json_object(report_raw, "v6 candidate report")
            baseline_commitments = validate_v6_confirmatory_baseline_commitments(
                lock.get("baseline_commitments"),
                root,
                candidate_training_report=candidate_report,
            )
        else:
            baseline_commitments = validate_confirmatory_baseline_commitments(
                lock.get("baseline_commitments"), root
            )
    except ValueError as exception:
        raise AttestationError(str(exception)) from exception
    baseline_digest = baseline_commitments_sha256(baseline_commitments)
    if lock.get("baseline_commitments_sha256") != baseline_digest:
        raise AttestationError("baseline commitment digest가 candidate lock과 다릅니다.")
    try:
        runtime_parity = validate_runtime_parity_lock_commitment(
            lock.get("runtime_parity"),
            project_root=root,
            expected_candidate_version=str(winner.get("version", "")),
            expected_candidate_artifact_manifest_sha256=(
                str(winner.get("artifact_manifest_sha256"))
                if is_v6
                else _canonical_manifest_sha256(
                    _mapping(winner.get("artifact_files"), "winner artifact files")
                )
            ),
            expected_candidate_model_family=(
                str(winner.get("model_family")) if is_v6 else None
            ),
            expected_base_source_kind=(
                str(winner.get("base_source_kind")) if is_v6 else None
            ),
            sealed_reservations={
                source: _mapping(reservations[source], f"reservation {source}")
                for source in ("NEWS", "DISCLOSURE")
            },
        )
    except ValueError as exception:
        raise AttestationError(str(exception)) from exception
    parity_evidence = _verify_committed_manifest(
        root,
        commit_sha,
        _mapping(runtime_parity.get("evidence"), "runtime parity evidence"),
        label="runtime parity evidence",
    )
    return {
        "sealed_reservations": reservation_manifests,
        "dataset_provenance": {
            "codebook": codebook,
            "sampling_implementation": sampling_implementation,
            "dataset_reports": report_manifests,
        },
        "code_provenance": {"training_script": training_script},
        "recipe_blobs": committed_recipe_blobs,
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_digest,
        "runtime_parity": runtime_parity,
        "runtime_parity_evidence": parity_evidence,
    }


def _canonical_manifest_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _verify_committed_manifest(
    root: Path,
    commit_sha: str,
    manifest: Mapping[str, Any],
    *,
    label: str,
) -> dict[str, int | str]:
    path = _validated_git_path(manifest.get("path"), f"{label} path")
    expected_sha = _validated_sha256(manifest.get("sha256"), f"{label} sha256")
    expected_bytes = _validated_byte_count(manifest.get("bytes"), f"{label} bytes")
    blob = _read_committed_blob(
        root,
        commit_sha,
        path,
        maximum_bytes=MAX_COMMITTED_ARTIFACT_BYTES,
        label=label,
    )
    if len(blob) != expected_bytes or sha256(blob).hexdigest() != expected_sha:
        raise AttestationError(f"{label}의 지정 commit bytes/hash가 lock commitment와 다릅니다.")
    return {"path": path, "bytes": len(blob), "sha256": sha256(blob).hexdigest()}


def _verify_committed_path_and_hash(
    root: Path,
    commit_sha: str,
    *,
    path_value: object,
    sha256_value: object,
    label: str,
) -> dict[str, int | str]:
    path = _validated_git_path(path_value, f"{label} path")
    expected_sha = _validated_sha256(sha256_value, f"{label} sha256")
    blob = _read_committed_blob(
        root,
        commit_sha,
        path,
        maximum_bytes=MAX_COMMITTED_ARTIFACT_BYTES,
        label=label,
    )
    digest = sha256(blob).hexdigest()
    if digest != expected_sha:
        raise AttestationError(f"{label}의 지정 commit hash가 lock commitment와 다릅니다.")
    return {"path": path, "bytes": len(blob), "sha256": digest}


def _verify_remote_commit(
    root: Path,
    commit_sha: str,
    remote_name: str,
    tracking_ref: str,
) -> None:
    _run_git(root, ["check-ref-format", tracking_ref], label="remote ref 형식 확인")
    remotes = {
        line
        for line in _git_text(root, ["remote"], label="remote 목록 조회").splitlines()
        if line
    }
    if remote_name not in remotes:
        raise AttestationError(f"Git remote가 없습니다: {remote_name}")
    _run_git(root, ["cat-file", "-e", f"{commit_sha}^{{commit}}"], label="commit 존재 확인")
    _run_git(root, ["show-ref", "--verify", "--quiet", tracking_ref], label="remote ref 확인")
    result = _run_git(
        root,
        ["merge-base", "--is-ancestor", commit_sha, tracking_ref],
        label="remote 포함 확인",
        allowed_returncodes=frozenset({0, 1}),
    )
    if result.returncode != 0:
        raise AttestationError(
            "지정 commit이 fetched remote-tracking ref의 ancestor가 아닙니다. "
            "먼저 push/fetch해야 합니다."
        )


def _validate_repository_root(root: Path) -> None:
    top_level = _git_text(root, ["rev-parse", "--show-toplevel"], label="repository root 확인")
    if Path(top_level).resolve() != root.resolve():
        raise AttestationError("project root는 Git repository 최상위 경로여야 합니다.")


def _read_committed_blob(
    root: Path,
    commit_sha: str,
    relative_path: str,
    *,
    maximum_bytes: int,
    label: str,
) -> bytes:
    path = _validated_git_path(relative_path, f"{label} path")
    object_spec = f"{commit_sha}:{path}"
    raw_size = _git_text(
        root,
        ["cat-file", "-s", object_spec],
        label=f"{label} blob 크기 확인",
    )
    try:
        size = int(raw_size)
    except ValueError as exception:
        raise AttestationError(f"{label} blob 크기가 올바르지 않습니다.") from exception
    if size < 0 or size > maximum_bytes:
        raise AttestationError(f"{label} blob이 허용 크기를 벗어났습니다: {size}")
    # 작업 트리가 아니라 고정된 commit blob 원문을 직접 검증한다.
    result = _run_git(
        root,
        ["show", "--no-ext-diff", "--no-textconv", object_spec],
        label=f"{label} blob 조회",
        maximum_stdout_bytes=maximum_bytes,
    )
    if len(result.stdout) != size:
        raise AttestationError(f"{label} blob 크기가 cat-file 결과와 다릅니다.")
    return result.stdout


def _run_git(
    root: Path,
    arguments: list[str],
    *,
    label: str,
    allowed_returncodes: frozenset[int] = frozenset({0}),
    maximum_stdout_bytes: int = MAX_GIT_METADATA_BYTES,
) -> subprocess.CompletedProcess[bytes]:
    environment = {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_PAGER": "cat",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
    }
    executable = shutil.which("git")
    if executable is None:
        raise AttestationError("git 실행 파일을 찾을 수 없습니다.")
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            [executable, "-c", "core.pager=cat", *arguments],
            cwd=root,
            env=environment,
            check=False,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exception:
        raise AttestationError(f"{label} Git 실행에 실패했습니다.") from exception
    if len(result.stdout) > maximum_stdout_bytes:
        raise AttestationError(f"{label} Git stdout이 허용 크기를 넘었습니다.")
    if len(result.stderr) > MAX_GIT_STDERR_BYTES:
        raise AttestationError(f"{label} Git stderr가 허용 크기를 넘었습니다.")
    if result.returncode not in allowed_returncodes:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        if len(stderr) > 512:
            stderr = stderr[:512] + "…"
        detail = f": {stderr}" if stderr else ""
        raise AttestationError(f"{label} Git 검증에 실패했습니다{detail}")
    return result


def _git_text(root: Path, arguments: list[str], *, label: str) -> str:
    raw = _run_git(root, arguments, label=label).stdout
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError as exception:
        raise AttestationError(f"{label} Git 출력이 UTF-8이 아닙니다.") from exception


def _validated_project_root(project_root: Path) -> Path:
    root = project_root.absolute()
    try:
        details = root.lstat()
    except OSError as exception:
        raise AttestationError(f"project root를 확인할 수 없습니다: {root}") from exception
    if stat.S_ISLNK(details.st_mode) or not stat.S_ISDIR(details.st_mode):
        raise AttestationError("project root는 symlink가 아닌 디렉터리여야 합니다.")
    return root


def _validated_path_inside_root(
    root: Path,
    value: Path,
    *,
    must_exist: bool,
    expect_directory: bool,
    label: str,
) -> Path:
    candidate = Path(os.path.abspath(value if value.is_absolute() else root / value))
    try:
        relative = candidate.relative_to(root)
    except ValueError as exception:
        raise AttestationError(f"{label} 경로가 project root 밖입니다.") from exception
    if not relative.parts:
        raise AttestationError(f"{label} 경로가 project root 자체일 수 없습니다.")
    current = root
    for index, component in enumerate(relative.parts):
        current /= component
        is_last = index == len(relative.parts) - 1
        if not current.exists() and not current.is_symlink():
            if must_exist or not is_last:
                raise AttestationError(f"{label} 경로 구성 요소가 없습니다: {current}")
            continue
        try:
            details = current.lstat()
        except OSError as exception:
            raise AttestationError(f"{label} 경로를 확인할 수 없습니다: {current}") from exception
        if stat.S_ISLNK(details.st_mode):
            raise AttestationError(f"{label} 경로에 symlink를 허용하지 않습니다: {current}")
        if not is_last and not stat.S_ISDIR(details.st_mode):
            raise AttestationError(f"{label} 상위 경로가 디렉터리가 아닙니다: {current}")
        if is_last and must_exist:
            expected = stat.S_ISDIR(details.st_mode) if expect_directory else stat.S_ISREG(
                details.st_mode
            )
            if not expected:
                raise AttestationError(f"{label} 파일 형식이 올바르지 않습니다: {current}")
    return candidate


def _read_regular_file(path: Path, maximum_bytes: int, label: str) -> bytes:
    parent_fd = _open_directory(path.parent, label)
    descriptor = -1
    try:
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path.name, flags, dir_fd=parent_fd)
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or details.st_size > maximum_bytes:
            raise AttestationError(f"{label}이 regular file이 아니거나 허용 크기를 넘었습니다.")
        chunks: list[bytes] = []
        remaining = maximum_bytes + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > maximum_bytes:
            raise AttestationError(f"{label}이 허용 크기를 넘었습니다.")
        return payload
    except OSError as exception:
        raise AttestationError(f"{label}을 안전하게 읽을 수 없습니다: {path}") from exception
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent_fd)


def _write_json_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    body = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    parent_fd = _open_directory(path.parent, "attestation output")
    descriptor = -1
    created = False
    try:
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        # 디렉터리 fd를 고정해 출력 상위 경로 교체 경쟁을 차단한다.
        descriptor = os.open(path.name, flags, 0o600, dir_fd=parent_fd)
        created = True
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb", closefd=False) as file:
            file.write(body)
            file.flush()
            os.fsync(file.fileno())
        os.fsync(parent_fd)
    except FileExistsError as exception:
        raise AttestationError(
            f"attestation 출력은 write-once이며 이미 존재합니다: {path}"
        ) from exception
    except OSError as exception:
        if created:
            try:
                os.unlink(path.name, dir_fd=parent_fd)
            except OSError:
                pass
        raise AttestationError(f"attestation 출력을 안전하게 쓸 수 없습니다: {path}") from exception
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent_fd)


def _open_directory(path: Path, label: str) -> int:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as exception:
        raise AttestationError(
            f"{label} 상위 디렉터리를 안전하게 열 수 없습니다: {path}"
        ) from exception
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise AttestationError(f"{label} 상위 경로가 디렉터리가 아닙니다: {path}")
    return descriptor


def _validated_remote_tracking_ref(remote_name: str, remote_ref: str) -> str:
    if not REMOTE_NAME_RE.fullmatch(remote_name) or remote_name in {".", ".."}:
        raise AttestationError("remote name이 올바르지 않습니다.")
    prefix = f"refs/remotes/{remote_name}/"
    if remote_ref.startswith("refs/remotes/"):
        if not remote_ref.startswith(prefix):
            raise AttestationError("remote ref가 지정 remote name과 일치하지 않습니다.")
        tracking_ref = remote_ref
    else:
        branch = remote_ref.removeprefix(f"{remote_name}/")
        tracking_ref = f"{prefix}{branch}"
    if (
        "\\" in tracking_ref
        or "\x00" in tracking_ref
        or tracking_ref.endswith("/")
        or ".." in tracking_ref
        or "@{" in tracking_ref
    ):
        raise AttestationError("remote-tracking ref 형식이 올바르지 않습니다.")
    return tracking_ref


def _validated_git_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise AttestationError(f"{label}가 올바르지 않습니다.")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", "..", ".git"} for part in path.parts):
        raise AttestationError(f"{label}가 repository 밖을 가리킵니다.")
    normalized = path.as_posix()
    if normalized != value:
        raise AttestationError(f"{label}가 정규화된 repository 상대 경로가 아닙니다.")
    return normalized


def _validated_object_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not HEX_OBJECT_RE.fullmatch(value):
        raise AttestationError(f"{label}는 전체 40/64자리 16진수여야 합니다.")
    return value.lower()


def _validated_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise AttestationError(f"{label}가 올바르지 않습니다.")
    return value


def _validated_byte_count(value: object, label: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= MAX_COMMITTED_ARTIFACT_BYTES
    ):
        raise AttestationError(f"{label}가 올바르지 않습니다.")
    return value


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise AttestationError(f"{label}가 JSON 객체가 아닙니다.")
    return value


def _load_json_object(raw: bytes, label: str) -> dict[str, Any]:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AttestationError(f"{label}에 중복 JSON key가 있습니다: {key}")
            result[key] = value
        return result

    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exception:
        raise AttestationError(f"{label} JSON을 해석할 수 없습니다.") from exception
    if not isinstance(payload, dict):
        raise AttestationError(f"{label}가 JSON 객체가 아닙니다.")
    return payload


def _validate_aware_iso_datetime(value: str, label: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exception:
        raise AttestationError(f"{label}이 ISO-8601 형식이 아닙니다.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AttestationError(f"{label}에 시간대가 없습니다.")


if __name__ == "__main__":
    main()
