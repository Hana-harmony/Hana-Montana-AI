from __future__ import annotations

import importlib.util
import json
import math
import struct
import sys
from array import array
from collections import Counter
from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, cast

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import torch

SCRIPT = Path("scripts/train_k_fnspid_dapt.py")


@pytest.fixture(scope="module")
def module() -> ModuleType:
    scripts = str(Path("scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location("train_k_fnspid_dapt", SCRIPT)
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def test_runner_never_names_public_test_and_keeps_confirmatory_labels_sealed() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "ratings_test.csv" not in source
    assert 'payload.get("review_status") != "NEEDS_BLIND_REVIEW"' in source
    assert 'payload.get("final_sentiment") != ""' in source
    assert 'payload.get("reviewer_id") != ""' in source
    assert "FORBIDDEN_SEALED_RESERVATION_FIELDS & payload.keys()" in source
    assert '"public_test_opened": False' in source
    assert '"confirmatory_sentiment_labels_opened": False' in source


def test_sealed_reservation_requires_full_blind_schema(module: ModuleType) -> None:
    payload = {
        "partition": "CONFIRMATORY_SEALED_TEST_REVIEW",
        "review_status": "NEEDS_BLIND_REVIEW",
        "final_sentiment": "",
        "reviewer_id": "",
        "reviewed_at": "",
        "review_note": "",
    }
    module.assert_blind_reservation_row(module.NEWS_RESERVATION_PATH, payload)
    for field, value in (
        ("final_sentiment", "POSITIVE"),
        ("reviewer_id", "reviewer"),
        ("sentiment", "POSITIVE"),
    ):
        exposed = {**payload, field: value}
        with pytest.raises(RuntimeError, match="blind"):
            module.assert_blind_reservation_row(module.NEWS_RESERVATION_PATH, exposed)


def test_fixed_corpus_and_training_contract(module: ModuleType) -> None:
    assert module.BASE_REVISION == "363b171d71443b0874b0bf9cea053eb5b1650633"
    assert module.CUTOFF_TIMESTAMP == "2026-04-01T00:00:00+09:00"
    assert module.CUTOFF_TRADE_DATE == "2026-04-01"
    assert module.EXPECTED["eligible_count"] == {"NEWS": 419_260, "DISCLOSURE": 699_031}
    assert module.EXPECTED["eligible_component_count"] == 967_550
    assert module.INVENTORY_ORACLE_STATUS == "LOCKED"
    assert module.PACK_ORACLE_STATUS == "LOCKED"
    assert module.require_locked_inventory_oracle()["status"] == (
        "APPROVED_PENDING_SOURCE_LOCK"
    )
    module.require_locked_pack_oracle()
    assert module.MICRO_BATCH_SIZE == 8
    assert module.ACCUMULATION_STEPS == 8
    assert module.EFFECTIVE_BATCH_SIZE == 64
    assert module.TOTAL_UPDATES == 3_908
    assert module.WARMUP_UPDATES == 196
    assert module.PILOT_PACK_COUNT == 1_024


def test_documents_metadata_matches_locked_contract(module: ModuleType) -> None:
    parquet = pq.ParquetFile(module.DOCUMENTS_PATH)

    assert parquet.metadata.num_rows == 1_247_685
    assert set(module.TEXT_COLUMNS) <= set(parquet.schema_arrow.names)


def test_stable_parquet_source_reuses_inode_and_detects_mutation(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    path = tmp_path / "source.parquet"
    pq.write_table(pa.table({"value": [1, 2, 3]}), path)

    with module.StableParquetSource(path) as source:
        first = list(source.iter_rows(("value",)))
        second = list(source.iter_rows(("value",)))

    assert first == second == [{"value": 1}, {"value": 2}, {"value": 3}]
    with pytest.raises(RuntimeError, match="순회 중 입력이 변경"):
        with module.StableParquetSource(path) as source:
            assert list(source.iter_rows(("value",))) == first
            path.write_bytes(b"tampered")


@pytest.mark.parametrize(
    ("published", "trade_date", "expected"),
    [
        ("2026-03-31T23:59:59+09:00", "2026-03-31", True),
        ("2026-04-01T00:00:00+09:00", "2026-03-31", False),
        ("2026-03-31T23:59:59+09:00", "2026-04-01", False),
    ],
)
def test_dual_cutoff_is_strict_and_conjunctive(
    module: ModuleType,
    published: str,
    trade_date: str,
    expected: bool,
) -> None:
    assert module.before_dual_cutoff(published, trade_date) is expected


@pytest.mark.parametrize(
    ("published", "trade_date"),
    [
        ("", "2026-03-31"),
        ("2026-03-31T23:59:59Z", "2026-03-31"),
        ("2026-02-30T12:00:00+09:00", "2026-03-31"),
        ("2026-03-31T23:59:59+09:00", "2026-02-30"),
    ],
)
def test_temporal_schema_fails_closed(
    module: ModuleType,
    published: str,
    trade_date: str,
) -> None:
    with pytest.raises(RuntimeError):
        module.before_dual_cutoff(published, trade_date)


def test_protected_component_closes_transitive_identity_chain(module: ModuleType) -> None:
    protected = [
        {
            "document_id": "protected",
            "canonical_url": "https://example.com/a?utm_source=x",
            "content_hash": "h0",
            "event_cluster_id": "e0",
        }
    ]
    documents = [
        {
            "document_id": "doc-1",
            "source_url": "https://example.com/a",
            "content_hash": "h1",
            "event_cluster_id": "e1",
        },
        {
            "document_id": "doc-2",
            "source_url": "https://example.com/b",
            "content_hash": "h1",
            "event_cluster_id": "e2",
        },
        {
            "document_id": "doc-3",
            "source_url": "https://example.com/c",
            "content_hash": "h3",
            "event_cluster_id": "e2",
        },
        {
            "document_id": "unrelated",
            "source_url": "https://example.com/z",
            "content_hash": "hz",
            "event_cluster_id": "ez",
        },
    ]

    component = module.build_protected_component(lambda: iter(documents), protected)

    assert component.document_ids == frozenset({"doc-1", "doc-2", "doc-3"})
    assert "unrelated" not in component.document_ids
    assert component.iteration_count >= 2


def test_union_find_component_split_closes_all_identity_types(module: ModuleType) -> None:
    rows = [
        {
            "document_id": "a",
            "source_url": "https://example.com/1",
            "content_hash": "h1",
            "event_cluster_id": "e1",
            "title": "반도체 수출 증가로 코스피가 장중 강세를 기록했다",
            "snippet": "외국인 순매수와 기업 실적 전망이 지수 상승을 이끌었다",
            "full_text": "",
        },
        {
            "document_id": "b",
            "source_url": "https://example.com/2",
            "content_hash": "h2",
            "event_cluster_id": "e2",
            "title": "반도체 수출 증가로 코스피가 장중 강세를 기록했다",
            "snippet": "외국인 순매수와 기업 실적 전망이 지수 상승을 이끌었다",
            "full_text": "",
        },
        {
            "document_id": "c",
            "source_url": "https://example.com/2",
            "content_hash": "h3",
            "event_cluster_id": "e3",
            "title": "다른 기사",
            "snippet": "내용",
            "full_text": "",
        },
    ]
    union_find = module.ComponentUnionFind()
    owners: dict[bytes, int] = {}
    indices: list[int] = []
    for row in rows:
        keys = module.component_keys_from_mapping(row)
        index = union_find.add(min(keys))
        indices.append(index)
        for key in keys:
            owner = owners.setdefault(key, index)
            union_find.union(index, owner)

    roots = {union_find.find(index) for index in indices}
    splits = {module.split_for_component(union_find.minimum_key(index)) for index in indices}
    assert len(roots) == 1
    assert len(splits) == 1


def test_exact_text_information_gate_rejects_disclosure_boilerplate(
    module: ModuleType,
) -> None:
    disclosure = {
        "source_type": "DISCLOSURE",
        "title": "NH투자증권 일괄신고추가서류 파생결합증권 주가연계증권",
        "snippet": "일괄신고추가서류 파생결합증권 주가연계증권",
        "full_text": "",
    }
    news = {
        "source_type": "NEWS",
        "title": "반도체 수출 증가로 코스피가 장중 강세를 기록했다",
        "snippet": "외국인 순매수와 기업 실적 전망이 지수 상승을 이끌었다",
        "full_text": "",
    }

    disclosure_hash, disclosure_status = module._normalized_exact_text_hash_with_status(disclosure)
    news_hash, news_status = module._normalized_exact_text_hash_with_status(news)

    assert disclosure_hash == ""
    assert disclosure_status == "rejected_redundant_title_snippet"
    assert len(news_hash) == 64
    assert news_status == "accepted_nonredundant_title_snippet"


def test_component_size_audit_uses_fixed_nearest_rank(module: ModuleType) -> None:
    assert module._component_size_distribution([1, 1, 2, 4, 10]) == {
        "component_count": 5,
        "document_count": 18,
        "p50": 2,
        "p95": 10,
        "p99": 10,
        "max": 10,
    }


def _indexed_signature(
    module: ModuleType,
    tokens: set[str],
    ranks: dict[str, int],
    row_index: int | None,
    source_type: str,
    protected: bool = False,
) -> Any:
    return module.FuzzyGraphSignature(
        row_index=row_index,
        source_type=source_type,
        digest=sha256(f"{source_type}:{row_index}".encode()).hexdigest(),
        text_length=len(tokens),
        token_ids=array("I", sorted(ranks[token] for token in tokens)),
        protected_seed=protected,
    )


def test_allpairs_prefix_filter_recall_matches_bruteforce(module: ModuleType) -> None:
    token_sets: list[set[str]] = []
    for group in range(12):
        base = {f"g{group}-t{index:03d}" for index in range(40)}
        token_sets.extend(
            [
                base,
                (base - {f"g{group}-t000", f"g{group}-t001"})
                | {f"g{group}-x000", f"g{group}-x001"},
                (base - {f"g{group}-t002", f"g{group}-t003"})
                | {f"g{group}-x002", f"g{group}-x003"},
            ]
        )
    frequencies: Counter[str] = Counter()
    for tokens in token_sets:
        frequencies.update(tokens)
    ranks = module.rank_fuzzy_shingles(frequencies)
    index = module.FuzzyAllPairsIndex(maximum_candidates=10_000)
    observed: set[tuple[int, int]] = set()
    for row_index, tokens in enumerate(token_sets):
        signature = _indexed_signature(module, tokens, ranks, row_index, "NEWS")
        for candidate_index, _score in index.add(signature):
            observed.add((candidate_index, row_index))

    brute_force: set[tuple[int, int]] = set()
    for right_index, right in enumerate(token_sets):
        for left_index, left in enumerate(token_sets[:right_index]):
            if not module.fuzzy_length_compatible(len(left), len(right)):
                continue
            intersection = len(left & right)
            if 20_000 * intersection >= module.FUZZY_MIN_DICE_SIMILARITY_BPS * (
                len(left) + len(right)
            ):
                brute_force.add((left_index, right_index))

    assert observed == brute_force


def test_fuzzy_graph_is_cross_source_and_transitively_protected(module: ModuleType) -> None:
    protected = {f"t{index:03d}" for index in range(100)}
    news = (protected - {"t000", "t001", "t002", "t003", "t004"}) | {
        f"x{index:03d}" for index in range(5)
    }
    disclosure = (protected - {f"t{index:03d}" for index in range(10)}) | {
        f"x{index:03d}" for index in range(10)
    }
    assert len(protected & disclosure) == 90
    assert len(news & disclosure) == 95
    frequencies: Counter[str] = Counter()
    for tokens in (protected, news, disclosure):
        frequencies.update(tokens)
    ranks = module.rank_fuzzy_shingles(frequencies)
    index = module.FuzzyAllPairsIndex(maximum_candidates=100)
    union_find = module.ComponentUnionFind()
    news_row = union_find.add(module.typed_component_key("document_id", "news"))
    disclosure_row = union_find.add(module.typed_component_key("document_id", "disclosure"))

    index.add(
        _indexed_signature(module, protected, ranks, None, "PROTECTED", protected=True),
        query=False,
    )
    news_matches = index.add(_indexed_signature(module, news, ranks, news_row, "NEWS"))
    assert [index.signatures[candidate].protected_seed for candidate, _ in news_matches] == [True]
    disclosure_matches = index.add(
        _indexed_signature(module, disclosure, ranks, disclosure_row, "DISCLOSURE")
    )
    corpus_matches = [
        candidate
        for candidate, _score in disclosure_matches
        if not index.signatures[candidate].protected_seed
    ]
    assert corpus_matches
    assert all(index.signatures[candidate].source_type == "NEWS" for candidate in corpus_matches)
    assert not any(
        index.signatures[candidate].protected_seed for candidate, _score in disclosure_matches
    )
    union_find.union(disclosure_row, news_row)

    assert union_find.find(disclosure_row) == union_find.find(news_row)
    assert module.split_for_component(union_find.minimum_key(disclosure_row)) == (
        module.split_for_component(union_find.minimum_key(news_row))
    )


def test_fuzzy_graph_honors_temporal_or_protected_scope_mask(module: ModuleType) -> None:
    title = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    snippet = "financial disclosure market reaction profit outlook volume volatility"
    rows = [
        {
            "document_id": f"document-{index}",
            "source_url": f"https://example.test/{index}",
            "content_hash": f"content-{index}",
            "event_cluster_id": f"cluster-{index}",
            "source_type": source,
            "title": title,
            "snippet": snippet,
            "full_text": "",
            "published_at_kst": "2026-03-31T00:00:00+09:00",
            "effective_trade_date": "2026-03-31",
        }
        for index, source in enumerate(("NEWS", "DISCLOSURE", "NEWS"))
    ]
    text_hash, status = module._normalized_exact_text_hash_with_status(rows[0])
    assert text_hash and status.startswith("accepted_")
    text = module._fuzzy_audit_text(rows[0], status)
    shingles = module._fuzzy_shingles(text)
    frequencies: Counter[str] = Counter()
    frequencies.update(shingles)
    frequencies.update(shingles)
    ranks = module.rank_fuzzy_shingles(frequencies)
    union_find = module.ComponentUnionFind()
    for index in range(3):
        union_find.add(module.typed_component_key("document_id", f"document-{index}"))

    _, audit = module.connect_allpairs_fuzzy_graph(
        document_rows_factory=lambda: iter(rows),
        protected_texts={},
        ranks=ranks,
        fuzzy_scope_mask=bytes((1, 2, 0)),
        union_find=union_find,
    )

    assert union_find.find(0) == union_find.find(1)
    assert union_find.find(2) != union_find.find(0)
    assert audit["scoped_corpus_document_count"] == 2
    assert audit["scoped_corpus_source_count"] == {"NEWS": 1, "DISCLOSURE": 1}
    assert audit["scoped_dual_cutoff_document_count"] == 1
    assert audit["scoped_exact_identity_protected_document_count"] == 1
    assert audit["cross_source_matched_pair_count"] == 1


def test_protection_increment_categories_are_disjoint_and_conserved(
    module: ModuleType,
) -> None:
    audit = module.ProtectionIncrementAudit(
        pre_fuzzy_exact_identity_protected_roots={0},
        direct_match_pre_fuzzy_roots={0, 1},
        post_fuzzy_protected_roots={10},
    )
    observations = (
        (0, 10, "NEWS"),
        (0, 10, "DISCLOSURE"),
        (1, 10, "NEWS"),
        (2, 10, "DISCLOSURE"),
        (3, 11, "NEWS"),
        (3, 11, "NEWS"),
    )
    for pre_fuzzy_root, post_fuzzy_root, source_type in observations:
        audit.observe(
            pre_fuzzy_root=pre_fuzzy_root,
            post_fuzzy_root=post_fuzzy_root,
            source_type=source_type,
        )

    record = audit.finalize()

    assert record["pre_fuzzy_exact_identity_protected_component_count"] == 1
    assert record["pre_fuzzy_exact_identity_protected_document_count"] == 2
    assert record["fuzzy_direct_increment_pre_fuzzy_component_count"] == 1
    assert record["fuzzy_direct_increment_document_count"] == 1
    assert record["fuzzy_transitive_only_increment_pre_fuzzy_component_count"] == 1
    assert record["fuzzy_transitive_only_increment_document_count"] == 1
    assert record["fuzzy_total_increment_pre_fuzzy_component_count"] == 2
    assert record["fuzzy_total_increment_document_count"] == 2
    assert record["post_fuzzy_protected_pre_fuzzy_component_membership_count"] == 3
    assert record["post_fuzzy_protected_component_count"] == 1
    assert record["post_fuzzy_protected_component_merge_reduction"] == 2
    assert record["post_fuzzy_protected_document_count"] == 4
    assert record["post_fuzzy_protected_source_document_count"] == {
        "NEWS": 2,
        "DISCLOSURE": 2,
    }
    assert record["protection_increment_categories_disjoint"] is True
    assert record["protection_increment_document_conservation_verified"] is True
    assert record["protection_increment_component_conservation_verified"] is True


def test_allpairs_candidate_limit_fails_without_truncation(module: ModuleType) -> None:
    tokens = {f"token-{index:03d}" for index in range(40)}
    frequencies: Counter[str] = Counter()
    for _ in range(3):
        frequencies.update(tokens)
    ranks = module.rank_fuzzy_shingles(frequencies)
    index = module.FuzzyAllPairsIndex(maximum_candidates=1)

    index.add(_indexed_signature(module, tokens, ranks, 0, "NEWS"))
    index.add(_indexed_signature(module, tokens, ranks, 1, "NEWS"))
    with pytest.raises(RuntimeError, match="한도를 초과"):
        index.add(_indexed_signature(module, tokens, ranks, 2, "NEWS"))

    assert len(index.signatures) == 2
    assert index.maximum_observed_candidates == 2


def test_fuzzy_audit_text_has_exact_head_tail_bound(module: ModuleType) -> None:
    long_row = {"title": "가" * 400, "snippet": "나" * 400}
    text = module._fuzzy_audit_text(long_row, "accepted_full_text")

    assert len(text) == module.FUZZY_TEXT_MAX_CHARS
    assert text.startswith("가" * 255)
    assert text.endswith("나" * 256)
    assert (
        module._fuzzy_audit_text(
            {"title": "short", "snippet": "text"},
            "accepted_nonredundant_title_snippet",
        )
        == ""
    )
    assert module._fuzzy_audit_text(long_row, "rejected_low_character_diversity") == ""


def test_split_matches_independent_sha256_reference(module: ModuleType) -> None:
    source = "NEWS"
    cluster = "cluster-x"
    digest = sha256(module.SPLIT_SALT + b"NEWS\0cluster-x").digest()
    expected = "VALIDATION" if int.from_bytes(digest[:8], "big") < (1 << 64) // 100 else "TRAIN"

    assert module.split_for(source, cluster) == expected
    assert module.split_for(source, cluster) == module.split_for(source, cluster)


def test_formatting_without_full_text_uses_exact_budget(module: ModuleType) -> None:
    segment, structural_positions, audit = module.format_tokenized_segment(
        source_type="NEWS",
        title_tokens=list(range(100, 200)),
        snippet_tokens=list(range(1_000, 1_500)),
        full_tokens=(),
        has_full_text=False,
    )

    assert len(segment) == module.PACK_CAPACITY
    assert segment[:2] == [module.SOURCE_MARKERS["NEWS"], module.FIELD_MARKERS["TITLE"]]
    assert audit["used_title"] == 64
    assert audit["used_snippet"] == 187
    assert audit["used_full"] == 0
    assert segment[-1] == module.SEP_ID
    assert structural_positions == [0, 1, 66]


def test_formatting_with_full_text_reserves_body_and_crops_head_tail(module: ModuleType) -> None:
    full = list(range(2_000, 2_500))
    segment, structural_positions, audit = module.format_tokenized_segment(
        source_type="DISCLOSURE",
        title_tokens=list(range(100, 200)),
        snippet_tokens=list(range(1_000, 1_500)),
        full_tokens=full,
        has_full_text=True,
    )

    body_index = segment.index(module.FIELD_MARKERS["BODY"])
    used_full = cast(int, audit["used_full"])
    assert len(segment) == module.PACK_CAPACITY
    assert audit["used_title"] == 64
    assert audit["used_snippet"] == 58
    assert used_full == 128
    assert segment[body_index + 1 : body_index + 65] == full[:64]
    assert segment[body_index + 65 : -1] == full[-64:]
    assert structural_positions == [0, 1, 66, body_index]


def test_best_fit_decreasing_uses_smallest_residual_then_pack_id(module: ModuleType) -> None:
    metadata = [
        module.SegmentMetadata(index, f"doc-{index}", length, bytes([index]) * 32)
        for index, length in enumerate((150, 105, 105, 100, 50))
    ]

    assert module.best_fit_decreasing(metadata) == [[0, 1], [2, 3, 4]]


def test_pack_serializer_and_masking_are_byte_stable(module: ModuleType) -> None:
    ids = (
        module.CLS_ID,
        module.SOURCE_MARKERS["NEWS"],
        module.FIELD_MARKERS["TITLE"],
        101,
        102,
        module.FIELD_MARKERS["SUMMARY"],
        103,
        module.SEP_ID,
        *((module.PAD_ID,) * (module.MAX_LENGTH - 8)),
    )
    structural_mask = tuple(index in {0, 1, 2, 5} for index in range(module.MAX_LENGTH))
    row = module.PackedRow("TRAIN", "NEWS", 7, 8, ids, (7,), structural_mask)
    masked, labels, audit = module.mask_pack(row, (5, 6, 7, 8, 9, 10))
    digest = sha256()
    module.update_mask_hash(digest, row, masked, labels)

    assert module.pack_identity("VALIDATION", "DISCLOSURE", 0x01020304).hex() == "010101020304"
    validation_row = module.PackedRow(
        "VALIDATION",
        "DISCLOSURE",
        0x01020304,
        8,
        ids,
        (7,),
        structural_mask,
    )
    assert module.pack_header(validation_row) == struct.pack(">BBIH", 1, 1, 0x01020304, 8)
    assert digest.hexdigest() == "3e608930fe52556362a6b11b19177d6a4f4a5f26ba17e2e9db32041f2a4736e3"
    assert audit == {"selected": 1, "mask": 0, "random": 1, "unchanged": 0}
    selected_positions = [index for index, value in enumerate(labels) if value != -100]
    assert selected_positions
    assert all(
        ids[index] not in module.SPECIAL_IDS and not structural_mask[index]
        for index in selected_positions
    )


def test_natural_marker_token_is_maskable_but_structural_position_is_not(
    module: ModuleType,
) -> None:
    ids = (
        module.CLS_ID,
        module.SOURCE_MARKERS["NEWS"],
        module.FIELD_MARKERS["TITLE"],
        module.SOURCE_MARKERS["DISCLOSURE"],
        module.SEP_ID,
        *((module.PAD_ID,) * (module.MAX_LENGTH - 5)),
    )
    structural = tuple(index in {0, 1, 2} for index in range(module.MAX_LENGTH))
    row = module.PackedRow("TRAIN", "NEWS", 0, 5, ids, (4,), structural)

    _, labels, audit = module.mask_pack(row, tuple(range(5, module.VOCAB_SIZE)))

    assert labels[3] == module.SOURCE_MARKERS["DISCLOSURE"]
    assert labels[1] == -100
    assert audit["selected"] == 1


def test_load_pack_store_copies_arrow_boolean_values(
    module: ModuleType, tmp_path: Path
) -> None:
    structural = [index < 3 for index in range(module.MAX_LENGTH)]
    input_ids = [module.PAD_ID] * module.MAX_LENGTH
    input_ids[:5] = [
        module.CLS_ID,
        module.SOURCE_MARKERS["NEWS"],
        module.FIELD_MARKERS["TITLE"],
        100,
        module.SEP_ID,
    ]
    table = pa.table(
        {
            "source_type": pa.array(["NEWS"]),
            "pack_id": pa.array([7], type=pa.uint32()),
            "valid_length": pa.array([5], type=pa.uint16()),
            "segment_lengths": pa.array([[4]], type=pa.list_(pa.uint16())),
            "structural_mask": pa.array(
                [structural], type=pa.list_(pa.bool_(), module.MAX_LENGTH)
            ),
            "input_ids": pa.array(
                [input_ids], type=pa.list_(pa.uint32(), module.MAX_LENGTH)
            ),
        }
    )
    path = tmp_path / "packs.parquet"
    pq.write_table(table, path)

    store = module.load_pack_store(path, "TRAIN")

    assert store.structural_masks.dtype == bool
    assert store.structural_masks.shape == (1, module.MAX_LENGTH)
    assert store.row(0).structural_mask[:5] == (True, True, True, False, False)


def test_document_block_mask_isolated_and_fails_closed(module: ModuleType) -> None:
    ids = (
        module.CLS_ID,
        10,
        module.SEP_ID,
        20,
        21,
        module.SEP_ID,
        *((module.PAD_ID,) * (module.MAX_LENGTH - 6)),
    )
    structural = (False,) * module.MAX_LENGTH
    row = module.PackedRow("TRAIN", "NEWS", 0, 6, ids, (2, 3), structural)

    mask = module.document_block_attention_mask(row)

    assert mask[0][0] is True
    assert sum(mask[0]) == 1
    assert mask[1][2] is True
    assert mask[1][3] is False
    assert mask[3][5] is True
    assert not any(mask[6])
    invalid = module.PackedRow("TRAIN", "NEWS", 0, 6, ids, (5, 0), structural)
    with pytest.raises(RuntimeError, match="경계"):
        module.document_block_attention_mask(invalid)


def test_accumulation_last_window_uses_actual_pack_count(module: ModuleType) -> None:
    pack_count = module.EFFECTIVE_BATCH_SIZE * 3 + 13
    windows = list(module.accumulation_windows(list(range(pack_count))))

    assert len(windows) == 4
    assert len(windows[-1]) == 2
    assert sum(map(len, windows[-1])) == 13
    assert [len(batch) for batch in windows[-1]] == [8, 5]


class _FakeEmbeddings(torch.nn.Module):
    position_biased_input = False

    def forward(self, *, input_ids: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        hidden = torch.nn.functional.one_hot(input_ids % 4, num_classes=4).float()
        return hidden * mask.unsqueeze(-1)


class _FakeEncoderStack(torch.nn.Module):
    conv = None

    def forward(
        self,
        hidden: torch.Tensor,
        attention_mask: torch.Tensor,
        **_: Any,
    ) -> Any:
        assert attention_mask.ndim == 3
        return SimpleNamespace(last_hidden_state=hidden)


class _FakeEncoder(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.embeddings = _FakeEmbeddings()
        self.encoder = _FakeEncoderStack()
        self.config = SimpleNamespace(
            relative_attention=True,
            pos_att_type=["p2c", "c2p"],
            position_biased_input=False,
        )
        self.z_steps = 0


class _FakeBase(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.deberta = _FakeEncoder()
        self.cls = torch.nn.Linear(4, 8, bias=False)


class _FakePeft(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.base = _FakeBase()

    def get_base_model(self) -> _FakeBase:
        return self.base


def test_sparse_mlm_scores_only_selected_positions(module: ModuleType) -> None:
    model = _FakePeft()
    input_ids = torch.tensor([[2, 5, 6, 0], [2, 7, 3, 0]], dtype=torch.long)
    labels = torch.tensor([[-100, 5, -100, -100], [-100, 7, -100, -100]], dtype=torch.long)
    attention_mask = (input_ids != 0).long()
    block_attention_mask = torch.tensor(
        [
            [
                [True, False, False, False],
                [False, True, True, False],
                [False, True, True, False],
                [False, False, False, False],
            ],
            [
                [True, False, False, False],
                [False, True, True, False],
                [False, True, True, False],
                [False, False, False, False],
            ],
        ],
        dtype=torch.bool,
    )

    pack_losses, token_losses = module.sparse_mlm_pack_losses(
        cast(Any, model),
        input_ids,
        attention_mask,
        block_attention_mask,
        labels,
    )

    assert pack_losses.shape == (2,)
    assert token_losses.shape == (2,)
    assert bool(torch.isfinite(pack_losses).all())

    model.base.deberta.config.relative_attention = False
    with pytest.raises(RuntimeError, match="block-diagonal encoder"):
        module.sparse_mlm_pack_losses(
            cast(Any, model),
            input_ids,
            attention_mask,
            block_attention_mask,
            labels,
        )


def test_real_deberta_encoder_blocks_cross_document_attention(module: ModuleType) -> None:
    from transformers import DebertaV2Config, DebertaV2Model

    torch.manual_seed(7)
    config = DebertaV2Config(
        vocab_size=64,
        hidden_size=16,
        num_hidden_layers=2,
        num_attention_heads=4,
        intermediate_size=32,
        max_position_embeddings=32,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        relative_attention=True,
        pos_att_type=["p2c", "c2p"],
        max_relative_positions=32,
        position_biased_input=False,
        conv_kernel_size=0,
    )
    model = DebertaV2Model(config).eval()
    first = torch.tensor([[2, 10, 3, 20, 21, 3]], dtype=torch.long)
    second = torch.tensor([[2, 10, 3, 30, 31, 3]], dtype=torch.long)
    row = module.PackedRow(
        "TRAIN",
        "NEWS",
        0,
        6,
        tuple(int(value) for value in first[0]),
        (2, 3),
        (False,) * module.MAX_LENGTH,
    )
    shifted = torch.tensor([[2, 20, 21, 3, 10, 3]], dtype=torch.long)
    shifted_row = module.PackedRow(
        "TRAIN",
        "NEWS",
        1,
        6,
        tuple(int(value) for value in shifted[0]),
        (3, 2),
        (False,) * module.MAX_LENGTH,
    )

    def encode(input_ids: torch.Tensor, packed_row: Any) -> torch.Tensor:
        valid = torch.ones_like(input_ids)
        full_mask = torch.tensor(
            module.document_block_attention_mask(packed_row),
            dtype=torch.bool,
        )[:6, :6].unsqueeze(0)
        embeddings = model.embeddings(input_ids=input_ids, mask=valid)
        return model.encoder(embeddings, full_mask, return_dict=True).last_hidden_state

    with torch.no_grad():
        first_output = encode(first, row)
        second_output = encode(second, row)
        shifted_output = encode(shifted, shifted_row)

    assert torch.allclose(first_output[:, 1:3], second_output[:, 1:3], atol=1e-6, rtol=0)
    assert not torch.allclose(first_output[:, 3:6], second_output[:, 3:6])
    assert torch.allclose(first_output[:, 1:3], shifted_output[:, 4:6], atol=1e-6, rtol=0)


def test_precision_contract_prohibits_fp16(module: ModuleType) -> None:
    with module.precision_context(torch.device("cpu"), "FP32"):
        pass
    with pytest.raises(RuntimeError, match="FP16"):
        module.precision_context(torch.device("cpu"), cast(Any, "FP16"))


def test_pilot_loader_rejects_fabricated_passed_gate(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    inputs = {"documents": {"path": "x", "bytes": 1, "sha256": "a" * 64}}
    dependencies = {"trainer": {"path": "x", "bytes": 1, "sha256": "b" * 64}}
    hardware = {"device": "cpu"}
    monkeypatch.setattr(module, "verify_source_inputs", lambda: (inputs, {}))
    monkeypatch.setattr(module, "dependency_records", lambda: dependencies)
    monkeypatch.setattr(module, "hardware_fingerprint", lambda _device: hardware)
    prepared_manifest = {"path": "manifest.json", "bytes": 1, "sha256": "c" * 64}
    prepared_artifacts: dict[str, dict[str, int | str]] = {}
    report = {
        "schema_version": "k-fnspid-dapt-precision-pilot/v2",
        "status": "PRECISION_SELECTED",
        "generated_at": "2026-07-16T00:00:00+00:00",
        "pilot_pack_count": module.PILOT_PACK_COUNT,
        "pilot_order": "canonical epoch-0 shuffle first 1024 packs",
        "seed": module.SEED,
        "prepared_manifest": prepared_manifest,
        "prepared_artifacts": prepared_artifacts,
        "input_artifacts": inputs,
        "dependency_artifacts": dependencies,
        "hardware_fingerprint": hardware,
        "fp32": {},
        "bf16": {"status": "PASS"},
        "bf16_gate": {"passed": True},
        "selected_precision": "BF16",
        "fp16_allowed": False,
        "artifact_promoted": False,
    }
    path = tmp_path / "pilot.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(RuntimeError, match="필드 계약"):
        module.load_pilot_report(
            path,
            prepared_manifest_record=prepared_manifest,
            prepared_artifacts=prepared_artifacts,
            device=torch.device("cpu"),
        )


def test_atomic_outputs_refuse_overwrite_and_symlink(module: ModuleType, tmp_path: Path) -> None:
    output = tmp_path / "artifact.json"
    module._atomic_write_new(output, b"first")
    assert output.read_bytes() == b"first"
    with pytest.raises(RuntimeError, match="이미 존재"):
        module._atomic_write_new(output, b"second")

    target = tmp_path / "target"
    target.write_bytes(b"target")
    symlink = tmp_path / "link"
    symlink.symlink_to(target)
    with pytest.raises(RuntimeError, match="이미 존재"):
        module._atomic_write_new(symlink, b"replacement")

    unsafe_directory = tmp_path / "unsafe-artifact"
    unsafe_directory.mkdir()
    (unsafe_directory / "optimizer.pt").write_bytes(b"pickle-capable")
    with pytest.raises(RuntimeError, match="pickle"):
        module.directory_artifact_manifest(unsafe_directory)


def test_safe_checkpoint_round_trip_and_context_tamper_rejection(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    torch.manual_seed(123)
    model = torch.nn.Linear(3, 2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda step: 1.0 - step / 10)
    loss = model(torch.ones(2, 3)).sum()
    loss.backward()
    optimizer.step()
    scheduler.step()
    optimizer.zero_grad(set_to_none=True)
    expected_parameters = {
        name: parameter.detach().clone() for name, parameter in model.named_parameters()
    }
    context = "a" * 64
    training_state = {
        "next_window_index": 1,
        "update_count": 1,
        "microbatch_count": 1,
        "pack_loss_sum": 1.25,
        "pack_count": 8,
        "consecutive_large_gradients": 0,
        "peak_memory": 0,
        "memory_samples": [0],
        "last_window_microbatch_count": 1,
        "last_window_pack_count": 8,
    }
    checkpoint_root = tmp_path / "checkpoints"
    module._save_training_checkpoint(
        checkpoint_root=checkpoint_root,
        model=cast(Any, model),
        optimizer=optimizer,
        scheduler=scheduler,
        context_sha256=context,
        state=training_state,
    )
    expected_random = torch.rand(4)
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
    torch.manual_seed(999)

    restored = module._load_training_checkpoint(
        checkpoint_path=checkpoint_root / "checkpoint-000001",
        checkpoint_root=checkpoint_root,
        model=cast(Any, model),
        optimizer=optimizer,
        scheduler=scheduler,
        context_sha256=context,
    )

    assert restored == training_state
    assert torch.equal(torch.rand(4), expected_random)
    for name, parameter in model.named_parameters():
        assert torch.equal(parameter, expected_parameters[name])
    assert not list(checkpoint_root.rglob("*.pkl"))
    assert not list(checkpoint_root.rglob("*.bin"))
    with pytest.raises(RuntimeError, match="context"):
        module._load_training_checkpoint(
            checkpoint_path=checkpoint_root / "checkpoint-000001",
            checkpoint_root=checkpoint_root,
            model=cast(Any, model),
            optimizer=optimizer,
            scheduler=scheduler,
            context_sha256="b" * 64,
        )


def test_oracle_recipe_hash_masks_only_reviewed_value_blocks(module: ModuleType) -> None:
    source = SCRIPT.read_bytes()
    changed = (
        source.replace(
            b'PACK_ORACLE_STATUS = "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3"',
            b'PACK_ORACLE_STATUS = "LOCKED"',
        )
        .replace(
            b"PACK_EXPECTED: dict[str, Any] = {",
            b'PACK_EXPECTED: dict[str, Any] = {"reviewed": 1,',
        )
        .replace(
            b"TOTAL_UPDATES = 3_908",
            b"TOTAL_UPDATES = 4_000",
        )
    )

    assert module._normalize_oracle_recipe_source(source) == (
        module._normalize_oracle_recipe_source(changed)
    )
    with pytest.raises(RuntimeError, match="mutable source block"):
        module._normalize_oracle_recipe_source(b"missing markers")


def _synthetic_oracle_values(module: ModuleType) -> tuple[dict[str, Any], dict[str, Any]]:
    tokenization = {
        "split_count": module.EXPECTED["split_count"],
        "full_text_count": {"NEWS": 1, "DISCLOSURE": 1},
        "raw_token_count": {"title": 100, "snippet": 80, "full": 60},
        "used_token_count": {"title": 90, "snippet": 70, "full": 50},
    }
    pack_count = {
        "TRAIN": {"NEWS": 2, "DISCLOSURE": 3},
        "VALIDATION": {"NEWS": 1, "DISCLOSURE": 1},
    }
    packing = {
        "pack_count": pack_count,
        "segment_token_count": 1_000,
        "packed_non_padding_token_count": 1_007,
        "padded_token_count": {
            "TRAIN": 5 * module.MAX_LENGTH,
            "VALIDATION": 2 * module.MAX_LENGTH,
        },
        "canonical_hashes": {
            name: sha256(name.encode()).hexdigest() for name in module.PACK_EXPECTED_HASH_FIELDS
        },
    }
    return tokenization, packing


def _synthetic_inventory(module: ModuleType) -> Any:
    protected = module.ProtectedComponent(
        keys={name: frozenset({f"{name}-value"}) for name in module.COMPONENT_KEY_CODES},
        document_ids=frozenset({"protected-document"}),
        iteration_count=1,
        key_set_sha256="1" * 64,
    )
    fuzzy_audit = {
        "policy_version": "allpairs-frequency-prefix-exact-dice-v3",
        "scope": (
            "dual-cutoff-documents-plus-exact-identity-protected-components-"
            "plus-protected-seeds-cross-source"
        ),
        "parquet_full_scan_count": 4,
        "scoped_corpus_document_count": 2,
        "candidate_generation": {
            "algorithm": "AllPairs/PPJoin global-frequency prefix filtering",
            "maximum_candidates_per_document_fail_closed": (
                module.FUZZY_MAX_CANDIDATES_PER_DOCUMENT
            ),
            "candidate_truncation_allowed": False,
            "source_type_partitioned": False,
        },
        "verification": {
            "method": "exact sorted-shingle intersection and integer Dice",
            "candidate_recall_contract": "complete for the fixed Dice threshold",
            "transitive_closure": "union-find over exact/identity/fuzzy edges",
        },
        "signature_count_including_protected": 3,
        "global_shingle_vocabulary_count": 100,
        "total_corpus_signature_token_ids": 80,
        "prefix_posting_count": 12,
        "candidate_document_count": 2,
        "candidate_pair_count": 2,
        "length_filtered_pair_count": 2,
        "exact_verified_pair_count": 2,
        "maximum_observed_candidates_per_document": 1,
        "matched_pair_count": 1,
        "cross_source_matched_pair_count": 1,
        "corpus_union_edge_count": 1,
        "protected_seed_edge_count": 1,
        "deterministic_storage_lower_bound_bytes": 368,
        "pre_fuzzy_exact_identity_protected_component_count": 1,
        "pre_fuzzy_exact_identity_protected_document_count": 1,
        "pre_fuzzy_exact_identity_protected_source_document_count": {
            "NEWS": 1,
            "DISCLOSURE": 0,
        },
        "fuzzy_direct_increment_pre_fuzzy_component_count": 0,
        "fuzzy_direct_increment_document_count": 0,
        "fuzzy_direct_increment_source_document_count": {"NEWS": 0, "DISCLOSURE": 0},
        "fuzzy_transitive_only_increment_pre_fuzzy_component_count": 0,
        "fuzzy_transitive_only_increment_document_count": 0,
        "fuzzy_transitive_only_increment_source_document_count": {
            "NEWS": 0,
            "DISCLOSURE": 0,
        },
        "fuzzy_total_increment_pre_fuzzy_component_count": 0,
        "fuzzy_total_increment_document_count": 0,
        "post_fuzzy_protected_pre_fuzzy_component_membership_count": 1,
        "post_fuzzy_protected_component_count": 1,
        "post_fuzzy_protected_component_merge_reduction": 0,
        "post_fuzzy_protected_document_count": 1,
        "post_fuzzy_protected_source_document_count": {"NEWS": 1, "DISCLOSURE": 0},
        "protection_increment_categories_disjoint": True,
        "protection_increment_document_conservation_verified": True,
        "protection_increment_component_conservation_verified": True,
        "train_validation_fuzzy_cross_split_after_component_split": 0,
        "remaining_eligible_protected_fuzzy_match_document_count": 0,
    }
    return module.CorpusInventory(
        protected=protected,
        source_document_count={"NEWS": 2, "DISCLOSURE": 2},
        raw_cutoff_count={"NEWS": 1, "DISCLOSURE": 1},
        purged_cutoff_count={"NEWS": 0, "DISCLOSURE": 0},
        eligible_count={"NEWS": 1, "DISCLOSURE": 1},
        split_count={
            "TRAIN": {"NEWS": 1, "DISCLOSURE": 0},
            "VALIDATION": {"NEWS": 0, "DISCLOSURE": 1},
        },
        eligible_ids_sha256="2" * 64,
        split_sha256="3" * 64,
        row_assignments=b"\x01\x02",
        row_assignments_sha256="4" * 64,
        component_count=2,
        duplicate_key_audit={
            name: {
                "eligible_duplicate_key_count": 0,
                "train_only": 0,
                "validation_only": 0,
                "cross_split": 0,
            }
            for name in module.COMPONENT_KEY_CODES
        },
        exact_text_gate_audit={"policy": "synthetic"},
        component_size_audit={"policy": "synthetic"},
        fuzzy_near_duplicate_audit=fuzzy_audit,
    )


def test_inventory_oracle_derivation_review_and_lock_are_separate(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    inventory = _synthetic_inventory(module)
    inputs = {"documents": {"path": "documents", "bytes": 1, "sha256": "a" * 64}}
    recipes = {"trainer": {"path": "trainer", "bytes": 1, "sha256": "b" * 64}}
    software = {"runtime": "synthetic"}
    monkeypatch.setattr(
        module,
        "INVENTORY_ORACLE_STATUS",
        "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3",
    )
    monkeypatch.setattr(module, "verify_source_inputs", lambda: (inputs, {}))
    monkeypatch.setattr(module, "oracle_recipe_records", lambda: recipes)
    monkeypatch.setattr(module, "oracle_software_fingerprint", lambda: software)
    monkeypatch.setattr(module, "compute_corpus_inventory", lambda **_: inventory)
    report_path = tmp_path / "inventory-derivation.json"
    receipt_path = tmp_path / "inventory-review.json"

    result = module.derive_inventory_oracle(
        report_path=report_path,
        actor_id="codex:inventory-derivation",
    )
    report = module.load_inventory_oracle_derivation_report(report_path)

    assert result["status"] == "INVENTORY_ORACLE_DERIVED_PENDING_REVIEW"
    assert report["prepared_artifact_promoted"] is False
    assert report["pack_oracle_derived"] is False
    assert report["performance"]["elapsed_seconds"] >= 0
    with pytest.raises(RuntimeError, match="reviewer ID"):
        module.record_inventory_oracle_review(
            derivation_report_path=report_path,
            receipt_path=receipt_path,
            reviewer_id="codex:inventory-derivation",
            review_note="self review must fail",
        )

    module.record_inventory_oracle_review(
        derivation_report_path=report_path,
        receipt_path=receipt_path,
        reviewer_id="codex:inventory-independent-review",
        review_note="AllPairs completeness, transitive union, 성능 계측을 독립 검토함",
    )
    receipt = module.load_inventory_oracle_review_receipt(
        receipt_path,
        derivation_report_path=report_path,
    )
    assert receipt["review_checklist"] == module.INVENTORY_ORACLE_REVIEW_CHECKLIST

    monkeypatch.setattr(module, "INVENTORY_ORACLE_STATUS", "LOCKED")
    monkeypatch.setattr(module, "EXPECTED", report["candidate_expected_counts"])
    monkeypatch.setattr(module, "EXPECTED_HASHES", report["candidate_expected_hashes"])
    monkeypatch.setattr(
        module,
        "INVENTORY_ORACLE_REVIEW_RECEIPT_SHA256",
        module.sha256_file(receipt_path),
    )
    monkeypatch.setattr(module, "DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT", report_path)
    monkeypatch.setattr(module, "DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT", receipt_path)

    locked = module.require_locked_inventory_oracle()
    assert locked["candidate_sha256"] == report["candidate_sha256"]
    lock_record = module.inventory_oracle_lock_record()
    assert lock_record["candidate_sha256"] == report["candidate_sha256"]
    assert lock_record["reviewer_id"] == "codex:inventory-independent-review"


def test_oracle_provenance_bundle_is_self_contained_and_hash_bound(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source_paths = {
        "DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT": tmp_path / "inventory-derive.json",
        "DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT": tmp_path / "inventory-review.json",
        "DEFAULT_PACK_ORACLE_DERIVATION_REPORT": tmp_path / "pack-derive.json",
        "DEFAULT_PACK_ORACLE_REVIEW_RECEIPT": tmp_path / "pack-review.json",
    }
    for index, (attribute, path) in enumerate(source_paths.items()):
        path.write_text(json.dumps({"index": index}) + "\n", encoding="utf-8")
        monkeypatch.setattr(module, attribute, path)
    inventory_lock = {
        "derivation_report": module.artifact_record(
            source_paths["DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT"]
        ),
        "independent_review_receipt": module.artifact_record(
            source_paths["DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT"]
        ),
    }
    pack_lock = {
        "derivation_report": module.artifact_record(
            source_paths["DEFAULT_PACK_ORACLE_DERIVATION_REPORT"]
        ),
        "independent_review_receipt": module.artifact_record(
            source_paths["DEFAULT_PACK_ORACLE_REVIEW_RECEIPT"]
        ),
    }
    bundle_directory = tmp_path / "artifact"
    bundle_directory.mkdir()

    records = module.bundle_locked_oracle_provenance(
        bundle_directory,
        inventory_lock=inventory_lock,
        pack_lock=pack_lock,
    )

    assert set(records) == {
        "inventory_derivation_report",
        "inventory_independent_review_receipt",
        "pack_derivation_report",
        "pack_independent_review_receipt",
    }
    for record in records.values():
        bundled_path = bundle_directory / str(record["path"])
        assert bundled_path.is_file()
        assert module.sha256_file(bundled_path) == record["sha256"]

    bad_inventory_lock = {
        **inventory_lock,
        "derivation_report": {
            **cast(dict[str, Any], inventory_lock["derivation_report"]),
            "sha256": "0" * 64,
        },
    }
    second_directory = tmp_path / "second-artifact"
    second_directory.mkdir()
    with pytest.raises(RuntimeError, match="lock record"):
        module.bundle_locked_oracle_provenance(
            second_directory,
            inventory_lock=bad_inventory_lock,
            pack_lock=pack_lock,
        )


def test_pack_oracle_derivation_review_is_two_actor_and_non_promoting(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    inputs = {"documents": {"path": "documents", "bytes": 1, "sha256": "a" * 64}}
    recipes = {"trainer": {"path": "trainer", "bytes": 1, "sha256": "b" * 64}}
    tokenization, packing = _synthetic_oracle_values(module)
    monkeypatch.setattr(module, "INVENTORY_ORACLE_STATUS", "LOCKED")
    monkeypatch.setattr(
        module,
        "PACK_ORACLE_STATUS",
        "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3",
    )
    monkeypatch.setattr(module, "require_locked_inventory_oracle", lambda: {})
    monkeypatch.setattr(module, "verify_source_inputs", lambda: (inputs, {}))
    monkeypatch.setattr(module, "oracle_recipe_records", lambda: recipes)
    monkeypatch.setattr(module, "compute_corpus_inventory", lambda **_: object())
    monkeypatch.setattr(
        module.AutoTokenizer,
        "from_pretrained",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(module, "verify_tokenizer_contract", lambda _tokenizer: (5, 6))
    monkeypatch.setattr(
        module,
        "build_segment_files",
        lambda **kwargs: (
            tokenization
            if kwargs["enforce_pack_oracle"] is False
            else pytest.fail("derivation must not enforce an empty oracle")
        ),
    )
    monkeypatch.setattr(
        module,
        "build_pack_files",
        lambda **kwargs: (
            packing
            if kwargs["enforce_pack_oracle"] is False
            else pytest.fail("derivation must not enforce an empty oracle")
        ),
    )
    monkeypatch.setattr(
        module,
        "verify_pack_semantics",
        lambda _directory, **_kwargs: {
            "pack_count": packing["pack_count"],
            "canonical_hashes": packing["canonical_hashes"],
        },
    )
    monkeypatch.setattr(module, "runtime_environment", lambda: {"runtime": "synthetic"})
    report_path = tmp_path / "oracle-derivation.json"
    receipt_path = tmp_path / "oracle-review.json"
    scratch = tmp_path / "scratch"

    result = module.derive_pack_oracle(
        report_path=report_path,
        scratch_dir=scratch,
        actor_id="codex:derivation",
    )
    report = module.load_pack_oracle_derivation_report(report_path)

    assert result["status"] == "PACK_ORACLE_DERIVED_PENDING_REVIEW"
    assert report["semantic_reread_verified"] is True
    assert report["scratch_artifacts_retained"] is False
    assert report["prepared_artifact_promoted"] is False
    assert report["precision_pilot_executed"] is False
    assert report["training_executed"] is False
    assert not scratch.exists()
    assert not list(tmp_path.glob(".scratch.tmp-*"))
    with pytest.raises(RuntimeError, match="reviewer ID"):
        module.record_pack_oracle_review(
            derivation_report_path=report_path,
            receipt_path=receipt_path,
            reviewer_id="codex:derivation",
            review_note="self review must fail",
        )

    review = module.record_pack_oracle_review(
        derivation_report_path=report_path,
        receipt_path=receipt_path,
        reviewer_id="codex:independent-red-team",
        review_note="결정적 count/hash와 비승격 계약을 독립 검토함",
    )
    receipt = module.load_pack_oracle_review_receipt(
        receipt_path,
        derivation_report_path=report_path,
    )

    assert review["candidate_sha256"] == report["candidate_sha256"]
    assert receipt["reviewer_id"] != receipt["derivation_actor_id"]
    assert receipt["review_checklist"] == module.PACK_ORACLE_REVIEW_CHECKLIST

    monkeypatch.setattr(module, "PACK_ORACLE_STATUS", "LOCKED")
    monkeypatch.setattr(module, "PACK_EXPECTED", report["candidate_expected_counts"])
    monkeypatch.setattr(module, "PACK_EXPECTED_HASHES", report["candidate_expected_hashes"])
    monkeypatch.setattr(
        module, "PACK_ORACLE_REVIEW_RECEIPT_SHA256", module.sha256_file(receipt_path)
    )
    monkeypatch.setattr(module, "DEFAULT_PACK_ORACLE_DERIVATION_REPORT", report_path)
    monkeypatch.setattr(module, "DEFAULT_PACK_ORACLE_REVIEW_RECEIPT", receipt_path)
    monkeypatch.setattr(module, "TOTAL_UPDATES", 1)
    monkeypatch.setattr(module, "WARMUP_UPDATES", 1)

    module.require_locked_pack_oracle()
    lock_record = module.pack_oracle_lock_record()
    assert lock_record["candidate_sha256"] == report["candidate_sha256"]
    assert lock_record["reviewer_id"] == "codex:independent-red-team"


def test_pack_oracle_report_recomputes_schedule_and_rejects_tamper(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    inputs = {"documents": {"path": "documents", "bytes": 1, "sha256": "a" * 64}}
    recipes = {"trainer": {"path": "trainer", "bytes": 1, "sha256": "b" * 64}}
    tokenization, packing = _synthetic_oracle_values(module)
    counts, hashes = module._pack_oracle_candidate(tokenization, packing)
    updates = 1
    report = {
        "schema_version": "k-fnspid-dapt-pack-oracle-derivation/v1",
        "status": "DERIVED_PENDING_INDEPENDENT_REVIEW",
        "generated_at": "2026-07-16T00:00:00+00:00",
        "derivation_actor_id": "codex:derive",
        "inventory_oracle_status_at_derivation": "LOCKED",
        "oracle_status_at_derivation": "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3",
        "input_artifacts": inputs,
        "oracle_recipe_artifacts": recipes,
        "oracle_software_fingerprint": module.oracle_software_fingerprint(),
        "inventory_commitments": module.EXPECTED_HASHES,
        "candidate_expected_counts": counts,
        "candidate_expected_hashes": hashes,
        "candidate_total_updates": updates + 1,
        "candidate_warmup_updates": 1,
        "candidate_sha256": "c" * 64,
        "semantic_reread_verified": True,
        "scratch_artifacts_retained": False,
        "prepared_artifact_promoted": False,
        "precision_pilot_executed": False,
        "training_executed": False,
        "runtime_environment": {},
    }
    path = tmp_path / "tampered.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(module, "verify_source_inputs", lambda: (inputs, {}))
    monkeypatch.setattr(module, "oracle_recipe_records", lambda: recipes)

    with pytest.raises(RuntimeError, match="schedule/hash"):
        module.load_pack_oracle_derivation_report(path)


def test_genuine_pilot_trial_shape_is_accepted_by_loader(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(module, "build_dapt_model", lambda _device: object())
    monkeypatch.setattr(module, "trainable_state_sha256", lambda _model: "a" * 64)
    evaluations = iter(
        [
            {
                "pack_count": 1_024,
                "masked_token_count": 100,
                "mean_nll": 2.0,
                "perplexity": math.exp(2.0),
            },
            {
                "pack_count": 1_024,
                "masked_token_count": 100,
                "mean_nll": 1.0,
                "perplexity": math.exp(1.0),
            },
        ]
    )
    monkeypatch.setattr(module, "evaluate_nll", lambda *_args, **_kwargs: next(evaluations))
    monkeypatch.setattr(
        module,
        "train_pack_indices",
        lambda *_args, **_kwargs: {
            "pack_count": 1_024,
            "microbatch_count": 128,
            "update_count": 16,
            "mean_pack_loss": 1.5,
            "last_window_microbatch_count": 8,
            "last_window_pack_count": 64,
            "peak_driver_allocated_bytes": 0,
            "driver_memory_samples": [0] * 128,
            "final_learning_rate": 1e-6,
            "resumed_from": None,
            "checkpoint_manifests": [],
        },
    )

    trial = module.run_precision_trial(
        store=cast(Any, object()),
        indices=list(range(1_024)),
        allowed_ids=(5, 6),
        device=torch.device("cpu"),
        precision="FP32",
    )

    assert "resumed_from" not in trial["training"]
    assert "checkpoint_manifests" not in trial["training"]
    module._validate_passed_precision_trial(trial, precision="FP32")


def test_model_recipe_is_frozen_lora_over_all_twelve_layers() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'target_modules=["query_proj", "value_proj"]' in source
    assert "layers_to_transform=list(range(12))" in source
    assert "r=16" in source
    assert "lora_alpha=32" in source
    assert "lora_dropout=0.05" in source
    assert 'parameter.requires_grad and "lora_" not in name' in source
