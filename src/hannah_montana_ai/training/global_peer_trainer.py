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
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    load_stock_universe,
)

GLOBAL_PEER_SCHEMA_VERSION = "global-peer-hybrid-ranker/v3"
GLOBAL_PEER_MODEL_VERSION_PREFIX = "global-peer-hybrid-ranker"
GENERIC_LISTED_SECTOR = "General Listed Equity"
GENERIC_LISTED_INDUSTRY = "Listed Operating Company"
NAVER_INDUSTRY_CODE_TAG_OVERRIDES: dict[str, tuple[str, ...]] = {
    "266": ("consumer brands",),
    "267": ("software platform",),
    "274": ("consumer brands",),
    "275": ("food and beverage",),
    "276": ("holding company",),
    "277": ("financials",),
    "287": ("software platform",),
    "292": ("semiconductors",),
    "293": ("software platform",),
    "297": ("consumer brands",),
    "303": ("consumer brands",),
    "327": ("consumer electronics",),
    "328": ("retail",),
    "330": ("insurance",),
    "331": ("energy",),
    "332": ("consumer brands",),
    "337": ("financials",),
    "338": ("consumer electronics",),
    "334": ("retail",),
}
NAVER_INDUSTRY_CODE_ALWAYS_OVERRIDE_CODES = {
    "267",
    "274",
    "276",
    "277",
    "287",
    "292",
    "293",
    "327",
    "328",
    "330",
    "331",
    "332",
    "334",
    "337",
    "338",
}
KOREAN_ADR_TICKERS = {
    "KB",
    "KEP",
    "KT",
    "LPL",
    "PKX",
    "SHG",
    "SKM",
    "WF",
}
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
PAIRWISE_FEATURE_NAMES = (
    "text_similarity",
    "semantic_similarity",
    "financial_similarity",
    "same_sector",
    "same_industry",
    "same_business_model",
    "same_scale_bucket",
    "specific_sector_mismatch",
    "specific_industry_mismatch",
    "peer_market_cap_log",
    "peer_revenue_log",
    "market_cap_log_gap",
    "revenue_log_gap",
    "operating_margin_gap",
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
class KoreaIndustryProfile:
    stock_code: str
    stock_name: str
    industry_code: str
    peer_stock_codes: tuple[str, ...]
    peer_stock_names: tuple[str, ...]
    business_tags: tuple[str, ...]
    sector: str
    industry: str
    business_model: str
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "peer_stock_codes": list(self.peer_stock_codes),
            "peer_stock_names": list(self.peer_stock_names),
            "business_tags": list(self.business_tags),
        }


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
    display_name: str = ""
    positioning_title: str = ""
    preferred_peer_ticker: str = ""
    headline_template: str = ""
    summary: str = ""


KOREA_ANCHORS: dict[str, PeerAnchor] = {
    "000660": PeerAnchor(
        profile_text=(
            "SK hynix memory semiconductor DRAM NAND HBM chips data center AI memory "
            "global memory manufacturer"
        ),
        business_tags=("semiconductors", "memory chips"),
        sector="Information Technology",
        industry="Semiconductors",
        business_model="Memory semiconductor manufacturing",
        scale_bucket="MEGA_CAP",
        preferred_peer_ticker="MU",
    ),
    "005930": PeerAnchor(
        profile_text=(
            "Samsung Electronics semiconductor memory DRAM NAND HBM foundry consumer "
            "electronics mobile display appliances global technology manufacturer"
        ),
        business_tags=("semiconductors", "memory chips", "consumer electronics"),
        sector="Information Technology",
        industry="Semiconductors",
        business_model="Semiconductor and electronics manufacturing",
        scale_bucket="MEGA_CAP",
        preferred_peer_ticker="MU",
    ),
    "006400": PeerAnchor(
        profile_text=(
            "Samsung SDI lithium ion battery EV battery cells energy storage electronic "
            "materials rechargeable battery manufacturer"
        ),
        business_tags=("battery",),
        sector="Industrials",
        industry="Battery and Energy Storage",
        business_model="Battery manufacturing and energy storage supply chain",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="QS",
    ),
    "017670": PeerAnchor(
        profile_text=(
            "SK Telecom wireless carrier mobile network broadband telecom operator "
            "5G communications services"
        ),
        business_tags=("telecommunications",),
        sector="Communication Services",
        industry="Telecommunications",
        business_model="Telecom network subscription services",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="VZ",
    ),
    "035420": PeerAnchor(
        profile_text=(
            "NAVER internet search portal online advertising commerce cloud content "
            "software platform online search advertising"
        ),
        business_tags=("software platform", "internet search", "online advertising"),
        sector="Information Technology",
        industry="Internet Platforms",
        business_model="Platform software, search advertising, and commerce",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="GOOGL",
    ),
    "051910": PeerAnchor(
        profile_text=(
            "LG Chem specialty chemicals petrochemicals advanced materials battery "
            "materials chemical manufacturer"
        ),
        business_tags=("chemicals",),
        sector="Materials",
        industry="Specialty Chemicals",
        business_model="Chemical and advanced materials manufacturing",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="DOW",
    ),
    "055550": PeerAnchor(
        profile_text=(
            "Shinhan Financial Group bank financial holding consumer banking credit cards "
            "wealth management capital markets"
        ),
        business_tags=("banking", "financials"),
        sector="Financials",
        industry="Banks",
        business_model="Banking, spread income, fees, and capital-market services",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="C",
    ),
    "066570": PeerAnchor(
        profile_text=(
            "LG Electronics consumer electronics home appliances TV display HVAC devices "
            "global electronics brand"
        ),
        business_tags=("consumer electronics", "home appliances"),
        sector="Consumer Discretionary",
        industry="Consumer Electronics and Appliances",
        business_model="Consumer electronics and appliance manufacturing",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="WHR",
    ),
    "068270": PeerAnchor(
        profile_text=(
            "Celltrion biosimilar monoclonal antibody biologics pharmaceutical developer "
            "biotech manufacturing global biosimilar company"
        ),
        business_tags=("biotech", "biosimilar"),
        sector="Health Care",
        industry="Biotechnology",
        business_model="Biologics and biosimilar development",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="BIIB",
    ),
    "086790": PeerAnchor(
        profile_text=(
            "Hana Financial Group bank financial holding commercial banking wealth "
            "management securities capital markets"
        ),
        business_tags=("banking", "financials"),
        sector="Financials",
        industry="Banks",
        business_model="Banking, spread income, fees, and capital-market services",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="C",
    ),
    "105560": PeerAnchor(
        profile_text=(
            "KB Financial Group bank financial holding commercial banking insurance "
            "credit card wealth management"
        ),
        business_tags=("banking", "financials"),
        sector="Financials",
        industry="Banks",
        business_model="Banking, spread income, fees, and capital-market services",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="C",
    ),
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
        display_name="Alteogen",
        positioning_title="Global Biotech Platform Leader",
        preferred_peer_ticker="HALO",
        headline_template=(
            "{stock_name_en} Is The '{peer_name}' of South Korea — A Global Biotech Platform Leader"
        ),
        summary=(
            "Alteogen is a high-margin Biotech Platform provider. Instead of developing "
            "its own new drugs, it licenses out its proprietary drug-delivery technology "
            "to global Big Pharma, securing long-term milestone and royalty fees."
        ),
    ),
    "207940": PeerAnchor(
        profile_text=(
            "Samsung Biologics biologics CDMO contract development manufacturing "
            "large scale biopharmaceutical manufacturing"
        ),
        business_tags=("biotech", "biologics cdmo"),
        sector="Health Care",
        industry="Biotechnology",
        business_model="Biologics contract development and manufacturing",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="TMO",
    ),
    "373220": PeerAnchor(
        profile_text=(
            "LG Energy Solution lithium ion EV battery cells energy storage battery "
            "manufacturer electric vehicle supply chain"
        ),
        business_tags=("battery",),
        sector="Industrials",
        industry="Battery and Energy Storage",
        business_model="Battery manufacturing and energy storage supply chain",
        scale_bucket="LARGE_CAP",
        preferred_peer_ticker="TSLA",
    ),
}

