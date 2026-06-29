from __future__ import annotations

import csv
import json
import math
import os
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    load_stock_universe,
)

GLOBAL_PEER_SCHEMA_VERSION = "global-peer-matcher/v1"
GLOBAL_PEER_MODEL_VERSION_PREFIX = "global-peer-tfidf"
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
SEC_TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
NASDAQ_QUOTE_SUMMARY_URL = "https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks"
NAVER_STOCK_INTEGRATION_URL = "https://m.stock.naver.com/api/stock/{stock_code}/integration"
OPEN_DART_FINANCIAL_URL = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
KRX_OPEN_API_BASE_URL = "https://data-dbg.krx.co.kr"
KRX_DAILY_TRADE_PATHS = (
    "/svc/apis/sto/stk_bydd_trd",
    "/svc/apis/sto/ksq_bydd_trd",
    "/svc/apis/sto/knx_bydd_trd",
)


@dataclass(frozen=True)
class UsStockUniverseEntry:
    ticker: str
    company_name: str
    exchange: str
    etf: bool
    test_issue: bool
    security_type: str


@dataclass(frozen=True)
class GlobalPeerFundamentals:
    market: str
    identifier: str
    fiscal_year: int | None
    market_cap_usd: float | None
    revenue_usd: float | None
    operating_income_usd: float | None
    net_income_usd: float | None
    currency: str
    source: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CompanyPeerProfile:
    identifier: str
    display_name: str
    market: str
    country: str
    exchange: str
    profile_text: str
    business_tags: tuple[str, ...]
    sector: str
    industry: str
    business_model: str
    scale_bucket: str
    fiscal_year: int | None
    market_cap_usd: float | None
    revenue_usd: float | None
    operating_income_usd: float | None
    net_income_usd: float | None
    financial_data_source: str
    financial_feature_vector: tuple[float, ...]
    eligible_peer: bool
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "business_tags": list(self.business_tags),
            "financial_feature_vector": list(self.financial_feature_vector),
        }


@dataclass(frozen=True)
class PeerTrainingResult:
    report: dict[str, object]


@dataclass(frozen=True)
class PeerAnchor:
    profile_text: str
    business_tags: tuple[str, ...]
    sector: str
    industry: str
    business_model: str
    scale_bucket: str
    market_cap_usd: float | None = None
    revenue_usd: float | None = None
    operating_income_usd: float | None = None
    net_income_usd: float | None = None
    fiscal_year: int | None = None
    financial_data_source: str = "CURATED_ANCHOR"
    positioning_title: str = ""
    preferred_peer_ticker: str = ""
    headline_template: str = ""
    summary: str = ""


KOREA_ANCHORS: dict[str, PeerAnchor] = {
    "196170": PeerAnchor(
        profile_text=(
            "Alteogen biotech platform hyaluronidase drug delivery technology "
            "converts intravenous biologics into subcutaneous formulation licensing "
            "milestone royalty big pharma"
        ),
        business_tags=("biotech platform", "drug delivery", "royalty licensing"),
        sector="Health Care",
        industry="Biotechnology",
        business_model="Biotech platform licensing",
        scale_bucket="MID_CAP",
        market_cap_usd=9_800_000_000,
        revenue_usd=230_000_000,
        operating_income_usd=50_000_000,
        net_income_usd=42_000_000,
        fiscal_year=2025,
        positioning_title="Global Biotech Platform Leader",
        preferred_peer_ticker="HALO",
        headline_template=(
            "{stock_name_en} Is The '{peer_name}' of South Korea — "
            "A Global Biotech Platform Leader"
        ),
        summary=(
            "Alteogen is a high-margin Biotech Platform provider. Instead of developing "
            "its own new drugs, it licenses out its proprietary drug-delivery technology "
            "to global Big Pharma, securing long-term milestone and royalty fees."
        ),
    ),
}

US_ANCHORS: dict[str, PeerAnchor] = {
    "HALO": PeerAnchor(
        profile_text=(
            "Halozyme Therapeutics biotech platform hyaluronidase drug delivery "
            "subcutaneous formulation licensing royalty milestone big pharma"
        ),
        business_tags=("biotech platform", "drug delivery", "royalty licensing"),
        sector="Health Care",
        industry="Biotechnology",
        business_model="Biotech platform licensing",
        scale_bucket="MID_CAP",
        market_cap_usd=7_900_000_000,
        revenue_usd=829_000_000,
        operating_income_usd=514_000_000,
        net_income_usd=399_000_000,
        fiscal_year=2025,
        positioning_title="Biotech Platform",
    ),
}

_SECURITY_SUFFIX_PATTERN = re.compile(
    r"\b(common stock|ordinary shares|class [a-z] ordinary shares|american depositary"
    r" shares|ads|adr|inc\.?|corp\.?|corporation|co\.?|company|ltd\.?|limited|plc|sa)\b",
    re.IGNORECASE,
)


def sync_us_stock_universe(output_path: Path) -> list[UsStockUniverseEntry]:
    entries = _parse_nasdaq_listed(_download_symbol_directory(NASDAQ_LISTED_URL))
    entries.extend(_parse_other_listed(_download_symbol_directory(OTHER_LISTED_URL)))
    entries = sorted(_dedupe_us_entries(entries), key=lambda stock: stock.ticker)
    write_us_stock_universe(output_path, entries)
    return entries


