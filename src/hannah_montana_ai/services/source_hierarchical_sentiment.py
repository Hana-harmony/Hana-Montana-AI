from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, NamedTuple, cast

from hannah_montana_ai.services.sentiment_input import encode_sentiment_input

SentimentLabel = Literal["NEGATIVE", "NEUTRAL", "POSITIVE"]
SentimentDomain = Literal[
    "NEWS_UNTARGETED",
    "NEWS_TARGETED",
    "DISCLOSURE_TARGETED",
]

LABEL_ORDER: tuple[SentimentLabel, ...] = ("NEGATIVE", "NEUTRAL", "POSITIVE")
DOMAIN_ORDER: tuple[SentimentDomain, ...] = (
    "NEWS_UNTARGETED",
    "NEWS_TARGETED",
    "DISCLOSURE_TARGETED",
)
DOMAIN_TO_ID = {domain: index for index, domain in enumerate(DOMAIN_ORDER)}
ANCHOR_DOMAIN: SentimentDomain = "NEWS_UNTARGETED"
RESIDUAL_DOMAINS: tuple[SentimentDomain, ...] = (
    "NEWS_TARGETED",
    "DISCLOSURE_TARGETED",
)
HEAD_ARCHITECTURE_VERSION = "shared-hierarchical-zero-residual/v2"
HEAD_ARTIFACT_FILENAME = "source_hierarchical_residual_heads.safetensors"
INPUT_FEATURE_VERSION = "source-target-prefix-head-tail/v2"
TEMPERATURE_GRID = tuple(
    round(value, 2) for value in (0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2)
)
NEUTRAL_THRESHOLD_GRID = tuple(
    round(value, 3)
    for value in (
        0.30,
        0.325,
        0.35,
        0.375,
        0.40,
        0.425,
        0.45,
        0.475,
        0.50,
        0.525,
        0.55,
        0.575,
        0.60,
    )
)


class SentimentInputContractError(ValueError):
    pass


class SourceHierarchicalRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DomainCalibration:
    temperature: float
    neutral_threshold: float
    sample_count: int
    fit_status: str


@dataclass(frozen=True, slots=True)
class SentimentPrediction:
    label: SentimentLabel
    calibrated_probabilities: dict[SentimentLabel, float]
    domain: SentimentDomain
    temperature: float
    neutral_threshold: float


class SourceHierarchicalOutput(NamedTuple):
    logits: Any
    boundary_logits: Any
    direction_logits: Any


def strict_sentiment_domain(source_type: str, target_security: str = "") -> SentimentDomain:
    source = source_type.strip().upper()
    target = target_security.strip()
    if source == "NEWS":
        return "NEWS_TARGETED" if target else "NEWS_UNTARGETED"
    if source == "DISCLOSURE":
        if not target:
            raise SentimentInputContractError(
                "공시 감성 추론에는 검증된 target_security가 필요합니다."
            )
        return "DISCLOSURE_TARGETED"
    raise SentimentInputContractError(f"지원하지 않는 감성 source_type입니다: {source_type!r}")