US_ANCHORS: dict[str, PeerAnchor] = {
    "BAC": PeerAnchor(
        profile_text="Bank of America large diversified bank consumer banking wealth management",
        business_tags=("banking", "financials"),
        sector="Financials",
        industry="Banks",
        business_model="Banking, spread income, fees, and capital-market services",
        scale_bucket="MEGA_CAP",
        positioning_title="Diversified Banking Group",
    ),
    "BIIB": PeerAnchor(
        profile_text="Biogen biologics biotechnology neurology pharmaceutical therapy developer",
        business_tags=("biotech", "biologics"),
        sector="Health Care",
        industry="Biotechnology",
        business_model="Biologics and specialty drug development",
        scale_bucket="LARGE_CAP",
        positioning_title="Biotechnology Company",
    ),
    "C": PeerAnchor(
        profile_text="Citigroup global bank financial holding commercial banking capital markets",
        business_tags=("banking", "financials"),
        sector="Financials",
        industry="Banks",
        business_model="Banking, spread income, fees, and capital-market services",
        scale_bucket="MEGA_CAP",
        positioning_title="Global Banking Group",
    ),
    "DOW": PeerAnchor(
        profile_text=(
            "Dow specialty chemicals petrochemicals advanced materials chemical manufacturer"
        ),
        business_tags=("chemicals",),
        sector="Materials",
        industry="Specialty Chemicals",
        business_model="Chemical and advanced materials manufacturing",
        scale_bucket="LARGE_CAP",
        positioning_title="Specialty Chemicals Manufacturer",
    ),
    "GOOG": PeerAnchor(
        profile_text="Alphabet Google internet search advertising cloud software platform commerce",
        business_tags=("software platform", "internet search", "online advertising"),
        sector="Information Technology",
        industry="Internet Platforms",
        business_model="Platform software, search advertising, and commerce",
        scale_bucket="MEGA_CAP",
        positioning_title="Global Internet Platform",
    ),
    "GOOGL": PeerAnchor(
        profile_text="Alphabet Google internet search advertising cloud software platform commerce",
        business_tags=("software platform", "internet search", "online advertising"),
        sector="Information Technology",
        industry="Internet Platforms",
        business_model="Platform software, search advertising, and commerce",
        scale_bucket="MEGA_CAP",
        positioning_title="Global Internet Platform",
    ),
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
    "JPM": PeerAnchor(
        profile_text=(
            "JPMorgan Chase large diversified bank consumer banking asset "
            "management capital markets"
        ),
        business_tags=("banking", "financials"),
        sector="Financials",
        industry="Banks",
        business_model="Banking, spread income, fees, and capital-market services",
        scale_bucket="MEGA_CAP",
        positioning_title="Diversified Banking Group",
    ),
    "MU": PeerAnchor(
        profile_text=(
            "Micron Technology memory semiconductor DRAM NAND HBM chips data center AI memory"
        ),
        business_tags=("semiconductors", "memory chips"),
        sector="Information Technology",
        industry="Semiconductors",
        business_model="Memory semiconductor manufacturing",
        scale_bucket="MEGA_CAP",
        positioning_title="Memory Semiconductor Manufacturer",
    ),
    "QS": PeerAnchor(
        profile_text=(
            "QuantumScape solid state lithium metal EV battery cells energy "
            "storage battery technology"
        ),
        business_tags=("battery",),
        sector="Industrials",
        industry="Battery and Energy Storage",
        business_model="Battery manufacturing and energy storage supply chain",
        scale_bucket="MID_CAP",
        positioning_title="Battery Technology Company",
    ),
    "SONY": PeerAnchor(
        profile_text=(
            "Sony consumer electronics image sensors entertainment devices TV "
            "audio global electronics brand"
        ),
        business_tags=("consumer electronics",),
        sector="Consumer Discretionary",
        industry="Consumer Electronics and Appliances",
        business_model="Consumer electronics and entertainment hardware",
        scale_bucket="LARGE_CAP",
        positioning_title="Consumer Electronics Group",
    ),
    "TMO": PeerAnchor(
        profile_text=(
            "Thermo Fisher Scientific life sciences biologics services CDMO "
            "bioproduction instruments"
        ),
        business_tags=("biotech", "biologics cdmo"),
        sector="Health Care",
        industry="Biotechnology",
        business_model="Biologics contract development and life-science services",
        scale_bucket="LARGE_CAP",
        positioning_title="Life Science Services Platform",
    ),
    "TSLA": PeerAnchor(
        profile_text=(
            "Tesla electric vehicle battery cells energy storage lithium ion "
            "manufacturing battery ecosystem"
        ),
        business_tags=("battery", "automotive"),
        sector="Industrials",
        industry="Battery and Energy Storage",
        business_model="Battery manufacturing and energy storage supply chain",
        scale_bucket="MEGA_CAP",
        positioning_title="EV Battery Ecosystem",
    ),
    "VZ": PeerAnchor(
        profile_text=(
            "Verizon wireless carrier mobile network broadband telecom operator "
            "5G communications services"
        ),
        business_tags=("telecommunications",),
        sector="Communication Services",
        industry="Telecommunications",
        business_model="Telecom network subscription services",
        scale_bucket="LARGE_CAP",
        positioning_title="Telecommunications Operator",
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


def fetch_naver_korea_industry_profile(stock: StockUniverseEntry) -> KoreaIndustryProfile | None:
    payload = _download_naver_json(NAVER_STOCK_INTEGRATION_URL.format(stock_code=stock.stock_code))
    if str(payload.get("stockEndType") or "") != "stock":
        return None
    industry_code = str(payload.get("industryCode") or "").strip()
    compare_rows = payload.get("industryCompareInfo", [])
    peer_codes: list[str] = []
    peer_names: list[str] = []
    if isinstance(compare_rows, list):
        for item in compare_rows:
            if not isinstance(item, dict):
                continue
            peer_code = str(item.get("itemCode") or "").strip()
            peer_name = str(item.get("stockName") or "").strip()
            if peer_code and peer_code != stock.stock_code:
                peer_codes.append(peer_code)
            if peer_name and peer_name != stock.stock_name:
                peer_names.append(peer_name)
    names = list(dict.fromkeys([stock.stock_name, stock.stock_name_en, *peer_names]))
    tags = tuple(infer_business_tags(" ".join(names), " ".join(names)))
    sector = infer_sector(tags)
    industry = infer_industry(tags)
    business_model = infer_business_model(tags)
    if not industry_code and not peer_names and sector == GENERIC_LISTED_SECTOR:
        return None
    return KoreaIndustryProfile(
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        industry_code=industry_code,
        peer_stock_codes=tuple(dict.fromkeys(peer_codes)),
        peer_stock_names=tuple(dict.fromkeys(peer_names)),
        business_tags=tags,
        sector=sector,
        industry=industry,
        business_model=business_model,
        source="NAVER_STOCK_INDUSTRY_COMPARE",
    )


def fetch_open_dart_annual_fundamentals(
    api_key: str,
    stock_code: str,
    corp_code: str,
    fiscal_year: int,
    krw_usd_rate: float = 0.00072,
) -> GlobalPeerFundamentals | None:
    for statement_type in ("CFS", "OFS"):
        payload = _download_json(
            f"{OPEN_DART_FINANCIAL_URL}?{
                urlencode(
                    {
                        'crtfc_key': api_key,
                        'corp_code': corp_code,
                        'bsns_year': str(fiscal_year),
                        'reprt_code': '11011',
                        'fs_div': statement_type,
                    }
                )
            }"
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


def load_korea_industry_profiles(path: Path) -> dict[str, KoreaIndustryProfile]:
    if not path.exists():
        return {}
    profiles: list[KoreaIndustryProfile] = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            stock_code = row["stock_code"].strip()
            if not stock_code:
                continue
            raw_tags = _split_pipe(row.get("business_tags", ""))
            business_tags = tuple(
                tag for tag in raw_tags if tag and tag != "general listed company"
            )
            peer_stock_names = _split_pipe(row.get("peer_stock_names", ""))
            if not business_tags:
                inferred_tags = infer_business_tags(
                    row.get("stock_name", "").strip(),
                    " ".join(peer_stock_names),
                )
                business_tags = tuple(
                    tag for tag in inferred_tags if tag and tag != "general listed company"
                )
            source = row.get("source", "").strip()
            industry_code = row.get("industry_code", "").strip()
            taxonomy_tags = NAVER_INDUSTRY_CODE_TAG_OVERRIDES.get(industry_code)
            if taxonomy_tags and (
                not business_tags
                or business_tags == ("holding company",)
                or industry_code in NAVER_INDUSTRY_CODE_ALWAYS_OVERRIDE_CODES
            ):
                business_tags = taxonomy_tags
                source = f"{source or 'NAVER_STOCK_INDUSTRY_COMPARE'}+NAVER_INDUSTRY_CODE_TAXONOMY"
            sector = infer_sector(business_tags) if business_tags else GENERIC_LISTED_SECTOR
            industry = infer_industry(business_tags) if business_tags else GENERIC_LISTED_INDUSTRY
            business_model = (
                infer_business_model(business_tags) if business_tags else "Operating company"
            )
            profiles.append(
                KoreaIndustryProfile(
                    stock_code=stock_code,
                    stock_name=row.get("stock_name", "").strip(),
                    industry_code=industry_code,
                    peer_stock_codes=_split_pipe(row.get("peer_stock_codes", "")),
                    peer_stock_names=peer_stock_names,
                    business_tags=business_tags,
                    sector=sector,
                    industry=industry,
                    business_model=business_model,
                    source=source,
                )
            )
    return {
        profile.stock_code: profile for profile in _impute_generic_korea_industry_profiles(profiles)
    }


def _impute_generic_korea_industry_profiles(
    profiles: Sequence[KoreaIndustryProfile],
) -> list[KoreaIndustryProfile]:
    labeled = [profile for profile in profiles if _is_specific_korea_industry_profile(profile)]
    generic = [profile for profile in profiles if not _is_specific_korea_industry_profile(profile)]
    if len(labeled) < 100 or not generic:
        return list(profiles)

    training_texts = [_korea_industry_profile_text(profile) for profile in labeled]
    training_labels = [_primary_operating_tag(profile.business_tags) for profile in labeled]
    industry_tag_counts: dict[str, Counter[str]] = {}
    for profile, label in zip(labeled, training_labels, strict=True):
        if profile.industry_code:
            industry_tag_counts.setdefault(profile.industry_code, Counter())[label] += 1

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1)
    features = vectorizer.fit_transform(training_texts)
    classifier = LogisticRegression(
        max_iter=1_000,
        class_weight="balanced",
        random_state=42,
    )
    classifier.fit(features, training_labels)

    generic_texts = [_korea_industry_profile_text(profile) for profile in generic]
    probabilities = classifier.predict_proba(vectorizer.transform(generic_texts))
    classes = [str(label) for label in classifier.classes_]
    imputed_by_code: dict[str, KoreaIndustryProfile] = {}
    for profile, row_probabilities in zip(generic, probabilities, strict=True):
        if profile.industry_code in NAVER_INDUSTRY_CODE_TAG_OVERRIDES:
            tags = NAVER_INDUSTRY_CODE_TAG_OVERRIDES[profile.industry_code]
            source = profile.source or "NAVER_STOCK_INDUSTRY_COMPARE"
            imputed_by_code[profile.stock_code] = KoreaIndustryProfile(
                stock_code=profile.stock_code,
                stock_name=profile.stock_name,
                industry_code=profile.industry_code,
                peer_stock_codes=profile.peer_stock_codes,
                peer_stock_names=profile.peer_stock_names,
                business_tags=tags,
                sector=infer_sector(tags),
                industry=infer_industry(tags),
                business_model=infer_business_model(tags),
                source=f"{source}+NAVER_INDUSTRY_CODE_TAXONOMY",
            )
            continue
        best_index = int(np.argmax(row_probabilities))
        predicted_tag = classes[best_index]
        confidence = float(row_probabilities[best_index])
        dominant_tag = _dominant_industry_tag(industry_tag_counts.get(profile.industry_code))
        if not _accept_imputed_korea_tag(
            predicted_tag=predicted_tag,
            confidence=confidence,
            dominant_tag=dominant_tag,
        ):
            continue
        tags = (predicted_tag,)
        source = profile.source or "NAVER_STOCK_INDUSTRY_COMPARE"
        imputed_by_code[profile.stock_code] = KoreaIndustryProfile(
            stock_code=profile.stock_code,
            stock_name=profile.stock_name,
            industry_code=profile.industry_code,
            peer_stock_codes=profile.peer_stock_codes,
            peer_stock_names=profile.peer_stock_names,
            business_tags=tags,
            sector=infer_sector(tags),
            industry=infer_industry(tags),
            business_model=infer_business_model(tags),
            source=f"{source}+ML_INDUSTRY_IMPUTATION",
        )

    return [imputed_by_code.get(profile.stock_code, profile) for profile in profiles]


def _is_specific_korea_industry_profile(profile: KoreaIndustryProfile) -> bool:
    return (
        bool(profile.business_tags)
        and profile.sector != GENERIC_LISTED_SECTOR
        and profile.industry != GENERIC_LISTED_INDUSTRY
    )


def _primary_operating_tag(tags: Sequence[str]) -> str:
    operating_tags = [tag for tag in tags if tag != "holding company"]
    return (operating_tags or list(tags) or ["general listed company"])[0]


def _korea_industry_profile_text(profile: KoreaIndustryProfile) -> str:
    return " ".join(
        value
        for value in [
            f"industry_code_{profile.industry_code}",
            profile.stock_name,
            " ".join(profile.peer_stock_names),
        ]
        if value
    )


def _dominant_industry_tag(tag_counts: Counter[str] | None) -> str | None:
    if not tag_counts:
        return None
    most_common = tag_counts.most_common(2)
    top_tag, top_count = most_common[0]
    total_count = sum(tag_counts.values())
    if top_count >= 5 and top_count / total_count >= 0.75:
        return top_tag
    return None


def _accept_imputed_korea_tag(
    *,
    predicted_tag: str,
    confidence: float,
    dominant_tag: str | None,
) -> bool:
    if confidence >= 0.65:
        return True
    return bool(dominant_tag and predicted_tag == dominant_tag and confidence >= 0.45)


def write_korea_industry_profiles(
    path: Path,
    rows: Sequence[KoreaIndustryProfile],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "stock_code",
                "stock_name",
                "industry_code",
                "peer_stock_codes",
                "peer_stock_names",
                "business_tags",
                "sector",
                "industry",
                "business_model",
                "source",
            ],
        )
        writer.writeheader()
        for row in sorted(rows, key=lambda item: item.stock_code):
            writer.writerow(
                {
                    "stock_code": row.stock_code,
                    "stock_name": row.stock_name,
                    "industry_code": row.industry_code,
                    "peer_stock_codes": "|".join(row.peer_stock_codes),
                    "peer_stock_names": "|".join(row.peer_stock_names),
                    "business_tags": "|".join(row.business_tags),
                    "sector": row.sector,
                    "industry": row.industry,
                    "business_model": row.business_model,
                    "source": row.source,
                }
            )


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
    korea_industry_path: Path | None = None,
) -> PeerTrainingResult:
    korea_universe = load_stock_universe(korea_stock_universe_path)
    us_universe = load_us_stock_universe(us_stock_universe_path)
    fundamentals = load_global_peer_fundamentals(fundamentals_path)
    korea_industries = (
        load_korea_industry_profiles(korea_industry_path) if korea_industry_path else {}
    )
    if len(korea_universe) < 3_000:
        raise ValueError("global peer training requires the full Korean stock universe")
    if len(us_universe) < 5_000:
        raise ValueError("global peer training requires the full United States stock universe")

    korea_profiles = [
        build_korea_profile(stock, fundamentals, korea_industries) for stock in korea_universe
    ]
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
        dtype=np.float32,
    )
    corpus = [profile.profile_text for profile in [*korea_profiles, *us_profiles]]
    corpus_matrix = vectorizer.fit_transform(corpus)
    eligible_us_matrix = vectorizer.transform(
        [profile.profile_text for profile in eligible_us_profiles]
    )
    semantic_reducer = TruncatedSVD(
        n_components=_semantic_component_count(corpus_matrix.shape[0], corpus_matrix.shape[1]),
        random_state=42,
    )
    semantic_reducer.fit(corpus_matrix)
    eligible_us_semantic_matrix = normalize(
        semantic_reducer.transform(eligible_us_matrix),
        norm="l2",
    )
    eligible_us_financial_matrix = np.array(
        [profile.financial_feature_vector for profile in eligible_us_profiles],
        dtype=float,
    )
    pairwise_ranker, pairwise_ranker_report = train_pairwise_peer_ranker(
        korea_profiles=korea_profiles,
        eligible_us_profiles=eligible_us_profiles,
        vectorizer=vectorizer,
        eligible_us_matrix=eligible_us_matrix,
        semantic_reducer=semantic_reducer,
        eligible_us_semantic_matrix=eligible_us_semantic_matrix,
    )
    trained_at = datetime.now(UTC).isoformat()
    version = f"{GLOBAL_PEER_MODEL_VERSION_PREFIX}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "schema_version": GLOBAL_PEER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "vectorizer": vectorizer,
        "eligible_us_matrix": eligible_us_matrix,
        "semantic_reducer": semantic_reducer,
        "eligible_us_semantic_matrix": eligible_us_semantic_matrix,
        "eligible_us_financial_matrix": eligible_us_financial_matrix,
        "pairwise_ranker": pairwise_ranker,
        "pairwise_feature_names": list(PAIRWISE_FEATURE_NAMES),
        "eligible_us_profiles": [profile.to_dict() for profile in eligible_us_profiles],
        "korea_profiles": {profile.identifier: profile.to_dict() for profile in korea_profiles},
        "korea_anchors": _anchors_to_payload(KOREA_ANCHORS),
        "us_anchors": _anchors_to_payload(US_ANCHORS),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path, compress=9)

    report = build_global_peer_training_report(
        version=version,
        trained_at=trained_at,
        korea_stock_universe_path=korea_stock_universe_path,
        us_stock_universe_path=us_stock_universe_path,
        fundamentals_path=fundamentals_path,
        korea_industry_path=korea_industry_path,
        model_path=model_path,
        korea_profiles=korea_profiles,
        us_profiles=us_profiles,
        eligible_us_profiles=eligible_us_profiles,
        korea_industry_profiles=korea_industries,
        vectorizer=vectorizer,
        eligible_us_matrix=eligible_us_matrix,
        pairwise_ranker_report=pairwise_ranker_report,
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
    korea_industry_path: Path | None,
    model_path: Path,
    korea_profiles: Sequence[CompanyPeerProfile],
    us_profiles: Sequence[CompanyPeerProfile],
    eligible_us_profiles: Sequence[CompanyPeerProfile],
    korea_industry_profiles: dict[str, KoreaIndustryProfile],
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
    pairwise_ranker_report: dict[str, object],
) -> dict[str, object]:
    anchor_evaluation = evaluate_anchor_pairs(vectorizer, eligible_us_matrix, eligible_us_profiles)
    tag_distribution = Counter(
        tag for profile in [*korea_profiles, *us_profiles] for tag in profile.business_tags
    )
    korea_fundamental_count = sum(1 for profile in korea_profiles if profile.financial_data_source)
    us_fundamental_count = sum(1 for profile in us_profiles if profile.financial_data_source)
    korea_industry_specific_count = sum(
        1
        for profile in korea_profiles
        if profile.sector not in {"Unclassified", GENERIC_LISTED_SECTOR}
        and profile.industry not in {"Unclassified", GENERIC_LISTED_INDUSTRY}
    )
    all_profiles = [*korea_profiles, *us_profiles]
    minimum_korea_universe_count = 3_000
    actual_korea_universe_count = len(korea_profiles)
    minimum_us_universe_count = 5_000
    actual_us_universe_count = len(us_profiles)
    minimum_anchor_top1_accuracy = 0.75
    raw_anchor_top1_accuracy = anchor_evaluation["top1_accuracy"]
    if not isinstance(raw_anchor_top1_accuracy, int | float):
        raise TypeError("anchor top1 accuracy must be numeric")
    actual_anchor_top1_accuracy = float(raw_anchor_top1_accuracy)
    raw_ranker_top1_accuracy = pairwise_ranker_report["top1_accuracy"]
    if not isinstance(raw_ranker_top1_accuracy, int | float):
        raise TypeError("pairwise ranker top1 accuracy must be numeric")
    minimum_pairwise_ranker_top1_accuracy = 0.85
    actual_pairwise_ranker_top1_accuracy = float(raw_ranker_top1_accuracy)
    coverage_gate: dict[str, object] = {
        "minimum_korea_universe_count": minimum_korea_universe_count,
        "actual_korea_universe_count": actual_korea_universe_count,
        "minimum_us_universe_count": minimum_us_universe_count,
        "actual_us_universe_count": actual_us_universe_count,
        "minimum_anchor_top1_accuracy": minimum_anchor_top1_accuracy,
        "actual_anchor_top1_accuracy": actual_anchor_top1_accuracy,
        "minimum_pairwise_ranker_top1_accuracy": minimum_pairwise_ranker_top1_accuracy,
        "actual_pairwise_ranker_top1_accuracy": actual_pairwise_ranker_top1_accuracy,
    }
    coverage_gate["status"] = (
        "pass"
        if actual_korea_universe_count >= minimum_korea_universe_count
        and actual_us_universe_count >= minimum_us_universe_count
        and actual_anchor_top1_accuracy >= minimum_anchor_top1_accuracy
        and actual_pairwise_ranker_top1_accuracy >= minimum_pairwise_ranker_top1_accuracy
        else "fail"
    )
    return {
        "schema_version": GLOBAL_PEER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "korea_stock_universe_path": _report_path(korea_stock_universe_path),
        "us_stock_universe_path": _report_path(us_stock_universe_path),
        "fundamentals_path": _report_path(fundamentals_path),
        "korea_industry_path": _report_path(korea_industry_path) if korea_industry_path else "",
        "model_path": _report_path(model_path),
        "korea_universe_count": len(korea_profiles),
        "us_universe_count": len(us_profiles),
        "korea_industry_profile_count": len(korea_industry_profiles),
        "korea_industry_specific_profile_count": korea_industry_specific_count,
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
        "pairwise_ranker_evaluation": pairwise_ranker_report,
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


def train_pairwise_peer_ranker(
    korea_profiles: Sequence[CompanyPeerProfile],
    eligible_us_profiles: Sequence[CompanyPeerProfile],
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
    semantic_reducer: TruncatedSVD,
    eligible_us_semantic_matrix: np.ndarray,
) -> tuple[LogisticRegression, dict[str, object]]:
    korea_by_code = {profile.identifier: profile for profile in korea_profiles}
    us_by_ticker = {profile.identifier: profile for profile in eligible_us_profiles}
    feature_rows: list[list[float]] = []
    labels: list[int] = []
    candidate_count_by_stock: dict[str, int] = {}

    for stock_code, anchor in KOREA_ANCHORS.items():
        if not anchor.preferred_peer_ticker:
            continue
        stock_profile = korea_by_code.get(stock_code)
        expected_profile = us_by_ticker.get(anchor.preferred_peer_ticker)
        if stock_profile is None or expected_profile is None:
            continue

        text_scores, semantic_scores, financial_scores, base_scores = _candidate_scores(
            stock_profile=stock_profile,
            eligible_us_profiles=eligible_us_profiles,
            vectorizer=vectorizer,
            eligible_us_matrix=eligible_us_matrix,
            semantic_reducer=semantic_reducer,
            eligible_us_semantic_matrix=eligible_us_semantic_matrix,
        )
        expected_index = next(
            index
            for index, profile in enumerate(eligible_us_profiles)
            if profile.identifier == expected_profile.identifier
        )
        hard_negative_indices = [
            int(index) for index in base_scores.argsort()[::-1] if int(index) != expected_index
        ][:40]
        candidate_indices = [expected_index, *hard_negative_indices]
        candidate_count_by_stock[stock_code] = len(candidate_indices)
        for index in candidate_indices:
            feature_rows.append(
                pairwise_feature_vector(
                    stock_profile,
                    eligible_us_profiles[index],
                    text_scores[index],
                    semantic_scores[index],
                    financial_scores[index],
                )
            )
            labels.append(1 if index == expected_index else 0)

    if not feature_rows or len(set(labels)) != 2:
        raise ValueError("global peer ranker requires positive and negative peer labels")

    ranker = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )
    ranker.fit(np.array(feature_rows, dtype=float), np.array(labels, dtype=int))
    evaluation = evaluate_pairwise_ranker(
        ranker=ranker,
        korea_profiles=korea_profiles,
        eligible_us_profiles=eligible_us_profiles,
        vectorizer=vectorizer,
        eligible_us_matrix=eligible_us_matrix,
        semantic_reducer=semantic_reducer,
        eligible_us_semantic_matrix=eligible_us_semantic_matrix,
    )
    return ranker, {
        **evaluation,
        "training_pair_count": len(KOREA_ANCHORS),
        "training_sample_count": len(feature_rows),
        "positive_sample_count": sum(labels),
        "negative_sample_count": len(labels) - sum(labels),
        "feature_names": list(PAIRWISE_FEATURE_NAMES),
        "candidate_count_by_stock": candidate_count_by_stock,
        "ranking_model": "LogisticRegression(class_weight=balanced)",
        "label_policy": (
            "curated_peer_pairs_used_as supervised pairwise ranking labels, "
            "not serving-time forced anchors"
        ),
    }


