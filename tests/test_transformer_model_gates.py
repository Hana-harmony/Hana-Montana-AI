import json
import math
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import hannah_montana_ai.services.transformer_sentiment_model as sentiment_module
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model_artifact_integrity import (
    build_artifact_manifest,
    verify_artifact_manifest,
)
from hannah_montana_ai.services.sentiment_release import expected_sentiment_gate_checks
from hannah_montana_ai.services.transformer_impact_model import (
    KfDebertaImpactModel,
    _log_prior_offsets,
    _temperature,
)
from hannah_montana_ai.services.transformer_impact_model import (
    _deployment_gate_passed as impact_gate_passed,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    KfDebertaSentimentModel,
    _artifact_manifest_sha256,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    _deployment_gate_passed as sentiment_gate_passed,
)


def _sentiment_artifact_manifest(include_metadata: bool = False) -> dict[str, Any]:
    names = [
        "adapter_config.json",
        "adapter_model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    ]
    if include_metadata:
        names.append("hannah_metadata.json")
    return {
        name: {"bytes": index + 1, "sha256": f"{index + 1:064x}"}
        for index, name in enumerate(names)
    }


def _eligible_sentiment_reports() -> tuple[dict[str, Any], dict[str, Any]]:
    version = "hana-montana-kf-deberta-k-fnspid-sentiment-seed17"
    training_manifest = _sentiment_artifact_manifest()
    locked_manifest = _sentiment_artifact_manifest(include_metadata=True)
    locked_hash = _artifact_manifest_sha256(locked_manifest)
    logit_bias_by_domain = {
        "NEWS_UNTARGETED": [0.0, 0.0, 0.0],
        "NEWS_TARGETED": [-0.1, 0.2, -0.1],
        "DISCLOSURE_TARGETED": [0.0, 0.1, -0.1],
    }
    training: dict[str, Any] = {
        "schema_version": "kf-deberta-sentiment-training/v2",
        "version": version,
        "base_model": "kakaobank/kf-deberta-base",
        "base_model_revision": "363b171d71443b0874b0bf9cea053eb5b1650633",
        "label_order": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
        "max_length": 192,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "logit_bias_by_domain": logit_bias_by_domain,
        "artifact_files": training_manifest,
    }
    benchmark: dict[str, Any] = {
        "schema_version": "korean-finance-sentiment-benchmark/v4",
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "candidate_lock": {
            "schema_version": "sentiment-candidate-lock/v1",
            "selection_only": True,
            "public_test_evaluated_before_lock": False,
            "operational_sealed_gold_evaluated_before_lock": False,
            "version": version,
            "artifact_files": locked_manifest,
            "artifact_manifest_sha256": locked_hash,
            "logit_bias_by_domain": json.loads(json.dumps(logit_bias_by_domain)),
        },
        "source_sealed_gold": {
            source_type: {
                "sample_count": 500,
                "accuracy": 0.91,
                "macro_f1": 0.86,
                "baseline_accuracy": 0.89,
                "baseline_macro_f1": 0.84,
                "kr_finbert_sc_accuracy": 0.78,
                "kr_finbert_sc_macro_f1": 0.76,
                "kr_finbert_sc_raw_accuracy": 0.77,
                "kr_finbert_sc_raw_macro_f1": 0.75,
                "qwen3_4b_teacher_accuracy": 0.80,
                "qwen3_4b_teacher_macro_f1": 0.78,
                "pre_k_fnspid_accuracy": 0.83,
                "pre_k_fnspid_macro_f1": 0.84,
                "fair_baseline_accuracy": 0.82,
                "fair_baseline_macro_f1": 0.81,
                "no_k_ablation_accuracy": 0.84,
                "no_k_ablation_macro_f1": 0.83,
            }
            for source_type in ("NEWS", "DISCLOSURE")
        },
        "public_test": {
            "sample_count": 932,
            "accuracy": 0.87,
            "macro_f1": 0.86,
            "kr_finbert_sc_accuracy": 0.75,
            "kr_finbert_sc_macro_f1": 0.73,
            "kr_finbert_sc_raw_accuracy": 0.74,
            "kr_finbert_sc_raw_macro_f1": 0.72,
            "pre_k_fnspid_accuracy": 0.85,
            "pre_k_fnspid_macro_f1": 0.85,
            "fair_baseline_accuracy": 0.84,
            "fair_baseline_macro_f1": 0.83,
            "no_k_ablation_accuracy": 0.83,
            "no_k_ablation_macro_f1": 0.82,
        },
        "deployment_gate": {
            "eligible": True,
            "candidate_model": "kf_deberta_lora_locked",
            "candidate_version": version,
            "candidate_artifact_manifest_sha256": locked_hash,
        },
    }
    p_value = math.erfc(10.0 / math.sqrt(2.0))
    interval = {
        "estimate": 0.10,
        "variance": 0.0001,
        "standard_error": 0.01,
        "low": 0.10 - 1.959963984540054 * 0.01,
        "high": 0.10 + 1.959963984540054 * 0.01,
        "two_sided_normal_p_value": p_value,
    }
    design = {
        "resampling_unit": "unique_event_cluster",
        "replicate_count": 600,
        "sample_n_h": {label: 200 for label in ("NEGATIVE", "NEUTRAL", "POSITIVE")},
        "population_N_h": {
            label: 1_000 for label in ("NEGATIVE", "NEUTRAL", "POSITIVE")
        },
    }
    inference_sources: dict[str, Any] = {}
    for source_type in ("NEWS", "DISCLOSURE"):
        metrics = benchmark["source_sealed_gold"][source_type]
        metrics["models"] = {
            model: {
                "sampling_design_delete_1_jackknife_95_ci": {
                    "method": "stratified_delete_1_jackknife_srswor_fpc/v1",
                    **design,
                    "accuracy": {
                        key: value
                        for key, value in interval.items()
                        if key != "two_sided_normal_p_value"
                    },
                    "macro_f1": {
                        key: value
                        for key, value in interval.items()
                        if key != "two_sided_normal_p_value"
                    },
                }
            }
            for model in (
                "kf_deberta_lora_locked",
                "kr_finbert_sc_raw_off_the_shelf",
                "pre_k_fnspid_kf_deberta",
                "kr_finbert_sc_same_data_fair",
                "kf_deberta_no_k_ablation",
            )
        }
        metrics["statistical_comparisons"] = {
            f"candidate_vs_{baseline}": {
                "paired_sampling_design_delete_1_jackknife_95_ci": {
                    "method": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
                    **design,
                    "accuracy_difference": dict(interval),
                    "macro_f1_difference": dict(interval)
                }
            }
            for baseline in (
                "kr_finbert_sc_raw_off_the_shelf",
                "pre_k_fnspid_kf_deberta",
                "kr_finbert_sc_same_data_fair",
                "kf_deberta_no_k_ablation",
            )
        }
        inference_sources[source_type] = {
            baseline: {
                "paired_sampling_design_jackknife_95_ci": dict(interval),
                "sampling_design_jackknife_normal_p_value": p_value,
                "holm_adjusted_p_value": p_value * 8,
                "statistically_superior": True,
            }
            for baseline in (
                "kr_finbert_sc_raw_off_the_shelf",
                "pre_k_fnspid_kf_deberta",
                "kr_finbert_sc_same_data_fair",
                "kf_deberta_no_k_ablation",
            )
        }
    benchmark["confirmatory_inference"] = {
        "family": (
            "NEWS/DISCLOSURE x raw KR-FinBERT-SC/pre-K-FNSPID/"
            "same-data KR-FinBERT-SC/no-K ablation"
        ),
        "family_hypothesis_count": 8,
        "multiple_comparison_correction": "Holm family-wise alpha=0.05",
        "primary_metric": "sampling-design-weighted plug-in Macro-F1",
        "paired_inference": (
            "stratified SRSWOR delete-1 jackknife with finite-population correction; "
            "Holm-adjusted paired normal tests"
        ),
        "sources": inference_sources,
        "raw_kr_finbert_reference_superiority_claim_allowed": True,
        "pre_k_fnspid_superiority_claim_allowed": True,
        "fair_baseline_superiority_claim_allowed": True,
        "no_k_ablation_superiority_claim_allowed": True,
        "qwen_confirmatory_exclusion": {
            "model": "Qwen3-4B-GGUF-Q4",
            "role": "blind_teacher_diagnostic_only",
            "affects_deployment_gate": False,
            "included_in_holm_family": False,
        },
        "target_aware_kr_finbert_input_ablation": {
            "role": "candidate_input_format_diagnostic_non_claim"
        },
        "global_sota_claim_allowed": False,
    }
    gate = benchmark["deployment_gate"]
    gate["thresholds"] = {
        "minimum_sealed_sample_count_per_source": 500,
        "minimum_sealed_accuracy_per_source": 0.90,
        "minimum_sealed_macro_f1_per_source": 0.85,
        "sealed_must_not_regress_vs_current_tfidf": True,
        "sealed_must_match_or_exceed_reference_family": [
            "target-aware snunlp/KR-FinBERT-SC",
            "raw snunlp/KR-FinBERT-SC",
            "same-data/split/selection-budget full-finetuned snunlp/KR-FinBERT-SC",
            "locked KF-DeBERTa no-K-FNSPID ablation",
        ],
        "blind_teacher_diagnostic_only_not_gating": "Qwen3-4B-GGUF-Q4",
        "sealed_must_improve_vs_pre_k_fnspid_model": True,
        "confirmatory_superiority_requires": "SRSWOR FPC delete-1 jackknife and Holm",
    }
    gate["secondary_regression_diagnostics"] = {
        "role": "repeatedly_exposed_secondary_regression_set_non_gating",
        "affects_deployment_decision": False,
    }
    gate["checks"] = expected_sentiment_gate_checks(benchmark)
    gate["decision"] = "DEPLOY_HANA_MONTANA_AI"
    return training, benchmark


def test_sentiment_gate_recomputes_metrics_before_accepting_eligibility() -> None:
    training, benchmark = _eligible_sentiment_reports()

    assert sentiment_gate_passed(training, benchmark)

    benchmark["deployment_gate"]["eligible"] = False
    assert not sentiment_gate_passed(training, benchmark)

    benchmark["deployment_gate"]["eligible"] = True
    benchmark["source_sealed_gold"]["NEWS"]["accuracy"] = 0.89
    assert not sentiment_gate_passed(training, benchmark)


@pytest.mark.parametrize("source_type", ("NEWS", "DISCLOSURE"))
def test_sentiment_gate_requires_each_source_sealed_gold(source_type: str) -> None:
    training, benchmark = _eligible_sentiment_reports()
    del benchmark["source_sealed_gold"][source_type]

    assert not sentiment_gate_passed(training, benchmark)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("sample_count", 499),
        ("accuracy", 0.8999),
        ("macro_f1", 0.8499),
        ("baseline_accuracy", 0.92),
        ("baseline_macro_f1", 0.87),
        ("kr_finbert_sc_macro_f1", 0.87),
        ("pre_k_fnspid_macro_f1", 0.86),
        ("no_k_ablation_macro_f1", 0.87),
    ),
)
def test_sentiment_gate_rejects_weak_or_regressed_source_metrics(
    field: str,
    value: int | float,
) -> None:
    training, benchmark = _eligible_sentiment_reports()
    benchmark["source_sealed_gold"]["DISCLOSURE"][field] = value

    assert not sentiment_gate_passed(training, benchmark)


