from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hannah_montana_ai.services.sentiment_runtime_parity import (
    LOGITS_MAX_ABS_ERROR_TOLERANCE,
    base_encoder_evidence,
    build_cpu_serving_parity_evidence,
    build_runtime_parity_lock_commitment,
    validate_cpu_serving_parity_evidence,
    validate_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    canonical_json_sha256,
)
from scripts.generate_sentiment_cpu_runtime_parity import _validate_dapt_merged_base


def test_cpu_batch16_and_packaged_batch1_parity_is_recomputed_from_logits(
    tmp_path: Path,
) -> None:
    evaluator_base, runtime_base = _identical_bases(tmp_path)
    inputs, evaluator, runtime = _parity_vectors()
    candidate_digest = "a" * 64
    evidence = build_cpu_serving_parity_evidence(
        candidate_version="candidate-v1",
        candidate_artifact_manifest_sha256=candidate_digest,
        reservation_inputs=inputs,
        evaluator_outputs=evaluator,
        packaged_runtime_outputs=runtime,
        evaluator_base_model=base_encoder_evidence(evaluator_base, tmp_path),
        packaged_runtime_base_model=base_encoder_evidence(runtime_base, tmp_path),
        generated_at="2026-07-16T00:00:00+00:00",
    )

    assert evidence["evaluator"]["batch_size"] == 16
    assert evidence["packaged_runtime"]["batch_size"] == 1
    assert evidence["comparison"]["exact_label_agreement"] is True
    assert evidence["comparison"]["logits_max_abs_error"] <= 1e-5
    assert validate_cpu_serving_parity_evidence(evidence) == evidence

    tampered = copy.deepcopy(evidence)
    tampered["packaged_runtime"]["outputs"][0]["logits"][0] += 0.1
    with pytest.raises(ValueError):
        validate_cpu_serving_parity_evidence(tampered)


def test_runtime_parity_lock_binds_reservations_and_actual_evidence_bytes(
    tmp_path: Path,
) -> None:
    evaluator_base, runtime_base = _identical_bases(tmp_path)
    inputs, evaluator, runtime = _parity_vectors()
    candidate_digest = "b" * 64
    evidence = build_cpu_serving_parity_evidence(
        candidate_version="candidate-v2",
        candidate_artifact_manifest_sha256=candidate_digest,
        reservation_inputs=inputs,
        evaluator_outputs=evaluator,
        packaged_runtime_outputs=runtime,
        evaluator_base_model=base_encoder_evidence(evaluator_base, tmp_path),
        packaged_runtime_base_model=base_encoder_evidence(runtime_base, tmp_path),
        generated_at="2026-07-16T00:00:00+00:00",
    )
    evidence_path = tmp_path / "reports/parity.json"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False), encoding="utf-8")
    reservations = _reservation_commitments(inputs)
    locked = build_runtime_parity_lock_commitment(
        evidence_path=evidence_path,
        project_root=tmp_path,
        expected_candidate_version="candidate-v2",
        expected_candidate_artifact_manifest_sha256=candidate_digest,
        sealed_reservations=reservations,
    )
    assert validate_runtime_parity_lock_commitment(
        locked,
        project_root=tmp_path,
        expected_candidate_version="candidate-v2",
        expected_candidate_artifact_manifest_sha256=candidate_digest,
        sealed_reservations=reservations,
    ) == locked

    evidence_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="실제 바이트"):
        validate_runtime_parity_lock_commitment(
            locked,
            project_root=tmp_path,
            expected_candidate_version="candidate-v2",
            expected_candidate_artifact_manifest_sha256=candidate_digest,
            sealed_reservations=reservations,
        )


def test_runtime_parity_rejects_different_base_safetensors(tmp_path: Path) -> None:
    evaluator_base, runtime_base = _identical_bases(tmp_path)
    (runtime_base / "model.safetensors").write_bytes(b"different")
    inputs, evaluator, runtime = _parity_vectors()

    with pytest.raises(ValueError, match="base encoder safetensors"):
        build_cpu_serving_parity_evidence(
            candidate_version="candidate-v3",
            candidate_artifact_manifest_sha256="c" * 64,
            reservation_inputs=inputs,
            evaluator_outputs=evaluator,
            packaged_runtime_outputs=runtime,
            evaluator_base_model=base_encoder_evidence(evaluator_base, tmp_path),
            packaged_runtime_base_model=base_encoder_evidence(runtime_base, tmp_path),
            generated_at="2026-07-16T00:00:00+00:00",
        )


