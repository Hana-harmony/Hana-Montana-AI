from __future__ import annotations

import html
from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    DocumentRiskLevel,
    DocumentVerificationStatus,
    FinancialGlossaryTerm,
    ForeignLimitUsageStatus,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
    OrderAvailabilityIndicator,
    PriceLimitStatus,
    StockOrderStatusRequest,
    StockOrderStatusResponse,
    TaxCaseType,
    TaxDocumentVerificationRequest,
    TaxDocumentVerificationResponse,
    TaxRefundStatusRequest,
    TaxRefundStatusResponse,
    TaxRefundWorkflowStatus,
)
from hannah_montana_ai.services.analyzer import AlertAnalyzer

FOREIGN_LIMIT_WARNING_BUFFER_PERCENT = 1.0
DIVIDEND_DOMESTIC_WITHHOLDING_RATE = 0.22
DIVIDEND_TREATY_LIMIT_RATE = 0.15
CAPITAL_GAINS_SELL_PROCEEDS_RATE = 0.11
CAPITAL_GAINS_PROFIT_RATE = 0.22
CASE_01_MAX_OWNERSHIP_RATE = 25.0
FOREIGN_OWNERSHIP_MODEL_VERSION = "foreign-ownership-boundary-v1"
TRADING_STATE_MODEL_VERSION = "krx-vi-price-limit-state-v1"
TRANSLATION_MODEL_VERSION = "local-financial-glossary-v2"
TAX_REFUND_MODEL_VERSION = "hk-treaty-refund-case-engine-v1"
DOCUMENT_VERIFICATION_MODEL_VERSION = "ocr-fraud-risk-gate-v1"
LOCAL_TAX_REFUND_SHARE = 0.10

FINANCIAL_TRANSLATION_GLOSSARY = (
    ("삼성전자", "Samsung Electronics", "stock", ("삼전", "Samsung Elec")),
    ("SK하이닉스", "SK hynix", "stock", ("하이닉스",)),
    ("한화시스템", "Hanwha Systems", "stock", ()),
    ("코웨이", "Coway", "stock", ()),
    ("젠큐릭스", "Gencurix", "stock", ()),
    ("감사의견 거절", "adverse audit opinion", "disclosure", ()),
    ("상장폐지", "delisting", "disclosure", ()),
    ("거래정지", "trading halt", "market_state", ()),
    ("공급계약", "supply contract", "event", ("단일판매ㆍ공급계약체결",)),
    ("유상증자", "paid-in capital increase", "event", ()),
    ("한국 증시", "Korean stock market", "market_state", ("증시",)),
    ("코스피", "KOSPI", "index", ()),
    ("환율", "exchange rate", "fx", ()),
    ("외환 지표", "foreign exchange indicator", "fx", ()),
    ("과세 개편", "tax reform", "tax", ()),
    ("빚투", "leveraged retail investing", "risk", ()),
    ("목표치", "target estimate", "market_state", ()),
    ("상향", "upward revision", "sentiment", ()),
    (
        "타법인주식및출자증권취득결정",
        "decision to acquire shares and equity securities of another corporation",
        "disclosure",
        ("타법인 주식 및 출자증권 취득 결정",),
    ),
    (
        "소송등의제기ㆍ신청",
        "filing or application of lawsuit",
        "disclosure",
        ("소송등의제기", "소송 등의 제기", "소송 등의 제기ㆍ신청"),
    ),
    (
        "소송등의판결ㆍ결정",
        "court ruling or decision on lawsuit",
        "disclosure",
        ("소송등의판결", "소송 등의 판결ㆍ결정"),
    ),
    (
        "임시주주총회결과",
        "extraordinary shareholders meeting result",
        "disclosure",
        ("임시 주주총회 결과",),
    ),
    (
        "일정금액이상의청구",
        "claim above a material amount",
        "disclosure",
        ("일정 금액 이상의 청구",),
    ),
    (
        "주권매매거래정지기간변경",
        "share trading halt period change",
        "market_state",
        ("주권 매매거래 정지기간 변경",),
    ),
    (
        "상장폐지사유발생",
        "delisting cause occurred",
        "disclosure",
        ("상장폐지 사유 발생",),
    ),
    (
        "불성실공시법인지정",
        "designation as an unfaithful disclosure corporation",
        "disclosure",
        ("불성실 공시법인 지정",),
    ),
    ("투자주의환기종목", "investment caution issue", "market_state", ("투자주의 환기종목",)),
    ("관리종목", "administrative issue", "market_state", ()),
    (
        "자기주식취득",
        "treasury share acquisition",
        "capital_action",
        ("자기주식 취득", "자사주 취득"),
    ),
    ("자사주 소각", "treasury share cancellation", "capital_action", ("자기주식 소각",)),
    ("전환사채", "convertible bond", "capital_action", ("CB",)),
    ("신주인수권부사채", "bond with warrants", "capital_action", ("BW",)),
    ("영업이익", "operating profit", "metric", ()),
    ("영업손실", "operating loss", "metric", ()),
    ("매출액", "revenue", "metric", ()),
    ("당기순이익", "net income", "metric", ()),
    ("흑자전환", "turnaround to profit", "sentiment", ()),
    ("적자전환", "turnaround to loss", "sentiment", ()),
    ("어닝쇼크", "earnings shock", "event", ()),
    ("어닝서프라이즈", "earnings surprise", "event", ()),
    ("외국인 보유율", "foreign ownership ratio", "metric", ("외국인지분율",)),
    ("한도소진율", "foreign ownership limit usage ratio", "metric", ()),
    ("실적", "earnings", "event", ()),
    ("수주", "order win", "event", ()),
    ("배당", "dividend", "event", ()),
    ("공시", "disclosure", "source", ()),
    ("뉴스", "news", "source", ()),
    ("증가", "increase", "sentiment", ()),
    ("감소", "decrease", "sentiment", ()),
    ("주가", "stock price", "market_state", ()),
    ("외국인", "foreign investor", "investor_type", ()),
    ("환급", "refund", "tax", ()),
)


