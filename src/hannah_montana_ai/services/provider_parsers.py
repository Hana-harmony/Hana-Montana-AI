from __future__ import annotations

import csv
import html
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from io import StringIO
from typing import Any, cast

from hannah_montana_ai.domain.schemas import (
    DocumentType,
    DocumentVerificationStatus,
    MarketType,
    StockOrderStatusRequest,
    TaxDocumentInput,
    TaxTransactionInput,
    TaxTransactionType,
    TradingSessionStatus,
)


class ProviderParseError(ValueError):
    pass


@dataclass(frozen=True)
class KisStockMasterRecord:
    stock_code: str
    stock_name: str
    stock_name_en: str
    market: MarketType
    issued_shares: int
    previous_close_price: int
    upper_limit_price: int
    lower_limit_price: int


@dataclass(frozen=True)
class KisRealtimeQuoteRecord:
    stock_code: str
    current_price: int
    dynamic_vi_activated: bool
    static_vi_activated: bool
    trading_session_status: TradingSessionStatus


@dataclass(frozen=True)
class KrxForeignHoldingRecord:
    stock_code: str
    foreign_owned_quantity: int
    foreign_ownership_rate: float
    foreign_limit_exhaustion_rate: float
    foreign_limit_quantity: int | None


def parse_kis_master_csv(payload: str) -> list[KisStockMasterRecord]:
    rows = csv.DictReader(StringIO(payload))
    return [parse_kis_master_row(row) for row in rows]


def parse_kis_master_row(row: Mapping[str, str]) -> KisStockMasterRecord:
    return KisStockMasterRecord(
        stock_code=_stock_code(_first(row, "stock_code", "종목코드", "pdno")),
        stock_name=_required_text(_first(row, "stock_name", "종목명", "prdt_name")),
        stock_name_en=_clean_text(_first(row, "stock_name_en", "영문명", "prdt_eng_name")),
        market=_market(_first(row, "market", "시장구분", "mket_id_cd")),
        issued_shares=_int(_first(row, "issued_shares", "발행주식수", "lstg_stqt")),
        previous_close_price=_int(_first(row, "previous_close_price", "전일종가", "stck_prpr")),
        upper_limit_price=_int(_first(row, "upper_limit_price", "상한가", "stck_mxpr")),
        lower_limit_price=_int(_first(row, "lower_limit_price", "하한가", "stck_llam")),
    )


def parse_kis_realtime_packet(payload: str | Mapping[str, Any]) -> KisRealtimeQuoteRecord:
    row = _mapping_payload(payload)
    return KisRealtimeQuoteRecord(
        stock_code=_stock_code(_first(row, "stock_code", "종목코드", "MKSC_SHRN_ISCD")),
        current_price=_int(_first(row, "current_price", "현재가", "STCK_PRPR")),
        dynamic_vi_activated=_yes(_first(row, "dynamic_vi_activated", "동적VI", "DYNM_VI_YN")),
        static_vi_activated=_yes(_first(row, "static_vi_activated", "정적VI", "STTC_VI_YN")),
        trading_session_status=_trading_session(
            _first(row, "trading_session_status", "체결구분", "TRHT_YN", "HTS_KOR_ISNM")
        ),
    )


def parse_krx_foreign_holding_row(row: Mapping[str, str]) -> KrxForeignHoldingRecord:
    return KrxForeignHoldingRecord(
        stock_code=_stock_code(_first(row, "stock_code", "종목코드", "ISU_SRT_CD")),
        foreign_owned_quantity=_int(_first(row, "foreign_owned_quantity", "외국인보유수량")),
        foreign_ownership_rate=_float(_first(row, "foreign_ownership_rate", "외국인보유율")),
        foreign_limit_exhaustion_rate=_float(
            _first(row, "foreign_limit_exhaustion_rate", "한도소진율")
        ),
        foreign_limit_quantity=_optional_int(
            _first(row, "foreign_limit_quantity", "외국인한도수량")
        ),
    )


def build_stock_order_status_request(
    *,
    master: KisStockMasterRecord,
    quote: KisRealtimeQuoteRecord,
    foreign_holding: KrxForeignHoldingRecord,
    foreign_limit_rate: float = 100.0,
    intraday_foreign_net_buy_quantity: int = 0,
    prediction_confidence_interval_percent: float = 0.04,
    local_currency: str = "KRW",
    local_fx_rate: float = 1.0,
) -> StockOrderStatusRequest:
    if master.stock_code != quote.stock_code or master.stock_code != foreign_holding.stock_code:
        raise ProviderParseError("종목코드가 master, quote, foreign_holding 사이에서 일치하지 않음")

    return StockOrderStatusRequest(
        stock_code=master.stock_code,
        stock_name=master.stock_name,
        stock_name_en=master.stock_name_en,
        market=master.market,
        issued_shares=master.issued_shares,
        foreign_owned_quantity=foreign_holding.foreign_owned_quantity,
        foreign_limit_rate=foreign_limit_rate,
        foreign_limit_quantity=foreign_holding.foreign_limit_quantity,
        intraday_foreign_net_buy_quantity=intraday_foreign_net_buy_quantity,
        prediction_confidence_interval_percent=prediction_confidence_interval_percent,
        current_price=quote.current_price,
        previous_close_price=master.previous_close_price,
        upper_limit_price=master.upper_limit_price,
        lower_limit_price=master.lower_limit_price,
        dynamic_vi_activated=quote.dynamic_vi_activated,
        static_vi_activated=quote.static_vi_activated,
        trading_session_status=quote.trading_session_status,
        local_currency=local_currency,
        local_fx_rate=local_fx_rate,
    )


