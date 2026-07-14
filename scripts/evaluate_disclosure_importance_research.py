from __future__ import annotations

import argparse
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from evaluate_k_fnspid_research import (
    calibration_metrics,
    classification_metrics,
    exact_mcnemar_p_value,
    paired_bootstrap,
)

from hannah_montana_ai.domain.schemas import Importance
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import load_labeled_alerts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
DEFAULT_STRESS_GOLD = (
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_stress_gold.jsonl"
)
DEFAULT_REPORT = PROJECT_ROOT / "reports/disclosure-importance-research-evaluation.json"
DEFAULT_TRAINING_REPORT = PROJECT_ROOT / "reports/disclosure-importance-training-report.json"
DEFAULT_CODEBOOK = PROJECT_ROOT / "docs/datasets/k-fnspid-v3-annotation-codebook.md"
LABEL_ORDER = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def main() -> None:
    parser = argparse.ArgumentParser(description="공시 의미 중요도의 논문용 통계 평가를 수행한다.")
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--stress-gold", type=Path, default=DEFAULT_STRESS_GOLD)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--bootstrap-samples", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=20260713)
    args = parser.parse_args()

    analyzer = AlertAnalyzer()
    if not analyzer.disclosure_importance_model.enabled:
        raise SystemExit("검증된 공시 의미 중요도 artifact가 활성화되지 않았습니다.")
    primary_rows = build_rows(analyzer, args.gold)
    stress_rows = build_rows(analyzer, args.stress_gold) if args.stress_gold.exists() else []
    primary_ids = {str(row["document_id"]) for row in primary_rows}
    stress_ids = {str(row["document_id"]) for row in stress_rows}
    if primary_ids & stress_ids:
        raise SystemExit("기본 Gold와 스트레스 Gold의 문서가 중복됩니다.")
    rows = [*primary_rows, *stress_rows]
    report = evaluate_rows(rows, bootstrap_samples=args.bootstrap_samples, seed=args.seed)
    training_report = json.loads(DEFAULT_TRAINING_REPORT.read_text(encoding="utf-8"))
    report["candidate_source"] = {
        "version": training_report["version"],
        "input_feature_version": training_report["input_feature_version"],
        "selected_feature_view": training_report["feature_selection"]["selected"],
        "training_report": {
            "path": display_path(DEFAULT_TRAINING_REPORT),
            **file_manifest(DEFAULT_TRAINING_REPORT),
        },
        "artifact": training_report["artifact"],
        "policy_codebook": {
            "path": display_path(DEFAULT_CODEBOOK),
            **file_manifest(DEFAULT_CODEBOOK),
        },
    }
    report["gold_sources"] = {
        "primary": {
            "path": display_path(args.gold),
            "sample_count": len(primary_rows),
            **file_manifest(args.gold),
        },
        "stress": {
            "path": display_path(args.stress_gold),
            "sample_count": len(stress_rows),
            **file_manifest(args.stress_gold),
        },
    }
    report["primary_gold"] = subset_metrics(primary_rows)
    report["stress_gold"] = subset_metrics(stress_rows)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def build_rows(analyzer: AlertAnalyzer, gold_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sample in load_labeled_alerts(gold_path):
        text = sample.model_text
        baseline_probabilities = analyzer.model.importance_probabilities(text, "DISCLOSURE")
        baseline = cast(
            Importance,
            max(baseline_probabilities, key=baseline_probabilities.__getitem__),
        )
        baseline = analyzer._augment_importance(text, "DISCLOSURE", baseline)
        candidate = analyzer.disclosure_importance_model.predict(
            sample.title or sample.text,
            sample.snippet,
            sample.full_content,
        )
        if candidate is None:
            raise RuntimeError("공시 의미 중요도 예측이 비활성화됐습니다.")
        candidate_importance = candidate.importance
        candidate_probabilities = candidate.probabilities
        if analyzer._rule_importance_floor(text, "DISCLOSURE") == "CRITICAL":
            candidate_importance = "CRITICAL"
            candidate_probabilities = analyzer._apply_probability_floor(
                candidate_probabilities,
                "CRITICAL",
                0.90,
            )
        rows.append(
            {
                "document_id": sample.document_id or sample.content_hash or sample.source_url,
                "expected": sample.importance,
                "baseline": baseline,
                "candidate": candidate_importance,
                "candidate_probabilities": candidate_probabilities,
                "year": sample.published_at[:4] or "UNKNOWN",
            }
        )
    return rows


def evaluate_rows(
    rows: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    if len(rows) < 500:
        raise ValueError("공시 중요도 연구 평가는 Gold 500건 이상이 필요합니다.")
    expected = [str(row["expected"]) for row in rows]
    baseline = [str(row["baseline"]) for row in rows]
    candidate = [str(row["candidate"]) for row in rows]
    baseline_only = sum(
        truth == left and truth != right
        for truth, left, right in zip(expected, baseline, candidate, strict=True)
    )
    candidate_only = sum(
        truth != left and truth == right
        for truth, left, right in zip(expected, baseline, candidate, strict=True)
    )
    confidence_intervals = paired_bootstrap(
        expected,
        baseline,
        candidate,
        samples=bootstrap_samples,
        seed=seed,
    )
    year_metrics: dict[str, Any] = {}
    for year in sorted({str(row["year"]) for row in rows}):
        subset = [row for row in rows if row["year"] == year]
        truth = [str(row["expected"]) for row in subset]
        year_metrics[year] = {
            "sample_count": len(subset),
            "baseline": classification_metrics(truth, [str(row["baseline"]) for row in subset]),
            "candidate": classification_metrics(truth, [str(row["candidate"]) for row in subset]),
        }
    candidate_metrics = classification_metrics(expected, candidate)
    candidate_metrics |= calibration_metrics(
        expected,
        [row["candidate_probabilities"] for row in rows],
    )
    macro_interval = confidence_intervals["macro_f1_difference"]
    accuracy_interval = confidence_intervals["accuracy_difference"]
    mcnemar_p_value = exact_mcnemar_p_value(baseline_only, candidate_only)
    return {
        "schema_version": "disclosure-importance-research-evaluation/v1",
        "sample_count": len(rows),
        "label_distribution": dict(sorted(Counter(expected).items())),
        "protocol": (
            "disjoint primary and high-risk stress Codex Gold; "
            "legacy analyzer vs Validation-selected semantic model with terminal-risk floor"
        ),
        "baseline": classification_metrics(expected, baseline),
        "candidate": candidate_metrics,
        "paired_bootstrap": {
            "samples": bootstrap_samples,
            "seed": seed,
            **confidence_intervals,
        },
        "mcnemar_exact": {
            "baseline_only_correct": baseline_only,
            "candidate_only_correct": candidate_only,
            "p_value": mcnemar_p_value,
        },
        "publication_year": year_metrics,
        "research_gate": {
            "minimum_gold_samples": 500,
            "accuracy_noninferior": (
                candidate_metrics["accuracy"]
                >= classification_metrics(expected, baseline)["accuracy"]
            ),
            "paired_macro_f1_ci_excludes_zero": float(macro_interval["low"]) > 0,
            "paired_accuracy_ci_excludes_zero": float(accuracy_interval["low"]) > 0,
            "mcnemar_p_below_0_05": mcnemar_p_value < 0.05,
            "eligible_for_accuracy_superiority_claim": (
                len(rows) >= 500 and float(accuracy_interval["low"]) > 0 and mcnemar_p_value < 0.05
            ),
            "eligible_for_superiority_claim": (
                len(rows) >= 500
                and candidate_metrics["accuracy"]
                >= classification_metrics(expected, baseline)["accuracy"]
                and float(macro_interval["low"]) > 0
            ),
        },
    }


def subset_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"sample_count": 0}
    expected = [str(row["expected"]) for row in rows]
    return {
        "sample_count": len(rows),
        "label_distribution": dict(sorted(Counter(expected).items())),
        "baseline": classification_metrics(
            expected,
            [str(row["baseline"]) for row in rows],
        ),
        "candidate": classification_metrics(
            expected,
            [str(row["candidate"]) for row in rows],
        ),
    }


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return resolved.name


def file_manifest(path: Path) -> dict[str, str | int]:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


if __name__ == "__main__":
    main()
