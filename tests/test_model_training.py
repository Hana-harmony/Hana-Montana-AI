import json
from pathlib import Path
from typing import Any

import joblib
import pytest

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model import (
    MachineLearningFinancialNlpModel,
    ModelArtifactInvalidError,
    ModelArtifactNotFoundError,
)
from hannah_montana_ai.training.collector import should_write_raw_alerts
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer
from hannah_montana_ai.training.ml_trainer import financial_tokenize, train_ml_model
from hannah_montana_ai.training.model_release_report import build_model_release_report
from hannah_montana_ai.training.pseudo_label_monitor import (
    build_pseudo_label_monitoring_report,
)
from hannah_montana_ai.training.weak_distiller import distill_weak_labeled_alerts

GOLD_EVENT_LABEL_QUALITY_GATES = {
    "CAPITAL_ACTION": {"precision": 0.90, "recall": 0.70, "f1": 0.80, "support": 70},
    "CONTRACT": {"precision": 0.70, "recall": 0.95, "f1": 0.80, "support": 70},
    "CORPORATE_ACTION": {"precision": 0.90, "recall": 0.95, "f1": 0.90, "support": 90},
    "DISCLOSURE": {"precision": 0.85, "recall": 0.80, "f1": 0.80, "support": 300},
    "EARNINGS": {"precision": 0.70, "recall": 0.95, "f1": 0.80, "support": 100},
    "GENERAL_MARKET": {"precision": 0.95, "recall": 0.95, "f1": 0.95, "support": 70},
    "MACRO": {"precision": 0.70, "recall": 0.90, "f1": 0.80, "support": 140},
    "RISK": {"precision": 0.95, "recall": 0.80, "f1": 0.85, "support": 160},
}

REAL_NEWS_EVENT_LABELS = {
    "CAPITAL_ACTION",
    "CONTRACT",
    "CORPORATE_ACTION",
    "EARNINGS",
    "GENERAL_MARKET",
    "MACRO",
    "RISK",
}


def test_training_builds_supervised_ml_artifact(tmp_path: Path) -> None:
    model_path = tmp_path / "financial_nlp_ml.joblib"
    report = train_ml_model(
        [
            Path("data/training/financial_alert_corpus.jsonl"),
            Path("data/training/financial_alert_augmented.jsonl"),
            Path("data/training/financial_alert_news_style_augmented.jsonl"),
            Path("data/training/financial_alert_real_news_gold.jsonl"),
        ],
        model_path,
    )

    assert model_path.exists()
    assert report.sample_count >= 300
    assert report.supervised_sample_count == report.sample_count
    assert report.pseudo_labeled_sample_count == 0
    assert report.pseudo_labeling["status"] == "not_configured"
    assert report.event_label_distribution["MACRO"] >= 40
    assert report.sentiment_label_distribution["NEGATIVE"] >= 100
    assert report.importance_label_distribution["CRITICAL"] >= 50
    assert report.training_sources == [
        "data/training/financial_alert_corpus.jsonl",
        "data/training/financial_alert_augmented.jsonl",
        "data/training/financial_alert_news_style_augmented.jsonl",
        "data/training/financial_alert_real_news_gold.jsonl",
    ]
    assert report.validation.sample_count >= 90
    assert report.validation.train_sample_count >= 300
    assert report.validation.event_macro_f1 >= 0.8
    assert report.validation.sentiment_accuracy >= 0.8
    assert report.validation.importance_accuracy >= 0.8
    assert report.validation.event_label_metrics["DISCLOSURE"]["support"] >= 10


def test_training_promotes_teacher_gated_pseudo_labels(tmp_path: Path) -> None:
    model_path = tmp_path / "financial_nlp_ml.joblib"
    weak_path = tmp_path / "weak_labeled_alerts.jsonl"
    rows = [
        {
            "text": "SK하이닉스 대규모 공급계약 체결로 장기 수주 기대 확대",
            "tags": ["CONTRACT"],
            "sentiment": "POSITIVE",
            "importance": "HIGH",
            "source_type": "NEWS",
        },
        {
            "text": "위험기업 상장폐지 우려와 주권매매거래정지 가능성 확대",
            "tags": ["RISK"],
            "sentiment": "NEGATIVE",
            "importance": "CRITICAL",
            "source_type": "NEWS",
        },
    ]
    weak_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    report = train_ml_model(
        [
            Path("data/training/financial_alert_corpus.jsonl"),
            Path("data/training/financial_alert_augmented.jsonl"),
            Path("data/training/financial_alert_news_style_augmented.jsonl"),
            Path("data/training/financial_alert_real_news_gold.jsonl"),
        ],
        model_path,
        pseudo_label_path=weak_path,
    )

    assert report.supervised_sample_count >= 300
    assert report.pseudo_labeled_sample_count >= 1
    assert report.sample_count == (
        report.supervised_sample_count + report.pseudo_labeled_sample_count
    )
    assert report.pseudo_labeling["status"] == "promoted_to_student_training"
    assert report.pseudo_labeling["promotion_method"] == "supervised_teacher_confidence_filter"
    assert report.pseudo_labeling["label_quotas"]["CORPORATE_ACTION"] == 40


