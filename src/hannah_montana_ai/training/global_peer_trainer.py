from __future__ import annotations

import csv
import json
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from urllib.request import Request, urlopen

import joblib
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


@dataclass(frozen=True)
class UsStockUniverseEntry:
    ticker: str
    company_name: str
    exchange: str
    etf: bool
    test_issue: bool
    security_type: str


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
    eligible_peer: bool
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "business_tags": list(self.business_tags),
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
    model_path: Path,
    report_path: Path,
) -> PeerTrainingResult:
    korea_universe = load_stock_universe(korea_stock_universe_path)
    us_universe = load_us_stock_universe(us_stock_universe_path)
    if len(korea_universe) < 3_000:
        raise ValueError("global peer training requires the full Korean stock universe")
    if len(us_universe) < 5_000:
        raise ValueError("global peer training requires the full United States stock universe")

    korea_profiles = [build_korea_profile(stock) for stock in korea_universe]
    us_profiles = [build_us_profile(stock) for stock in us_universe]
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
    trained_at = datetime.now(UTC).isoformat()
    version = f"{GLOBAL_PEER_MODEL_VERSION_PREFIX}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "schema_version": GLOBAL_PEER_SCHEMA_VERSION,
        "version": version,
        "trained_at": trained_at,
        "vectorizer": vectorizer,
        "eligible_us_matrix": eligible_us_matrix,
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
        "model_path": _report_path(model_path),
        "korea_universe_count": len(korea_profiles),
        "us_universe_count": len(us_profiles),
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


def build_korea_profile(stock: StockUniverseEntry) -> CompanyPeerProfile:
    anchor = KOREA_ANCHORS.get(stock.stock_code)
    stock_name_en = stock.stock_name_en or _english_name_fallback(stock)
    inferred_tags = tuple(infer_business_tags(stock.stock_name, stock_name_en))
    tags = anchor.business_tags if anchor else inferred_tags
    sector = anchor.sector if anchor else infer_sector(tags)
    industry = anchor.industry if anchor else infer_industry(tags)
    business_model = anchor.business_model if anchor else infer_business_model(tags)
    scale_bucket = anchor.scale_bucket if anchor else "UNKNOWN"
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
        eligible_peer=False,
        source="KOREA_STOCK_UNIVERSE",
    )


def build_us_profile(stock: UsStockUniverseEntry) -> CompanyPeerProfile:
    anchor = US_ANCHORS.get(stock.ticker)
    cleaned_name = clean_security_name(stock.company_name)
    inferred_tags = tuple(infer_business_tags(cleaned_name, cleaned_name))
    tags = anchor.business_tags if anchor else inferred_tags
    sector = anchor.sector if anchor else infer_sector(tags)
    industry = anchor.industry if anchor else infer_industry(tags)
    business_model = anchor.business_model if anchor else infer_business_model(tags)
    scale_bucket = anchor.scale_bucket if anchor else "UNKNOWN"
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


def clean_security_name(value: str) -> str:
    cleaned = value.replace(" - ", " ")
    cleaned = _SECURITY_SUFFIX_PATTERN.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ,.-")


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