def test_sentiment_gate_keeps_qwen_teacher_as_non_gating_diagnostic() -> None:
    training, benchmark = _eligible_sentiment_reports()
    benchmark["source_sealed_gold"]["DISCLOSURE"][
        "qwen3_4b_teacher_macro_f1"
    ] = 1.0

    assert sentiment_gate_passed(training, benchmark)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("sample_count", 899),
        ("macro_f1", 0.8499),
        ("kr_finbert_sc_macro_f1", 0.87),
        ("pre_k_fnspid_macro_f1", 0.87),
    ),
)
def test_sentiment_gate_keeps_public_test_as_non_gating_diagnostic(
    field: str,
    value: int | float,
) -> None:
    training, benchmark = _eligible_sentiment_reports()
    benchmark["public_test"][field] = value

    assert sentiment_gate_passed(training, benchmark)


@pytest.mark.parametrize(
    "mutation",
    (
        "training_version",
        "gate_version",
        "lock_hash",
        "gate_hash",
        "feature_version",
        "logit_bias",
    ),
)
def test_sentiment_gate_requires_matching_locked_artifact_contract(
    mutation: str,
) -> None:
    training, benchmark = _eligible_sentiment_reports()
    if mutation == "training_version":
        training["version"] = "different"
    elif mutation == "gate_version":
        benchmark["deployment_gate"]["candidate_version"] = "different"
    elif mutation == "lock_hash":
        benchmark["candidate_lock"]["artifact_manifest_sha256"] = "0" * 64
    elif mutation == "gate_hash":
        benchmark["deployment_gate"]["candidate_artifact_manifest_sha256"] = "0" * 64
    elif mutation == "feature_version":
        training["input_feature_version"] = "legacy/v1"
    else:
        benchmark["candidate_lock"]["logit_bias_by_domain"]["NEWS_TARGETED"] = [
            0.0,
            0.0,
            0.0,
        ]

    assert not sentiment_gate_passed(training, benchmark)