def test_financial_tokenizer_extracts_domain_terms_without_spacing_dependency() -> None:
    tokens = financial_tokenize(
        "삼성전자 잠정실적 공시와 고환율 속 수주 턴어라운드, 주주환원과 주식병합"
    )

    assert "잠정실적" in tokens
    assert "수주" in tokens
    assert "주식병합" in tokens
    assert "finance:잠정실적" in tokens
    assert "finance:고환율" in tokens
    assert "finance:턴어라운드" in tokens
    assert "finance:주주환원" in tokens
    assert "finance:주식병합" in tokens


def test_missing_model_artifact_raises_explicit_error(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactNotFoundError):
        MachineLearningFinancialNlpModel(tmp_path / "missing.joblib")


def test_invalid_model_artifact_requires_expected_payload_keys(tmp_path: Path) -> None:
    model_path = tmp_path / "invalid.joblib"
    joblib.dump({"version": "broken"}, model_path)

    with pytest.raises(ModelArtifactInvalidError):
        MachineLearningFinancialNlpModel(model_path)


def test_ml_model_passes_evaluation_dataset() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_eval.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count >= 500
    assert result.event_tag_recall >= 0.8
    assert result.sentiment_accuracy >= 0.85
    assert result.importance_accuracy >= 0.8
    assert result.stock_accuracy >= 1.0
    assert result.event_macro_f1 >= 0.8
    assert result.event_label_metrics["DISCLOSURE"].support >= 300
    assert result.event_label_metrics["GENERAL_MARKET"].f1 >= 0.9
    assert result.sentiment_confusion_matrix["NEGATIVE"]["NEGATIVE"] >= 200
    assert result.importance_confusion_matrix["CRITICAL"]["CRITICAL"] >= 70


def test_ml_model_passes_label_level_golden_quality_gates() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_eval.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    for label, gates in GOLD_EVENT_LABEL_QUALITY_GATES.items():
        metric = result.event_label_metrics[label]
        assert metric.precision >= gates["precision"], label
        assert metric.recall >= gates["recall"], label
        assert metric.f1 >= gates["f1"], label
        assert metric.support >= gates["support"], label

    assert result.sentiment_confusion_matrix["NEGATIVE"]["NEGATIVE"] >= 200
    assert result.sentiment_confusion_matrix["POSITIVE"]["POSITIVE"] >= 230
    assert result.sentiment_confusion_matrix["NEUTRAL"]["NEUTRAL"] >= 230
    assert result.importance_confusion_matrix["CRITICAL"]["CRITICAL"] >= 80
    assert result.importance_confusion_matrix["HIGH"]["HIGH"] >= 290
    assert result.importance_confusion_matrix["MEDIUM"]["MEDIUM"] >= 230
    assert result.importance_confusion_matrix["LOW"]["LOW"] >= 20


def test_ml_model_passes_real_disclosure_gold_dataset() -> None:
    samples = load_labeled_alerts(
        Path("data/evaluation/financial_alert_real_disclosure_gold.jsonl")
    )
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count >= 30
    assert result.event_tag_recall >= 0.9
    assert result.event_macro_f1 >= 0.9
    assert result.sentiment_accuracy >= 0.9
    assert result.importance_accuracy >= 0.9
    assert result.stock_accuracy >= 1.0
    assert result.event_label_metrics["DISCLOSURE"].f1 >= 0.95
    assert result.event_label_metrics["RISK"].recall >= 0.9
    assert result.sentiment_confusion_matrix["NEGATIVE"]["NEGATIVE"] >= 7
    assert result.importance_confusion_matrix["LOW"]["LOW"] >= 6


