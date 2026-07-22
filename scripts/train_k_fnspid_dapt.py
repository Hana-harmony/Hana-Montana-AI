from __future__ import annotations

import argparse
import ast
import base64
import ctypes
import errno
import importlib.metadata
import json
import math
import os
import platform
import random
import re
import resource
import shutil
import stat
import struct
import sys
import time
import unicodedata
import uuid
from array import array
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, cast

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import torch
import torch.nn.functional as functional
from huggingface_hub import hf_hub_download
from peft import LoraConfig, PeftModel, get_peft_model
from safetensors.torch import load_file as load_safetensors
from safetensors.torch import save_file as save_safetensors
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer, get_linear_schedule_with_warmup

from hannah_montana_ai.training.sentiment_protocol import canonical_sentiment_url

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_PATH = PROJECT_ROOT / "data/k_fnspid/v4/documents.parquet"
DATASET_MANIFEST_PATH = PROJECT_ROOT / "data/k_fnspid/v4/manifest.json"
NEWS_DEVELOPMENT_PATH = PROJECT_ROOT / "data/evaluation/k_fnspid_sentiment_development_gold.jsonl"
DISCLOSURE_DEVELOPMENT_PATH = (
    PROJECT_ROOT / "data/evaluation/k_fnspid_disclosure_sentiment_development_gold.jsonl"
)
NEWS_RESERVATION_PATH = PROJECT_ROOT / "data/gold/confirmatory_sealed_test_review.jsonl"
DISCLOSURE_RESERVATION_PATH = (
    PROJECT_ROOT / "data/gold/disclosure_confirmatory_sealed_test_review.jsonl"
)
DEFAULT_PREPARED_DIR = PROJECT_ROOT / "data/k_fnspid/v4_dapt_temporal_v2"
DEFAULT_PILOT_REPORT = PROJECT_ROOT / "reports/k-fnspid-v4-kf-deberta-dapt-pilot-v2.json"
DEFAULT_ARTIFACT_DIR = (
    PROJECT_ROOT / "artifacts/pretraining/kf-deberta-k-fnspid-v4-dapt-temporal-v2"
)
DEFAULT_CHECKPOINT_DIR = (
    PROJECT_ROOT / "artifacts/pretraining/.kf-deberta-k-fnspid-v4-dapt-checkpoints-v2"
)
DEFAULT_PACK_ORACLE_DERIVATION_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-v4-dapt-pack-oracle-derivation-v3.json"
)
DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-v4-dapt-inventory-oracle-derivation-v4.json"
)
DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT = (
    PROJECT_ROOT / "reports/k-fnspid-v4-dapt-inventory-oracle-review-v4.json"
)
DEFAULT_PACK_ORACLE_REVIEW_RECEIPT = (
    PROJECT_ROOT / "reports/k-fnspid-v4-dapt-pack-oracle-review-v3.json"
)
DEFAULT_PACK_ORACLE_SCRATCH_DIR = (
    PROJECT_ROOT / "data/k_fnspid/.v4-dapt-pack-oracle-derivation-work"
)

BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
DOCUMENTS_SHA256 = "045fb260f2145345f81f76f381d2631e884a1cbc8d6208758702b4564f582e03"
DATASET_MANIFEST_SHA256 = "80b08190c538c1baeef418e4b50d5d9cb2ff9980ceb784a85b2988048ccc91c4"
BASE_FILE_HASHES = {
    "pytorch_model.bin": "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c",
    "config.json": "4cba21a6fb53b5d75e2b7af83756eeb6d5e8a471164130999be395e1b8ff0848",
    "tokenizer.json": "915388090e2d63e3869c54b5334d6005e453a51de12088d908175dd765fd8372",
    "tokenizer_config.json": "d9273237da0f2143974a8eccdc50a733fcda064528299f7295e6434226cdbda1",
    "special_tokens_map.json": "311de3f4eed9d76a43bf0d71f10e62e086ca65ccce9f15d5da0d2098bf519ecc",
    "vocab.txt": "f0b8ae70418060f22ec301511a6337ad49a7fb0f60a8bf9091b373aba9c0c3e0",
}
PROTECTED_FILE_HASHES = {
    NEWS_DEVELOPMENT_PATH: "f433e4cdc5372594d54de19083519278aae51b0385e310410b2e738d4c7d0f55",
    DISCLOSURE_DEVELOPMENT_PATH: (
        "8527d567c303d91c45d6e1dbe55a28e7725bef8bfb28f60f7962016c071c1e07"
    ),
    NEWS_RESERVATION_PATH: "2d901eae6d7a84dd2e85fff74f4a942a8d5fe8ecbd2f569a3838bf2b9d28c8c5",
    DISCLOSURE_RESERVATION_PATH: (
        "0bd8258338bf1bc0f1a4c8cff832c5f1affe19e5d103c2032d56e602793879dd"
    ),
}
SEALED_RESERVATION_PARTITIONS = {
    NEWS_RESERVATION_PATH: "CONFIRMATORY_SEALED_TEST_REVIEW",
    DISCLOSURE_RESERVATION_PATH: "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
}
FORBIDDEN_SEALED_RESERVATION_FIELDS = frozenset(
    {
        "sentiment",
        "sampling_stratum",
        "weak_label",
        "weak_sentiment",
        "rule_confidence",
        "inclusion_probability",
        "analysis_weight",
        "design_weight",
    }
)

CUTOFF_TIMESTAMP = "2026-04-01T00:00:00+09:00"
CUTOFF_TRADE_DATE = "2026-04-01"
SPLIT_SALT = b"k-fnspid-v4-dapt-dual-cutoff-20260401-val-v1\0"
COMPONENT_KEY_SALT = b"k-fnspid-v4-dapt-component-key-v2\0"
NORMALIZED_TEXT_SALT = b"k-fnspid-v4-dapt-normalized-exact-text-v1\0"
PACK_SALT = b"k-fnspid-v4-dapt-pack-v1\0"
TRAIN_MASK_SALT = b"k-fnspid-v4-dapt-train-mask-v1\0"
VALIDATION_MASK_SALT = b"k-fnspid-v4-dapt-val-mask-v1\0"
EPOCH_ORDER_SALT = b"k-fnspid-v4-dapt-epoch-order-v1\0"
SPLIT_CODES = {"TRAIN": 0, "VALIDATION": 1}
SOURCE_CODES = {"NEWS": 0, "DISCLOSURE": 1}
SOURCE_MARKERS = {"NEWS": 878, "DISCLOSURE": 1292}
FIELD_MARKERS = {"TITLE": 3348, "SUMMARY": 7633, "BODY": 12050}
MARKER_IDS = frozenset((*SOURCE_MARKERS.values(), *FIELD_MARKERS.values()))
SPECIAL_IDS = frozenset({0, 1, 2, 3, 4})
PAD_ID = 0
UNK_ID = 1
CLS_ID = 2
SEP_ID = 3
MASK_ID = 4
VOCAB_SIZE = 130_000
MAX_LENGTH = 256
PACK_CAPACITY = 255
SEED = 20_260_716
EPOCH_INDEX = 0
MICRO_BATCH_SIZE = 8
ACCUMULATION_STEPS = 8
EFFECTIVE_BATCH_SIZE = 64
LEARNING_RATE = 5e-5
ADAM_BETAS = (0.9, 0.98)
ADAM_EPSILON = 1e-6
WEIGHT_DECAY = 0.01
MAX_GRAD_NORM = 1.0
DRIVER_MEMORY_LIMIT_BYTES = 18 * 1024**3
PILOT_PACK_COUNT = 1_024
CHECKPOINT_INTERVAL_UPDATES = 128
ALLOWED_RANDOM_VOCAB_SHA256 = "ef31b0efc4cf81b95b596441d6e51732df68ead153ed8bce1d9499f8b13d273a"
SERIALIZER_BYTE_ORDER = "big-endian"
UNUSED_TOKEN_COUNT = 566
# PACK_ORACLE_LOCK_BEGIN
# 이 블록만 derivation/review 뒤 바꾼다. semantic recipe hash에서는 블록 전체를 마스킹한다.
INVENTORY_ORACLE_STATUS = "LOCKED"
INVENTORY_ORACLE_REVIEW_RECEIPT_SHA256 = (
    "3a58702712fd01960d18a42f9f8cd035339e69acc59c05b444b606f6cf90521f"
)
PACK_ORACLE_STATUS = "LOCKED"
PACK_ORACLE_REVIEW_RECEIPT_SHA256 = (
    "fd3a51e4f464ba9a5a63a2997df21662a4e2c638703f11fb0f1bf10a5c520ff9"
)
TOTAL_UPDATES = 3_908
WARMUP_UPDATES = 196
# PACK_ORACLE_LOCK_END
EXACT_TEXT_MIN_ALNUM = 32
EXACT_TEXT_MIN_DISTINCT_ALNUM = 12
EXACT_TEXT_MIN_FULL_TEXT_ALNUM = 128
EXACT_TEXT_REDUNDANT_FIELD_MAX_DELTA = 24
EXACT_TEXT_GATE_STATUSES = (
    "accepted_full_text",
    "accepted_nonredundant_title_snippet",
    "rejected_empty",
    "rejected_low_alphanumeric_count",
    "rejected_low_character_diversity",
    "rejected_missing_title_or_snippet",
    "rejected_redundant_title_snippet",
)
FUZZY_AUDIT_SALT = b"k-fnspid-v4-dapt-protected-fuzzy-audit-v1\0"
FUZZY_TEXT_MAX_CHARS = 512
FUZZY_SHINGLE_WIDTH = 4
FUZZY_MIN_TEXT_CHARS = 32
FUZZY_MIN_SHINGLE_COUNT = 24
FUZZY_MIN_DICE_SIMILARITY_BPS = 9_200
FUZZY_JACCARD_NUMERATOR = 23
FUZZY_JACCARD_DENOMINATOR = 27
FUZZY_MAX_CANDIDATES_PER_DOCUMENT = 100_000
INVENTORY_FUZZY_OPERATION_FIELDS = frozenset(
    {
        "parquet_full_scan_count",
        "scoped_corpus_document_count",
        "signature_count_including_protected",
        "global_shingle_vocabulary_count",
        "total_corpus_signature_token_ids",
        "prefix_posting_count",
        "candidate_document_count",
        "candidate_pair_count",
        "length_filtered_pair_count",
        "exact_verified_pair_count",
        "maximum_observed_candidates_per_document",
        "matched_pair_count",
        "cross_source_matched_pair_count",
        "corpus_union_edge_count",
        "protected_seed_edge_count",
        "deterministic_storage_lower_bound_bytes",
    }
)

# INVENTORY_ORACLE_VALUES_BEGIN
EXPECTED = {
    "source_document_count": {"NEWS": 524_696, "DISCLOSURE": 722_989},
    "raw_cutoff_count": {"NEWS": 419_969, "DISCLOSURE": 699_813},
    "protected_component_document_count": 2_826,
    "protected_key_count": {
        "document_id": 2_826,
        "canonical_url": 2_679,
        "content_hash": 2_826,
        "event_cluster_id": 2_346,
        "normalized_exact_text_hash": 2_243,
    },
    "purged_cutoff_count": {"NEWS": 709, "DISCLOSURE": 782},
    "eligible_count": {"NEWS": 419_260, "DISCLOSURE": 699_031},
    "split_count": {
        "TRAIN": {"NEWS": 415_197, "DISCLOSURE": 692_015},
        "VALIDATION": {"NEWS": 4_063, "DISCLOSURE": 7_016},
    },
    "eligible_component_count": 967_550,
    "duplicate_key_audit": {
        "document_id": {
            "eligible_duplicate_key_count": 0,
            "train_only": 0,
            "validation_only": 0,
            "cross_split": 0,
        },
        "canonical_url": {
            "eligible_duplicate_key_count": 23_597,
            "train_only": 23_391,
            "validation_only": 206,
            "cross_split": 0,
        },
        "content_hash": {
            "eligible_duplicate_key_count": 0,
            "train_only": 0,
            "validation_only": 0,
            "cross_split": 0,
        },
        "event_cluster_id": {
            "eligible_duplicate_key_count": 57_673,
            "train_only": 57_129,
            "validation_only": 544,
            "cross_split": 0,
        },
        "normalized_exact_text_hash": {
            "eligible_duplicate_key_count": 3_837,
            "train_only": 3_816,
            "validation_only": 21,
            "cross_split": 0,
        },
    },
}
EXPECTED_HASHES = {
    "protected_key_set": "dc2d8749bb38826b405c893545722ec2bb968feb734b7e5ff3df93be515f5be8",
    "eligible_ordered_document_ids": (
        "09532e7d1e244e7e4c1a0a2a4c768b16d411cfba2ec1e691e9c95589cb05d09d"
    ),
    "split_jsonl": "eb5fb296b8373e484ea25440ce2f3a637b2576b3066e73b593ffc13ee1a05342",
    "row_assignments": "71b074d3ce597e2ea3ec2b76c5e4b05b4c4ebc852b523e1599d897e0f98f5176",
    "exact_text_gate_audit": "0f079632cb9d02b46984b32e4b44edc6b6cefaab2eb103fa09b79ba5ef2de960",
    "component_size_audit": "fe3ef7f345c5ea2684ba9b6e10c13f011da659e4da51d72014ba7659f2a233d0",
    "fuzzy_near_duplicate_audit": (
        "7151806bd337002dabde1b7243ced7ebe11148b76108e1c917d3d361d30331e3"
    ),
    "allowed_random_token_ids": ALLOWED_RANDOM_VOCAB_SHA256,
}
# INVENTORY_ORACLE_VALUES_END

# AllPairs fuzzy v3 inventory가 잠긴 뒤 pack derivation-only로 산출한다.
# 독립 검토하기 전까지 pack candidate를 학습에 사용하지 않는다.
# PACK_ORACLE_VALUES_BEGIN
PACK_EXPECTED: dict[str, Any] = {
    "full_text_count": {"NEWS": 3_792, "DISCLOSURE": 7_104},
    "raw_token_count": {
        "title": 18_993_463,
        "snippet": 36_556_505,
        "full": 28_333_791,
    },
    "used_token_count": {
        "title": 18_991_508,
        "snippet": 36_556_460,
        "full": 2_183_933,
    },
    "pack_count": {
        "TRAIN": {"NEWS": 147_532, "DISCLOSURE": 102_526},
        "VALIDATION": {"NEWS": 1_457, "DISCLOSURE": 1_050},
    },
    "segment_token_count": 62_215_961,
    "packed_non_padding_token_count": 62_468_526,
    "padded_token_count": {"TRAIN": 64_014_848, "VALIDATION": 641_792},
}
PACK_EXPECTED_HASHES: dict[str, str] = {
    "unmasked_packed_ids": (
        "50087c5707dc03b00650ccf8e5d9a6bc498167da179d74a5e4cdda438364d63a"
    ),
    "pack_lineage_jsonl": (
        "89f21c7a4bd525623382e4b18348a9df87bfe5933a2f470683ce00202ecfe3e8"
    ),
    "train_epoch0_masks": (
        "0d169e23c920eb6533ed9a139ee0ed693525d712fd09110c68c92167707a4e36"
    ),
    "validation_fixed_masks": (
        "1b0a6d8103174288455c41c63aa202eff08ddd82af05aa117f37bc46ab5a5541"
    ),
}
# PACK_ORACLE_VALUES_END
PACK_EXPECTED_FIELDS = {
    "full_text_count",
    "raw_token_count",
    "used_token_count",
    "pack_count",
    "segment_token_count",
    "packed_non_padding_token_count",
    "padded_token_count",
}
PACK_EXPECTED_HASH_FIELDS = {
    "unmasked_packed_ids",
    "pack_lineage_jsonl",
    "train_epoch0_masks",
    "validation_fixed_masks",
}


def require_locked_inventory_oracle() -> dict[str, Any]:
    if INVENTORY_ORACLE_STATUS != "LOCKED":
        raise RuntimeError("AllPairs fuzzy v3 inventory oracle이 검토·고정되지 않았습니다.")
    if not re.fullmatch(r"[0-9a-f]{64}", INVENTORY_ORACLE_REVIEW_RECEIPT_SHA256):
        raise RuntimeError("inventory oracle 독립 검토 receipt hash가 고정되지 않았습니다.")
    verify_exact_file(
        DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT,
        INVENTORY_ORACLE_REVIEW_RECEIPT_SHA256,
        "inventory oracle 독립 검토 receipt",
    )
    receipt = load_inventory_oracle_review_receipt(
        DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT,
        derivation_report_path=DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT,
    )
    if (
        receipt["candidate_expected_counts"] != EXPECTED
        or receipt["candidate_expected_hashes"] != EXPECTED_HASHES
    ):
        raise RuntimeError("inventory 검토 receipt와 source oracle 값이 다릅니다.")
    return receipt


def require_locked_pack_oracle() -> None:
    require_locked_inventory_oracle()
    if (
        PACK_ORACLE_STATUS != "LOCKED"
        or set(PACK_EXPECTED) != PACK_EXPECTED_FIELDS
        or set(PACK_EXPECTED_HASHES) != PACK_EXPECTED_HASH_FIELDS
    ):
        raise RuntimeError(
            "연결요소 v2 pack oracle이 검토·고정되지 않아 prepare/pilot/train을 차단합니다."
        )
    if not re.fullmatch(r"[0-9a-f]{64}", PACK_ORACLE_REVIEW_RECEIPT_SHA256):
        raise RuntimeError("pack oracle 독립 검토 receipt hash가 고정되지 않았습니다.")
    verify_exact_file(
        DEFAULT_PACK_ORACLE_REVIEW_RECEIPT,
        PACK_ORACLE_REVIEW_RECEIPT_SHA256,
        "pack oracle 독립 검토 receipt",
    )
    receipt = load_pack_oracle_review_receipt(
        DEFAULT_PACK_ORACLE_REVIEW_RECEIPT,
        derivation_report_path=DEFAULT_PACK_ORACLE_DERIVATION_REPORT,
    )
    if (
        receipt["candidate_expected_counts"] != PACK_EXPECTED
        or receipt["candidate_expected_hashes"] != PACK_EXPECTED_HASHES
    ):
        raise RuntimeError("검토 receipt와 source의 pack oracle 값이 다릅니다.")
    expected_train_packs = sum(PACK_EXPECTED["pack_count"]["TRAIN"].values())
    if math.ceil(expected_train_packs / EFFECTIVE_BATCH_SIZE) != TOTAL_UPDATES:
        raise RuntimeError("pack oracle과 TOTAL_UPDATES 계약이 다릅니다.")
    if math.ceil(TOTAL_UPDATES * 0.05) != WARMUP_UPDATES:
        raise RuntimeError("TOTAL_UPDATES와 warmup 5% 계약이 다릅니다.")


def inventory_oracle_lock_record() -> dict[str, Any]:
    receipt = require_locked_inventory_oracle()
    return {
        "status": INVENTORY_ORACLE_STATUS,
        "expected_counts": EXPECTED,
        "expected_hashes": EXPECTED_HASHES,
        "candidate_sha256": receipt["candidate_sha256"],
        "derivation_report": artifact_record(DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT),
        "independent_review_receipt": artifact_record(DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT),
        "reviewer_id": receipt["reviewer_id"],
    }


def pack_oracle_lock_record() -> dict[str, Any]:
    if INVENTORY_ORACLE_STATUS != "LOCKED" or PACK_ORACLE_STATUS != "LOCKED":
        raise RuntimeError("pack oracle lock provenance는 LOCKED 상태에서만 생성합니다.")
    receipt = load_pack_oracle_review_receipt(
        DEFAULT_PACK_ORACLE_REVIEW_RECEIPT,
        derivation_report_path=DEFAULT_PACK_ORACLE_DERIVATION_REPORT,
    )
    return {
        "status": PACK_ORACLE_STATUS,
        "expected_counts": PACK_EXPECTED,
        "expected_hashes": PACK_EXPECTED_HASHES,
        "candidate_sha256": receipt["candidate_sha256"],
        "derivation_report": artifact_record(DEFAULT_PACK_ORACLE_DERIVATION_REPORT),
        "independent_review_receipt": artifact_record(DEFAULT_PACK_ORACLE_REVIEW_RECEIPT),
        "reviewer_id": receipt["reviewer_id"],
    }


def bundle_locked_oracle_provenance(
    directory: Path,
    *,
    inventory_lock: Mapping[str, Any],
    pack_lock: Mapping[str, Any],
) -> dict[str, dict[str, int | str]]:
    sources = {
        "inventory_derivation_report": (
            DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT,
            inventory_lock.get("derivation_report"),
            "provenance/oracles/inventory-derivation.json",
        ),
        "inventory_independent_review_receipt": (
            DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT,
            inventory_lock.get("independent_review_receipt"),
            "provenance/oracles/inventory-independent-review.json",
        ),
        "pack_derivation_report": (
            DEFAULT_PACK_ORACLE_DERIVATION_REPORT,
            pack_lock.get("derivation_report"),
            "provenance/oracles/pack-derivation.json",
        ),
        "pack_independent_review_receipt": (
            DEFAULT_PACK_ORACLE_REVIEW_RECEIPT,
            pack_lock.get("independent_review_receipt"),
            "provenance/oracles/pack-independent-review.json",
        ),
    }
    bundled: dict[str, dict[str, int | str]] = {}
    for name, (source, expected_record, relative) in sources.items():
        actual_record = artifact_record(source)
        if not isinstance(expected_record, Mapping) or dict(expected_record) != actual_record:
            raise RuntimeError(f"{name} lock record와 원천 artifact가 다릅니다.")
        payload = _stable_file_payload(source)
        if (
            len(payload) != actual_record["bytes"]
            or sha256(payload).hexdigest() != actual_record["sha256"]
        ):
            raise RuntimeError(f"{name} bundle 중 원천이 변경되었습니다.")
        target = directory / relative
        _atomic_write_new(target, payload)
        copied = artifact_record(target)
        bundled[name] = {
            "path": relative,
            "bytes": copied["bytes"],
            "sha256": copied["sha256"],
        }
    return bundled


COMPONENT_KEY_CODES = {
    "document_id": 0,
    "canonical_url": 1,
    "content_hash": 2,
    "event_cluster_id": 3,
    "normalized_exact_text_hash": 4,
}

IDENTITY_COLUMNS = (
    "document_id",
    "source_url",
    "content_hash",
    "event_cluster_id",
)
COMPONENT_COLUMNS = (*IDENTITY_COLUMNS, "title", "snippet", "full_text", "source_type")
INVENTORY_COLUMNS = (
    *COMPONENT_COLUMNS,
    "published_at_kst",
    "effective_trade_date",
)
TEXT_COLUMNS = INVENTORY_COLUMNS
PUBLISHED_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00$")
TRADE_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
UNUSED_TOKEN_PATTERN = re.compile(r"\[unused\d+\]")
UNSAFE_SERIALIZED_SUFFIXES = frozenset({".bin", ".pt", ".pth", ".pkl", ".pickle", ".joblib"})


@dataclass(frozen=True, slots=True)
class Identity:
    document_id: str
    canonical_url: str
    content_hash: str
    event_cluster_id: str

    def values(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (name, value)
            for name, value in (
                ("document_id", self.document_id),
                ("canonical_url", self.canonical_url),
                ("content_hash", self.content_hash),
                ("event_cluster_id", self.event_cluster_id),
            )
            if value
        )


@dataclass(frozen=True, slots=True)
class ProtectedComponent:
    keys: dict[str, frozenset[str]]
    document_ids: frozenset[str]
    iteration_count: int
    key_set_sha256: str


@dataclass(frozen=True, slots=True)
class CorpusInventory:
    protected: ProtectedComponent
    source_document_count: dict[str, int]
    raw_cutoff_count: dict[str, int]
    purged_cutoff_count: dict[str, int]
    eligible_count: dict[str, int]
    split_count: dict[str, dict[str, int]]
    eligible_ids_sha256: str
    split_sha256: str
    row_assignments: bytes
    row_assignments_sha256: str
    component_count: int
    duplicate_key_audit: dict[str, dict[str, int]]
    exact_text_gate_audit: dict[str, Any]
    component_size_audit: dict[str, Any]
    fuzzy_near_duplicate_audit: dict[str, Any]

    @property
    def eligible_total(self) -> int:
        return sum(self.eligible_count.values())


class ComponentUnionFind:
    """문서 provenance 연결 성분을 행 순서와 무관한 대표키로 관리한다."""

    def __init__(self) -> None:
        self.parents = array("I")
        self.ranks = array("B")
        self.minimum_keys: list[bytes] = []

    def add(self, minimum_key: bytes) -> int:
        index = len(self.parents)
        self.parents.append(index)
        self.ranks.append(0)
        self.minimum_keys.append(minimum_key)
        return index

    def find(self, index: int) -> int:
        root = index
        while self.parents[root] != root:
            root = self.parents[root]
        while self.parents[index] != index:
            parent = self.parents[index]
            self.parents[index] = root
            index = parent
        return root

    def union(self, left: int, right: int) -> int:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return left_root
        if self.ranks[left_root] < self.ranks[right_root]:
            left_root, right_root = right_root, left_root
        self.parents[right_root] = left_root
        if self.ranks[left_root] == self.ranks[right_root]:
            self.ranks[left_root] += 1
        self.minimum_keys[left_root] = min(
            self.minimum_keys[left_root],
            self.minimum_keys[right_root],
        )
        return left_root

    def minimum_key(self, index: int) -> bytes:
        return self.minimum_keys[self.find(index)]


@dataclass(frozen=True, slots=True)
class SegmentMetadata:
    row_index: int
    document_id: str
    length: int
    sort_digest: bytes


@dataclass(frozen=True, slots=True)
class FuzzyGraphSignature:
    row_index: int | None
    source_type: str
    digest: str
    text_length: int
    token_ids: array[int]
    protected_seed: bool


class FuzzyAllPairsIndex:
    """빈도순 prefix filter 뒤 exact Dice로 완전 후보를 검증한다."""

    def __init__(self, *, maximum_candidates: int) -> None:
        if maximum_candidates <= 0:
            raise ValueError("fuzzy candidate 한도는 양수여야 합니다.")
        self.maximum_candidates = maximum_candidates
        self.signatures: list[FuzzyGraphSignature] = []
        self.postings: dict[int, array[int]] = {}
        self.candidate_document_count = 0
        self.candidate_pair_count = 0
        self.length_filtered_pair_count = 0
        self.exact_verified_pair_count = 0
        self.maximum_observed_candidates = 0
        self.prefix_posting_count = 0

    def add(
        self,
        signature: FuzzyGraphSignature,
        *,
        query: bool = True,
    ) -> list[tuple[int, int]]:
        token_count = len(signature.token_ids)
        if token_count < FUZZY_MIN_SHINGLE_COUNT:
            raise RuntimeError("fuzzy signature가 minimum shingle 수보다 짧습니다.")
        prefix_length = fuzzy_prefix_length(token_count)
        candidates: set[int] = set()
        if query:
            for token_id in signature.token_ids[:prefix_length]:
                candidates.update(self.postings.get(int(token_id), ()))
        candidate_count = len(candidates)
        self.maximum_observed_candidates = max(
            self.maximum_observed_candidates,
            candidate_count,
        )
        if candidate_count > self.maximum_candidates:
            raise RuntimeError(
                "AllPairs fuzzy candidate 완전 검증 한도를 초과했습니다: "
                f"{candidate_count}>{self.maximum_candidates}"
            )
        if candidates:
            self.candidate_document_count += 1
            self.candidate_pair_count += candidate_count
        matches: list[tuple[int, int]] = []
        for candidate_index in sorted(candidates):
            candidate = self.signatures[candidate_index]
            if not fuzzy_length_compatible(
                token_count,
                len(candidate.token_ids),
            ):
                continue
            self.length_filtered_pair_count += 1
            intersection = sorted_intersection_count(
                signature.token_ids,
                candidate.token_ids,
            )
            self.exact_verified_pair_count += 1
            denominator = token_count + len(candidate.token_ids)
            if 20_000 * intersection < FUZZY_MIN_DICE_SIMILARITY_BPS * denominator:
                continue
            score = (20_000 * intersection) // denominator
            matches.append((candidate_index, score))
        signature_index = len(self.signatures)
        self.signatures.append(signature)
        for token_id in signature.token_ids[:prefix_length]:
            posting = self.postings.setdefault(int(token_id), array("I"))
            posting.append(signature_index)
            self.prefix_posting_count += 1
        return matches


