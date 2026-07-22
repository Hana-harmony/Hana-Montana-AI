from __future__ import annotations

import hmac
import json
import os
import stat
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "sentiment-confirmatory-baseline-commitments/v1"
DIRECTORY_SCHEMA_VERSION = "sentiment-full-directory-manifest/v1"
REQUIRED_SEEDS = (17, 42, 73)
REQUIRED_BASELINES = frozenset(
    {
        "hana_tfidf_logistic",
        "pre_k_fnspid_kf_deberta",
        "kr_finbert_sc_same_data_fair",
        "kf_deberta_no_k_ablation",
    }
)
MAX_MANIFEST_FILES = 10_000
NO_K_SOURCE_NAMES = frozenset(
    {
        "PUBLIC_TRAIN",
        "K_FNSPID_CODEX_GOLD",
        "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_RULE_SILVER",
        "K_FNSPID_DISCLOSURE_RULE_SILVER",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE",
    }
)


def file_commitment(path: Path, project_root: Path) -> dict[str, int | str]:
    root = _directory(project_root, "프로젝트 root")
    regular = _project_file(path, root, "commitment 파일")
    return {
        "path": regular.relative_to(root).as_posix(),
        "bytes": regular.stat().st_size,
        "sha256": _file_sha256(regular),
    }


def directory_commitment(path: Path, project_root: Path) -> dict[str, Any]:
    root = _directory(project_root, "프로젝트 root")
    directory = _project_directory(path, root, "artifact 디렉터리")
    files = _directory_manifest(directory)
    return {
        "schema_version": DIRECTORY_SCHEMA_VERSION,
        "path": directory.relative_to(root).as_posix(),
        "files": files,
        "manifest_sha256": canonical_json_sha256(files),
    }


def validate_file_commitment(
    value: object,
    project_root: Path,
    label: str,
) -> dict[str, int | str]:
    root = _directory(project_root, "프로젝트 root")
    record = _mapping(value, label)
    if set(record) != {"path", "bytes", "sha256"}:
        raise ValueError(f"{label} 파일 commitment 구성이 올바르지 않습니다.")
    path = _project_relative_file(record.get("path"), root, label)
    size = record.get("bytes")
    digest = _sha256_value(record.get("sha256"), label)
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ValueError(f"{label} 파일 크기가 올바르지 않습니다.")
    actual_size, actual_digest = _file_identity(path)
    if actual_size != size or not hmac.compare_digest(actual_digest, digest):
        raise ValueError(f"{label} 실제 바이트가 잠긴 commitment와 다릅니다.")
    return {"path": path.relative_to(root).as_posix(), "bytes": size, "sha256": digest}


def validate_directory_commitment(
    value: object,
    project_root: Path,
    label: str,
) -> dict[str, Any]:
    root = _directory(project_root, "프로젝트 root")
    record = _mapping(value, label)
    if set(record) != {"schema_version", "path", "files", "manifest_sha256"}:
        raise ValueError(f"{label} full manifest 구성이 올바르지 않습니다.")
    if record.get("schema_version") != DIRECTORY_SCHEMA_VERSION:
        raise ValueError(f"{label} full manifest schema가 올바르지 않습니다.")
    directory = _project_relative_directory(record.get("path"), root, label)
    declared = _manifest(record.get("files"), label)
    digest = _sha256_value(record.get("manifest_sha256"), f"{label} manifest")
    if not hmac.compare_digest(canonical_json_sha256(declared), digest):
        raise ValueError(f"{label} manifest digest가 올바르지 않습니다.")
    actual = _directory_manifest(directory)
    if actual != declared:
        raise ValueError(f"{label} 실제 artifact 바이트가 full manifest와 다릅니다.")
    return {
        "schema_version": DIRECTORY_SCHEMA_VERSION,
        "path": directory.relative_to(root).as_posix(),
        "files": declared,
        "manifest_sha256": digest,
    }


