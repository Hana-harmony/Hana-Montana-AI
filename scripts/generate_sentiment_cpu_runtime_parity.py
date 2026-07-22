from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.sentiment_artifact_contract import (
    ARTIFACT_SCHEMA_VERSION as V6_ARTIFACT_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    SourceHierarchicalArtifactContract,
    validate_source_hierarchical_artifact,
    validate_source_hierarchical_base_directory,
)
from hannah_montana_ai.services.sentiment_input import (
    encode_sentiment_input,
    sentiment_source_domain,
    validated_sentiment_logit_biases,
)
from hannah_montana_ai.services.sentiment_runtime_parity import (
    EVALUATOR_BATCH_SIZE,
    PACKAGED_RUNTIME_BATCH_SIZE,
    base_encoder_evidence,
    build_cpu_serving_parity_evidence,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    SentimentPrediction,
    load_source_hierarchical_runtime,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    canonical_json_sha256,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEWS_RESERVATION = (
    PROJECT_ROOT / "data/gold/confirmatory_sealed_test_review.jsonl"
)
DEFAULT_DISCLOSURE_RESERVATION = (
    PROJECT_ROOT / "data/gold/disclosure_confirmatory_sealed_test_review.jsonl"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "reports/sentiment-cpu-runtime-parity.json"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
RESERVATION_PARTITIONS = {
    "NEWS": "CONFIRMATORY_SEALED_TEST_REVIEW",
    "DISCLOSURE": "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
}
REQUIRED_CANDIDATE_FILES = (
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "hannah_metadata.json",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Gold 라벨을 열지 않고 evaluator CPU batch16과 packaged runtime CPU batch1의 "
            "예측 parity evidence를 생성한다."
        )
    )
    parser.add_argument("--candidate-artifact", type=Path, required=True)
    parser.add_argument("--evaluator-base-model", type=Path, required=True)
    parser.add_argument("--packaged-runtime-base-model", type=Path, required=True)
    parser.add_argument("--news-reservation", type=Path, default=DEFAULT_NEWS_RESERVATION)
    parser.add_argument(
        "--disclosure-reservation", type=Path, default=DEFAULT_DISCLOSURE_RESERVATION
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"runtime parity evidence가 이미 존재합니다: {args.output}")
    try:
        evidence = generate_evidence(
            candidate_artifact=args.candidate_artifact,
            evaluator_base_model=args.evaluator_base_model,
            packaged_runtime_base_model=args.packaged_runtime_base_model,
            news_reservation=args.news_reservation,
            disclosure_reservation=args.disclosure_reservation,
            project_root=PROJECT_ROOT,
        )
        _write_json_exclusive(args.output, evidence)
    except (OSError, RuntimeError, ValueError) as exception:
        raise SystemExit(str(exception)) from exception
    print(json.dumps(evidence, ensure_ascii=False))


def generate_evidence(
    *,
    candidate_artifact: Path,
    evaluator_base_model: Path,
    packaged_runtime_base_model: Path,
    news_reservation: Path,
    disclosure_reservation: Path,
    project_root: Path,
) -> dict[str, Any]:
    artifact = _project_directory(candidate_artifact, project_root, "candidate artifact")
    evaluator_base = _project_directory(
        evaluator_base_model, project_root, "evaluator base model"
    )
    runtime_base = _project_directory(
        packaged_runtime_base_model, project_root, "packaged runtime base model"
    )
    metadata = _load_json(artifact / "hannah_metadata.json", "candidate metadata")
    if metadata.get("schema_version") == V6_ARTIFACT_SCHEMA_VERSION:
        return _generate_v6_evidence(
            artifact=artifact,
            evaluator_base=evaluator_base,
            runtime_base=runtime_base,
            metadata=metadata,
            news_reservation=news_reservation,
            disclosure_reservation=disclosure_reservation,
            project_root=project_root,
        )
    version = metadata.get("version")
    max_length = metadata.get("max_length")
    if (
        not isinstance(version, str)
        or not version
        or isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not 16 <= max_length <= 512
    ):
        raise ValueError("candidate metadata version/max_length 계약이 올바르지 않습니다.")
    biases = validated_sentiment_logit_biases(metadata.get("logit_bias_by_domain"))
    reservations: dict[str, list[dict[str, Any]]] = {
        "NEWS": _load_unlabeled_reservation(
            _project_file(news_reservation, project_root, "NEWS reservation"), "NEWS"
        ),
        "DISCLOSURE": _load_unlabeled_reservation(
            _project_file(
                disclosure_reservation,
                project_root,
                "DISCLOSURE reservation",
            ),
            "DISCLOSURE",
        ),
    }
    all_rows = [row for source in ("NEWS", "DISCLOSURE") for row in reservations[source]]
    input_records = {
        source: [
            {
                "item_id": str(row["item_id"]),
                "source_record_sha256": str(row["source_record_sha256"]),
            }
            for row in reservations[source]
        ]
        for source in ("NEWS", "DISCLOSURE")
    }
    evaluator_outputs = _predict_cpu(
        all_rows,
        artifact,
        evaluator_base,
        max_length=max_length,
        logit_bias_by_domain=biases,
        batch_size=EVALUATOR_BATCH_SIZE,
    )
    runtime_outputs = _predict_cpu(
        all_rows,
        artifact,
        runtime_base,
        max_length=max_length,
        logit_bias_by_domain=biases,
        batch_size=PACKAGED_RUNTIME_BATCH_SIZE,
    )
    return build_cpu_serving_parity_evidence(
        candidate_version=version,
        candidate_artifact_manifest_sha256=_candidate_artifact_manifest_sha256(artifact),
        reservation_inputs=input_records,
        evaluator_outputs=evaluator_outputs,
        packaged_runtime_outputs=runtime_outputs,
        evaluator_base_model=base_encoder_evidence(evaluator_base, project_root),
        packaged_runtime_base_model=base_encoder_evidence(runtime_base, project_root),
        generated_at=datetime.now(UTC).isoformat(),
    )


def _generate_v6_evidence(
    *,
    artifact: Path,
    evaluator_base: Path,
    runtime_base: Path,
    metadata: dict[str, Any],
    news_reservation: Path,
    disclosure_reservation: Path,
    project_root: Path,
) -> dict[str, Any]:
    contract = validate_source_hierarchical_artifact(artifact)
    evaluator_base = validate_source_hierarchical_base_directory(evaluator_base)
    runtime_base = validate_source_hierarchical_base_directory(runtime_base)
    if contract.base_source_kind == "DAPT_MERGED_FP32":
        _validate_dapt_merged_base(
            contract.base_source,
            evaluator_base=evaluator_base,
            runtime_base=runtime_base,
            project_root=project_root,
        )
    elif contract.base_source_kind != "PINNED_RAW":
        raise ValueError("지원하지 않는 v6 base source입니다.")
    if metadata != contract.metadata:
        raise ValueError("검증 전후 v6 metadata가 변경되었습니다.")
    reservations: dict[str, list[dict[str, Any]]] = {
        "NEWS": _load_unlabeled_reservation(
            _project_file(news_reservation, project_root, "NEWS reservation"),
            "NEWS",
        ),
        "DISCLOSURE": _load_unlabeled_reservation(
            _project_file(
                disclosure_reservation,
                project_root,
                "DISCLOSURE reservation",
            ),
            "DISCLOSURE",
        ),
    }
    rows = [row for source in ("NEWS", "DISCLOSURE") for row in reservations[source]]
    inputs = {
        source: [
            {
                "item_id": str(row["item_id"]),
                "source_record_sha256": str(row["source_record_sha256"]),
            }
            for row in reservations[source]
        ]
        for source in ("NEWS", "DISCLOSURE")
    }
    evaluator_outputs = _predict_v6_cpu(
        rows,
        artifact,
        evaluator_base,
        contract=contract,
        batch_size=EVALUATOR_BATCH_SIZE,
    )
    runtime_outputs = _predict_v6_cpu(
        rows,
        artifact,
        runtime_base,
        contract=contract,
        batch_size=PACKAGED_RUNTIME_BATCH_SIZE,
    )
    return build_cpu_serving_parity_evidence(
        candidate_version=contract.version,
        candidate_artifact_manifest_sha256=contract.locked_manifest_sha256,
        candidate_model_family=V6_MODEL_FAMILY,
        base_source_kind=contract.base_source_kind,
        reservation_inputs=inputs,
        evaluator_outputs=evaluator_outputs,
        packaged_runtime_outputs=runtime_outputs,
        evaluator_base_model=base_encoder_evidence(evaluator_base, project_root),
        packaged_runtime_base_model=base_encoder_evidence(runtime_base, project_root),
        generated_at=datetime.now(UTC).isoformat(),
    )


def _validate_dapt_merged_base(
    base_source: dict[str, Any],
    *,
    evaluator_base: Path,
    runtime_base: Path,
    project_root: Path,
) -> Path:
    """DAPT manifest가 고정한 merged FP32 바이트만 허용한다."""
    manifest_record = base_source.get("artifact_manifest")
    merged_records = base_source.get("merged_fp32_artifact_files")
    if not isinstance(manifest_record, dict) or not isinstance(merged_records, dict):
        raise ValueError("DAPT base provenance manifest가 없습니다.")
    manifest_path_value = manifest_record.get("path")
    if not isinstance(manifest_path_value, str) or not manifest_path_value.strip():
        raise ValueError("DAPT base provenance manifest 경로가 없습니다.")
    manifest_path = _project_file(
        Path(manifest_path_value), project_root, "DAPT artifact manifest"
    )
    if (
        manifest_record.get("bytes") != manifest_path.stat().st_size
        or manifest_record.get("sha256") != _file_sha256(manifest_path)
    ):
        raise ValueError("DAPT artifact manifest 바이트가 provenance와 다릅니다.")

    declared_base = _project_directory(
        manifest_path.parent / "merged_fp32",
        project_root,
        "DAPT merged_fp32",
    )
    if evaluator_base != declared_base or runtime_base != declared_base:
        raise ValueError(
            "DAPT parity는 학습 provenance에 hash-bound된 merged_fp32만 허용합니다."
        )

    expected_names = {
        "merged_fp32/config.json",
        "merged_fp32/model.safetensors",
    }
    if set(merged_records) != expected_names:
        raise ValueError("DAPT merged_fp32 파일 commitment가 다릅니다.")
    for relative_name in sorted(expected_names):
        record = merged_records.get(relative_name)
        if not isinstance(record, dict):
            raise ValueError(f"DAPT merged_fp32 commitment가 없습니다: {relative_name}")
        file_path = _project_file(
            manifest_path.parent / relative_name,
            project_root,
            f"DAPT merged_fp32/{relative_name}",
        )
        if (
            record.get("bytes") != file_path.stat().st_size
            or record.get("sha256") != _file_sha256(file_path)
        ):
            raise ValueError(f"DAPT merged_fp32 바이트가 provenance와 다릅니다: {relative_name}")
    return declared_base


def _predict_v6_cpu(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    base_model_dir: Path,
    *,
    contract: SourceHierarchicalArtifactContract,
    batch_size: int,
) -> list[dict[str, Any]]:
    if batch_size not in {EVALUATOR_BATCH_SIZE, PACKAGED_RUNTIME_BATCH_SIZE}:
        raise ValueError("v6 runtime parity batch size가 canonical 계약과 다릅니다.")
    runtime = load_source_hierarchical_runtime(
        artifact_dir=artifact_dir,
        base_model_dir=base_model_dir,
        max_length=contract.max_length,
        calibration_by_domain=contract.calibration_by_domain,
    )
    outputs: list[dict[str, Any]] = []
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        predictions = runtime.predict_batch(
            tuple(
                (
                    str(row["text"]),
                    str(row["source_type"]),
                    _target_security(row),
                )
                for row in batch_rows
            )
        )
        for row, prediction in zip(batch_rows, predictions, strict=True):
            outputs.append(_v6_prediction_row(str(row["item_id"]), prediction))
    return outputs


def _v6_prediction_row(item_id: str, prediction: SentimentPrediction) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "label": prediction.label,
        "domain": prediction.domain,
        "temperature": prediction.temperature,
        "neutral_threshold": prediction.neutral_threshold,
        "probabilities": {
            label: float(prediction.calibrated_probabilities[label]) for label in LABEL_ORDER
        },
    }


