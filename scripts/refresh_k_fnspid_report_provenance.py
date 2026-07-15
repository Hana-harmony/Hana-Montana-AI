from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from train_k_fnspid_impact_model import load_rows

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v4"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="논리 데이터 동일성을 검증한 뒤 K-FNSPID report provenance를 정정한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--report", type=Path, action="append", required=True)
    args = parser.parse_args()

    rows = load_rows(args.dataset_dir)
    partition_count = Counter(str(row["split"]) for row in rows)
    test_expected = {
        str(row["document_id"]): str(row["importance"]) for row in rows if row["split"] == "TEST"
    }
    manifest = _manifest(args.dataset_dir)
    results = [
        _refresh_report(path, manifest, partition_count, test_expected) for path in args.report
    ]
    print(json.dumps({"status": "pass", "reports": results}, ensure_ascii=False))


def _refresh_report(
    path: Path,
    manifest: dict[str, Any],
    partition_count: Counter[str],
    test_expected: dict[str, str],
) -> dict[str, Any]:
    safe_path = _safe_path(path)
    report = _load_json(safe_path)
    configured_counts = report.get("partition_count")
    expected_counts = {name: partition_count[name] for name in ("TRAIN", "VALIDATION", "TEST")}
    if configured_counts != expected_counts:
        raise SystemExit(f"현재 분할 개수와 report가 다릅니다: {safe_path}")

    prediction_manifest = report.get("test_predictions")
    if not isinstance(prediction_manifest, dict):
        raise SystemExit(f"Test prediction manifest가 없습니다: {safe_path}")
    prediction_path = _safe_path(PROJECT_ROOT / str(prediction_manifest.get("path", "")))
    if not _matches_manifest(prediction_path, prediction_manifest):
        raise SystemExit(f"Test prediction 파일 무결성이 다릅니다: {prediction_path}")
    predictions = _load_predictions(prediction_path)
    if predictions != test_expected:
        raise SystemExit(f"현재 Test 문서 ID·정답과 prediction이 다릅니다: {safe_path}")

    previous = report.get("dataset_manifest")
    if not isinstance(previous, dict) or not previous.get("sha256"):
        raise SystemExit(f"기존 dataset manifest 정보가 없습니다: {safe_path}")
    previous_sha256 = str(previous["sha256"])
    if previous_sha256 == manifest["sha256"]:
        return {"path": _display_path(safe_path), "changed": False}

    report["dataset_manifest"] = manifest
    history = report.setdefault("provenance_refresh", [])
    if not isinstance(history, list):
        raise SystemExit(f"provenance_refresh 형식이 올바르지 않습니다: {safe_path}")
    history.append(
        {
            "refreshed_at": datetime.now(UTC).isoformat(),
            "reason": "JSONL shard 재배치 후 동일 Parquet·분할의 원천 manifest 정정",
            "previous_manifest_sha256": previous_sha256,
            "current_manifest_sha256": manifest["sha256"],
            "identity_checks": {
                "partition_count": expected_counts,
                "test_document_id_and_label_count": len(test_expected),
                "test_predictions_sha256": prediction_manifest["sha256"],
            },
        }
    )
    _atomic_json(safe_path, report)
    return {
        "path": _display_path(safe_path),
        "changed": True,
        "previous_manifest_sha256": previous_sha256,
        "current_manifest_sha256": manifest["sha256"],
    }


def _manifest(dataset_dir: Path) -> dict[str, Any]:
    path = _safe_path(dataset_dir / "manifest.json")
    payload = _load_json(path)
    if payload.get("status") != "pass" or not payload.get("dataset_version"):
        raise SystemExit("검증을 통과한 K-FNSPID manifest가 필요합니다.")
    return {
        "path": _display_path(path),
        "dataset_version": str(payload["dataset_version"]),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _load_predictions(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            payload = json.loads(line)
            document_id = str(payload["document_id"])
            if document_id in rows:
                raise SystemExit(f"Test prediction document_id가 중복되었습니다: {document_id}")
            rows[document_id] = str(payload["expected"])
    return rows


def _matches_manifest(path: Path, manifest: dict[str, Any]) -> bool:
    return (
        path.is_file()
        and not path.is_symlink()
        and path.stat().st_size == int(manifest.get("bytes", -1))
        and _sha256(path) == str(manifest.get("sha256", ""))
    )


def _safe_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT.resolve()):
        raise SystemExit(f"프로젝트 밖 경로는 사용할 수 없습니다: {path}")
    return resolved


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON 객체가 필요합니다: {path}")
    return cast(dict[str, Any], payload)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT.resolve()))


if __name__ == "__main__":
    main()
