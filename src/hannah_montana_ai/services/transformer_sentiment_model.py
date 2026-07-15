from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.model_artifact_integrity import (
    verify_artifact_manifest,
)
from hannah_montana_ai.services.sentiment_calibration import apply_source_logit_bias

BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")


class KfDebertaSentimentModel:
    def __init__(
        self,
        adapter_path: Path,
        training_report_path: Path,
        benchmark_report_path: Path,
        local_base_model_path: Path,
    ) -> None:
        self.enabled = False
        self.version = "kf-deberta-sentiment-unavailable"
        self.max_length = 192
        self.transformer_weight = 0.8
        self.source_biases: dict[str, dict[str, float]] = {}
        self._torch: Any = None
        self._tokenizer: Any = None
        self._model: Any = None
        if not all(
            path.exists() for path in (adapter_path, training_report_path, benchmark_report_path)
        ):
            return
        training_report = json.loads(training_report_path.read_text(encoding="utf-8"))
        benchmark_report = json.loads(benchmark_report_path.read_text(encoding="utf-8"))
        if not _deployment_gate_passed(
            training_report, benchmark_report
        ) or not verify_artifact_manifest(adapter_path, training_report.get("artifact_files")):
            return

        # 기본 설치에서는 선택 의존성이 없으므로 기존 모델로 안전하게 축소 운용한다.
        try:
            import torch
            from peft import PeftModel
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ModuleNotFoundError as exception:
            if exception.name not in {"torch", "peft", "transformers"}:
                raise
            return

        local_base = local_base_model_path.is_dir()
        base_reference = str(local_base_model_path) if local_base else BASE_MODEL
        base_options: dict[str, Any] = {
            "trust_remote_code": False,
            "local_files_only": local_base,
        }
        # 어댑터 경로는 배포 gate를 통과한 로컬 디렉터리만 허용한다.
        tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
            adapter_path,
            revision="local-verified-artifact",
            trust_remote_code=False,
            local_files_only=True,
        )
        base = AutoModelForSequenceClassification.from_pretrained(
            base_reference,
            revision=BASE_MODEL_REVISION if not local_base else "local-safe-artifact",
            num_labels=len(LABEL_ORDER),
            id2label={index: label for index, label in enumerate(LABEL_ORDER)},
            label2id={label: index for index, label in enumerate(LABEL_ORDER)},
            use_safetensors=local_base,
            **base_options,
        )
        model = PeftModel.from_pretrained(
            base,
            adapter_path,
            is_trainable=False,
            use_safetensors=True,
        )
        model.eval()
        self._torch = torch
        self._tokenizer = tokenizer
        self._model = model
        self.max_length = int(training_report.get("max_length", 192))
        candidate_name = str(benchmark_report.get("deployment_gate", {}).get("candidate_model", ""))
        self.transformer_weight = (
            1.0 if candidate_name in {"kf_deberta_lora", "kf_deberta_lora_calibrated"} else 0.8
        )
        if candidate_name == "kf_deberta_lora_calibrated":
            configured = (
                benchmark_report.get("candidate_selection", {})
                .get("calibration", {})
                .get("source_biases", {})
            )
            if isinstance(configured, dict):
                self.source_biases = {
                    str(source_type).upper(): {
                        str(label): float(bias)
                        for label, bias in biases.items()
                        if isinstance(bias, int | float)
                    }
                    for source_type, biases in configured.items()
                    if isinstance(biases, dict)
                }
        self.version = str(training_report["version"])
        self.enabled = True

    def probabilities(self, text: str, source_type: str = "NEWS") -> dict[str, float] | None:
        if not self.enabled or self._model is None:
            return None
        encoded = self._tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        with self._torch.inference_mode():
            logits = self._model(**encoded).logits[0]
            values = self._torch.softmax(logits, dim=-1).cpu().tolist()
        probabilities = {
            label: float(probability)
            for label, probability in zip(LABEL_ORDER, values, strict=True)
        }
        return apply_source_logit_bias(probabilities, source_type, self.source_biases)


def _deployment_gate_passed(
    training_report: dict[str, Any],
    benchmark_report: dict[str, Any],
) -> bool:
    test = training_report.get("test", {})
    gate = benchmark_report.get("deployment_gate", {})
    models = benchmark_report.get("models", {})
    candidate_name = benchmark_report.get("deployment_gate", {}).get(
        "candidate_model", "kf_deberta_lora_ensemble"
    )
    benchmark = models.get(
        candidate_name,
        models.get("kf_deberta_lora_ensemble", models.get("kf_deberta_lora", {})),
    )
    selection = benchmark_report.get("candidate_selection", {})
    return (
        int(test.get("sample_count", 0)) >= 900
        and float(test.get("macro_f1", 0.0)) >= 0.85
        and int(benchmark_report.get("sample_count", 0)) >= 900
        and float(benchmark.get("macro_f1", 0.0)) >= 0.85
        and gate.get("candidate_locked_before_current_evaluation") is True
        and selection.get("candidate_frozen_before_current_evaluation") is True
        and selection.get("historical_public_test_exposure_disclosed") is True
        and isinstance(selection.get("artifact_historically_exposed_to_public_test"), bool)
        and selection.get("test_used_for_selection") is False
        and selection.get("operational_gold_used_for_selection") is False
        and gate.get("eligible") is True
    )


@lru_cache(maxsize=1)
def load_kf_deberta_sentiment_model(
    adapter_path: Path,
    training_report_path: Path,
    benchmark_report_path: Path,
    local_base_model_path: Path,
) -> KfDebertaSentimentModel:
    return KfDebertaSentimentModel(
        adapter_path,
        training_report_path,
        benchmark_report_path,
        local_base_model_path,
    )