def _predict_cpu(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    base_model_dir: Path,
    *,
    max_length: int,
    logit_bias_by_domain: dict[str, tuple[float, ...]],
    batch_size: int,
) -> list[dict[str, Any]]:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if batch_size not in {EVALUATOR_BATCH_SIZE, PACKAGED_RUNTIME_BATCH_SIZE}:
        raise ValueError("runtime parity batch size가 canonical 계약과 다릅니다.")
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")
    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615 - 검증 대상 로컬 artifact
        artifact_dir,
        revision="local-parity-artifact",
        trust_remote_code=False,
        local_files_only=True,
    )
    base = AutoModelForSequenceClassification.from_pretrained(  # nosec B615
        base_model_dir,
        revision="local-parity-base",
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
        trust_remote_code=False,
        local_files_only=True,
        use_safetensors=True,
    )
    model = PeftModel.from_pretrained(
        base,
        artifact_dir,
        is_trainable=False,
        local_files_only=True,
        use_safetensors=True,
    )
    model.to(device)
    model.eval()
    outputs: list[dict[str, Any]] = []
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        features = [
            encode_sentiment_input(
                tokenizer,
                str(row["text"]),
                str(row["source_type"]),
                max_length,
                _target_security(row),
            )
            for row in batch_rows
        ]
        padded = tokenizer.pad(features, padding=True, return_tensors="pt")
        encoded = {name: value.to(device) for name, value in padded.items()}
        with torch.inference_mode():
            logits = model(**encoded).logits
            bias = logits.new_tensor(
                [
                    logit_bias_by_domain[
                        sentiment_source_domain(
                            str(row["source_type"]), _target_security(row)
                        )
                    ]
                    for row in batch_rows
                ]
            )
            adjusted = (logits + bias).to(dtype=torch.float64).cpu()
        for row, values in zip(batch_rows, adjusted.tolist(), strict=True):
            index = max(range(len(values)), key=values.__getitem__)
            outputs.append(
                {
                    "item_id": str(row["item_id"]),
                    "label": LABEL_ORDER[index],
                    "logits": [float(value) for value in values],
                }
            )
    return outputs