def evaluate_pairwise_ranker(
    ranker: LogisticRegression,
    korea_profiles: Sequence[CompanyPeerProfile],
    eligible_us_profiles: Sequence[CompanyPeerProfile],
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
    semantic_reducer: TruncatedSVD,
    eligible_us_semantic_matrix: np.ndarray,
) -> dict[str, object]:
    korea_by_code = {profile.identifier: profile for profile in korea_profiles}
    rows: list[dict[str, object]] = []
    top1_hits = 0
    top3_hits = 0
    reciprocal_ranks: list[float] = []

    for stock_code, anchor in KOREA_ANCHORS.items():
        stock_profile = korea_by_code.get(stock_code)
        if stock_profile is None or not anchor.preferred_peer_ticker:
            continue
        scores = rank_pair_candidates(
            ranker=ranker,
            stock_profile=stock_profile,
            eligible_us_profiles=eligible_us_profiles,
            vectorizer=vectorizer,
            eligible_us_matrix=eligible_us_matrix,
            semantic_reducer=semantic_reducer,
            eligible_us_semantic_matrix=eligible_us_semantic_matrix,
        )
        ranked_indices = scores.argsort()[::-1]
        predicted_profile = eligible_us_profiles[int(ranked_indices[0])]
        expected_rank = next(
            (
                rank
                for rank, index in enumerate(ranked_indices, start=1)
                if eligible_us_profiles[int(index)].identifier == anchor.preferred_peer_ticker
            ),
            len(ranked_indices) + 1,
        )
        hit_top1 = predicted_profile.identifier == anchor.preferred_peer_ticker
        hit_top3 = expected_rank <= 3
        top1_hits += 1 if hit_top1 else 0
        top3_hits += 1 if hit_top3 else 0
        reciprocal_ranks.append(1.0 / expected_rank)
        rows.append(
            {
                "stock_code": stock_code,
                "expected_peer_ticker": anchor.preferred_peer_ticker,
                "predicted_peer_ticker": predicted_profile.identifier,
                "expected_peer_rank": expected_rank,
                "score": round(float(scores[int(ranked_indices[0])]), 6),
                "top1_hit": hit_top1,
                "top3_hit": hit_top3,
            }
        )

    sample_count = len(rows)
    return {
        "sample_count": sample_count,
        "top1_accuracy": top1_hits / sample_count if sample_count else 0.0,
        "top3_accuracy": top3_hits / sample_count if sample_count else 0.0,
        "mean_reciprocal_rank": (
            sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        ),
        "rows": rows,
    }


