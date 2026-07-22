from __future__ import annotations

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
    canonical_json_sha256,
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
    "v6_fair_baseline_commitment": (
        "src/hannah_montana_ai/training/sentiment_v6_baseline_commitment.py"
    ),
    "v6_raw_reference_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_raw_reference.py"
    ),
    "v6_raw_reference_materializer": (
        "scripts/materialize_kr_finbert_sc_raw_reference.py"
    ),
    "dependency_manifest": "pyproject.toml",
    "dependency_lock": "uv.lock",
}
LIMITATIONS = (
    "Git object ID는 내용 변경을 탐지하지만 독립된 신뢰 시각 또는 서명을 제공하지 않는다.",
    (
        "원격 ref는 force-push될 수 있으며 이 증명은 검증 시점의 로컬 "
        "fetched remote-tracking ref만 확인한다."
    ),
    (
        "committer 시각은 커밋 작성자가 설정할 수 있으므로 신뢰 가능한 "
        "타임스탬프로 해석할 수 없다."
    ),
)
HEX_OBJECT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
REMOTE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
MAX_JSON_BYTES = 8 * 1024 * 1024
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_GIT_METADATA_BYTES = 16 * 1024
MAX_GIT_STDERR_BYTES = 16 * 1024
GIT_TIMEOUT_SECONDS = 30


def validate_candidate_git_attestation(
    attestation_path: Path,
    candidate_lock_path: Path,
    *,
    project_root: Path,
) -> dict[str, Any]:
    root = _project_root(project_root)
    attestation_file = _project_file(
        root,
        attestation_path,
        label="candidate Git attestation",
    )
    lock_file = _project_file(root, candidate_lock_path, label="candidate lock")
    attestation_raw = _read_regular_file(attestation_file, MAX_JSON_BYTES, "Git attestation")
    lock_raw = _read_regular_file(lock_file, MAX_JSON_BYTES, "candidate lock")
    attestation = _load_json(attestation_raw, "candidate Git attestation")
    lock = _load_json(lock_raw, "candidate lock")
    if (
        attestation.get("schema_version") != SCHEMA_VERSION
        or attestation.get("role") != ROLE
        or tuple(attestation.get("limitations", ())) != LIMITATIONS
    ):
        raise ValueError("candidate Git attestation 계약이 올바르지 않습니다.")
    if (
        lock.get("schema_version") not in {LOCK_SCHEMA_VERSION, V6_LOCK_SCHEMA_VERSION}
        or lock.get("external_git_commitment_required") is not True
    ):
        raise ValueError("candidate lock의 외부 Git commitment 계약이 올바르지 않습니다.")

    git = _mapping(attestation.get("git"), "attestation.git")
    commit_sha = _object_id(git.get("commit_sha"), "commit SHA")
    tree_sha = _object_id(git.get("tree_sha"), "tree SHA")
    remote_name = _remote_name(git.get("remote_name"))
    remote_tracking_ref = _remote_tracking_ref(
        git.get("remote_tracking_ref"),
        remote_name,
    )
    if git.get("commit_is_ancestor_of_remote_tracking_ref") is not True:
        raise ValueError("attestation에 원격 ancestor 검증 결과가 없습니다.")
    committer_time_text = _string(git.get("committer_time_iso"), "committer_time_iso")
    committer_time = _aware_datetime(committer_time_text, "committer_time_iso")
    attested_at_text = _string(attestation.get("attested_at"), "attested_at")
    attested_at = _aware_datetime(attested_at_text, "attested_at")
    now = datetime.now(UTC)
    if attested_at > now or committer_time > attested_at:
        raise ValueError("Git attestation 시각 순서가 올바르지 않습니다.")

    lock_relative = lock_file.relative_to(root).as_posix()
    lock_record = _mapping(attestation.get("candidate_lock"), "attestation.candidate_lock")
    lock_sha256 = sha256(lock_raw).hexdigest()
    if (
        lock_record.get("path") != lock_relative
        or lock_record.get("bytes") != len(lock_raw)
        or lock_record.get("sha256") != lock_sha256
        or lock_record.get("bytes_equal_local_lock") is not True
    ):
        raise ValueError("attestation candidate lock commitment가 로컬 lock과 다릅니다.")

    _validate_repository_root(root)
    _verify_remote_ancestry(root, commit_sha, remote_name, remote_tracking_ref)
    actual_tree = _git_text(
        root,
        ["show", "-s", "--format=%T", commit_sha],
        label="commit tree 조회",
    )
    actual_time = _git_text(
        root,
        ["show", "-s", "--format=%cI", commit_sha],
        label="commit 시각 조회",
    )
    if actual_tree != tree_sha or actual_time != committer_time_text:
        raise ValueError("attestation commit tree 또는 committer 시각이 Git object와 다릅니다.")
    committed_lock = _committed_blob(
        root,
        commit_sha,
        lock_relative,
        maximum_bytes=MAX_JSON_BYTES,
        label="candidate lock",
    )
    if committed_lock != lock_raw:
        raise ValueError("candidate lock이 attested commit의 bytes와 다릅니다.")

    manifests = _mapping(
        attestation.get("committed_artifact_manifests"),
        "committed_artifact_manifests",
    )
    validated_manifests = _validate_committed_manifests(
        root,
        commit_sha,
        lock,
        manifests,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "role": ROLE,
        "path": attestation_file.relative_to(root).as_posix(),
        "sha256": sha256(attestation_raw).hexdigest(),
        "attested_at": attested_at.isoformat(),
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "committer_time_iso": committer_time.isoformat(),
        "remote_name": remote_name,
        "remote_tracking_ref": remote_tracking_ref,
        "candidate_lock_path": lock_relative,
        "candidate_lock_sha256": lock_sha256,
        "committed_artifact_manifests": validated_manifests,
        "limitations": list(LIMITATIONS),
    }


