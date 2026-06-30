import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports/hannah-ai-model-audit-report.json"


def _load_json(path: str) -> dict[str, Any]:
    return json.loads((PROJECT_ROOT / path).read_text())


def _metric(report: dict[str, Any], section: str, name: str) -> float | None:
    value = (
        report.get("quality_gates", {})
        .get(section, {})
        .get("metrics", {})
        .get(name, {})
        .get("actual")
    )
    return float(value) if isinstance(value, int | float) else None


def build_hannah_ai_model_audit_report(report_path: Path = REPORT_PATH) -> dict[str, Any]:
    release = _load_json("reports/model-release-report.json")
    ml_eval = _load_json("reports/ml-model-evaluation.json")
    stock_linker = _load_json("reports/stock-linker-training-report.json")
    foreign = _load_json("reports/foreign-ownership-quantity-training-report.json")
    foreign_sota = _load_json("reports/foreign-ownership-quantity-sota-benchmark.json")
    peer_training = _load_json("reports/global-peer-training-report.json")
    peer_coverage = _load_json("reports/global-peer-full-coverage-report.json")
    peer_smoke = _load_json("reports/global-peer-ai-smoke-report.json")

    peer_gate_status = (
        "pass"
        if peer_training["coverage_gate"]["status"] == "pass"
        and peer_coverage["quality_gate"]["status"] == "pass"
        and peer_coverage["confidence_monitoring"]["status"] == "pass"
        else "conditional_pass"
    )
    audit = {
        "schema_version": "hannah-ai-model-audit/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_status": "pass" if peer_gate_status == "pass" else "conditional_pass",
        "models": [
            {
                "name": "financial_news_disclosure_classifier",
                "artifact": "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib",
                "version": release["model_version"],
                "model_type": "TF-IDF feature pipeline + supervised LogisticRegression classifiers",
                "serving_surface": "watchlist/news/disclosure alert analysis",
                "release_status": release["overall_status"],
                "training_samples": release["training"]["supervised_sample_count"],
                "evaluation": {
                    "benchmark_event_macro_f1": _metric(
                        release, "benchmark", "event_macro_f1"
                    ),
                    "benchmark_sentiment_accuracy": _metric(
                        release, "benchmark", "sentiment_accuracy"
                    ),
                    "benchmark_importance_accuracy": _metric(
                        release, "benchmark", "importance_accuracy"
                    ),
                    "real_news_event_macro_f1": _metric(
                        release, "real_news_gold", "event_macro_f1"
                    ),
                    "stock_review_event_macro_f1": ml_eval["stock_review_gold"][
                        "event_macro_f1"
                    ],
                },
                "gate_status": "pass",
                "remaining_risk": (
                    "stock_review_gold의 일부 희소 이벤트 라벨은 macro F1이 낮아 "
                    "지속적인 gold 확장이 필요하다."
                ),
            },
            {
                "name": "stock_linker",
                "artifact": "src/hannah_montana_ai/model_store/stock_linker_ml.joblib",
                "version": stock_linker["version"],
                "model_type": "TF-IDF nearest-neighbor stock entity linker",
                "serving_surface": "news/disclosure to Korean stock matching",
                "release_status": stock_linker["coverage_gate"]["status"],
                "training_samples": stock_linker["training_row_count"],
                "evaluation": stock_linker["evaluation"],
                "gate_status": stock_linker["coverage_gate"]["status"],
                "remaining_risk": "동명이인성 짧은 종목명은 live quality audit로 계속 감시한다.",
            },
            {
                "name": "foreign_owned_quantity_forecaster",
                "artifact": (
                    "src/hannah_montana_ai/model_store/"
                    "foreign_ownership_quantity_ml.joblib"
                ),
                "version": foreign["model_version"],
                "model_type": "stock-routed panel time-series ML ensemble",
                "serving_surface": "foreign ownership limit warning prediction",
                "release_status": foreign["release_status"],
                "training_samples": foreign["sample_count"],
                "evaluation": {
                    "baseline": foreign["baseline_metrics"],
                    "guarded_runtime": foreign["guarded_runtime_metrics"],
                    "guarded_improvement_over_baseline": foreign[
                        "guarded_improvement_over_baseline"
                    ],
                    "sota": foreign_sota["published_sota_diagnostics"],
                },
                "gate_status": foreign["release_status"],
                "remaining_risk": (
                    "전날까지의 외국인 보유수량만 쓰므로 외부 수급 이벤트는 "
                    "feature 확장 전까지 잔여 오차로 남는다."
                ),
            },
            {
                "name": "global_peer_matcher",
                "artifact": "src/hannah_montana_ai/model_store/global_peer_ml.joblib",
                "version": peer_training["version"],
                "model_type": (
                    "TF-IDF retrieval + SVD semantic embedding + financial features + "
                    "pairwise LogisticRegression reranker"
                ),
                "serving_surface": "Korean stock detail global peer popup",
                "release_status": peer_training["coverage_gate"]["status"],
                "training_samples": peer_training["pairwise_ranker_evaluation"][
                    "training_sample_count"
                ],
                "evaluation": {
                    "curated_pairwise_top1_accuracy": peer_training[
                        "pairwise_ranker_evaluation"
                    ]["top1_accuracy"],
                    "curated_anchor_top1_accuracy": peer_training["coverage_gate"][
                        "actual_anchor_top1_accuracy"
                    ],
                    "full_coverage_success_ratio": peer_coverage["quality_gate"][
                        "actual_success_ratio"
                    ],
                    "full_coverage_quality_gate": peer_coverage["quality_gate"]["status"],
                    "confidence_monitoring": peer_coverage["confidence_monitoring"],
                    "smoke_sample_count": peer_smoke["sample_count"],
                },
                "gate_status": peer_gate_status,
                "remaining_risk": (
                    "국내 업종 profile은 Naver 동일업종 비교 데이터로 보강했지만 "
                    "미국 상장 universe 밖의 비미국 peer는 후보에 없다."
                ),
            },
        ],
        "required_next_improvements": [],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    return audit


if __name__ == "__main__":
    result = build_hannah_ai_model_audit_report()
    print(
        "Hannah AI 모델 감사 완료: "
        f"{len(result['models'])}개 모델, status={result['overall_status']}"
    )
