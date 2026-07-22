from __future__ import annotations

import json
from typing import Any

SCHEMA_VERSION = "k-fnspid-sentiment-statistical-analysis-plan/v2"

CANDIDATE_MODEL_NAME = "kf_deberta_lora_locked"
TFIDF_BASELINE_MODEL_NAME = "hana_tfidf_logistic"
TARGET_AWARE_REFERENCE_MODEL_NAME = "kr_finbert_sc"
RAW_REFERENCE_MODEL_NAME = "kr_finbert_sc_raw_off_the_shelf"
QWEN_TEACHER_MODEL_NAME = "qwen3_4b_blind_teacher"
PRE_K_FNSPID_MODEL_NAME = "pre_k_fnspid_kf_deberta"
FAIR_BASELINE_MODEL_NAME = "kr_finbert_sc_same_data_fair"
NO_K_ABLATION_MODEL_NAME = "kf_deberta_no_k_ablation"

FAMILYWISE_ALPHA = 0.05
CONFIDENCE_LEVEL = 0.95
PRACTICAL_SUPERIORITY_MARGIN = 0.02
DEFAULT_BOOTSTRAP_SAMPLES = 2_000
DEFAULT_BOOTSTRAP_SEED = 20260715
EVALUATION_BATCH_SIZE = 16
MIN_SEALED_SAMPLE_COUNT = 500
MIN_SEALED_ACCURACY = 0.90
MIN_SEALED_MACRO_F1 = 0.85
MIN_PUBLIC_MACRO_F1 = 0.85

CONFIRMATORY_SOURCES = ("NEWS", "DISCLOSURE")
CONFIRMATORY_BASELINE_MODEL_NAMES = (
    RAW_REFERENCE_MODEL_NAME,
    PRE_K_FNSPID_MODEL_NAME,
    FAIR_BASELINE_MODEL_NAME,
    NO_K_ABLATION_MODEL_NAME,
)

RECIPE_RELATIVE_PATHS = (
    ("candidate_trainer", "scripts/train_kf_deberta_sentiment_v2.py"),
    ("fair_trainer", "scripts/train_k_fnspid_fair_baseline.py"),
    ("evaluator", "scripts/evaluate_locked_kf_deberta_sentiment.py"),
    ("sentiment_input", "src/hannah_montana_ai/services/sentiment_input.py"),
    ("sentiment_protocol", "src/hannah_montana_ai/training/sentiment_protocol.py"),
    ("sentiment_sampling", "src/hannah_montana_ai/training/sentiment_sampling.py"),
    ("candidate_lock_script", "scripts/lock_kf_deberta_sentiment_candidate.py"),
    ("dual_review_adjudicator", "scripts/adjudicate_k_fnspid_sentiment_reviews.py"),
    ("teacher_labeler", "scripts/label_k_fnspid_sentiment_with_qwen.py"),
    ("sentiment_decision_merger", "scripts/merge_k_fnspid_sentiment_decisions.py"),
    ("dual_review_gold_promoter", "scripts/promote_k_fnspid_sentiment_gold.py"),
    (
        "historical_auxiliary_promoter",
        "scripts/promote_historical_sentiment_training_gold.py",
    ),
    ("git_attestation_script", "scripts/attest_sentiment_candidate_git_commit.py"),
    (
        "git_attestation_runtime_validator",
        "src/hannah_montana_ai/training/sentiment_git_attestation.py",
    ),
    (
        "statistical_analysis_plan",
        "src/hannah_montana_ai/training/sentiment_evaluation_plan.py",
    ),
    ("pyproject", "pyproject.toml"),
    ("uv_lock", "uv.lock"),
)


