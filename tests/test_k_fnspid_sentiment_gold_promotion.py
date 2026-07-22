from __future__ import annotations

import importlib.util
import json
import stat
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from hannah_montana_ai.training.dataset import load_labeled_alerts
from tests.sentiment_review_provenance_fixture import (
    build_verified_dual_review_provenance,
)


def _load_script() -> ModuleType:
    path = Path("scripts/promote_k_fnspid_sentiment_gold.py")
    spec = importlib.util.spec_from_file_location("promote_k_fnspid_sentiment_gold", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = _load_script()


def test_teacher_and_promotion_provenance_contracts_match() -> None:
    path = Path("scripts/label_k_fnspid_sentiment_with_qwen.py")
    spec = importlib.util.spec_from_file_location("label_k_fnspid_sentiment_contract", path)
    assert spec is not None and spec.loader is not None
    labeler = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = labeler
    spec.loader.exec_module(labeler)

    assert MODULE.PROMPT_VERSION == labeler.PROMPT_VERSION
    assert MODULE.OPERATIONAL_RULES_SHA256 == labeler.OPERATIONAL_RULES_SHA256
    assert MODULE.GOLD_REVIEWER_VISIBILITY == labeler.GOLD_REVIEWER_VISIBILITY
    assert (
        MODULE.CANDIDATE_PREDICTION_VISIBILITY
        == labeler.CANDIDATE_PREDICTION_VISIBILITY
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _review_rows() -> list[dict[str, Any]]:
    return [
        {
            "schema_version": MODULE.REVIEW_SCHEMA_VERSION,
            "dataset_version": "K-FNSPID-v4",
            "partition": "TRAIN_REVIEW",
            "document_id": f"doc-{index}",
            "source_type": "NEWS" if index < 2 else "DISCLOSURE",
            "stock_code": f"00000{index}",
            "stock_name": f"테스트기업{index}",
            "title": f"테스트기업{index} 영업이익 변화",
            "snippet": f"테스트기업{index}의 영업이익 관련 사실이 확인됐다.",
            "text": f"테스트기업{index} 영업이익 변화 [SEP] 관련 사실이 확인됐다.",
            "source_url": f"https://news.example/{index}",
            "canonical_url": f"https://news.example/{index}",
            "content_hash": f"content-{index}",
            "provider": "TEST_PROVIDER" if index < 2 else "OPENDART",
            "published_at_kst": f"2024-01-0{index + 1}T09:00:00+09:00",
            "effective_trade_date": f"2024-01-0{index + 1}",
            "event_cluster_id": f"event-{index}",
            "codebook_version": MODULE.CODEBOOK_VERSION,
            "review_status": "NEEDS_BLIND_REVIEW",
            "final_sentiment": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "review_note": "",
        }
        for index in range(3)
    ]


def _teacher_rows(review_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = ("POSITIVE", "NEUTRAL", "NEGATIVE")
    codebook_path = MODULE.DEFAULT_CODEBOOK_PATH.resolve()
    codebook_sha256 = sha256(codebook_path.read_bytes()).hexdigest()
    rows: list[dict[str, Any]] = []
    for index, source_record in enumerate(review_rows):
        source_sha256 = MODULE._canonical_sha256(source_record)
        item_id = MODULE._resolve_item_id(source_record, source_sha256)
        text, input_scope = MODULE._resolve_teacher_text(source_record, "test")
        teacher_input = {
            "item_id": item_id,
            "source_type": source_record["source_type"],
            "target_security": MODULE._resolve_target_security(source_record),
            "input_scope": input_scope,
            "text": text,
        }
        rows.append(
            {
                "schema_version": MODULE.TEACHER_SCHEMA_VERSION,
                "item_id": item_id,
                "source_record": source_record,
                "source_record_sha256": source_sha256,
                "teacher_input": teacher_input,
                "teacher_input_sha256": MODULE._canonical_sha256(teacher_input),
                "teacher_input_truncated": False,
                "sentiment": labels[index],
                "confidence": 0.91 - index * 0.1,
                "rationale": "대상 기업의 경제적 방향을 문서에서 확인했다.",
                "label_quality": "SILVER",
                "review_status": "needs_codex_review",
                "needs_codex_review": True,
                "teacher_provider": MODULE.TEACHER_PROVIDER,
                "teacher_model_requested": "Qwen3-4B-GGUF-Q4",
                "teacher_model_served": "Qwen3-4B-GGUF-Q4",
                "teacher_endpoint_scope": MODULE.TEACHER_ENDPOINT_SCOPE,
                "prompt_version": MODULE.PROMPT_VERSION,
                "operational_rules_sha256": MODULE.OPERATIONAL_RULES_SHA256,
                "sampling_seed": MODULE.TEACHER_SAMPLING_SEED,
                "codebook_path": MODULE._display_path(codebook_path),
                "codebook_sha256": codebook_sha256,
                "gold_reviewer_visibility": MODULE.GOLD_REVIEWER_VISIBILITY,
                "candidate_prediction_visibility": MODULE.CANDIDATE_PREDICTION_VISIBILITY,
                "model_blind": True,
                "market_blind": True,
                "generated_at_utc": "2026-07-15T12:00:00+00:00",
            }
        )
    return rows


def _decisions(teacher_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = ("POSITIVE", "POSITIVE", "NEGATIVE")
    return [
        {
            "schema_version": "k-fnspid-sentiment-dual-review-decision/v1",
            "item_id": row["item_id"],
            "reviewer_1": {
                "stage_1": "NEUTRAL" if labels[index] == "NEUTRAL" else "DIRECTIONAL",
                "stage_2": labels[index] if labels[index] != "NEUTRAL" else "NOT_APPLICABLE",
                "final_sentiment": labels[index],
                "label_evidence": "1차 독립 근거",
                "decision_path": "NEUTRAL_DIRECTIONAL_THEN_POLARITY",
                "reviewer_id": "codex-stage-1",
                "reviewed_at": "2026-07-15T12:00:00+00:00",
                "reviewer_type": "CODEX_AI",
                "model_blind": True,
                "market_blind": True,
            },
            "reviewer_2": {
                "stage_1": "NEUTRAL" if labels[index] == "NEUTRAL" else "DIRECTIONAL",
                "stage_2": labels[index] if labels[index] != "NEUTRAL" else "NOT_APPLICABLE",
                "final_sentiment": labels[index],
                "label_evidence": "2차 독립 근거",
                "decision_path": "NEUTRAL_DIRECTIONAL_THEN_POLARITY",
                "reviewer_id": "codex-stage-2",
                "reviewed_at": "2026-07-15T12:10:00+00:00",
                "reviewer_type": "CODEX_AI",
                "model_blind": True,
                "market_blind": True,
            },
            "independent_reviewer_count": 2,
            "inter_reviewer_agreement": True,
            "decision_path": "INDEPENDENT_REVIEWER_AGREEMENT",
            "adjudication": None,
            "final_sentiment": labels[index],
            "review_note": "코드북에 따라 문서 내 대상 기업의 방향성을 독립 판정했다.",
            "reviewer_id": "codex-stage-1+codex-stage-2",
            "reviewed_at": "2026-07-15T12:30:00+00:00",
            "review_status": MODULE.APPROVED_STATUS,
            "reviewer_type": "INDEPENDENT_CODEX_AI",
            "model_blind": True,
            "market_blind": True,
        }
        for index, row in enumerate(teacher_rows)
    ]


def _packet_paths(tmp_path: Path) -> dict[str, Path]:
    return {
        "review": tmp_path / "review.jsonl",
        "teacher": tmp_path / "teacher.jsonl",
        "decisions": tmp_path / "decisions.jsonl",
        "output": tmp_path / "gold.jsonl",
        "report": tmp_path / "report.json",
        "provenance": tmp_path / "dual-review-provenance.json",
    }


def _write_valid_packet(
    tmp_path: Path,
) -> tuple[dict[str, Path], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    paths = _packet_paths(tmp_path)
    review_rows = _review_rows()
    teacher_rows = _teacher_rows(review_rows)
    decisions = _decisions(teacher_rows)
    _write_jsonl(paths["review"], review_rows)
    _write_jsonl(paths["teacher"], teacher_rows)
    _write_jsonl(paths["decisions"], decisions)
    paths["provenance"] = build_verified_dual_review_provenance(
        root=tmp_path,
        review_path=paths["review"],
        final_decisions=decisions,
        final_decisions_path=paths["decisions"],
    )
    return paths, review_rows, teacher_rows, _read_jsonl(paths["decisions"])


def _promote(paths: dict[str, Path]) -> Any:
    return MODULE.promote_gold(
        review_path=paths["review"],
        teacher_path=paths["teacher"],
        decisions_path=paths["decisions"],
        output_path=paths["output"],
        report_path=paths["report"],
        review_provenance_path=paths["provenance"],
    )


def _refresh_provenance(paths: dict[str, Path]) -> None:
    run_index = len(list(paths["review"].parent.glob("provenance-run-*"))) + 1
    root = paths["review"].parent / f"provenance-run-{run_index}"
    root.mkdir()
    paths["provenance"] = build_verified_dual_review_provenance(
        root=root,
        review_path=paths["review"],
        final_decisions=_read_jsonl(paths["decisions"]),
        final_decisions_path=paths["decisions"],
    )


def test_promotion_requires_exact_provenance_and_writes_loadable_gold_atomically(
    tmp_path: Path,
) -> None:
    paths, review_rows, teacher_rows, _ = _write_valid_packet(tmp_path)

    summary = _promote(paths)

    gold_rows = _read_jsonl(paths["output"])
    samples = load_labeled_alerts(paths["output"])
    report = json.loads(paths["report"].read_text(encoding="utf-8"))
    assert summary.sample_count == 3
    assert summary.agreement_count == 2
    assert summary.disagreement_count == 1
    assert len(samples) == 3
    assert all(sample.tags == [] and sample.importance == "MEDIUM" for sample in samples)
    assert all(sample.source_review_status == MODULE.APPROVED_STATUS for sample in samples)
    assert [row["sentiment"] for row in gold_rows] == ["POSITIVE", "POSITIVE", "NEGATIVE"]
    assert all(row["label_quality"] == "GOLD" for row in gold_rows)
    assert all(row["needs_codex_review"] is False for row in gold_rows)
    assert len({row["promoted_at"] for row in gold_rows}) == 1
    assert report["status"] == "pass"
    assert report["sample_count"] == 3
    assert report["independent_reviewer_agreement"]["agreement_rate"] == 1.0
    assert report["qwen_final_agreement"]["agreement_rate"] == pytest.approx(2 / 3, 1e-6)
    assert report["qwen_final_agreement"]["transition_distribution"] == {"NEUTRAL->POSITIVE": 1}
    assert report["label_distribution"] == {"NEGATIVE": 1, "POSITIVE": 2}
    assert report["coverage"]["source_type_distribution"] == {
        "DISCLOSURE": 1,
        "NEWS": 2,
    }
    assert report["coverage"]["stock_count"] == 3
    assert report["coverage"]["event_count"] == 3
    assert report["file_sha256"]["gold_output"] == sha256(paths["output"].read_bytes()).hexdigest()
    assert report["file_sha256"]["review_input"] == sha256(paths["review"].read_bytes()).hexdigest()
    assert report["provenance"]["teacher"]["prompt_version"] == MODULE.PROMPT_VERSION
    assert report["provenance"]["teacher"]["codebook_sha256"] == teacher_rows[0]["codebook_sha256"]
    assert report["integrity"]["review_teacher_item_sets_exact"] is True
    assert gold_rows[0]["source_record_sha256"] == MODULE._canonical_sha256(review_rows[0])
    assert gold_rows[0]["independent_reviewer_count"] == 2
    assert gold_rows[0]["annotation_protocol"] == MODULE.CODEBOOK_VERSION
    assert gold_rows[0]["candidate_manifest_sha256"] == "NOT_APPLICABLE_PRE_LOCK_DEVELOPMENT"
    assert stat.S_IMODE(paths["output"].stat().st_mode) == 0o600
    assert stat.S_IMODE(paths["report"].stat().st_mode) == 0o600
    assert not list(tmp_path.glob(".*.tmp"))


@pytest.mark.parametrize("artifact", ["teacher", "decisions"])
def test_promotion_rejects_missing_item_from_any_input_set(
    tmp_path: Path,
    artifact: str,
) -> None:
    paths, _, teacher_rows, decisions = _write_valid_packet(tmp_path)
    rows = teacher_rows if artifact == "teacher" else decisions
    _write_jsonl(paths[artifact], rows[:-1])

    with pytest.raises(ValueError, match="item_id 집합"):
        _promote(paths)

    assert not paths["output"].exists()


def test_teacher_silver_alone_can_never_be_promoted_to_gold(tmp_path: Path) -> None:
    paths, _, _, _ = _write_valid_packet(tmp_path)
    paths["decisions"].unlink()

    with pytest.raises(FileNotFoundError, match="Codex decisions"):
        _promote(paths)

    assert not paths["output"].exists()


def test_duplicate_codex_decision_is_rejected(tmp_path: Path) -> None:
    paths, _, _, decisions = _write_valid_packet(tmp_path)
    _write_jsonl(paths["decisions"], decisions + [decisions[0]])

    with pytest.raises(ValueError, match="중복 item_id"):
        _promote(paths)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("final_sentiment", "BULLISH"),
        ("review_status", "needs_codex_review"),
        ("reviewer_id", ""),
        ("review_note", ""),
        ("reviewed_at", ""),
        ("reviewed_at", "2026-07-15T12:30:00"),
    ],
)
def test_illegal_or_incomplete_codex_decision_is_rejected(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    paths, _, _, decisions = _write_valid_packet(tmp_path)
    decisions[0][field] = value
    _write_jsonl(paths["decisions"], decisions)

    with pytest.raises(ValueError):
        _promote(paths)


def test_codex_decision_with_unexpected_field_is_rejected(tmp_path: Path) -> None:
    paths, _, _, decisions = _write_valid_packet(tmp_path)
    decisions[0]["teacher_override"] = True
    _write_jsonl(paths["decisions"], decisions)

    with pytest.raises(ValueError, match="스키마"):
        _promote(paths)


@pytest.mark.parametrize(
    "mutation",
    [
        "source_record",
        "source_record_sha256",
        "teacher_input_sha256",
        "prompt_version",
        "model_blind",
    ],
)
def test_teacher_hash_or_provenance_tampering_is_rejected(
    tmp_path: Path,
    mutation: str,
) -> None:
    paths, _, teacher_rows, _ = _write_valid_packet(tmp_path)
    if mutation == "source_record":
        teacher_rows[0]["source_record"]["title"] = "변조된 제목"
    elif mutation == "model_blind":
        teacher_rows[0][mutation] = False
    else:
        teacher_rows[0][mutation] = "0" * 64
    _write_jsonl(paths["teacher"], teacher_rows)

    with pytest.raises(ValueError):
        _promote(paths)


def test_codebook_file_hash_must_match_teacher_provenance(tmp_path: Path) -> None:
    paths, _, _, _ = _write_valid_packet(tmp_path)
    changed_codebook = tmp_path / "codebook.md"
    changed_codebook.write_text(
        MODULE.DEFAULT_CODEBOOK_PATH.read_text(encoding="utf-8") + "\n변경\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="codebook_path|codebook_sha256"):
        MODULE.promote_gold(
            review_path=paths["review"],
            teacher_path=paths["teacher"],
            decisions_path=paths["decisions"],
            output_path=paths["output"],
            report_path=paths["report"],
            codebook_path=changed_codebook,
            review_provenance_path=paths["provenance"],
        )


def test_validation_failure_does_not_replace_existing_output(tmp_path: Path) -> None:
    paths, _, _, decisions = _write_valid_packet(tmp_path)
    paths["output"].write_bytes(b"existing-gold\n")
    paths["report"].write_bytes(b"existing-report\n")
    original_output = paths["output"].read_bytes()
    original_report = paths["report"].read_bytes()
    decisions[0]["reviewer_id"] = ""
    _write_jsonl(paths["decisions"], decisions)

    with pytest.raises(ValueError):
        _promote(paths)

    assert paths["output"].read_bytes() == original_output
    assert paths["report"].read_bytes() == original_report


def test_successful_gold_promotion_is_write_once(tmp_path: Path) -> None:
    paths, _, _, _ = _write_valid_packet(tmp_path)
    _promote(paths)

    with pytest.raises(ValueError, match="다시 승격"):
        _promote(paths)


def test_sealed_gold_requires_candidate_lock_manifest(tmp_path: Path) -> None:
    paths, review_rows, teacher_rows, decisions = _write_valid_packet(tmp_path)
    for row in review_rows:
        row["partition"] = "SEALED_TEST_REVIEW"
    teacher_rows = _teacher_rows(review_rows)
    decisions = _decisions(teacher_rows)
    _write_jsonl(paths["review"], review_rows)
    _write_jsonl(paths["teacher"], teacher_rows)
    _write_jsonl(paths["decisions"], decisions)
    _refresh_provenance(paths)

    with pytest.raises(ValueError, match="candidate lock"):
        _promote(paths)


def _write_candidate_lock(
    path: Path,
    *,
    locked_at: str,
    review_path: Path | None = None,
    partition: str = "CONFIRMATORY_SEALED_TEST_REVIEW",
    schema_version: str = "sentiment-candidate-lock/v1",
) -> None:
    sealed_reservations: dict[str, Any] = {}
    if review_path is not None:
        rows = _read_jsonl(review_path)
        sealed_reservations["NEWS"] = {
            "path": str(review_path.relative_to(path.parent)),
            "sha256": sha256(review_path.read_bytes()).hexdigest(),
            "bytes": review_path.stat().st_size,
            "sample_count": len(rows),
            "partition": partition,
            "source_type": "NEWS",
        }
    path.write_text(
        json.dumps(
            {
                "schema_version": schema_version,
                "locked_at": locked_at,
                "selection_only": True,
                "public_test_evaluated_before_lock": False,
                "operational_sealed_gold_evaluated_before_lock": False,
                "external_git_commitment_required": True,
                "sealed_reservations": sealed_reservations,
            }
        ),
        encoding="utf-8",
    )


def _stub_git_attestation(
    monkeypatch: pytest.MonkeyPatch,
    lock_path: Path,
    *,
    committer_time: str = "2026-07-15T11:59:58+00:00",
) -> Path:
    attestation_path = lock_path.parent / "git-attestation.json"
    attestation_path.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(
        MODULE,
        "validate_candidate_git_attestation",
        lambda *_args, **_kwargs: {
            "candidate_lock_sha256": sha256(lock_path.read_bytes()).hexdigest(),
            "sha256": "a" * 64,
            "commit_sha": "b" * 40,
            "committer_time_iso": committer_time,
        },
    )
    return attestation_path


def _make_news_only(review_rows: list[dict[str, Any]]) -> None:
    for row in review_rows:
        row["source_type"] = "NEWS"


@pytest.mark.parametrize(
    "lock_schema_version",
    ["sentiment-candidate-lock/v1", "sentiment-candidate-lock/v2"],
)
def test_sealed_gold_accepts_only_decisions_created_after_candidate_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    lock_schema_version: str,
) -> None:
    paths, review_rows, teacher_rows, decisions = _write_valid_packet(tmp_path)
    for row in review_rows:
        row["partition"] = "CONFIRMATORY_SEALED_TEST_REVIEW"
    _make_news_only(review_rows)
    teacher_rows = _teacher_rows(review_rows)
    decisions = _decisions(teacher_rows)
    _write_jsonl(paths["review"], review_rows)
    _write_jsonl(paths["teacher"], teacher_rows)
    _write_jsonl(paths["decisions"], decisions)
    _refresh_provenance(paths)
    lock_path = tmp_path / "candidate-lock.json"
    _write_candidate_lock(
        lock_path,
        locked_at="2026-07-15T11:59:59+00:00",
        review_path=paths["review"],
        schema_version=lock_schema_version,
    )
    attestation_path = _stub_git_attestation(monkeypatch, lock_path)

    summary = MODULE.promote_gold(
        review_path=paths["review"],
        teacher_path=paths["teacher"],
        decisions_path=paths["decisions"],
        output_path=paths["output"],
        report_path=paths["report"],
        review_provenance_path=paths["provenance"],
        candidate_lock_path=lock_path,
        candidate_git_attestation_path=attestation_path,
        project_root=tmp_path,
    )

    assert summary.sample_count == 3
    assert all(
        row["candidate_manifest_sha256"] == sha256(lock_path.read_bytes()).hexdigest()
        for row in _read_jsonl(paths["output"])
    )
    assert all(
        row["candidate_git_attestation_sha256"] == "a" * 64
        and row["candidate_git_commit_sha"] == "b" * 40
        for row in _read_jsonl(paths["output"])
    )


def test_sealed_gold_requires_candidate_git_attestation(tmp_path: Path) -> None:
    paths, review_rows, _, _ = _write_valid_packet(tmp_path)
    for row in review_rows:
        row["partition"] = "CONFIRMATORY_SEALED_TEST_REVIEW"
    _make_news_only(review_rows)
    teacher_rows = _teacher_rows(review_rows)
    decisions = _decisions(teacher_rows)
    _write_jsonl(paths["review"], review_rows)
    _write_jsonl(paths["teacher"], teacher_rows)
    _write_jsonl(paths["decisions"], decisions)
    _refresh_provenance(paths)
    lock_path = tmp_path / "candidate-lock.json"
    _write_candidate_lock(
        lock_path,
        locked_at="2026-07-15T11:59:59+00:00",
        review_path=paths["review"],
    )

    with pytest.raises(ValueError, match="Git attestation"):
        MODULE.promote_gold(
            review_path=paths["review"],
            teacher_path=paths["teacher"],
            decisions_path=paths["decisions"],
            output_path=paths["output"],
            report_path=paths["report"],
            review_provenance_path=paths["provenance"],
            candidate_lock_path=lock_path,
            project_root=tmp_path,
        )


@pytest.mark.parametrize(
    "timestamp_path",
    ["teacher", "reviewer_1", "reviewer_2", "final"],
)
def test_sealed_gold_rejects_any_pre_lock_decision_timestamp(
    tmp_path: Path,
    timestamp_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths, review_rows, teacher_rows, decisions = _write_valid_packet(tmp_path)
    for row in review_rows:
        row["partition"] = "CONFIRMATORY_SEALED_TEST_REVIEW"
    _make_news_only(review_rows)
    teacher_rows = _teacher_rows(review_rows)
    decisions = _decisions(teacher_rows)
    if timestamp_path == "teacher":
        teacher_rows[0]["generated_at_utc"] = "2026-07-15T11:59:59+00:00"
    elif timestamp_path == "final":
        decisions[0]["reviewed_at"] = "2026-07-15T11:59:59+00:00"
    else:
        decisions[0][timestamp_path]["reviewed_at"] = "2026-07-15T11:59:59+00:00"
    _write_jsonl(paths["review"], review_rows)
    _write_jsonl(paths["teacher"], teacher_rows)
    _write_jsonl(paths["decisions"], decisions)
    _refresh_provenance(paths)
    if timestamp_path == "final":
        refreshed = _read_jsonl(paths["decisions"])
        refreshed[0]["reviewed_at"] = "2026-07-15T11:59:59+00:00"
        _write_jsonl(paths["decisions"], refreshed)
    lock_path = tmp_path / "candidate-lock.json"
    _write_candidate_lock(
        lock_path,
        locked_at="2026-07-15T12:00:00+00:00",
        review_path=paths["review"],
    )
    attestation_path = _stub_git_attestation(monkeypatch, lock_path)

    with pytest.raises(ValueError, match="candidate lock보다 빠릅니다"):
        MODULE.promote_gold(
            review_path=paths["review"],
            teacher_path=paths["teacher"],
            decisions_path=paths["decisions"],
            output_path=paths["output"],
            report_path=paths["report"],
            review_provenance_path=paths["provenance"],
            candidate_lock_path=lock_path,
            candidate_git_attestation_path=attestation_path,
            project_root=tmp_path,
        )


def test_teacher_input_truncation_must_preserve_source_prefix_and_suffix(
    tmp_path: Path,
) -> None:
    paths, review_rows, teacher_rows, _ = _write_valid_packet(tmp_path)
    review_rows[0]["text"] = "앞" * 400 + "뒤" * 400
    source_sha256 = MODULE._canonical_sha256(review_rows[0])
    item_id = MODULE._resolve_item_id(review_rows[0], source_sha256)
    truncated = (
        review_rows[0]["text"][:300] + MODULE.TRUNCATION_MARKER + review_rows[0]["text"][-80:]
    )
    teacher_rows[0]["source_record"] = review_rows[0]
    teacher_rows[0]["source_record_sha256"] = source_sha256
    teacher_rows[0]["teacher_input"]["item_id"] = item_id
    teacher_rows[0]["teacher_input"]["text"] = truncated
    teacher_rows[0]["teacher_input_sha256"] = MODULE._canonical_sha256(
        teacher_rows[0]["teacher_input"]
    )
    teacher_rows[0]["teacher_input_truncated"] = True
    decisions = _decisions(teacher_rows)
    _write_jsonl(paths["review"], review_rows)
    _write_jsonl(paths["teacher"], teacher_rows)
    _write_jsonl(paths["decisions"], decisions)
    _refresh_provenance(paths)

    summary = _promote(paths)

    assert summary.sample_count == 3


def test_output_or_input_symlink_is_rejected(tmp_path: Path) -> None:
    paths, _, _, _ = _write_valid_packet(tmp_path)
    real_output = tmp_path / "real-output.jsonl"
    real_output.write_text("safe\n", encoding="utf-8")
    paths["output"].symlink_to(real_output)

    with pytest.raises(ValueError, match="symlink"):
        _promote(paths)

    assert real_output.read_text(encoding="utf-8") == "safe\n"
