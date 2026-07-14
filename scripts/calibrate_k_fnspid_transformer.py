from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from peft import PeftModel
from torch.utils.data import DataLoader
from train_k_fnspid_impact_model import load_rows
from train_k_fnspid_transformer import (
    BASE_MODEL,
    BASE_MODEL_REVISION,
    DEFAULT_BASELINE_REPORT,
    DEFAULT_DATASET,
    DEFAULT_OUTPUT,
    DEFAULT_PREDICTIONS,
    DEFAULT_REPORT,
    LABEL_ORDER,
    EncodedImpactDataset,
    _apply_log_prior_correction,
    _classification_metrics,
    _dataset_manifest,
    _select_log_prior_correction,
    _write_predictions,
)
from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding

from hannah_montana_ai.services.model_artifact_integrity import build_artifact_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_FILES = (
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="학습 완료 KF-DeBERTa에 Validation 전용 log-prior 보정을 적용한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--candidate-artifact-dir", type=Path, action="append")
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--predictions-path", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--baseline-report-path", type=Path, default=DEFAULT_BASELINE_REPORT)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    report = _load_report(args.report_path)
    if (
        report.get("dataset_manifest", {}).get("sha256")
        != _dataset_manifest(args.dataset_dir)["sha256"]
    ):
        raise SystemExit("학습 report와 현재 K-FNSPID manifest가 다릅니다.")
    rows = load_rows(args.dataset_dir)
    partitions = {
        name: [row for row in rows if row["split"] == name]
        for name in ("TRAIN", "VALIDATION", "TEST")
    }
    device = _device()
    max_length = int(report.get("max_length", 256))
    candidate_dirs = args.candidate_artifact_dir or [args.artifact_dir]
    candidates: list[dict[str, Any]] = []
    for candidate_dir in candidate_dirs:
        build_artifact_manifest(candidate_dir, ARTIFACT_FILES)
        tokenizer, model = _load_model(candidate_dir, device)
        validation_logits, validation_labels = _predict(
            model,
            tokenizer,
            partitions["VALIDATION"],
            max_length=max_length,
            batch_size=args.batch_size,
            device=device,
        )
        postprocessing = _select_log_prior_correction(
            validation_logits,
            validation_labels,
            partitions["TRAIN"],
        )
        corrected_validation = _apply_log_prior_correction(
            validation_logits,
            postprocessing,
        )
        raw_metrics = _classification_metrics(
            validation_labels,
            validation_logits.argmax(axis=-1),
        )
        corrected_metrics = _classification_metrics(
            validation_labels,
            corrected_validation.argmax(axis=-1),
        )
        candidates.append(
            {
                "artifact_dir": candidate_dir.resolve(),
                "postprocessing": postprocessing,
                "validation_raw": raw_metrics,
                "validation": corrected_metrics,
            }
        )
        del model
        _clear_device_cache(device)
    selected = max(
        candidates,
        key=lambda candidate: (
            float(candidate["validation"]["macro_f1"]),
            float(candidate["validation"]["quadratic_kappa"]),
            float(candidate["validation"]["accuracy"]),
        ),
    )
    selected_dir = cast(Path, selected["artifact_dir"])
    if selected_dir != args.artifact_dir.resolve():
        _promote_candidate(selected_dir, args.artifact_dir)
    tokenizer, model = _load_model(args.artifact_dir, device)
    test_logits, test_labels = _predict(
        model,
        tokenizer,
        partitions["TEST"],
        max_length=max_length,
        batch_size=args.batch_size,
        device=device,
    )
    postprocessing = cast(dict[str, Any], selected["postprocessing"])
    corrected_test = _apply_log_prior_correction(test_logits, postprocessing)
    version = str(report["version"]).split("-prior", maxsplit=1)[0]
    report["version"] = f"{version}-prior{float(postprocessing['selected_strength']):.2f}"
    report["postprocessing"] = postprocessing
    report["evaluation_protocol"] = (
        "TRAIN fit; Validation selects checkpoint, log-prior correction, and seed; "
        "frozen TEST is evaluated once for final deployment and superiority gates"
    )
    report["checkpoint_selection"] = {
        "partition": "VALIDATION",
        "metric": "prior-corrected macro_f1, then quadratic_kappa and accuracy",
        "selected_artifact_dir": _display_path(selected_dir),
        "candidates": [
            {
                "artifact_dir": _display_path(cast(Path, candidate["artifact_dir"])),
                "selected_strength": candidate["postprocessing"]["selected_strength"],
                "validation_raw": candidate["validation_raw"],
                "validation": candidate["validation"],
            }
            for candidate in candidates
        ],
    }
    report["validation_raw"] = selected["validation_raw"]
    report["test_raw"] = _classification_metrics(test_labels, test_logits.argmax(axis=-1))
    report["validation"] = {
        **selected["validation"],
        "sample_count": len(partitions["VALIDATION"]),
    }
    report["test"] = {
        **_classification_metrics(test_labels, corrected_test.argmax(axis=-1)),
        "sample_count": len(test_labels),
    }
    report["postprocessing_runtime"] = {"device": str(device), "batch_size": args.batch_size}
    baseline = _load_report(args.baseline_report_path).get("test", {})
    report["baseline_test"] = baseline
    eligible = (
        len(test_labels) >= 1_000
        and float(report["test"]["macro_f1"]) >= 0.35
        and float(report["test"]["quadratic_kappa"]) >= 0.20
        and float(report["test"]["macro_f1"]) >= float(baseline.get("macro_f1", 0.0))
        and float(report["test"]["quadratic_kappa"]) >= float(baseline.get("quadratic_kappa", 0.0))
    )
    report["deployment_gate"] = {
        "minimum_test_sample_count": 1_000,
        "minimum_macro_f1": 0.35,
        "minimum_quadratic_kappa": 0.20,
        "must_match_or_exceed_baseline": "k-fnspid-impact-tfidf-logreg",
        "eligible": eligible,
        "decision": "DEPLOY_KF_DEBERTA_IMPACT" if eligible else "KEEP_TFIDF_IMPACT",
    }
    report["test_predictions"] = _write_predictions(
        args.predictions_path,
        partitions["TEST"],
        corrected_test,
    )
    report["artifact_files"] = build_artifact_manifest(args.artifact_dir, ARTIFACT_FILES)
    _update_metadata(args.artifact_dir, report)
    _atomic_json(args.report_path, report)
    print(
        json.dumps(
            {
                "selected_strength": postprocessing["selected_strength"],
                "checkpoint_selection": report["checkpoint_selection"],
                "validation_raw": report["validation_raw"],
                "validation": report["validation"],
                "test_raw": report["test_raw"],
                "test": report["test"],
                "deployment_gate": report["deployment_gate"],
            },
            ensure_ascii=False,
        )
    )


