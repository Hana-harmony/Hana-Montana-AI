from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.dataset import resolve_jsonl_paths
from hannah_montana_ai.training.sentiment_protocol import (
    LABEL_ORDER,
    ProvenanceGroupKey,
    assert_sentiment_groups_disjoint,
    sentiment_provenance,
)
from hannah_montana_ai.training.sentiment_sampling import (
    DISCLOSURE_ADVERSE_AUXILIARY,
)

from build_k_fnspid_sentiment_dataset import (  # isort: skip
    CODEBOOK_VERSION,
    DEFAULT_DATASET_DIR,
    DEFAULT_OUTPUT_DIR,
    PROJECT_ROOT,
    Candidate,
    _review_payload,
    _sha256,
    _stable_digest,
    load_candidates,
)

FRAME_START = "2026-04-01"
FRAME_END = "2026-12-31"
SAMPLE_PER_STRATUM = 200
SAMPLING_SEED = "k-fnspid-prevalence-sealed-v1:2026-07-15"
WEAK_STRATUM_VERSION = "k-fnspid-prevalence-weak-stratum/v1"
NEWS_PARTITION = "PREVALENCE_SEALED_TEST_REVIEW"
DISCLOSURE_PARTITION = "DISCLOSURE_PREVALENCE_SEALED_TEST_REVIEW"
DEFAULT_NEWS_OUTPUT_PATH = DEFAULT_OUTPUT_DIR / "prevalence_sealed_test_review.jsonl"
DEFAULT_DISCLOSURE_OUTPUT_PATH = (
    DEFAULT_OUTPUT_DIR / "disclosure_prevalence_sealed_test_review.jsonl"
)
DEFAULT_REPORT_PATH = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-prevalence-sealed-sampling-design.json"
)
EXISTING_REVIEW_PATHS = (
    DEFAULT_OUTPUT_DIR / "train_review.jsonl",
    DEFAULT_OUTPUT_DIR / "development_review.jsonl",
    DEFAULT_OUTPUT_DIR / "sealed_test_review.jsonl",
    DEFAULT_OUTPUT_DIR / "disclosure_development_review.jsonl",
    DEFAULT_OUTPUT_DIR / "disclosure_sealed_test_review.jsonl",
)
SILVER_PATHS = (
    PROJECT_ROOT / "data/training/k_fnspid_sentiment_silver.jsonl",
    PROJECT_ROOT / "data/training/k_fnspid_disclosure_sentiment_silver.jsonl",
)


@dataclass(frozen=True, slots=True)
class IdentityCollection:
    paths: tuple[Path, ...]
    rows: tuple[dict[str, str], ...]
    group_keys: frozenset[ProvenanceGroupKey]
    row_count: int
    rows_without_identity: int


@dataclass(frozen=True, slots=True)
class SamplingUnit:
    component_id: int
    candidate: Candidate
    sampling_stratum: str
    identity_sha256: str


@dataclass(frozen=True, slots=True)
class SamplingDesign:
    frames: dict[str, dict[str, tuple[SamplingUnit, ...]]]
    selected: dict[str, dict[str, tuple[SamplingUnit, ...]]]
    component_audit: dict[str, int]


