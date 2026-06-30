import json
from pathlib import Path

from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.training.global_peer_trainer import load_us_stock_universe


def test_us_stock_universe_covers_full_listed_symbol_directory() -> None:
    entries = load_us_stock_universe(Path("data/reference/us_stock_universe.csv"))

    assert len(entries) >= 5_000
    assert any(entry.ticker == "HALO" for entry in entries)


def test_global_peer_model_matches_alteogen_to_halozyme() -> None:
    matcher = GlobalPeerMatcher(Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib"))

    response = matcher.match(
        GlobalPeerMatchRequest(
            stock_code="196170",
            stock_name="알테오젠",
            stock_name_en="Alteogen",
            market="KOSDAQ",
        )
    )

    assert response.primary_peer.ticker == "HALO"
    assert response.primary_peer.company_name == "Halozyme Therapeutics"
    assert response.primary_peer.sector == "Health Care"
    assert response.primary_peer.industry == "Biotechnology"
    assert response.primary_peer.business_model == "Biotech platform licensing"
    assert response.primary_peer.scale_bucket == "MID_CAP"
    assert response.primary_peer.revenue_usd is not None
    assert response.primary_peer.operating_income_usd is not None
    assert "SEC_COMPANYFACTS" in response.primary_peer.financial_data_source
    assert "NASDAQ_SUMMARY_MARKET_CAP" in response.primary_peer.financial_data_source
    assert response.primary_peer.financial_similarity_score is not None
    assert any("Sector" in factor for factor in response.primary_peer.matched_factors)
    assert any("Scale" in factor for factor in response.primary_peer.matched_factors)
    assert any("Financial similarity" in factor for factor in response.primary_peer.matched_factors)
    assert response.confidence_level in {"MEDIUM", "HIGH"}
    assert "Alteogen Is The 'Halozyme Therapeutics'" in response.headline
    assert "drug-delivery technology" in response.summary
    assert response.model_version.startswith("global-peer-hybrid-ranker-")


def test_global_peer_model_quality_smoke_matches_core_korean_stocks() -> None:
    matcher = GlobalPeerMatcher(Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib"))
    cases = [
        ("005930", "삼성전자", "Samsung Electronics", "KOSPI", "MU"),
        ("000660", "SK하이닉스", "SK hynix", "KOSPI", "MU"),
        ("035420", "NAVER", "NAVER", "KOSPI", "GOOGL"),
        ("017670", "SK텔레콤", "SK Telecom", "KOSPI", "VZ"),
        ("066570", "LG전자", "LG Electronics", "KOSPI", "WHR"),
        ("373220", "LG에너지솔루션", "LG Energy Solution", "KOSPI", "TSLA"),
    ]

    for stock_code, stock_name, stock_name_en, market, expected_ticker in cases:
        response = matcher.match(
            GlobalPeerMatchRequest(
                stock_code=stock_code,
                stock_name=stock_name,
                stock_name_en=stock_name_en,
                market=market,
            )
        )

        assert response.primary_peer.ticker == expected_ticker
        assert response.primary_peer.ticker not in {stock_name_en, stock_name}
        assert response.primary_peer.sector != "Unclassified"
        assert response.primary_peer.industry != "Unclassified"
        assert response.primary_peer.matched_factors


def test_global_peer_model_prioritizes_domain_and_explains_financial_context() -> None:
    matcher = GlobalPeerMatcher(Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib"))

    response = matcher.match(
        GlobalPeerMatchRequest(
            stock_code="035420",
            stock_name="NAVER",
            stock_name_en="NAVER",
            market="KOSPI",
        )
    )

    factors = response.primary_peer.matched_factors
    assert response.primary_peer.ticker == "GOOGL"
    assert factors[0] == "Sector: both are mapped to Information Technology."
    assert factors[1] == "Industry: both are mapped to Internet Platforms."
    assert any("scale differs" in factor for factor in factors)
    assert any("relative US-market positioning" in factor for factor in factors)


def test_global_peer_request_accepts_krx_alphanumeric_stock_codes() -> None:
    request = GlobalPeerMatchRequest(
        stock_code="0001A0",
        stock_name="덕양에너젠",
        market="KOSPI",
    )

    assert request.stock_code == "0001A0"


def test_global_peer_full_coverage_report_passes_all_stock_gate() -> None:
    report = json.loads(Path("reports/global-peer-full-coverage-report.json").read_text())

    assert report["schema_version"] == "global-peer-full-coverage/v1"
    assert report["attempted_count"] >= 3_000
    assert report["attempted_count"] == report["success_count"]
    assert report["failure_count"] == 0
    assert report["quality_gate"]["status"] == "pass"
    assert report["confidence_monitoring"]["status"] == "pass"
    assert report["confidence_monitoring"]["actual_low_confidence_ratio"] < 0.35
    assert report["same_company_noise_count"] == 0
    assert report["matched_factor_missing_count"] == 0


def test_global_peer_all_results_report_documents_every_stock() -> None:
    report = json.loads(Path("reports/global-peer-all-results.json").read_text())

    assert report["schema_version"] == "global-peer-all-results/v1"
    assert report["performance"]["attempted_count"] >= 3_000
    assert report["performance"]["attempted_count"] == report["performance"]["success_count"]
    assert report["performance"]["failure_count"] == 0
    assert report["performance"]["quality_status"] == "pass"
    assert report["performance"]["low_confidence_ratio"] < 0.35
    assert len(report["results"]) == report["performance"]["success_count"]
    assert Path("docs/GLOBAL_PEER_ALL_RESULTS.md").exists()
    assert Path("reports/global-peer-all-results.csv").exists()
