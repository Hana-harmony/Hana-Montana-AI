from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

from hannah_montana_ai.domain.schemas import Importance, Sentiment
from hannah_montana_ai.training.dataset import LabeledAlert, load_labeled_alerts
from hannah_montana_ai.training.weak_distiller import distill_weak_labeled_alerts

_TOKEN_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+)?%?|[A-Za-z][A-Za-z0-9+.-]*|[가-힣]+")
_NON_TOKEN_CHAR_PATTERN = re.compile(r"[^0-9a-z가-힣]+")

FINANCIAL_DOMAIN_TERMS: tuple[str, ...] = (
    "감자",
    "거래정지",
    "계약",
    "공급계약",
    "공시",
    "고배당",
    "금리",
    "관세",
    "노사갈등",
    "단일판매",
    "배당",
    "변동성",
    "분기보고서",
    "빚투",
    "소송등",
    "상장폐지",
    "실적",
    "영업이익",
    "유상증자",
    "무상증자",
    "임상",
    "임단협",
    "임원주요주주",
    "자사주",
    "자사주매입",
    "자기주식",
    "자기주식처분",
    "자기주식취득",
    "잠정실적",
    "전환사채",
    "지분인수",
    "지분매각",
    "지분취득",
    "지분처분",
    "지분투자",
    "턴어라운드",
    "판매실적",
    "생산차질",
    "생산능력",
    "최대주주",
    "특허분쟁",
    "주권매매거래정지",
    "주요사항보고서",
    "주식교환",
    "주식분할",
    "주식병합",
    "주주총회",
    "주주환원",
    "주주가치",
    "출자증권",
    "타법인주식",
    "증자",
    "소각",
    "수주",
    "횡령배임",
    "합병",
    "인수",
    "매각",
    "회사분할",
    "사업재편",
    "리밸런싱",
    "자산효율화",
    "공급망",
    "화재",
    "신사업",
    "웹3",
    "환율",
    "고환율",
    "흑자전환",
)

PSEUDO_LABEL_QUOTAS = {
    "RISK": 140,
    "CONTRACT": 180,
    "CAPITAL_ACTION": 0,
    "CORPORATE_ACTION": 40,
    "EARNINGS": 0,
    "MACRO": 0,
    "DISCLOSURE": 0,
    "GENERAL_MARKET": 0,
}
STOCK_CANDIDATE_LABEL_QUOTAS = {
    "RISK": 200,
    "CONTRACT": 200,
    "CAPITAL_ACTION": 0,
    "CORPORATE_ACTION": 0,
    "EARNINGS": 0,
    "MACRO": 0,
    "DISCLOSURE": 0,
    "GENERAL_MARKET": 0,
}
STOCK_CANDIDATE_PER_STOCK_QUOTA = 1
EVENT_PROBABILITY_THRESHOLD = 0.30
EVENT_LABEL_THRESHOLDS = {
    "CONTRACT": 0.34,
    "CORPORATE_ACTION": 0.22,
    "EARNINGS": 0.36,
    "MACRO": 0.32,
    "RISK": 0.56,
}


@dataclass(frozen=True)
class MlTrainingReport:
    version: str
    trained_at: str
    sample_count: int
    supervised_sample_count: int
    pseudo_labeled_sample_count: int
    training_sources: list[str]
    event_label_distribution: dict[str, int]
    sentiment_label_distribution: dict[str, int]
    importance_label_distribution: dict[str, int]
    validation: MlValidationReport
    event_probability_threshold: float
    event_label_thresholds: dict[str, float]
    pseudo_labeling: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "trained_at": self.trained_at,
            "sample_count": self.sample_count,
            "supervised_sample_count": self.supervised_sample_count,
            "pseudo_labeled_sample_count": self.pseudo_labeled_sample_count,
            "training_sources": self.training_sources,
            "event_label_distribution": self.event_label_distribution,
            "sentiment_label_distribution": self.sentiment_label_distribution,
            "importance_label_distribution": self.importance_label_distribution,
            "validation": self.validation.to_dict(),
            "event_probability_threshold": self.event_probability_threshold,
            "event_label_thresholds": self.event_label_thresholds,
            "pseudo_labeling": self.pseudo_labeling,
        }


