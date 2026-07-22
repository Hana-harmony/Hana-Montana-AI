from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import shutil
import sys
import time
import uuid
from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from huggingface_hub import hf_hub_download
from safetensors.torch import save_file
from torch import nn
from transformers import AutoModel, AutoTokenizer

try:
    from scripts import train_kf_deberta_sentiment_v6 as v6
except ImportError:  # pragma: no cover - scripts/ 직접 실행 경로
    v6_name = "train_kf_deberta_sentiment_v6"
    v6_module = sys.modules.get(v6_name)
    if v6_module is None:
        v6_spec = importlib.util.spec_from_file_location(
            v6_name,
            Path(__file__).with_name("train_kf_deberta_sentiment_v6.py"),
        )
        if v6_spec is None or v6_spec.loader is None:
            raise RuntimeError("v6 후보 학습 계약을 load할 수 없습니다.") from None
        v6_module = importlib.util.module_from_spec(v6_spec)
        sys.modules[v6_name] = v6_module
        v6_spec.loader.exec_module(v6_module)
    v6 = cast(Any, v6_module)

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
            raise RuntimeError("v5 데이터 계약을 load할 수 없습니다.") from None
        v5_module = importlib.util.module_from_spec(v5_spec)
        sys.modules[v5_name] = v5_module
        v5_spec.loader.exec_module(v5_module)
    v5 = cast(Any, v5_module)

from hannah_montana_ai.services.kr_finbert_sc_v6_baseline import (
    ARTIFACT_SCHEMA_VERSION,
    BASE_MODEL,
    BASE_MODEL_FILES_SHA256,
    BASE_MODEL_REVISION,
    MANIFEST_SCHEMA_VERSION,
    MODEL_FAMILY,
    RUNTIME_SCHEMA_VERSION,
    load_kr_finbert_sc_v6_runtime,
    validate_kr_finbert_sc_v6_artifact,
)
from hannah_montana_ai.services.sentiment_input import encode_sentiment_input
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    ANCHOR_DOMAIN,
    DOMAIN_ORDER,
    DOMAIN_TO_ID,
    HEAD_ARCHITECTURE_VERSION,
    HEAD_ARTIFACT_FILENAME,
    INPUT_FEATURE_VERSION,
    LABEL_ORDER,
    RESIDUAL_DOMAINS,
    build_source_hierarchical_classifier,
    calibrated_sentiment_prediction,
    source_hierarchical_head_state_dict,
    validate_domain_calibration,
)
from hannah_montana_ai.training.sentiment_v6_baseline_commitment import (
    BASELINE_MODEL_NAME,
    SELECTION_SCHEMA_VERSION,
    build_v6_kr_finbert_sc_baseline_commitment,
    canonical_json_sha256,
    validate_v6_kr_finbert_sc_baseline_commitment,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_SEEDS = (17, 42, 73)
TRAINING_SCHEMA_VERSION = "k-fnspid-v6-fair-shared-residual-baseline-training/v2"
VALIDATION_SCHEMA_VERSION = "kr-finbert-sc-shared-residual-sentiment-validation/v2"
WINNER_SCHEMA_VERSION = "kr-finbert-sc-shared-residual-fair-baseline-winner/v2"
EXECUTION_SNAPSHOT_SCHEMA_VERSION = "kr-finbert-sc-v6-training-execution-snapshot/v2"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "artifacts/sentiment/fair_baselines/kr-finbert-sc-v6"
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "reports/fair_baselines/kr-finbert-sc-v6"

# 후보와 데이터·단계·update 규칙은 같고 전체 encoder에 맞춘 LR만 다르다.
MAX_LENGTH = 256
STAGE1_EPOCHS = 2
STAGE2_EPOCHS = 4
BATCH_SIZE = 8
EVAL_BATCH_SIZE = 16
GRADIENT_ACCUMULATION_STEPS = 2
STAGE1_LEARNING_RATE = 2e-5
STAGE2_LEARNING_RATE = 4e-4
CANDIDATE_STAGE1_LEARNING_RATE = 8e-5
WEIGHT_DECAY = 0.01
R_DROP_ALPHA = v6.R_DROP_ALPHA
RUNTIME_PARITY_LOGIT_ATOL = 1e-6
RUNTIME_PARITY_PROBABILITY_ATOL = 1e-7


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "v6와 동일 데이터·source 계층 과제로 KR-FinBERT-SC 전체 fine-tune 기준선을 학습한다."
        )
    )
    value.add_argument("--dataset-dir", type=Path, default=v5.DEFAULT_DATASET)
    value.add_argument("--silver-path", type=Path, default=v5.DEFAULT_SILVER)
    value.add_argument("--disclosure-silver-path", type=Path, default=v5.DEFAULT_DISCLOSURE_SILVER)
    value.add_argument("--train-gold-path", type=Path, default=v5.DEFAULT_TRAIN_GOLD)
    value.add_argument(
        "--news-auxiliary-gold-path",
        type=Path,
        default=v5.DEFAULT_NEWS_AUXILIARY_GOLD,
    )
    value.add_argument(
        "--disclosure-auxiliary-gold-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_AUXILIARY_GOLD,
    )
    value.add_argument(
        "--news-auxiliary-report-path",
        type=Path,
        default=v5.DEFAULT_NEWS_AUXILIARY_REPORT,
    )
    value.add_argument(
        "--disclosure-auxiliary-report-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_AUXILIARY_REPORT,
    )
    value.add_argument(
        "--development-gold-path",
        type=Path,
        default=v5.DEFAULT_DEVELOPMENT_GOLD,
    )
    value.add_argument(
        "--disclosure-development-gold-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD,
    )
    value.add_argument(
        "--news-sealed-review-path",
        type=Path,
        default=v5.DEFAULT_NEWS_SEALED_REVIEW,
    )
    value.add_argument(
        "--disclosure-sealed-review-path",
        type=Path,
        default=v5.DEFAULT_DISCLOSURE_SEALED_REVIEW,
    )
    value.add_argument(
        "--sampling-design-report",
        type=Path,
        default=v5.DEFAULT_SAMPLING_DESIGN_REPORT,
    )
    # 후보와 동일한 Gold 이중 검수 provenance를 입력 계약에 포함한다.
    v6.add_gold_provenance_arguments(value)
    value.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    value.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    value.add_argument("--checkpoint-root", type=Path)
    value.add_argument("--seed", type=int, choices=MODEL_SEEDS, default=17)
    value.add_argument("--device", choices=("auto", "cuda", "mps", "cpu"), default="auto")
    value.add_argument("--gradient-checkpointing", action="store_true")
    value.add_argument("--validate-only", action="store_true")
    value.add_argument("--aggregate-only", action="store_true")
    return value


