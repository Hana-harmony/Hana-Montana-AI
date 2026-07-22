from __future__ import annotations

import hmac
import json
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from hannah_montana_ai.services.kr_finbert_sc_v6_baseline import (
    validate_kr_finbert_sc_v6_artifact,
)

SCHEMA_VERSION = "sentiment-v6-kr-finbert-sc-shared-residual-baseline-commitment/v2"
SELECTION_SCHEMA_VERSION = "k-fnspid-v6-fair-shared-residual-baseline-selection/v2"
BASELINE_MODEL_NAME = "kr_finbert_sc_v6_shared_residual_same_data_schedule_fair"
REQUIRED_MODEL_SEEDS = (17, 42, 73)
MAX_JSON_BYTES = 16 * 1024 * 1024


def build_v6_kr_finbert_sc_baseline_commitment(
    *,
    project_root: Path,
    selection_report: Path,
) -> dict[str, Any]:
    root = _directory(project_root, "프로젝트 root")
    selection_path = _project_file(selection_report, root, "v6 기준선 selection")
    selection = _json_object(selection_path, "v6 기준선 selection")
    if selection.get("schema_version") != SELECTION_SCHEMA_VERSION:
        raise ValueError("v6 기준선 selection schema가 올바르지 않습니다.")
    runs = selection.get("runs")
    if not isinstance(runs, list) or len(runs) != len(REQUIRED_MODEL_SEEDS):
        raise ValueError("v6 기준선 selection은 정확히 세 seed run을 가져야 합니다.")

    seed_runs: dict[str, Any] = {}
    selection_matching = selection.get("candidate_matching_contract")
    if not isinstance(selection_matching, dict):
        raise ValueError("v6 기준선 selection candidate matching 계약이 없습니다.")
    seed_executed = selection_matching.get("seed_executed_optimizer_steps")
    if not isinstance(seed_executed, dict):
        raise ValueError("v6 기준선 selection seed optimizer step 계약이 없습니다.")
    selection_matching_common = {
        key: value
        for key, value in selection_matching.items()
        if key != "seed_executed_optimizer_steps"
    }
    for raw_run in runs:
        if not isinstance(raw_run, dict):
            raise ValueError("v6 기준선 seed run이 객체가 아닙니다.")
        seed = _seed(raw_run.get("seed"))
        report_path = _project_relative_file(
            raw_run.get("report_path"), root, f"seed{seed} report"
        )
        artifact_path = _project_relative_directory(
            raw_run.get("artifact_path"), root, f"seed{seed} artifact"
        )
        report = _json_object(report_path, f"seed{seed} report")
        artifact = validate_kr_finbert_sc_v6_artifact(artifact_path)
        report_matching = report.get("candidate_matching_contract")
        if not isinstance(report_matching, dict):
            raise ValueError(f"seed{seed} candidate matching 계약이 없습니다.")
        report_matching_common = {
            key: value
            for key, value in report_matching.items()
            if key != "executed_optimizer_steps"
        }
        if (
            report.get("seed") != seed
            or report.get("public_test_opened") is not False
            or report.get("confirmatory_labels_opened") is not False
            or report.get("recipe_commitment_sha256")
            != selection.get("recipe_commitment_sha256")
            or report.get("prepared_partition_commitments")
            != artifact.prepared_partition_commitments
            or report_matching != artifact.candidate_matching_contract
            or report_matching_common != selection_matching_common
            or seed_executed.get(str(seed))
            != report_matching.get("executed_optimizer_steps")
        ):
            raise ValueError(f"seed{seed} report와 artifact/selection 계약이 다릅니다.")
        seed_runs[str(seed)] = {
            "report": _file_record(report_path, root),
            "artifact": {
                "path": artifact_path.relative_to(root).as_posix(),
                "version": artifact.version,
                "artifact_manifest_sha256": artifact.artifact_manifest_sha256,
            },
            "recipe_commitment_sha256": report["recipe_commitment_sha256"],
            "prepared_partition_commitments": report[
                "prepared_partition_commitments"
            ],
            "candidate_matching_contract": report.get("candidate_matching_contract"),
        }
    if set(seed_runs) != {str(seed) for seed in REQUIRED_MODEL_SEEDS}:
        raise ValueError("v6 기준선 model seed 집합이 고정 계약과 다릅니다.")
    selected_seed = _seed(selection.get("selected_seed"))
    winner = seed_runs[str(selected_seed)]
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline_model_name": BASELINE_MODEL_NAME,
        "public_test_labels_used": False,
        "confirmatory_labels_used": False,
        "required_model_seeds": list(REQUIRED_MODEL_SEEDS),
        "selection_report": _file_record(selection_path, root),
        "selected_seed": selected_seed,
        "seed_runs": seed_runs,
        "winner_artifact": winner["artifact"],
        "recipe_commitment_sha256": selection.get("recipe_commitment_sha256"),
        "candidate_matching_contract": selection.get("candidate_matching_contract"),
    }


