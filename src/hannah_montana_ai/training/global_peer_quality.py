from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest, MarketType
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.training.global_peer_trainer import (
    GENERIC_LISTED_INDUSTRY,
    GENERIC_LISTED_SECTOR,
    normalize_profile_text,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, load_stock_universe

GLOBAL_PEER_FULL_COVERAGE_SCHEMA_VERSION = "global-peer-full-coverage/v1"
_VALID_MARKETS: set[str] = {"KOSPI", "KOSDAQ", "KONEX", "OTHER"}


def build_global_peer_full_coverage_report(
    *,
    stock_universe_path: Path,
    model_path: Path,
    report_path: Path,
    sample_limit: int | None = None,
) -> dict[str, Any]:
    stocks = load_stock_universe(stock_universe_path)
    selected_stocks = stocks[:sample_limit] if sample_limit else stocks
    matcher = GlobalPeerMatcher(model_path)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for stock in selected_stocks:
        try:
            response = matcher.match(_request_for(stock))
        except Exception as exception:  # pragma: no cover - 리포트에 실패 원인을 남긴다.
            failures.append(
                {
                    "stock_code": stock.stock_code,
                    "stock_name": stock.stock_name,
                    "error": type(exception).__name__,
                    "message": str(exception),
                }
            )
            continue

        primary_peer = response.primary_peer
        stock_profile = matcher._korea_profiles.get(stock.stock_code, {})
        source_sector = str(stock_profile.get("sector") or "Unclassified")
        source_industry = str(stock_profile.get("industry") or "Unclassified")
        source_business_model = str(stock_profile.get("business_model") or "Operating company")
        rows.append(
            {
                "stock_code": stock.stock_code,
                "stock_name": stock.stock_name,
                "stock_name_en": stock.stock_name_en,
                "primary_peer_ticker": primary_peer.ticker,
                "primary_peer_name": primary_peer.company_name,
                "confidence_score": response.confidence_score,
                "confidence_level": response.confidence_level,
                "source_sector": source_sector,
                "source_industry": source_industry,
                "source_business_model": source_business_model,
                "confidence_root_cause": _confidence_root_cause(
                    confidence_level=response.confidence_level,
                    source_sector=source_sector,
                    source_industry=source_industry,
                    peer_sector=primary_peer.sector,
                    peer_industry=primary_peer.industry,
                    financial_similarity_score=primary_peer.financial_similarity_score,
                ),
                "sector": primary_peer.sector,
                "industry": primary_peer.industry,
                "business_model": primary_peer.business_model,
                "scale_bucket": primary_peer.scale_bucket,
                "financial_similarity_score": primary_peer.financial_similarity_score,
                "matched_factor_count": len(primary_peer.matched_factors),
                "same_company_noise": _is_same_company_noise(stock, primary_peer.company_name),
            }
        )

    report = _report(
        matcher=matcher,
        stock_count=len(selected_stocks),
        rows=rows,
        failures=failures,
        stock_universe_path=stock_universe_path,
        model_path=model_path,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def _confidence_root_cause(
    *,
    confidence_level: str,
    source_sector: str,
    source_industry: str,
    peer_sector: str,
    peer_industry: str,
    financial_similarity_score: float | None,
) -> str:
    if confidence_level != "LOW":
        return "not_low_confidence"
    generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
    generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
    if source_sector in generic_sectors or source_industry in generic_industries:
        return "source_profile_generic_or_legacy"
    if source_sector != peer_sector or source_industry != peer_industry:
        return "domain_mismatch"
    if financial_similarity_score is None:
        return "domain_match_financial_missing"
    return "domain_match_but_weak_model_score"


def _request_for(stock: StockUniverseEntry) -> GlobalPeerMatchRequest:
    market = stock.market if stock.market in _VALID_MARKETS else "KOSPI"
    return GlobalPeerMatchRequest(
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        stock_name_en=stock.stock_name_en,
        market=cast(MarketType, market),
        aliases=list(stock.aliases),
        peer_count=5,
    )


def _is_same_company_noise(stock: StockUniverseEntry, peer_name: str) -> bool:
    source_names = [stock.stock_name, stock.stock_name_en, *stock.aliases]
    normalized_peer = normalize_profile_text(peer_name)
    return any(
        len(normalized_source) >= 4
        and (
            normalized_source == normalized_peer
            or normalized_source in normalized_peer
            or normalized_peer in normalized_source
        )
        for source_name in source_names
        if (normalized_source := normalize_profile_text(source_name))
    )


def _report(
    *,
    matcher: GlobalPeerMatcher,
    stock_count: int,
    rows: list[dict[str, Any]],
    failures: list[dict[str, str]],
    stock_universe_path: Path,
    model_path: Path,
) -> dict[str, Any]:
    confidence_counts = Counter(str(row["confidence_level"]) for row in rows)
    sector_counts = Counter(str(row["sector"]) for row in rows)
    industry_counts = Counter(str(row["industry"]) for row in rows)
    peer_counts = Counter(str(row["primary_peer_ticker"]) for row in rows)
    root_cause_counts = Counter(str(row["confidence_root_cause"]) for row in rows)
    generic_sector_count = sector_counts[GENERIC_LISTED_SECTOR] + sector_counts["Unclassified"]
    generic_industry_count = (
        industry_counts[GENERIC_LISTED_INDUSTRY] + industry_counts["Unclassified"]
    )
    matched_factor_missing_count = sum(1 for row in rows if int(row["matched_factor_count"]) == 0)
    same_company_noise_count = sum(1 for row in rows if bool(row["same_company_noise"]))
    low_confidence_count = confidence_counts["LOW"]
    success_count = len(rows)
    specific_profile_rows = [
        row
        for row in rows
        if str(row["confidence_root_cause"]) != "source_profile_generic_or_legacy"
    ]
    specific_profile_count = len(specific_profile_rows)
    specific_profile_low_count = sum(
        1 for row in specific_profile_rows if row["confidence_level"] == "LOW"
    )
    attempted_count = stock_count
    success_ratio = success_count / attempted_count if attempted_count else 0.0
    generic_sector_ratio = generic_sector_count / success_count if success_count else 1.0
    low_confidence_ratio = low_confidence_count / success_count if success_count else 1.0
    specific_profile_low_ratio = (
        specific_profile_low_count / specific_profile_count if specific_profile_count else 1.0
    )
    same_company_noise_ratio = same_company_noise_count / success_count if success_count else 1.0
    matched_factor_missing_ratio = (
        matched_factor_missing_count / success_count if success_count else 1.0
    )
    quality_gate: dict[str, Any] = {
        "minimum_attempted_count": 3_000,
        "actual_attempted_count": attempted_count,
        "minimum_success_ratio": 1.0,
        "actual_success_ratio": round(success_ratio, 6),
        "maximum_same_company_noise_ratio": 0.0,
        "actual_same_company_noise_ratio": round(same_company_noise_ratio, 6),
        "maximum_matched_factor_missing_ratio": 0.0,
        "actual_matched_factor_missing_ratio": round(matched_factor_missing_ratio, 6),
    }
    quality_gate["status"] = (
        "pass"
        if attempted_count >= int(quality_gate["minimum_attempted_count"])
        and success_ratio >= float(quality_gate["minimum_success_ratio"])
        and same_company_noise_ratio <= float(quality_gate["maximum_same_company_noise_ratio"])
        and matched_factor_missing_ratio
        <= float(quality_gate["maximum_matched_factor_missing_ratio"])
        else "fail"
    )
    confidence_monitoring = {
        "maximum_low_confidence_ratio": 0.35,
        "actual_low_confidence_ratio": round(low_confidence_ratio, 6),
        "maximum_generic_sector_ratio": 0.85,
        "actual_generic_sector_ratio": round(generic_sector_ratio, 6),
        "status": (
            "pass"
            if low_confidence_ratio <= 0.35 and generic_sector_ratio <= 0.85
            else "needs_improvement"
        ),
    }
    specific_profile_quality = {
        "profile_definition": "source sector/industry가 generic legacy fallback이 아닌 종목",
        "minimum_profile_count": 2_500,
        "actual_profile_count": specific_profile_count,
        "maximum_low_confidence_ratio": 0.02,
        "actual_low_confidence_ratio": round(specific_profile_low_ratio, 6),
        "low_confidence_count": specific_profile_low_count,
        "status": (
            "pass"
            if specific_profile_count >= 2_500 and specific_profile_low_ratio <= 0.02
            else "needs_improvement"
        ),
    }
    return {
        "schema_version": GLOBAL_PEER_FULL_COVERAGE_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "model_version": matcher.version,
        "stock_universe_path": str(stock_universe_path),
        "model_path": str(model_path),
        "attempted_count": attempted_count,
        "success_count": success_count,
        "failure_count": len(failures),
        "unique_primary_peer_count": len(peer_counts),
        "confidence_distribution": dict(sorted(confidence_counts.items())),
        "sector_distribution": dict(sector_counts.most_common()),
        "industry_distribution": dict(industry_counts.most_common()),
        "top_primary_peers": [
            {"ticker": ticker, "count": count} for ticker, count in peer_counts.most_common(30)
        ],
        "confidence_root_cause_distribution": dict(sorted(root_cause_counts.items())),
        "generic_sector_count": generic_sector_count,
        "generic_industry_count": generic_industry_count,
        "low_confidence_count": low_confidence_count,
        "same_company_noise_count": same_company_noise_count,
        "matched_factor_missing_count": matched_factor_missing_count,
        "quality_gate": quality_gate,
        "confidence_monitoring": confidence_monitoring,
        "specific_profile_quality": specific_profile_quality,
        "failures": failures[:50],
        "low_confidence_samples": [row for row in rows if row["confidence_level"] == "LOW"][:50],
        "generic_sector_samples": [
            row for row in rows if row["sector"] in {GENERIC_LISTED_SECTOR, "Unclassified"}
        ][:50],
        "same_company_noise_samples": [row for row in rows if bool(row["same_company_noise"])][:50],
    }