class ProtectionIncrementAudit:
    """fuzzy 전후 보호 성분 증분을 비중복 범주로 계수한다."""

    def __init__(
        self,
        *,
        pre_fuzzy_exact_identity_protected_roots: set[int],
        direct_match_pre_fuzzy_roots: set[int],
        post_fuzzy_protected_roots: set[int],
    ) -> None:
        self.baseline_roots = set(pre_fuzzy_exact_identity_protected_roots)
        self.direct_match_roots = set(direct_match_pre_fuzzy_roots)
        self.final_roots = set(post_fuzzy_protected_roots)
        self.protected_pre_fuzzy_roots: set[int] = set()
        self.document_count: Counter[str] = Counter()
        self.source_document_count: dict[str, Counter[str]] = {
            "BASELINE_EXACT_IDENTITY": Counter(),
            "FUZZY_DIRECT_INCREMENT": Counter(),
            "FUZZY_TRANSITIVE_ONLY_INCREMENT": Counter(),
        }

    def observe(self, *, pre_fuzzy_root: int, post_fuzzy_root: int, source_type: str) -> None:
        if source_type not in SOURCE_CODES:
            raise RuntimeError("보호 증분 source_type이 잘못되었습니다.")
        if post_fuzzy_root not in self.final_roots:
            return
        self.protected_pre_fuzzy_roots.add(pre_fuzzy_root)
        if pre_fuzzy_root in self.baseline_roots:
            category = "BASELINE_EXACT_IDENTITY"
        elif pre_fuzzy_root in self.direct_match_roots:
            category = "FUZZY_DIRECT_INCREMENT"
        else:
            category = "FUZZY_TRANSITIVE_ONLY_INCREMENT"
        self.document_count[category] += 1
        self.source_document_count[category][source_type] += 1

    def finalize(self) -> dict[str, Any]:
        if not self.baseline_roots <= self.protected_pre_fuzzy_roots:
            raise RuntimeError("pre-fuzzy 보호 성분이 post-fuzzy 보호 집합에서 누락됐습니다.")
        added_roots = self.protected_pre_fuzzy_roots - self.baseline_roots
        direct_added_roots = added_roots & self.direct_match_roots
        transitive_added_roots = added_roots - direct_added_roots
        baseline_documents = int(self.document_count["BASELINE_EXACT_IDENTITY"])
        direct_documents = int(self.document_count["FUZZY_DIRECT_INCREMENT"])
        transitive_documents = int(self.document_count["FUZZY_TRANSITIVE_ONLY_INCREMENT"])
        post_fuzzy_documents = baseline_documents + direct_documents + transitive_documents
        membership_count = len(self.protected_pre_fuzzy_roots)
        final_root_count = len(self.final_roots)
        merge_reduction = membership_count - final_root_count
        if (
            len(self.baseline_roots) + len(direct_added_roots) + len(transitive_added_roots)
            != membership_count
            or merge_reduction < 0
        ):
            raise RuntimeError("fuzzy 보호 component 보존 법칙이 깨졌습니다.")
        baseline_sources = _ordered_source_counts(
            self.source_document_count["BASELINE_EXACT_IDENTITY"]
        )
        direct_sources = _ordered_source_counts(
            self.source_document_count["FUZZY_DIRECT_INCREMENT"]
        )
        transitive_sources = _ordered_source_counts(
            self.source_document_count["FUZZY_TRANSITIVE_ONLY_INCREMENT"]
        )
        final_sources = {
            source: baseline_sources[source] + direct_sources[source] + transitive_sources[source]
            for source in ("NEWS", "DISCLOSURE")
        }
        if sum(final_sources.values()) != post_fuzzy_documents:
            raise RuntimeError("fuzzy 보호 source 보존 법칙이 깨졌습니다.")
        return {
            "pre_fuzzy_exact_identity_protected_component_count": len(self.baseline_roots),
            "pre_fuzzy_exact_identity_protected_document_count": baseline_documents,
            "pre_fuzzy_exact_identity_protected_source_document_count": baseline_sources,
            "fuzzy_direct_increment_pre_fuzzy_component_count": len(direct_added_roots),
            "fuzzy_direct_increment_document_count": direct_documents,
            "fuzzy_direct_increment_source_document_count": direct_sources,
            "fuzzy_transitive_only_increment_pre_fuzzy_component_count": len(
                transitive_added_roots
            ),
            "fuzzy_transitive_only_increment_document_count": transitive_documents,
            "fuzzy_transitive_only_increment_source_document_count": transitive_sources,
            "fuzzy_total_increment_pre_fuzzy_component_count": len(added_roots),
            "fuzzy_total_increment_document_count": direct_documents + transitive_documents,
            "post_fuzzy_protected_pre_fuzzy_component_membership_count": membership_count,
            "post_fuzzy_protected_component_count": final_root_count,
            "post_fuzzy_protected_component_merge_reduction": merge_reduction,
            "post_fuzzy_protected_document_count": post_fuzzy_documents,
            "post_fuzzy_protected_source_document_count": final_sources,
            "protection_increment_categories_disjoint": True,
            "protection_increment_document_conservation_verified": True,
            "protection_increment_component_conservation_verified": True,
        }