@dataclass(frozen=True)
class ForeignOwnershipPrediction:
    foreign_limit_quantity: int
    foreign_limit_remaining_quantity: int
    ownership_rate: float
    limit_exhaustion_rate: float
    predicted_rate_min: float
    predicted_rate_max: float
    usage_status: ForeignLimitUsageStatus
    limit_warning: bool
    model_version: str


@dataclass(frozen=True)
class TradingStatePrediction:
    vi_activation_status: Literal["Y", "N"]
    vi_reasons: list[str]
    price_limit_status: PriceLimitStatus
    immediate_execution_available: bool
    guidance_message: str
    model_version: str


@dataclass(frozen=True)
class OrderAvailabilityPrediction:
    buy_order_available: bool
    sell_order_available: bool
    indicator: OrderAvailabilityIndicator
    restriction_reasons: list[str]


@dataclass(frozen=True)
class TranslationPrediction:
    translated_title: str
    translated_summary: str
    translation_status: Literal["TRANSLATED", "SOURCE_LANGUAGE_FALLBACK"]
    glossary_terms: list[FinancialGlossaryTerm]
    quality_flags: list[str]
    provider: str
    model_version: str


@dataclass(frozen=True)
class TaxRefundPrediction:
    tax_case_type: TaxCaseType
    document_status: Literal["VERIFIED", "PENDING"]
    workflow_status: TaxRefundWorkflowStatus
    government_verification_ref: str
    required_documents_completed: bool
    total_withheld_tax: int
    dividend_refund_amount: int
    capital_gains_refund_amount: int
    eligible_refund_amount: int
    national_tax_refund_amount: int
    local_tax_refund_amount: int
    instant_payout_fee_amount: int
    instant_payout_amount: int
    compliance_sandbox_flag: Literal["Y", "N"]
    clawback_required_if_rejected: bool
    required_next_actions: list[str]
    risk_disclosure_message: str
    review_message: str
    tax_model_version: str
    document_model_version: str


@dataclass(frozen=True)
class TaxDocumentVerificationPrediction:
    verification_status: DocumentVerificationStatus
    fraud_risk_score: float
    risk_level: DocumentRiskLevel
    manual_review_required: bool
    extracted_fields: dict[str, str]
    missing_required_fields: list[str]
    rejection_reasons: list[str]
    document_model_version: str


class ForeignOwnershipBoundaryModel:
    version = FOREIGN_OWNERSHIP_MODEL_VERSION

    def predict(self, request: StockOrderStatusRequest) -> ForeignOwnershipPrediction:
        foreign_limit_quantity = request.foreign_limit_quantity or round(
            request.issued_shares * request.foreign_limit_rate / 100
        )
        ownership_rate = _rate(
            request.foreign_owned_quantity,
            request.issued_shares,
        )
        limit_exhaustion_rate = _rate(
            request.foreign_owned_quantity,
            foreign_limit_quantity,
        )
        predicted_center = _rate(
            request.foreign_owned_quantity + request.intraday_foreign_net_buy_quantity,
            request.issued_shares,
        )
        predicted_min = max(
            0.0,
            predicted_center - request.prediction_confidence_interval_percent,
        )
        predicted_max = min(
            request.foreign_limit_rate,
            predicted_center + request.prediction_confidence_interval_percent,
        )
        limit_remaining_quantity = max(0, foreign_limit_quantity - request.foreign_owned_quantity)
        usage_status = _foreign_limit_usage_status(predicted_max, request.foreign_limit_rate)
        return ForeignOwnershipPrediction(
            foreign_limit_quantity=foreign_limit_quantity,
            foreign_limit_remaining_quantity=limit_remaining_quantity,
            ownership_rate=round(ownership_rate, 4),
            limit_exhaustion_rate=round(limit_exhaustion_rate, 4),
            predicted_rate_min=round(predicted_min, 4),
            predicted_rate_max=round(predicted_max, 4),
            usage_status=usage_status,
            limit_warning=usage_status != "NORMAL",
            model_version=self.version,
        )


