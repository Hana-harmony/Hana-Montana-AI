from __future__ import annotations

from hannah_montana_ai.training.sentiment_evaluation_plan import (
    NO_K_ABLATION_MODEL_NAME,
    QWEN_TEACHER_MODEL_NAME,
    canonical_statistical_analysis_plan,
)


def test_confirmatory_plan_has_exact_eight_hypotheses_and_excludes_qwen() -> None:
    plan = canonical_statistical_analysis_plan()
    hypotheses = plan["holm_hypotheses"]

    assert len(hypotheses) == 8
    assert {
        (hypothesis["source_type"], hypothesis["baseline_model"])
        for hypothesis in hypotheses
        if hypothesis["baseline_model"] == NO_K_ABLATION_MODEL_NAME
    } == {
        ("NEWS", NO_K_ABLATION_MODEL_NAME),
        ("DISCLOSURE", NO_K_ABLATION_MODEL_NAME),
    }
    assert all(
        hypothesis["baseline_model"] != QWEN_TEACHER_MODEL_NAME
        for hypothesis in hypotheses
    )
    assert plan["excluded_confirmatory_models"][QWEN_TEACHER_MODEL_NAME][
        "affects_deployment_gate"
    ] is False
    assert plan["primary_metric"] == "sampling_design_weighted_plugin_macro_f1"
    assert plan["paired_design_inference"]["practical_superiority_rule"] == {
        "metric": "absolute_macro_f1_difference",
        "minimum_difference": 0.02,
        "confidence_interval_lower_bound_must_reach_minimum": True,
        "required_for_large_or_material_superiority_wording": True,
        "affects_statistical_superiority_flag": False,
    }
    assert plan["paired_design_inference"]["zero_standard_error_policy"] == (
        "p_value_one_fail_closed"
    )
    assert plan["confirmatory_inference_backend"] == {
        "device": "cpu",
        "evaluator_batch_size": 16,
        "packaged_runtime_batch_size": 1,
        "parity_input": "unlabeled_confirmatory_reservation_only",
        "exact_label_agreement_required": True,
        "logits_max_abs_error_tolerance": 1e-5,
        "base_encoder_safetensors_manifest_must_match": True,
    }