@dataclass(frozen=True)
class MlValidationReport:
    sample_count: int
    train_sample_count: int
    event_subset_recall: float
    event_macro_f1: float
    sentiment_accuracy: float
    importance_accuracy: float
    event_label_metrics: dict[str, dict[str, float | int]]
    sentiment_confusion_matrix: dict[str, dict[str, int]]
    importance_confusion_matrix: dict[str, dict[str, int]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "train_sample_count": self.train_sample_count,
            "event_subset_recall": self.event_subset_recall,
            "event_macro_f1": self.event_macro_f1,
            "sentiment_accuracy": self.sentiment_accuracy,
            "importance_accuracy": self.importance_accuracy,
            "event_label_metrics": self.event_label_metrics,
            "sentiment_confusion_matrix": self.sentiment_confusion_matrix,
            "importance_confusion_matrix": self.importance_confusion_matrix,
        }


@dataclass(frozen=True)
class PseudoLabelPromotionResult:
    samples: list[LabeledAlert]
    report: dict[str, Any]


def train_ml_model(
    training_paths: list[Path],
    model_path: Path,
    pseudo_label_path: Path | None = None,
    stock_candidate_path: Path | None = None,
) -> MlTrainingReport:
    supervised_samples = _load_samples(training_paths)
    if len(supervised_samples) < 30:
        raise ValueError("ML training requires at least 30 labeled samples")

    validation = _validate_holdout(supervised_samples)
    pseudo_label_result = _promote_pseudo_labels(
        supervised_samples,
        pseudo_label_path,
        stock_candidate_path,
    )
    samples = [*supervised_samples, *pseudo_label_result.samples]

    event_texts = [_event_text(sample.text, sample.source_type) for sample in samples]
    supervised_texts = [sample.text for sample in supervised_samples]
    supervised_importance_texts = [
        _importance_text(sample.text, sample.source_type) for sample in supervised_samples
    ]
    event_targets = [sample.tags for sample in samples]
    supervised_sentiment_targets = [sample.sentiment for sample in supervised_samples]
    supervised_importance_targets = [sample.importance for sample in supervised_samples]

    event_binarizer = MultiLabelBinarizer()
    event_matrix = event_binarizer.fit_transform(event_targets)

    event_model = Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                    )
                ),
            ),
        ]
    )
    sentiment_model = Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    importance_model = Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )

    event_model.fit(event_texts, event_matrix)
    sentiment_model.fit(supervised_texts, supervised_sentiment_targets)
    importance_model.fit(supervised_importance_texts, supervised_importance_targets)

    trained_at = datetime.now(UTC).isoformat()
    version = f"financial-ml-tfidf-logreg-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "version": version,
        "trained_at": trained_at,
        "event_model": event_model,
        "event_binarizer": event_binarizer,
        "sentiment_model": sentiment_model,
        "importance_model": importance_model,
        "event_probability_threshold": EVENT_PROBABILITY_THRESHOLD,
        "event_label_thresholds": EVENT_LABEL_THRESHOLDS,
        "sample_count": len(samples),
        "supervised_sample_count": len(supervised_samples),
        "pseudo_labeled_sample_count": len(pseudo_label_result.samples),
        "training_sources": _training_source_paths(training_paths),
        "pseudo_labeling": pseudo_label_result.report,
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)

    return MlTrainingReport(
        version=version,
        trained_at=trained_at,
        sample_count=len(samples),
        supervised_sample_count=len(supervised_samples),
        pseudo_labeled_sample_count=len(pseudo_label_result.samples),
        training_sources=artifact["training_sources"],
        event_label_distribution=_event_distribution(samples),
        sentiment_label_distribution=dict(Counter(supervised_sentiment_targets)),
        importance_label_distribution=dict(Counter(supervised_importance_targets)),
        validation=validation,
        event_probability_threshold=EVENT_PROBABILITY_THRESHOLD,
        event_label_thresholds=EVENT_LABEL_THRESHOLDS,
        pseudo_labeling=pseudo_label_result.report,
    )


