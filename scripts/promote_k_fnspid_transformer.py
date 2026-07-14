from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.services.model_artifact_integrity import verify_artifact_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MULTISEED_REPORT = PROJECT_ROOT / "reports/k-fnspid-transformer-multiseed-report.json"
DEFAULT_REPORT = PROJECT_ROOT / "reports/k-fnspid-transformer-training-report.json"
DEFAULT_PREDICTIONS = PROJECT_ROOT / "reports/k-fnspid-transformer-test-predictions.jsonl"
DEFAULT_ARTIFACT = PROJECT_ROOT / "src/hannah_montana_ai/model_store/k_fnspid_impact_transformer"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validation으로 선택한 K-FNSPID Transformer를 배포 경로에 승격한다."
    )
    parser.add_argument("--multiseed-report", type=Path, default=DEFAULT_MULTISEED_REPORT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--predictions-path", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args()

    multiseed = _load_json(_safe_path(args.multiseed_report))
    selected_seed = int(multiseed["selected_seed_by_validation"])
    selected_report_path = _selected_report_path(multiseed, selected_seed)
    selected_report = _load_json(selected_report_path)
    if int(selected_report["seed"]) != selected_seed:
        raise SystemExit("선택 seed와 학습 report의 seed가 다릅니다.")
    if selected_report.get("deployment_gate", {}).get("eligible") is not True:
        raise SystemExit("Test 배포 gate를 통과하지 못한 모델은 승격할 수 없습니다.")
    dataset_manifest = selected_report.get("dataset_manifest", {})
    dataset_manifest_path = _safe_path(PROJECT_ROOT / str(dataset_manifest.get("path", "")))
    if not _matches_manifest(dataset_manifest_path, dataset_manifest):
        raise SystemExit("학습에 사용한 K-FNSPID manifest가 현재 파일과 다릅니다.")

    source_artifact = _safe_path(PROJECT_ROOT / str(multiseed["selected_artifact_dir"]))
    if not verify_artifact_manifest(source_artifact, selected_report.get("artifact_files")):
        raise SystemExit("선택 artifact의 SHA-256 또는 크기가 report와 다릅니다.")

    prediction_manifest = selected_report["test_predictions"]
    source_predictions = _safe_path(PROJECT_ROOT / str(prediction_manifest["path"]))
    if not _matches_manifest(source_predictions, prediction_manifest):
        raise SystemExit("선택 Test 예측 파일의 SHA-256 또는 크기가 report와 다릅니다.")

    target_artifact = _safe_path(args.artifact_dir)
    target_report = _safe_path(args.report_path)
    target_predictions = _safe_path(args.predictions_path)
    if source_artifact != target_artifact:
        _replace_artifact_directory(source_artifact, target_artifact, selected_report)

    target_predictions.parent.mkdir(parents=True, exist_ok=True)
    if source_predictions != target_predictions:
        prediction_temp = target_predictions.with_suffix(target_predictions.suffix + ".tmp")
        shutil.copy2(source_predictions, prediction_temp)
        os.replace(prediction_temp, target_predictions)

    selected_report["artifact_dir"] = str(target_artifact.relative_to(PROJECT_ROOT))
    selected_report["test_predictions"] = {
        **prediction_manifest,
        "path": str(target_predictions.relative_to(PROJECT_ROOT)),
    }
    target_report.parent.mkdir(parents=True, exist_ok=True)
    report_temp = target_report.with_suffix(target_report.suffix + ".tmp")
    report_temp.write_text(
        json.dumps(selected_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(report_temp, target_report)
    print(
        json.dumps(
            {
                "selected_seed": selected_seed,
                "version": selected_report["version"],
                "artifact_dir": str(target_artifact.relative_to(PROJECT_ROOT)),
                "report": str(target_report.relative_to(PROJECT_ROOT)),
                "predictions": str(target_predictions.relative_to(PROJECT_ROOT)),
            },
            ensure_ascii=False,
        )
    )


def _selected_report_path(multiseed: dict[str, Any], selected_seed: int) -> Path:
    for configured in multiseed["report_paths"]:
        path = _safe_path(PROJECT_ROOT / str(configured))
        report = _load_json(path)
        if int(report["seed"]) == selected_seed:
            return path
    raise SystemExit("선택 seed에 해당하는 학습 report가 없습니다.")


def _replace_artifact_directory(
    source: Path,
    target: Path,
    report: dict[str, Any],
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent))
    backup = target.parent / f".{target.name}-backup"
    try:
        for path in source.iterdir():
            if path.is_file() and not path.is_symlink():
                shutil.copy2(path, staging / path.name)
        if not verify_artifact_manifest(staging, report.get("artifact_files")):
            raise RuntimeError("staging artifact 무결성 검증에 실패했습니다.")
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


def _matches_manifest(path: Path, manifest: dict[str, Any]) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == int(manifest.get("bytes", -1))
        and _sha256(path) == str(manifest.get("sha256", ""))
    )


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"JSON 객체가 필요합니다: {path}")
    return cast(dict[str, Any], data)


def _safe_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT.resolve()):
        raise SystemExit(f"프로젝트 밖의 경로는 사용할 수 없습니다: {path}")
    return resolved


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
