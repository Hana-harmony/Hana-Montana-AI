from __future__ import annotations

import base64
import binascii
import html
import re
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Literal, Protocol, cast

from hanah_tax_ocr.ocr import TesseractOCREngine
from hanah_tax_ocr.parsers import build_parser_registry
from hanah_tax_ocr.pipeline import TaxDocumentPipeline
from hanah_tax_ocr.review import TaxDocumentReviewer
from hanah_tax_ocr.schemas import (
    DocumentType as OcrDocumentType,
)
from hanah_tax_ocr.schemas import (
    ExtractedDocument,
    OCRPage,
    OCRResult,
    ReviewStatus,
)
from hannah_montana_ai.core.config import get_settings
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
    SourceType,
    StockOrderStatusRequest,
    StockOrderStatusResponse,
    SummaryLines,
    TaxCaseType,
    TaxDocumentVerificationRequest,
    TaxDocumentVerificationResponse,
    TaxRefundStatusRequest,
    TaxRefundStatusResponse,
    TaxRefundWorkflowStatus,
)
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.korean_financial_terms import load_financial_term_entries
from hannah_montana_ai.services.korean_translation_generator import (
    SOURCE_LANGUAGE_FALLBACK_PROVIDER,
    KoreanTranslationContext,
    KoreanTranslationResult,
)

FOREIGN_LIMIT_WARNING_BUFFER_PERCENT = 1.0
DIVIDEND_DOMESTIC_WITHHOLDING_RATE = 0.22
DIVIDEND_TREATY_LIMIT_RATE = 0.15
CAPITAL_GAINS_SELL_PROCEEDS_RATE = 0.11
CAPITAL_GAINS_PROFIT_RATE = 0.22
CASE_01_MAX_OWNERSHIP_RATE = 25.0
FOREIGN_OWNERSHIP_MODEL_VERSION = "foreign-ownership-boundary-v1"
TRADING_STATE_MODEL_VERSION = "krx-vi-price-limit-state-v1"
TRANSLATION_MODEL_VERSION = "local-llm:Qwen3-4B-GGUF-Q4"
TAX_REFUND_MODEL_VERSION = "us-treaty-refund-case-engine-v1"
DOCUMENT_VERIFICATION_MODEL_VERSION = "ocr-fraud-risk-gate-v1"
HANAH_TAX_OCR_MODEL_VERSION = "hanah-tax-ocr-e2e-review-v2"
LOCAL_TAX_REFUND_SHARE = 0.10
TEXT_TAX_DOCUMENT_CONTENT_TYPES = {
    "text/plain",
    "text/csv",
    "application/json",
}
OCR_TAX_DOCUMENT_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/tiff",
    "image/bmp",
}
OCR_TAX_DOCUMENT_SUFFIXES = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
}


class KoreanTranslationService(Protocol):
    def translate(self, context: KoreanTranslationContext) -> KoreanTranslationResult:
        pass