def test_sentiment_gate_rejects_old_report() -> None:
    training, benchmark = _eligible_sentiment_reports()
    benchmark["schema_version"] = "korean-finance-sentiment-benchmark/v3"
    assert not sentiment_gate_passed(training, benchmark)


@pytest.mark.parametrize(
    "candidate_model",
    (
        "kf_deberta_lora",
        "kf_deberta_lora_stacker",
        "kf_deberta_lora_ensemble",
        "kf_deberta_lora_calibrated",
    ),
)
def test_sentiment_gate_rejects_unserved_candidate(candidate_model: str) -> None:
    training, benchmark = _eligible_sentiment_reports()
    benchmark["deployment_gate"]["candidate_model"] = candidate_model
    assert not sentiment_gate_passed(training, benchmark)


def test_sentiment_model_uses_shared_source_input_encoder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, str, str, int, str]] = []

    def fake_encode(
        tokenizer: object,
        text: str,
        source_type: str,
        max_length: int,
        target_security: str,
    ) -> dict[str, list[int]]:
        calls.append((tokenizer, text, source_type, max_length, target_security))
        return {"input_ids": [1, 2], "attention_mask": [1, 1]}

    class FakeValues:
        def cpu(self) -> "FakeValues":
            return self

        def tolist(self) -> list[float]:
            return [0.2, 0.3, 0.5]

    class FakeLogits:
        def __init__(self) -> None:
            self.applied_bias: tuple[float, ...] | None = None

        def __getitem__(self, index: int) -> "FakeLogits":
            assert index == 0
            return self

        def new_tensor(self, values: tuple[float, ...]) -> tuple[float, ...]:
            return values

        def __add__(self, bias: tuple[float, ...]) -> "FakeLogits":
            self.applied_bias = bias
            return self

    class FakeTorch:
        @staticmethod
        def tensor(values: list[list[int]]) -> list[list[int]]:
            return values

        @staticmethod
        def inference_mode() -> Any:
            return nullcontext()

        @staticmethod
        def softmax(logits: object, dim: int) -> FakeValues:
            assert dim == -1
            return FakeValues()

    class FakeModel:
        def __init__(self) -> None:
            self.encoded: dict[str, Any] | None = None
            self.logits = FakeLogits()

        def __call__(self, **encoded: Any) -> SimpleNamespace:
            self.encoded = encoded
            return SimpleNamespace(logits=self.logits)

    monkeypatch.setattr(sentiment_module, "encode_sentiment_input", fake_encode)
    model = object.__new__(KfDebertaSentimentModel)
    model.enabled = True
    model.max_length = 192
    model._input_feature_version = "source-target-prefix-head-tail/v2"
    model._logit_bias_by_domain = {
        "NEWS_UNTARGETED": (0.0, 0.0, 0.0),
        "NEWS_TARGETED": (-0.1, 0.2, -0.1),
        "DISCLOSURE_TARGETED": (0.0, 0.1, -0.1),
    }
    model._eligible_sources = frozenset({"NEWS", "DISCLOSURE"})
    model._torch = FakeTorch()
    model._tokenizer = object()
    model._model = FakeModel()

    assert model.probabilities("장문 공시", "disclosure", "하나금융지주") == {
        "NEGATIVE": 0.2,
        "NEUTRAL": 0.3,
        "POSITIVE": 0.5,
    }
    assert calls == [
        (model._tokenizer, "장문 공시", "DISCLOSURE", 192, "하나금융지주")
    ]
    assert model._model.encoded == {
        "input_ids": [[1, 2]],
        "attention_mask": [[1, 1]],
    }
    assert model._model.logits.applied_bias == (0.0, 0.1, -0.1)

    assert model.probabilities("입력", "SOCIAL") is None
    assert model.probabilities("대상 없는 공시", "DISCLOSURE") is None
    assert len(calls) == 1


