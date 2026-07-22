from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
)

from build_k_fnspid_sentiment_dataset import (  # isort: skip
    CODEBOOK_VERSION,
    DEFAULT_DATASET_DIR,
    DEFAULT_DISCLOSURE_SILVER_PATH,
    DEFAULT_OUTPUT_DIR,
    DISCLOSURE_REVIEW_PARTITIONS,
    PROJECT_ROOT,
    PROTECTED_PATHS,
    _file_report,
    _load_protected_rows,
    _review_payload,
    _write_json_atomic,
    _write_jsonl_atomic,
    load_candidates,
    select_review_partitions,
    select_silver_rows,
)

DEFAULT_REPORT_PATH = (
    PROJECT_ROOT / "reports/k-fnspid-disclosure-sentiment-dataset-report.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-FNSPID 공시 감성 실버 학습셋과 독립 검수 패킷을 생성한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--silver-path", type=Path, default=DEFAULT_DISCLOSURE_SILVER_PATH
    )
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--silver-per-label", type=int, default=900)
    parser.add_argument("--seed", type=str, default="20260715")
    args = parser.parse_args()

    protected_rows = _load_protected_rows(PROTECTED_PATHS)
    candidates, source_audit = load_candidates(
        args.dataset_dir,
        protected_rows,
        source_types={"DISCLOSURE"},
    )
    review = select_review_partitions(
        candidates,
        args.seed,
        partition_specs=DISCLOSURE_REVIEW_PARTITIONS,
        source_type="DISCLOSURE",
    )
    reserved_rows = [candidate.group_row() for rows in review.values() for candidate in rows]
    silver = select_silver_rows(
        candidates,
        protected_rows + reserved_rows,
        args.silver_per_label,
        args.seed,
        source_type="DISCLOSURE",
    )
    assert_sentiment_groups_disjoint(
        {
            **{
                name: [candidate.group_row() for candidate in rows]
                for name, rows in review.items()
            },
            "DISCLOSURE_SILVER_TRAIN": silver,
            "LEGACY_PROTECTED": protected_rows,
        }
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_paths: dict[str, Path] = {}
    for partition, rows in review.items():
        output_path = args.output_dir / f"{partition.casefold()}.jsonl"
        _write_jsonl_atomic(output_path, [_review_payload(row, partition) for row in rows])
        output_paths[partition] = output_path
    args.silver_path.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl_atomic(args.silver_path, silver)

    report = {
        "schema_version": "k-fnspid-disclosure-sentiment-dataset-report/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset_version": "K-FNSPID-v4",
        "codebook_version": CODEBOOK_VERSION,
        "sampling_seed": args.seed,
        "source_audit": source_audit,
        "independence_contract": {
            "group_keys": [
                "canonical_url",
                "normalized_text",
                "content_hash",
                "event_cluster_id",
            ],
            "legacy_gold_role": "contaminated_regression_diagnostic_only",
            "sealed_test_policy": "candidate_hash_locked_before_first_label_evaluation",
        },
        "partitions": {
            **{
                name: {
                    **_file_report(
                        path, [_review_payload(row, name) for row in review[name]]
                    ),
                    "blind_sampling_distribution": dict(
                        sorted(
                            Counter(row.sampling_stratum for row in review[name]).items()
                        )
                    ),
                }
                for name, path in output_paths.items()
            },
            "DISCLOSURE_SILVER_TRAIN": _file_report(args.silver_path, silver),
        },
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(args.report_path, report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
