from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel

STOCK_GOLD_ACTIVE_REVIEW_REPORT_SCHEMA_VERSION = "stock-gold-active-review-report/v1"
STOCK_GOLD_COVERAGE_ACTIVE_REVIEW_REPORT_SCHEMA_VERSION = (
    "stock-gold-coverage-active-review-report/v1"
)
STOCK_GOLD_COVERAGE_ACTIVE_REVIEW_PACKET_SCHEMA_VERSION = (
    "stock-gold-coverage-active-review-packet/v1"
)


def build_stock_gold_active_review_report(
    training_review_path: Path,
    evaluation_review_path: Path,
    model_path: Path,
    top_n_per_split: int = 50,
) -> dict[str, Any]:
    model = MachineLearningFinancialNlpModel(model_path)
    training_rows = _load_jsonl(training_review_path)
    evaluation_rows = _load_jsonl(evaluation_review_path)
    training_suggestions = _build_split_suggestions(
        rows=training_rows,
        split="training",
        model=model,
        top_n=top_n_per_split,
    )
    evaluation_suggestions = _build_split_suggestions(
        rows=evaluation_rows,
        split="evaluation",
        model=model,
        top_n=top_n_per_split,
    )
    return {
        "schema_version": STOCK_GOLD_ACTIVE_REVIEW_REPORT_SCHEMA_VERSION,
        "model_version": model.version,
        "model_path": _report_path(model_path),
        "top_n_per_split": top_n_per_split,
        "training_review": training_suggestions,
        "evaluation_review": evaluation_suggestions,
        "review_policy": (
            "model suggestions are reviewer assistance only and are not promoted "
            "without human_review_approved final labels"
        ),
    }


def build_stock_gold_coverage_active_review_report(
    coverage_plan_path: Path,
    model_path: Path,
    top_n_per_split: int = 100,
    top_n_per_wave: int = 10,
) -> dict[str, Any]:
    model = MachineLearningFinancialNlpModel(model_path)
    rows = _load_jsonl(coverage_plan_path)
    packet_rows = _build_coverage_packet_rows(rows, model)
    training_rows = [row for row in packet_rows if row.get("intended_split") == "training"]
    evaluation_rows = [row for row in packet_rows if row.get("intended_split") == "evaluation"]
    training_suggestions = _build_coverage_split_suggestions(
        rows=training_rows,
        top_n_per_split=top_n_per_split,
        top_n_per_wave=top_n_per_wave,
    )
    evaluation_suggestions = _build_coverage_split_suggestions(
        rows=evaluation_rows,
        top_n_per_split=top_n_per_split,
        top_n_per_wave=top_n_per_wave,
    )
    return {
        "schema_version": STOCK_GOLD_COVERAGE_ACTIVE_REVIEW_REPORT_SCHEMA_VERSION,
        "model_version": model.version,
        "model_path": _report_path(model_path),
        "coverage_plan_path": _report_path(coverage_plan_path),
        "top_n_per_split": top_n_per_split,
        "top_n_per_wave": top_n_per_wave,
        "training_review": training_suggestions,
        "evaluation_review": evaluation_suggestions,
        "review_policy": (
            "coverage plan suggestions are reviewer assistance only and are not "
            "promoted without human_review_approved final labels"
        ),
    }


def build_stock_gold_coverage_active_review_packet(
    coverage_plan_path: Path,
    model_path: Path,
) -> list[dict[str, Any]]:
    model = MachineLearningFinancialNlpModel(model_path)
    rows = _load_jsonl(coverage_plan_path)
    return _build_coverage_packet_rows(rows, model)