def test_ml_model_passes_real_news_gold_dataset() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_real_news_gold.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count >= 50
    assert result.event_tag_recall >= 0.9
    assert result.event_macro_f1 >= 0.9
    assert result.sentiment_accuracy >= 0.9
    assert result.importance_accuracy >= 0.9
    assert result.stock_accuracy >= 1.0
    assert result.event_label_metrics["GENERAL_MARKET"].recall >= 0.9
    assert result.event_label_metrics["MACRO"].recall >= 0.9
    assert result.event_label_metrics["EARNINGS"].recall >= 0.9
    assert result.event_label_metrics["RISK"].recall >= 0.9
    assert result.event_label_metrics["CAPITAL_ACTION"].support >= 5
    assert result.event_label_metrics["CAPITAL_ACTION"].recall >= 0.9
    assert result.event_label_metrics["CONTRACT"].support >= 5
    assert result.event_label_metrics["CONTRACT"].recall >= 0.9
    assert result.event_label_metrics["CORPORATE_ACTION"].support >= 3
    assert result.event_label_metrics["CORPORATE_ACTION"].recall >= 0.9


def test_real_news_gold_training_and_evaluation_are_disjoint() -> None:
    training_samples = load_labeled_alerts(
        Path("data/training/financial_alert_real_news_gold.jsonl")
    )
    evaluation_samples = load_labeled_alerts(
        Path("data/evaluation/financial_alert_real_news_gold.jsonl")
    )

    training_texts = {sample.text for sample in training_samples}
    evaluation_texts = {sample.text for sample in evaluation_samples}

    assert len(training_samples) >= 60
    assert len(evaluation_samples) >= 80
    assert training_texts.isdisjoint(evaluation_texts)


def test_real_news_gold_dataset_is_expanded_and_traceable() -> None:
    training_rows = _read_jsonl(Path("data/training/financial_alert_real_news_gold.jsonl"))
    evaluation_rows = _read_jsonl(
        Path("data/evaluation/financial_alert_real_news_gold.jsonl")
    )
    raw_urls = {
        row["original_url"]
        for row in _read_jsonl(Path("data/raw/collected_alerts.jsonl"))
        if row.get("source_type") == "NEWS"
    }

    assert len(training_rows) >= 60
    assert len(evaluation_rows) >= 80
    assert _stock_code_count(training_rows) >= 25
    assert _stock_code_count(evaluation_rows) >= 30

    for label in REAL_NEWS_EVENT_LABELS:
        assert _label_support(training_rows, label) >= 7, label
        assert _label_support(evaluation_rows, label) >= 8, label

    assert all(row["source_url"] in raw_urls for row in training_rows)
    assert all(row["source_url"] in raw_urls for row in evaluation_rows)


def test_model_release_report_matches_source_reports() -> None:
    training_report = _read_json(Path("reports/ml-training-report.json"))
    evaluation_report = _read_json(Path("reports/ml-model-evaluation.json"))
    distillation_report = _read_json(Path("reports/weak-distillation-report.json"))
    release_report = _read_json(Path("reports/model-release-report.json"))

    expected = build_model_release_report(
        training_report,
        evaluation_report,
        distillation_report,
    )

    assert release_report == expected
    assert release_report["overall_status"] == "pass"
    assert release_report["model_version"] == training_report["version"]
    assert release_report["training"]["sample_count"] == 4049
    assert release_report["training"]["pseudo_labeled_sample_count"] == 440
    assert release_report["quality_gates"]["real_news_gold"]["sample_count"] == 80
    assert release_report["pseudo_labeling"]["weak_label_accepted_count"] == 360
    assert release_report["pseudo_labeling"]["stock_candidate_accepted_count"] == 80
    assert release_report["pseudo_labeling"]["accepted_count_by_primary_label"] == {
        "CONTRACT": 220,
        "CORPORATE_ACTION": 40,
        "RISK": 180,
    }
    stock_candidate_labeling = release_report["pseudo_labeling"][
        "stock_candidate_labeling"
    ]
    assert stock_candidate_labeling["status"] == "promoted_to_event_student_training"
    assert stock_candidate_labeling["candidate_count"] == 6244
    assert stock_candidate_labeling["accepted_count"] == 80
    assert stock_candidate_labeling["accepted_stock_count"] == 73
    assert stock_candidate_labeling["accepted_count_by_primary_label"]["RISK"] == 40
    assert stock_candidate_labeling["accepted_count_by_primary_label"]["CONTRACT"] == 40
    assert release_report["quality_gates"]["real_news_gold"]["status"] == "pass"
    assert (
        release_report["quality_gates"]["real_news_gold"]["metrics"][
            "event_macro_f1"
        ]["actual"]
        >= 0.9
    )
    assert (
        release_report["data_lineage"]["committed_data_policy"]
        == "raw_and_processed_training_data_are_tracked"
    )


