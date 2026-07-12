from hannah_montana_ai.services.market_impact_model import (
    MarketImpactPrediction,
    blend_importance,
)


def test_blend_upgrades_only_one_level_for_high_confidence_market_signal() -> None:
    prediction = MarketImpactPrediction(
        importance="CRITICAL",
        confidence=0.8,
        materiality_score=0.9,
        model_version="impact-v1",
    )

    importance, confidence = blend_importance("LOW", 0.6, prediction)

    assert importance == "MEDIUM"
    assert confidence == 0.8


def test_blend_keeps_semantic_importance_when_market_signal_is_uncertain() -> None:
    prediction = MarketImpactPrediction(
        importance="HIGH",
        confidence=0.4,
        materiality_score=0.5,
        model_version="impact-v1",
    )

    importance, confidence = blend_importance("MEDIUM", 0.7, prediction)

    assert importance == "MEDIUM"
    assert confidence == 0.49
