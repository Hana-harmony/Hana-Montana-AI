from __future__ import annotations

import importlib.util
import json
import stat
import sys
import urllib.error
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


def _load_script() -> ModuleType:
    path = Path("scripts/label_k_fnspid_sentiment_with_qwen.py")
    spec = importlib.util.spec_from_file_location("label_k_fnspid_sentiment_with_qwen", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = _load_script()


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self._body[:size] if size >= 0 else self._body


class _FakeTeacherClient:
    endpoint = "http://127.0.0.1:18081"
    model = "Qwen3-4B-GGUF-Q4"

    def __init__(self, *, fail_on_call: int | None = None) -> None:
        self.calls: list[list[str]] = []
        self.fail_on_call = fail_on_call

    def label_batch(
        self,
        items: list[Any],
        *,
        codebook_path: str,
        codebook_text: str,
        codebook_sha256: str,
    ) -> Any:
        del codebook_sha256
        assert codebook_path.endswith("codebook.md")
        assert "POSITIVE" in codebook_text
        self.calls.append([item.item_id for item in items])
        if self.fail_on_call == len(self.calls):
            raise RuntimeError("중단 시나리오")
        decisions = tuple(
            MODULE.TeacherDecision(
                item_id=item.item_id,
                sentiment="POSITIVE" if index % 2 == 0 else "NEUTRAL",
                confidence=0.91 - index * 0.1,
                rationale="문서에 대상 기업의 경제적 방향이 명시되었다.",
            )
            for index, item in enumerate(items)
        )
        return MODULE.TeacherBatchResult(decisions=decisions, served_model=self.model)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _input_rows(count: int = 3) -> list[dict[str, Any]]:
    return [
        {
            "document_id": f"doc-{index}",
            "source_type": "NEWS" if index % 2 == 0 else "DISCLOSURE",
            "title": f"테스트기업 {index} 영업이익 증가",
            "snippet": "영업이익이 전년 대비 증가했다.",
            "target_security": f"00000{index}",
            "source_url": f"https://news.example/{index}",
            "content_hash": f"hash-{index}",
            "event_cluster_id": f"event-{index}",
        }
        for index in range(count)
    ]


@pytest.mark.parametrize(
    "endpoint",
    ["http://127.0.0.1:18081", "https://127.0.0.2", "http://[::1]:18081/"],
)
def test_loopback_endpoint_accepts_only_literal_loopback_ip(endpoint: str) -> None:
    assert MODULE.validate_loopback_endpoint(endpoint) == endpoint.rstrip("/")


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://example.com",
        "http://localhost:18081",
        "http://0.0.0.0:18081",
        "http://127.0.0.1:18081/v1",
        "http://user:pass@127.0.0.1:18081",
        "file:///tmp/qwen.sock",
    ],
)
def test_loopback_endpoint_fails_closed(endpoint: str) -> None:
    with pytest.raises(ValueError):
        MODULE.validate_loopback_endpoint(endpoint)


def test_review_input_preserves_provenance_but_hides_existing_predictions(tmp_path: Path) -> None:
    input_path = tmp_path / "review.jsonl"
    row = _input_rows(1)[0] | {
        "sentiment": "NEGATIVE",
        "model_prediction": "MODEL_SHOULD_NOT_SEE",
        "confidence": 0.99,
        "market_return": 42.0,
    }
    _write_jsonl(input_path, [row])

    item = MODULE.read_review_items(input_path)[0]

    assert item.source_record == row
    assert item.teacher_input["text"].startswith("테스트기업")
    serialized_input = json.dumps(item.teacher_input, ensure_ascii=False)
    assert "MODEL_SHOULD_NOT_SEE" not in serialized_input
    assert "market_return" not in serialized_input
    assert "sentiment" not in item.teacher_input