@dataclass(frozen=True, slots=True)
class PackedRow:
    split: str
    source_type: str
    pack_id: int
    valid_length: int
    input_ids: tuple[int, ...]
    segment_lengths: tuple[int, ...]
    structural_mask: tuple[bool, ...]

    @property
    def identity(self) -> bytes:
        return pack_identity(self.split, self.source_type, self.pack_id)


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _stable_file_measurements(path: Path) -> tuple[int, str]:
    digest = sha256()
    with path.open("rb") as file:
        before = os.fstat(file.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError(f"입력이 일반 파일이 아닙니다: {path}")
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
        after = os.fstat(file.fileno())
    current = path.stat()
    if _stat_identity(before) != _stat_identity(after) or _stat_identity(after) != _stat_identity(
        current
    ):
        raise RuntimeError(f"파일 hash 계산 중 입력이 변경되었습니다: {path}")
    return int(after.st_size), digest.hexdigest()


def _stable_file_payload(path: Path) -> bytes:
    if path.is_symlink():
        raise RuntimeError(f"입력이 symlink입니다: {path}")
    with path.open("rb") as file:
        before = os.fstat(file.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError(f"입력이 일반 파일이 아닙니다: {path}")
        payload = file.read()
        after = os.fstat(file.fileno())
    current = path.stat()
    if (
        path.is_symlink()
        or _stat_identity(before) != _stat_identity(after)
        or _stat_identity(after) != _stat_identity(current)
        or len(payload) != after.st_size
    ):
        raise RuntimeError(f"입력을 읽는 중 파일이 변경되었습니다: {path}")
    return payload


def sha256_file(path: Path) -> str:
    return _stable_file_measurements(path)[1]


def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return sha256(payload).hexdigest()


def artifact_record(path: Path, *, allow_symlink: bool = False) -> dict[str, int | str]:
    if (path.is_symlink() and not allow_symlink) or not path.is_file():
        raise RuntimeError(f"입력이 일반 파일이 아닙니다: {path}")
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise RuntimeError(f"입력 파일을 확인할 수 없습니다: {path}")
    try:
        display = str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        display = str(path.resolve())
    size, digest = _stable_file_measurements(resolved)
    return {"path": display, "bytes": size, "sha256": digest}


def verify_exact_file(path: Path, expected_hash: str, label: str) -> dict[str, int | str]:
    record = artifact_record(path)
    if record["sha256"] != expected_hash:
        raise RuntimeError(f"{label} SHA-256이 고정 계약과 다릅니다.")
    return record


def resolve_base_files() -> dict[str, Path]:
    resolved: dict[str, Path] = {}
    for filename, expected_hash in BASE_FILE_HASHES.items():
        cached = Path(
            hf_hub_download(
                repo_id=BASE_MODEL,
                filename=filename,
                revision=BASE_REVISION,
                local_files_only=True,
            )
        )
        target = cached.resolve(strict=True)
        if not target.is_file() or sha256_file(target) != expected_hash:
            raise RuntimeError(f"base {filename} SHA-256이 고정 계약과 다릅니다.")
        resolved[filename] = target
    return resolved


def verify_source_inputs() -> tuple[dict[str, dict[str, int | str]], dict[str, Path]]:
    records = {
        "documents": verify_exact_file(DOCUMENTS_PATH, DOCUMENTS_SHA256, "documents.parquet"),
        "dataset_manifest": verify_exact_file(
            DATASET_MANIFEST_PATH,
            DATASET_MANIFEST_SHA256,
            "K-FNSPID manifest",
        ),
    }
    for path, expected_hash in PROTECTED_FILE_HASHES.items():
        records[f"protected_{path.stem}"] = verify_exact_file(
            path,
            expected_hash,
            path.name,
        )
    base_files = resolve_base_files()
    for filename, path in sorted(base_files.items()):
        record = artifact_record(path, allow_symlink=True)
        record["path"] = f"hf://{BASE_MODEL}@{BASE_REVISION}/{filename}"
        records[f"base_{filename}"] = record
    return records, base_files


def normalize_identity(value: object) -> str:
    return unicodedata.normalize("NFKC", str(value or "")).strip().casefold()


def identity_from_values(
    document_id: object,
    source_url: object,
    content_hash: object,
    event_cluster_id: object,
) -> Identity:
    return Identity(
        document_id=normalize_identity(document_id),
        canonical_url=canonical_sentiment_url(str(source_url or "")),
        content_hash=normalize_identity(content_hash),
        event_cluster_id=normalize_identity(event_cluster_id),
    )


def identity_from_mapping(row: Mapping[str, Any]) -> Identity:
    return identity_from_values(
        row.get("document_id"),
        row.get("canonical_url") or row.get("source_url"),
        row.get("content_hash"),
        row.get("event_cluster_id"),
    )


def normalize_exact_text(value: object) -> str:
    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(normalized.split())


def _normalized_exact_text_hash_with_status(row: Mapping[str, Any]) -> tuple[str, str]:
    fields = (
        normalize_exact_text(row.get("title")),
        normalize_exact_text(row.get("snippet")),
        normalize_exact_text(row.get("full_text")),
    )
    if not any(fields):
        fallback = normalize_exact_text(row.get("text"))
        if not fallback:
            return "", "rejected_empty"
        fields = (fallback, "", "")
    alphanumeric_fields = tuple(
        "".join(character for character in field if character.isalnum()) for field in fields
    )
    combined = "".join(alphanumeric_fields)
    if len(combined) < EXACT_TEXT_MIN_ALNUM:
        return "", "rejected_low_alphanumeric_count"
    if len(set(combined)) < EXACT_TEXT_MIN_DISTINCT_ALNUM:
        return "", "rejected_low_character_diversity"
    title, snippet, full_text = alphanumeric_fields
    if len(full_text) >= EXACT_TEXT_MIN_FULL_TEXT_ALNUM:
        status = "accepted_full_text"
    elif not title or not snippet:
        return "", "rejected_missing_title_or_snippet"
    elif (snippet in title or title in snippet) and abs(len(title) - len(snippet)) <= (
        EXACT_TEXT_REDUNDANT_FIELD_MAX_DELTA
    ):
        return "", "rejected_redundant_title_snippet"
    else:
        status = "accepted_nonredundant_title_snippet"
    payload = json.dumps(fields, ensure_ascii=False, separators=(",", ":")).encode()
    return sha256(NORMALIZED_TEXT_SALT + payload).hexdigest(), status


def normalized_exact_text_hash(row: Mapping[str, Any]) -> str:
    return _normalized_exact_text_hash_with_status(row)[0]


def _fuzzy_audit_text(row: Mapping[str, Any], text_gate_status: str) -> str:
    if not text_gate_status.startswith("accepted_"):
        return ""
    title = normalize_exact_text(row.get("title"))
    snippet = normalize_exact_text(row.get("snippet"))
    text = " ".join(value for value in (title, snippet) if value)
    if len(text) < FUZZY_MIN_TEXT_CHARS:
        return ""
    if len(text) <= FUZZY_TEXT_MAX_CHARS:
        return text
    head = (FUZZY_TEXT_MAX_CHARS - 1) // 2
    tail = FUZZY_TEXT_MAX_CHARS - 1 - head
    return f"{text[:head]} {text[-tail:]}"


def _fuzzy_shingles(text: str) -> frozenset[str]:
    if len(text) < FUZZY_SHINGLE_WIDTH:
        return frozenset()
    return frozenset(
        text[index : index + FUZZY_SHINGLE_WIDTH]
        for index in range(len(text) - FUZZY_SHINGLE_WIDTH + 1)
    )


def rank_fuzzy_shingles(frequencies: Counter[str]) -> dict[str, int]:
    if not frequencies:
        raise RuntimeError("fuzzy shingle vocabulary가 비어 있습니다.")
    ordered = sorted(
        frequencies,
        key=lambda token: (frequencies[token], token.encode("utf-8")),
    )
    for rank, token in enumerate(ordered):
        frequencies[token] = rank
    return frequencies


def fuzzy_prefix_length(token_count: int) -> int:
    if token_count < FUZZY_MIN_SHINGLE_COUNT:
        raise ValueError("fuzzy token 수가 minimum보다 작습니다.")
    required = (
        FUZZY_JACCARD_NUMERATOR * token_count + FUZZY_JACCARD_DENOMINATOR - 1
    ) // FUZZY_JACCARD_DENOMINATOR
    return token_count - required + 1


def fuzzy_length_compatible(
    left_token_count: int,
    right_token_count: int,
) -> bool:
    if min(left_token_count, right_token_count) < FUZZY_MIN_SHINGLE_COUNT:
        return False
    if (
        FUZZY_JACCARD_DENOMINATOR * right_token_count < FUZZY_JACCARD_NUMERATOR * left_token_count
        or FUZZY_JACCARD_NUMERATOR * right_token_count
        > FUZZY_JACCARD_DENOMINATOR * left_token_count
    ):
        return False
    return True


def sorted_intersection_count(left: Sequence[int], right: Sequence[int]) -> int:
    left_index = 0
    right_index = 0
    count = 0
    while left_index < len(left) and right_index < len(right):
        left_value = int(left[left_index])
        right_value = int(right[right_index])
        if left_value == right_value:
            count += 1
            left_index += 1
            right_index += 1
        elif left_value < right_value:
            left_index += 1
        else:
            right_index += 1
    return count


def fuzzy_signature_from_text(
    *,
    text: str,
    ranks: Mapping[str, int],
    row_index: int | None,
    source_type: str,
    digest: str,
    protected_seed: bool,
) -> FuzzyGraphSignature | None:
    shingles = _fuzzy_shingles(text)
    if len(text) < FUZZY_MIN_TEXT_CHARS or len(shingles) < FUZZY_MIN_SHINGLE_COUNT:
        return None
    try:
        token_ids = array("I", sorted(ranks[token] for token in shingles))
    except KeyError as exception:
        raise RuntimeError("fuzzy shingle rank가 누락되었습니다.") from exception
    return FuzzyGraphSignature(
        row_index=row_index,
        source_type=source_type,
        digest=digest,
        text_length=len(text),
        token_ids=token_ids,
        protected_seed=protected_seed,
    )


def connect_allpairs_fuzzy_graph(
    *,
    document_rows_factory: Any,
    protected_texts: Mapping[str, str],
    ranks: Mapping[str, int],
    fuzzy_scope_mask: Sequence[int],
    union_find: ComponentUnionFind,
) -> tuple[set[int], dict[str, Any]]:
    if len(fuzzy_scope_mask) != len(union_find.parents):
        raise RuntimeError("fuzzy scope mask와 component index 크기가 다릅니다.")
    index = FuzzyAllPairsIndex(maximum_candidates=FUZZY_MAX_CANDIDATES_PER_DOCUMENT)
    protected_signature_owners: dict[int, int] = {}
    for text, digest in sorted(protected_texts.items(), key=lambda item: item[1]):
        signature = fuzzy_signature_from_text(
            text=text,
            ranks=ranks,
            row_index=None,
            source_type="PROTECTED",
            digest=digest,
            protected_seed=True,
        )
        if signature is not None:
            index.add(signature, query=False)

    direct_protected_match_rows: set[int] = set()
    information_source_count: Counter[str] = Counter()
    matched_source_pairs: Counter[str] = Counter()
    matched_pair_count = 0
    corpus_union_edge_count = 0
    cross_source_edge_count = 0
    protected_seed_edge_count = 0
    total_signature_token_ids = 0
    top_matches: list[dict[str, Any]] = []
    scoped_source_count: Counter[str] = Counter()
    scoped_dual_cutoff_document_count = 0
    scoped_exact_protected_document_count = 0
    scoped_overlap_document_count = 0
    observed_row_count = 0
    for row_index, row in enumerate(document_rows_factory()):
        observed_row_count = row_index + 1
        if row_index >= len(fuzzy_scope_mask):
            raise RuntimeError("fuzzy graph 행 수가 scope mask를 초과했습니다.")
        scope_mask = int(fuzzy_scope_mask[row_index])
        if scope_mask not in {0, 1, 2, 3}:
            raise RuntimeError("fuzzy scope mask bit가 유효하지 않습니다.")
        if scope_mask == 0:
            continue
        source = str(row.get("source_type"))
        if source not in SOURCE_CODES:
            raise RuntimeError(f"fuzzy graph source_type이 잘못되었습니다: {source}")
        scoped_source_count[source] += 1
        if scope_mask & 1:
            scoped_dual_cutoff_document_count += 1
        if scope_mask & 2:
            scoped_exact_protected_document_count += 1
        if scope_mask == 3:
            scoped_overlap_document_count += 1
        _, text_gate_status = _component_values_with_text_status(row)
        text = _fuzzy_audit_text(row, text_gate_status)
        if not text:
            continue
        identity = identity_from_mapping(row)
        signature = fuzzy_signature_from_text(
            text=text,
            ranks=ranks,
            row_index=row_index,
            source_type=source,
            digest=sha256(FUZZY_AUDIT_SALT + identity.document_id.encode()).hexdigest(),
            protected_seed=False,
        )
        if signature is None:
            continue
        information_source_count[source] += 1
        total_signature_token_ids += len(signature.token_ids)
        matches = index.add(signature)
        current_signature_index = len(index.signatures) - 1
        for candidate_index, similarity_bps in matches:
            candidate = index.signatures[candidate_index]
            matched_pair_count += 1
            left_digest, right_digest = sorted((signature.digest, candidate.digest))
            top_matches.append(
                {
                    "left_document_digest": left_digest,
                    "right_document_digest": right_digest,
                    "similarity_bps": similarity_bps,
                    "protected_seed_edge": candidate.protected_seed,
                }
            )
            top_matches.sort(
                key=lambda item: (
                    -int(item["similarity_bps"]),
                    str(item["left_document_digest"]),
                    str(item["right_document_digest"]),
                )
            )
            del top_matches[20:]
            if candidate.protected_seed:
                direct_protected_match_rows.add(row_index)
                protected_seed_edge_count += 1
                owner = protected_signature_owners.setdefault(candidate_index, row_index)
                if owner != row_index:
                    union_find.union(row_index, owner)
                continue
            candidate_row_index = candidate.row_index
            if candidate_row_index is None:
                raise RuntimeError("corpus fuzzy signature에 row index가 없습니다.")
            source_pair = "/".join(sorted((source, candidate.source_type)))
            matched_source_pairs[source_pair] += 1
            if source != candidate.source_type:
                cross_source_edge_count += 1
            if union_find.find(row_index) != union_find.find(candidate_row_index):
                corpus_union_edge_count += 1
                union_find.union(row_index, candidate_row_index)
        if index.signatures[current_signature_index] is not signature:
            raise RuntimeError("fuzzy index append 순서가 손상되었습니다.")
    if observed_row_count != len(fuzzy_scope_mask):
        raise RuntimeError("fuzzy graph 행 수와 scope mask 크기가 다릅니다.")
    audit = {
        "policy_version": "allpairs-frequency-prefix-exact-dice-v3",
        "scope": (
            "dual-cutoff-documents-plus-exact-identity-protected-components-"
            "plus-protected-seeds-cross-source"
        ),
        "parquet_full_scan_count": 4,
        "scoped_corpus_document_count": sum(scoped_source_count.values()),
        "scoped_corpus_source_count": _ordered_source_counts(scoped_source_count),
        "scoped_dual_cutoff_document_count": scoped_dual_cutoff_document_count,
        "scoped_exact_identity_protected_document_count": (scoped_exact_protected_document_count),
        "scoped_dual_cutoff_and_protected_overlap_document_count": (scoped_overlap_document_count),
        "normalization": {
            "unicode": "NFKC",
            "casefold": True,
            "whitespace": "single-space",
            "fields": ["title", "snippet"],
            "head_tail_maximum_characters": FUZZY_TEXT_MAX_CHARS,
            "minimum_text_characters": FUZZY_MIN_TEXT_CHARS,
            "character_shingle_width": FUZZY_SHINGLE_WIDTH,
            "minimum_unique_shingles": FUZZY_MIN_SHINGLE_COUNT,
        },
        "candidate_generation": {
            "algorithm": "AllPairs/PPJoin global-frequency prefix filtering",
            "global_order": "ascending document-frequency then UTF-8 token bytes",
            "dice_similarity_bps": FUZZY_MIN_DICE_SIMILARITY_BPS,
            "equivalent_jaccard_fraction": [
                FUZZY_JACCARD_NUMERATOR,
                FUZZY_JACCARD_DENOMINATOR,
            ],
            "prefix_length": "n-ceil(23*n/27)+1",
            "length_filter": "23*n/27 <= m <= 27*n/23",
            "maximum_candidates_per_document_fail_closed": (FUZZY_MAX_CANDIDATES_PER_DOCUMENT),
            "candidate_truncation_allowed": False,
            "source_type_partitioned": False,
        },
        "verification": {
            "method": "exact sorted-shingle intersection and integer Dice",
            "acceptance_inequality": "20000*intersection >= 9200*(left_size+right_size)",
            "candidate_recall_contract": "complete for the fixed Dice threshold",
            "transitive_closure": "union-find over exact/identity/fuzzy edges",
        },
        "protected_unique_text_count": len(protected_texts),
        "information_bearing_document_count": sum(information_source_count.values()),
        "information_bearing_source_count": _ordered_source_counts(information_source_count),
        "signature_count_including_protected": len(index.signatures),
        "global_shingle_vocabulary_count": len(ranks),
        "total_corpus_signature_token_ids": total_signature_token_ids,
        "prefix_posting_count": index.prefix_posting_count,
        "candidate_document_count": index.candidate_document_count,
        "candidate_pair_count": index.candidate_pair_count,
        "length_filtered_pair_count": index.length_filtered_pair_count,
        "exact_verified_pair_count": index.exact_verified_pair_count,
        "maximum_observed_candidates_per_document": index.maximum_observed_candidates,
        "matched_pair_count": matched_pair_count,
        "matched_source_pair_count": dict(sorted(matched_source_pairs.items())),
        "cross_source_matched_pair_count": cross_source_edge_count,
        "corpus_union_edge_count": corpus_union_edge_count,
        "protected_seed_edge_count": protected_seed_edge_count,
        "direct_protected_match_document_count": len(direct_protected_match_rows),
        "transitive_protected_component_purge": True,
        "train_validation_fuzzy_cross_split_after_component_split": 0,
        "deterministic_storage_lower_bound_bytes": (
            4 * (total_signature_token_ids + index.prefix_posting_count)
        ),
        "top_20_verified_matches": top_matches,
    }
    return direct_protected_match_rows, audit


def _component_values_with_text_status(
    row: Mapping[str, Any],
) -> tuple[tuple[tuple[str, str], ...], str]:
    identity = identity_from_mapping(row)
    text_hash, status = _normalized_exact_text_hash_with_status(row)
    values = list(identity.values())
    if text_hash:
        values.append(("normalized_exact_text_hash", text_hash))
    return tuple(values), status


def component_values_from_mapping(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    return _component_values_with_text_status(row)[0]


def typed_component_key(name: str, value: str) -> bytes:
    if name not in COMPONENT_KEY_CODES or not value:
        raise ValueError("component key 이름 또는 값이 유효하지 않습니다.")
    code = COMPONENT_KEY_CODES[name]
    digest = sha256(COMPONENT_KEY_SALT + bytes((code,)) + b"\0" + value.encode("utf-8")).digest()
    return bytes((code,)) + digest


def component_keys_from_mapping(row: Mapping[str, Any]) -> tuple[bytes, ...]:
    return tuple(
        typed_component_key(name, value) for name, value in component_values_from_mapping(row)
    )


def assert_blind_reservation_row(path: Path, payload: Mapping[str, Any]) -> None:
    expected_partition = SEALED_RESERVATION_PARTITIONS.get(path)
    if expected_partition is None:
        return
    exposed = FORBIDDEN_SEALED_RESERVATION_FIELDS & payload.keys()
    if exposed or (
        payload.get("partition") != expected_partition
        or payload.get("review_status") != "NEEDS_BLIND_REVIEW"
        or payload.get("final_sentiment") != ""
        or payload.get("reviewer_id") != ""
        or payload.get("reviewed_at") != ""
        or payload.get("review_note") != ""
    ):
        raise RuntimeError("확증 reservation blind 계약이 열려 있습니다.")


def read_protected_seed_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for path, expected_hash in PROTECTED_FILE_HASHES.items():
        current: list[dict[str, Any]] = []
        payload_bytes = _stable_file_payload(path)
        if sha256(payload_bytes).hexdigest() != expected_hash:
            raise RuntimeError(f"보호 파일 SHA-256이 고정 계약과 다릅니다: {path}")
        for line_number, line in enumerate(payload_bytes.decode("utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise RuntimeError(f"보호 행이 JSON object가 아닙니다: {path}:{line_number}")
            assert_blind_reservation_row(path, payload)
            current.append(payload)
        counts[path.name] = len(current)
        rows.extend(current)
    if counts != {
        NEWS_DEVELOPMENT_PATH.name: 449,
        DISCLOSURE_DEVELOPMENT_PATH.name: 450,
        NEWS_RESERVATION_PATH.name: 600,
        DISCLOSURE_RESERVATION_PATH.name: 600,
    }:
        raise RuntimeError(f"보호 행 수가 고정 계약과 다릅니다: {counts}")
    return rows


class StableParquetSource:
    """하나의 file descriptor로 반복 순회하고 변경을 검출한다."""

    def __init__(self, path: Path) -> None:
        if path.is_symlink():
            raise RuntimeError(f"Parquet 입력이 symlink입니다: {path}")
        self.path = path
        self._file = path.open("rb")
        try:
            self._initial_stat = os.fstat(self._file.fileno())
            current = path.stat()
            if (
                not stat.S_ISREG(self._initial_stat.st_mode)
                or path.is_symlink()
                or _stat_identity(self._initial_stat) != _stat_identity(current)
            ):
                raise RuntimeError(f"Parquet 입력이 안정적인 일반 파일이 아닙니다: {path}")
            self.parquet = pq.ParquetFile(self._file)
        except BaseException:
            self._file.close()
            raise

    def __enter__(self) -> StableParquetSource:
        return self

    def __exit__(self, exception_type: object, *_: object) -> None:
        try:
            if exception_type is None:
                self.verify_unchanged()
        finally:
            self._file.close()

    def verify_unchanged(self) -> None:
        current_descriptor = os.fstat(self._file.fileno())
        current_path = self.path.stat()
        if (
            self.path.is_symlink()
            or _stat_identity(self._initial_stat) != _stat_identity(current_descriptor)
            or _stat_identity(current_descriptor) != _stat_identity(current_path)
        ):
            raise RuntimeError(f"Parquet 순회 중 입력이 변경되었습니다: {self.path}")

    def iter_rows(self, columns: Sequence[str]) -> Iterator[dict[str, Any]]:
        for batch in self.parquet.iter_batches(
            batch_size=65_536,
            columns=list(columns),
            use_threads=False,
        ):
            values = {name: batch.column(index).to_pylist() for index, name in enumerate(columns)}
            for row_index in range(batch.num_rows):
                yield {name: values[name][row_index] for name in columns}


def _iter_parquet_rows(path: Path, columns: Sequence[str]) -> Iterator[dict[str, Any]]:
    with StableParquetSource(path) as source:
        yield from source.iter_rows(columns)


def build_protected_component(
    document_rows_factory: Any,
    protected_rows: Sequence[Mapping[str, Any]],
) -> ProtectedComponent:
    keys: dict[str, set[str]] = {
        "document_id": set(),
        "canonical_url": set(),
        "content_hash": set(),
        "event_cluster_id": set(),
    }
    for row in protected_rows:
        for name, value in identity_from_mapping(row).values():
            keys[name].add(value)
    matched_document_ids: set[str] = set()
    iteration = 0
    while True:
        iteration += 1
        before = sum(len(values) for values in keys.values())
        for row in document_rows_factory():
            identity = identity_from_mapping(row)
            values = identity.values()
            if not any(value in keys[name] for name, value in values):
                continue
            if identity.document_id:
                matched_document_ids.add(identity.document_id)
            for name, value in values:
                keys[name].add(value)
        after = sum(len(values) for values in keys.values())
        if after == before:
            break
        if iteration >= 64:
            raise RuntimeError("보호 provenance 성분이 64회 내에 수렴하지 않았습니다.")
    digest = sha256()
    for name, value in sorted(
        ((name, value) for name, values in keys.items() for value in values),
        key=lambda item: (item[0].encode(), item[1].encode()),
    ):
        digest.update(name.encode())
        digest.update(b"\t")
        digest.update(value.encode())
        digest.update(b"\n")
    return ProtectedComponent(
        keys={name: frozenset(values) for name, values in keys.items()},
        document_ids=frozenset(matched_document_ids),
        iteration_count=iteration,
        key_set_sha256=digest.hexdigest(),
    )


def validate_temporal_fields(published_at_kst: object, effective_trade_date: object) -> None:
    published = str(published_at_kst or "")
    trade_date = str(effective_trade_date or "")
    if not PUBLISHED_PATTERN.fullmatch(published) or not TRADE_DATE_PATTERN.fullmatch(trade_date):
        raise RuntimeError("문서 시간 스키마가 엄격한 ISO 계약과 다릅니다.")
    try:
        parsed = datetime.fromisoformat(published)
        parsed_date = date.fromisoformat(trade_date)
    except ValueError as exception:
        raise RuntimeError("문서 시간 값이 유효하지 않습니다.") from exception
    offset = parsed.utcoffset()
    if offset is None or int(offset.total_seconds()) != 9 * 3600:
        raise RuntimeError("published_at_kst가 +09:00이 아닙니다.")
    if parsed_date.isoformat() != trade_date:
        raise RuntimeError("effective_trade_date가 정규화되지 않았습니다.")


def before_dual_cutoff(published_at_kst: str, effective_trade_date: str) -> bool:
    validate_temporal_fields(published_at_kst, effective_trade_date)
    return published_at_kst < CUTOFF_TIMESTAMP and effective_trade_date < CUTOFF_TRADE_DATE


def split_for(source_type: str, event_cluster_id: str) -> str:
    if source_type not in SOURCE_CODES or not event_cluster_id:
        raise RuntimeError("분할 group key가 유효하지 않습니다.")
    group_key = source_type.encode() + b"\0" + event_cluster_id.encode()
    value = int.from_bytes(sha256(SPLIT_SALT + group_key).digest()[:8], "big")
    return "VALIDATION" if value < (1 << 64) // 100 else "TRAIN"


def split_for_component(component_key: bytes) -> str:
    if len(component_key) != 33 or component_key[0] not in COMPONENT_KEY_CODES.values():
        raise RuntimeError("분할 component key가 유효하지 않습니다.")
    value = int.from_bytes(sha256(SPLIT_SALT + component_key).digest()[:8], "big")
    return "VALIDATION" if value < (1 << 64) // 100 else "TRAIN"


def _nearest_rank_percentile(sorted_sizes: Sequence[int], percentile: float) -> int:
    if not sorted_sizes or not 0.0 < percentile <= 1.0:
        raise ValueError("component percentile 입력이 유효하지 않습니다.")
    index = max(0, math.ceil(len(sorted_sizes) * percentile) - 1)
    return int(sorted_sizes[index])


def _component_size_distribution(sizes: Sequence[int]) -> dict[str, int]:
    ordered = sorted(int(size) for size in sizes if size > 0)
    if not ordered:
        return {
            "component_count": 0,
            "document_count": 0,
            "p50": 0,
            "p95": 0,
            "p99": 0,
            "max": 0,
        }
    return {
        "component_count": len(ordered),
        "document_count": sum(ordered),
        "p50": _nearest_rank_percentile(ordered, 0.50),
        "p95": _nearest_rank_percentile(ordered, 0.95),
        "p99": _nearest_rank_percentile(ordered, 0.99),
        "max": ordered[-1],
    }


def _ordered_gate_counts(values: Mapping[str, Counter[str]]) -> dict[str, dict[str, int]]:
    return {
        status: {
            source: int(values.get(source, Counter()).get(status, 0))
            for source in ("NEWS", "DISCLOSURE")
        }
        for status in EXACT_TEXT_GATE_STATUSES
    }


def compute_corpus_inventory(
    documents_path: Path = DOCUMENTS_PATH,
    *,
    enforce_expected: bool = True,
) -> CorpusInventory:
    if enforce_expected:
        require_locked_inventory_oracle()
    with StableParquetSource(documents_path) as documents:
        return _compute_corpus_inventory_from_source(
            documents,
            enforce_expected=enforce_expected,
        )


def _compute_corpus_inventory_from_source(
    documents: StableParquetSource,
    *,
    enforce_expected: bool,
) -> CorpusInventory:
    parquet = documents.parquet
    if parquet.metadata.num_rows != 1_247_685:
        raise RuntimeError("documents.parquet 행 수가 고정 계약과 다릅니다.")
    missing = set(TEXT_COLUMNS) - set(parquet.schema_arrow.names)
    if missing:
        raise RuntimeError(f"documents.parquet 스키마가 부족합니다: {sorted(missing)}")
    protected_rows = read_protected_seed_rows()
    protected_fuzzy_texts: dict[str, str] = {}
    for row in protected_rows:
        _, text_gate_status = _component_values_with_text_status(row)
        text = _fuzzy_audit_text(row, text_gate_status)
        if not text:
            continue
        shingles = _fuzzy_shingles(text)
        if len(shingles) < FUZZY_MIN_SHINGLE_COUNT:
            continue
        protected_fuzzy_texts[text] = sha256(
            FUZZY_AUDIT_SALT + b"protected\0" + text.encode()
        ).hexdigest()

    union_find = ComponentUnionFind()
    key_owner: dict[bytes, int] = {}
    duplicate_key_counts: dict[bytes, int] = {}
    text_gate_counts: dict[str, Counter[str]] = {
        "NEWS": Counter(),
        "DISCLOSURE": Counter(),
    }
    for row_index, row in enumerate(documents.iter_rows(COMPONENT_COLUMNS)):
        values, text_gate_status = _component_values_with_text_status(row)
        keys = tuple(typed_component_key(name, value) for name, value in values)
        identity = identity_from_mapping(row)
        if not all((identity.document_id, identity.content_hash, identity.event_cluster_id)):
            raise RuntimeError(f"필수 문서 identity가 비어 있습니다: row={row_index}")
        source = str(row.get("source_type"))
        if source not in SOURCE_CODES:
            raise RuntimeError(f"지원하지 않는 source_type입니다: {source}")
        text_gate_counts[source][text_gate_status] += 1
        if not keys:
            raise RuntimeError(f"문서 component key가 비어 있습니다: row={row_index}")
        current = union_find.add(min(keys))
        for key in keys:
            owner = key_owner.get(key)
            if owner is None:
                key_owner[key] = current
            else:
                duplicate_key_counts[key] = duplicate_key_counts.get(key, 1) + 1
                union_find.union(current, owner)
    if len(union_find.parents) != parquet.metadata.num_rows:
        raise RuntimeError("component index의 문서 수가 원천 행 수와 다릅니다.")

    protected_key_values: dict[str, set[str]] = {name: set() for name in COMPONENT_KEY_CODES}
    protected_owner_indices: set[int] = set()
    protected_gate_counts: dict[str, Counter[str]] = {
        "NEWS": Counter(),
        "DISCLOSURE": Counter(),
    }
    for row in protected_rows:
        values, text_gate_status = _component_values_with_text_status(row)
        source = str(row.get("source_type"))
        if source not in SOURCE_CODES:
            raise RuntimeError(f"보호 행 source_type이 잘못되었습니다: {source}")
        protected_gate_counts[source][text_gate_status] += 1
        for name, value in values:
            protected_key_values[name].add(value)
            owner = key_owner.get(typed_component_key(name, value))
            if owner is not None:
                protected_owner_indices.add(owner)
    if not protected_owner_indices:
        raise RuntimeError("보호 provenance component를 documents에서 찾지 못했습니다.")
    pre_fuzzy_exact_or_identity_protected_roots = {
        union_find.find(owner) for owner in protected_owner_indices
    }

    fuzzy_scope_mask = bytearray(parquet.metadata.num_rows)
    pre_fuzzy_roots = array("I", [0]) * parquet.metadata.num_rows
    fuzzy_shingle_frequencies: Counter[str] = Counter()
    for text in protected_fuzzy_texts:
        fuzzy_shingle_frequencies.update(_fuzzy_shingles(text))
    for row_index, row in enumerate(documents.iter_rows(INVENTORY_COLUMNS)):
        published = str(row["published_at_kst"])
        trade_date = str(row["effective_trade_date"])
        inside_dual_cutoff = before_dual_cutoff(published, trade_date)
        pre_fuzzy_root = union_find.find(row_index)
        pre_fuzzy_roots[row_index] = pre_fuzzy_root
        exact_or_identity_protected = pre_fuzzy_root in pre_fuzzy_exact_or_identity_protected_roots
        scope_mask = int(inside_dual_cutoff) | (int(exact_or_identity_protected) << 1)
        fuzzy_scope_mask[row_index] = scope_mask
        if not scope_mask:
            continue
        _, text_gate_status = _component_values_with_text_status(row)
        fuzzy_text = _fuzzy_audit_text(row, text_gate_status)
        if fuzzy_text:
            shingles = _fuzzy_shingles(fuzzy_text)
            if len(shingles) >= FUZZY_MIN_SHINGLE_COUNT:
                fuzzy_shingle_frequencies.update(shingles)
    fuzzy_ranks = rank_fuzzy_shingles(fuzzy_shingle_frequencies)
    direct_fuzzy_protected_rows, fuzzy_near_duplicate_audit = connect_allpairs_fuzzy_graph(
        document_rows_factory=lambda: documents.iter_rows(INVENTORY_COLUMNS),
        protected_texts=protected_fuzzy_texts,
        ranks=fuzzy_ranks,
        fuzzy_scope_mask=fuzzy_scope_mask,
        union_find=union_find,
    )
    del fuzzy_ranks
    del fuzzy_shingle_frequencies
    del fuzzy_scope_mask

    direct_match_pre_fuzzy_roots = {
        int(pre_fuzzy_roots[row_index]) for row_index in direct_fuzzy_protected_rows
    }
    exact_or_identity_protected_roots = {
        union_find.find(owner) for owner in protected_owner_indices
    }
    direct_fuzzy_protected_roots = {
        union_find.find(row_index) for row_index in direct_fuzzy_protected_rows
    }
    protected_roots = exact_or_identity_protected_roots | direct_fuzzy_protected_roots
    protection_increment_audit = ProtectionIncrementAudit(
        pre_fuzzy_exact_identity_protected_roots=(pre_fuzzy_exact_or_identity_protected_roots),
        direct_match_pre_fuzzy_roots=direct_match_pre_fuzzy_roots,
        post_fuzzy_protected_roots=protected_roots,
    )

    source_count: Counter[str] = Counter()
    raw_cutoff_count: Counter[str] = Counter()
    purged_count: Counter[str] = Counter()
    eligible_count: Counter[str] = Counter()
    split_count: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    eligible_rows: list[tuple[str, str]] = []
    assignments = bytearray(parquet.metadata.num_rows)
    eligible_root_seen = bytearray(parquet.metadata.num_rows)
    root_document_counts = array("I", [0]) * parquet.metadata.num_rows
    root_news_counts = array("I", [0]) * parquet.metadata.num_rows
    root_disclosure_counts = array("I", [0]) * parquet.metadata.num_rows
    eligible_root_counts = array("I", [0]) * parquet.metadata.num_rows
    eligible_news_counts = array("I", [0]) * parquet.metadata.num_rows
    eligible_disclosure_counts = array("I", [0]) * parquet.metadata.num_rows
    component_count = 0
    duplicate_key_masks: dict[bytes, int] = {}
    protected_document_ids: set[str] = set()
    root_triggers: dict[int, tuple[int, bytes]] = {}
    for key, count in duplicate_key_counts.items():
        root = union_find.find(key_owner[key])
        current_trigger = root_triggers.get(root)
        if (
            current_trigger is None
            or count > current_trigger[0]
            or (count == current_trigger[0] and key < current_trigger[1])
        ):
            root_triggers[root] = (count, key)
    del key_owner
    for row_index, row in enumerate(documents.iter_rows(INVENTORY_COLUMNS)):
        source = str(row["source_type"])
        if source not in SOURCE_CODES:
            raise RuntimeError(f"지원하지 않는 source_type입니다: {source}")
        source_count[source] += 1
        identity = identity_from_mapping(row)
        root = union_find.find(row_index)
        protection_increment_audit.observe(
            pre_fuzzy_root=int(pre_fuzzy_roots[row_index]),
            post_fuzzy_root=root,
            source_type=source,
        )
        root_document_counts[root] += 1
        if source == "NEWS":
            root_news_counts[root] += 1
        else:
            root_disclosure_counts[root] += 1
        values, _ = _component_values_with_text_status(row)
        keys = tuple(typed_component_key(name, value) for name, value in values)
        if root in protected_roots:
            protected_document_ids.add(identity.document_id)
            for name, value in values:
                protected_key_values[name].add(value)
        published = str(row["published_at_kst"])
        trade_date = str(row["effective_trade_date"])
        if not before_dual_cutoff(published, trade_date):
            continue
        raw_cutoff_count[source] += 1
        if root in protected_roots:
            purged_count[source] += 1
            continue
        split = split_for_component(union_find.minimum_key(root))
        assignments[row_index] = 1 if split == "TRAIN" else 2
        if not eligible_root_seen[root]:
            eligible_root_seen[root] = 1
            component_count += 1
        eligible_root_counts[root] += 1
        if source == "NEWS":
            eligible_news_counts[root] += 1
        else:
            eligible_disclosure_counts[root] += 1
        split_mask = assignments[row_index]
        for key in keys:
            if key in duplicate_key_counts:
                duplicate_key_masks[key] = duplicate_key_masks.get(key, 0) | split_mask
        eligible_count[source] += 1
        split_count[split][source] += 1
        eligible_rows.append((identity.document_id, split))
    cross_split_keys = [key for key, mask in duplicate_key_masks.items() if mask == 3]
    if cross_split_keys:
        by_type = Counter(key[0] for key in cross_split_keys)
        raise RuntimeError(f"component key가 TRAIN/VALIDATION에 교차 배치되었습니다: {by_type}")
    duplicate_key_audit: dict[str, dict[str, int]] = {}
    for name, code in COMPONENT_KEY_CODES.items():
        masks = [mask for key, mask in duplicate_key_masks.items() if key[0] == code]
        duplicate_key_audit[name] = {
            "eligible_duplicate_key_count": len(masks),
            "train_only": sum(mask == 1 for mask in masks),
            "validation_only": sum(mask == 2 for mask in masks),
            "cross_split": sum(mask == 3 for mask in masks),
        }

    key_type_by_code = {code: name for name, code in COMPONENT_KEY_CODES.items()}

    def component_entry(root: int, *, eligible: bool) -> dict[str, Any]:
        trigger_count, trigger_key = root_triggers.get(
            root,
            (1, union_find.minimum_key(root)),
        )
        if eligible:
            news_count = int(eligible_news_counts[root])
            disclosure_count = int(eligible_disclosure_counts[root])
        else:
            news_count = int(root_news_counts[root])
            disclosure_count = int(root_disclosure_counts[root])
        return {
            "component_key_digest": union_find.minimum_key(root).hex(),
            "document_count": news_count + disclosure_count,
            "source_document_count": {
                "NEWS": news_count,
                "DISCLOSURE": disclosure_count,
            },
            "trigger_key_type": key_type_by_code[trigger_key[0]],
            "trigger_key_digest": trigger_key.hex(),
            "trigger_document_frequency": trigger_count,
            "protected": root in protected_roots,
        }

    all_roots = [
        index
        for index, size in enumerate(root_document_counts)
        if size and union_find.find(index) == index
    ]
    eligible_roots = [index for index, size in enumerate(eligible_root_counts) if size]
    protected_root_list = sorted(protected_roots, key=union_find.minimum_key)

    def top_entries(roots: Sequence[int], *, eligible: bool) -> list[dict[str, Any]]:
        counts = eligible_root_counts if eligible else root_document_counts
        ordered = sorted(roots, key=lambda root: (-int(counts[root]), union_find.minimum_key(root)))
        return [component_entry(root, eligible=eligible) for root in ordered[:20]]

    component_size_audit = {
        "percentile_method": "nearest-rank",
        "all_document_components": _component_size_distribution(
            [root_document_counts[root] for root in all_roots]
        ),
        "eligible_components": _component_size_distribution(
            [eligible_root_counts[root] for root in eligible_roots]
        ),
        "protected_components": _component_size_distribution(
            [root_document_counts[root] for root in protected_root_list]
        ),
        "top_20_all_document_components": top_entries(all_roots, eligible=False),
        "top_20_eligible_components": top_entries(eligible_roots, eligible=True),
        "top_20_protected_components": top_entries(protected_root_list, eligible=False),
    }
    exact_text_gate_audit = {
        "policy_version": "normalized-exact-text-information-gate-v1",
        "minimum_alphanumeric_characters": EXACT_TEXT_MIN_ALNUM,
        "minimum_distinct_alphanumeric_characters": EXACT_TEXT_MIN_DISTINCT_ALNUM,
        "full_text_override_minimum_alphanumeric_characters": EXACT_TEXT_MIN_FULL_TEXT_ALNUM,
        "redundant_title_snippet_maximum_length_delta": (EXACT_TEXT_REDUNDANT_FIELD_MAX_DELTA),
        "corpus_status_count": _ordered_gate_counts(text_gate_counts),
        "protected_status_count": _ordered_gate_counts(protected_gate_counts),
    }
    protection_increment_record = protection_increment_audit.finalize()
    protected_document_count_after_fuzzy = sum(
        root_document_counts[root] for root in protected_roots
    )
    if (
        protection_increment_record["post_fuzzy_protected_document_count"]
        != protected_document_count_after_fuzzy
        or len(protected_document_ids) != protected_document_count_after_fuzzy
    ):
        raise RuntimeError("fuzzy 보호 증분과 최종 보호 문서 수가 다릅니다.")
    fuzzy_near_duplicate_audit = {
        **fuzzy_near_duplicate_audit,
        **protection_increment_record,
        "remaining_eligible_protected_fuzzy_match_document_count": 0,
        "interpretation": (
            "fixed-threshold candidate-complete AllPairs graph; exact/identity/fuzzy edges are "
            "unioned before protected purge and component split"
        ),
    }
    eligible_rows.sort(key=lambda item: item[0].encode())
    if any(
        left[0] == right[0] for left, right in zip(eligible_rows, eligible_rows[1:], strict=False)
    ):
        raise RuntimeError("학습 후보 document_id가 중복됩니다.")
    eligible_digest = sha256()
    split_digest = sha256()
    for document_id, split in eligible_rows:
        eligible_digest.update(document_id.encode())
        eligible_digest.update(b"\n")
        split_digest.update(
            (
                json.dumps(
                    {"document_id": document_id, "split": split},
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            ).encode()
        )
    protected_digest = sha256()
    for name, value in sorted(
        ((name, value) for name, values in protected_key_values.items() for value in values),
        key=lambda item: (item[0].encode(), item[1].encode()),
    ):
        protected_digest.update(name.encode())
        protected_digest.update(b"\t")
        protected_digest.update(value.encode())
        protected_digest.update(b"\n")
    component = ProtectedComponent(
        keys={name: frozenset(values) for name, values in protected_key_values.items()},
        document_ids=frozenset(protected_document_ids),
        iteration_count=1,
        key_set_sha256=protected_digest.hexdigest(),
    )
    assignment_bytes = bytes(assignments)
    inventory = CorpusInventory(
        protected=component,
        source_document_count=_ordered_source_counts(source_count),
        raw_cutoff_count=_ordered_source_counts(raw_cutoff_count),
        purged_cutoff_count=_ordered_source_counts(purged_count),
        eligible_count=_ordered_source_counts(eligible_count),
        split_count={
            split: _ordered_source_counts(split_count[split]) for split in ("TRAIN", "VALIDATION")
        },
        eligible_ids_sha256=eligible_digest.hexdigest(),
        split_sha256=split_digest.hexdigest(),
        row_assignments=assignment_bytes,
        row_assignments_sha256=sha256(assignment_bytes).hexdigest(),
        component_count=component_count,
        duplicate_key_audit=duplicate_key_audit,
        exact_text_gate_audit=exact_text_gate_audit,
        component_size_audit=component_size_audit,
        fuzzy_near_duplicate_audit=fuzzy_near_duplicate_audit,
    )
    if enforce_expected:
        assert_inventory_contract(inventory)
    return inventory


def _ordered_source_counts(values: Mapping[str, int]) -> dict[str, int]:
    return {source: int(values.get(source, 0)) for source in ("NEWS", "DISCLOSURE")}


def inventory_oracle_candidate(
    inventory: CorpusInventory,
) -> tuple[dict[str, Any], dict[str, str]]:
    counts = {
        "source_document_count": inventory.source_document_count,
        "raw_cutoff_count": inventory.raw_cutoff_count,
        "protected_component_document_count": len(inventory.protected.document_ids),
        "protected_key_count": {
            name: len(inventory.protected.keys[name]) for name in COMPONENT_KEY_CODES
        },
        "purged_cutoff_count": inventory.purged_cutoff_count,
        "eligible_count": inventory.eligible_count,
        "split_count": inventory.split_count,
        "eligible_component_count": inventory.component_count,
        "duplicate_key_audit": inventory.duplicate_key_audit,
    }
    hashes = {
        "protected_key_set": inventory.protected.key_set_sha256,
        "eligible_ordered_document_ids": inventory.eligible_ids_sha256,
        "split_jsonl": inventory.split_sha256,
        "row_assignments": inventory.row_assignments_sha256,
        "exact_text_gate_audit": canonical_json_sha256(inventory.exact_text_gate_audit),
        "component_size_audit": canonical_json_sha256(inventory.component_size_audit),
        "fuzzy_near_duplicate_audit": canonical_json_sha256(inventory.fuzzy_near_duplicate_audit),
        "allowed_random_token_ids": ALLOWED_RANDOM_VOCAB_SHA256,
    }
    if set(counts) != set(EXPECTED) or set(hashes) != set(EXPECTED_HASHES):
        raise RuntimeError("inventory oracle candidate 필드 계약이 다릅니다.")
    return counts, hashes


def assert_inventory_contract(inventory: CorpusInventory) -> None:
    require_locked_inventory_oracle()
    actual, hashes = inventory_oracle_candidate(inventory)
    if actual != EXPECTED:
        raise RuntimeError(f"DAPT corpus count 계약이 불일치합니다: {actual}")
    if hashes != EXPECTED_HASHES:
        raise RuntimeError(f"DAPT corpus canonical hash 계약이 불일치합니다: {hashes}")


def verify_tokenizer_contract(tokenizer: Any) -> tuple[int, ...]:
    exact_tokens = {
        "뉴스": 878,
        "공시": 1292,
        "제목": 3348,
        "요약": 7633,
        "본문": 12050,
    }
    if tokenizer.vocab_size != VOCAB_SIZE or set(tokenizer.all_special_ids) != SPECIAL_IDS:
        raise RuntimeError("tokenizer vocab/special ID 계약이 다릅니다.")
    for token, token_id in exact_tokens.items():
        encoded = tokenizer(token, add_special_tokens=False)["input_ids"]
        if encoded != [token_id] or tokenizer.convert_tokens_to_ids(token) != token_id:
            raise RuntimeError(f"DAPT marker가 단일 token이 아닙니다: {token}")
    allowed = tuple(
        token_id
        for token_id in range(VOCAB_SIZE)
        if token_id not in SPECIAL_IDS
        and not UNUSED_TOKEN_PATTERN.fullmatch(str(tokenizer.convert_ids_to_tokens(token_id)))
    )
    digest = sha256()
    for token_id in allowed:
        digest.update(struct.pack(">I", token_id))
    if (
        len(allowed) != 129_429
        or allowed[:5] != (5, 6, 7, 8, 9)
        or allowed[-5:] != (129_429, 129_430, 129_431, 129_432, 129_433)
        or digest.hexdigest() != EXPECTED_HASHES["allowed_random_token_ids"]
    ):
        raise RuntimeError("MLM random replacement vocabulary 계약이 다릅니다.")
    return allowed


def crop_head_tail(tokens: Sequence[int], count: int) -> list[int]:
    if count < 0:
        raise ValueError("crop token 수는 음수일 수 없습니다.")
    if count >= len(tokens):
        return list(tokens)
    head_count = (count + 1) // 2
    tail_count = count // 2
    return (
        [*tokens[:head_count], *tokens[-tail_count:]] if tail_count else list(tokens[:head_count])
    )


def format_document_segment(
    tokenizer: Any,
    *,
    source_type: str,
    title: object,
    snippet: object,
    full_text: object,
) -> tuple[list[int], list[int], dict[str, int | bool]]:
    if source_type not in SOURCE_MARKERS:
        raise RuntimeError(f"지원하지 않는 source_type입니다: {source_type}")
    title_text = str(title or "").strip()
    snippet_text = str(snippet or "").strip()
    full_text_value = str(full_text or "").strip()
    title_tokens = list(tokenizer(title_text, add_special_tokens=False)["input_ids"])
    snippet_tokens = list(tokenizer(snippet_text, add_special_tokens=False)["input_ids"])
    full_tokens = list(tokenizer(full_text_value, add_special_tokens=False)["input_ids"])
    return format_tokenized_segment(
        source_type=source_type,
        title_tokens=title_tokens,
        snippet_tokens=snippet_tokens,
        full_tokens=full_tokens,
        has_full_text=bool(full_text_value),
    )


def format_tokenized_segment(
    *,
    source_type: str,
    title_tokens: Sequence[int],
    snippet_tokens: Sequence[int],
    full_tokens: Sequence[int],
    has_full_text: bool,
) -> tuple[list[int], list[int], dict[str, int | bool]]:
    if source_type not in SOURCE_MARKERS:
        raise RuntimeError(f"지원하지 않는 source_type입니다: {source_type}")
    title_used = list(title_tokens[:64])
    if not has_full_text:
        snippet_used = list(snippet_tokens[: 251 - len(title_used)])
        full_used: list[int] = []
        segment = [
            SOURCE_MARKERS[source_type],
            FIELD_MARKERS["TITLE"],
            *title_used,
            FIELD_MARKERS["SUMMARY"],
            *snippet_used,
            SEP_ID,
        ]
        structural_positions = [0, 1, 2 + len(title_used)]
    else:
        full_reserve = min(len(full_tokens), 128)
        snippet_count = min(len(snippet_tokens), 250 - len(title_used) - full_reserve)
        snippet_used = list(snippet_tokens[:snippet_count])
        full_count = min(len(full_tokens), 250 - len(title_used) - len(snippet_used))
        full_used = crop_head_tail(full_tokens, full_count)
        segment = [
            SOURCE_MARKERS[source_type],
            FIELD_MARKERS["TITLE"],
            *title_used,
            FIELD_MARKERS["SUMMARY"],
            *snippet_used,
            FIELD_MARKERS["BODY"],
            *full_used,
            SEP_ID,
        ]
        structural_positions = [
            0,
            1,
            2 + len(title_used),
            3 + len(title_used) + len(snippet_used),
        ]
    if not 1 <= len(segment) <= PACK_CAPACITY or segment[-1] != SEP_ID:
        raise RuntimeError("DAPT document segment 길이 계약 위반입니다.")
    return (
        segment,
        structural_positions,
        {
            "has_full_text": has_full_text,
            "raw_title": len(title_tokens),
            "raw_snippet": len(snippet_tokens),
            "raw_full": len(full_tokens),
            "used_title": len(title_used),
            "used_snippet": len(snippet_used),
            "used_full": len(full_used),
        },
    )


def best_fit_decreasing(metadata: Sequence[SegmentMetadata]) -> list[list[int]]:
    ordered = sorted(
        metadata,
        key=lambda item: (-item.length, item.sort_digest, item.document_id.encode()),
    )
    bins: list[list[int]] = []
    residuals: list[int] = []
    available: list[list[int]] = [[] for _ in range(PACK_CAPACITY + 1)]
    import heapq

    for item in ordered:
        selected_remaining = next(
            (
                remaining
                for remaining in range(item.length, PACK_CAPACITY + 1)
                if available[remaining]
            ),
            None,
        )
        if selected_remaining is None:
            pack_id = len(bins)
            bins.append([item.row_index])
            remaining = PACK_CAPACITY - item.length
            residuals.append(remaining)
        else:
            pack_id = heapq.heappop(available[selected_remaining])
            if residuals[pack_id] != selected_remaining:
                raise RuntimeError("BFD residual heap이 손상되었습니다.")
            bins[pack_id].append(item.row_index)
            remaining = selected_remaining - item.length
            residuals[pack_id] = remaining
        if remaining:
            heapq.heappush(available[remaining], pack_id)
    return bins


def pack_identity(split: str, source_type: str, pack_id: int) -> bytes:
    if split not in SPLIT_CODES or source_type not in SOURCE_CODES or not 0 <= pack_id < 2**32:
        raise ValueError("pack identity가 허용 범위를 벗어났습니다.")
    return bytes((SPLIT_CODES[split], SOURCE_CODES[source_type])) + pack_id.to_bytes(4, "big")


def pack_header(row: PackedRow) -> bytes:
    return struct.pack(
        ">BBIH",
        SPLIT_CODES[row.split],
        SOURCE_CODES[row.source_type],
        row.pack_id,
        row.valid_length,
    )


def segment_sha256(tokens: Sequence[int]) -> str:
    digest = sha256()
    for token_id in tokens:
        digest.update(struct.pack(">I", token_id))
    return digest.hexdigest()


def mask_pack(
    row: PackedRow,
    allowed_ids: Sequence[int],
) -> tuple[tuple[int, ...], tuple[int, ...], dict[str, int]]:
    if (
        len(row.input_ids) != MAX_LENGTH
        or len(row.structural_mask) != MAX_LENGTH
        or row.input_ids[0] != CLS_ID
        or sum(row.segment_lengths) != row.valid_length - 1
    ):
        raise RuntimeError("mask 입력 pack 계약 위반입니다.")
    if not allowed_ids:
        raise RuntimeError("random replacement token 목록이 비어 있습니다.")
    identity = row.identity
    salt = TRAIN_MASK_SALT if row.split == "TRAIN" else VALIDATION_MASK_SALT
    masked = list(row.input_ids)
    labels = [-100] * MAX_LENGTH
    candidates: list[tuple[int, int, bytes]] = []
    selected: list[tuple[int, bytes]] = []
    threshold = (15 * (1 << 64)) // 100
    for position in range(row.valid_length):
        original = row.input_ids[position]
        if original in SPECIAL_IDS or row.structural_mask[position]:
            continue
        epoch = EPOCH_INDEX.to_bytes(4, "big") if row.split == "TRAIN" else b""
        digest = sha256(salt + identity + epoch + position.to_bytes(2, "big")).digest()
        value = int.from_bytes(digest[:8], "big")
        candidates.append((value, position, digest))
        if value < threshold:
            selected.append((position, digest))
    if not candidates:
        raise RuntimeError("MLM mask 후보 token이 없습니다.")
    if not selected:
        _, position, digest = min(candidates, key=lambda item: (item[0], item[1]))
        selected.append((position, digest))
    replacement_counts: Counter[str] = Counter()
    for position, digest in selected:
        original = row.input_ids[position]
        labels[position] = original
        replacement_value = int.from_bytes(digest[8:16], "big")
        if replacement_value < (8 * (1 << 64)) // 10:
            masked[position] = MASK_ID
            replacement_counts["MASK"] += 1
        elif replacement_value < (9 * (1 << 64)) // 10:
            random_index = int.from_bytes(digest[16:24], "big") % len(allowed_ids)
            masked[position] = int(allowed_ids[random_index])
            replacement_counts["RANDOM"] += 1
        else:
            replacement_counts["UNCHANGED"] += 1
    return (
        tuple(masked),
        tuple(labels),
        {
            "selected": len(selected),
            "mask": replacement_counts["MASK"],
            "random": replacement_counts["RANDOM"],
            "unchanged": replacement_counts["UNCHANGED"],
        },
    )


def update_pack_ids_hash(digest: Any, row: PackedRow) -> None:
    digest.update(pack_header(row))
    digest.update(struct.pack(">H", len(row.segment_lengths)))
    for length in row.segment_lengths:
        digest.update(struct.pack(">H", length))
    digest.update(bytes(row.structural_mask))
    for token_id in row.input_ids:
        digest.update(struct.pack(">I", token_id))


def update_mask_hash(
    digest: Any,
    row: PackedRow,
    masked_input_ids: Sequence[int],
    labels: Sequence[int],
) -> None:
    update_pack_ids_hash(digest, row)
    for token_id in masked_input_ids:
        digest.update(struct.pack(">I", token_id))
    for label in labels:
        digest.update(struct.pack(">i", label))


def epoch_order_key(row: PackedRow) -> tuple[bytes, bytes]:
    identity = row.identity
    digest = sha256(
        EPOCH_ORDER_SALT + SEED.to_bytes(8, "big") + EPOCH_INDEX.to_bytes(4, "big") + identity
    ).digest()
    return digest, identity


def pack_schema(*, masked: bool = False) -> pa.Schema:
    fields = [
        pa.field("source_type", pa.string(), nullable=False),
        pa.field("pack_id", pa.uint32(), nullable=False),
        pa.field("valid_length", pa.uint16(), nullable=False),
        pa.field("segment_lengths", pa.list_(pa.uint16()), nullable=False),
        pa.field("structural_mask", pa.list_(pa.bool_(), MAX_LENGTH), nullable=False),
        pa.field("input_ids", pa.list_(pa.uint32(), MAX_LENGTH), nullable=False),
    ]
    if masked:
        fields.append(pa.field("labels", pa.list_(pa.int32(), MAX_LENGTH), nullable=False))
    return pa.schema(fields)


def segment_schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("document_id", pa.string(), nullable=False),
            pa.field("length", pa.uint16(), nullable=False),
            pa.field("sort_digest", pa.binary(32), nullable=False),
            pa.field("token_ids", pa.list_(pa.uint32()), nullable=False),
            pa.field("structural_positions", pa.list_(pa.uint16()), nullable=False),
        ]
    )


def lineage_schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("document_id", pa.string(), nullable=False),
            pa.field("source_type", pa.string(), nullable=False),
            pa.field("split", pa.string(), nullable=False),
            pa.field("pack_id", pa.uint32(), nullable=False),
            pa.field("offset", pa.uint16(), nullable=False),
            pa.field("length", pa.uint16(), nullable=False),
            pa.field("segment_sha256", pa.string(), nullable=False),
        ]
    )


def _write_table_batch(
    writer: pq.ParquetWriter,
    rows: list[dict[str, Any]],
    schema: pa.Schema,
) -> None:
    if rows:
        writer.write_table(pa.Table.from_pylist(rows, schema=schema), row_group_size=len(rows))
        rows.clear()


def _require_absent_output(path: Path, label: str) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"{label} 출력이 이미 존재합니다: {path}")


def _safe_temporary_directory(target: Path) -> Path:
    _require_absent_output(target, "directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.parent / f".{target.name}.tmp-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    return temporary


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_tree(directory: Path) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError("fsync 대상 artifact directory가 유효하지 않습니다.")
    directories = [directory]
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"artifact에 symlink가 포함되었습니다: {path}")
        if path.is_file():
            descriptor = os.open(path, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        elif path.is_dir():
            directories.append(path)
    for path in reversed(directories):
        _fsync_directory(path)


def _atomic_rename_directory_new(source: Path, target: Path) -> None:
    if source.is_symlink() or not source.is_dir() or target.exists() or target.is_symlink():
        raise RuntimeError("atomic directory publish 사전조건이 충족되지 않았습니다.")
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    target_bytes = os.fsencode(target)
    result: int
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        rename_excl = 0x00000004
        result = int(libc.renamex_np(source_bytes, target_bytes, rename_excl))
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        at_fdcwd = -100
        rename_noreplace = 1
        result = int(
            libc.renameat2(
                at_fdcwd,
                source_bytes,
                at_fdcwd,
                target_bytes,
                rename_noreplace,
            )
        )
    else:
        raise RuntimeError("현재 플랫폼이 atomic no-clobber directory publish를 지원하지 않습니다.")
    if result != 0:
        error_number = ctypes.get_errno()
        if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
            raise RuntimeError(f"출력이 실행 중 생성되었습니다: {target}")
        raise OSError(error_number, os.strerror(error_number), str(target))
    _fsync_directory(target.parent)


def _atomic_write_new(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"출력이 이미 존재합니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.tmp-{uuid.uuid4().hex}"
    try:
        with temporary.open("xb") as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exception:
            raise RuntimeError(f"출력이 실행 중 생성되었습니다: {path}") from exception
        _fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def runtime_environment() -> dict[str, Any]:
    cuda_cudnn_version = (
        torch.backends.cudnn.version()  # type: ignore[no-untyped-call]
        if torch.cuda.is_available()
        else None
    )
    return {
        "python": sys.version,
        "python_executable": str(Path(sys.executable).resolve()),
        "platform": platform.platform(),
        "platform_release": platform.release(),
        "mac_version": platform.mac_ver()[0],
        "machine": platform.machine(),
        "torch": torch.__version__,
        "transformers": importlib.metadata.version("transformers"),
        "peft": importlib.metadata.version("peft"),
        "pyarrow": pa.__version__,
        "numpy": np.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn_runtime": cuda_cudnn_version,
        "cuda_device_count": torch.cuda.device_count(),
        "mps_available": torch.backends.mps.is_available(),
        "mps_built": torch.backends.mps.is_built(),
        "cuda_available": torch.cuda.is_available(),
        "mps_fallback_enabled": os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1",
        "deterministic_algorithms_enabled": torch.are_deterministic_algorithms_enabled(),
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
        "cuda_matmul_allow_tf32": bool(torch.backends.cuda.matmul.allow_tf32),
        "cudnn_allow_tf32": bool(torch.backends.cudnn.allow_tf32),
        "default_dtype": str(torch.get_default_dtype()),
    }


def oracle_software_fingerprint() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "unicode_database": unicodedata.unidata_version,
        "transformers": importlib.metadata.version("transformers"),
        "tokenizers": importlib.metadata.version("tokenizers"),
        "huggingface_hub": importlib.metadata.version("huggingface-hub"),
        "pyarrow": pa.__version__,
        "numpy": np.__version__,
    }


def dependency_records() -> dict[str, dict[str, int | str]]:
    return {
        "pyproject": artifact_record(PROJECT_ROOT / "pyproject.toml"),
        "uv_lock": artifact_record(PROJECT_ROOT / "uv.lock"),
        "trainer": artifact_record(Path(__file__).resolve()),
        "sentiment_protocol": artifact_record(
            PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py"
        ),
    }


def _normalize_oracle_recipe_source(source: bytes) -> bytes:
    normalized = source
    for begin, end in (
        (b"# PACK_ORACLE_LOCK_BEGIN", b"# PACK_ORACLE_LOCK_END"),
        (b"# INVENTORY_ORACLE_VALUES_BEGIN", b"# INVENTORY_ORACLE_VALUES_END"),
        (b"# PACK_ORACLE_VALUES_BEGIN", b"# PACK_ORACLE_VALUES_END"),
    ):
        pattern = re.compile(rb"(?ms)^(" + re.escape(begin) + rb")$.*?^(" + re.escape(end) + rb")$")
        normalized, replacement_count = pattern.subn(
            rb"\1\n<PACK_ORACLE_MUTABLE_BLOCK>\n\2",
            normalized,
        )
        if replacement_count != 1:
            raise RuntimeError("pack oracle mutable source block 계약이 다릅니다.")
    return normalized


def oracle_recipe_records() -> dict[str, dict[str, int | str]]:
    """oracle 값과 상태만 제외한 derivation recipe를 고정한다."""
    trainer_path = Path(__file__).resolve()
    normalized = _normalize_oracle_recipe_source(_stable_file_payload(trainer_path))
    trainer_record: dict[str, int | str] = {
        "path": str(trainer_path.relative_to(PROJECT_ROOT)),
        "bytes": len(normalized),
        "sha256": sha256(normalized).hexdigest(),
    }
    return {
        "pyproject": artifact_record(PROJECT_ROOT / "pyproject.toml"),
        "uv_lock": artifact_record(PROJECT_ROOT / "uv.lock"),
        "trainer_semantic_without_oracle_values": trainer_record,
        "sentiment_protocol": artifact_record(
            PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py"
        ),
    }


def inventory_record(inventory: CorpusInventory) -> dict[str, Any]:
    return {
        "source_document_count": inventory.source_document_count,
        "raw_dual_cutoff_count": inventory.raw_cutoff_count,
        "protected_component": {
            "document_count": len(inventory.protected.document_ids),
            "key_count": {name: len(values) for name, values in inventory.protected.keys.items()},
            "fixed_point_iterations": inventory.protected.iteration_count,
            "key_set_sha256": inventory.protected.key_set_sha256,
            "algorithm": "single-pass-union-find-v2",
            "computed_across_all_documents_regardless_of_cutoff": True,
        },
        "purged_inside_cutoff_count": inventory.purged_cutoff_count,
        "eligible_count": inventory.eligible_count,
        "eligible_total": inventory.eligible_total,
        "split_count": inventory.split_count,
        "eligible_ordered_document_ids_sha256": inventory.eligible_ids_sha256,
        "split_canonical_jsonl_sha256": inventory.split_sha256,
        "row_assignments_sha256": inventory.row_assignments_sha256,
        "eligible_component_count": inventory.component_count,
        "duplicate_key_zero_overlap_audit": inventory.duplicate_key_audit,
        "normalized_exact_text_information_gate": inventory.exact_text_gate_audit,
        "normalized_exact_text_information_gate_sha256": canonical_json_sha256(
            inventory.exact_text_gate_audit
        ),
        "component_size_audit": inventory.component_size_audit,
        "component_size_audit_sha256": canonical_json_sha256(inventory.component_size_audit),
        "fuzzy_near_duplicate_audit": inventory.fuzzy_near_duplicate_audit,
        "fuzzy_near_duplicate_audit_sha256": canonical_json_sha256(
            inventory.fuzzy_near_duplicate_audit
        ),
        "dual_cutoff": {
            "published_at_kst_strictly_before": CUTOFF_TIMESTAMP,
            "effective_trade_date_strictly_before": CUTOFF_TRADE_DATE,
            "operator": "AND",
        },
    }


def _maximum_resident_set_record() -> dict[str, int | str]:
    maximum = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if sys.platform == "darwin":
        return {"value": maximum, "unit": "bytes"}
    return {"value": maximum, "unit": "kibibytes"}


def derive_inventory_oracle(
    *,
    report_path: Path,
    actor_id: str,
) -> dict[str, Any]:
    if INVENTORY_ORACLE_STATUS != "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3":
        raise RuntimeError(
            "inventory oracle derivation은 AllPairs fuzzy v3 PENDING에서만 허용됩니다."
        )
    _require_absent_output(report_path, "inventory oracle derivation report")
    actor = actor_id.strip()
    if not actor or len(actor) > 128 or any(character in actor for character in "\r\n\0"):
        raise RuntimeError("inventory oracle derivation actor ID가 유효하지 않습니다.")
    inputs, _ = verify_source_inputs()
    recipes = oracle_recipe_records()
    software = oracle_software_fingerprint()
    started = time.monotonic()
    inventory = compute_corpus_inventory(enforce_expected=False)
    elapsed_seconds = time.monotonic() - started
    counts, hashes = inventory_oracle_candidate(inventory)
    candidate_sha256 = canonical_json_sha256({"expected_counts": counts, "expected_hashes": hashes})
    current_inputs, _ = verify_source_inputs()
    if (
        current_inputs != inputs
        or oracle_recipe_records() != recipes
        or oracle_software_fingerprint() != software
    ):
        raise RuntimeError("inventory oracle derivation 중 입력/recipe/runtime이 변경되었습니다.")
    report = {
        "schema_version": "k-fnspid-dapt-inventory-oracle-derivation/v2",
        "status": "DERIVED_PENDING_INDEPENDENT_REVIEW",
        "generated_at": datetime.now(UTC).isoformat(),
        "derivation_actor_id": actor,
        "inventory_oracle_status_at_derivation": INVENTORY_ORACLE_STATUS,
        "input_artifacts": inputs,
        "oracle_recipe_artifacts": recipes,
        "oracle_software_fingerprint": software,
        "candidate_expected_counts": counts,
        "candidate_expected_hashes": hashes,
        "candidate_sha256": candidate_sha256,
        "inventory": inventory_record(inventory),
        "performance": {
            "elapsed_seconds": elapsed_seconds,
            "process_maximum_resident_set": _maximum_resident_set_record(),
            "deterministic_fuzzy_operation_counts": {
                name: inventory.fuzzy_near_duplicate_audit[name]
                for name in sorted(INVENTORY_FUZZY_OPERATION_FIELDS)
            },
        },
        "prepared_artifact_promoted": False,
        "pack_oracle_derived": False,
        "precision_pilot_executed": False,
        "training_executed": False,
    }
    _atomic_write_new(
        report_path,
        (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(),
    )
    return {
        "status": "INVENTORY_ORACLE_DERIVED_PENDING_REVIEW",
        "candidate_sha256": candidate_sha256,
        "derivation_report": artifact_record(report_path),
        "performance": report["performance"],
    }


def _segment_paths(directory: Path) -> dict[tuple[str, str], Path]:
    return {
        (split, source): directory / f"segments-{split.lower()}-{source.lower()}.parquet"
        for split in ("TRAIN", "VALIDATION")
        for source in ("NEWS", "DISCLOSURE")
    }


def build_segment_files(
    *,
    directory: Path,
    inventory: CorpusInventory,
    tokenizer: Any,
    enforce_pack_oracle: bool = True,
) -> dict[str, Any]:
    paths = _segment_paths(directory)
    schema = segment_schema()
    writers = {
        key: pq.ParquetWriter(
            path,
            schema,
            compression="zstd",
            compression_level=9,
            use_dictionary=True,
        )
        for key, path in paths.items()
    }
    buffers: dict[tuple[str, str], list[dict[str, Any]]] = {key: [] for key in paths}
    observed_split: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    full_counts: Counter[str] = Counter()
    raw_tokens: Counter[str] = Counter()
    used_tokens: Counter[str] = Counter()
    pending: list[dict[str, Any]] = []

    def flush_pending() -> None:
        if not pending:
            return
        title_texts = [str(row["title"] or "").strip() for row in pending]
        snippet_texts = [str(row["snippet"] or "").strip() for row in pending]
        full_texts = [str(row["full_text"] or "").strip() for row in pending]
        title_batch = tokenizer(title_texts, add_special_tokens=False)["input_ids"]
        snippet_batch = tokenizer(snippet_texts, add_special_tokens=False)["input_ids"]
        full_batch = tokenizer(full_texts, add_special_tokens=False)["input_ids"]
        for row, title_ids, snippet_ids, full_ids, full_text in zip(
            pending,
            title_batch,
            snippet_batch,
            full_batch,
            full_texts,
            strict=True,
        ):
            source = str(row["source_type"])
            identity = identity_from_mapping(row)
            split = str(row["_dapt_split"])
            if split not in SPLIT_CODES:
                raise RuntimeError("inventory row assignment가 잘못되었습니다.")
            segment, structural_positions, audit = format_tokenized_segment(
                source_type=source,
                title_tokens=title_ids,
                snippet_tokens=snippet_ids,
                full_tokens=full_ids,
                has_full_text=bool(full_text),
            )
            if audit["has_full_text"]:
                full_counts[source] += 1
            for field in ("title", "snippet", "full"):
                raw_tokens[field] += int(audit[f"raw_{field}"])
                used_tokens[field] += int(audit[f"used_{field}"])
            key = (split, source)
            buffers[key].append(
                {
                    "document_id": identity.document_id,
                    "length": len(segment),
                    "sort_digest": sha256(PACK_SALT + identity.document_id.encode()).digest(),
                    "token_ids": segment,
                    "structural_positions": structural_positions,
                }
            )
            observed_split[split][source] += 1
            if len(buffers[key]) >= 4_096:
                _write_table_batch(writers[key], buffers[key], schema)
        pending.clear()

    try:
        for row_index, row in enumerate(_iter_parquet_rows(DOCUMENTS_PATH, TEXT_COLUMNS)):
            source = str(row["source_type"])
            if source not in SOURCE_CODES:
                raise RuntimeError(f"지원하지 않는 source_type입니다: {source}")
            assignment = inventory.row_assignments[row_index]
            if assignment == 0:
                continue
            if assignment not in {1, 2}:
                raise RuntimeError("inventory row assignment code가 잘못되었습니다.")
            row["_dapt_split"] = "TRAIN" if assignment == 1 else "VALIDATION"
            pending.append(row)
            if len(pending) >= 2_048:
                flush_pending()
        flush_pending()
        for key, writer in writers.items():
            _write_table_batch(writer, buffers[key], schema)
    finally:
        for writer in writers.values():
            writer.close()
    actual_split = {
        split: _ordered_source_counts(observed_split[split]) for split in ("TRAIN", "VALIDATION")
    }
    audit = {
        "split_count": actual_split,
        "full_text_count": _ordered_source_counts(full_counts),
        "raw_token_count": {name: raw_tokens[name] for name in ("title", "snippet", "full")},
        "used_token_count": {name: used_tokens[name] for name in ("title", "snippet", "full")},
    }
    if audit["split_count"] != EXPECTED["split_count"]:
        raise RuntimeError(f"DAPT tokenize split count 계약이 불일치합니다: {audit}")
    if enforce_pack_oracle and (
        audit["full_text_count"] != PACK_EXPECTED["full_text_count"]
        or audit["raw_token_count"] != PACK_EXPECTED["raw_token_count"]
        or audit["used_token_count"] != PACK_EXPECTED["used_token_count"]
    ):
        raise RuntimeError(f"DAPT tokenize/crop count 계약이 불일치합니다: {audit}")
    return audit


def _segment_metadata(table: pa.Table) -> list[SegmentMetadata]:
    document_ids = table.column("document_id").to_pylist()
    lengths = table.column("length").to_pylist()
    digests = table.column("sort_digest").to_pylist()
    return [
        SegmentMetadata(
            row_index=index,
            document_id=str(document_id),
            length=int(length),
            sort_digest=bytes(digest),
        )
        for index, (document_id, length, digest) in enumerate(
            zip(document_ids, lengths, digests, strict=True)
        )
    ]


def build_pack_files(
    *,
    directory: Path,
    allowed_ids: Sequence[int],
    enforce_pack_oracle: bool = True,
) -> dict[str, Any]:
    train_path = directory / "train_packs.parquet"
    validation_path = directory / "validation_packs.parquet"
    validation_masks_path = directory / "validation_fixed_masks.parquet"
    lineage_path = directory / "pack_lineage.parquet"
    unmasked_schema = pack_schema()
    masked_schema = pack_schema(masked=True)
    retained_lineage_schema = lineage_schema()
    train_writer = pq.ParquetWriter(
        train_path,
        unmasked_schema,
        compression="zstd",
        compression_level=9,
        use_dictionary=True,
    )
    validation_writer = pq.ParquetWriter(
        validation_path,
        unmasked_schema,
        compression="zstd",
        compression_level=9,
        use_dictionary=True,
    )
    validation_masks_writer = pq.ParquetWriter(
        validation_masks_path,
        masked_schema,
        compression="zstd",
        compression_level=9,
        use_dictionary=True,
    )
    lineage_writer = pq.ParquetWriter(
        lineage_path,
        retained_lineage_schema,
        compression="zstd",
        compression_level=9,
        use_dictionary=True,
    )
    pack_digest = sha256()
    lineage_digest = sha256()
    train_mask_digest = sha256()
    validation_mask_digest = sha256()
    pack_counts: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    document_counts: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    mask_counts: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    segment_token_count = 0
    non_padding_token_count = 0
    train_buffer: list[dict[str, Any]] = []
    validation_buffer: list[dict[str, Any]] = []
    validation_mask_buffer: list[dict[str, Any]] = []
    lineage_buffer: list[dict[str, Any]] = []
    segment_paths = _segment_paths(directory)
    try:
        for split in ("TRAIN", "VALIDATION"):
            for source in ("NEWS", "DISCLOSURE"):
                table = pq.read_table(segment_paths[(split, source)])
                metadata = _segment_metadata(table)
                bins = best_fit_decreasing(metadata)
                document_ids = table.column("document_id")
                token_lists = table.column("token_ids")
                structural_position_lists = table.column("structural_positions")
                for pack_id, indices in enumerate(bins):
                    packed = [CLS_ID]
                    structural_mask = [True]
                    segment_lengths: list[int] = []
                    lineage_rows: list[bytes] = []
                    for row_index in indices:
                        document_id = str(document_ids[row_index].as_py())
                        tokens = [int(value) for value in token_lists[row_index].as_py()]
                        structural_positions = {
                            int(value) for value in structural_position_lists[row_index].as_py()
                        }
                        offset = len(packed)
                        packed.extend(tokens)
                        structural_mask.extend(
                            position in structural_positions for position in range(len(tokens))
                        )
                        segment_lengths.append(len(tokens))
                        document_counts[split][source] += 1
                        lineage_rows.append(
                            (
                                json.dumps(
                                    {
                                        "document_id": document_id,
                                        "source_type": source,
                                        "split": split,
                                        "pack_id": pack_id,
                                        "offset": offset,
                                        "length": len(tokens),
                                        "segment_sha256": segment_sha256(tokens),
                                    },
                                    ensure_ascii=False,
                                    sort_keys=True,
                                    separators=(",", ":"),
                                )
                                + "\n"
                            ).encode()
                        )
                        lineage_buffer.append(
                            {
                                "document_id": document_id,
                                "source_type": source,
                                "split": split,
                                "pack_id": pack_id,
                                "offset": offset,
                                "length": len(tokens),
                                "segment_sha256": segment_sha256(tokens),
                            }
                        )
                        if len(lineage_buffer) >= 4_096:
                            _write_table_batch(
                                lineage_writer,
                                lineage_buffer,
                                retained_lineage_schema,
                            )
                    valid_length = len(packed)
                    if valid_length > MAX_LENGTH:
                        raise RuntimeError("BFD pack이 256 token을 초과했습니다.")
                    packed.extend([PAD_ID] * (MAX_LENGTH - valid_length))
                    structural_mask.extend([False] * (MAX_LENGTH - valid_length))
                    row = PackedRow(
                        split=split,
                        source_type=source,
                        pack_id=pack_id,
                        valid_length=valid_length,
                        input_ids=tuple(packed),
                        segment_lengths=tuple(segment_lengths),
                        structural_mask=tuple(structural_mask),
                    )
                    update_pack_ids_hash(pack_digest, row)
                    for lineage_row in lineage_rows:
                        lineage_digest.update(lineage_row)
                    masked, labels, mask_audit = mask_pack(row, allowed_ids)
                    target_mask_digest = (
                        train_mask_digest if split == "TRAIN" else validation_mask_digest
                    )
                    update_mask_hash(target_mask_digest, row, masked, labels)
                    mask_counts[split].update(mask_audit)
                    output = {
                        "source_type": source,
                        "pack_id": pack_id,
                        "valid_length": valid_length,
                        "segment_lengths": segment_lengths,
                        "structural_mask": structural_mask,
                        "input_ids": list(row.input_ids),
                    }
                    if split == "TRAIN":
                        train_buffer.append(output)
                        if len(train_buffer) >= 1_024:
                            _write_table_batch(train_writer, train_buffer, unmasked_schema)
                    else:
                        validation_buffer.append(output)
                        validation_mask_buffer.append(
                            {**output, "input_ids": list(masked), "labels": list(labels)}
                        )
                        if len(validation_buffer) >= 1_024:
                            _write_table_batch(
                                validation_writer,
                                validation_buffer,
                                unmasked_schema,
                            )
                            _write_table_batch(
                                validation_masks_writer,
                                validation_mask_buffer,
                                masked_schema,
                            )
                    pack_counts[split][source] += 1
                    group_segment_tokens = valid_length - 1
                    segment_token_count += group_segment_tokens
                    non_padding_token_count += valid_length
        _write_table_batch(train_writer, train_buffer, unmasked_schema)
        _write_table_batch(validation_writer, validation_buffer, unmasked_schema)
        _write_table_batch(validation_masks_writer, validation_mask_buffer, masked_schema)
        _write_table_batch(lineage_writer, lineage_buffer, retained_lineage_schema)
    finally:
        train_writer.close()
        validation_writer.close()
        validation_masks_writer.close()
        lineage_writer.close()
    counts = {
        split: _ordered_source_counts(pack_counts[split]) for split in ("TRAIN", "VALIDATION")
    }
    packed_document_counts = {
        split: _ordered_source_counts(document_counts[split]) for split in ("TRAIN", "VALIDATION")
    }
    if packed_document_counts != EXPECTED["split_count"]:
        raise RuntimeError("DAPT pack lineage 문서 수가 inventory split과 다릅니다.")
    padded_counts = {
        split: sum(counts[split].values()) * MAX_LENGTH for split in ("TRAIN", "VALIDATION")
    }
    hashes = {
        "unmasked_packed_ids": pack_digest.hexdigest(),
        "pack_lineage_jsonl": lineage_digest.hexdigest(),
        "train_epoch0_masks": train_mask_digest.hexdigest(),
        "validation_fixed_masks": validation_mask_digest.hexdigest(),
    }
    actual = {
        "pack_count": counts,
        "segment_token_count": segment_token_count,
        "packed_non_padding_token_count": non_padding_token_count,
        "padded_token_count": padded_counts,
    }
    expected = {name: PACK_EXPECTED[name] for name in actual} if enforce_pack_oracle else actual
    if enforce_pack_oracle and (
        actual != expected or any(hashes[name] != PACK_EXPECTED_HASHES[name] for name in hashes)
    ):
        raise RuntimeError(f"DAPT pack/mask 계약이 불일치합니다: {actual}, {hashes}")
    return {
        **actual,
        "document_count": packed_document_counts,
        "canonical_hashes": hashes,
        "mask_count": {
            split: {
                name: mask_counts[split][name]
                for name in ("selected", "mask", "random", "unchanged")
            }
            for split in ("TRAIN", "VALIDATION")
        },
        "token_utilization": non_padding_token_count / sum(padded_counts.values()),
    }


def _pack_oracle_candidate(
    tokenization: Mapping[str, Any],
    packing: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    counts = {
        "full_text_count": tokenization["full_text_count"],
        "raw_token_count": tokenization["raw_token_count"],
        "used_token_count": tokenization["used_token_count"],
        "pack_count": packing["pack_count"],
        "segment_token_count": packing["segment_token_count"],
        "packed_non_padding_token_count": packing["packed_non_padding_token_count"],
        "padded_token_count": packing["padded_token_count"],
    }
    hashes = dict(cast(Mapping[str, str], packing["canonical_hashes"]))
    if set(counts) != PACK_EXPECTED_FIELDS or set(hashes) != PACK_EXPECTED_HASH_FIELDS:
        raise RuntimeError("derivation pack oracle 필드 계약이 다릅니다.")
    if any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes.values()):
        raise RuntimeError("derivation pack oracle hash가 유효하지 않습니다.")
    return counts, hashes


def derive_pack_oracle(
    *,
    report_path: Path,
    scratch_dir: Path,
    actor_id: str,
) -> dict[str, Any]:
    """prepared artifact를 게시하지 않고 pack oracle 후보만 산출한다."""
    if (
        INVENTORY_ORACLE_STATUS != "LOCKED"
        or PACK_ORACLE_STATUS != "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3"
    ):
        raise RuntimeError("pack oracle derivation은 PENDING 상태에서만 허용됩니다.")
    require_locked_inventory_oracle()
    _require_absent_output(report_path, "pack oracle derivation report")
    _require_absent_output(scratch_dir, "pack oracle derivation scratch")
    normalized_actor = actor_id.strip()
    if (
        not normalized_actor
        or len(normalized_actor) > 128
        or any(character in normalized_actor for character in "\r\n\0")
    ):
        raise RuntimeError("pack oracle derivation actor ID가 유효하지 않습니다.")
    inputs, _ = verify_source_inputs()
    recipes = oracle_recipe_records()
    inventory = compute_corpus_inventory(enforce_expected=True)
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        local_files_only=True,
    )
    allowed_ids = verify_tokenizer_contract(tokenizer)
    temporary = _safe_temporary_directory(scratch_dir)
    try:
        tokenization = build_segment_files(
            directory=temporary,
            inventory=inventory,
            tokenizer=tokenizer,
            enforce_pack_oracle=False,
        )
        packing = build_pack_files(
            directory=temporary,
            allowed_ids=allowed_ids,
            enforce_pack_oracle=False,
        )
        candidate_counts, candidate_hashes = _pack_oracle_candidate(tokenization, packing)
        verify_pack_semantics(
            temporary,
            allowed_ids=allowed_ids,
            expected_pack_count=candidate_counts["pack_count"],
            expected_document_count=cast(
                Mapping[str, Mapping[str, int]],
                EXPECTED["split_count"],
            ),
            expected_hashes=candidate_hashes,
        )
        current_inputs, _ = verify_source_inputs()
        if current_inputs != inputs or oracle_recipe_records() != recipes:
            raise RuntimeError("pack oracle derivation 중 입력 또는 recipe가 변경되었습니다.")
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
            _fsync_directory(temporary.parent)
    total_updates = math.ceil(
        sum(candidate_counts["pack_count"]["TRAIN"].values()) / EFFECTIVE_BATCH_SIZE
    )
    warmup_updates = math.ceil(total_updates * 0.05)
    candidate_digest = canonical_json_sha256(
        {
            "expected_counts": candidate_counts,
            "expected_hashes": candidate_hashes,
            "total_updates": total_updates,
            "warmup_updates": warmup_updates,
        }
    )
    report = {
        "schema_version": "k-fnspid-dapt-pack-oracle-derivation/v1",
        "status": "DERIVED_PENDING_INDEPENDENT_REVIEW",
        "generated_at": datetime.now(UTC).isoformat(),
        "derivation_actor_id": normalized_actor,
        "inventory_oracle_status_at_derivation": INVENTORY_ORACLE_STATUS,
        "oracle_status_at_derivation": PACK_ORACLE_STATUS,
        "input_artifacts": inputs,
        "oracle_recipe_artifacts": recipes,
        "oracle_software_fingerprint": oracle_software_fingerprint(),
        "inventory_commitments": EXPECTED_HASHES,
        "candidate_expected_counts": candidate_counts,
        "candidate_expected_hashes": candidate_hashes,
        "candidate_total_updates": total_updates,
        "candidate_warmup_updates": warmup_updates,
        "candidate_sha256": candidate_digest,
        "semantic_reread_verified": True,
        "scratch_artifacts_retained": False,
        "prepared_artifact_promoted": False,
        "precision_pilot_executed": False,
        "training_executed": False,
        "runtime_environment": runtime_environment(),
    }
    _atomic_write_new(
        report_path,
        (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(),
    )
    return {
        "status": "PACK_ORACLE_DERIVED_PENDING_REVIEW",
        "candidate_sha256": candidate_digest,
        "derivation_report": artifact_record(report_path),
    }


def prepare_corpus(output_dir: Path) -> dict[str, Any]:
    _require_absent_output(output_dir, "prepared DAPT")
    require_locked_pack_oracle()
    inventory_oracle_provenance = inventory_oracle_lock_record()
    pack_oracle_provenance = pack_oracle_lock_record()
    inputs, _ = verify_source_inputs()
    dependencies = dependency_records()
    inventory = compute_corpus_inventory()
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        local_files_only=True,
    )
    allowed_ids = verify_tokenizer_contract(tokenizer)
    temporary = _safe_temporary_directory(output_dir)
    try:
        tokenization = build_segment_files(
            directory=temporary,
            inventory=inventory,
            tokenizer=tokenizer,
        )
        packing = build_pack_files(directory=temporary, allowed_ids=allowed_ids)
        for path in _segment_paths(temporary).values():
            path.unlink()
        artifact_files: dict[str, dict[str, int | str]] = {}
        for name, filename in (
            ("train_packs", "train_packs.parquet"),
            ("validation_packs", "validation_packs.parquet"),
            ("validation_fixed_masks", "validation_fixed_masks.parquet"),
            ("pack_lineage", "pack_lineage.parquet"),
        ):
            record = artifact_record(temporary / filename)
            record["path"] = _expected_artifact_path(output_dir, filename)
            artifact_files[name] = record
        current_inputs, _ = verify_source_inputs()
        current_dependencies = dependency_records()
        if (
            current_inputs != inputs
            or current_dependencies != dependencies
            or inventory_oracle_lock_record() != inventory_oracle_provenance
            or pack_oracle_lock_record() != pack_oracle_provenance
        ):
            raise RuntimeError("DAPT 입력이 prepare 중 변경되었습니다.")
        manifest = {
            "schema_version": "k-fnspid-dapt-prepared/v2",
            "status": "PREPARED_NOT_TRAINED",
            "generated_at": datetime.now(UTC).isoformat(),
            "dataset_revision": "K-FNSPID-v4",
            "input_artifacts": inputs,
            "dependency_artifacts": dependencies,
            "base_model": {
                "repository": BASE_MODEL,
                "revision": BASE_REVISION,
                "weights_only": True,
                "trust_remote_code": False,
                "source_file_hashes": BASE_FILE_HASHES,
            },
            "inventory": inventory_record(inventory),
            "inventory_oracle": inventory_oracle_provenance,
            "pack_oracle": pack_oracle_provenance,
            "tokenization": tokenization,
            "packing": packing,
            "artifact_files": artifact_files,
            "serializer_contract": {
                "version": "k-fnspid-dapt-canonical-serializers/v2",
                "pack_header": ">BBIH",
                "split_codes": SPLIT_CODES,
                "source_codes": SOURCE_CODES,
                "uint_token_byte_order": SERIALIZER_BYTE_ORDER,
                "lineage_json": "UTF-8 sorted keys compact JSONL with final LF",
            },
            "masking": {
                "probability": 0.15,
                "replacement": {"mask": 0.8, "random": 0.1, "unchanged": 0.1},
                "special_ids_excluded": sorted(SPECIAL_IDS),
                "structural_marker_positions_excluded": True,
                "natural_marker_token_ids_eligible": sorted(MARKER_IDS),
                "unused_token_count_excluded": UNUSED_TOKEN_COUNT,
                "allowed_random_token_count": len(allowed_ids),
                "allowed_random_token_ids_sha256": EXPECTED_HASHES["allowed_random_token_ids"],
                "train_epoch": EPOCH_INDEX,
                "fixed_validation_masks": True,
            },
            "runtime_environment": runtime_environment(),
            "claim_limitations": [
                "DAPT의 downstream 성능 개선은 아직 확인되지 않았다.",
                "현재 supervised v5에는 2026년 4~7월 자료가 포함되어 전체 모델은 OOT가 아니다.",
                "DAPT는 단일 seed로 설계되어 seed 불확실성을 추정하지 못한다.",
            ],
        }
        manifest_path = temporary / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        _fsync_tree(temporary)
        _atomic_rename_directory_new(temporary, output_dir)
        return {
            "status": "PREPARED",
            "prepared_manifest": artifact_record(output_dir / "manifest.json"),
            "prepared_directory": str(output_dir),
        }
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def read_json_object(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"{label}이 없거나 symlink입니다: {path}")
    value = json.loads(_stable_file_payload(path).decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}이 JSON object가 아닙니다.")
    return value


def _validate_utc_timestamp(value: object, label: str) -> None:
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError as exception:
        raise RuntimeError(f"{label}이 유효하지 않습니다.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise RuntimeError(f"{label}이 UTC가 아닙니다.")


def _validate_protection_increment_audit(
    fuzzy_audit: Mapping[str, Any],
    *,
    expected_post_fuzzy_document_count: object,
) -> None:
    count_fields = (
        "pre_fuzzy_exact_identity_protected_component_count",
        "pre_fuzzy_exact_identity_protected_document_count",
        "fuzzy_direct_increment_pre_fuzzy_component_count",
        "fuzzy_direct_increment_document_count",
        "fuzzy_transitive_only_increment_pre_fuzzy_component_count",
        "fuzzy_transitive_only_increment_document_count",
        "fuzzy_total_increment_pre_fuzzy_component_count",
        "fuzzy_total_increment_document_count",
        "post_fuzzy_protected_pre_fuzzy_component_membership_count",
        "post_fuzzy_protected_component_count",
        "post_fuzzy_protected_component_merge_reduction",
        "post_fuzzy_protected_document_count",
    )
    values = {name: fuzzy_audit.get(name) for name in count_fields}
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in values.values()
    ):
        raise RuntimeError("inventory fuzzy 보호 증분 count가 유효하지 않습니다.")
    counts = cast(dict[str, int], values)
    baseline_sources = _validate_source_count_map(
        fuzzy_audit.get("pre_fuzzy_exact_identity_protected_source_document_count"),
        "pre-fuzzy protected source count",
    )
    direct_sources = _validate_source_count_map(
        fuzzy_audit.get("fuzzy_direct_increment_source_document_count"),
        "direct fuzzy increment source count",
    )
    transitive_sources = _validate_source_count_map(
        fuzzy_audit.get("fuzzy_transitive_only_increment_source_document_count"),
        "transitive fuzzy increment source count",
    )
    final_sources = _validate_source_count_map(
        fuzzy_audit.get("post_fuzzy_protected_source_document_count"),
        "post-fuzzy protected source count",
    )
    if (
        counts["fuzzy_total_increment_pre_fuzzy_component_count"]
        != counts["fuzzy_direct_increment_pre_fuzzy_component_count"]
        + counts["fuzzy_transitive_only_increment_pre_fuzzy_component_count"]
        or counts["fuzzy_total_increment_document_count"]
        != counts["fuzzy_direct_increment_document_count"]
        + counts["fuzzy_transitive_only_increment_document_count"]
        or counts["post_fuzzy_protected_pre_fuzzy_component_membership_count"]
        != counts["pre_fuzzy_exact_identity_protected_component_count"]
        + counts["fuzzy_total_increment_pre_fuzzy_component_count"]
        or counts["post_fuzzy_protected_component_count"]
        + counts["post_fuzzy_protected_component_merge_reduction"]
        != counts["post_fuzzy_protected_pre_fuzzy_component_membership_count"]
        or counts["post_fuzzy_protected_document_count"]
        != counts["pre_fuzzy_exact_identity_protected_document_count"]
        + counts["fuzzy_total_increment_document_count"]
        or counts["post_fuzzy_protected_document_count"] != expected_post_fuzzy_document_count
        or sum(baseline_sources.values())
        != counts["pre_fuzzy_exact_identity_protected_document_count"]
        or sum(direct_sources.values()) != counts["fuzzy_direct_increment_document_count"]
        or sum(transitive_sources.values())
        != counts["fuzzy_transitive_only_increment_document_count"]
        or any(
            final_sources[source]
            != baseline_sources[source] + direct_sources[source] + transitive_sources[source]
            for source in ("NEWS", "DISCLOSURE")
        )
        or fuzzy_audit.get("protection_increment_categories_disjoint") is not True
        or fuzzy_audit.get("protection_increment_document_conservation_verified") is not True
        or fuzzy_audit.get("protection_increment_component_conservation_verified") is not True
    ):
        raise RuntimeError("inventory fuzzy 보호 증분 보존 계약이 다릅니다.")


def load_inventory_oracle_derivation_report(path: Path) -> dict[str, Any]:
    report = read_json_object(path, "inventory oracle derivation report")
    _require_exact_keys(
        report,
        {
            "schema_version",
            "status",
            "generated_at",
            "derivation_actor_id",
            "inventory_oracle_status_at_derivation",
            "input_artifacts",
            "oracle_recipe_artifacts",
            "oracle_software_fingerprint",
            "candidate_expected_counts",
            "candidate_expected_hashes",
            "candidate_sha256",
            "inventory",
            "performance",
            "prepared_artifact_promoted",
            "pack_oracle_derived",
            "precision_pilot_executed",
            "training_executed",
        },
        "inventory oracle derivation report",
    )
    actor = report["derivation_actor_id"]
    if (
        report["schema_version"] != "k-fnspid-dapt-inventory-oracle-derivation/v2"
        or report["status"] != "DERIVED_PENDING_INDEPENDENT_REVIEW"
        or report["inventory_oracle_status_at_derivation"]
        != "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3"
        or not isinstance(actor, str)
        or not actor.strip()
        or len(actor) > 128
        or any(character in actor for character in "\r\n\0")
        or report["prepared_artifact_promoted"] is not False
        or report["pack_oracle_derived"] is not False
        or report["precision_pilot_executed"] is not False
        or report["training_executed"] is not False
    ):
        raise RuntimeError("inventory oracle derivation report 계약이 다릅니다.")
    _validate_utc_timestamp(report["generated_at"], "inventory oracle generated_at")
    current_inputs, _ = verify_source_inputs()
    if (
        report["input_artifacts"] != current_inputs
        or report["oracle_recipe_artifacts"] != oracle_recipe_records()
        or report["oracle_software_fingerprint"] != oracle_software_fingerprint()
    ):
        raise RuntimeError("inventory oracle derivation provenance가 현재 계약과 다릅니다.")
    counts = _require_exact_keys(
        report["candidate_expected_counts"],
        set(EXPECTED),
        "inventory oracle candidate counts",
    )
    hashes = _require_exact_keys(
        report["candidate_expected_hashes"],
        set(EXPECTED_HASHES),
        "inventory oracle candidate hashes",
    )
    if any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
        for value in hashes.values()
    ):
        raise RuntimeError("inventory oracle candidate SHA-256이 유효하지 않습니다.")
    digest = canonical_json_sha256({"expected_counts": counts, "expected_hashes": hashes})
    inventory = report["inventory"]
    if not isinstance(inventory, dict) or not isinstance(
        inventory.get("fuzzy_near_duplicate_audit"), dict
    ):
        raise RuntimeError("inventory oracle 상세 audit이 없습니다.")
    fuzzy_audit = cast(dict[str, Any], inventory["fuzzy_near_duplicate_audit"])
    if (
        report["candidate_sha256"] != digest
        or hashes["fuzzy_near_duplicate_audit"] != canonical_json_sha256(fuzzy_audit)
        or inventory.get("source_document_count") != counts["source_document_count"]
        or inventory.get("eligible_count") != counts["eligible_count"]
        or inventory.get("split_count") != counts["split_count"]
        or inventory.get("eligible_component_count") != counts["eligible_component_count"]
        or fuzzy_audit.get("policy_version") != "allpairs-frequency-prefix-exact-dice-v3"
        or fuzzy_audit.get("scope")
        != (
            "dual-cutoff-documents-plus-exact-identity-protected-components-"
            "plus-protected-seeds-cross-source"
        )
        or fuzzy_audit.get("train_validation_fuzzy_cross_split_after_component_split") != 0
        or fuzzy_audit.get("remaining_eligible_protected_fuzzy_match_document_count") != 0
    ):
        raise RuntimeError("inventory oracle candidate/audit 재계산 결과가 다릅니다.")
    _validate_protection_increment_audit(
        fuzzy_audit,
        expected_post_fuzzy_document_count=counts["protected_component_document_count"],
    )
    candidate_generation = fuzzy_audit.get("candidate_generation")
    verification = fuzzy_audit.get("verification")
    if (
        not isinstance(candidate_generation, dict)
        or candidate_generation.get("algorithm")
        != "AllPairs/PPJoin global-frequency prefix filtering"
        or candidate_generation.get("candidate_truncation_allowed") is not False
        or candidate_generation.get("source_type_partitioned") is not False
        or candidate_generation.get("maximum_candidates_per_document_fail_closed")
        != FUZZY_MAX_CANDIDATES_PER_DOCUMENT
        or not isinstance(verification, dict)
        or verification.get("method") != "exact sorted-shingle intersection and integer Dice"
        or verification.get("candidate_recall_contract") != "complete for the fixed Dice threshold"
        or verification.get("transitive_closure") != "union-find over exact/identity/fuzzy edges"
    ):
        raise RuntimeError("inventory oracle AllPairs fuzzy 계약이 다릅니다.")
    performance = _require_exact_keys(
        report["performance"],
        {
            "elapsed_seconds",
            "process_maximum_resident_set",
            "deterministic_fuzzy_operation_counts",
        },
        "inventory oracle performance",
    )
    elapsed = _finite_number(performance["elapsed_seconds"], "inventory elapsed seconds")
    rss = _require_exact_keys(
        performance["process_maximum_resident_set"],
        {"value", "unit"},
        "inventory maximum resident set",
    )
    if (
        elapsed < 0
        or not isinstance(rss["value"], int)
        or isinstance(rss["value"], bool)
        or rss["value"] <= 0
        or rss["unit"] not in {"bytes", "kibibytes"}
    ):
        raise RuntimeError("inventory performance 계측이 유효하지 않습니다.")
    operation_counts = _require_exact_keys(
        performance["deterministic_fuzzy_operation_counts"],
        set(INVENTORY_FUZZY_OPERATION_FIELDS),
        "inventory fuzzy operation counts",
    )
    if (
        any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in operation_counts.values()
        )
        or any(fuzzy_audit.get(name) != value for name, value in operation_counts.items())
        or operation_counts["parquet_full_scan_count"] != 4
        or operation_counts["length_filtered_pair_count"]
        != operation_counts["exact_verified_pair_count"]
        or operation_counts["exact_verified_pair_count"] > operation_counts["candidate_pair_count"]
        or operation_counts["matched_pair_count"] > operation_counts["exact_verified_pair_count"]
        or operation_counts["cross_source_matched_pair_count"]
        > operation_counts["matched_pair_count"]
        or operation_counts["maximum_observed_candidates_per_document"]
        > FUZZY_MAX_CANDIDATES_PER_DOCUMENT
        or operation_counts["deterministic_storage_lower_bound_bytes"]
        != 4
        * (
            operation_counts["total_corpus_signature_token_ids"]
            + operation_counts["prefix_posting_count"]
        )
    ):
        raise RuntimeError("inventory fuzzy operation count가 audit과 다릅니다.")
    return report


