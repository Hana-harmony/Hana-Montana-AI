from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

from hannah_montana_ai.training.k_fnspid.schema import MarketSession, PublishedPrecision

KOREA_ZONE = ZoneInfo("Asia/Seoul")
MARKET_OPEN = time(9, 0)
MARKET_CLOSE = time(15, 30)


@dataclass(frozen=True)
class NormalizedPublicationTime:
    published_at_utc: str
    published_at_kst: str
    precision: PublishedPrecision
    market_session: MarketSession


def normalize_publication_time(value: str, trading_dates: set[date]) -> NormalizedPublicationTime:
    stripped = value.strip()
    if len(stripped) == 8 and stripped.isdigit():
        parsed_date = datetime.strptime(stripped, "%Y%m%d").date()
        local = datetime.combine(parsed_date, time.min, tzinfo=KOREA_ZONE)
        session: MarketSession = "UNKNOWN" if parsed_date in trading_dates else "NON_TRADING"
        return NormalizedPublicationTime(
            published_at_utc=local.astimezone(UTC).isoformat(),
            published_at_kst=local.isoformat(),
            precision="DATE",
            market_session=session,
        )

    parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    local = parsed.astimezone(KOREA_ZONE)
    if local.date() not in trading_dates:
        session = "NON_TRADING"
    elif local.time() < MARKET_OPEN:
        session = "PRE_MARKET"
    elif local.time() <= MARKET_CLOSE:
        session = "REGULAR"
    else:
        session = "AFTER_CLOSE"
    return NormalizedPublicationTime(
        published_at_utc=parsed.astimezone(UTC).isoformat(),
        published_at_kst=local.isoformat(),
        precision="MINUTE",
        market_session=session,
    )


def effective_trade_date(publication: NormalizedPublicationTime, trading_dates: list[date]) -> str:
    local_date = datetime.fromisoformat(publication.published_at_kst).date()
    if (
        publication.market_session in {"PRE_MARKET", "REGULAR", "UNKNOWN"}
        and local_date in trading_dates
    ):
        return local_date.isoformat()
    for candidate in trading_dates:
        if candidate > local_date:
            return candidate.isoformat()
    return ""
