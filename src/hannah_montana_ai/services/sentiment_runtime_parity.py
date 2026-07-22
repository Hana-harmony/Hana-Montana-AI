from __future__ import annotations

import hmac
import json
import math
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    canonical_json_sha256,
    directory_commitment,
    file_commitment,
    validate_directory_commitment,
    validate_file_commitment,
)

SCHEMA_VERSION = "sentiment-cpu-serving-parity/v1"
LOCK_SCHEMA_VERSION = "sentiment-cpu-serving-parity-lock/v1"
V6_SCHEMA_VERSION = "sentiment-cpu-serving-parity/v2"
V6_LOCK_SCHEMA_VERSION = "sentiment-cpu-serving-parity-lock/v2"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
EVALUATOR_BATCH_SIZE = 16
PACKAGED_RUNTIME_BATCH_SIZE = 1
LOGITS_MAX_ABS_ERROR_TOLERANCE = 1e-5
PROBABILITY_MAX_ABS_ERROR_TOLERANCE = 1e-6
EXPECTED_SOURCES = ("NEWS", "DISCLOSURE")


def build_cpu_serving_parity_evidence(
    *,
    candidate_version: str,
    candidate_artifact_manifest_sha256: str,
    reservation_inputs: Mapping[str, Sequence[Mapping[str, str]]],
    evaluator_outputs: Sequence[Mapping[str, object]],
    packaged_runtime_outputs: Sequence[Mapping[str, object]],
    evaluator_base_model: Mapping[str, object],
    packaged_runtime_base_model: Mapping[str, object],
    generated_at: str,
    candidate_model_family: str | None = None,
    base_source_kind: str | None = None,
) -> dict[str, Any]:
    if candidate_model_family is not None or base_source_kind is not None:
        return _build_v6_cpu_serving_parity_evidence(
            candidate_version=candidate_version,
            candidate_artifact_manifest_sha256=candidate_artifact_manifest_sha256,
            candidate_model_family=candidate_model_family,
            base_source_kind=base_source_kind,
            reservation_inputs=reservation_inputs,
            evaluator_outputs=evaluator_outputs,
            packaged_runtime_outputs=packaged_runtime_outputs,
            evaluator_base_model=evaluator_base_model,
            packaged_runtime_base_model=packaged_runtime_base_model,
            generated_at=generated_at,
        )
    candidate_digest = _sha256_value(
        candidate_artifact_manifest_sha256, "candidate artifact manifest"
    )
    if not isinstance(candidate_version, str) or not candidate_version.strip():
        raise ValueError("runtime parity candidate version이 없습니다.")
    inputs = _normalized_reservation_inputs(reservation_inputs)
    evaluator = _normalized_outputs(
        evaluator_outputs,
        expected_item_ids=_ordered_item_ids(inputs),
        label="evaluator",
    )
    packaged = _normalized_outputs(
        packaged_runtime_outputs,
        expected_item_ids=_ordered_item_ids(inputs),
        label="packaged runtime",
    )
    evaluator_base = _base_safetensors_commitment(evaluator_base_model, "evaluator base model")
    runtime_base = _base_safetensors_commitment(
        packaged_runtime_base_model, "packaged runtime base model"
    )
    if evaluator_base["safetensors_files"] != runtime_base["safetensors_files"]:
        raise ValueError("evaluator와 packaged runtime의 base encoder safetensors가 다릅니다.")
    max_abs_error = 0.0
    exact_labels = True
    comparison_rows: list[dict[str, Any]] = []
    for left, right in zip(evaluator, packaged, strict=True):
        if left["item_id"] != right["item_id"]:
            raise ValueError("runtime parity 출력 item 순서가 다릅니다.")
        row_error = max(
            abs(float(a) - float(b))
            for a, b in zip(left["logits"], right["logits"], strict=True)
        )
        max_abs_error = max(max_abs_error, row_error)
        labels_match = left["label"] == right["label"]
        exact_labels = exact_labels and labels_match
        comparison_rows.append(
            {
                "item_id": left["item_id"],
                "labels_equal": labels_match,
                "logits_max_abs_error": row_error,
            }
        )
    if not exact_labels or max_abs_error > LOGITS_MAX_ABS_ERROR_TOLERANCE:
        raise ValueError("CPU batch16/batch1 serving parity 허용 오차를 초과했습니다.")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "candidate": {
            "version": candidate_version,
            "artifact_manifest_sha256": candidate_digest,
        },
        "input_contract": {
            "role": "unlabeled_confirmatory_reservation_only",
            "confirmatory_or_public_labels_opened": False,
            "sources": inputs,
            "item_order_sha256": canonical_json_sha256(_ordered_item_ids(inputs)),
            "sample_count": len(evaluator),
        },
        "evaluator": {
            "backend": "cpu",
            "batch_size": EVALUATOR_BATCH_SIZE,
            "label_order": list(LABEL_ORDER),
            "outputs": evaluator,
            "outputs_sha256": canonical_json_sha256(evaluator),
            "base_encoder": evaluator_base,
        },
        "packaged_runtime": {
            "backend": "cpu",
            "batch_size": PACKAGED_RUNTIME_BATCH_SIZE,
            "label_order": list(LABEL_ORDER),
            "outputs": packaged,
            "outputs_sha256": canonical_json_sha256(packaged),
            "base_encoder": runtime_base,
        },
        "comparison": {
            "exact_label_agreement": exact_labels,
            "logits_max_abs_error": max_abs_error,
            "logits_max_abs_error_tolerance": LOGITS_MAX_ABS_ERROR_TOLERANCE,
            "base_encoder_safetensors_identical": True,
            "rows": comparison_rows,
            "rows_sha256": canonical_json_sha256(comparison_rows),
            "passed": True,
        },
    }
    return validate_cpu_serving_parity_evidence(payload)


