from __future__ import annotations

import json
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer
from hannah_montana_ai.training.ml_trainer import (
    DEFAULT_STOCK_CANDIDATE_PROMOTION_CONFIG,
    STOCK_CANDIDATE_LABEL_QUOTAS,
    StockCandidatePromotionConfig,
    train_ml_model,
)
from hannah_montana_ai.training.model_release_report import QUALITY_GATE_THRESHOLDS

STOCK_CANDIDATE_QUOTA_EXPERIMENT_SCHEMA_VERSION = (
    "stock-candidate-quota-experiment/v1"
)


@dataclass(frozen=True)
class StockCandidateQuotaProfile:
    name: str
    label_quotas: dict[str, int]
    per_stock_quota: int

    def to_config(self) -> StockCandidatePromotionConfig:
        return StockCandidatePromotionConfig(
            label_quotas=self.label_quotas,
            per_stock_quota=self.per_stock_quota,
        )


DEFAULT_EXPERIMENT_PROFILES = (
    StockCandidateQuotaProfile(
        name="previous_release",
        label_quotas={
            **STOCK_CANDIDATE_LABEL_QUOTAS,
            "RISK": 250,
            "CONTRACT": 250,
        },
        per_stock_quota=1,
    ),
    StockCandidateQuotaProfile(
        name="current_release",
        label_quotas=STOCK_CANDIDATE_LABEL_QUOTAS,
        per_stock_quota=DEFAULT_STOCK_CANDIDATE_PROMOTION_CONFIG.per_stock_quota,
    ),
    StockCandidateQuotaProfile(
        name="balanced_event_probe",
        label_quotas={
            "RISK": 350,
            "CONTRACT": 350,
            "CAPITAL_ACTION": 120,
            "CORPORATE_ACTION": 120,
            "EARNINGS": 120,
            "MACRO": 80,
            "DISCLOSURE": 0,
            "GENERAL_MARKET": 0,
        },
        per_stock_quota=1,
    ),
)


def build_stock_candidate_quota_experiment_report(
    training_paths: Sequence[Path],
    pseudo_label_path: Path,
    stock_candidate_path: Path,
    evaluation_paths: Mapping[str, Path],
    profiles: Sequence[StockCandidateQuotaProfile] = DEFAULT_EXPERIMENT_PROFILES,
) -> dict[str, Any]:
    profile_reports = [
        _run_profile(
            training_paths=training_paths,
            pseudo_label_path=pseudo_label_path,
            stock_candidate_path=stock_candidate_path,
            evaluation_paths=evaluation_paths,
            profile=profile,
        )
        for profile in profiles
    ]
    promotable_profiles = [
        profile for profile in profile_reports if profile["overall_status"] == "pass"
    ]
    best_profile = _best_profile(promotable_profiles)
    return {
        "schema_version": STOCK_CANDIDATE_QUOTA_EXPERIMENT_SCHEMA_VERSION,
        "profile_count": len(profile_reports),
        "profiles": profile_reports,
        "best_promotable_profile": best_profile,
        "experiment_policy": (
            "quota experiments train temporary artifacts and do not update the "
            "release model until quality gates are reviewed"
        ),
    }


def write_stock_candidate_quota_experiment_report(
    path: Path,
    report: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _run_profile(
    training_paths: Sequence[Path],
    pseudo_label_path: Path,
    stock_candidate_path: Path,
    evaluation_paths: Mapping[str, Path],
    profile: StockCandidateQuotaProfile,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        model_path = Path(temporary_directory) / "financial_nlp_ml.joblib"
        training_report = train_ml_model(
            list(training_paths),
            model_path,
            pseudo_label_path=pseudo_label_path,
            stock_candidate_path=stock_candidate_path,
            stock_candidate_config=profile.to_config(),
        )
        analyzer = AlertAnalyzer()
        analyzer.model = MachineLearningFinancialNlpModel(model_path)
        evaluation_results = {
            dataset_name: evaluate_alert_analyzer(
                load_labeled_alerts(path),
                analyzer,
            ).to_dict()
            for dataset_name, path in evaluation_paths.items()
        }

    quality_gates = _quality_gates(training_report.validation.to_dict(), evaluation_results)
    stock_candidate_labeling = training_report.pseudo_labeling.get(
        "stock_candidate_labeling",
        {},
    )
    return {
        "profile": {
            "name": profile.name,
            "label_quotas": profile.label_quotas,
            "per_stock_quota": profile.per_stock_quota,
        },
        "model_version": training_report.version,
        "sample_count": training_report.sample_count,
        "pseudo_labeled_sample_count": training_report.pseudo_labeled_sample_count,
        "stock_candidate_labeling": stock_candidate_labeling,
        "quality_gates": quality_gates,
        "overall_status": _overall_status(quality_gates),
        "evaluation": evaluation_results,
    }


def _quality_gates(
    holdout_metrics: dict[str, Any],
    evaluation_results: Mapping[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    datasets = {
        "holdout": holdout_metrics,
        **evaluation_results,
    }
    return {
        dataset_name: _dataset_gate(
            metrics=datasets[dataset_name],
            thresholds=thresholds,
        )
        for dataset_name, thresholds in QUALITY_GATE_THRESHOLDS.items()
    }


def _dataset_gate(
    metrics: dict[str, Any],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    metric_results = {
        metric_name: _metric_gate(metrics, metric_name, minimum)
        for metric_name, minimum in thresholds.items()
    }
    return {
        "sample_count": metrics["sample_count"],
        "status": _overall_status(metric_results),
        "metrics": metric_results,
    }


def _metric_gate(
    metrics: Mapping[str, Any],
    metric_name: str,
    minimum: float,
) -> dict[str, Any]:
    actual = float(metrics[metric_name])
    return {
        "actual": actual,
        "minimum": minimum,
        "margin": actual - minimum,
        "status": "pass" if actual >= minimum else "fail",
    }


def _overall_status(gates: Mapping[str, Any]) -> str:
    return "pass" if all(_gate_passed(gate) for gate in gates.values()) else "fail"


def _gate_passed(gate: Any) -> bool:
    if isinstance(gate, str):
        return gate == "pass"
    if isinstance(gate, dict):
        return gate.get("status") == "pass"
    return False


def _best_profile(profile_reports: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    if not profile_reports:
        return None
    best = max(
        profile_reports,
        key=lambda row: (
            int(row["stock_candidate_labeling"].get("accepted_stock_count", 0) or 0),
            int(row["stock_candidate_labeling"].get("accepted_count", 0) or 0),
            str(row["profile"]["name"]),
        ),
    )
    return {
        "name": best["profile"]["name"],
        "accepted_count": best["stock_candidate_labeling"].get("accepted_count", 0),
        "accepted_stock_count": best["stock_candidate_labeling"].get(
            "accepted_stock_count",
            0,
        ),
        "accepted_count_by_primary_label": best["stock_candidate_labeling"].get(
            "accepted_count_by_primary_label",
            {},
        ),
    }
