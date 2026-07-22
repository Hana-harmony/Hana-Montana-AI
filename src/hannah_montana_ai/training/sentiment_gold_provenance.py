from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CODEBOOK_PATH = PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-codebook.md"
PROMPT_PATH = PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-review-prompt-v1.md"
PROVENANCE_ROOT = PROJECT_ROOT / "data/gold/review_v2"

DEFAULT_TRAIN_PROVENANCE = PROVENANCE_ROOT / "train/dual-review-manifest-v2.json"
DEFAULT_NEWS_AUXILIARY_PROVENANCE = (
    PROVENANCE_ROOT / "news-auxiliary/dual-review-manifest-v2.json"
)
DEFAULT_DISCLOSURE_AUXILIARY_PROVENANCE = (
    PROVENANCE_ROOT / "disclosure-auxiliary/dual-review-manifest-v2.json"
)
DEFAULT_NEWS_DEVELOPMENT_PROVENANCE = (
    PROVENANCE_ROOT / "news-development/dual-review-manifest-v2.json"
)
DEFAULT_DISCLOSURE_DEVELOPMENT_PROVENANCE = (
    PROVENANCE_ROOT / "disclosure-development/dual-review-manifest-v2.json"
)


@dataclass(frozen=True, slots=True)
class GoldProvenanceInput:
    role: str
    gold_path: Path
    manifest_path: Path


def add_gold_provenance_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--train-gold-provenance-path",
        type=Path,
        default=DEFAULT_TRAIN_PROVENANCE,
    )
    parser.add_argument(
        "--news-auxiliary-gold-provenance-path",
        type=Path,
        default=DEFAULT_NEWS_AUXILIARY_PROVENANCE,
    )
    parser.add_argument(
        "--disclosure-auxiliary-gold-provenance-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_AUXILIARY_PROVENANCE,
    )
    parser.add_argument(
        "--news-development-gold-provenance-path",
        type=Path,
        default=DEFAULT_NEWS_DEVELOPMENT_PROVENANCE,
    )
    parser.add_argument(
        "--disclosure-development-gold-provenance-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_DEVELOPMENT_PROVENANCE,
    )


def gold_provenance_inputs(args: argparse.Namespace) -> tuple[GoldProvenanceInput, ...]:
    return (
        GoldProvenanceInput(
            "train_gold",
            args.train_gold_path,
            args.train_gold_provenance_path,
        ),
        GoldProvenanceInput(
            "news_auxiliary_training_gold",
            args.news_auxiliary_gold_path,
            args.news_auxiliary_gold_provenance_path,
        ),
        GoldProvenanceInput(
            "disclosure_auxiliary_training_gold",
            args.disclosure_auxiliary_gold_path,
            args.disclosure_auxiliary_gold_provenance_path,
        ),
        GoldProvenanceInput(
            "news_development_gold",
            args.development_gold_path,
            args.news_development_gold_provenance_path,
        ),
        GoldProvenanceInput(
            "disclosure_development_gold",
            args.disclosure_development_gold_path,
            args.disclosure_development_gold_provenance_path,
        ),
    )


def gold_provenance_paths(args: argparse.Namespace) -> dict[str, Path]:
    return {
        f"{item.role}_dual_review_provenance": item.manifest_path
        for item in gold_provenance_inputs(args)
    }


def validate_all_gold_provenance(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    return {
        item.role: validate_gold_provenance(item)
        for item in gold_provenance_inputs(args)
    }


def validate_gold_provenance(contract: GoldProvenanceInput) -> dict[str, Any]:
    # 검수 manifest의 receipt chain과 실제 학습 Gold 라벨을 함께 고정한다.
    from scripts.k_fnspid_sentiment_review_provenance import (
        read_json,
        read_jsonl,
        validate_dual_review_manifest,
    )

    for label, path in (
        ("Gold", contract.gold_path),
        ("dual-review manifest", contract.manifest_path),
        ("codebook", CODEBOOK_PATH),
        ("review prompt", PROMPT_PATH),
    ):
        _require_regular_file(path, f"{contract.role} {label}")

    manifest = read_json(contract.manifest_path)
    artifacts = _mapping(manifest.get("artifacts"), "manifest.artifacts")
    review_path = _artifact_path(artifacts, "review_packet")
    decision_path = _artifact_path(artifacts, "merged_decision")
    _require_regular_file(review_path, f"{contract.role} review packet")
    _require_regular_file(decision_path, f"{contract.role} merged decision")

    validated = validate_dual_review_manifest(
        contract.manifest_path,
        review_path=review_path,
        decision_path=decision_path,
        codebook_path=CODEBOOK_PATH,
        prompt_path=PROMPT_PATH,
    )
    decisions = read_jsonl(decision_path)
    gold_rows = read_jsonl(contract.gold_path)
    decisions_by_id = _unique_rows(decisions, "final decision")
    gold_by_id = _unique_rows(gold_rows, "Gold")
    expected_ids = {
        item_id
        for item_id, row in decisions_by_id.items()
        if row.get("final_sentiment") != "UNRESOLVED"
    }
    if set(gold_by_id) != expected_ids:
        raise ValueError(
            f"{contract.role} Gold item 집합이 receipt-bound 최종 decision과 다릅니다."
        )
    for item_id, gold in gold_by_id.items():
        decision = decisions_by_id[item_id]
        if (
            gold.get("sentiment") != decision.get("final_sentiment")
            or gold.get("review_status") != "CODEX_REVIEW_APPROVED"
            or gold.get("model_blind") is not True
            or gold.get("market_blind") is not True
            or gold.get("independent_reviewer_count") != 2
            or gold.get("inter_reviewer_agreement")
            != decision.get("inter_reviewer_agreement")
            or gold.get("decision_path") != decision.get("decision_path")
        ):
            raise ValueError(
                f"{contract.role} Gold {item_id}가 검증된 dual-review decision과 다릅니다."
            )
    manifest_bytes = contract.manifest_path.read_bytes()
    return {
        "status": "VERIFIED_BLIND_PROVENANCE",
        "gold_row_count": len(gold_rows),
        "gold_sha256": sha256(contract.gold_path.read_bytes()).hexdigest(),
        "dual_review_manifest_sha256": sha256(manifest_bytes).hexdigest(),
        "dual_review_payload_sha256": validated["merge_manifest_payload_sha256"],
        "review_packet_path": _display_path(review_path),
        "merged_decision_path": _display_path(decision_path),
    }


def _unique_rows(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        item_id = row.get("item_id")
        if not isinstance(item_id, str) or not item_id.strip() or item_id in result:
            raise ValueError(f"{label} item_id가 비었거나 중복됩니다.")
        result[item_id] = row
    return result


def _artifact_path(artifacts: dict[str, Any], field: str) -> Path:
    record = _mapping(artifacts.get(field), f"manifest.artifacts.{field}")
    raw = record.get("path")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"manifest.artifacts.{field}.path가 없습니다.")
    path = Path(raw)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _require_regular_file(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label}는 symlink가 아닌 일반 파일이어야 합니다: {path}")


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return cast(dict[str, Any], value)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())
