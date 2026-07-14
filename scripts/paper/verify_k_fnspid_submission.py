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
    manifest = load("data/k_fnspid/v3/manifest.json")
    sentiment = load("reports/korean-finance-sentiment-benchmark.json")
    impact = load("reports/k-fnspid-research-evaluation.json")
    multiseed = load("reports/k-fnspid-transformer-multiseed-report.json")
    disclosure = load("reports/disclosure-importance-research-evaluation.json")

    expected_counts = {
        "document_count": 550_662,
        "entity_count": 819_772,
        "impact_count": 398_942,
        "unconfounded_impact_count": 130_566,
    }
    for key, expected in expected_counts.items():
        actual = manifest[key]
        if actual != expected:
            raise AssertionError(f"manifest.{key}: expected={expected}, actual={actual}")

    if manifest["source_type_count"] != {"DISCLOSURE": 25_966, "NEWS": 524_696}:
        raise AssertionError("source_type_count changed")
    if manifest["full_text_source_type_count"]["DISCLOSURE"] != 8_972:
        raise AssertionError("disclosure full-text count changed")

    assert_close(sentiment["models"]["kr_finbert_sc"]["macro_f1"], 0.7272, "KR-FinBERT-SC macro-F1")
    assert_close(sentiment["models"]["kf_deberta_lora"]["macro_f1"], 0.8850, "KF-DeBERTa macro-F1")
    assert_close(impact["baseline"]["macro_f1"], 0.3429, "market baseline macro-F1")
    assert_close(impact["transformer"]["macro_f1"], 0.3820, "market Transformer macro-F1")
    assert_close(impact["source_type"]["NEWS"]["transformer"]["macro_f1"], 0.3847, "news macro-F1")
    assert_close(
        impact["source_type"]["DISCLOSURE"]["transformer"]["macro_f1"],
        0.2211,
        "disclosure macro-F1",
    )
    if multiseed["selected_seed_by_validation"] != 73:
        raise AssertionError("selected market-impact seed changed")
    assert_close(multiseed["test"]["macro_f1"]["sample_std"], 0.0102, "three-seed macro-F1 std")
    assert_close(disclosure["candidate"]["macro_f1"], 0.9962, "disclosure operational macro-F1")

    print("submission metrics verified against frozen reports")


if __name__ == "__main__":
    main()