def _load_samples(paths: list[Path]) -> list[LabeledAlert]:
    samples: list[LabeledAlert] = []
    seen: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for sample in load_labeled_alerts(path):
            key = f"{sample.source_type}:{sample.text}"
            if key in seen:
                continue
            samples.append(sample)
            seen.add(key)
    return samples


def _training_source_paths(paths: list[Path]) -> list[str]:
    repository_root = Path.cwd().resolve()
    sources: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        resolved_path = path.resolve()
        try:
            sources.append(str(resolved_path.relative_to(repository_root)))
        except ValueError:
            sources.append(str(resolved_path))
    return sources


def _promote_pseudo_labels(
    supervised_samples: Sequence[LabeledAlert],
    pseudo_label_path: Path | None,
    stock_candidate_path: Path | None = None,
) -> PseudoLabelPromotionResult:
    if pseudo_label_path is None:
        base_result = PseudoLabelPromotionResult(
            samples=[],
            report={"status": "not_configured", "accepted_count": 0},
        )
        return _merge_stock_candidate_pseudo_labels(
            supervised_samples,
            base_result,
            stock_candidate_path,
        )
    if not pseudo_label_path.exists():
        base_result = PseudoLabelPromotionResult(
            samples=[],
            report={
                "status": "source_missing",
                "source_path": _report_path(pseudo_label_path),
                "accepted_count": 0,
            },
        )
        return _merge_stock_candidate_pseudo_labels(
            supervised_samples,
            base_result,
            stock_candidate_path,
        )

    distillation = distill_weak_labeled_alerts(pseudo_label_path)
    if not distillation.samples:
        base_result = PseudoLabelPromotionResult(
            samples=[],
            report={
                **distillation.report,
                "status": "no_distilled_candidates",
                "accepted_count": 0,
            },
        )
        return _merge_stock_candidate_pseudo_labels(
            supervised_samples,
            base_result,
            stock_candidate_path,
        )

    teacher = _fit_teacher(supervised_samples)
    accepted_by_label: dict[str, list[tuple[float, str, LabeledAlert]]] = {
        label: [] for label in PSEUDO_LABEL_QUOTAS
    }
    rejected_reasons: Counter[str] = Counter()
    seen_texts = {sample.text for sample in supervised_samples}

    for weak_sample in distillation.samples:
        if weak_sample.text in seen_texts:
            rejected_reasons["duplicate_supervised_text"] += 1
            continue

        prediction = _teacher_predict(teacher, weak_sample)
        if prediction is None:
            rejected_reasons["low_teacher_confidence"] += 1
            continue
        pseudo_sample, score = prediction
        if not set(weak_sample.tags).intersection(pseudo_sample.tags):
            rejected_reasons["teacher_weak_event_disagreement"] += 1
            continue

        primary_label = _primary_label(pseudo_sample.tags)
        tie_breaker = f"{primary_label}:{pseudo_sample.text}"
        accepted_by_label[primary_label].append((score, tie_breaker, pseudo_sample))

    promoted_samples: list[LabeledAlert] = []
    accepted_count_by_primary_label: dict[str, int] = {}
    for label, quota in PSEUDO_LABEL_QUOTAS.items():
        rows = sorted(accepted_by_label[label], key=lambda item: (-item[0], item[1]))
        selected = [sample for _, _, sample in rows[:quota]]
        promoted_samples.extend(selected)
        accepted_count_by_primary_label[label] = len(selected)

    report = {
        **distillation.report,
        "status": "promoted_to_student_training",
        "promotion_method": "supervised_teacher_confidence_filter",
        "teacher_training_sample_count": len(supervised_samples),
        "accepted_count": len(promoted_samples),
        "accepted_count_by_primary_label": accepted_count_by_primary_label,
        "rejected_count_by_teacher_reason": dict(sorted(rejected_reasons.items())),
        "label_quotas": PSEUDO_LABEL_QUOTAS,
        "pseudo_sample_influence_control": (
            "confidence_threshold_and_label_quota_for_event_model_only"
        ),
        "event_probability_threshold": 0.42,
        "minimum_event_confidence": 0.58,
        "minimum_sentiment_confidence": 0.72,
        "minimum_importance_confidence": 0.68,
    }
    base_result = PseudoLabelPromotionResult(samples=promoted_samples, report=report)
    return _merge_stock_candidate_pseudo_labels(
        supervised_samples,
        base_result,
        stock_candidate_path,
    )


