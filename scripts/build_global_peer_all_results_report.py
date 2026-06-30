import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest, MarketType
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.training.global_peer_quality import _is_same_company_noise
from hannah_montana_ai.training.global_peer_trainer import (
    GENERIC_LISTED_INDUSTRY,
    GENERIC_LISTED_SECTOR,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, load_stock_universe

VALID_MARKETS: set[str] = {"KOSPI", "KOSDAQ", "KONEX", "OTHER"}


def build_global_peer_all_results_report(
    *,
    stock_universe_path: Path,
    model_path: Path,
    report_path: Path,
    csv_path: Path,
    doc_path: Path,
) -> dict[str, object]:
    stocks = load_stock_universe(stock_universe_path)
    matcher = GlobalPeerMatcher(model_path)
    rows: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []

    for stock in stocks:
        try:
            response = matcher.match(_request_for(stock))
        except Exception as exception:  # pragma: no cover - 전체 리포트에 실패를 남긴다.
            failures.append(
                {
                    "stock_code": stock.stock_code,
                    "stock_name": stock.stock_name,
                    "error": type(exception).__name__,
                    "message": str(exception),
                }
            )
            continue

        primary = response.primary_peer
        stock_profile = matcher._korea_profiles.get(stock.stock_code, {})
        source_sector = str(stock_profile.get("sector") or "")
        source_industry = str(stock_profile.get("industry") or "")
        source_business_model = str(stock_profile.get("business_model") or "")
        row = {
            "stock_code": stock.stock_code,
            "stock_name": stock.stock_name,
            "stock_name_en": response.stock_name_en,
            "market": stock.market or "KOSPI",
            "source_sector": source_sector,
            "source_industry": source_industry,
            "source_business_model": source_business_model,
            "primary_peer_ticker": primary.ticker,
            "primary_peer_name": primary.company_name,
            "primary_peer_sector": primary.sector,
            "primary_peer_industry": primary.industry,
            "primary_peer_business_model": primary.business_model,
            "primary_peer_scale_bucket": primary.scale_bucket,
            "similarity_score": primary.similarity_score,
            "confidence_score": response.confidence_score,
            "confidence_level": response.confidence_level,
            "financial_similarity_score": primary.financial_similarity_score,
            "domain_match_level": _domain_match_level(
                source_sector,
                source_industry,
                source_business_model,
                primary.sector,
                primary.industry,
                primary.business_model,
            ),
            "confidence_root_cause": _confidence_root_cause(
                confidence_level=response.confidence_level,
                source_sector=source_sector,
                source_industry=source_industry,
                peer_sector=primary.sector,
                peer_industry=primary.industry,
                financial_similarity_score=primary.financial_similarity_score,
            ),
            "financial_context": _financial_context(primary.matched_factors),
            "same_company_noise": _is_same_company_noise(stock, primary.company_name),
            "matched_factors": primary.matched_factors,
            "headline": response.headline,
            "summary": response.summary,
            "model_version": response.model_version,
            "source": response.source,
            "explanation_source": response.explanation_source,
            "explanation_model_version": response.explanation_model_version,
            "explanation_prompt_version": response.explanation_prompt_version,
        }
        rows.append(row)

    report = _report(
        model_version=matcher.version,
        stock_universe_path=stock_universe_path,
        model_path=model_path,
        rows=rows,
        failures=failures,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _write_csv(csv_path, rows)
    _write_markdown(doc_path, report)
    return report


def _request_for(stock: StockUniverseEntry) -> GlobalPeerMatchRequest:
    market = stock.market if stock.market in VALID_MARKETS else "KOSPI"
    return GlobalPeerMatchRequest(
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        stock_name_en=stock.stock_name_en,
        market=cast(MarketType, market),
        aliases=list(stock.aliases),
        peer_count=5,
    )


def _domain_match_level(
    source_sector: str,
    source_industry: str,
    source_business_model: str,
    peer_sector: str,
    peer_industry: str,
    peer_business_model: str,
) -> str:
    generic_sectors = {"", "Unclassified", GENERIC_LISTED_SECTOR}
    generic_industries = {"", "Unclassified", GENERIC_LISTED_INDUSTRY}
    if source_industry not in generic_industries and source_industry == peer_industry:
        if source_business_model == peer_business_model:
            return "industry_and_business_model"
        return "industry"
    if source_sector not in generic_sectors and source_sector == peer_sector:
        return "sector"
    return "generic_or_mismatch"


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
    generic_sectors = {"", "Unclassified", GENERIC_LISTED_SECTOR}
    generic_industries = {"", "Unclassified", GENERIC_LISTED_INDUSTRY}
    if source_sector in generic_sectors or source_industry in generic_industries:
        return "source_profile_generic_or_legacy"
    if source_sector != peer_sector or source_industry != peer_industry:
        return "domain_mismatch"
    if financial_similarity_score is None:
        return "domain_match_financial_missing"
    return "domain_match_but_weak_model_score"


def _financial_context(factors: list[str]) -> str:
    joined = " ".join(factors)
    if "direct market cap" in joined:
        return "direct_financial_similarity"
    if "partial direct similarity" in joined:
        return "partial_direct_similarity"
    if "relative US-market positioning" in joined:
        return "us_market_relative_proxy"
    if "not a direct balance-sheet match" in joined:
        return "domain_first_proxy"
    return "not_available"


def _report(
    *,
    model_version: str,
    stock_universe_path: Path,
    model_path: Path,
    rows: list[dict[str, object]],
    failures: list[dict[str, str]],
) -> dict[str, object]:
    attempted_count = len(rows) + len(failures)
    success_count = len(rows)
    confidence_counts = Counter(str(row["confidence_level"]) for row in rows)
    domain_counts = Counter(str(row["domain_match_level"]) for row in rows)
    root_cause_counts = Counter(str(row["confidence_root_cause"]) for row in rows)
    financial_context_counts = Counter(str(row["financial_context"]) for row in rows)
    generic_or_mismatch_count = domain_counts["generic_or_mismatch"]
    low_count = confidence_counts["LOW"]
    specific_profile_rows = [
        row
        for row in rows
        if str(row["confidence_root_cause"]) != "source_profile_generic_or_legacy"
    ]
    specific_profile_count = len(specific_profile_rows)
    specific_profile_low_count = sum(
        1 for row in specific_profile_rows if row["confidence_level"] == "LOW"
    )
    specific_profile_low_ratio = (
        specific_profile_low_count / specific_profile_count if specific_profile_count else 1.0
    )
    same_company_noise_count = sum(1 for row in rows if bool(row["same_company_noise"]))
    performance = {
        "attempted_count": attempted_count,
        "success_count": success_count,
        "failure_count": len(failures),
        "success_ratio": round(success_count / attempted_count, 6) if attempted_count else 0.0,
        "confidence_distribution": dict(sorted(confidence_counts.items())),
        "low_confidence_ratio": round(low_count / success_count, 6) if success_count else 1.0,
        "domain_match_distribution": dict(sorted(domain_counts.items())),
        "confidence_root_cause_distribution": dict(sorted(root_cause_counts.items())),
        "generic_or_mismatch_ratio": (
            round(generic_or_mismatch_count / success_count, 6) if success_count else 1.0
        ),
        "financial_context_distribution": dict(sorted(financial_context_counts.items())),
        "specific_profile_quality": {
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
        },
        "same_company_noise_count": same_company_noise_count,
        "quality_status": (
            "pass"
            if success_count == attempted_count
            and low_count / success_count < 0.35
            and same_company_noise_count == 0
            else "fail"
        ),
    }
    return {
        "schema_version": "global-peer-all-results/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "model_version": model_version,
        "stock_universe_path": str(stock_universe_path),
        "model_path": str(model_path),
        "performance": performance,
        "failures": failures,
        "results": rows,
    }


def _write_csv(csv_path: Path, rows: list[dict[str, object]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "stock_code",
        "stock_name",
        "stock_name_en",
        "market",
        "source_sector",
        "source_industry",
        "source_business_model",
        "primary_peer_ticker",
        "primary_peer_name",
        "primary_peer_sector",
        "primary_peer_industry",
        "primary_peer_business_model",
        "primary_peer_scale_bucket",
        "similarity_score",
        "confidence_score",
        "confidence_level",
        "financial_similarity_score",
        "domain_match_level",
        "confidence_root_cause",
        "financial_context",
        "same_company_noise",
        "matched_factors",
        "headline",
        "model_version",
        "source",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        " | ".join(cast(list[str], row[key]))
                        if key == "matched_factors"
                        else row.get(key, "")
                    )
                    for key in fieldnames
                }
            )


def _write_markdown(doc_path: Path, report: dict[str, object]) -> None:
    performance = cast(dict[str, object], report["performance"])
    rows = cast(list[dict[str, object]], report["results"])
    lines = [
        "# 글로벌 피어 전종목 현재 결과",
        "",
        "## 성능 요약",
        f"- 모델 버전: `{report['model_version']}`",
        f"- 시도/성공/실패: {performance['attempted_count']} / "
        f"{performance['success_count']} / {performance['failure_count']}",
        f"- 성공률: {performance['success_ratio']}",
        f"- confidence 분포: {performance['confidence_distribution']}",
        f"- LOW confidence 비율: {performance['low_confidence_ratio']}",
        f"- domain match 분포: {performance['domain_match_distribution']}",
        f"- confidence root cause 분포: {performance['confidence_root_cause_distribution']}",
        f"- generic/mismatch 비율: {performance['generic_or_mismatch_ratio']}",
        f"- financial context 분포: {performance['financial_context_distribution']}",
        f"- specific profile 품질: {performance['specific_profile_quality']}",
        f"- 동일회사 중복 노이즈: {performance['same_company_noise_count']}",
        f"- quality status: `{performance['quality_status']}`",
        "",
        "## 전체 종목 결과",
        (
            "| 종목코드 | 종목명 | 원천 세부 분야 | primary peer | confidence | "
            "domain match | confidence root cause | financial context |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['stock_code']} | "
            f"{_escape_markdown(str(row['stock_name']))} | "
            f"{_escape_markdown(str(row['source_industry']))} | "
            f"{row['primary_peer_ticker']} {_escape_markdown(str(row['primary_peer_name']))} | "
            f"{row['confidence_level']} {row['confidence_score']} | "
            f"{row['domain_match_level']} | "
            f"{row['confidence_root_cause']} | "
            f"{row['financial_context']} |"
        )
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    settings = get_settings()
    result = build_global_peer_all_results_report(
        stock_universe_path=settings.stock_universe_path,
        model_path=settings.global_peer_model_path,
        report_path=settings.global_peer_all_results_report_path,
        csv_path=settings.global_peer_all_results_csv_path,
        doc_path=settings.global_peer_all_results_doc_path,
    )
    performance = cast(dict[str, object], result["performance"])
    print(
        "글로벌 피어 전종목 결과 저장 완료: "
        f"{performance['success_count']}/{performance['attempted_count']}개, "
        f"quality={performance['quality_status']}"
    )
