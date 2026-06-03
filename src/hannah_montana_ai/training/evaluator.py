from dataclasses import dataclass

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import LabeledAlert


@dataclass(frozen=True)
class EvaluationResult:
    sample_count: int
    event_tag_recall: float
    sentiment_accuracy: float
    importance_accuracy: float
    stock_accuracy: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "sample_count": self.sample_count,
            "event_tag_recall": self.event_tag_recall,
            "sentiment_accuracy": self.sentiment_accuracy,
            "importance_accuracy": self.importance_accuracy,
            "stock_accuracy": self.stock_accuracy,
        }


def evaluate_alert_analyzer(
    samples: list[LabeledAlert],
    analyzer: AlertAnalyzer,
) -> EvaluationResult:
    event_hits = 0
    sentiment_hits = 0
    importance_hits = 0
    stock_hits = 0

    for sample in samples:
        request = _request_from_sample(sample)
        prediction = analyzer.analyze(request)
        if set(sample.tags).issubset(set(prediction.event_tags)):
            event_hits += 1
        if prediction.sentiment == sample.sentiment:
            sentiment_hits += 1
        if prediction.importance == sample.importance:
            importance_hits += 1
        if prediction.stock_code == sample.stock_code:
            stock_hits += 1

    total = len(samples)
    return EvaluationResult(
        sample_count=total,
        event_tag_recall=event_hits / total,
        sentiment_accuracy=sentiment_hits / total,
        importance_accuracy=importance_hits / total,
        stock_accuracy=stock_hits / total,
    )


def _request_from_sample(sample: LabeledAlert) -> AlertAnalysisRequest:
    stock_universe = []
    if sample.stock_code and sample.stock_name:
        stock_universe.append(
            StockCandidate(
                stock_code=sample.stock_code,
                stock_name=sample.stock_name,
                stock_name_en=sample.stock_name,
                aliases=[],
            )
        )

    return AlertAnalysisRequest.model_validate(
        {
            "source_type": sample.source_type,
            "title": sample.text,
            "snippet": "",
            "original_url": "https://example.com/evaluation",
            "stock_universe": [stock.model_dump() for stock in stock_universe],
        }
    )