def _validate_committed_manifests(
    root: Path,
    commit_sha: str,
    lock: Mapping[str, Any],
    attested: Mapping[str, Any],
) -> dict[str, Any]:
    lock_reservations = _mapping(lock.get("sealed_reservations"), "sealed_reservations")
    attested_reservations = _mapping(
        attested.get("sealed_reservations"),
        "attested sealed_reservations",
    )
    if set(lock_reservations) != {"NEWS", "DISCLOSURE"} or set(attested_reservations) != {
        "NEWS",
        "DISCLOSURE",
    }:
        raise ValueError("NEWS/DISCLOSURE reservation commitment가 완전하지 않습니다.")
    reservations = {
        source: _validate_manifest(
            root,
            commit_sha,
            _mapping(lock_reservations[source], f"lock reservation {source}"),
            _mapping(attested_reservations[source], f"attested reservation {source}"),
            label=f"{source} reservation",
        )
        for source in ("NEWS", "DISCLOSURE")
    }

    provenance = _mapping(lock.get("dataset_provenance"), "dataset_provenance")
    attested_provenance = _mapping(
        attested.get("dataset_provenance"),
        "attested dataset_provenance",
    )
    codebook = _validate_manifest(
        root,
        commit_sha,
        _mapping(provenance.get("codebook"), "lock codebook"),
        _mapping(attested_provenance.get("codebook"), "attested codebook"),
        label="sentiment codebook",
    )
    sampling = _validate_manifest(
        root,
        commit_sha,
        _mapping(provenance.get("sampling_implementation"), "lock sampling implementation"),
        _mapping(
            attested_provenance.get("sampling_implementation"),
            "attested sampling implementation",
        ),
        label="sampling implementation",
    )
    lock_reports = _mapping(provenance.get("dataset_reports"), "lock dataset reports")
    attested_reports = _mapping(
        attested_provenance.get("dataset_reports"),
        "attested dataset reports",
    )
    report_names = {"NEWS", "DISCLOSURE", "SAMPLING_DESIGN"}
    if set(lock_reports) != report_names or set(attested_reports) != report_names:
        raise ValueError("NEWS/DISCLOSURE/SAMPLING_DESIGN report commitment가 완전하지 않습니다.")
    reports = {
        name: _validate_manifest(
            root,
            commit_sha,
            _mapping(lock_reports[name], f"lock report {name}"),
            _mapping(attested_reports[name], f"attested report {name}"),
            label=f"dataset report {name}",
        )
        for name in sorted(report_names)
    }

    recipe = _mapping(lock.get("recipe"), "lock recipe")
    lock_recipe_blobs = _mapping(recipe.get("blobs"), "lock recipe blobs")
    attested_recipe_blobs = _mapping(
        attested.get("recipe_blobs"),
        "attested recipe blobs",
    )
    is_v6 = lock.get("schema_version") == V6_LOCK_SCHEMA_VERSION
    expected_recipe_paths = (
        V6_RECIPE_RELATIVE_PATHS if is_v6 else dict(RECIPE_RELATIVE_PATHS)
    )
    if (
        set(lock_recipe_blobs) != set(expected_recipe_paths)
        or set(lock_recipe_blobs) != set(attested_recipe_blobs)
    ):
        raise ValueError("attested recipe blob 집합이 candidate lock과 다릅니다.")
    recipe_records: dict[str, dict[str, int | str]] = {}
    for name in sorted(lock_recipe_blobs):
        if not isinstance(name, str) or not name or len(name) > 128:
            raise ValueError("candidate recipe blob 이름이 올바르지 않습니다.")
        recipe_records[name] = _validate_manifest(
            root,
            commit_sha,
            _mapping(lock_recipe_blobs[name], f"lock recipe blob {name}"),
            _mapping(attested_recipe_blobs[name], f"attested recipe blob {name}"),
            label=f"recipe blob {name}",
        )
        if recipe_records[name]["path"] != expected_recipe_paths[name]:
            raise ValueError(f"recipe blob 경로가 고정 계약과 다릅니다: {name}")
    code_provenance = _mapping(attested.get("code_provenance"), "attested code_provenance")
    attested_training_script = _mapping(
        code_provenance.get("training_script"),
        "attested training script",
    )
    training_record = recipe_records.get("candidate_trainer")
    historical_promoter = recipe_records.get("historical_auxiliary_promoter")
    legacy_recipe_valid = (
        historical_promoter is not None
        and recipe.get("training_script") == training_record["path"]
        and recipe.get("training_script_sha256") == training_record["sha256"]
        and recipe.get("auxiliary_training_gold_promoter") == historical_promoter["path"]
        and recipe.get("auxiliary_training_gold_promoter_sha256")
        == historical_promoter["sha256"]
    ) if training_record is not None else False
    v6_recipe_valid = (
        recipe.get("schema_version") == "sentiment-candidate-recipe/v3"
        and set(recipe) == {"schema_version", "blobs"}
    )
    if (
        training_record is None
        or dict(attested_training_script) != training_record
        or (v6_recipe_valid if is_v6 else legacy_recipe_valid) is not True
    ):
        raise ValueError("candidate recipe legacy commitment가 blob 집합과 다릅니다.")
    winner = _mapping(lock.get("winner"), "lock winner")
    if is_v6:
        report_relative = _git_path(winner.get("report_path"), "v6 candidate report")
        report_raw = _read_regular_file(
            root / report_relative,
            MAX_JSON_BYTES,
            "v6 candidate report",
        )
        if sha256(report_raw).hexdigest() != winner.get("report_sha256"):
            raise ValueError("v6 candidate report hash가 lock과 다릅니다.")
        baseline_commitments = validate_v6_confirmatory_baseline_commitments(
            lock.get("baseline_commitments"),
            root,
            candidate_training_report=_load_json(report_raw, "v6 candidate report"),
        )
    else:
        baseline_commitments = validate_confirmatory_baseline_commitments(
            lock.get("baseline_commitments"), root
        )
    baseline_digest = baseline_commitments_sha256(baseline_commitments)
    attested_baselines = _mapping(
        attested.get("baseline_commitments"), "attested baseline commitments"
    )
    if (
        dict(attested_baselines) != baseline_commitments
        or attested.get("baseline_commitments_sha256") != baseline_digest
        or lock.get("baseline_commitments_sha256") != baseline_digest
    ):
        raise ValueError("baseline manifests가 candidate lock·Git attestation과 다릅니다.")
    runtime_parity = validate_runtime_parity_lock_commitment(
        lock.get("runtime_parity"),
        project_root=root,
        expected_candidate_version=str(winner.get("version", "")),
        expected_candidate_artifact_manifest_sha256=(
            str(winner.get("artifact_manifest_sha256"))
            if is_v6
            else canonical_json_sha256(
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
            source: _mapping(lock_reservations[source], f"lock reservation {source}")
            for source in ("NEWS", "DISCLOSURE")
        },
    )
    attested_runtime_parity = _mapping(
        attested.get("runtime_parity"), "attested runtime parity"
    )
    if dict(attested_runtime_parity) != runtime_parity:
        raise ValueError("runtime parity lock이 Git attestation과 다릅니다.")
    parity_evidence = _validate_manifest(
        root,
        commit_sha,
        _mapping(runtime_parity.get("evidence"), "runtime parity evidence"),
        _mapping(
            attested.get("runtime_parity_evidence"),
            "attested runtime parity evidence",
        ),
        label="runtime parity evidence",
    )
    return {
        "sealed_reservations": reservations,
        "dataset_provenance": {
            "codebook": codebook,
            "sampling_implementation": sampling,
            "dataset_reports": reports,
        },
        "code_provenance": {"training_script": training_record},
        "recipe_blobs": recipe_records,
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_digest,
        "runtime_parity": runtime_parity,
        "runtime_parity_evidence": parity_evidence,
    }


def _validate_manifest(
    root: Path,
    commit_sha: str,
    locked: Mapping[str, Any],
    attested: Mapping[str, Any],
    *,
    label: str,
) -> dict[str, int | str]:
    record: dict[str, int | str] = {
        "path": _git_path(locked.get("path"), f"{label} path"),
        "bytes": _byte_count(locked.get("bytes"), f"{label} bytes"),
        "sha256": _sha256_value(locked.get("sha256"), f"{label} sha256"),
    }
    if dict(attested) != record:
        raise ValueError(f"{label} attestation manifest가 candidate lock과 다릅니다.")
    blob = _committed_blob(
        root,
        commit_sha,
        str(record["path"]),
        maximum_bytes=MAX_ARTIFACT_BYTES,
        label=label,
    )
    if len(blob) != record["bytes"] or sha256(blob).hexdigest() != record["sha256"]:
        raise ValueError(f"{label} commitment가 attested commit blob과 다릅니다.")
    _validate_local_blob(root, record, label)
    return record


def _validate_local_blob(root: Path, record: Mapping[str, int | str], label: str) -> None:
    path = _project_file(root, Path(str(record["path"])), label=label)
    raw = _read_regular_file(path, MAX_ARTIFACT_BYTES, label)
    if len(raw) != record["bytes"] or sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError(f"{label} working-tree 파일이 attested commit과 다릅니다.")


def _verify_remote_ancestry(
    root: Path,
    commit_sha: str,
    remote_name: str,
    tracking_ref: str,
) -> None:
    _run_git(root, ["check-ref-format", tracking_ref], label="remote ref 형식 확인")
    remotes = set(_git_text(root, ["remote"], label="remote 목록 조회").splitlines())
    if remote_name not in remotes:
        raise ValueError(f"attestation remote가 repository에 없습니다: {remote_name}")
    _run_git(root, ["cat-file", "-e", f"{commit_sha}^{{commit}}"], label="commit 확인")
    _run_git(root, ["show-ref", "--verify", "--quiet", tracking_ref], label="remote ref 확인")
    result = _run_git(
        root,
        ["merge-base", "--is-ancestor", commit_sha, tracking_ref],
        label="remote ancestor 확인",
        allowed_returncodes=frozenset({0, 1}),
    )
    if result.returncode != 0:
        raise ValueError(
            "attested commit이 현재 fetched remote-tracking ref의 ancestor가 아닙니다."
        )


def _validate_repository_root(root: Path) -> None:
    actual = Path(
        _git_text(root, ["rev-parse", "--show-toplevel"], label="repository root 확인")
    ).resolve()
    if actual != root.resolve():
        raise ValueError("project_root가 Git repository 최상위 경로가 아닙니다.")


def _committed_blob(
    root: Path,
    commit_sha: str,
    relative_path: str,
    *,
    maximum_bytes: int,
    label: str,
) -> bytes:
    path = _git_path(relative_path, f"{label} path")
    object_spec = f"{commit_sha}:{path}"
    raw_size = _git_text(
        root,
        ["cat-file", "-s", object_spec],
        label=f"{label} blob 크기 확인",
    )
    try:
        size = int(raw_size)
    except ValueError as error:
        raise ValueError(f"{label} commit blob 크기가 올바르지 않습니다.") from error
    if not 0 <= size <= maximum_bytes:
        raise ValueError(f"{label} commit blob이 허용 크기를 벗어났습니다.")
    result = _run_git(
        root,
        ["show", "--no-ext-diff", "--no-textconv", object_spec],
        label=f"{label} commit blob 조회",
        maximum_stdout_bytes=maximum_bytes,
    )
    if len(result.stdout) != size:
        raise ValueError(f"{label} commit blob 크기가 사전 검증값과 다릅니다.")
    return result.stdout


def _run_git(
    root: Path,
    arguments: list[str],
    *,
    label: str,
    allowed_returncodes: frozenset[int] = frozenset({0}),
    maximum_stdout_bytes: int = MAX_GIT_METADATA_BYTES,
) -> subprocess.CompletedProcess[bytes]:
    executable = shutil.which("git")
    if executable is None:
        raise ValueError("git 실행 파일을 찾을 수 없습니다.")
    environment = {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_PAGER": "cat",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
    }
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            [executable, "-c", "core.pager=cat", *arguments],
            cwd=root,
            env=environment,
            check=False,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f"{label} Git 실행에 실패했습니다.") from error
    if len(result.stdout) > maximum_stdout_bytes or len(result.stderr) > MAX_GIT_STDERR_BYTES:
        raise ValueError(f"{label} Git 출력이 허용 크기를 넘었습니다.")
    if result.returncode not in allowed_returncodes:
        raise ValueError(f"{label} Git 검증에 실패했습니다.")
    return result