def validate_arguments(args: argparse.Namespace) -> None:
    if args.validate_only and args.aggregate_only:
        raise SystemExit("validate-only와 aggregate-only는 함께 사용할 수 없습니다.")
    if args.output_root.resolve() == args.report_root.resolve():
        raise SystemExit("artifact와 report 출력 root는 분리해야 합니다.")


def _seed_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    return (
        args.output_root / f"seed{args.seed}",
        args.report_root / f"seed{args.seed}.json",
    )


def _preflight_seed_outputs(output_dir: Path, report_path: Path) -> None:
    for description, path in (("artifact", output_dir), ("report", report_path)):
        if path.exists() or path.is_symlink():
            raise SystemExit(f"{description} 출력은 write-once이며 이미 존재합니다: {path}")


def recipe_contract() -> dict[str, Any]:
    return {
        "schema_version": "kr-finbert-sc-shared-residual-fair-recipe/v2",
        "baseline_model_name": BASELINE_MODEL_NAME,
        "encoder": {
            "repository": BASE_MODEL,
            "revision": BASE_MODEL_REVISION,
            "source_files_sha256": BASE_MODEL_FILES_SHA256,
            "fine_tuning": "FULL_ENCODER",
            "upstream_sequence_classifier_head": "DISCARDED",
            "safe_source_weights": "model.safetensors",
        },
        "data": {
            "builder": "scripts.train_kf_deberta_sentiment_v6.prepare_partitions",
            "data_selection_seed": v5.DATA_SELECTION_SEED,
            "expected_full_commitments": v6.EXPECTED_FULL_COMMITMENTS,
            "public_test_opened": False,
            "confirmatory_labels_opened": False,
        },
        "model_seeds": list(MODEL_SEEDS),
        "task": {
            "input_feature_version": INPUT_FEATURE_VERSION,
            "source_domains": list(DOMAIN_ORDER),
            "label_order": list(LABEL_ORDER),
            "head_architecture": {
                "version": HEAD_ARCHITECTURE_VERSION,
                "anchor_domain": ANCHOR_DOMAIN,
                "residual_domains": list(RESIDUAL_DOMAINS),
                "residual_initialization": "EXACT_ZERO",
            },
            "heads": ["neutral_vs_directional", "negative_vs_positive"],
            "composition": "normalized-hierarchical-log-probabilities/v1",
            "loss": v6.LOSS_CONTRACT_VERSION,
            "calibration": ("calibration-only-sequential-temperature-neutral-threshold-shrunk/v1"),
            "selection_primary": "weakest-source-domain-macro-f1",
            "selection_secondary": "overall-macro-f1",
        },
        "schedule": {
            "stage1_epochs": STAGE1_EPOCHS,
            "stage2_epochs": STAGE2_EPOCHS,
            "batch_size": BATCH_SIZE,
            "eval_batch_size": EVAL_BATCH_SIZE,
            "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
            "optimizer": "AdamW",
            "scheduler": "cosine-with-8pct-warmup",
            "gradient_clip_norm": 1.0,
            "checkpoint_rule": "fixed-full-epoch; best-in-stage-checkpoint-selected",
            "stage2_scope": "SOURCE_HEADS_ONLY_GOLD_REFINEMENT",
            "rdrop_alpha": R_DROP_ALPHA,
            "weight_decay": WEIGHT_DECAY,
        },
        "architecture_specific_optimization": {
            "baseline_stage1_learning_rate": STAGE1_LEARNING_RATE,
            "candidate_lora_stage1_learning_rate": CANDIDATE_STAGE1_LEARNING_RATE,
            "shared_stage2_head_learning_rate": STAGE2_LEARNING_RATE,
            "reason": "전체 encoder fine-tune 안정성을 위한 사전 명시 LR 차이",
        },
        "shared_implementation": {
            "dataset": "DomainEncodedDataset",
            "collator": "DomainCollator",
            "training_loop": "train_stage",
            "loss": "hierarchical_calibrated_loss",
            "rdrop": "hierarchical_rdrop_consistency",
            "calibration": "fit_calibration",
            "metrics": "metrics_by_domain",
        },
    }


def recipe_commitment_sha256() -> str:
    return canonical_json_sha256(recipe_contract())


def candidate_matching_contract(
    *,
    prepared_partition_commitments: dict[str, Any],
    input_artifacts: dict[str, Any],
    stage1_optimizer_steps: int,
    stage2_optimizer_steps: int,
    stage1_planned_optimizer_steps: int,
    stage2_planned_optimizer_steps: int,
    gradient_checkpointing: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "kr-finbert-sc-v6-candidate-matching-contract/v1",
        "candidate_trainer": "scripts/train_kf_deberta_sentiment_v6.py",
        "prepared_partition_commitments": prepared_partition_commitments,
        "input_artifacts_sha256": canonical_json_sha256(input_artifacts),
        "configured_schedule": {
            "stage1_epochs": STAGE1_EPOCHS,
            "stage2_epochs": STAGE2_EPOCHS,
            "batch_size": BATCH_SIZE,
            "eval_batch_size": EVAL_BATCH_SIZE,
            "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
            "gradient_checkpointing": gradient_checkpointing,
            "optimizer": "AdamW",
            "scheduler": "cosine-with-8pct-warmup",
            "checkpoint_and_stopping_rule": ("fixed-full-epoch; best-in-stage-checkpoint-selected"),
        },
        "planned_optimizer_steps": {
            "stage1": stage1_planned_optimizer_steps,
            "stage2": stage2_planned_optimizer_steps,
            "total": stage1_planned_optimizer_steps + stage2_planned_optimizer_steps,
        },
        "executed_optimizer_steps": {
            "stage1": stage1_optimizer_steps,
            "stage2": stage2_optimizer_steps,
            "total": stage1_optimizer_steps + stage2_optimizer_steps,
        },
        "matching_semantics": {
            "same_raw_source_rows": True,
            "same_group_disjoint_partitions": True,
            "same_data_selection_seed": True,
            "same_model_seed_set": True,
            "same_target_aware_input": True,
            "same_source_hierarchical_task_loss_calibration_selection": True,
            "same_schedule_implementation_and_configured_rule": True,
            "planned_equals_executed_optimizer_steps": True,
        },
    }


