from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.k_fnspid_sentiment_review_provenance import (
    NONEXPOSURE_VALUE,
    REVIEW_PACKET_KIND,
    REVIEW_ROLE,
    VERIFIED_STATUS,
    assert_independent_receipts,
    create_review_receipt,
    sha256_file,
    validate_review_receipt,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _packet() -> list[dict[str, object]]:
    return [
        {
            "document_id": "doc-1",
            "stock_code": "000001",
            "source_type": "NEWS",
            "text": "대상 기업의 영업이익이 증가했다.",
            "review_status": "NEEDS_BLIND_REVIEW",
            "final_sentiment": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "review_note": "",
        },
        {
            "document_id": "doc-2",
            "stock_code": "000002",
            "source_type": "DISCLOSURE",
            "text": "대상 기업의 계약이 해지됐다.",
            "review_status": "NEEDS_BLIND_REVIEW",
            "final_sentiment": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "review_note": "",
        },
    ]


def _decisions(reviewer_id: str = "codex-reviewer-a") -> list[dict[str, object]]:
    return [
        {
            "item_id": "doc-1::000001",
            "final_sentiment": "POSITIVE",
            "review_note": "영업이익 증가가 명시되었다.",
            "reviewer_id": reviewer_id,
            "reviewed_at": "2026-07-16T01:01:00+00:00",
            "review_status": "CODEX_REVIEW_APPROVED",
        },
        {
            "item_id": "doc-2::000002",
            "final_sentiment": "NEGATIVE",
            "review_note": "계약 해지가 명시되었다.",
            "reviewer_id": reviewer_id,
            "reviewed_at": "2026-07-16T01:02:00+00:00",
            "review_status": "CODEX_REVIEW_APPROVED",
        },
    ]


def _artifacts(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    packet = tmp_path / "packet.jsonl"
    decision = tmp_path / "decision.jsonl"
    codebook = tmp_path / "codebook.md"
    prompt = tmp_path / "prompt.md"
    _write_jsonl(packet, _packet())
    _write_jsonl(decision, _decisions())
    codebook.write_bytes(Path("docs/datasets/k-fnspid-sentiment-codebook.md").read_bytes())
    prompt.write_bytes(Path("docs/datasets/k-fnspid-sentiment-review-prompt-v1.md").read_bytes())
    return packet, decision, codebook, prompt


def _create(
    tmp_path: Path,
    *,
    reviewer_id: str = "codex-reviewer-a",
    run_id: str = "11111111-1111-4111-8111-111111111111",
    context_id: str = "22222222-2222-4222-8222-222222222222",
) -> tuple[Path, Path, Path, Path, Path, dict[str, object]]:
    packet, decision, codebook, prompt = _artifacts(tmp_path)
    if reviewer_id != "codex-reviewer-a":
        _write_jsonl(decision, _decisions(reviewer_id))
    receipt_path = tmp_path / "receipt.json"
    receipt = create_review_receipt(
        packet_path=packet,
        decision_path=decision,
        codebook_path=codebook,
        prompt_path=prompt,
        output_path=receipt_path,
        packet_kind=REVIEW_PACKET_KIND,
        role=REVIEW_ROLE,
        reviewer_id=reviewer_id,
        reviewer_model="GPT-5",
        reviewer_model_version="2026-07-16",
        independent_run_id=run_id,
        context_id=context_id,
        row_start=1,
        row_end=2,
        run_started_at="2026-07-16T01:00:00+00:00",
        run_completed_at="2026-07-16T01:03:00+00:00",
    )
    return packet, decision, codebook, prompt, receipt_path, receipt


def test_receipt_binds_packet_codebook_prompt_model_run_context_and_range(
    tmp_path: Path,
) -> None:
    packet, decision, codebook, prompt, receipt_path, receipt = _create(tmp_path)

    validated = validate_review_receipt(
        receipt_path,
        packet_path=packet,
        decision_path=decision,
        codebook_path=codebook,
        prompt_path=prompt,
        expected_packet_kind=REVIEW_PACKET_KIND,
        expected_role=REVIEW_ROLE,
    )

    assert validated == receipt
    assert receipt["status"] == VERIFIED_STATUS
    assert receipt["reviewer"] == {
        "reviewer_id": "codex-reviewer-a",
        "reviewer_type": "CODEX_AI",
        "model_name": "GPT-5",
        "model_version": "2026-07-16",
    }
    assert receipt["input_scope"]["row_start_inclusive"] == 1
    assert receipt["input_scope"]["row_end_inclusive"] == 2
    assert receipt["artifacts"]["packet"]["sha256"] == sha256_file(packet)
    assert receipt["artifacts"]["codebook"]["sha256"] == sha256_file(codebook)
    assert receipt["artifacts"]["prompt"]["sha256"] == sha256_file(prompt)
    assert all(
        value == NONEXPOSURE_VALUE
        for value in receipt["blindness"].values()
        if isinstance(value, str)
    )


def test_receipt_supports_explicit_noncontiguous_packet_selection(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    decision = tmp_path / "decision.jsonl"
    codebook = tmp_path / "codebook.md"
    prompt = tmp_path / "prompt.md"
    rows = _packet()
    rows.append(
        {
            **rows[0],
            "document_id": "doc-3",
            "stock_code": "000003",
            "text": "대상 기업의 신규 계약이 체결됐다.",
        }
    )
    decisions = [_decisions()[0], {**_decisions()[0], "item_id": "doc-3::000003"}]
    _write_jsonl(packet, rows)
    _write_jsonl(decision, decisions)
    codebook.write_bytes(Path("docs/datasets/k-fnspid-sentiment-codebook.md").read_bytes())
    prompt.write_bytes(Path("docs/datasets/k-fnspid-sentiment-review-prompt-v1.md").read_bytes())
    receipt_path = tmp_path / "receipt.json"

    receipt = create_review_receipt(
        packet_path=packet,
        decision_path=decision,
        codebook_path=codebook,
        prompt_path=prompt,
        output_path=receipt_path,
        packet_kind=REVIEW_PACKET_KIND,
        role=REVIEW_ROLE,
        reviewer_id="codex-reviewer-a",
        reviewer_model="GPT-5",
        reviewer_model_version="2026-07-16",
        independent_run_id="11111111-1111-4111-8111-111111111111",
        context_id="22222222-2222-4222-8222-222222222222",
        row_start=1,
        row_end=3,
        selected_item_ids=["doc-1::000001", "doc-3::000003"],
        run_started_at="2026-07-16T01:00:00+00:00",
        run_completed_at="2026-07-16T01:03:00+00:00",
    )

    assert receipt["input_scope"]["selected_item_ids"] == [
        "doc-1::000001",
        "doc-3::000003",
    ]
    assert (
        validate_review_receipt(
            receipt_path,
            packet_path=packet,
            decision_path=decision,
            codebook_path=codebook,
            prompt_path=prompt,
            expected_packet_kind=REVIEW_PACKET_KIND,
            expected_role=REVIEW_ROLE,
        )
        == receipt
    )


def test_receipt_rejects_noncontiguous_selection_out_of_packet_order(
    tmp_path: Path,
) -> None:
    packet, decision, codebook, prompt = _artifacts(tmp_path)
    _write_jsonl(decision, list(reversed(_decisions())))

    with pytest.raises(ValueError, match="packet 순서"):
        create_review_receipt(
            packet_path=packet,
            decision_path=decision,
            codebook_path=codebook,
            prompt_path=prompt,
            output_path=tmp_path / "receipt.json",
            packet_kind=REVIEW_PACKET_KIND,
            role=REVIEW_ROLE,
            reviewer_id="codex-reviewer-a",
            reviewer_model="GPT-5",
            reviewer_model_version="2026-07-16",
            independent_run_id="11111111-1111-4111-8111-111111111111",
            context_id="22222222-2222-4222-8222-222222222222",
            row_start=1,
            row_end=2,
            selected_item_ids=["doc-2::000002", "doc-1::000001"],
            run_started_at="2026-07-16T01:00:00+00:00",
            run_completed_at="2026-07-16T01:03:00+00:00",
        )


@pytest.mark.parametrize("artifact", ["packet", "decision", "codebook", "prompt"])
def test_receipt_fails_closed_after_any_bound_artifact_mutation(
    tmp_path: Path,
    artifact: str,
) -> None:
    packet, decision, codebook, prompt, receipt_path, _ = _create(tmp_path)
    paths = {
        "packet": packet,
        "decision": decision,
        "codebook": codebook,
        "prompt": prompt,
    }
    paths[artifact].write_bytes(paths[artifact].read_bytes() + b"\n")

    with pytest.raises(ValueError, match="변경"):
        validate_review_receipt(
            receipt_path,
            packet_path=packet,
            decision_path=decision,
            codebook_path=codebook,
            prompt_path=prompt,
            expected_packet_kind=REVIEW_PACKET_KIND,
            expected_role=REVIEW_ROLE,
        )


@pytest.mark.parametrize("field", ["candidate_prediction", "teacher_sentiment", "probabilities"])
def test_receipt_rejects_any_candidate_or_teacher_signal_in_review_packet(
    tmp_path: Path,
    field: str,
) -> None:
    packet, decision, codebook, prompt = _artifacts(tmp_path)
    rows = _packet()
    rows[0][field] = "PROHIBITED"
    _write_jsonl(packet, rows)

    with pytest.raises(ValueError, match="금지 필드"):
        create_review_receipt(
            packet_path=packet,
            decision_path=decision,
            codebook_path=codebook,
            prompt_path=prompt,
            output_path=tmp_path / "receipt.json",
            packet_kind=REVIEW_PACKET_KIND,
            role=REVIEW_ROLE,
            reviewer_id="codex-reviewer-a",
            reviewer_model="GPT-5",
            reviewer_model_version="2026-07-16",
            independent_run_id="11111111-1111-4111-8111-111111111111",
            context_id="22222222-2222-4222-8222-222222222222",
            row_start=1,
            row_end=2,
            run_started_at="2026-07-16T01:00:00+00:00",
            run_completed_at="2026-07-16T01:03:00+00:00",
        )


def test_independence_gate_rejects_reused_context_even_with_different_reviewer(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    *_, first = _create(first_root)
    *_, second = _create(
        second_root,
        reviewer_id="codex-reviewer-b",
        run_id="33333333-3333-4333-8333-333333333333",
        context_id="22222222-2222-4222-8222-222222222222",
    )

    with pytest.raises(ValueError, match="context_id"):
        assert_independent_receipts([first, second])


def test_receipt_self_hash_tampering_is_rejected(tmp_path: Path) -> None:
    packet, decision, codebook, prompt, receipt_path, receipt = _create(tmp_path)
    receipt["reviewer"]["model_version"] = "forged"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    with pytest.raises(ValueError, match="자체 해시"):
        validate_review_receipt(
            receipt_path,
            packet_path=packet,
            decision_path=decision,
            codebook_path=codebook,
            prompt_path=prompt,
            expected_packet_kind=REVIEW_PACKET_KIND,
            expected_role=REVIEW_ROLE,
        )