def _load_unlabeled_reservation(path: Path, expected_source: str) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{expected_source} unlabeled reservation이 없습니다: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exception:
                raise ValueError(
                    f"{expected_source} reservation JSON이 올바르지 않습니다: {line_number}"
                ) from exception
            if (
                not isinstance(row, dict)
                or row.get("schema_version") != "k-fnspid-sentiment-review-row/v1"
                or row.get("source_type") != expected_source
                or row.get("partition") != RESERVATION_PARTITIONS[expected_source]
                or row.get("review_status") != "NEEDS_BLIND_REVIEW"
                or row.get("final_sentiment") not in {"", None}
                or _contains_opened_label(row)
            ):
                raise ValueError(
                    f"{expected_source} reservation이 unlabeled 계약을 위반했습니다: {line_number}"
                )
            source_digest = canonical_json_sha256(row)
            item_id = _review_item_id(row, source_digest)
            text = row.get("text", row.get("model_text", row.get("content")))
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"{expected_source} reservation 원문이 없습니다: {line_number}")
            rows.append(
                {
                    **row,
                    "text": text,
                    "item_id": item_id,
                    "source_record_sha256": source_digest,
                }
            )
    if not rows or len({str(row["item_id"]) for row in rows}) != len(rows):
        raise ValueError(f"{expected_source} reservation item이 비어 있거나 중복됩니다.")
    return rows