def test_safe_batching_bounds_items_and_total_text(tmp_path: Path) -> None:
    input_path = tmp_path / "review.jsonl"
    rows = [
        {
            "document_id": f"long-{index}",
            "source_type": "NEWS",
            "text": "가" * 2_000,
            "target_security": f"00000{index}",
        }
        for index in range(15)
    ]
    _write_jsonl(input_path, rows)
    items = MODULE.read_review_items(input_path)

    batches = MODULE._safe_batches(items, max_items=32)

    assert [len(batch) for batch in batches] == [6, 6, 3]
    assert all(
        sum(len(item.teacher_input["text"]) for item in batch)
        <= MODULE.MAX_BATCH_TEXT_CHARS
        for batch in batches
    )


def test_qwen_client_sends_one_structured_batch_and_records_served_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "review.jsonl"
    _write_jsonl(input_path, _input_rows(2))
    items = MODULE.read_review_items(input_path)
    captured: dict[str, Any] = {}
    annotations = [
        {
            "item_id": item.item_id,
            "sentiment": "POSITIVE",
            "confidence": 0.8,
            "rationale": "영업이익 증가가 명시되었다.",
        }
        for item in items
    ]
    response_payload = {
        "model": "qwen-served-revision",
        "choices": [{"message": {"content": json.dumps({"annotations": annotations})}}],
    }

    def fake_urlopen(request: Any, timeout: float) -> _FakeResponse:
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse(response_payload)

    monkeypatch.setattr(MODULE.urllib.request, "urlopen", fake_urlopen)
    client = MODULE.QwenSentimentClient(timeout_seconds=7.5, max_attempts=1)

    result = client.label_batch(
        items,
        codebook_path="docs/codebook.md",
        codebook_text="# codebook\nPOSITIVE NEUTRAL NEGATIVE",
        codebook_sha256="a" * 64,
    )

    assert captured["url"] == "http://127.0.0.1:18081/v1/chat/completions"
    assert captured["timeout"] == 7.5
    request_payload = captured["payload"]
    assert request_payload["temperature"] == 0.0
    assert request_payload["seed"] == MODULE.SAMPLING_SEED
    assert request_payload["response_format"]["type"] == "json_schema"
    assert request_payload["response_format"]["json_schema"]["strict"] is True
    assert "docs/codebook.md" in request_payload["messages"][1]["content"]
    assert len(result.decisions) == 2
    assert result.served_model == "qwen-served-revision"