INVENTORY_ORACLE_REVIEW_CHECKLIST = {
    "source_and_protected_hashes_verified": True,
    "allpairs_candidate_completeness_reviewed": True,
    "bruteforce_property_test_reviewed": True,
    "cross_source_and_transitive_union_reviewed": True,
    "protected_and_train_validation_zero_overlap_reviewed": True,
    "performance_and_memory_reviewed": True,
    "no_downstream_artifact_promoted": True,
}


def record_inventory_oracle_review(
    *,
    derivation_report_path: Path,
    receipt_path: Path,
    reviewer_id: str,
    review_note: str,
) -> dict[str, Any]:
    if INVENTORY_ORACLE_STATUS != "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3":
        raise RuntimeError("inventory oracle review는 source lock 전 PENDING에서만 허용됩니다.")
    _require_absent_output(receipt_path, "inventory oracle review receipt")
    report = load_inventory_oracle_derivation_report(derivation_report_path)
    reviewer = reviewer_id.strip()
    note = review_note.strip()
    if (
        not reviewer
        or len(reviewer) > 128
        or any(character in reviewer for character in "\r\n\0")
        or reviewer == report["derivation_actor_id"]
    ):
        raise RuntimeError("독립 inventory oracle reviewer ID가 유효하지 않습니다.")
    if not note or len(note) > 2_000 or "\0" in note:
        raise RuntimeError("inventory oracle review note가 유효하지 않습니다.")
    receipt = {
        "schema_version": "k-fnspid-dapt-inventory-oracle-review/v2",
        "status": "APPROVED_PENDING_SOURCE_LOCK",
        "reviewed_at": datetime.now(UTC).isoformat(),
        "reviewer_id": reviewer,
        "derivation_actor_id": report["derivation_actor_id"],
        "review_note": note,
        "derivation_report": artifact_record(derivation_report_path),
        "input_artifacts": report["input_artifacts"],
        "oracle_recipe_artifacts": report["oracle_recipe_artifacts"],
        "oracle_software_fingerprint": report["oracle_software_fingerprint"],
        "candidate_expected_counts": report["candidate_expected_counts"],
        "candidate_expected_hashes": report["candidate_expected_hashes"],
        "candidate_sha256": report["candidate_sha256"],
        "review_checklist": INVENTORY_ORACLE_REVIEW_CHECKLIST,
        "independent_review_declared": True,
    }
    _atomic_write_new(
        receipt_path,
        (json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(),
    )
    return {
        "status": "INVENTORY_ORACLE_REVIEWED_PENDING_SOURCE_LOCK",
        "candidate_sha256": report["candidate_sha256"],
        "review_receipt": artifact_record(receipt_path),
    }


def load_inventory_oracle_review_receipt(
    path: Path,
    *,
    derivation_report_path: Path,
) -> dict[str, Any]:
    receipt = read_json_object(path, "inventory oracle review receipt")
    _require_exact_keys(
        receipt,
        {
            "schema_version",
            "status",
            "reviewed_at",
            "reviewer_id",
            "derivation_actor_id",
            "review_note",
            "derivation_report",
            "input_artifacts",
            "oracle_recipe_artifacts",
            "oracle_software_fingerprint",
            "candidate_expected_counts",
            "candidate_expected_hashes",
            "candidate_sha256",
            "review_checklist",
            "independent_review_declared",
        },
        "inventory oracle review receipt",
    )
    report = load_inventory_oracle_derivation_report(derivation_report_path)
    reviewer = receipt["reviewer_id"]
    note = receipt["review_note"]
    if (
        receipt["schema_version"] != "k-fnspid-dapt-inventory-oracle-review/v2"
        or receipt["status"] != "APPROVED_PENDING_SOURCE_LOCK"
        or receipt["derivation_report"] != artifact_record(derivation_report_path)
        or receipt["derivation_actor_id"] != report["derivation_actor_id"]
        or not isinstance(reviewer, str)
        or not reviewer.strip()
        or reviewer == report["derivation_actor_id"]
        or not isinstance(note, str)
        or not note.strip()
        or receipt["input_artifacts"] != report["input_artifacts"]
        or receipt["oracle_recipe_artifacts"] != report["oracle_recipe_artifacts"]
        or receipt["oracle_software_fingerprint"] != report["oracle_software_fingerprint"]
        or receipt["candidate_expected_counts"] != report["candidate_expected_counts"]
        or receipt["candidate_expected_hashes"] != report["candidate_expected_hashes"]
        or receipt["candidate_sha256"] != report["candidate_sha256"]
        or receipt["review_checklist"] != INVENTORY_ORACLE_REVIEW_CHECKLIST
        or receipt["independent_review_declared"] is not True
    ):
        raise RuntimeError("inventory oracle review receipt 계약이 다릅니다.")
    _validate_utc_timestamp(receipt["reviewed_at"], "inventory oracle reviewed_at")
    return receipt


def _validate_source_count_map(value: object, label: str) -> dict[str, int]:
    mapping = _require_exact_keys(value, {"NEWS", "DISCLOSURE"}, label)
    if any(
        not isinstance(count, int) or isinstance(count, bool) or count < 0
        for count in mapping.values()
    ):
        raise RuntimeError(f"{label} count가 유효하지 않습니다.")
    return cast(dict[str, int], mapping)


def _validate_pack_oracle_candidate(
    counts_value: object,
    hashes_value: object,
) -> tuple[dict[str, Any], dict[str, str]]:
    counts = _require_exact_keys(counts_value, PACK_EXPECTED_FIELDS, "pack oracle candidate counts")
    for field in ("full_text_count",):
        _validate_source_count_map(counts[field], f"pack oracle {field}")
    for field in ("raw_token_count", "used_token_count"):
        mapping = _require_exact_keys(counts[field], {"title", "snippet", "full"}, field)
        if any(
            not isinstance(count, int) or isinstance(count, bool) or count < 0
            for count in mapping.values()
        ):
            raise RuntimeError(f"pack oracle {field} count가 유효하지 않습니다.")
    if any(
        counts["used_token_count"][field] > counts["raw_token_count"][field]
        for field in ("title", "snippet", "full")
    ):
        raise RuntimeError("pack oracle used token count가 raw count를 초과합니다.")
    pack_count = _require_exact_keys(counts["pack_count"], {"TRAIN", "VALIDATION"}, "pack count")
    for split in ("TRAIN", "VALIDATION"):
        source_counts = _validate_source_count_map(pack_count[split], f"pack count {split}")
        if not all(source_counts.values()):
            raise RuntimeError("pack oracle source별 pack count가 0입니다.")
    for field in (
        "segment_token_count",
        "packed_non_padding_token_count",
    ):
        if (
            not isinstance(counts[field], int)
            or isinstance(counts[field], bool)
            or counts[field] <= 0
        ):
            raise RuntimeError(f"pack oracle {field}가 유효하지 않습니다.")
    padded = _require_exact_keys(
        counts["padded_token_count"],
        {"TRAIN", "VALIDATION"},
        "padded token count",
    )
    if any(
        not isinstance(count, int) or isinstance(count, bool) or count <= 0
        for count in padded.values()
    ):
        raise RuntimeError("pack oracle padded token count가 유효하지 않습니다.")
    total_pack_count = sum(sum(pack_count[split].values()) for split in ("TRAIN", "VALIDATION"))
    if (
        any(
            padded[split] != sum(pack_count[split].values()) * MAX_LENGTH
            for split in ("TRAIN", "VALIDATION")
        )
        or counts["packed_non_padding_token_count"]
        != counts["segment_token_count"] + total_pack_count
        or counts["packed_non_padding_token_count"] > sum(padded.values())
    ):
        raise RuntimeError("pack oracle pack/token 산술 계약이 다릅니다.")
    hashes = _require_exact_keys(
        hashes_value,
        PACK_EXPECTED_HASH_FIELDS,
        "pack oracle candidate hashes",
    )
    if any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
        for value in hashes.values()
    ):
        raise RuntimeError("pack oracle candidate SHA-256이 유효하지 않습니다.")
    return counts, cast(dict[str, str], hashes)


