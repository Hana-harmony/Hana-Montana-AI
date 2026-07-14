import pytest

from hannah_montana_ai.training.evaluator import _macro_f1, _single_label_metrics


def test_single_label_metrics_exposes_class_imbalance() -> None:
    metrics = _single_label_metrics(
        [
            ("NEGATIVE", "NEGATIVE"),
            ("NEUTRAL", "NEGATIVE"),
            ("POSITIVE", "POSITIVE"),
        ]
    )

    assert metrics["NEGATIVE"].precision == pytest.approx(0.5)
    assert metrics["NEGATIVE"].recall == pytest.approx(1.0)
    assert metrics["NEUTRAL"].f1 == 0.0
    assert metrics["POSITIVE"].f1 == 1.0
    assert _macro_f1(metrics) == pytest.approx(5 / 9)


def test_single_label_metrics_preserves_expected_support() -> None:
    metrics = _single_label_metrics(
        [("LOW", "LOW"), ("LOW", "MEDIUM"), ("HIGH", "HIGH")],
        ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
    )

    assert metrics["LOW"].support == 2
    assert metrics["MEDIUM"].support == 0
    assert metrics["HIGH"].support == 1
    assert metrics["CRITICAL"].support == 0
