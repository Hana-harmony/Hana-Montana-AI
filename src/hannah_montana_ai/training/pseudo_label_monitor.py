from __future__ import annotations

from typing import Any

PSEUDO_LABEL_MONITOR_SCHEMA_VERSION = "pseudo-label-monitor/v1"
EXPANSION_CANDIDATE_MIN_HIGH_SIGNAL_COUNT = 500


def build_pseudo_label_monitoring_report(
    distillation_report: dict[str, Any],
    release_report: dict[str, Any],
) -> dict[str, Any]:
    high_signal_candidate_count = _high_signal_candidate_count(distillation_report)
    teacher_rejections = distillation_report.get("rejected_count_by_teacher_reason", {})
    teacher_rejected_count = sum(int(count) for count in teacher_rejections.values())
    promoted_count = int(distillation_report.get("accepted_count", 0))
    teacher_passed_not_promoted_count = max(
        high_signal_candidate_count - teacher_rejected_count - promoted_count,
        0,
    )
    labels = _label_monitoring_rows(distillation_report)
    gate_snapshot = _gate_snapshot(release_report)

    return {
        "schema_version": PSEUDO_LABEL_MONITOR_SCHEMA_VERSION,
        "model_version": release_report["model_version"],
        "report_created_at": release_report["report_created_at"],
        "overall_status": _overall_status(labels, gate_snapshot),
        "candidate_funnel": {
            "raw_candidate_count": distillation_report.get("candidate_count", 0),
            "high_signal_candidate_count": high_signal_candidate_count,
            "teacher_rejected_count": teacher_rejected_count,
            "teacher_rejected_count_by_reason": teacher_rejections,
            "teacher_passed_not_promoted_or_quota_limited_count": (
                teacher_passed_not_promoted_count
            ),
            "promoted_count": promoted_count,
        },
        "confidence_thresholds": {
            "minimum_event_confidence": distillation_report.get(
                "minimum_event_confidence",
            ),
            "minimum_sentiment_confidence": distillation_report.get(
                "minimum_sentiment_confidence",
            ),
            "minimum_importance_confidence": distillation_report.get(
                "minimum_importance_confidence",
            ),
        },
        "labels": labels,
        "quality_gate_snapshot": gate_snapshot,
        "expansion_policy": {
            "status": "guarded",
            "rule": (
                "zero_quota_labels_require_gold_gate_experiment_before_student_training"
            ),
            "minimum_expansion_candidate_high_signal_count": (
                EXPANSION_CANDIDATE_MIN_HIGH_SIGNAL_COUNT
            ),
        },
        "report_inputs": {
            "weak_distillation_report": "reports/weak-distillation-report.json",
            "model_release_report": "reports/model-release-report.json",
        },
    }


def _label_monitoring_rows(
    distillation_report: dict[str, Any],
) -> list[dict[str, Any]]:
    high_signal_counts = distillation_report.get("event_label_distribution", {})
    promoted_counts = distillation_report.get("accepted_count_by_primary_label", {})
    quotas = _effective_label_quotas(distillation_report)
    labels = sorted(set(high_signal_counts) | set(promoted_counts) | set(quotas))

    return [
        _label_monitoring_row(
            label,
            int(high_signal_counts.get(label, 0)),
            int(promoted_counts.get(label, 0)),
            int(quotas.get(label, 0)),
        )
        for label in labels
    ]


def _effective_label_quotas(distillation_report: dict[str, Any]) -> dict[str, int]:
    quotas = {
        label: int(quota)
        for label, quota in distillation_report.get("label_quotas", {}).items()
    }
    stock_quotas = distillation_report.get("stock_candidate_labeling", {}).get(
        "label_quotas",
        {},
    )
    for label, quota in stock_quotas.items():
        quotas[label] = quotas.get(label, 0) + int(quota)
    return quotas


def _label_monitoring_row(
    label: str,
    high_signal_count: int,
    promoted_count: int,
    quota: int,
) -> dict[str, Any]:
    if quota == 0 and high_signal_count >= EXPANSION_CANDIDATE_MIN_HIGH_SIGNAL_COUNT:
        decision = "expansion_candidate_hold_for_gold_gate"
    elif quota == 0:
        decision = "hold_low_pool_or_non_target_label"
    elif promoted_count >= quota:
        decision = "quota_filled"
    elif promoted_count > 0:
        decision = "under_quota_monitor"
    else:
        decision = "no_promotion_monitor"

    return {
        "label": label,
        "high_signal_event_count": high_signal_count,
        "student_training_quota": quota,
        "promoted_count": promoted_count,
        "promotion_rate_from_high_signal": _safe_ratio(
            promoted_count,
            high_signal_count,
        ),
        "decision": decision,
    }


def _gate_snapshot(release_report: dict[str, Any]) -> dict[str, Any]:
    gates = release_report.get("quality_gates", {})
    return {
        name: {
            "status": gate["status"],
            "sample_count": gate["sample_count"],
            "lowest_margin": min(
                metric["margin"] for metric in gate["metrics"].values()
            ),
        }
        for name, gate in gates.items()
    }


def _high_signal_candidate_count(distillation_report: dict[str, Any]) -> int:
    source_distribution = distillation_report.get("source_type_distribution", {})
    return sum(int(count) for count in source_distribution.values())


def _overall_status(
    labels: list[dict[str, Any]],
    gate_snapshot: dict[str, Any],
) -> str:
    gates_pass = all(gate["status"] == "pass" for gate in gate_snapshot.values())
    active_labels_have_promotions = all(
        label["promoted_count"] > 0
        for label in labels
        if label["student_training_quota"] > 0
    )
    return "pass" if gates_pass and active_labels_have_promotions else "fail"


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
