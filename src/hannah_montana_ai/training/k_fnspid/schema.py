from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

PublishedPrecision = Literal["MINUTE", "DATE"]
MarketSession = Literal["PRE_MARKET", "REGULAR", "AFTER_CLOSE", "NON_TRADING", "UNKNOWN"]
EntityRelation = Literal["PRIMARY", "RELATED"]


@dataclass(frozen=True)
class CanonicalDocument:
    document_id: str
    provider: str
    source_type: str
    title: str
    snippet: str
    full_text: str
    source_url: str
    content_hash: str
    published_at_utc: str
    published_at_kst: str
    published_precision: PublishedPrecision
    market_session: MarketSession
    effective_trade_date: str
    event_cluster_id: str = ""
    collected_at: str = ""
    dataset_version: str = "k-fnspid-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DocumentEntity:
    document_id: str
    stock_code: str
    stock_name: str
    market: str
    relation: EntityRelation
    confidence: float
    evidence: tuple[str, ...] = field(default_factory=tuple)
    mapping_method: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = list(self.evidence)
        return payload


@dataclass(frozen=True)
class DailyPrice:
    stock_code: str
    trade_date: str
    market: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    adjusted_close: float
    volume: int
    trading_value: float


@dataclass(frozen=True)
class MarketImpact:
    document_id: str
    stock_code: str
    effective_trade_date: str
    abnormal_return_1d: float | None
    abnormal_return_3d: float | None
    abnormal_return_5d: float | None
    abnormal_volume_z: float | None
    volatility_shock: float | None
    materiality_score: float | None
    market_direction_1d: str
    importance: str
    label_confidence: float
    confounded: bool
    label_version: str = "k-fnspid-impact-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