class TradingStateModel:
    version = TRADING_STATE_MODEL_VERSION

    def predict(self, request: StockOrderStatusRequest) -> TradingStatePrediction:
        vi_reasons = _vi_reasons(request)
        price_limit_status = _price_limit_status(request)
        immediate_execution_available = (
            not vi_reasons
            and price_limit_status == "NORMAL"
            and request.trading_session_status == "REGULAR"
        )
        return TradingStatePrediction(
            vi_activation_status="Y" if vi_reasons else "N",
            vi_reasons=vi_reasons,
            price_limit_status=price_limit_status,
            immediate_execution_available=immediate_execution_available,
            guidance_message=_order_guidance_message(
                vi_reasons,
                price_limit_status,
                immediate_execution_available,
            ),
            model_version=self.version,
        )


class FinancialTranslationModel:
    version = TRANSLATION_MODEL_VERSION
    provider = "local-financial-glossary"

    def translate_event(
        self,
        request: IntelligenceEventRequest,
        summary: str,
    ) -> TranslationPrediction:
        title_translation = translate_financial_korean_to_english(request.title)
        summary_translation = translate_financial_korean_to_english(summary)
        glossary_terms = _merge_glossary_terms(
            title_translation.glossary_terms,
            summary_translation.glossary_terms,
        )
        quality_flags = _translation_quality_flags(
            request.title,
            title_translation.translated_text,
            summary,
            summary_translation.translated_text,
            glossary_terms,
        )
        translation_status: Literal["TRANSLATED", "SOURCE_LANGUAGE_FALLBACK"] = (
            "TRANSLATED"
            if title_translation.translated_text != html.unescape(request.title)
            or summary_translation.translated_text != html.unescape(summary)
            else "SOURCE_LANGUAGE_FALLBACK"
        )
        return TranslationPrediction(
            translated_title=title_translation.translated_text,
            translated_summary=summary_translation.translated_text,
            translation_status=translation_status,
            glossary_terms=glossary_terms,
            quality_flags=quality_flags,
            provider=self.provider,
            model_version=self.version,
        )


class TaxDocumentVerificationModel:
    version = DOCUMENT_VERIFICATION_MODEL_VERSION

    def predict(self, request: TaxDocumentVerificationRequest) -> TaxDocumentVerificationPrediction:
        extracted_fields = _normalize_document_fields(request)
        missing_required_fields = _missing_required_document_fields(request, extracted_fields)
        rejection_reasons = _document_rejection_reasons(
            request,
            missing_required_fields,
        )
        risk_level = _document_risk_level(request.ocr_confidence, request.fraud_signal_score)
        verification_status = _document_verification_status(
            request,
            missing_required_fields,
            rejection_reasons,
        )
        return TaxDocumentVerificationPrediction(
            verification_status=verification_status,
            fraud_risk_score=round(request.fraud_signal_score, 4),
            risk_level=risk_level,
            manual_review_required=verification_status != "VERIFIED",
            extracted_fields=extracted_fields,
            missing_required_fields=missing_required_fields,
            rejection_reasons=rejection_reasons,
            document_model_version=self.version,
        )