def test_analyzer_serves_confirmatory_release_without_legacy_stacker() -> None:
    analyzer = object.__new__(AlertAnalyzer)
    analyzer.model = SimpleNamespace(
        sentiment_probabilities=lambda _text: {
            "NEGATIVE": 0.6,
            "NEUTRAL": 0.3,
            "POSITIVE": 0.1,
        }
    )
    release_probabilities = {
        "NEGATIVE": 0.1,
        "NEUTRAL": 0.2,
        "POSITIVE": 0.7,
    }
    analyzer.sentiment_transformer = SimpleNamespace(
        enabled=True,
        release_id="sentiment-release-v2",
        probabilities=lambda *_args: dict(release_probabilities),
    )

    def forbidden_stacker(**_kwargs: object) -> None:
        pytest.fail("확증 release 출력에 legacy stacker를 적용하면 안 됩니다.")

    analyzer.sentiment_stacker = SimpleNamespace(probabilities=forbidden_stacker)

    assert analyzer._sentiment_probabilities("본문", "NEWS") == release_probabilities


def test_impact_gate_requires_large_temporal_test_and_ordinal_quality() -> None:
    report: dict[str, Any] = {
        "test": {"sample_count": 999, "macro_f1": 0.5, "quadratic_kappa": 0.4},
        "deployment_gate": {"eligible": True},
    }

    assert not impact_gate_passed(report)

    report["test"]["sample_count"] = 1_000
    assert impact_gate_passed(report)


