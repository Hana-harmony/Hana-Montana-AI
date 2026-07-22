from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / path).read_text(encoding="utf-8")))


def assert_close(actual: float, expected: float, label: str) -> None:
    if abs(actual - expected) > 5e-5:
        raise AssertionError(f"{label}: expected={expected}, actual={actual}")


def main() -> None:
    manifest = load("data/k_fnspid/v4/manifest.json")
    sentiment = load("reports/korean-finance-sentiment-benchmark.json")
    confirmatory_sentiment_path = ROOT / "reports/korean-finance-sentiment-benchmark-v4.json"
    confirmatory_sentiment = cast(
        dict[str, Any],
        json.loads(confirmatory_sentiment_path.read_text(encoding="utf-8")),
    )
    impact = load("reports/k-fnspid-research-evaluation.json")
    disclosure_multiseed = load(
        "reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json"
    )
    disclosure = load("reports/disclosure-importance-research-evaluation.json")
    sentiment_inputs = load(
        "reports/k-fnspid-sentiment-v6-input-commitment-lock-v2.json"
    )
    dapt = load("data/k_fnspid/v4_dapt_temporal_v2/manifest.json")
    dapt_pilot = load("reports/k-fnspid-v4-kf-deberta-dapt-pilot-v2.json")
    submission = load("docs/paper/acl/submission-manifest.json")
    author = load("docs/paper/acl/author-metadata.json")

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

    if sentiment["sample_count"] != 932:
        raise AssertionError("decontaminated sentiment test count changed")
    assert_close(sentiment["models"]["kr_finbert_sc"]["macro_f1"], 0.7266, "KR-FinBERT-SC macro-F1")
    assert_close(sentiment["models"]["kf_deberta_lora"]["macro_f1"], 0.8849, "KF-DeBERTa macro-F1")
    protocol = sentiment["statistical_comparison"]["protocol"]
    if protocol["historical_test_reuse"] is not True:
        raise AssertionError("historical sentiment test reuse must remain disclosed")
    if protocol["confirmatory_claim_allowed"] is not False:
        raise AssertionError("historically reused sentiment Test cannot support confirmation")
    selection = sentiment["candidate_selection"]
    if selection["test_used_for_selection"] or selection["operational_gold_used_for_selection"]:
        raise AssertionError("sentiment candidate selection used Test or operational Gold")
    if (
        selection["artifact_historically_exposed_to_public_test"] is not True
        or selection["historical_public_test_exposure_disclosed"] is not True
    ):
        raise AssertionError("historical sentiment artifact exposure must remain explicit")
    if sentiment["deployment_gate"]["eligible"]:
        raise AssertionError("sentiment candidate unexpectedly passed the operational gate")
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

    if sentiment_inputs["status"] != "LOCKED":
        raise AssertionError("sentiment v6 input commitment is not locked")
    expected_partitions = {
        "TRAIN": 32_907,
        "CHECKPOINT": 911,
        "CALIBRATION": 455,
        "SELECTION": 461,
        "NEWS_CONFIRMATORY_RESERVATION": 600,
        "DISCLOSURE_CONFIRMATORY_RESERVATION": 600,
    }
    for role, expected in expected_partitions.items():
        actual = sentiment_inputs["prepared_partition_commitments"][role]["row_count"]
        if actual != expected:
            raise AssertionError(
                f"sentiment partition {role}: expected={expected}, actual={actual}"
            )
    expected_gold = {
        "primary_news": 596,
        "auxiliary_news": 598,
        "auxiliary_disclosure": 600,
        "development_news": 448,
        "development_disclosure": 447,
    }
    for source, expected in expected_gold.items():
        actual = sentiment_inputs["gold_inputs"][source]["rows"]
        if actual != expected:
            raise AssertionError(
                f"sentiment Gold {source}: expected={expected}, actual={actual}"
            )
    review = sentiment_inputs["independent_review"]
    if not review["actual_commitments_match"] or not review["all_gold_provenance_verified"]:
        raise AssertionError("independent sentiment commitment review failed")
    if review["all_15_partition_pair_group_overlaps"] != 0:
        raise AssertionError("sentiment partitions overlap")

    if dapt["schema_version"] != "k-fnspid-dapt-prepared/v2":
        raise AssertionError("DAPT prepared schema changed")
    if dapt["inventory"]["eligible_total"] != 1_118_291:
        raise AssertionError("DAPT eligible document count changed")
    if dapt["packing"]["packed_non_padding_token_count"] != 62_468_526:
        raise AssertionError("DAPT non-padding token count changed")
    if dapt_pilot["selected_precision"] != "FP32" or dapt_pilot["fp32"]["status"] != "PASS":
        raise AssertionError("DAPT FP32 precision pilot is not locked")
    if not (
        dapt_pilot["fp32"]["final_fixed_pilot"]["mean_nll"]
        < dapt_pilot["fp32"]["initial_fixed_pilot"]["mean_nll"]
    ):
        raise AssertionError("DAPT FP32 pilot did not reduce validation NLL")

    if submission["system_name"] != "Hana Montana AI(KF-DeBERTa + K-FNSPID)":
        raise AssertionError("paper system name changed")
    confirmatory_sha256 = hashlib.sha256(confirmatory_sentiment_path.read_bytes()).hexdigest()
    expected_verification = f"VERIFIED_AGAINST_REPORT_SHA256_{confirmatory_sha256}"
    if submission["metric_report_verification"] != expected_verification:
        raise AssertionError("submission manifest is not bound to the confirmatory report")
    if confirmatory_sentiment["schema_version"] != "korean-finance-sentiment-benchmark/v5":
        raise AssertionError("confirmatory sentiment schema changed")
    consumption = confirmatory_sentiment["sealed_evaluation_consumption"]
    if not consumption["one_shot"] or consumption["labels_loaded_before_receipt"]:
        raise AssertionError("confirmatory evaluation did not preserve one-shot sealing")
    gate = confirmatory_sentiment["deployment_gate"]
    if gate["eligible"] or gate["decision"] != "KEEP_CURRENT_MODEL":
        raise AssertionError("confirmatory deployment decision changed")
    expected_confirmatory = {
        "NEWS": {
            "sample_count": 600,
            "accuracy": 0.7503186489425128,
            "macro_f1": 0.5530330480216619,
            "kr_finbert_sc_raw_accuracy": 0.5781314229595588,
            "kr_finbert_sc_raw_macro_f1": 0.4936772419839708,
            "pre_k_fnspid_accuracy": 0.473671740731647,
            "pre_k_fnspid_macro_f1": 0.4395663720141798,
            "fair_baseline_accuracy": 0.7677017642313486,
            "fair_baseline_macro_f1": 0.5770932722672032,
        },
        "DISCLOSURE": {
            "sample_count": 600,
            "accuracy": 0.8645814903028203,
            "macro_f1": 0.6023636438636694,
            "kr_finbert_sc_raw_accuracy": 0.8535156515821671,
            "kr_finbert_sc_raw_macro_f1": 0.6146393032642109,
            "pre_k_fnspid_accuracy": 0.8479763525008467,
            "pre_k_fnspid_macro_f1": 0.5357548042726713,
            "fair_baseline_accuracy": 0.8513559033684889,
            "fair_baseline_macro_f1": 0.5647212604875623,
        },
    }
    for source_type, expected in expected_confirmatory.items():
        actual = confirmatory_sentiment["source_sealed_gold"][source_type]
        if actual["sample_count"] != expected["sample_count"]:
            raise AssertionError(f"{source_type} confirmatory sample count changed")
        for metric, expected_value in expected.items():
            if metric == "sample_count":
                continue
            assert_close(actual[metric], expected_value, f"{source_type} {metric}")
    if author["name_en"] != "Sunghyun Choi" or author["name_ko"] != "최성현":
        raise AssertionError("author identity changed")
    if author["affiliation_ko"] != "한국공학대학교 컴퓨터공학부 소프트웨어학과":
        raise AssertionError("author affiliation changed")

    required_english_facts = (
        "Hana Montana AI(KF-DeBERTa + K-FNSPID)",
        "0.7503 / 0.5530",
        "0.8646 / 0.6024",
        "KEEP\\_CURRENT\\_MODEL",
        "1,118,291",
        "62,468,526",
    )
    source_path = "docs/paper/acl/k-fnspid-v4-arr-review.tex"
    source = (ROOT / source_path).read_text(encoding="utf-8")
    for fact in required_english_facts:
        if fact not in source:
            raise AssertionError(f"{source_path} missing current fact: {fact}")

    required_korean_facts = (
        "Hana Montana AI(KF-DeBERTa + K-FNSPID)",
        "0.7503 / 0.5530",
        "0.8646 / 0.6024",
        "승격하지 않았다",
        "1,118,291",
        "\\section{논의}",
        "\\subsection{연구의 한계}",
        "\\section{결론}",
    )
    source_path = "docs/paper/acl/k-fnspid-v4-ko.tex"
    source = (ROOT / source_path).read_text(encoding="utf-8")
    for fact in required_korean_facts:
        if fact not in source:
            raise AssertionError(f"{source_path} missing current fact: {fact}")

    forbidden_korean_facts = ("LOCKED\\_RESULT\\_PENDING", "평가 진행 중")
    for fact in forbidden_korean_facts:
        if fact in source:
            raise AssertionError(f"{source_path} contains internal workflow term: {fact}")

    print(f"submission metrics verified against frozen reports ({confirmatory_sha256})")


if __name__ == "__main__":
    main()