TRANSLATION_SUPPORT_GLOSSARY = (
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
    ("개선", "improvement", "sentiment", ()),
    ("상폐 위기", "delisting crisis", "risk", ("상장폐지 위기",)),
    ("응원", "support", "sentiment", ()),
    ("급등", "surge", "sentiment", ()),
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
DISPLAY_FINANCIAL_GLOSSARY_TERMS = frozenset(
    {
        "삼전닉스",
        "빚투",
        "어닝쇼크",
        "어닝서프라이즈",
    }
)
QWEN_TRANSLATION_GLOSSARY_CATEGORY_PRIORITY = {
    "stock": 0,
    "market_slang": 1,
    "risk": 2,
    "event": 3,
    "disclosure": 4,
    "market_state": 5,
    "index": 6,
    "fx": 7,
    "metric": 8,
}


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
    translated_summary_lines: SummaryLines
    translated_content: str
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
    ocr_confidence: float
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
    provider = SOURCE_LANGUAGE_FALLBACK_PROVIDER

    def __init__(self, translation_generator: KoreanTranslationService | None = None) -> None:
        self._translation_generator = translation_generator

    def translate_event(
        self,
        request: IntelligenceEventRequest,
        summary: str,
        summary_lines: SummaryLines | None = None,
    ) -> TranslationPrediction:
        source_summary_lines = _source_summary_lines(summary, summary_lines)
        title_translation = translate_financial_korean_to_english(request.title)
        summary_translation = translate_financial_korean_to_english(summary)
        content_translation = translate_financial_korean_to_english(request.content)
        glossary_terms = _merge_glossary_terms(
            title_translation.glossary_terms,
            summary_translation.glossary_terms,
            content_translation.glossary_terms,
        )
        display_glossary_terms = _display_glossary_terms(glossary_terms)
        qwen_glossary_terms = _qwen_translation_glossary_terms(glossary_terms)
        qwen_title_translation = self._translate_with_qwen(
            text=request.title,
            source_type=request.source_type,
            title=request.title,
            glossary_terms=qwen_glossary_terms,
        )
        qwen_summary_translation = self._translate_with_qwen(
            text=summary,
            source_type=request.source_type,
            title=request.title,
            glossary_terms=qwen_glossary_terms,
        )
        qwen_content_translation = self._translate_with_qwen(
            text=request.content,
            source_type=request.source_type,
            title=request.title,
            glossary_terms=qwen_glossary_terms,
        )
        translated_title = _preferred_translation(qwen_title_translation)
        translated_summary = _preferred_translation(qwen_summary_translation)
        translated_summary_lines, summary_line_qwen_results = self._translate_summary_lines(
            source_summary_lines,
            request=request,
            glossary_terms=qwen_glossary_terms,
        )
        translated_summary = _join_summary_lines(translated_summary_lines) or translated_summary
        translated_content = _preferred_content_translation(qwen_content_translation)
        quality_flags = _translation_quality_flags(
            request.title,
            translated_title,
            summary,
            translated_summary,
            display_glossary_terms,
            translation_terms_applied=bool(glossary_terms),
        )
        quality_flags.extend(
            _qwen_translation_quality_flags(
                qwen_title_translation,
                qwen_summary_translation,
                qwen_content_translation,
                *summary_line_qwen_results,
            )
        )
        if _contains_hangul(_join_summary_lines(translated_summary_lines)):
            quality_flags.append("UNTRANSLATED_SUMMARY_LINE_REVIEW_REQUIRED")
        if _contains_hangul(translated_content):
            quality_flags.append("UNTRANSLATED_CONTENT_REVIEW_REQUIRED")
        requires_content_translation = (
            bool(request.content.strip())
            and request.source_license_policy != "NAVER_SEARCH_SNIPPET_ONLY"
        )
        if requires_content_translation and not translated_content.strip():
            quality_flags.append("CONTENT_TRANSLATION_UNAVAILABLE")
        quality_flags = list(dict.fromkeys(quality_flags))
        translation_status: Literal["TRANSLATED", "SOURCE_LANGUAGE_FALLBACK"] = (
            "TRANSLATED"
            if (
                (not requires_content_translation or bool(translated_content.strip()))
                and (
                    translated_title != html.unescape(request.title)
                    or translated_summary != html.unescape(summary)
                    or translated_content != html.unescape(request.content)
                )
            )
            else "SOURCE_LANGUAGE_FALLBACK"
        )
        provider = _translation_provider(
            qwen_content_translation,
            qwen_summary_translation,
            qwen_title_translation,
            fallback=self.provider,
        )
        model_version = _translation_model_version(
            qwen_content_translation,
            qwen_summary_translation,
            qwen_title_translation,
            fallback=self.version,
        )
        return TranslationPrediction(
            translated_title=translated_title,
            translated_summary=translated_summary,
            translated_summary_lines=translated_summary_lines,
            translated_content=translated_content,
            translation_status=translation_status,
            glossary_terms=display_glossary_terms,
            quality_flags=quality_flags,
            provider=provider,
            model_version=model_version,
        )

    def _translate_with_qwen(
        self,
        *,
        text: str,
        source_type: SourceType,
        title: str,
        glossary_terms: list[FinancialGlossaryTerm],
    ) -> KoreanTranslationResult | None:
        if self._translation_generator is None or not _contains_hangul(text):
            return None
        return self._translation_generator.translate(
            KoreanTranslationContext(
                text=text,
                source_type=source_type,
                title=title,
                glossary_terms=glossary_terms,
            )
        )

    def _translate_summary_lines(
        self,
        summary_lines: SummaryLines,
        *,
        request: IntelligenceEventRequest,
        glossary_terms: list[FinancialGlossaryTerm],
    ) -> tuple[SummaryLines, list[KoreanTranslationResult | None]]:
        translated_lines: list[str] = []
        qwen_results: list[KoreanTranslationResult | None] = []
        for line in (summary_lines.what, summary_lines.why, summary_lines.impact):
            qwen_result = self._translate_with_qwen(
                text=line,
                source_type=request.source_type,
                title=request.title,
                glossary_terms=glossary_terms,
            )
            qwen_results.append(qwen_result)
            translated_lines.append(
                _normalize_summary_line(
                    _preferred_translation(qwen_result)
                )
            )
        return (
            SummaryLines(
                what=translated_lines[0],
                why=translated_lines[1],
                impact=translated_lines[2],
            ),
            qwen_results,
        )


class TaxDocumentVerificationModel:
    version = DOCUMENT_VERIFICATION_MODEL_VERSION

    def predict(self, request: TaxDocumentVerificationRequest) -> TaxDocumentVerificationPrediction:
        ocr_prediction = _predict_with_hanah_tax_ocr(request)
        if ocr_prediction is not None:
            return ocr_prediction

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
            ocr_confidence=request.ocr_confidence,
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
        dividend_refund_amount = _dividend_refund_amount(request) if eligible_for_refund else 0
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
    def __init__(
        self,
        analyzer: AlertAnalyzer,
        translation_model: FinancialTranslationModel | None = None,
    ) -> None:
        self._analyzer = analyzer
        self._translation_model = translation_model or FinancialTranslationModel()

    def build_response(self, request: IntelligenceEventRequest) -> IntelligenceEventResponse:
        analysis_request = AlertAnalysisRequest(
            source_type=request.source_type,
            title=request.title,
            snippet=request.snippet,
            content=request.content,
            image_urls=request.image_urls,
            canonical_url=request.canonical_url,
            content_hash=request.content_hash,
            source_license_policy=request.source_license_policy,
            original_url=request.original_url,
            stock_universe=request.stock_universe,
        )
        analysis = self._analyzer.analyze(analysis_request)
        translation_request = request.model_copy(
            update={"content": analysis.original_content or request.content}
        )
        translation = self._translation_model.translate_event(
            translation_request,
            analysis.summary,
            analysis.summary_lines,
        )

        return IntelligenceEventResponse(
            alert_id=_alert_id(request),
            duplicate_key=analysis.duplicate_key,
            stock_code=analysis.stock_code,
            stock_name=analysis.stock_name,
            news_disclosure_type=request.source_type,
            original_title=request.title,
            translated_title=translation.translated_title,
            summary=analysis.summary,
            summary_lines=translation.translated_summary_lines,
            translated_summary=translation.translated_summary,
            original_content=analysis.original_content,
            translated_content=translation.translated_content,
            original_body=analysis.original_body,
            translated_body=translation.translated_content,
            body_source_type=analysis.body_source_type,
            image_urls=analysis.image_urls,
            content_availability=analysis.content_availability,
            sentiment=analysis.sentiment,
            importance=analysis.importance,
            event_tag=analysis.event_tags[0],
            event_tags=analysis.event_tags,
            related_stocks=analysis.related_stocks,
            is_holder_target=analysis.holder_target,
            is_watchlist_target=analysis.watchlist_target,
            cluster_key=analysis.cluster_key,
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
            data_source="Naver/OpenDART/NLP/QwenTranslationAdapter",
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

    translated = _grounded_short_financial_sentence_translation(
        source_text,
        translated,
        matched_terms,
    )

    return FinancialTranslationResult(
        translated_text=" ".join(translated.split()),
        glossary_terms=matched_terms,
    )


@lru_cache
def _ordered_glossary_entries() -> tuple[_GlossaryEntry, ...]:
    support_entries = tuple(
        _GlossaryEntry(
            normalized_term=normalized_term,
            english_term=english_term,
            category=category,
            aliases=aliases,
        )
        for normalized_term, english_term, category, aliases in TRANSLATION_SUPPORT_GLOSSARY
    )
    dictionary_entries = tuple(
        _GlossaryEntry(
            normalized_term=entry.normalized_term,
            english_term=entry.english_term,
            category=entry.category,
            aliases=entry.aliases,
        )
        for entry in load_financial_term_entries(
            get_settings().korean_financial_terms_seed_path
        )
    )
    entries_by_term = {entry.normalized_term: entry for entry in support_entries}
    entries_by_term.update({entry.normalized_term: entry for entry in dictionary_entries})
    return tuple(
        sorted(
            entries_by_term.values(),
            key=lambda entry: max(len(term) for term in (entry.normalized_term, *entry.aliases)),
            reverse=True,
        )
    )


def _grounded_short_financial_sentence_translation(
    source_text: str,
    translated_text: str,
    matched_terms: list[FinancialGlossaryTerm],
) -> str:
    if not _contains_hangul(translated_text):
        return translated_text
    normalized_source = " ".join(source_text.split())
    company = _primary_stock_english_term(matched_terms)
    if (
        company
        and "영업이익" in normalized_source
        and ("증가" in normalized_source or "개선" in normalized_source)
        and any(term in normalized_source for term in ("예상", "기대", "전망"))
    ):
        direction = "improve" if "개선" in normalized_source else "increase"
        period = "second-quarter " if "2분기" in normalized_source else ""
        drivers = _earnings_driver_surfaces(normalized_source)
        driver_text = f" on {_join_english_items(drivers)}" if drivers else ""
        return f"{company} expects {period}operating profit to {direction}{driver_text}."
    return translated_text


def _primary_stock_english_term(
    matched_terms: list[FinancialGlossaryTerm],
) -> str:
    for term in matched_terms:
        if term.category == "stock":
            return term.english_term
    return ""


def _earnings_driver_surfaces(source_text: str) -> list[str]:
    drivers: list[str] = []
    if "공급계약" in source_text:
        drivers.append("supply-contract expansion")
    if "반도체" in source_text and "수요 회복" in source_text:
        drivers.append("recovering semiconductor demand")
    elif "수요 회복" in source_text:
        drivers.append("recovering demand")
    return drivers


def _join_english_items(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} and {items[-1]}"


def _merge_glossary_terms(
    *term_groups: list[FinancialGlossaryTerm],
) -> list[FinancialGlossaryTerm]:
    merged: list[FinancialGlossaryTerm] = []
    seen_terms: set[tuple[str, str]] = set()
    for terms in term_groups:
        for term in terms:
            term_key = (term.normalized_term, term.english_term)
            if term_key in seen_terms:
                continue
            merged.append(term)
            seen_terms.add(term_key)
    return merged


def _display_glossary_terms(terms: list[FinancialGlossaryTerm]) -> list[FinancialGlossaryTerm]:
    return [
        term
        for term in terms
        if term.normalized_term in DISPLAY_FINANCIAL_GLOSSARY_TERMS
        and _contains_hangul(term.normalized_term)
    ]


def _qwen_translation_glossary_terms(
    terms: list[FinancialGlossaryTerm],
) -> list[FinancialGlossaryTerm]:
    return sorted(
        [term for term in terms if term.category in QWEN_TRANSLATION_GLOSSARY_CATEGORY_PRIORITY],
        key=lambda term: (
            QWEN_TRANSLATION_GLOSSARY_CATEGORY_PRIORITY[term.category],
            term.normalized_term,
        ),
    )


def _source_summary_lines(summary: str, summary_lines: SummaryLines | None) -> SummaryLines:
    if summary_lines and _join_summary_lines(summary_lines):
        return SummaryLines(
            what=_normalize_summary_line(summary_lines.what),
            why=_normalize_summary_line(summary_lines.why),
            impact=_normalize_summary_line(summary_lines.impact),
        )
    lines = [
        line
        for line in (_normalize_summary_line(line) for line in summary.splitlines())
        if line
    ]
    if len(lines) < 3:
        lines = _sentence_summary_lines(summary)
    while len(lines) < 3:
        lines.append("")
    return SummaryLines(what=lines[0], why=lines[1], impact=lines[2])


def _sentence_summary_lines(summary: str) -> list[str]:
    normalized = " ".join(html.unescape(summary or "").split())
    if not normalized:
        return []
    sentences = re.findall(r"[^.!?。？！]+[.!?。？！]", normalized)
    if not sentences:
        return [_normalize_summary_line(normalized)]
    return [_normalize_summary_line(sentence) for sentence in sentences[:3]]


def _join_summary_lines(summary_lines: SummaryLines) -> str:
    return "\n".join(
        line
        for line in (
            _normalize_summary_line(summary_lines.what),
            _normalize_summary_line(summary_lines.why),
            _normalize_summary_line(summary_lines.impact),
        )
        if line
    )


def _normalize_summary_line(value: str) -> str:
    normalized = " ".join(html.unescape(value or "").split())
    normalized = re.sub(r"^(?:what|why|impact)\s*[:：\-]\s*", "", normalized, flags=re.I)
    normalized = normalized.strip(" -•")
    normalized = _first_sentence_or_text(normalized)
    normalized = _fit_summary_line(normalized)
    if normalized and not normalized.endswith((".", "!", "?", "。", "！", "？")):
        normalized = f"{normalized}."
    return normalized


def _first_sentence_or_text(value: str) -> str:
    match = re.match(r"(.+?[.!?。？！])(?:\s|$)", value)
    if match:
        return match.group(1).strip()
    return value


def _fit_summary_line(value: str, max_length: int = 500) -> str:
    if len(value) <= max_length:
        return value
    clipped = value[: max_length - 1].rstrip()
    for delimiter in (".", "!", "?", "。", "！", "？"):
        index = clipped.rfind(delimiter)
        if index >= 120:
            return clipped[: index + 1].strip()
    word_boundary = clipped.rfind(" ")
    if word_boundary >= 120:
        clipped = clipped[:word_boundary].rstrip()
    return clipped.rstrip(".!?。？！") + "."


def _preferred_translation(
    qwen_result: KoreanTranslationResult | None,
    *,
    allow_flagged_english: bool = False,
) -> str:
    if (
        qwen_result is not None
        and qwen_result.translated_text.strip()
        and not qwen_result.quality_flags
        and qwen_result.provider != SOURCE_LANGUAGE_FALLBACK_PROVIDER
    ):
        return qwen_result.translated_text.strip()
    if (
        allow_flagged_english
        and qwen_result is not None
        and qwen_result.translated_text.strip()
        and qwen_result.provider != SOURCE_LANGUAGE_FALLBACK_PROVIDER
        and not _contains_hangul(qwen_result.translated_text)
        and _has_only_tolerable_translation_flags(qwen_result.quality_flags)
    ):
        return qwen_result.translated_text.strip()
    return ""


def _preferred_content_translation(
    qwen_result: KoreanTranslationResult | None,
) -> str:
    candidate = _preferred_translation(
        qwen_result,
        allow_flagged_english=True,
    ).strip()
    if candidate and not _contains_hangul(candidate):
        return candidate
    return ""


def _has_only_tolerable_translation_flags(flags: list[str]) -> bool:
    if not flags:
        return True
    return all(
        flag == "SOURCE_NUMBER_MISSING" or flag.startswith("SOURCE_TERM_MISSING:")
        for flag in flags
    )


def _qwen_translation_quality_flags(
    *results: KoreanTranslationResult | None,
) -> list[str]:
    flags: list[str] = []
    for result in results:
        if result is None:
            continue
        if (
            result.provider == SOURCE_LANGUAGE_FALLBACK_PROVIDER
            and not result.translated_text.strip()
        ):
            continue
        if (
            result.translated_text.strip()
            and result.provider != SOURCE_LANGUAGE_FALLBACK_PROVIDER
            and not _contains_hangul(result.translated_text)
            and _has_only_tolerable_translation_flags(result.quality_flags)
        ):
            continue
        for flag in result.quality_flags:
            flags.append(f"QWEN_TRANSLATION_{flag}")
    if any(
        result is not None
        and result.translated_text.strip()
        and (
            not result.quality_flags
            or (
                not _contains_hangul(result.translated_text)
                and _has_only_tolerable_translation_flags(result.quality_flags)
            )
        )
        and result.provider != SOURCE_LANGUAGE_FALLBACK_PROVIDER
        for result in results
    ):
        flags.append("QWEN_TRANSLATION_APPLIED")
    return flags


def _translation_provider(
    *results: KoreanTranslationResult | None,
    fallback: str,
) -> str:
    for result in results:
        if (
            result is not None
            and result.translated_text.strip()
            and not result.quality_flags
            and result.provider != SOURCE_LANGUAGE_FALLBACK_PROVIDER
        ):
            return result.provider
    return fallback


def _translation_model_version(
    *results: KoreanTranslationResult | None,
    fallback: str,
) -> str:
    for result in results:
        if (
            result is not None
            and result.translated_text.strip()
            and not result.quality_flags
            and result.provider != SOURCE_LANGUAGE_FALLBACK_PROVIDER
        ):
            return result.model_version
    return fallback


def _translation_quality_flags(
    title: str,
    translated_title: str,
    summary: str,
    translated_summary: str,
    glossary_terms: list[FinancialGlossaryTerm],
    *,
    translation_terms_applied: bool = False,
) -> list[str]:
    flags: list[str] = []
    if glossary_terms:
        flags.append("FINANCIAL_GLOSSARY_APPLIED")
    if _contains_korean_financial_term(title, translated_title) or _contains_korean_financial_term(
        summary,
        translated_summary,
    ):
        flags.append("UNTRANSLATED_FINANCIAL_TERM_REVIEW_REQUIRED")
    if translation_terms_applied and "FINANCIAL_TRANSLATION_TERMS_APPLIED" not in flags:
        flags.append("FINANCIAL_TRANSLATION_TERMS_APPLIED")
    if not flags:
        flags.append("SOURCE_LANGUAGE_FALLBACK_REVIEW_REQUIRED")
    return flags


def _contains_korean_financial_term(source_text: str, translated_text: str) -> bool:
    if source_text == translated_text:
        return False
    return any(
        term in translated_text
        for entry in _ordered_glossary_entries()
        for term in (entry.normalized_term, *entry.aliases)
        if _contains_hangul(term)
    )


def _contains_hangul(value: str) -> bool:
    return bool(re.search(r"[가-힣]", value))


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
            ocr_confidence=round(prediction.ocr_confidence, 4),
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
        trading_state.immediate_execution_available and ownership.usage_status != "LIMIT_REACHED"
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
        f"{request.source_type}:{request.title}:{request.original_url}:{request.target_language}"
    )
    return sha256(payload.encode()).hexdigest()


def _required_documents_completed(request: TaxRefundStatusRequest) -> bool:
    verified_types = {
        document.document_type
        for document in request.documents
        if document.verification_status == "VERIFIED"
        and document.ocr_confidence >= 0.75
        and document.fraud_risk_score <= 0.2
    }
    has_application = bool(
        {"TREATY_APPLICATION", "REDUCED_TAX_APPLICATION"} & verified_types
    )
    return "RESIDENCE_CERTIFICATE" in verified_types and has_application


def _predict_with_hanah_tax_ocr(
    request: TaxDocumentVerificationRequest,
) -> TaxDocumentVerificationPrediction | None:
    if not request.document_content_base64:
        return None
    ocr_document_type = _ocr_document_type(request.document_type)
    if ocr_document_type is None:
        return None

    (
        ocr_result,
        pipeline_extracted,
        ocr_confidence,
        unavailable_reason,
        document_checks,
    ) = _ocr_result_from_request(request, ocr_document_type)
    if unavailable_reason is not None:
        return TaxDocumentVerificationPrediction(
            verification_status="REJECTED",
            ocr_confidence=0.0,
            fraud_risk_score=1.0,
            risk_level="HIGH",
            manual_review_required=True,
            extracted_fields={"document_type": str(request.document_type)},
            missing_required_fields=["ocr_text"],
            rejection_reasons=[unavailable_reason],
            document_model_version=HANAH_TAX_OCR_MODEL_VERSION,
        )
    if ocr_result is None:
        return None

    text = ocr_result.combined_text()
    if not text:
        return None

    parser = build_parser_registry()[ocr_document_type]
    extracted = pipeline_extracted or parser.parse(ocr_result, request.file_name)
    extracted.quality_checks.update(document_checks)
    review_result = TaxDocumentReviewer().review([extracted])
    review_reasons = [finding.code for finding in review_result.findings]
    extracted_fields = {
        key: str(value)
        for key, value in extracted.fields.items()
        if value is not None and str(value).strip()
    }
    extracted_fields.update(_normalize_document_fields(request, text))
    missing_required_fields = _missing_required_document_fields(request, extracted_fields, text)
    hard_rejection_reasons = _document_rejection_reasons(
        request,
        missing_required_fields,
        text,
        ocr_confidence,
    )
    rejection_reasons = [
        *hard_rejection_reasons,
        *(reason for reason in review_reasons if reason not in hard_rejection_reasons),
    ]
    verification_status = _ocr_review_status(
        review_result.status,
        missing_required_fields,
        hard_rejection_reasons,
        ocr_confidence,
    )
    fraud_risk_score = _ocr_fraud_risk_score(request.fraud_signal_score, review_result.status)
    return TaxDocumentVerificationPrediction(
        verification_status=verification_status,
        ocr_confidence=ocr_confidence,
        fraud_risk_score=fraud_risk_score,
        risk_level=_document_risk_level(ocr_confidence, fraud_risk_score),
        manual_review_required=verification_status != "VERIFIED",
        extracted_fields=extracted_fields,
        missing_required_fields=missing_required_fields,
        rejection_reasons=rejection_reasons,
        document_model_version=HANAH_TAX_OCR_MODEL_VERSION,
    )


def _ocr_document_type(document_type: str) -> OcrDocumentType | None:
    mapping = {
        "RESIDENCE_CERTIFICATE": OcrDocumentType.RESIDENCY_CERTIFICATE,
        "APOSTILLE": OcrDocumentType.APOSTILLE,
        "TREATY_APPLICATION": OcrDocumentType.WITHHOLDING_TAX_FORM,
        "REDUCED_TAX_APPLICATION": OcrDocumentType.WITHHOLDING_TAX_FORM,
    }
    return mapping.get(document_type)


def _ocr_result_from_request(
    request: TaxDocumentVerificationRequest,
    ocr_document_type: OcrDocumentType,
) -> tuple[
    OCRResult | None,
    ExtractedDocument | None,
    float,
    str | None,
    dict[str, object],
]:
    if request.extracted_text.strip():
        return (
            OCRResult(pages=[OCRPage(page_number=1, raw_text=request.extracted_text.strip())]),
            None,
            request.ocr_confidence,
            None,
            {},
        )
    if not request.document_content_base64:
        return None, None, request.ocr_confidence, None, {}

    raw = _decode_bytes_payload(request.document_content_base64)
    if raw is None:
        return None, None, 0.0, "DOCUMENT_BASE64_INVALID", {}

    content_type = request.content_type.lower().split(";", 1)[0].strip()
    suffix = Path(request.file_name).suffix.lower()
    if content_type in TEXT_TAX_DOCUMENT_CONTENT_TYPES or suffix == ".txt":
        text = _decode_text_bytes(raw)
        if not text:
            return None, None, 0.0, "OCR_TEXT_EMPTY", {}
        return (
            OCRResult(pages=[OCRPage(page_number=1, raw_text=text)]),
            None,
            request.ocr_confidence,
            None,
            {},
        )

    if (
        content_type not in OCR_TAX_DOCUMENT_CONTENT_TYPES
        and suffix not in OCR_TAX_DOCUMENT_SUFFIXES
    ):
        return None, None, 0.0, "OCR_CONTENT_TYPE_UNSUPPORTED", {}

    return _run_real_tax_ocr(
        raw,
        suffix or _suffix_for_content_type(content_type),
        ocr_document_type,
        request.file_name,
    )


def _decode_bytes_payload(document_content_base64: str) -> bytes | None:
    if not document_content_base64:
        return None
    try:
        return base64.b64decode(document_content_base64, validate=True)
    except (binascii.Error, ValueError):
        return None


def _decode_text_payload(document_content_base64: str) -> str:
    raw = _decode_bytes_payload(document_content_base64)
    if raw is None:
        return ""
    return _decode_text_bytes(raw)


def _decode_text_bytes(raw: bytes) -> str:
    if b"\x00" in raw[:512]:
        return ""
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="ignore").strip()


