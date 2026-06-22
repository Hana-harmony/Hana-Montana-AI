from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.dataset import load_labeled_alerts

FULL_CONTENT_DATASET_REPORT_SCHEMA_VERSION = "full-content-training-dataset/v1"
ALLOWED_LICENSE_POLICIES = {
    "internal_rights_safe_full_article_v1",
    "internal_rights_safe_disclosure_text_v1",
    "licensed_naver_original_full_text_v1",
    "licensed_partner_full_text_v1",
    "opendart_public_disclosure_text_v1",
}


def build_full_content_dataset_report(
    path: Path,
    *,
    minimum_rows: int = 10,
    minimum_full_text_characters: int = 180,
) -> dict[str, Any]:
    rows = load_labeled_alerts(path)
    errors: list[str] = []
    license_counter: Counter[str] = Counter()
    source_type_counter: Counter[str] = Counter()
    label_counter: Counter[str] = Counter()
    content_hashes: set[str] = set()

    for index, row in enumerate(rows, start=1):
        if row.content_availability != "FULL_TEXT":
            errors.append(f"row {index}: content_availability must be FULL_TEXT")
        if len(row.full_content.strip()) < minimum_full_text_characters:
            errors.append(f"row {index}: full_content is too short")
        if row.source_license_policy not in ALLOWED_LICENSE_POLICIES:
            errors.append(f"row {index}: unsupported source_license_policy")
        if not row.content_hash:
            errors.append(f"row {index}: content_hash is required")
        elif row.content_hash in content_hashes:
            errors.append(f"row {index}: duplicate content_hash")
        content_hashes.add(row.content_hash)
        license_counter[row.source_license_policy or "missing"] += 1
        source_type_counter[row.source_type] += 1
        label_counter.update(row.tags)

    if len(rows) < minimum_rows:
        errors.append(f"dataset row count below minimum: {len(rows)} < {minimum_rows}")
    if not {"NEWS", "DISCLOSURE"}.issubset(source_type_counter):
        errors.append("dataset must include both NEWS and DISCLOSURE full text rows")

    return {
        "schema_version": FULL_CONTENT_DATASET_REPORT_SCHEMA_VERSION,
        "dataset_path": _report_path(path),
        "status": "pass" if not errors else "fail",
        "row_count": len(rows),
        "minimum_rows": minimum_rows,
        "minimum_full_text_characters": minimum_full_text_characters,
        "source_type_count": dict(sorted(source_type_counter.items())),
        "source_license_policy_count": dict(sorted(license_counter.items())),
        "label_count": dict(sorted(label_counter.items())),
        "allowed_license_policies": sorted(ALLOWED_LICENSE_POLICIES),
        "errors": errors,
    }


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