def _git_text(root: Path, arguments: list[str], *, label: str) -> str:
    raw = _run_git(root, arguments, label=label).stdout
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} Git 출력이 UTF-8이 아닙니다.") from error


def _project_root(path: Path) -> Path:
    root = path.absolute()
    try:
        details = root.lstat()
    except OSError as error:
        raise ValueError(f"project_root를 확인할 수 없습니다: {root}") from error
    if stat.S_ISLNK(details.st_mode) or not stat.S_ISDIR(details.st_mode):
        raise ValueError("project_root는 symlink가 아닌 디렉터리여야 합니다.")
    return root


def _project_file(root: Path, value: Path, *, label: str) -> Path:
    candidate = Path(os.path.abspath(value if value.is_absolute() else root / value))
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} 경로가 project_root 밖입니다.") from error
    if not relative.parts:
        raise ValueError(f"{label} 경로가 project_root 자체일 수 없습니다.")
    current = root
    for component in relative.parts:
        current /= component
        try:
            details = current.lstat()
        except OSError as error:
            raise ValueError(f"{label} 경로를 확인할 수 없습니다: {current}") from error
        if stat.S_ISLNK(details.st_mode):
            raise ValueError(f"{label} 경로에 symlink를 허용하지 않습니다.")
    if not stat.S_ISREG(candidate.lstat().st_mode):
        raise ValueError(f"{label}이 regular file이 아닙니다.")
    return candidate