def _merge_stock_candidate_pseudo_labels(
    supervised_samples: Sequence[LabeledAlert],
    base_result: PseudoLabelPromotionResult,
    stock_candidate_path: Path | None,
) -> PseudoLabelPromotionResult:
    stock_result = _promote_stock_candidate_labels(supervised_samples, stock_candidate_path)
    if not stock_result.samples:
        return PseudoLabelPromotionResult(
            samples=base_result.samples,
            report={
                **base_result.report,
                "stock_candidate_labeling": stock_result.report,
            },
        )

    merged_samples = [*base_result.samples, *stock_result.samples]
    merged_label_counts = Counter(_primary_label(sample.tags) for sample in merged_samples)
    return PseudoLabelPromotionResult(
        samples=merged_samples,
        report={
            **base_result.report,
            "status": "promoted_to_student_training",
            "accepted_count": len(merged_samples),
            "accepted_count_by_primary_label": dict(
                sorted(merged_label_counts.items(), key=lambda item: item[0])
            ),
            "stock_candidate_labeling": stock_result.report,
            "pseudo_sample_influence_control": (
                "weak_and_stock_candidate_pseudo_labels_are_event_model_only"
            ),
        },
    )


def _promote_stock_candidate_labels(
    supervised_samples: Sequence[LabeledAlert],
    stock_candidate_path: Path | None,
) -> PseudoLabelPromotionResult:
    if stock_candidate_path is None:
        return PseudoLabelPromotionResult(
            samples=[],
            report={"status": "not_configured", "accepted_count": 0},
        )
    if not stock_candidate_path.exists():
        return PseudoLabelPromotionResult(
            samples=[],
            report={
                "status": "source_missing",
                "source_path": _report_path(stock_candidate_path),
                "accepted_count": 0,
            },
        )

    candidates = _load_stock_candidate_samples(stock_candidate_path)
    teacher = _fit_teacher(supervised_samples)
    seen_texts = {sample.text for sample in supervised_samples}
    accepted_by_label: dict[str, list[tuple[float, str, LabeledAlert]]] = {
        label: [] for label in STOCK_CANDIDATE_LABEL_QUOTAS
    }
    accepted_by_stock: defaultdict[str, int] = defaultdict(int)
    rejected_reasons: Counter[str] = Counter()

    for candidate in candidates:
        if candidate.text in seen_texts:
            rejected_reasons["duplicate_supervised_text"] += 1
            continue
        primary_label = _primary_label(candidate.tags)
        if STOCK_CANDIDATE_LABEL_QUOTAS.get(primary_label, 0) == 0:
            rejected_reasons["zero_quota_label"] += 1
            continue
        if accepted_by_stock[candidate.stock_code or "UNKNOWN"] >= STOCK_CANDIDATE_PER_STOCK_QUOTA:
            rejected_reasons["per_stock_quota_filled"] += 1
            continue

        prediction = _teacher_predict(teacher, candidate)
        if prediction is None:
            rejected_reasons["low_teacher_confidence"] += 1
            continue
        pseudo_sample, score = prediction
        if not set(candidate.tags).intersection(pseudo_sample.tags):
            rejected_reasons["teacher_candidate_event_disagreement"] += 1
            continue

        pseudo_primary_label = _primary_label(pseudo_sample.tags)
        if STOCK_CANDIDATE_LABEL_QUOTAS.get(pseudo_primary_label, 0) == 0:
            rejected_reasons["teacher_zero_quota_label"] += 1
            continue
        tie_breaker = f"{pseudo_primary_label}:{pseudo_sample.stock_code}:{pseudo_sample.text}"
        accepted_by_label[pseudo_primary_label].append((score, tie_breaker, pseudo_sample))
        accepted_by_stock[pseudo_sample.stock_code or "UNKNOWN"] += 1

    promoted_samples: list[LabeledAlert] = []
    accepted_count_by_primary_label: dict[str, int] = {}
    for label, quota in STOCK_CANDIDATE_LABEL_QUOTAS.items():
        rows = sorted(accepted_by_label[label], key=lambda item: (-item[0], item[1]))
        selected = [sample for _, _, sample in rows[:quota]]
        promoted_samples.extend(selected)
        accepted_count_by_primary_label[label] = len(selected)

    accepted_stock_codes = {sample.stock_code for sample in promoted_samples if sample.stock_code}
    return PseudoLabelPromotionResult(
        samples=promoted_samples,
        report={
            "status": "promoted_to_event_student_training"
            if promoted_samples
            else "no_promoted_candidates",
            "source_path": _report_path(stock_candidate_path),
            "candidate_count": len(candidates),
            "accepted_count": len(promoted_samples),
            "accepted_stock_count": len(accepted_stock_codes),
            "accepted_count_by_primary_label": accepted_count_by_primary_label,
            "rejected_count_by_reason": dict(sorted(rejected_reasons.items())),
            "label_quotas": STOCK_CANDIDATE_LABEL_QUOTAS,
            "per_stock_quota": STOCK_CANDIDATE_PER_STOCK_QUOTA,
            "promotion_method": "supervised_teacher_gate_on_stock_balanced_queue",
            "pseudo_sample_influence_control": "event_model_only",
        },
    )