def validate_cpu_serving_parity_evidence(value: object) -> dict[str, Any]:
    payload = _mapping(value, "CPU serving parity evidence")
    if payload.get("schema_version") == V6_SCHEMA_VERSION:
        return _validate_v6_cpu_serving_parity_evidence(payload)
    if set(payload) != {
        "schema_version",
        "generated_at",
        "candidate",
        "input_contract",
        "evaluator",
        "packaged_runtime",
        "comparison",
    } or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("CPU serving parity evidence schema가 올바르지 않습니다.")
    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at.strip():
        raise ValueError("CPU serving parity evidence 생성 시각이 없습니다.")
    candidate = _mapping(payload.get("candidate"), "parity candidate")
    if set(candidate) != {"version", "artifact_manifest_sha256"}:
        raise ValueError("runtime parity candidate commitment가 올바르지 않습니다.")
    version = candidate.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("runtime parity candidate version이 없습니다.")
    candidate_digest = _sha256_value(
        candidate.get("artifact_manifest_sha256"), "runtime parity candidate"
    )

    contract = _mapping(payload.get("input_contract"), "runtime parity input contract")
    if (
        set(contract)
        != {
            "role",
            "confirmatory_or_public_labels_opened",
            "sources",
            "item_order_sha256",
            "sample_count",
        }
        or contract.get("role") != "unlabeled_confirmatory_reservation_only"
        or contract.get("confirmatory_or_public_labels_opened") is not False
    ):
        raise ValueError("runtime parity가 unlabeled reservation 계약을 위반했습니다.")
    sources = _normalized_reservation_inputs(
        _mapping(contract.get("sources"), "runtime parity reservation sources")
    )
    item_ids = _ordered_item_ids(sources)
    if contract.get("item_order_sha256") != canonical_json_sha256(item_ids):
        raise ValueError("runtime parity reservation item 순서 digest가 다릅니다.")
    sample_count = contract.get("sample_count")
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count < 1:
        raise ValueError("runtime parity sample count가 올바르지 않습니다.")

    evaluator = _validate_backend(
        payload.get("evaluator"),
        expected_batch_size=EVALUATOR_BATCH_SIZE,
        expected_item_ids=item_ids,
        label="evaluator",
    )
    packaged = _validate_backend(
        payload.get("packaged_runtime"),
        expected_batch_size=PACKAGED_RUNTIME_BATCH_SIZE,
        expected_item_ids=item_ids,
        label="packaged runtime",
    )
    if sample_count != len(evaluator["outputs"]):
        raise ValueError("runtime parity sample count가 출력 수와 다릅니다.")
    left_base = evaluator["base_encoder"]
    right_base = packaged["base_encoder"]
    if left_base["safetensors_files"] != right_base["safetensors_files"]:
        raise ValueError("runtime parity base encoder safetensors manifest가 다릅니다.")

    comparison = _mapping(payload.get("comparison"), "runtime parity comparison")
    required_comparison = {
        "exact_label_agreement",
        "logits_max_abs_error",
        "logits_max_abs_error_tolerance",
        "base_encoder_safetensors_identical",
        "rows",
        "rows_sha256",
        "passed",
    }
    if set(comparison) != required_comparison:
        raise ValueError("runtime parity comparison 구성이 올바르지 않습니다.")
    expected_rows: list[dict[str, Any]] = []
    max_abs_error = 0.0
    exact_labels = True
    for left, right in zip(evaluator["outputs"], packaged["outputs"], strict=True):
        row_error = max(
            abs(float(a) - float(b))
            for a, b in zip(left["logits"], right["logits"], strict=True)
        )
        max_abs_error = max(max_abs_error, row_error)
        labels_equal = left["label"] == right["label"]
        exact_labels = exact_labels and labels_equal
        expected_rows.append(
            {
                "item_id": left["item_id"],
                "labels_equal": labels_equal,
                "logits_max_abs_error": row_error,
            }
        )
    declared_rows = comparison.get("rows")
    if declared_rows != expected_rows or comparison.get("rows_sha256") != canonical_json_sha256(
        expected_rows
    ):
        raise ValueError("runtime parity 비교 결과를 원시 logits에서 재현할 수 없습니다.")
    tolerance = _finite_number(
        comparison.get("logits_max_abs_error_tolerance"), "runtime parity tolerance"
    )
    declared_error = _finite_number(
        comparison.get("logits_max_abs_error"), "runtime parity max error"
    )
    if (
        not math.isclose(tolerance, LOGITS_MAX_ABS_ERROR_TOLERANCE, rel_tol=0.0, abs_tol=0.0)
        or not math.isclose(declared_error, max_abs_error, rel_tol=0.0, abs_tol=1e-15)
        or comparison.get("exact_label_agreement") is not exact_labels
        or comparison.get("base_encoder_safetensors_identical") is not True
        or comparison.get("passed") is not True
        or not exact_labels
        or max_abs_error > LOGITS_MAX_ABS_ERROR_TOLERANCE
    ):
        raise ValueError("runtime parity pass 조건을 충족하지 않습니다.")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "candidate": {
            "version": version,
            "artifact_manifest_sha256": candidate_digest,
        },
        "input_contract": {
            "role": contract["role"],
            "confirmatory_or_public_labels_opened": False,
            "sources": sources,
            "item_order_sha256": contract["item_order_sha256"],
            "sample_count": sample_count,
        },
        "evaluator": evaluator,
        "packaged_runtime": packaged,
        "comparison": {
            **comparison,
            "logits_max_abs_error": declared_error,
            "logits_max_abs_error_tolerance": tolerance,
        },
    }


