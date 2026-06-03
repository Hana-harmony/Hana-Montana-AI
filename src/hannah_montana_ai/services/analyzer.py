from hashlib import sha256

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    StockCandidate,
)
from hannah_montana_ai.services.model import KeywordFinancialNlpModel
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine


class AlertAnalyzer:
    def __init__(self) -> None:
        settings = get_settings()
        self.rule_engine = FinancialRuleEngine()
        self.model = KeywordFinancialNlpModel(settings.model_path)

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        text = f"{request.title} {request.snippet}"
        primary_stock = self._match_primary_stock(text, request.stock_universe)
        event_tags = self.model.predict_event_tags(text)
        sentiment = self.model.classify_sentiment(text)
        importance = self.model.classify_importance(text, request.source_type)
        related_stocks = self._match_related_stocks(text, request.stock_universe)

        stock_code = primary_stock.stock_code if primary_stock else None
        stock_name = primary_stock.stock_name if primary_stock else None

        return AlertAnalysisResponse(
            stock_code=stock_code,
            stock_name=stock_name,
            source_type=request.source_type,
            original_title=request.title,
            summary=self.rule_engine.summarize(request.title, request.snippet),
            event_tags=event_tags,
            sentiment=sentiment,
            importance=importance,
            related_stocks=related_stocks,
            holder_target=self.rule_engine.holder_target(importance),
            watchlist_target=self.rule_engine.watchlist_target(importance),
            duplicate_key=self._duplicate_key(request.source_type, request.title, stock_code),
            model_version=self.model.version,
        )

    def _match_primary_stock(
        self,
        text: str,
        stock_universe: list[StockCandidate],
    ) -> StockCandidate | None:
        for stock in stock_universe:
            if self._stock_in_text(text, stock):
                return stock
        return None

    def _match_related_stocks(self, text: str, stock_universe: list[StockCandidate]) -> list[str]:
        return [stock.stock_code for stock in stock_universe if self._stock_in_text(text, stock)]

    def _stock_in_text(self, text: str, stock: StockCandidate) -> bool:
        return (
            stock.stock_code in text
            or stock.stock_name in text
            or stock.stock_name_en.lower() in text.lower()
        )

    def _duplicate_key(self, source_type: str, title: str, stock_code: str | None) -> str:
        normalized = " ".join(title.lower().split())
        raw_key = f"{source_type}:{stock_code or 'UNKNOWN'}:{normalized}"
        return sha256(raw_key.encode("utf-8")).hexdigest()
