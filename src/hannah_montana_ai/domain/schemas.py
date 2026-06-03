from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

SourceType = Literal["NEWS", "DISCLOSURE"]
Sentiment = Literal["POSITIVE", "NEUTRAL", "NEGATIVE"]
Importance = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


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