def fetch_sec_ticker_cik_map() -> dict[str, str]:
    payload = _download_json(SEC_TICKER_CIK_URL)
    return {
        str(row["ticker"]).upper(): f"{int(row['cik_str']):010d}"
        for row in payload.values()
        if isinstance(row, dict) and row.get("ticker") and row.get("cik_str")
    }


def fetch_sec_annual_fundamentals(
    ticker: str,
    cik: str,
    fiscal_year: int,
) -> GlobalPeerFundamentals | None:
    payload = _download_json(SEC_COMPANY_FACTS_URL.format(cik=cik))
    root_facts = payload.get("facts", {})
    if not isinstance(root_facts, dict):
        return None
    facts = root_facts.get("us-gaap", {})
    if not isinstance(facts, dict):
        return None
    revenue = _sec_fact_value(
        facts,
        fiscal_year,
        (
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
        ),
    )
    operating_income = _sec_fact_value(
        facts,
        fiscal_year,
        ("OperatingIncomeLoss",),
    )
    net_income = _sec_fact_value(
        facts,
        fiscal_year,
        ("NetIncomeLoss", "ProfitLoss"),
    )
    if revenue is None and operating_income is None and net_income is None:
        return None
    return GlobalPeerFundamentals(
        market="US",
        identifier=ticker.upper(),
        fiscal_year=fiscal_year,
        market_cap_usd=None,
        revenue_usd=revenue,
        operating_income_usd=operating_income,
        net_income_usd=net_income,
        currency="USD",
        source="SEC_COMPANYFACTS",
    )


def fetch_nasdaq_market_cap_usd(ticker: str) -> float | None:
    payload = _download_nasdaq_json(NASDAQ_QUOTE_SUMMARY_URL.format(ticker=ticker.upper()))
    data = payload.get("data", {})
    if not isinstance(data, dict):
        return None
    summary_data = data.get("summaryData", {})
    if not isinstance(summary_data, dict):
        return None
    market_cap = summary_data.get("MarketCap", {})
    if not isinstance(market_cap, dict):
        return None
    return _parse_optional_float(str(market_cap.get("value", "")))


def fetch_naver_korea_market_cap_usd(
    stock_code: str,
    krw_usd_rate: float,
) -> float | None:
    payload = _download_naver_json(NAVER_STOCK_INTEGRATION_URL.format(stock_code=stock_code))
    total_infos = payload.get("totalInfos", [])
    if not isinstance(total_infos, list):
        return None
    for item in total_infos:
        if not isinstance(item, dict):
            continue
        if item.get("code") == "marketValue" or item.get("key") == "시총":
            market_cap_krw = _parse_korean_market_value_krw(str(item.get("value", "")))
            return None if market_cap_krw is None else market_cap_krw * krw_usd_rate
    return None


def fetch_open_dart_annual_fundamentals(
    api_key: str,
    stock_code: str,
    corp_code: str,
    fiscal_year: int,
    krw_usd_rate: float = 0.00072,
) -> GlobalPeerFundamentals | None:
    for statement_type in ("CFS", "OFS"):
        payload = _download_json(
            f"{OPEN_DART_FINANCIAL_URL}?{urlencode({
                'crtfc_key': api_key,
                'corp_code': corp_code,
                'bsns_year': str(fiscal_year),
                'reprt_code': '11011',
                'fs_div': statement_type,
            })}"
        )
        rows = payload.get("list", [])
        if isinstance(rows, list) and rows:
            revenue = _open_dart_account_value(
                rows,
                ("ifrs-full_Revenue", "ifrs-full_RevenueFromContractsWithCustomers"),
                ("수익(매출액)", "매출액", "영업수익"),
            )
            operating_income = _open_dart_account_value(
                rows,
                ("dart_OperatingIncomeLoss", "ifrs-full_ProfitLossFromOperatingActivities"),
                ("영업이익", "영업손실"),
            )
            net_income = _open_dart_account_value(
                rows,
                ("ifrs-full_ProfitLoss",),
                ("당기순이익", "당기순손실", "분기순이익", "연결당기순이익"),
            )
            if revenue is None and operating_income is None and net_income is None:
                return None
            return GlobalPeerFundamentals(
                market="KR",
                identifier=stock_code,
                fiscal_year=fiscal_year,
                market_cap_usd=None,
                revenue_usd=_convert_krw_to_usd(revenue, krw_usd_rate),
                operating_income_usd=_convert_krw_to_usd(operating_income, krw_usd_rate),
                net_income_usd=_convert_krw_to_usd(net_income, krw_usd_rate),
                currency="USD",
                source=f"OPEN_DART_FNLTT_SINGLE_ACCOUNT_ALL_{statement_type}",
            )
    return None


