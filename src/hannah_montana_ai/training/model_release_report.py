from __future__ import annotations

from typing import Any

MODEL_RELEASE_REPORT_SCHEMA_VERSION = "model-release-report/v1"
MODEL_ARTIFACT_PATH = "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
MINIMUM_BOOTSTRAP_STOCK_CANDIDATE_COUNT = 500

QUALITY_GATE_THRESHOLDS: dict[str, dict[str, float]] = {
    "holdout": {
        "event_subset_recall": 0.80,
        "event_macro_f1": 0.80,
        "sentiment_accuracy": 0.80,
        "importance_accuracy": 0.80,
    },
    "benchmark": {
        "event_tag_recall": 0.80,
        "event_macro_f1": 0.80,
        "sentiment_accuracy": 0.85,
        "importance_accuracy": 0.80,
        "stock_accuracy": 1.00,
    },
    "real_disclosure_gold": {
        "event_tag_recall": 0.90,
        "event_macro_f1": 0.90,
        "sentiment_accuracy": 0.90,
        "importance_accuracy": 0.90,
        "stock_accuracy": 1.00,
    },
    "real_news_gold": {
        "event_tag_recall": 0.90,
        "event_macro_f1": 0.90,
        "sentiment_accuracy": 0.90,
        "importance_accuracy": 0.90,
        "stock_accuracy": 1.00,
    },
}