def test_impact_gate_requires_matching_source_expert() -> None:
    report = {
        "source_type": "DISCLOSURE",
        "test": {"sample_count": 590, "macro_f1": 0.34, "quadratic_kappa": 0.12},
        "deployment_gate": {
            "minimum_test_sample_count": 500,
            "minimum_macro_f1": 0.30,
            "minimum_quadratic_kappa": 0.08,
            "eligible": True,
        },
    }

    assert impact_gate_passed(report, "DISCLOSURE")
    assert not impact_gate_passed(report, "NEWS")


def test_impact_log_prior_correction_requires_validation_provenance() -> None:
    report = {
        "postprocessing": {
            "method": "validation-selected-log-prior-correction/v1",
            "selection_partition": "VALIDATION",
            "selected_strength": 0.5,
            "training_class_priors": {
                "LOW": 0.7,
                "MEDIUM": 0.2,
                "HIGH": 0.08,
                "CRITICAL": 0.02,
            },
        }
    }

    offsets = _log_prior_offsets(report)
    assert offsets is not None
    assert offsets[0] > offsets[-1]

    report["postprocessing"]["selection_partition"] = "TEST"
    assert _log_prior_offsets(report) is None


def test_impact_log_prior_temperature_v2_uses_validation_provenance() -> None:
    report = {
        "postprocessing": {
            "method": "validation-selected-log-prior-temperature/v2",
            "selection_partition": "VALIDATION",
            "selected_strength": 0.35,
            "selected_temperature": 0.9,
            "training_class_priors": {
                "LOW": 0.7,
                "MEDIUM": 0.2,
                "HIGH": 0.08,
                "CRITICAL": 0.02,
            },
        }
    }

    assert _log_prior_offsets(report) is not None
    assert _temperature(report) == 0.9

    report["postprocessing"]["method"] = "unreviewed-postprocessing/v3"
    assert _log_prior_offsets(report) is None