def build_confirmatory_baseline_commitments(
    *,
    project_root: Path,
    tfidf_model: Path,
    pre_k_artifact: Path,
    pre_k_training_report: Path,
    fair_artifact_root: Path,
    fair_selection_report: Path,
    no_k_selection_report: Path,
    no_k_winner_manifest: Path,
) -> dict[str, Any]:
    root = _directory(project_root, "프로젝트 root")
    pre_k = {
        "training_report": file_commitment(pre_k_training_report, root),
        "winner_artifact": directory_commitment(pre_k_artifact, root),
    }
    fair = _build_fair_commitment(
        project_root=root,
        artifact_root=fair_artifact_root,
        selection_report=fair_selection_report,
    )
    no_k = _build_no_k_commitment(
        project_root=root,
        selection_report=no_k_selection_report,
        winner_manifest=no_k_winner_manifest,
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "confirmatory_labels_used": False,
        "public_test_labels_used": False,
        "baselines": {
            "hana_tfidf_logistic": {"artifact": file_commitment(tfidf_model, root)},
            "pre_k_fnspid_kf_deberta": pre_k,
            "kr_finbert_sc_same_data_fair": fair,
            "kf_deberta_no_k_ablation": no_k,
        },
    }
    return validate_confirmatory_baseline_commitments(payload, root)


def validate_confirmatory_baseline_commitments(
    value: object,
    project_root: Path,
) -> dict[str, Any]:
    root = _directory(project_root, "프로젝트 root")
    payload = _mapping(value, "confirmatory baseline commitments")
    baselines = _mapping(payload.get("baselines"), "confirmatory baselines")
    if (
        set(payload)
        != {
            "schema_version",
            "confirmatory_labels_used",
            "public_test_labels_used",
            "baselines",
        }
        or payload.get("schema_version") != SCHEMA_VERSION
        or payload.get("confirmatory_labels_used") is not False
        or payload.get("public_test_labels_used") is not False
        or set(baselines) != REQUIRED_BASELINES
    ):
        raise ValueError("confirmatory baseline lock 계약이 완전하지 않습니다.")

    tfidf = _mapping(baselines["hana_tfidf_logistic"], "TF-IDF baseline")
    if set(tfidf) != {"artifact"}:
        raise ValueError("TF-IDF baseline commitment 구성이 올바르지 않습니다.")
    normalized_tfidf = {
        "artifact": validate_file_commitment(tfidf["artifact"], root, "TF-IDF artifact")
    }

    pre_k = _mapping(baselines["pre_k_fnspid_kf_deberta"], "pre-K baseline")
    if set(pre_k) != {"training_report", "winner_artifact"}:
        raise ValueError("pre-K baseline commitment 구성이 올바르지 않습니다.")
    normalized_pre_k = {
        "training_report": validate_file_commitment(
            pre_k["training_report"], root, "pre-K training report"
        ),
        "winner_artifact": validate_directory_commitment(
            pre_k["winner_artifact"], root, "pre-K winner artifact"
        ),
    }

    normalized_fair = _validate_seeded_baseline(
        baselines["kr_finbert_sc_same_data_fair"],
        root,
        label="same-data fair baseline",
        expected_selection_schema="k-fnspid-fair-baseline-selection/v1",
        expected_ablation_mode=None,
    )
    normalized_no_k = _validate_seeded_baseline(
        baselines["kf_deberta_no_k_ablation"],
        root,
        label="no-K ablation baseline",
        expected_selection_schema="k-fnspid-sentiment-ablation-selection/v1",
        expected_ablation_mode="NO_K",
    )
    winner_manifest = validate_file_commitment(
        normalized_no_k.get("winner_manifest"), root, "no-K winner manifest"
    )
    winner_payload = _load_json(
        _project_relative_file(winner_manifest["path"], root, "no-K winner manifest"),
        "no-K winner manifest",
    )
    _validate_no_k_winner_payload(winner_payload, normalized_no_k, root)
    normalized_no_k["winner_manifest"] = winner_manifest

    return {
        "schema_version": SCHEMA_VERSION,
        "confirmatory_labels_used": False,
        "public_test_labels_used": False,
        "baselines": {
            "hana_tfidf_logistic": normalized_tfidf,
            "pre_k_fnspid_kf_deberta": normalized_pre_k,
            "kr_finbert_sc_same_data_fair": normalized_fair,
            "kf_deberta_no_k_ablation": normalized_no_k,
        },
    }


def baseline_commitments_sha256(value: object) -> str:
    return canonical_json_sha256(value)