def parse_tax_document_rows(rows: Sequence[Mapping[str, str]]) -> list[TaxDocumentInput]:
    return [
        TaxDocumentInput(
            document_type=_document_type(_first(row, "document_type", "서류유형")),
            file_name=_required_text(_first(row, "file_name", "파일명")),
            verification_status=_document_status(_first(row, "verification_status", "검증상태")),
            ocr_confidence=_float(_first(row, "ocr_confidence", "OCR신뢰도")),
            fraud_risk_score=_float(_first(row, "fraud_risk_score", "위변조위험도")),
        )
        for row in rows
    ]


def parse_tax_transaction_rows(rows: Sequence[Mapping[str, str]]) -> list[TaxTransactionInput]:
    return [
        TaxTransactionInput(
            transaction_type=_transaction_type(_first(row, "transaction_type", "거래유형")),
            gross_dividend_amount=_optional_int(_first(row, "gross_dividend_amount", "총배당금"))
            or 0,
            sell_proceeds=_optional_int(_first(row, "sell_proceeds", "총매도지급액")) or 0,
            capital_gain=_optional_int(_first(row, "capital_gain", "양도차익")) or 0,
            withheld_tax=_optional_int(_first(row, "withheld_tax", "기납부원천세")) or 0,
            listed_market_trade=_yes(
                _first(row, "listed_market_trade", "장내거래여부", default="Y")
            ),
            ownership_rate_percent=_float(_first(row, "ownership_rate_percent", "지분율")),
        )
        for row in rows
    ]


def _mapping_payload(payload: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(payload, str):
        stripped = payload.strip()
        if stripped.startswith("{"):
            loaded = json.loads(stripped)
            if not isinstance(loaded, dict):
                raise ProviderParseError("JSON payload는 객체여야 함")
            return loaded
        parts = stripped.split("|")
        if len(parts) < 5:
            raise ProviderParseError("KIS 구분자 패킷은 최소 5개 필드가 필요함")
        return {
            "stock_code": parts[0],
            "current_price": parts[1],
            "dynamic_vi_activated": parts[2],
            "static_vi_activated": parts[3],
            "trading_session_status": parts[4],
        }
    return payload


def _first(row: Mapping[str, Any], *keys: str, default: str = "") -> Any:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip() != "":
            return value
    return default


def _stock_code(value: Any) -> str:
    normalized = _clean_text(value).zfill(6)
    if len(normalized) != 6 or not normalized.isdigit():
        raise ProviderParseError(f"6자리 종목코드가 아님: {value}")
    return normalized


def _required_text(value: Any) -> str:
    normalized = _clean_text(value)
    if not normalized:
        raise ProviderParseError("필수 텍스트 값이 비어 있음")
    return normalized


def _clean_text(value: Any) -> str:
    return " ".join(html.unescape(str(value or "")).strip().split())


def _int(value: Any) -> int:
    normalized = _clean_text(value).replace(",", "")
    try:
        return int(float(normalized))
    except ValueError as exception:
        raise ProviderParseError(f"정수 변환 실패: {value}") from exception


def _optional_int(value: Any) -> int | None:
    if _clean_text(value) == "":
        return None
    return _int(value)


def _float(value: Any) -> float:
    normalized = _clean_text(value).replace(",", "").replace("%", "")
    try:
        return float(normalized)
    except ValueError as exception:
        raise ProviderParseError(f"실수 변환 실패: {value}") from exception


def _yes(value: Any) -> bool:
    return _clean_text(value).upper() in {"Y", "1", "TRUE", "T", "예", "단일가"}


def _market(value: Any) -> MarketType:
    normalized = _clean_text(value).upper()
    aliases = {
        "STK": "KOSPI",
        "KS": "KOSPI",
        "KOSPI": "KOSPI",
        "KSQ": "KOSDAQ",
        "KQ": "KOSDAQ",
        "KOSDAQ": "KOSDAQ",
        "KNX": "KONEX",
        "KONEX": "KONEX",
    }
    return cast(MarketType, aliases.get(normalized, "OTHER"))


def _trading_session(value: Any) -> TradingSessionStatus:
    normalized = _clean_text(value).upper()
    if normalized in {"SINGLE_PRICE", "단일가", "Y", "VI"}:
        return "SINGLE_PRICE"
    if normalized in {"PRE_OPEN", "장전"}:
        return "PRE_OPEN"
    if normalized in {"CLOSED", "장마감"}:
        return "CLOSED"
    return "REGULAR"


def _document_status(value: Any) -> DocumentVerificationStatus:
    normalized = _clean_text(value).upper()
    if normalized in {"VERIFIED", "완료", "승인"}:
        return "VERIFIED"
    if normalized in {"REJECTED", "거절", "반려"}:
        return "REJECTED"
    return "PENDING"


def _document_type(value: Any) -> DocumentType:
    normalized = _clean_text(value).upper()
    if normalized in {"RESIDENCE_CERTIFICATE", "거주자증명서"}:
        return "RESIDENCE_CERTIFICATE"
    if normalized in {"TREATY_APPLICATION", "제한세율신청서", "조세조약신청서"}:
        return "TREATY_APPLICATION"
    if normalized in {"PASSPORT", "여권"}:
        return "PASSPORT"
    return "OTHER"


def _transaction_type(value: Any) -> TaxTransactionType:
    normalized = _clean_text(value).upper()
    if normalized in {"DIVIDEND", "배당"}:
        return "DIVIDEND"
    if normalized in {"SELL", "매도", "양도"}:
        return "SELL"
    raise ProviderParseError(f"지원하지 않는 세무 거래유형: {value}")
