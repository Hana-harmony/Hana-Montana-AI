import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import KoreanFinancialTermExplainRequest
from hannah_montana_ai.services.korean_financial_terms import (
    KoreanFinancialTermExplanationService,
)


def main() -> None:
    args = _parse_args()
    settings = get_settings()
    service = KoreanFinancialTermExplanationService(
        seed_path=settings.korean_financial_terms_seed_path,
        model_version=settings.korean_financial_term_model_version,
    )
    rows = [_load_json(line) for line in args.gold_path.read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row]
    results: list[dict[str, Any]] = []
    for row in rows:
        request = KoreanFinancialTermExplainRequest(
            term=str(row["term"]),
            title=str(row.get("title", "")),
            context=str(row.get("context", "")),
            allow_web_search=False,
        )
        response = service.explain(request)
        passed = (
            response.normalized_term == row["expected_normalized_term"]
            and response.english_term == row["expected_english_term"]
            and response.source == row["expected_source"]
            and response.display_mode == row["expected_display_mode"]
            and response.confidence_score >= float(row["minimum_confidence"])
        )
        results.append(
            {
                "term": request.term,
                "passed": passed,
                "expected_source": row["expected_source"],
                "actual_source": response.source,
                "expected_display_mode": row["expected_display_mode"],
                "actual_display_mode": response.display_mode,
                "expected_normalized_term": row["expected_normalized_term"],
                "actual_normalized_term": response.normalized_term,
                "expected_english_term": row["expected_english_term"],
                "actual_english_term": response.english_term,
                "confidence_score": response.confidence_score,
                "cacheable": response.cacheable,
            }
        )
    passed_count = sum(1 for result in results if result["passed"])
    cacheable_count = sum(1 for result in results if result["cacheable"])
    dictionary_count = sum(1 for result in results if result["actual_source"] == "DICTIONARY")
    report = {
        "schema_version": "korean-financial-term-explanation-eval/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "model_version": settings.korean_financial_term_model_version,
        "sample_count": len(results),
        "passed_count": passed_count,
        "accuracy": round(passed_count / len(results), 6) if results else 0.0,
        "dictionary_coverage": round(dictionary_count / len(results), 6) if results else 0.0,
        "cacheable_rate": round(cacheable_count / len(results), 6) if results else 0.0,
        "quality_gate": "pass" if results and passed_count == len(results) else "fail",
        "rows": results,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    if report["quality_gate"] != "pass":
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Korean financial term explanation.")
    parser.add_argument(
        "--gold-path",
        type=Path,
        default=Path("data/evaluation/korean_financial_term_explanation_gold.jsonl"),
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("reports/korean-financial-term-explanation-eval.json"),
    )
    return parser.parse_args()


def _load_json(line: str) -> dict[str, Any]:
    if not line.strip():
        return {}
    parsed = json.loads(line)
    if not isinstance(parsed, dict):
        return {}
    return parsed


if __name__ == "__main__":
    main()