def _build_fair_commitment(
    *,
    project_root: Path,
    artifact_root: Path,
    selection_report: Path,
) -> dict[str, Any]:
    selection_path = _project_file(selection_report, project_root, "공정 기준선 selection")
    selection = _load_json(selection_path, "공정 기준선 selection")
    if selection.get("schema_version") != "k-fnspid-fair-baseline-selection/v1":
        raise ValueError("공정 기준선 selection schema가 올바르지 않습니다.")
    runs = selection.get("runs")
    if not isinstance(runs, list):
        raise ValueError("공정 기준선 selection seed run이 없습니다.")
    reports: dict[str, dict[str, int | str]] = {}
    for run in runs:
        record = _mapping(run, "공정 기준선 seed run")
        seed = _seed(record.get("seed"), "공정 기준선 seed")
        report = _mapping(record.get("report"), f"공정 기준선 seed{seed} report")
        report_path = _project_relative_file(report.get("path"), project_root, "공정 기준선 report")
        reports[str(seed)] = file_commitment(report_path, project_root)
    if set(reports) != {str(seed) for seed in REQUIRED_SEEDS}:
        raise ValueError("공정 기준선은 정확히 3개 고정 seed report가 필요합니다.")
    selected_seed = _seed(selection.get("selected_seed"), "공정 기준선 selected seed")
    return {
        "selection_report": file_commitment(selection_path, project_root),
        "seed_reports": reports,
        "selected_seed": selected_seed,
        "winner_artifact": directory_commitment(
            artifact_root / f"seed{selected_seed}", project_root
        ),
    }


def _build_no_k_commitment(
    *,
    project_root: Path,
    selection_report: Path,
    winner_manifest: Path,
) -> dict[str, Any]:
    selection_path = _project_file(selection_report, project_root, "no-K selection")
    selection = _load_json(selection_path, "no-K selection")
    if (
        selection.get("schema_version") != "k-fnspid-sentiment-ablation-selection/v1"
        or selection.get("ablation_mode") != "NO_K"
        or selection.get("deployment_eligible") is not False
    ):
        raise ValueError("no-K selection 계약이 올바르지 않습니다.")
    candidate_reports = selection.get("candidate_reports")
    if not isinstance(candidate_reports, Mapping):
        raise ValueError("no-K 3-seed report commitment가 없습니다.")
    reports: dict[str, dict[str, int | str]] = {}
    for seed_text, raw in candidate_reports.items():
        if not isinstance(seed_text, str) or not seed_text.isdigit():
            raise ValueError("no-K seed report key가 올바르지 않습니다.")
        seed = _seed(int(seed_text), "no-K seed")
        record = _mapping(raw, "no-K seed report")
        path = _project_relative_file(record.get("path"), project_root, "no-K seed report")
        reports[str(seed)] = file_commitment(path, project_root)
    if set(reports) != {str(seed) for seed in REQUIRED_SEEDS}:
        raise ValueError("no-K ablation은 정확히 3개 고정 seed report가 필요합니다.")
    winner = _mapping(selection.get("winner"), "no-K winner")
    selected_seed = _seed(winner.get("seed"), "no-K selected seed")
    winner_path = _project_file(winner_manifest, project_root, "no-K winner manifest")
    linked_winner = _mapping(
        selection.get("winner_artifact_manifest"), "no-K linked winner manifest"
    )
    actual_winner_record = file_commitment(winner_path, project_root)
    if linked_winner != actual_winner_record:
        raise ValueError("no-K selection의 winner manifest commitment가 실제 바이트와 다릅니다.")
    winner_payload = _load_json(winner_path, "no-K winner manifest")
    artifact_path = _project_relative_directory(
        winner_payload.get("artifact_directory"), project_root, "no-K winner artifact"
    )
    return {
        "selection_report": file_commitment(selection_path, project_root),
        "seed_reports": reports,
        "selected_seed": selected_seed,
        "winner_manifest": actual_winner_record,
        "winner_artifact": directory_commitment(artifact_path, project_root),
    }


