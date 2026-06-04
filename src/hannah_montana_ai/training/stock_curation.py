from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    StockUniverseMatcher,
    load_stock_universe,
)
from hannah_montana_ai.training.weak_distiller import (
    DISCLOSURE_NOISE_PATTERNS,
    HIGH_SIGNAL_PATTERNS,
    PRIMARY_LABEL_PRIORITY,
)
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert, weak_label

STOCK_CURATION_QUEUE_SCHEMA_VERSION = "stock-curation-queue/v1"
STOCK_CURATION_REPORT_SCHEMA_VERSION = "stock-curation-report/v1"
STOCK_GOLD_REVIEW_BATCH_SCHEMA_VERSION = "stock-gold-review-batch/v1"
STOCK_GOLD_REVIEW_REPORT_SCHEMA_VERSION = "stock-gold-review-report/v1"


@dataclass(frozen=True)
class StockTrainingCandidate:
    text: str
    tags: list[str]
    sentiment: str
    importance: str
    source_type: str
    stock_code: str
    stock_name: str
    primary_label: str
    signal_score: int
    original_url: str
    provider: str
    content_hash: str
    curation_status: str = "needs_human_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StockTrainingCandidateBuildResult:
    candidates: list[StockTrainingCandidate]
    report: dict[str, Any]


@dataclass(frozen=True)
class StockGoldReviewRow:
    review_key: str
    intended_split: str
    text: str
    tags: list[str]
    sentiment: str
    importance: str
    source_type: str
    stock_code: str
    stock_name: str
    primary_label: str
    signal_score: int
    original_url: str
    provider: str
    content_hash: str
    review_status: str = "needs_human_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StockGoldReviewBatchBuildResult:
    training_rows: list[StockGoldReviewRow]
    evaluation_rows: list[StockGoldReviewRow]
    report: dict[str, Any]


def build_stock_training_candidates(
    raw_alert_path: Path,
    stock_universe_path: Path,
    per_stock_label_quota: int = 2,
    minimum_signal_score: int = 3,
    minimum_stock_count: int = 300,
) -> StockTrainingCandidateBuildResult:
    stock_universe = load_stock_universe(stock_universe_path)
    matcher = StockUniverseMatcher(stock_universe)
    raw_alerts = _load_raw_alerts(raw_alert_path)
    stock_names = {stock.stock_code: stock.stock_name for stock in stock_universe}
    selected_by_bucket: dict[tuple[str, str], list[StockTrainingCandidate]] = defaultdict(list)
    rejected_reasons: Counter[str] = Counter()

    for alert in raw_alerts:
        stock = matcher.match_raw_alert(alert)
        if stock is None:
            rejected_reasons["stock_not_matched"] += 1
            continue
        labeled = weak_label(alert)
        if labeled is None:
            rejected_reasons["weak_label_missing"] += 1
            continue
        primary_label = _primary_label(labeled.tags)
        reason = _reject_reason(alert, primary_label)
        if reason:
            rejected_reasons[reason] += 1
            continue
        signal_score = _signal_score(alert.text, labeled.tags, labeled.importance, primary_label)
        if signal_score < minimum_signal_score:
            rejected_reasons["low_signal"] += 1
            continue
        candidate = StockTrainingCandidate(
            text=labeled.text,
            tags=labeled.tags,
            sentiment=labeled.sentiment,
            importance=labeled.importance,
            source_type=labeled.source_type,
            stock_code=stock.stock_code,
            stock_name=stock.stock_name,
            primary_label=primary_label,
            signal_score=signal_score,
            original_url=alert.original_url,
            provider=alert.provider,
            content_hash=alert.content_hash,
        )
        selected_by_bucket[(stock.stock_code, primary_label)].append(candidate)

    candidates = _select_balanced_candidates(selected_by_bucket, per_stock_label_quota)
    report = _build_report(
        raw_alert_path=raw_alert_path,
        stock_universe_path=stock_universe_path,
        raw_alerts=raw_alerts,
        stock_universe=stock_universe,
        stock_names=stock_names,
        candidates=candidates,
        rejected_reasons=rejected_reasons,
        per_stock_label_quota=per_stock_label_quota,
        minimum_signal_score=minimum_signal_score,
        minimum_stock_count=minimum_stock_count,
    )
    return StockTrainingCandidateBuildResult(candidates=candidates, report=report)


