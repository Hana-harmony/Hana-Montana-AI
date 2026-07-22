from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY,
    validate_source_hierarchical_artifact,
)
from hannah_montana_ai.services.sentiment_release import (
    LOCAL_ATTESTATION_MODE,
    V6_REQUIRED_RUNTIME_CODE,
    SentimentReleaseError,
    verify_sentiment_release,
)
from hannah_montana_ai.services.sentiment_runtime_parity import (
    build_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    canonical_json_sha256,
)

REAL_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _script_module(name: str, relative: str) -> ModuleType:
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, REAL_PROJECT_ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"script module을 불러올 수 없습니다: {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _reservation_row(source: str) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": "k-fnspid-sentiment-review-row/v1",
        "review_key": f"fixture-{source.casefold()}-1",
        "source_type": source,
        "partition": (
            "CONFIRMATORY_SEALED_TEST_REVIEW"
            if source == "NEWS"
            else "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW"
        ),
        "review_status": "NEEDS_BLIND_REVIEW",
        "final_sentiment": "",
        "text": "영업 이익 개선",
    }
    if source == "DISCLOSURE":
        row["target_security"] = "005930"
    return row


def _reservation_commitment(
    *,
    source: str,
    path: Path,
    evidence: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    records = evidence["input_contract"]["sources"][source]
    item_ids = sorted(str(record["item_id"]) for record in records)
    source_records = sorted(records, key=lambda record: str(record["item_id"]))
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": _file_sha256(path),
        "bytes": path.stat().st_size,
        "sample_count": len(records),
        "partition": (
            "CONFIRMATORY_SEALED_TEST_REVIEW"
            if source == "NEWS"
            else "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW"
        ),
        "source_type": source,
        "item_id_set_sha256": canonical_json_sha256(item_ids),
        "source_record_set_sha256": canonical_json_sha256(source_records),
    }


