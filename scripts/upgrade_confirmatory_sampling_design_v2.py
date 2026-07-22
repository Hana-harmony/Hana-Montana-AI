from __future__ import annotations

import argparse
import json
import math
import os
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    PROJECT_ROOT
    / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design.json"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
)
SOURCE_SCHEMA = "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v1"
OUTPUT_SCHEMA = "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v2"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="봉인 표본은 유지하고 estimand/FPC 계약만 v2로 승격한다."
    )
    value.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    value.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return value


def main() -> None:
    args = parser().parse_args()
    upgraded = upgrade_report(args.source, args.output)
    print(json.dumps(upgraded["upgrade_provenance"], ensure_ascii=False, sort_keys=True))


def upgrade_report(source_path: Path, output_path: Path) -> dict[str, Any]:
    source = _read_json(source_path, "v1 sampling design")
    if output_path.exists() or output_path.is_symlink():
        raise ValueError("v2 sampling design 출력이 이미 존재합니다.")
    if (
        source.get("schema_version") != SOURCE_SCHEMA
        or source.get("report_role") != "UNLABELED_CONFIRMATORY_RESERVATION"
        or source.get("labels_available_at_reservation") is not False
        or source.get("candidate_predictions_available") is not False
    ):
        raise ValueError("v1 봉인 sampling design 계약이 올바르지 않습니다.")
    design = _mapping(source.get("sampling_design"), "sampling_design")
    weak = _mapping(design.get("weak_rule_stratum"), "weak_rule_stratum")
    if (
        weak.get("version") != "k-fnspid-confirmatory-weak-stratum/v1"
        or weak.get("gold_label_role") != "none; sampling auxiliary only"
    ):
        raise ValueError("v1 weak-rule auxiliary stratum 계약이 다릅니다.")
    _validate_reservations(source)

    upgraded = json.loads(json.dumps(source, ensure_ascii=False))
    upgraded["schema_version"] = OUTPUT_SCHEMA
    old_frame = _mapping(upgraded.get("estimand_and_frame"), "estimand_and_frame")
    upgraded["estimand_and_frame"] = {
        "primary_estimands": (
            "K-FNSPID-v4 snapshot의 적격 canonical 문서-증권 유한 모집단에서 "
            "출처별 후보·고정 기준선의 설계가중 plug-in Macro-F1과 "
            "후보-minus-기준선 paired contrast"
        ),
        "descriptive_secondary_estimand": (
            "사후 Gold label로 기술하는 출처별 모집단 감성 비율"
        ),
        "sampling_strata_role": (
            "Gold 감성이 아닌 사전 고정 weak-rule auxiliary strata"
        ),
        "eligible_unit": (
            "품질 계약과 단일 PRIMARY 대상 조건을 만족하고 기존 provenance "
            "구성요소와 겹치지 않는 canonical document-security unit"
        ),
        **{
            key: old_frame[key]
            for key in (
                "effective_trade_date_start",
                "effective_trade_date_end_inclusive",
                "snapshot_max_effective_trade_date_observed_at_generation",
                "future_dates_after_snapshot_claimed",
                "source_types",
                "snapshot",
            )
        },
    }
    upgraded_design = _mapping(upgraded.get("sampling_design"), "sampling_design")
    upgraded_design["finite_population_correction_contract"] = (
        "Evaluator must use reported N_h, n_h and f_h. The SRSWOR variance "
        "multiplier is 1-f_h=(N_h-n_h)/N_h, with its square root applied to "
        "standard errors."
    )
    _upgrade_fpc(upgraded)
    upgraded["upgrade_provenance"] = {
        "schema_version": "confirmatory-sampling-design-contract-upgrade/v1",
        "source_schema_version": SOURCE_SCHEMA,
        "source_path": source_path.resolve().relative_to(PROJECT_ROOT).as_posix(),
        "source_bytes": source_path.stat().st_size,
        "source_sha256": _file_sha256(source_path),
        "sampling_units_changed": False,
        "reservation_bytes_changed": False,
        "gold_labels_opened": False,
        "candidate_predictions_opened": False,
        "change_scope": "estimand wording and SRSWOR jackknife FPC metadata only",
        "upgraded_at": datetime.now(UTC).isoformat(),
    }
    _write_json_exclusive(output_path, upgraded)
    return upgraded


def _validate_reservations(report: dict[str, Any]) -> None:
    partitions = _mapping(report.get("partitions"), "partitions")
    for partition in (
        "CONFIRMATORY_SEALED_TEST_REVIEW",
        "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
    ):
        record = _mapping(partitions.get(partition), partition)
        output = _mapping(record.get("output"), f"{partition} output")
        path = (PROJECT_ROOT / str(output.get("path", ""))).resolve(strict=True)
        path.relative_to(PROJECT_ROOT.resolve())
        if (
            path.is_symlink()
            or not path.is_file()
            or output.get("bytes") != path.stat().st_size
            or output.get("sha256") != _file_sha256(path)
        ):
            raise ValueError(f"{partition} reservation commitment가 실제 바이트와 다릅니다.")
        rows = path.read_text(encoding="utf-8").splitlines()
        if len(rows) != record.get("sample_count"):
            raise ValueError(f"{partition} reservation 행 수가 다릅니다.")
        for line in rows:
            row = json.loads(line)
            if (
                not isinstance(row, dict)
                or row.get("final_sentiment") != ""
                or row.get("reviewer_id") != ""
                or row.get("reviewed_at") != ""
            ):
                raise ValueError(f"{partition} reservation label이 개봉되었습니다.")


def _upgrade_fpc(report: dict[str, Any]) -> None:
    partitions = _mapping(report.get("partitions"), "partitions")
    for raw_partition in partitions.values():
        partition = _mapping(raw_partition, "partition")
        strata = _mapping(partition.get("strata"), "strata")
        if set(strata) != set(LABEL_ORDER):
            raise ValueError("sampling stratum 집합이 다릅니다.")
        for label in LABEL_ORDER:
            stratum = _mapping(strata[label], label)
            population = stratum.get("frame_N_h")
            sample = stratum.get("sample_n_h")
            if (
                isinstance(population, bool)
                or not isinstance(population, int)
                or isinstance(sample, bool)
                or not isinstance(sample, int)
                or not 1 < sample <= population
            ):
                raise ValueError("sampling N_h/n_h가 올바르지 않습니다.")
            multiplier = (population - sample) / population
            finite = _mapping(
                stratum.get("finite_population_correction"),
                f"{label} finite_population_correction",
            )
            finite["variance_multiplier"] = multiplier
            finite["variance_multiplier_exact"] = f"{population - sample}/{population}"
            finite["standard_error_multiplier"] = math.sqrt(multiplier)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} 파일이 없습니다.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError(f"{label} JSON을 읽을 수 없습니다.") from exception
    return _mapping(value, label)


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}가 JSON 객체가 아닙니다.")
    return value


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_exclusive(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    with path.open("xb") as file:
        file.write(payload)
        file.flush()
        os.fsync(file.fileno())
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    main()
