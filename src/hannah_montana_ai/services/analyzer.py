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
    TranslationStatus,
)
from hannah_montana_ai.services.disclosure_importance_model import DisclosureImportanceModel
from hannah_montana_ai.services.korean_financial_terms import (
    load_financial_term_entries,
)
from hannah_montana_ai.services.korean_translation_generator import (
    STATUS_SOURCE_LANGUAGE_FALLBACK,
    STATUS_TRANSLATED,
    KoreanTranslationContext,
    KoreanTranslationGenerator,
    KoreanTranslationResult,
)
from hannah_montana_ai.services.market_impact_model import (
    KFnspidMarketImpactModel,
    blend_importance,
)
from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.news_summary_generator import (
    NewsSummaryContext,
    NewsSummaryGenerator,
)
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine
from hannah_montana_ai.services.sentiment_policy import apply_financial_sentiment_policy
from hannah_montana_ai.services.sentiment_stacker import load_sentiment_stacker
from hannah_montana_ai.services.stock_linker import MachineLearningStockLinker
from hannah_montana_ai.services.transformer_impact_model import (
    load_kf_deberta_impact_model,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    load_kf_deberta_sentiment_model,
)
from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    load_stock_universe,
    normalize_stock_term,
)


def _contains_glossary_surface(text: str, surface: str) -> bool:
    candidate = surface.strip()
    if not candidate:
        return False
    if re.search(r"[A-Za-z0-9]", candidate):
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(candidate)}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        return bool(pattern.search(text))
    return candidate in text


@dataclass(frozen=True)
class StockMatchResult:
    stock: StockCandidate | StockUniverseEntry | None
    confidence: float


