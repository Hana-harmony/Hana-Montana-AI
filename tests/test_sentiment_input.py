from __future__ import annotations

import pytest

from hannah_montana_ai.services.sentiment_input import (
    encode_sentiment_input,
    sentiment_document_text,
    sentiment_model_text,
    sentiment_source_domain,
    validated_sentiment_logit_biases,
)


class FakeTokenizer:
    cls_token_id = 101
    sep_token_id = 102
    model_input_names = ["input_ids", "token_type_ids", "attention_mask"]

    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        assert not add_special_tokens
        return list(range(len(text.split())))

    def num_special_tokens_to_add(self, *, pair: bool) -> int:
        assert not pair
        return 2


def test_sentiment_input_adds_source_prefix() -> None:
    assert sentiment_model_text("실적 발표", "NEWS") == "[뉴스] 실적 발표"
    assert sentiment_model_text("사업보고서", "DISCLOSURE") == "[공시] 사업보고서"
    assert sentiment_model_text("실적 발표", "NEWS", "하나 금융") == (
        "[뉴스] [대상:하나 금융] 실적 발표"
    )


def test_sentiment_document_text_matches_k_fnspid_contract() -> None:
    assert sentiment_document_text("  실적   발표 ", " 매출 증가 ") == (
        "실적 발표 [SEP] 매출 증가"
    )
    assert sentiment_document_text("공시 제목") == "공시 제목"


def test_sentiment_source_domain_separates_target_contract() -> None:
    assert sentiment_source_domain("NEWS") == "NEWS_UNTARGETED"
    assert sentiment_source_domain("news", "하나금융지주") == "NEWS_TARGETED"
    assert sentiment_source_domain("DISCLOSURE") == "DISCLOSURE_TARGETED"


def test_logit_bias_contract_is_fail_closed() -> None:
    valid = {
        "NEWS_UNTARGETED": [0.0, 0.1, -0.1],
        "NEWS_TARGETED": [0, 0, 0],
        "DISCLOSURE_TARGETED": [0.2, -0.2, 0.0],
    }

    assert validated_sentiment_logit_biases(valid)["NEWS_UNTARGETED"] == (
        0.0,
        0.1,
        -0.1,
    )
    invalid = {**valid, "NEWS_TARGETED": [0.0, float("nan"), 0.0]}
    with pytest.raises(ValueError, match="범위"):
        validated_sentiment_logit_biases(invalid)


def test_head_tail_encoding_preserves_document_end() -> None:
    encoded = encode_sentiment_input(
        FakeTokenizer(),
        " ".join(f"토큰{index}" for index in range(20)),
        "NEWS",
        max_length=12,
    )

    assert len(encoded["input_ids"]) == 12
    assert encoded["input_ids"][:3] == [101, 0, 1]
    assert encoded["input_ids"][-4:] == [18, 19, 20, 102]
    assert encoded["token_type_ids"] == [0] * 12


def test_encoding_rejects_unsafe_short_limit() -> None:
    with pytest.raises(ValueError, match="8 이상"):
        encode_sentiment_input(FakeTokenizer(), "짧은 문장", "NEWS", max_length=8)