def build_model_release_report(
    training_report: dict[str, Any],
    evaluation_report: dict[str, Any],
    distillation_report: dict[str, Any],
    coverage_validation_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    quality_gates = _build_quality_gates(training_report, evaluation_report)
    consistency_checks = _build_consistency_checks(training_report, distillation_report)
    overall_status = _overall_status(quality_gates, consistency_checks)
    service_readiness = _build_service_readiness(
        quality_gates,
        consistency_checks,
        distillation_report,
    )
    audited_gold_readiness = _build_audited_gold_readiness(coverage_validation_report)

    return {
        "schema_version": MODEL_RELEASE_REPORT_SCHEMA_VERSION,
        "model_version": training_report["version"],
        "report_created_at": training_report["trained_at"],
        "overall_status": overall_status,
        "artifact": {
            "path": MODEL_ARTIFACT_PATH,
            "trained_at": training_report["trained_at"],
            "event_probability_threshold": training_report["event_probability_threshold"],
            "event_label_thresholds": training_report.get("event_label_thresholds", {}),
        },
        "data_lineage": {
            "training_sources": training_report["training_sources"],
            "weak_label_source": distillation_report.get("source_path"),
            "committed_data_policy": "raw_and_processed_training_data_are_tracked",
            "full_content_training": training_report.get("full_content_training", {}),
            "sentiment_importance_training": training_report.get(
                "sentiment_importance_training",
                {},
            ),
        },
        "training": {
            "sample_count": training_report["sample_count"],
            "supervised_sample_count": training_report["supervised_sample_count"],
            "pseudo_labeled_sample_count": training_report["pseudo_labeled_sample_count"],
            "event_label_distribution": training_report["event_label_distribution"],
            "sentiment_label_distribution": training_report["sentiment_label_distribution"],
            "importance_label_distribution": training_report["importance_label_distribution"],
        },
        "pseudo_labeling": _build_pseudo_labeling_summary(
            training_report,
            distillation_report,
        ),
        "quality_gates": quality_gates,
        "consistency_checks": consistency_checks,
        "service_readiness": service_readiness,
        "audited_gold_readiness": audited_gold_readiness,
        "weakest_event_labels": _build_weakest_event_labels(evaluation_report),
        "report_inputs": {
            "training_report": "reports/ml-training-report.json",
            "evaluation_report": "reports/ml-model-evaluation.json",
            "weak_distillation_report": "reports/weak-distillation-report.json",
            "coverage_validation_report": (
                "reports/stock-gold-coverage-validation-report.json"
                if coverage_validation_report is not None
                else None
            ),
        },
    }


def _build_quality_gates(
    training_report: dict[str, Any],
    evaluation_report: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    datasets = {
        "holdout": training_report["validation"],
        "benchmark": evaluation_report["benchmark"],
        "real_disclosure_gold": evaluation_report["real_disclosure_gold"],
        "real_news_gold": evaluation_report["real_news_gold"],
    }

    return {
        dataset_name: _build_dataset_gate(
            dataset_name,
            datasets[dataset_name],
            QUALITY_GATE_THRESHOLDS[dataset_name],
        )
        for dataset_name in QUALITY_GATE_THRESHOLDS
    }


def _build_dataset_gate(
    dataset_name: str,
    metrics: dict[str, Any],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    metric_results = {
        metric_name: _build_metric_gate(metrics, metric_name, minimum)
        for metric_name, minimum in thresholds.items()
    }
    return {
        "dataset": dataset_name,
        "sample_count": metrics["sample_count"],
        "status": _status_from_checks(metric_results.values()),
        "metrics": metric_results,
    }


def _build_metric_gate(
    metrics: dict[str, Any],
    metric_name: str,
    minimum: float,
) -> dict[str, Any]:
    actual = float(metrics[metric_name])
    margin = actual - minimum
    return {
        "actual": actual,
        "minimum": minimum,
        "margin": margin,
        "status": "pass" if margin >= 0 else "fail",
    }


def _build_pseudo_labeling_summary(
    training_report: dict[str, Any],
    distillation_report: dict[str, Any],
) -> dict[str, Any]:
    stock_candidate_labeling = distillation_report.get("stock_candidate_labeling", {})
    stock_candidate_accepted_count = int(
        stock_candidate_labeling.get("accepted_count", 0) or 0
    )
    accepted_count = int(distillation_report.get("accepted_count", 0) or 0)
    return {
        "status": distillation_report.get("status"),
        "candidate_count": distillation_report.get("candidate_count"),
        "accepted_count": accepted_count,
        "weak_label_accepted_count": max(
            accepted_count - stock_candidate_accepted_count,
            0,
        ),
        "stock_candidate_accepted_count": stock_candidate_accepted_count,
        "accepted_count_by_primary_label": distillation_report.get(
            "accepted_count_by_primary_label",
            {},
        ),
        "rejected_count": distillation_report.get("rejected_count"),
        "rejected_count_by_reason": distillation_report.get("rejected_count_by_reason", {}),
        "rejected_count_by_teacher_reason": distillation_report.get(
            "rejected_count_by_teacher_reason",
            {},
        ),
        "promotion_method": distillation_report.get("promotion_method"),
        "teacher_training_sample_count": distillation_report.get(
            "teacher_training_sample_count",
        ),
        "student_event_training_sample_count": training_report[
            "pseudo_labeled_sample_count"
        ],
        "minimum_event_confidence": distillation_report.get("minimum_event_confidence"),
        "minimum_sentiment_confidence": distillation_report.get(
            "minimum_sentiment_confidence",
        ),
        "minimum_importance_confidence": distillation_report.get(
            "minimum_importance_confidence",
        ),
        "stock_candidate_labeling": stock_candidate_labeling,
    }


def _build_consistency_checks(
    training_report: dict[str, Any],
    distillation_report: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    checks = {
        "pseudo_count_matches_training": {
            "expected": distillation_report.get("accepted_count"),
            "actual": training_report["pseudo_labeled_sample_count"],
        },
        "teacher_sample_count_matches_supervised": {
            "expected": training_report["supervised_sample_count"],
            "actual": distillation_report.get("teacher_training_sample_count"),
        },
    }
    return {
        name: {
            **values,
            "status": "pass" if values["expected"] == values["actual"] else "fail",
        }
        for name, values in checks.items()
    }


def _build_service_readiness(
    quality_gates: dict[str, dict[str, Any]],
    consistency_checks: dict[str, dict[str, Any]],
    distillation_report: dict[str, Any],
) -> dict[str, Any]:
    quality_status = _status_from_checks(quality_gates.values())
    consistency_status = _status_from_checks(consistency_checks.values())
    stock_candidate_labeling = distillation_report.get("stock_candidate_labeling", {})
    accepted_stock_count = int(stock_candidate_labeling.get("accepted_stock_count", 0) or 0)
    stock_candidate_status = (
        "pass"
        if accepted_stock_count >= MINIMUM_BOOTSTRAP_STOCK_CANDIDATE_COUNT
        else "fail"
    )
    checks = {
        "model_quality_release": {
            "status": quality_status,
            "required_status": "pass",
        },
        "release_consistency": {
            "status": consistency_status,
            "required_status": "pass",
        },
        "stock_candidate_bootstrap_coverage": {
            "status": stock_candidate_status,
            "accepted_stock_count": accepted_stock_count,
            "minimum_accepted_stock_count": MINIMUM_BOOTSTRAP_STOCK_CANDIDATE_COUNT,
            "coverage_type": "event-model-only pseudo labels",
        },
    }
    return {
        "overall_status": _status_from_checks(checks.values()),
        "readiness_type": "bootstrap_service_readiness",
        "checks": checks,
        "policy": (
            "service bootstrap readiness is based on release quality gates, "
            "consistency checks, and gated stock-candidate pseudo coverage; "
            "approved coverage gold is tracked separately as audited gold readiness"
        ),
    }


def _build_audited_gold_readiness(
    coverage_validation_report: dict[str, Any] | None,
) -> dict[str, Any]:
    if coverage_validation_report is None:
        return {
            "overall_status": "fail",
            "checks": {
                "coverage_validation": {
                    "status": "missing",
                    "reason": "coverage validation report is required for service readiness",
                }
            },
            "policy": (
                "audited gold readiness requires approved stock coverage validation"
            ),
        }

    coverage_status = str(coverage_validation_report.get("overall_status", "fail"))
    training_validation = coverage_validation_report.get("training_validation", {})
    evaluation_validation = coverage_validation_report.get("evaluation_validation", {})
    return {
        "overall_status": "pass" if coverage_status == "pass" else "fail",
        "readiness_type": "audited_gold_readiness",
        "checks": {
            "coverage_validation": {
                "status": coverage_status,
                "schema_version": coverage_validation_report.get("schema_version"),
                "training_target_stock_count": training_validation.get(
                    "target_stock_count"
                ),
                "training_eligible_stock_count": training_validation.get(
                    "eligible_stock_count"
                ),
                "training_remaining_stock_count_to_target": training_validation.get(
                    "remaining_stock_count_to_target"
                ),
                "evaluation_target_stock_count": evaluation_validation.get(
                    "target_stock_count"
                ),
                "evaluation_eligible_stock_count": evaluation_validation.get(
                    "eligible_stock_count"
                ),
                "evaluation_remaining_stock_count_to_target": evaluation_validation.get(
                    "remaining_stock_count_to_target"
                ),
                "minimum_wave_approved_stocks": coverage_validation_report.get(
                    "minimum_wave_approved_stocks"
                ),
            }
        },
        "policy": (
            "human_review_approved or codex_review_approved stock review gold is not "
            "required for bootstrap service readiness, but is required before claiming "
            "audited gold coverage readiness"
        ),
    }


def _build_weakest_event_labels(
    evaluation_report: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    return {
        dataset_name: _weakest_labels(dataset_metrics.get("event_label_metrics", {}))
        for dataset_name, dataset_metrics in evaluation_report.items()
    }


def _weakest_labels(
    label_metrics: dict[str, dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    rows = [
        {
            "label": label,
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "support": metrics["support"],
        }
        for label, metrics in label_metrics.items()
    ]
    return sorted(rows, key=lambda row: (row["f1"], row["recall"], row["label"]))[:limit]


def _overall_status(
    quality_gates: dict[str, dict[str, Any]],
    consistency_checks: dict[str, dict[str, Any]],
) -> str:
    gate_statuses = [gate["status"] for gate in quality_gates.values()]
    check_statuses = [check["status"] for check in consistency_checks.values()]
    return _status_from_checks([*gate_statuses, *check_statuses])


def _status_from_checks(checks: Any) -> str:
    return "pass" if all(_check_passed(check) for check in checks) else "fail"


def _check_passed(check: Any) -> bool:
    if isinstance(check, str):
        return check == "pass"
    if isinstance(check, dict):
        return check.get("status") == "pass"
    return False