def _read_regular_file(path: Path, maximum_bytes: int, label: str) -> bytes:
    parent_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = -1
    try:
        parent_fd = os.open(path.parent, parent_flags)
    except OSError as error:
        raise ValueError(f"{label} 상위 디렉터리를 안전하게 열 수 없습니다.") from error
    try:
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path.name, flags, dir_fd=parent_fd)
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or not 0 <= details.st_size <= maximum_bytes:
            raise ValueError(f"{label} 파일 크기 또는 형식이 올바르지 않습니다.")
        payload = b""
        while len(payload) <= maximum_bytes:
            chunk = os.read(descriptor, min(1024 * 1024, maximum_bytes + 1 - len(payload)))
            if not chunk:
                break
            payload += chunk
        if len(payload) > maximum_bytes:
            raise ValueError(f"{label} 파일이 허용 크기를 넘었습니다.")
        return payload
    except OSError as error:
        raise ValueError(f"{label} 파일을 안전하게 읽을 수 없습니다.") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent_fd)


def _load_json(raw: bytes, label: str) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{label}에 중복 key가 있습니다: {key}")
            result[key] = value
        return result

    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} JSON을 해석할 수 없습니다.") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return payload


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} 문자열이 올바르지 않습니다.")
    return value


def _object_id(value: object, label: str) -> str:
    raw = _string(value, label)
    if not HEX_OBJECT_RE.fullmatch(raw):
        raise ValueError(f"{label}는 소문자 전체 40/64자리 object ID여야 합니다.")
    return raw