def _load_stock_candidate_samples(path: Path) -> list[LabeledAlert]:
    samples: list[LabeledAlert] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get("curation_status") != "needs_human_review":
            continue
        samples.append(
            LabeledAlert(
                text=payload["text"],
                tags=payload["tags"],
                sentiment=payload["sentiment"],
                importance=payload["importance"],
                source_type=payload.get("source_type", "NEWS"),
                stock_code=payload.get("stock_code"),
                stock_name=payload.get("stock_name"),
            )
        )
    return samples


def _fit_teacher(samples: Sequence[LabeledAlert]) -> dict[str, Any]:
    event_binarizer = MultiLabelBinarizer()
    event_matrix = event_binarizer.fit_transform([sample.tags for sample in samples])

    event_model = _event_model()
    sentiment_model = _single_label_model()
    importance_model = _importance_model()

    event_model.fit(
        [_event_text(sample.text, sample.source_type) for sample in samples],
        event_matrix,
    )
    sentiment_model.fit(
        [sample.text for sample in samples],
        [sample.sentiment for sample in samples],
    )
    importance_model.fit(
        [_importance_text(sample.text, sample.source_type) for sample in samples],
        [sample.importance for sample in samples],
    )
    return {
        "event_model": event_model,
        "event_binarizer": event_binarizer,
        "sentiment_model": sentiment_model,
        "importance_model": importance_model,
    }


