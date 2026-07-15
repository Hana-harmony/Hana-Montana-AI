from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def assert_close(actual: float, expected: float, label: str) -> None:
    if abs(actual - expected) > 5e-5:
        raise AssertionError(f"{label}: expected={expected}, actual={actual}")


def main() -> None:
    manifest = load("data/k_fnspid/v4/manifest.json")
    sentiment = load("reports/korean-finance-sentiment-benchmark.json")
    impact = load("reports/k-fnspid-research-evaluation.json")
    disclosure_multiseed = load(
        "reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json"
    )
    disclosure = load("reports/disclosure-importance-research-evaluation.json")

    expected_counts = {
        "document_count": 1_247_685,
        "entity_count": 1_136_118,
        "impact_count": 715_015,
        "unconfounded_impact_count": 255_168,
    }
    for key, expected in expected_counts.items():
        actual = manifest[key]
        if actual != expected:
            raise AssertionError(f"manifest.{key}: expected={expected}, actual={actual}")

    if manifest["source_type_count"] != {"DISCLOSURE": 722_989, "NEWS": 524_696}:
        raise AssertionError("source_type_count changed")
    if manifest["full_text_source_type_count"]["DISCLOSURE"] != 8_972:
        raise AssertionError("disclosure full-text count changed")

    assert_close(sentiment["models"]["kr_finbert_sc"]["macro_f1"], 0.7272, "KR-FinBERT-SC macro-F1")
    assert_close(sentiment["models"]["kf_deberta_lora"]["macro_f1"], 0.8850, "KF-DeBERTa macro-F1")
    assert_close(impact["baseline"]["macro_f1"], 0.3210, "market baseline macro-F1")
    assert_close(impact["transformer"]["macro_f1"], 0.3690, "market Transformer macro-F1")
    assert_close(impact["source_type"]["NEWS"]["transformer"]["macro_f1"], 0.3745, "news macro-F1")
    assert_close(
        impact["source_type"]["DISCLOSURE"]["transformer"]["macro_f1"],
        0.3216,
        "disclosure macro-F1",
    )
    if disclosure_multiseed["selected_seed_by_validation"] != 17:
        raise AssertionError("selected disclosure market-impact seed changed")
    assert_close(
        disclosure_multiseed["test"]["macro_f1"]["sample_std"],
        0.0052,
        "disclosure three-seed macro-F1 std",
    )
    if not impact["research_gate"]["eligible_for_superiority_claim"]:
        raise AssertionError("source-routed superiority gate failed")
    assert_close(disclosure["candidate"]["macro_f1"], 0.9962, "disclosure operational macro-F1")

    print("submission metrics verified against frozen reports")


if __name__ == "__main__":
    main()
