from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

from hannah_montana_ai.domain.schemas import Importance
from hannah_montana_ai.services.impact_model_features import (
    IMPACT_INPUT_FEATURE_VERSION,
    build_impact_model_text,
)
from hannah_montana_ai.services.market_impact_model import MarketImpactPrediction
from hannah_montana_ai.services.model_artifact_integrity import (
    verify_artifact_manifest,
)

BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
LABEL_ORDER: tuple[Importance, ...] = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


class KfDebertaImpactModel:
    def __init__(
        self,
        adapter_path: Path,
        report_path: Path,
        local_base_model_path: Path,
    ) -> None:
        self.enabled = False
        self.version = "kf-deberta-impact-unavailable"
        self.max_length = 256
        self.input_feature_version = "k-fnspid-text-v1"
        self.log_prior_offsets = [0.0] * len(LABEL_ORDER)
        self._torch: Any = None
        self._tokenizer: Any = None
        self._model: Any = None
        if not adapter_path.exists() or not report_path.exists():
            return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        log_prior_offsets = _log_prior_offsets(report)
        if (
            not _deployment_gate_passed(report)
            or not verify_artifact_manifest(adapter_path, report.get("artifact_files"))
            or log_prior_offsets is None
        ):
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
        self.max_length = int(report.get("max_length", 256))
        self.input_feature_version = str(report.get("input_feature_version", "k-fnspid-text-v1"))
        self.log_prior_offsets = log_prior_offsets
        self.version = str(report["version"])
        self.enabled = True

    def predict(self, text: str, source_type: str = "NEWS") -> MarketImpactPrediction | None:
        if not self.enabled or self._model is None:
            return None
        model_text = (
            build_impact_model_text(text, source_type)
            if self.input_feature_version == IMPACT_INPUT_FEATURE_VERSION
            else text
        )
        encoded = self._tokenizer(
            model_text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        with self._torch.inference_mode():
            logits = self._model(**encoded).logits[0]
            logits = logits + self._torch.tensor(
                self.log_prior_offsets,
                device=logits.device,
                dtype=logits.dtype,
            )
            probabilities = self._torch.softmax(logits, dim=-1).cpu().tolist()
        predicted_index = max(range(len(probabilities)), key=probabilities.__getitem__)
        materiality = sum(
            index * float(probability) for index, probability in enumerate(probabilities)
        ) / (len(LABEL_ORDER) - 1)
        return MarketImpactPrediction(
            importance=LABEL_ORDER[predicted_index],
            confidence=float(probabilities[predicted_index]),
            materiality_score=round(materiality, 6),
            model_version=self.version,
        )


def _deployment_gate_passed(report: dict[str, Any]) -> bool:
    test = report.get("test", {})
    gate = report.get("deployment_gate", {})
    return (
        int(test.get("sample_count", 0)) >= 1_000
        and float(test.get("macro_f1", 0.0)) >= 0.35
        and float(test.get("quadratic_kappa", 0.0)) >= 0.20
        and gate.get("eligible") is True
    )


def _log_prior_offsets(report: dict[str, Any]) -> list[float] | None:
    configured = report.get("postprocessing")
    if configured is None:
        return (
            None
            if report.get("input_feature_version") == IMPACT_INPUT_FEATURE_VERSION
            else [0.0] * len(LABEL_ORDER)
        )
    if (
        not isinstance(configured, dict)
        or configured.get("method") != "validation-selected-log-prior-correction/v1"
        or configured.get("selection_partition") != "VALIDATION"
    ):
        return None
    try:
        strength = float(configured["selected_strength"])
        prior_by_label = configured["training_class_priors"]
        priors = [float(prior_by_label[label]) for label in LABEL_ORDER]
    except (KeyError, TypeError, ValueError):
        return None
    if (
        not 0.0 <= strength <= 2.0
        or any(not math.isfinite(prior) or prior <= 0.0 for prior in priors)
        or not math.isclose(sum(priors), 1.0, rel_tol=0.0, abs_tol=1e-6)
    ):
        return None
    return [strength * math.log(prior) for prior in priors]


@lru_cache(maxsize=1)
def load_kf_deberta_impact_model(
    adapter_path: Path,
    report_path: Path,
    local_base_model_path: Path,
) -> KfDebertaImpactModel:
    return KfDebertaImpactModel(adapter_path, report_path, local_base_model_path)
