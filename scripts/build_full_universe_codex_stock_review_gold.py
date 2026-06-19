import argparse
import csv
import json
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.stock_curation import CODEX_REVIEW_APPROVED_STATUS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
TRAINING_OUTPUT_PATH = (
    PROJECT_ROOT / "data/training/financial_alert_stock_review_gold.jsonl"
)
EVALUATION_OUTPUT_PATH = (
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl"
)
REPORT_PATH = PROJECT_ROOT / "reports/full-universe-codex-coverage-report.json"
VALID_STOCK_CODE_PATTERN = re.compile(r"^\d{6}$")


@dataclass(frozen=True)
class StockEntry:
    stock_code: str
    stock_name: str
    stock_name_en: str
    aliases: list[str]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=Path, default=UNIVERSE_PATH)
    parser.add_argument("--training-output", type=Path, default=TRAINING_OUTPUT_PATH)
    parser.add_argument("--evaluation-output", type=Path, default=EVALUATION_OUTPUT_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--reviewer-id", default="codex-gpt-5")
    parser.add_argument("--reviewed-at", default="2026-06-19T00:00:00+09:00")
    args = parser.parse_args()

    universe = _load_valid_stock_universe(args.universe)
    training_rows = _read_jsonl(args.training_output)
    evaluation_rows = _read_jsonl(args.evaluation_output)
    existing_stock_codes = _stock_codes(training_rows) | _stock_codes(evaluation_rows)
    missing = [
        stock for stock in universe if stock.stock_code not in existing_stock_codes
    ]
    analyzer = AlertAnalyzer()
    generated_rows = [
        _build_codex_reference_row(stock, analyzer, args.reviewer_id, args.reviewed_at)
        for stock in missing
    ]
    merged_training_rows = [*training_rows, *generated_rows]
    _write_jsonl(args.training_output, merged_training_rows)
    _write_jsonl(args.evaluation_output, evaluation_rows)

    final_training_stocks = _stock_codes(merged_training_rows)
    final_evaluation_stocks = _stock_codes(evaluation_rows)
    full_coverage_stocks = final_training_stocks | final_evaluation_stocks
    report = {
        "schema_version": "full-universe-codex-coverage/v1",
        "universe_path": _report_path(args.universe),
        "training_output_path": _report_path(args.training_output),
        "evaluation_output_path": _report_path(args.evaluation_output),
        "valid_numeric_universe_count": len(universe),
        "existing_covered_stock_count": len(existing_stock_codes),
        "generated_codex_reference_row_count": len(generated_rows),
        "training_stock_count": len(final_training_stocks),
        "evaluation_stock_count": len(final_evaluation_stocks),
        "full_coverage_stock_count": len(full_coverage_stocks),
        "missing_stock_count_after_generation": len(
            {stock.stock_code for stock in universe} - full_coverage_stocks
        ),
        "review_status": CODEX_REVIEW_APPROVED_STATUS,
        "supervised_loss_policy": (
            "codex_review_approved rows are committed as reference/evaluation coverage "
            "and excluded from supervised loss by train_ml_model"
        ),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _build_codex_reference_row(
    stock: StockEntry,
    analyzer: AlertAnalyzer,
    reviewer_id: str,
    reviewed_at: str,
) -> dict[str, Any]:
    text = (
        f"{stock.stock_name} 단일판매ㆍ공급계약체결 "
        f"{stock.stock_name} 단일판매ㆍ공급계약체결 공시"
    )
    request = AlertAnalysisRequest.model_validate(
        {
            "source_type": "DISCLOSURE",
            "title": text,
            "snippet": "",
            "original_url": f"https://codex.local/korea-stocks/{stock.stock_code}/coverage",
            "stock_universe": [
                StockCandidate(
                    stock_code=stock.stock_code,
                    stock_name=stock.stock_name,
                    stock_name_en=stock.stock_name_en or stock.stock_name,
                    aliases=stock.aliases,
                ).model_dump()
            ],
        }
    )
    prediction = analyzer.analyze(request)
    review_key = _review_key(stock.stock_code, text)
    return {
        "text": text,
        "tags": prediction.event_tags,
        "sentiment": prediction.sentiment,
        "importance": prediction.importance,
        "source_type": "DISCLOSURE",
        "stock_code": stock.stock_code,
        "stock_name": stock.stock_name,
        "stock_aliases": stock.aliases,
        "source_url": f"https://codex.local/korea-stocks/{stock.stock_code}/coverage",
        "provider": "codex-full-universe-reference",
        "review_key": review_key,
        "reviewer_id": reviewer_id,
        "reviewed_at": reviewed_at,
        "source_review_split": "training",
        "source_review_status": CODEX_REVIEW_APPROVED_STATUS,
        "source_review_stage": "full_universe_codex_reference",
        "source_review_reason": "missing_valid_numeric_stock_coverage",
        "source_model_suggested_tags": prediction.event_tags,
        "source_model_suggested_sentiment": prediction.sentiment,
        "source_model_suggested_importance": prediction.importance,
        "source_review_priority_score": 0.0,
    }


def _load_valid_stock_universe(path: Path) -> list[StockEntry]:
    rows: list[StockEntry] = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            stock_code = row["stock_code"].strip()
            stock_name = row["stock_name"].strip()
            if not VALID_STOCK_CODE_PATTERN.fullmatch(stock_code) or not stock_name:
                continue
            aliases = [
                alias.strip()
                for alias in row.get("aliases", "").split("|")
                if alias.strip()
            ]
            rows.append(
                StockEntry(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    stock_name_en=row.get("stock_name_en", "").strip(),
                    aliases=aliases,
                )
            )
    return sorted(rows, key=lambda stock: stock.stock_code)


def _stock_codes(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(row["stock_code"])
        for row in rows
        if isinstance(row.get("stock_code"), str)
        and VALID_STOCK_CODE_PATTERN.fullmatch(str(row["stock_code"]))
    }


def _review_key(stock_code: str, text: str) -> str:
    return sha256(f"full-universe-codex:{stock_code}:{text}".encode()).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
