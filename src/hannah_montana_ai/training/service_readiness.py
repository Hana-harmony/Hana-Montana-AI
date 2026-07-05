from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

SERVICE_READINESS_REPORT_SCHEMA_VERSION = "service-readiness-report/v1"
MINIMUM_TRAINING_REFERENCE_STOCK_COUNT = 3_000
MINIMUM_EVALUATION_REFERENCE_STOCK_COUNT = 500
MINIMUM_TRAINABLE_STOCK_NAME_ACCURACY = 0.99
QWEN_LOCAL_LLM_BASE_MODEL = "mlx-community/Qwen3-0.6B-4bit"
QWEN_LOCAL_LLM_MIN_PASS_RATE = 1.0
QWEN_LOCAL_LLM_MIN_EVAL_SAMPLE_COUNT = 5
QWEN_LOCAL_LLM_FEATURES = {
    "korean_financial_terms": {
        "training_schema": "korean-term-qwen3-explainer-training/v1",
        "eval_schema": "korean-term-qwen3-generation-eval/v1",
    },
    "news_summary": {
        "training_schema": "news-summary-qwen3-training/v1",
        "eval_schema": "news-summary-qwen3-generation-eval/v1",
    },
    "korean_translation": {
        "training_schema": "korean-translation-qwen3-training/v1",
        "eval_schema": "korean-translation-qwen3-generation-eval/v1",
    },
}


def build_service_readiness_report(
    *,
    model_release_report: dict[str, Any],
    live_news_monitoring_status: dict[str, Any],
    full_universe_coverage_report: dict[str, Any],
    stock_coverage_report: dict[str, Any],
    stock_linker_training_report: dict[str, Any],
    pseudo_label_monitoring_report: dict[str, Any],
    confidence_calibration_report: dict[str, Any],
    qwen_training_reports: dict[str, dict[str, Any]] | None = None,
    qwen_generation_eval_reports: dict[str, dict[str, Any]] | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    model_version = str(model_release_report.get("model_version") or "")
    checks = {
        "model_release_gate": _equals_check(
            actual=model_release_report.get("overall_status"),
            expected="pass",
        ),
        "bootstrap_service_readiness": _equals_check(
            actual=model_release_report.get("service_readiness", {}).get("overall_status"),
            expected="pass",
        ),
        "audited_gold_readiness": _equals_check(
            actual=model_release_report.get("audited_gold_readiness", {}).get("overall_status"),
            expected="pass",
        ),
        "live_news_monitoring": _equals_check(
            actual=live_news_monitoring_status.get("overall_status"),
            expected="pass",
        ),
        "confidence_policy_observe_only": _equals_check(
            actual=live_news_monitoring_status.get("policy", {}).get("confidence_usage"),
            expected="observe_only",
        ),
        "full_universe_reference_coverage": _full_universe_coverage_check(
            full_universe_coverage_report
        ),
        "stock_reference_coverage": _stock_reference_coverage_check(stock_coverage_report),
        "stock_linker_coverage": _stock_linker_coverage_check(stock_linker_training_report),
        "pseudo_label_monitoring": _equals_check(
            actual=pseudo_label_monitoring_report.get("overall_status"),
            expected="pass",
        ),
        "confidence_calibration_report": _confidence_calibration_check(
            confidence_calibration_report,
            model_version,
        ),
        "qwen_local_llm_release_gate": _qwen_local_llm_release_check(
            qwen_training_reports or {},
            qwen_generation_eval_reports or {},
        ),
    }
    overall_status = (
        "pass" if all(check["status"] == "pass" for check in checks.values()) else "fail"
    )
    return {
        "schema_version": SERVICE_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(UTC)).isoformat(),
        "overall_status": overall_status,
        "model_version": model_version,
        "checks": checks,
        "policy": {
            "confidence_usage": "observe_only",
            "description": (
                "confidence 값은 품질 관측과 UI 표시용 메타데이터로만 제공한다. "
                "Hannah는 신뢰도 기반 자동 차단 결정을 만들지 않는다."
            ),
        },
        "continuous_operations": {
            "human_gold_increment": (
                "사람 검수 gold label은 운영 로그와 월별 증분 수집으로 계속 확대한다."
            ),
            "drift_monitoring": (
                "live-news smoke/drift 리포트가 stale 또는 attention이면 운영 credential 환경에서 "
                "배치를 재생성하고 release 전 원인을 확인한다."
            ),
            "rollback": (
                "model-release-report와 service-readiness-report가 pass였던 "
                "직전 artifact로 되돌린다."
            ),
        },
        "required_action": _required_action(overall_status),
    }