def _run_real_tax_ocr(
    raw: bytes,
    suffix: str,
    ocr_document_type: OcrDocumentType,
    source_name: str,
) -> tuple[
    OCRResult | None,
    ExtractedDocument | None,
    float,
    str | None,
    dict[str, object],
]:
    suffix = suffix if suffix in OCR_TAX_DOCUMENT_SUFFIXES else ".bin"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="hanah-tax-ocr-",
            suffix=suffix,
            delete=False,
        ) as temp:
            temp.write(raw)
            temp_path = Path(temp.name)
        pipeline_result = TaxDocumentPipeline(
            ocr_engine=TesseractOCREngine(lang=_ocr_language(ocr_document_type)),
        ).process(
            ocr_document_type,
            temp_path,
            source_name=source_name,
        )
        return (
            pipeline_result.ocr_result,
            pipeline_result.extracted_document,
            pipeline_result.ocr_confidence,
            None,
            cast(
                dict[str, object],
                pipeline_result.extracted_document.quality_checks,
            ),
        )
    except RuntimeError:
        return None, None, 0.0, "OCR_ENGINE_UNAVAILABLE", {}
    except OSError:
        return None, None, 0.0, "OCR_INPUT_UNREADABLE", {}
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _ocr_language(document_type: OcrDocumentType) -> str:
    if document_type == OcrDocumentType.WITHHOLDING_TAX_FORM:
        return "kor+eng"
    return "eng"