def _build_v6_cpu_serving_parity_evidence(
    *,
    candidate_version: str,
    candidate_artifact_manifest_sha256: str,
    candidate_model_family: str | None,
    base_source_kind: str | None,
    reservation_inputs: Mapping[str, Sequence[Mapping[str, str]]],
    evaluator_outputs: Sequence[Mapping[str, object]],
    packaged_runtime_outputs: Sequence[Mapping[str, object]],
    evaluator_base_model: Mapping[str, object],
    packaged_runtime_base_model: Mapping[str, object],
    generated_at: str,
) -> dict[str, Any]:
    if candidate_model_family != V6_MODEL_FAMILY:
        raise ValueError("v6 runtime parity model family가 올바르지 않습니다.")
    if base_source_kind not in {"PINNED_RAW", "DAPT_MERGED_FP32"}:
        raise ValueError("v6 runtime parity base source 종류가 올바르지 않습니다.")
    candidate_digest = _sha256_value(
        candidate_artifact_manifest_sha256,
        "v6 candidate artifact manifest",
    )
    if not isinstance(candidate_version, str) or not candidate_version.strip():
        raise ValueError("v6 runtime parity candidate version이 없습니다.")
    if not isinstance(generated_at, str) or not generated_at.strip():
        raise ValueError("v6 runtime parity 생성 시각이 없습니다.")
    inputs = _normalized_reservation_inputs(reservation_inputs)
    expected_items = _ordered_source_items(inputs)
    evaluator = _normalized_v6_outputs(
        evaluator_outputs,
        expected_items=expected_items,
        label="evaluator",
    )
    packaged = _normalized_v6_outputs(
        packaged_runtime_outputs,
        expected_items=expected_items,
        label="packaged runtime",
    )
    evaluator_base = _base_safetensors_commitment(evaluator_base_model, "evaluator base model")
    runtime_base = _base_safetensors_commitment(
        packaged_runtime_base_model,
        "packaged runtime base model",
    )
    if evaluator_base["safetensors_files"] != runtime_base["safetensors_files"]:
        raise ValueError("evaluator와 packaged runtime의 base encoder safetensors가 다릅니다.")

    maximum_error = 0.0
    exact_labels = True
    calibration_equal = True
    comparison_rows: list[dict[str, Any]] = []
    for left, right in zip(evaluator, packaged, strict=True):
        row_error = max(
            abs(float(left["probabilities"][name]) - float(right["probabilities"][name]))
            for name in LABEL_ORDER
        )
        labels_equal = left["label"] == right["label"]
        row_calibration_equal = all(
            left[name] == right[name]
            for name in ("domain", "temperature", "neutral_threshold")
        )
        maximum_error = max(maximum_error, row_error)
        exact_labels = exact_labels and labels_equal
        calibration_equal = calibration_equal and row_calibration_equal
        comparison_rows.append(
            {
                "item_id": left["item_id"],
                "labels_equal": labels_equal,
                "calibration_equal": row_calibration_equal,
                "probability_max_abs_error": row_error,
            }
        )
    if (
        not exact_labels
        or not calibration_equal
        or maximum_error > PROBABILITY_MAX_ABS_ERROR_TOLERANCE
    ):
        raise ValueError("v6 CPU batch16/batch1 serving parity 허용 오차를 초과했습니다.")
    payload = {
        "schema_version": V6_SCHEMA_VERSION,
        "generated_at": generated_at,
        "candidate": {
            "model_family": candidate_model_family,
            "version": candidate_version,
            "artifact_manifest_sha256": candidate_digest,
            "base_source_kind": base_source_kind,
        },
        "input_contract": {
            "role": "unlabeled_confirmatory_reservation_only",
            "confirmatory_or_public_labels_opened": False,
            "sources": inputs,
            "item_order_sha256": canonical_json_sha256(_ordered_item_ids(inputs)),
            "sample_count": len(evaluator),
        },
        "evaluator": _v6_backend_payload(
            evaluator,
            EVALUATOR_BATCH_SIZE,
            evaluator_base,
        ),
        "packaged_runtime": _v6_backend_payload(
            packaged,
            PACKAGED_RUNTIME_BATCH_SIZE,
            runtime_base,
        ),
        "comparison": {
            "exact_label_agreement": exact_labels,
            "calibration_contract_identical": calibration_equal,
            "probability_max_abs_error": maximum_error,
            "probability_max_abs_error_tolerance": PROBABILITY_MAX_ABS_ERROR_TOLERANCE,
            "base_encoder_safetensors_identical": True,
            "rows": comparison_rows,
            "rows_sha256": canonical_json_sha256(comparison_rows),
            "passed": True,
        },
    }
    return _validate_v6_cpu_serving_parity_evidence(payload)