def _validate_seeded_baseline(
    value: object,
    project_root: Path,
    *,
    label: str,
    expected_selection_schema: str,
    expected_ablation_mode: str | None,
) -> dict[str, Any]:
    record = _mapping(value, label)
    required = {"selection_report", "seed_reports", "selected_seed", "winner_artifact"}
    if expected_ablation_mode is not None:
        required.add("winner_manifest")
    if set(record) != required:
        raise ValueError(f"{label} commitment 구성이 올바르지 않습니다.")
    selection_record = validate_file_commitment(
        record["selection_report"], project_root, f"{label} selection"
    )
    selection_path = _project_relative_file(
        selection_record["path"], project_root, f"{label} selection"
    )
    selection = _load_json(selection_path, f"{label} selection")
    if selection.get("schema_version") != expected_selection_schema:
        raise ValueError(f"{label} selection schema가 다릅니다.")
    if expected_ablation_mode is not None and (
        selection.get("ablation_mode") != expected_ablation_mode
        or selection.get("deployment_eligible") is not False
    ):
        raise ValueError("no-K selection이 연구 전용 계약을 위반했습니다.")
    selected_seed = _seed(record.get("selected_seed"), f"{label} selected seed")
    declared_reports = _mapping(record.get("seed_reports"), f"{label} seed reports")
    if set(declared_reports) != {str(seed) for seed in REQUIRED_SEEDS}:
        raise ValueError(f"{label}는 정확히 3개 고정 seed report가 필요합니다.")
    reports = {
        seed: validate_file_commitment(
            declared_reports[seed], project_root, f"{label} seed{seed} report"
        )
        for seed in sorted(declared_reports)
    }
    _validate_selection_links(selection, reports, selected_seed, project_root, label)
    winner = validate_directory_commitment(
        record["winner_artifact"], project_root, f"{label} winner artifact"
    )
    normalized: dict[str, Any] = {
        "selection_report": selection_record,
        "seed_reports": reports,
        "selected_seed": selected_seed,
        "winner_artifact": winner,
    }
    if expected_ablation_mode is not None:
        normalized["winner_manifest"] = record["winner_manifest"]
    return normalized


def _validate_selection_links(
    selection: dict[str, Any],
    reports: dict[str, dict[str, int | str]],
    selected_seed: int,
    project_root: Path,
    label: str,
) -> None:
    raw_selected = selection.get("selected_seed")
    if raw_selected is None:
        winner = _mapping(selection.get("winner"), f"{label} winner")
        raw_selected = winner.get("seed")
    if _seed(raw_selected, f"{label} selected seed") != selected_seed:
        raise ValueError(f"{label} selected seed가 selection과 다릅니다.")
    if selection.get("schema_version") == "k-fnspid-fair-baseline-selection/v1":
        runs = selection.get("runs")
        if not isinstance(runs, list):
            raise ValueError("공정 기준선 selection run이 없습니다.")
        linked = {
            str(_seed(_mapping(run, "fair run").get("seed"), "fair seed")): _mapping(
                _mapping(run, "fair run").get("report"), "fair report"
            )
            for run in runs
        }
    else:
        candidates = selection.get("candidate_reports")
        if not isinstance(candidates, Mapping):
            raise ValueError("no-K selection candidate report가 없습니다.")
        linked = {
            str(_seed(int(seed), "no-K seed")): _mapping(run, "no-K report")
            for seed, run in candidates.items()
            if isinstance(seed, str) and seed.isdigit()
        }
    if set(linked) != set(reports):
        raise ValueError(f"{label} selection report seed 집합이 다릅니다.")
    for seed, commitment in reports.items():
        linked_path = _project_relative_file(linked[seed].get("path"), project_root, label)
        if linked_path.relative_to(project_root).as_posix() != commitment["path"]:
            raise ValueError(f"{label} seed{seed} report 경로가 selection과 다릅니다.")
        linked_bytes = linked[seed].get("bytes")
        linked_digest = linked[seed].get("sha256")
        if linked_bytes is not None and linked_bytes != commitment["bytes"]:
            raise ValueError(f"{label} seed{seed} report 크기가 selection과 다릅니다.")
        if linked_digest is not None and linked_digest != commitment["sha256"]:
            raise ValueError(f"{label} seed{seed} report digest가 selection과 다릅니다.")
        report = _load_json(linked_path, f"{label} seed{seed} report")
        expected_schema = (
            "k-fnspid-fair-baseline-training/v1"
            if selection.get("schema_version") == "k-fnspid-fair-baseline-selection/v1"
            else "k-fnspid-sentiment-ablation-training/v1"
        )
        if report.get("schema_version") != expected_schema:
            raise ValueError(f"{label} seed{seed} report schema가 다릅니다.")
        if expected_schema == "k-fnspid-sentiment-ablation-training/v1" and (
            report.get("ablation_mode", report.get("mode")) != "NO_K"
            or report.get("public_test_opened") is not False
            or _mapping(report.get("test"), "no-K test").get("sample_count") != 0
        ):
            raise ValueError("no-K seed report가 봉인·ablation 계약을 위반했습니다.")
        if expected_schema == "k-fnspid-sentiment-ablation-training/v1":
            _validate_no_k_training_report(report, int(seed))


