from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

SourceType = Literal["NEWS", "DISCLOSURE"]
Sentiment = Literal["POSITIVE", "NEUTRAL", "NEGATIVE"]
Importance = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
MarketType = Literal["KOSPI", "KOSDAQ", "KONEX", "OTHER"]
PriceLimitStatus = Literal["UPPER", "LOWER", "NORMAL"]
ForeignLimitUsageStatus = Literal["NORMAL", "CAUTION", "LIMIT_REACHED"]
OrderAvailabilityIndicator = Literal["AVAILABLE", "CAUTION", "LIMITED"]
YesNoFlag = Literal["Y", "N"]
ViActivationStatus = YesNoFlag
TradingSessionStatus = Literal["REGULAR", "SINGLE_PRICE", "PRE_OPEN", "CLOSED"]
TaxCaseType = Literal["CASE_01", "CASE_REVIEW_REQUIRED"]
TaxRefundWorkflowStatus = Literal[
    "DOCUMENTS_PENDING",
    "REVIEW_REQUIRED",
    "NO_REFUND_AVAILABLE",
    "ELIGIBLE_FOR_INSTANT_PAYOUT",
    "QUARTERLY_REFUND_READY",
]
DocumentType = Literal["RESIDENCE_CERTIFICATE", "TREATY_APPLICATION", "PASSPORT", "OTHER"]
DocumentVerificationStatus = Literal["VERIFIED", "PENDING", "REJECTED"]
DocumentRiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
TaxTransactionType = Literal["DIVIDEND", "SELL"]


class StockCandidate(BaseModel):
    stock_code: str = Field(pattern=r"^\d{6}$")
    stock_name: str = Field(min_length=1, max_length=80)
    stock_name_en: str = Field(min_length=1, max_length=120)
    aliases: list[str] = Field(default_factory=list, max_length=20)


class AlertAnalysisRequest(BaseModel):
    source_type: SourceType
    title: str = Field(min_length=1, max_length=300)
    snippet: str = Field(default="", max_length=1000)
    original_url: HttpUrl
    stock_universe: list[StockCandidate] = Field(default_factory=list, max_length=50)


class AlertAnalysisResponse(BaseModel):
    stock_code: str | None
    stock_name: str | None
    source_type: SourceType
    original_title: str
    summary: str
    event_tags: list[str]
    sentiment: Sentiment
    importance: Importance
    related_stocks: list[str]
    holder_target: bool
    watchlist_target: bool
    duplicate_key: str
    model_version: str
    event_confidence: float = Field(ge=0.0, le=1.0)
    sentiment_confidence: float = Field(ge=0.0, le=1.0)
    importance_confidence: float = Field(ge=0.0, le=1.0)
    stock_match_confidence: float = Field(ge=0.0, le=1.0)


class StockOrderStatusRequest(BaseModel):
    stock_code: str = Field(pattern=r"^\d{6}$")
    stock_name: str = Field(min_length=1, max_length=80)
    stock_name_en: str = Field(default="", max_length=120)
    market: MarketType = "KOSPI"
    issued_shares: int = Field(gt=0)
    foreign_owned_quantity: int = Field(ge=0)
    foreign_limit_rate: float = Field(default=100.0, ge=0.0, le=100.0)
    foreign_limit_quantity: int | None = Field(default=None, ge=0)
    intraday_foreign_net_buy_quantity: int = 0
    prediction_confidence_interval_percent: float = Field(default=0.04, ge=0.0, le=10.0)
    current_price: int = Field(ge=0)
    previous_close_price: int = Field(ge=0)
    upper_limit_price: int = Field(ge=0)
    lower_limit_price: int = Field(ge=0)
    dynamic_vi_activated: bool = False
    static_vi_activated: bool = False
    trading_session_status: TradingSessionStatus = "REGULAR"
    base_currency: str = Field(default="KRW", min_length=3, max_length=3)
    local_currency: str = Field(default="KRW", min_length=3, max_length=3)
    local_fx_rate: float = Field(default=1.0, gt=0.0)


class StockOrderStatusResponse(BaseModel):
    stock_code: str
    stock_name: str
    stock_name_en: str
    market: MarketType
    issued_shares: int
    current_price: int
    previous_close_price: int
    upper_limit_price: int
    lower_limit_price: int
    local_currency: str
    local_current_price: float
    foreign_owned_quantity: int
    foreign_limit_quantity: int
    foreign_limit_remaining_quantity: int
    foreign_ownership_rate: float
    foreign_limit_exhaustion_rate: float
    fx_predicted_rate_min: float
    fx_predicted_rate_max: float
    foreign_limit_usage_status: ForeignLimitUsageStatus
    foreign_limit_warning: bool
    vi_activation_status: ViActivationStatus
    vi_activation_reason: list[str]
    price_limit_status: PriceLimitStatus
    immediate_execution_available: bool
    buy_order_available: bool
    sell_order_available: bool
    order_availability_indicator: OrderAvailabilityIndicator
    order_restriction_reasons: list[str]
    order_guidance_message: str
    prediction_model_version: str
    trading_state_model_version: str
    data_source: str


class ForeignOwnershipHistoryPoint(BaseModel):
    base_date: date
    foreign_owned_quantity: int = Field(ge=0)
    foreign_ownership_rate: float = Field(ge=0.0, le=100.0)
    foreign_limit_quantity: int = Field(gt=0)
    foreign_limit_exhaustion_rate: float = Field(ge=0.0)


