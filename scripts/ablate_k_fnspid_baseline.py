from __future__ import annotations

import argparse
import gc
import json
import random
import time
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any

from train_k_fnspid_impact_model import build_model, evaluate, load_rows

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v4"
DEFAULT_BASELINE_REPORT = PROJECT_ROOT / "reports/k-fnspid-impact-training-report.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports/k-fnspid-baseline-ablation-report.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="K-FNSPID 입력 feature ablation을 수행한다.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--baseline-report", type=Path, default=DEFAULT_BASELINE_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    baseline = json.loads(args.baseline_report.read_text(encoding="utf-8"))
    manifest_path = args.dataset_dir / "manifest.json"
    if (
        baseline.get("dataset_manifest", {}).get("sha256")
        != sha256(manifest_path.read_bytes()).hexdigest()
    ):
        raise SystemExit("ablation과 기준선의 K-FNSPID manifest가 다릅니다.")
    runs: dict[str, Any] = {
        "full_context_with_source": {
            "validation": baseline["validation"],
            "test": baseline["test"],
            "reused_report": str(args.baseline_report.relative_to(PROJECT_ROOT)),
        }
    }
    configurations = {
        "full_context_without_source": {
            "include_full_text": True,
            "include_source_prefix": False,
        },
        "title_snippet_with_source": {
            "include_full_text": False,
            "include_source_prefix": True,
        },
    }
    for name, options in configurations.items():
        started = time.perf_counter()
        rows = load_rows(args.dataset_dir, **options)
        partitions = {
            partition: [row for row in rows if row["split"] == partition]
            for partition in ("TRAIN", "VALIDATION", "TEST")
        }
        if {partition: len(values) for partition, values in partitions.items()} != baseline[
            "partition_count"
        ]:
            raise SystemExit(f"ablation 분할이 기준선과 다릅니다: {name}")
        model = build_model()
        model.fit(
            [str(row["text"]) for row in partitions["TRAIN"]],
            [str(row["importance"]) for row in partitions["TRAIN"]],
        )
        runs[name] = {
            "options": options,
            "validation": evaluate(model, partitions["VALIDATION"]),
            "test": evaluate(model, partitions["TEST"]),
            "elapsed_seconds": round(time.perf_counter() - started, 6),
        }
        del model, rows, partitions
        gc.collect()

    learning_curve: dict[str, Any] = {}
    rows = load_rows(args.dataset_dir)
    partitions = {
        partition: [row for row in rows if row["split"] == partition]
        for partition in ("TRAIN", "VALIDATION", "TEST")
    }
    for training_count in (20_000, 50_000):
        started = time.perf_counter()
        training_rows = _stratified_sample(
            partitions["TRAIN"], training_count, seed=20260713 + training_count
        )
        model = build_model()
        model.fit(
            [str(row["text"]) for row in training_rows],
            [str(row["importance"]) for row in training_rows],
        )
        learning_curve[str(training_count)] = {
            "validation": evaluate(model, partitions["VALIDATION"]),
            "test": evaluate(model, partitions["TEST"]),
            "elapsed_seconds": round(time.perf_counter() - started, 6),
        }
        del model, training_rows
        gc.collect()
    del rows, partitions

    report = {
        "schema_version": "k-fnspid-baseline-ablation/v1",
        "dataset_dir": str(args.dataset_dir.relative_to(PROJECT_ROOT)),
        "dataset_manifest": baseline["dataset_manifest"],
        "protocol": "same TRAIN fit and frozen time TEST; no Test-based selection",
        "runs": runs,
        "learning_curve": {
            **learning_curve,
            str(baseline["evaluation_training_count"]): {
                "validation": baseline["validation"],
                "test": baseline["test"],
                "reused_report": str(args.baseline_report.relative_to(PROJECT_ROOT)),
            },
        },
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _stratified_sample(
    rows: list[dict[str, Any]],
    size: int,
    *,
    seed: int,
) -> list[dict[str, Any]]:
    if size >= len(rows):
        return list(rows)
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row["importance"])].append(row)
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 층화 표본
    selected: list[dict[str, Any]] = []
    for label in sorted(buckets):
        bucket = buckets[label]
        generator.shuffle(bucket)
        target = max(1, round(size * len(bucket) / len(rows)))
        selected.extend(bucket[:target])
    generator.shuffle(selected)
    return selected[:size]


if __name__ == "__main__":
    main()