def rank_pair_candidates(
    ranker: LogisticRegression,
    stock_profile: CompanyPeerProfile,
    eligible_us_profiles: Sequence[CompanyPeerProfile],
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
    semantic_reducer: TruncatedSVD,
    eligible_us_semantic_matrix: np.ndarray,
) -> np.ndarray:
    text_scores, semantic_scores, financial_scores, base_scores = _candidate_scores(
        stock_profile=stock_profile,
        eligible_us_profiles=eligible_us_profiles,
        vectorizer=vectorizer,
        eligible_us_matrix=eligible_us_matrix,
        semantic_reducer=semantic_reducer,
        eligible_us_semantic_matrix=eligible_us_semantic_matrix,
    )
    feature_rows = np.array(
        [
            pairwise_feature_vector(
                stock_profile,
                peer_profile,
                text_scores[index],
                semantic_scores[index],
                financial_scores[index],
            )
            for index, peer_profile in enumerate(eligible_us_profiles)
        ],
        dtype=float,
    )
    ranker_scores = np.asarray(ranker.predict_proba(feature_rows)[:, 1], dtype=float)
    combined = np.asarray((0.60 * ranker_scores) + (0.40 * base_scores), dtype=float)
    for index, peer_profile in enumerate(eligible_us_profiles):
        combined[index] *= domain_priority_multiplier(stock_profile, peer_profile)
    return combined


