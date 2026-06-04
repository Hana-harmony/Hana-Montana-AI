from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    load_stock_universe,
    normalize_stock_term,
)

STOCK_LINKER_SCHEMA_VERSION = "stock-linker-training/v1"
STOCK_LINKER_MODEL_VERSION_PREFIX = "stock-linker-tfidf"
STOCK_LINKER_SIMILARITY_THRESHOLD = 0.58


@dataclass(frozen=True)
class StockLinkerTrainingRow:
    stock_code: str
    stock_name: str
    term: str
    normalized_term: str
    source: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class StockLinkerTrainingResult:
    rows: list[StockLinkerTrainingRow]
    report: dict[str, Any]


def build_stock_linker_training_rows(
    stock_universe: Sequence[StockUniverseEntry],
) -> list[StockLinkerTrainingRow]:
    rows: list[StockLinkerTrainingRow] = []
    seen: set[tuple[str, str]] = set()
    for stock in stock_universe:
        term_sources = [
            (stock.stock_code, "stock_code"),
            (stock.stock_name, "stock_name"),
            (stock.stock_name_en, "stock_name_en"),
            *[(alias, "alias") for alias in stock.aliases],
        ]
        for term, source in term_sources:
            normalized = normalize_stock_term(term)
            if not _is_trainable_stock_term(normalized):
                continue
            key = (stock.stock_code, normalized)
            if key in seen:
                continue
            rows.append(
                StockLinkerTrainingRow(
                    stock_code=stock.stock_code,
                    stock_name=stock.stock_name,
                    term=term,
                    normalized_term=normalized,
                    source=source,
                )
            )
            seen.add(key)
    return sorted(rows, key=lambda row: (row.stock_code, row.source, row.normalized_term))


def train_stock_linker_model(
    stock_universe_path: Path,
    model_path: Path,
    training_data_path: Path,
) -> StockLinkerTrainingResult:
    stock_universe = load_stock_universe(stock_universe_path)
    rows = build_stock_linker_training_rows(stock_universe)
    if not rows:
        raise ValueError("stock linker training requires at least one stock term")

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), lowercase=False)
    training_texts = [row.normalized_term for row in rows]
    term_matrix = vectorizer.fit_transform(training_texts)
    trained_at = datetime.now(UTC).isoformat()
    version = f"{STOCK_LINKER_MODEL_VERSION_PREFIX}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "schema_version": STOCK_LINKER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "vectorizer": vectorizer,
        "term_matrix": term_matrix,
        "rows": [row.to_dict() for row in rows],
        "similarity_threshold": STOCK_LINKER_SIMILARITY_THRESHOLD,
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)
    write_stock_linker_training_data(training_data_path, rows)
    report = build_stock_linker_report(
        version=version,
        trained_at=trained_at,
        stock_universe_path=stock_universe_path,
        model_path=model_path,
        training_data_path=training_data_path,
        stock_universe=stock_universe,
        rows=rows,
        vectorizer=vectorizer,
        term_matrix=term_matrix,
    )
    return StockLinkerTrainingResult(rows=rows, report=report)


def build_stock_linker_report(
    version: str,
    trained_at: str,
    stock_universe_path: Path,
    model_path: Path,
    training_data_path: Path,
    stock_universe: Sequence[StockUniverseEntry],
    rows: Sequence[StockLinkerTrainingRow],
    vectorizer: TfidfVectorizer,
    term_matrix: Any,
) -> dict[str, Any]:
    code_accuracy = _evaluate_template_accuracy(
        stock_universe,
        vectorizer,
        term_matrix,
        rows,
        template="{stock_code} 주요사항보고서 공시",
    )
    trainable_name_stocks = [
        stock
        for stock in stock_universe
        if _is_trainable_stock_term(normalize_stock_term(stock.stock_name))
    ]
    name_accuracy = _evaluate_template_accuracy(
        trainable_name_stocks,
        vectorizer,
        term_matrix,
        rows,
        template="{stock_name} 실적 개선 기대",
    )
    source_distribution = Counter(row.source for row in rows)
    stock_count = len({row.stock_code for row in rows})
    return {
        "schema_version": STOCK_LINKER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "stock_universe_path": _report_path(stock_universe_path),
        "model_path": _report_path(model_path),
        "training_data_path": _report_path(training_data_path),
        "universe_count": len(stock_universe),
        "training_row_count": len(rows),
        "training_stock_count": stock_count,
        "source_distribution": dict(sorted(source_distribution.items())),
        "similarity_threshold": STOCK_LINKER_SIMILARITY_THRESHOLD,
        "evaluation": {
            "all_stock_code_template_accuracy": code_accuracy,
            "trainable_stock_name_template_accuracy": name_accuracy,
        },
        "coverage_gate": {
            "minimum_training_stock_count": len(stock_universe),
            "actual_training_stock_count": stock_count,
            "status": "pass" if stock_count == len(stock_universe) else "fail",
        },
    }


def write_stock_linker_training_data(
    path: Path,
    rows: Sequence[StockLinkerTrainingRow],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row.to_dict(), ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_stock_linker_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _evaluate_template_accuracy(
    stock_universe: Sequence[StockUniverseEntry],
    vectorizer: TfidfVectorizer,
    term_matrix: Any,
    rows: Sequence[StockLinkerTrainingRow],
    template: str,
) -> float:
    if not stock_universe:
        return 0.0
    hits = 0
    for stock in stock_universe:
        text = normalize_stock_term(
            template.format(stock_code=stock.stock_code, stock_name=stock.stock_name)
        )
        query_vector = vectorizer.transform([text])
        similarities = cosine_similarity(query_vector, term_matrix)[0]
        best_index = int(similarities.argmax())
        if rows[best_index].stock_code == stock.stock_code:
            hits += 1
    return hits / len(stock_universe)


def _is_trainable_stock_term(value: str) -> bool:
    if value.isdigit() and len(value) == 6:
        return True
    return len(value) >= 3


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
