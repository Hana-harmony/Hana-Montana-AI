from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORTS = (
    PROJECT_ROOT / "reports/k-fnspid-transformer-training-report-seed17.json",
    PROJECT_ROOT / "reports/k-fnspid-transformer-training-report.json",
    PROJECT_ROOT / "reports/k-fnspid-transformer-training-report-seed73.json",
)
DEFAULT_OUTPUT = PROJECT_ROOT / "reports/k-fnspid-transformer-multiseed-report.json"
METRICS = ("accuracy", "macro_f1", "quadratic_kappa")


def main() -> None:
    parser = argparse.ArgumentParser(description="K-FNSPID 반복 seed 실험을 집계한다.")
    parser.add_argument("--report", type=Path, action="append")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report_paths = args.report or list(DEFAULT_REPORTS)
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in report_paths]
    aggregate = aggregate_reports(reports, report_paths)
    args.output.write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(aggregate, ensure_ascii=False))


def aggregate_reports(
    reports: list[dict[str, Any]],
    report_paths: list[Path],
) -> dict[str, Any]:
    if len(reports) < 3:
        raise ValueError("논문용 집계에는 최소 3개 seed가 필요합니다.")
    seeds = [int(report["seed"]) for report in reports]
    if len(set(seeds)) != len(seeds):
        raise ValueError("seed가 중복되었습니다.")
    signatures = {
        json.dumps(
            {
                "dataset_dir": report["dataset_dir"],
                "dataset_manifest_sha256": report["dataset_manifest"]["sha256"],
                "partition_count": report["partition_count"],
                "training_objective": report["training_objective"],
                "training_hyperparameters": report["training_hyperparameters"],
                "postprocessing_protocol": _postprocessing_protocol(report),
                "base_model": report["base_model"],
                "base_model_revision": report["base_model_revision"],
                "max_length": report["max_length"],
            },
            sort_keys=True,
        )
        for report in reports
    }
    if len(signatures) != 1:
        raise ValueError("seed 실험의 데이터·목적함수·길이 설정이 일치하지 않습니다.")

    selected = max(reports, key=lambda report: float(report["validation"]["macro_f1"]))
    return {
        "schema_version": "k-fnspid-transformer-multiseed/v1",
        "run_count": len(reports),
        "seeds": sorted(seeds),
        "selection_protocol": "validation macro F1 only; TEST is excluded from selection",
        "selected_seed_by_validation": int(selected["seed"]),
        "selected_version": selected["version"],
        "selected_artifact_dir": _artifact_dir(selected),
        "selected_predictions_path": selected["test_predictions"]["path"],
        "report_paths": [_display_path(path) for path in report_paths],
        "validation": summarize_partition(reports, "validation"),
        "test": summarize_partition(reports, "test"),
        "runs": [
            {
                "seed": int(report["seed"]),
                "version": report["version"],
                "validation": {metric: float(report["validation"][metric]) for metric in METRICS},
                "test": {metric: float(report["test"][metric]) for metric in METRICS},
            }
            for report in sorted(reports, key=lambda report: int(report["seed"]))
        ],
    }


def summarize_partition(
    reports: list[dict[str, Any]],
    partition: str,
) -> dict[str, dict[str, float]]:
    return {
        metric: summarize([float(report[partition][metric]) for report in reports])
        for metric in METRICS
    }


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": mean(values),
        "sample_std": stdev(values),
        "minimum": min(values),
        "maximum": max(values),
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _artifact_dir(report: dict[str, Any]) -> str:
    configured = report.get("artifact_dir")
    if configured:
        return str(configured)
    seed = int(report["seed"])
    suffix = "" if seed == 42 else f"_seed{seed}"
    return f"src/hannah_montana_ai/model_store/k_fnspid_impact_transformer{suffix}"


def _postprocessing_protocol(report: dict[str, Any]) -> dict[str, Any]:
    postprocessing = report["postprocessing"]
    return {
        "method": postprocessing["method"],
        "selection_partition": postprocessing["selection_partition"],
        "selection_objective": postprocessing["selection_objective"],
        "strength_grid": postprocessing["strength_grid"],
    }


if __name__ == "__main__":
    main()