def test_pseudo_label_monitoring_report_matches_source_reports() -> None:
    distillation_report = _read_json(Path("reports/weak-distillation-report.json"))
    release_report = _read_json(Path("reports/model-release-report.json"))
    monitoring_report = _read_json(
        Path("reports/pseudo-label-promotion-monitoring.json")
    )

    expected = build_pseudo_label_monitoring_report(
        distillation_report,
        release_report,
    )
    label_decisions = {
        row["label"]: row["decision"] for row in monitoring_report["labels"]
    }

    assert monitoring_report == expected
    assert monitoring_report["overall_status"] == "pass"
    assert monitoring_report["candidate_funnel"]["raw_candidate_count"] == 37278
    assert monitoring_report["candidate_funnel"]["high_signal_candidate_count"] == 4845
    assert monitoring_report["candidate_funnel"]["promoted_count"] == 440
    assert (
        monitoring_report["candidate_funnel"][
            "teacher_passed_not_promoted_or_quota_limited_count"
        ]
        == 1281
    )
    assert _label_row(monitoring_report, "RISK")["student_training_quota"] == 180
    assert _label_row(monitoring_report, "CONTRACT")["student_training_quota"] == 220
    assert label_decisions["RISK"] == "quota_filled"
    assert label_decisions["CONTRACT"] == "quota_filled"
    assert label_decisions["CORPORATE_ACTION"] == "quota_filled"
    assert (
        label_decisions["CAPITAL_ACTION"]
        == "expansion_candidate_hold_for_gold_gate"
    )
    assert label_decisions["GENERAL_MARKET"] == "hold_low_pool_or_non_target_label"
    assert (
        monitoring_report["expansion_policy"]["rule"]
        == "zero_quota_labels_require_gold_gate_experiment_before_student_training"
    )


def test_weak_distiller_filters_noise_and_balances_high_signal_samples(tmp_path: Path) -> None:
    weak_path = tmp_path / "weak.jsonl"
    rows = [
        {
            "text": "삼성전자 대규모 공급계약 체결로 수주 기대 확대",
            "tags": ["CONTRACT"],
            "sentiment": "POSITIVE",
            "importance": "HIGH",
            "source_type": "NEWS",
        },
        {
            "text": "SK하이닉스 상장폐지 우려와 거래정지 가능성 확대",
            "tags": ["RISK"],
            "sentiment": "NEGATIVE",
            "importance": "CRITICAL",
            "source_type": "NEWS",
        },
        {
            "text": "자산운용 ETF 투자설명서 집합투자증권 정정 제출",
            "tags": ["DISCLOSURE"],
            "sentiment": "NEUTRAL",
            "importance": "HIGH",
            "source_type": "DISCLOSURE",
        },
        {
            "text": "내용 없음",
            "tags": ["GENERAL_MARKET"],
            "sentiment": "NEUTRAL",
            "importance": "LOW",
            "source_type": "NEWS",
        },
    ]
    weak_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    result = distill_weak_labeled_alerts(weak_path)

    assert [sample.tags[0] for sample in result.samples] == ["RISK", "CONTRACT"]
    assert result.report["candidate_count"] == 4
    assert result.report["accepted_count"] == 2
    assert result.report["rejected_count_by_reason"]["disclosure_noise"] == 1
    assert result.report["rejected_count_by_reason"]["too_short"] == 1


def test_collection_guard_prevents_dataset_shrink() -> None:
    assert should_write_raw_alerts(existing_count=1000, next_count=900) is False
    assert should_write_raw_alerts(existing_count=1000, next_count=1000) is True
    assert should_write_raw_alerts(existing_count=1000, next_count=1, force=True) is True


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _stock_code_count(rows: list[dict[str, Any]]) -> int:
    return len({row["stock_code"] for row in rows if row.get("stock_code")})


def _label_support(rows: list[dict[str, Any]], label: str) -> int:
    return sum(label in row["tags"] for row in rows)


def _label_row(report: dict[str, Any], label: str) -> dict[str, Any]:
    return next(row for row in report["labels"] if row["label"] == label)
