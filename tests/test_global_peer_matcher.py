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
    assert any("Sector" in factor for factor in response.primary_peer.matched_factors)
    assert any("Scale" in factor for factor in response.primary_peer.matched_factors)
    assert response.confidence_level in {"MEDIUM", "HIGH"}
    assert "Alteogen Is The 'Halozyme Therapeutics'" in response.headline
    assert "drug-delivery technology" in response.summary
    assert response.model_version.startswith("global-peer-tfidf-")