def test_qwen_client_retries_transient_transport_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "review.jsonl"
    _write_jsonl(input_path, _input_rows(1))
    items = MODULE.read_review_items(input_path)
    content = {
        "annotations": [
            {
                "item_id": items[0].item_id,
                "sentiment": "NEUTRAL",
                "confidence": 0.55,
                "rationale": "확정된 경제적 방향이 없다.",
            }
        ]
    }
    response = _FakeResponse({"choices": [{"message": {"content": json.dumps(content)}}]})
    attempts = 0

    def fake_urlopen(_request: Any, timeout: float) -> _FakeResponse:
        nonlocal attempts
        assert timeout == 1.0
        attempts += 1
        if attempts == 1:
            raise urllib.error.URLError("일시 오류")
        return response

    monkeypatch.setattr(MODULE.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(MODULE.time, "sleep", lambda _seconds: None)
    client = MODULE.QwenSentimentClient(
        timeout_seconds=1.0,
        max_attempts=2,
        retry_base_seconds=0.01,
    )

    result = client.label_batch(
        items,
        codebook_path="docs/codebook.md",
        codebook_text="POSITIVE NEUTRAL NEGATIVE",
        codebook_sha256="b" * 64,
    )

    assert attempts == 2
    assert result.decisions[0].sentiment == "NEUTRAL"


@pytest.mark.parametrize(
    "annotation",
    [
        {"item_id": "a", "sentiment": "BULLISH", "confidence": 0.5, "rationale": "x"},
        {"item_id": "a", "sentiment": "POSITIVE", "confidence": True, "rationale": "x"},
        {"item_id": "a", "sentiment": "POSITIVE", "confidence": 1.1, "rationale": "x"},
        {
            "item_id": "a",
            "sentiment": "POSITIVE",
            "confidence": 0.5,
            "rationale": "x",
            "unexpected": "field",
        },
    ],
)
def test_teacher_response_is_strictly_validated(annotation: dict[str, Any]) -> None:
    with pytest.raises(MODULE.TeacherResponseError):
        MODULE._validate_teacher_payload({"annotations": [annotation]}, ["a"])


def test_compact_teacher_response_maps_integer_codes() -> None:
    decisions = MODULE._validate_teacher_payload(
        [[1, 1, 93, 0], [2, 0, 61, 3], [3, -1, 88, 1]],
        ["1", "2", "3"],
    )

    assert [(row.sentiment, row.confidence, row.rationale) for row in decisions] == [
        ("POSITIVE", 0.93, "EXPLICIT_POSITIVE"),
        ("NEUTRAL", 0.61, "PROCEDURAL_FACT"),
        ("NEGATIVE", 0.88, "EXPLICIT_NEGATIVE"),
    ]


@pytest.mark.parametrize(
    "payload",
    [
        [[True, 1, 90, 0]],
        [[1, 2, 90, 0]],
        [[1, 1, 101, 0]],
        [[1, 1, 90, 6]],
        [[1, 1, 90]],
    ],
)
def test_compact_teacher_response_rejects_invalid_codes(payload: object) -> None:
    with pytest.raises(MODULE.TeacherResponseError):
        MODULE._validate_teacher_payload(payload, ["1"])


def test_label_packet_is_atomic_resumable_and_never_promotes_gold(tmp_path: Path) -> None:
    input_path = tmp_path / "review.jsonl"
    output_path = tmp_path / "silver.jsonl"
    codebook_path = tmp_path / "codebook.md"
    rows = _input_rows(3)
    _write_jsonl(input_path, rows)
    codebook_path.write_text("# codebook\nPOSITIVE NEUTRAL NEGATIVE\n", encoding="utf-8")
    client = _FakeTeacherClient()

    summary = MODULE.label_review_packet(
        input_path=input_path,
        output_path=output_path,
        codebook_path=codebook_path,
        client=client,
        batch_size=2,
    )
    output_rows = _read_jsonl(output_path)

    assert summary.input_count == 3
    assert summary.resumed_count == 0
    assert summary.labeled_count == 3
    assert client.calls == [["doc-0::000000", "doc-1::000001"], ["doc-2::000002"]]
    assert [row["source_record"] for row in output_rows] == rows
    assert all(row["label_quality"] == "SILVER" for row in output_rows)
    assert all(row["review_status"] == "needs_codex_review" for row in output_rows)
    assert all(row["needs_codex_review"] is True for row in output_rows)
    assert all("sentiment" not in row["teacher_input"] for row in output_rows)
    assert all(row["teacher_model_requested"] == client.model for row in output_rows)
    assert all(row["prompt_version"] == MODULE.PROMPT_VERSION for row in output_rows)
    assert all(
        row["gold_reviewer_visibility"] == MODULE.GOLD_REVIEWER_VISIBILITY
        and row["candidate_prediction_visibility"]
        == MODULE.CANDIDATE_PREDICTION_VISIBILITY
        for row in output_rows
    )
    assert all(row["model_blind"] is True and row["market_blind"] is True for row in output_rows)
    assert stat.S_IMODE(output_path.stat().st_mode) == 0o600
    assert not list(tmp_path.glob(".silver.jsonl.*.tmp"))

    resumed_client = _FakeTeacherClient()
    resumed = MODULE.label_review_packet(
        input_path=input_path,
        output_path=output_path,
        codebook_path=codebook_path,
        client=resumed_client,
        batch_size=1,
    )

    assert resumed.resumed_count == 3
    assert resumed.labeled_count == 0
    assert resumed_client.calls == []


def test_completed_batches_survive_failure_and_resume_only_missing_rows(tmp_path: Path) -> None:
    input_path = tmp_path / "review.jsonl"
    output_path = tmp_path / "silver.jsonl"
    codebook_path = tmp_path / "codebook.md"
    _write_jsonl(input_path, _input_rows(3))
    codebook_path.write_text("POSITIVE NEUTRAL NEGATIVE", encoding="utf-8")
    failing_client = _FakeTeacherClient(fail_on_call=2)

    with pytest.raises(RuntimeError, match="중단 시나리오"):
        MODULE.label_review_packet(
            input_path=input_path,
            output_path=output_path,
            codebook_path=codebook_path,
            client=failing_client,
            batch_size=2,
        )

    assert len(_read_jsonl(output_path)) == 2
    resumed_client = _FakeTeacherClient()
    summary = MODULE.label_review_packet(
        input_path=input_path,
        output_path=output_path,
        codebook_path=codebook_path,
        client=resumed_client,
        batch_size=2,
    )

    assert summary.resumed_count == 2
    assert summary.labeled_count == 1
    assert resumed_client.calls == [["doc-2::000002"]]
    assert len(_read_jsonl(output_path)) == 3


def test_missing_codebook_fails_before_any_teacher_request(tmp_path: Path) -> None:
    client = _FakeTeacherClient()

    with pytest.raises(FileNotFoundError, match="코드북"):
        MODULE.label_review_packet(
            input_path=tmp_path / "missing-input.jsonl",
            output_path=tmp_path / "silver.jsonl",
            codebook_path=tmp_path / "missing-codebook.md",
            client=client,
        )

    assert client.calls == []


@pytest.mark.parametrize("linked_kind", ["input", "output", "codebook"])
def test_label_packet_rejects_symlink_boundaries(
    tmp_path: Path,
    linked_kind: str,
) -> None:
    real_input = tmp_path / "real-review.jsonl"
    real_output = tmp_path / "real-silver.jsonl"
    real_codebook = tmp_path / "real-codebook.md"
    _write_jsonl(real_input, _input_rows(1))
    real_output.write_text("", encoding="utf-8")
    real_codebook.write_text("POSITIVE NEUTRAL NEGATIVE", encoding="utf-8")
    paths = {
        "input": (tmp_path / "review.jsonl", real_input),
        "output": (tmp_path / "silver.jsonl", real_output),
        "codebook": (tmp_path / "codebook.md", real_codebook),
    }
    linked_path, target_path = paths[linked_kind]
    linked_path.symlink_to(target_path)
    input_path = linked_path if linked_kind == "input" else real_input
    output_path = linked_path if linked_kind == "output" else tmp_path / "new-silver.jsonl"
    codebook_path = linked_path if linked_kind == "codebook" else real_codebook
    client = _FakeTeacherClient()

    with pytest.raises(ValueError, match="symlink"):
        MODULE.label_review_packet(
            input_path=input_path,
            output_path=output_path,
            codebook_path=codebook_path,
            client=client,
        )

    assert client.calls == []


def test_resume_rejects_changed_source_record(tmp_path: Path) -> None:
    input_path = tmp_path / "review.jsonl"
    output_path = tmp_path / "silver.jsonl"
    codebook_path = tmp_path / "codebook.md"
    rows = _input_rows(1)
    _write_jsonl(input_path, rows)
    codebook_path.write_text("POSITIVE NEUTRAL NEGATIVE", encoding="utf-8")
    MODULE.label_review_packet(
        input_path=input_path,
        output_path=output_path,
        codebook_path=codebook_path,
        client=_FakeTeacherClient(),
    )
    rows[0]["snippet"] = "원본이 변경됐다."
    _write_jsonl(input_path, rows)

    with pytest.raises(ValueError, match="provenance"):
        MODULE.label_review_packet(
            input_path=input_path,
            output_path=output_path,
            codebook_path=codebook_path,
            client=_FakeTeacherClient(),
        )