def _teacher_predict(
    teacher: dict[str, Any],
    sample: LabeledAlert,
) -> tuple[LabeledAlert, float] | None:
    event_probabilities = teacher["event_model"].predict_proba(
        [_event_text(sample.text, sample.source_type)]
    )[0]
    event_classes = list(teacher["event_binarizer"].classes_)
    event_tags = _event_tags_from_probabilities(event_classes, event_probabilities, threshold=0.42)
    event_confidence = float(max(event_probabilities) if len(event_probabilities) else 0.0)
    if event_confidence < 0.58:
        return None

    sentiment_probabilities = teacher["sentiment_model"].predict_proba([sample.text])[0]
    sentiment_classes = list(teacher["sentiment_model"].classes_)
    sentiment_index = int(
        max(range(len(sentiment_probabilities)), key=sentiment_probabilities.__getitem__)
    )
    sentiment_confidence = float(sentiment_probabilities[sentiment_index])
    if sentiment_confidence < 0.72:
        return None

    importance_probabilities = teacher["importance_model"].predict_proba(
        [_importance_text(sample.text, sample.source_type)]
    )[0]
    importance_classes = list(teacher["importance_model"].classes_)
    importance_index = int(
        max(range(len(importance_probabilities)), key=importance_probabilities.__getitem__)
    )
    importance_confidence = float(importance_probabilities[importance_index])
    if importance_confidence < 0.68:
        return None

    score = event_confidence + sentiment_confidence + importance_confidence
    return (
        LabeledAlert(
            text=sample.text,
            tags=sorted(event_tags),
            sentiment=cast(Sentiment, sentiment_classes[sentiment_index]),
            importance=cast(Importance, importance_classes[importance_index]),
            source_type=sample.source_type,
            stock_code=sample.stock_code,
            stock_name=sample.stock_name,
        ),
        score,
    )


def _primary_label(tags: list[str]) -> str:
    priority = (
        "RISK",
        "CONTRACT",
        "CAPITAL_ACTION",
        "CORPORATE_ACTION",
        "EARNINGS",
        "MACRO",
        "DISCLOSURE",
        "GENERAL_MARKET",
    )
    tag_set = set(tags)
    for label in priority:
        if label in tag_set:
            return label
    return "GENERAL_MARKET"


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def _char_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        min_df=1,
        max_features=120_000,
        sublinear_tf=True,
    )


def _hybrid_vectorizer() -> FeatureUnion:
    return FeatureUnion(
        [
            (
                "char_wb",
                _char_vectorizer(),
            ),
            (
                "financial_word",
                TfidfVectorizer(
                    tokenizer=financial_tokenize,
                    token_pattern=None,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=80_000,
                    sublinear_tf=True,
                    lowercase=False,
                ),
            ),
        ],
        transformer_weights={
            "char_wb": 1.0,
            "financial_word": 1.2,
        },
    )


def financial_tokenize(text: str) -> list[str]:
    normalized_text = text.lower()
    tokens = _TOKEN_PATTERN.findall(normalized_text)
    compact_text = _NON_TOKEN_CHAR_PATTERN.sub("", normalized_text)

    # 한국어 금융 복합어는 띄어쓰기와 조사 때문에 일반 token split만으로 놓치기 쉽다.
    domain_tokens = [
        f"finance:{term}"
        for term in FINANCIAL_DOMAIN_TERMS
        if _NON_TOKEN_CHAR_PATTERN.sub("", term) in compact_text
    ]
    return [*tokens, *domain_tokens]


def _importance_text(text: str, source_type: str) -> str:
    return f"source_type={source_type} {text}"


def _event_text(text: str, source_type: str) -> str:
    return f"source_type={source_type} {text}"