@pytest.mark.parametrize(
    ("source_type", "artifact_dir", "report_path"),
    (
        (
            "NEWS",
            "src/hannah_montana_ai/model_store/k_fnspid_impact_news_transformer",
            "reports/k-fnspid-impact-news-transformer-training-report.json",
        ),
        (
            "DISCLOSURE",
            "src/hannah_montana_ai/model_store/k_fnspid_impact_disclosure_transformer",
            "reports/k-fnspid-impact-disclosure-transformer-training-report.json",
        ),
    ),
)
def test_promoted_impact_experts_satisfy_runtime_contract(
    source_type: str,
    artifact_dir: str,
    report_path: str,
) -> None:
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))

    assert impact_gate_passed(report, source_type)
    assert verify_artifact_manifest(Path(artifact_dir), report["artifact_files"])
    assert _log_prior_offsets(report) is not None
    assert _temperature(report) is not None


def test_current_impact_feature_requires_postprocessing() -> None:
    assert _log_prior_offsets({"input_feature_version": "k-fnspid-text-v2"}) is None
    assert _log_prior_offsets({"input_feature_version": "k-fnspid-text-v1"}) == [
        0.0,
        0.0,
        0.0,
        0.0,
    ]


def test_impact_temperature_requires_validation_selection() -> None:
    report = {
        "postprocessing": {
            "selection_partition": "VALIDATION",
            "selected_temperature": 1.35,
        }
    }

    assert _temperature(report) == 1.35
    report["postprocessing"]["selection_partition"] = "TEST"
    assert _temperature(report) is None


def test_artifact_manifest_rejects_tampered_file(tmp_path: Path) -> None:
    artifact = tmp_path / "adapter_model.safetensors"
    artifact.write_bytes(b"verified")
    manifest = build_artifact_manifest(tmp_path, (artifact.name,))

    assert verify_artifact_manifest(tmp_path, manifest)

    artifact.write_bytes(b"tampered")
    assert not verify_artifact_manifest(tmp_path, manifest)


def test_artifact_manifest_rejects_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target.safetensors"
    target.write_bytes(b"verified")
    linked = tmp_path / "adapter_model.safetensors"
    linked.symlink_to(target.name)
    manifest = {
        linked.name: {
            "bytes": target.stat().st_size,
            "sha256": "a9f096bb7506ebc6f281f6a47d14b45f4af9dc9e5ef2465e7615ba9f329768e8",
        }
    }

    assert not verify_artifact_manifest(tmp_path, manifest)
    with pytest.raises(ValueError, match="symlink"):
        build_artifact_manifest(tmp_path, (linked.name,))


def test_transformers_fall_back_when_optional_runtime_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)

    sentiment = KfDebertaSentimentModel(
        Path("src/hannah_montana_ai/model_store/kf_deberta_sentiment"),
        Path("reports/kf-deberta-sentiment-training-report.json"),
        Path("reports/korean-finance-sentiment-benchmark.json"),
        Path("/missing/base-model"),
    )
    impact = KfDebertaImpactModel(
        Path("src/hannah_montana_ai/model_store/k_fnspid_impact_transformer"),
        Path("reports/k-fnspid-transformer-training-report.json"),
        Path("/missing/base-model"),
    )

    assert sentiment.enabled is False
    assert impact.enabled is False
