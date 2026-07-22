from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import platform
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    EarlyStoppingCallback,
    EvalPrediction,
    TrainingArguments,
)

from hannah_montana_ai.services.model_artifact_integrity import (
    build_artifact_manifest,
    verify_artifact_manifest,
)
from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    decontaminate_public_partitions,
    purge_sentiment_group_overlap,
    stratified_hash_three_way_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import train_kf_deberta_sentiment_v2 as v5  # noqa: E402

MODEL_SEEDS = (17, 42, 73)
MAX_LENGTH = 256
EPOCHS = 1.5
BATCH_SIZE = 8
GRADIENT_ACCUMULATION_STEPS = 2
LEARNING_RATE = 1e-4
NEWS_SILVER_PER_LABEL = 6_000
DISCLOSURE_SILVER_PER_LABEL = 900
TARGET_SWAP_PER_SOURCE = 1_500
TRAINING_STRATEGY = "group-purged-three-way-ablation-target-swap-rdrop-hierarchical-upper6-lora/v1"
SCHEMA_VERSION = "k-fnspid-sentiment-ablation-training/v1"
SELECTION_SCHEMA_VERSION = "k-fnspid-sentiment-ablation-selection/v1"
WINNER_MANIFEST_SCHEMA_VERSION = "k-fnspid-sentiment-ablation-winner-manifest/v1"


class AblationMode(StrEnum):
    NO_K = "NO_K"
    NEWS_ONLY = "NEWS_ONLY"
    DISCLOSURE_ONLY = "DISCLOSURE_ONLY"
    FULL = "FULL"


@dataclass(frozen=True)
class AblationPaths:
    dataset_dir: Path = v5.DEFAULT_DATASET
    news_silver: Path = v5.DEFAULT_SILVER
    disclosure_silver: Path = v5.DEFAULT_DISCLOSURE_SILVER
    main_news_gold: Path = v5.DEFAULT_TRAIN_GOLD
    news_auxiliary_gold: Path = v5.DEFAULT_NEWS_AUXILIARY_GOLD
    disclosure_auxiliary_gold: Path = v5.DEFAULT_DISCLOSURE_AUXILIARY_GOLD
    news_auxiliary_report: Path = v5.DEFAULT_NEWS_AUXILIARY_REPORT
    disclosure_auxiliary_report: Path = v5.DEFAULT_DISCLOSURE_AUXILIARY_REPORT
    news_development_gold: Path = v5.DEFAULT_DEVELOPMENT_GOLD
    disclosure_development_gold: Path = v5.DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD
    news_reservation: Path = v5.DEFAULT_NEWS_SEALED_REVIEW
    disclosure_reservation: Path = v5.DEFAULT_DISCLOSURE_SEALED_REVIEW
    sampling_design: Path = v5.DEFAULT_SAMPLING_DESIGN_REPORT


@dataclass(frozen=True)
class PreparedAblation:
    mode: AblationMode
    train_rows: list[dict[str, Any]]
    checkpoint_rows: list[dict[str, Any]]
    calibration_rows: list[dict[str, Any]]
    selection_rows: list[dict[str, Any]]
    news_reservation: list[dict[str, Any]]
    disclosure_reservation: list[dict[str, Any]]
    target_swap_rows: list[dict[str, Any]]
    prepared_partition_commitments: dict[str, dict[str, int | str]]
    public_audit: dict[str, Any]
    news_silver_audit: dict[str, Any]
    disclosure_silver_audit: dict[str, Any]
    final_overlap_audit: dict[str, Any]
    raw_source_counts: dict[str, int]


def input_paths(paths: AblationPaths) -> dict[str, Path]:
    values = {
        "public_train": paths.dataset_dir / "ratings_train.csv",
        "public_validation": paths.dataset_dir / "ratings_val.csv",
        "news_silver": paths.news_silver,
        "disclosure_silver": paths.disclosure_silver,
        "main_news_gold": paths.main_news_gold,
        "news_auxiliary_training_gold": paths.news_auxiliary_gold,
        "disclosure_auxiliary_training_gold": paths.disclosure_auxiliary_gold,
        "news_auxiliary_training_report": paths.news_auxiliary_report,
        "disclosure_auxiliary_training_report": paths.disclosure_auxiliary_report,
        "news_development_gold": paths.news_development_gold,
        "disclosure_development_gold": paths.disclosure_development_gold,
        "news_sealed_review_reservation": paths.news_reservation,
        "disclosure_sealed_review_reservation": paths.disclosure_reservation,
        "sealed_sampling_design": paths.sampling_design,
    }
    values.update(
        {
            f"legacy_evaluation_{index}": path
            for index, path in enumerate(v5.LEGACY_EVALUATION_PATHS, start=1)
        }
    )
    return values