def _equals_check(*, actual: Any, expected: Any) -> dict[str, Any]:
    return {
        "actual": actual,
        "expected": expected,
        "status": "pass" if actual == expected else "fail",
    }


def _full_universe_coverage_check(report: dict[str, Any]) -> dict[str, Any]:
    valid_universe_count = int(report.get("valid_numeric_universe_count") or 0)
    full_coverage_count = int(report.get("full_coverage_stock_count") or 0)
    missing_count = int(report.get("missing_stock_count_after_generation") or 0)
    status = (
        "pass"
        if missing_count == 0 and full_coverage_count >= valid_universe_count > 0
        else "fail"
    )
    return {
        "valid_numeric_universe_count": valid_universe_count,
        "full_coverage_stock_count": full_coverage_count,
        "missing_stock_count_after_generation": missing_count,
        "review_status": report.get("review_status"),
        "status": status,
    }


def _stock_reference_coverage_check(report: dict[str, Any]) -> dict[str, Any]:
    gate_status = report.get("coverage_gates", {}).get("overall_status")
    training_stock_count = int(report.get("training_stock_count") or 0)
    evaluation_stock_count = int(report.get("evaluation_stock_count") or 0)
    status = (
        "pass"
        if gate_status == "pass"
        and training_stock_count >= MINIMUM_TRAINING_REFERENCE_STOCK_COUNT
        and evaluation_stock_count >= MINIMUM_EVALUATION_REFERENCE_STOCK_COUNT
        else "fail"
    )
    return {
        "coverage_gate_status": gate_status,
        "training_stock_count": training_stock_count,
        "minimum_training_stock_count": MINIMUM_TRAINING_REFERENCE_STOCK_COUNT,
        "evaluation_stock_count": evaluation_stock_count,
        "minimum_evaluation_stock_count": MINIMUM_EVALUATION_REFERENCE_STOCK_COUNT,
        "status": status,
    }


def _stock_linker_coverage_check(report: dict[str, Any]) -> dict[str, Any]:
    evaluation = report.get("evaluation", {})
    all_code_accuracy = float(evaluation.get("all_stock_code_template_accuracy") or 0.0)
    trainable_name_accuracy = float(
        evaluation.get("trainable_stock_name_template_accuracy") or 0.0
    )
    coverage_gate_status = report.get("coverage_gate", {}).get("status")
    status = (
        "pass"
        if coverage_gate_status == "pass"
        and all_code_accuracy == 1.0
        and trainable_name_accuracy >= MINIMUM_TRAINABLE_STOCK_NAME_ACCURACY
        else "fail"
    )
    return {
        "coverage_gate_status": coverage_gate_status,
        "all_stock_code_template_accuracy": all_code_accuracy,
        "required_all_stock_code_template_accuracy": 1.0,
        "trainable_stock_name_template_accuracy": trainable_name_accuracy,
        "minimum_trainable_stock_name_template_accuracy": MINIMUM_TRAINABLE_STOCK_NAME_ACCURACY,
        "status": status,
    }


def _confidence_calibration_check(report: dict[str, Any], model_version: str) -> dict[str, Any]:
    datasets = report.get("datasets", {})
    required_datasets = {"benchmark", "real_news_gold"}
    missing_datasets = sorted(required_datasets - set(datasets))
    status = (
        "pass"
        if report.get("schema_version") == "model-confidence-calibration/v1"
        and report.get("model_version") == model_version
        and not missing_datasets
        else "fail"
    )
    return {
        "schema_version": report.get("schema_version"),
        "model_version": report.get("model_version"),
        "expected_model_version": model_version,
        "required_datasets": sorted(required_datasets),
        "missing_datasets": missing_datasets,
        "status": status,
    }