def load_pack_oracle_derivation_report(path: Path) -> dict[str, Any]:
    report = read_json_object(path, "pack oracle derivation report")
    _require_exact_keys(
        report,
        {
            "schema_version",
            "status",
            "generated_at",
            "derivation_actor_id",
            "inventory_oracle_status_at_derivation",
            "oracle_status_at_derivation",
            "input_artifacts",
            "oracle_recipe_artifacts",
            "oracle_software_fingerprint",
            "inventory_commitments",
            "candidate_expected_counts",
            "candidate_expected_hashes",
            "candidate_total_updates",
            "candidate_warmup_updates",
            "candidate_sha256",
            "semantic_reread_verified",
            "scratch_artifacts_retained",
            "prepared_artifact_promoted",
            "precision_pilot_executed",
            "training_executed",
            "runtime_environment",
        },
        "pack oracle derivation report",
    )
    actor = report["derivation_actor_id"]
    if (
        report["schema_version"] != "k-fnspid-dapt-pack-oracle-derivation/v1"
        or report["status"] != "DERIVED_PENDING_INDEPENDENT_REVIEW"
        or report["inventory_oracle_status_at_derivation"] != "LOCKED"
        or report["oracle_status_at_derivation"] != "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3"
        or not isinstance(actor, str)
        or not actor.strip()
        or len(actor) > 128
        or any(character in actor for character in "\r\n\0")
        or report["semantic_reread_verified"] is not True
        or report["scratch_artifacts_retained"] is not False
        or report["prepared_artifact_promoted"] is not False
        or report["precision_pilot_executed"] is not False
        or report["training_executed"] is not False
        or not isinstance(report["runtime_environment"], dict)
    ):
        raise RuntimeError("pack oracle derivation report 계약이 다릅니다.")
    _validate_utc_timestamp(report["generated_at"], "pack oracle derivation generated_at")
    current_inputs, _ = verify_source_inputs()
    if (
        report["input_artifacts"] != current_inputs
        or report["oracle_recipe_artifacts"] != oracle_recipe_records()
        or report["oracle_software_fingerprint"] != oracle_software_fingerprint()
        or report["inventory_commitments"] != EXPECTED_HASHES
    ):
        raise RuntimeError("pack oracle derivation provenance가 현재 계약과 다릅니다.")
    counts, hashes = _validate_pack_oracle_candidate(
        report["candidate_expected_counts"],
        report["candidate_expected_hashes"],
    )
    updates = math.ceil(sum(counts["pack_count"]["TRAIN"].values()) / EFFECTIVE_BATCH_SIZE)
    warmup = math.ceil(updates * 0.05)
    digest = canonical_json_sha256(
        {
            "expected_counts": counts,
            "expected_hashes": hashes,
            "total_updates": updates,
            "warmup_updates": warmup,
        }
    )
    if (
        report["candidate_total_updates"] != updates
        or report["candidate_warmup_updates"] != warmup
        or report["candidate_sha256"] != digest
    ):
        raise RuntimeError("pack oracle candidate schedule/hash 재계산 결과가 다릅니다.")
    return report


