from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = PROJECT_ROOT / "reports/k-fnspid-impact-test-predictions.jsonl"
TRANSFORMER_PATH = PROJECT_ROOT / "reports/k-fnspid-transformer-test-predictions.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/k-fnspid-research-evaluation.json"
LABEL_ORDER = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def main() -> None:
    parser = argparse.ArgumentParser(description="K-FNSPID 모델의 논문용 통계 평가를 수행한다.")
    parser.add_argument("--baseline", type=Path, action="append")
    parser.add_argument("--transformer", type=Path, action="append")
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--bootstrap-samples", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=20260713)
    args = parser.parse_args()

    baseline_paths = args.baseline or [BASELINE_PATH]
    transformer_paths = args.transformer or [TRANSFORMER_PATH]
    baseline = [row for path in baseline_paths for row in load_predictions(path)]
    transformer = [row for path in transformer_paths for row in load_predictions(path)]
    aligned = align_predictions(baseline, transformer)
    report = evaluate_research(
        aligned,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )
    report["prediction_sources"] = {
        "baseline": [_display_path(path) for path in baseline_paths],
        "transformer": [_display_path(path) for path in transformer_paths],
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def load_predictions(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def align_predictions(
    baseline: list[dict[str, Any]],
    transformer: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline_by_id = _index_predictions(baseline, model_name="기준선")
    transformer_by_id = _index_predictions(transformer, model_name="Transformer")
    if baseline_by_id.keys() != transformer_by_id.keys():
        raise ValueError("기준선과 Transformer의 Test 문서 집합이 다릅니다.")
    rows: list[dict[str, Any]] = []
    for document_id in sorted(baseline_by_id):
        left = baseline_by_id[document_id]
        right = transformer_by_id[document_id]
        for field in ("expected", "source_type", "stock_code", "effective_trade_date"):
            if left[field] != right[field]:
                raise ValueError(f"paired 평가 메타데이터 불일치({field}): {document_id}")
        rows.append(
            {
                "document_id": document_id,
                "expected": left["expected"],
                "baseline": left["predicted"],
                "transformer": right["predicted"],
                "baseline_probabilities": left["probabilities"],
                "transformer_probabilities": right["probabilities"],
                "source_type": right["source_type"],
                "stock_code": right["stock_code"],
                "effective_trade_date": right["effective_trade_date"],
            }
        )
    return rows


def _index_predictions(
    rows: list[dict[str, Any]],
    *,
    model_name: str,
) -> dict[str, dict[str, Any]]:
    required = {
        "document_id",
        "expected",
        "predicted",
        "probabilities",
        "source_type",
        "stock_code",
        "effective_trade_date",
    }
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        missing = required - row.keys()
        if missing:
            raise ValueError(f"{model_name} 예측 필드 누락: {sorted(missing)}")
        document_id = str(row["document_id"]).strip()
        if not document_id or document_id in indexed:
            raise ValueError(
                f"{model_name} 예측 document_id가 비었거나 중복되었습니다: {document_id}"
            )
        if (
            str(row["expected"]) not in LABEL_ORDER
            or str(row["predicted"]) not in LABEL_ORDER
        ):
            raise ValueError(f"{model_name} 예측 라벨이 코드북과 다릅니다: {document_id}")
        _validate_probability_vector(row["probabilities"], model_name, document_id)
        indexed[document_id] = row
    return indexed


def _validate_probability_vector(
    probabilities: Any,
    model_name: str,
    document_id: str,
) -> None:
    if not isinstance(probabilities, dict) or set(probabilities) != set(LABEL_ORDER):
        raise ValueError(f"{model_name} 확률 라벨이 코드북과 다릅니다: {document_id}")
    values = [float(probabilities[label]) for label in LABEL_ORDER]
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in values):
        raise ValueError(f"{model_name} 확률 범위가 올바르지 않습니다: {document_id}")
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-5):
        raise ValueError(f"{model_name} 확률 합이 1이 아닙니다: {document_id}")


def evaluate_research(
    rows: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    if len(rows) < 100:
        raise ValueError("논문용 통계 평가에는 최소 100개 Test 표본이 필요합니다.")
    expected = [str(row["expected"]) for row in rows]
    baseline = [str(row["baseline"]) for row in rows]
    transformer = [str(row["transformer"]) for row in rows]
    baseline_metrics = classification_metrics(expected, baseline)
    transformer_metrics = classification_metrics(expected, transformer)
    baseline_metrics |= calibration_metrics(
        expected,
        [row["baseline_probabilities"] for row in rows],
    )
    transformer_metrics |= calibration_metrics(
        expected,
        [row["transformer_probabilities"] for row in rows],
    )
    confidence_intervals = paired_bootstrap(
        expected,
        baseline,
        transformer,
        samples=bootstrap_samples,
        seed=seed,
    )
    clustered_confidence_intervals = clustered_paired_bootstrap(
        rows,
        cluster_key="effective_trade_date",
        samples=bootstrap_samples,
        seed=seed,
    )
    baseline_only = sum(
        truth == left and truth != right
        for truth, left, right in zip(expected, baseline, transformer, strict=True)
    )
    transformer_only = sum(
        truth != left and truth == right
        for truth, left, right in zip(expected, baseline, transformer, strict=True)
    )
    source_metrics: dict[str, Any] = {}
    for source_type in sorted({str(row["source_type"]) for row in rows}):
        subset = [row for row in rows if row["source_type"] == source_type]
        source_expected = [str(row["expected"]) for row in subset]
        source_baseline = [str(row["baseline"]) for row in subset]
        source_transformer = [str(row["transformer"]) for row in subset]
        source_baseline_metrics = classification_metrics(source_expected, source_baseline)
        source_transformer_metrics = classification_metrics(source_expected, source_transformer)
        source_cluster_count = len(
            {str(row["effective_trade_date"]) for row in subset}
        )
        source_clustered: dict[str, Any]
        if source_cluster_count >= 20:
            source_clustered = {
                "status": "available",
                "cluster_count": source_cluster_count,
                **clustered_paired_bootstrap(
                    subset,
                    cluster_key="effective_trade_date",
                    samples=bootstrap_samples,
                    seed=seed,
                ),
            }
        else:
            source_clustered = {
                "status": "insufficient_clusters",
                "cluster_count": source_cluster_count,
                "minimum_cluster_count": 20,
            }
        source_metrics[source_type] = {
            "sample_count": len(subset),
            "baseline": source_baseline_metrics,
            "transformer": source_transformer_metrics,
            "clustered_bootstrap": source_clustered,
            "non_regression_gate": {
                "macro_f1_not_below_baseline": (
                    float(source_transformer_metrics["macro_f1"])
                    >= float(source_baseline_metrics["macro_f1"])
                ),
                "quadratic_kappa_not_below_baseline": (
                    float(source_transformer_metrics["quadratic_kappa"])
                    >= float(source_baseline_metrics["quadratic_kappa"])
                ),
            },
        }
    significant_clustered_gains = {
        metric: clustered_confidence_intervals[f"{metric}_difference"]["low"] > 0
        for metric in ("accuracy", "macro_f1", "quadratic_kappa")
    }
    mcnemar_p_value = exact_mcnemar_p_value(baseline_only, transformer_only)
    mcnemar_significant = mcnemar_p_value < 0.05
    source_non_regression = all(
        all(bool(value) for value in metrics["non_regression_gate"].values())
        for metrics in source_metrics.values()
    )
    eligible_for_superiority_claim = (
        len(rows) >= 10_000
        and all(significant_clustered_gains.values())
        and mcnemar_significant
        and source_non_regression
    )
    return {
        "schema_version": "k-fnspid-research-evaluation/v1",
        "sample_count": len(rows),
        "label_distribution": dict(sorted(Counter(expected).items())),
        "baseline": baseline_metrics,
        "transformer": transformer_metrics,
        "paired_bootstrap": {
            "samples": bootstrap_samples,
            "seed": seed,
            **confidence_intervals,
        },
        "clustered_bootstrap": {
            "cluster_key": "effective_trade_date",
            "cluster_count": len({str(row["effective_trade_date"]) for row in rows}),
            "samples": bootstrap_samples,
            "seed": seed,
            **clustered_confidence_intervals,
        },
        "mcnemar_exact": {
            "baseline_only_correct": baseline_only,
            "transformer_only_correct": transformer_only,
            "p_value": mcnemar_p_value,
        },
        "source_type": source_metrics,
        "research_gate": {
            "minimum_test_samples": 10_000,
            "trade_date_clustered_accuracy_ci_excludes_zero": significant_clustered_gains[
                "accuracy"
            ],
            "trade_date_clustered_macro_f1_ci_excludes_zero": significant_clustered_gains[
                "macro_f1"
            ],
            "trade_date_clustered_quadratic_kappa_ci_excludes_zero": (
                significant_clustered_gains["quadratic_kappa"]
            ),
            "mcnemar_exact_p_below_0_05": mcnemar_significant,
            "all_source_macro_f1_and_kappa_non_regression": source_non_regression,
            "eligible_for_superiority_claim": eligible_for_superiority_claim,
        },
    }


def classification_metrics(expected: list[str], predicted: list[str]) -> dict[str, Any]:
    expected_ordinal = [LABEL_ORDER.index(label) for label in expected]
    predicted_ordinal = [LABEL_ORDER.index(label) for label in predicted]
    precision, recall, class_f1, support = precision_recall_fscore_support(
        expected,
        predicted,
        labels=LABEL_ORDER,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(
                expected,
                predicted,
                labels=LABEL_ORDER,
                average="macro",
                zero_division=0,
            )
        ),
        "quadratic_kappa": float(
            cohen_kappa_score(expected_ordinal, predicted_ordinal, weights="quadratic")
        ),
        "ordinal_mean_absolute_error": sum(
            abs(truth - prediction)
            for truth, prediction in zip(expected_ordinal, predicted_ordinal, strict=True)
        )
        / len(expected),
        "per_class": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(class_f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(LABEL_ORDER)
        },
        "confusion_matrix": confusion_matrix(
            expected,
            predicted,
            labels=LABEL_ORDER,
        ).tolist(),
        "confusion_matrix_label_order": list(LABEL_ORDER),
    }


def calibration_metrics(
    expected: list[str],
    probability_rows: list[dict[str, float]],
    bins: int = 15,
) -> dict[str, float]:
    ece = 0.0
    brier_total = 0.0
    bucket_rows: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for truth, probabilities in zip(expected, probability_rows, strict=True):
        predicted = max(probabilities, key=probabilities.__getitem__)
        confidence = float(probabilities[predicted])
        bucket = min(int(confidence * bins), bins - 1)
        bucket_rows[bucket].append((confidence, predicted == truth))
        brier_total += sum(
            (float(probabilities.get(label, 0.0)) - float(label == truth)) ** 2
            for label in LABEL_ORDER
        )
    for bucket_values in bucket_rows:
        if not bucket_values:
            continue
        mean_confidence = sum(row[0] for row in bucket_values) / len(bucket_values)
        accuracy = sum(row[1] for row in bucket_values) / len(bucket_values)
        ece += len(bucket_values) / len(expected) * abs(mean_confidence - accuracy)
    return {
        "expected_calibration_error_15_bin": ece,
        "multiclass_brier_score": brier_total / len(expected),
    }


def paired_bootstrap(
    expected: list[str],
    baseline: list[str],
    transformer: list[str],
    *,
    samples: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    differences: dict[str, list[float]] = {
        "accuracy": [],
        "macro_f1": [],
        "quadratic_kappa": [],
    }
    for _ in range(samples):
        indices = [generator.randrange(len(expected)) for _ in expected]
        truth = [expected[index] for index in indices]
        left = [baseline[index] for index in indices]
        right = [transformer[index] for index in indices]
        left_metrics = bootstrap_metrics(truth, left)
        right_metrics = bootstrap_metrics(truth, right)
        for metric in differences:
            differences[metric].append(float(right_metrics[metric]) - float(left_metrics[metric]))
    return {
        f"{metric}_difference": percentile_interval(values)
        for metric, values in differences.items()
    }


def clustered_paired_bootstrap(
    rows: list[dict[str, Any]],
    *,
    cluster_key: str,
    samples: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    clusters: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        cluster = str(row.get(cluster_key, ""))
        if not cluster or cluster == "UNKNOWN":
            raise ValueError(f"cluster bootstrap 필드가 없습니다: {cluster_key}")
        clusters.setdefault(cluster, []).append(row)
    if len(clusters) < 20:
        raise ValueError("cluster bootstrap에는 최소 20개 거래일이 필요합니다.")

    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    cluster_names = sorted(clusters)
    differences: dict[str, list[float]] = {
        "accuracy": [],
        "macro_f1": [],
        "quadratic_kappa": [],
    }
    for _ in range(samples):
        sampled_rows = [
            row for _ in cluster_names for row in clusters[generator.choice(cluster_names)]
        ]
        expected = [str(row["expected"]) for row in sampled_rows]
        baseline = [str(row["baseline"]) for row in sampled_rows]
        transformer = [str(row["transformer"]) for row in sampled_rows]
        baseline_metrics = bootstrap_metrics(expected, baseline)
        transformer_metrics = bootstrap_metrics(expected, transformer)
        for metric in differences:
            differences[metric].append(
                float(transformer_metrics[metric]) - float(baseline_metrics[metric])
            )
    return {
        f"{metric}_difference": percentile_interval(values)
        for metric, values in differences.items()
    }


def bootstrap_metrics(expected: list[str], predicted: list[str]) -> dict[str, float]:
    """반복 재표집에서 필요한 세 지표만 4x4 혼동행렬로 계산한다."""
    label_indices = {label: index for index, label in enumerate(LABEL_ORDER)}
    matrix = [[0] * len(LABEL_ORDER) for _ in LABEL_ORDER]
    for truth, prediction in zip(expected, predicted, strict=True):
        matrix[label_indices[truth]][label_indices[prediction]] += 1

    sample_count = len(expected)
    row_totals = [sum(row) for row in matrix]
    column_totals = [sum(matrix[row][column] for row in range(4)) for column in range(4)]
    true_positives = [matrix[index][index] for index in range(4)]
    class_f1 = [
        (2.0 * true_positives[index] / (row_totals[index] + column_totals[index]))
        if row_totals[index] + column_totals[index]
        else 0.0
        for index in range(4)
    ]

    weighted_observed = 0.0
    weighted_expected = 0.0
    for truth_index in range(4):
        for prediction_index in range(4):
            weight = ((truth_index - prediction_index) / 3.0) ** 2
            weighted_observed += weight * matrix[truth_index][prediction_index] / sample_count
            weighted_expected += (
                weight
                * row_totals[truth_index]
                * column_totals[prediction_index]
                / (sample_count * sample_count)
            )
    quadratic_kappa = (
        1.0 - weighted_observed / weighted_expected if weighted_expected else 1.0
    )
    return {
        "accuracy": sum(true_positives) / sample_count,
        "macro_f1": sum(class_f1) / len(class_f1),
        "quadratic_kappa": quadratic_kappa,
    }


def percentile_interval(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    low_index = max(0, math.floor((len(ordered) - 1) * 0.025))
    high_index = min(len(ordered) - 1, math.ceil((len(ordered) - 1) * 0.975))
    return {
        "mean": sum(ordered) / len(ordered),
        "low": ordered[low_index],
        "high": ordered[high_index],
    }


def exact_mcnemar_p_value(baseline_only: int, transformer_only: int) -> float:
    discordant = baseline_only + transformer_only
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, value) for value in range(min(baseline_only, transformer_only) + 1)
    ) / (2**discordant)
    return float(min(1.0, 2.0 * tail))


if __name__ == "__main__":
    main()
