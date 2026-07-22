import pytest

from hannah_montana_ai.training.sentiment_protocol import (
    assert_disjoint_partitions,
    assert_sentiment_groups_disjoint,
    canonical_sentiment_url,
    conflict_safe_deduplicate,
    decontaminate_public_partitions,
    normalized_sentiment_text,
    purge_sentiment_group_overlap,
    sentiment_provenance,
    stratified_hash_split,
    stratified_hash_three_way_split,
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


def test_three_way_split_is_deterministic_stratified_and_group_disjoint() -> None:
    rows = [
        {
            "text": f"{label}-{index}",
            "label": label,
            "event_cluster_id": f"{label}-event-{index}",
        }
        for label in ("NEGATIVE", "NEUTRAL", "POSITIVE")
        for index in range(20)
    ]

    first = stratified_hash_three_way_split(
        rows,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=5,
    )
    second = stratified_hash_three_way_split(
        rows,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=5,
    )

    assert first == second
    for label in ("NEGATIVE", "NEUTRAL", "POSITIVE"):
        assert sum(row["label"] == label for row in first["CHECKPOINT"]) == 10
        assert sum(row["label"] == label for row in first["CALIBRATION"]) == 5
        assert sum(row["label"] == label for row in first["SELECTION"]) == 5
    assert_sentiment_groups_disjoint(first)


def test_three_way_split_fails_closed_when_a_label_is_too_small() -> None:
    rows = [
        {"text": f"{label}-{index}", "label": label}
        for label in ("NEGATIVE", "NEUTRAL", "POSITIVE")
        for index in range(18)
    ]

    with pytest.raises(ValueError, match="최소 5건"):
        stratified_hash_three_way_split(
            rows,
            checkpoint_name="CHECKPOINT",
            calibration_name="CALIBRATION",
            selection_name="SELECTION",
            minimum_per_label=5,
        )


def test_disjoint_assertion_fails_closed() -> None:
    with pytest.raises(ValueError, match="중복"):
        assert_disjoint_partitions(
            {
                "TRAIN": [{"text": "중복", "label": "NEUTRAL"}],
                "TEST": [{"text": "중 복", "label": "NEUTRAL"}],
            }
        )


def test_canonical_url_removes_tracking_parameters() -> None:
    left = canonical_sentiment_url(
        "HTTPS://News.Example.com:443/article/42/?id=7&utm_source=naver&fbclid=x#section"
    )
    right = canonical_sentiment_url("https://news.example.com/article/42?id=7")

    assert left == right


def test_provenance_preserves_all_group_identities() -> None:
    provenance = sentiment_provenance(
        {
            "text": "  삼성전자, 실적 개선! ",
            "source_url": "https://news.example.com/1?utm_medium=feed",
            "content_hash": "ABC123",
            "event_cluster_id": "EVENT-9",
        }
    )

    assert provenance.row_key == (
        "https://news.example.com/1",
        "삼성전자실적개선",
        "abc123",
        "event-9",
    )
    assert provenance.group_keys == {
        ("canonical_url", "https://news.example.com/1"),
        ("normalized_text", "삼성전자실적개선"),
        ("content_hash", "abc123"),
        ("event_cluster_id", "event-9"),
    }


def test_group_purge_removes_url_hash_and_event_overlap() -> None:
    training = [
        {
            "text": "URL 중복",
            "source_url": "https://news.example.com/1?utm_campaign=x",
            "content_hash": "train-hash-1",
            "event_cluster_id": "train-event-1",
        },
        {
            "text": "해시 중복",
            "source_url": "https://news.example.com/2",
            "content_hash": "shared-hash",
            "event_cluster_id": "train-event-2",
        },
        {
            "text": "사건 중복",
            "source_url": "https://news.example.com/3",
            "content_hash": "train-hash-3",
            "event_cluster_id": "shared-event",
        },
        {
            "text": "독립 학습 문장",
            "source_url": "https://news.example.com/4",
            "content_hash": "train-hash-4",
            "event_cluster_id": "train-event-4",
        },
    ]
    protected = [
        {"text": "A", "source_url": "https://news.example.com/1", "content_hash": "a"},
        {"text": "B", "source_url": "https://gold.example.com/2", "content_hash": "SHARED-HASH"},
        {
            "text": "C",
            "source_url": "https://gold.example.com/3",
            "event_cluster_id": "SHARED-EVENT",
        },
    ]

    cleaned, audit = purge_sentiment_group_overlap(training, protected)

    assert [row["text"] for row in cleaned] == ["독립 학습 문장"]
    assert audit["removed_count"] == 3
    assert_sentiment_groups_disjoint({"TRAIN": cleaned, "GOLD": protected})


def test_group_purge_removes_transitively_connected_event() -> None:
    training = [
        {
            "text": "보호 URL과 직접 연결",
            "source_url": "https://news.example.com/protected",
            "event_cluster_id": "connected-event",
        },
        {
            "text": "첫 번째 행과 같은 사건",
            "source_url": "https://news.example.com/indirect",
            "event_cluster_id": "connected-event",
        },
        {"text": "독립 행", "source_url": "https://news.example.com/safe"},
    ]
    protected = [{"text": "보호 행", "source_url": "https://news.example.com/protected"}]

    cleaned, audit = purge_sentiment_group_overlap(training, protected)

    assert [row["text"] for row in cleaned] == ["독립 행"]
    assert audit["propagated_removed_count"] == 1
