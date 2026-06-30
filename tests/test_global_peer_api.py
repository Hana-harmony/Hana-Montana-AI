from fastapi.testclient import TestClient

from hannah_montana_ai.main import app


def test_global_peer_match_api_returns_alteogen_halozyme_popup_copy() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/market/global-peers/match",
        json={
            "stock_code": "196170",
            "stock_name": "알테오젠",
            "stock_name_en": "Alteogen",
            "market": "KOSDAQ",
            "peer_count": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["primary_peer"]["ticker"] == "HALO"
    assert data["headline"].startswith("Alteogen Is The 'Halozyme Therapeutics'")
    assert data["source"] == "HANNAH_GLOBAL_PEER_HYBRID_RANKER"
    assert data["explanation_source"] == "GROUNDED_TEMPLATE_STRUCTURED_RAG"
    assert data["explanation_prompt_version"] == "global-peer-structured-rag-explainer-v3"
