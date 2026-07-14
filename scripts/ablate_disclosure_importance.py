from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from train_disclosure_importance_model import (
    DEFAULT_GOLD,
    DEFAULT_TRAINING,
    _critical_augmentations,
    _evaluate,
    _select_probability_temperature,
    _source_manifest,
    _training_rows,
    build_model,
)

from hannah_montana_ai.training.dataset import load_jsonl_payloads

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = PROJECT_ROOT / "reports/disclosure-importance-ablation-report.json"
FEATURE_SETS = {
    "title_only": ("title",),
    "title_and_snippet": ("title", "snippet"),
    "title_snippet_full_content": ("title", "snippet", "full_content"),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="공시 의미 중요도 입력 feature ablation을 동일 시간 분할로 평가한다."
    )
    parser.add_argument("--training-path", type=Path, default=DEFAULT_TRAINING)
    parser.add_argument("--gold-path", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    gold_rows = load_jsonl_payloads(args.gold_path)
    gold_urls = {str(row.get("source_url", "")) for row in gold_rows}
    source_rows = load_jsonl_payloads(args.training_path)
    training_rows = [*_training_rows(source_rows, gold_urls), *_critical_augmentations()]
    train_rows = [row for row in training_rows if str(row["published_at"]) < "20260101"]
    validation_rows = [row for row in training_rows if str(row["published_at"]) >= "20260101"]

    runs: dict[str, Any] = {}
    for name, fields in FEATURE_SETS.items():
        projected_train = _project_rows(train_rows, fields)
        projected_validation = _project_rows(validation_rows, fields)
        projected_final = _project_rows(training_rows, fields)
        projected_gold = _project_rows(gold_rows, fields)

        validation_model = build_model()
        validation_model.fit(
            [str(row["text"]) for row in projected_train],
            [str(row["importance"]) for row in projected_train],
        )
        temperature = _select_probability_temperature(
            validation_model,
            projected_validation,
        )
        validation = _evaluate(validation_model, projected_validation, temperature)

        final_model = build_model()
        final_model.fit(
            [str(row["text"]) for row in projected_final],
            [str(row["importance"]) for row in projected_final],
        )
        runs[name] = {
            "fields": list(fields),
            "temperature": temperature,
            "validation": validation,
            "gold_test": _evaluate(final_model, projected_gold, temperature),
        }

    report = {
        "schema_version": "disclosure-importance-ablation/v1",
        "protocol": (
            "동일 약지도 Train/2026 Validation/URL 비중복 Gold; feature별 독립 학습; "
            "Gold는 feature 선택에 사용하지 않음"
        ),
        "training_source": _source_manifest(args.training_path),
        "gold_source": _source_manifest(args.gold_path),
        "gold_url_overlap_count": sum(
            str(row.get("source_url", "")) in gold_urls for row in training_rows
        ),
        "partition_count": {
            "TRAIN": len(train_rows),
            "VALIDATION": len(validation_rows),
            "FINAL_TRAIN": len(training_rows),
            "GOLD_TEST": len(gold_rows),
        },
        "runs": runs,
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _project_rows(
    rows: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for row in rows:
        text = " ".join(str(row.get(field, "")).strip() for field in fields if row.get(field))
        if not text:
            text = str(row.get("text", "")).strip()
        copy = {
            key: value
            for key, value in row.items()
            if key not in {"title", "snippet", "full_content"}
        }
        copy["text"] = text
        projected.append(copy)
    return projected


if __name__ == "__main__":
    main()