def domain_priority_multiplier(
    stock_profile: CompanyPeerProfile,
    peer_profile: CompanyPeerProfile,
) -> float:
    generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
    generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
    multiplier = 1.0
    if stock_profile.sector not in generic_sectors:
        if peer_profile.sector in generic_sectors:
            multiplier *= 0.60
        elif stock_profile.sector != peer_profile.sector:
            multiplier *= 0.20
    if stock_profile.industry not in generic_industries:
        if peer_profile.industry in generic_industries:
            multiplier *= 0.75
        elif stock_profile.industry != peer_profile.industry:
            multiplier *= 0.45
    return multiplier


def pairwise_feature_vector(
    stock_profile: CompanyPeerProfile,
    peer_profile: CompanyPeerProfile,
    text_similarity: float,
    semantic_similarity: float,
    financial_similarity: float,
) -> list[float]:
    generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
    generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
    same_sector = stock_profile.sector == peer_profile.sector and stock_profile.sector not in {
        *generic_sectors,
    }
    same_industry = (
        stock_profile.industry == peer_profile.industry
        and stock_profile.industry not in {*generic_industries}
    )
    same_business_model = stock_profile.business_model == peer_profile.business_model
    same_scale = (
        stock_profile.scale_bucket != "UNKNOWN"
        and stock_profile.scale_bucket == peer_profile.scale_bucket
    )
    specific_sector_mismatch = (
        stock_profile.sector not in generic_sectors
        and peer_profile.sector not in generic_sectors
        and stock_profile.sector != peer_profile.sector
    )
    specific_industry_mismatch = (
        stock_profile.industry not in generic_industries
        and peer_profile.industry not in generic_industries
        and stock_profile.industry != peer_profile.industry
    )
    return [
        float(text_similarity),
        float(semantic_similarity),
        float(financial_similarity),
        1.0 if same_sector else 0.0,
        1.0 if same_industry else 0.0,
        1.0 if same_business_model else 0.0,
        1.0 if same_scale else 0.0,
        1.0 if specific_sector_mismatch else 0.0,
        1.0 if specific_industry_mismatch else 0.0,
        _normalized_log_feature(peer_profile.market_cap_usd),
        _normalized_log_feature(peer_profile.revenue_usd),
        _log_gap(stock_profile.market_cap_usd, peer_profile.market_cap_usd),
        _log_gap(stock_profile.revenue_usd, peer_profile.revenue_usd),
        abs(
            _margin_feature(stock_profile.operating_income_usd, stock_profile.revenue_usd)
            - _margin_feature(peer_profile.operating_income_usd, peer_profile.revenue_usd)
        ),
    ]