class TaxRefundAdvanceModel:
    version = TAX_REFUND_MODEL_VERSION
    document_model_version = DOCUMENT_VERIFICATION_MODEL_VERSION

    def predict(self, request: TaxRefundStatusRequest) -> TaxRefundPrediction:
        required_documents_completed = _required_documents_completed(request)
        document_status: Literal["VERIFIED", "PENDING"] = (
            "VERIFIED" if required_documents_completed else "PENDING"
        )
        tax_case_type = _tax_case_type(request)
        total_withheld_tax = sum(transaction.withheld_tax for transaction in request.transactions)
        eligible_for_refund = required_documents_completed and tax_case_type == "CASE_01"
        dividend_refund_amount = (
            _dividend_refund_amount(request) if eligible_for_refund else 0
        )
        capital_gains_refund_amount = (
            _capital_gains_refund_amount(request) if eligible_for_refund else 0
        )
        eligible_refund_amount = min(
            total_withheld_tax,
            dividend_refund_amount + capital_gains_refund_amount,
        )
        local_tax_refund_amount = round(eligible_refund_amount * LOCAL_TAX_REFUND_SHARE)
        national_tax_refund_amount = max(0, eligible_refund_amount - local_tax_refund_amount)
        instant_payout_fee_amount = (
            round(eligible_refund_amount * request.instant_payout_fee_rate / 100)
            if request.instant_payout_requested
            else 0
        )
        instant_payout_amount = max(0, eligible_refund_amount - instant_payout_fee_amount)
        compliance_sandbox_flag: Literal["Y", "N"] = (
            "Y"
            if request.instant_payout_requested
            and eligible_refund_amount > 0
            and tax_case_type == "CASE_01"
            else "N"
        )
        workflow_status = _tax_refund_workflow_status(
            required_documents_completed,
            tax_case_type,
            eligible_refund_amount,
            request.instant_payout_requested,
        )
        return TaxRefundPrediction(
            tax_case_type=tax_case_type,
            document_status=document_status,
            workflow_status=workflow_status,
            government_verification_ref=_government_verification_ref(request),
            required_documents_completed=required_documents_completed,
            total_withheld_tax=total_withheld_tax,
            dividend_refund_amount=dividend_refund_amount,
            capital_gains_refund_amount=capital_gains_refund_amount,
            eligible_refund_amount=eligible_refund_amount,
            national_tax_refund_amount=national_tax_refund_amount,
            local_tax_refund_amount=local_tax_refund_amount,
            instant_payout_fee_amount=instant_payout_fee_amount,
            instant_payout_amount=instant_payout_amount,
            compliance_sandbox_flag=compliance_sandbox_flag,
            clawback_required_if_rejected=compliance_sandbox_flag == "Y",
            required_next_actions=_tax_required_next_actions(
                required_documents_completed,
                tax_case_type,
                eligible_refund_amount,
                workflow_status,
            ),
            risk_disclosure_message=_tax_risk_disclosure_message(compliance_sandbox_flag),
            review_message=_tax_review_message(
                required_documents_completed,
                tax_case_type,
                eligible_refund_amount,
            ),
            tax_model_version=self.version,
            document_model_version=self.document_model_version,
        )


class StockOrderStatusService:
    def __init__(
        self,
        ownership_model: ForeignOwnershipBoundaryModel | None = None,
        trading_state_model: TradingStateModel | None = None,
    ) -> None:
        self._ownership_model = ownership_model or ForeignOwnershipBoundaryModel()
        self._trading_state_model = trading_state_model or TradingStateModel()

    def build_response(self, request: StockOrderStatusRequest) -> StockOrderStatusResponse:
        ownership = self._ownership_model.predict(request)
        trading_state = self._trading_state_model.predict(request)
        order_availability = _order_availability(ownership, trading_state)

        return StockOrderStatusResponse(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            stock_name_en=request.stock_name_en,
            market=request.market,
            issued_shares=request.issued_shares,
            current_price=request.current_price,
            previous_close_price=request.previous_close_price,
            upper_limit_price=request.upper_limit_price,
            lower_limit_price=request.lower_limit_price,
            local_currency=request.local_currency,
            local_current_price=round(request.current_price * request.local_fx_rate, 4),
            foreign_owned_quantity=request.foreign_owned_quantity,
            foreign_limit_quantity=ownership.foreign_limit_quantity,
            foreign_limit_remaining_quantity=ownership.foreign_limit_remaining_quantity,
            foreign_ownership_rate=ownership.ownership_rate,
            foreign_limit_exhaustion_rate=ownership.limit_exhaustion_rate,
            fx_predicted_rate_min=ownership.predicted_rate_min,
            fx_predicted_rate_max=ownership.predicted_rate_max,
            foreign_limit_usage_status=ownership.usage_status,
            foreign_limit_warning=ownership.limit_warning,
            vi_activation_status=trading_state.vi_activation_status,
            vi_activation_reason=trading_state.vi_reasons,
            price_limit_status=trading_state.price_limit_status,
            immediate_execution_available=trading_state.immediate_execution_available,
            buy_order_available=order_availability.buy_order_available,
            sell_order_available=order_availability.sell_order_available,
            order_availability_indicator=order_availability.indicator,
            order_restriction_reasons=order_availability.restriction_reasons,
            order_guidance_message=trading_state.guidance_message,
            prediction_model_version=ownership.model_version,
            trading_state_model_version=trading_state.model_version,
            data_source="KIS/PredictEngine",
        )