def _validate_v6_cpu_serving_parity_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema_version",
        "generated_at",
        "candidate",
        "input_contract",
        "evaluator",
        "packaged_runtime",
        "comparison",
    }
    if set(payload) != required or payload.get("schema_version") != V6_SCHEMA_VERSION:
        raise ValueError("v6 CPU serving parity evidence schema가 올바르지 않습니다.")
    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at.strip():
        raise ValueError("v6 CPU serving parity evidence 생성 시각이 없습니다.")
    candidate = _mapping(payload.get("candidate"), "v6 parity candidate")
    if (
        set(candidate)
        != {"model_family", "version", "artifact_manifest_sha256", "base_source_kind"}
        or candidate.get("model_family") != V6_MODEL_FAMILY
        or candidate.get("base_source_kind") not in {"PINNED_RAW", "DAPT_MERGED_FP32"}
        or not isinstance(candidate.get("version"), str)
        or not str(candidate["version"]).strip()
    ):
        raise ValueError("v6 runtime parity candidate commitment가 올바르지 않습니다.")
    candidate_digest = _sha256_value(
        candidate.get("artifact_manifest_sha256"),
        "v6 runtime parity candidate",
    )
    contract = _mapping(payload.get("input_contract"), "v6 runtime parity input contract")
    if (
        set(contract)
        != {
            "role",
            "confirmatory_or_public_labels_opened",
            "sources",
            "item_order_sha256",
            "sample_count",
        }
        or contract.get("role") != "unlabeled_confirmatory_reservation_only"
        or contract.get("confirmatory_or_public_labels_opened") is not False
    ):
        raise ValueError("v6 runtime parity가 unlabeled reservation 계약을 위반했습니다.")
    sources = _normalized_reservation_inputs(
        _mapping(contract.get("sources"), "v6 runtime parity reservation sources")
    )
    item_ids = _ordered_item_ids(sources)
    expected_items = _ordered_source_items(sources)
    if contract.get("item_order_sha256") != canonical_json_sha256(item_ids):
        raise ValueError("v6 runtime parity reservation item 순서 digest가 다릅니다.")
    sample_count = contract.get("sample_count")
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count < 1:
        raise ValueError("v6 runtime parity sample count가 올바르지 않습니다.")
    evaluator = _validate_v6_backend(
        payload.get("evaluator"),
        expected_batch_size=EVALUATOR_BATCH_SIZE,
        expected_items=expected_items,
        label="evaluator",
    )
    packaged = _validate_v6_backend(
        payload.get("packaged_runtime"),
        expected_batch_size=PACKAGED_RUNTIME_BATCH_SIZE,
        expected_items=expected_items,
        label="packaged runtime",
    )
    if sample_count != len(evaluator["outputs"]):
        raise ValueError("v6 runtime parity sample count가 출력 수와 다릅니다.")
    if evaluator["base_encoder"]["safetensors_files"] != packaged["base_encoder"][
        "safetensors_files"
    ]:
        raise ValueError("v6 runtime parity base encoder safetensors manifest가 다릅니다.")

    comparison = _mapping(payload.get("comparison"), "v6 runtime parity comparison")
    if set(comparison) != {
        "exact_label_agreement",
        "calibration_contract_identical",
        "probability_max_abs_error",
        "probability_max_abs_error_tolerance",
        "base_encoder_safetensors_identical",
        "rows",
        "rows_sha256",
        "passed",
    }:
        raise ValueError("v6 runtime parity comparison 구성이 올바르지 않습니다.")
    expected_rows: list[dict[str, Any]] = []
    maximum_error = 0.0
    exact_labels = True
    calibration_equal = True
    for left, right in zip(evaluator["outputs"], packaged["outputs"], strict=True):
        row_error = max(
            abs(float(left["probabilities"][name]) - float(right["probabilities"][name]))
            for name in LABEL_ORDER
        )
        labels_equal = left["label"] == right["label"]
        row_calibration_equal = all(
            left[name] == right[name]
            for name in ("domain", "temperature", "neutral_threshold")
        )
        maximum_error = max(maximum_error, row_error)
        exact_labels = exact_labels and labels_equal
        calibration_equal = calibration_equal and row_calibration_equal
        expected_rows.append(
            {
                "item_id": left["item_id"],
                "labels_equal": labels_equal,
                "calibration_equal": row_calibration_equal,
                "probability_max_abs_error": row_error,
            }
        )
    declared_error = _finite_number(
        comparison.get("probability_max_abs_error"),
        "v6 runtime parity max error",
    )
    declared_tolerance = _finite_number(
        comparison.get("probability_max_abs_error_tolerance"),
        "v6 runtime parity tolerance",
    )
    if (
        comparison.get("rows") != expected_rows
        or comparison.get("rows_sha256") != canonical_json_sha256(expected_rows)
        or not math.isclose(declared_error, maximum_error, rel_tol=0.0, abs_tol=1e-15)
        or not math.isclose(
            declared_tolerance,
            PROBABILITY_MAX_ABS_ERROR_TOLERANCE,
            rel_tol=0.0,
            abs_tol=0.0,
        )
        or comparison.get("exact_label_agreement") is not exact_labels
        or comparison.get("calibration_contract_identical") is not calibration_equal
        or comparison.get("base_encoder_safetensors_identical") is not True
        or comparison.get("passed") is not True
        or not exact_labels
        or not calibration_equal
        or maximum_error > PROBABILITY_MAX_ABS_ERROR_TOLERANCE
    ):
        raise ValueError("v6 runtime parity pass 조건을 충족하지 않습니다.")
    return {
        "schema_version": V6_SCHEMA_VERSION,
        "generated_at": generated_at,
        "candidate": {
            "model_family": V6_MODEL_FAMILY,
            "version": str(candidate["version"]),
            "artifact_manifest_sha256": candidate_digest,
            "base_source_kind": str(candidate["base_source_kind"]),
        },
        "input_contract": {
            "role": contract["role"],
            "confirmatory_or_public_labels_opened": False,
            "sources": sources,
            "item_order_sha256": contract["item_order_sha256"],
            "sample_count": sample_count,
        },
        "evaluator": evaluator,
        "packaged_runtime": packaged,
        "comparison": {
            **comparison,
            "probability_max_abs_error": declared_error,
            "probability_max_abs_error_tolerance": declared_tolerance,
        },
    }


def _v6_backend_payload(
    outputs: list[dict[str, Any]],
    batch_size: int,
    base_encoder: dict[str, Any],
) -> dict[str, Any]:
    return {
        "backend": "cpu",
        "batch_size": batch_size,
        "decision_contract": "domain_temperature_neutral_threshold/v1",
        "label_order": list(LABEL_ORDER),
        "outputs": outputs,
        "outputs_sha256": canonical_json_sha256(outputs),
        "base_encoder": base_encoder,
    }


