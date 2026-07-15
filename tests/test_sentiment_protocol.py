import pytest

from hannah_montana_ai.training.sentiment_protocol import (
    assert_disjoint_partitions,
    conflict_safe_deduplicate,
    decontaminate_public_partitions,
    normalized_sentiment_text,
    stratified_hash_split,
)


def test_normalization_detects_spacing_and_punctuation_rewrites() -> None:
    assert normalized_sentiment_text("삼성전자, 영업이익 증가!") == normalized_sentiment_text(
        "삼성전자 영업 이익 증가"
    )


def test_conflicting_duplicates_are_all_excluded() -> None:
    rows = [
        {"text": "같은 공시", "label": "POSITIVE"},
        {"text": "같은공시", "label": "NEGATIVE"},
        {"text": "다른 공시", "label": "NEUTRAL"},
    ]

    cleaned, audit = conflict_safe_deduplicate(rows)

    assert cleaned == [{"text": "다른 공시", "label": "NEUTRAL"}]
    assert audit["conflicting_text_count"] == 1


def test_decontamination_preserves_test_and_removes_lower_priority_overlap() -> None:
    partitions = {
        "TRAIN": [
            {"text": "공통 문장", "label": "POSITIVE"},
            {"text": "학습 전용", "label": "NEGATIVE"},
        ],
        "VALIDATION": [
            {"text": "검증 전용", "label": "NEUTRAL"},
            {"text": "공통문장", "label": "POSITIVE"},
        ],
        "TEST": [{"text": "공통-문장", "label": "POSITIVE"}],
    }

    cleaned, audit = decontaminate_public_partitions(partitions)

    assert [row["text"] for row in cleaned["TEST"]] == ["공통-문장"]
    assert [row["text"] for row in cleaned["VALIDATION"]] == ["검증 전용"]
    assert [row["text"] for row in cleaned["TRAIN"]] == ["학습 전용"]
    assert audit["cross_partition_removed"] == {"TRAIN": 1, "VALIDATION": 1, "TEST": 0}


def test_hash_split_is_deterministic_and_stratified() -> None:
    rows = [
        {"text": f"{label}-{index}", "label": label}
        for label in ("NEGATIVE", "NEUTRAL", "POSITIVE")
        for index in range(4)
    ]

    first = stratified_hash_split(rows, left_name="CALIBRATION", right_name="SELECTION")
    second = stratified_hash_split(rows, left_name="CALIBRATION", right_name="SELECTION")

    assert first == second
    assert {row["label"] for row in first["CALIBRATION"]} == {
        "NEGATIVE",
        "NEUTRAL",
        "POSITIVE",
    }
    assert_disjoint_partitions(first)


def test_disjoint_assertion_fails_closed() -> None:
    with pytest.raises(ValueError, match="중복"):
        assert_disjoint_partitions(
            {
                "TRAIN": [{"text": "중복", "label": "NEUTRAL"}],
                "TEST": [{"text": "중 복", "label": "NEUTRAL"}],
            }
        )