def validate_domain_calibration(value: object) -> dict[SentimentDomain, DomainCalibration]:
    if not isinstance(value, Mapping) or set(value) != set(DOMAIN_ORDER):
        raise ValueError("v6 감성 domain calibration 구성이 올바르지 않습니다.")
    result: dict[SentimentDomain, DomainCalibration] = {}
    for domain in DOMAIN_ORDER:
        raw = value.get(domain)
        if not isinstance(raw, Mapping) or set(raw) != {
            "temperature",
            "neutral_threshold",
            "sample_count",
            "fit_status",
        }:
            raise ValueError(f"v6 감성 calibration 필드가 올바르지 않습니다: {domain}")
        temperature = _finite_float(raw.get("temperature"), f"{domain} temperature")
        threshold = _finite_float(raw.get("neutral_threshold"), f"{domain} neutral threshold")
        sample_count = raw.get("sample_count")
        fit_status = raw.get("fit_status")
        if (
            temperature not in TEMPERATURE_GRID
            or threshold not in NEUTRAL_THRESHOLD_GRID
            or isinstance(sample_count, bool)
            or not isinstance(sample_count, int)
            or sample_count < 0
            or fit_status
            not in {
                "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK",
                "INSUFFICIENT_CALIBRATION_ROWS_DEFAULTED",
            }
        ):
            raise ValueError(f"v6 감성 calibration 값이 올바르지 않습니다: {domain}")
        if fit_status == "INSUFFICIENT_CALIBRATION_ROWS_DEFAULTED":
            if temperature != 1.0 or threshold != 0.5:
                raise ValueError("부족 표본 calibration은 고정 기본값만 허용합니다.")
        elif sample_count < 30:
            raise ValueError("학습된 domain calibration에는 최소 30개 표본이 필요합니다.")
        result[domain] = DomainCalibration(
            temperature=temperature,
            neutral_threshold=threshold,
            sample_count=sample_count,
            fit_status=str(fit_status),
        )
    return result


def calibrated_sentiment_prediction(
    log_probabilities: Sequence[float],
    domain: SentimentDomain,
    calibration_by_domain: Mapping[SentimentDomain, DomainCalibration],
) -> SentimentPrediction:
    if domain not in DOMAIN_TO_ID or len(log_probabilities) != len(LABEL_ORDER):
        raise ValueError("v6 감성 추론 출력 차원이 올바르지 않습니다.")
    values = [_finite_float(value, "v6 감성 log probability") for value in log_probabilities]
    calibration = calibration_by_domain.get(domain)
    if calibration is None:
        raise ValueError("v6 감성 domain calibration이 없습니다.")
    scaled = [value / calibration.temperature for value in values]
    maximum = max(scaled)
    exponentials = [math.exp(value - maximum) for value in scaled]
    denominator = sum(exponentials)
    if not math.isfinite(denominator) or denominator <= 0.0:
        raise ValueError("v6 감성 확률을 정규화할 수 없습니다.")
    probability_values = [value / denominator for value in exponentials]
    if probability_values[1] >= calibration.neutral_threshold:
        label: SentimentLabel = "NEUTRAL"
    else:
        label = "NEGATIVE" if probability_values[0] >= probability_values[2] else "POSITIVE"
    probabilities = {
        label_name: probability
        for label_name, probability in zip(LABEL_ORDER, probability_values, strict=True)
    }
    return SentimentPrediction(
        label=label,
        calibrated_probabilities=probabilities,
        domain=domain,
        temperature=calibration.temperature,
        neutral_threshold=calibration.neutral_threshold,
    )


def prediction_from_probabilities(
    probabilities: Mapping[str, float],
    source_type: str,
    target_security: str = "",
) -> SentimentPrediction:
    source = source_type.strip().upper()
    if source not in {"NEWS", "DISCLOSURE"}:
        raise SentimentInputContractError(f"지원하지 않는 감성 source_type입니다: {source_type!r}")
    domain: SentimentDomain
    if source == "DISCLOSURE":
        domain = "DISCLOSURE_TARGETED"
    else:
        domain = "NEWS_TARGETED" if target_security.strip() else "NEWS_UNTARGETED"
    normalized: dict[SentimentLabel, float] = {}
    total = 0.0
    for label in LABEL_ORDER:
        probability = _finite_float(probabilities.get(label), f"{label} probability")
        if probability < 0.0:
            raise ValueError("감성 확률은 음수일 수 없습니다.")
        normalized[label] = probability
        total += probability
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("감성 확률 합계가 올바르지 않습니다.")
    normalized = {label: value / total for label, value in normalized.items()}
    label = max(LABEL_ORDER, key=lambda name: normalized[name])
    return SentimentPrediction(
        label=label,
        calibrated_probabilities=normalized,
        domain=domain,
        temperature=1.0,
        neutral_threshold=0.5,
    )