def expected_optimizer_steps(row_count: int, epochs: int) -> int:
    if (
        isinstance(row_count, bool)
        or not isinstance(row_count, int)
        or isinstance(epochs, bool)
        or not isinstance(epochs, int)
        or row_count < 1
        or epochs < 1
    ):
        raise ValueError("optimizer step 계산 입력은 양수여야 합니다.")
    batches_per_epoch = math.ceil(row_count / BATCH_SIZE)
    return math.ceil(batches_per_epoch / GRADIENT_ACCUMULATION_STEPS) * epochs


def build_model(*, gradient_checkpointing: bool) -> nn.Module:
    encoder = AutoModel.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        trust_remote_code=False,
        local_files_only=False,
        use_safetensors=True,
        weights_only=True,
    )
    for parameter in encoder.parameters():
        parameter.requires_grad = True
    if gradient_checkpointing:
        encoder.gradient_checkpointing_enable()
        if hasattr(encoder.config, "use_cache"):
            encoder.config.use_cache = False
    hidden_size = int(cast(Any, encoder.config).hidden_size)
    return cast(nn.Module, build_source_hierarchical_classifier(encoder, hidden_size))


def _training_code_paths() -> dict[str, Path]:
    return {
        "baseline_trainer": Path(__file__).resolve(),
        "candidate_v6_trainer": PROJECT_ROOT / "scripts/train_kf_deberta_sentiment_v6.py",
        "v5_data_contract": PROJECT_ROOT / "scripts/train_kf_deberta_sentiment_v2.py",
        "sentiment_input": PROJECT_ROOT / "src/hannah_montana_ai/services/sentiment_input.py",
        "source_hierarchical_runtime": PROJECT_ROOT
        / "src/hannah_montana_ai/services/source_hierarchical_sentiment.py",
        "baseline_runtime": PROJECT_ROOT
        / "src/hannah_montana_ai/services/kr_finbert_sc_v6_baseline.py",
        "baseline_commitment": PROJECT_ROOT
        / "src/hannah_montana_ai/training/sentiment_v6_baseline_commitment.py",
        "sentiment_protocol": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py",
    }


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _regular_file_record(path: Path, root: Path | None = None) -> dict[str, int | str]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise RuntimeError(f"일반 파일만 허용합니다: {path}")
    display = str(resolved)
    if root is not None:
        display = resolved.relative_to(root.resolve(strict=True)).as_posix()
    return {
        "path": display,
        "bytes": resolved.stat().st_size,
        "sha256": _sha256_file(resolved),
    }


def pinned_base_snapshot() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for filename, expected_sha256 in sorted(BASE_MODEL_FILES_SHA256.items()):
        cached = Path(
            hf_hub_download(
                repo_id=BASE_MODEL,
                filename=filename,
                revision=BASE_MODEL_REVISION,
            )
        ).resolve(strict=True)
        if not cached.is_file() or _sha256_file(cached) != expected_sha256:
            raise RuntimeError(f"고정 KR-FinBERT-SC base/tokenizer hash가 다릅니다: {filename}")
        records[filename] = {
            **_regular_file_record(cached),
            "repository": BASE_MODEL,
            "revision": BASE_MODEL_REVISION,
            "expected_sha256": expected_sha256,
        }
    return records


def _snapshot_material(input_paths: dict[str, Path]) -> dict[str, Any]:
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
            "safetensors": importlib.metadata.version("safetensors"),
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
        },
        "pinned_base_files": pinned_base_snapshot(),
        "recipe_commitment_sha256": recipe_commitment_sha256(),
    }


def capture_execution_snapshot(input_paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "schema_version": EXECUTION_SNAPSHOT_SCHEMA_VERSION,
        "captured_at": datetime.now(UTC).isoformat(),
        "material": _snapshot_material(input_paths),
    }


def assert_execution_snapshot_unchanged(
    snapshot: dict[str, Any], input_paths: dict[str, Path]
) -> None:
    if (
        snapshot.get("schema_version") != EXECUTION_SNAPSHOT_SCHEMA_VERSION
        or not isinstance(snapshot.get("material"), dict)
        or snapshot["material"] != _snapshot_material(input_paths)
    ):
        raise RuntimeError(
            "학습 시작 후 input·code·dependency·KR-FinBERT-SC base/tokenizer가 변경되었습니다."
        )