def fetch_krx_market_caps_usd(
    auth_key: str,
    base_date: str,
    krw_usd_rate: float,
    base_url: str = KRX_OPEN_API_BASE_URL,
) -> dict[str, float]:
    market_caps: dict[str, float] = {}
    for path in KRX_DAILY_TRADE_PATHS:
        payload = _download_krx_json(
            url=f"{base_url}{path}?{urlencode({'basDd': base_date})}",
            auth_key=auth_key,
        )
        rows = payload.get("OutBlock_1", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            stock_code = str(row.get("ISU_SRT_CD", "")).strip()
            market_cap_krw = _parse_optional_float(str(row.get("MKTCAP", "")))
            if stock_code and market_cap_krw:
                market_caps[stock_code] = market_cap_krw * krw_usd_rate
    return market_caps


def load_us_stock_universe(path: Path) -> list[UsStockUniverseEntry]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as file:
        return [
            UsStockUniverseEntry(
                ticker=row["ticker"].strip(),
                company_name=row["company_name"].strip(),
                exchange=row["exchange"].strip(),
                etf=row["etf"].strip().upper() == "Y",
                test_issue=row["test_issue"].strip().upper() == "Y",
                security_type=row["security_type"].strip(),
            )
            for row in csv.DictReader(file)
        ]


def load_global_peer_fundamentals(path: Path) -> dict[tuple[str, str], GlobalPeerFundamentals]:
    if not path.exists():
        return {}
    fundamentals: dict[tuple[str, str], GlobalPeerFundamentals] = {}
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            market = row["market"].strip().upper()
            identifier = row["identifier"].strip().upper()
            fundamentals[(market, identifier)] = GlobalPeerFundamentals(
                market=market,
                identifier=identifier,
                fiscal_year=_parse_optional_int(row.get("fiscal_year", "")),
                market_cap_usd=_parse_optional_float(row.get("market_cap_usd", "")),
                revenue_usd=_parse_optional_float(row.get("revenue_usd", "")),
                operating_income_usd=_parse_optional_float(row.get("operating_income_usd", "")),
                net_income_usd=_parse_optional_float(row.get("net_income_usd", "")),
                currency=row.get("currency", "USD").strip().upper() or "USD",
                source=row.get("source", "").strip(),
            )
    return fundamentals


def write_global_peer_fundamentals(
    path: Path,
    rows: Sequence[GlobalPeerFundamentals],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "market",
                "identifier",
                "fiscal_year",
                "market_cap_usd",
                "revenue_usd",
                "operating_income_usd",
                "net_income_usd",
                "currency",
                "source",
            ],
        )
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (item.market, item.identifier)):
            writer.writerow(
                {
                    "market": row.market,
                    "identifier": row.identifier,
                    "fiscal_year": row.fiscal_year or "",
                    "market_cap_usd": _format_optional_float(row.market_cap_usd),
                    "revenue_usd": _format_optional_float(row.revenue_usd),
                    "operating_income_usd": _format_optional_float(row.operating_income_usd),
                    "net_income_usd": _format_optional_float(row.net_income_usd),
                    "currency": row.currency,
                    "source": row.source,
                }
            )


def write_us_stock_universe(path: Path, entries: Sequence[UsStockUniverseEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["ticker", "company_name", "exchange", "etf", "test_issue", "security_type"],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "ticker": entry.ticker,
                    "company_name": entry.company_name,
                    "exchange": entry.exchange,
                    "etf": "Y" if entry.etf else "N",
                    "test_issue": "Y" if entry.test_issue else "N",
                    "security_type": entry.security_type,
                }
            )


