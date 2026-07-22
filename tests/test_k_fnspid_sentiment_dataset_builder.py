from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _module() -> ModuleType:
    path = Path("scripts/build_k_fnspid_sentiment_dataset.py")
    spec = importlib.util.spec_from_file_location("build_k_fnspid_sentiment_dataset", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_weak_labels_require_unambiguous_strong_direction() -> None:
    module = _module()

    assert module.weak_sentiment_label("영업이익 사상 최대, 흑자 전환")[0] == "POSITIVE"
    assert module.weak_sentiment_label("영업이익 급감하며 적자 전환")[0] == "NEGATIVE"
    assert module.weak_sentiment_label("주주총회 개최 공시")[0] == "NEUTRAL"
    assert module.weak_sentiment_label("매출 증가했지만 영업이익 급감")[0] == "NEUTRAL"


def test_review_payload_never_promotes_sampling_label_to_gold() -> None:
    module = _module()
    candidate = module.Candidate(
        document_id="doc-1",
        source_type="NEWS",
        title="테스트 기업 주주총회 개최 결정",
        snippet="정기 주주총회를 다음 달 개최한다.",
        source_url="https://news.example.com/1?utm_source=naver",
        content_hash="hash-1",
        published_at_kst="2026-05-01T09:00:00+09:00",
        effective_trade_date="2026-05-01",
        event_cluster_id="event-1",
        stock_code="000001",
        stock_name="테스트",
        sampling_stratum="NEUTRAL",
        rule_confidence=0.84,
    )

    payload = module._review_payload(candidate, "SEALED_TEST_REVIEW")

    assert payload["final_sentiment"] == ""
    assert payload["review_status"] == "NEEDS_BLIND_REVIEW"
    assert "sentiment" not in payload
    assert "sampling_stratum" not in payload
    assert "sampling_rule_confidence" not in payload
    assert payload["canonical_url"] == "https://news.example.com/1"


def test_silver_payload_keeps_weak_provenance_and_low_weight() -> None:
    module = _module()
    candidate = module.Candidate(
        document_id="doc-2",
        source_type="NEWS",
        title="테스트 기업 영업이익 사상 최대",
        snippet="영업이익이 전년보다 크게 증가했다.",
        source_url="https://news.example.com/2",
        content_hash="hash-2",
        published_at_kst="2024-05-01T09:00:00+09:00",
        effective_trade_date="2024-05-01",
        event_cluster_id="event-2",
        stock_code="000002",
        stock_name="테스트",
        sampling_stratum="POSITIVE",
        rule_confidence=0.96,
    )

    payload = module._silver_payload(candidate)

    assert payload["sentiment"] == "POSITIVE"
    assert payload["label_provenance"] == "STRICT_RULE_SILVER_V1"
    assert payload["review_status"] == "UNREVIEWED_SILVER"
    assert 0.0 < payload["sample_weight"] < 0.5