class IntelligenceEventService:
    def __init__(self, analyzer: AlertAnalyzer) -> None:
        self._analyzer = analyzer
        self._translation_model = FinancialTranslationModel()

    def build_response(self, request: IntelligenceEventRequest) -> IntelligenceEventResponse:
        analysis_request = AlertAnalysisRequest(
            source_type=request.source_type,
            title=request.title,
            snippet=request.snippet,
            original_url=request.original_url,
            stock_universe=request.stock_universe,
        )
        analysis = self._analyzer.analyze(analysis_request)
        translation = self._translation_model.translate_event(request, analysis.summary)

        return IntelligenceEventResponse(
            alert_id=_alert_id(request),
            duplicate_key=analysis.duplicate_key,
            stock_code=analysis.stock_code,
            stock_name=analysis.stock_name,
            news_disclosure_type=request.source_type,
            original_title=request.title,
            translated_title=translation.translated_title,
            summary=analysis.summary,
            translated_summary=translation.translated_summary,
            sentiment=analysis.sentiment,
            importance=analysis.importance,
            event_tag=analysis.event_tags[0],
            event_tags=analysis.event_tags,
            related_stocks=analysis.related_stocks,
            is_holder_target=analysis.holder_target,
            is_watchlist_target=analysis.watchlist_target,
            glossary_terms=translation.glossary_terms,
            translation_quality_flags=translation.quality_flags,
            original_url=request.original_url,
            provider=request.provider,
            published_at=request.published_at,
            translation_provider=translation.provider,
            translation_model_version=translation.model_version,
            translation_status=translation.translation_status,
            model_version=analysis.model_version,
            event_confidence=analysis.event_confidence,
            sentiment_confidence=analysis.sentiment_confidence,
            importance_confidence=analysis.importance_confidence,
            stock_match_confidence=analysis.stock_match_confidence,
            review_required=analysis.review_required,
            review_reasons=analysis.review_reasons,
            data_source="Naver/OpenDART/NLP/DeepLTranslationAdapter",
        )


class TaxRefundStatusService:
    def __init__(self, tax_refund_model: TaxRefundAdvanceModel | None = None) -> None:
        self._tax_refund_model = tax_refund_model or TaxRefundAdvanceModel()

    def build_response(self, request: TaxRefundStatusRequest) -> TaxRefundStatusResponse:
        prediction = self._tax_refund_model.predict(request)
        return TaxRefundStatusResponse(
            investor_id=request.investor_id,
            tax_year=request.tax_year,
            tax_case_type=prediction.tax_case_type,
            refund_workflow_status=prediction.workflow_status,
            government_verification_ref=prediction.government_verification_ref,
            document_verification_status=prediction.document_status,
            required_documents_completed=prediction.required_documents_completed,
            total_withheld_tax=prediction.total_withheld_tax,
            dividend_refund_amount=prediction.dividend_refund_amount,
            capital_gains_refund_amount=prediction.capital_gains_refund_amount,
            eligible_refund_amount=prediction.eligible_refund_amount,
            national_tax_refund_amount=prediction.national_tax_refund_amount,
            local_tax_refund_amount=prediction.local_tax_refund_amount,
            instant_payout_fee_rate=round(request.instant_payout_fee_rate, 2),
            instant_payout_fee_amount=prediction.instant_payout_fee_amount,
            instant_payout_amount=prediction.instant_payout_amount,
            compliance_sandbox_flag=prediction.compliance_sandbox_flag,
            clawback_required_if_rejected=prediction.clawback_required_if_rejected,
            required_next_actions=prediction.required_next_actions,
            risk_disclosure_message=prediction.risk_disclosure_message,
            tax_model_version=prediction.tax_model_version,
            document_model_version=prediction.document_model_version,
            review_message=prediction.review_message,
        )


@dataclass(frozen=True)
class FinancialTranslationResult:
    translated_text: str
    glossary_terms: list[FinancialGlossaryTerm]


@dataclass(frozen=True)
class _GlossaryEntry:
    normalized_term: str
    english_term: str
    category: str
    aliases: tuple[str, ...]


def translate_financial_korean_to_english(text: str) -> FinancialTranslationResult:
    source_text = html.unescape(text)
    translated = source_text
    matched_terms: list[FinancialGlossaryTerm] = []
    seen_terms: set[tuple[str, str]] = set()

    for entry in _ordered_glossary_entries():
        for source_term in (entry.normalized_term, *entry.aliases):
            if source_term not in source_text:
                continue
            translated = translated.replace(source_term, entry.english_term)
            term_key = (entry.normalized_term, entry.english_term)
            if term_key in seen_terms:
                continue
            matched_terms.append(
                FinancialGlossaryTerm(
                    source_term=source_term,
                    normalized_term=entry.normalized_term,
                    english_term=entry.english_term,
                    category=entry.category,
                )
            )
            seen_terms.add(term_key)

    return FinancialTranslationResult(
        translated_text=" ".join(translated.split()),
        glossary_terms=matched_terms,
    )


