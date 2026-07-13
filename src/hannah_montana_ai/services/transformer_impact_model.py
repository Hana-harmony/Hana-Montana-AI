from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from hannah_montana_ai.domain.schemas import Importance
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
        self._torch: Any = None
        self._tokenizer: Any = None
        self._model: Any = None
        if not adapter_path.exists() or not report_path.exists():
            return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if not _deployment_gate_passed(report) or not verify_artifact_manifest(
            adapter_path, report.get("artifact_files")
        ):
            return

        # 서빙에서는 검증된 LoRA safetensors와 고정된 베이스 리비전만 사용한다.
        import torch
        from peft import PeftModel
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

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
        self.version = str(report["version"])
        self.enabled = True

    def predict(self, text: str) -> MarketImpactPrediction | None:
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


@lru_cache(maxsize=1)
def load_kf_deberta_impact_model(
    adapter_path: Path,
    report_path: Path,
    local_base_model_path: Path,
) -> KfDebertaImpactModel:
    return KfDebertaImpactModel(adapter_path, report_path, local_base_model_path)