def write_stock_gold_active_review_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_stock_gold_active_review_packet(
    path: Path,
    rows: Sequence[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _build_split_suggestions(
    rows: Sequence[dict[str, Any]],
    split: str,
    model: MachineLearningFinancialNlpModel,
    top_n: int,
) -> dict[str, Any]:
    suggestions = [_suggest_review_row(row, split, model) for row in rows]
    ranked = sorted(
        suggestions,
        key=lambda row: (
            -float(row["review_priority_score"]),
            str(row["stock_code"]),
            str(row["review_key"]),
        ),
    )
    disagreement_counter = Counter(
        reason
        for row in suggestions
        for reason in row["disagreement_reasons"]
    )
    return {
        "review_row_count": len(rows),
        "suggestion_count": len(suggestions),
        "top_priority_rows": ranked[:top_n],
        "disagreement_count_by_reason": dict(sorted(disagreement_counter.items())),
        "average_review_priority_score": _average(
            float(row["review_priority_score"]) for row in suggestions
        ),
    }


def _build_coverage_split_suggestions(
    rows: Sequence[dict[str, Any]],
    top_n_per_split: int,
    top_n_per_wave: int,
) -> dict[str, Any]:
    ranked = _rank_suggestions(rows)
    disagreement_counter = Counter(
        reason
        for row in rows
        for reason in row["disagreement_reasons"]
    )
    stage_counter = Counter(str(row["review_stage"]) for row in rows)
    return {
        "review_row_count": len(rows),
        "suggestion_count": len(rows),
        "top_priority_rows": ranked[:top_n_per_split],
        "wave_priority_rows": _top_rows_by_wave(ranked, top_n_per_wave),
        "review_wave_count": len({int(row["review_wave"]) for row in rows}),
        "disagreement_count_by_reason": dict(sorted(disagreement_counter.items())),
        "review_stage_distribution": dict(sorted(stage_counter.items())),
        "average_review_priority_score": _average(
            float(row["review_priority_score"]) for row in rows
        ),
    }


def _suggest_review_row(
    row: dict[str, Any],
    split: str,
    model: MachineLearningFinancialNlpModel,
) -> dict[str, Any]:
    text = str(row["text"])
    source_type = str(row["source_type"])
    event_scores = model.event_tag_probabilities(text, source_type)
    suggested_tags = model.predict_event_tags(text, source_type)
    sentiment_scores = model.sentiment_probabilities(text)
    suggested_sentiment, sentiment_confidence = _top_label(sentiment_scores)
    importance_scores = model.importance_probabilities(text, source_type)
    suggested_importance, importance_confidence = _top_label(importance_scores)
    event_top_label, event_confidence = _top_label(event_scores)
    event_margin = _top_margin(event_scores)
    original_tags = {str(tag) for tag in row.get("tags", [])}
    suggested_tag_set = set(suggested_tags)
    disagreement_reasons = _disagreement_reasons(
        original_tags=original_tags,
        suggested_tags=suggested_tag_set,
        original_sentiment=str(row["sentiment"]),
        suggested_sentiment=suggested_sentiment,
        original_importance=str(row["importance"]),
        suggested_importance=suggested_importance,
    )
    priority_score = _review_priority_score(
        disagreement_count=len(disagreement_reasons),
        event_confidence=event_confidence,
        event_margin=event_margin,
        sentiment_confidence=sentiment_confidence,
        importance_confidence=importance_confidence,
        signal_score=int(row.get("signal_score", 0) or 0),
    )
    return {
        "review_key": row["review_key"],
        "intended_split": split,
        "stock_code": row["stock_code"],
        "stock_name": row["stock_name"],
        "source_type": source_type,
        "primary_label": row["primary_label"],
        "original_tags": sorted(original_tags),
        "suggested_tags": suggested_tags,
        "suggested_sentiment": suggested_sentiment,
        "suggested_importance": suggested_importance,
        "event_top_label": event_top_label,
        "event_confidence": round(event_confidence, 6),
        "event_margin": round(event_margin, 6),
        "sentiment_confidence": round(sentiment_confidence, 6),
        "importance_confidence": round(importance_confidence, 6),
        "disagreement_reasons": disagreement_reasons,
        "review_priority_score": round(priority_score, 6),
        "original_url": row["original_url"],
    }


def _coverage_suggest_review_row(
    suggestion: dict[str, Any],
    original_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        **suggestion,
        "review_wave": int(original_row.get("review_wave", 0) or 0),
        "review_stage": str(original_row.get("review_stage", "")),
        "review_reason": str(original_row.get("review_reason", "")),
    }


def _build_coverage_packet_rows(
    rows: Sequence[dict[str, Any]],
    model: MachineLearningFinancialNlpModel,
) -> list[dict[str, Any]]:
    packet_rows = [
        _coverage_packet_row(
            suggestion=_coverage_suggest_review_row(
                _suggest_review_row(row, str(row["intended_split"]), model),
                row,
            ),
            original_row=row,
        )
        for row in rows
    ]
    return sorted(
        packet_rows,
        key=lambda row: (
            str(row["intended_split"]),
            int(row["review_wave"]),
            -float(row["review_priority_score"]),
            str(row["stock_code"]),
            str(row["review_key"]),
        ),
    )


def _coverage_packet_row(
    suggestion: dict[str, Any],
    original_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": STOCK_GOLD_COVERAGE_ACTIVE_REVIEW_PACKET_SCHEMA_VERSION,
        "review_key": suggestion["review_key"],
        "intended_split": suggestion["intended_split"],
        "review_wave": suggestion["review_wave"],
        "review_stage": suggestion["review_stage"],
        "review_reason": suggestion["review_reason"],
        "review_status": original_row.get("review_status", "needs_human_review"),
        "reviewer_id": original_row.get("reviewer_id", ""),
        "reviewed_at": original_row.get("reviewed_at", ""),
        "review_notes": original_row.get("review_notes", ""),
        "text": original_row["text"],
        "stock_code": suggestion["stock_code"],
        "stock_name": suggestion["stock_name"],
        "source_type": suggestion["source_type"],
        "primary_label": suggestion["primary_label"],
        "tags": list(original_row.get("tags", [])),
        "sentiment": original_row["sentiment"],
        "importance": original_row["importance"],
        "suggested_tags": suggestion["suggested_tags"],
        "suggested_sentiment": suggestion["suggested_sentiment"],
        "suggested_importance": suggestion["suggested_importance"],
        "event_top_label": suggestion["event_top_label"],
        "event_confidence": suggestion["event_confidence"],
        "event_margin": suggestion["event_margin"],
        "sentiment_confidence": suggestion["sentiment_confidence"],
        "importance_confidence": suggestion["importance_confidence"],
        "disagreement_reasons": suggestion["disagreement_reasons"],
        "review_priority_score": suggestion["review_priority_score"],
        "final_tags": original_row.get("final_tags", []),
        "final_sentiment": original_row.get("final_sentiment", ""),
        "final_importance": original_row.get("final_importance", ""),
        "original_url": suggestion["original_url"],
        "provider": original_row["provider"],
        "content_hash": original_row["content_hash"],
    }


def _rank_suggestions(
    suggestions: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        suggestions,
        key=lambda row: (
            -float(row["review_priority_score"]),
            int(row.get("review_wave", 0) or 0),
            str(row["stock_code"]),
            str(row["review_key"]),
        ),
    )


def _top_rows_by_wave(
    ranked: Sequence[dict[str, Any]],
    top_n_per_wave: int,
) -> dict[str, list[dict[str, Any]]]:
    rows_by_wave: dict[str, list[dict[str, Any]]] = {}
    for row in ranked:
        wave = str(row.get("review_wave", 0))
        if len(rows_by_wave.setdefault(wave, [])) >= top_n_per_wave:
            continue
        rows_by_wave[wave].append(row)
    return dict(sorted(rows_by_wave.items(), key=lambda item: int(item[0])))


def _disagreement_reasons(
    original_tags: set[str],
    suggested_tags: set[str],
    original_sentiment: str,
    suggested_sentiment: str,
    original_importance: str,
    suggested_importance: str,
) -> list[str]:
    reasons: list[str] = []
    if not original_tags.intersection(suggested_tags):
        reasons.append("event_tag_disagreement")
    if original_sentiment != suggested_sentiment:
        reasons.append("sentiment_disagreement")
    if original_importance != suggested_importance:
        reasons.append("importance_disagreement")
    return reasons


def _review_priority_score(
    disagreement_count: int,
    event_confidence: float,
    event_margin: float,
    sentiment_confidence: float,
    importance_confidence: float,
    signal_score: int,
) -> float:
    uncertainty_score = (
        (1.0 - event_confidence) * 35.0
        + (1.0 - event_margin) * 25.0
        + (1.0 - sentiment_confidence) * 20.0
        + (1.0 - importance_confidence) * 20.0
    )
    return disagreement_count * 100.0 + uncertainty_score + min(signal_score, 10) * 2.0


def _top_label(scores: dict[str, float]) -> tuple[str, float]:
    if not scores:
        return "", 0.0
    label, score = max(scores.items(), key=lambda item: item[1])
    return label, score


def _top_margin(scores: dict[str, float]) -> float:
    if len(scores) < 2:
        return 1.0
    ordered_scores = sorted(scores.values(), reverse=True)
    return max(0.0, ordered_scores[0] - ordered_scores[1])


def _average(values: Iterable[float]) -> float:
    collected_values = list(values)
    if not collected_values:
        return 0.0
    return sum(collected_values) / len(collected_values)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