def _candidate_scores(
    stock_profile: CompanyPeerProfile,
    eligible_us_profiles: Sequence[CompanyPeerProfile],
    vectorizer: TfidfVectorizer,
    eligible_us_matrix: object,
    semantic_reducer: TruncatedSVD,
    eligible_us_semantic_matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    query_vector = vectorizer.transform([stock_profile.profile_text])
    text_scores = cosine_similarity(query_vector, eligible_us_matrix)[0]
    query_semantic = normalize(semantic_reducer.transform(query_vector), norm="l2")
    semantic_scores = cosine_similarity(query_semantic, eligible_us_semantic_matrix)[0]
    financial_scores = np.array(
        [
            _financial_similarity(
                stock_profile.financial_feature_vector,
                peer_profile.financial_feature_vector,
            )
            for peer_profile in eligible_us_profiles
        ],
        dtype=float,
    )
    base_scores = (0.50 * text_scores) + (0.30 * semantic_scores) + (0.20 * financial_scores)
    return text_scores, semantic_scores, financial_scores, base_scores


def _financial_similarity(stock_vector: Sequence[float], peer_vector: Sequence[float]) -> float:
    if not has_financial_signal(stock_vector) or not has_financial_signal(peer_vector):
        return 0.0
    stock_array = np.array(stock_vector, dtype=float).reshape(1, -1)
    peer_array = np.array(peer_vector, dtype=float).reshape(1, -1)
    score = float(cosine_similarity(stock_array, peer_array)[0][0])
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def _semantic_component_count(sample_count: int, feature_count: int) -> int:
    return max(2, min(256, sample_count - 1, feature_count - 1))


def _log_gap(left: float | None, right: float | None) -> float:
    left_value = _log_feature(left)
    right_value = _log_feature(right)
    if left_value == 0.0 or right_value == 0.0:
        return 1.0
    return abs(left_value - right_value)


def _normalized_log_feature(value: float | None) -> float:
    if value is None or value <= 0:
        return 0.0
    return max(0.0, min(1.0, math.log10(value) / 12.0))


def build_korea_profile(
    stock: StockUniverseEntry,
    fundamentals: dict[tuple[str, str], GlobalPeerFundamentals] | None = None,
    industry_profiles: dict[str, KoreaIndustryProfile] | None = None,
) -> CompanyPeerProfile:
    anchor = KOREA_ANCHORS.get(stock.stock_code)
    industry_profile = industry_profiles.get(stock.stock_code) if industry_profiles else None
    fundamental = _fundamental_for("KR", stock.stock_code, anchor, fundamentals)
    stock_name_en = stock.stock_name_en or _english_name_fallback(stock)
    inferred_tags = tuple(infer_business_tags(stock.stock_name, stock_name_en))
    if anchor:
        tags = anchor.business_tags
        sector = anchor.sector
        industry = anchor.industry
        business_model = anchor.business_model
    elif industry_profile and industry_profile.sector != GENERIC_LISTED_SECTOR:
        tags = industry_profile.business_tags
        sector = industry_profile.sector
        industry = industry_profile.industry
        business_model = industry_profile.business_model
    else:
        tags = inferred_tags
        sector = infer_sector(tags)
        industry = infer_industry(tags)
        business_model = infer_business_model(tags)
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
            industry_profile.industry_code if industry_profile else "",
            " ".join(industry_profile.peer_stock_names[:20]) if industry_profile else "",
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
        source=(
            "KOREA_STOCK_UNIVERSE+NAVER_STOCK_INDUSTRY_COMPARE"
            if industry_profile
            else "KOREA_STOCK_UNIVERSE"
        ),
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
        (
            (
                "bio",
                "biologics",
                "therapeutics",
                "pharma",
                "pharmaceutical",
                "medicine",
                "medical",
                "medtech",
                "healthcare",
                "diagnostic",
                "diagnostics",
                "hospital",
                "dental",
                "clinic",
                "life science",
                "celltrion",
                "셀트리온",
                "삼성바이오",
                "제약",
                "바이오",
                "헬스케어",
                "의료",
                "약품",
                "의약",
                "유한양행",
                "헬스",
                "메디",
                "진단",
                "병원",
                "치과",
                "알테오젠",
            ),
            "biotech",
        ),
        (("drug delivery", "hyaluronidase", "subcutaneous"), "drug delivery"),
        (
            (
                "semiconductor",
                "electronics",
                "memory",
                "dram",
                "hbm",
                "chip",
                "hynix",
                "하이닉스",
                "반도체",
                "전자",
            ),
            "semiconductors",
        ),
        (
            (
                "consumer electronics",
                "home appliance",
                "appliance",
                "lg electronics",
                "sony",
                "whirlpool",
                "가전",
                "엘지전자",
            ),
            "consumer electronics",
        ),
        (
            (
                "bank",
                "bancorp",
                "bancshares",
                "bank holding",
                "금융지주",
                "은행",
            ),
            "banking",
        ),
        (("insurance", "손해보험", "생명보험", "보험"), "insurance"),
        (
            (
                "financial",
                "finance",
                "financial group",
                "financial holding",
                "capital",
                "securities",
                "금융",
                "증권",
                "캐피탈",
            ),
            "financials",
        ),
        (("motor", "auto", "vehicle", "자동차", "모터스", "기아"), "automotive"),
        (("tire", "mobility", "타이어", "모빌리티", "오토"), "automotive"),
        (("motion", "모션", "부품"), "automotive"),
        (
            ("battery", "lg energy solution", "sdi", "삼성sdi", "배터리", "에너지솔루션", "전지"),
            "battery",
        ),
        (("electric", "electrical", "전기", "전선"), "electrical equipment"),
        (
            (
                "energy",
                "electric utility",
                "power",
                "gas",
                "oil",
                "petroleum",
                "solar",
                "renewable",
                "전력",
                "에너지",
                "가스",
                "석유",
                "정유",
                "태양광",
            ),
            "energy",
        ),
        (("steel", "metal", "스틸", "철강"), "materials"),
        (("cement", "glass", "시멘트", "유리"), "materials"),
        (("material", "materials", "소재", "메탈", "알루미늄", "페인트"), "materials"),
        (("game", "gaming", "게임"), "gaming"),
        (
            (
                "platform",
                "internet",
                "technology",
                "technologies",
                "tech",
                "software",
                "cloud",
                "search",
                "portal",
                "naver",
                "kakao",
                "플랫폼",
                "테크",
                "시스템",
                "솔루션",
                "정보",
                "소프트웨어",
                "네이버",
                "카카오",
            ),
            "software platform",
        ),
        (
            (
                "construction",
                "engineering",
                "e&c",
                "builder",
                "건설",
                "엔지니어링",
                "토건",
                "개발",
            ),
            "construction",
        ),
        (
            (
                "machinery",
                "machine",
                "industrial",
                "automation",
                "plant",
                "equipment",
                "중공업",
                "기계",
                "공업",
                "산업",
                "자동화",
                "설비",
                "두산",
            ),
            "industrial machinery",
        ),
        (
            (
                "food",
                "foods",
                "beverage",
                "restaurant",
                "brewery",
                "푸드",
                "식품",
                "제당",
                "음료",
                "주류",
                "맥주",
                "진로",
                "하이트",
                "농심",
                "오뚜기",
                "유업",
            ),
            "food and beverage",
        ),
        (
            (
                "cosmetic",
                "cosmetics",
                "beauty",
                "apparel",
                "fashion",
                "화장품",
                "코스메틱",
                "뷰티",
                "패션",
                "의류",
                "가구",
            ),
            "consumer brands",
        ),
        (
            (
                "media",
                "studio",
                "entertainment",
                "contents",
                "broadcast",
                "미디어",
                "엔터",
                "콘텐츠",
                "스튜디오",
                "방송",
            ),
            "media entertainment",
        ),
        (
            (
                "retail",
                "commerce",
                "store",
                "trading",
                "유통",
                "백화점",
                "홈쇼핑",
                "쇼핑",
                "상사",
            ),
            "retail",
        ),
        (("air", "aerospace", "항공"), "aerospace"),
        (("ship", "marine", "조선"), "shipbuilding"),
        (("chemical", "케미", "화학"), "chemicals"),
        (("telecom", "communications", "텔레콤", "통신"), "telecommunications"),
        (
            (
                "logistics",
                "shipping",
                "transport",
                "express",
                "물류",
                "운송",
                "해운",
                "택배",
                "통운",
                "고속",
                "상선",
            ),
            "logistics",
        ),
        (("reit", "real estate", "property", "리츠", "부동산"), "real estate"),
        (("education", "learning", "edu", "교육"), "education"),
        (
            (
                "hotel",
                "casino",
                "travel",
                "leisure",
                "호텔",
                "카지노",
                "여행",
                "레저",
                "골프",
            ),
            "leisure",
        ),
        (("holding", "holdings", "investment", "홀딩스", "지주", "투자"), "holding company"),
        (("paper", "packaging", "제지", "포장"), "materials"),
        (("textile", "fiber", "섬유"), "consumer brands"),
    ]
    tags = [tag for keywords, tag in rules if any(keyword in text for keyword in keywords)]
    return list(dict.fromkeys(tags or ["general listed company"]))