def test_dapt_parity_resolves_hash_bound_merged_directory_from_manifest(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "artifacts/pretraining/run/manifest.json"
    merged = manifest_path.parent / "merged_fp32"
    merged.mkdir(parents=True)
    manifest_path.write_text("{}", encoding="utf-8")
    (merged / "config.json").write_text("{}", encoding="utf-8")
    (merged / "model.safetensors").write_bytes(b"safe-weights")
    provenance = _dapt_provenance(tmp_path, manifest_path, merged)

    assert (
        _validate_dapt_merged_base(
            provenance,
            evaluator_base=merged.resolve(),
            runtime_base=merged.resolve(),
            project_root=tmp_path,
        )
        == merged.resolve()
    )


def test_dapt_parity_rejects_base_not_declared_by_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "artifacts/pretraining/run/manifest.json"
    merged = manifest_path.parent / "merged_fp32"
    alternate = tmp_path / "artifacts/pretraining/alternate/merged_fp32"
    for directory in (merged, alternate):
        directory.mkdir(parents=True)
        (directory / "config.json").write_text("{}", encoding="utf-8")
        (directory / "model.safetensors").write_bytes(b"safe-weights")
    manifest_path.write_text("{}", encoding="utf-8")
    provenance = _dapt_provenance(tmp_path, manifest_path, merged)

    with pytest.raises(ValueError, match="hash-bound"):
        _validate_dapt_merged_base(
            provenance,
            evaluator_base=alternate.resolve(),
            runtime_base=alternate.resolve(),
            project_root=tmp_path,
        )


def _identical_bases(root: Path) -> tuple[Path, Path]:
    evaluator = root / "models/evaluator"
    runtime = root / "models/runtime"
    for directory in (evaluator, runtime):
        directory.mkdir(parents=True)
        (directory / "model.safetensors").write_bytes(b"same-base-weights")
        (directory / "config.json").write_text("{}", encoding="utf-8")
    return evaluator, runtime


def _dapt_provenance(
    root: Path,
    manifest_path: Path,
    merged: Path,
) -> dict[str, object]:
    from hashlib import sha256

    def record(path: Path) -> dict[str, int | str]:
        return {
            "bytes": path.stat().st_size,
            "sha256": sha256(path.read_bytes()).hexdigest(),
        }

    return {
        "artifact_manifest": {
            "path": manifest_path.relative_to(root).as_posix(),
            **record(manifest_path),
        },
        "merged_fp32_artifact_files": {
            "merged_fp32/config.json": record(merged / "config.json"),
            "merged_fp32/model.safetensors": record(merged / "model.safetensors"),
        },
    }


def _parity_vectors() -> tuple[
    dict[str, list[dict[str, str]]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    inputs = {
        "NEWS": [{"item_id": "news-1", "source_record_sha256": "1" * 64}],
        "DISCLOSURE": [
            {"item_id": "disclosure-1", "source_record_sha256": "2" * 64}
        ],
    }
    evaluator: list[dict[str, object]] = [
        {"item_id": "news-1", "label": "POSITIVE", "logits": [-1.0, 0.0, 2.0]},
        {
            "item_id": "disclosure-1",
            "label": "NEGATIVE",
            "logits": [2.0, 0.0, -1.0],
        },
    ]
    runtime = copy.deepcopy(evaluator)
    runtime[0]["logits"] = [-1.0, 0.0, 2.0 + LOGITS_MAX_ABS_ERROR_TOLERANCE / 2]
    return inputs, evaluator, runtime


def _reservation_commitments(
    inputs: dict[str, list[dict[str, str]]],
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for source, rows in inputs.items():
        result[source] = {
            "sample_count": len(rows),
            "item_id_set_sha256": canonical_json_sha256(
                sorted(row["item_id"] for row in rows)
            ),
            "source_record_set_sha256": canonical_json_sha256(
                sorted(rows, key=lambda row: row["item_id"])
            ),
        }
    return result
