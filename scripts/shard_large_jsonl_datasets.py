from __future__ import annotations

import argparse
from pathlib import Path

from hannah_montana_ai.training.collector import (
    raw_alert_to_dict,
    read_raw_alerts,
    write_sharded_jsonl,
)
from hannah_montana_ai.training.dataset import load_jsonl_payloads

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
DEFAULT_WEAK = PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="대규모 JSONL 데이터셋을 검증 가능한 shard manifest로 변환한다."
    )
    parser.add_argument("--raw-path", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--weak-path", type=Path, default=DEFAULT_WEAK)
    parser.add_argument("--rows-per-shard", type=int, default=50_000)
    args = parser.parse_args()

    raw_rows = [raw_alert_to_dict(row) for row in read_raw_alerts(args.raw_path)]
    weak_rows = load_jsonl_payloads(args.weak_path)
    write_sharded_jsonl(
        args.raw_path,
        raw_rows,
        rows_per_shard=args.rows_per_shard,
    )
    write_sharded_jsonl(
        args.weak_path,
        weak_rows,
        rows_per_shard=args.rows_per_shard,
    )
    print(f"raw={len(raw_rows)} weak={len(weak_rows)} rows_per_shard={args.rows_per_shard}")


if __name__ == "__main__":
    main()
