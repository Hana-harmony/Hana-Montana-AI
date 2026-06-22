import re
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import cast

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    Importance,
    Sentiment,
    StockCandidate,
)
from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine
from hannah_montana_ai.services.stock_linker import MachineLearningStockLinker
from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    load_stock_universe,
    normalize_stock_term,
)


@dataclass(frozen=True)
class StockMatchResult:
    stock: StockCandidate | StockUniverseEntry | None
    confidence: float


class AlertAnalyzer:
    _DUPLICATE_BRACKET_NOISE_TERMS = frozenset(
        {
            "속보",
            "단독",
            "종합",
            "상보",
            "공시",
            "특징주",
            "마켓인사이트",
            "투자노트",
            "시황",
            "장중시황",
            "마감시황",
        }
    )
    _DUPLICATE_BRACKET_PATTERN = re.compile(
        r"\[[^\]]{1,20}\]|\([^)]{1,20}\)|【[^】]{1,20}】|〈[^〉]{1,20}〉"
    )
    _DUPLICATE_LEADING_NOISE_PATTERN = re.compile(
        r"^\s*(?:속보|단독|종합|상보|특징주|공시)\s*[:：\-]\s*",
        re.IGNORECASE,
    )
    _DUPLICATE_TAIL_NOISE_PATTERNS = (
        re.compile(
            r"\s*[-|/]\s*(?:연합뉴스|한국경제|매일경제|머니투데이|이데일리|서울경제|"
            r"파이낸셜뉴스|뉴스1|뉴시스|조선비즈|Reuters|Bloomberg)\s*$",
            re.IGNORECASE,
        ),
        re.compile(r"\s*[-|/]\s*[가-힣]{2,4}\s*기자\s*$"),
        re.compile(r"\s+[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\s*$", re.IGNORECASE),
    )
    _MACRO_CONTEXT_TERMS = ("수출", "업황", "공급망", "환율", "금리", "물가")
    _GENERAL_MARKET_CONTEXT_TERMS = ("시총", "주가 급등", "증시")

    def __init__(self) -> None:
        settings = get_settings()
        self.rule_engine = FinancialRuleEngine()
        self.model = MachineLearningFinancialNlpModel(settings.model_path)
        self.stock_linker = MachineLearningStockLinker(settings.stock_linker_model_path)
        self._internal_stock_universe = _load_internal_stock_universe(
            settings.stock_universe_path
        )
        self._internal_stock_by_code = {
            stock.stock_code: stock for stock in self._internal_stock_universe
        }

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        text = f"{request.title} {request.snippet} {request.content}".strip()
        primary_stock_match = self._match_primary_stock_from_request_or_internal(
            text,
            request.stock_universe,
        )
        primary_stock = primary_stock_match.stock
        event_probabilities = self.model.event_tag_probabilities(text, request.source_type)
        event_tags = self._augment_event_tags(
            text,
            request.source_type,
            self.model.predict_event_tags(text, request.source_type),
        )
        sentiment_probabilities = self.model.sentiment_probabilities(text)
        sentiment = cast(Sentiment, self._top_label(sentiment_probabilities, fallback="NEUTRAL"))
        importance_probabilities = self.model.importance_probabilities(text, request.source_type)
        importance = cast(
            Importance,
            self._top_label(importance_probabilities, fallback="MEDIUM"),
        )
        related_stocks = self._match_related_stocks_from_request_or_internal(
            text,
            request.stock_universe,
        )

        stock_code = primary_stock.stock_code if primary_stock else None
        stock_name = primary_stock.stock_name if primary_stock else None
        event_confidence = self._event_confidence(event_tags, event_probabilities)
        sentiment_confidence = sentiment_probabilities.get(sentiment, 0.0)
        importance_confidence = importance_probabilities.get(importance, 0.0)
        summary_lines = self.rule_engine.summarize_what_why_impact(
            request.title,
            request.snippet,
            request.content,
            importance,
            sentiment,
        )
        summary = "\n".join(
            line for line in (summary_lines.what, summary_lines.why, summary_lines.impact) if line
        )
        duplicate_key = self._duplicate_key(request.source_type, request.title, stock_code)

        return AlertAnalysisResponse(
            stock_code=stock_code,
            stock_name=stock_name,
            source_type=request.source_type,
            original_title=request.title,
            summary=summary,
            summary_lines=summary_lines,
            content_availability="FULL_TEXT" if request.content else "SUMMARY_ONLY",
            original_content=request.content,
            image_urls=request.image_urls,
            event_tags=event_tags,
            sentiment=sentiment,
            importance=importance,
            related_stocks=related_stocks,
            holder_target=self.rule_engine.holder_target(importance),
            watchlist_target=self.rule_engine.watchlist_target(importance),
            duplicate_key=duplicate_key,
            cluster_key=self._cluster_key(request, stock_code, duplicate_key),
            model_version=self.model.version,
            event_confidence=round(event_confidence, 6),
            sentiment_confidence=round(sentiment_confidence, 6),
            importance_confidence=round(importance_confidence, 6),
            stock_match_confidence=round(primary_stock_match.confidence, 6),
        )

    def _match_primary_stock(
        self,
        text: str,
        stock_universe: Sequence[StockCandidate | StockUniverseEntry],
        *,
        allow_short_terms: bool = False,
    ) -> StockCandidate | StockUniverseEntry | None:
        matches = self._stock_matches(
            text,
            stock_universe,
            allow_short_terms=allow_short_terms,
        )
        return matches[0][1] if matches else None

    def _match_primary_stock_from_request_or_internal(
        self,
        text: str,
        request_universe: list[StockCandidate],
    ) -> StockMatchResult:
        request_match = self._match_primary_stock(
            text,
            request_universe,
            allow_short_terms=True,
        )
        if request_match is not None:
            return StockMatchResult(request_match, 1.0)
        ml_match = self._match_leading_internal_stock_with_ml(text)
        if ml_match is not None:
            return ml_match
        internal_match = self._match_leading_internal_stock(text)
        if internal_match is not None:
            return StockMatchResult(internal_match, 0.94)
        return StockMatchResult(None, 0.0)

    def _match_leading_internal_stock_with_ml(
        self,
        text: str,
    ) -> StockMatchResult | None:
        prediction = self.stock_linker.predict_stock_code_with_score(text)
        if prediction is None:
            return None
        stock_code, score = prediction
        stock = self._internal_stock_by_code.get(stock_code)
        if stock is None:
            return None
        position = self._stock_match_position(
            normalize_stock_term(text),
            stock,
            allow_short_terms=False,
        )
        if position != 0:
            return None
        return StockMatchResult(stock, min(max(score, 0.0), 1.0))

    def _match_leading_internal_stock(
        self,
        text: str,
    ) -> StockUniverseEntry | None:
        matches = self._stock_matches(text, self._internal_stock_universe)
        return cast(StockUniverseEntry, matches[0][1]) if matches and matches[0][0] == 0 else None

    def _match_related_stocks(
        self,
        text: str,
        stock_universe: Sequence[StockCandidate | StockUniverseEntry],
        *,
        allow_short_terms: bool = False,
    ) -> list[str]:
        return [
            stock.stock_code
            for _, stock in self._stock_matches(
                text,
                stock_universe,
                allow_short_terms=allow_short_terms,
            )
        ]

    def _match_related_stocks_from_request_or_internal(
        self,
        text: str,
        request_universe: list[StockCandidate],
    ) -> list[str]:
        matches = [
            *self._stock_matches(text, request_universe, allow_short_terms=True),
            *self._stock_matches(
                text,
                self._internal_stock_universe,
                allow_short_terms=False,
            ),
        ]
        deduplicated: list[tuple[int, StockCandidate | StockUniverseEntry]] = []
        seen_codes: set[str] = set()
        for position, stock in sorted(matches, key=lambda match: match[0]):
            if stock.stock_code in seen_codes:
                continue
            deduplicated.append((position, stock))
            seen_codes.add(stock.stock_code)
        return [stock.stock_code for _, stock in deduplicated]

    def _stock_matches(
        self,
        text: str,
        stock_universe: Sequence[StockCandidate | StockUniverseEntry],
        *,
        allow_short_terms: bool = False,
    ) -> list[tuple[int, StockCandidate | StockUniverseEntry]]:
        normalized_text = normalize_stock_term(text)
        matches: list[tuple[int, StockCandidate | StockUniverseEntry]] = []
        seen_codes: set[str] = set()

        for stock in stock_universe:
            position = self._stock_match_position(
                normalized_text,
                stock,
                allow_short_terms=allow_short_terms,
            )
            if position is not None and stock.stock_code not in seen_codes:
                matches.append((position, stock))
                seen_codes.add(stock.stock_code)

        return sorted(matches, key=lambda match: match[0])

    def _stock_match_position(
        self,
        normalized_text: str,
        stock: StockCandidate | StockUniverseEntry,
        *,
        allow_short_terms: bool = False,
    ) -> int | None:
        candidates = [stock.stock_code, stock.stock_name, stock.stock_name_en, *stock.aliases]
        positions = [
            normalized_text.find(normalized_candidate)
            for candidate in candidates
            if candidate
            if (normalized_candidate := normalize_stock_term(candidate))
            if allow_short_terms or self._is_usable_stock_match_term(normalized_candidate)
        ]
        found_positions = [position for position in positions if position >= 0]
        return min(found_positions) if found_positions else None

    def _stock_universe_for_request(
        self,
        request_universe: list[StockCandidate],
    ) -> tuple[StockCandidate | StockUniverseEntry, ...]:
        merged: list[StockCandidate | StockUniverseEntry] = []
        seen_codes: set[str] = set()
        for request_stock in request_universe:
            if request_stock.stock_code in seen_codes:
                continue
            merged.append(request_stock)
            seen_codes.add(request_stock.stock_code)
        for internal_stock in self._internal_stock_universe:
            if internal_stock.stock_code in seen_codes:
                continue
            merged.append(internal_stock)
            seen_codes.add(internal_stock.stock_code)
        return tuple(merged)

    def _is_usable_stock_match_term(self, value: str) -> bool:
        if value.isdigit() and len(value) == 6:
            return True
        return len(value) >= 3

    def _event_confidence(
        self,
        event_tags: list[str],
        event_probabilities: dict[str, float],
    ) -> float:
        if not event_tags:
            return 0.0
        return max(event_probabilities.get(tag, 0.0) for tag in event_tags)

    def _augment_event_tags(
        self,
        text: str,
        source_type: str,
        event_tags: list[str],
    ) -> list[str]:
        if source_type != "NEWS":
            return event_tags

        tag_set = set(event_tags)
        if self._has_macro_context(text):
            tag_set.add("MACRO")
        if any(term in text for term in self._GENERAL_MARKET_CONTEXT_TERMS):
            tag_set.add("GENERAL_MARKET")
        return sorted(tag_set)

    def _has_macro_context(self, text: str) -> bool:
        if any(term in text for term in self._MACRO_CONTEXT_TERMS):
            return True
        return "정책" in text and ("지원" in text or "중소기업" in text)

    def _top_label(self, probabilities: dict[str, float], *, fallback: str) -> str:
        if not probabilities:
            return fallback
        return max(probabilities.items(), key=lambda item: item[1])[0]

    def _duplicate_key(self, source_type: str, title: str, stock_code: str | None) -> str:
        normalized = self._normalize_duplicate_title(title)
        raw_key = f"{source_type.upper()}:{stock_code or 'UNKNOWN'}:{normalized}"
        return sha256(raw_key.encode("utf-8")).hexdigest()

    def _cluster_key(
        self,
        request: AlertAnalysisRequest,
        stock_code: str | None,
        duplicate_key: str,
    ) -> str:
        source = request.source_type.upper()
        stock = stock_code or "UNKNOWN"
        if request.content_hash:
            raw_key = f"{source}:{stock}:{request.content_hash}"
            return sha256(raw_key.encode("utf-8")).hexdigest()
        if request.content:
            raw_key = f"{source}:{stock}:{request.content[:600]}"
            return sha256(raw_key.encode("utf-8")).hexdigest()
        return duplicate_key

    def _normalize_duplicate_title(self, title: str) -> str:
        canonical_title = self._strip_duplicate_bracket_noise(title)
        canonical_title = self._DUPLICATE_LEADING_NOISE_PATTERN.sub("", canonical_title)
        for pattern in self._DUPLICATE_TAIL_NOISE_PATTERNS:
            canonical_title = pattern.sub("", canonical_title)
        return self._normalize_for_match(canonical_title)

    def _strip_duplicate_bracket_noise(self, title: str) -> str:
        def replace_noise(match: re.Match[str]) -> str:
            text = match.group(0)[1:-1]
            normalized = self._normalize_for_match(text)
            if normalized in self._DUPLICATE_BRACKET_NOISE_TERMS:
                return " "
            return match.group(0)

        return self._DUPLICATE_BRACKET_PATTERN.sub(replace_noise, title)

    def _normalize_for_match(self, value: str) -> str:
        lowered = value.lower()
        return re.sub(r"[^0-9a-z가-힣]+", "", lowered)


@lru_cache
def _load_internal_stock_universe(
    stock_universe_path: Path,
) -> tuple[StockUniverseEntry, ...]:
    return tuple(load_stock_universe(stock_universe_path))
