from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

try:
    from scripts.train_k_fnspid_transformer import MODEL_PRESETS
except ModuleNotFoundError:  # 직접 실행 시 scripts 디렉터리에서 import한다.
    from train_k_fnspid_transformer import MODEL_PRESETS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCHEMA = "k-fnspid-impact-strong-baseline-training/v1"
EXPECTED_ARTIFACT_FILES = {
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-FNSPID 시장영향 공개 비교군 artifact 무결성을 검증한다."
    )
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--model-preset", choices=tuple(MODEL_PRESETS), required=True)
    parser.add_argument(
        "--source-type",
        choices=("SHARED", "NEWS", "DISCLOSURE"),
        required=True,
    )
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    report_path = _project_path(args.report)
    if not report_path.is_file():
        raise SystemExit(2)
    report = _object(json.loads(report_path.read_text(encoding="utf-8")), "report")
    validate_report(
        report,
        model_preset=args.model_preset,
        source_type=args.source_type,
        seed=args.seed,
    )
    print(
        json.dumps(
            {
                "status": "VERIFIED_EXACT_ARTIFACT_REUSE",
                "report": str(report_path.relative_to(PROJECT_ROOT)),
                "report_sha256": _sha256(report_path),
                "model_preset": args.model_preset,
                "source_type": args.source_type,
                "seed": args.seed,
            },
            ensure_ascii=False,
        )
    )


def validate_report(
    report: dict[str, Any],
    *,
    model_preset: str,
    source_type: str,
    seed: int,
) -> None:
    preset = MODEL_PRESETS[model_preset]
    if not preset.comparison_only:
        raise ValueError("운영 모델은 공개 비교군 재사용 검증 대상이 아닙니다.")
    expected = {
        "schema_version": EXPECTED_SCHEMA,
        "model_preset": model_preset,
        "base_model": preset.model_id,
        "base_model_revision": preset.revision,
        "base_model_safetensors_sha256": preset.model_safetensors_sha256,
        "comparison_only": True,
        "source_type": None if source_type == "SHARED" else source_type,
        "seed": seed,
    }
    for field, value in expected.items():
        if report.get(field) != value:
            raise ValueError(f"비교군 report 계약 불일치({field})")
    _validate_recipe(
        report,
        model_preset=model_preset,
        source_type=source_type,
    )
    if report.get("deployment_gate", {}).get("decision") != "RESEARCH_BASELINE_ONLY":
        raise ValueError("공개 비교군이 운영 배포 후보로 표시되었습니다.")

    dataset_dir = _project_path(Path(str(report["dataset_dir"])))
    manifest_path = dataset_dir / "manifest.json"
    dataset_manifest = _object(report.get("dataset_manifest"), "dataset_manifest")
    if _sha256(manifest_path) != dataset_manifest.get("sha256"):
        raise ValueError("현재 K-FNSPID manifest와 비교군 report가 다릅니다.")

    artifact_dir = _project_path(Path(str(report["artifact_dir"])))
    artifact_files = _object(report.get("artifact_files"), "artifact_files")
    if set(artifact_files) != EXPECTED_ARTIFACT_FILES:
        raise ValueError("공개 비교군의 필수 safe artifact 목록이 다릅니다.")
    for name, raw_manifest in artifact_files.items():
        file_path = artifact_dir / name
        _verify_file(file_path, _object(raw_manifest, f"artifact_files.{name}"))

    predictions = _object(report.get("test_predictions"), "test_predictions")
    prediction_path = _project_path(Path(str(predictions["path"])))
    _verify_file(prediction_path, predictions)


def _validate_recipe(
    report: dict[str, Any],
    *,
    model_preset: str,
    source_type: str,
) -> None:
    hyperparameters = _object(
        report.get("training_hyperparameters"),
        "training_hyperparameters",
    )
    objective = _object(report.get("training_objective"), "training_objective")
    is_large = model_preset == "KLUE_ROBERTA_LARGE"
    if source_type == "SHARED":
        expected = {
            "max_length": 256,
            "epochs_requested": 3.0,
            "effective_batch_size": 32,
            "learning_rate": 0.0002,
            "gradient_checkpointing": is_large,
            "focal_gamma": 1.5,
            "ordinal_loss_weight": 0.30,
            "label_smoothing": 0.02,
        }
        expected_evaluation_only = False
    elif source_type == "NEWS":
        expected = {
            "max_length": 256,
            "epochs_requested": 3.0,
            "effective_batch_size": 64,
            "learning_rate": 0.0002,
            "gradient_checkpointing": is_large,
            "focal_gamma": 1.5,
            "ordinal_loss_weight": 0.30,
            "label_smoothing": 0.02,
        }
        expected_evaluation_only = True
    else:
        expected = {
            "max_length": 128,
            "epochs_requested": 1.0,
            "effective_batch_size": 32,
            "learning_rate": 0.00005,
            "gradient_checkpointing": is_large,
            "focal_gamma": 1.0,
            "ordinal_loss_weight": 0.20,
            "label_smoothing": 0.01,
        }
        expected_evaluation_only = False
    actual = {
        "max_length": int(report.get("max_length", -1)),
        "epochs_requested": float(hyperparameters.get("epochs_requested", -1)),
        "effective_batch_size": int(hyperparameters.get("effective_batch_size", -1)),
        "learning_rate": float(hyperparameters.get("learning_rate", -1)),
        "gradient_checkpointing": bool(
            hyperparameters.get("gradient_checkpointing", False)
        ),
        "focal_gamma": float(objective.get("focal_gamma", -1)),
        "ordinal_loss_weight": float(objective.get("ordinal_loss_weight", -1)),
        "label_smoothing": float(objective.get("label_smoothing", -1)),
    }
    if actual != expected:
        raise ValueError("공개 비교군의 잠긴 학습 recipe가 다릅니다.")
    if hyperparameters.get("evaluation_only") is not expected_evaluation_only:
        raise ValueError("공개 비교군의 학습·동결평가 단계 계약이 다릅니다.")
    lora = _object(hyperparameters.get("lora"), "training_hyperparameters.lora")
    expected_initial_adapter = None
    if source_type in {"NEWS", "DISCLOSURE"}:
        artifact_dir = Path(str(report.get("artifact_dir", "")))
        source_dir = artifact_dir.parent
        if source_dir.name != source_type.casefold():
            raise ValueError("공개 비교군의 source artifact 경로가 다릅니다.")
        expected_initial_adapter = str(source_dir.parent / "shared" / "seed42")
    if (
        int(lora.get("rank", -1)) != 16
        or int(lora.get("alpha", -1)) != 32
        or float(lora.get("dropout", -1)) != 0.1
        or lora.get("initial_adapter_path") != expected_initial_adapter
    ):
        raise ValueError("공개 비교군의 LoRA recipe가 다릅니다.")


def _verify_file(path: Path, manifest: dict[str, Any]) -> None:
    if not path.is_file():
        raise ValueError(f"artifact 파일이 없습니다: {path}")
    if path.stat().st_size != int(manifest.get("bytes", -1)):
        raise ValueError(f"artifact 크기가 다릅니다: {path}")
    if _sha256(path) != manifest.get("sha256"):
        raise ValueError(f"artifact SHA-256이 다릅니다: {path}")


def _project_path(path: Path) -> Path:
    resolved = path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError(f"프로젝트 밖의 경로는 사용할 수 없습니다: {path}")
    return resolved


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} 객체가 올바르지 않습니다.")
    return value


if __name__ == "__main__":
    main()