def _copy_runtime_contract(root: Path) -> None:
    for relative in V6_REQUIRED_RUNTIME_CODE:
        source = REAL_PROJECT_ROOT / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def test_real_tiny_v6_lock_eval_parity_promotion_release_e2e(tmp_path: Path) -> None:
    evaluator = _script_module(
        "v6_e2e_evaluator",
        "scripts/evaluate_locked_kf_deberta_sentiment.py",
    )
    parity_generator = _script_module(
        "v6_e2e_parity_generator",
        "scripts/generate_sentiment_cpu_runtime_parity.py",
    )
    promoter = _script_module(
        "v6_e2e_promoter",
        "scripts/promote_kf_deberta_sentiment_deployment.py",
    )
    fixture_builder = _script_module(
        "v6_e2e_fixture_builder",
        "tests/test_source_hierarchical_sentiment_runtime.py",
    )
    root = tmp_path / "project"
    fixture_root = root / "fixture"
    fixture_root.mkdir(parents=True)
    artifact, training_source, _production_benchmark, base = (
        fixture_builder._write_real_v6_fixture(fixture_root)
    )
    locked_artifact = root / "artifacts/sentiment/locked"
    shutil.copytree(artifact, locked_artifact)
    training_path = root / "reports/v6-training.json"
    training_path.parent.mkdir(parents=True)
    shutil.copy2(training_source, training_path)
    contract = validate_source_hierarchical_artifact(locked_artifact)

    news_reservation = root / "data/gold/news-fixture.jsonl"
    disclosure_reservation = root / "data/gold/disclosure-fixture.jsonl"
    _write_json(news_reservation, _reservation_row("NEWS"))
    news_reservation.write_text(news_reservation.read_text(encoding="utf-8") + "\n")
    _write_json(disclosure_reservation, _reservation_row("DISCLOSURE"))
    disclosure_reservation.write_text(
        disclosure_reservation.read_text(encoding="utf-8") + "\n"
    )
    parity = parity_generator.generate_evidence(
        candidate_artifact=locked_artifact,
        evaluator_base_model=base,
        packaged_runtime_base_model=base,
        news_reservation=news_reservation,
        disclosure_reservation=disclosure_reservation,
        project_root=root,
    )
    parity_path = root / "reports/v6-runtime-parity.json"
    _write_json(parity_path, parity)
    reservations = {
        source: _reservation_commitment(
            source=source,
            path=news_reservation if source == "NEWS" else disclosure_reservation,
            evidence=parity,
            root=root,
        )
        for source in ("NEWS", "DISCLOSURE")
    }
    parity_lock = build_runtime_parity_lock_commitment(
        evidence_path=parity_path,
        project_root=root,
        expected_candidate_version=contract.version,
        expected_candidate_artifact_manifest_sha256=contract.locked_manifest_sha256,
        expected_candidate_model_family=MODEL_FAMILY,
        expected_base_source_kind=contract.base_source_kind,
        sealed_reservations=reservations,
    )
    lock = {
        "schema_version": "sentiment-candidate-lock/v2",
        "locked_at": "2026-07-16T00:00:00+00:00",
        "selection_only": True,
        "public_test_evaluated_before_lock": False,
        "operational_sealed_gold_evaluated_before_lock": False,
        "external_git_commitment_required": True,
        "sealed_reservations": reservations,
        "runtime_parity": parity_lock,
        "winner": {
            "model_family": MODEL_FAMILY,
            "version": contract.version,
            "report_path": training_path.relative_to(root).as_posix(),
            "report_sha256": _file_sha256(training_path),
            "locked_artifact_dir": locked_artifact.relative_to(root).as_posix(),
            "artifact_files": contract.locked_manifest,
            "artifact_manifest_sha256": contract.locked_manifest_sha256,
            "base_source_kind": contract.base_source_kind,
            "base_source": contract.base_source,
        },
    }
    lock_path = root / "reports/sentiment-candidate-lock.json"
    _write_json(lock_path, lock)

    mock_rows = [
        {
            "fixture_only": True,
            "item_id": "mock-news",
            "text": "영업 이익 개선",
            "source_type": "NEWS",
            "target_security": "",
        },
        {
            "fixture_only": True,
            "item_id": "mock-disclosure",
            "text": "영업 이익 개선",
            "source_type": "DISCLOSURE",
            "target_security": "005930",
        },
    ]
    benchmark = evaluator.build_v6_contract_evaluation_fixture(
        rows=mock_rows,
        artifact_dir=locked_artifact,
        base_model_dir=base,
        candidate_lock=lock,
        batch_size=2,
    )
    benchmark_path = root / "reports/v6-evaluation-fixture.json"
    _write_json(benchmark_path, benchmark)
    _copy_runtime_contract(root)

    releases_root = root / "releases/sentiment"
    current = releases_root / "current.json"
    promoted = promoter.promote_candidate(
        project_root=root,
        lock_manifest=lock_path,
        locked_artifact=locked_artifact,
        candidate_report=training_path,
        benchmark_report=benchmark_path,
        base_model_path=base,
        runtime_base_model_path=Path("/release-tree-bound-v6"),
        releases_root=releases_root,
        current_pointer=current,
        source_git_commit="0" * 40,
        source_dirty=True,
        synthetic_fixture=True,
    )

    verified = verify_sentiment_release(
        current,
        Path("/release-tree-bound-v6"),
        project_root=root,
        runtime_environment="test",
        attestation_mode=LOCAL_ATTESTATION_MODE,
    )
    assert promoted["release_mode"] == "SYNTHETIC_CONTRACT_FIXTURE"
    assert verified.release_id == promoted["release_id"]
    assert verified.version == contract.version
    assert verified.base_model_path.is_relative_to(releases_root)
    assert verified.base_model_path.name == "pinned_raw"
    assert benchmark["fixture_contract"]["real_labels_opened"] is False
    assert all("prediction" in row for row in benchmark["mock_predictions"])

    with pytest.raises(SentimentReleaseError, match="synthetic.*production"):
        verify_sentiment_release(
            current,
            Path("/release-tree-bound-v6"),
            project_root=root,
            runtime_environment="production",
            attestation_mode=LOCAL_ATTESTATION_MODE,
            expected_release_id=str(promoted["release_id"]),
            expected_git_commit="0" * 40,
        )