def _suffix_for_content_type(content_type: str) -> str:
    mapping = {
        "application/pdf": ".pdf",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/tiff": ".tiff",
        "image/bmp": ".bmp",
    }
    return mapping.get(content_type, ".bin")


def _ocr_review_status(
    review_status: ReviewStatus,
    missing_required_fields: list[str],
    rejection_reasons: list[str],
    ocr_confidence: float,
) -> DocumentVerificationStatus:
    if rejection_reasons or review_status == ReviewStatus.REJECT:
        return "REJECTED"
    if (
        review_status == ReviewStatus.PASS
        and not missing_required_fields
        and ocr_confidence >= 0.75
    ):
        return "VERIFIED"
    return "PENDING"


def _ocr_fraud_risk_score(fraud_signal_score: float, review_status: ReviewStatus) -> float:
    if review_status in {ReviewStatus.REJECT, ReviewStatus.NEEDS_REVIEW}:
        return round(max(fraud_signal_score, 0.35), 4)
    return round(fraud_signal_score, 4)


def _normalize_document_fields(
    request: TaxDocumentVerificationRequest,
    ocr_text: str | None = None,
) -> dict[str, str]:
    fields = {
        key.strip().lower(): value.strip()
        for key, value in request.extracted_fields.items()
        if key.strip() and value.strip()
    }
    normalized_text = (ocr_text if ocr_text is not None else request.extracted_text).lower()
    fields.setdefault("document_type", request.document_type)
    if request.expected_residency_country and _country_present(
        normalized_text,
        request.expected_residency_country,
    ):
        country_code = request.expected_residency_country.upper()
        fields.setdefault("residency_country", country_code)
        fields.setdefault("residency_country_code", country_code)
    return fields