def _ordered_glossary_entries() -> tuple[_GlossaryEntry, ...]:
    entries = tuple(
        _GlossaryEntry(
            normalized_term=normalized_term,
            english_term=english_term,
            category=category,
            aliases=aliases,
        )
        for normalized_term, english_term, category, aliases in FINANCIAL_TRANSLATION_GLOSSARY
    )
    return tuple(
        sorted(
            entries,
            key=lambda entry: max(
                len(term) for term in (entry.normalized_term, *entry.aliases)
            ),
            reverse=True,
        )
    )


def _merge_glossary_terms(
    first: list[FinancialGlossaryTerm],
    second: list[FinancialGlossaryTerm],
) -> list[FinancialGlossaryTerm]:
    merged: list[FinancialGlossaryTerm] = []
    seen_terms: set[tuple[str, str]] = set()
    for term in [*first, *second]:
        term_key = (term.normalized_term, term.english_term)
        if term_key in seen_terms:
            continue
        merged.append(term)
        seen_terms.add(term_key)
    return merged


def _translation_quality_flags(
    title: str,
    translated_title: str,
    summary: str,
    translated_summary: str,
    glossary_terms: list[FinancialGlossaryTerm],
) -> list[str]:
    flags: list[str] = []
    if glossary_terms:
        flags.append("FINANCIAL_GLOSSARY_APPLIED")
    if _contains_korean_financial_term(title, translated_title) or _contains_korean_financial_term(
        summary,
        translated_summary,
    ):
        flags.append("UNTRANSLATED_FINANCIAL_TERM_REVIEW_REQUIRED")
    if not flags:
        flags.append("SOURCE_LANGUAGE_FALLBACK_REVIEW_REQUIRED")
    return flags


def _contains_korean_financial_term(source_text: str, translated_text: str) -> bool:
    if source_text == translated_text:
        return False
    return any(
        term in translated_text
        for normalized_term, _, _, aliases in FINANCIAL_TRANSLATION_GLOSSARY
        for term in (normalized_term, *aliases)
    )


class TaxDocumentVerificationService:
    def __init__(self, model: TaxDocumentVerificationModel | None = None) -> None:
        self._model = model or TaxDocumentVerificationModel()

    def build_response(
        self,
        request: TaxDocumentVerificationRequest,
    ) -> TaxDocumentVerificationResponse:
        prediction = self._model.predict(request)
        return TaxDocumentVerificationResponse(
            document_type=request.document_type,
            file_name=request.file_name,
            verification_status=prediction.verification_status,
            ocr_confidence=round(request.ocr_confidence, 4),
            fraud_risk_score=prediction.fraud_risk_score,
            risk_level=prediction.risk_level,
            manual_review_required=prediction.manual_review_required,
            extracted_fields=prediction.extracted_fields,
            missing_required_fields=prediction.missing_required_fields,
            rejection_reasons=prediction.rejection_reasons,
            document_model_version=prediction.document_model_version,
        )


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator * 100


def _foreign_limit_usage_status(
    predicted_max: float,
    foreign_limit_rate: float,
) -> ForeignLimitUsageStatus:
    if predicted_max >= foreign_limit_rate:
        return "LIMIT_REACHED"
    if predicted_max >= foreign_limit_rate - FOREIGN_LIMIT_WARNING_BUFFER_PERCENT:
        return "CAUTION"
    return "NORMAL"


def _vi_reasons(request: StockOrderStatusRequest) -> list[str]:
    reasons: list[str] = []
    if request.dynamic_vi_activated:
        reasons.append("DYNAMIC_VI")
    if request.static_vi_activated:
        reasons.append("STATIC_VI")
    if request.trading_session_status == "SINGLE_PRICE":
        reasons.append("SINGLE_PRICE_SESSION")
    return reasons


def _price_limit_status(request: StockOrderStatusRequest) -> PriceLimitStatus:
    if request.upper_limit_price and request.current_price >= request.upper_limit_price:
        return "UPPER"
    if request.lower_limit_price and request.current_price <= request.lower_limit_price:
        return "LOWER"
    return "NORMAL"


def _order_availability(
    ownership: ForeignOwnershipPrediction,
    trading_state: TradingStatePrediction,
) -> OrderAvailabilityPrediction:
    reasons: list[str] = []
    if not trading_state.immediate_execution_available:
        reasons.append("REALTIME_EXECUTION_LIMITED")
    if ownership.usage_status == "LIMIT_REACHED":
        reasons.append("FOREIGN_LIMIT_REACHED")
    elif ownership.usage_status == "CAUTION":
        reasons.append("FOREIGN_LIMIT_CAUTION")

    buy_order_available = (
        trading_state.immediate_execution_available
        and ownership.usage_status != "LIMIT_REACHED"
    )
    sell_order_available = trading_state.immediate_execution_available
    indicator: OrderAvailabilityIndicator
    if not buy_order_available and not sell_order_available:
        indicator = "LIMITED"
    elif reasons:
        indicator = "CAUTION"
    else:
        indicator = "AVAILABLE"

    return OrderAvailabilityPrediction(
        buy_order_available=buy_order_available,
        sell_order_available=sell_order_available,
        indicator=indicator,
        restriction_reasons=reasons,
    )