def _event_distribution(samples: list[LabeledAlert]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for sample in samples:
        counter.update(sample.tags)
    return dict(counter)


def _validate_holdout(samples: list[LabeledAlert]) -> MlValidationReport:
    stratify_labels = _safe_stratify_labels(samples)
    train_samples, validation_samples = train_test_split(
        samples,
        test_size=0.2,
        random_state=42,
        stratify=stratify_labels,
    )

    event_binarizer = MultiLabelBinarizer()
    event_train_matrix = event_binarizer.fit_transform([sample.tags for sample in train_samples])

    event_model = _event_model()
    sentiment_model = _single_label_model()
    importance_model = _importance_model()

    event_model.fit(
        [_event_text(sample.text, sample.source_type) for sample in train_samples],
        event_train_matrix,
    )
    sentiment_model.fit(
        [sample.text for sample in train_samples],
        [sample.sentiment for sample in train_samples],
    )
    importance_model.fit(
        [_importance_text(sample.text, sample.source_type) for sample in train_samples],
        [sample.importance for sample in train_samples],
    )

    probabilities = event_model.predict_proba(
        [_event_text(sample.text, sample.source_type) for sample in validation_samples]
    )
    event_classes = list(event_binarizer.classes_)
    predicted_event_tags = [
        _event_tags_from_probabilities(event_classes, row, threshold=0.35)
        for row in probabilities
    ]
    expected_event_tags = [set(sample.tags) for sample in validation_samples]

    predicted_sentiments = list(
        sentiment_model.predict([sample.text for sample in validation_samples])
    )
    expected_sentiments = [sample.sentiment for sample in validation_samples]

    predicted_importance = list(
        importance_model.predict(
            [_importance_text(sample.text, sample.source_type) for sample in validation_samples]
        )
    )
    expected_importance = [sample.importance for sample in validation_samples]

    event_metrics = _event_label_metrics(expected_event_tags, predicted_event_tags)
    return MlValidationReport(
        sample_count=len(validation_samples),
        train_sample_count=len(train_samples),
        event_subset_recall=_subset_recall(expected_event_tags, predicted_event_tags),
        event_macro_f1=_macro_f1(event_metrics),
        sentiment_accuracy=_accuracy(expected_sentiments, predicted_sentiments),
        importance_accuracy=_accuracy(expected_importance, predicted_importance),
        event_label_metrics=event_metrics,
        sentiment_confusion_matrix=_confusion_matrix(expected_sentiments, predicted_sentiments),
        importance_confusion_matrix=_confusion_matrix(expected_importance, predicted_importance),
    )


def _event_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                    )
                ),
            ),
        ]
    )


def _single_label_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def _importance_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def _event_tags_from_probabilities(
    classes: list[str],
    probabilities: Any,
    threshold: float,
) -> set[str]:
    tags = {
        str(label)
        for label, probability in zip(classes, probabilities, strict=True)
        if probability >= threshold
    }
    if tags:
        return tags
    top_index = int(max(range(len(probabilities)), key=lambda index: probabilities[index]))
    return {str(classes[top_index])} if classes else {"GENERAL_MARKET"}


def _event_label_metrics(
    expected_tags: list[set[str]],
    predicted_tags: list[set[str]],
) -> dict[str, dict[str, float | int]]:
    labels = sorted(set().union(*expected_tags, *predicted_tags))
    metrics: dict[str, dict[str, float | int]] = {}
    for label in labels:
        true_positive = sum(
            1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
            if label in expected and label in predicted
        )
        false_positive = sum(
            1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
            if label not in expected and label in predicted
        )
        false_negative = sum(
            1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
            if label in expected and label not in predicted
        )
        precision = _safe_divide(true_positive, true_positive + false_positive)
        recall = _safe_divide(true_positive, true_positive + false_negative)
        metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1": _f1(precision, recall),
            "support": sum(1 for expected in expected_tags if label in expected),
        }
    return metrics


def _subset_recall(expected_tags: list[set[str]], predicted_tags: list[set[str]]) -> float:
    hits = sum(
        1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
        if expected.issubset(predicted)
    )
    return _safe_divide(hits, len(expected_tags))


def _macro_f1(metrics: dict[str, dict[str, float | int]]) -> float:
    if not metrics:
        return 0.0
    return sum(float(metric["f1"]) for metric in metrics.values()) / len(metrics)


def _accuracy(expected: list[str], predicted: list[str]) -> float:
    hits = sum(1 for left, right in zip(expected, predicted, strict=True) if left == right)
    return _safe_divide(hits, len(expected))


def _confusion_matrix(expected: list[str], predicted: list[str]) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = {}
    for expected_label, predicted_label in zip(expected, predicted, strict=True):
        matrix.setdefault(expected_label, {})
        matrix[expected_label][predicted_label] = matrix[expected_label].get(predicted_label, 0) + 1
    return {
        expected_label: dict(sorted(predictions.items()))
        for expected_label, predictions in sorted(matrix.items())
    }


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _safe_divide(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _safe_stratify_labels(samples: list[LabeledAlert]) -> list[str] | None:
    labels = [sample.tags[0] for sample in samples]
    counts = Counter(labels)
    if min(counts.values(), default=0) < 2:
        return None
    return labels