def _validate_v6_backend(
    value: object,
    *,
    expected_batch_size: int,
    expected_items: list[tuple[str, str]],
    label: str,
) -> dict[str, Any]:
    backend = _mapping(value, label)
    if (
        set(backend)
        != {
            "backend",
            "batch_size",
            "decision_contract",
            "label_order",
            "outputs",
            "outputs_sha256",
            "base_encoder",
        }
        or backend.get("backend") != "cpu"
        or backend.get("batch_size") != expected_batch_size
        or backend.get("decision_contract")
        != "domain_temperature_neutral_threshold/v1"
        or tuple(backend.get("label_order", ())) != LABEL_ORDER
    ):
        raise ValueError(f"{label} v6 backend는 canonical CPU batch 계약과 다릅니다.")
    outputs = _normalized_v6_outputs(
        backend.get("outputs"),
        expected_items=expected_items,
        label=label,
    )
    if backend.get("outputs_sha256") != canonical_json_sha256(outputs):
        raise ValueError(f"{label} v6 output digest가 다릅니다.")
    return {
        "backend": "cpu",
        "batch_size": expected_batch_size,
        "decision_contract": "domain_temperature_neutral_threshold/v1",
        "label_order": list(LABEL_ORDER),
        "outputs": outputs,
        "outputs_sha256": backend["outputs_sha256"],
        "base_encoder": _base_safetensors_commitment(
            backend.get("base_encoder"),
            f"{label} base",
        ),
    }


def build_runtime_parity_lock_commitment(
    *,
    evidence_path: Path,
    project_root: Path,
    expected_candidate_version: str,
    expected_candidate_artifact_manifest_sha256: str,
    sealed_reservations: Mapping[str, Mapping[str, object]],
    expected_candidate_model_family: str | None = None,
    expected_base_source_kind: str | None = None,
) -> dict[str, Any]:
    if expected_candidate_model_family is not None or expected_base_source_kind is not None:
        return _build_v6_runtime_parity_lock_commitment(
            evidence_path=evidence_path,
            project_root=project_root,
            expected_candidate_version=expected_candidate_version,
            expected_candidate_artifact_manifest_sha256=(
                expected_candidate_artifact_manifest_sha256
            ),
            expected_candidate_model_family=expected_candidate_model_family,
            expected_base_source_kind=expected_base_source_kind,
            sealed_reservations=sealed_reservations,
        )
    evidence_record = file_commitment(evidence_path, project_root)
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence = validate_cpu_serving_parity_evidence(payload)
    if (
        evidence["candidate"]["version"] != expected_candidate_version
        or not hmac.compare_digest(
            str(evidence["candidate"]["artifact_manifest_sha256"]),
            _sha256_value(
                expected_candidate_artifact_manifest_sha256,
                "expected candidate artifact manifest",
            ),
        )
    ):
        raise ValueError("runtime parity evidence가 선택된 candidate와 다릅니다.")
    _validate_reservation_linkage(evidence["input_contract"]["sources"], sealed_reservations)
    evaluator_base = evidence["evaluator"]["base_encoder"]["directory"]
    runtime_base = evidence["packaged_runtime"]["base_encoder"]["directory"]
    validate_directory_commitment(evaluator_base, project_root, "evaluator base encoder")
    validate_directory_commitment(runtime_base, project_root, "packaged runtime base encoder")
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "evidence": evidence_record,
        "candidate_version": expected_candidate_version,
        "candidate_artifact_manifest_sha256": expected_candidate_artifact_manifest_sha256,
        "reservation_item_order_sha256": evidence["input_contract"]["item_order_sha256"],
        "sample_count": evidence["input_contract"]["sample_count"],
        "evaluator_backend": {"device": "cpu", "batch_size": EVALUATOR_BATCH_SIZE},
        "packaged_runtime_backend": {
            "device": "cpu",
            "batch_size": PACKAGED_RUNTIME_BATCH_SIZE,
        },
        "exact_label_agreement": True,
        "logits_max_abs_error": evidence["comparison"]["logits_max_abs_error"],
        "logits_max_abs_error_tolerance": LOGITS_MAX_ABS_ERROR_TOLERANCE,
        "base_encoder_safetensors_manifest_sha256": canonical_json_sha256(
            evidence["evaluator"]["base_encoder"]["safetensors_files"]
        ),
        "evaluator_base_encoder": evaluator_base,
        "packaged_runtime_base_encoder": runtime_base,
    }


def validate_runtime_parity_lock_commitment(
    value: object,
    *,
    project_root: Path,
    expected_candidate_version: str,
    expected_candidate_artifact_manifest_sha256: str,
    sealed_reservations: Mapping[str, Mapping[str, object]],
    expected_candidate_model_family: str | None = None,
    expected_base_source_kind: str | None = None,
) -> dict[str, Any]:
    record = _mapping(value, "runtime parity lock")
    if record.get("schema_version") == V6_LOCK_SCHEMA_VERSION:
        return _validate_v6_runtime_parity_lock_commitment(
            record,
            project_root=project_root,
            expected_candidate_version=expected_candidate_version,
            expected_candidate_artifact_manifest_sha256=(
                expected_candidate_artifact_manifest_sha256
            ),
            expected_candidate_model_family=expected_candidate_model_family,
            expected_base_source_kind=expected_base_source_kind,
            sealed_reservations=sealed_reservations,
        )
    required = {
        "schema_version",
        "evidence",
        "candidate_version",
        "candidate_artifact_manifest_sha256",
        "reservation_item_order_sha256",
        "sample_count",
        "evaluator_backend",
        "packaged_runtime_backend",
        "exact_label_agreement",
        "logits_max_abs_error",
        "logits_max_abs_error_tolerance",
        "base_encoder_safetensors_manifest_sha256",
        "evaluator_base_encoder",
        "packaged_runtime_base_encoder",
    }
    if set(record) != required or record.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise ValueError("runtime parity lock commitment 구성이 올바르지 않습니다.")
    evidence_record = validate_file_commitment(
        record.get("evidence"), project_root, "parity evidence"
    )
    evidence_path = Path(project_root).resolve() / str(evidence_record["path"])
    try:
        evidence_raw = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError("runtime parity evidence JSON을 읽을 수 없습니다.") from exception
    evidence = validate_cpu_serving_parity_evidence(evidence_raw)
    expected = build_runtime_parity_lock_commitment(
        evidence_path=evidence_path,
        project_root=project_root,
        expected_candidate_version=expected_candidate_version,
        expected_candidate_artifact_manifest_sha256=expected_candidate_artifact_manifest_sha256,
        sealed_reservations=sealed_reservations,
    )
    if record != expected:
        raise ValueError("runtime parity lock을 evidence 실제 바이트에서 재현할 수 없습니다.")
    if evidence["comparison"]["passed"] is not True:
        raise ValueError("runtime parity evidence가 실패 상태입니다.")
    return expected