def _predict(
    model: Any,
    tokenizer: Any,
    rows: list[dict[str, Any]],
    *,
    max_length: int,
    batch_size: int,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray]:
    dataset = EncodedImpactDataset(rows, tokenizer, max_length)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=DataCollatorWithPadding(tokenizer=tokenizer),
    )
    logits: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    with torch.inference_mode():
        for batch in loader:
            expected = batch.pop("labels")
            output = model(**{name: value.to(device) for name, value in batch.items()})
            logits.append(output.logits.detach().cpu().numpy())
            labels.append(expected.numpy())
    return np.concatenate(logits), np.concatenate(labels).astype(int)


def _load_model(artifact_dir: Path, device: torch.device) -> tuple[Any, Any]:
    # 원격 다운로드 없이 SHA 검증된 로컬 artifact만 읽는다.
    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
        artifact_dir,
        revision="local-verified-artifact",
        trust_remote_code=False,
        local_files_only=True,
    )
    base = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
        trust_remote_code=False,
    )
    model = PeftModel.from_pretrained(
        base,
        artifact_dir,
        is_trainable=False,
        use_safetensors=True,
    )
    model.to(device)
    model.eval()
    return tokenizer, model


def _promote_candidate(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent))
    backup = target.parent / f".{target.name}-prior-backup"
    try:
        for name in ARTIFACT_FILES:
            source_path = source / name
            if not source_path.is_file() or source_path.is_symlink():
                raise RuntimeError(f"안전하지 않은 checkpoint 파일입니다: {source_path}")
            shutil.copy2(source_path, staging / name)
        build_artifact_manifest(staging, ARTIFACT_FILES)
        if backup.exists():
            shutil.rmtree(backup)
        if target.exists():
            os.replace(target, backup)
        os.replace(staging, target)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if not target.exists() and backup.exists():
            os.replace(backup, target)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _clear_device_cache(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "mps":
        torch.mps.empty_cache()


def _device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _load_report(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON 객체 report가 필요합니다: {path}")
    return cast(dict[str, Any], payload)


def _update_metadata(artifact_dir: Path, report: dict[str, Any]) -> None:
    path = artifact_dir / "hannah_metadata.json"
    metadata = {
        "schema_version": "k-fnspid-transformer-artifact/v1",
        "version": report["version"],
        "base_model": report["base_model"],
        "base_model_revision": report["base_model_revision"],
        "label_order": report["label_order"],
        "max_length": report["max_length"],
        "trained_at": report["trained_at"],
        "artifact_files": report["artifact_files"],
        "input_feature_version": report["input_feature_version"],
        "seed": report["seed"],
        "postprocessing": report["postprocessing"],
    }
    _atomic_json(path, metadata)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


if __name__ == "__main__":
    main()