def _missing_required_document_fields(
    request: TaxDocumentVerificationRequest,
    extracted_fields: dict[str, str],
    ocr_text: str | None = None,
) -> list[str]:
    required_fields = ["document_type"]
    if request.document_type == "RESIDENCE_CERTIFICATE":
        required_fields.extend(
            [
                "taxpayer_name",
                "tin",
                "tax_year",
                "issue_date",
                "residency_country",
                "residency_country_code",
            ]
        )
    elif request.document_type == "APOSTILLE":
        required_fields.extend(
            [
                "issuing_country",
                "signed_by",
                "signer_capacity",
                "seal_owner",
                "issued_at",
                "issued_on",
                "issuing_authority",
                "certificate_number",
            ]
        )
    elif request.document_type in {"TREATY_APPLICATION", "REDUCED_TAX_APPLICATION"}:
        required_fields.extend(
            [
                "first_name",
                "last_name",
                "address",
                "tin",
                "residency_country",
                "residency_country_code",
                "dividend_tax_rate",
                "signature_date",
            ]
        )
    missing = [field for field in required_fields if field not in extracted_fields]
    normalized_text = (ocr_text if ocr_text is not None else request.extracted_text).lower()
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
    ocr_text: str | None = None,
    ocr_confidence: float | None = None,
) -> list[str]:
    reasons: list[str] = []
    effective_ocr_confidence = request.ocr_confidence if ocr_confidence is None else ocr_confidence
    if effective_ocr_confidence < 0.5:
        reasons.append("OCR_CONFIDENCE_TOO_LOW")
    if request.fraud_signal_score >= 0.7:
        reasons.append("HIGH_FORGERY_RISK")
    normalized_text = ocr_text if ocr_text is not None else request.extracted_text
    if not normalized_text.strip() and not request.extracted_fields:
        reasons.append("NO_EXTRACTED_CONTENT")
    if missing_required_fields and effective_ocr_confidence < 0.65:
        reasons.append("REQUIRED_FIELDS_UNREADABLE")
    return reasons


