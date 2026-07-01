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
    BodySourceType,
    FinancialGlossaryTerm,
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
    _FINANCIAL_GLOSSARY = (
        (
            "개미",
            "retail investors",
            "market_slang",
            ("개미투자자", "개미 투자자", "동학개미", "서학개미"),
        ),
        ("대장주", "bellwether stock", "market_slang", ("대표주", "주도주")),
        ("따따블", "IPO quadruple jump", "ipo_slang", ("공모가 4배",)),
        ("품절주", "low-float stock", "market_slang", ()),
        ("빚투", "leveraged retail investing", "risk_slang", ()),
        ("어닝쇼크", "earnings shock", "event", ()),
        ("어닝서프라이즈", "earnings surprise", "event", ()),
        ("실적", "earnings", "event", ()),
        ("공시", "disclosure", "source", ()),
        ("외국인", "foreign investors", "investor_type", ()),
        ("기관", "institutional investors", "investor_type", ()),
        ("개인", "individual investors", "investor_type", ()),
    )
    _SUMMARY_ONLY_CONFIDENCE_CAP = 0.55
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
    _RISK_CONTEXT_TERMS = (
        "감사의견 거절",
        "거래정지",
        "리스크",
        "변동성",
        "생산차질",
        "소송",
        "소액주주",
        "우려",
        "적자",
        "차질",
        "철회",
        "흔들",
    )
    _CORPORATE_ACTION_CONTEXT_TERMS = (
        "리밸런싱",
        "매각",
        "분할",
        "사업재편",
        "인수",
        "주식교환",
        "지분 인수",
        "지분인수",
        "지분 취득",
        "지분취득",
        "지분투자",
        "최대주주",
        "합병",
    )
    _EARNINGS_CONTEXT_TERMS = (
        "사상 최대",
        "수익성",
        "순이익",
        "성장 재편",
        "실적 개선",
        "영업이익",
        "적자",
        "턴어라운드",
        "호황",
        "흑자",
    )
    _NEGATIVE_SENTIMENT_CONTEXT_TERMS = (
        "감소",
        "경계",
        "리스크",
        "변동성",
        "생산차질",
        "손실",
        "압박",
        "우려",
        "적자",
        "차질",
        "철회",
        "하락",
        "흔들",
    )
    _NEUTRAL_SENTIMENT_CONTEXT_TERMS = (
        "될까",
        "변수",
        "압박",
        "재검토",
        "정체",
        "흔들림",
    )
    _SEVERE_NEGATIVE_SENTIMENT_CONTEXT_TERMS = (
        "감사의견 거절",
        "거래정지",
        "생산차질",
        "손실",
        "소송",
        "우려",
        "적자",
        "차질",
        "철회",
        "하락",
    )
    _POSITIVE_SENTIMENT_CONTEXT_TERMS = (
        "개선",
        "계약",
        "성장",
        "수주",
        "증가",
        "들썩",
        "등극",
        "청신호",
        "주목",
        "지분 인수",
        "지분인수",
        "지분투자",
        "턴어라운드",
        "호실적",
        "흑자",
    )
    _STOCK_ATTRIBUTION_CONTEXT_TERMS = ("연구원", "애널리스트", "리서치", "센터장")
    _INTERNAL_STOCK_MATCH_EXCLUDED_NAMES = frozenset(
        {
            "국민은행",
            "신한은행",
            "우리은행",
            "하나은행",
        }
    )

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
        has_full_content = bool(request.content.strip())
        analysis_content = self.rule_engine.clean_article_text(request.content, request.title)
        text = f"{request.title} {request.snippet} {analysis_content}".strip()
        primary_stock_match = self._match_primary_stock_from_request_or_internal(
            request.title,
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
        sentiment = self._augment_sentiment(text, sentiment)
        importance_probabilities = self.model.importance_probabilities(text, request.source_type)
        importance = cast(
            Importance,
            self._top_label(importance_probabilities, fallback="MEDIUM"),
        )
        importance = self._augment_importance(text, request.source_type, importance)
        related_stocks = self._match_related_stocks_from_request_or_internal(
            text,
            request.stock_universe,
        )

        stock_code = primary_stock.stock_code if primary_stock else None
        stock_name = primary_stock.stock_name if primary_stock else None
        event_confidence = self._event_confidence(event_tags, event_probabilities)
        sentiment_confidence = sentiment_probabilities.get(sentiment, 0.0)
        importance_confidence = importance_probabilities.get(importance, 0.0)
        event_confidence, sentiment_confidence, importance_confidence = (
            self._cap_summary_only_confidences(
                has_full_content,
                event_confidence,
                sentiment_confidence,
                importance_confidence,
            )
        )
        summary_lines = self.rule_engine.summarize_what_why_impact(
            request.title,
            request.snippet,
            analysis_content,
            importance,
            sentiment,
        )
        summary = "\n".join(
            line for line in (summary_lines.what, summary_lines.why, summary_lines.impact) if line
        )
        glossary_terms = self._extract_financial_glossary_terms(text)
        duplicate_key = self._duplicate_key(request.source_type, request.title, stock_code)

        return AlertAnalysisResponse(
            stock_code=stock_code,
            stock_name=stock_name,
            source_type=request.source_type,
            original_title=request.title,
            summary=summary,
            summary_lines=summary_lines,
            content_availability="FULL_TEXT" if has_full_content else "SUMMARY_ONLY",
            original_content=request.content,
            original_body=request.content,
            body_source_type=_body_source_type(request.source_type, request.content),
            image_urls=request.image_urls,
            event_tags=event_tags,
            sentiment=sentiment,
            importance=importance,
            related_stocks=related_stocks,
            holder_target=self.rule_engine.holder_target(importance),
            watchlist_target=self.rule_engine.watchlist_target(importance),
            glossary_terms=glossary_terms,
            translation_quality_flags=(
                ["FINANCIAL_GLOSSARY_APPLIED"] if glossary_terms else []
            ),
            duplicate_key=duplicate_key,
            cluster_key=self._cluster_key(request, stock_code, duplicate_key),
            model_version=self.model.version,
            event_confidence=round(event_confidence, 6),
            sentiment_confidence=round(sentiment_confidence, 6),
            importance_confidence=round(importance_confidence, 6),
            stock_match_confidence=round(primary_stock_match.confidence, 6),
        )

    def _extract_financial_glossary_terms(self, text: str) -> list[FinancialGlossaryTerm]:
        matched_terms: list[FinancialGlossaryTerm] = []
        seen_terms: set[str] = set()
        for normalized_term, english_term, category, aliases in sorted(
            self._FINANCIAL_GLOSSARY,
            key=lambda entry: max(len(term) for term in (entry[0], *entry[3])),
            reverse=True,
        ):
            source_term = next(
                (term for term in (normalized_term, *aliases) if term and term in text),
                "",
            )
            if not source_term or normalized_term in seen_terms:
                continue
            matched_terms.append(
                FinancialGlossaryTerm(
                    source_term=source_term,
                    normalized_term=normalized_term,
                    english_term=english_term,
                    category=category,
                )
            )
            seen_terms.add(normalized_term)
        return matched_terms

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
        return sorted(matches, key=lambda match: match[0])[0][1] if matches else None

    def _match_primary_stock_from_request_or_internal(
        self,
        title: str,
        text: str,
        request_universe: list[StockCandidate],
    ) -> StockMatchResult:
        ambiguous_replacement = self._longer_internal_match_for_ambiguous_request_title(
            title,
            text,
            request_universe,
        )
        if ambiguous_replacement is not None:
            return StockMatchResult(ambiguous_replacement, 0.97)
        title_match = self._best_primary_stock_match(
            title,
            request_universe,
            prefer_request=True,
        )
        if title_match is not None:
            confidence = 1.0 if title_match in request_universe else 0.97
            return StockMatchResult(title_match, confidence)
        exact_match = self._best_primary_stock_match(
            text,
            request_universe,
            prefer_request=True,
        )
        if exact_match is not None:
            confidence = 1.0 if exact_match in request_universe else 0.96
            return StockMatchResult(exact_match, confidence)
        ml_match = self._match_leading_internal_stock_with_ml(text)
        if ml_match is not None:
            return ml_match
        internal_match = self._match_leading_internal_stock(text)
        if internal_match is not None:
            return StockMatchResult(internal_match, 0.94)
        return StockMatchResult(None, 0.0)

    def _best_primary_stock_match(
        self,
        text: str,
        request_universe: list[StockCandidate],
        *,
        prefer_request: bool = False,
    ) -> StockCandidate | StockUniverseEntry | None:
        request_matches = self._stock_matches(text, request_universe, allow_short_terms=True)
        if prefer_request and request_matches:
            internal_matches = self._stock_matches(text, self._internal_stock_universe)
            specific_internal_match = self._more_specific_same_position_match(
                request_matches[0],
                internal_matches,
            )
            if specific_internal_match is not None:
                return specific_internal_match
            return request_matches[0][1]
        matches = [
            *request_matches,
            *self._stock_matches(text, self._internal_stock_universe),
        ]
        return sorted(matches, key=lambda match: match[0])[0][1] if matches else None

    def _longer_internal_match_for_ambiguous_request_title(
        self,
        title: str,
        text: str,
        request_universe: list[StockCandidate],
    ) -> StockUniverseEntry | None:
        request_matches = self._stock_matches(title, request_universe, allow_short_terms=True)
        if not request_matches:
            return None
        request_stock = request_matches[0][1]
        if not self._is_ambiguous_short_request_stock(request_stock):
            return None
        for _, internal_stock in self._stock_matches(text, self._internal_stock_universe):
            if not isinstance(internal_stock, StockUniverseEntry):
                continue
            if internal_stock.stock_code == request_stock.stock_code:
                continue
            if self._stock_match_specificity(internal_stock) <= self._stock_match_specificity(
                request_stock
            ):
                continue
            if self._is_shadowing_stock_match(
                (request_matches[0][0], request_stock),
                (request_matches[0][0], internal_stock),
            ) or self._stock_terms_contain(internal_stock, request_stock):
                return internal_stock
        return None

    def _is_ambiguous_short_request_stock(
        self,
        stock: StockCandidate | StockUniverseEntry,
    ) -> bool:
        normalized_name = normalize_stock_term(stock.stock_name)
        return bool(normalized_name) and len(normalized_name) <= 2

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
        matches = self._drop_shadowed_short_stock_matches(matches)
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
            if self._is_excluded_stock(stock):
                continue
            position = self._stock_match_position(
                normalized_text,
                stock,
                allow_short_terms=allow_short_terms,
            )
            if position is not None and stock.stock_code not in seen_codes:
                matches.append((position, stock))
                seen_codes.add(stock.stock_code)

        return sorted(
            matches,
            key=lambda match: (
                match[0],
                -self._stock_match_specificity(match[1]),
                match[1].stock_code,
            ),
        )

    def _stock_match_position(
        self,
        normalized_text: str,
        stock: StockCandidate | StockUniverseEntry,
        *,
        allow_short_terms: bool = False,
    ) -> int | None:
        candidates = [stock.stock_code, stock.stock_name, stock.stock_name_en, *stock.aliases]
        found_positions: list[int] = []
        for candidate in candidates:
            if not candidate:
                continue
            normalized_candidate = normalize_stock_term(candidate)
            if not normalized_candidate:
                continue
            if not allow_short_terms and not self._is_usable_stock_match_term(
                normalized_candidate
            ):
                continue
            start = 0
            while True:
                position = normalized_text.find(normalized_candidate, start)
                if position < 0:
                    break
                if not self._is_stock_attribution_context(
                    normalized_text,
                    position,
                    len(normalized_candidate),
                ):
                    found_positions.append(position)
                start = position + len(normalized_candidate)
        return min(found_positions) if found_positions else None

    def _is_stock_attribution_context(
        self,
        normalized_text: str,
        position: int,
        length: int,
    ) -> bool:
        context = normalized_text[position : position + length + 24]
        return any(term in context for term in self._STOCK_ATTRIBUTION_CONTEXT_TERMS)

    def _more_specific_same_position_match(
        self,
        request_match: tuple[int, StockCandidate | StockUniverseEntry],
        internal_matches: list[tuple[int, StockCandidate | StockUniverseEntry]],
    ) -> StockCandidate | StockUniverseEntry | None:
        if not self._is_ambiguous_short_request_stock(request_match[1]):
            return None
        for internal_match in internal_matches:
            if self._is_shadowing_stock_match(request_match, internal_match):
                return internal_match[1]
        return None

    def _drop_shadowed_short_stock_matches(
        self,
        matches: list[tuple[int, StockCandidate | StockUniverseEntry]],
    ) -> list[tuple[int, StockCandidate | StockUniverseEntry]]:
        filtered: list[tuple[int, StockCandidate | StockUniverseEntry]] = []
        for candidate in matches:
            if any(
                self._is_shadowing_stock_match(candidate, other)
                for other in matches
                if other is not candidate
            ):
                continue
            filtered.append(candidate)
        return filtered

    def _is_shadowing_stock_match(
        self,
        short_match: tuple[int, StockCandidate | StockUniverseEntry],
        long_match: tuple[int, StockCandidate | StockUniverseEntry],
    ) -> bool:
        short_position, short_stock = short_match
        long_position, long_stock = long_match
        if short_stock.stock_code == long_stock.stock_code:
            return False
        if self._stock_match_specificity(long_stock) <= self._stock_match_specificity(
            short_stock
        ):
            return False
        if short_position != long_position and not self._is_ambiguous_short_request_stock(
            short_stock
        ):
            return False
        return self._stock_terms_contain(long_stock, short_stock)

    def _stock_match_specificity(
        self,
        stock: StockCandidate | StockUniverseEntry,
    ) -> int:
        terms = [stock.stock_name, stock.stock_name_en, *stock.aliases]
        return max((len(normalize_stock_term(term)) for term in terms if term), default=0)

    def _stock_terms_contain(
        self,
        long_stock: StockCandidate | StockUniverseEntry,
        short_stock: StockCandidate | StockUniverseEntry,
    ) -> bool:
        long_terms = self._normalized_non_code_stock_terms(long_stock)
        short_terms = self._normalized_non_code_stock_terms(short_stock)
        return any(
            short_term and short_term in long_term
            for short_term in short_terms
            for long_term in long_terms
        )

    def _normalized_non_code_stock_terms(
        self,
        stock: StockCandidate | StockUniverseEntry,
    ) -> tuple[str, ...]:
        return tuple(
            normalized
            for term in (stock.stock_name, stock.stock_name_en, *stock.aliases)
            if (normalized := normalize_stock_term(term))
        )

    def _is_excluded_stock(self, stock: StockCandidate | StockUniverseEntry) -> bool:
        return stock.stock_name in self._INTERNAL_STOCK_MATCH_EXCLUDED_NAMES

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
        if value.isascii() and value.isalpha() and len(value) < 4:
            return False
        return len(value) >= 3

    def _event_confidence(
        self,
        event_tags: list[str],
        event_probabilities: dict[str, float],
    ) -> float:
        if not event_tags:
            return 0.0
        return max(event_probabilities.get(tag, 0.0) for tag in event_tags)

    def _cap_summary_only_confidences(
        self,
        has_full_content: bool,
        event_confidence: float,
        sentiment_confidence: float,
        importance_confidence: float,
    ) -> tuple[float, float, float]:
        if has_full_content:
            return event_confidence, sentiment_confidence, importance_confidence
        cap = self._SUMMARY_ONLY_CONFIDENCE_CAP
        return (
            min(event_confidence, cap),
            min(sentiment_confidence, cap),
            min(importance_confidence, cap),
        )

    def _augment_event_tags(
        self,
        text: str,
        source_type: str,
        event_tags: list[str],
    ) -> list[str]:
        tag_set = set(event_tags)
        if source_type == "NEWS":
            tag_set.discard("DISCLOSURE")
            if "EARNINGS" in tag_set and "실적 없는" in text:
                tag_set.remove("EARNINGS")
            if self._has_macro_context(text):
                tag_set.add("MACRO")
            if any(term in text for term in self._GENERAL_MARKET_CONTEXT_TERMS):
                tag_set.add("GENERAL_MARKET")
        if any(term in text for term in self._RISK_CONTEXT_TERMS):
            tag_set.add("RISK")
        if any(term in text for term in self._CORPORATE_ACTION_CONTEXT_TERMS):
            tag_set.add("CORPORATE_ACTION")
        if any(term in text for term in self._EARNINGS_CONTEXT_TERMS):
            tag_set.add("EARNINGS")
        return sorted(tag_set)

    def _augment_sentiment(self, text: str, sentiment: Sentiment) -> Sentiment:
        negative_score = sum(
            1 for term in self._NEGATIVE_SENTIMENT_CONTEXT_TERMS if term in text
        )
        positive_score = sum(
            1 for term in self._POSITIVE_SENTIMENT_CONTEXT_TERMS if term in text
        )
        has_severe_negative = any(
            term in text for term in self._SEVERE_NEGATIVE_SENTIMENT_CONTEXT_TERMS
        )
        if negative_score > positive_score and (has_severe_negative or negative_score >= 2):
            return "NEGATIVE"
        has_neutral_context = any(
            term in text for term in self._NEUTRAL_SENTIMENT_CONTEXT_TERMS
        )
        if sentiment == "POSITIVE" and has_neutral_context and not has_severe_negative:
            return "NEUTRAL"
        if positive_score > negative_score and sentiment != "NEGATIVE":
            return "POSITIVE"
        return sentiment

    def _augment_importance(
        self,
        text: str,
        source_type: str,
        importance: Importance,
    ) -> Importance:
        rule_importance = self._rule_importance_floor(text, source_type)
        priority = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        elevated = (
            rule_importance
            if priority[rule_importance] > priority[importance]
            else importance
        )
        return self._cap_importance(text, elevated)

    def _rule_importance_floor(self, text: str, source_type: str) -> Importance:
        if self.rule_engine._contains_any(text, self.rule_engine.critical_keywords):
            return "CRITICAL"
        high_signal_terms = (
            "공급계약",
            "거래정지",
            "분할",
            "상장폐지",
            "생산차질",
            "유상증자",
            "자사주",
            "주식교환",
            "합병",
            "횡령",
            "배임",
        )
        if any(term in text for term in high_signal_terms):
            return "HIGH"
        if len(text) > 80:
            return "MEDIUM"
        return "LOW"

    def _cap_importance(self, text: str, importance: Importance) -> Importance:
        if importance != "CRITICAL":
            return importance
        if "소송" not in text:
            return importance
        critical_terms = ("감사의견 거절", "거래정지", "상장폐지", "일정금액", "횡령", "배임")
        if any(term in text for term in critical_terms):
            return importance
        return "HIGH"

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
    return tuple(
        stock
        for stock in load_stock_universe(stock_universe_path)
        if stock.stock_name not in AlertAnalyzer._INTERNAL_STOCK_MATCH_EXCLUDED_NAMES
    )


def _body_source_type(source_type: str, content: str) -> BodySourceType:
    if not content:
        return "PROVIDER_SNIPPET"
    if source_type == "DISCLOSURE":
        return "DISCLOSURE_BODY"
    return "FULL_TEXT"
