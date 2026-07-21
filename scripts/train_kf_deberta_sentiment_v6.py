from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import random
import shutil
import signal
import sys
import tempfile
import time
import uuid
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, cast

# 파일 경로 실행에서도 신뢰된 저장소 내부 모듈만 해석한다.
_DIRECT_EXECUTION_ROOT = Path(__file__).resolve().parents[1]
if __package__ in {None, ""} and str(_DIRECT_EXECUTION_ROOT) not in sys.path:
    sys.path.insert(0, str(_DIRECT_EXECUTION_ROOT))

import numpy as np
import torch
import torch.nn.functional as functional
from huggingface_hub import hf_hub_download
from numpy.typing import NDArray
from peft import LoraConfig, TaskType, get_peft_model
from safetensors.torch import load_file, save_file
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModel,
    AutoTokenizer,
    DataCollatorWithPadding,
    get_cosine_schedule_with_warmup,
)

try:
    from scripts import train_kf_deberta_sentiment_v2 as v5
except ImportError:  # pragma: no cover - scripts/ 직접 실행 경로
    v5_name = "train_kf_deberta_sentiment_v2"
    v5_module = sys.modules.get(v5_name)
    if v5_module is None:
        v5_spec = importlib.util.spec_from_file_location(
            v5_name,
            Path(__file__).with_name("train_kf_deberta_sentiment_v2.py"),
        )
        if v5_spec is None or v5_spec.loader is None:
            raise RuntimeError("v5 학습 계약을 load할 수 없습니다.") from None
        v5_module = importlib.util.module_from_spec(v5_spec)
        sys.modules[v5_name] = v5_module
        v5_spec.loader.exec_module(v5_module)
    v5 = cast(Any, v5_module)

from hannah_montana_ai.services.sentiment_artifact_contract import (
    ARTIFACT_MANIFEST_SCHEMA_VERSION as ARTIFACT_MANIFEST_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    ARTIFACT_SCHEMA_VERSION,
    TRAINING_SCHEMA_VERSION,
    validate_source_hierarchical_artifact,
    validate_source_hierarchical_base_directory,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    EXPECTED_HEAD_ARCHITECTURE as EXPECTED_HEAD_ARCHITECTURE,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    EXPECTED_HEAD_TENSOR_CONTRACT as EXPECTED_HEAD_TENSOR_CONTRACT,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    RUNTIME_LOADER_SCHEMA_VERSION as RUNTIME_LOADER_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_input import encode_sentiment_input
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    ANCHOR_DOMAIN,
    HEAD_ARCHITECTURE_VERSION,
    RESIDUAL_DOMAINS,
    DomainCalibration,
    SentimentDomain,
    SourceHierarchicalOutput,
    build_source_hierarchical_classifier,
    calibrated_sentiment_prediction,
    load_source_hierarchical_runtime,
    source_hierarchical_head_state_dict,
    strict_sentiment_domain,
    validate_domain_calibration,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    DOMAIN_ORDER as COMMON_DOMAIN_ORDER,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    DOMAIN_TO_ID as COMMON_DOMAIN_TO_ID,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    HEAD_ARTIFACT_FILENAME as HEAD_ARTIFACT_FILENAME,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    LABEL_ORDER as COMMON_LABEL_ORDER,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    NEUTRAL_THRESHOLD_GRID as COMMON_NEUTRAL_THRESHOLD_GRID,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    TEMPERATURE_GRID as COMMON_TEMPERATURE_GRID,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    compose_hierarchical_log_probabilities as common_compose_log_probabilities,
)
from hannah_montana_ai.training.sentiment_gold_provenance import (
    add_gold_provenance_arguments,
    gold_provenance_paths,
    validate_all_gold_provenance,
)
from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    decontaminate_public_partitions,
    purge_sentiment_group_overlap,
    stratified_hash_three_way_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LABEL_ORDER = tuple(COMMON_LABEL_ORDER)
DOMAIN_ORDER = tuple(COMMON_DOMAIN_ORDER)
DOMAIN_TO_ID = dict(COMMON_DOMAIN_TO_ID)
if tuple(v5.LABEL_ORDER) != LABEL_ORDER:
    raise RuntimeError("v5 data label 계약과 공용 runtime label 계약이 다릅니다.")
LORA_LAYERS = tuple(range(12))
LORA_TARGET_MODULES = ("query_proj", "key_proj", "value_proj", "dense")
LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.08
R_DROP_ALPHA = 0.25
BOUNDARY_LOSS_WEIGHT = 0.55
DIRECTION_LOSS_WEIGHT = 0.25
COMPOSITE_LOSS_WEIGHT = 0.20
BOUNDARY_LABEL_SMOOTHING = 0.03
DIRECTION_LABEL_SMOOTHING = 0.03
COMPOSITE_LABEL_SMOOTHING = 0.02
LOSS_CONTRACT_VERSION = "fixed-domain-task-cell-mass-hierarchical-ce/v3"
MAX_ACTIVE_CELL_MASS_RATIO = 10.0
MAX_SUPPORTED_CELL_MASS_RATIO = 25.0
MIN_HIGH_IMBALANCE_CELL_COUNT = 30
MIN_HIGH_IMBALANCE_CELL_MASS = 30.0
TEMPERATURE_GRID = tuple(COMMON_TEMPERATURE_GRID)
NEUTRAL_THRESHOLD_GRID = tuple(COMMON_NEUTRAL_THRESHOLD_GRID)
TEMPERATURE_SHRINKAGE = 0.20
NEUTRAL_THRESHOLD_SHRINKAGE = 0.08
MIN_CALIBRATION_DOMAIN_ROWS = 30
MIN_CALIBRATION_LABEL_ROWS = 5
RUNTIME_PARITY_LOGIT_ATOL = 1e-6
RUNTIME_PARITY_PROBABILITY_ATOL = 1e-7
PROGRESS_LOG_INTERVAL_OPTIMIZER_STEPS = 16
STAGE_CHECKPOINT_SCHEMA_VERSION = "kf-deberta-sentiment-v6-stage-checkpoint/v1"
CHECKPOINT_CONTEXT_MIGRATION_SCHEMA_VERSION = (
    "kf-deberta-sentiment-v6-completed-stage-context-migration/v1"
)
CHECKPOINT_CONTEXT_MIGRATION_SCOPE = (
    "POST_COMPLETED_STAGE_NON_TENSOR_GUARD_AND_PROVENANCE_CONTRACT_FIXES"
)
GOLD_DATASET_MARKER = "GOLD"
EXPECTED_FULL_COMMITMENTS: dict[str, dict[str, int | str]] = {
    "TRAIN": {
        "row_count": 32_907,
        "sha256": "952770420702aa1ee5a84e687bda9aac574da4a7db7af8ec84e9772aaba4a15c",
    },
    "CHECKPOINT": {
        "row_count": 911,
        "sha256": "a623918c406ead7a6e3b4f8a454a52fa46f8eb4daa3d4a0862fd5dcd8b3f95ab",
    },
    "CALIBRATION": {
        "row_count": 455,
        "sha256": "e88c34659d10f7bb7b52796a8e48f313d6324d3b6726798c04834cc8a3a10794",
    },
    "SELECTION": {
        "row_count": 461,
        "sha256": "09073e3677fbde1c995cc11f082ad2e69c8c8fb7de60f5e49d1f11dff1174d5c",
    },
    "NEWS_CONFIRMATORY_RESERVATION": {
        "row_count": 600,
        "sha256": "66c517a7a08a6fd94dc5123dc11d2933ee8dc023531f08709fbc2cc58c098741",
    },
    "DISCLOSURE_CONFIRMATORY_RESERVATION": {
        "row_count": 600,
        "sha256": "bc4b77b79690ee9567483462a8a9722e371d374717278df4e39112f9729d40cc",
    },
}
FORBIDDEN_EVALUATION_BASENAMES = frozenset(
    {
        "ratings_test.csv",
        "k_fnspid_sentiment_confirmatory_sealed_gold.jsonl",
        "k_fnspid_disclosure_sentiment_confirmatory_sealed_gold.jsonl",
    }
)
FORBIDDEN_EVALUATION_FRAGMENT = "confirmatory_sealed_gold"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/sentiment/v6-candidates/seed42-no-dapt"
DEFAULT_REPORT = PROJECT_ROOT / "reports/candidates/kf-deberta-sentiment-v6-seed42-no-dapt.json"
ADAPTIVE_SELECTION_ROLE = "ADAPTIVE_DEVELOPMENT_SELECTION"
PINNED_BASE_FILE_HASHES = {
    "pytorch_model.bin": v5.BASE_MODEL_WEIGHT_SHA256,
    "config.json": "4cba21a6fb53b5d75e2b7af83756eeb6d5e8a471164130999be395e1b8ff0848",
    "tokenizer.json": "915388090e2d63e3869c54b5334d6005e453a51de12088d908175dd765fd8372",
    "tokenizer_config.json": "d9273237da0f2143974a8eccdc50a733fcda064528299f7295e6434226cdbda1",
    "special_tokens_map.json": "311de3f4eed9d76a43bf0d71f10e62e086ca65ccce9f15d5da0d2098bf519ecc",
    "vocab.txt": "f0b8ae70418060f22ec301511a6337ad49a7fb0f60a8bf9091b373aba9c0c3e0",
}
DAPT_VERIFIER_CONTRACT = (
    "DAPT artifact manifest/training v2의 input·dependency·prepared·pilot·inventory·pack·"
    "merged_fp32·validation NLL을 현재 source와 재검증한 경우에만 base-source로 사용한다."
)
DAPT_BASE_SOURCE_FAIL_CLOSED = False


HierarchicalOutput = SourceHierarchicalOutput


@dataclass(frozen=True)
class PreparedPartitions:
    train_rows: list[dict[str, Any]]
    checkpoint_rows: list[dict[str, Any]]
    calibration_rows: list[dict[str, Any]]
    selection_rows: list[dict[str, Any]]
    gold_refinement_rows: list[dict[str, Any]]
    commitments: dict[str, dict[str, int | str]]
    input_paths: dict[str, Path]
    gold_provenance: dict[str, dict[str, Any]]
    audit: dict[str, Any]


@dataclass(frozen=True)
class BaseSource:
    kind: str
    model_path: str | Path
    provenance: dict[str, Any]


@dataclass(frozen=True)
class DomainMassObjective:
    row_count: int
    domain_row_counts: tuple[int, ...]
    domain_weight_mass: tuple[float, ...]
    boundary_cell_counts: tuple[tuple[int, int], ...]
    boundary_cell_mass: tuple[tuple[float, float], ...]
    direction_cell_counts: tuple[tuple[int, int], ...]
    direction_cell_mass: tuple[tuple[float, float], ...]
    composite_cell_counts: tuple[tuple[int, int, int], ...]
    composite_cell_mass: tuple[tuple[float, float, float], ...]
    minimum_active_cell_count: int
    minimum_active_cell_mass: float
    maximum_active_cell_mass_ratio: float


@dataclass(frozen=True)
class StageResult:
    stage: str
    best_epoch: int
    checkpoint_score: tuple[float, float]
    checkpoint_metrics: dict[str, Any]
    history: list[dict[str, Any]]
    state: dict[str, torch.Tensor]
    optimizer_steps: int
    planned_optimizer_steps: int
    best_optimizer_step: int
    wall_seconds: float
    objective_provenance: dict[str, Any]
    active_parameter_provenance: dict[str, Any]
    checkpoint_context_migration: dict[str, Any] | None


@dataclass(frozen=True)
class StageResumeState:
    completed_epoch: int
    best_epoch: int
    best_score: tuple[float, float]
    best_metrics: dict[str, Any]
    history: list[dict[str, Any]]
    optimizer_steps: int
    best_optimizer_step: int
    elapsed_wall_seconds: float
    best_state: dict[str, torch.Tensor]
    context_migration: dict[str, Any] | None


class TrainingInterruptionAudit:
    def __init__(self) -> None:
        self._wall_started = time.monotonic()
        self._cpu_started = time.process_time()
        self._last_progress = self._wall_started
        self._resume_events: list[dict[str, float | str]] = []
        self._installed = False
        self._previous_sigcont: Any = None

    def install(self) -> None:
        if self._installed or not hasattr(signal, "SIGCONT"):
            return
        self._previous_sigcont = signal.getsignal(signal.SIGCONT)
        signal.signal(signal.SIGCONT, self._on_continue)
        self._installed = True

    def close(self) -> None:
        if self._installed:
            signal.signal(signal.SIGCONT, self._previous_sigcont)
            self._installed = False

    def mark_progress(self) -> None:
        self._last_progress = time.monotonic()

    def _on_continue(self, _signum: int, _frame: Any) -> None:
        now = time.monotonic()
        self._resume_events.append(
            {
                "observed_at": datetime.now(UTC).isoformat(),
                "seconds_since_last_progress": now - self._last_progress,
            }
        )
        self._last_progress = now

    def report(self) -> dict[str, Any]:
        return {
            "wall_seconds": time.monotonic() - self._wall_started,
            "process_cpu_seconds": time.process_time() - self._cpu_started,
            "sigcont_resume_events": list(self._resume_events),
            "exact_pause_duration_available": False,
            "limitation": (
                "SIGSTOP is not catchable; SIGCONT observations and wall/CPU clocks are "
                "recorded, but exact suspension duration cannot be proven."
            ),
        }


def SourceHierarchicalClassifier(
    encoder: nn.Module,
    hidden_size: int,
    dropout: float = 0.12,
) -> nn.Module:
    return cast(
        nn.Module,
        build_source_hierarchical_classifier(
            encoder,
            hidden_size,
            dropout=dropout,
        ),
    )


def compose_hierarchical_log_probabilities(
    boundary_logits: torch.Tensor,
    direction_logits: torch.Tensor,
) -> torch.Tensor:
    return cast(
        torch.Tensor,
        common_compose_log_probabilities(boundary_logits, direction_logits),
    )


class DomainEncodedDataset(Dataset[dict[str, Any]]):
    def __init__(self, rows: list[dict[str, Any]], tokenizer: Any, max_length: int) -> None:
        self.features: list[dict[str, Any]] = []
        for row in rows:
            domain = strict_source_domain(
                str(row.get("source_type", "")),
                v5._target_security(row),
            )
            self.features.append(
                {
                    **encode_sentiment_input(
                        tokenizer,
                        str(row["text"]),
                        str(row["source_type"]),
                        max_length,
                        v5._target_security(row),
                    ),
                    "labels": LABEL_ORDER.index(str(row["label"])),
                    "sample_weight": v5._sample_weight(row),
                    "domain_ids": DOMAIN_TO_ID[domain],
                }
            )

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.features[index]

    def domain_mass_objective(self) -> DomainMassObjective:
        return domain_mass_objective_from_features(self.features)


class DomainCollator:
    def __init__(self, tokenizer: Any) -> None:
        self._collator = DataCollatorWithPadding(tokenizer=tokenizer)

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        sample_weights = torch.tensor(
            [float(feature["sample_weight"]) for feature in features],
            dtype=torch.float32,
        )
        model_features = [
            {name: value for name, value in feature.items() if name != "sample_weight"}
            for feature in features
        ]
        batch = cast(dict[str, torch.Tensor], self._collator(model_features))
        batch["sample_weight"] = sample_weights
        return batch


def strict_source_domain(source_type: str, target_security: str) -> SentimentDomain:
    return strict_sentiment_domain(source_type, target_security)


def _validate_domain_ids(domain_ids: torch.Tensor, batch_size: int) -> None:
    if (
        domain_ids.ndim != 1
        or domain_ids.shape[0] != batch_size
        or domain_ids.dtype not in {torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8}
        or bool((domain_ids < 0).any())
        or bool((domain_ids >= len(DOMAIN_ORDER)).any())
    ):
        raise ValueError("감성 source domain id 계약이 올바르지 않습니다.")