def build_stock_gold_review_batches(
    candidate_path: Path,
    training_paths: Sequence[Path],
    evaluation_paths: Sequence[Path],
    training_stock_target: int = 300,
    evaluation_stock_target: int = 100,
) -> StockGoldReviewBatchBuildResult:
    candidates = _load_stock_training_candidates(candidate_path)
    existing_training_stocks = _sample_stock_codes(training_paths)
    existing_evaluation_stocks = _sample_stock_codes(evaluation_paths)
    reserved_stocks = existing_training_stocks | existing_evaluation_stocks
    ranked_candidates = _rank_review_candidates(candidates)
    training_candidates = _select_review_candidates(
        ranked_candidates,
        excluded_stocks=reserved_stocks,
        target_stock_count=training_stock_target,
    )
    evaluation_candidates = _select_review_candidates(
        ranked_candidates,
        excluded_stocks=reserved_stocks
        | {candidate.stock_code for candidate in training_candidates},
        target_stock_count=evaluation_stock_target,
    )
    training_rows = [
        _to_review_row(candidate, intended_split="training")
        for candidate in training_candidates
    ]
    evaluation_rows = [
        _to_review_row(candidate, intended_split="evaluation")
        for candidate in evaluation_candidates
    ]
    report = _build_gold_review_report(
        candidate_path=candidate_path,
        candidates=candidates,
        training_rows=training_rows,
        evaluation_rows=evaluation_rows,
        existing_training_stocks=existing_training_stocks,
        existing_evaluation_stocks=existing_evaluation_stocks,
        training_stock_target=training_stock_target,
        evaluation_stock_target=evaluation_stock_target,
    )
    return StockGoldReviewBatchBuildResult(
        training_rows=training_rows,
        evaluation_rows=evaluation_rows,
        report=report,
    )


def write_stock_training_candidates(
    path: Path,
    candidates: Sequence[StockTrainingCandidate],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(candidate.to_dict(), ensure_ascii=False) + "\n"
            for candidate in candidates
        ),
        encoding="utf-8",
    )