def compose_hierarchical_log_probabilities(
    boundary_logits: Any,
    direction_logits: Any,
) -> Any:
    import torch
    import torch.nn.functional as functional

    if boundary_logits.ndim != 1 or tuple(direction_logits.shape) != (
        boundary_logits.shape[0],
        2,
    ):
        raise ValueError("계층형 감성 출력 형상이 올바르지 않습니다.")
    directional = functional.logsigmoid(boundary_logits)
    neutral = functional.logsigmoid(-boundary_logits)
    polarity = functional.log_softmax(direction_logits, dim=-1)
    return torch.stack(
        (
            directional + polarity[:, 0],
            neutral,
            directional + polarity[:, 1],
        ),
        dim=-1,
    )


def build_source_hierarchical_classifier(
    encoder: Any,
    hidden_size: int,
    *,
    dropout: float = 0.12,
) -> Any:
    import torch
    from torch import nn

    if hidden_size < 1 or not 0.0 <= dropout < 1.0:
        raise ValueError("계층형 감성 head 설정이 올바르지 않습니다.")

    class _SharedHead(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.normalization = nn.LayerNorm(hidden_size)
            self.dropout = nn.Dropout(dropout)
            self.boundary = nn.Linear(hidden_size, 1)
            self.direction = nn.Linear(hidden_size, 2)

        def forward(self, pooled: Any) -> tuple[Any, Any, Any]:
            hidden = self.dropout(self.normalization(pooled))
            return hidden, self.boundary(hidden).squeeze(-1), self.direction(hidden)

    class _ZeroResidualHead(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.boundary = nn.Linear(hidden_size, 1)
            self.direction = nn.Linear(hidden_size, 2)
            nn.init.zeros_(self.boundary.weight)
            nn.init.zeros_(self.boundary.bias)
            nn.init.zeros_(self.direction.weight)
            nn.init.zeros_(self.direction.bias)

        def forward(self, hidden: Any) -> tuple[Any, Any]:
            return self.boundary(hidden).squeeze(-1), self.direction(hidden)

    class _SourceClassifier(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = encoder
            self.shared_head = _SharedHead()
            self.domain_residuals = nn.ModuleDict(
                {domain: _ZeroResidualHead() for domain in RESIDUAL_DOMAINS}
            )

        def forward(
            self,
            input_ids: Any,
            attention_mask: Any,
            domain_ids: Any | None = None,
            token_type_ids: Any | None = None,
        ) -> SourceHierarchicalOutput:
            if domain_ids is None:
                raise ValueError("서비스 감성 추론에는 source domain이 반드시 필요합니다.")
            if (
                domain_ids.ndim != 1
                or domain_ids.shape[0] != input_ids.shape[0]
                or bool((domain_ids < 0).any())
                or bool((domain_ids >= len(DOMAIN_ORDER)).any())
            ):
                raise ValueError("감성 source domain id 계약이 올바르지 않습니다.")
            encoder_inputs: dict[str, Any] = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
            }
            if token_type_ids is not None:
                encoder_inputs["token_type_ids"] = token_type_ids
            encoded = self.encoder(**encoder_inputs, return_dict=True)
            hidden = getattr(encoded, "last_hidden_state", None)
            if not isinstance(hidden, torch.Tensor) or hidden.ndim != 3:
                raise RuntimeError("KF-DeBERTa encoder 출력 계약이 올바르지 않습니다.")
            pooled = hidden[:, 0]
            route = domain_ids.to(device=pooled.device, dtype=torch.long)
            hidden, selected_boundary, selected_direction = self.shared_head(pooled)
            boundary_residual = torch.zeros_like(selected_boundary)
            direction_residual = torch.zeros_like(selected_direction)
            for domain in RESIDUAL_DOMAINS:
                selected = route == DOMAIN_TO_ID[domain]
                if not bool(selected.any()):
                    continue
                residual_boundary, residual_direction = self.domain_residuals[domain](
                    hidden
                )
                boundary_mask = selected.to(dtype=residual_boundary.dtype)
                direction_mask = boundary_mask.unsqueeze(-1)
                boundary_residual = boundary_residual + residual_boundary * boundary_mask
                direction_residual = direction_residual + residual_direction * direction_mask
            selected_boundary = selected_boundary + boundary_residual
            selected_direction = selected_direction + direction_residual
            logits = compose_hierarchical_log_probabilities(
                selected_boundary,
                selected_direction,
            )
            return SourceHierarchicalOutput(logits, selected_boundary, selected_direction)

    return _SourceClassifier()


def source_hierarchical_head_state_dict(model: Any) -> dict[str, Any]:
    shared = getattr(model, "shared_head", None)
    residuals = getattr(model, "domain_residuals", None)
    if shared is None or residuals is None or set(residuals) != set(RESIDUAL_DOMAINS):
        raise SourceHierarchicalRuntimeError("v2 shared-residual 감성 head 구조가 없습니다.")
    return {
        **{f"shared_head.{name}": tensor for name, tensor in shared.state_dict().items()},
        **{f"domain_residuals.{name}": tensor for name, tensor in residuals.state_dict().items()},
    }


def load_source_hierarchical_heads(model: Any, path: Path) -> None:
    import torch
    from safetensors import SafetensorError
    from safetensors.torch import load_file

    if path.is_symlink() or not path.is_file():
        raise SourceHierarchicalRuntimeError("v6 감성 head artifact가 없습니다.")
    try:
        state = load_file(str(path), device="cpu")
    except (OSError, ValueError, RuntimeError, SafetensorError) as exception:
        raise SourceHierarchicalRuntimeError(
            "v6 감성 head artifact를 읽을 수 없습니다."
        ) from exception
    expected = source_hierarchical_head_state_dict(model)
    if set(state) != set(expected):
        raise SourceHierarchicalRuntimeError("v6 감성 head tensor 집합이 다릅니다.")
    for name, tensor in state.items():
        reference = expected[name]
        if (
            tuple(tensor.shape) != tuple(reference.shape)
            or tensor.dtype != reference.dtype
            or not bool(torch.isfinite(tensor).all())
        ):
            raise SourceHierarchicalRuntimeError(f"v6 감성 head tensor 계약이 다릅니다: {name}")
    shared_prefix = "shared_head."
    residual_prefix = "domain_residuals."
    model.shared_head.load_state_dict(
        {
            name.removeprefix(shared_prefix): tensor
            for name, tensor in state.items()
            if name.startswith(shared_prefix)
        },
        strict=True,
    )
    model.domain_residuals.load_state_dict(
        {
            name.removeprefix(residual_prefix): tensor
            for name, tensor in state.items()
            if name.startswith(residual_prefix)
        },
        strict=True,
    )


class SourceHierarchicalSentimentRuntime:
    def __init__(
        self,
        *,
        model: Any,
        tokenizer: Any,
        torch_module: Any,
        max_length: int,
        calibration_by_domain: Mapping[SentimentDomain, DomainCalibration],
    ) -> None:
        self._model = model
        self._tokenizer = tokenizer
        self._torch = torch_module
        self._max_length = max_length
        self._calibration = dict(calibration_by_domain)

    def predict(
        self,
        text: str,
        source_type: str,
        target_security: str = "",
    ) -> SentimentPrediction:
        return self.predict_batch(((text, source_type, target_security),))[0]

    def predict_batch(
        self,
        items: Sequence[tuple[str, str, str]],
    ) -> list[SentimentPrediction]:
        if not items:
            return []
        domains: list[SentimentDomain] = []
        feature_rows: list[dict[str, list[int]]] = []
        expected_keys: set[str] | None = None
        for text, source_type, target_security in items:
            domain = strict_sentiment_domain(source_type, target_security)
            features = encode_sentiment_input(
                self._tokenizer,
                text,
                source_type.strip().upper(),
                self._max_length,
                target_security,
            )
            keys = set(features)
            if expected_keys is None:
                expected_keys = keys
            elif keys != expected_keys:
                raise SourceHierarchicalRuntimeError(
                    "v6 감성 tokenizer의 batch feature 집합이 다릅니다."
                )
            domains.append(domain)
            feature_rows.append(features)
        if expected_keys is None:
            raise SourceHierarchicalRuntimeError("v6 감성 batch feature가 없습니다.")
        sequence_length = max(
            len(values) for features in feature_rows for values in features.values()
        )
        pad_token_id = getattr(self._tokenizer, "pad_token_id", 0)
        if isinstance(pad_token_id, bool) or not isinstance(pad_token_id, int):
            pad_token_id = 0
        encoded = {
            name: self._torch.tensor(
                [
                    features[name]
                    + [pad_token_id if name == "input_ids" else 0]
                    * (sequence_length - len(features[name]))
                    for features in feature_rows
                ],
                dtype=self._torch.long,
            )
            for name in sorted(expected_keys)
        }
        encoded["domain_ids"] = self._torch.tensor(
            [DOMAIN_TO_ID[domain] for domain in domains],
            dtype=self._torch.long,
        )
        try:
            with self._torch.inference_mode():
                output = self._model(**encoded)
                values = output.logits.detach().to(dtype=self._torch.float64).cpu().tolist()
        except Exception as exception:
            raise SourceHierarchicalRuntimeError("v6 감성 추론 실행에 실패했습니다.") from exception
        if len(values) != len(domains):
            raise SourceHierarchicalRuntimeError("v6 감성 batch 출력 수가 입력과 다릅니다.")
        return [
            calibrated_sentiment_prediction(row, domain, self._calibration)
            for row, domain in zip(values, domains, strict=True)
        ]


def load_source_hierarchical_runtime(
    *,
    artifact_dir: Path,
    base_model_dir: Path,
    max_length: int,
    calibration_by_domain: Mapping[SentimentDomain, DomainCalibration],
) -> SourceHierarchicalSentimentRuntime:
    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModel, AutoTokenizer
    except ModuleNotFoundError as exception:
        raise SourceHierarchicalRuntimeError("v6 감성 실행 의존성이 없습니다.") from exception

    if (
        base_model_dir.is_symlink()
        or not base_model_dir.is_dir()
        or artifact_dir.is_symlink()
        or not artifact_dir.is_dir()
    ):
        raise SourceHierarchicalRuntimeError("v6 감성 base 또는 artifact 경로가 올바르지 않습니다.")
    try:
        tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
            artifact_dir,
            revision="local-verified-v6-artifact",
            trust_remote_code=False,
            local_files_only=True,
        )
        base = AutoModel.from_pretrained(  # nosec B615
            base_model_dir,
            revision="local-verified-v6-base",
            trust_remote_code=False,
            local_files_only=True,
            use_safetensors=True,
            weights_only=True,
        )
        encoder = PeftModel.from_pretrained(
            base,
            artifact_dir / "adapter",
            is_trainable=False,
            local_files_only=True,
            use_safetensors=True,
        )
        hidden_size = int(cast(Any, encoder.config).hidden_size)
        model = build_source_hierarchical_classifier(encoder, hidden_size)
        load_source_hierarchical_heads(
            model,
            artifact_dir / HEAD_ARTIFACT_FILENAME,
        )
        model.to(torch.device("cpu"))
        model.eval()
    except SourceHierarchicalRuntimeError:
        raise
    except Exception as exception:
        raise SourceHierarchicalRuntimeError(
            "v6 감성 runtime을 안전하게 load할 수 없습니다."
        ) from exception
    return SourceHierarchicalSentimentRuntime(
        model=model,
        tokenizer=tokenizer,
        torch_module=torch,
        max_length=max_length,
        calibration_by_domain=calibration_by_domain,
    )


def _finite_float(value: object, description: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{description} 값이 숫자가 아닙니다.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{description} 값이 유한하지 않습니다.")
    return result