def domain_mass_objective_from_features(
    features: list[dict[str, Any]],
) -> DomainMassObjective:
    if not features:
        raise ValueError("도메인 균형 목적함수는 빈 학습 데이터를 허용하지 않습니다.")
    domain_counts = [0] * len(DOMAIN_ORDER)
    domain_mass = [0.0] * len(DOMAIN_ORDER)
    boundary_counts = [[0, 0] for _ in DOMAIN_ORDER]
    boundary_mass = [[0.0, 0.0] for _ in DOMAIN_ORDER]
    direction_counts = [[0, 0] for _ in DOMAIN_ORDER]
    direction_mass = [[0.0, 0.0] for _ in DOMAIN_ORDER]
    composite_counts = [[0, 0, 0] for _ in DOMAIN_ORDER]
    composite_mass = [[0.0, 0.0, 0.0] for _ in DOMAIN_ORDER]
    for feature in features:
        domain_id = feature.get("domain_ids")
        label = feature.get("labels")
        weight = feature.get("sample_weight")
        if (
            isinstance(domain_id, bool)
            or not isinstance(domain_id, int)
            or not 0 <= domain_id < len(DOMAIN_ORDER)
            or isinstance(label, bool)
            or not isinstance(label, int)
            or not 0 <= label < len(LABEL_ORDER)
            or isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(float(weight))
            or float(weight) <= 0.0
        ):
            raise ValueError("도메인 질량 계약의 label·domain·sample_weight가 잘못되었습니다.")
        numeric_weight = float(weight)
        domain_counts[domain_id] += 1
        domain_mass[domain_id] += numeric_weight
        boundary_id = 0 if label == 1 else 1
        boundary_counts[domain_id][boundary_id] += 1
        boundary_mass[domain_id][boundary_id] += numeric_weight
        composite_counts[domain_id][label] += 1
        composite_mass[domain_id][label] += numeric_weight
        if label != 1:
            direction_id = 0 if label == 0 else 1
            direction_counts[domain_id][direction_id] += 1
            direction_mass[domain_id][direction_id] += numeric_weight
    if not any(mass > 0.0 for mass in domain_mass):
        raise ValueError("활성 source domain이 없습니다.")

    active_counts: list[int] = []
    active_masses: list[float] = []
    maximum_ratio = 1.0
    for domain_id, count in enumerate(domain_counts):
        if count == 0:
            continue
        task_cells = (
            (boundary_counts[domain_id], boundary_mass[domain_id]),
            (direction_counts[domain_id], direction_mass[domain_id]),
            (composite_counts[domain_id], composite_mass[domain_id]),
        )
        for counts, masses in task_cells:
            if any(cell_count < 1 for cell_count in counts) or any(
                not math.isfinite(cell_mass) or cell_mass <= 0.0 for cell_mass in masses
            ):
                raise ValueError("활성 domain의 task-class cell이 비어 있습니다.")
            active_counts.extend(counts)
            active_masses.extend(masses)
            ratio = max(masses) / min(masses)
            maximum_ratio = max(maximum_ratio, ratio)
    minimum_count = min(active_counts)
    minimum_mass = min(active_masses)
    high_imbalance_without_support = maximum_ratio > MAX_ACTIVE_CELL_MASS_RATIO and (
        minimum_count < MIN_HIGH_IMBALANCE_CELL_COUNT
        or minimum_mass < MIN_HIGH_IMBALANCE_CELL_MASS
    )
    if maximum_ratio > MAX_SUPPORTED_CELL_MASS_RATIO or high_imbalance_without_support:
        raise ValueError("활성 domain의 task-class 질량 비율이 안전 한도를 초과했습니다.")
    return DomainMassObjective(
        row_count=len(features),
        domain_row_counts=tuple(domain_counts),
        domain_weight_mass=tuple(domain_mass),
        boundary_cell_counts=cast(Any, tuple(tuple(row) for row in boundary_counts)),
        boundary_cell_mass=cast(Any, tuple(tuple(row) for row in boundary_mass)),
        direction_cell_counts=cast(Any, tuple(tuple(row) for row in direction_counts)),
        direction_cell_mass=cast(Any, tuple(tuple(row) for row in direction_mass)),
        composite_cell_counts=cast(Any, tuple(tuple(row) for row in composite_counts)),
        composite_cell_mass=cast(Any, tuple(tuple(row) for row in composite_mass)),
        minimum_active_cell_count=minimum_count,
        minimum_active_cell_mass=minimum_mass,
        maximum_active_cell_mass_ratio=maximum_ratio,
    )


def domain_mass_objective_record(objective: DomainMassObjective) -> dict[str, Any]:
    return {
        "schema_version": LOSS_CONTRACT_VERSION,
        "row_count": objective.row_count,
        "domain_order": list(DOMAIN_ORDER),
        "boundary_cell_order": ["NEUTRAL", "DIRECTIONAL"],
        "direction_cell_order": ["NEGATIVE", "POSITIVE"],
        "composite_cell_order": list(LABEL_ORDER),
        "domain_row_counts": list(objective.domain_row_counts),
        "domain_weight_mass": list(objective.domain_weight_mass),
        "boundary_cell_counts": [list(row) for row in objective.boundary_cell_counts],
        "boundary_cell_mass": [list(row) for row in objective.boundary_cell_mass],
        "direction_cell_counts": [list(row) for row in objective.direction_cell_counts],
        "direction_cell_mass": [list(row) for row in objective.direction_cell_mass],
        "composite_cell_counts": [list(row) for row in objective.composite_cell_counts],
        "composite_cell_mass": [list(row) for row in objective.composite_cell_mass],
        "minimum_active_cell_count": objective.minimum_active_cell_count,
        "minimum_active_cell_mass": objective.minimum_active_cell_mass,
        "maximum_active_cell_mass_ratio": objective.maximum_active_cell_mass_ratio,
        "maximum_allowed_cell_mass_ratio_without_minimum_support": (
            MAX_ACTIVE_CELL_MASS_RATIO
        ),
        "maximum_supported_cell_mass_ratio": MAX_SUPPORTED_CELL_MASS_RATIO,
        "minimum_high_imbalance_cell_count": MIN_HIGH_IMBALANCE_CELL_COUNT,
        "minimum_high_imbalance_cell_mass": MIN_HIGH_IMBALANCE_CELL_MASS,
    }