class ForeignOwnershipTimeseriesPredictionRequest(BaseModel):
    stock_code: str = Field(pattern=r"^\d{6}$")
    side: Literal["BUY", "SELL"] = "BUY"
    quantity: int = Field(default=0, ge=0)
    foreign_owned_quantity: int = Field(ge=0)
    foreign_ownership_rate: float = Field(ge=0.0, le=100.0)
    foreign_limit_quantity: int = Field(gt=0)
    foreign_limit_exhaustion_rate: float = Field(ge=0.0)
    base_date: date
    observed_intraday_volume: int = Field(default=0, ge=0)
    history: list[ForeignOwnershipHistoryPoint] = Field(default_factory=list, max_length=90)


class ForeignOwnershipTimeseriesPredictionResponse(BaseModel):
    stock_code: str
    min_foreign_limit_exhaustion_rate: float
    base_foreign_limit_exhaustion_rate: float
    max_foreign_limit_exhaustion_rate: float
    order_impact_rate: float
    intraday_uncertainty_rate: float
    observed_intraday_volume: int
    trend_daily_change_rate: float
    history_observation_count: int
    history_window_days: int
    base_date: date
    calculated_at: datetime
    confidence_level: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    model_version: str
    source: str


class IntelligenceEventRequest(AlertAnalysisRequest):
    target_language: Literal["en"] = "en"
    provider: str = Field(default="", max_length=80)
    published_at: str = Field(default="", max_length=80)


class FinancialGlossaryTerm(BaseModel):
    source_term: str = Field(min_length=1, max_length=80)
    normalized_term: str = Field(min_length=1, max_length=80)
    english_term: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=40)


class IntelligenceEventResponse(BaseModel):
    alert_id: str
    duplicate_key: str
    stock_code: str | None
    stock_name: str | None
    news_disclosure_type: SourceType
    original_title: str
    translated_title: str
    summary: str
    translated_summary: str
    sentiment: Sentiment
    importance: Importance
    event_tag: str
    event_tags: list[str]
    related_stocks: list[str]
    is_holder_target: bool
    is_watchlist_target: bool
    glossary_terms: list[FinancialGlossaryTerm]
    translation_quality_flags: list[str]
    original_url: HttpUrl
    provider: str
    published_at: str
    translation_provider: str
    translation_model_version: str
    translation_status: Literal["TRANSLATED", "SOURCE_LANGUAGE_FALLBACK"]
    model_version: str
    event_confidence: float = Field(ge=0.0, le=1.0)
    sentiment_confidence: float = Field(ge=0.0, le=1.0)
    importance_confidence: float = Field(ge=0.0, le=1.0)
    stock_match_confidence: float = Field(ge=0.0, le=1.0)
    data_source: str


class TaxDocumentInput(BaseModel):
    document_type: DocumentType
    file_name: str = Field(min_length=1, max_length=180)
    verification_status: DocumentVerificationStatus
    ocr_confidence: float = Field(ge=0.0, le=1.0)
    fraud_risk_score: float = Field(ge=0.0, le=1.0)


class TaxDocumentVerificationRequest(BaseModel):
    document_type: DocumentType
    file_name: str = Field(min_length=1, max_length=180)
    extracted_text: str = Field(default="", max_length=8000)
    ocr_confidence: float = Field(ge=0.0, le=1.0)
    fraud_signal_score: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_investor_id: str | None = Field(default=None, max_length=80)
    expected_residency_country: str | None = Field(default=None, min_length=2, max_length=2)
    extracted_fields: dict[str, str] = Field(default_factory=dict, max_length=30)


class TaxDocumentVerificationResponse(BaseModel):
    document_type: DocumentType
    file_name: str
    verification_status: DocumentVerificationStatus
    ocr_confidence: float
    fraud_risk_score: float
    risk_level: DocumentRiskLevel
    manual_review_required: bool
    extracted_fields: dict[str, str]
    missing_required_fields: list[str]
    rejection_reasons: list[str]
    document_model_version: str


class TaxTransactionInput(BaseModel):
    transaction_type: TaxTransactionType
    gross_dividend_amount: int = Field(default=0, ge=0)
    sell_proceeds: int = Field(default=0, ge=0)
    capital_gain: int = 0
    withheld_tax: int = Field(default=0, ge=0)
    listed_market_trade: bool = True
    ownership_rate_percent: float = Field(default=0.0, ge=0.0, le=100.0)


class TaxRefundStatusRequest(BaseModel):
    investor_id: str = Field(min_length=1, max_length=80)
    tax_residency_country: str = Field(default="US", min_length=2, max_length=2)
    tax_year: str = Field(min_length=4, max_length=20)
    documents: list[TaxDocumentInput] = Field(default_factory=list, max_length=20)
    transactions: list[TaxTransactionInput] = Field(default_factory=list, max_length=500)
    instant_payout_requested: bool = True
    instant_payout_fee_rate: float = Field(default=3.0, ge=0.0, le=30.0)


class TaxRefundStatusResponse(BaseModel):
    investor_id: str
    tax_year: str
    tax_case_type: TaxCaseType
    refund_workflow_status: TaxRefundWorkflowStatus
    government_verification_ref: str
    document_verification_status: DocumentVerificationStatus
    required_documents_completed: bool
    total_withheld_tax: int
    dividend_refund_amount: int
    capital_gains_refund_amount: int
    eligible_refund_amount: int
    national_tax_refund_amount: int
    local_tax_refund_amount: int
    instant_payout_fee_rate: float
    instant_payout_fee_amount: int
    instant_payout_amount: int
    compliance_sandbox_flag: YesNoFlag
    clawback_required_if_rejected: bool
    required_next_actions: list[str]
    risk_disclosure_message: str
    tax_model_version: str
    document_model_version: str
    review_message: str