def infer_sector(tags: Sequence[str]) -> str:
    sector_rules = {
        "biotech": "Health Care",
        "drug delivery": "Health Care",
        "semiconductors": "Information Technology",
        "memory chips": "Information Technology",
        "consumer electronics": "Consumer Discretionary",
        "home appliances": "Consumer Discretionary",
        "electrical equipment": "Industrials",
        "banking": "Financials",
        "insurance": "Financials",
        "holding company": "Financials",
        "financials": "Financials",
        "automotive": "Consumer Discretionary",
        "battery": "Industrials",
        "energy": "Energy",
        "materials": "Materials",
        "gaming": "Communication Services",
        "software platform": "Information Technology",
        "construction": "Industrials",
        "industrial machinery": "Industrials",
        "food and beverage": "Consumer Staples",
        "consumer brands": "Consumer Staples",
        "media entertainment": "Communication Services",
        "retail": "Consumer Discretionary",
        "aerospace": "Industrials",
        "shipbuilding": "Industrials",
        "chemicals": "Materials",
        "telecommunications": "Communication Services",
        "logistics": "Industrials",
        "real estate": "Real Estate",
        "education": "Consumer Discretionary",
        "leisure": "Consumer Discretionary",
    }
    return next((sector_rules[tag] for tag in tags if tag in sector_rules), GENERIC_LISTED_SECTOR)