def validate_v6_kr_finbert_sc_baseline_commitment(
    value: object,
    *,
    project_root: Path,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("v6 KR-FinBERT-SC baseline commitment가 객체가 아닙니다.")
    expected_fields = {
        "schema_version",
        "baseline_model_name",
        "public_test_labels_used",
        "confirmatory_labels_used",
        "required_model_seeds",
        "selection_report",
        "selected_seed",
        "seed_runs",
        "winner_artifact",
        "recipe_commitment_sha256",
        "candidate_matching_contract",
    }
    if (
        set(value) != expected_fields
        or value.get("schema_version") != SCHEMA_VERSION
        or value.get("baseline_model_name") != BASELINE_MODEL_NAME
        or value.get("public_test_labels_used") is not False
        or value.get("confirmatory_labels_used") is not False
        or value.get("required_model_seeds") != list(REQUIRED_MODEL_SEEDS)
    ):
        raise ValueError("v6 KR-FinBERT-SC baseline commitment 계약이 다릅니다.")
    root = _directory(project_root, "프로젝트 root")
    selection_record = value.get("selection_report")
    if not isinstance(selection_record, dict):
        raise ValueError("v6 기준선 selection commitment가 없습니다.")
    selection_path = _project_relative_file(
        selection_record.get("path"), root, "v6 기준선 selection"
    )
    if _file_record(selection_path, root) != selection_record:
        raise ValueError("v6 기준선 selection 실제 바이트가 commitment와 다릅니다.")
    expected = build_v6_kr_finbert_sc_baseline_commitment(
        project_root=root,
        selection_report=selection_path,
    )
    if not hmac.compare_digest(canonical_json_sha256(value), canonical_json_sha256(expected)):
        raise ValueError("v6 KR-FinBERT-SC baseline commitment가 재검증 결과와 다릅니다.")
    return expected


def canonical_json_sha256(value: object) -> str:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exception:
        raise ValueError("baseline commitment가 canonical JSON이 아닙니다.") from exception
    return sha256(payload).hexdigest()


def _file_record(path: Path, root: Path) -> dict[str, int | str]:
    regular = _project_file(path, root, "commitment 파일")
    digest = sha256()
    with regular.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return {
        "path": regular.relative_to(root).as_posix(),
        "bytes": regular.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def _directory(path: Path, description: str) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{description}가 일반 디렉터리가 아닙니다.")
    return path.resolve(strict=True)


def _project_file(path: Path, root: Path, description: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{description}가 일반 파일이 아닙니다.")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exception:
        raise ValueError(f"{description}가 프로젝트 밖을 가리킵니다.") from exception
    return resolved


def _project_relative_file(value: object, root: Path, description: str) -> Path:
    relative = _safe_relative(value, description)
    return _project_file(root / relative, root, description)


def _project_relative_directory(value: object, root: Path, description: str) -> Path:
    relative = _safe_relative(value, description)
    path = root / relative
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{description}가 일반 디렉터리가 아닙니다.")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exception:
        raise ValueError(f"{description}가 프로젝트 밖을 가리킵니다.") from exception
    return resolved


def _safe_relative(value: object, description: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise ValueError(f"{description} 상대 경로가 문자열이 아닙니다.")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"{description} 상대 경로가 안전하지 않습니다.")
    return path


def _json_object(path: Path, description: str) -> dict[str, Any]:
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError(f"{description} 크기 제한을 초과했습니다.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError(f"{description} JSON을 읽을 수 없습니다.") from exception
    if not isinstance(value, dict):
        raise ValueError(f"{description}가 JSON 객체가 아닙니다.")
    return value


def _seed(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value not in REQUIRED_MODEL_SEEDS:
        raise ValueError("v6 기준선 seed가 고정 집합에 없습니다.")
    return value