def _contains_opened_label(row: dict[str, Any]) -> bool:
    exact_fields = {
        "label",
        "gold_label",
        "prediction",
        "predicted_label",
        "probabilities",
        "logits",
    }
    for key, value in row.items():
        normalized = key.casefold()
        if normalized == "final_sentiment":
            continue
        if normalized in exact_fields or "sentiment" in normalized:
            if value is not None and value != "":
                return True
    return False


def _review_item_id(row: dict[str, Any], source_sha256: str) -> str:
    for field in ("review_key", "annotation_id", "item_id"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = row.get("document_id")
    target = row.get("target_security") or row.get("stock_code")
    target_value = target.strip() if isinstance(target, str) else "UNSPECIFIED"
    if isinstance(document_id, str) and document_id.strip():
        return f"{document_id.strip()}::{target_value}"
    content_hash = row.get("content_hash")
    if isinstance(content_hash, str) and content_hash.strip():
        return f"{content_hash.strip()}::{target_value}"
    return source_sha256


def _target_security(row: dict[str, Any]) -> str:
    for field in ("target_security", "stock_name", "stock_code"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _candidate_artifact_manifest_sha256(artifact: Path) -> str:
    manifest: dict[str, dict[str, int | str]] = {}
    for name in REQUIRED_CANDIDATE_FILES:
        path = artifact / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"candidate parity artifact가 부족합니다: {name}")
        manifest[name] = {"bytes": path.stat().st_size, "sha256": _file_sha256(path)}
    return canonical_json_sha256(manifest)


def _project_directory(path: Path, project_root: Path, label: str) -> Path:
    root = project_root.resolve(strict=True)
    absolute = path if path.is_absolute() else root / path
    try:
        relative = absolute.absolute().relative_to(root.absolute())
    except ValueError as exception:
        raise ValueError(f"{label} 경로가 프로젝트 밖입니다.") from exception
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"{label} 경로에 symlink가 있습니다.")
    resolved = absolute.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exception:
        raise ValueError(f"{label} 경로가 프로젝트 밖입니다.") from exception
    if resolved.is_symlink() or not resolved.is_dir():
        raise ValueError(f"{label}는 symlink가 아닌 디렉터리여야 합니다.")
    return resolved


def _project_file(path: Path, project_root: Path, label: str) -> Path:
    root = project_root.resolve(strict=True)
    absolute = path if path.is_absolute() else root / path
    try:
        relative = absolute.absolute().relative_to(root.absolute())
    except ValueError as exception:
        raise ValueError(f"{label} 경로가 프로젝트 밖입니다.") from exception
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"{label} 경로에 symlink가 있습니다.")
    resolved = absolute.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exception:
        raise ValueError(f"{label} 경로가 프로젝트 밖입니다.") from exception
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError(f"{label}는 symlink가 아닌 일반 파일이어야 합니다.")
    return resolved


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} 파일이 없습니다.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError(f"{label} JSON을 읽을 수 없습니다.") from exception
    if not isinstance(payload, dict):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return payload


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_exclusive(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"runtime parity evidence가 이미 존재합니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exception:
            raise ValueError(f"runtime parity evidence가 이미 존재합니다: {path}") from exception
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