def _validate_no_k_training_report(report: dict[str, Any], seed: int) -> None:
    distribution = _mapping(
        report.get("training_source_distribution"), "no-K training sources"
    )
    provenance = _mapping(
        report.get("source_selection_provenance"), "no-K source provenance"
    )
    calibration = _mapping(report.get("decision_calibration"), "no-K calibration")
    partition_count = _mapping(report.get("partition_count"), "no-K partition count")
    public_count = distribution.get("PUBLIC_TRAIN")
    excluded_sources = {
        name: _mapping(details, f"no-K excluded source {name}")
        for name, details in provenance.items()
        if name != "PUBLIC_TRAIN"
    }
    if (
        report.get("artifact_role") != "RESEARCH_ABLATION_NOT_DEPLOYABLE"
        or report.get("seed") != seed
        or report.get("training_strategy")
        != "group-purged-three-way-ablation-target-swap-rdrop-hierarchical-upper6-lora/v1"
        or set(distribution) != {"PUBLIC_TRAIN"}
        or set(provenance) != NO_K_SOURCE_NAMES
        or isinstance(public_count, bool)
        or not isinstance(public_count, int)
        or public_count < 1
        or _mapping(provenance.get("PUBLIC_TRAIN"), "no-K public source").get(
            "decision"
        )
        != "INCLUDED"
        or not excluded_sources
        or any(
            details.get("decision") != "EXCLUDED"
            or details.get("pre_dedup_selected_count") != 0
            for details in excluded_sources.values()
        )
        or report.get("target_swap_count") != 0
        or report.get("target_swap_source_distribution") != {}
        or partition_count.get("PUBLIC_TEST_NOT_LOADED") != 0
        or calibration.get("public_test_used_for_fit") is not False
        or calibration.get("sealed_gold_used_for_fit") is not False
    ):
        raise ValueError("no-K seed report에 K-FNSPID 또는 봉인 label 사용 흔적이 있습니다.")


def _validate_no_k_winner_payload(
    payload: dict[str, Any],
    no_k: dict[str, Any],
    project_root: Path,
) -> None:
    if (
        payload.get("schema_version")
        != "k-fnspid-sentiment-ablation-winner-manifest/v1"
        or payload.get("artifact_role") != "RESEARCH_ABLATION_NOT_DEPLOYABLE"
        or payload.get("ablation_mode", payload.get("mode")) != "NO_K"
        or payload.get("deployment_eligible") is not False
        or payload.get("confirmatory_or_public_test_used") is not False
        or _seed(payload.get("selected_seed"), "no-K winner seed")
        != no_k["selected_seed"]
    ):
        raise ValueError("no-K winner manifest가 연구 전용·봉인 계약을 위반했습니다.")
    artifact = no_k["winner_artifact"]
    artifact_path = _project_relative_directory(
        payload.get("artifact_directory"), project_root, "no-K winner artifact"
    )
    if artifact_path.relative_to(project_root).as_posix() != artifact["path"]:
        raise ValueError("no-K winner artifact 경로가 winner manifest와 다릅니다.")
    metadata = _load_json(artifact_path / "hannah_metadata.json", "no-K winner metadata")
    if (
        metadata.get("schema_version")
        != "kf-deberta-sentiment-ablation-artifact/v1"
        or metadata.get("artifact_role") != "RESEARCH_ABLATION_NOT_DEPLOYABLE"
        or metadata.get("ablation_mode") != "NO_K"
        or _seed(metadata.get("seed"), "no-K metadata seed")
        != no_k["selected_seed"]
    ):
        raise ValueError("no-K winner metadata가 연구 전용 ablation 계약과 다릅니다.")
    declared_files = _manifest(payload.get("artifact_files"), "no-K winner artifact")
    if declared_files != artifact["files"]:
        raise ValueError("no-K winner artifact full manifest가 실제 바이트와 다릅니다.")
    selected_report = _mapping(payload.get("selected_training_report"), "no-K selected report")
    report_path = _project_relative_file(
        selected_report.get("path"), project_root, "no-K selected report"
    )
    locked_report = no_k["seed_reports"][str(no_k["selected_seed"])]
    if report_path.relative_to(project_root).as_posix() != locked_report["path"]:
        raise ValueError("no-K winner report가 선택된 seed report와 다릅니다.")
    if selected_report.get("bytes") not in {None, locked_report["bytes"]}:
        raise ValueError("no-K winner report 크기가 다릅니다.")
    if selected_report.get("sha256") not in {None, locked_report["sha256"]}:
        raise ValueError("no-K winner report digest가 다릅니다.")


