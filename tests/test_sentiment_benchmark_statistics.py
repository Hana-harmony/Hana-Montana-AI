from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_script() -> ModuleType:
    path = Path("scripts/benchmark_korean_finance_sentiment.py")
    spec = importlib.util.spec_from_file_location("benchmark_korean_finance_sentiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_metrics_report_fixed_label_level_results() -> None:
    module = _load_script()

    result = module._metrics(
        ["NEGATIVE", "NEUTRAL", "POSITIVE"],
        ["NEGATIVE", "NEUTRAL", "NEUTRAL"],
    )

    assert list(result["label_metrics"]) == list(module.LABEL_ORDER)
    assert result["label_metrics"]["POSITIVE"]["recall"] == 0.0
    assert result["label_metrics"]["POSITIVE"]["support"] == 1


def test_paired_comparison_detects_clear_candidate_gain() -> None:
    module = _load_script()
    module.BOOTSTRAP_SAMPLES = 200
    expected = ["NEGATIVE", "NEUTRAL", "POSITIVE"] * 20
    reference = ["NEUTRAL"] * len(expected)
    candidate = expected.copy()

    result = module._paired_comparison(expected, reference, candidate)

    assert result["macro_f1_difference_95_ci"]["low"] > 0
    assert result["mcnemar_exact"]["p_value"] < 0.001
    assert result["statistically_significant_macro_f1_gain"] is True