def _build_v6_runtime_parity_lock_commitment(
    *,
    evidence_path: Path,
    project_root: Path,
    expected_candidate_version: str,
    expected_candidate_artifact_manifest_sha256: str,
    expected_candidate_model_family: str | None,
    expected_base_source_kind: str | None,
    sealed_reservations: Mapping[str, Mapping[str, object]],
) -> dict[str, Any]:
    if expected_candidate_model_family != V6_MODEL_FAMILY:
        raise ValueError("v6 runtime parity lock model family가 다릅니다.")
    if expected_base_source_kind not in {"PINNED_RAW", "DAPT_MERGED_FP32"}:
        raise ValueError("v6 runtime parity lock base source 종류가 다릅니다.")
    evidence_record = file_commitment(evidence_path, project_root)
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError("v6 runtime parity evidence JSON을 읽을 수 없습니다.") from exception
    evidence = validate_cpu_serving_parity_evidence(payload)
    candidate = evidence["candidate"]
    if (
        evidence.get("schema_version") != V6_SCHEMA_VERSION
        or candidate["version"] != expected_candidate_version
        or candidate["model_family"] != expected_candidate_model_family
        or candidate["base_source_kind"] != expected_base_source_kind
        or not hmac.compare_digest(
            str(candidate["artifact_manifest_sha256"]),
            _sha256_value(
                expected_candidate_artifact_manifest_sha256,
                "expected v6 candidate artifact manifest",
            ),
        )
    ):
        raise ValueError("v6 runtime parity evidence가 선택된 candidate와 다릅니다.")
    _validate_reservation_linkage(evidence["input_contract"]["sources"], sealed_reservations)
    evaluator_base = evidence["evaluator"]["base_encoder"]["directory"]
    runtime_base = evidence["packaged_runtime"]["base_encoder"]["directory"]
    validate_directory_commitment(evaluator_base, project_root, "v6 evaluator base encoder")
    validate_directory_commitment(runtime_base, project_root, "v6 packaged runtime base encoder")
    return {
        "schema_version": V6_LOCK_SCHEMA_VERSION,
        "evidence": evidence_record,
        "candidate_model_family": expected_candidate_model_family,
        "candidate_version": expected_candidate_version,
        "candidate_artifact_manifest_sha256": expected_candidate_artifact_manifest_sha256,
        "base_source_kind": expected_base_source_kind,
        "reservation_item_order_sha256": evidence["input_contract"]["item_order_sha256"],
        "sample_count": evidence["input_contract"]["sample_count"],
        "evaluator_backend": {"device": "cpu", "batch_size": EVALUATOR_BATCH_SIZE},
        "packaged_runtime_backend": {
            "device": "cpu",
            "batch_size": PACKAGED_RUNTIME_BATCH_SIZE,
        },
        "decision_contract": "domain_temperature_neutral_threshold/v1",
        "exact_label_agreement": True,
        "calibration_contract_identical": True,
        "probability_max_abs_error": evidence["comparison"]["probability_max_abs_error"],
        "probability_max_abs_error_tolerance": PROBABILITY_MAX_ABS_ERROR_TOLERANCE,
        "base_encoder_safetensors_manifest_sha256": canonical_json_sha256(
            evidence["evaluator"]["base_encoder"]["safetensors_files"]
        ),
        "evaluator_base_encoder": evaluator_base,
        "packaged_runtime_base_encoder": runtime_base,
    }


def _validate_v6_runtime_parity_lock_commitment(
    record: dict[str, Any],
    *,
    project_root: Path,
    expected_candidate_version: str,
    expected_candidate_artifact_manifest_sha256: str,
    expected_candidate_model_family: str | None,
    expected_base_source_kind: str | None,
    sealed_reservations: Mapping[str, Mapping[str, object]],
) -> dict[str, Any]:
    required = {
        "schema_version",
        "evidence",
        "candidate_model_family",
        "candidate_version",
        "candidate_artifact_manifest_sha256",
        "base_source_kind",
        "reservation_item_order_sha256",
        "sample_count",
        "evaluator_backend",
        "packaged_runtime_backend",
        "decision_contract",
        "exact_label_agreement",
        "calibration_contract_identical",
        "probability_max_abs_error",
        "probability_max_abs_error_tolerance",
        "base_encoder_safetensors_manifest_sha256",
        "evaluator_base_encoder",
        "packaged_runtime_base_encoder",
    }
    if set(record) != required or record.get("schema_version") != V6_LOCK_SCHEMA_VERSION:
        raise ValueError("v6 runtime parity lock commitment 구성이 올바르지 않습니다.")
    evidence_record = validate_file_commitment(
        record.get("evidence"),
        project_root,
        "v6 parity evidence",
    )
    evidence_path = Path(project_root).resolve() / str(evidence_record["path"])
    expected = _build_v6_runtime_parity_lock_commitment(
        evidence_path=evidence_path,
        project_root=project_root,
        expected_candidate_version=expected_candidate_version,
        expected_candidate_artifact_manifest_sha256=(
            expected_candidate_artifact_manifest_sha256
        ),
        expected_candidate_model_family=expected_candidate_model_family,
        expected_base_source_kind=expected_base_source_kind,
        sealed_reservations=sealed_reservations,
    )
    if record != expected:
        raise ValueError("v6 runtime parity lock을 evidence 바이트에서 재현할 수 없습니다.")
    return expected


