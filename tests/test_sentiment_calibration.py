import pytest

from hannah_montana_ai.services.sentiment_calibration import apply_source_logit_bias


def test_source_logit_bias_is_normalized_and_source_specific() -> None:
    probabilities = {"NEGATIVE": 0.2, "NEUTRAL": 0.6, "POSITIVE": 0.2}
    calibrated = apply_source_logit_bias(
        probabilities,
        "DISCLOSURE",
        {
            "DISCLOSURE": {
                "NEGATIVE": 0.0,
                "NEUTRAL": 0.0,
                "POSITIVE": 1.0,
            }
        },
    )

    assert sum(calibrated.values()) == pytest.approx(1.0)
    assert calibrated["POSITIVE"] > probabilities["POSITIVE"]
    assert apply_source_logit_bias(probabilities, "NEWS", {}) is probabilities