def prepare_ablation_data(
    mode: AblationMode,
    paths: AblationPaths,
) -> PreparedAblation:
    for name, path in input_paths(paths).items():
        v5._require_regular_input(path, name)

    public, public_audit = decontaminate_public_partitions(
        {
            "TRAIN": v5._load_public_rows(paths.dataset_dir / "ratings_train.csv"),
            "VALIDATION": v5._load_public_rows(paths.dataset_dir / "ratings_val.csv"),
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
    development_gold = v5._load_reviewed_rows(
        paths.news_development_gold,
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
        paths.disclosure_development_gold,
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
        paths.news_reservation,
        "CONFIRMATORY_SEALED_TEST_REVIEW",
        "NEWS",
    )
    disclosure_reservation = v5._load_sealed_reservation_rows(
        paths.disclosure_reservation,
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

    include_news = mode in {AblationMode.NEWS_ONLY, AblationMode.FULL}
    include_disclosure = mode in {AblationMode.DISCLOSURE_ONLY, AblationMode.FULL}
    main_news_gold: list[dict[str, Any]] = []
    news_auxiliary_gold: list[dict[str, Any]] = []
    disclosure_auxiliary_gold: list[dict[str, Any]] = []
    news_silver: list[dict[str, Any]] = []
    disclosure_silver: list[dict[str, Any]] = []
    news_silver_audit = _excluded_audit(paths.news_silver, "NEWS", mode)
    disclosure_silver_audit = _excluded_audit(
        paths.disclosure_silver,
        "DISCLOSURE",
        mode,
    )
    if include_news:
        main_news_gold = v5._load_reviewed_rows(
            paths.main_news_gold,
            "TRAIN_REVIEW",
            weight=1.5,
        )
        news_auxiliary_gold = v5._load_auxiliary_training_rows(
            paths.news_auxiliary_gold,
            paths.news_auxiliary_report,
            "NEWS",
            weight=1.5,
        )
        news_silver, news_silver_audit = v5._load_silver_rows(
            paths.news_silver,
            protected,
            NEWS_SILVER_PER_LABEL,
            v5.DATA_SELECTION_SEED,
        )
    if include_disclosure:
        disclosure_auxiliary_gold = v5._load_auxiliary_training_rows(
            paths.disclosure_auxiliary_gold,
            paths.disclosure_auxiliary_report,
            "DISCLOSURE",
            weight=1.5,
        )
        disclosure_silver, disclosure_silver_audit = v5._load_silver_rows(
            paths.disclosure_silver,
            protected,
            DISCLOSURE_SILVER_PER_LABEL,
            v5.DATA_SELECTION_SEED + 11,
        )

    public_train = [
        {**row, "source_type": "NEWS", "sample_weight": 1.0, "dataset": "PUBLIC_TRAIN"}
        for row in public["TRAIN"]
    ]
    raw_source_counts = {
        "PUBLIC_TRAIN": len(public_train),
        "K_FNSPID_CODEX_GOLD": len(main_news_gold),
        "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD": len(news_auxiliary_gold),
        "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD": len(disclosure_auxiliary_gold),
        "K_FNSPID_RULE_SILVER": len(news_silver),
        "K_FNSPID_DISCLOSURE_RULE_SILVER": len(disclosure_silver),
    }
    train_rows = v5._deduplicate_weighted(
        [
            *public_train,
            *[{**row, "dataset": "K_FNSPID_CODEX_GOLD"} for row in main_news_gold],
            *[
                {**row, "dataset": "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD"}
                for row in news_auxiliary_gold
            ],
            *[
                {**row, "dataset": "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD"}
                for row in disclosure_auxiliary_gold
            ],
            *[{**row, "dataset": "K_FNSPID_RULE_SILVER"} for row in news_silver],
            *[{**row, "dataset": "K_FNSPID_DISCLOSURE_RULE_SILVER"} for row in disclosure_silver],
        ]
    )
    train_rows, final_overlap_audit = purge_sentiment_group_overlap(train_rows, protected)
    target_swap_rows = (
        []
        if mode is AblationMode.NO_K
        else v5.build_target_swap_hard_negatives(
            train_rows,
            per_source=TARGET_SWAP_PER_SOURCE,
            seed=v5.DATA_SELECTION_SEED,
        )
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
    _validate_mode_contract(mode, train_rows, target_swap_rows)
    commitments = v5._prepared_partition_commitments(
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_reservation=news_reservation,
        disclosure_reservation=disclosure_reservation,
    )
    return PreparedAblation(
        mode=mode,
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_reservation=news_reservation,
        disclosure_reservation=disclosure_reservation,
        target_swap_rows=target_swap_rows,
        prepared_partition_commitments=commitments,
        public_audit=public_audit,
        news_silver_audit=news_silver_audit,
        disclosure_silver_audit=disclosure_silver_audit,
        final_overlap_audit=final_overlap_audit,
        raw_source_counts=raw_source_counts,
    )


def _validate_mode_contract(
    mode: AblationMode,
    train_rows: list[dict[str, Any]],
    target_swap_rows: list[dict[str, Any]],
) -> None:
    allowed = {
        AblationMode.NO_K: {"PUBLIC_TRAIN"},
        AblationMode.NEWS_ONLY: {
            "PUBLIC_TRAIN",
            "K_FNSPID_CODEX_GOLD",
            "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_RULE_SILVER",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
        },
        AblationMode.DISCLOSURE_ONLY: {
            "PUBLIC_TRAIN",
            "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_DISCLOSURE_RULE_SILVER",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
        },
        AblationMode.FULL: {
            "PUBLIC_TRAIN",
            "K_FNSPID_CODEX_GOLD",
            "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_RULE_SILVER",
            "K_FNSPID_DISCLOSURE_RULE_SILVER",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
        },
    }[mode]
    observed = {str(row.get("dataset", "")) for row in train_rows}
    if not observed or not observed <= allowed:
        raise RuntimeError(f"Ablation source contract violation: mode={mode}, sources={observed}")
    swap_sources = {str(row.get("source_type", "")).upper() for row in target_swap_rows}
    expected_swap_sources = {
        AblationMode.NO_K: set(),
        AblationMode.NEWS_ONLY: {"NEWS"},
        AblationMode.DISCLOSURE_ONLY: {"DISCLOSURE"},
        AblationMode.FULL: {"NEWS", "DISCLOSURE"},
    }[mode]
    if swap_sources != expected_swap_sources:
        raise RuntimeError(
            "Ablation target-swap contract violation: "
            f"mode={mode}, expected={expected_swap_sources}, actual={swap_sources}"
        )
    if mode is AblationMode.NO_K and any(
        str(row.get("dataset", "")).startswith("K_FNSPID") for row in train_rows
    ):
        raise RuntimeError("NO_K에 K-FNSPID 학습 행이 포함되었습니다.")


def _excluded_audit(path: Path, source_type: str, mode: AblationMode) -> dict[str, Any]:
    return {
        "path": _display_path(path),
        "sha256": v5._sha256(path),
        "source_type": source_type,
        "selected_count": 0,
        "status": "EXCLUDED_BY_ABLATION_MODE",
        "mode": mode.value,
    }


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def _artifact_records(paths: dict[str, Path]) -> dict[str, dict[str, int | str]]:
    return {name: v5._input_artifact_record(path) for name, path in sorted(paths.items())}


def _recipe_paths() -> dict[str, Path]:
    return {
        "ablation_runner": Path(__file__).resolve(),
        "candidate_trainer_v5": Path(v5.__file__).resolve(),
        "sentiment_input": PROJECT_ROOT / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_protocol": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py",
        "sentiment_sampling": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_sampling.py",
        "model_artifact_integrity": PROJECT_ROOT
        / "src/hannah_montana_ai/services/model_artifact_integrity.py",
        "pyproject": PROJECT_ROOT / "pyproject.toml",
        "uv_lock": PROJECT_ROOT / "uv.lock",
    }


def _assert_records_unchanged(
    expected: dict[str, dict[str, int | str]],
    paths: dict[str, Path],
    label: str,
) -> None:
    actual = _artifact_records(paths)
    if actual != expected:
        raise RuntimeError(f"{label} artifact changed during ablation execution.")


def _base_model_provenance() -> dict[str, Any]:
    return {
        "repository": v5.BASE_MODEL,
        "revision": v5.BASE_MODEL_REVISION,
        "source_weight_filename": v5.BASE_MODEL_WEIGHT_FILENAME,
        "source_weights_format": "pytorch_model.bin",
        "source_weight_sha256": v5.BASE_MODEL_WEIGHT_SHA256,
        "deserialization": "torch_weights_only",
        "trust_remote_code": False,
        "weights_only": True,
        "validation_stage": "EXPECTED_HASH_LOCK",
        "training_stage": "RESOLVED_CACHE_BYTES_VERIFIED_BEFORE_DESERIALIZATION",
    }


def _source_selection_provenance(prepared: PreparedAblation) -> dict[str, Any]:
    included = {
        AblationMode.NO_K: {"PUBLIC_TRAIN"},
        AblationMode.NEWS_ONLY: {
            "PUBLIC_TRAIN",
            "K_FNSPID_CODEX_GOLD",
            "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_RULE_SILVER",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS",
        },
        AblationMode.DISCLOSURE_ONLY: {
            "PUBLIC_TRAIN",
            "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_DISCLOSURE_RULE_SILVER",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE",
        },
        AblationMode.FULL: {
            "PUBLIC_TRAIN",
            "K_FNSPID_CODEX_GOLD",
            "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
            "K_FNSPID_RULE_SILVER",
            "K_FNSPID_DISCLOSURE_RULE_SILVER",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS",
            "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE",
        },
    }[prepared.mode]
    swap_counts = Counter(
        str(row.get("source_type", "")).upper() for row in prepared.target_swap_rows
    )
    counts = {
        **prepared.raw_source_counts,
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS": swap_counts.get("NEWS", 0),
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE": swap_counts.get("DISCLOSURE", 0),
    }
    artifact_names = {
        "PUBLIC_TRAIN": ["public_train"],
        "K_FNSPID_CODEX_GOLD": ["main_news_gold"],
        "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD": [
            "news_auxiliary_training_gold",
            "news_auxiliary_training_report",
        ],
        "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD": [
            "disclosure_auxiliary_training_gold",
            "disclosure_auxiliary_training_report",
        ],
        "K_FNSPID_RULE_SILVER": ["news_silver"],
        "K_FNSPID_DISCLOSURE_RULE_SILVER": ["disclosure_silver"],
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS": [
            "main_news_gold",
            "news_auxiliary_training_gold",
            "news_silver",
        ],
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE": [
            "disclosure_auxiliary_training_gold",
            "disclosure_silver",
        ],
    }
    return {
        name: {
            "decision": "INCLUDED" if name in included else "EXCLUDED",
            "pre_dedup_selected_count": count,
            "input_artifact_names": artifact_names[name],
            "derivation": (
                "DETERMINISTIC_ABSENT_TARGET_SWAP_V2"
                if "TARGET_SWAP" in name
                else "DIRECT_OR_DECONTAMINATED_INPUT"
            ),
        }
        for name, count in counts.items()
    }


def _validation_plan() -> dict[str, Any]:
    return {
        "schema_version": "k-fnspid-sentiment-ablation-validation-plan/v1",
        "fixed_model_seeds": list(MODEL_SEEDS),
        "primary_required": {
            "mode": AblationMode.NO_K.value,
            "required_seed_runs": list(MODEL_SEEDS),
            "comparison": "FULL canonical v5 candidate on the same prepared holdouts and seeds",
            "status": "MANDATORY_BEFORE_PAPER_COMPONENT_CLAIM",
        },
        "secondary_recommended": [
            {
                "mode": AblationMode.NEWS_ONLY.value,
                "recommended_seed_runs": list(MODEL_SEEDS),
            },
            {
                "mode": AblationMode.DISCLOSURE_ONLY.value,
                "recommended_seed_runs": list(MODEL_SEEDS),
            },
        ],
        "full_mode_role": "REPRODUCIBILITY_PARITY_WITH_CANONICAL_V5_PREPARATION",
        "selection_rule": (
            "checkpoint-only early stopping; calibration-only bias; selection-only report"
        ),
        "claim_limitations": [
            "개발 파티션 반복 노출 가능성이 있어 ablation 결과는 확증 성능 근거가 아니다.",
            (
                "학습원 제거는 데이터 양과 도메인을 함께 바꾸므로 개별 데이터 "
                "구성요소의 순수 인과효과로 해석할 수 없다."
            ),
            "봉인 reservation의 라벨과 공개 Test는 ablation 선택, 보정, 보고에 사용하지 않는다.",
        ],
    }


def _protocol_record(
    prepared: PreparedAblation,
    seed: int,
    inputs: dict[str, dict[str, int | str]],
    recipe: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "ablation_mode": prepared.mode.value,
        "seed": seed,
        "data_selection_seed": v5.DATA_SELECTION_SEED,
        "dataset_revision": v5.DATASET_REVISION,
        "public_dataset_revision": v5.PUBLIC_DATASET_REVISION,
        "public_test_opened": False,
        "base_model_provenance": _base_model_provenance(),
        "input_artifacts": inputs,
        "recipe_artifacts": recipe,
        "training_strategy": TRAINING_STRATEGY,
        "runtime_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": importlib.metadata.version("transformers"),
            "peft": importlib.metadata.version("peft"),
            "numpy": np.__version__,
            "mps_available": torch.backends.mps.is_available(),
            "cuda_available": torch.cuda.is_available(),
            "bitwise_deterministic_guaranteed": False,
        },
        "training_arguments": {
            "model_seed": seed,
            "data_selection_seed": v5.DATA_SELECTION_SEED,
            "max_length": MAX_LENGTH,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
            "learning_rate": LEARNING_RATE,
            "lr_scheduler_type": "cosine",
            "warmup_fraction": 0.08,
            "weight_decay": 0.01,
            "news_silver_per_label": NEWS_SILVER_PER_LABEL,
            "disclosure_silver_per_label": DISCLOSURE_SILVER_PER_LABEL,
            "target_swap_per_source": TARGET_SWAP_PER_SOURCE,
            "rdrop_alpha": v5.R_DROP_ALPHA,
            "early_stopping_patience": 1,
            "gradient_checkpointing": False,
        },
        "model_recipe": {
            "architecture": "KF-DeBERTa sequence classification",
            "lora_rank": 24,
            "lora_alpha": 48,
            "lora_dropout": 0.08,
            "lora_layers": list(v5.LORA_LAYERS),
            "lora_target_modules": ["query_proj", "key_proj", "value_proj", "dense"],
            "modules_to_save": ["pooler", "classifier"],
            "input_feature_version": "source-target-prefix-head-tail/v2",
            "loss": "effective-mass-class-balanced-focal-plus-hierarchical-boundary/v2",
            "rdrop_alpha": v5.R_DROP_ALPHA,
        },
        "partition_count": {
            "TRAIN": len(prepared.train_rows),
            "CHECKPOINT": len(prepared.checkpoint_rows),
            "CALIBRATION": len(prepared.calibration_rows),
            "SELECTION": len(prepared.selection_rows),
            "PUBLIC_TEST_NOT_LOADED": 0,
        },
        "training_source_distribution": dict(
            sorted(Counter(str(row["dataset"]) for row in prepared.train_rows).items())
        ),
        "training_source_type_distribution": dict(
            sorted(Counter(str(row["source_type"]) for row in prepared.train_rows).items())
        ),
        "training_label_distribution": v5._label_distribution(prepared.train_rows),
        "training_weight_audit": v5._training_weight_audit(prepared.train_rows),
        "target_swap_count": len(prepared.target_swap_rows),
        "target_swap_source_distribution": dict(
            sorted(
                Counter(
                    str(row.get("source_type", "")).upper() for row in prepared.target_swap_rows
                ).items()
            )
        ),
        "source_selection_provenance": _source_selection_provenance(prepared),
        "prepared_partition_commitments": prepared.prepared_partition_commitments,
        "model_seed_prepared_partition_commitments": {
            str(model_seed): prepared.prepared_partition_commitments for model_seed in MODEL_SEEDS
        },
        "seed_data_commitment_contract": (
            "All model seeds must have byte-identical prepared partition commitments."
        ),
        "public_partition_leakage_audit": prepared.public_audit,
        "news_silver_audit": prepared.news_silver_audit,
        "disclosure_silver_audit": prepared.disclosure_silver_audit,
        "final_group_overlap_purge": prepared.final_overlap_audit,
        "ablation_validation_plan": _validation_plan(),
        "causal_claim_status": "DESCRIPTIVE_COMPONENT_ABLATION_NOT_CAUSAL_IDENTIFICATION",
    }


def _train(
    prepared: PreparedAblation,
    *,
    seed: int,
    output_dir: Path,
    report_path: Path,
    inputs: dict[str, dict[str, int | str]],
    recipe: dict[str, dict[str, int | str]],
    paths: AblationPaths,
) -> dict[str, Any]:
    checkpoint_dir = output_dir.parent / f".{output_dir.name}-checkpoints"
    for label, path in (
        ("ablation artifact", output_dir),
        ("ablation report", report_path),
        ("ablation checkpoint", checkpoint_dir),
    ):
        if path.exists() or path.is_symlink():
            raise SystemExit(f"{label} output already exists: {path}")

    v5._verify_base_model_weights()
    tokenizer = AutoTokenizer.from_pretrained(
        v5.BASE_MODEL,
        revision=v5.BASE_MODEL_REVISION,
        trust_remote_code=False,
    )
    base = AutoModelForSequenceClassification.from_pretrained(
        v5.BASE_MODEL,
        revision=v5.BASE_MODEL_REVISION,
        num_labels=len(v5.LABEL_ORDER),
        id2label={index: label for index, label in enumerate(v5.LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(v5.LABEL_ORDER)},
        trust_remote_code=False,
        weights_only=True,
    )
    model = get_peft_model(
        base,
        LoraConfig(
            task_type=TaskType.SEQ_CLS,
            r=24,
            lora_alpha=48,
            lora_dropout=0.08,
            target_modules=["query_proj", "key_proj", "value_proj", "dense"],
            layers_to_transform=list(v5.LORA_LAYERS),
            layers_pattern="layer",
            modules_to_save=["pooler", "classifier"],
        ),
    )
    datasets = {
        "TRAIN": v5.EncodedSentimentDataset(prepared.train_rows, tokenizer, MAX_LENGTH),
        "CHECKPOINT": v5.EncodedSentimentDataset(
            prepared.checkpoint_rows,
            tokenizer,
            MAX_LENGTH,
        ),
        "CALIBRATION": v5.EncodedSentimentDataset(
            prepared.calibration_rows,
            tokenizer,
            MAX_LENGTH,
        ),
        "SELECTION": v5.EncodedSentimentDataset(
            prepared.selection_rows,
            tokenizer,
            MAX_LENGTH,
        ),
    }
    class_weights = v5._effective_number_weights(prepared.train_rows)
    optimizer_steps = max(
        1,
        round(len(prepared.train_rows) * EPOCHS / (BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS)),
    )
    trainer = v5.HierarchicalSentimentTrainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(checkpoint_dir),
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=max(4, BATCH_SIZE * 2),
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE,
            lr_scheduler_type="cosine",
            warmup_steps=max(1, round(optimizer_steps * 0.08)),
            weight_decay=0.01,
            gradient_checkpointing=False,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_steps=50,
            load_best_model_at_end=True,
            metric_for_best_model="macro_f1",
            greater_is_better=True,
            save_total_limit=2,
            seed=seed,
            data_seed=seed,
            report_to="none",
            dataloader_num_workers=0,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        ),
        train_dataset=datasets["TRAIN"],
        eval_dataset=datasets["CHECKPOINT"],
        data_collator=v5.WeightedSentimentCollator(tokenizer),
        processing_class=tokenizer,
        compute_metrics=v5._metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
        class_weights=class_weights,
        rdrop_alpha=v5.R_DROP_ALPHA,
    )
    train_result = trainer.train()
    trainer.remove_callback(EarlyStoppingCallback)
    calibration_output = trainer.predict(datasets["CALIBRATION"])
    calibration_logits = v5._prediction_logits(calibration_output)
    logit_bias_by_domain = v5._fit_logit_bias_by_domain(
        calibration_logits,
        prepared.calibration_rows,
    )
    uncalibrated_metrics = v5._metrics(
        EvalPrediction(
            predictions=calibration_logits,
            label_ids=np.asarray(calibration_output.label_ids),
        )
    )
    calibration_metrics = v5._evaluate_partition(
        trainer,
        datasets["CALIBRATION"],
        prepared.calibration_rows,
        logit_bias_by_domain,
        "calibration",
    )
    selection_metrics = v5._evaluate_partition(
        trainer,
        datasets["SELECTION"],
        prepared.selection_rows,
        logit_bias_by_domain,
        "selection",
    )
    selection_breakdown = v5._evaluate_breakdown(
        trainer,
        prepared.selection_rows,
        tokenizer,
        MAX_LENGTH,
        logit_bias_by_domain,
    )

    _assert_records_unchanged(inputs, input_paths(paths), "input")
    _assert_records_unchanged(recipe, _recipe_paths(), "recipe")
    output_dir.mkdir(parents=True, exist_ok=False)
    trained_model: Any = trainer.model
    trained_model.save_pretrained(output_dir, safe_serialization=True)
    tokenizer.save_pretrained(output_dir)
    artifact_files = build_artifact_manifest(
        output_dir,
        (
            "adapter_config.json",
            "adapter_model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
        ),
    )
    trained_at = datetime.now(UTC).isoformat()
    version = (
        "hana-montana-kf-deberta-k-fnspid-sentiment-ablation-"
        f"{prepared.mode.value.lower()}-seed{seed}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    )
    metadata = {
        "schema_version": "kf-deberta-sentiment-ablation-artifact/v1",
        "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
        "version": version,
        "ablation_mode": prepared.mode.value,
        "seed": seed,
        "base_model": v5.BASE_MODEL,
        "base_model_revision": v5.BASE_MODEL_REVISION,
        "label_order": v5.LABEL_ORDER,
        "max_length": MAX_LENGTH,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "logit_bias_by_domain": logit_bias_by_domain,
        "trained_at": trained_at,
        "artifact_files": artifact_files,
        "artifact_directory": _display_path(output_dir),
    }
    with (output_dir / "hannah_metadata.json").open("x", encoding="utf-8") as file:
        file.write(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")

    report = {
        **_protocol_record(prepared, seed, inputs, recipe),
        **metadata,
        "schema_version": SCHEMA_VERSION,
        "class_weights": class_weights.tolist(),
        "calibration": calibration_metrics,
        "decision_calibration": {
            "method": "validation-only-domain-logit-offset-grid/v1",
            "fit_partition": "CALIBRATION_ONLY",
            "selection_used_for_fit": False,
            "public_test_used_for_fit": False,
            "sealed_gold_used_for_fit": False,
            "uncalibrated_metrics": uncalibrated_metrics,
            "logit_bias_by_domain": logit_bias_by_domain,
        },
        "selection": selection_metrics,
        "selection_breakdown": selection_breakdown,
        "selection_score": v5._selection_score(selection_breakdown),
        "training_runtime": v5._trainer_runtime_record(trainer, train_result),
        "test": {"sample_count": 0, "status": "NOT_AVAILABLE_TO_ABLATION_RUNNER"},
        "trainable_parameter_count": v5._parameter_counts(trained_model)[0],
        "total_parameter_count": v5._parameter_counts(trained_model)[1],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("x", encoding="utf-8") as file:
        file.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def _mode_slug(mode: AblationMode) -> str:
    return mode.value.lower().replace("_", "-")


def aggregate_no_k_runs(
    *,
    report_dir: Path,
    artifact_root: Path,
    selection_report_path: Path,
    winner_manifest_path: Path,
    validate_only: bool,
) -> dict[str, Any]:
    report_paths = {
        seed: report_dir / f"kf-deberta-sentiment-no-k-seed{seed}.json" for seed in MODEL_SEEDS
    }
    reports: dict[int, dict[str, Any]] = {}
    for seed, path in report_paths.items():
        v5._require_regular_input(path, f"NO_K seed{seed} report")
        report = v5._read_json_object(path, f"NO_K seed{seed} report")
        _validate_no_k_candidate_report(
            report,
            seed=seed,
            artifact_dir=artifact_root / f"seed{seed}",
        )
        reports[seed] = report
    _validate_no_k_cross_seed_contract(reports)

    ranked = sorted(
        reports.items(),
        key=lambda item: (-float(item[1]["selection_score"]), item[0]),
    )
    selected_seed, selected_report = ranked[0]
    selected_artifact_dir = artifact_root / f"seed{selected_seed}"
    selected_report_record = v5._input_artifact_record(report_paths[selected_seed])
    winner_manifest = {
        "schema_version": WINNER_MANIFEST_SCHEMA_VERSION,
        "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
        "ablation_mode": AblationMode.NO_K.value,
        "selected_seed": selected_seed,
        "selection_score": float(selected_report["selection_score"]),
        "selection_rule": "highest fixed development selection score; lower seed breaks ties",
        "selected_training_report": selected_report_record,
        "artifact_directory": _display_path(selected_artifact_dir),
        "artifact_files": _full_directory_manifest(selected_artifact_dir),
        "base_model_provenance": selected_report["base_model_provenance"],
        "prepared_partition_commitments": selected_report["prepared_partition_commitments"],
        "confirmatory_or_public_test_used": False,
        "deployment_eligible": False,
    }
    winner_bytes = _json_document_bytes(winner_manifest)
    winner_record = {
        "path": _display_path(winner_manifest_path),
        "bytes": len(winner_bytes),
        "sha256": sha256(winner_bytes).hexdigest(),
    }
    selection_report = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "artifact_role": "PAPER_ABLATION_EVIDENCE_NOT_DEPLOYMENT_SELECTION",
        "ablation_mode": AblationMode.NO_K.value,
        "required_seed_runs": list(MODEL_SEEDS),
        "candidate_reports": {
            str(seed): v5._input_artifact_record(path)
            for seed, path in sorted(report_paths.items())
        },
        "ranking": [
            {
                "rank": index,
                "seed": seed,
                "selection_score": float(report["selection_score"]),
            }
            for index, (seed, report) in enumerate(ranked, start=1)
        ],
        "selection_rule": {
            "metric": "minimum macro-F1 across fixed development selection domains",
            "direction": "MAXIMIZE",
            "tie_break": "LOWEST_FIXED_SEED",
            "checkpoint_partition_used_for_early_stopping": True,
            "calibration_partition_used_for_logit_bias_only": True,
            "selection_partition_used_for_ranking_only": True,
            "confirmatory_or_public_test_used": False,
        },
        "winner": {
            "seed": selected_seed,
            "selection_score": float(selected_report["selection_score"]),
            "training_report": selected_report_record,
            "artifact_directory": _display_path(selected_artifact_dir),
        },
        "winner_artifact_manifest": winner_record,
        "prepared_partition_commitments": selected_report["prepared_partition_commitments"],
        "model_seed_prepared_partition_commitments": selected_report[
            "model_seed_prepared_partition_commitments"
        ],
        "claim_status": "DESCRIPTIVE_COMPONENT_ABLATION_NOT_CAUSAL_IDENTIFICATION",
        "deployment_eligible": False,
    }
    if validate_only:
        return {
            "status": "NO_K_AGGREGATION_VALIDATED_WITHOUT_WRITE",
            "planned_winner_manifest": winner_manifest,
            "planned_selection_report": selection_report,
        }
    for label, path in (
        ("winner manifest", winner_manifest_path),
        ("selection report", selection_report_path),
    ):
        if path.exists() or path.is_symlink():
            raise SystemExit(f"NO_K {label} output already exists: {path}")
    winner_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with winner_manifest_path.open("xb") as file:
        file.write(winner_bytes)
    if v5._input_artifact_record(winner_manifest_path) != winner_record:
        raise RuntimeError("NO_K winner manifest write verification failed.")
    selection_report_path.parent.mkdir(parents=True, exist_ok=True)
    with selection_report_path.open("xb") as file:
        file.write(_json_document_bytes(selection_report))
    return {
        "status": "NO_K_AGGREGATION_WRITTEN",
        "selection_report": v5._input_artifact_record(selection_report_path),
        "winner_artifact_manifest": v5._input_artifact_record(winner_manifest_path),
        "selected_seed": selected_seed,
    }


def _validate_no_k_candidate_report(
    report: dict[str, Any],
    *,
    seed: int,
    artifact_dir: Path,
) -> None:
    selection_score = report.get("selection_score")
    artifact_files = report.get("artifact_files")
    test_record = report.get("test")
    seed_commitments = report.get("model_seed_prepared_partition_commitments")
    partition_count = report.get("partition_count")
    source_provenance = report.get("source_selection_provenance")
    decision_calibration = report.get("decision_calibration")
    expected_sources = {
        "PUBLIC_TRAIN",
        "K_FNSPID_CODEX_GOLD",
        "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_RULE_SILVER",
        "K_FNSPID_DISCLOSURE_RULE_SILVER",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE",
    }
    required_nonempty_mappings = (
        report.get("base_model_provenance"),
        report.get("input_artifacts"),
        report.get("recipe_artifacts"),
        report.get("training_arguments"),
        report.get("model_recipe"),
        report.get("prepared_partition_commitments"),
        report.get("training_label_distribution"),
        report.get("selection_breakdown"),
    )
    if (
        report.get("schema_version") != SCHEMA_VERSION
        or report.get("artifact_role") != "RESEARCH_ABLATION_NOT_DEPLOYABLE"
        or report.get("ablation_mode") != AblationMode.NO_K.value
        or report.get("seed") != seed
        or report.get("training_strategy") != TRAINING_STRATEGY
        or isinstance(selection_score, bool)
        or not isinstance(selection_score, int | float)
        or not math.isfinite(float(selection_score))
        or not 0.0 <= float(selection_score) <= 1.0
        or not isinstance(artifact_files, dict)
        or not artifact_files
        or not isinstance(test_record, dict)
        or test_record.get("sample_count") != 0
        or not isinstance(seed_commitments, dict)
        or set(seed_commitments) != {str(value) for value in MODEL_SEEDS}
        or any(
            value != report.get("prepared_partition_commitments")
            for value in seed_commitments.values()
        )
        or any(not isinstance(value, dict) or not value for value in required_nonempty_mappings)
        or report.get("public_test_opened") is not False
        or report.get("training_source_distribution") != {"PUBLIC_TRAIN": 7413}
        or report.get("target_swap_count") != 0
        or report.get("target_swap_source_distribution") != {}
        or not isinstance(partition_count, dict)
        or partition_count.get("PUBLIC_TEST_NOT_LOADED") != 0
        or not isinstance(source_provenance, dict)
        or set(source_provenance) != expected_sources
        or any(not isinstance(details, dict) for details in source_provenance.values())
        or source_provenance.get("PUBLIC_TRAIN", {}).get("decision") != "INCLUDED"
        or any(
            details.get("decision") != "EXCLUDED" or details.get("pre_dedup_selected_count") != 0
            for name, details in source_provenance.items()
            if name != "PUBLIC_TRAIN" and isinstance(details, dict)
        )
        or not isinstance(decision_calibration, dict)
        or decision_calibration.get("sealed_gold_used_for_fit") is not False
        or report.get("causal_claim_status")
        != "DESCRIPTIVE_COMPONENT_ABLATION_NOT_CAUSAL_IDENTIFICATION"
    ):
        raise SystemExit(f"NO_K seed{seed} report contract violation.")
    if report.get("artifact_directory") != _display_path(artifact_dir):
        raise SystemExit(f"NO_K seed{seed} artifact path mismatch.")
    if artifact_dir.is_symlink() or not artifact_dir.is_dir():
        raise SystemExit(f"NO_K seed{seed} artifact directory is invalid.")
    if not verify_artifact_manifest(artifact_dir, artifact_files):
        raise SystemExit(f"NO_K seed{seed} artifact manifest mismatch.")
    metadata = v5._read_json_object(
        artifact_dir / "hannah_metadata.json",
        f"NO_K seed{seed} artifact metadata",
    )
    if (
        metadata.get("schema_version") != "kf-deberta-sentiment-ablation-artifact/v1"
        or metadata.get("artifact_role") != "RESEARCH_ABLATION_NOT_DEPLOYABLE"
        or metadata.get("ablation_mode") != AblationMode.NO_K.value
        or metadata.get("seed") != seed
        or metadata.get("artifact_files") != artifact_files
        or metadata.get("artifact_directory") != _display_path(artifact_dir)
    ):
        raise SystemExit(f"NO_K seed{seed} artifact metadata mismatch.")
    expected_score = v5._selection_score(report.get("selection_breakdown", {}))
    if not math.isclose(float(selection_score), expected_score, rel_tol=0.0, abs_tol=1e-12):
        raise SystemExit(f"NO_K seed{seed} selection score mismatch.")


def _validate_no_k_cross_seed_contract(reports: dict[int, dict[str, Any]]) -> None:
    if set(reports) != set(MODEL_SEEDS):
        raise SystemExit("NO_K aggregate requires exactly seeds 17, 42, and 73.")
    first = reports[MODEL_SEEDS[0]]
    invariant_fields = (
        "dataset_revision",
        "public_dataset_revision",
        "base_model_provenance",
        "input_artifacts",
        "recipe_artifacts",
        "model_recipe",
        "partition_count",
        "training_source_distribution",
        "training_source_type_distribution",
        "training_label_distribution",
        "training_weight_audit",
        "target_swap_count",
        "target_swap_source_distribution",
        "source_selection_provenance",
        "prepared_partition_commitments",
        "model_seed_prepared_partition_commitments",
    )
    first_arguments = dict(first.get("training_arguments", {}))
    first_arguments.pop("model_seed", None)
    for seed in MODEL_SEEDS[1:]:
        current = reports[seed]
        if any(current.get(field) != first.get(field) for field in invariant_fields):
            raise SystemExit(f"NO_K seed{seed} cross-seed recipe or data mismatch.")
        current_arguments = dict(current.get("training_arguments", {}))
        current_arguments.pop("model_seed", None)
        if current_arguments != first_arguments:
            raise SystemExit(f"NO_K seed{seed} training argument mismatch.")


def _full_directory_manifest(directory: Path) -> dict[str, dict[str, int | str]]:
    if directory.is_symlink() or not directory.is_dir():
        raise SystemExit(f"Ablation artifact directory is invalid: {directory}")
    files: dict[str, dict[str, int | str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"Ablation artifact contains a symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(directory).as_posix()
        files[relative] = {"bytes": path.stat().st_size, "sha256": v5._sha256(path)}
    if "hannah_metadata.json" not in files or not files:
        raise SystemExit("Ablation artifact full manifest is incomplete.")
    return files


def _json_document_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="K-FNSPID 감성 학습 데이터 구성요소의 고정-recipe ablation을 실행한다."
    )
    parser.add_argument("--mode", type=AblationMode, choices=list(AblationMode))
    parser.add_argument("--aggregate-no-k", action="store_true")
    parser.add_argument("--seed", type=int, choices=MODEL_SEEDS, default=42)
    parser.add_argument("--dataset-dir", type=Path, default=v5.DEFAULT_DATASET)
    parser.add_argument("--silver-path", type=Path, default=v5.DEFAULT_SILVER)
    parser.add_argument(
        "--disclosure-silver-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_SILVER,
    )
    parser.add_argument("--train-gold-path", type=Path, default=v5.DEFAULT_TRAIN_GOLD)
    parser.add_argument(
        "--news-auxiliary-gold-path",
        type=Path,
        default=v5.DEFAULT_NEWS_AUXILIARY_GOLD,
    )
    parser.add_argument(
        "--disclosure-auxiliary-gold-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_AUXILIARY_GOLD,
    )
    parser.add_argument(
        "--news-auxiliary-report-path",
        type=Path,
        default=v5.DEFAULT_NEWS_AUXILIARY_REPORT,
    )
    parser.add_argument(
        "--disclosure-auxiliary-report-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_AUXILIARY_REPORT,
    )
    parser.add_argument(
        "--development-gold-path",
        type=Path,
        default=v5.DEFAULT_DEVELOPMENT_GOLD,
    )
    parser.add_argument(
        "--disclosure-development-gold-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD,
    )
    parser.add_argument(
        "--news-sealed-review-path",
        type=Path,
        default=v5.DEFAULT_NEWS_SEALED_REVIEW,
    )
    parser.add_argument(
        "--disclosure-sealed-review-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_SEALED_REVIEW,
    )
    parser.add_argument(
        "--sampling-design-report",
        type=Path,
        default=v5.DEFAULT_SAMPLING_DESIGN_REPORT,
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--report-path", type=Path)
    parser.add_argument(
        "--ablation-report-dir",
        type=Path,
        default=PROJECT_ROOT / "reports/ablations",
    )
    parser.add_argument(
        "--ablation-artifact-root",
        type=Path,
        default=PROJECT_ROOT / "artifacts/sentiment/ablations/no-k",
    )
    parser.add_argument(
        "--selection-report-path",
        type=Path,
        default=PROJECT_ROOT / "reports/ablations/kf-deberta-sentiment-no-k-selection.json",
    )
    parser.add_argument(
        "--winner-manifest-path",
        type=Path,
        default=PROJECT_ROOT
        / "artifacts/sentiment/ablations/no-k/selection/winner-artifact-manifest.json",
    )
    parser.add_argument("--validate-only", action="store_true")
    return parser


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.aggregate_no_k:
        if args.mode is not None:
            parser.error("--aggregate-no-k cannot be combined with --mode.")
        result = aggregate_no_k_runs(
            report_dir=args.ablation_report_dir,
            artifact_root=args.ablation_artifact_root,
            selection_report_path=args.selection_report_path,
            winner_manifest_path=args.winner_manifest_path,
            validate_only=args.validate_only,
        )
        print(json.dumps(result, ensure_ascii=False))
        return
    if args.mode is None:
        parser.error("--mode is required unless --aggregate-no-k is selected.")
    mode = AblationMode(args.mode)
    paths = AblationPaths(
        dataset_dir=args.dataset_dir,
        news_silver=args.silver_path,
        disclosure_silver=args.disclosure_silver_path,
        main_news_gold=args.train_gold_path,
        news_auxiliary_gold=args.news_auxiliary_gold_path,
        disclosure_auxiliary_gold=args.disclosure_auxiliary_gold_path,
        news_auxiliary_report=args.news_auxiliary_report_path,
        disclosure_auxiliary_report=args.disclosure_auxiliary_report_path,
        news_development_gold=args.development_gold_path,
        disclosure_development_gold=args.disclosure_development_gold_path,
        news_reservation=args.news_sealed_review_path,
        disclosure_reservation=args.disclosure_sealed_review_path,
        sampling_design=args.sampling_design_report,
    )
    v5._set_seed(args.seed)
    all_input_paths = input_paths(paths)
    input_records = _artifact_records(all_input_paths)
    recipe_paths = _recipe_paths()
    recipe_records = _artifact_records(recipe_paths)
    prepared = prepare_ablation_data(mode, paths)
    _assert_records_unchanged(input_records, all_input_paths, "input")
    _assert_records_unchanged(recipe_records, recipe_paths, "recipe")
    protocol = _protocol_record(prepared, args.seed, input_records, recipe_records)
    if args.validate_only:
        print(
            json.dumps(
                {"status": "VALIDATED_WITHOUT_TRAINING", **protocol},
                ensure_ascii=False,
            )
        )
        return

    output_dir = args.output_dir or (
        PROJECT_ROOT / "artifacts/sentiment/ablations" / _mode_slug(mode) / f"seed{args.seed}"
    )
    report_path = args.report_path or (
        PROJECT_ROOT
        / "reports/ablations"
        / f"kf-deberta-sentiment-{_mode_slug(mode)}-seed{args.seed}.json"
    )
    report = _train(
        prepared,
        seed=args.seed,
        output_dir=output_dir,
        report_path=report_path,
        inputs=input_records,
        recipe=recipe_records,
        paths=paths,
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