def write_stock_gold_review_rows(
    path: Path,
    rows: Sequence[StockGoldReviewRow],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row.to_dict(), ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_stock_gold_review_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_stock_curation_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _select_balanced_candidates(
    selected_by_bucket: dict[tuple[str, str], list[StockTrainingCandidate]],
    per_stock_label_quota: int,
) -> list[StockTrainingCandidate]:
    selected: list[StockTrainingCandidate] = []
    for bucket, rows in sorted(selected_by_bucket.items()):
        del bucket
        ranked = sorted(rows, key=lambda row: (-row.signal_score, row.content_hash))
        selected.extend(ranked[:per_stock_label_quota])
    return sorted(selected, key=lambda row: (row.stock_code, row.primary_label, row.content_hash))


def _build_report(
    raw_alert_path: Path,
    stock_universe_path: Path,
    raw_alerts: Sequence[RawCollectedAlert],
    stock_universe: Sequence[StockUniverseEntry],
    stock_names: dict[str, str],
    candidates: Sequence[StockTrainingCandidate],
    rejected_reasons: Counter[str],
    per_stock_label_quota: int,
    minimum_signal_score: int,
    minimum_stock_count: int,
) -> dict[str, Any]:
    stock_distribution = Counter(candidate.stock_code for candidate in candidates)
    label_distribution = Counter(candidate.primary_label for candidate in candidates)
    source_distribution = Counter(candidate.source_type for candidate in candidates)
    sentiment_distribution = Counter(candidate.sentiment for candidate in candidates)
    importance_distribution = Counter(candidate.importance for candidate in candidates)
    stock_count = len(stock_distribution)
    gate = {
        "minimum_stock_count": minimum_stock_count,
        "actual_stock_count": stock_count,
        "status": "pass" if stock_count >= minimum_stock_count else "fail",
    }
    return {
        "schema_version": STOCK_CURATION_REPORT_SCHEMA_VERSION,
        "queue_schema_version": STOCK_CURATION_QUEUE_SCHEMA_VERSION,
        "raw_alert_path": _report_path(raw_alert_path),
        "stock_universe_path": _report_path(stock_universe_path),
        "raw_alert_count": len(raw_alerts),
        "universe_count": len(stock_universe),
        "candidate_count": len(candidates),
        "candidate_stock_count": stock_count,
        "candidate_coverage_ratio": _ratio(stock_count, len(stock_universe)),
        "per_stock_label_quota": per_stock_label_quota,
        "minimum_signal_score": minimum_signal_score,
        "curation_status": "needs_human_review",
        "coverage_gate": gate,
        "label_distribution": dict(sorted(label_distribution.items())),
        "source_type_distribution": dict(sorted(source_distribution.items())),
        "sentiment_distribution": dict(sorted(sentiment_distribution.items())),
        "importance_distribution": dict(sorted(importance_distribution.items())),
        "top_candidate_stocks": _top_stock_rows(stock_distribution, stock_names),
        "rejected_count_by_reason": dict(sorted(rejected_reasons.items())),
        "promotion_policy": (
            "queue rows are not treated as gold labels until human review promotes them"
        ),
    }


def _load_raw_alerts(path: Path) -> list[RawCollectedAlert]:
    if not path.exists():
        return []
    alerts: list[RawCollectedAlert] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        alerts.append(
            RawCollectedAlert(
                source_type=payload["source_type"],
                title=payload["title"],
                snippet=payload["snippet"],
                original_url=payload["original_url"],
                published_at=payload["published_at"],
                provider=payload["provider"],
            )
        )
    return alerts


def _reject_reason(alert: RawCollectedAlert, primary_label: str) -> str | None:
    if primary_label == "GENERAL_MARKET":
        return "general_market_not_stock_specific"
    if alert.source_type == "DISCLOSURE" and any(
        pattern in alert.text for pattern in DISCLOSURE_NOISE_PATTERNS
    ):
        return "disclosure_noise"
    return None


def _signal_score(
    text: str,
    tags: Iterable[str],
    importance: str,
    primary_label: str,
) -> int:
    score = sum(1 for pattern in HIGH_SIGNAL_PATTERNS.get(primary_label, ()) if pattern in text)
    for tag in tags:
        score += sum(1 for pattern in HIGH_SIGNAL_PATTERNS.get(tag, ()) if pattern in text)
    if importance in {"HIGH", "CRITICAL"}:
        score += 1
    return score


def _primary_label(tags: Sequence[str]) -> str:
    tag_set = set(tags)
    for label in PRIMARY_LABEL_PRIORITY:
        if label in tag_set:
            return label
    return "GENERAL_MARKET"


def _top_stock_rows(
    stock_distribution: Counter[str],
    stock_names: dict[str, str],
    limit: int = 20,
) -> list[dict[str, int | str]]:
    return [
        {
            "stock_code": stock_code,
            "stock_name": stock_names.get(stock_code, ""),
            "candidate_count": count,
        }
        for stock_code, count in stock_distribution.most_common(limit)
    ]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def candidate_review_key(candidate: StockTrainingCandidate) -> str:
    return sha256(
        f"{candidate.source_type}:{candidate.stock_code}:{candidate.primary_label}:"
        f"{candidate.content_hash}".encode()
    ).hexdigest()


def _load_stock_training_candidates(path: Path) -> list[StockTrainingCandidate]:
    if not path.exists():
        return []
    candidates: list[StockTrainingCandidate] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        candidates.append(
            StockTrainingCandidate(
                text=payload["text"],
                tags=list(payload["tags"]),
                sentiment=payload["sentiment"],
                importance=payload["importance"],
                source_type=payload["source_type"],
                stock_code=payload["stock_code"],
                stock_name=payload["stock_name"],
                primary_label=payload["primary_label"],
                signal_score=int(payload["signal_score"]),
                original_url=payload["original_url"],
                provider=payload["provider"],
                content_hash=payload["content_hash"],
                curation_status=payload.get("curation_status", "needs_human_review"),
            )
        )
    return candidates


def _sample_stock_codes(paths: Sequence[Path]) -> set[str]:
    stock_codes: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            stock_code = payload.get("stock_code")
            if isinstance(stock_code, str) and stock_code:
                stock_codes.add(stock_code)
    return stock_codes


def _rank_review_candidates(
    candidates: Sequence[StockTrainingCandidate],
) -> list[StockTrainingCandidate]:
    return sorted(
        candidates,
        key=lambda row: (
            _label_rank(row.primary_label),
            -row.signal_score,
            row.stock_code,
            row.content_hash,
        ),
    )


def _select_review_candidates(
    candidates: Sequence[StockTrainingCandidate],
    excluded_stocks: set[str],
    target_stock_count: int,
) -> list[StockTrainingCandidate]:
    selected: list[StockTrainingCandidate] = []
    seen_stocks: set[str] = set()
    buckets: dict[str, list[StockTrainingCandidate]] = defaultdict(list)
    for candidate in candidates:
        buckets[candidate.primary_label].append(candidate)
    labels = sorted(buckets, key=_label_rank)
    while len(selected) < target_stock_count:
        added_this_round = False
        for label in labels:
            while buckets[label]:
                candidate = buckets[label].pop(0)
                if (
                    candidate.stock_code in excluded_stocks
                    or candidate.stock_code in seen_stocks
                ):
                    continue
                selected.append(candidate)
                seen_stocks.add(candidate.stock_code)
                added_this_round = True
                break
            if len(selected) == target_stock_count:
                break
        if not added_this_round:
            break
    return selected


def _to_review_row(
    candidate: StockTrainingCandidate,
    intended_split: str,
) -> StockGoldReviewRow:
    return StockGoldReviewRow(
        review_key=candidate_review_key(candidate),
        intended_split=intended_split,
        text=candidate.text,
        tags=candidate.tags,
        sentiment=candidate.sentiment,
        importance=candidate.importance,
        source_type=candidate.source_type,
        stock_code=candidate.stock_code,
        stock_name=candidate.stock_name,
        primary_label=candidate.primary_label,
        signal_score=candidate.signal_score,
        original_url=candidate.original_url,
        provider=candidate.provider,
        content_hash=candidate.content_hash,
    )


def _build_gold_review_report(
    candidate_path: Path,
    candidates: Sequence[StockTrainingCandidate],
    training_rows: Sequence[StockGoldReviewRow],
    evaluation_rows: Sequence[StockGoldReviewRow],
    existing_training_stocks: set[str],
    existing_evaluation_stocks: set[str],
    training_stock_target: int,
    evaluation_stock_target: int,
) -> dict[str, Any]:
    training_stock_codes = {row.stock_code for row in training_rows}
    evaluation_stock_codes = {row.stock_code for row in evaluation_rows}
    return {
        "schema_version": STOCK_GOLD_REVIEW_REPORT_SCHEMA_VERSION,
        "batch_schema_version": STOCK_GOLD_REVIEW_BATCH_SCHEMA_VERSION,
        "candidate_path": _report_path(candidate_path),
        "candidate_count": len(candidates),
        "candidate_stock_count": len({candidate.stock_code for candidate in candidates}),
        "existing_training_stock_count": len(existing_training_stocks),
        "existing_evaluation_stock_count": len(existing_evaluation_stocks),
        "training_review": _review_split_report(
            training_rows,
            target_stock_count=training_stock_target,
            actual_stock_count=len(training_stock_codes),
        ),
        "evaluation_review": _review_split_report(
            evaluation_rows,
            target_stock_count=evaluation_stock_target,
            actual_stock_count=len(evaluation_stock_codes),
        ),
        "disjoint_stock_check": {
            "status": (
                "pass"
                if training_stock_codes.isdisjoint(evaluation_stock_codes)
                else "fail"
            )
        },
        "promotion_policy": (
            "review rows are not supervised or gold labels until human_review_approved"
        ),
    }


def _review_split_report(
    rows: Sequence[StockGoldReviewRow],
    target_stock_count: int,
    actual_stock_count: int,
) -> dict[str, Any]:
    return {
        "target_stock_count": target_stock_count,
        "actual_row_count": len(rows),
        "actual_stock_count": actual_stock_count,
        "status": "pass" if actual_stock_count >= target_stock_count else "fail",
        "label_distribution": dict(
            sorted(Counter(row.primary_label for row in rows).items())
        ),
        "source_type_distribution": dict(
            sorted(Counter(row.source_type for row in rows).items())
        ),
        "review_status": "needs_human_review",
    }


def _label_rank(label: str) -> int:
    try:
        return PRIMARY_LABEL_PRIORITY.index(label)
    except ValueError:
        return len(PRIMARY_LABEL_PRIORITY)