def infer_industry(tags: Sequence[str]) -> str:
    industry_rules = {
        "biotech": "Biotechnology",
        "drug delivery": "Drug Delivery Technology",
        "semiconductors": "Semiconductors",
        "memory chips": "Semiconductors",
        "consumer electronics": "Consumer Electronics and Appliances",
        "home appliances": "Consumer Electronics and Appliances",
        "electrical equipment": "Electrical Equipment",
        "banking": "Banks",
        "insurance": "Insurance",
        "holding company": "Investment Holding Companies",
        "financials": "Financial Services",
        "automotive": "Automobiles",
        "battery": "Battery and Energy Storage",
        "energy": "Energy Infrastructure",
        "materials": "Metals and Materials",
        "gaming": "Interactive Entertainment",
        "software platform": "Software",
        "construction": "Construction and Engineering",
        "industrial machinery": "Machinery and Industrial Equipment",
        "food and beverage": "Food and Beverage",
        "consumer brands": "Household and Personal Products",
        "media entertainment": "Media and Entertainment",
        "retail": "Retail",
        "aerospace": "Aerospace and Defense",
        "shipbuilding": "Shipbuilding",
        "chemicals": "Specialty Chemicals",
        "telecommunications": "Telecommunications",
        "logistics": "Logistics and Transportation",
        "real estate": "Real Estate",
        "education": "Education Services",
        "leisure": "Hotels, Restaurants, and Leisure",
    }
    return next(
        (industry_rules[tag] for tag in tags if tag in industry_rules),
        GENERIC_LISTED_INDUSTRY,
    )


def infer_business_model(tags: Sequence[str]) -> str:
    if "royalty licensing" in tags or "drug delivery" in tags:
        return "Technology licensing and royalties"
    if "banking" in tags:
        return "Banking, spread income, fees, and capital-market services"
    if "insurance" in tags:
        return "Insurance underwriting and financial services"
    if "memory chips" in tags:
        return "Memory semiconductor manufacturing"
    if "consumer electronics" in tags or "home appliances" in tags:
        return "Consumer electronics and appliance manufacturing"
    if "electrical equipment" in tags:
        return "Electrical equipment and components manufacturing"
    if "battery" in tags:
        return "Battery manufacturing and energy storage supply chain"
    if "semiconductors" in tags:
        return "Semiconductor manufacturing or supply chain"
    if "automotive" in tags:
        return "Automobile manufacturing and mobility supply chain"
    if "chemicals" in tags:
        return "Chemical and advanced materials manufacturing"
    if "materials" in tags:
        return "Metals, materials, and industrial inputs"
    if "software platform" in tags:
        return "Platform software and recurring services"
    if "construction" in tags:
        return "Construction, engineering, and infrastructure projects"
    if "industrial machinery" in tags:
        return "Industrial machinery and equipment manufacturing"
    if "food and beverage" in tags:
        return "Packaged food, beverage, and consumer staples"
    if "consumer brands" in tags:
        return "Branded consumer products and distribution"
    if "media entertainment" in tags:
        return "Content production, distribution, and advertising"
    if "retail" in tags:
        return "Merchandising and commerce"
    if "holding company" in tags:
        return "Investment holding and portfolio management"
    if "financials" in tags:
        return "Spread, fee, and capital-market services"
    if "telecommunications" in tags:
        return "Telecom network subscription services"
    if "logistics" in tags:
        return "Logistics, shipping, and transportation services"
    if "real estate" in tags:
        return "Real estate ownership and leasing"
    if "education" in tags:
        return "Education content and learning services"
    if "leisure" in tags:
        return "Travel, leisure, and hospitality services"
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
    if "$" in stock.ticker:
        return False
    if stock.ticker.upper() in KOREAN_ADR_TICKERS:
        return False
    name = stock.company_name.lower()
    excluded_tokens = (
        "acquisition",
        "blank check",
        "gigcapital",
        "gores holdings",
        "ordinary shares",
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
        " spac",
        " corp i ",
        " corp ii ",
        " corp iii ",
        " corp iv ",
        " corp v ",
        " corp vi ",
        " corp vii ",
        " corp viii ",
        " corp ix ",
        " corp x ",
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
            "display_name": anchor.display_name,
            "positioning_title": anchor.positioning_title,
            "preferred_peer_ticker": anchor.preferred_peer_ticker,
            "headline_template": anchor.headline_template,
            "summary": anchor.summary,
        }
        for key, anchor in anchors.items()
    }


def _split_pipe(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split("|") if item.strip())


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