def _order_guidance_message(
    vi_reasons: list[str],
    price_limit_status: PriceLimitStatus,
    immediate_execution_available: bool,
) -> str:
    if vi_reasons:
        return (
            "해당 종목은 현재 변동성 완화장치(VI) 또는 단일가 매매 상태로 "
            "실시간 즉시 체결이 제한될 수 있습니다."
        )
    if price_limit_status == "UPPER":
        return "현재 상한가 도달 상태로 매수 주문 체결이 지연되거나 불가능할 수 있습니다."
    if price_limit_status == "LOWER":
        return "현재 하한가 도달 상태로 매도 주문 체결이 지연되거나 불가능할 수 있습니다."
    if immediate_execution_available:
        return "정규장 기준 실시간 즉시 체결 가능 상태입니다."
    return "현재 거래 세션 상태를 확인해야 합니다."


def _alert_id(request: IntelligenceEventRequest) -> str:
    payload = (
        f"{request.source_type}:{request.title}:"
        f"{request.original_url}:{request.target_language}"
    )
    return sha256(payload.encode()).hexdigest()


def _required_documents_completed(request: TaxRefundStatusRequest) -> bool:
    required_types = {"RESIDENCE_CERTIFICATE", "TREATY_APPLICATION"}
    verified_types = {
        document.document_type
        for document in request.documents
        if document.verification_status == "VERIFIED"
        and document.ocr_confidence >= 0.8
        and document.fraud_risk_score <= 0.2
    }
    return required_types.issubset(verified_types)


def _normalize_document_fields(request: TaxDocumentVerificationRequest) -> dict[str, str]:
    fields = {
        key.strip().lower(): value.strip()
        for key, value in request.extracted_fields.items()
        if key.strip() and value.strip()
    }
    normalized_text = request.extracted_text.lower()
    fields.setdefault("document_type", request.document_type)
    if request.expected_investor_id and request.expected_investor_id.lower() in normalized_text:
        fields.setdefault("investor_id", request.expected_investor_id)
    if request.expected_residency_country and _country_present(
        normalized_text,
        request.expected_residency_country,
    ):
        fields.setdefault("residency_country", request.expected_residency_country.upper())
    return fields


def _missing_required_document_fields(
    request: TaxDocumentVerificationRequest,
    extracted_fields: dict[str, str],
) -> list[str]:
    required_fields = ["document_type"]
    if request.document_type == "RESIDENCE_CERTIFICATE":
        required_fields.extend(["investor_id", "residency_country"])
    elif request.document_type == "TREATY_APPLICATION":
        required_fields.extend(["investor_id", "treaty_application_marker"])
    missing = [field for field in required_fields if field not in extracted_fields]
    normalized_text = request.extracted_text.lower()
    if request.document_type == "TREATY_APPLICATION" and "treaty_application_marker" in missing:
        if any(keyword in normalized_text for keyword in ("treaty", "제한세율", "조세조약")):
            missing.remove("treaty_application_marker")
    if request.document_type == "RESIDENCE_CERTIFICATE" and "residency_country" in missing:
        if request.expected_residency_country and _country_present(
            normalized_text,
            request.expected_residency_country,
        ):
            missing.remove("residency_country")
    return missing


def _document_rejection_reasons(
    request: TaxDocumentVerificationRequest,
    missing_required_fields: list[str],
) -> list[str]:
    reasons: list[str] = []
    if request.ocr_confidence < 0.5:
        reasons.append("OCR_CONFIDENCE_TOO_LOW")
    if request.fraud_signal_score >= 0.7:
        reasons.append("HIGH_FORGERY_RISK")
    if not request.extracted_text.strip() and not request.extracted_fields:
        reasons.append("NO_EXTRACTED_CONTENT")
    if missing_required_fields and request.ocr_confidence < 0.65:
        reasons.append("REQUIRED_FIELDS_UNREADABLE")
    return reasons


def _document_risk_level(ocr_confidence: float, fraud_signal_score: float) -> DocumentRiskLevel:
    if ocr_confidence < 0.65 or fraud_signal_score >= 0.5:
        return "HIGH"
    if ocr_confidence < 0.8 or fraud_signal_score > 0.2:
        return "MEDIUM"
    return "LOW"


def _document_verification_status(
    request: TaxDocumentVerificationRequest,
    missing_required_fields: list[str],
    rejection_reasons: list[str],
) -> DocumentVerificationStatus:
    if rejection_reasons:
        return "REJECTED"
    if missing_required_fields or request.ocr_confidence < 0.8 or request.fraud_signal_score > 0.2:
        return "PENDING"
    return "VERIFIED"