def _fixed_domain_mass_mean(
    values: torch.Tensor,
    sample_weights: torch.Tensor,
    domain_ids: torch.Tensor,
    objective: DomainMassObjective,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    if (
        values.ndim != 1
        or not len(values)
        or sample_weights.shape != values.shape
        or domain_ids.shape != values.shape
        or (mask is not None and mask.shape != values.shape)
        or objective.row_count < len(values)
        or len(objective.domain_weight_mass) != len(DOMAIN_ORDER)
    ):
        raise ValueError("고정 도메인 질량 loss 입력 계약이 일치하지 않습니다.")
    _validate_domain_ids(domain_ids, len(values))
    weights = sample_weights.to(device=values.device, dtype=values.dtype)
    if not bool(torch.isfinite(weights).all()) or bool((weights <= 0.0).any()):
        raise ValueError("감성 sample_weight는 유한한 양수여야 합니다.")
    active = torch.ones_like(values, dtype=torch.bool) if mask is None else mask.bool()
    masses = (
        objective.domain_weight_mass
        if mask is None
        else tuple(sum(row) for row in objective.direction_cell_mass)
    )
    active_domain_count = sum(mass > 0.0 for mass in masses)
    if active_domain_count == 0 or not bool(active.any()):
        return values.sum() * 0.0
    mass_tensor = torch.tensor(masses, device=values.device, dtype=values.dtype)
    selected_domains = domain_ids[active].to(device=values.device, dtype=torch.long)
    selected_masses = mass_tensor[selected_domains]
    if bool((selected_masses <= 0.0).any()) or not bool(torch.isfinite(selected_masses).all()):
        raise ValueError("학습 행의 source domain이 고정 질량 계약에 없습니다.")
    # 전체 epoch 질량을 분모로 고정해 batch 내 domain 출현빈에 의한 목적함수 변형을 막는다.
    contribution = values[active] * weights[active] / selected_masses
    scale = objective.row_count / (len(values) * active_domain_count)
    return contribution.sum() * scale


def _fixed_task_cell_mass_mean(
    values: torch.Tensor,
    sample_weights: torch.Tensor,
    domain_ids: torch.Tensor,
    cell_ids: torch.Tensor,
    cell_mass: tuple[tuple[float, ...], ...],
    objective: DomainMassObjective,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    if (
        values.ndim != 1
        or not len(values)
        or sample_weights.shape != values.shape
        or domain_ids.shape != values.shape
        or cell_ids.shape != values.shape
        or (mask is not None and mask.shape != values.shape)
        or len(cell_mass) != len(DOMAIN_ORDER)
        or not cell_mass
        or any(len(row) != len(cell_mass[0]) for row in cell_mass)
    ):
        raise ValueError("고정 domain×task-class 질량 loss 계약이 일치하지 않습니다.")
    _validate_domain_ids(domain_ids, len(values))
    active = torch.ones_like(values, dtype=torch.bool) if mask is None else mask.bool()
    if not bool(active.any()):
        return values.sum() * 0.0
    weights = sample_weights.to(device=values.device, dtype=values.dtype)
    cells = cell_ids.to(device=values.device, dtype=torch.long)
    cell_count = len(cell_mass[0])
    if (
        bool((cells[active] < 0).any())
        or bool((cells[active] >= cell_count).any())
        or not bool(torch.isfinite(weights).all())
        or bool((weights <= 0.0).any())
    ):
        raise ValueError("고정 task-class 질량 입력 값이 올바르지 않습니다.")
    mass_tensor = torch.tensor(cell_mass, device=values.device, dtype=values.dtype)
    selected_mass = mass_tensor[
        domain_ids[active].to(device=values.device, dtype=torch.long),
        cells[active],
    ]
    if bool((selected_mass <= 0.0).any()) or not bool(torch.isfinite(selected_mass).all()):
        raise ValueError("학습 행의 domain×task-class cell 질량이 없습니다.")
    active_cell_count = sum(mass > 0.0 for row in cell_mass for mass in row)
    contribution = values[active] * weights[active] / selected_mass
    scale = objective.row_count / (len(values) * active_cell_count)
    return contribution.sum() * scale


def hierarchical_calibrated_loss(
    output: HierarchicalOutput,
    labels: torch.Tensor,
    sample_weights: torch.Tensor,
    domain_ids: torch.Tensor,
    domain_mass: DomainMassObjective,
) -> torch.Tensor:
    if labels.ndim != 1 or labels.shape[0] != output.logits.shape[0]:
        raise ValueError("감성 label 형상이 올바르지 않습니다.")
    _validate_domain_ids(domain_ids, labels.shape[0])
    directional_targets = (labels != 1).to(dtype=output.boundary_logits.dtype)
    smoothed_boundary_targets = directional_targets * (1.0 - BOUNDARY_LABEL_SMOOTHING)
    smoothed_boundary_targets += 0.5 * BOUNDARY_LABEL_SMOOTHING
    boundary_rows = functional.binary_cross_entropy_with_logits(
        output.boundary_logits,
        smoothed_boundary_targets,
        reduction="none",
    )
    boundary_loss = _fixed_task_cell_mass_mean(
        boundary_rows,
        sample_weights.to(output.logits.device),
        domain_ids,
        (labels != 1).long(),
        domain_mass.boundary_cell_mass,
        domain_mass,
    )

    non_neutral = labels != 1
    direction_rows = functional.cross_entropy(
        output.direction_logits,
        (labels == 2).long(),
        reduction="none",
        label_smoothing=DIRECTION_LABEL_SMOOTHING,
    )
    direction_loss = _fixed_task_cell_mass_mean(
        direction_rows,
        sample_weights.to(output.logits.device),
        domain_ids,
        (labels == 2).long(),
        domain_mass.direction_cell_mass,
        domain_mass,
        non_neutral,
    )
    composite_rows = functional.cross_entropy(
        output.logits,
        labels,
        reduction="none",
        label_smoothing=COMPOSITE_LABEL_SMOOTHING,
    )
    composite_loss = _fixed_task_cell_mass_mean(
        composite_rows,
        sample_weights.to(output.logits.device),
        domain_ids,
        labels,
        domain_mass.composite_cell_mass,
        domain_mass,
    )
    return (
        BOUNDARY_LOSS_WEIGHT * boundary_loss
        + DIRECTION_LOSS_WEIGHT * direction_loss
        + COMPOSITE_LOSS_WEIGHT * composite_loss
    )


def _symmetric_kl_rows(first_log: torch.Tensor, second_log: torch.Tensor) -> torch.Tensor:
    if first_log.shape != second_log.shape or first_log.ndim != 2:
        raise ValueError("R-Drop 확률 형상이 일치하지 않습니다.")
    first_probability = first_log.exp()
    second_probability = second_log.exp()
    forward = (first_probability * (first_log - second_log)).sum(dim=-1)
    reverse = (second_probability * (second_log - first_log)).sum(dim=-1)
    return 0.5 * (forward + reverse)


def hierarchical_rdrop_consistency(
    first: HierarchicalOutput,
    second: HierarchicalOutput,
    sample_weights: torch.Tensor,
    domain_ids: torch.Tensor,
    domain_mass: DomainMassObjective,
) -> torch.Tensor:
    first_boundary = torch.stack(
        (
            functional.logsigmoid(-first.boundary_logits),
            functional.logsigmoid(first.boundary_logits),
        ),
        dim=-1,
    )
    second_boundary = torch.stack(
        (
            functional.logsigmoid(-second.boundary_logits),
            functional.logsigmoid(second.boundary_logits),
        ),
        dim=-1,
    )
    boundary_rows = _symmetric_kl_rows(first_boundary, second_boundary)
    direction_rows = _symmetric_kl_rows(
        functional.log_softmax(first.direction_logits, dim=-1),
        functional.log_softmax(second.direction_logits, dim=-1),
    )
    weights = sample_weights.to(first.logits.device)
    boundary = _fixed_domain_mass_mean(boundary_rows, weights, domain_ids, domain_mass)
    direction = _fixed_domain_mass_mean(direction_rows, weights, domain_ids, domain_mass)
    return 0.5 * (boundary + direction)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="source-specific hierarchical KF-DeBERTa v6 감성 후보를 학습한다."
    )
    value.add_argument("--dataset-dir", type=Path, default=v5.DEFAULT_DATASET)
    value.add_argument("--silver-path", type=Path, default=v5.DEFAULT_SILVER)
    value.add_argument("--disclosure-silver-path", type=Path, default=v5.DEFAULT_DISCLOSURE_SILVER)
    value.add_argument("--train-gold-path", type=Path, default=v5.DEFAULT_TRAIN_GOLD)
    value.add_argument(
        "--news-auxiliary-gold-path", type=Path, default=v5.DEFAULT_NEWS_AUXILIARY_GOLD
    )
    value.add_argument(
        "--disclosure-auxiliary-gold-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_AUXILIARY_GOLD,
    )
    value.add_argument(
        "--news-auxiliary-report-path", type=Path, default=v5.DEFAULT_NEWS_AUXILIARY_REPORT
    )
    value.add_argument(
        "--disclosure-auxiliary-report-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_AUXILIARY_REPORT,
    )
    value.add_argument("--development-gold-path", type=Path, default=v5.DEFAULT_DEVELOPMENT_GOLD)
    value.add_argument(
        "--disclosure-development-gold-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD,
    )
    value.add_argument(
        "--news-sealed-review-path", type=Path, default=v5.DEFAULT_NEWS_SEALED_REVIEW
    )
    value.add_argument(
        "--disclosure-sealed-review-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_SEALED_REVIEW,
    )
    value.add_argument(
        "--sampling-design-report", type=Path, default=v5.DEFAULT_SAMPLING_DESIGN_REPORT
    )
    add_gold_provenance_arguments(value)
    value.add_argument("--base-source", default="pinned")
    value.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    value.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    value.add_argument("--checkpoint-root", type=Path)
    value.add_argument("--checkpoint-context-migration", type=Path)
    value.add_argument("--stage2-checkpoint-context-migration", type=Path)
    value.add_argument("--seed", type=int, default=42)
    value.add_argument("--max-length", type=int, default=256)
    value.add_argument("--stage1-epochs", type=int, default=2)
    value.add_argument("--stage2-epochs", type=int, default=4)
    value.add_argument("--batch-size", type=int, default=8)
    value.add_argument("--eval-batch-size", type=int, default=16)
    value.add_argument("--gradient-accumulation-steps", type=int, default=2)
    value.add_argument("--stage1-learning-rate", type=float, default=8e-5)
    value.add_argument("--stage2-learning-rate", type=float, default=4e-4)
    value.add_argument("--weight-decay", type=float, default=0.01)
    value.add_argument("--rdrop-alpha", type=float, default=R_DROP_ALPHA)
    value.add_argument("--gradient-checkpointing", action="store_true")
    value.add_argument("--device", choices=("auto", "cuda", "mps", "cpu"), default="auto")
    value.add_argument("--validate-only", action="store_true")
    return value


def validate_arguments(args: argparse.Namespace) -> None:
    if (
        not 16 <= args.max_length <= 512
        or args.stage1_epochs < 1
        or args.stage2_epochs < 1
        or args.batch_size < 1
        or args.eval_batch_size < 1
        or args.gradient_accumulation_steps < 1
        or args.stage1_learning_rate <= 0.0
        or args.stage2_learning_rate <= 0.0
        or not 0.0 <= args.weight_decay <= 1.0
        or not 0.0 <= args.rdrop_alpha <= 2.0
    ):
        raise SystemExit("학습 인자가 허용 범위를 벗어났습니다.")


def _input_paths(args: argparse.Namespace) -> dict[str, Path]:
    paths = {
        "public_train": args.dataset_dir / "ratings_train.csv",
        "public_validation": args.dataset_dir / "ratings_val.csv",
        "news_silver": args.silver_path,
        "disclosure_silver": args.disclosure_silver_path,
        "train_gold": args.train_gold_path,
        "news_auxiliary_training_gold": args.news_auxiliary_gold_path,
        "disclosure_auxiliary_training_gold": args.disclosure_auxiliary_gold_path,
        "news_auxiliary_training_report": args.news_auxiliary_report_path,
        "disclosure_auxiliary_training_report": args.disclosure_auxiliary_report_path,
        "news_development_gold": args.development_gold_path,
        "disclosure_development_gold": args.disclosure_development_gold_path,
        "news_sealed_review_reservation": args.news_sealed_review_path,
        "disclosure_sealed_review_reservation": args.disclosure_sealed_review_path,
        "sealed_sampling_design": args.sampling_design_report,
    }
    paths.update(
        {
            f"legacy_evaluation_{index}": path
            for index, path in enumerate(v5.LEGACY_EVALUATION_PATHS, start=1)
        }
    )
    paths.update(gold_provenance_paths(args))
    return paths


def assert_training_path_allowed(path: Path, role: str) -> None:
    lowered = path.as_posix().casefold()
    if (
        path.name.casefold() in FORBIDDEN_EVALUATION_BASENAMES
        or FORBIDDEN_EVALUATION_FRAGMENT in lowered
    ):
        raise SystemExit(
            f"봉인 후 단 한 번만 열 수 있는 평가 경로는 학습에 사용할 수 없습니다: {role}"
        )


def _validate_reservation_paths(args: argparse.Namespace) -> None:
    for actual, expected, label in (
        (args.news_sealed_review_path, v5.DEFAULT_NEWS_SEALED_REVIEW, "NEWS"),
        (
            args.disclosure_sealed_review_path,
            v5.DEFAULT_DISCLOSURE_SEALED_REVIEW,
            "DISCLOSURE",
        ),
    ):
        if actual.resolve() != expected.resolve():
            raise SystemExit(f"{label} 봉인 reservation 경로는 고정된 무라벨 입력만 허용합니다.")


def prepare_partitions(args: argparse.Namespace) -> PreparedPartitions:
    _validate_reservation_paths(args)
    input_paths = _input_paths(args)
    for name, path in input_paths.items():
        assert_training_path_allowed(path, name)
        v5._require_regular_input(path, name)
    gold_provenance = validate_all_gold_provenance(args)

    public, public_audit = decontaminate_public_partitions(
        {
            "TRAIN": v5._load_public_rows(args.dataset_dir / "ratings_train.csv"),
            "VALIDATION": v5._load_public_rows(args.dataset_dir / "ratings_val.csv"),
            "TEST": [],
        }
    )
    public_development = stratified_hash_three_way_split(
        public["VALIDATION"],
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=v5.MIN_DEVELOPMENT_LABEL_COUNT,
    )
    train_gold = v5._load_reviewed_rows(args.train_gold_path, "TRAIN_REVIEW", weight=1.5)
    news_auxiliary_gold = v5._load_auxiliary_training_rows(
        args.news_auxiliary_gold_path,
        args.news_auxiliary_report_path,
        "NEWS",
        weight=1.5,
    )
    disclosure_auxiliary_gold = v5._load_auxiliary_training_rows(
        args.disclosure_auxiliary_gold_path,
        args.disclosure_auxiliary_report_path,
        "DISCLOSURE",
        weight=1.5,
    )
    development_gold = v5._load_reviewed_rows(
        args.development_gold_path,
        "DEVELOPMENT_REVIEW",
        weight=1.0,
    )
    development_split = stratified_hash_three_way_split(
        development_gold,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=v5.MIN_DEVELOPMENT_LABEL_COUNT,
    )
    disclosure_development_gold = v5._load_reviewed_rows(
        args.disclosure_development_gold_path,
        "DISCLOSURE_DEVELOPMENT_REVIEW",
        weight=1.0,
    )
    disclosure_development_split = stratified_hash_three_way_split(
        disclosure_development_gold,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=v5.MIN_DEVELOPMENT_LABEL_COUNT,
    )
    news_reservation = v5._load_sealed_reservation_rows(
        args.news_sealed_review_path,
        "CONFIRMATORY_SEALED_TEST_REVIEW",
        "NEWS",
    )
    disclosure_reservation = v5._load_sealed_reservation_rows(
        args.disclosure_sealed_review_path,
        "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        "DISCLOSURE",
    )
    protected = [
        *public_development["CHECKPOINT"],
        *public_development["CALIBRATION"],
        *public_development["SELECTION"],
        *development_gold,
        *disclosure_development_gold,
        *news_reservation,
        *disclosure_reservation,
        *v5._load_legacy_protected_rows(),
    ]
    silver, silver_audit = v5._load_silver_rows(
        args.silver_path,
        protected,
        6_000,
        v5.DATA_SELECTION_SEED,
    )
    disclosure_silver, disclosure_silver_audit = v5._load_silver_rows(
        args.disclosure_silver_path,
        protected,
        900,
        v5.DATA_SELECTION_SEED + 11,
    )
    public_train = [
        {**row, "source_type": "NEWS", "sample_weight": 1.0, "dataset": "PUBLIC_TRAIN"}
        for row in public["TRAIN"]
    ]
    train_rows = v5._deduplicate_weighted(
        [
            *public_train,
            *[{**row, "dataset": "K_FNSPID_CODEX_GOLD"} for row in train_gold],
            *[
                {**row, "dataset": "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD"}
                for row in news_auxiliary_gold
            ],
            *[
                {**row, "dataset": "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD"}
                for row in disclosure_auxiliary_gold
            ],
            *[{**row, "dataset": "K_FNSPID_RULE_SILVER"} for row in silver],
            *[{**row, "dataset": "K_FNSPID_DISCLOSURE_RULE_SILVER"} for row in disclosure_silver],
        ]
    )
    train_rows, final_overlap_audit = purge_sentiment_group_overlap(train_rows, protected)
    target_swap_rows = v5.build_target_swap_hard_negatives(
        train_rows,
        per_source=1_500,
        seed=v5.DATA_SELECTION_SEED,
    )
    train_rows = [*train_rows, *target_swap_rows]
    checkpoint_rows = [
        *[
            {**row, "source_type": "NEWS", "dataset": "PUBLIC_CHECKPOINT"}
            for row in public_development["CHECKPOINT"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DEVELOPMENT_CHECKPOINT"}
            for row in development_split["CHECKPOINT"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DISCLOSURE_DEVELOPMENT_CHECKPOINT"}
            for row in disclosure_development_split["CHECKPOINT"]
        ],
    ]
    calibration_rows = [
        *[
            {**row, "source_type": "NEWS", "dataset": "PUBLIC_CALIBRATION"}
            for row in public_development["CALIBRATION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DEVELOPMENT_CALIBRATION"}
            for row in development_split["CALIBRATION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DISCLOSURE_DEVELOPMENT_CALIBRATION"}
            for row in disclosure_development_split["CALIBRATION"]
        ],
    ]
    selection_rows = [
        *[
            {**row, "source_type": "NEWS", "dataset": "PUBLIC_SELECTION"}
            for row in public_development["SELECTION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DEVELOPMENT_SELECTION"}
            for row in development_split["SELECTION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION"}
            for row in disclosure_development_split["SELECTION"]
        ],
    ]
    assert_sentiment_groups_disjoint(
        {
            "TRAIN": train_rows,
            "CHECKPOINT": checkpoint_rows,
            "CALIBRATION": calibration_rows,
            "SELECTION": selection_rows,
            "PUBLIC_TEST": public["TEST"],
            "NEWS_SEALED_RESERVATION": news_reservation,
            "DISCLOSURE_SEALED_RESERVATION": disclosure_reservation,
        }
    )
    commitments = v5._prepared_partition_commitments(
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_reservation=news_reservation,
        disclosure_reservation=disclosure_reservation,
    )
    if commitments != EXPECTED_FULL_COMMITMENTS:
        raise SystemExit("v6 학습 입력이 고정된 v5 32,907행 commitment와 다릅니다.")
    for row in [*train_rows, *checkpoint_rows, *calibration_rows, *selection_rows]:
        strict_source_domain(str(row.get("source_type", "")), v5._target_security(row))
    gold_refinement_rows = [
        row for row in train_rows if GOLD_DATASET_MARKER in str(row.get("dataset", ""))
    ]
    if not gold_refinement_rows or any(
        "SILVER" in str(row.get("dataset", "")) for row in gold_refinement_rows
    ):
        raise SystemExit("Gold-clean head refinement 입력 계약을 확인할 수 없습니다.")
    audit = {
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "public_partition_leakage_audit": public_audit,
        "silver_audit": silver_audit,
        "disclosure_silver_audit": disclosure_silver_audit,
        "final_group_overlap_purge": final_overlap_audit,
        "target_swap_count": len(target_swap_rows),
        "training_weight_audit": v5._training_weight_audit(train_rows),
    }
    return PreparedPartitions(
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        gold_refinement_rows=gold_refinement_rows,
        commitments=commitments,
        input_paths=input_paths,
        gold_provenance=gold_provenance,
        audit=audit,
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _regular_file_record(path: Path, root: Path | None = None) -> dict[str, int | str]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"일반 파일만 허용합니다: {path}")
    resolved = path.resolve(strict=True)
    display = str(resolved)
    if root is not None:
        display = resolved.relative_to(root.resolve()).as_posix()
    return {
        "path": display,
        "bytes": resolved.stat().st_size,
        "sha256": _sha256_file(resolved),
    }


def _training_code_paths() -> dict[str, Path]:
    return {
        "v6_trainer": Path(__file__).resolve(),
        "v5_data_contract": PROJECT_ROOT / "scripts/train_kf_deberta_sentiment_v2.py",
        "sentiment_input": PROJECT_ROOT / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_artifact_contract": PROJECT_ROOT
        / "src/hannah_montana_ai/services/sentiment_artifact_contract.py",
        "source_hierarchical_sentiment": PROJECT_ROOT
        / "src/hannah_montana_ai/services/source_hierarchical_sentiment.py",
        "sentiment_protocol": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py",
    }


def _pinned_base_file_snapshot(*, include_weight: bool) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for filename, expected_sha256 in sorted(PINNED_BASE_FILE_HASHES.items()):
        if filename == v5.BASE_MODEL_WEIGHT_FILENAME and not include_weight:
            continue
        cached = Path(
            hf_hub_download(
                repo_id=v5.BASE_MODEL,
                filename=filename,
                revision=v5.BASE_MODEL_REVISION,
            )
        )
        resolved = cached.resolve(strict=True)
        if not resolved.is_file() or _sha256_file(resolved) != expected_sha256:
            raise RuntimeError(f"고정 base/tokenizer hash가 다릅니다: {filename}")
        records[filename] = {
            **_regular_file_record(resolved),
            "repository": v5.BASE_MODEL,
            "revision": v5.BASE_MODEL_REVISION,
            "expected_sha256": expected_sha256,
        }
    return records


def _execution_snapshot_material(
    input_paths: dict[str, Path],
    base_source: BaseSource,
) -> dict[str, Any]:
    return {
        "input_artifacts": {
            name: v5._input_artifact_record(path) for name, path in sorted(input_paths.items())
        },
        "training_code": {
            name: _regular_file_record(path, PROJECT_ROOT)
            for name, path in sorted(_training_code_paths().items())
        },
        "dependency_artifacts": {
            "pyproject": v5._input_artifact_record(PROJECT_ROOT / "pyproject.toml"),
            "uv_lock": v5._input_artifact_record(PROJECT_ROOT / "uv.lock"),
        },
        "dependency_versions": {
            "numpy": importlib.metadata.version("numpy"),
            "peft": importlib.metadata.version("peft"),
            "safetensors": importlib.metadata.version("safetensors"),
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
        },
        "base_source_kind": base_source.kind,
        "base_source": base_source.provenance,
        "pinned_base_tokenizer_files": _pinned_base_file_snapshot(
            include_weight=base_source.kind == "PINNED_RAW"
        ),
    }


def capture_execution_snapshot(
    input_paths: dict[str, Path],
    base_source: BaseSource,
) -> dict[str, Any]:
    return {
        "schema_version": "kf-deberta-training-execution-snapshot/v1",
        "captured_at": datetime.now(UTC).isoformat(),
        "material": _execution_snapshot_material(input_paths, base_source),
    }


def assert_execution_snapshot_unchanged(
    snapshot: dict[str, Any],
    input_paths: dict[str, Path],
    base_source_argument: str,
) -> BaseSource:
    if snapshot.get(
        "schema_version"
    ) != "kf-deberta-training-execution-snapshot/v1" or not isinstance(
        snapshot.get("material"), dict
    ):
        raise RuntimeError("학습 실행 snapshot 계약이 잘못되었습니다.")
    current_base = resolve_base_source(base_source_argument, verify_pinned=True)
    current = _execution_snapshot_material(input_paths, current_base)
    if current != snapshot["material"]:
        raise RuntimeError("학습 시작 후 input·code·dependency·base/tokenizer가 변경되었습니다.")
    return current_base


def verify_dapt_base(directory: Path) -> BaseSource:
    try:
        import scripts.train_k_fnspid_dapt as dapt
    except ModuleNotFoundError as exception:  # scripts/ 직접 실행 경로
        if exception.name not in {"scripts", "scripts.train_k_fnspid_dapt"}:
            raise
        module_name = "train_k_fnspid_dapt"
        dapt_module = sys.modules.get(module_name)
        if dapt_module is None:
            module_path = Path(__file__).with_name("train_k_fnspid_dapt.py")
            dapt_spec = importlib.util.spec_from_file_location(module_name, module_path)
            if dapt_spec is None or dapt_spec.loader is None:
                raise RuntimeError("DAPT artifact 계약을 load할 수 없습니다.") from None
            dapt_module = importlib.util.module_from_spec(dapt_spec)
            sys.modules[module_name] = dapt_module
            dapt_spec.loader.exec_module(dapt_module)
        dapt = cast(Any, dapt_module)

    root = directory.resolve(strict=True)
    if directory.is_symlink() or not root.is_dir():
        raise RuntimeError("DAPT artifact root가 일반 directory가 아닙니다.")
    try:
        root.relative_to(PROJECT_ROOT.resolve(strict=True))
    except ValueError as exception:
        raise RuntimeError("DAPT artifact root가 project 밖에 있습니다.") from exception
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RuntimeError("DAPT artifact manifest가 일반 파일이 아닙니다.")
    manifest = dapt.read_json_object(manifest_path, "DAPT artifact manifest")
    expected_manifest_fields = {
        "schema_version",
        "status",
        "generated_at",
        "input_artifacts",
        "prepared_manifest",
        "prepared_artifacts",
        "pilot_report",
        "dependency_artifacts",
        "hardware",
        "base_model_provenance",
        "corpus_commitments",
        "inventory_oracle",
        "pack_commitments",
        "bundled_oracle_provenance",
        "artifact_files",
        "adapter_safe_serialization",
        "merged_fp32_included",
        "merged_fp32",
        "overwrite_allowed",
        "symlinks_allowed",
    }
    if (
        set(manifest) != expected_manifest_fields
        or manifest.get("schema_version") != "k-fnspid-kf-deberta-dapt-artifact-manifest/v2"
        or manifest.get("status") != "ATOMIC_COMPLETE"
        or manifest.get("adapter_safe_serialization") is not True
        or manifest.get("merged_fp32_included") is not True
        or manifest.get("overwrite_allowed") is not False
        or manifest.get("symlinks_allowed") is not False
    ):
        raise RuntimeError("DAPT artifact manifest 계약이 다릅니다.")
    try:
        generated_at = datetime.fromisoformat(str(manifest["generated_at"]))
    except ValueError as exception:
        raise RuntimeError("DAPT artifact 생성시각이 유효하지 않습니다.") from exception
    if generated_at.tzinfo is None or generated_at.utcoffset() != UTC.utcoffset(generated_at):
        raise RuntimeError("DAPT artifact 생성시각이 UTC가 아닙니다.")

    declared_files = manifest.get("artifact_files")
    if not isinstance(declared_files, dict) or not declared_files:
        raise RuntimeError("DAPT artifact file manifest가 없습니다.")
    actual_files = dapt.directory_artifact_manifest(root)
    actual_files.pop("manifest.json", None)
    if actual_files != declared_files:
        raise RuntimeError("DAPT artifact file hash가 manifest와 다릅니다.")
    required_files = {
        "adapter/adapter_config.json",
        "adapter/adapter_model.safetensors",
        "training_report.json",
        "merged_fp32/config.json",
    }
    if not required_files.issubset(actual_files) or not any(
        name.startswith("merged_fp32/") and name.endswith(".safetensors") for name in actual_files
    ):
        raise RuntimeError("DAPT merged FP32 필수 artifact가 없습니다.")

    merged = manifest.get("merged_fp32")
    merged_files = {
        name: record for name, record in actual_files.items() if name.startswith("merged_fp32/")
    }
    if (
        not isinstance(merged, dict)
        or set(merged) != {"included", "path", "artifact_files"}
        or merged.get("included") is not True
        or merged.get("path") != "merged_fp32"
        or merged.get("artifact_files") != merged_files
    ):
        raise RuntimeError("DAPT merged FP32 manifest 연결이 다릅니다.")

    current_inputs, _ = dapt.verify_source_inputs()
    current_dependencies = dapt.dependency_records()
    current_inventory_oracle = dapt.inventory_oracle_lock_record()
    current_pack_oracle = dapt.pack_oracle_lock_record()
    if (
        manifest.get("input_artifacts") != current_inputs
        or manifest.get("dependency_artifacts") != current_dependencies
        or manifest.get("inventory_oracle") != current_inventory_oracle
        or manifest.get("pack_commitments") != current_pack_oracle
        or manifest.get("corpus_commitments") != dapt.EXPECTED_HASHES
    ):
        raise RuntimeError("DAPT 입력·dependency·oracle commitment가 현재 source와 다릅니다.")

    prepared_manifest = manifest.get("prepared_manifest")
    if not isinstance(prepared_manifest, dict) or not isinstance(
        prepared_manifest.get("path"), str
    ):
        raise RuntimeError("DAPT prepared manifest record가 잘못되었습니다.")
    prepared_relative = PurePosixPath(str(prepared_manifest["path"]))
    if (
        prepared_relative.is_absolute()
        or ".." in prepared_relative.parts
        or "\\" in str(prepared_relative)
    ):
        raise RuntimeError("DAPT prepared manifest 경로가 project-relative가 아닙니다.")
    prepared_path = (PROJECT_ROOT / Path(*prepared_relative.parts)).resolve(strict=True)
    try:
        prepared_path.relative_to(PROJECT_ROOT.resolve(strict=True))
    except ValueError as exception:
        raise RuntimeError("DAPT prepared manifest가 project 밖에 있습니다.") from exception
    prepared_dir = prepared_path.parent
    current_prepared = dapt.prepared_snapshot(prepared_dir)
    if (
        dapt.artifact_record(prepared_path) != prepared_manifest
        or manifest.get("prepared_artifacts") != current_prepared
    ):
        raise RuntimeError("DAPT prepared corpus가 학습 artifact와 다릅니다.")

    pilot_record = manifest.get("pilot_report")
    if not isinstance(pilot_record, dict) or not isinstance(pilot_record.get("path"), str):
        raise RuntimeError("DAPT pilot record가 잘못되었습니다.")
    pilot_relative = PurePosixPath(str(pilot_record["path"]))
    if pilot_relative.is_absolute() or ".." in pilot_relative.parts or "\\" in str(pilot_relative):
        raise RuntimeError("DAPT pilot 경로가 project-relative가 아닙니다.")
    pilot_path = (PROJECT_ROOT / Path(*pilot_relative.parts)).resolve(strict=True)
    try:
        pilot_path.relative_to(PROJECT_ROOT.resolve(strict=True))
    except ValueError as exception:
        raise RuntimeError("DAPT pilot report가 project 밖에 있습니다.") from exception
    if dapt.artifact_record(pilot_path) != pilot_record:
        raise RuntimeError("DAPT pilot report가 학습 artifact와 다릅니다.")
    pilot = dapt.read_json_object(pilot_path, "DAPT precision pilot")
    if pilot.get("status") != "PRECISION_SELECTED" or pilot.get("selected_precision") not in {
        "FP32",
        "BF16",
    }:
        raise RuntimeError("DAPT precision pilot 선택 계약이 다릅니다.")

    base_provenance = manifest.get("base_model_provenance")
    if (
        not isinstance(base_provenance, dict)
        or base_provenance.get("repository") != dapt.BASE_MODEL
        or base_provenance.get("revision") != dapt.BASE_REVISION
        or base_provenance.get("file_hashes") != dapt.BASE_FILE_HASHES
        or base_provenance.get("weights_only") is not True
        or base_provenance.get("trust_remote_code") is not False
    ):
        raise RuntimeError("DAPT 원본 base provenance가 고정 계약과 다릅니다.")

    report = dapt.read_json_object(root / "training_report.json", "DAPT training report")
    validation = report.get("validation")
    optimizer = report.get("optimizer")
    training = report.get("training")
    if (
        report.get("schema_version") != "k-fnspid-kf-deberta-dapt-training/v2"
        or report.get("status") != "TRAINED_PENDING_ATOMIC_MANIFEST"
        or report.get("public_test_opened") is not False
        or report.get("confirmatory_sentiment_labels_opened") is not False
        or report.get("precision") != pilot.get("selected_precision")
        or report.get("merged_fp32") != "merged_fp32"
        or report.get("prepared_manifest") != prepared_manifest
        or report.get("prepared_artifacts") != current_prepared
        or report.get("pilot_report") != pilot_record
        or report.get("inventory_oracle") != current_inventory_oracle
        or report.get("pack_oracle") != current_pack_oracle
        or not isinstance(validation, dict)
        or validation.get("nll_improved") is not True
        or not isinstance(optimizer, dict)
        or optimizer.get("total_updates") != dapt.TOTAL_UPDATES
        or optimizer.get("warmup_updates") != dapt.WARMUP_UPDATES
        or not isinstance(training, dict)
        or training.get("update_count") != dapt.TOTAL_UPDATES
    ):
        raise RuntimeError("DAPT training report 계약이 다릅니다.")
    frozen = validation.get("frozen_base")
    final = validation.get("end_of_epoch")
    if (
        not isinstance(frozen, dict)
        or not isinstance(final, dict)
        or not isinstance(frozen.get("mean_nll"), (int, float))
        or not isinstance(final.get("mean_nll"), (int, float))
        or float(final["mean_nll"]) >= float(frozen["mean_nll"])
    ):
        raise RuntimeError("DAPT validation NLL 개선을 재검증할 수 없습니다.")

    merged_path = validate_source_hierarchical_base_directory(root / "merged_fp32")
    manifest_record = dapt.artifact_record(manifest_path)
    return BaseSource(
        kind="DAPT_MERGED_FP32",
        model_path=merged_path,
        provenance={
            "schema_version": "kf-deberta-dapt-base-source/v2",
            "artifact_manifest": manifest_record,
            "merged_fp32_artifact_files": merged_files,
            "training_report": actual_files["training_report.json"],
            "prepared_manifest": prepared_manifest,
            "pilot_report": pilot_record,
            "inventory_oracle": current_inventory_oracle,
            "pack_oracle": current_pack_oracle,
            "base_model": dapt.BASE_MODEL,
            "base_revision": dapt.BASE_REVISION,
            "precision": report["precision"],
            "validation_nll": {
                "frozen_base": frozen["mean_nll"],
                "end_of_epoch": final["mean_nll"],
            },
        },
    )


def resolve_base_source(value: str, *, verify_pinned: bool) -> BaseSource:
    if value == "pinned":
        weight_path = v5._verify_base_model_weights() if verify_pinned else None
        return BaseSource(
            kind="PINNED_RAW",
            model_path=v5.BASE_MODEL,
            provenance={
                "repository": v5.BASE_MODEL,
                "revision": v5.BASE_MODEL_REVISION,
                "source_weight_filename": v5.BASE_MODEL_WEIGHT_FILENAME,
                "source_weight_sha256": v5.BASE_MODEL_WEIGHT_SHA256,
                "verified_cache_path": str(weight_path) if weight_path else None,
                "weights_only": True,
                "trust_remote_code": False,
            },
        )
    return verify_dapt_base(Path(value))


def build_model(base_source: BaseSource, *, gradient_checkpointing: bool) -> Any:
    if base_source.kind == "PINNED_RAW":
        base = AutoModel.from_pretrained(
            v5.BASE_MODEL,
            revision=v5.BASE_MODEL_REVISION,
            trust_remote_code=False,
            weights_only=True,
        )
    else:
        # manifest 전체 hash를 검증한 로컬 safetensors만 load한다.
        base = AutoModel.from_pretrained(  # nosec B615
            base_source.model_path,
            local_files_only=True,
            use_safetensors=True,
            trust_remote_code=False,
            weights_only=True,
        )
    encoder = get_peft_model(
        base,
        LoraConfig(
            task_type=TaskType.FEATURE_EXTRACTION,
            r=LORA_RANK,
            lora_alpha=LORA_ALPHA,
            lora_dropout=LORA_DROPOUT,
            target_modules=list(LORA_TARGET_MODULES),
            layers_to_transform=list(LORA_LAYERS),
            layers_pattern="layer",
        ),
    )
    if gradient_checkpointing:
        encoder.gradient_checkpointing_enable()
        if hasattr(encoder.config, "use_cache"):
            encoder.config.use_cache = False
    encoder_config = cast(Any, encoder.config)
    hidden_size = int(encoder_config.hidden_size)
    return SourceHierarchicalClassifier(encoder, hidden_size)


def _device(name: str) -> torch.device:
    if name == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit("CUDA를 사용할 수 없습니다.")
        return torch.device("cuda")
    if name == "mps":
        if not torch.backends.mps.is_available():
            raise SystemExit("MPS를 사용할 수 없습니다.")
        return torch.device("mps")
    if name == "cpu":
        return torch.device("cpu")
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _to_device(batch: dict[str, torch.Tensor], device: torch.device) -> dict[str, torch.Tensor]:
    return {name: value.to(device) for name, value in batch.items()}


def _model_forward(model: nn.Module, batch: dict[str, torch.Tensor]) -> HierarchicalOutput:
    inputs = {
        name: batch[name]
        for name in ("input_ids", "attention_mask", "token_type_ids", "domain_ids")
        if name in batch
    }
    return cast(HierarchicalOutput, model(**inputs))


def _capture_state(model: nn.Module, names: set[str] | None = None) -> dict[str, torch.Tensor]:
    return {
        name: parameter.detach().cpu().clone()
        for name, parameter in model.named_parameters()
        if (names is None and parameter.requires_grad) or (names is not None and name in names)
    }


def _restore_state(model: nn.Module, state: dict[str, torch.Tensor]) -> None:
    parameters = dict(model.named_parameters())
    if set(state) - set(parameters):
        raise RuntimeError("학습 checkpoint parameter 계약이 다릅니다.")
    with torch.no_grad():
        for name, value in state.items():
            parameters[name].copy_(value.to(parameters[name].device))


def _optimizer(model: nn.Module, learning_rate: float, weight_decay: float) -> AdamW:
    decay: list[nn.Parameter] = []
    no_decay: list[nn.Parameter] = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        if name.endswith("bias") or "normalization" in name or "layer_norm" in name.casefold():
            no_decay.append(parameter)
        else:
            decay.append(parameter)
    if not decay and not no_decay:
        raise RuntimeError("학습 가능 parameter가 없습니다.")
    return AdamW(
        [
            {"params": decay, "weight_decay": weight_decay},
            {"params": no_decay, "weight_decay": 0.0},
        ],
        lr=learning_rate,
        betas=(0.9, 0.999),
        eps=1e-8,
    )


def _tensor_state_sha256(state: dict[str, torch.Tensor]) -> str:
    digest = sha256()
    for name, tensor in sorted(state.items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(json.dumps(list(value.shape), separators=(",", ":")).encode("ascii"))
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def _configure_stage_residuals(
    model: nn.Module,
    objective: DomainMassObjective,
) -> tuple[dict[str, Any], dict[str, torch.Tensor]]:
    residuals = getattr(model, "domain_residuals", None)
    shared = getattr(model, "shared_head", None)
    if residuals is None or shared is None or set(residuals) != set(RESIDUAL_DOMAINS):
        raise RuntimeError("v2 shared-residual classifier 구조가 없습니다.")
    active_domains = {
        domain
        for domain_id, domain in enumerate(DOMAIN_ORDER)
        if objective.domain_row_counts[domain_id] > 0
    }
    inactive_state: dict[str, torch.Tensor] = {}
    membership: dict[str, bool] = {}
    for domain in RESIDUAL_DOMAINS:
        active = domain in active_domains
        membership[domain] = active
        module = residuals[domain]
        for name, parameter in module.named_parameters():
            parameter.requires_grad = active
            if not active:
                inactive_state[f"domain_residuals.{domain}.{name}"] = (
                    parameter.detach().cpu().clone()
                )
    parameter_names = sorted(
        name for name, parameter in model.named_parameters() if parameter.requires_grad
    )
    parameter_name_digest = sha256("\n".join(parameter_names).encode("utf-8")).hexdigest()
    provenance = {
        "schema_version": "shared-residual-active-parameter-provenance/v2",
        "head_architecture": HEAD_ARCHITECTURE_VERSION,
        "anchor_domain": ANCHOR_DOMAIN,
        "active_domains": [domain for domain in DOMAIN_ORDER if domain in active_domains],
        "shared_head_in_optimizer": any(
            parameter.requires_grad for parameter in shared.parameters()
        ),
        "residual_optimizer_membership": membership,
        "encoder_in_optimizer": any(
            parameter.requires_grad for parameter in cast(Any, model).encoder.parameters()
        ),
        "trainable_parameter_name_count": len(parameter_names),
        "trainable_parameter_names_sha256": parameter_name_digest,
        "inactive_residual_parameter_count": len(inactive_state),
        "inactive_residual_exact_zero_before": all(
            bool(torch.count_nonzero(tensor) == 0) for tensor in inactive_state.values()
        ),
        "inactive_residual_state_sha256_before": _tensor_state_sha256(inactive_state),
    }
    return provenance, inactive_state


def _verify_inactive_residuals_preserved(
    model: nn.Module,
    before: dict[str, torch.Tensor],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    parameters = dict(model.named_parameters())
    after = {name: parameters[name].detach().cpu().clone() for name in before}
    if any(not torch.equal(before[name], after[name]) for name in before):
        raise RuntimeError("비활성 source residual이 optimizer에 의해 변경되었습니다.")
    return {
        **provenance,
        "inactive_residual_state_sha256_after": _tensor_state_sha256(after),
        "inactive_residual_bitwise_preserved": True,
        "inactive_residual_exact_zero_after": all(
            bool(torch.count_nonzero(tensor) == 0) for tensor in after.values()
        ),
    }


def _stage_checkpoint_context_sha256(material: dict[str, Any]) -> str:
    return sha256(
        json.dumps(
            material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _optimizer_checkpoint_state(
    optimizer: torch.optim.Optimizer,
) -> tuple[dict[str, Any], dict[str, torch.Tensor]]:
    state = optimizer.state_dict()
    tensors: dict[str, torch.Tensor] = {}
    scalar_state: dict[str, dict[str, Any]] = {}
    for parameter_id, values in state["state"].items():
        parameter_scalars: dict[str, Any] = {}
        for name, value in values.items():
            if isinstance(value, torch.Tensor):
                tensors[f"optimizer.{parameter_id}.{name}"] = value.detach().cpu().contiguous()
            elif value is None or isinstance(value, (bool, int, float, str)):
                parameter_scalars[name] = value
            else:
                raise RuntimeError("지원하지 않는 optimizer checkpoint 값입니다.")
        scalar_state[str(parameter_id)] = parameter_scalars
    return {
        "state_scalars": scalar_state,
        "param_groups": state["param_groups"],
    }, tensors


def _restore_optimizer_checkpoint_state(
    optimizer: torch.optim.Optimizer,
    record: dict[str, Any],
    tensors: dict[str, torch.Tensor],
) -> None:
    scalar_state = record.get("state_scalars")
    param_groups = record.get("param_groups")
    if not isinstance(scalar_state, dict) or not isinstance(param_groups, list):
        raise RuntimeError("optimizer checkpoint 계약이 잘못되었습니다.")
    state: dict[int, dict[str, Any]] = {}
    for parameter_id_text, values in scalar_state.items():
        if not str(parameter_id_text).isdigit() or not isinstance(values, dict):
            raise RuntimeError("optimizer checkpoint parameter 계약이 잘못되었습니다.")
        state[int(parameter_id_text)] = dict(values)
    prefix = "optimizer."
    for name, tensor in tensors.items():
        if not name.startswith(prefix):
            continue
        remainder = name[len(prefix) :]
        parameter_id_text, separator, state_name = remainder.partition(".")
        if not separator or not parameter_id_text.isdigit() or not state_name:
            raise RuntimeError("optimizer checkpoint tensor 이름이 잘못되었습니다.")
        state.setdefault(int(parameter_id_text), {})[state_name] = tensor
    restored_param_groups: list[dict[str, Any]] = []
    for group in param_groups:
        if not isinstance(group, dict):
            raise RuntimeError("optimizer checkpoint param group이 잘못되었습니다.")
        restored = dict(group)
        betas = restored.get("betas")
        if isinstance(betas, list):
            restored["betas"] = tuple(betas)
        restored_param_groups.append(restored)
    optimizer.load_state_dict({"state": state, "param_groups": restored_param_groups})


def _save_stage_checkpoint(
    *,
    checkpoint_directory: Path,
    context_sha256: str,
    stage: str,
    completed_epoch: int,
    epochs: int,
    model: nn.Module,
    state_names: set[str],
    best_state: dict[str, torch.Tensor],
    best_epoch: int,
    best_score: tuple[float, float],
    best_metrics: dict[str, Any],
    history: list[dict[str, Any]],
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    generator: torch.Generator,
    optimizer_steps: int,
    best_optimizer_step: int,
    elapsed_wall_seconds: float,
    device: torch.device,
) -> Path:
    if checkpoint_directory.is_symlink():
        raise RuntimeError("stage checkpoint root는 symlink일 수 없습니다.")
    checkpoint_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = checkpoint_directory / f"epoch-{completed_epoch:03d}"
    if target.exists() or target.is_symlink():
        raise RuntimeError(f"stage checkpoint가 이미 존재합니다: {target}")
    temporary = checkpoint_directory / f".{target.name}.tmp-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    try:
        tensors: dict[str, torch.Tensor] = {
            **{
                f"model.current.{name}": tensor
                for name, tensor in _capture_state(model, state_names).items()
            },
            **{f"model.best.{name}": tensor for name, tensor in best_state.items()},
            "rng.torch_cpu": torch.get_rng_state().cpu().contiguous(),
            "rng.loader_generator": generator.get_state().cpu().contiguous(),
        }
        if device.type == "mps":
            tensors["rng.mps"] = torch.mps.get_rng_state().cpu().contiguous()
        optimizer_record, optimizer_tensors = _optimizer_checkpoint_state(optimizer)
        tensors.update(optimizer_tensors)
        tensor_path = temporary / "training_state.safetensors"
        save_file(tensors, tensor_path)
        state_record = {
            "schema_version": STAGE_CHECKPOINT_SCHEMA_VERSION,
            "context_sha256": context_sha256,
            "stage": stage,
            "completed_epoch": completed_epoch,
            "epochs": epochs,
            "best_epoch": best_epoch,
            "best_score": list(best_score),
            "best_metrics": best_metrics,
            "history": history,
            "optimizer_steps": optimizer_steps,
            "best_optimizer_step": best_optimizer_step,
            "elapsed_wall_seconds": elapsed_wall_seconds,
            "optimizer": optimizer_record,
            "scheduler": scheduler.state_dict(),
            "device_type": device.type,
            "state_names": sorted(state_names),
        }
        state_path = temporary / "state.json"
        state_path.write_text(
            json.dumps(state_record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest = {
            "schema_version": STAGE_CHECKPOINT_SCHEMA_VERSION,
            "context_sha256": context_sha256,
            "stage": stage,
            "completed_epoch": completed_epoch,
            "files": {
                "state.json": _sha256_file(state_path),
                "training_state.safetensors": _sha256_file(tensor_path),
            },
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.rename(temporary, target)
        for previous in checkpoint_directory.iterdir():
            if (
                previous != target
                and previous.is_dir()
                and not previous.is_symlink()
                and previous.name.startswith("epoch-")
            ):
                shutil.rmtree(previous)
        return target
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def _validate_completed_stage_context_migration(
    *,
    migration_path: Path | None,
    checkpoint: Path,
    manifest_path: Path,
    tensor_path: Path,
    checkpoint_context_sha256: str,
    expected_context_sha256: str,
    stage: str,
    completed_epoch: int,
    epochs: int,
) -> dict[str, Any]:
    if migration_path is None:
        raise RuntimeError("stage checkpoint context가 변경되었지만 migration이 없습니다.")
    expected_path = checkpoint / "context-migration.json"
    if (
        migration_path.is_symlink()
        or not migration_path.is_file()
        or migration_path.resolve() != expected_path.resolve()
        or migration_path.parent.resolve() != checkpoint.resolve()
    ):
        raise RuntimeError("checkpoint context migration 경로 계약이 잘못되었습니다.")
    record = json.loads(migration_path.read_text(encoding="utf-8"))
    required_keys = {
        "schema_version",
        "scope",
        "stage",
        "completed_epoch",
        "epochs",
        "old_context_sha256",
        "new_context_sha256",
        "checkpoint_manifest_sha256",
        "training_state_sha256",
        "tensor_payload_unchanged",
        "reason",
        "rule_change",
        "verified_tests",
    }
    if (
        not isinstance(record, dict)
        or set(record) != required_keys
        or record.get("schema_version") != CHECKPOINT_CONTEXT_MIGRATION_SCHEMA_VERSION
        or record.get("scope") != CHECKPOINT_CONTEXT_MIGRATION_SCOPE
        or record.get("stage") != stage
        or record.get("completed_epoch") != completed_epoch
        or record.get("epochs") != epochs
        or completed_epoch != epochs
        or record.get("old_context_sha256") != checkpoint_context_sha256
        or record.get("new_context_sha256") != expected_context_sha256
        or record.get("checkpoint_manifest_sha256") != _sha256_file(manifest_path)
        or record.get("training_state_sha256") != _sha256_file(tensor_path)
        or record.get("tensor_payload_unchanged") is not True
        or not isinstance(record.get("reason"), str)
        or not str(record["reason"]).strip()
        or not isinstance(record.get("rule_change"), str)
        or not str(record["rule_change"]).strip()
        or not isinstance(record.get("verified_tests"), list)
        or not record["verified_tests"]
        or not all(isinstance(item, str) and item.strip() for item in record["verified_tests"])
    ):
        raise RuntimeError("completed-stage checkpoint context migration 계약이 다릅니다.")
    return {
        **record,
        "path": str(migration_path),
        "sha256": _sha256_file(migration_path),
    }


def _load_latest_stage_checkpoint(
    *,
    checkpoint_directory: Path,
    context_sha256: str,
    stage: str,
    epochs: int,
    model: nn.Module,
    state_names: set[str],
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    generator: torch.Generator,
    device: torch.device,
    context_migration_path: Path | None = None,
) -> StageResumeState | None:
    if not checkpoint_directory.exists():
        if context_migration_path is not None:
            raise RuntimeError("checkpoint 없이 context migration을 지정할 수 없습니다.")
        return None
    if checkpoint_directory.is_symlink() or not checkpoint_directory.is_dir():
        raise RuntimeError("stage checkpoint root 계약이 잘못되었습니다.")
    entries = list(checkpoint_directory.iterdir())
    if any(path.is_symlink() for path in entries):
        raise RuntimeError("stage checkpoint root에 symlink가 포함되어 있습니다.")
    candidates = sorted(
        path for path in entries if path.is_dir() and path.name.startswith("epoch-")
    )
    if not candidates:
        if context_migration_path is not None:
            raise RuntimeError("완료 checkpoint 없이 context migration을 지정할 수 없습니다.")
        return None
    checkpoint = candidates[-1]
    manifest_path = checkpoint / "manifest.json"
    state_path = checkpoint / "state.json"
    tensor_path = checkpoint / "training_state.safetensors"
    if any(
        path.is_symlink() or not path.is_file() for path in (manifest_path, state_path, tensor_path)
    ):
        raise RuntimeError("stage checkpoint 필수 파일 계약이 잘못되었습니다.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    state_record = json.loads(state_path.read_text(encoding="utf-8"))
    expected_files = manifest.get("files")
    checkpoint_context = manifest.get("context_sha256")
    if (
        manifest.get("schema_version") != STAGE_CHECKPOINT_SCHEMA_VERSION
        or state_record.get("schema_version") != STAGE_CHECKPOINT_SCHEMA_VERSION
        or not isinstance(checkpoint_context, str)
        or state_record.get("context_sha256") != checkpoint_context
        or manifest.get("stage") != stage
        or state_record.get("stage") != stage
        or state_record.get("epochs") != epochs
        or state_record.get("state_names") != sorted(state_names)
        or not isinstance(expected_files, dict)
        or expected_files.get("state.json") != _sha256_file(state_path)
        or expected_files.get("training_state.safetensors") != _sha256_file(tensor_path)
    ):
        raise RuntimeError("stage checkpoint manifest/context 계약이 다릅니다.")
    completed_epoch = int(state_record["completed_epoch"])
    context_migration: dict[str, Any] | None = None
    if checkpoint_context != context_sha256:
        context_migration = _validate_completed_stage_context_migration(
            migration_path=context_migration_path,
            checkpoint=checkpoint,
            manifest_path=manifest_path,
            tensor_path=tensor_path,
            checkpoint_context_sha256=checkpoint_context,
            expected_context_sha256=context_sha256,
            stage=stage,
            completed_epoch=completed_epoch,
            epochs=epochs,
        )
    elif context_migration_path is not None:
        raise RuntimeError("동일 context checkpoint에는 migration을 지정할 수 없습니다.")
    tensors = load_file(tensor_path, device="cpu")
    current_prefix = "model.current."
    best_prefix = "model.best."
    current_state = {
        name[len(current_prefix) :]: tensor
        for name, tensor in tensors.items()
        if name.startswith(current_prefix)
    }
    best_state = {
        name[len(best_prefix) :]: tensor
        for name, tensor in tensors.items()
        if name.startswith(best_prefix)
    }
    if set(current_state) != state_names or set(best_state) != state_names:
        raise RuntimeError("stage checkpoint model tensor 계약이 다릅니다.")
    _restore_state(model, current_state)
    optimizer_record = state_record.get("optimizer")
    scheduler_record = state_record.get("scheduler")
    if not isinstance(optimizer_record, dict) or not isinstance(scheduler_record, dict):
        raise RuntimeError("stage checkpoint optimizer/scheduler 계약이 잘못되었습니다.")
    _restore_optimizer_checkpoint_state(optimizer, optimizer_record, tensors)
    scheduler.load_state_dict(scheduler_record)
    torch.set_rng_state(tensors["rng.torch_cpu"])
    generator.set_state(tensors["rng.loader_generator"])
    if device.type == "mps":
        if "rng.mps" not in tensors:
            raise RuntimeError("MPS stage checkpoint RNG가 없습니다.")
        torch.mps.set_rng_state(tensors["rng.mps"])
    if completed_epoch < 1 or completed_epoch > epochs:
        raise RuntimeError("stage checkpoint epoch가 잘못되었습니다.")
    best_score_values = state_record.get("best_score")
    if not isinstance(best_score_values, list) or len(best_score_values) != 2:
        raise RuntimeError("stage checkpoint best score가 잘못되었습니다.")
    return StageResumeState(
        completed_epoch=completed_epoch,
        best_epoch=int(state_record["best_epoch"]),
        best_score=(float(best_score_values[0]), float(best_score_values[1])),
        best_metrics=cast(dict[str, Any], state_record["best_metrics"]),
        history=cast(list[dict[str, Any]], state_record["history"]),
        optimizer_steps=int(state_record["optimizer_steps"]),
        best_optimizer_step=int(state_record["best_optimizer_step"]),
        elapsed_wall_seconds=float(state_record["elapsed_wall_seconds"]),
        best_state=best_state,
        context_migration=context_migration,
    )


@torch.no_grad()
def predict(
    model: nn.Module,
    dataset: Dataset[dict[str, Any]],
    collator: DomainCollator,
    *,
    batch_size: int,
    device: torch.device,
) -> tuple[NDArray[np.float64], NDArray[np.int64], NDArray[np.int64]]:
    model.eval()
    logits: list[NDArray[np.float64]] = []
    labels: list[NDArray[np.int64]] = []
    domains: list[NDArray[np.int64]] = []
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collator)
    for raw_batch in loader:
        batch = _to_device(raw_batch, device)
        output = _model_forward(model, batch)
        logits.append(output.logits.detach().cpu().numpy().astype(np.float64))
        labels.append(batch["labels"].detach().cpu().numpy().astype(np.int64))
        domains.append(batch["domain_ids"].detach().cpu().numpy().astype(np.int64))
    return np.concatenate(logits), np.concatenate(labels), np.concatenate(domains)


def _metric_block(expected: NDArray[np.int64], predicted: NDArray[np.int64]) -> dict[str, Any]:
    return {
        "sample_count": int(len(expected)),
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(
                expected,
                predicted,
                labels=range(len(LABEL_ORDER)),
                average="macro",
                zero_division=0,
            )
        ),
        "label_distribution": {
            label: int((expected == index).sum()) for index, label in enumerate(LABEL_ORDER)
        },
    }


def metrics_by_domain(
    expected: NDArray[np.int64],
    predicted: NDArray[np.int64],
    domains: NDArray[np.int64],
) -> dict[str, Any]:
    result: dict[str, Any] = {"OVERALL": _metric_block(expected, predicted)}
    for domain_id, domain in enumerate(DOMAIN_ORDER):
        selected = domains == domain_id
        if not bool(selected.any()):
            raise RuntimeError(f"checkpoint에 {domain} 표본이 없습니다.")
        result[domain] = _metric_block(expected[selected], predicted[selected])
    return result


def weakest_source_score(metrics: dict[str, Any]) -> tuple[float, float]:
    source_f1 = [float(metrics[domain]["macro_f1"]) for domain in DOMAIN_ORDER]
    return min(source_f1), float(metrics["OVERALL"]["macro_f1"])


def train_stage(
    model: nn.Module,
    train_dataset: DomainEncodedDataset,
    checkpoint_dataset: DomainEncodedDataset,
    collator: DomainCollator,
    *,
    stage: str,
    epochs: int,
    learning_rate: float,
    weight_decay: float,
    batch_size: int,
    eval_batch_size: int,
    gradient_accumulation_steps: int,
    rdrop_alpha: float,
    seed: int,
    device: torch.device,
    state_names: set[str],
    interruption_audit: TrainingInterruptionAudit | None = None,
    checkpoint_directory: Path | None = None,
    checkpoint_context_sha256: str | None = None,
    checkpoint_context_migration_path: Path | None = None,
) -> StageResult:
    stage_started = time.monotonic()
    mass_method = getattr(train_dataset, "domain_mass_objective", None)
    if not callable(mass_method):
        raise TypeError("학습 Dataset은 고정 도메인 질량 계약을 제공해야 합니다.")
    domain_mass = mass_method()
    if not isinstance(domain_mass, DomainMassObjective):
        raise TypeError("고정 도메인 질량 계약 형식이 잘못되었습니다.")
    active_parameter_provenance, inactive_residual_state = _configure_stage_residuals(
        model,
        domain_mass,
    )
    generator = torch.Generator()
    generator.manual_seed(seed)
    loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
        collate_fn=collator,
        num_workers=0,
        pin_memory=False,
    )
    optimizer = _optimizer(model, learning_rate, weight_decay)
    steps_per_epoch = math.ceil(len(loader) / gradient_accumulation_steps)
    total_steps = steps_per_epoch * epochs
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, round(total_steps * 0.08)),
        num_training_steps=total_steps,
    )
    best_state = _capture_state(model, state_names)
    best_score = (-math.inf, -math.inf)
    best_metrics: dict[str, Any] = {}
    best_epoch = 0
    history: list[dict[str, Any]] = []
    optimizer_steps = 0
    best_optimizer_step = 0
    elapsed_before_resume = 0.0
    start_epoch = 1
    checkpoint_context_migration: dict[str, Any] | None = None
    if (checkpoint_directory is None) != (checkpoint_context_sha256 is None):
        raise RuntimeError("stage checkpoint directory와 context는 함께 지정해야 합니다.")
    if checkpoint_context_migration_path is not None and checkpoint_directory is None:
        raise RuntimeError("stage checkpoint 없이 context migration을 지정할 수 없습니다.")
    if checkpoint_directory is not None and checkpoint_context_sha256 is not None:
        resumed = _load_latest_stage_checkpoint(
            checkpoint_directory=checkpoint_directory,
            context_sha256=checkpoint_context_sha256,
            stage=stage,
            epochs=epochs,
            model=model,
            state_names=state_names,
            optimizer=optimizer,
            scheduler=scheduler,
            generator=generator,
            device=device,
            context_migration_path=checkpoint_context_migration_path,
        )
        if resumed is not None:
            best_state = resumed.best_state
            best_score = resumed.best_score
            best_metrics = resumed.best_metrics
            best_epoch = resumed.best_epoch
            history = resumed.history
            optimizer_steps = resumed.optimizer_steps
            best_optimizer_step = resumed.best_optimizer_step
            elapsed_before_resume = resumed.elapsed_wall_seconds
            checkpoint_context_migration = resumed.context_migration
            start_epoch = resumed.completed_epoch + 1
            print(
                json.dumps(
                    {
                        "event": "TRAINING_STAGE_RESUMED",
                        "stage": stage,
                        "completed_epoch": resumed.completed_epoch,
                        "next_epoch": start_epoch,
                        "optimizer_step": optimizer_steps,
                        "planned_optimizer_steps": total_steps,
                        "checkpoint_directory": str(checkpoint_directory),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    print(
        json.dumps(
            {
                "event": "TRAINING_STAGE_STARTED",
                "stage": stage,
                "epochs": epochs,
                "train_rows": len(train_dataset),
                "checkpoint_rows": len(checkpoint_dataset),
                "steps_per_epoch": steps_per_epoch,
                "planned_optimizer_steps": total_steps,
                "device": str(device),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    for epoch in range(start_epoch, epochs + 1):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        total_loss_mass = 0.0
        epoch_rows_seen = 0
        current_window_sample_count = 0
        for batch_index, raw_batch in enumerate(loader):
            if batch_index % gradient_accumulation_steps == 0:
                current_window_sample_count = min(
                    gradient_accumulation_steps * batch_size,
                    len(train_dataset) - batch_index * batch_size,
                )
            batch = _to_device(raw_batch, device)
            actual_batch_size = int(batch["labels"].shape[0])
            first = _model_forward(model, batch)
            first_loss = hierarchical_calibrated_loss(
                first,
                batch["labels"],
                batch["sample_weight"],
                batch["domain_ids"],
                domain_mass,
            )
            loss = first_loss
            if rdrop_alpha > 0.0:
                second = _model_forward(model, batch)
                second_loss = hierarchical_calibrated_loss(
                    second,
                    batch["labels"],
                    batch["sample_weight"],
                    batch["domain_ids"],
                    domain_mass,
                )
                consistency = hierarchical_rdrop_consistency(
                    first,
                    second,
                    batch["sample_weight"],
                    batch["domain_ids"],
                    domain_mass,
                )
                loss = 0.5 * (first_loss + second_loss) + rdrop_alpha * consistency
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError(f"{stage} loss가 NaN/Inf입니다.")
            cast(
                Any,
                loss * (actual_batch_size / current_window_sample_count),
            ).backward()
            total_loss_mass += float(loss.detach().cpu()) * actual_batch_size
            epoch_rows_seen += actual_batch_size
            should_step = (
                batch_index + 1
            ) % gradient_accumulation_steps == 0 or batch_index + 1 == len(loader)
            if should_step:
                gradient_norm = torch.nn.utils.clip_grad_norm_(
                    [parameter for parameter in model.parameters() if parameter.requires_grad],
                    1.0,
                )
                if not bool(torch.isfinite(gradient_norm)):
                    raise FloatingPointError(f"{stage} gradient norm이 NaN/Inf입니다.")
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_steps += 1
                if (
                    optimizer_steps % PROGRESS_LOG_INTERVAL_OPTIMIZER_STEPS == 0
                    or optimizer_steps == total_steps
                ):
                    print(
                        json.dumps(
                            {
                                "event": "TRAINING_PROGRESS",
                                "stage": stage,
                                "epoch": epoch,
                                "epoch_rows_seen": epoch_rows_seen,
                                "epoch_rows_total": len(train_dataset),
                                "optimizer_step": optimizer_steps,
                                "planned_optimizer_steps": total_steps,
                                "mean_train_row_weighted_batch_estimator_so_far": (
                                    total_loss_mass / epoch_rows_seen
                                ),
                                "wall_seconds": (
                                    elapsed_before_resume + time.monotonic() - stage_started
                                ),
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
            if interruption_audit is not None:
                interruption_audit.mark_progress()
        checkpoint_logits, checkpoint_labels, checkpoint_domains = predict(
            model,
            checkpoint_dataset,
            collator,
            batch_size=eval_batch_size,
            device=device,
        )
        checkpoint_metrics = metrics_by_domain(
            checkpoint_labels,
            checkpoint_logits.argmax(axis=-1),
            checkpoint_domains,
        )
        score = weakest_source_score(checkpoint_metrics)
        if interruption_audit is not None:
            interruption_audit.mark_progress()
        history.append(
            {
                "epoch": epoch,
                "mean_train_row_weighted_batch_estimator": total_loss_mass / len(train_dataset),
                "checkpoint_metrics": checkpoint_metrics,
                "checkpoint_primary_weakest_source_macro_f1": score[0],
                "checkpoint_secondary_overall_macro_f1": score[1],
            }
        )
        print(
            json.dumps(
                {
                    "event": "TRAINING_EPOCH_COMPLETED",
                    "stage": stage,
                    "epoch": epoch,
                    "mean_train_row_weighted_batch_estimator": (
                        total_loss_mass / len(train_dataset)
                    ),
                    "checkpoint_primary_weakest_source_macro_f1": score[0],
                    "checkpoint_secondary_overall_macro_f1": score[1],
                    "wall_seconds": elapsed_before_resume + time.monotonic() - stage_started,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if score > best_score:
            best_score = score
            best_state = _capture_state(model, state_names)
            best_metrics = checkpoint_metrics
            best_epoch = epoch
            best_optimizer_step = optimizer_steps
        if checkpoint_directory is not None and checkpoint_context_sha256 is not None:
            checkpoint_path = _save_stage_checkpoint(
                checkpoint_directory=checkpoint_directory,
                context_sha256=checkpoint_context_sha256,
                stage=stage,
                completed_epoch=epoch,
                epochs=epochs,
                model=model,
                state_names=state_names,
                best_state=best_state,
                best_epoch=best_epoch,
                best_score=best_score,
                best_metrics=best_metrics,
                history=history,
                optimizer=optimizer,
                scheduler=scheduler,
                generator=generator,
                optimizer_steps=optimizer_steps,
                best_optimizer_step=best_optimizer_step,
                elapsed_wall_seconds=(elapsed_before_resume + time.monotonic() - stage_started),
                device=device,
            )
            print(
                json.dumps(
                    {
                        "event": "TRAINING_STAGE_CHECKPOINT_SAVED",
                        "stage": stage,
                        "epoch": epoch,
                        "checkpoint": str(checkpoint_path),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    if optimizer_steps != total_steps:
        raise RuntimeError("고정 full-epoch optimizer update 계약이 일치하지 않습니다.")
    _restore_state(model, best_state)
    active_parameter_provenance = _verify_inactive_residuals_preserved(
        model,
        inactive_residual_state,
        active_parameter_provenance,
    )
    return StageResult(
        stage=stage,
        best_epoch=best_epoch,
        checkpoint_score=best_score,
        checkpoint_metrics=best_metrics,
        history=history,
        state=best_state,
        optimizer_steps=optimizer_steps,
        planned_optimizer_steps=total_steps,
        best_optimizer_step=best_optimizer_step,
        wall_seconds=elapsed_before_resume + time.monotonic() - stage_started,
        objective_provenance=domain_mass_objective_record(domain_mass),
        active_parameter_provenance=active_parameter_provenance,
        checkpoint_context_migration=checkpoint_context_migration,
    )


def _validate_log_probability_matrix(values: NDArray[np.float64]) -> None:
    if (
        not isinstance(values, np.ndarray)
        or values.ndim != 2
        or values.shape[0] == 0
        or values.shape[1] != len(LABEL_ORDER)
        or not np.issubdtype(values.dtype, np.floating)
        or not bool(np.isfinite(values).all())
    ):
        raise ValueError("감성 log-probability 행렬 계약이 잘못되었습니다.")


def _validate_calibration_arrays(
    logits: NDArray[np.float64],
    domains: NDArray[np.int64],
    *,
    labels: NDArray[np.int64] | None = None,
    require_every_domain: bool,
) -> None:
    _validate_log_probability_matrix(logits)
    row_count = logits.shape[0]
    if (
        not isinstance(domains, np.ndarray)
        or domains.shape != (row_count,)
        or not np.issubdtype(domains.dtype, np.integer)
        or np.issubdtype(domains.dtype, np.bool_)
        or bool((domains < 0).any())
        or bool((domains >= len(DOMAIN_ORDER)).any())
    ):
        raise ValueError("감성 calibration domain 계약이 잘못되었습니다.")
    if labels is not None and (
        not isinstance(labels, np.ndarray)
        or labels.shape != (row_count,)
        or not np.issubdtype(labels.dtype, np.integer)
        or np.issubdtype(labels.dtype, np.bool_)
        or bool((labels < 0).any())
        or bool((labels >= len(LABEL_ORDER)).any())
    ):
        raise ValueError("감성 calibration label 계약이 잘못되었습니다.")
    if require_every_domain and set(np.unique(domains).tolist()) != set(range(len(DOMAIN_ORDER))):
        raise ValueError("calibration 분할에 모든 source domain이 있어야 합니다.")


def _common_calibrated_rows(
    logits: NDArray[np.float64],
    domain: str,
    *,
    temperature: float,
    neutral_threshold: float,
    sample_count: int,
    fit_status: str,
) -> tuple[NDArray[np.float64], NDArray[np.int64]]:
    _validate_log_probability_matrix(logits)
    calibration = DomainCalibration(
        temperature=temperature,
        neutral_threshold=neutral_threshold,
        sample_count=sample_count,
        fit_status=fit_status,
    )
    probabilities = np.empty_like(logits, dtype=np.float64)
    predictions = np.full(len(logits), -1, dtype=np.int64)
    for index, row in enumerate(logits):
        prediction = calibrated_sentiment_prediction(
            row.tolist(),
            cast(Any, domain),
            cast(Any, {domain: calibration}),
        )
        probabilities[index] = [prediction.calibrated_probabilities[label] for label in LABEL_ORDER]
        predictions[index] = LABEL_ORDER.index(prediction.label)
    if not bool(np.isfinite(probabilities).all()) or bool((predictions < 0).any()):
        raise RuntimeError("공용 runtime calibration이 모든 행을 처리하지 못했습니다.")
    return probabilities, predictions


def fit_calibration(
    logits: NDArray[np.float64],
    labels: NDArray[np.int64],
    domains: NDArray[np.int64],
) -> dict[str, dict[str, float | int | str]]:
    _validate_calibration_arrays(
        logits,
        domains,
        labels=labels,
        require_every_domain=True,
    )
    result: dict[str, dict[str, float | int | str]] = {}
    for domain_id, domain in enumerate(DOMAIN_ORDER):
        selected = domains == domain_id
        domain_logits = logits[selected]
        domain_labels = labels[selected]
        counts = np.bincount(domain_labels, minlength=len(LABEL_ORDER))
        if len(domain_labels) < MIN_CALIBRATION_DOMAIN_ROWS or bool(
            (counts < MIN_CALIBRATION_LABEL_ROWS).any()
        ):
            result[domain] = {
                "temperature": 1.0,
                "neutral_threshold": 0.5,
                "sample_count": int(len(domain_labels)),
                "fit_status": "INSUFFICIENT_CALIBRATION_ROWS_DEFAULTED",
            }
            continue
        temperature_candidates: list[tuple[float, float]] = []
        for temperature in TEMPERATURE_GRID:
            probabilities, _ = _common_calibrated_rows(
                domain_logits,
                domain,
                temperature=temperature,
                neutral_threshold=0.5,
                sample_count=len(domain_labels),
                fit_status="CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK",
            )
            true_probabilities = probabilities[np.arange(len(domain_labels)), domain_labels]
            if bool((true_probabilities <= 0.0).any()):
                raise FloatingPointError("calibration NLL 확률이 0 이하입니다.")
            nll = -float(np.log(true_probabilities).mean())
            objective = nll + TEMPERATURE_SHRINKAGE * math.log(temperature) ** 2
            temperature_candidates.append((objective, temperature))
        _, best_temperature = min(
            temperature_candidates,
            key=lambda item: (item[0], abs(item[1] - 1.0), item[1]),
        )
        threshold_candidates: list[tuple[float, float]] = []
        for threshold in NEUTRAL_THRESHOLD_GRID:
            _, predicted = _common_calibrated_rows(
                domain_logits,
                domain,
                temperature=best_temperature,
                neutral_threshold=threshold,
                sample_count=len(domain_labels),
                fit_status="CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK",
            )
            macro_f1 = float(
                f1_score(
                    domain_labels,
                    predicted,
                    labels=range(len(LABEL_ORDER)),
                    average="macro",
                    zero_division=0,
                )
            )
            objective = macro_f1 - NEUTRAL_THRESHOLD_SHRINKAGE * (threshold - 0.5) ** 2
            threshold_candidates.append((objective, threshold))
        _, best_threshold = max(
            threshold_candidates,
            key=lambda item: (item[0], -abs(item[1] - 0.5), -item[1]),
        )
        result[domain] = {
            "temperature": float(best_temperature),
            "neutral_threshold": float(best_threshold),
            "sample_count": int(len(domain_labels)),
            "fit_status": "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK",
        }
    return result


def calibrated_predictions(
    logits: NDArray[np.float64],
    domains: NDArray[np.int64],
    calibration: dict[str, dict[str, float | int | str]],
) -> NDArray[np.int64]:
    _validate_calibration_arrays(
        logits,
        domains,
        require_every_domain=False,
    )
    validated = validate_domain_calibration(calibration)
    result = np.full(len(logits), -1, dtype=np.int64)
    for index, row in enumerate(logits):
        domain = DOMAIN_ORDER[int(domains[index])]
        prediction = calibrated_sentiment_prediction(
            row.tolist(),
            cast(Any, domain),
            validated,
        )
        result[index] = LABEL_ORDER.index(prediction.label)
    if bool((result < 0).any()):
        raise RuntimeError("calibration 예측이 모든 행에 할당되지 않았습니다.")
    return result


def _artifact_records(directory: Path) -> dict[str, dict[str, int | str]]:
    records: dict[str, dict[str, int | str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"artifact에 symlink가 포함되어 있습니다: {path}")
        if path.is_file():
            relative = path.relative_to(directory).as_posix()
            records[relative] = {
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
    return records


def save_artifact(
    model: nn.Module,
    tokenizer: Any,
    output_dir: Path,
    metadata: dict[str, Any],
) -> dict[str, dict[str, int | str]]:
    if output_dir.exists() or output_dir.is_symlink():
        raise RuntimeError(f"후보 artifact 출력이 이미 존재합니다: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_dir.parent / f".{output_dir.name}.tmp-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    try:
        adapter_dir = temporary / "adapter"
        cast(Any, model.encoder).save_pretrained(adapter_dir, safe_serialization=True)
        adapter_files = list(adapter_dir.rglob("*"))
        if not (adapter_dir / "adapter_model.safetensors").is_file() or any(
            path.suffix == ".bin" for path in adapter_files if path.is_file()
        ):
            raise RuntimeError("LoRA adapter는 safetensors로만 저장해야 합니다.")
        head_state = {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in source_hierarchical_head_state_dict(model).items()
        }
        save_file(head_state, temporary / HEAD_ARTIFACT_FILENAME)
        tokenizer.save_pretrained(temporary)
        metadata_path = temporary / "hannah_metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        artifact_files = _artifact_records(temporary)
        manifest = {
            "schema_version": ARTIFACT_MANIFEST_SCHEMA_VERSION,
            "status": "ATOMIC_COMPLETE",
            "generated_at": datetime.now(UTC).isoformat(),
            "artifact_files": artifact_files,
            "safe_serialization_only": True,
            "symlinks_allowed": False,
            "overwrite_allowed": False,
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if output_dir.exists() or output_dir.is_symlink():
            raise RuntimeError("학습 중 artifact 출력이 생성되었습니다.")
        os.rename(temporary, output_dir)
        return artifact_files
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def _runtime_parity_canaries(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_domain: dict[str, dict[str, str]] = {}
    for row in rows:
        source_type = str(row.get("source_type", "")).strip().upper()
        target_security = v5._target_security(row)
        domain = strict_source_domain(source_type, target_security)
        text = str(row.get("text", "")).strip()
        if domain not in by_domain and text:
            by_domain[domain] = {
                "domain": domain,
                "source_type": source_type,
                "target_security": target_security,
                "text": text,
            }
    if set(by_domain) != set(DOMAIN_ORDER):
        raise RuntimeError("CPU runtime parity canary에 모든 source domain이 없습니다.")
    return [by_domain[domain] for domain in DOMAIN_ORDER]


@contextmanager
def _runtime_parity_base_directory(base_source: BaseSource) -> Iterator[Path]:
    if base_source.kind == "DAPT_MERGED_FP32":
        directory = validate_source_hierarchical_base_directory(Path(base_source.model_path))
        yield directory
        return
    with tempfile.TemporaryDirectory(prefix="hannah-v6-parity-base-") as temporary:
        directory = Path(temporary) / "base"
        base = AutoModel.from_pretrained(
            v5.BASE_MODEL,
            revision=v5.BASE_MODEL_REVISION,
            trust_remote_code=False,
            weights_only=True,
        )
        base.save_pretrained(directory, safe_serialization=True)
        del base
        yield validate_source_hierarchical_base_directory(directory)


def _parity_input_tensors(
    tokenizer: Any,
    canary: dict[str, str],
    max_length: int,
) -> tuple[dict[str, torch.Tensor], dict[str, list[int]]]:
    features = encode_sentiment_input(
        tokenizer,
        canary["text"],
        canary["source_type"],
        max_length,
        canary["target_security"],
    )
    tensors = {name: torch.tensor([values], dtype=torch.long) for name, values in features.items()}
    tensors["domain_ids"] = torch.tensor(
        [DOMAIN_TO_ID[cast(Any, canary["domain"])]],
        dtype=torch.long,
    )
    return tensors, features


def verify_production_cpu_roundtrip(
    *,
    model: nn.Module,
    tokenizer: Any,
    artifact_dir: Path,
    base_source: BaseSource,
    calibration: dict[str, dict[str, float | int | str]],
    canary_rows: list[dict[str, Any]],
    max_length: int,
    validate_deployable_artifact: bool,
) -> dict[str, Any]:
    started = time.monotonic()
    validated_calibration = validate_domain_calibration(calibration)
    if validate_deployable_artifact:
        contract = validate_source_hierarchical_artifact(artifact_dir)
        if (
            contract.max_length != max_length
            or contract.calibration_by_domain != validated_calibration
            or contract.base_source_kind != base_source.kind
        ):
            raise RuntimeError("CPU runtime parity artifact 계약이 학습 계약과 다릅니다.")
    canaries = _runtime_parity_canaries(canary_rows)
    model.to(torch.device("cpu"))
    model.eval()
    records: list[dict[str, Any]] = []
    logits_max_abs_error = 0.0
    probability_max_abs_error = 0.0
    with _runtime_parity_base_directory(base_source) as base_directory:
        runtime = load_source_hierarchical_runtime(
            artifact_dir=artifact_dir,
            base_model_dir=base_directory,
            max_length=max_length,
            calibration_by_domain=validated_calibration,
        )
        loaded_model = getattr(runtime, "_model", None)
        loaded_tokenizer = getattr(runtime, "_tokenizer", None)
        loaded_torch = getattr(runtime, "_torch", None)
        if (
            not isinstance(loaded_model, nn.Module)
            or loaded_tokenizer is None
            or loaded_torch is not torch
        ):
            raise RuntimeError(
                "production runtime raw-logit parity interface를 확인할 수 없습니다."
            )
        loaded_model.eval()
        for canary in canaries:
            expected_inputs, expected_features = _parity_input_tensors(
                tokenizer,
                canary,
                max_length,
            )
            loaded_inputs, loaded_features = _parity_input_tensors(
                loaded_tokenizer,
                canary,
                max_length,
            )
            if loaded_features != expected_features:
                raise RuntimeError("artifact tokenizer CPU round-trip feature가 다릅니다.")
            with torch.inference_mode():
                expected_output = _model_forward(model, expected_inputs)
                loaded_output = _model_forward(loaded_model, loaded_inputs)
            expected_logits = expected_output.logits.detach().to(torch.float64).cpu()
            loaded_logits = loaded_output.logits.detach().to(torch.float64).cpu()
            if expected_logits.shape != (1, len(LABEL_ORDER)) or loaded_logits.shape != (
                1,
                len(LABEL_ORDER),
            ):
                raise RuntimeError("CPU runtime parity logit 형상이 다릅니다.")
            logit_error = float(torch.max(torch.abs(expected_logits - loaded_logits)))
            if not math.isfinite(logit_error) or logit_error > RUNTIME_PARITY_LOGIT_ATOL:
                raise RuntimeError(
                    "production CPU runtime logit parity가 허용 오차를 초과했습니다."
                )
            domain = cast(Any, canary["domain"])
            expected_prediction = calibrated_sentiment_prediction(
                expected_logits[0].tolist(),
                domain,
                validated_calibration,
            )
            loaded_prediction = runtime.predict(
                canary["text"],
                canary["source_type"],
                canary["target_security"],
            )
            probability_error = max(
                abs(
                    expected_prediction.calibrated_probabilities[label]
                    - loaded_prediction.calibrated_probabilities[label]
                )
                for label in LABEL_ORDER
            )
            if (
                not math.isfinite(probability_error)
                or probability_error > RUNTIME_PARITY_PROBABILITY_ATOL
                or expected_prediction.label != loaded_prediction.label
            ):
                raise RuntimeError(
                    "production CPU runtime 확률/임계값 최종 label parity가 잘못되었습니다."
                )
            logits_max_abs_error = max(logits_max_abs_error, logit_error)
            probability_max_abs_error = max(
                probability_max_abs_error,
                probability_error,
            )
            commitment = sha256(
                json.dumps(
                    canary,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            records.append(
                {
                    "domain": canary["domain"],
                    "input_commitment_sha256": commitment,
                    "logits_max_abs_error": logit_error,
                    "probability_max_abs_error": probability_error,
                    "expected_label": expected_prediction.label,
                    "loaded_label": loaded_prediction.label,
                    "exact_label_agreement": True,
                }
            )
    return {
        "schema_version": "kf-deberta-shared-residual-training-cpu-roundtrip/v2",
        "status": "PASS",
        "loader": (
            "hannah_montana_ai.services.source_hierarchical_sentiment."
            "load_source_hierarchical_runtime"
        ),
        "device": "cpu",
        "canary_count": len(records),
        "domains": [record["domain"] for record in records],
        "logits_atol": RUNTIME_PARITY_LOGIT_ATOL,
        "probability_atol": RUNTIME_PARITY_PROBABILITY_ATOL,
        "logits_max_abs_error": logits_max_abs_error,
        "probability_max_abs_error": probability_max_abs_error,
        "exact_final_threshold_label_agreement": True,
        "raw_logits_access": "TRAINER_INTERNAL_PRODUCTION_RUNTIME_MODEL_INSPECTION",
        "records": records,
        "wall_seconds": time.monotonic() - started,
    }


def _parameter_counts(model: nn.Module) -> tuple[int, int]:
    trainable = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    total = sum(parameter.numel() for parameter in model.parameters())
    return trainable, total


def main() -> None:
    args = parser().parse_args()
    validate_arguments(args)
    if args.report_path.exists() or args.report_path.is_symlink():
        raise SystemExit(f"후보 report 출력이 이미 존재합니다: {args.report_path}")
    if args.output_dir.exists() or args.output_dir.is_symlink():
        raise SystemExit(f"후보 artifact 출력이 이미 존재합니다: {args.output_dir}")
    checkpoint_root = args.checkpoint_root or (
        args.output_dir.parent / f".{args.output_dir.name}-training-checkpoints"
    )
    if checkpoint_root.is_symlink():
        raise SystemExit("후보 checkpoint root는 symlink일 수 없습니다.")
    _set_seed(args.seed)
    execution_snapshot: dict[str, Any] | None = None
    if args.validate_only:
        prepared = prepare_partitions(args)
        base_source = resolve_base_source(args.base_source, verify_pinned=False)
    else:
        _validate_reservation_paths(args)
        startup_input_paths = _input_paths(args)
        for name, path in startup_input_paths.items():
            assert_training_path_allowed(path, name)
            v5._require_regular_input(path, name)
        base_source = resolve_base_source(args.base_source, verify_pinned=True)
        execution_snapshot = capture_execution_snapshot(startup_input_paths, base_source)
        prepared = prepare_partitions(args)
        base_source = assert_execution_snapshot_unchanged(
            execution_snapshot,
            prepared.input_paths,
            args.base_source,
        )
    validation = {
        "status": "VALIDATED_WITHOUT_TRAINING" if args.validate_only else "READY_TO_TRAIN",
        "schema_version": "kf-deberta-shared-residual-sentiment-validation/v2",
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "train_count": len(prepared.train_rows),
        "checkpoint_count": len(prepared.checkpoint_rows),
        "calibration_count": len(prepared.calibration_rows),
        "selection_count": len(prepared.selection_rows),
        "gold_refinement_count": len(prepared.gold_refinement_rows),
        "verified_gold_provenance": prepared.gold_provenance,
        "prepared_partition_commitments": prepared.commitments,
        "data_selection_seed": v5.DATA_SELECTION_SEED,
        "base_source": base_source.provenance,
        "model_recipe": {
            "encoder": "shared-kf-deberta",
            "lora_layers": list(LORA_LAYERS),
            "lora_target_modules": list(LORA_TARGET_MODULES),
            "lora_rank": LORA_RANK,
            "lora_alpha": LORA_ALPHA,
            "head_architecture": EXPECTED_HEAD_ARCHITECTURE,
            "source_domains": list(DOMAIN_ORDER),
            "head_outputs": ["neutral_vs_directional", "negative_vs_positive"],
            "three_class_composition": "normalized-hierarchical-log-probabilities/v1",
            "loss": LOSS_CONTRACT_VERSION,
            "checkpoint_primary": "weakest-source-domain-macro-f1",
            "calibration": "calibration-only-sequential-temperature-neutral-threshold-shrunk/v1",
            "adaptive_development_selection_primary": "weakest-source-domain-macro-f1",
        },
        "partition_roles": {
            "SELECTION": ADAPTIVE_SELECTION_ROLE,
            "CONFIRMATORY": "ONLY_INDEPENDENT_GENERALIZATION_EVIDENCE_AFTER_LOCK",
        },
        "dapt_verifier_contract": DAPT_VERIFIER_CONTRACT,
    }
    if args.validate_only:
        print(json.dumps(validation, ensure_ascii=False))
        return

    tokenizer = AutoTokenizer.from_pretrained(
        v5.BASE_MODEL,
        revision=v5.BASE_MODEL_REVISION,
        trust_remote_code=False,
    )
    model = cast(
        nn.Module,
        build_model(base_source, gradient_checkpointing=args.gradient_checkpointing),
    )
    device = _device(args.device)
    model.to(device)
    collator = DomainCollator(tokenizer)
    datasets = {
        "TRAIN": DomainEncodedDataset(prepared.train_rows, tokenizer, args.max_length),
        "CHECKPOINT": DomainEncodedDataset(prepared.checkpoint_rows, tokenizer, args.max_length),
        "CALIBRATION": DomainEncodedDataset(prepared.calibration_rows, tokenizer, args.max_length),
        "SELECTION": DomainEncodedDataset(prepared.selection_rows, tokenizer, args.max_length),
        "GOLD_REFINEMENT": DomainEncodedDataset(
            prepared.gold_refinement_rows, tokenizer, args.max_length
        ),
    }
    trainable_names = {
        name for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    if execution_snapshot is None:
        raise RuntimeError("실행 snapshot 없이 학습 checkpoint를 구성할 수 없습니다.")
    checkpoint_context_sha256 = _stage_checkpoint_context_sha256(
        {
            "execution_material": execution_snapshot["material"],
            "seed": args.seed,
            "max_length": args.max_length,
            "stage1_epochs": args.stage1_epochs,
            "stage2_epochs": args.stage2_epochs,
            "batch_size": args.batch_size,
            "eval_batch_size": args.eval_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "stage1_learning_rate": args.stage1_learning_rate,
            "stage2_learning_rate": args.stage2_learning_rate,
            "weight_decay": args.weight_decay,
            "rdrop_alpha": args.rdrop_alpha,
            "gradient_checkpointing": bool(args.gradient_checkpointing),
        }
    )
    interruption_audit = TrainingInterruptionAudit()
    interruption_audit.install()
    stage1 = train_stage(
        model,
        datasets["TRAIN"],
        datasets["CHECKPOINT"],
        collator,
        stage="STAGE1_DOMAIN_BALANCED_FULL",
        epochs=args.stage1_epochs,
        learning_rate=args.stage1_learning_rate,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        rdrop_alpha=args.rdrop_alpha,
        seed=args.seed,
        device=device,
        state_names=trainable_names,
        interruption_audit=interruption_audit,
        checkpoint_directory=checkpoint_root / "stage1",
        checkpoint_context_sha256=checkpoint_context_sha256,
        checkpoint_context_migration_path=args.checkpoint_context_migration,
    )
    for parameter in cast(Any, model).encoder.parameters():
        parameter.requires_grad = False
    stage2 = train_stage(
        model,
        datasets["GOLD_REFINEMENT"],
        datasets["CHECKPOINT"],
        collator,
        stage="STAGE2_GOLD_CLEAN_HEADS_ONLY",
        epochs=args.stage2_epochs,
        learning_rate=args.stage2_learning_rate,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        rdrop_alpha=args.rdrop_alpha,
        seed=args.seed + 1_003,
        device=device,
        state_names=trainable_names,
        interruption_audit=interruption_audit,
        checkpoint_directory=checkpoint_root / "stage2",
        checkpoint_context_sha256=checkpoint_context_sha256,
        checkpoint_context_migration_path=args.stage2_checkpoint_context_migration,
    )
    selected_stage = stage2
    if stage1.checkpoint_score >= stage2.checkpoint_score:
        _restore_state(model, stage1.state)
        selected_stage = stage1

    calibration_logits, calibration_labels, calibration_domains = predict(
        model,
        datasets["CALIBRATION"],
        collator,
        batch_size=args.eval_batch_size,
        device=device,
    )
    calibration = fit_calibration(
        calibration_logits,
        calibration_labels,
        calibration_domains,
    )
    calibration_predictions = calibrated_predictions(
        calibration_logits,
        calibration_domains,
        calibration,
    )
    calibration_metrics = metrics_by_domain(
        calibration_labels,
        calibration_predictions,
        calibration_domains,
    )
    selection_logits, selection_labels, selection_domains = predict(
        model,
        datasets["SELECTION"],
        collator,
        batch_size=args.eval_batch_size,
        device=device,
    )
    selection_predictions = calibrated_predictions(
        selection_logits,
        selection_domains,
        calibration,
    )
    selection_metrics = metrics_by_domain(
        selection_labels,
        selection_predictions,
        selection_domains,
    )
    selection_score = weakest_source_score(selection_metrics)
    interruption_audit.mark_progress()
    interruption_audit.close()
    interruption_provenance = interruption_audit.report()
    version = (
        f"hana-montana-kf-deberta-k-fnspid-sentiment-v6-seed{args.seed}-"
        f"{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    )
    runtime_loader_contract = {
        "schema_version": RUNTIME_LOADER_SCHEMA_VERSION,
        "base_source": base_source.provenance,
        "adapter_path": "adapter",
        "heads_path": HEAD_ARTIFACT_FILENAME,
        "tokenizer_source": "artifact-root",
        "domain_order": list(DOMAIN_ORDER),
        "domain_required": True,
        "unknown_domain_behavior": "FAIL_CLOSED",
        "pooling": "last_hidden_state_cls",
        "head_tensor_contract": EXPECTED_HEAD_TENSOR_CONTRACT,
        "head_architecture": EXPECTED_HEAD_ARCHITECTURE,
        "composition": {
            "NEGATIVE": "log_sigmoid(boundary)+log_softmax(direction)[0]",
            "NEUTRAL": "log_sigmoid(-boundary)",
            "POSITIVE": "log_sigmoid(boundary)+log_softmax(direction)[1]",
        },
        "calibration": calibration,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "max_length": args.max_length,
    }
    metadata = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "version": version,
        "base_model": v5.BASE_MODEL,
        "base_model_revision": v5.BASE_MODEL_REVISION,
        "base_source_kind": base_source.kind,
        "label_order": list(LABEL_ORDER),
        "runtime_loader_contract": runtime_loader_contract,
        "prepared_partition_commitments": prepared.commitments,
        "selected_stage": selected_stage.stage,
        "trained_at": datetime.now(UTC).isoformat(),
    }
    if execution_snapshot is None:
        raise RuntimeError("실행 snapshot 없이 학습 artifact를 저장할 수 없습니다.")
    base_source = assert_execution_snapshot_unchanged(
        execution_snapshot,
        prepared.input_paths,
        args.base_source,
    )
    if base_source.provenance != runtime_loader_contract["base_source"]:
        raise RuntimeError("저장 직전 base-source provenance가 변경되었습니다.")
    model.to(torch.device("cpu"))
    artifact_files = save_artifact(model, tokenizer, args.output_dir, metadata)
    try:
        production_cpu_roundtrip = verify_production_cpu_roundtrip(
            model=model,
            tokenizer=tokenizer,
            artifact_dir=args.output_dir,
            base_source=base_source,
            calibration=calibration,
            canary_rows=prepared.selection_rows,
            max_length=args.max_length,
            validate_deployable_artifact=True,
        )
    except Exception:
        # 현재 실행이 생성한 parity 실패 후보는 배포 후보로 남기지 않는다.
        shutil.rmtree(args.output_dir)
        raise
    trainable_count, total_count = _parameter_counts(model)
    report = {
        **metadata,
        "schema_version": TRAINING_SCHEMA_VERSION,
        "model_family": MODEL_FAMILY,
        "max_length": args.max_length,
        "seed": args.seed,
        "dataset_revision": v5.DATASET_REVISION,
        "public_dataset_revision": v5.PUBLIC_DATASET_REVISION,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "execution_snapshot": execution_snapshot,
        "input_artifacts": execution_snapshot["material"]["input_artifacts"],
        "training_code": execution_snapshot["material"]["training_code"],
        "dependency_artifacts": execution_snapshot["material"]["dependency_artifacts"],
        "dependency_versions": execution_snapshot["material"]["dependency_versions"],
        "pinned_base_tokenizer_files": execution_snapshot["material"][
            "pinned_base_tokenizer_files"
        ],
        "base_source": base_source.provenance,
        "training_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": importlib.metadata.version("transformers"),
            "peft": importlib.metadata.version("peft"),
            "numpy": np.__version__,
            "device": str(device),
            "bitwise_deterministic_guaranteed": False,
        },
        "training_arguments": {
            "seed": args.seed,
            "data_selection_seed": v5.DATA_SELECTION_SEED,
            "stage1_epochs": args.stage1_epochs,
            "stage2_epochs": args.stage2_epochs,
            "batch_size": args.batch_size,
            "eval_batch_size": args.eval_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "stage1_learning_rate": args.stage1_learning_rate,
            "stage2_learning_rate": args.stage2_learning_rate,
            "weight_decay": args.weight_decay,
            "rdrop_alpha": args.rdrop_alpha,
            "gradient_checkpointing": bool(args.gradient_checkpointing),
        },
        "restart_safe_stage_checkpointing": {
            "schema_version": STAGE_CHECKPOINT_SCHEMA_VERSION,
            "checkpoint_root": str(checkpoint_root),
            "context_sha256": checkpoint_context_sha256,
            "interval": "END_OF_EPOCH",
            "atomic_directory_publish": True,
            "safe_tensor_serialization_only": True,
            "automatic_latest_resume": True,
            "completed_stage_context_migrations": {
                "stage1": stage1.checkpoint_context_migration,
                "stage2": stage2.checkpoint_context_migration,
            },
            "restores": [
                "CURRENT_MODEL",
                "BEST_MODEL",
                "OPTIMIZER",
                "SCHEDULER",
                "TORCH_CPU_RNG",
                "MPS_RNG_WHEN_USED",
                "DATALOADER_GENERATOR_RNG",
            ],
        },
        "architecture": validation["model_recipe"],
        "loss": {
            "method": LOSS_CONTRACT_VERSION,
            "boundary_weight": BOUNDARY_LOSS_WEIGHT,
            "direction_weight": DIRECTION_LOSS_WEIGHT,
            "composite_weight": COMPOSITE_LOSS_WEIGHT,
            "boundary_label_smoothing": BOUNDARY_LABEL_SMOOTHING,
            "direction_label_smoothing": DIRECTION_LABEL_SMOOTHING,
            "composite_label_smoothing": COMPOSITE_LABEL_SMOOTHING,
            "gold_weight": 1.5,
            "public_weight": 1.0,
            "silver_weight": "source row sample_weight",
            "target_swap_weight": v5.TARGET_SWAP_WEIGHT,
            "normalization": (
                "inverse fixed full-epoch domain×task-class weight mass; unbiased batch estimator"
            ),
        },
        "stage_selection": {
            "fit_partition": "CHECKPOINT_ONLY",
            "primary": "weakest-source-domain-macro-f1",
            "secondary": "overall-macro-f1",
            "selected_stage": selected_stage.stage,
            "stage1": {
                "best_epoch": stage1.best_epoch,
                "checkpoint_score": list(stage1.checkpoint_score),
                "checkpoint_metrics": stage1.checkpoint_metrics,
                "history": stage1.history,
                "optimizer_steps": stage1.optimizer_steps,
                "planned_optimizer_steps": stage1.planned_optimizer_steps,
                "best_optimizer_step": stage1.best_optimizer_step,
                "wall_seconds": stage1.wall_seconds,
                "objective_provenance": stage1.objective_provenance,
                "active_parameter_provenance": stage1.active_parameter_provenance,
            },
            "stage2": {
                "encoder_and_lora_frozen": True,
                "training_rows": len(prepared.gold_refinement_rows),
                "best_epoch": stage2.best_epoch,
                "checkpoint_score": list(stage2.checkpoint_score),
                "checkpoint_metrics": stage2.checkpoint_metrics,
                "history": stage2.history,
                "optimizer_steps": stage2.optimizer_steps,
                "planned_optimizer_steps": stage2.planned_optimizer_steps,
                "best_optimizer_step": stage2.best_optimizer_step,
                "wall_seconds": stage2.wall_seconds,
                "objective_provenance": stage2.objective_provenance,
                "active_parameter_provenance": stage2.active_parameter_provenance,
            },
            "executed_optimizer_steps_total": stage1.optimizer_steps + stage2.optimizer_steps,
            "planned_optimizer_steps_total": (
                stage1.planned_optimizer_steps + stage2.planned_optimizer_steps
            ),
            "fixed_full_epoch_budget": True,
            "selected_checkpoint_lineage_global_step": (
                stage1.best_optimizer_step
                if selected_stage is stage1
                else stage1.best_optimizer_step + stage2.best_optimizer_step
            ),
            "calibration_used": False,
            "adaptive_development_selection_used": False,
        },
        "calibration": {
            "fit_partition": "CALIBRATION_ONLY",
            "method": "sequential-1d-temperature-then-neutral-threshold/v1",
            "temperature_grid": list(TEMPERATURE_GRID),
            "neutral_threshold_grid": list(NEUTRAL_THRESHOLD_GRID),
            "temperature_shrinkage": TEMPERATURE_SHRINKAGE,
            "neutral_threshold_shrinkage": NEUTRAL_THRESHOLD_SHRINKAGE,
            "selection_used_for_fit": False,
            "public_test_used_for_fit": False,
            "confirmatory_used_for_fit": False,
            "parameters": calibration,
            "metrics": calibration_metrics,
        },
        "candidate_selection": {
            "fit_partition": ADAPTIVE_SELECTION_ROLE,
            "legacy_commitment_partition_name": "SELECTION",
            "primary": "weakest-source-domain-macro-f1",
            "primary_value": selection_score[0],
            "secondary_overall_macro_f1": selection_score[1],
            "metrics": selection_metrics,
            "independent_generalization_evidence": False,
            "reason": "Prior v5 diagnostics informed the v6 model and training design.",
            "confirmatory_is_only_independent_generalization_evidence": True,
            "public_test_used": False,
            "confirmatory_used": False,
        },
        "partition_roles": {
            "SELECTION": {
                "semantic_role": ADAPTIVE_SELECTION_ROLE,
                "independent_generalization_evidence": False,
            },
            "CONFIRMATORY": {
                "semantic_role": "ONLY_INDEPENDENT_GENERALIZATION_EVIDENCE_AFTER_LOCK",
                "opened": False,
            },
        },
        "partition_count": {
            "TRAIN": len(prepared.train_rows),
            "CHECKPOINT": len(prepared.checkpoint_rows),
            "CALIBRATION": len(prepared.calibration_rows),
            "SELECTION": len(prepared.selection_rows),
            "GOLD_REFINEMENT": len(prepared.gold_refinement_rows),
            "PUBLIC_TEST_NOT_LOADED": 0,
            "CONFIRMATORY_LABELS_NOT_LOADED": 0,
        },
        "training_source_distribution": dict(
            sorted(Counter(str(row.get("dataset", "")) for row in prepared.train_rows).items())
        ),
        "training_label_distribution": v5._label_distribution(prepared.train_rows),
        "prepared_partition_commitments": prepared.commitments,
        "verified_gold_provenance": prepared.gold_provenance,
        "data_audit": prepared.audit,
        "interruption_provenance": interruption_provenance,
        "production_cpu_roundtrip": production_cpu_roundtrip,
        "dapt_verifier_contract": DAPT_VERIFIER_CONTRACT,
        "artifact_files": artifact_files,
        "runtime_loader_contract": runtime_loader_contract,
        "trainable_parameter_count_after_head_freeze": trainable_count,
        "total_parameter_count": total_count,
        "test": {"sample_count": 0, "status": "SEALED_UNTIL_CANDIDATE_LOCK"},
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    with args.report_path.open("x", encoding="utf-8") as file:
        file.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