def canonical_statistical_analysis_plan() -> dict[str, Any]:
    hypotheses = [
        {
            "hypothesis_id": f"{source.casefold()}_candidate_gt_{baseline}",
            "source_type": source,
            "candidate_model": CANDIDATE_MODEL_NAME,
            "baseline_model": baseline,
            "metric": "sampling_design_weighted_plugin_macro_f1",
            "contrast": "candidate_minus_baseline",
            "null_hypothesis": "difference=0",
            "alternative_hypothesis": "difference!=0",
            "claim_direction": "candidate>baseline",
        }
        for source in CONFIRMATORY_SOURCES
        for baseline in CONFIRMATORY_BASELINE_MODEL_NAMES
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "frozen_before_public_test_or_sealed_gold": True,
        "familywise_alpha": FAMILYWISE_ALPHA,
        "multiple_comparison_correction": "holm_bonferroni/v1",
        "primary_metric": "sampling_design_weighted_plugin_macro_f1",
        "primary_metric_definition": {
            "display_name": "sampling-design-weighted plug-in Macro-F1",
            "estimator": (
                "각 표본의 고정 설계가중치로 3x3 모집단 혼동행렬 셀 총계를 추정한 뒤, "
                "각 클래스의 precision·recall·F1을 plug-in 계산하고 세 클래스 F1을 "
                "동일 가중 산술평균한다."
            ),
            "class_order": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
            "class_average": "unweighted_arithmetic_mean_over_three_class_plugin_f1",
            "zero_denominator_rule": "metric_component_equals_zero",
            "variance_estimator": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
        },
        "estimand_and_finite_frame": {
            "frame": (
                "K-FNSPID-v4 2026-04-01..2026-07-13 eligible canonical "
                "document-security units"
            ),
            "primary_estimands": (
                "source-specific design-weighted plug-in Macro-F1 and paired "
                "candidate-minus-named-baseline contrasts"
            ),
            "sampling_strata": "prelocked weak-rule auxiliary strata, not Gold labels",
            "long_horizon_or_external_population_claim_allowed": False,
        },
        "evaluation_batch_size": EVALUATION_BATCH_SIZE,
        "confirmatory_inference_backend": {
            "device": "cpu",
            "evaluator_batch_size": EVALUATION_BATCH_SIZE,
            "packaged_runtime_batch_size": 1,
            "parity_input": "unlabeled_confirmatory_reservation_only",
            "exact_label_agreement_required": True,
            "logits_max_abs_error_tolerance": 1e-5,
            "base_encoder_safetensors_manifest_must_match": True,
        },
        "holm_hypotheses": hypotheses,
        "paired_design_inference": {
            "estimator": "candidate_minus_baseline",
            "variance_method": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
            "finite_population_correction": True,
            "sampling_unit": "event_cluster_id",
            "confidence_level": CONFIDENCE_LEVEL,
            "p_value_method": "two_sided_normal_from_design_jackknife_standard_error/v1",
            "inference_scope": "asymptotic_design_based_approximation",
            "zero_standard_error_policy": "p_value_one_fail_closed",
            "superiority_rule": {
                "observed_difference_must_be_positive": True,
                "confidence_interval_lower_bound_must_be_positive": True,
                "holm_adjusted_p_value_must_be_below_alpha": True,
            },
            "practical_superiority_rule": {
                "metric": "absolute_macro_f1_difference",
                "minimum_difference": PRACTICAL_SUPERIORITY_MARGIN,
                "confidence_interval_lower_bound_must_reach_minimum": True,
                "required_for_large_or_material_superiority_wording": True,
                "affects_statistical_superiority_flag": False,
            },
        },
        "bootstrap": {
            "samples": DEFAULT_BOOTSTRAP_SAMPLES,
            "base_seed": DEFAULT_BOOTSTRAP_SEED,
            "confidence_level": CONFIDENCE_LEVEL,
            "partition_seed_offsets": {
                "public_test": 0,
                "sealed_news": 1,
                "sealed_disclosure": 2,
                "legacy_news": 3,
                "legacy_disclosure": 4,
            },
            "role": "secondary_interval_and_randomization_diagnostics",
        },
        "thresholds": {
            "sealed_per_source": {
                "minimum_sample_count": MIN_SEALED_SAMPLE_COUNT,
                "minimum_accuracy": MIN_SEALED_ACCURACY,
                "minimum_macro_f1": MIN_SEALED_MACRO_F1,
                "accuracy_non_regression_models": [
                    TFIDF_BASELINE_MODEL_NAME,
                    TARGET_AWARE_REFERENCE_MODEL_NAME,
                    RAW_REFERENCE_MODEL_NAME,
                    FAIR_BASELINE_MODEL_NAME,
                    NO_K_ABLATION_MODEL_NAME,
                ],
                "macro_f1_non_regression_models": [
                    TFIDF_BASELINE_MODEL_NAME,
                    TARGET_AWARE_REFERENCE_MODEL_NAME,
                    RAW_REFERENCE_MODEL_NAME,
                    FAIR_BASELINE_MODEL_NAME,
                    NO_K_ABLATION_MODEL_NAME,
                ],
                "macro_f1_strict_improvement_models": [PRE_K_FNSPID_MODEL_NAME],
                "holm_superiority_models": list(CONFIRMATORY_BASELINE_MODEL_NAMES),
            },
            "public_test_diagnostic_only": {
                "minimum_macro_f1": MIN_PUBLIC_MACRO_F1,
                "macro_f1_non_regression_models": [
                    TARGET_AWARE_REFERENCE_MODEL_NAME,
                    PRE_K_FNSPID_MODEL_NAME,
                    FAIR_BASELINE_MODEL_NAME,
                ],
                "affects_deployment_decision": False,
            },
        },
        "model_names": {
            "candidate": CANDIDATE_MODEL_NAME,
            "tfidf_baseline": TFIDF_BASELINE_MODEL_NAME,
            "target_aware_reference_diagnostic": TARGET_AWARE_REFERENCE_MODEL_NAME,
            "raw_reference": RAW_REFERENCE_MODEL_NAME,
            "blind_teacher": QWEN_TEACHER_MODEL_NAME,
            "pre_k_fnspid_baseline": PRE_K_FNSPID_MODEL_NAME,
            "same_data_fair_baseline": FAIR_BASELINE_MODEL_NAME,
            "no_k_ablation_baseline": NO_K_ABLATION_MODEL_NAME,
        },
        "excluded_confirmatory_models": {
            QWEN_TEACHER_MODEL_NAME: {
                "role": "blind_teacher_diagnostic_only",
                "included_in_holm_family": False,
                "affects_deployment_gate": False,
                "reason": (
                    "Qwen blind teacher는 확증 가설에서 사전 지정한 학습·artifact 기준선이 "
                    "아니므로 Holm family와 배포 gate에서 제외한다."
                ),
            }
        },
        "claim_scope": {
            "global_sota_claim_allowed": False,
            "confirmatory_population": (
                "fixed_new_k_fnspid_stratified_probability_samples_for_news_and_disclosure"
            ),
            "allowed_claim": "locked_candidate_vs_named_locked_baselines_only",
            "large_or_material_wording_requires_practical_margin": True,
            "excluded_claim": (
                "global_or_all_korean_finance_benchmark_sota; generic KR-FinBERT-SC "
                "superiority; long-horizon temporal generalization; K-FNSPID-only "
                "causal effect"
            ),
        },
    }


def validate_statistical_analysis_plan(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("후보 lock에 canonical statistical_analysis_plan이 없습니다.")
    expected = canonical_statistical_analysis_plan()
    try:
        actual_json = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        expected_json = json.dumps(
            expected,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exception:
        raise ValueError("statistical_analysis_plan이 canonical JSON이 아닙니다.") from exception
    if actual_json != expected_json:
        raise ValueError("statistical_analysis_plan이 고정된 확증 평가 계약과 다릅니다.")
    return expected


def validate_evaluation_runtime_parameters(
    plan: object,
    *,
    batch_size: int,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    validated = validate_statistical_analysis_plan(plan)
    bootstrap = validated["bootstrap"]
    if (
        isinstance(batch_size, bool)
        or batch_size != validated["evaluation_batch_size"]
        or isinstance(bootstrap_samples, bool)
        or bootstrap_samples != bootstrap["samples"]
        or isinstance(bootstrap_seed, bool)
        or bootstrap_seed != bootstrap["base_seed"]
    ):
        raise ValueError(
            "evaluation CLI 인자는 잠긴 statistical_analysis_plan과 정확히 일치해야 합니다."
        )
    return validated