def _qwen_local_llm_release_check(
    training_reports: dict[str, dict[str, Any]],
    generation_eval_reports: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    feature_checks = {
        feature_name: _qwen_feature_check(
            feature_name=feature_name,
            training_report=training_reports.get(feature_name, {}),
            generation_eval_report=generation_eval_reports.get(feature_name, {}),
            expected_training_schema=str(contract["training_schema"]),
            expected_eval_schema=str(contract["eval_schema"]),
        )
        for feature_name, contract in QWEN_LOCAL_LLM_FEATURES.items()
    }
    status = (
        "pass"
        if feature_checks
        and all(check["status"] == "pass" for check in feature_checks.values())
        else "fail"
    )
    return {
        "base_model": QWEN_LOCAL_LLM_BASE_MODEL,
        "minimum_eval_pass_rate": QWEN_LOCAL_LLM_MIN_PASS_RATE,
        "minimum_eval_sample_count": QWEN_LOCAL_LLM_MIN_EVAL_SAMPLE_COUNT,
        "features": feature_checks,
        "status": status,
    }


def _qwen_feature_check(
    *,
    feature_name: str,
    training_report: dict[str, Any],
    generation_eval_report: dict[str, Any],
    expected_training_schema: str,
    expected_eval_schema: str,
) -> dict[str, Any]:
    training = training_report.get("training", {})
    adapter_dir = str(training_report.get("adapter_dir") or "")
    serving_note = str(training_report.get("serving_note") or "").lower()
    pass_rate = float(generation_eval_report.get("pass_rate") or 0.0)
    sample_count = int(generation_eval_report.get("sample_count") or 0)
    quality_status = generation_eval_report.get("quality_status", "pass")
    failure_reasons = []
    if training_report.get("schema_version") != expected_training_schema:
        failure_reasons.append("training_schema_mismatch")
    if generation_eval_report.get("schema_version") != expected_eval_schema:
        failure_reasons.append("generation_eval_schema_mismatch")
    if training_report.get("base_model") != QWEN_LOCAL_LLM_BASE_MODEL:
        failure_reasons.append("training_base_model_mismatch")
    if generation_eval_report.get("model") != QWEN_LOCAL_LLM_BASE_MODEL:
        failure_reasons.append("generation_eval_model_mismatch")
    if training.get("executed") is not True or training.get("return_code") != 0:
        failure_reasons.append("training_not_successful")
    if not adapter_dir or generation_eval_report.get("adapter_dir") != adapter_dir:
        failure_reasons.append("adapter_dir_mismatch")
    if pass_rate < QWEN_LOCAL_LLM_MIN_PASS_RATE:
        failure_reasons.append("generation_eval_pass_rate_below_gate")
    if sample_count < QWEN_LOCAL_LLM_MIN_EVAL_SAMPLE_COUNT:
        failure_reasons.append("generation_eval_sample_count_below_gate")
    if quality_status != "pass":
        failure_reasons.append("generation_eval_quality_status_failed")
    for required_term in ("t4g.medium", "gguf", "openai-compatible"):
        if required_term not in serving_note:
            failure_reasons.append(f"serving_note_missing:{required_term}")
    return {
        "feature": feature_name,
        "training_schema": training_report.get("schema_version"),
        "expected_training_schema": expected_training_schema,
        "generation_eval_schema": generation_eval_report.get("schema_version"),
        "expected_generation_eval_schema": expected_eval_schema,
        "base_model": training_report.get("base_model"),
        "generation_eval_model": generation_eval_report.get("model"),
        "adapter_dir": adapter_dir,
        "generation_eval_adapter_dir": generation_eval_report.get("adapter_dir"),
        "training_executed": training.get("executed"),
        "training_return_code": training.get("return_code"),
        "sample_count": sample_count,
        "pass_rate": pass_rate,
        "quality_status": quality_status,
        "serving_runtime_gate": "t4g.medium GGUF OpenAI-compatible sidecar",
        "failure_reasons": failure_reasons,
        "status": "pass" if not failure_reasons else "fail",
    }


def _required_action(overall_status: str) -> str:
    if overall_status == "pass":
        return (
            "추가 조치 없음. 현재 release, coverage, live-news, confidence 정책이 "
            "서비스 readiness gate를 통과했다."
        )
    return (
        "fail 상태 check를 수정한 뒤 관련 리포트를 재생성하고 "
        "service readiness gate를 다시 실행한다."
    )
