import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parents[1] / "scripts/benchmark_korean_finance_sentiment.py"
SPEC = importlib.util.spec_from_file_location("benchmark_korean_finance_sentiment", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
_locked_candidate = MODULE._locked_candidate


def test_locked_candidate_requires_selection_only_provenance() -> None:
    report = {
        "candidate_selection": {
            "locked_candidate": "kf_deberta_lora",
            "selection_partition": "VALIDATION_SELECTION",
            "test_used_for_selection": False,
            "operational_gold_used_for_selection": False,
        }
    }

    assert _locked_candidate(report, {"kf_deberta_lora"}) == "kf_deberta_lora"


@pytest.mark.parametrize(
    "field", ["test_used_for_selection", "operational_gold_used_for_selection"]
)
def test_locked_candidate_rejects_evaluation_selected_model(field: str) -> None:
    report = {
        "candidate_selection": {
            "locked_candidate": "kf_deberta_lora",
            "selection_partition": "VALIDATION_SELECTION",
            "test_used_for_selection": False,
            "operational_gold_used_for_selection": False,
        }
    }
    report["candidate_selection"][field] = True

    with pytest.raises(SystemExit, match="고정된 감성 후보"):
        _locked_candidate(report, {"kf_deberta_lora"})