def safetensors_only_manifest(directory_record: object) -> dict[str, dict[str, int | str]]:
    directory = _mapping(directory_record, "base encoder directory")
    files = _mapping(directory.get("files"), "base encoder files")
    selected = {
        name: dict(_mapping(entry, f"base encoder {name}"))
        for name, entry in files.items()
        if name.endswith(".safetensors")
    }
    if not selected:
        raise ValueError("base encoder에 safetensors 가중치가 없습니다.")
    return dict(sorted(selected.items()))


def _validate_backend(
    value: object,
    *,
    expected_batch_size: int,
    expected_item_ids: list[str],
    label: str,
) -> dict[str, Any]:
    backend = _mapping(value, label)
    if set(backend) != {
        "backend",
        "batch_size",
        "label_order",
        "outputs",
        "outputs_sha256",
        "base_encoder",
    }:
        raise ValueError(f"{label} runtime parity backend 구성이 올바르지 않습니다.")
    if (
        backend.get("backend") != "cpu"
        or backend.get("batch_size") != expected_batch_size
        or tuple(backend.get("label_order", ())) != LABEL_ORDER
    ):
        raise ValueError(f"{label} backend는 canonical CPU batch 계약과 다릅니다.")
    outputs = _normalized_outputs(
        backend.get("outputs"), expected_item_ids=expected_item_ids, label=label
    )
    if backend.get("outputs_sha256") != canonical_json_sha256(outputs):
        raise ValueError(f"{label} output digest가 다릅니다.")
    base = _base_safetensors_commitment(backend.get("base_encoder"), f"{label} base")
    return {
        "backend": "cpu",
        "batch_size": expected_batch_size,
        "label_order": list(LABEL_ORDER),
        "outputs": outputs,
        "outputs_sha256": backend["outputs_sha256"],
        "base_encoder": base,
    }


def _base_safetensors_commitment(value: object, label: str) -> dict[str, Any]:
    base = _mapping(value, label)
    if set(base) != {"directory", "safetensors_files", "safetensors_manifest_sha256"}:
        raise ValueError(f"{label} base encoder commitment 구성이 올바르지 않습니다.")
    directory = _mapping(base.get("directory"), f"{label} directory")
    selected = safetensors_only_manifest(directory)
    declared = {
        name: dict(_mapping(entry, f"{label} {name}"))
        for name, entry in _mapping(base.get("safetensors_files"), label).items()
    }
    if selected != declared:
        raise ValueError(f"{label} safetensors subset이 full directory manifest와 다릅니다.")
    digest = canonical_json_sha256(declared)
    if base.get("safetensors_manifest_sha256") != digest:
        raise ValueError(f"{label} safetensors manifest digest가 다릅니다.")
    return {
        "directory": directory,
        "safetensors_files": declared,
        "safetensors_manifest_sha256": digest,
    }


def base_encoder_evidence(directory: Path, project_root: Path) -> dict[str, Any]:
    full = directory_commitment(directory, project_root)
    selected = safetensors_only_manifest(full)
    return {
        "directory": full,
        "safetensors_files": selected,
        "safetensors_manifest_sha256": canonical_json_sha256(selected),
    }


def _normalized_reservation_inputs(
    value: Mapping[str, Sequence[Mapping[str, str]]] | object,
) -> dict[str, list[dict[str, str]]]:
    sources = _mapping(value, "reservation inputs")
    if set(sources) != set(EXPECTED_SOURCES):
        raise ValueError("runtime parity에는 NEWS/DISCLOSURE reservation이 모두 필요합니다.")
    normalized: dict[str, list[dict[str, str]]] = {}
    seen: set[str] = set()
    for source in EXPECTED_SOURCES:
        rows = sources[source]
        if not isinstance(rows, Sequence) or isinstance(rows, str | bytes) or not rows:
            raise ValueError(f"runtime parity {source} reservation이 비어 있습니다.")
        normalized_rows: list[dict[str, str]] = []
        for raw in rows:
            row = _mapping(raw, f"runtime parity {source} input")
            if set(row) != {"item_id", "source_record_sha256"}:
                raise ValueError("runtime parity 입력에는 식별자와 원문 digest만 허용됩니다.")
            item_id = row.get("item_id")
            if not isinstance(item_id, str) or not item_id or item_id in seen:
                raise ValueError("runtime parity item_id가 없거나 중복됩니다.")
            source_digest = _sha256_value(
                row.get("source_record_sha256"), "runtime parity source record"
            )
            seen.add(item_id)
            normalized_rows.append(
                {"item_id": item_id, "source_record_sha256": source_digest}
            )
        normalized[source] = normalized_rows
    return normalized


def _ordered_item_ids(sources: Mapping[str, Sequence[Mapping[str, str]]]) -> list[str]:
    return [str(row["item_id"]) for source in EXPECTED_SOURCES for row in sources[source]]