class _DisjointSet:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-FNSPID 감성 prevalence 추정용 신규 sealed 확률표본을 생성한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--news-output-path", type=Path, default=DEFAULT_NEWS_OUTPUT_PATH)
    parser.add_argument(
        "--disclosure-output-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_OUTPUT_PATH,
    )
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    output_paths = (
        args.news_output_path,
        args.disclosure_output_path,
        args.report_path,
    )
    _preflight_new_outputs(output_paths)

    protected = load_protected_identity_collections()
    combined_protected_keys = frozenset(
        key for collection in protected.values() for key in collection.group_keys
    )
    candidates, source_audit = load_candidates(
        args.dataset_dir,
        [],
        source_types={"NEWS", "DISCLOSURE"},
    )
    design = build_sampling_design(
        candidates,
        combined_protected_keys,
        seed=SAMPLING_SEED,
        sample_per_stratum=SAMPLE_PER_STRATUM,
    )

    news_units = _flatten_selected(design.selected["NEWS"])
    disclosure_units = _flatten_selected(design.selected["DISCLOSURE"])
    news_payloads = [_review_payload(unit.candidate, NEWS_PARTITION) for unit in news_units]
    disclosure_payloads = [
        _review_payload(unit.candidate, DISCLOSURE_PARTITION) for unit in disclosure_units
    ]
    protected_rows = [row for collection in protected.values() for row in collection.rows]
    assert_sentiment_groups_disjoint(
        {
            NEWS_PARTITION: [unit.candidate.group_row() for unit in news_units],
            DISCLOSURE_PARTITION: [unit.candidate.group_row() for unit in disclosure_units],
            "ALL_EXISTING_PROTECTED_IDENTITIES": protected_rows,
        }
    )

    _write_new_jsonl(args.news_output_path, news_payloads)
    _write_new_jsonl(args.disclosure_output_path, disclosure_payloads)
    report = build_sampling_report(
        design=design,
        protected=protected,
        source_audit=source_audit,
        news_output_path=args.news_output_path,
        disclosure_output_path=args.disclosure_output_path,
    )
    _write_new_json(args.report_path, report)
    print(json.dumps(report, ensure_ascii=False))


def load_protected_identity_collections() -> dict[str, IdentityCollection]:
    training_paths = tuple(
        path
        for path in sorted((PROJECT_ROOT / "data/training").glob("*.jsonl"))
        if path not in SILVER_PATHS
    )
    evaluation_paths = tuple(sorted((PROJECT_ROOT / "data/evaluation").glob("*.jsonl")))
    categories = {
        "existing_review_packets": EXISTING_REVIEW_PATHS,
        "k_fnspid_silver_sets": SILVER_PATHS,
        "other_training_sets": training_paths,
        "evaluation_sets": evaluation_paths,
    }
    return {category: _load_identity_collection(paths) for category, paths in categories.items()}