def _artifact_records(directory: Path) -> dict[str, dict[str, int | str]]:
    records: dict[str, dict[str, int | str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"artifact에 symlink가 포함되어 있습니다: {path}")
        if path.is_file():
            records[path.relative_to(directory).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
    return records


def _write_json_file(path: Path, value: dict[str, Any], *, exclusive: bool) -> None:
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())


def save_artifact(
    model: nn.Module,
    tokenizer: Any,
    output_dir: Path,
    metadata: dict[str, Any],
) -> dict[str, dict[str, int | str]]:
    if output_dir.exists() or output_dir.is_symlink():
        raise RuntimeError(f"기준선 artifact 출력이 이미 존재합니다: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_dir.parent / f".{output_dir.name}.tmp-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    try:
        encoder_dir = temporary / "encoder"
        cast(Any, model).encoder.save_pretrained(
            encoder_dir,
            safe_serialization=True,
            max_shard_size="1GB",
        )
        encoder_files = [path for path in encoder_dir.rglob("*") if path.is_file()]
        if not (encoder_dir / "model.safetensors").is_file() or any(
            path.suffix.casefold() in {".bin", ".pt", ".pth"} for path in encoder_files
        ):
            raise RuntimeError("전체 fine-tune encoder는 단일 safetensors로 저장해야 합니다.")
        head_state = {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in source_hierarchical_head_state_dict(model).items()
        }
        save_file(head_state, temporary / HEAD_ARTIFACT_FILENAME)
        tokenizer.save_pretrained(temporary)
        _write_json_file(temporary / "hannah_metadata.json", metadata, exclusive=True)
        artifact_files = _artifact_records(temporary)
        manifest = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "status": "ATOMIC_COMPLETE",
            "generated_at": datetime.now(UTC).isoformat(),
            "artifact_files": artifact_files,
            "artifact_manifest_sha256": canonical_json_sha256(artifact_files),
            "safe_serialization_only": True,
            "symlinks_allowed": False,
            "overwrite_allowed": False,
        }
        _write_json_file(temporary / "manifest.json", manifest, exclusive=True)
        for directory in (encoder_dir, temporary):
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        if output_dir.exists() or output_dir.is_symlink():
            raise RuntimeError("학습 중 기준선 artifact 출력이 생성되었습니다.")
        os.rename(temporary, output_dir)
        parent_descriptor = os.open(output_dir.parent, os.O_RDONLY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
        validate_kr_finbert_sc_v6_artifact(output_dir)
        return artifact_files
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def _parity_tensors(
    tokenizer: Any,
    canary: dict[str, str],
) -> tuple[dict[str, torch.Tensor], dict[str, list[int]]]:
    features = encode_sentiment_input(
        tokenizer,
        canary["text"],
        canary["source_type"],
        MAX_LENGTH,
        canary["target_security"],
    )
    tensors = {name: torch.tensor([values], dtype=torch.long) for name, values in features.items()}
    tensors["domain_ids"] = torch.tensor(
        [DOMAIN_TO_ID[cast(Any, canary["domain"])]], dtype=torch.long
    )
    return tensors, features


def verify_production_cpu_roundtrip(
    *,
    model: nn.Module,
    tokenizer: Any,
    artifact_dir: Path,
    calibration: dict[str, dict[str, float | int | str]],
    canary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    started = time.monotonic()
    validated_calibration = validate_domain_calibration(calibration)
    contract = validate_kr_finbert_sc_v6_artifact(artifact_dir)
    if contract.max_length != MAX_LENGTH or contract.calibration_by_domain != validated_calibration:
        raise RuntimeError("기준선 CPU parity artifact 계약이 학습 계약과 다릅니다.")
    runtime = load_kr_finbert_sc_v6_runtime(artifact_dir)
    loaded_model = getattr(runtime, "_model", None)
    loaded_tokenizer = getattr(runtime, "_tokenizer", None)
    if not isinstance(loaded_model, nn.Module) or loaded_tokenizer is None:
        raise RuntimeError("기준선 production runtime raw-logit interface가 없습니다.")
    model.to(torch.device("cpu"))
    model.eval()
    loaded_model.eval()
    records: list[dict[str, Any]] = []
    max_logit_error = 0.0
    max_probability_error = 0.0
    for canary in v6._runtime_parity_canaries(canary_rows):
        expected_inputs, expected_features = _parity_tensors(tokenizer, canary)
        loaded_inputs, loaded_features = _parity_tensors(loaded_tokenizer, canary)
        if expected_features != loaded_features:
            raise RuntimeError("기준선 artifact tokenizer round-trip feature가 다릅니다.")
        with torch.inference_mode():
            expected = v6._model_forward(model, expected_inputs)
            loaded = v6._model_forward(loaded_model, loaded_inputs)
        expected_logits = expected.logits.detach().to(torch.float64).cpu()
        loaded_logits = loaded.logits.detach().to(torch.float64).cpu()
        logit_error = float(torch.max(torch.abs(expected_logits - loaded_logits)))
        domain = cast(Any, canary["domain"])
        expected_prediction = calibrated_sentiment_prediction(
            expected_logits[0].tolist(), domain, validated_calibration
        )
        loaded_prediction = runtime.predict(
            canary["text"], canary["source_type"], canary["target_security"]
        )
        probability_error = max(
            abs(
                expected_prediction.calibrated_probabilities[label]
                - loaded_prediction.calibrated_probabilities[label]
            )
            for label in LABEL_ORDER
        )
        if (
            not math.isfinite(logit_error)
            or logit_error > RUNTIME_PARITY_LOGIT_ATOL
            or not math.isfinite(probability_error)
            or probability_error > RUNTIME_PARITY_PROBABILITY_ATOL
            or expected_prediction.label != loaded_prediction.label
        ):
            raise RuntimeError("기준선 production CPU logit/probability/label parity가 다릅니다.")
        max_logit_error = max(max_logit_error, logit_error)
        max_probability_error = max(max_probability_error, probability_error)
        records.append(
            {
                "domain": canary["domain"],
                "input_commitment_sha256": canonical_json_sha256(canary),
                "logits_max_abs_error": logit_error,
                "probability_max_abs_error": probability_error,
                "expected_label": expected_prediction.label,
                "loaded_label": loaded_prediction.label,
                "exact_label_agreement": True,
            }
        )
    return {
        "schema_version": "kr-finbert-sc-v6-training-cpu-roundtrip/v1",
        "status": "PASS",
        "loader": (
            "hannah_montana_ai.services.kr_finbert_sc_v6_baseline.load_kr_finbert_sc_v6_runtime"
        ),
        "device": "cpu",
        "canary_count": len(records),
        "domains": [record["domain"] for record in records],
        "logits_atol": RUNTIME_PARITY_LOGIT_ATOL,
        "probability_atol": RUNTIME_PARITY_PROBABILITY_ATOL,
        "logits_max_abs_error": max_logit_error,
        "probability_max_abs_error": max_probability_error,
        "exact_final_threshold_label_agreement": True,
        "records": records,
        "wall_seconds": time.monotonic() - started,
    }


def _stage_record(result: v6.StageResult) -> dict[str, Any]:
    return {
        "stage": result.stage,
        "best_epoch": result.best_epoch,
        "checkpoint_score": list(result.checkpoint_score),
        "checkpoint_metrics": result.checkpoint_metrics,
        "history": result.history,
        "optimizer_steps": result.optimizer_steps,
        "planned_optimizer_steps": result.planned_optimizer_steps,
        "best_optimizer_step": result.best_optimizer_step,
        "wall_seconds": result.wall_seconds,
        "objective_provenance": result.objective_provenance,
        "active_parameter_provenance": result.active_parameter_provenance,
    }


def train_seed(args: argparse.Namespace) -> dict[str, Any]:
    output_dir, report_path = _seed_paths(args)
    _preflight_seed_outputs(output_dir, report_path)
    checkpoint_root = args.checkpoint_root or (
        output_dir.parent / f".{output_dir.name}-training-checkpoints"
    )
    if checkpoint_root.is_symlink():
        raise RuntimeError("기준선 checkpoint root는 symlink일 수 없습니다.")
    v6._set_seed(args.seed)
    input_paths = v6._input_paths(args)
    v6._validate_reservation_paths(args)
    for name, path in input_paths.items():
        v6.assert_training_path_allowed(path, name)
        v5._require_regular_input(path, name)
    execution_snapshot = capture_execution_snapshot(input_paths)
    prepared = v6.prepare_partitions(args)
    assert_execution_snapshot_unchanged(execution_snapshot, prepared.input_paths)

    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        trust_remote_code=False,
        use_fast=True,
    )
    model = build_model(gradient_checkpointing=args.gradient_checkpointing)
    device = v6._device(args.device)
    model.to(device)
    collator = v6.DomainCollator(tokenizer)
    datasets = {
        "TRAIN": v6.DomainEncodedDataset(prepared.train_rows, tokenizer, MAX_LENGTH),
        "CHECKPOINT": v6.DomainEncodedDataset(prepared.checkpoint_rows, tokenizer, MAX_LENGTH),
        "CALIBRATION": v6.DomainEncodedDataset(prepared.calibration_rows, tokenizer, MAX_LENGTH),
        "SELECTION": v6.DomainEncodedDataset(prepared.selection_rows, tokenizer, MAX_LENGTH),
        "GOLD_REFINEMENT": v6.DomainEncodedDataset(
            prepared.gold_refinement_rows, tokenizer, MAX_LENGTH
        ),
    }
    stage1_names = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    stage1_trainable_count = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    total_parameter_count = sum(parameter.numel() for parameter in model.parameters())
    checkpoint_context_sha256 = v6._stage_checkpoint_context_sha256(
        {
            "execution_material": execution_snapshot["material"],
            "seed": args.seed,
            "max_length": MAX_LENGTH,
            "stage1_epochs": STAGE1_EPOCHS,
            "stage2_epochs": STAGE2_EPOCHS,
            "batch_size": BATCH_SIZE,
            "eval_batch_size": EVAL_BATCH_SIZE,
            "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
            "stage1_learning_rate": STAGE1_LEARNING_RATE,
            "stage2_learning_rate": STAGE2_LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "rdrop_alpha": R_DROP_ALPHA,
            "gradient_checkpointing": bool(args.gradient_checkpointing),
        }
    )
    interruption = v6.TrainingInterruptionAudit()
    interruption.install()
    try:
        stage1 = v6.train_stage(
            model,
            datasets["TRAIN"],
            datasets["CHECKPOINT"],
            collator,
            stage="STAGE1_DOMAIN_BALANCED_FULL_ENCODER",
            epochs=STAGE1_EPOCHS,
            learning_rate=STAGE1_LEARNING_RATE,
            weight_decay=WEIGHT_DECAY,
            batch_size=BATCH_SIZE,
            eval_batch_size=EVAL_BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            rdrop_alpha=R_DROP_ALPHA,
            seed=args.seed,
            device=device,
            state_names=stage1_names,
            interruption_audit=interruption,
            checkpoint_directory=checkpoint_root / "stage1",
            checkpoint_context_sha256=checkpoint_context_sha256,
        )
        for parameter in cast(Any, model).encoder.parameters():
            parameter.requires_grad = False
        stage2_names = {
            name for name, parameter in model.named_parameters() if parameter.requires_grad
        }
        stage2 = v6.train_stage(
            model,
            datasets["GOLD_REFINEMENT"],
            datasets["CHECKPOINT"],
            collator,
            stage="STAGE2_GOLD_CLEAN_HEADS_ONLY",
            epochs=STAGE2_EPOCHS,
            learning_rate=STAGE2_LEARNING_RATE,
            weight_decay=WEIGHT_DECAY,
            batch_size=BATCH_SIZE,
            eval_batch_size=EVAL_BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            rdrop_alpha=R_DROP_ALPHA,
            seed=args.seed + 1_003,
            device=device,
            state_names=stage2_names,
            interruption_audit=interruption,
            checkpoint_directory=checkpoint_root / "stage2",
            checkpoint_context_sha256=checkpoint_context_sha256,
        )
        planned_stage1_steps = expected_optimizer_steps(len(prepared.train_rows), STAGE1_EPOCHS)
        planned_stage2_steps = expected_optimizer_steps(
            len(prepared.gold_refinement_rows), STAGE2_EPOCHS
        )
        if (
            stage1.optimizer_steps != planned_stage1_steps
            or stage2.optimizer_steps != planned_stage2_steps
            or len(stage1.history) != STAGE1_EPOCHS
            or len(stage2.history) != STAGE2_EPOCHS
        ):
            raise RuntimeError(
                "v6 공정 기준선은 고정 full-epoch와 planned=executed optimizer step을 "
                "충족해야 합니다."
            )
        selected_stage = stage2
        if stage1.checkpoint_score >= stage2.checkpoint_score:
            v6._restore_state(model, stage1.state)
            selected_stage = stage1

        calibration_logits, calibration_labels, calibration_domains = v6.predict(
            model,
            datasets["CALIBRATION"],
            collator,
            batch_size=EVAL_BATCH_SIZE,
            device=device,
        )
        calibration = v6.fit_calibration(
            calibration_logits, calibration_labels, calibration_domains
        )
        calibration_predictions = v6.calibrated_predictions(
            calibration_logits, calibration_domains, calibration
        )
        calibration_metrics = v6.metrics_by_domain(
            calibration_labels, calibration_predictions, calibration_domains
        )
        selection_logits, selection_labels, selection_domains = v6.predict(
            model,
            datasets["SELECTION"],
            collator,
            batch_size=EVAL_BATCH_SIZE,
            device=device,
        )
        selection_predictions = v6.calibrated_predictions(
            selection_logits, selection_domains, calibration
        )
        selection_metrics = v6.metrics_by_domain(
            selection_labels, selection_predictions, selection_domains
        )
        selection_score = v6.weakest_source_score(selection_metrics)
        interruption.mark_progress()
    finally:
        interruption.close()
    interruption_provenance = interruption.report()

    version = (
        f"kr-finbert-sc-k-fnspid-source-hierarchical-v6-seed{args.seed}-"
        f"{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    )
    runtime_contract = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "encoder_path": "encoder",
        "heads_path": HEAD_ARTIFACT_FILENAME,
        "tokenizer_source": "artifact-root",
        "domain_order": list(DOMAIN_ORDER),
        "label_order": list(LABEL_ORDER),
        "domain_required": True,
        "unknown_domain_behavior": "FAIL_CLOSED",
        "head_architecture": {
            "version": HEAD_ARCHITECTURE_VERSION,
            "anchor_domain": ANCHOR_DOMAIN,
            "residual_domains": list(RESIDUAL_DOMAINS),
            "residual_initialization": "EXACT_ZERO",
            "known_untrained_domain_fallback": "SHARED_HEAD_ZERO_RESIDUAL",
            "unknown_domain_behavior": "FAIL_CLOSED",
        },
        "pooling": "last_hidden_state_cls",
        "calibration": calibration,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "max_length": MAX_LENGTH,
    }
    matching_contract = candidate_matching_contract(
        prepared_partition_commitments=prepared.commitments,
        input_artifacts=execution_snapshot["material"]["input_artifacts"],
        stage1_optimizer_steps=stage1.optimizer_steps,
        stage2_optimizer_steps=stage2.optimizer_steps,
        stage1_planned_optimizer_steps=planned_stage1_steps,
        stage2_planned_optimizer_steps=planned_stage2_steps,
        gradient_checkpointing=bool(args.gradient_checkpointing),
    )
    metadata = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "model_family": MODEL_FAMILY,
        "version": version,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": list(LABEL_ORDER),
        "prepared_partition_commitments": prepared.commitments,
        "candidate_matching_contract": matching_contract,
        "runtime_loader_contract": runtime_contract,
        "recipe_commitment_sha256": recipe_commitment_sha256(),
        "selected_stage": selected_stage.stage,
        "trained_at": datetime.now(UTC).isoformat(),
    }
    assert_execution_snapshot_unchanged(execution_snapshot, prepared.input_paths)
    model.to(torch.device("cpu"))
    artifact_files = save_artifact(model, tokenizer, output_dir, metadata)
    try:
        cpu_roundtrip = verify_production_cpu_roundtrip(
            model=model,
            tokenizer=tokenizer,
            artifact_dir=output_dir,
            calibration=calibration,
            canary_rows=prepared.selection_rows,
        )
        assert_execution_snapshot_unchanged(execution_snapshot, prepared.input_paths)
    except Exception:
        shutil.rmtree(output_dir)
        raise

    report = {
        **metadata,
        "schema_version": TRAINING_SCHEMA_VERSION,
        "seed": args.seed,
        "baseline_model_name": BASELINE_MODEL_NAME,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "execution_snapshot": execution_snapshot,
        "training_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": importlib.metadata.version("transformers"),
            "numpy": np.__version__,
            "device": str(device),
            "bitwise_deterministic_guaranteed": False,
        },
        "recipe": recipe_contract(),
        "training_arguments": {
            "seed": args.seed,
            "data_selection_seed": v5.DATA_SELECTION_SEED,
            "max_length": MAX_LENGTH,
            "stage1_epochs": STAGE1_EPOCHS,
            "stage2_epochs": STAGE2_EPOCHS,
            "batch_size": BATCH_SIZE,
            "eval_batch_size": EVAL_BATCH_SIZE,
            "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
            "stage1_learning_rate": STAGE1_LEARNING_RATE,
            "stage2_learning_rate": STAGE2_LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "rdrop_alpha": R_DROP_ALPHA,
            "gradient_checkpointing": bool(args.gradient_checkpointing),
        },
        "restart_safe_stage_checkpointing": {
            "schema_version": v6.STAGE_CHECKPOINT_SCHEMA_VERSION,
            "checkpoint_root": str(checkpoint_root),
            "context_sha256": checkpoint_context_sha256,
            "interval": "END_OF_EPOCH",
            "atomic_directory_publish": True,
            "safe_tensor_serialization_only": True,
            "automatic_latest_resume": True,
        },
        "fairness_contract": {
            "raw_source_rows": "EXACT_V6_PREPARED_PARTITIONS",
            "group_disjoint_partitions": True,
            "same_data_selection_seed": True,
            "same_model_seed_set": True,
            "same_epoch_batch_accumulation_scheduler_and_checkpoint_rule": True,
            "planned_equals_executed_optimizer_steps": True,
            "same_target_aware_input": True,
            "same_source_hierarchical_task_loss_calibration_selection": True,
            "intended_differences": {
                "encoder": "snunlp/KR-FinBert-SC instead of KF-DeBERTa",
                "adaptation": "full encoder fine-tune instead of LoRA",
                "stage1_learning_rate": {
                    "baseline": STAGE1_LEARNING_RATE,
                    "candidate": CANDIDATE_STAGE1_LEARNING_RATE,
                },
                "parameter_count_reported": True,
            },
        },
        "candidate_matching_contract": matching_contract,
        "stage_selection": {
            "fit_partition": "CHECKPOINT_ONLY",
            "primary": "weakest-source-domain-macro-f1",
            "secondary": "overall-macro-f1",
            "selected_stage": selected_stage.stage,
            "stage1": _stage_record(stage1),
            "stage2": {
                **_stage_record(stage2),
                "encoder_frozen": True,
                "training_rows": len(prepared.gold_refinement_rows),
            },
            "executed_optimizer_steps_total": (stage1.optimizer_steps + stage2.optimizer_steps),
            "planned_optimizer_steps_total": (
                stage1.planned_optimizer_steps + stage2.planned_optimizer_steps
            ),
        },
        "calibration": {
            "fit_partition": "CALIBRATION_ONLY",
            "selection_used_for_fit": False,
            "public_test_used_for_fit": False,
            "confirmatory_used_for_fit": False,
            "parameters": calibration,
            "metrics": calibration_metrics,
        },
        "candidate_selection": {
            "fit_partition": v6.ADAPTIVE_SELECTION_ROLE,
            "primary": "weakest-source-domain-macro-f1",
            "primary_value": selection_score[0],
            "secondary_overall_macro_f1": selection_score[1],
            "metrics": selection_metrics,
            "independent_generalization_evidence": False,
            "confirmatory_is_only_independent_generalization_evidence": True,
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
        "prepared_partition_commitments": prepared.commitments,
        "data_audit": prepared.audit,
        "training_source_distribution": dict(
            sorted(Counter(str(row.get("dataset", "")) for row in prepared.train_rows).items())
        ),
        "training_label_distribution": v5._label_distribution(prepared.train_rows),
        "parameter_counts": {
            "stage1_trainable_full_encoder_and_heads": stage1_trainable_count,
            "stage2_trainable_heads_only": sum(
                parameter.numel() for parameter in model.parameters() if parameter.requires_grad
            ),
            "total": total_parameter_count,
        },
        "interruption_provenance": interruption_provenance,
        "production_cpu_roundtrip": cpu_roundtrip,
        "artifact_path": output_dir.resolve().relative_to(PROJECT_ROOT).as_posix(),
        "artifact_files": artifact_files,
        "test": {"sample_count": 0, "status": "SEALED_UNTIL_CANDIDATE_LOCK"},
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_file(report_path, report, exclusive=True)
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    return report


def validation_plan(args: argparse.Namespace) -> dict[str, Any]:
    prepared = v6.prepare_partitions(args)
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": "VALIDATED_WITHOUT_TRAINING",
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "seed": args.seed,
        "required_model_seeds": list(MODEL_SEEDS),
        "prepared_partition_commitments": prepared.commitments,
        "partition_count": {
            "TRAIN": len(prepared.train_rows),
            "CHECKPOINT": len(prepared.checkpoint_rows),
            "CALIBRATION": len(prepared.calibration_rows),
            "SELECTION": len(prepared.selection_rows),
            "GOLD_REFINEMENT": len(prepared.gold_refinement_rows),
        },
        "recipe": recipe_contract(),
        "recipe_commitment_sha256": recipe_commitment_sha256(),
        "base_hash_verification": "REQUIRED_AT_REAL_TRAINING_START_AND_PRE_SAVE",
    }


def _json_object(path: Path, description: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"{description}가 일반 파일이 아닙니다: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{description}가 JSON 객체가 아닙니다.")
    return value


def _score(value: object, description: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise RuntimeError(f"{description} 값이 숫자가 아닙니다.")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise RuntimeError(f"{description} 값이 [0,1] 범위를 벗어났습니다.")
    return result


def _project_record(path: Path, project_root: Path) -> dict[str, int | str]:
    return _regular_file_record(path, project_root)


def aggregate_runs(
    *,
    output_root: Path,
    report_root: Path,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = project_root.resolve(strict=True)
    selection_path = report_root / "selection.json"
    winner_path = report_root / "winner.json"
    commitment_path = report_root / "sap-baseline-commitment.json"
    aggregate_paths = (selection_path, winner_path, commitment_path)
    existing = [path.exists() or path.is_symlink() for path in aggregate_paths]
    if any(existing):
        if not all(existing):
            raise RuntimeError("3-seed aggregate 출력 일부만 존재합니다.")
        selection = _json_object(selection_path, "기존 3-seed selection")
        winner = _json_object(winner_path, "기존 3-seed winner")
        commitment = _json_object(commitment_path, "기존 3-seed commitment")
        validated = validate_v6_kr_finbert_sc_baseline_commitment(
            commitment,
            project_root=root,
        )
        selected_seed = selection.get("selected_seed")
        selected_run = next(
            (
                run
                for run in selection.get("runs", [])
                if isinstance(run, dict) and run.get("seed") == selected_seed
            ),
            None,
        )
        if (
            selection.get("schema_version") != SELECTION_SCHEMA_VERSION
            or not isinstance(selected_run, dict)
            or winner.get("schema_version") != WINNER_SCHEMA_VERSION
            or winner.get("selected_seed") != selected_seed
            or winner.get("selection_report") != _project_record(selection_path, root)
            or winner.get("winner_report") != selected_run.get("report")
            or winner.get("winner_artifact_path") != selected_run.get("artifact_path")
            or winner.get("winner_artifact_manifest_sha256")
            != selected_run.get("artifact_manifest_sha256")
            or validated.get("selected_seed") != selected_seed
        ):
            raise RuntimeError("기존 3-seed aggregate 연결 계약이 다릅니다.")
        result = {
            **selection,
            "reuse_status": "VERIFIED_EXACT_ARTIFACT_REUSE",
            "winner_manifest": _project_record(winner_path, root),
            "sap_baseline_commitment": _project_record(commitment_path, root),
            "sap_baseline_commitment_sha256": canonical_json_sha256(commitment),
        }
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return result
    reports: list[dict[str, Any]] = []
    recipe_digest: str | None = None
    partition_commitments: dict[str, Any] | None = None
    common_matching_contract: dict[str, Any] | None = None
    seed_optimizer_steps: dict[str, Any] = {}
    for seed in MODEL_SEEDS:
        report_path = report_root / f"seed{seed}.json"
        artifact_path = output_root / f"seed{seed}"
        report = _json_object(report_path, f"seed{seed} report")
        artifact = validate_kr_finbert_sc_v6_artifact(artifact_path)
        if (
            report.get("schema_version") != TRAINING_SCHEMA_VERSION
            or report.get("seed") != seed
            or report.get("baseline_model_name") != BASELINE_MODEL_NAME
            or report.get("public_test_opened") is not False
            or report.get("confirmatory_labels_opened") is not False
            or report.get("test") != {"sample_count": 0, "status": "SEALED_UNTIL_CANDIDATE_LOCK"}
            or report.get("prepared_partition_commitments")
            != artifact.prepared_partition_commitments
            or report.get("candidate_matching_contract") != artifact.candidate_matching_contract
        ):
            raise RuntimeError(f"seed{seed} 기준선 report/artifact 계약이 다릅니다.")
        if report.get("production_cpu_roundtrip", {}).get("status") != "PASS":
            raise RuntimeError(f"seed{seed} production CPU parity가 PASS가 아닙니다.")
        current_recipe = report.get("recipe_commitment_sha256")
        if not isinstance(current_recipe, str) or len(current_recipe) != 64:
            raise RuntimeError(f"seed{seed} recipe commitment가 없습니다.")
        if recipe_digest is None:
            recipe_digest = current_recipe
            partition_commitments = report["prepared_partition_commitments"]
        elif (
            current_recipe != recipe_digest
            or report["prepared_partition_commitments"] != partition_commitments
        ):
            raise RuntimeError("세 seed의 recipe 또는 raw partition commitment가 다릅니다.")
        raw_matching = report.get("candidate_matching_contract")
        if not isinstance(raw_matching, dict):
            raise RuntimeError(f"seed{seed} candidate_matching_contract가 없습니다.")
        executed_steps = raw_matching.get("executed_optimizer_steps")
        planned_steps = raw_matching.get("planned_optimizer_steps")
        if (
            not isinstance(executed_steps, dict)
            or not isinstance(planned_steps, dict)
            or set(executed_steps) != {"stage1", "stage2", "total"}
            or set(planned_steps) != {"stage1", "stage2", "total"}
            or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 1
                for value in executed_steps.values()
            )
            or executed_steps["total"] != executed_steps["stage1"] + executed_steps["stage2"]
            or executed_steps != planned_steps
        ):
            raise RuntimeError(f"seed{seed} 실제 optimizer step 계약이 잘못되었습니다.")
        matching_projection = {
            key: value for key, value in raw_matching.items() if key != "executed_optimizer_steps"
        }
        if common_matching_contract is None:
            common_matching_contract = matching_projection
        elif matching_projection != common_matching_contract:
            raise RuntimeError("세 seed의 candidate matching 공통 계약이 다릅니다.")
        seed_optimizer_steps[str(seed)] = executed_steps
        selection = report.get("candidate_selection")
        if not isinstance(selection, dict):
            raise RuntimeError(f"seed{seed} adaptive selection 지표가 없습니다.")
        primary_score = _score(
            selection.get("primary_value"), f"seed{seed} weakest-source Macro-F1"
        )
        secondary_score = _score(
            selection.get("secondary_overall_macro_f1"),
            f"seed{seed} overall Macro-F1",
        )
        reports.append(
            {
                "seed": seed,
                "report_path": report_path.resolve().relative_to(root).as_posix(),
                "artifact_path": artifact_path.resolve().relative_to(root).as_posix(),
                "report": _project_record(report_path, root),
                "artifact_manifest_sha256": artifact.artifact_manifest_sha256,
                "primary_weakest_source_macro_f1": primary_score,
                "secondary_overall_macro_f1": secondary_score,
                "parameter_counts": report.get("parameter_counts"),
            }
        )
    if recipe_digest is None or partition_commitments is None or common_matching_contract is None:
        raise RuntimeError("3-seed 기준선 report가 없습니다.")
    winner = max(
        reports,
        key=lambda row: (
            float(row["primary_weakest_source_macro_f1"]),
            float(row["secondary_overall_macro_f1"]),
            -int(row["seed"]),
        ),
    )
    selection = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "baseline_model_name": BASELINE_MODEL_NAME,
        "generated_at": datetime.now(UTC).isoformat(),
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "model_seeds": list(MODEL_SEEDS),
        "selection_partition": v6.ADAPTIVE_SELECTION_ROLE,
        "independent_generalization_evidence": False,
        "primary": "weakest-source-domain-macro-f1",
        "secondary": "overall-macro-f1",
        "selected_seed": winner["seed"],
        "recipe_commitment_sha256": recipe_digest,
        "prepared_partition_commitments": partition_commitments,
        "candidate_matching_contract": {
            **common_matching_contract,
            "seed_executed_optimizer_steps": seed_optimizer_steps,
        },
        "runs": reports,
    }
    report_root.mkdir(parents=True, exist_ok=True)
    _write_json_file(selection_path, selection, exclusive=True)
    winner_manifest = {
        "schema_version": WINNER_SCHEMA_VERSION,
        "selected_seed": winner["seed"],
        "selection_report": _project_record(selection_path, root),
        "winner_report": winner["report"],
        "winner_artifact_path": winner["artifact_path"],
        "winner_artifact_manifest_sha256": winner["artifact_manifest_sha256"],
        "recipe_commitment_sha256": recipe_digest,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
    }
    _write_json_file(winner_path, winner_manifest, exclusive=True)
    commitment = build_v6_kr_finbert_sc_baseline_commitment(
        project_root=root,
        selection_report=selection_path,
    )
    _write_json_file(commitment_path, commitment, exclusive=True)
    validate_v6_kr_finbert_sc_baseline_commitment(commitment, project_root=root)
    result = {
        **selection,
        "winner_manifest": _project_record(winner_path, root),
        "sap_baseline_commitment": _project_record(commitment_path, root),
        "sap_baseline_commitment_sha256": canonical_json_sha256(commitment),
    }
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return result


def main(argv: Sequence[str] | None = None) -> None:
    args = parser().parse_args(argv)
    validate_arguments(args)
    if args.aggregate_only:
        aggregate_runs(output_root=args.output_root, report_root=args.report_root)
        return
    if args.validate_only:
        print(json.dumps(validation_plan(args), ensure_ascii=False, allow_nan=False))
        return
    train_seed(args)


if __name__ == "__main__":
    main()
