import re
from hashlib import sha256

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    StockCandidate,
)
from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine


class AlertAnalyzer:
    def __init__(self) -> None:
        settings = get_settings()
        self.rule_engine = FinancialRuleEngine()
        self.model = MachineLearningFinancialNlpModel(settings.model_path)

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
        matches = self._stock_matches(text, stock_universe)
        return matches[0][1] if matches else None

    def _match_related_stocks(self, text: str, stock_universe: list[StockCandidate]) -> list[str]:
        return [stock.stock_code for _, stock in self._stock_matches(text, stock_universe)]

    def _stock_matches(
        self,
        text: str,
        stock_universe: list[StockCandidate],
    ) -> list[tuple[int, StockCandidate]]:
        normalized_text = self._normalize_for_match(text)
        matches: list[tuple[int, StockCandidate]] = []
        seen_codes: set[str] = set()

        for stock in stock_universe:
            position = self._stock_match_position(normalized_text, stock)
            if position is not None and stock.stock_code not in seen_codes:
                matches.append((position, stock))
                seen_codes.add(stock.stock_code)

        return sorted(matches, key=lambda match: match[0])

    def _stock_match_position(self, normalized_text: str, stock: StockCandidate) -> int | None:
        candidates = [stock.stock_code, stock.stock_name, stock.stock_name_en, *stock.aliases]
        positions = [
            normalized_text.find(self._normalize_for_match(candidate))
            for candidate in candidates
            if candidate
        ]
        found_positions = [position for position in positions if position >= 0]
        return min(found_positions) if found_positions else None

    def _duplicate_key(self, source_type: str, title: str, stock_code: str | None) -> str:
        normalized = self._normalize_for_match(title)
        raw_key = f"{source_type}:{stock_code or 'UNKNOWN'}:{normalized}"
        return sha256(raw_key.encode("utf-8")).hexdigest()

    def _normalize_for_match(self, value: str) -> str:
        lowered = value.lower()
        return re.sub(r"[^0-9a-z가-힣]+", "", lowered)