def _directory_manifest(directory: Path) -> dict[str, dict[str, int | str]]:
    files: dict[str, dict[str, int | str]] = {}
    for current, directory_names, file_names in os.walk(directory, followlinks=False):
        directory_names.sort()
        file_names.sort()
        current_path = Path(current)
        for name in directory_names:
            child = current_path / name
            if child.is_symlink():
                raise ValueError(f"artifact에 symlink 디렉터리가 있습니다: {child}")
        for name in file_names:
            path = current_path / name
            if path.is_symlink():
                raise ValueError(f"artifact에 symlink 파일이 있습니다: {path}")
            details = path.stat(follow_symlinks=False)
            if not stat.S_ISREG(details.st_mode):
                raise ValueError(f"artifact에 일반 파일이 아닌 항목이 있습니다: {path}")
            relative = path.relative_to(directory).as_posix()
            files[relative] = {
                "bytes": details.st_size,
                "sha256": _file_sha256(path),
            }
            if len(files) > MAX_MANIFEST_FILES:
                raise ValueError("artifact 파일 수가 안전 한도를 초과했습니다.")
    if not files:
        raise ValueError(f"artifact 디렉터리가 비어 있습니다: {directory}")
    return files


def _manifest(value: object, label: str) -> dict[str, dict[str, int | str]]:
    raw = _mapping(value, f"{label} files")
    if not raw or len(raw) > MAX_MANIFEST_FILES:
        raise ValueError(f"{label} manifest 파일 수가 올바르지 않습니다.")
    result: dict[str, dict[str, int | str]] = {}
    for name, entry_value in raw.items():
        relative = _safe_relative_path(name, f"{label} file")
        entry = _mapping(entry_value, f"{label} {relative}")
        size = entry.get("bytes")
        digest = _sha256_value(entry.get("sha256"), f"{label} {relative}")
        if set(entry) != {"bytes", "sha256"} or isinstance(size, bool) or not isinstance(size, int):
            raise ValueError(f"{label} manifest entry가 올바르지 않습니다.")
        result[relative.as_posix()] = {"bytes": size, "sha256": digest}
    if len(result) != len(raw):
        raise ValueError(f"{label} manifest 경로가 중복됩니다.")
    return dict(sorted(result.items()))


def _project_relative_file(value: object, root: Path, label: str) -> Path:
    relative = _safe_relative_path(value, label)
    return _project_file(root / relative, root, label)


def _project_relative_directory(value: object, root: Path, label: str) -> Path:
    relative = _safe_relative_path(value, label)
    return _project_directory(root / relative, root, label)


def _project_file(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    _inside(resolved, root, label)
    _reject_symlink_components(path, root, label)
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError(f"{label}는 일반 파일이어야 합니다.")
    return resolved


def _project_directory(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    _inside(resolved, root, label)
    _reject_symlink_components(path, root, label)
    if resolved.is_symlink() or not resolved.is_dir():
        raise ValueError(f"{label}는 디렉터리여야 합니다.")
    return resolved


def _directory(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if resolved.is_symlink() or not resolved.is_dir():
        raise ValueError(f"{label}는 디렉터리여야 합니다.")
    return resolved


def _inside(path: Path, root: Path, label: str) -> None:
    try:
        path.relative_to(root)
    except ValueError as exception:
        raise ValueError(f"{label} 경로가 프로젝트 밖입니다.") from exception


def _reject_symlink_components(path: Path, root: Path, label: str) -> None:
    absolute = path if path.is_absolute() else root / path
    try:
        relative = absolute.absolute().relative_to(root.absolute())
    except ValueError as exception:
        raise ValueError(f"{label} 경로가 프로젝트 밖입니다.") from exception
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label} 경로에 symlink가 있습니다.")


def _safe_relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} 경로가 없습니다.")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"{label} 상대 경로가 올바르지 않습니다.")
    return Path(*pure.parts)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError(f"{label} JSON을 읽을 수 없습니다.") from exception
    return dict(_mapping(value, label))


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return dict(value)


def _seed(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value not in REQUIRED_SEEDS:
        raise ValueError(f"{label}는 고정 seed {list(REQUIRED_SEEDS)} 중 하나여야 합니다.")
    return value


def _sha256_value(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} SHA-256 형식이 올바르지 않습니다.")
    return value


def _file_identity(path: Path) -> tuple[int, str]:
    before = path.stat(follow_symlinks=False)
    digest = _file_sha256(path)
    after = path.stat(follow_symlinks=False)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError(f"commitment 해시 계산 중 파일이 변경됐습니다: {path}")
    return after.st_size, digest


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