def _load_identity_collection(paths: tuple[Path, ...]) -> IdentityCollection:
    rows: list[dict[str, str]] = []
    group_keys: set[ProvenanceGroupKey] = set()
    rows_without_identity = 0
    resolved_input_paths: list[Path] = []
    for path in paths:
        if path.is_symlink():
            raise ValueError(f"보호 JSONL symlink는 허용하지 않습니다: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"보호 JSONL이 없습니다: {path}")
        resolved_paths = resolve_jsonl_paths(path)
        resolved_input_paths.append(path)
        resolved_input_paths.extend(
            resolved_path for resolved_path in resolved_paths if resolved_path != path
        )
        for resolved_path in resolved_paths:
            with resolved_path.open(encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if not line.strip():
                        continue
                    payload = json.loads(line)
                    if not isinstance(payload, dict):
                        raise ValueError(
                            f"보호 JSONL 행은 객체여야 합니다: {resolved_path}:{line_number}"
                        )
                    row = _identity_row(payload)
                    keys = sentiment_provenance(row).group_keys
                    if not keys:
                        rows_without_identity += 1
                        continue
                    rows.append(row)
                    group_keys.update(keys)
    return IdentityCollection(
        paths=tuple(dict.fromkeys(resolved_input_paths)),
        rows=tuple(rows),
        group_keys=frozenset(group_keys),
        row_count=len(rows),
        rows_without_identity=rows_without_identity,
    )


def _identity_row(payload: dict[str, Any]) -> dict[str, str]:
    source_record = payload.get("source_record")
    if isinstance(source_record, dict):
        payload = source_record
    text = str(payload.get("text") or "").strip()
    if not text:
        title = str(payload.get("title") or "").strip()
        snippet = str(payload.get("snippet") or "").strip()
        full_content = str(payload.get("full_content") or payload.get("content") or "").strip()
        text = " ".join(part for part in (title, snippet, full_content) if part)
    return {
        "text": text,
        "source_url": str(payload.get("source_url") or payload.get("original_url") or ""),
        "content_hash": str(payload.get("content_hash") or ""),
        "event_cluster_id": str(payload.get("event_cluster_id") or ""),
    }


def build_sampling_design(
    candidates: list[Candidate],
    protected_group_keys: frozenset[ProvenanceGroupKey],
    *,
    seed: str,
    sample_per_stratum: int,
    frame_start: str = FRAME_START,
    frame_end: str = FRAME_END,
    news_partition: str = NEWS_PARTITION,
    disclosure_partition: str = DISCLOSURE_PARTITION,
) -> SamplingDesign:
    if not seed:
        raise ValueError("표본 추출 seed는 빈 수 없습니다.")
    if sample_per_stratum <= 0:
        raise ValueError("층별 표본 수는 양수여야 합니다.")
    if not frame_start or not frame_end or frame_start > frame_end:
        raise ValueError("표본 프레임 기간이 올바르지 않습니다.")
    if not news_partition or not disclosure_partition or news_partition == disclosure_partition:
        raise ValueError("출처별 partition 이름은 비어 있지 않고 서로 달라야 합니다.")
    frame_candidates = [
        candidate
        for candidate in candidates
        if candidate.source_type in {"NEWS", "DISCLOSURE"}
        and frame_start <= candidate.effective_trade_date <= frame_end
    ]
    dsu = _DisjointSet(len(frame_candidates))
    protected_key_digests = {_group_key_digest(key) for key in protected_group_keys}
    key_owner: dict[bytes, int] = {}
    identity_digests: list[tuple[bytes, ...]] = []
    for index, candidate in enumerate(frame_candidates):
        keys = tuple(
            sorted(
                _group_key_digest(key)
                for key in sentiment_provenance(candidate.group_row()).group_keys
            )
        )
        if not keys:
            raise ValueError(f"후보 provenance가 비어 있습니다: {candidate.document_id}")
        identity_digests.append(keys)
        for key in keys:
            previous_owner = key_owner.setdefault(key, index)
            dsu.union(index, previous_owner)

    protected_components: set[int] = set()
    component_sizes: Counter[int] = Counter()
    for index, keys in enumerate(identity_digests):
        root = dsu.find(index)
        component_sizes[root] += 1
        if any(key in protected_key_digests for key in keys):
            protected_components.add(root)

    representative_indices: dict[tuple[int, str], int] = {}
    for index, candidate in enumerate(frame_candidates):
        root = dsu.find(index)
        if root in protected_components:
            continue
        representative_key = (root, candidate.source_type)
        previous_index = representative_indices.get(representative_key)
        if previous_index is None or _candidate_identity_order(
            candidate
        ) < _candidate_identity_order(frame_candidates[previous_index]):
            representative_indices[representative_key] = index

    source_units: dict[str, list[SamplingUnit]] = {"NEWS": [], "DISCLOSURE": []}
    for (component_id, source_type), index in representative_indices.items():
        candidate = frame_candidates[index]
        source_units[source_type].append(
            SamplingUnit(
                component_id=component_id,
                candidate=candidate,
                sampling_stratum=_prevalence_sampling_stratum(candidate),
                identity_sha256=_candidate_identity_digest(candidate),
            )
        )

    news_frames = _stratify_units(source_units["NEWS"])
    news_selected = _select_equal_probability_units(
        news_frames,
        seed=f"{seed}:{news_partition}",
        sample_per_stratum=sample_per_stratum,
    )
    selected_news_components = {
        unit.component_id for units in news_selected.values() for unit in units
    }
    disclosure_units = [
        unit
        for unit in source_units["DISCLOSURE"]
        if unit.component_id not in selected_news_components
    ]
    disclosure_frames = _stratify_units(disclosure_units)
    disclosure_selected = _select_equal_probability_units(
        disclosure_frames,
        seed=f"{seed}:{disclosure_partition}",
        sample_per_stratum=sample_per_stratum,
    )

    frames = {"NEWS": news_frames, "DISCLOSURE": disclosure_frames}
    selected = {"NEWS": news_selected, "DISCLOSURE": disclosure_selected}
    _assert_design_disjoint(
        selected,
        protected_group_keys,
        news_partition=news_partition,
        disclosure_partition=disclosure_partition,
    )
    return SamplingDesign(
        frames=frames,
        selected=selected,
        component_audit={
            "input_candidate_count": len(candidates),
            "date_source_frame_document_count": len(frame_candidates),
            "date_source_frame_component_count": len(component_sizes),
            "protected_component_count": len(protected_components),
            "protected_component_document_count": sum(
                component_sizes[root] for root in protected_components
            ),
            "canonical_news_sampling_unit_count": len(source_units["NEWS"]),
            "canonical_disclosure_sampling_unit_count_before_cross_source_exclusion": len(
                source_units["DISCLOSURE"]
            ),
            "disclosure_unit_count_excluded_by_news_selection": len(source_units["DISCLOSURE"])
            - len(disclosure_units),
            "canonical_disclosure_sampling_unit_count": len(disclosure_units),
        },
    )


def _stratify_units(
    units: list[SamplingUnit],
) -> dict[str, tuple[SamplingUnit, ...]]:
    return {
        label: tuple(
            sorted(
                (unit for unit in units if unit.sampling_stratum == label),
                key=lambda unit: (
                    unit.candidate.document_id,
                    unit.identity_sha256,
                ),
            )
        )
        for label in LABEL_ORDER
    }


def _prevalence_sampling_stratum(candidate: Candidate) -> str:
    base_stratum = candidate.sampling_stratum
    if (
        candidate.source_type == "DISCLOSURE"
        and base_stratum == "NEUTRAL"
        and DISCLOSURE_ADVERSE_AUXILIARY.search(candidate.text)
    ):
        return "NEGATIVE"
    return base_stratum


def _select_equal_probability_units(
    frames: dict[str, tuple[SamplingUnit, ...]],
    *,
    seed: str,
    sample_per_stratum: int,
) -> dict[str, tuple[SamplingUnit, ...]]:
    selected: dict[str, tuple[SamplingUnit, ...]] = {}
    for label in LABEL_ORDER:
        frame = frames[label]
        if len(frame) < sample_per_stratum:
            raise RuntimeError(f"{label} prevalence 표본 부족: {len(frame)}/{sample_per_stratum}")
        ranked = sorted(
            frame,
            key=lambda unit: (
                _stable_digest(
                    unit.candidate.document_id,
                    f"{seed}:{label}",
                ),
                unit.identity_sha256,
            ),
        )
        selected[label] = tuple(ranked[:sample_per_stratum])
    return selected


def _assert_design_disjoint(
    selected: dict[str, dict[str, tuple[SamplingUnit, ...]]],
    protected_group_keys: frozenset[ProvenanceGroupKey],
    *,
    news_partition: str = NEWS_PARTITION,
    disclosure_partition: str = DISCLOSURE_PARTITION,
) -> None:
    news_rows = [
        unit.candidate.group_row() for units in selected["NEWS"].values() for unit in units
    ]
    disclosure_rows = [
        unit.candidate.group_row() for units in selected["DISCLOSURE"].values() for unit in units
    ]
    selected_keys = {
        key
        for row in [*news_rows, *disclosure_rows]
        for key in sentiment_provenance(row).group_keys
    }
    if selected_keys & protected_group_keys:
        raise ValueError("신규 sealed 표본과 보호 식별자가 중복됩니다.")
    assert_sentiment_groups_disjoint(
        {news_partition: news_rows, disclosure_partition: disclosure_rows}
    )


def build_sampling_report(
    *,
    design: SamplingDesign,
    protected: dict[str, IdentityCollection],
    source_audit: dict[str, Any],
    news_output_path: Path,
    disclosure_output_path: Path,
) -> dict[str, Any]:
    combined_protected_keys = frozenset(
        key for collection in protected.values() for key in collection.group_keys
    )
    return {
        "schema_version": "k-fnspid-sentiment-prevalence-sampling-design/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset_version": "K-FNSPID-v4",
        "codebook_version": CODEBOOK_VERSION,
        "frame": {
            "effective_trade_date_start": FRAME_START,
            "effective_trade_date_end": FRAME_END,
            "source_types": ["NEWS", "DISCLOSURE"],
            "eligibility": "K-FNSPID-v4 quality contract and unique PRIMARY entity",
        },
        "sampling_design": {
            "method": "stratified_equal_allocation_without_replacement_by_seeded_sha256_rank/v1",
            "seed": SAMPLING_SEED,
            "hash_function": "SHA-256",
            "strata": list(LABEL_ORDER),
            "weak_rule_stratum": {
                "version": WEAK_STRATUM_VERSION,
                "base_rule": "build_k_fnspid_sentiment_dataset.weak_sentiment_label",
                "disclosure_adverse_auxiliary_regex": (DISCLOSURE_ADVERSE_AUXILIARY.pattern),
                "contract_sha256": _weak_stratum_contract_digest(),
                "gold_label_role": "none; sampling auxiliary only",
            },
            "sample_per_stratum": SAMPLE_PER_STRATUM,
            "sampling_unit": (
                "canonical representative of a transitive provenance component "
                "within the date/source frame"
            ),
            "representative_rule": (
                "lexicographic document_id, canonical identity digest tie-break"
            ),
            "source_selection_order": ["NEWS", "DISCLOSURE"],
            "cross_source_rule": (
                "NEWS-selected provenance components are removed from the "
                "DISCLOSURE frame before DISCLOSURE ranking"
            ),
            "stock_or_diversity_cap": None,
            "equal_probability_contract": (
                "Within each final source/weak-rule stratum, all N_h canonical "
                "units are ranked once by the predeclared seeded SHA-256 rule; "
                "the first n_h units are selected, giving pi_h=n_h/N_h under "
                "the predeclared hash-randomization design."
            ),
            "review_packet_blinding": (
                "Weak-rule strata and weights are omitted from review rows and "
                "are reconstructed with the versioned weak rule only after review."
            ),
        },
        "distinction_from_existing_challenge_sets": {
            "existing_partitions": [
                "SEALED_TEST_REVIEW",
                "DISCLOSURE_SEALED_TEST_REVIEW",
            ],
            "existing_role": (
                "balanced challenge discrimination set with stock-diversity constraints"
            ),
            "new_role": (
                "source-separated prevalence-estimable probability sample with "
                "declared inclusion probabilities and analysis weights"
            ),
            "identity_overlap_allowed": False,
        },
        "protected_identity_sets": {
            "combined": {
                "group_key_count": len(combined_protected_keys),
                "identity_set_sha256": _identity_set_digest(combined_protected_keys),
            },
            "categories": {
                category: _protected_collection_report(collection)
                for category, collection in protected.items()
            },
        },
        "candidate_source_audit": source_audit,
        "component_audit": design.component_audit,
        "partitions": {
            NEWS_PARTITION: _partition_report(
                source_type="NEWS",
                output_path=news_output_path,
                frames=design.frames["NEWS"],
                selected=design.selected["NEWS"],
            ),
            DISCLOSURE_PARTITION: _partition_report(
                source_type="DISCLOSURE",
                output_path=disclosure_output_path,
                frames=design.frames["DISCLOSURE"],
                selected=design.selected["DISCLOSURE"],
            ),
        },
    }


def _protected_collection_report(collection: IdentityCollection) -> dict[str, Any]:
    return {
        "paths": [_path_report(path) for path in collection.paths],
        "identity_row_count": collection.row_count,
        "rows_without_provenance_identity": collection.rows_without_identity,
        "group_key_count": len(collection.group_keys),
        "identity_set_sha256": _identity_set_digest(collection.group_keys),
    }


def _partition_report(
    *,
    source_type: str,
    output_path: Path,
    frames: dict[str, tuple[SamplingUnit, ...]],
    selected: dict[str, tuple[SamplingUnit, ...]],
    output_seed: str = SAMPLING_SEED,
) -> dict[str, Any]:
    selected_units = _flatten_selected(selected, output_seed=output_seed)
    return {
        "source_type": source_type,
        "sample_count": len(selected_units),
        "output": _path_report(output_path),
        "frame_sampling_unit_identity_set_sha256": _unit_identity_set_digest(
            unit for units in frames.values() for unit in units
        ),
        "selected_sampling_unit_identity_set_sha256": _unit_identity_set_digest(selected_units),
        "stock_count_observed_after_sampling": len(
            {unit.candidate.stock_code for unit in selected_units}
        ),
        "strata": {label: _stratum_report(frames[label], selected[label]) for label in LABEL_ORDER},
    }


def _stratum_report(
    frame: tuple[SamplingUnit, ...],
    selected: tuple[SamplingUnit, ...],
) -> dict[str, Any]:
    frame_count = len(frame)
    sample_count = len(selected)
    if frame_count <= 0 or sample_count <= 0 or sample_count > frame_count:
        raise ValueError("층별 표본 설계 수가 올바르지 않습니다.")
    return {
        "frame_N_h": frame_count,
        "sample_n_h": sample_count,
        "inclusion_probability": sample_count / frame_count,
        "inclusion_probability_exact": f"{sample_count}/{frame_count}",
        "analysis_weight": frame_count / sample_count,
        "analysis_weight_exact": f"{frame_count}/{sample_count}",
        "frame_sampling_unit_identity_set_sha256": _unit_identity_set_digest(frame),
        "selected_sampling_unit_identity_set_sha256": _unit_identity_set_digest(selected),
    }


def _flatten_selected(
    selected: dict[str, tuple[SamplingUnit, ...]],
    *,
    output_seed: str = SAMPLING_SEED,
) -> list[SamplingUnit]:
    units = [unit for label in LABEL_ORDER for unit in selected[label]]
    return sorted(
        units,
        key=lambda unit: (
            _stable_digest(unit.candidate.document_id, f"{output_seed}:output"),
            unit.identity_sha256,
        ),
    )


def _candidate_identity_order(candidate: Candidate) -> tuple[str, str]:
    return candidate.document_id, _candidate_identity_digest(candidate)


def _candidate_identity_digest(candidate: Candidate) -> str:
    keys = sentiment_provenance(candidate.group_row()).group_keys
    return _identity_set_digest(keys)


def _group_key_digest(key: ProvenanceGroupKey) -> bytes:
    name, value = key
    return sha256(f"{name}\0{value}".encode()).digest()


def _weak_stratum_contract_digest() -> str:
    contract = "\n".join(
        (
            WEAK_STRATUM_VERSION,
            "NEWS=base weak_sentiment_label",
            "DISCLOSURE=base; NEUTRAL matching auxiliary regex becomes NEGATIVE",
            DISCLOSURE_ADVERSE_AUXILIARY.pattern,
        )
    )
    return sha256(contract.encode()).hexdigest()


def _identity_set_digest(keys: frozenset[ProvenanceGroupKey] | set[ProvenanceGroupKey]) -> str:
    digest = sha256()
    for name, value in sorted(keys):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(value.encode())
        digest.update(b"\n")
    return digest.hexdigest()


def _unit_identity_set_digest(units: Iterable[SamplingUnit]) -> str:
    digest = sha256()
    for identity in sorted(unit.identity_sha256 for unit in units):
        digest.update(identity.encode())
        digest.update(b"\n")
    return digest.hexdigest()


def _path_report(path: Path) -> dict[str, str | int]:
    try:
        display_path = str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        display_path = str(path.resolve())
    return {
        "path": display_path,
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _preflight_new_outputs(paths: tuple[Path, ...]) -> None:
    if len({path.resolve(strict=False) for path in paths}) != len(paths):
        raise ValueError("신규 산출물 경로가 중복됩니다.")
    for path in paths:
        if path.is_symlink() or path.exists():
            raise FileExistsError(f"불변 산출물이 이미 존재합니다: {path}")


def _write_new_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _write_new_file_atomic(path, _encode_jsonl(rows))


def _encode_jsonl(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows
    ).encode()


def _write_new_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    _write_new_file_atomic(path, encoded)


def _write_new_file_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or path.exists():
        raise FileExistsError(f"불변 산출물이 이미 존재합니다: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o644)
        os.link(temporary, path, follow_symlinks=False)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except FileExistsError as error:
        raise FileExistsError(f"불변 산출물이 동시에 생성되었습니다: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