def _sha256_value(value: object, label: str) -> str:
    raw = _string(value, label)
    if not SHA256_RE.fullmatch(raw):
        raise ValueError(f"{label}가 SHA-256 형식이 아닙니다.")
    return raw


def _byte_count(value: object, label: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= MAX_ARTIFACT_BYTES
    ):
        raise ValueError(f"{label}가 올바르지 않습니다.")
    return value


def _git_path(value: object, label: str) -> str:
    raw = _string(value, label)
    path = PurePosixPath(raw)
    if (
        "\\" in raw
        or "\x00" in raw
        or path.is_absolute()
        or path.as_posix() != raw
        or any(part in {"", ".", "..", ".git"} for part in path.parts)
    ):
        raise ValueError(f"{label}가 안전한 repository 상대 경로가 아닙니다.")
    return raw


def _remote_name(value: object) -> str:
    raw = _string(value, "remote_name")
    if not REMOTE_NAME_RE.fullmatch(raw) or raw in {".", ".."}:
        raise ValueError("remote_name 형식이 올바르지 않습니다.")
    return raw


def _remote_tracking_ref(value: object, remote_name: str) -> str:
    raw = _string(value, "remote_tracking_ref")
    prefix = f"refs/remotes/{remote_name}/"
    if (
        not raw.startswith(prefix)
        or raw.endswith("/")
        or "\\" in raw
        or "\x00" in raw
        or ".." in raw
        or "@{" in raw
    ):
        raise ValueError("remote_tracking_ref 형식이 올바르지 않습니다.")
    return raw


def _aware_datetime(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label}이 ISO-8601 형식이 아닙니다.") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label}에 시간대가 없습니다.")
    return parsed.astimezone(UTC)