def _document_risk_level(ocr_confidence: float, fraud_signal_score: float) -> DocumentRiskLevel:
    if ocr_confidence < 0.65 or fraud_signal_score >= 0.5:
        return "HIGH"
    if ocr_confidence < 0.75 or fraud_signal_score > 0.2:
        return "MEDIUM"
    return "LOW"


def _document_verification_status(
    request: TaxDocumentVerificationRequest,
    missing_required_fields: list[str],
    rejection_reasons: list[str],
) -> DocumentVerificationStatus:
    if rejection_reasons:
        return "REJECTED"
    if missing_required_fields or request.ocr_confidence < 0.75 or request.fraud_signal_score > 0.2:
        return "PENDING"
    return "VERIFIED"


def _country_present(normalized_text: str, country: str) -> bool:
    country = country.upper()
    country_aliases = {
        "US": ("us", "usa", "united states", "미국"),
    }
    aliases = country_aliases.get(country, (country.lower(),))
    return any(alias in normalized_text for alias in aliases)


def _tax_case_type(request: TaxRefundStatusRequest) -> TaxCaseType:
    if request.tax_residency_country != "US":
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
    return round(gross_dividend * (DIVIDEND_DOMESTIC_WITHHOLDING_RATE - DIVIDEND_TREATY_LIMIT_RATE))


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
    return "한미 조세조약 CASE_01 요건을 충족하여 샌드박스 선지급 가능 상태입니다."
