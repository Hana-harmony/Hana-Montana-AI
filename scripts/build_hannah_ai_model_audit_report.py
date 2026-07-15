import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports/hannah-ai-model-audit-report.json"


def _load_json(path: str) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads((PROJECT_ROOT / path).read_text())
    return payload


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
    peer_all_results = _load_json("reports/global-peer-all-results.json")
    sentiment = _load_json("reports/kf-deberta-sentiment-training-report.json")
    sentiment_benchmark = _load_json("reports/korean-finance-sentiment-benchmark.json")
    disclosure_importance = _load_json("reports/disclosure-importance-training-report.json")
    disclosure_research = _load_json("reports/disclosure-importance-research-evaluation.json")
    impact_baselines = {
        source_type: _load_json(
            f"reports/k-fnspid-impact-{source_type.lower()}-training-report.json"
        )
        for source_type in ("NEWS", "DISCLOSURE")
    }
    impact_transformers = {
        source_type: _load_json(
            f"reports/k-fnspid-impact-{source_type.lower()}-transformer-training-report.json"
        )
        for source_type in ("NEWS", "DISCLOSURE")
    }
    impact_research = _load_json("reports/k-fnspid-research-evaluation.json")

    peer_gate_status = (
        "pass"
        if peer_training["coverage_gate"]["status"] == "pass"
        and peer_coverage["quality_gate"]["status"] == "pass"
        and peer_coverage["confidence_monitoring"]["status"] == "pass"
        else "conditional_pass"
    )
    core_model_gates_passed = (
        sentiment_benchmark["deployment_gate"]["eligible"]
        and disclosure_importance["deployment_gate"]["eligible"]
        and disclosure_research["research_gate"]["eligible_for_superiority_claim"]
        and all(
            report["deployment_gate"]["eligible"]
            for report in impact_transformers.values()
        )
        and impact_research["research_gate"]["eligible_for_superiority_claim"]
    )
    audit = {
        "schema_version": "hannah-ai-model-audit/v2",
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_status": (
            "pass" if peer_gate_status == "pass" and core_model_gates_passed else "conditional_pass"
        ),
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
                    "benchmark_event_macro_f1": _metric(release, "benchmark", "event_macro_f1"),
                    "benchmark_sentiment_accuracy": _metric(
                        release, "benchmark", "sentiment_accuracy"
                    ),
                    "benchmark_importance_accuracy": _metric(
                        release, "benchmark", "importance_accuracy"
                    ),
                    "real_news_event_macro_f1": _metric(
                        release, "real_news_gold", "event_macro_f1"
                    ),
                    "stock_review_event_macro_f1": ml_eval["stock_review_gold"]["event_macro_f1"],
                },
                "gate_status": "pass",
                "remaining_risk": (
                    "stock_review_gold의 일부 희소 이벤트 라벨은 macro F1이 낮아 "
                    "지속적인 gold 확장이 필요하다."
                ),
            },
            {
                "name": "korean_finance_sentiment_transformer",
                "artifact": "src/hannah_montana_ai/model_store/kf_deberta_sentiment",
                "version": sentiment["version"],
                "model_type": "KF-DeBERTa base + LoRA finance sentiment classifier",
                "serving_surface": "news/disclosure sentiment analysis",
                "release_status": sentiment_benchmark["deployment_gate"]["decision"],
                "training_samples": sentiment.get(
                    "cumulative_training_exposure_count",
                    sentiment["partition_count"]["TRAIN"],
                ),
                "evaluation": {
                    "validation": sentiment["validation"],
                    "test": sentiment["test"],
                    "independent_benchmark": sentiment_benchmark["models"],
                    "operational_gold": sentiment_benchmark["operational_gold"],
                },
                "gate_status": (
                    "pass" if sentiment_benchmark["deployment_gate"]["eligible"] else "fail"
                ),
                "remaining_risk": (
                    "공개 감성 데이터와 실제 운영 뉴스의 분포 차이는 지속적인 "
                    "시간 외삽 Gold로 감시한다."
                ),
            },
            {
                "name": "disclosure_semantic_importance_classifier",
                "artifact": "src/hannah_montana_ai/model_store/disclosure_importance_ml.joblib",
                "version": disclosure_importance["version"],
                "model_type": (
                    "Validation-selected title+snippet TF-IDF LogisticRegression "
                    "+ terminal-risk policy"
                ),
                "serving_surface": "disclosure semantic importance analysis",
                "release_status": disclosure_importance["deployment_gate"]["decision"],
                "training_samples": disclosure_importance["partition_count"]["FINAL_TRAIN"],
                "evaluation": {
                    "feature_selection": disclosure_importance["feature_selection"],
                    "model_only_gold": disclosure_importance["gold_test"],
                    "operational_gold": disclosure_research["candidate"],
                    "baseline_operational_gold": disclosure_research["baseline"],
                    "paired_bootstrap": disclosure_research["paired_bootstrap"],
                    "mcnemar_exact": disclosure_research["mcnemar_exact"],
                },
                "gate_status": (
                    "pass"
                    if disclosure_importance["deployment_gate"]["eligible"]
                    and disclosure_research["research_gate"]["eligible_for_superiority_claim"]
                    else "fail"
                ),
                "remaining_risk": (
                    "Gold는 동일 코드북의 Codex 단일 검수이므로 독립 금융 전문가 "
                    "평가자 간 일치도를 대신하지 않는다."
                ),
            },
            *[
                {
                    "name": f"k_fnspid_{source_type.lower()}_market_impact_expert",
                    "artifact": (
                        "src/hannah_montana_ai/model_store/"
                        f"k_fnspid_impact_{source_type.lower()}_transformer"
                        if impact_transformers[source_type]["deployment_gate"]["eligible"]
                        else "src/hannah_montana_ai/model_store/"
                        f"k_fnspid_impact_{source_type.lower()}_ml.joblib"
                    ),
                    "version": (
                        impact_transformers[source_type]["version"]
                        if impact_transformers[source_type]["deployment_gate"]["eligible"]
                        else impact_baselines[source_type]["version"]
                    ),
                    "model_type": (
                        "source-routed KF-DeBERTa base + LoRA ordinal expert"
                        if impact_transformers[source_type]["deployment_gate"]["eligible"]
                        else "source-routed TF-IDF char n-gram OVR LogisticRegression"
                    ),
                    "serving_surface": f"{source_type.lower()} market-impact fields",
                    "release_status": impact_transformers[source_type]["deployment_gate"][
                        "decision"
                    ],
                    "training_samples": impact_baselines[source_type][
                        "final_training_count"
                    ],
                    "evaluation": {
                        "baseline_test": impact_baselines[source_type]["test"],
                        "transformer_validation": impact_transformers[source_type][
                            "validation"
                        ],
                        "transformer_test": impact_transformers[source_type]["test"],
                        "source_research": impact_research["source_type"][source_type],
                    },
                    "gate_status": (
                        "pass"
                        if impact_transformers[source_type]["deployment_gate"]["eligible"]
                        and all(
                            impact_research["source_type"][source_type][
                                "non_regression_gate"
                            ].values()
                        )
                        else "fail"
                    ),
                    "remaining_risk": (
                        "텍스트만으로 가격 충격을 예측하므로 단독 투자 신호가 아니라 "
                        "의미 기반 중요도의 보조 신호로만 사용한다."
                    ),
                }
                for source_type in ("NEWS", "DISCLOSURE")
            ],
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
                    "src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib"
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
                    "TF-IDF retrieval + SVD semantic embedding + financial, domain, "
                    "profile-quality, and global-familiarity dynamic similarity"
                ),
                "serving_surface": "Korean stock detail global peer popup",
                "release_status": peer_training["coverage_gate"]["status"],
                "training_samples": peer_training["korea_universe_count"],
                "evaluation": {
                    "active_korea_universe_count": peer_training["korea_universe_count"],
                    "eligible_us_peer_count": peer_training["eligible_us_peer_count"],
                    "full_coverage_success_ratio": peer_coverage["quality_gate"][
                        "actual_success_ratio"
                    ],
                    "full_coverage_quality_gate": peer_coverage["quality_gate"]["status"],
                    "all_results_quality_status": peer_all_results["performance"]["quality_status"],
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
        "required_next_improvements": [
            "공시 의미 중요도 Gold를 독립 금융 전문가 2인 이상으로 재주석하고 합의도를 보고한다.",
            "장중 시세와 과거 가격 문맥을 분리된 후속 실험에 추가해 "
            "텍스트 단독 시장영향 한계를 검증한다.",
        ],
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