def _country_present(normalized_text: str, country: str) -> bool:
    country = country.upper()
    country_aliases = {
        "HK": ("hk", "hong kong", "홍콩"),
        "US": ("us", "usa", "united states", "미국"),
    }
    aliases = country_aliases.get(country, (country.lower(),))
    return any(alias in normalized_text for alias in aliases)


def _tax_case_type(request: TaxRefundStatusRequest) -> TaxCaseType:
    if request.tax_residency_country != "HK":
        return "CASE_REVIEW_REQUIRED"
    if any(not transaction.listed_market_trade for transaction in request.transactions):
        return "CASE_REVIEW_REQUIRED"
    max_ownership_rate = max(
        (transaction.ownership_rate_percent for transaction in request.transactions),
        default=0.0,
    )
    if max_ownership_rate >= CASE_01_MAX_OWNERSHIP_RATE:
        return "CASE_REVIEW_REQUIRED"
    return "CASE_01"


def _dividend_refund_amount(request: TaxRefundStatusRequest) -> int:
    gross_dividend = sum(
        transaction.gross_dividend_amount
        for transaction in request.transactions
        if transaction.transaction_type == "DIVIDEND"
    )
    return round(
        gross_dividend * (DIVIDEND_DOMESTIC_WITHHOLDING_RATE - DIVIDEND_TREATY_LIMIT_RATE)
    )


def _capital_gains_refund_amount(request: TaxRefundStatusRequest) -> int:
    sell_proceeds = sum(
        transaction.sell_proceeds
        for transaction in request.transactions
        if transaction.transaction_type == "SELL"
    )
    capital_gain = sum(
        max(0, transaction.capital_gain)
        for transaction in request.transactions
        if transaction.transaction_type == "SELL"
    )
    return round(
        min(
            sell_proceeds * CAPITAL_GAINS_SELL_PROCEEDS_RATE,
            capital_gain * CAPITAL_GAINS_PROFIT_RATE,
        )
    )


def _government_verification_ref(request: TaxRefundStatusRequest) -> str:
    payload = f"{request.investor_id}:{request.tax_residency_country}:{request.tax_year}"
    return f"TX-{sha256(payload.encode()).hexdigest()[:10].upper()}"


def _tax_refund_workflow_status(
    required_documents_completed: bool,
    tax_case_type: TaxCaseType,
    eligible_refund_amount: int,
    instant_payout_requested: bool,
) -> TaxRefundWorkflowStatus:
    if not required_documents_completed:
        return "DOCUMENTS_PENDING"
    if tax_case_type != "CASE_01":
        return "REVIEW_REQUIRED"
    if eligible_refund_amount <= 0:
        return "NO_REFUND_AVAILABLE"
    if instant_payout_requested:
        return "ELIGIBLE_FOR_INSTANT_PAYOUT"
    return "QUARTERLY_REFUND_READY"


def _tax_required_next_actions(
    required_documents_completed: bool,
    tax_case_type: TaxCaseType,
    eligible_refund_amount: int,
    workflow_status: TaxRefundWorkflowStatus,
) -> list[str]:
    if not required_documents_completed:
        return ["UPLOAD_RESIDENCE_CERTIFICATE", "UPLOAD_TREATY_APPLICATION"]
    if tax_case_type != "CASE_01":
        return ["MANUAL_TAX_REVIEW_REQUIRED"]
    if eligible_refund_amount <= 0:
        return ["WAIT_FOR_ELIGIBLE_TAX_EVENT"]
    if workflow_status == "ELIGIBLE_FOR_INSTANT_PAYOUT":
        return ["CONFIRM_INSTANT_PAYOUT_TERMS"]
    return ["SUBMIT_QUARTERLY_REFUND_BATCH"]


def _tax_risk_disclosure_message(compliance_sandbox_flag: Literal["Y", "N"]) -> str:
    if compliance_sandbox_flag == "Y":
        return "국세청 검토 결과 면세 자격 거부 시 선지급 금액은 자동 환수될 수 있습니다."
    return "분기 사후 환급 선택 시 국세청 검토 완료 후 환급금이 확정됩니다."


def _tax_review_message(
    required_documents_completed: bool,
    tax_case_type: TaxCaseType,
    eligible_refund_amount: int,
) -> str:
    if not required_documents_completed:
        return "거주자증명서와 제한세율신청서 검증 완료 후 환급 가능 금액을 확정합니다."
    if tax_case_type != "CASE_01":
        return "상장주식 장내거래 및 25% 미만 지분율 조건을 추가 검토해야 합니다."
    if eligible_refund_amount <= 0:
        return "현재 선지급 가능한 환급금이 없습니다."
    return "CASE_01 요건을 충족하여 샌드박스 선지급 가능 상태입니다."