class AlertAnalyzer:
    _SUMMARY_ONLY_CONFIDENCE_CAP = 0.34
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
    _MARKET_WIDE_TITLE_PREFIXES = (
        "한국 증시",
        "국내 증시",
        "한국 주식시장",
        "국내 주식시장",
        "코스피",
        "코스닥",
        "증시",
    )
    _MARKET_WIDE_TITLE_TERMS = (
        "시총 세계",
        "시장 시가총액",
        "증시 시총",
        "지수 상승",
        "지수 하락",
        "외국인 순매수",
        "외국인 순매도",
    )
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
    _DISCLOSURE_EVENT_CODEBOOK = (
        (
            "RISK",
            (
                "상장폐지",
                "횡령",
                "배임",
                "감사의견거절",
                "부도",
                "회생절차",
                "파산",
                "소송등의제기",
                "소송등의판결",
                "거래정지",
                "불성실공시",
            ),
        ),
        (
            "CONTRACT",
            ("단일판매ㆍ공급계약", "단일판매·공급계약", "공급계약체결", "공급계약"),
        ),
        (
            "CAPITAL_ACTION",
            (
                "자기주식취득",
                "현금ㆍ현물배당",
                "현금·현물배당",
                "유상증자",
                "무상증자",
                "감자결정",
                "전환사채",
                "신주인수권부사채",
                "자기주식처분",
            ),
        ),
        (
            "CORPORATE_ACTION",
            (
                "회사합병",
                "회사분할",
                "합병",
                "분할",
                "영업양수",
                "영업양도",
                "타법인주식",
                "최대주주 변경을 수반",
            ),
        ),
        (
            "EARNINGS",
            ("영업실적", "실적", "매출액또는손익구조", "매출액 또는 손익구조"),
        ),
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
    _SHORT_STOCK_MEDIA_CONTEXT_TERMS = (
        "biz",
        "medianet",
        "sbsi",
        "뉴스",
        "스포츠",
        "기자",
        "앵커",
        "에따르면",
        "보도",
        "방송보도",
        "드라마",
        "금토드라마",
        "금토극",
        "그것이알고싶다",
        "사옥",
        "제작발표회",
        "sidebyside",
        "사이드바이사이드",
    )
    _INTERNAL_STOCK_MATCH_EXCLUDED_NAMES = frozenset(
        {
            "국민은행",
            "신한은행",
            "우리은행",
            "하나은행",
        }
    )
    _NON_FINANCIAL_MEDIA_TERMS = (
        "골프",
        "포토",
        "라운드",
        "홀 경기",
        "선수",
        "드라마",
        "영화",
        "예능",
        "콘서트",
        "시구",
        "화보",
        "수면",
        "갤럭시 워치",
        "갤럭시워치",
        "건강",
        "의대",
        "심리학",
        "착용",
        "성인",
    )
    _FINANCIAL_RELEVANCE_TERMS = (
        "주가",
        "주식",
        "증시",
        "코스피",
        "코스닥",
        "투자",
        "실적",
        "영업이익",
        "순이익",
        "매출",
        "공시",
        "수주",
        "계약",
        "공급",
        "인수",
        "합병",
        "분할",
        "배당",
        "자사주",
        "대출",
        "금리",
        "환율",
        "리밸런싱",
        "순매수",
        "순매도",
        "목표주가",
        "상장",
        "거래정지",
        "자금",
        "증권",
        "턴어라운드",
    )

    def __init__(
        self,
        summary_generator: NewsSummaryGenerator | None = None,
        translation_generator: KoreanTranslationGenerator | None = None,
    ) -> None:
        settings = get_settings()
        self.rule_engine = FinancialRuleEngine()
        self.model = MachineLearningFinancialNlpModel(settings.model_path)
        self.market_impact_models = {
            "NEWS": KFnspidMarketImpactModel(
                settings.market_impact_news_model_path,
                settings.market_impact_news_training_report_path,
                "NEWS",
            ),
            "DISCLOSURE": KFnspidMarketImpactModel(
                settings.market_impact_disclosure_model_path,
                settings.market_impact_disclosure_training_report_path,
                "DISCLOSURE",
            ),
        }
        self.sentiment_transformer = load_kf_deberta_sentiment_model(
            settings.sentiment_transformer_path,
            settings.sentiment_transformer_training_report_path,
            settings.sentiment_transformer_benchmark_report_path,
            settings.transformer_base_model_path,
        )
        self.sentiment_stacker = load_sentiment_stacker(
            settings.sentiment_stacker_path,
            settings.sentiment_stacker_report_path,
            settings.sentiment_transformer_benchmark_report_path,
        )
        self.disclosure_importance_model = DisclosureImportanceModel(
            settings.disclosure_importance_model_path,
            settings.disclosure_importance_report_path,
        )
        self.market_impact_transformers = {
            "NEWS": load_kf_deberta_impact_model(
                settings.market_impact_news_transformer_path,
                settings.market_impact_news_transformer_report_path,
                settings.transformer_base_model_path,
                "NEWS",
            ),
            "DISCLOSURE": load_kf_deberta_impact_model(
                settings.market_impact_disclosure_transformer_path,
                settings.market_impact_disclosure_transformer_report_path,
                settings.transformer_base_model_path,
                "DISCLOSURE",
            ),
        }
        self.stock_linker = MachineLearningStockLinker(settings.stock_linker_model_path)
        self.summary_generator = summary_generator or NewsSummaryGenerator()
        self.translation_generator = (
            translation_generator or KoreanTranslationGenerator.from_settings(settings)
        )
        self._internal_stock_universe = _load_internal_stock_universe(settings.stock_universe_path)
        self._internal_stock_by_code = {
            stock.stock_code: stock for stock in self._internal_stock_universe
        }
        self._financial_glossary_entries = load_financial_term_entries(
            settings.korean_financial_terms_seed_path
        )

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        has_full_content = bool(request.content.strip())
        body_source_text = request.content if has_full_content else request.snippet
        analysis_content = self.rule_engine.clean_article_text(body_source_text, request.title)
        model_content = analysis_content if has_full_content else ""
        text = f"{request.title} {request.snippet} {model_content}".strip()
        primary_stock_match = self._match_primary_stock_from_request_or_internal(
            request.title,
            text,
            request.stock_universe,
        )
        if self._is_tangential_non_financial_stock_mention(text, request.stock_universe):
            primary_stock_match = StockMatchResult(None, 0.0)
        primary_stock = primary_stock_match.stock
        event_probabilities = self.model.event_tag_probabilities(text, request.source_type)
        event_tags = self._augment_event_tags(
            text,
            request.source_type,
            self.model.predict_event_tags(text, request.source_type),
        )
        sentiment_probabilities = self._sentiment_probabilities(text, request.source_type)
        sentiment = cast(Sentiment, self._top_label(sentiment_probabilities, fallback="NEUTRAL"))
        sentiment = self._augment_sentiment(text, sentiment)
        disclosure_importance = (
            self.disclosure_importance_model.predict(
                request.title,
                request.snippet,
                model_content,
            )
            if request.source_type == "DISCLOSURE"
            else None
        )
        if disclosure_importance is None:
            importance_probabilities = self.model.importance_probabilities(
                text, request.source_type
            )
            importance = cast(
                Importance,
                self._top_label(importance_probabilities, fallback="MEDIUM"),
            )
            importance = self._augment_importance(text, request.source_type, importance)
        else:
            importance_probabilities = disclosure_importance.probabilities
            importance = disclosure_importance.importance
        if self._rule_importance_floor(text, request.source_type) == "CRITICAL":
            importance = "CRITICAL"
            importance_probabilities = self._apply_probability_floor(
                importance_probabilities,
                "CRITICAL",
                0.90,
            )
        market_impact_text = self._market_impact_input(text, primary_stock)
        impact_transformer = self.market_impact_transformers[request.source_type]
        impact_baseline = self.market_impact_models[request.source_type]
        market_impact_prediction = (
            impact_transformer.predict(market_impact_text, request.source_type)
            if impact_transformer.enabled
            else impact_baseline.predict(market_impact_text, request.source_type)
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
        importance, importance_confidence = blend_importance(
            importance,
            importance_confidence,
            market_impact_prediction,
        )
        event_confidence, sentiment_confidence, importance_confidence = (
            self._cap_summary_only_confidences(
                has_full_content,
                event_confidence,
                sentiment_confidence,
                importance_confidence,
            )
        )
        fallback_summary_lines = self.rule_engine.summarize_what_why_impact(
            request.title,
            request.snippet,
            analysis_content,
            importance,
            sentiment,
        )
        request_stock_mismatch = self._is_request_stock_mismatch(
            primary_stock,
            request.stock_universe,
        )
        if request_stock_mismatch:
            # 폐기될 타 종목 기사는 생성형 요약과 번역 호출 전에 차단한다.
            summary_lines = fallback_summary_lines
        else:
            summary_lines = self.summary_generator.generate(
                NewsSummaryContext(
                    title=request.title,
                    snippet=request.snippet,
                    content=analysis_content,
                    source_type=request.source_type,
                    importance=importance,
                    sentiment=sentiment,
                    event_tags=event_tags,
                    stock_code=stock_code,
                    stock_name=stock_name,
                    stock_name_en=primary_stock.stock_name_en if primary_stock else "",
                    fallback=fallback_summary_lines,
                )
            )
        summary = "\n".join(
            line for line in (summary_lines.what, summary_lines.why, summary_lines.impact) if line
        )
        glossary_terms = self._with_primary_stock_glossary(
            self._extract_financial_glossary_terms(text),
            primary_stock,
            text,
        )
        duplicate_key = self._duplicate_key(request.source_type, request.title, stock_code)
        response_content = request.content.strip() if has_full_content else analysis_content
        if request_stock_mismatch:
            translations = self._request_stock_mismatch_translations()
        else:
            translations = self._translate_analysis_fields(
                request,
                glossary_terms,
                summary,
                response_content,
            )
        translated_title = translations["TITLE"]
        translated_summary = translations["SUMMARY"]
        translated_content = translations["CONTENT"]
        translation_quality_flags = self._analysis_translation_quality_flags(
            glossary_terms,
            translated_title,
            translated_summary,
            translated_content,
        )
        translation_provider = self._first_translation_provider(
            translated_content,
            translated_summary,
            translated_title,
        )
        translation_model_version = self._first_translation_model_version(
            translated_content,
            translated_summary,
            translated_title,
        )
        translation_status = self._analysis_translation_status(
            response_content,
            translated_content,
        )

        return AlertAnalysisResponse(
            stock_code=stock_code,
            stock_name=stock_name,
            source_type=request.source_type,
            original_title=request.title,
            translated_title=translated_title.translated_text,
            summary=summary,
            summary_lines=summary_lines,
            translated_summary=translated_summary.translated_text,
            content_availability="FULL_TEXT" if has_full_content else "SUMMARY_ONLY",
            original_content=response_content,
            translated_content=translated_content.translated_text,
            original_body=response_content,
            translated_body=translated_content.translated_text,
            body_source_type=_body_source_type(request.source_type, response_content),
            image_urls=request.image_urls,
            event_tags=event_tags,
            sentiment=sentiment,
            importance=importance,
            market_impact_importance=(
                market_impact_prediction.importance if market_impact_prediction else None
            ),
            market_impact_score=(
                market_impact_prediction.materiality_score if market_impact_prediction else None
            ),
            market_impact_confidence=(
                round(market_impact_prediction.confidence, 6) if market_impact_prediction else None
            ),
            related_stocks=related_stocks,
            holder_target=self.rule_engine.holder_target(importance),
            watchlist_target=self.rule_engine.watchlist_target(importance),
            glossary_terms=glossary_terms,
            translation_quality_flags=translation_quality_flags,
            translation_provider=translation_provider,
            translation_model_version=translation_model_version,
            translation_status=translation_status,
            duplicate_key=duplicate_key,
            cluster_key=self._cluster_key(request, stock_code, duplicate_key),
            model_version=self._analysis_model_version(request.source_type),
            event_confidence=round(event_confidence, 6),
            sentiment_confidence=round(sentiment_confidence, 6),
            importance_confidence=round(importance_confidence, 6),
            stock_match_confidence=round(primary_stock_match.confidence, 6),
        )

    def _analysis_model_version(self, source_type: str) -> str:
        versions = [self.model.version]
        if self.sentiment_transformer.enabled:
            versions.append(f"sentiment:{self.sentiment_transformer.version}")
        if self.sentiment_stacker.enabled:
            versions.append(f"sentiment-stack:{self.sentiment_stacker.version}")
        if self.disclosure_importance_model.enabled:
            versions.append(f"disclosure-importance:{self.disclosure_importance_model.version}")
        transformer = self.market_impact_transformers[source_type]
        baseline = self.market_impact_models[source_type]
        selected = transformer if transformer.enabled else baseline
        if selected.enabled:
            source_code = "n" if source_type == "NEWS" else "d"
            versions.append(f"impact-{source_code}:{selected.version}")
        return "|".join(versions)

    def _sentiment_probabilities(self, text: str, source_type: str = "NEWS") -> dict[str, float]:
        baseline = self.model.sentiment_probabilities(text)
        transformer = (
            self.sentiment_transformer.probabilities(text, source_type)
            if self.sentiment_transformer.enabled
            else None
        )
        if transformer is None:
            return baseline
        stacked = self.sentiment_stacker.probabilities(
            transformer=transformer,
            baseline=baseline,
            text=text,
            source_type=source_type,
        )
        if stacked is not None:
            return stacked
        # 실제 금융 문장의 Transformer 성능을 유지하면서 기존 회귀 분포를 보정한다.
        transformer_weight = self.sentiment_transformer.transformer_weight
        return {
            label: transformer_weight * transformer[label]
            + (1.0 - transformer_weight) * baseline[label]
            for label in transformer
        }

    def _translate_analysis_text(
        self,
        text: str,
        request: AlertAnalysisRequest,
        glossary_terms: list[FinancialGlossaryTerm],
        *,
        title: str,
    ) -> KoreanTranslationResult:
        if not text.strip():
            return KoreanTranslationResult(
                translated_text="",
                provider="",
                model_version=self.model.version,
                status=STATUS_SOURCE_LANGUAGE_FALLBACK,
                prompt_version="",
                quality_flags=[],
            )
        return self.translation_generator.translate(
            KoreanTranslationContext(
                text=text,
                source_type=request.source_type,
                title=title,
                glossary_terms=glossary_terms,
            )
        )

    def _is_request_stock_mismatch(
        self,
        primary_stock: StockCandidate | StockUniverseEntry | None,
        request_universe: list[StockCandidate],
    ) -> bool:
        if primary_stock is None or not request_universe:
            return False
        return all(stock.stock_code != primary_stock.stock_code for stock in request_universe)

    def _request_stock_mismatch_translations(self) -> dict[str, KoreanTranslationResult]:
        values = {
            "TITLE": "Article about a different listed company",
            "SUMMARY": (
                "The article primarily concerns a different listed company. "
                "The requested stock is not the leading issuer. "
                "The item is excluded from the requested stock feed."
            ),
            "CONTENT": "The article is outside the requested stock candidate scope.",
        }
        return {
            field: KoreanTranslationResult(
                translated_text=value,
                provider="request-stock-mismatch-gate",
                model_version=self.model.version,
                status=STATUS_TRANSLATED,
                prompt_version="",
                quality_flags=[],
            )
            for field, value in values.items()
        }

    def _translate_analysis_fields(
        self,
        request: AlertAnalysisRequest,
        glossary_terms: list[FinancialGlossaryTerm],
        summary: str,
        response_content: str,
    ) -> dict[str, KoreanTranslationResult]:
        source_fields = {
            "TITLE": request.title,
            "SUMMARY": summary,
            "CONTENT": response_content,
        }
        contexts = {
            field: KoreanTranslationContext(
                text=text,
                source_type=request.source_type,
                title=request.title,
                glossary_terms=glossary_terms,
            )
            for field, text in source_fields.items()
        }
        # 구조화 번역이 실패하면 기존 필드별 경로로 복구해 본문 누락을 막는다.
        batched = self.translation_generator.translate_alert_fields(contexts)
        if batched is not None:
            return batched
        return {
            field: self._translate_analysis_text(
                text,
                request,
                glossary_terms,
                title=request.title,
            )
            for field, text in source_fields.items()
        }

    def _analysis_translation_quality_flags(
        self,
        glossary_terms: list[FinancialGlossaryTerm],
        *translations: KoreanTranslationResult,
    ) -> list[str]:
        flags = (
            ["FINANCIAL_GLOSSARY_APPLIED"]
            if any(term.category != "company" for term in glossary_terms)
            else []
        )
        for translation in translations:
            flags.extend(translation.quality_flags)
        return sorted(set(flags))[:20]

    def _first_translation_provider(
        self,
        *translations: KoreanTranslationResult,
    ) -> str:
        for translation in translations:
            if translation.provider:
                return translation.provider
        return ""

    def _first_translation_model_version(
        self,
        *translations: KoreanTranslationResult,
    ) -> str:
        for translation in translations:
            if translation.model_version:
                return translation.model_version
        return self.model.version

    def _analysis_translation_status(
        self,
        response_content: str,
        translated_content: KoreanTranslationResult,
    ) -> TranslationStatus:
        if not response_content.strip():
            return "TRANSLATED"
        return translated_content.status

    def _extract_financial_glossary_terms(self, text: str) -> list[FinancialGlossaryTerm]:
        matched_terms: list[FinancialGlossaryTerm] = []
        seen_terms: set[str] = set()
        for entry in sorted(
            self._financial_glossary_entries,
            key=lambda item: max(len(term) for term in (item.normalized_term, *item.aliases)),
            reverse=True,
        ):
            normalized_term = entry.normalized_term
            source_term = next(
                (
                    term
                    for term in (normalized_term, *entry.aliases)
                    if _contains_glossary_surface(text, term)
                ),
                "",
            )
            if not source_term or normalized_term in seen_terms:
                continue
            matched_terms.append(
                FinancialGlossaryTerm(
                    source_term=source_term,
                    normalized_term=normalized_term,
                    english_term=entry.english_term,
                    category=entry.category,
                    description=entry.definition,
                )
            )
            seen_terms.add(normalized_term)
        return matched_terms

    def _with_primary_stock_glossary(
        self,
        glossary_terms: list[FinancialGlossaryTerm],
        primary_stock: StockCandidate | StockUniverseEntry | None,
        text: str,
    ) -> list[FinancialGlossaryTerm]:
        if (
            primary_stock is None
            or not primary_stock.stock_name_en.strip()
            or primary_stock.stock_name not in text
        ):
            return glossary_terms
        if any(term.normalized_term == primary_stock.stock_name for term in glossary_terms):
            return glossary_terms
        return [
            FinancialGlossaryTerm(
                source_term=primary_stock.stock_name,
                normalized_term=primary_stock.stock_name,
                english_term=primary_stock.stock_name_en,
                category="company",
                description="Verified English name for the matched listed company.",
            ),
            *glossary_terms,
        ]

    def _is_tangential_non_financial_stock_mention(
        self,
        text: str,
        request_universe: Sequence[StockCandidate],
    ) -> bool:
        if not request_universe:
            return False
        normalized = re.sub(r"\s+", " ", text)
        if not any(term in normalized for term in self._NON_FINANCIAL_MEDIA_TERMS):
            return False
        return not any(term in normalized for term in self._FINANCIAL_RELEVANCE_TERMS)

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
        if not request_universe and self._is_market_wide_title(title):
            return StockMatchResult(None, 0.0)
        exact_match = self._best_primary_stock_match(
            text,
            request_universe,
            prefer_request=True,
        )
        if exact_match is not None:
            confidence = 1.0 if exact_match in request_universe else 0.96
            return StockMatchResult(exact_match, confidence)
        if self._is_market_wide_title(title) and exact_match not in request_universe:
            return StockMatchResult(None, 0.0)
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
            if self._is_preferred_share_request(request_matches[0][1]):
                return request_matches[0][1]
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

    def _is_preferred_share_request(
        self,
        stock: StockCandidate | StockUniverseEntry,
    ) -> bool:
        normalized_name = normalize_stock_term(stock.stock_name)
        return re.search(r"[1-9]?우[bc]?$", normalized_name) is not None

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
            if not allow_short_terms and not self._is_usable_stock_match_term(normalized_candidate):
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
                    normalized_candidate,
                ):
                    found_positions.append(position)
                start = position + len(normalized_candidate)
        return min(found_positions) if found_positions else None

    def _is_stock_attribution_context(
        self,
        normalized_text: str,
        position: int,
        length: int,
        normalized_candidate: str,
    ) -> bool:
        # 회사명 자체의 '리서치'를 증권사 인용 문맥으로 오인하지 않는다.
        context = (
            normalized_text[max(0, position - 24) : position]
            + normalized_text[position + length : position + length + 24]
        )
        if any(term in context for term in self._STOCK_ATTRIBUTION_CONTEXT_TERMS):
            return True
        return (
            normalized_candidate.isascii()
            and len(normalized_candidate) <= 3
            and any(term in context for term in self._SHORT_STOCK_MEDIA_CONTEXT_TERMS)
        )

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
        if self._stock_match_specificity(long_stock) <= self._stock_match_specificity(short_stock):
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

    def _is_market_wide_title(self, title: str) -> bool:
        normalized = re.sub(r"\s+", " ", title).strip()
        if not normalized:
            return False
        return normalized.startswith(self._MARKET_WIDE_TITLE_PREFIXES) or any(
            term in normalized for term in self._MARKET_WIDE_TITLE_TERMS
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
        if source_type == "DISCLOSURE":
            # 구조화된 DART 제목은 v3 코드북으로 제한해 출처 외 이벤트 오탐을 막는다.
            tag_set = {"DISCLOSURE"}
            for label, patterns in self._DISCLOSURE_EVENT_CODEBOOK:
                if any(pattern in text for pattern in patterns):
                    tag_set.add(label)
                    break
            return sorted(tag_set)

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
        # 검증된 Transformer 판단은 키워드 규칙으로 덮어쓰지 않는다.
        if self.sentiment_transformer.enabled:
            return sentiment
        return apply_financial_sentiment_policy(text, sentiment)

    def _has_mixed_market_sentiment(self, text: str) -> bool:
        if not ("코스피" in text and "코스닥" in text):
            return False
        has_positive_axis = any(
            term in text for term in ("회복", "반등", "상승 전환", "순매수", "유입")
        )
        has_negative_axis = any(
            term in text for term in ("하락", "약세", "순매도", "내렸다", "밀렸다")
        )
        return has_positive_axis and has_negative_axis and "반면" in text

    def _augment_importance(
        self,
        text: str,
        source_type: str,
        importance: Importance,
    ) -> Importance:
        rule_importance = self._rule_importance_floor(text, source_type)
        priority = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        elevated = (
            rule_importance if priority[rule_importance] > priority[importance] else importance
        )
        return self._cap_importance(text, elevated)

    def _rule_importance_floor(self, text: str, source_type: str) -> Importance:
        if self.rule_engine._contains_any(text, self.rule_engine.critical_keywords):
            return "CRITICAL"
        if source_type == "DISCLOSURE" and any(
            term in text
            for term in (
                "사업보고서",
                "분기보고서",
                "반기보고서",
                "감사보고서제출",
                "주주총회소집공고",
                "주주총회소집결의",
                "기업설명회개최",
                "임원ㆍ주요주주특정증권",
                "임원·주요주주특정증권",
                "주식등의대량보유상황보고서",
            )
        ):
            return "LOW"
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
            "영업양수",
            "영업양도",
            "전환사채",
            "신주인수권부사채",
            "현금ㆍ현물배당",
            "현금·현물배당",
            "매출액또는손익구조",
            "영업실적",
            "횡령",
            "배임",
        )
        if any(term in text for term in high_signal_terms):
            return "HIGH"
        if source_type == "DISCLOSURE" and any(
            term in text
            for term in (
                "최대주주등소유주식변동",
                "대표이사변경",
                "조회공시",
                "주주총회결과",
            )
        ):
            return "MEDIUM"
        if len(text) > 80:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _apply_probability_floor(
        probabilities: dict[str, float],
        label: str,
        floor: float,
    ) -> dict[str, float]:
        current = float(probabilities.get(label, 0.0))
        if current >= floor:
            return probabilities
        other_total = sum(float(value) for name, value in probabilities.items() if name != label)
        if other_total <= 0.0:
            return {name: float(name == label) for name in probabilities}
        remaining = 1.0 - floor
        return {
            name: floor if name == label else remaining * float(value) / other_total
            for name, value in probabilities.items()
        }

    @staticmethod
    def _market_impact_input(
        text: str,
        primary_stock: StockCandidate | StockUniverseEntry | None,
    ) -> str:
        if primary_stock is None:
            return text
        return f"{text} {primary_stock.stock_name}".strip()

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
