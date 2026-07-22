from __future__ import annotations

import math
from typing import Any

SOURCE_PREFIX = {
    "NEWS": "[뉴스]",
    "DISCLOSURE": "[공시]",
}
HEAD_RATIO = 0.72
SENTIMENT_LOGIT_BIAS_DOMAINS = (
    "NEWS_UNTARGETED",
    "NEWS_TARGETED",
    "DISCLOSURE_TARGETED",
)
MAX_ABS_LOGIT_BIAS = 8.0


def sentiment_document_text(title: str, snippet: str = "") -> str:
    normalized_title = " ".join(title.split())
    normalized_snippet = " ".join(snippet.split())
    if normalized_title and normalized_snippet:
        return f"{normalized_title} [SEP] {normalized_snippet}"
    return normalized_title or normalized_snippet


def sentiment_model_text(text: str, source_type: str, target_security: str = "") -> str:
    prefix = SOURCE_PREFIX.get(source_type.upper(), "[금융문서]")
    target = " ".join(target_security.split())[:80]
    target_prefix = f" [대상:{target}]" if target else ""
    return f"{prefix}{target_prefix} {text.strip()}"


def sentiment_source_domain(source_type: str, target_security: str = "") -> str:
    if source_type.strip().upper() == "DISCLOSURE":
        return "DISCLOSURE_TARGETED"
    return "NEWS_TARGETED" if target_security.strip() else "NEWS_UNTARGETED"


def validated_sentiment_logit_biases(value: object) -> dict[str, tuple[float, ...]]:
    if not isinstance(value, dict) or set(value) != set(SENTIMENT_LOGIT_BIAS_DOMAINS):
        raise ValueError("감성 도메인별 logit bias 구성이 올바르지 않습니다.")
    result: dict[str, tuple[float, ...]] = {}
    for domain in SENTIMENT_LOGIT_BIAS_DOMAINS:
        raw_bias = value.get(domain)
        if not isinstance(raw_bias, list | tuple) or len(raw_bias) != 3:
            raise ValueError("감성 도메인별 logit bias 차원이 올바르지 않습니다.")
        bias: list[float] = []
        for raw_value in raw_bias:
            if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
                raise ValueError("감성 도메인별 logit bias 값이 숫자가 아닙니다.")
            numeric = float(raw_value)
            if not math.isfinite(numeric) or abs(numeric) > MAX_ABS_LOGIT_BIAS:
                raise ValueError("감성 도메인별 logit bias 범위가 올바르지 않습니다.")
            bias.append(numeric)
        result[domain] = tuple(bias)
    return result


def encode_sentiment_input(
    tokenizer: Any,
    text: str,
    source_type: str,
    max_length: int,
    target_security: str = "",
) -> dict[str, list[int]]:
    """긴 문서의 결론부를 보존하도록 앞뒤 토큰을 결합한다."""
    token_ids = tokenizer.encode(
        sentiment_model_text(text, source_type, target_security),
        add_special_tokens=False,
    )
    special_token_count = int(tokenizer.num_special_tokens_to_add(pair=False))
    token_budget = max_length - special_token_count
    if token_budget < 8:
        raise ValueError("감성 입력 max_length는 특수 토큰을 제외하고 8 이상이어야 합니다.")
    if len(token_ids) > token_budget:
        head_count = max(1, round(token_budget * HEAD_RATIO))
        tail_count = token_budget - head_count
        token_ids = token_ids[:head_count] + token_ids[-tail_count:]
    cls_token_id = tokenizer.cls_token_id
    sep_token_id = tokenizer.sep_token_id
    if (
        isinstance(cls_token_id, bool)
        or not isinstance(cls_token_id, int)
        or isinstance(sep_token_id, bool)
        or not isinstance(sep_token_id, int)
        or special_token_count != 2
    ):
        raise ValueError("KF-DeBERTa tokenizer의 CLS/SEP 계약이 올바르지 않습니다.")
    input_ids = [cls_token_id, *token_ids, sep_token_id]
    encoded = {
        "input_ids": [int(value) for value in input_ids],
        "attention_mask": [1] * len(input_ids),
    }
    if "token_type_ids" in tokenizer.model_input_names:
        encoded["token_type_ids"] = [0] * len(input_ids)
    return encoded