def _ordered_source_items(
    sources: Mapping[str, Sequence[Mapping[str, str]]],
) -> list[tuple[str, str]]:
    return [
        (str(row["item_id"]), source)
        for source in EXPECTED_SOURCES
        for row in sources[source]
    ]


def _normalized_v6_outputs(
    value: Sequence[Mapping[str, object]] | object,
    *,
    expected_items: list[tuple[str, str]],
    label: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ValueError(f"{label} v6 outputs가 배열이 아닙니다.")
    if len(value) != len(expected_items):
        raise ValueError(f"{label} v6 output 수가 reservation과 다릅니다.")
    normalized: list[dict[str, Any]] = []
    for (expected_id, source), raw in zip(expected_items, value, strict=True):
        row = _mapping(raw, f"{label} v6 output")
        if (
            set(row)
            != {
                "item_id",
                "label",
                "domain",
                "temperature",
                "neutral_threshold",
                "probabilities",
            }
            or row.get("item_id") != expected_id
        ):
            raise ValueError(f"{label} v6 output item 계약이 올바르지 않습니다.")
        domain = row.get("domain")
        allowed_domains = (
            {"NEWS_UNTARGETED", "NEWS_TARGETED"}
            if source == "NEWS"
            else {"DISCLOSURE_TARGETED"}
        )
        if domain not in allowed_domains:
            raise ValueError(f"{label} v6 source/domain 계약이 올바르지 않습니다.")
        temperature = _finite_number(row.get("temperature"), f"{label} temperature")
        threshold = _finite_number(
            row.get("neutral_threshold"),
            f"{label} neutral threshold",
        )
        if temperature <= 0.0 or not 0.0 <= threshold <= 1.0:
            raise ValueError(f"{label} v6 calibration 값이 올바르지 않습니다.")
        probabilities_raw = _mapping(row.get("probabilities"), f"{label} probabilities")
        if set(probabilities_raw) != set(LABEL_ORDER):
            raise ValueError(f"{label} v6 probability label 집합이 다릅니다.")
        probabilities = {
            name: _finite_number(probabilities_raw[name], f"{label} {name} probability")
            for name in LABEL_ORDER
        }
        if any(value < 0.0 or value > 1.0 for value in probabilities.values()) or not math.isclose(
            sum(probabilities.values()),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-6,
        ):
            raise ValueError(f"{label} v6 probability 분포가 올바르지 않습니다.")
        predicted = (
            "NEUTRAL"
            if probabilities["NEUTRAL"] >= threshold
            else (
                "NEGATIVE"
                if probabilities["NEGATIVE"] >= probabilities["POSITIVE"]
                else "POSITIVE"
            )
        )
        if row.get("label") != predicted:
            raise ValueError(f"{label} v6 label을 calibration 계약에서 재현할 수 없습니다.")
        normalized.append(
            {
                "item_id": expected_id,
                "label": predicted,
                "domain": domain,
                "temperature": temperature,
                "neutral_threshold": threshold,
                "probabilities": probabilities,
            }
        )
    return normalized


def _normalized_outputs(
    value: Sequence[Mapping[str, object]] | object,
    *,
    expected_item_ids: list[str],
    label: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ValueError(f"{label} outputs가 배열이 아닙니다.")
    if len(value) != len(expected_item_ids):
        raise ValueError(f"{label} output 수가 reservation과 다릅니다.")
    normalized: list[dict[str, Any]] = []
    for expected_id, raw in zip(expected_item_ids, value, strict=True):
        row = _mapping(raw, f"{label} output")
        if set(row) != {"item_id", "label", "logits"} or row.get("item_id") != expected_id:
            raise ValueError(f"{label} output item 계약이 올바르지 않습니다.")
        logits_value = row.get("logits")
        if not isinstance(logits_value, Sequence) or isinstance(logits_value, str | bytes):
            raise ValueError(f"{label} logits가 배열이 아닙니다.")
        logits = [_finite_number(item, f"{label} logit") for item in logits_value]
        if len(logits) != len(LABEL_ORDER):
            raise ValueError(f"{label} logits 차원이 label order와 다릅니다.")
        index = max(range(len(logits)), key=logits.__getitem__)
        predicted = LABEL_ORDER[index]
        if row.get("label") != predicted:
            raise ValueError(f"{label} label을 logits argmax에서 재현할 수 없습니다.")
        normalized.append({"item_id": expected_id, "label": predicted, "logits": logits})
    return normalized


def _validate_reservation_linkage(
    sources: Mapping[str, Sequence[Mapping[str, str]]],
    reservations: Mapping[str, Mapping[str, object]],
) -> None:
    if set(reservations) != set(EXPECTED_SOURCES):
        raise ValueError("candidate lock reservation source 집합이 다릅니다.")
    for source in EXPECTED_SOURCES:
        rows = list(sources[source])
        record = _mapping(reservations[source], f"{source} reservation commitment")
        if record.get("sample_count") != len(rows):
            raise ValueError(f"runtime parity {source} 표본 수가 candidate lock과 다릅니다.")
        item_digest = canonical_json_sha256(sorted(str(row["item_id"]) for row in rows))
        source_digest = canonical_json_sha256(
            sorted(
                (
                    {
                        "item_id": str(row["item_id"]),
                        "source_record_sha256": str(row["source_record_sha256"]),
                    }
                    for row in rows
                ),
                key=lambda row: row["item_id"],
            )
        )
        if (
            record.get("item_id_set_sha256") != item_digest
            or record.get("source_record_set_sha256") != source_digest
        ):
            raise ValueError(f"runtime parity {source} 입력이 잠긴 reservation과 다릅니다.")


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return dict(value)


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{label} 값이 숫자가 아닙니다.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} 값이 유한하지 않습니다.")
    return number


def _sha256_value(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} SHA-256 형식이 올바르지 않습니다.")
    return value


def evidence_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