def train_global_peer_model(
    korea_stock_universe_path: Path,
    us_stock_universe_path: Path,
    fundamentals_path: Path,
    model_path: Path,
    report_path: Path,
) -> PeerTrainingResult:
    korea_universe = load_stock_universe(korea_stock_universe_path)
    us_universe = load_us_stock_universe(us_stock_universe_path)
    fundamentals = load_global_peer_fundamentals(fundamentals_path)
    if len(korea_universe) < 3_000:
        raise ValueError("global peer training requires the full Korean stock universe")
    if len(us_universe) < 5_000:
        raise ValueError("global peer training requires the full United States stock universe")

    korea_profiles = [build_korea_profile(stock, fundamentals) for stock in korea_universe]
    us_profiles = [build_us_profile(stock, fundamentals) for stock in us_universe]
    eligible_us_profiles = [profile for profile in us_profiles if profile.eligible_peer]
    if not eligible_us_profiles:
        raise ValueError("global peer training requires at least one eligible US peer")

    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        lowercase=True,
        strip_accents="unicode",
    )
    corpus = [profile.profile_text for profile in [*korea_profiles, *us_profiles]]
    vectorizer.fit(corpus)
    eligible_us_matrix = vectorizer.transform(
        [profile.profile_text for profile in eligible_us_profiles]
    )
    eligible_us_financial_matrix = np.array(
        [profile.financial_feature_vector for profile in eligible_us_profiles],
        dtype=float,
    )
    trained_at = datetime.now(UTC).isoformat()
    version = f"{GLOBAL_PEER_MODEL_VERSION_PREFIX}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "schema_version": GLOBAL_PEER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "vectorizer": vectorizer,
        "eligible_us_matrix": eligible_us_matrix,
        "eligible_us_financial_matrix": eligible_us_financial_matrix,
        "eligible_us_profiles": [profile.to_dict() for profile in eligible_us_profiles],
        "korea_profiles": {profile.identifier: profile.to_dict() for profile in korea_profiles},
        "korea_anchors": _anchors_to_payload(KOREA_ANCHORS),
        "us_anchors": _anchors_to_payload(US_ANCHORS),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)

    report = build_global_peer_training_report(
        version=version,
        trained_at=trained_at,
        korea_stock_universe_path=korea_stock_universe_path,
        us_stock_universe_path=us_stock_universe_path,
        fundamentals_path=fundamentals_path,
        model_path=model_path,
        korea_profiles=korea_profiles,
        us_profiles=us_profiles,
        eligible_us_profiles=eligible_us_profiles,
        vectorizer=vectorizer,
        eligible_us_matrix=eligible_us_matrix,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return PeerTrainingResult(report=report)


def build_global_peer_training_report(
    version: str,
    trained_at: str,
    korea_stock_universe_path: Path,
    us_stock_universe_path: Path,
    fundamentals_path: Path,
    model_path: Path,
    korea_profiles: Sequence[CompanyPeerProfile],
    us_profiles: Sequence[CompanyPeerProfile],
    eligible_us_profiles: Sequence[CompanyPeerProfile],
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
) -> dict[str, object]:
    anchor_evaluation = evaluate_anchor_pairs(vectorizer, eligible_us_matrix, eligible_us_profiles)
    tag_distribution = Counter(
        tag for profile in [*korea_profiles, *us_profiles] for tag in profile.business_tags
    )
    korea_fundamental_count = sum(1 for profile in korea_profiles if profile.financial_data_source)
    us_fundamental_count = sum(1 for profile in us_profiles if profile.financial_data_source)
    all_profiles = [*korea_profiles, *us_profiles]
    minimum_korea_universe_count = 3_000
    actual_korea_universe_count = len(korea_profiles)
    minimum_us_universe_count = 5_000
    actual_us_universe_count = len(us_profiles)
    minimum_anchor_top1_accuracy = 1.0
    raw_anchor_top1_accuracy = anchor_evaluation["top1_accuracy"]
    if not isinstance(raw_anchor_top1_accuracy, int | float):
        raise TypeError("anchor top1 accuracy must be numeric")
    actual_anchor_top1_accuracy = float(raw_anchor_top1_accuracy)
    coverage_gate: dict[str, object] = {
        "minimum_korea_universe_count": minimum_korea_universe_count,
        "actual_korea_universe_count": actual_korea_universe_count,
        "minimum_us_universe_count": minimum_us_universe_count,
        "actual_us_universe_count": actual_us_universe_count,
        "minimum_anchor_top1_accuracy": minimum_anchor_top1_accuracy,
        "actual_anchor_top1_accuracy": actual_anchor_top1_accuracy,
    }
    coverage_gate["status"] = (
        "pass"
        if actual_korea_universe_count >= minimum_korea_universe_count
        and actual_us_universe_count >= minimum_us_universe_count
        and actual_anchor_top1_accuracy >= minimum_anchor_top1_accuracy
        else "fail"
    )
    return {
        "schema_version": GLOBAL_PEER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "korea_stock_universe_path": _report_path(korea_stock_universe_path),
        "us_stock_universe_path": _report_path(us_stock_universe_path),
        "fundamentals_path": _report_path(fundamentals_path),
        "model_path": _report_path(model_path),
        "korea_universe_count": len(korea_profiles),
        "us_universe_count": len(us_profiles),
        "korea_fundamental_coverage_count": korea_fundamental_count,
        "us_fundamental_coverage_count": us_fundamental_count,
        "fundamental_field_coverage": {
            "market_cap_usd": sum(1 for profile in all_profiles if profile.market_cap_usd),
            "revenue_usd": sum(1 for profile in all_profiles if profile.revenue_usd is not None),
            "operating_income_usd": sum(
                1 for profile in all_profiles if profile.operating_income_usd is not None
            ),
            "net_income_usd": sum(
                1 for profile in all_profiles if profile.net_income_usd is not None
            ),
        },
        "eligible_us_peer_count": len(eligible_us_profiles),
        "tag_distribution": dict(sorted(tag_distribution.items())),
        "anchor_evaluation": anchor_evaluation,
        "coverage_gate": coverage_gate,
    }


def evaluate_anchor_pairs(
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
    eligible_us_profiles: Sequence[CompanyPeerProfile],
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    hits = 0
    for stock_code, anchor in KOREA_ANCHORS.items():
        query_vector = vectorizer.transform([anchor.profile_text])
        similarities = cosine_similarity(query_vector, eligible_us_matrix)[0]
        best_index = int(similarities.argmax())
        best_profile = eligible_us_profiles[best_index]
        hit = best_profile.identifier == anchor.preferred_peer_ticker
        hits += 1 if hit else 0
        rows.append(
            {
                "stock_code": stock_code,
                "expected_peer_ticker": anchor.preferred_peer_ticker,
                "predicted_peer_ticker": best_profile.identifier,
                "score": round(float(similarities[best_index]), 6),
                "hit": hit,
            }
        )
    return {
        "sample_count": len(rows),
        "top1_accuracy": hits / len(rows) if rows else 0.0,
        "rows": rows,
    }


def build_korea_profile(
    stock: StockUniverseEntry,
    fundamentals: dict[tuple[str, str], GlobalPeerFundamentals] | None = None,
) -> CompanyPeerProfile:
    anchor = KOREA_ANCHORS.get(stock.stock_code)
    fundamental = _fundamental_for("KR", stock.stock_code, anchor, fundamentals)
    stock_name_en = stock.stock_name_en or _english_name_fallback(stock)
    inferred_tags = tuple(infer_business_tags(stock.stock_name, stock_name_en))
    tags = anchor.business_tags if anchor else inferred_tags
    sector = anchor.sector if anchor else infer_sector(tags)
    industry = anchor.industry if anchor else infer_industry(tags)
    business_model = anchor.business_model if anchor else infer_business_model(tags)
    scale_bucket = derive_scale_bucket(fundamental.market_cap_usd)
    if scale_bucket == "UNKNOWN" and anchor:
        scale_bucket = anchor.scale_bucket
    financial_tokens = financial_profile_tokens(fundamental)
    base_text = " ".join(
        value
        for value in [
            stock.stock_code,
            stock.stock_name,
            stock_name_en,
            stock.market,
            " ".join(stock.aliases),
            anchor.profile_text if anchor else "",
            " ".join(tags),
            sector,
            industry,
            business_model,
            scale_bucket,
            " ".join(financial_tokens),
        ]
        if value
    )
    return CompanyPeerProfile(
        identifier=stock.stock_code,
        display_name=stock_name_en,
        market=stock.market or "KOREA",
        country="KR",
        exchange=stock.market or "KOREA",
        profile_text=normalize_profile_text(base_text),
        business_tags=tags,
        sector=sector,
        industry=industry,
        business_model=business_model,
        scale_bucket=scale_bucket,
        fiscal_year=fundamental.fiscal_year,
        market_cap_usd=fundamental.market_cap_usd,
        revenue_usd=fundamental.revenue_usd,
        operating_income_usd=fundamental.operating_income_usd,
        net_income_usd=fundamental.net_income_usd,
        financial_data_source=fundamental.source,
        financial_feature_vector=build_financial_feature_vector(fundamental),
        eligible_peer=False,
        source="KOREA_STOCK_UNIVERSE",
    )


def build_us_profile(
    stock: UsStockUniverseEntry,
    fundamentals: dict[tuple[str, str], GlobalPeerFundamentals] | None = None,
) -> CompanyPeerProfile:
    anchor = US_ANCHORS.get(stock.ticker)
    fundamental = _fundamental_for("US", stock.ticker, anchor, fundamentals)
    cleaned_name = clean_security_name(stock.company_name)
    inferred_tags = tuple(infer_business_tags(cleaned_name, cleaned_name))
    tags = anchor.business_tags if anchor else inferred_tags
    sector = anchor.sector if anchor else infer_sector(tags)
    industry = anchor.industry if anchor else infer_industry(tags)
    business_model = anchor.business_model if anchor else infer_business_model(tags)
    scale_bucket = derive_scale_bucket(fundamental.market_cap_usd)
    if scale_bucket == "UNKNOWN" and anchor:
        scale_bucket = anchor.scale_bucket
    financial_tokens = financial_profile_tokens(fundamental)
    base_text = " ".join(
        value
        for value in [
            stock.ticker,
            cleaned_name,
            stock.exchange,
            anchor.profile_text if anchor else "",
            " ".join(tags),
            sector,
            industry,
            business_model,
            scale_bucket,
            " ".join(financial_tokens),
        ]
        if value
    )
    return CompanyPeerProfile(
        identifier=stock.ticker,
        display_name=cleaned_name,
        market="US",
        country="US",
        exchange=stock.exchange,
        profile_text=normalize_profile_text(base_text),
        business_tags=tags,
        sector=sector,
        industry=industry,
        business_model=business_model,
        scale_bucket=scale_bucket,
        fiscal_year=fundamental.fiscal_year,
        market_cap_usd=fundamental.market_cap_usd,
        revenue_usd=fundamental.revenue_usd,
        operating_income_usd=fundamental.operating_income_usd,
        net_income_usd=fundamental.net_income_usd,
        financial_data_source=fundamental.source,
        financial_feature_vector=build_financial_feature_vector(fundamental),
        eligible_peer=is_eligible_us_peer(stock),
        source="NASDAQ_TRADER_SYMBOL_DIRECTORY",
    )


def infer_business_tags(stock_name: str, stock_name_en: str) -> list[str]:
    text = f"{stock_name} {stock_name_en}".lower()
    rules = [
        (("bio", "therapeutics", "pharma", "제약", "바이오", "알테오젠"), "biotech"),
        (("drug delivery", "hyaluronidase", "subcutaneous"), "drug delivery"),
        (("semiconductor", "electronics", "chip", "반도체", "전자"), "semiconductors"),
        (("bank", "financial", "finance", "금융", "은행", "증권"), "financials"),
        (("motor", "auto", "vehicle", "자동차", "모터스"), "automotive"),
        (("energy", "electric", "power", "전력", "에너지"), "energy"),
        (("steel", "metal", "스틸", "철강"), "materials"),
        (("game", "gaming", "게임"), "gaming"),
        (
            ("platform", "internet", "software", "cloud", "플랫폼", "소프트웨어"),
            "software platform",
        ),
        (("retail", "commerce", "store", "유통"), "retail"),
        (("air", "aerospace", "항공"), "aerospace"),
        (("ship", "marine", "조선"), "shipbuilding"),
        (("chemical", "케미", "화학"), "chemicals"),
        (("telecom", "communications", "통신"), "telecommunications"),
    ]
    tags = [tag for keywords, tag in rules if any(keyword in text for keyword in keywords)]
    return list(dict.fromkeys(tags or ["general listed company"]))


def infer_sector(tags: Sequence[str]) -> str:
    sector_rules = {
        "biotech": "Health Care",
        "drug delivery": "Health Care",
        "semiconductors": "Information Technology",
        "financials": "Financials",
        "automotive": "Consumer Discretionary",
        "energy": "Energy",
        "materials": "Materials",
        "gaming": "Communication Services",
        "software platform": "Information Technology",
        "retail": "Consumer Discretionary",
        "aerospace": "Industrials",
        "shipbuilding": "Industrials",
        "chemicals": "Materials",
        "telecommunications": "Communication Services",
    }
    return next((sector_rules[tag] for tag in tags if tag in sector_rules), "Unclassified")


def infer_industry(tags: Sequence[str]) -> str:
    industry_rules = {
        "biotech": "Biotechnology",
        "drug delivery": "Drug Delivery Technology",
        "semiconductors": "Semiconductors",
        "financials": "Financial Services",
        "automotive": "Automobiles",
        "energy": "Energy Infrastructure",
        "materials": "Metals and Materials",
        "gaming": "Interactive Entertainment",
        "software platform": "Software",
        "retail": "Retail",
        "aerospace": "Aerospace and Defense",
        "shipbuilding": "Shipbuilding",
        "chemicals": "Specialty Chemicals",
        "telecommunications": "Telecommunications",
    }
    return next((industry_rules[tag] for tag in tags if tag in industry_rules), "Unclassified")


def infer_business_model(tags: Sequence[str]) -> str:
    if "royalty licensing" in tags or "drug delivery" in tags:
        return "Technology licensing and royalties"
    if "software platform" in tags:
        return "Platform software and recurring services"
    if "financials" in tags:
        return "Spread, fee, and capital-market services"
    if "semiconductors" in tags:
        return "Semiconductor manufacturing or supply chain"
    if "retail" in tags:
        return "Merchandising and commerce"
    return "Operating company"


def derive_scale_bucket(market_cap_usd: float | None) -> str:
    if market_cap_usd is None or market_cap_usd <= 0:
        return "UNKNOWN"
    if market_cap_usd >= 200_000_000_000:
        return "MEGA_CAP"
    if market_cap_usd >= 10_000_000_000:
        return "LARGE_CAP"
    if market_cap_usd >= 2_000_000_000:
        return "MID_CAP"
    if market_cap_usd >= 300_000_000:
        return "SMALL_CAP"
    return "MICRO_CAP"


def derive_revenue_bucket(revenue_usd: float | None) -> str:
    if revenue_usd is None or revenue_usd <= 0:
        return "UNKNOWN_REVENUE"
    if revenue_usd >= 100_000_000_000:
        return "MEGA_REVENUE"
    if revenue_usd >= 10_000_000_000:
        return "LARGE_REVENUE"
    if revenue_usd >= 1_000_000_000:
        return "MID_REVENUE"
    if revenue_usd >= 100_000_000:
        return "SMALL_REVENUE"
    return "MICRO_REVENUE"


def derive_profitability_bucket(
    revenue_usd: float | None,
    operating_income_usd: float | None,
) -> str:
    if revenue_usd is None or revenue_usd <= 0 or operating_income_usd is None:
        return "UNKNOWN_MARGIN"
    margin = operating_income_usd / revenue_usd
    if margin >= 0.35:
        return "HIGH_MARGIN"
    if margin >= 0.15:
        return "MID_MARGIN"
    if margin >= 0.0:
        return "LOW_MARGIN"
    return "LOSS_MAKING"


def financial_profile_tokens(fundamental: GlobalPeerFundamentals) -> tuple[str, ...]:
    tokens = [
        derive_scale_bucket(fundamental.market_cap_usd),
        derive_revenue_bucket(fundamental.revenue_usd),
        derive_profitability_bucket(fundamental.revenue_usd, fundamental.operating_income_usd),
    ]
    if fundamental.market_cap_usd and fundamental.market_cap_usd > 0:
        tokens.append(f"marketcap_{int(math.log10(fundamental.market_cap_usd))}")
    if fundamental.revenue_usd and fundamental.revenue_usd > 0:
        tokens.append(f"revenue_{int(math.log10(fundamental.revenue_usd))}")
    return tuple(token for token in tokens if not token.startswith("UNKNOWN"))


def build_financial_feature_vector(fundamental: GlobalPeerFundamentals) -> tuple[float, ...]:
    market_cap = _log_feature(fundamental.market_cap_usd)
    revenue = _log_feature(fundamental.revenue_usd)
    operating_income = _signed_log_feature(fundamental.operating_income_usd)
    net_income = _signed_log_feature(fundamental.net_income_usd)
    operating_margin = _margin_feature(fundamental.operating_income_usd, fundamental.revenue_usd)
    net_margin = _margin_feature(fundamental.net_income_usd, fundamental.revenue_usd)
    return (
        market_cap,
        revenue,
        operating_income,
        net_income,
        operating_margin,
        net_margin,
    )


def has_financial_signal(vector: Sequence[float]) -> bool:
    return any(abs(value) > 0.000001 for value in vector)


def _fundamental_for(
    market: str,
    identifier: str,
    anchor: PeerAnchor | None,
    fundamentals: dict[tuple[str, str], GlobalPeerFundamentals] | None,
) -> GlobalPeerFundamentals:
    key = (market.upper(), identifier.upper())
    if fundamentals and key in fundamentals:
        return fundamentals[key]
    if anchor:
        return GlobalPeerFundamentals(
            market=market.upper(),
            identifier=identifier.upper(),
            fiscal_year=anchor.fiscal_year,
            market_cap_usd=anchor.market_cap_usd,
            revenue_usd=anchor.revenue_usd,
            operating_income_usd=anchor.operating_income_usd,
            net_income_usd=anchor.net_income_usd,
            currency="USD",
            source=anchor.financial_data_source,
        )
    return GlobalPeerFundamentals(
        market=market.upper(),
        identifier=identifier.upper(),
        fiscal_year=None,
        market_cap_usd=None,
        revenue_usd=None,
        operating_income_usd=None,
        net_income_usd=None,
        currency="USD",
        source="",
    )


def _log_feature(value: float | None) -> float:
    if value is None or value <= 0:
        return 0.0
    return math.log10(value)


def _signed_log_feature(value: float | None) -> float:
    if value is None or value == 0:
        return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * math.log10(abs(value) + 1.0)


def _margin_feature(numerator: float | None, denominator: float | None) -> float:
    if numerator is None or denominator is None or denominator <= 0:
        return 0.0
    return max(-1.0, min(1.0, numerator / denominator))


def clean_security_name(value: str) -> str:
    cleaned = value.replace(" - ", " ")
    cleaned = _SECURITY_SUFFIX_PATTERN.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ,.-")


def _parse_optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized or normalized.lower() in {"none", "null", "nan"}:
        return None
    try:
        return int(normalized)
    except ValueError:
        return None


def _parse_optional_float(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = value.replace(",", "").strip()
    if not normalized or normalized.lower() in {"none", "null", "nan"}:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}".rstrip("0").rstrip(".")


def normalize_profile_text(value: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z가-힣]+", " ", value)
    return re.sub(r"\s+", " ", normalized).strip().lower()


def is_eligible_us_peer(stock: UsStockUniverseEntry) -> bool:
    if stock.etf or stock.test_issue:
        return False
    name = stock.company_name.lower()
    excluded_tokens = (
        " etf",
        " etn",
        " fund",
        " right",
        " rights",
        " unit",
        " units",
        " warrant",
        " warrants",
        " preferred",
        " note",
        " notes",
        " bond",
    )
    return not any(token in name for token in excluded_tokens)


def _download_symbol_directory(url: str) -> str:
    request = Request(  # noqa: S310  # nosec B310
        url,
        headers={"User-Agent": "Hannah-Montana-AI global peer sync"},
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310  # nosec B310
        payload = cast(bytes, response.read())
        return payload.decode("utf-8", errors="replace")


def _download_json(url: str) -> dict[str, object]:
    request = Request(  # noqa: S310  # nosec B310
        url,
        headers={
            "User-Agent": os.getenv(
                "SEC_USER_AGENT",
                "Hannah-Montana-AI/1.0 contact dev@hana-harmony.local",
            ),
            "Accept": "application/json",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310  # nosec B310
        payload = cast(bytes, response.read())
    decoded = json.loads(payload.decode("utf-8", errors="replace"))
    if not isinstance(decoded, dict):
        raise ValueError("JSON response must be an object")
    return decoded


def _download_nasdaq_json(url: str) -> dict[str, object]:
    request = Request(  # noqa: S310  # nosec B310
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/",
        },
    )
    with urlopen(request, timeout=10) as response:  # noqa: S310  # nosec B310
        payload = cast(bytes, response.read())
    decoded = json.loads(payload.decode("utf-8", errors="replace"))
    if not isinstance(decoded, dict):
        raise ValueError("NASDAQ JSON response must be an object")
    return decoded


def _download_naver_json(url: str) -> dict[str, object]:
    request = Request(  # noqa: S310  # nosec B310
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://m.stock.naver.com/",
        },
    )
    with urlopen(request, timeout=10) as response:  # noqa: S310  # nosec B310
        payload = cast(bytes, response.read())
    decoded = json.loads(payload.decode("utf-8", errors="replace"))
    if not isinstance(decoded, dict):
        raise ValueError("Naver stock JSON response must be an object")
    return decoded


def _download_krx_json(url: str, auth_key: str) -> dict[str, object]:
    request = Request(  # noqa: S310  # nosec B310
        url,
        headers={
            "AUTH_KEY": auth_key,
            "Accept": "application/json",
            "User-Agent": "Hannah-Montana-AI global peer fundamentals sync",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310  # nosec B310
        payload = cast(bytes, response.read())
    decoded = json.loads(payload.decode("utf-8", errors="replace"))
    if not isinstance(decoded, dict):
        raise ValueError("KRX JSON response must be an object")
    return decoded


def _sec_fact_value(
    facts: dict[str, object],
    fiscal_year: int,
    concept_names: Sequence[str],
) -> float | None:
    candidates: list[tuple[int, str, float]] = []
    for concept_name in concept_names:
        concept = facts.get(concept_name)
        if not isinstance(concept, dict):
            continue
        units = concept.get("units")
        if not isinstance(units, dict):
            continue
        usd_rows = units.get("USD")
        if not isinstance(usd_rows, list):
            continue
        for row in usd_rows:
            if not isinstance(row, dict):
                continue
            form = str(row.get("form", ""))
            frame = str(row.get("frame", ""))
            row_year = _parse_optional_int(str(row.get("fy", "")))
            value = row.get("val")
            if row_year is None or row_year > fiscal_year:
                continue
            if form not in {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}:
                continue
            if frame and not frame.startswith(f"CY{row_year}"):
                continue
            if isinstance(value, int | float):
                candidates.append((row_year, concept_name, float(value)))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _open_dart_account_value(
    rows: Sequence[object],
    account_ids: Sequence[str],
    account_names: Sequence[str],
) -> float | None:
    normalized_ids = {value.lower() for value in account_ids}
    normalized_names = tuple(account_names)
    income_rows = [row for row in rows if _is_open_dart_income_statement_row(row)]
    for row in income_rows:
        if not isinstance(row, dict):
            continue
        account_id = str(row.get("account_id", "")).lower()
        if account_id not in normalized_ids:
            continue
        parsed = _parse_optional_float(str(row.get("thstrm_amount", "")))
        if parsed is not None:
            return parsed
    for row in income_rows:
        if not isinstance(row, dict):
            continue
        account_name = str(row.get("account_nm", ""))
        if not any(name in account_name for name in normalized_names):
            continue
        parsed = _parse_optional_float(str(row.get("thstrm_amount", "")))
        if parsed is not None:
            return parsed
    return None


def _is_open_dart_income_statement_row(row: object) -> bool:
    if not isinstance(row, dict):
        return False
    statement_division = str(row.get("sj_div", "")).upper()
    return not statement_division or statement_division in {"IS", "CIS"}


def _convert_krw_to_usd(value: float | None, krw_usd_rate: float) -> float | None:
    if value is None:
        return None
    return value * krw_usd_rate


def _parse_korean_market_value_krw(value: str) -> float | None:
    normalized = value.replace(",", "").replace(" ", "")
    if not normalized or normalized in {"-", "N/A"}:
        return None
    total = 0.0
    jo_match = re.search(r"([0-9.]+)조", normalized)
    eok_match = re.search(r"([0-9.]+)억", normalized)
    if jo_match:
        total += float(jo_match.group(1)) * 1_000_000_000_000
    if eok_match:
        total += float(eok_match.group(1)) * 100_000_000
    if total > 0:
        return total
    numeric = _parse_optional_float(normalized)
    return None if numeric is None else numeric


def _parse_nasdaq_listed(payload: str) -> list[UsStockUniverseEntry]:
    rows = _pipe_rows(payload)
    return [
        UsStockUniverseEntry(
            ticker=row["Symbol"].strip(),
            company_name=row["Security Name"].strip(),
            exchange=_nasdaq_market(row.get("Market Category", "")),
            etf=row.get("ETF", "").strip().upper() == "Y",
            test_issue=row.get("Test Issue", "").strip().upper() == "Y",
            security_type="NASDAQ_LISTED",
        )
        for row in rows
        if row.get("Symbol", "").strip()
    ]


def _parse_other_listed(payload: str) -> list[UsStockUniverseEntry]:
    rows = _pipe_rows(payload)
    return [
        UsStockUniverseEntry(
            ticker=row["ACT Symbol"].strip(),
            company_name=row["Security Name"].strip(),
            exchange=_other_exchange(row.get("Exchange", "")),
            etf=row.get("ETF", "").strip().upper() == "Y",
            test_issue=row.get("Test Issue", "").strip().upper() == "Y",
            security_type="OTHER_LISTED",
        )
        for row in rows
        if row.get("ACT Symbol", "").strip()
    ]


def _pipe_rows(payload: str) -> list[dict[str, str]]:
    lines = [
        line
        for line in payload.splitlines()
        if line.strip() and not line.startswith("File Creation Time:")
    ]
    return list(csv.DictReader(lines, delimiter="|"))


def _dedupe_us_entries(entries: Sequence[UsStockUniverseEntry]) -> list[UsStockUniverseEntry]:
    deduped: dict[str, UsStockUniverseEntry] = {}
    for entry in entries:
        deduped.setdefault(entry.ticker, entry)
    return list(deduped.values())


def _nasdaq_market(value: str) -> str:
    return {
        "Q": "NASDAQ_GLOBAL_SELECT",
        "G": "NASDAQ_GLOBAL",
        "S": "NASDAQ_CAPITAL",
    }.get(value.strip().upper(), "NASDAQ")


def _other_exchange(value: str) -> str:
    return {
        "A": "NYSE_AMERICAN",
        "N": "NYSE",
        "P": "NYSE_ARCA",
        "Z": "CBOE_BZX",
        "V": "IEXG",
    }.get(value.strip().upper(), value.strip().upper() or "US")


def _english_name_fallback(stock: StockUniverseEntry) -> str:
    if stock.stock_code == "196170":
        return "Alteogen"
    return stock.stock_name_en or stock.stock_name


def _anchors_to_payload(anchors: dict[str, PeerAnchor]) -> dict[str, dict[str, object]]:
    return {
        key: {
            "profile_text": anchor.profile_text,
            "business_tags": list(anchor.business_tags),
            "sector": anchor.sector,
            "industry": anchor.industry,
            "business_model": anchor.business_model,
            "scale_bucket": anchor.scale_bucket,
            "market_cap_usd": anchor.market_cap_usd,
            "revenue_usd": anchor.revenue_usd,
            "operating_income_usd": anchor.operating_income_usd,
            "net_income_usd": anchor.net_income_usd,
            "fiscal_year": anchor.fiscal_year,
            "financial_data_source": anchor.financial_data_source,
            "positioning_title": anchor.positioning_title,
            "preferred_peer_ticker": anchor.preferred_peer_ticker,
            "headline_template": anchor.headline_template,
            "summary": anchor.summary,
        }
        for key, anchor in anchors.items()
    }


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