PACK_ORACLE_REVIEW_CHECKLIST = {
    "source_and_protected_hashes_verified": True,
    "deterministic_counts_and_hashes_reviewed": True,
    "semantic_pack_reread_reviewed": True,
    "pack_mask_lineage_contract_reviewed": True,
    "no_prepared_artifact_promoted": True,
    "no_precision_pilot_or_training_executed": True,
    "candidate_schedule_reviewed": True,
}


def record_pack_oracle_review(
    *,
    derivation_report_path: Path,
    receipt_path: Path,
    reviewer_id: str,
    review_note: str,
) -> dict[str, Any]:
    if (
        INVENTORY_ORACLE_STATUS != "LOCKED"
        or PACK_ORACLE_STATUS != "PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3"
    ):
        raise RuntimeError("pack oracle review는 source lock 전 PENDING 상태에서만 허용됩니다.")
    require_locked_inventory_oracle()
    _require_absent_output(receipt_path, "pack oracle review receipt")
    report = load_pack_oracle_derivation_report(derivation_report_path)
    reviewer = reviewer_id.strip()
    note = review_note.strip()
    if (
        not reviewer
        or len(reviewer) > 128
        or any(character in reviewer for character in "\r\n\0")
        or reviewer == report["derivation_actor_id"]
    ):
        raise RuntimeError("독립 pack oracle reviewer ID가 유효하지 않습니다.")
    if not note or len(note) > 2_000 or "\0" in note:
        raise RuntimeError("pack oracle review note가 유효하지 않습니다.")
    receipt = {
        "schema_version": "k-fnspid-dapt-pack-oracle-review/v1",
        "status": "APPROVED_PENDING_SOURCE_LOCK",
        "reviewed_at": datetime.now(UTC).isoformat(),
        "reviewer_id": reviewer,
        "derivation_actor_id": report["derivation_actor_id"],
        "review_note": note,
        "derivation_report": artifact_record(derivation_report_path),
        "input_artifacts": report["input_artifacts"],
        "oracle_recipe_artifacts": report["oracle_recipe_artifacts"],
        "oracle_software_fingerprint": report["oracle_software_fingerprint"],
        "candidate_expected_counts": report["candidate_expected_counts"],
        "candidate_expected_hashes": report["candidate_expected_hashes"],
        "candidate_total_updates": report["candidate_total_updates"],
        "candidate_warmup_updates": report["candidate_warmup_updates"],
        "candidate_sha256": report["candidate_sha256"],
        "review_checklist": PACK_ORACLE_REVIEW_CHECKLIST,
        "independent_review_declared": True,
    }
    _atomic_write_new(
        receipt_path,
        (json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(),
    )
    return {
        "status": "PACK_ORACLE_REVIEWED_PENDING_SOURCE_LOCK",
        "review_receipt": artifact_record(receipt_path),
        "candidate_sha256": report["candidate_sha256"],
    }


def load_pack_oracle_review_receipt(
    path: Path,
    *,
    derivation_report_path: Path,
) -> dict[str, Any]:
    receipt = read_json_object(path, "pack oracle review receipt")
    _require_exact_keys(
        receipt,
        {
            "schema_version",
            "status",
            "reviewed_at",
            "reviewer_id",
            "derivation_actor_id",
            "review_note",
            "derivation_report",
            "input_artifacts",
            "oracle_recipe_artifacts",
            "oracle_software_fingerprint",
            "candidate_expected_counts",
            "candidate_expected_hashes",
            "candidate_total_updates",
            "candidate_warmup_updates",
            "candidate_sha256",
            "review_checklist",
            "independent_review_declared",
        },
        "pack oracle review receipt",
    )
    report = load_pack_oracle_derivation_report(derivation_report_path)
    reviewer = receipt["reviewer_id"]
    note = receipt["review_note"]
    if (
        receipt["schema_version"] != "k-fnspid-dapt-pack-oracle-review/v1"
        or receipt["status"] != "APPROVED_PENDING_SOURCE_LOCK"
        or receipt["derivation_report"] != artifact_record(derivation_report_path)
        or receipt["derivation_actor_id"] != report["derivation_actor_id"]
        or not isinstance(reviewer, str)
        or not reviewer.strip()
        or reviewer == report["derivation_actor_id"]
        or not isinstance(note, str)
        or not note.strip()
        or receipt["input_artifacts"] != report["input_artifacts"]
        or receipt["oracle_recipe_artifacts"] != report["oracle_recipe_artifacts"]
        or receipt["oracle_software_fingerprint"] != report["oracle_software_fingerprint"]
        or receipt["candidate_expected_counts"] != report["candidate_expected_counts"]
        or receipt["candidate_expected_hashes"] != report["candidate_expected_hashes"]
        or receipt["candidate_total_updates"] != report["candidate_total_updates"]
        or receipt["candidate_warmup_updates"] != report["candidate_warmup_updates"]
        or receipt["candidate_sha256"] != report["candidate_sha256"]
        or receipt["review_checklist"] != PACK_ORACLE_REVIEW_CHECKLIST
        or receipt["independent_review_declared"] is not True
    ):
        raise RuntimeError("pack oracle review receipt 계약이 다릅니다.")
    _validate_utc_timestamp(receipt["reviewed_at"], "pack oracle reviewed_at")
    return receipt


def _expected_artifact_path(directory: Path, filename: str) -> str:
    resolved = (directory / filename).resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def load_prepared_manifest(directory: Path) -> dict[str, Any]:
    require_locked_pack_oracle()
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError(f"prepared DAPT directory가 없거나 symlink입니다: {directory}")
    manifest = read_json_object(directory / "manifest.json", "prepared DAPT manifest")
    if (
        manifest.get("schema_version") != "k-fnspid-dapt-prepared/v2"
        or manifest.get("status") != "PREPARED_NOT_TRAINED"
        or manifest.get("dataset_revision") != "K-FNSPID-v4"
    ):
        raise RuntimeError("prepared DAPT manifest 계약이 다릅니다.")
    artifacts = manifest.get("artifact_files")
    expected_files = {
        "train_packs": "train_packs.parquet",
        "validation_packs": "validation_packs.parquet",
        "validation_fixed_masks": "validation_fixed_masks.parquet",
        "pack_lineage": "pack_lineage.parquet",
    }
    if not isinstance(artifacts, dict) or set(artifacts) != set(expected_files):
        raise RuntimeError("prepared DAPT artifact 목록이 다릅니다.")
    for name, filename in expected_files.items():
        record = artifacts[name]
        path = directory / filename
        actual = artifact_record(path)
        if not isinstance(record, dict) or (
            record.get("path") != _expected_artifact_path(directory, filename)
            or record.get("bytes") != actual["bytes"]
            or record.get("sha256") != actual["sha256"]
        ):
            raise RuntimeError(f"prepared DAPT artifact hash가 다릅니다: {name}")
    inputs, _ = verify_source_inputs()
    if manifest.get("input_artifacts") != inputs:
        raise RuntimeError("prepared DAPT 입력 provenance가 현재 파일과 다릅니다.")
    if manifest.get("dependency_artifacts") != dependency_records():
        raise RuntimeError("prepared DAPT recipe/dependency가 현재 코드와 다릅니다.")
    inventory = manifest.get("inventory")
    packing = manifest.get("packing")
    if (
        not isinstance(inventory, dict)
        or inventory.get("eligible_total")
        != sum(cast(dict[str, int], EXPECTED["eligible_count"]).values())
        or inventory.get("eligible_component_count") != EXPECTED["eligible_component_count"]
        or inventory.get("eligible_ordered_document_ids_sha256")
        != EXPECTED_HASHES["eligible_ordered_document_ids"]
        or inventory.get("split_canonical_jsonl_sha256") != EXPECTED_HASHES["split_jsonl"]
        or inventory.get("row_assignments_sha256") != EXPECTED_HASHES["row_assignments"]
        or inventory.get("duplicate_key_zero_overlap_audit") != EXPECTED["duplicate_key_audit"]
        or inventory.get("normalized_exact_text_information_gate_sha256")
        != EXPECTED_HASHES["exact_text_gate_audit"]
        or inventory.get("component_size_audit_sha256") != EXPECTED_HASHES["component_size_audit"]
        or inventory.get("fuzzy_near_duplicate_audit_sha256")
        != EXPECTED_HASHES["fuzzy_near_duplicate_audit"]
        or manifest.get("inventory_oracle") != inventory_oracle_lock_record()
        or manifest.get("pack_oracle") != pack_oracle_lock_record()
        or not isinstance(packing, dict)
        or packing.get("pack_count") != PACK_EXPECTED["pack_count"]
        or packing.get("canonical_hashes")
        != {
            name: PACK_EXPECTED_HASHES[name]
            for name in (
                "unmasked_packed_ids",
                "pack_lineage_jsonl",
                "train_epoch0_masks",
                "validation_fixed_masks",
            )
        }
    ):
        raise RuntimeError("prepared DAPT semantic commitment가 다릅니다.")
    return manifest


def iter_packed_rows(path: Path, split: str) -> Iterator[PackedRow]:
    if split not in SPLIT_CODES:
        raise ValueError(f"지원하지 않는 split입니다: {split}")
    expected_source = "NEWS"
    expected_pack_id = 0
    for row in _iter_parquet_rows(
        path,
        (
            "source_type",
            "pack_id",
            "valid_length",
            "segment_lengths",
            "structural_mask",
            "input_ids",
        ),
    ):
        source = str(row["source_type"])
        if source not in SOURCE_CODES:
            raise RuntimeError(f"pack source_type이 잘못되었습니다: {source}")
        if source != expected_source:
            if expected_source != "NEWS" or source != "DISCLOSURE":
                raise RuntimeError("pack source canonical order가 잘못되었습니다.")
            expected_source = "DISCLOSURE"
            expected_pack_id = 0
        pack_id = int(row["pack_id"])
        valid_length = int(row["valid_length"])
        segment_lengths = tuple(int(value) for value in row["segment_lengths"])
        structural_mask = tuple(bool(value) for value in row["structural_mask"])
        input_ids = tuple(int(value) for value in row["input_ids"])
        if pack_id != expected_pack_id:
            raise RuntimeError("pack_id가 source 내에서 연속적이지 않습니다.")
        if (
            len(input_ids) != MAX_LENGTH
            or len(structural_mask) != MAX_LENGTH
            or not 2 <= valid_length <= MAX_LENGTH
            or not segment_lengths
            or any(length <= 0 for length in segment_lengths)
            or sum(segment_lengths) != valid_length - 1
            or input_ids[0] != CLS_ID
            or structural_mask[0] is not True
            or input_ids[valid_length - 1] != SEP_ID
            or any(value != PAD_ID for value in input_ids[valid_length:])
            or any(structural_mask[valid_length:])
        ):
            raise RuntimeError("packed token/padding 계약이 잘못되었습니다.")
        boundary = 1
        for length in segment_lengths:
            boundary += length
            if input_ids[boundary - 1] != SEP_ID:
                raise RuntimeError("packed document 경계가 SEP_ID로 끝나지 않습니다.")
        yield PackedRow(
            split,
            source,
            pack_id,
            valid_length,
            input_ids,
            segment_lengths,
            structural_mask,
        )
        expected_pack_id += 1


def verify_pack_semantics(
    directory: Path,
    *,
    allowed_ids: Sequence[int],
    expected_pack_count: Mapping[str, Mapping[str, int]],
    expected_document_count: Mapping[str, Mapping[str, int]],
    expected_hashes: Mapping[str, str],
) -> dict[str, Any]:
    pack_digest = sha256()
    lineage_digest = sha256()
    train_mask_digest = sha256()
    validation_mask_digest = sha256()
    counts: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    document_counts: dict[str, Counter[str]] = {
        "TRAIN": Counter(),
        "VALIDATION": Counter(),
    }
    validation_mask_rows = _iter_parquet_rows(
        directory / "validation_fixed_masks.parquet",
        (
            "source_type",
            "pack_id",
            "valid_length",
            "segment_lengths",
            "structural_mask",
            "input_ids",
            "labels",
        ),
    )
    next_validation_mask = next(validation_mask_rows, None)
    lineage_rows = _iter_parquet_rows(
        directory / "pack_lineage.parquet",
        (
            "document_id",
            "source_type",
            "split",
            "pack_id",
            "offset",
            "length",
            "segment_sha256",
        ),
    )
    next_lineage = next(lineage_rows, None)
    for split, filename in (
        ("TRAIN", "train_packs.parquet"),
        ("VALIDATION", "validation_packs.parquet"),
    ):
        for row in iter_packed_rows(directory / filename, split):
            update_pack_ids_hash(pack_digest, row)
            expected_offset = 1
            for expected_length in row.segment_lengths:
                document_counts[split][row.source_type] += 1
                if next_lineage is None:
                    raise RuntimeError("retained lineage 행이 부족합니다.")
                document_id = str(next_lineage["document_id"])
                offset = int(next_lineage["offset"])
                length = int(next_lineage["length"])
                actual_segment_hash = segment_sha256(row.input_ids[offset : offset + length])
                if (
                    str(next_lineage["source_type"]) != row.source_type
                    or str(next_lineage["split"]) != split
                    or int(next_lineage["pack_id"]) != row.pack_id
                    or offset != expected_offset
                    or length != expected_length
                    or str(next_lineage["segment_sha256"]) != actual_segment_hash
                ):
                    raise RuntimeError("retained lineage와 packed segment가 다릅니다.")
                lineage_digest.update(
                    (
                        json.dumps(
                            {
                                "document_id": document_id,
                                "source_type": row.source_type,
                                "split": split,
                                "pack_id": row.pack_id,
                                "offset": offset,
                                "length": length,
                                "segment_sha256": actual_segment_hash,
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                        + "\n"
                    ).encode()
                )
                expected_offset += length
                next_lineage = next(lineage_rows, None)
            masked, labels, _ = mask_pack(row, allowed_ids)
            target = train_mask_digest if split == "TRAIN" else validation_mask_digest
            update_mask_hash(target, row, masked, labels)
            counts[split][row.source_type] += 1
            if split == "VALIDATION":
                if next_validation_mask is None:
                    raise RuntimeError("validation fixed mask 행이 부족합니다.")
                expected_tuple = (
                    row.source_type,
                    row.pack_id,
                    row.valid_length,
                    row.segment_lengths,
                    row.structural_mask,
                    masked,
                    labels,
                )
                actual_tuple = (
                    str(next_validation_mask["source_type"]),
                    int(next_validation_mask["pack_id"]),
                    int(next_validation_mask["valid_length"]),
                    tuple(int(value) for value in next_validation_mask["segment_lengths"]),
                    tuple(bool(value) for value in next_validation_mask["structural_mask"]),
                    tuple(int(value) for value in next_validation_mask["input_ids"]),
                    tuple(int(value) for value in next_validation_mask["labels"]),
                )
                if actual_tuple != expected_tuple:
                    raise RuntimeError("validation fixed mask artifact가 재생성 결과와 다릅니다.")
                next_validation_mask = next(validation_mask_rows, None)
    if next_validation_mask is not None:
        raise RuntimeError("validation fixed mask 행이 남아 있습니다.")
    if next_lineage is not None:
        raise RuntimeError("retained lineage 행이 남아 있습니다.")
    actual_counts = {
        split: _ordered_source_counts(counts[split]) for split in ("TRAIN", "VALIDATION")
    }
    actual_document_counts = {
        split: _ordered_source_counts(document_counts[split]) for split in ("TRAIN", "VALIDATION")
    }
    hashes = {
        "unmasked_packed_ids": pack_digest.hexdigest(),
        "pack_lineage_jsonl": lineage_digest.hexdigest(),
        "train_epoch0_masks": train_mask_digest.hexdigest(),
        "validation_fixed_masks": validation_mask_digest.hexdigest(),
    }
    if (
        actual_counts != expected_pack_count
        or actual_document_counts != expected_document_count
        or any(hashes[name] != expected_hashes[name] for name in hashes)
    ):
        raise RuntimeError(
            "DAPT pack semantic verification이 실패했습니다: "
            f"packs={actual_counts}, documents={actual_document_counts}, hashes={hashes}"
        )
    return {
        "pack_count": actual_counts,
        "document_count": actual_document_counts,
        "canonical_hashes": hashes,
    }


def verify_prepared_semantics(directory: Path, tokenizer: Any) -> dict[str, Any]:
    manifest = load_prepared_manifest(directory)
    allowed_ids = verify_tokenizer_contract(tokenizer)
    verification = verify_pack_semantics(
        directory,
        allowed_ids=allowed_ids,
        expected_pack_count=PACK_EXPECTED["pack_count"],
        expected_document_count=cast(
            Mapping[str, Mapping[str, int]],
            EXPECTED["split_count"],
        ),
        expected_hashes=PACK_EXPECTED_HASHES,
    )
    return {
        "prepared_manifest": artifact_record(directory / "manifest.json"),
        **verification,
        "manifest": manifest,
    }


@dataclass(frozen=True, slots=True)
class PackStore:
    split: str
    sources: np.ndarray[Any, np.dtype[np.uint8]]
    pack_ids: np.ndarray[Any, np.dtype[np.uint32]]
    valid_lengths: np.ndarray[Any, np.dtype[np.uint16]]
    segment_lengths: tuple[tuple[int, ...], ...]
    structural_masks: np.ndarray[Any, np.dtype[np.bool_]]
    input_ids: np.ndarray[Any, np.dtype[np.uint32]]
    labels: np.ndarray[Any, np.dtype[np.int32]] | None = None

    def __len__(self) -> int:
        return int(self.input_ids.shape[0])

    def row(self, index: int) -> PackedRow:
        source_code = int(self.sources[index])
        source = "NEWS" if source_code == SOURCE_CODES["NEWS"] else "DISCLOSURE"
        return PackedRow(
            split=self.split,
            source_type=source,
            pack_id=int(self.pack_ids[index]),
            valid_length=int(self.valid_lengths[index]),
            input_ids=tuple(int(value) for value in self.input_ids[index]),
            segment_lengths=self.segment_lengths[index],
            structural_mask=tuple(bool(value) for value in self.structural_masks[index]),
        )


def load_pack_store(path: Path, split: str, *, labels: bool = False) -> PackStore:
    columns = [
        "source_type",
        "pack_id",
        "valid_length",
        "segment_lengths",
        "structural_mask",
        "input_ids",
    ]
    if labels:
        columns.append("labels")
    table = pq.read_table(path, columns=columns)
    source_values = np.asarray(
        [SOURCE_CODES[str(value)] for value in table.column("source_type").to_pylist()],
        dtype=np.uint8,
    )
    pack_ids = np.asarray(table.column("pack_id").to_numpy(), dtype=np.uint32)
    valid_lengths = np.asarray(table.column("valid_length").to_numpy(), dtype=np.uint16)
    segment_lengths = tuple(
        tuple(int(value) for value in values)
        for values in table.column("segment_lengths").to_pylist()
    )
    structural_array = table.column("structural_mask").combine_chunks()
    structural_masks = np.asarray(
        structural_array.values.to_numpy(zero_copy_only=False),
        dtype=np.bool_,
    ).reshape(-1, MAX_LENGTH)
    ids_array = table.column("input_ids").combine_chunks()
    input_ids = np.asarray(ids_array.values.to_numpy(), dtype=np.uint32).reshape(-1, MAX_LENGTH)
    label_values: np.ndarray[Any, np.dtype[np.int32]] | None = None
    if labels:
        labels_array = table.column("labels").combine_chunks()
        label_values = np.asarray(labels_array.values.to_numpy(), dtype=np.int32).reshape(
            -1,
            MAX_LENGTH,
        )
    return PackStore(
        split=split,
        sources=source_values,
        pack_ids=pack_ids,
        valid_lengths=valid_lengths,
        segment_lengths=segment_lengths,
        structural_masks=structural_masks,
        input_ids=input_ids,
        labels=label_values,
    )


def epoch_order_indices(store: PackStore) -> list[int]:
    return sorted(
        range(len(store)),
        key=lambda index: epoch_order_key(store.row(index)),
    )


def accumulation_windows(indices: Sequence[int]) -> Iterator[list[list[int]]]:
    for window_start in range(0, len(indices), EFFECTIVE_BATCH_SIZE):
        window_indices = indices[window_start : window_start + EFFECTIVE_BATCH_SIZE]
        yield [
            list(window_indices[start : start + MICRO_BATCH_SIZE])
            for start in range(0, len(window_indices), MICRO_BATCH_SIZE)
        ]


def document_block_attention_mask(row: PackedRow) -> tuple[tuple[bool, ...], ...]:
    if (
        not row.segment_lengths
        or any(length <= 0 for length in row.segment_lengths)
        or sum(row.segment_lengths) != row.valid_length - 1
    ):
        raise RuntimeError("document block 경계가 유효하지 않습니다.")
    block_ids = [-1] * MAX_LENGTH
    block_ids[0] = 0
    cursor = 1
    for block_id, length in enumerate(row.segment_lengths, start=1):
        end = cursor + length
        if end > row.valid_length or row.input_ids[end - 1] != SEP_ID:
            raise RuntimeError("document block이 SEP_ID 경계와 일치하지 않습니다.")
        block_ids[cursor:end] = [block_id] * length
        cursor = end
    if cursor != row.valid_length:
        raise RuntimeError("document block 길이 합이 valid_length와 다릅니다.")
    return tuple(tuple(left >= 0 and left == right for right in block_ids) for left in block_ids)


def build_masked_batch(
    store: PackStore,
    indices: Sequence[int],
    allowed_ids: Sequence[int],
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    masked_rows: list[tuple[int, ...]] = []
    label_rows: list[tuple[int, ...]] = []
    block_masks: list[tuple[tuple[bool, ...], ...]] = []
    for index in indices:
        row = store.row(index)
        if store.labels is None:
            masked, labels, _ = mask_pack(row, allowed_ids)
        else:
            masked = tuple(int(value) for value in store.input_ids[index])
            labels = tuple(int(value) for value in store.labels[index])
        masked_rows.append(masked)
        label_rows.append(labels)
        block_masks.append(document_block_attention_mask(row))
    input_ids = torch.tensor(masked_rows, dtype=torch.long, device=device)
    labels_tensor = torch.tensor(label_rows, dtype=torch.long, device=device)
    attention_mask = (input_ids != PAD_ID).long()
    block_attention_mask = torch.tensor(block_masks, dtype=torch.bool, device=device)
    return input_ids, attention_mask, block_attention_mask, labels_tensor


def set_training_seed() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)


def build_dapt_model(device: torch.device) -> PeftModel:
    set_training_seed()
    base = AutoModelForMaskedLM.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        local_files_only=True,
        weights_only=True,
        torch_dtype=torch.float32,
    )
    base_parameter_count = sum(parameter.numel() for parameter in base.parameters())
    if base_parameter_count != 186_012_880:
        raise RuntimeError(f"KF-DeBERTa base parameter count가 다릅니다: {base_parameter_count}")
    model = get_peft_model(
        base,
        LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            target_modules=["query_proj", "value_proj"],
            layers_to_transform=list(range(12)),
            layers_pattern="layer",
        ),
    )
    trainable = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    if trainable != 589_824:
        raise RuntimeError(f"DAPT LoRA trainable parameter count가 다릅니다: {trainable}")
    if any(
        parameter.requires_grad and "lora_" not in name
        for name, parameter in model.named_parameters()
    ):
        raise RuntimeError("LoRA 외 base/embedding/MLM head parameter가 열려 있습니다.")
    return cast(PeftModel, model.to(device))


def sparse_mlm_pack_losses(
    model: PeftModel,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    block_attention_mask: torch.Tensor,
    labels: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    base = model.get_base_model()
    encoder = getattr(base, "deberta", None)
    mlm_head = getattr(base, "cls", None)
    if encoder is None or mlm_head is None:
        raise RuntimeError("KF-DeBERTa sparse MLM 구조를 확인할 수 없습니다.")
    embeddings = getattr(encoder, "embeddings", None)
    encoder_stack = getattr(encoder, "encoder", None)
    config = getattr(encoder, "config", None)
    if (
        embeddings is None
        or encoder_stack is None
        or config is None
        or getattr(encoder_stack, "conv", None) is not None
        or getattr(encoder, "z_steps", None) != 0
        or getattr(embeddings, "position_biased_input", None) is not False
        or getattr(config, "relative_attention", None) is not True
        or list(getattr(config, "pos_att_type", ())) != ["p2c", "c2p"]
        or getattr(config, "position_biased_input", None) is not False
        or block_attention_mask.shape
        != (input_ids.shape[0], input_ids.shape[1], input_ids.shape[1])
    ):
        raise RuntimeError("KF-DeBERTa block-diagonal encoder 계약이 다릅니다.")
    embedding_output = embeddings(input_ids=input_ids, mask=attention_mask)
    hidden = encoder_stack(
        embedding_output,
        block_attention_mask,
        output_hidden_states=False,
        output_attentions=False,
        return_dict=True,
    ).last_hidden_state
    selected = labels != -100
    coordinates = selected.nonzero(as_tuple=False)
    if coordinates.numel() == 0:
        raise RuntimeError("MLM batch에 masked token이 없습니다.")
    selected_hidden = hidden[selected]
    logits = mlm_head(selected_hidden).float()
    expected = labels[selected]
    if not bool(torch.isfinite(logits).all()):
        raise FloatingPointError("sparse MLM logits에 NaN/Inf가 포함되었습니다.")
    token_losses = functional.cross_entropy(logits, expected, reduction="none")
    if not bool(torch.isfinite(token_losses).all()):
        raise FloatingPointError("sparse MLM loss에 NaN/Inf가 포함되었습니다.")
    pack_sums = torch.zeros(input_ids.shape[0], dtype=torch.float32, device=input_ids.device)
    pack_counts = torch.zeros_like(pack_sums)
    pack_sums.index_add_(0, coordinates[:, 0], token_losses)
    pack_counts.index_add_(0, coordinates[:, 0], torch.ones_like(token_losses))
    if bool((pack_counts == 0).any()):
        raise RuntimeError("MLM pack에 masked token이 없습니다.")
    return pack_sums / pack_counts, token_losses


def precision_context(device: torch.device, precision: Literal["BF16", "FP32"]) -> Any:
    if precision == "BF16":
        return torch.autocast(device_type=device.type, dtype=torch.bfloat16)
    if precision != "FP32":
        raise RuntimeError("FP16은 DAPT 실행에서 금지됩니다.")
    return nullcontext()


def selected_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def driver_allocated_memory(device: torch.device) -> int:
    if device.type == "mps" and hasattr(torch.mps, "driver_allocated_memory"):
        return int(torch.mps.driver_allocated_memory())
    if device.type == "cuda":
        return int(torch.cuda.memory_allocated(device))
    return 0


def enforce_driver_memory_limit(device: torch.device) -> int:
    allocated = driver_allocated_memory(device)
    if allocated >= DRIVER_MEMORY_LIMIT_BYTES:
        raise MemoryError("DAPT driver allocated memory가 18 GiB 한계에 도달했습니다.")
    return allocated


def evaluate_nll(
    model: PeftModel,
    store: PackStore,
    allowed_ids: Sequence[int],
    device: torch.device,
    precision: Literal["BF16", "FP32"],
    indices: Sequence[int] | None = None,
) -> dict[str, float | int]:
    selected_indices = list(range(len(store))) if indices is None else list(indices)
    model.eval()
    loss_sum = 0.0
    token_count = 0
    with torch.no_grad():
        for start in range(0, len(selected_indices), MICRO_BATCH_SIZE):
            batch_indices = selected_indices[start : start + MICRO_BATCH_SIZE]
            input_ids, attention_mask, block_attention_mask, labels = build_masked_batch(
                store,
                batch_indices,
                allowed_ids,
                device,
            )
            with precision_context(device, precision):
                _, token_losses = sparse_mlm_pack_losses(
                    model,
                    input_ids,
                    attention_mask,
                    block_attention_mask,
                    labels,
                )
            loss_sum += float(token_losses.sum().detach().cpu())
            token_count += int(token_losses.numel())
            enforce_driver_memory_limit(device)
    if token_count == 0:
        raise RuntimeError("validation masked token 수가 0입니다.")
    mean_nll = loss_sum / token_count
    if not math.isfinite(mean_nll):
        raise FloatingPointError("validation NLL이 NaN/Inf입니다.")
    return {
        "pack_count": len(selected_indices),
        "masked_token_count": token_count,
        "mean_nll": mean_nll,
        "perplexity": math.exp(min(mean_nll, 80.0)),
    }


def _encode_tensor_state(tensor: torch.Tensor) -> str:
    return base64.b64encode(tensor.detach().cpu().contiguous().numpy().tobytes()).decode("ascii")


def _rng_state_record() -> dict[str, Any]:
    numpy_state = np.random.get_state(legacy=True)
    if not isinstance(numpy_state, tuple) or len(numpy_state) != 5:
        raise RuntimeError("NumPy legacy RNG state 계약이 다릅니다.")
    record: dict[str, Any] = {
        "python": repr(random.getstate()),
        "numpy": {
            "algorithm": numpy_state[0],
            "keys": numpy_state[1].astype(np.uint32).tolist(),
            "position": int(numpy_state[2]),
            "has_gauss": int(numpy_state[3]),
            "cached_gaussian": float(numpy_state[4]),
        },
        "torch_cpu": _encode_tensor_state(torch.get_rng_state()),
        "torch_cuda": [_encode_tensor_state(value) for value in torch.cuda.get_rng_state_all()]
        if torch.cuda.is_available()
        else [],
        "torch_mps": (
            _encode_tensor_state(torch.mps.get_rng_state())
            if torch.backends.mps.is_available() and hasattr(torch.mps, "get_rng_state")
            else None
        ),
    }
    return record


def _decode_uint8_state(value: object, label: str) -> torch.Tensor:
    if not isinstance(value, str):
        raise RuntimeError(f"{label} RNG state가 문자열이 아닙니다.")
    try:
        payload = base64.b64decode(value, validate=True)
    except ValueError as exception:
        raise RuntimeError(f"{label} RNG state가 base64가 아닙니다.") from exception
    return torch.frombuffer(bytearray(payload), dtype=torch.uint8).clone()


def _restore_rng_state(record: object) -> None:
    value = _require_exact_keys(
        record,
        {"python", "numpy", "torch_cpu", "torch_cuda", "torch_mps"},
        "checkpoint RNG",
    )
    python_state = value["python"]
    if not isinstance(python_state, str):
        raise RuntimeError("Python RNG state가 문자열이 아닙니다.")
    parsed_python_state = ast.literal_eval(python_state)
    if not isinstance(parsed_python_state, tuple):
        raise RuntimeError("Python RNG state가 tuple이 아닙니다.")
    numpy_record = _require_exact_keys(
        value["numpy"],
        {"algorithm", "keys", "position", "has_gauss", "cached_gaussian"},
        "NumPy RNG",
    )
    if (
        numpy_record["algorithm"] != "MT19937"
        or not isinstance(numpy_record["keys"], list)
        or len(numpy_record["keys"]) != 624
    ):
        raise RuntimeError("NumPy RNG state 계약이 다릅니다.")
    numpy_keys = np.asarray(numpy_record["keys"], dtype=np.uint32)
    random.setstate(parsed_python_state)
    np.random.set_state(
        (
            "MT19937",
            numpy_keys,
            int(numpy_record["position"]),
            int(numpy_record["has_gauss"]),
            _finite_number(numpy_record["cached_gaussian"], "NumPy cached gaussian"),
        )
    )
    torch.set_rng_state(_decode_uint8_state(value["torch_cpu"], "Torch CPU"))
    cuda_states = value["torch_cuda"]
    if not isinstance(cuda_states, list):
        raise RuntimeError("Torch CUDA RNG state가 list가 아닙니다.")
    if torch.cuda.is_available():
        if len(cuda_states) != torch.cuda.device_count():
            raise RuntimeError("Torch CUDA RNG device 수가 다릅니다.")
        torch.cuda.set_rng_state_all(
            [_decode_uint8_state(item, "Torch CUDA") for item in cuda_states]
        )
    elif cuda_states:
        raise RuntimeError("CUDA가 없는데 checkpoint에 CUDA RNG가 있습니다.")
    mps_state = value["torch_mps"]
    if torch.backends.mps.is_available() and hasattr(torch.mps, "set_rng_state"):
        if mps_state is None:
            raise RuntimeError("MPS checkpoint RNG state가 없습니다.")
        torch.mps.set_rng_state(_decode_uint8_state(mps_state, "Torch MPS"))
    elif mps_state is not None:
        raise RuntimeError("MPS가 없는데 checkpoint에 MPS RNG가 있습니다.")


def _save_training_checkpoint(
    *,
    checkpoint_root: Path,
    model: PeftModel,
    optimizer: AdamW,
    scheduler: Any,
    context_sha256: str,
    state: dict[str, Any],
) -> dict[str, int | str]:
    update_count = int(state["update_count"])
    target = checkpoint_root / f"checkpoint-{update_count:06d}"
    temporary = _safe_temporary_directory(target)
    try:
        tensors: dict[str, torch.Tensor] = {}
        optimizer_layout: dict[str, dict[str, list[str] | dict[str, float | int]]] = {}
        named_trainable = {
            name: parameter
            for name, parameter in model.named_parameters()
            if parameter.requires_grad
        }
        for name, parameter in sorted(named_trainable.items()):
            tensors[f"model::{name}"] = parameter.detach().cpu().contiguous().clone()
            tensor_names: list[str] = []
            scalar_values: dict[str, float | int] = {}
            for state_name, state_value in optimizer.state.get(parameter, {}).items():
                if isinstance(state_value, torch.Tensor):
                    tensor_key = f"optimizer::{name}::{state_name}"
                    tensors[tensor_key] = state_value.detach().cpu().contiguous().clone()
                    tensor_names.append(state_name)
                elif isinstance(state_value, (int, float)) and not isinstance(state_value, bool):
                    scalar_values[state_name] = state_value
                else:
                    raise RuntimeError("지원하지 않는 optimizer checkpoint state입니다.")
            optimizer_layout[name] = {
                "tensor_names": sorted(tensor_names),
                "scalar_values": scalar_values,
            }
        save_safetensors(tensors, temporary / "training_state.safetensors")
        state_record = {
            "schema_version": "k-fnspid-dapt-checkpoint-state/v1",
            "context_sha256": context_sha256,
            "training": state,
            "optimizer_layout": optimizer_layout,
            "optimizer_lrs": [float(group["lr"]) for group in optimizer.param_groups],
            "scheduler": scheduler.state_dict(),
            "rng": _rng_state_record(),
        }
        (temporary / "state.json").write_text(
            json.dumps(state_record, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        artifact_files = directory_artifact_manifest(temporary)
        manifest = {
            "schema_version": "k-fnspid-dapt-checkpoint-manifest/v1",
            "status": "ATOMIC_COMPLETE",
            "update_count": update_count,
            "context_sha256": context_sha256,
            "artifact_files": artifact_files,
            "pickle_allowed": False,
            "safe_tensor_state": True,
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        check = directory_artifact_manifest(temporary)
        check.pop("manifest.json", None)
        if check != artifact_files:
            raise RuntimeError("checkpoint manifest 생성 중 파일이 변경되었습니다.")
        _fsync_tree(temporary)
        _atomic_rename_directory_new(temporary, target)
        return artifact_record(target / "manifest.json")
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def _load_training_checkpoint(
    *,
    checkpoint_path: Path,
    checkpoint_root: Path,
    model: PeftModel,
    optimizer: AdamW,
    scheduler: Any,
    context_sha256: str,
) -> dict[str, Any]:
    if checkpoint_path.parent.resolve() != checkpoint_root.resolve():
        raise RuntimeError("resume checkpoint가 지정 checkpoint root 밖에 있습니다.")
    manifest = read_json_object(checkpoint_path / "manifest.json", "DAPT checkpoint manifest")
    _require_exact_keys(
        manifest,
        {
            "schema_version",
            "status",
            "update_count",
            "context_sha256",
            "artifact_files",
            "pickle_allowed",
            "safe_tensor_state",
        },
        "DAPT checkpoint manifest",
    )
    if (
        manifest["schema_version"] != "k-fnspid-dapt-checkpoint-manifest/v1"
        or manifest["status"] != "ATOMIC_COMPLETE"
        or manifest["pickle_allowed"] is not False
        or manifest["safe_tensor_state"] is not True
        or checkpoint_path.name != f"checkpoint-{int(manifest['update_count']):06d}"
    ):
        raise RuntimeError("DAPT checkpoint manifest 계약이 다릅니다.")
    if manifest["context_sha256"] != context_sha256:
        raise RuntimeError("DAPT checkpoint context SHA-256이 다릅니다.")
    actual_files = directory_artifact_manifest(checkpoint_path)
    actual_files.pop("manifest.json", None)
    if actual_files != manifest["artifact_files"]:
        raise RuntimeError("DAPT checkpoint artifact hash가 다릅니다.")
    state_record = read_json_object(checkpoint_path / "state.json", "DAPT checkpoint state")
    _require_exact_keys(
        state_record,
        {
            "schema_version",
            "context_sha256",
            "training",
            "optimizer_layout",
            "optimizer_lrs",
            "scheduler",
            "rng",
        },
        "DAPT checkpoint state",
    )
    if (
        state_record["schema_version"] != "k-fnspid-dapt-checkpoint-state/v1"
        or state_record["context_sha256"] != context_sha256
    ):
        raise RuntimeError("DAPT checkpoint state 계약이 다릅니다.")
    tensors = load_safetensors(checkpoint_path / "training_state.safetensors", device="cpu")
    named_trainable = {
        name: parameter for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    layout = _require_exact_keys(
        state_record["optimizer_layout"],
        set(named_trainable),
        "checkpoint optimizer layout",
    )
    expected_tensor_keys: set[str] = set()
    optimizer.state.clear()
    for name, parameter in sorted(named_trainable.items()):
        model_key = f"model::{name}"
        expected_tensor_keys.add(model_key)
        value = tensors.get(model_key)
        if value is None or value.shape != parameter.shape or value.dtype != parameter.dtype:
            raise RuntimeError(f"checkpoint model tensor 계약이 다릅니다: {name}")
        parameter.data.copy_(value.to(parameter.device))
        entry = _require_exact_keys(
            layout[name],
            {"tensor_names", "scalar_values"},
            f"checkpoint optimizer layout {name}",
        )
        tensor_names = entry["tensor_names"]
        scalar_values = entry["scalar_values"]
        if not isinstance(tensor_names, list) or not isinstance(scalar_values, dict):
            raise RuntimeError("checkpoint optimizer layout 값이 잘못되었습니다.")
        parameter_state: dict[str, Any] = {}
        for state_name in tensor_names:
            if not isinstance(state_name, str):
                raise RuntimeError("optimizer tensor state 이름이 문자열이 아닙니다.")
            tensor_key = f"optimizer::{name}::{state_name}"
            expected_tensor_keys.add(tensor_key)
            if tensor_key not in tensors:
                raise RuntimeError("optimizer tensor state가 없습니다.")
            parameter_state[state_name] = tensors[tensor_key].to(parameter.device)
        for state_name, state_value in scalar_values.items():
            parameter_state[str(state_name)] = _finite_number(
                state_value,
                f"optimizer scalar {name}.{state_name}",
            )
        if parameter_state:
            optimizer.state[parameter] = parameter_state
    if set(tensors) != expected_tensor_keys:
        raise RuntimeError("checkpoint safetensors에 예상 밖 tensor가 있습니다.")
    scheduler.load_state_dict(state_record["scheduler"])
    lrs = state_record["optimizer_lrs"]
    if not isinstance(lrs, list) or len(lrs) != len(optimizer.param_groups):
        raise RuntimeError("checkpoint optimizer LR 계약이 다릅니다.")
    for group, learning_rate in zip(optimizer.param_groups, lrs, strict=True):
        group["lr"] = _finite_number(learning_rate, "checkpoint optimizer LR")
    training_state = _require_exact_keys(
        state_record["training"],
        {
            "next_window_index",
            "update_count",
            "microbatch_count",
            "pack_loss_sum",
            "pack_count",
            "consecutive_large_gradients",
            "peak_memory",
            "memory_samples",
            "last_window_microbatch_count",
            "last_window_pack_count",
        },
        "checkpoint training state",
    )
    if training_state["update_count"] != manifest["update_count"]:
        raise RuntimeError("checkpoint update_count가 manifest와 다릅니다.")
    _restore_rng_state(state_record["rng"])
    return training_state


def train_pack_indices(
    model: PeftModel,
    store: PackStore,
    indices: Sequence[int],
    allowed_ids: Sequence[int],
    device: torch.device,
    precision: Literal["BF16", "FP32"],
    checkpoint_root: Path | None = None,
    resume_checkpoint: Path | None = None,
    checkpoint_context_sha256: str | None = None,
) -> dict[str, Any]:
    if len(set(indices)) != len(indices):
        raise RuntimeError("DAPT epoch order에 중복 pack이 있습니다.")
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = AdamW(
        trainable,
        lr=LEARNING_RATE,
        betas=ADAM_BETAS,
        eps=ADAM_EPSILON,
        weight_decay=WEIGHT_DECAY,
    )
    scheduler = get_linear_schedule_with_warmup(  # type: ignore[no-untyped-call]
        optimizer,
        num_warmup_steps=WARMUP_UPDATES,
        num_training_steps=TOTAL_UPDATES,
    )
    model.train()
    if (checkpoint_root is None) != (checkpoint_context_sha256 is None):
        raise RuntimeError("checkpoint root와 context hash는 함께 지정해야 합니다.")
    if resume_checkpoint is not None and checkpoint_root is None:
        raise RuntimeError("resume checkpoint에는 checkpoint root가 필요합니다.")
    if checkpoint_context_sha256 is not None and not re.fullmatch(
        r"[0-9a-f]{64}", checkpoint_context_sha256
    ):
        raise RuntimeError("checkpoint context SHA-256이 잘못되었습니다.")
    if checkpoint_root is not None and resume_checkpoint is None and checkpoint_root.exists():
        if checkpoint_root.is_symlink() or any(checkpoint_root.iterdir()):
            raise RuntimeError("새 DAPT 실행의 checkpoint root가 비어 있지 않습니다.")
    update_count = 0
    microbatch_count = 0
    pack_loss_sum = 0.0
    pack_count = 0
    consecutive_large_gradients = 0
    peak_memory = 0
    memory_samples: list[int] = []
    last_window_microbatch_count = 0
    last_window_pack_count = 0
    next_window_index = 0
    resumed_from: dict[str, int | str] | None = None
    checkpoint_manifests: list[dict[str, int | str]] = []
    if resume_checkpoint is not None:
        if checkpoint_root is None or checkpoint_context_sha256 is None:
            raise RuntimeError("resume checkpoint context가 없습니다.")
        resumed_state = _load_training_checkpoint(
            checkpoint_path=resume_checkpoint,
            checkpoint_root=checkpoint_root,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            context_sha256=checkpoint_context_sha256,
        )
        next_window_index = int(resumed_state["next_window_index"])
        update_count = int(resumed_state["update_count"])
        microbatch_count = int(resumed_state["microbatch_count"])
        pack_loss_sum = _finite_number(resumed_state["pack_loss_sum"], "resume pack loss sum")
        pack_count = int(resumed_state["pack_count"])
        consecutive_large_gradients = int(resumed_state["consecutive_large_gradients"])
        peak_memory = int(resumed_state["peak_memory"])
        samples = resumed_state["memory_samples"]
        if not isinstance(samples, list) or not all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in samples
        ):
            raise RuntimeError("resume memory sample 계약이 다릅니다.")
        memory_samples = list(samples)
        last_window_microbatch_count = int(resumed_state["last_window_microbatch_count"])
        last_window_pack_count = int(resumed_state["last_window_pack_count"])
        if next_window_index != update_count or pack_count > len(indices):
            raise RuntimeError("resume window/update/pack count가 유효하지 않습니다.")
        resumed_from = artifact_record(resume_checkpoint / "manifest.json")
    expected_updates = math.ceil(len(indices) / EFFECTIVE_BATCH_SIZE)
    for window_index, window in enumerate(accumulation_windows(indices)):
        if window_index < next_window_index:
            continue
        total_window_packs = sum(len(batch) for batch in window)
        if total_window_packs == 0:
            continue
        optimizer.zero_grad(set_to_none=True)
        for batch_indices in window:
            input_ids, attention_mask, block_attention_mask, labels = build_masked_batch(
                store,
                batch_indices,
                allowed_ids,
                device,
            )
            with precision_context(device, precision):
                pack_losses, _ = sparse_mlm_pack_losses(
                    model,
                    input_ids,
                    attention_mask,
                    block_attention_mask,
                    labels,
                )
                # 마지막 accumulation window는 실제 pack 수로 정규화한다.
                scaled_loss = pack_losses.sum() / total_window_packs
            if not bool(torch.isfinite(scaled_loss)):
                raise FloatingPointError("DAPT train loss가 NaN/Inf입니다.")
            scaled_loss.backward()  # type: ignore[no-untyped-call]
            pack_loss_sum += float(pack_losses.detach().sum().cpu())
            pack_count += len(batch_indices)
            microbatch_count += 1
            allocated = enforce_driver_memory_limit(device)
            peak_memory = max(peak_memory, allocated)
            memory_samples.append(allocated)
        if any(
            parameter.grad is not None and not bool(torch.isfinite(parameter.grad).all())
            for parameter in trainable
        ):
            raise FloatingPointError("DAPT gradient에 NaN/Inf가 포함되었습니다.")
        grad_norm_tensor = torch.nn.utils.clip_grad_norm_(trainable, MAX_GRAD_NORM)
        grad_norm = float(grad_norm_tensor.detach().cpu())
        if not math.isfinite(grad_norm):
            raise FloatingPointError("DAPT gradient norm이 NaN/Inf입니다.")
        consecutive_large_gradients = consecutive_large_gradients + 1 if grad_norm > 100.0 else 0
        if consecutive_large_gradients >= 2:
            raise FloatingPointError("DAPT gradient norm이 2회 연속 100을 초과했습니다.")
        optimizer.step()
        scheduler.step()
        update_count += 1
        last_window_microbatch_count = len(window)
        last_window_pack_count = total_window_packs
        next_window_index = window_index + 1
        if (
            checkpoint_root is not None
            and checkpoint_context_sha256 is not None
            and (
                update_count % CHECKPOINT_INTERVAL_UPDATES == 0 or update_count == expected_updates
            )
        ):
            checkpoint_manifests.append(
                _save_training_checkpoint(
                    checkpoint_root=checkpoint_root,
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    context_sha256=checkpoint_context_sha256,
                    state={
                        "next_window_index": next_window_index,
                        "update_count": update_count,
                        "microbatch_count": microbatch_count,
                        "pack_loss_sum": pack_loss_sum,
                        "pack_count": pack_count,
                        "consecutive_large_gradients": consecutive_large_gradients,
                        "peak_memory": peak_memory,
                        "memory_samples": memory_samples,
                        "last_window_microbatch_count": last_window_microbatch_count,
                        "last_window_pack_count": last_window_pack_count,
                    },
                )
            )
    if update_count != expected_updates or pack_count != len(indices):
        raise RuntimeError("DAPT epoch에 pack 누락/반복이 발생했습니다.")
    return {
        "pack_count": pack_count,
        "microbatch_count": microbatch_count,
        "update_count": update_count,
        "mean_pack_loss": pack_loss_sum / pack_count,
        "last_window_microbatch_count": last_window_microbatch_count,
        "last_window_pack_count": last_window_pack_count,
        "peak_driver_allocated_bytes": peak_memory,
        "driver_memory_samples": memory_samples,
        "final_learning_rate": float(scheduler.get_last_lr()[0]),
        "resumed_from": resumed_from,
        "checkpoint_manifests": checkpoint_manifests,
    }


def trainable_state_sha256(model: PeftModel) -> str:
    digest = sha256()
    for name, parameter in sorted(model.named_parameters()):
        if not parameter.requires_grad:
            continue
        digest.update(name.encode())
        digest.update(b"\0")
        tensor = parameter.detach().float().cpu().contiguous().numpy()
        digest.update(tensor.tobytes(order="C"))
    return digest.hexdigest()


def hardware_fingerprint(device: torch.device) -> dict[str, Any]:
    environment = runtime_environment()
    device_index = device.index if device.index is not None else 0
    total_memory: int | None = None
    if device.type == "cuda":
        total_memory = int(torch.cuda.get_device_properties(device).total_memory)
    elif device.type == "mps" and hasattr(torch.mps, "recommended_max_memory"):
        total_memory = int(torch.mps.recommended_max_memory())
    return {
        "runtime_environment": environment,
        "device_type": device.type,
        "device_index": device_index,
        "device_name": (
            torch.cuda.get_device_name(device)
            if device.type == "cuda"
            else platform.processor() or platform.machine()
        ),
        "device_total_or_recommended_memory_bytes": total_memory,
    }


def bf16_candidate_supported(device: torch.device) -> bool:
    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1":
        return False
    if device.type == "cuda":
        return bool(torch.cuda.is_bf16_supported())
    if device.type != "mps":
        return False
    try:
        probe = torch.ones(1, device=device, dtype=torch.bfloat16)
        return probe.dtype == torch.bfloat16
    except (RuntimeError, TypeError):
        return False


def memory_slope_over_128_batches(samples: Sequence[int]) -> float:
    if len(samples) < 2:
        return 0.0
    window = np.asarray(samples[-128:], dtype=np.float64)
    x_values = np.arange(len(window), dtype=np.float64)
    slope = float(np.polyfit(x_values, window, 1)[0])
    return slope * 128.0


def run_precision_trial(
    *,
    store: PackStore,
    indices: Sequence[int],
    allowed_ids: Sequence[int],
    device: torch.device,
    precision: Literal["BF16", "FP32"],
) -> dict[str, Any]:
    model = build_dapt_model(device)
    initial_state_hash = trainable_state_sha256(model)
    initial = evaluate_nll(model, store, allowed_ids, device, precision, indices)
    training = train_pack_indices(model, store, indices, allowed_ids, device, precision)
    final = evaluate_nll(model, store, allowed_ids, device, precision, indices)
    samples = cast(list[int], training.pop("driver_memory_samples"))
    resumed_from = training.pop("resumed_from")
    checkpoint_manifests = training.pop("checkpoint_manifests")
    if resumed_from is not None or checkpoint_manifests != []:
        raise RuntimeError("precision pilot에 resume/checkpoint 기록이 포함되었습니다.")
    result = {
        "status": "PASS",
        "precision": precision,
        "initial_adapter_sha256": initial_state_hash,
        "initial_fixed_pilot": initial,
        "training": training,
        "final_fixed_pilot": final,
        "loss_reduced": float(final["mean_nll"]) < float(initial["mean_nll"]),
        "last_128_microbatch_memory_slope_bytes": memory_slope_over_128_batches(samples),
    }
    del model
    if device.type == "mps":
        torch.mps.empty_cache()
    elif device.type == "cuda":
        torch.cuda.empty_cache()
    return result


def run_precision_pilot(
    *,
    prepared_dir: Path,
    report_path: Path,
) -> dict[str, Any]:
    _require_absent_output(report_path, "DAPT precision pilot report")
    inputs, _ = verify_source_inputs()
    dependencies = dependency_records()
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        local_files_only=True,
    )
    allowed_ids = verify_tokenizer_contract(tokenizer)
    prepared_verification = verify_prepared_semantics(prepared_dir, tokenizer)
    prepared_files = prepared_snapshot(prepared_dir)
    inventory_oracle_provenance = inventory_oracle_lock_record()
    pack_oracle_provenance = pack_oracle_lock_record()
    train_store = load_pack_store(prepared_dir / "train_packs.parquet", "TRAIN")
    order = epoch_order_indices(train_store)
    pilot_indices = order[:PILOT_PACK_COUNT]
    if len(pilot_indices) != PILOT_PACK_COUNT:
        raise RuntimeError("BF16 pilot pack이 1,024개보다 적습니다.")
    device = selected_device()
    fingerprint = hardware_fingerprint(device)
    fp32 = run_precision_trial(
        store=train_store,
        indices=pilot_indices,
        allowed_ids=allowed_ids,
        device=device,
        precision="FP32",
    )
    bf16: dict[str, Any]
    if bf16_candidate_supported(device):
        try:
            bf16 = run_precision_trial(
                store=train_store,
                indices=pilot_indices,
                allowed_ids=allowed_ids,
                device=device,
                precision="BF16",
            )
        except (RuntimeError, FloatingPointError, MemoryError) as exception:
            bf16 = {
                "status": "FAIL",
                "precision": "BF16",
                "reason": f"{type(exception).__name__}: {exception}",
            }
    else:
        bf16 = {
            "status": "FAIL",
            "precision": "BF16",
            "reason": "BF16_UNSUPPORTED_OR_MPS_FALLBACK_ENABLED",
        }
    relative_difference: float | None = None
    direction_matches = False
    bf16_passed = bf16.get("status") == "PASS"
    if bf16_passed:
        fp32_final = float(fp32["final_fixed_pilot"]["mean_nll"])
        bf16_final = float(bf16["final_fixed_pilot"]["mean_nll"])
        relative_difference = abs(bf16_final - fp32_final) / max(abs(fp32_final), 1e-12)
        direction_matches = bool(bf16["loss_reduced"]) == bool(fp32["loss_reduced"])
        bf16_passed = (
            relative_difference <= 0.02
            and direction_matches
            and int(bf16["training"]["peak_driver_allocated_bytes"]) < DRIVER_MEMORY_LIMIT_BYTES
            and float(bf16["last_128_microbatch_memory_slope_bytes"]) <= 64 * 1024**2
        )
    selected_precision: Literal["BF16", "FP32"] = "BF16" if bf16_passed else "FP32"
    current_inputs, _ = verify_source_inputs()
    if (
        current_inputs != inputs
        or dependency_records() != dependencies
        or prepared_snapshot(prepared_dir) != prepared_files
        or inventory_oracle_lock_record() != inventory_oracle_provenance
        or pack_oracle_lock_record() != pack_oracle_provenance
    ):
        raise RuntimeError("DAPT pilot 중 입력/recipe가 변경되었습니다.")
    report = {
        "schema_version": "k-fnspid-dapt-precision-pilot/v2",
        "status": "PRECISION_SELECTED",
        "generated_at": datetime.now(UTC).isoformat(),
        "pilot_pack_count": PILOT_PACK_COUNT,
        "pilot_order": "canonical epoch-0 shuffle first 1024 packs",
        "seed": SEED,
        "prepared_manifest": prepared_verification["prepared_manifest"],
        "prepared_artifacts": prepared_files,
        "input_artifacts": inputs,
        "dependency_artifacts": dependencies,
        "hardware_fingerprint": fingerprint,
        "fp32": fp32,
        "bf16": bf16,
        "bf16_gate": {
            "passed": bf16_passed,
            "relative_final_nll_difference": relative_difference,
            "loss_reduction_direction_matches": direction_matches,
            "maximum_relative_nll_difference": 0.02,
            "maximum_driver_allocated_bytes": DRIVER_MEMORY_LIMIT_BYTES,
            "maximum_last_128_memory_slope_bytes": 64 * 1024**2,
            "mps_fallback_forbidden": True,
        },
        "selected_precision": selected_precision,
        "fp16_allowed": False,
        "artifact_promoted": False,
    }
    _atomic_write_new(
        report_path,
        (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode(),
    )
    return {
        "status": "PILOT_COMPLETE",
        "selected_precision": selected_precision,
        "pilot_report": artifact_record(report_path),
    }


def _require_exact_keys(value: object, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise RuntimeError(f"{label} 필드 계약이 다릅니다.")
    return cast(dict[str, Any], value)


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"{label}이 숫자가 아닙니다.")
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError(f"{label}에 NaN/Inf가 포함되었습니다.")
    return result


def _validate_nll_record(value: object, label: str, expected_pack_count: int) -> dict[str, Any]:
    record = _require_exact_keys(
        value,
        {"pack_count", "masked_token_count", "mean_nll", "perplexity"},
        label,
    )
    if (
        record["pack_count"] != expected_pack_count
        or not isinstance(record["masked_token_count"], int)
        or isinstance(record["masked_token_count"], bool)
        or record["masked_token_count"] <= 0
    ):
        raise RuntimeError(f"{label} count 계약이 다릅니다.")
    mean_nll = _finite_number(record["mean_nll"], f"{label}.mean_nll")
    perplexity = _finite_number(record["perplexity"], f"{label}.perplexity")
    expected_perplexity = math.exp(min(mean_nll, 80.0))
    if mean_nll < 0 or not math.isclose(perplexity, expected_perplexity, rel_tol=1e-12):
        raise RuntimeError(f"{label} NLL/perplexity 계약이 다릅니다.")
    return record


def _validate_passed_precision_trial(
    value: object,
    *,
    precision: Literal["BF16", "FP32"],
) -> dict[str, Any]:
    trial = _require_exact_keys(
        value,
        {
            "status",
            "precision",
            "initial_adapter_sha256",
            "initial_fixed_pilot",
            "training",
            "final_fixed_pilot",
            "loss_reduced",
            "last_128_microbatch_memory_slope_bytes",
        },
        f"{precision} pilot trial",
    )
    if trial["status"] != "PASS" or trial["precision"] != precision:
        raise RuntimeError(f"{precision} pilot status가 PASS가 아닙니다.")
    adapter_hash = trial["initial_adapter_sha256"]
    if not isinstance(adapter_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", adapter_hash):
        raise RuntimeError(f"{precision} initial adapter hash가 잘못되었습니다.")
    initial = _validate_nll_record(
        trial["initial_fixed_pilot"],
        f"{precision}.initial_fixed_pilot",
        PILOT_PACK_COUNT,
    )
    final = _validate_nll_record(
        trial["final_fixed_pilot"],
        f"{precision}.final_fixed_pilot",
        PILOT_PACK_COUNT,
    )
    if initial["masked_token_count"] != final["masked_token_count"]:
        raise RuntimeError(f"{precision} pilot fixed mask token 수가 변했습니다.")
    training = _require_exact_keys(
        trial["training"],
        {
            "pack_count",
            "microbatch_count",
            "update_count",
            "mean_pack_loss",
            "last_window_microbatch_count",
            "last_window_pack_count",
            "peak_driver_allocated_bytes",
            "final_learning_rate",
        },
        f"{precision}.training",
    )
    if (
        training["pack_count"] != PILOT_PACK_COUNT
        or training["microbatch_count"] != PILOT_PACK_COUNT // MICRO_BATCH_SIZE
        or training["update_count"] != PILOT_PACK_COUNT // EFFECTIVE_BATCH_SIZE
        or training["last_window_microbatch_count"] != ACCUMULATION_STEPS
        or training["last_window_pack_count"] != EFFECTIVE_BATCH_SIZE
        or not isinstance(training["peak_driver_allocated_bytes"], int)
        or isinstance(training["peak_driver_allocated_bytes"], bool)
        or training["peak_driver_allocated_bytes"] < 0
    ):
        raise RuntimeError(f"{precision} pilot training count 계약이 다릅니다.")
    _finite_number(training["mean_pack_loss"], f"{precision}.mean_pack_loss")
    _finite_number(training["final_learning_rate"], f"{precision}.final_learning_rate")
    slope = _finite_number(
        trial["last_128_microbatch_memory_slope_bytes"],
        f"{precision}.memory_slope",
    )
    expected_reduced = float(final["mean_nll"]) < float(initial["mean_nll"])
    if trial["loss_reduced"] is not expected_reduced:
        raise RuntimeError(f"{precision} pilot loss_reduced 계산이 다릅니다.")
    trial["last_128_microbatch_memory_slope_bytes"] = slope
    return trial


def load_pilot_report(
    path: Path,
    *,
    prepared_manifest_record: dict[str, int | str],
    prepared_artifacts: dict[str, dict[str, int | str]],
    device: torch.device,
) -> dict[str, Any]:
    report = read_json_object(path, "DAPT precision pilot report")
    expected_top_level = {
        "schema_version",
        "status",
        "generated_at",
        "pilot_pack_count",
        "pilot_order",
        "seed",
        "prepared_manifest",
        "prepared_artifacts",
        "input_artifacts",
        "dependency_artifacts",
        "hardware_fingerprint",
        "fp32",
        "bf16",
        "bf16_gate",
        "selected_precision",
        "fp16_allowed",
        "artifact_promoted",
    }
    _require_exact_keys(report, expected_top_level, "DAPT precision pilot report")
    current_inputs, _ = verify_source_inputs()
    current_dependencies = dependency_records()
    if (
        report.get("schema_version") != "k-fnspid-dapt-precision-pilot/v2"
        or report.get("status") != "PRECISION_SELECTED"
        or report.get("pilot_pack_count") != PILOT_PACK_COUNT
        or report.get("pilot_order") != "canonical epoch-0 shuffle first 1024 packs"
        or report.get("seed") != SEED
        or report.get("prepared_manifest") != prepared_manifest_record
        or report.get("prepared_artifacts") != prepared_artifacts
        or report.get("input_artifacts") != current_inputs
        or report.get("dependency_artifacts") != current_dependencies
        or report.get("selected_precision") not in {"BF16", "FP32"}
        or report.get("fp16_allowed") is not False
        or report.get("artifact_promoted") is not False
        or report.get("hardware_fingerprint") != hardware_fingerprint(device)
    ):
        raise RuntimeError("DAPT precision pilot report 계약이 다릅니다.")
    try:
        generated_at = datetime.fromisoformat(str(report["generated_at"]))
    except ValueError as exception:
        raise RuntimeError("pilot generated_at이 유효하지 않습니다.") from exception
    if generated_at.tzinfo is None or generated_at.utcoffset() != UTC.utcoffset(generated_at):
        raise RuntimeError("pilot generated_at이 UTC가 아닙니다.")
    fp32 = _validate_passed_precision_trial(report["fp32"], precision="FP32")
    if fp32["loss_reduced"] is not True:
        raise RuntimeError("FP32 pilot loss가 감소하지 않았습니다.")
    bf16_value = report["bf16"]
    bf16_passed_trial = isinstance(bf16_value, dict) and bf16_value.get("status") == "PASS"
    bf16: dict[str, Any] | None = None
    if bf16_passed_trial:
        bf16 = _validate_passed_precision_trial(bf16_value, precision="BF16")
        if bf16["initial_adapter_sha256"] != fp32["initial_adapter_sha256"]:
            raise RuntimeError("FP32/BF16 initial adapter hash가 다릅니다.")
        if (
            bf16["initial_fixed_pilot"]["masked_token_count"]
            != fp32["initial_fixed_pilot"]["masked_token_count"]
        ):
            raise RuntimeError("FP32/BF16 fixed pilot mask token 수가 다릅니다.")
    else:
        failed = _require_exact_keys(bf16_value, {"status", "precision", "reason"}, "BF16 fail")
        if (
            failed["status"] != "FAIL"
            or failed["precision"] != "BF16"
            or not isinstance(failed["reason"], str)
            or not failed["reason"].strip()
        ):
            raise RuntimeError("BF16 fail record가 잘못되었습니다.")
    gate = _require_exact_keys(
        report["bf16_gate"],
        {
            "passed",
            "relative_final_nll_difference",
            "loss_reduction_direction_matches",
            "maximum_relative_nll_difference",
            "maximum_driver_allocated_bytes",
            "maximum_last_128_memory_slope_bytes",
            "mps_fallback_forbidden",
        },
        "BF16 gate",
    )
    relative_difference: float | None = None
    direction_matches = False
    recomputed_passed = False
    if bf16 is not None:
        fp32_final = float(fp32["final_fixed_pilot"]["mean_nll"])
        bf16_final = float(bf16["final_fixed_pilot"]["mean_nll"])
        relative_difference = abs(bf16_final - fp32_final) / max(abs(fp32_final), 1e-12)
        direction_matches = bool(bf16["loss_reduced"]) == bool(fp32["loss_reduced"])
        recomputed_passed = (
            relative_difference <= 0.02
            and direction_matches
            and int(bf16["training"]["peak_driver_allocated_bytes"]) < DRIVER_MEMORY_LIMIT_BYTES
            and float(bf16["last_128_microbatch_memory_slope_bytes"]) <= 64 * 1024**2
        )
    gate_relative = gate["relative_final_nll_difference"]
    if relative_difference is None:
        relative_matches = gate_relative is None
    else:
        relative_matches = math.isclose(
            _finite_number(gate_relative, "BF16 gate relative difference"),
            relative_difference,
            rel_tol=1e-12,
        )
    if (
        gate["passed"] is not recomputed_passed
        or not relative_matches
        or gate["loss_reduction_direction_matches"] is not direction_matches
        or gate["maximum_relative_nll_difference"] != 0.02
        or gate["maximum_driver_allocated_bytes"] != DRIVER_MEMORY_LIMIT_BYTES
        or gate["maximum_last_128_memory_slope_bytes"] != 64 * 1024**2
        or gate["mps_fallback_forbidden"] is not True
        or report["selected_precision"] != ("BF16" if recomputed_passed else "FP32")
    ):
        raise RuntimeError("BF16 gate 재계산 결과가 pilot report와 다릅니다.")
    return report


def directory_artifact_manifest(directory: Path) -> dict[str, dict[str, int | str]]:
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError(f"artifact directory가 없거나 symlink입니다: {directory}")
    records: dict[str, dict[str, int | str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"artifact에 symlink가 포함되었습니다: {path}")
        if not path.is_file():
            continue
        if path.suffix.casefold() in UNSAFE_SERIALIZED_SUFFIXES:
            raise RuntimeError(f"artifact에 pickle 가능 직렬화 파일이 포함되었습니다: {path}")
        relative = path.relative_to(directory).as_posix()
        size, digest = _stable_file_measurements(path)
        records[relative] = {
            "bytes": size,
            "sha256": digest,
        }
    if not records:
        raise RuntimeError("artifact file이 없습니다.")
    return records


def prepared_snapshot(directory: Path) -> dict[str, dict[str, int | str]]:
    return {
        filename: artifact_record(directory / filename)
        for filename in (
            "manifest.json",
            "train_packs.parquet",
            "validation_packs.parquet",
            "validation_fixed_masks.parquet",
            "pack_lineage.parquet",
        )
    }


def train_dapt(
    *,
    prepared_dir: Path,
    pilot_report_path: Path,
    output_dir: Path,
    merge_fp32: bool,
    checkpoint_dir: Path,
    resume_checkpoint: Path | None,
) -> dict[str, Any]:
    _require_absent_output(output_dir, "DAPT model artifact")
    if checkpoint_dir.is_symlink():
        raise RuntimeError("DAPT checkpoint root가 symlink입니다.")
    started = time.monotonic()
    inputs, _ = verify_source_inputs()
    dependencies = dependency_records()
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        local_files_only=True,
    )
    allowed_ids = verify_tokenizer_contract(tokenizer)
    prepared_verification = verify_prepared_semantics(prepared_dir, tokenizer)
    prepared_files = prepared_snapshot(prepared_dir)
    device = selected_device()
    pilot = load_pilot_report(
        pilot_report_path,
        prepared_manifest_record=prepared_verification["prepared_manifest"],
        prepared_artifacts=prepared_files,
        device=device,
    )
    pilot_record = artifact_record(pilot_report_path)
    inventory_oracle_provenance = inventory_oracle_lock_record()
    pack_oracle_provenance = pack_oracle_lock_record()
    precision = cast(Literal["BF16", "FP32"], pilot["selected_precision"])
    if precision == "BF16" and not bf16_candidate_supported(device):
        raise RuntimeError("BF16 pilot hardware gate가 현재 runtime에서 유효하지 않습니다.")

    train_store = load_pack_store(prepared_dir / "train_packs.parquet", "TRAIN")
    validation_store = load_pack_store(
        prepared_dir / "validation_fixed_masks.parquet",
        "VALIDATION",
        labels=True,
    )
    expected_train_packs = sum(PACK_EXPECTED["pack_count"]["TRAIN"].values())
    expected_validation_packs = sum(PACK_EXPECTED["pack_count"]["VALIDATION"].values())
    if len(train_store) != expected_train_packs or len(validation_store) != (
        expected_validation_packs
    ):
        raise RuntimeError("DAPT pack count가 고정 계약과 다릅니다.")
    order = epoch_order_indices(train_store)
    order_digest = sha256()
    for index in order:
        order_digest.update(train_store.row(index).identity)
    checkpoint_context = {
        "schema_version": "k-fnspid-dapt-checkpoint-context/v1",
        "inputs": inputs,
        "dependencies": dependencies,
        "prepared_files": prepared_files,
        "pilot_report": pilot_record,
        "inventory_oracle": inventory_oracle_provenance,
        "pack_oracle": pack_oracle_provenance,
        "precision": precision,
        "epoch_order_sha256": order_digest.hexdigest(),
        "seed": SEED,
        "total_updates": TOTAL_UPDATES,
        "warmup_updates": WARMUP_UPDATES,
        "micro_batch_size": MICRO_BATCH_SIZE,
        "effective_batch_size": EFFECTIVE_BATCH_SIZE,
    }
    checkpoint_context_sha256 = canonical_json_sha256(checkpoint_context)
    model = build_dapt_model(device)
    initial_adapter_hash = trainable_state_sha256(model)
    frozen_validation = evaluate_nll(
        model,
        validation_store,
        allowed_ids,
        device,
        precision,
    )
    training = train_pack_indices(
        model,
        train_store,
        order,
        allowed_ids,
        device,
        precision,
        checkpoint_root=checkpoint_dir,
        resume_checkpoint=resume_checkpoint,
        checkpoint_context_sha256=checkpoint_context_sha256,
    )
    expected_last_pack_count = len(train_store) % EFFECTIVE_BATCH_SIZE or EFFECTIVE_BATCH_SIZE
    expected_last_microbatch_count = math.ceil(expected_last_pack_count / MICRO_BATCH_SIZE)
    if (
        training["update_count"] != TOTAL_UPDATES
        or training["last_window_microbatch_count"] != expected_last_microbatch_count
        or training["last_window_pack_count"] != expected_last_pack_count
    ):
        raise RuntimeError("DAPT update/last accumulation 계약이 다릅니다.")
    final_validation = evaluate_nll(
        model,
        validation_store,
        allowed_ids,
        device,
        precision,
    )
    if float(final_validation["mean_nll"]) >= float(frozen_validation["mean_nll"]):
        raise RuntimeError("DAPT 종료 validation NLL이 frozen-base step-0 NLL보다 낮지 않습니다.")

    current_inputs, _ = verify_source_inputs()
    if (
        current_inputs != inputs
        or dependency_records() != dependencies
        or prepared_snapshot(prepared_dir) != prepared_files
        or artifact_record(pilot_report_path) != pilot_record
        or inventory_oracle_lock_record() != inventory_oracle_provenance
        or pack_oracle_lock_record() != pack_oracle_provenance
    ):
        raise RuntimeError("DAPT train 중 입력/recipe/pilot이 변경되었습니다.")

    temporary = _safe_temporary_directory(output_dir)
    try:
        adapter_dir = temporary / "adapter"
        model.save_pretrained(str(adapter_dir), safe_serialization=True)
        if not (adapter_dir / "adapter_model.safetensors").is_file() or any(
            path.suffix == ".bin" for path in adapter_dir.rglob("*")
        ):
            raise RuntimeError("DAPT adapter가 safetensors로 저장되지 않았습니다.")
        merged_path: str | None = None
        if merge_fp32:
            merged_dir = temporary / "merged_fp32"
            model = model.to("cpu").float()
            merged = model.merge_and_unload(safe_merge=True)
            if any(parameter.dtype != torch.float32 for parameter in merged.parameters()):
                raise RuntimeError("merged DAPT base에 FP32가 아닌 parameter가 있습니다.")
            merged.save_pretrained(merged_dir, safe_serialization=True, max_shard_size="5GB")
            if not list(merged_dir.glob("*.safetensors")) or any(
                path.suffix == ".bin" for path in merged_dir.rglob("*")
            ):
                raise RuntimeError("merged FP32 base가 safetensors로 저장되지 않았습니다.")
            merged_path = "merged_fp32"
        bundled_oracle_provenance = bundle_locked_oracle_provenance(
            temporary,
            inventory_lock=inventory_oracle_provenance,
            pack_lock=pack_oracle_provenance,
        )
        report = {
            "schema_version": "k-fnspid-kf-deberta-dapt-training/v2",
            "status": "TRAINED_PENDING_ATOMIC_MANIFEST",
            "trained_at": datetime.now(UTC).isoformat(),
            "dataset_revision": "K-FNSPID-v4",
            "base_model": BASE_MODEL,
            "base_revision": BASE_REVISION,
            "seed": SEED,
            "precision": precision,
            "public_test_opened": False,
            "confirmatory_sentiment_labels_opened": False,
            "model_recipe": {
                "objective": "sparse masked language modeling",
                "base_frozen": True,
                "embedding_frozen": True,
                "mlm_head_frozen": True,
                "lora_layers": list(range(12)),
                "lora_target_modules": ["query_proj", "value_proj"],
                "lora_rank": 16,
                "lora_alpha": 32,
                "lora_dropout": 0.05,
                "trainable_parameter_count": 589_824,
                "base_parameter_count": 186_012_880,
                "initial_adapter_sha256": initial_adapter_hash,
                "packed_document_attention": ("document-block-diagonal-with-singleton-cls"),
                "cross_document_attention_allowed": False,
            },
            "optimizer": {
                "name": "AdamW",
                "learning_rate": LEARNING_RATE,
                "betas": list(ADAM_BETAS),
                "epsilon": ADAM_EPSILON,
                "weight_decay": WEIGHT_DECAY,
                "gradient_clip_norm": MAX_GRAD_NORM,
                "warmup_updates": WARMUP_UPDATES,
                "total_updates": TOTAL_UPDATES,
                "schedule": "linear_warmup_then_linear_decay_to_zero",
            },
            "batching": {
                "micro_batch_size": MICRO_BATCH_SIZE,
                "gradient_accumulation_steps": ACCUMULATION_STEPS,
                "effective_batch_size": EFFECTIVE_BATCH_SIZE,
                "last_window_microbatch_count": expected_last_microbatch_count,
                "last_window_pack_count": expected_last_pack_count,
                "last_window_actual_size_normalization": True,
                "drop_last": False,
                "repeat_last": False,
                "checkpoint_interval_updates": CHECKPOINT_INTERVAL_UPDATES,
                "checkpoint_context_sha256": checkpoint_context_sha256,
                "resume_checkpoint": str(resume_checkpoint) if resume_checkpoint else None,
            },
            "epochs": 1,
            "early_stopping": False,
            "gradient_checkpointing": False,
            "validation": {
                "evaluation_points": ["STEP_0_FROZEN_BASE", "END_OF_EPOCH"],
                "fixed_masks": True,
                "frozen_base": frozen_validation,
                "end_of_epoch": final_validation,
                "nll_improved": True,
            },
            "training": training,
            "prepared_manifest": prepared_verification["prepared_manifest"],
            "prepared_artifacts": prepared_files,
            "pilot_report": pilot_record,
            "inventory_oracle": inventory_oracle_provenance,
            "pack_oracle": pack_oracle_provenance,
            "bundled_oracle_provenance": bundled_oracle_provenance,
            "merged_fp32": merged_path,
            "runtime_environment": runtime_environment(),
            "elapsed_seconds": time.monotonic() - started,
            "claim_limitations": [
                (
                    "DAPT의 supervised downstream 성능 개선은 no-DAPT 3-seed paired "
                    "평가 전까지 알 수 없다."
                ),
                "현재 supervised v5는 2026년 4~7월 자료를 포함하므로 OOT 근거가 아니다.",
                "DAPT는 단일 seed로 수행되어 pretraining seed 불확실성을 추정하지 못한다.",
            ],
        }
        report_path = temporary / "training_report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        artifact_files = directory_artifact_manifest(temporary)
        merged_artifact_files = {
            name: record
            for name, record in artifact_files.items()
            if name.startswith("merged_fp32/")
        }
        manifest = {
            "schema_version": "k-fnspid-kf-deberta-dapt-artifact-manifest/v2",
            "status": "ATOMIC_COMPLETE",
            "generated_at": datetime.now(UTC).isoformat(),
            "input_artifacts": inputs,
            "prepared_manifest": prepared_verification["prepared_manifest"],
            "prepared_artifacts": prepared_files,
            "pilot_report": pilot_record,
            "dependency_artifacts": dependencies,
            "hardware": runtime_environment(),
            "base_model_provenance": {
                "repository": BASE_MODEL,
                "revision": BASE_REVISION,
                "file_hashes": BASE_FILE_HASHES,
                "weights_only": True,
                "trust_remote_code": False,
            },
            "corpus_commitments": EXPECTED_HASHES,
            "inventory_oracle": inventory_oracle_provenance,
            "pack_commitments": pack_oracle_provenance,
            "bundled_oracle_provenance": bundled_oracle_provenance,
            "artifact_files": artifact_files,
            "adapter_safe_serialization": True,
            "merged_fp32_included": merge_fp32,
            "merged_fp32": {
                "included": merge_fp32,
                "path": "merged_fp32" if merge_fp32 else None,
                "artifact_files": merged_artifact_files,
            },
            "overwrite_allowed": False,
            "symlinks_allowed": False,
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        post_manifest_files = directory_artifact_manifest(temporary)
        post_manifest_files.pop("manifest.json", None)
        if post_manifest_files != artifact_files:
            raise RuntimeError("manifest 생성 중 DAPT artifact가 변경되었습니다.")
        _fsync_tree(temporary)
        _atomic_rename_directory_new(temporary, output_dir)
        published_files = directory_artifact_manifest(output_dir)
        published_files.pop("manifest.json", None)
        if published_files != artifact_files:
            raise RuntimeError("publish 후 DAPT artifact hash가 manifest와 다릅니다.")
        return {
            "status": "TRAINED",
            "precision": precision,
            "artifact_manifest": artifact_record(output_dir / "manifest.json"),
            "validation": report["validation"],
        }
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def validate_read_only() -> dict[str, Any]:
    inputs, _ = verify_source_inputs()
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        local_files_only=True,
    )
    allowed_ids = verify_tokenizer_contract(tokenizer)
    inventory = compute_corpus_inventory(enforce_expected=True)
    return {
        "status": "VALIDATED_READ_ONLY_WITHOUT_PREPARE_OR_TRAINING",
        "schema_version": "k-fnspid-dapt-validation/v2",
        "input_artifacts": inputs,
        "dependency_artifacts": dependency_records(),
        "inventory": inventory_record(inventory),
        "tokenizer_contract": {
            "vocab_size": VOCAB_SIZE,
            "special_ids": sorted(SPECIAL_IDS),
            "marker_ids": sorted(MARKER_IDS),
            "allowed_random_token_count": len(allowed_ids),
            "allowed_random_token_ids_sha256": EXPECTED_HASHES["allowed_random_token_ids"],
        },
        "model_recipe": {
            "base_frozen": True,
            "lora_layers": list(range(12)),
            "lora_target_modules": ["query_proj", "value_proj"],
            "lora_rank": 16,
            "lora_alpha": 32,
            "lora_dropout": 0.05,
            "trainable_parameter_count": 589_824,
            "packed_document_attention": "document-block-diagonal-with-singleton-cls",
            "cross_document_attention_allowed": False,
        },
        "training_recipe": {
            "seed": SEED,
            "epochs": 1,
            "micro_batch_size": MICRO_BATCH_SIZE,
            "gradient_accumulation_steps": ACCUMULATION_STEPS,
            "effective_batch_size": EFFECTIVE_BATCH_SIZE,
            "total_updates": TOTAL_UPDATES,
            "warmup_updates": WARMUP_UPDATES,
            "optimizer": "AdamW",
            "learning_rate": LEARNING_RATE,
            "betas": list(ADAM_BETAS),
            "epsilon": ADAM_EPSILON,
            "weight_decay": WEIGHT_DECAY,
            "fp16_allowed": False,
            "safe_checkpoint_interval_updates": CHECKPOINT_INTERVAL_UPDATES,
            "checkpoint_pickle_allowed": False,
        },
        "inventory_commitments": EXPECTED_HASHES,
        "pack_oracle": {
            "status": PACK_ORACLE_STATUS,
            "expected_counts": PACK_EXPECTED,
            "expected_hashes": PACK_EXPECTED_HASHES,
            "prepare_pilot_train_allowed": PACK_ORACLE_STATUS == "LOCKED",
        },
        "public_test_opened": False,
        "confirmatory_sentiment_labels_opened": False,
        "runtime_environment": runtime_environment(),
        "claim_limitations": [
            "DAPT downstream 성능 개선은 아직 알 수 없다.",
            "현재 supervised v5는 out-of-time 실험이 아니다.",
            "DAPT는 단일 seed로 설계되었다.",
        ],
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="K-FNSPID v4 strict temporal corpus로 KF-DeBERTa DAPT를 준비하고 학습한다."
    )
    action = value.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--derive-inventory-oracle", action="store_true")
    action.add_argument("--record-inventory-oracle-review", action="store_true")
    action.add_argument("--derive-pack-oracle", action="store_true")
    action.add_argument("--record-pack-oracle-review", action="store_true")
    action.add_argument("--prepare-only", action="store_true")
    action.add_argument("--pilot-packs", action="store_true")
    action.add_argument("--train", action="store_true")
    value.add_argument("--prepared-dir", type=Path, default=DEFAULT_PREPARED_DIR)
    value.add_argument("--pilot-report", type=Path, default=DEFAULT_PILOT_REPORT)
    value.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    value.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    value.add_argument("--resume-checkpoint", type=Path)
    value.add_argument("--merge-fp32", action="store_true")
    value.add_argument(
        "--inventory-oracle-report",
        type=Path,
        default=DEFAULT_INVENTORY_ORACLE_DERIVATION_REPORT,
    )
    value.add_argument(
        "--inventory-oracle-review-receipt",
        type=Path,
        default=DEFAULT_INVENTORY_ORACLE_REVIEW_RECEIPT,
    )
    value.add_argument(
        "--pack-oracle-report",
        type=Path,
        default=DEFAULT_PACK_ORACLE_DERIVATION_REPORT,
    )
    value.add_argument(
        "--pack-oracle-review-receipt",
        type=Path,
        default=DEFAULT_PACK_ORACLE_REVIEW_RECEIPT,
    )
    value.add_argument(
        "--pack-oracle-scratch-dir",
        type=Path,
        default=DEFAULT_PACK_ORACLE_SCRATCH_DIR,
    )
    value.add_argument("--actor-id", default="")
    value.add_argument("--reviewer-id", default="")
    value.add_argument("--review-note", default="")
    return value


def main() -> None:
    args = parser().parse_args()
    if args.merge_fp32 and not args.train:
        raise SystemExit("--merge-fp32는 --train과만 사용할 수 있습니다.")
    if args.resume_checkpoint is not None and not args.train:
        raise SystemExit("--resume-checkpoint는 --train과만 사용할 수 있습니다.")
    if args.derive_inventory_oracle:
        result = derive_inventory_oracle(
            report_path=args.inventory_oracle_report,
            actor_id=args.actor_id,
        )
    elif args.record_inventory_oracle_review:
        result = record_inventory_oracle_review(
            derivation_report_path=args.inventory_oracle_report,
            receipt_path=args.inventory_oracle_review_receipt,
            reviewer_id=args.reviewer_id,
            review_note=args.review_note,
        )
    elif args.derive_pack_oracle:
        result = derive_pack_oracle(
            report_path=args.pack_oracle_report,
            scratch_dir=args.pack_oracle_scratch_dir,
            actor_id=args.actor_id,
        )
    elif args.record_pack_oracle_review:
        result = record_pack_oracle_review(
            derivation_report_path=args.pack_oracle_report,
            receipt_path=args.pack_oracle_review_receipt,
            reviewer_id=args.reviewer_id,
            review_note=args.review_note,
        )
    elif args.validate_only:
        result = validate_read_only()
    elif args.prepare_only:
        result = prepare_corpus(args.prepared_dir)
    elif args.pilot_packs:
        result = run_precision_pilot(
            prepared_dir=args.prepared_dir,
            report_path=args.pilot_report,
        )
    else:
        result = train_dapt(
            prepared_dir=args.prepared_dir,
            pilot_report_path=args.pilot_report,
            output_dir=args.output_dir,
            merge_fp32=args.merge_fp32,
            checkpoint_dir=args.checkpoint_dir,
            resume_checkpoint=args.resume_checkpoint,
        )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
