from __future__ import annotations

import importlib.util
import sys
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = PROJECT_ROOT / "scripts/evaluate_locked_kf_deberta_sentiment.py"
EXPECTED_EVALUATOR_SHA256 = (
    "5d62560687038a5177be47c38a7fe1c8b2a682e1fdb1c3b6d91e335a8dbbc625"
)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_locked_evaluator() -> ModuleType:
    if _file_sha256(EVALUATOR_PATH) != EXPECTED_EVALUATOR_SHA256:
        raise RuntimeError("복구 실행의 canonical evaluator hash가 candidate lock과 다릅니다.")
    spec = importlib.util.spec_from_file_location("locked_sentiment_evaluator", EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("canonical evaluator를 로드할 수 없습니다.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _declared_merged_directory(candidate_lock: dict[str, Any]) -> Path:
    base_source = candidate_lock.get("base_source")
    parity = candidate_lock.get("runtime_parity")
    if not isinstance(base_source, dict) or not isinstance(parity, dict):
        raise RuntimeError("복구할 DAPT/parity provenance가 없습니다.")
    manifest_record = base_source.get("artifact_manifest")
    source_files = base_source.get("merged_fp32_artifact_files")
    parity_base = parity.get("evaluator_base_encoder")
    if not all(isinstance(value, dict) for value in (manifest_record, source_files, parity_base)):
        raise RuntimeError("복구할 merged_fp32 commitment가 없습니다.")
    assert isinstance(manifest_record, dict)
    assert isinstance(source_files, dict)
    assert isinstance(parity_base, dict)
    manifest_value = manifest_record.get("path")
    parity_value = parity_base.get("path")
    if not isinstance(manifest_value, str) or not isinstance(parity_value, str):
        raise RuntimeError("복구할 merged_fp32 경로가 없습니다.")
    manifest_path = (PROJECT_ROOT / manifest_value).resolve(strict=True)
    declared = (manifest_path.parent / "merged_fp32").resolve(strict=True)
    parity_path = (PROJECT_ROOT / parity_value).resolve(strict=True)
    if declared != parity_path or declared.name != "merged_fp32":
        raise RuntimeError("DAPT manifest와 runtime parity의 merged_fp32 경로가 다릅니다.")
    if (
        manifest_path.stat().st_size != manifest_record.get("bytes")
        or _file_sha256(manifest_path) != manifest_record.get("sha256")
    ):
        raise RuntimeError("DAPT artifact manifest commitment가 다릅니다.")
    parity_files = parity_base.get("files")
    if not isinstance(parity_files, dict):
        raise RuntimeError("runtime parity base 파일 commitment가 없습니다.")
    for filename in ("config.json", "model.safetensors"):
        source_record = source_files.get(f"merged_fp32/{filename}")
        parity_record = parity_files.get(filename)
        path = declared / filename
        if (
            not isinstance(source_record, dict)
            or not isinstance(parity_record, dict)
            or source_record != parity_record
            or path.stat().st_size != parity_record.get("bytes")
            or _file_sha256(path) != parity_record.get("sha256")
        ):
            raise RuntimeError(f"merged_fp32 파일 commitment가 다릅니다: {filename}")
    return declared


def _verify_recursive_manifest(
    module: ModuleType, directory: Path, manifest: dict[str, Any]
) -> None:
    resolved_directory = directory.resolve(strict=True)
    if directory.is_symlink() or not resolved_directory.is_dir():
        raise ValueError(f"artifact 디렉터리가 없거나 symlink입니다: {directory}")
    for filename, expected in manifest.items():
        relative = Path(filename) if isinstance(filename, str) else Path("/")
        if (
            not isinstance(filename, str)
            or relative.is_absolute()
            or ".." in relative.parts
            or not isinstance(expected, dict)
        ):
            raise ValueError("artifact manifest 경로가 안전하지 않습니다.")
        path = resolved_directory / relative
        resolved_path = path.resolve(strict=True)
        if (
            path.is_symlink()
            or not resolved_path.is_file()
            or not resolved_path.is_relative_to(resolved_directory)
        ):
            raise ValueError(f"artifact 파일이 없거나 안전하지 않습니다: {filename}")
        expected_hash = module._sha256_value(expected.get("sha256"), filename)
        expected_bytes = expected.get("bytes")
        if (
            not isinstance(expected_bytes, int)
            or isinstance(expected_bytes, bool)
            or resolved_path.stat().st_size != expected_bytes
            or _file_sha256(resolved_path) != expected_hash
        ):
            raise ValueError(f"artifact 무결성 검증에 실패했습니다: {filename}")


def main() -> None:
    module = _load_locked_evaluator()
    original_attested = module.validate_attested_candidate
    original_artifact = module.validate_source_hierarchical_artifact
    original_legacy = module.load_legacy_diagnostic
    original_no_k = module.predict_v6_no_k_ablation

    def load_legacy_with_disclosure_target(path: Path, expected_source: str) -> Any:
        rows = original_legacy(path, expected_source)
        if expected_source != "DISCLOSURE":
            return rows
        samples = module.load_labeled_alerts(path)
        if len(rows) != len(samples):
            raise RuntimeError("기존 공시 진단셋 행 수가 로드 과정에서 달라졌습니다.")
        recovered: list[dict[str, Any]] = []
        for row, sample in zip(rows, samples, strict=True):
            target = (sample.stock_name or sample.stock_code or "").strip()
            if not target:
                raise RuntimeError("기존 공시 진단셋에 검증할 종목 식별자가 없습니다.")
            recovered.append({**row, "target_security": target})
        return recovered

    def validate_attested_with_recovery(
        *args: Any, **kwargs: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        candidate_lock, attestation = original_attested(*args, **kwargs)
        declared = _declared_merged_directory(candidate_lock)
        base_source = {**candidate_lock["base_source"], "merged_directory": str(declared)}
        candidate_lock = {**candidate_lock, "base_source": base_source}

        def validate_artifact_with_recovery(*artifact_args: Any, **artifact_kwargs: Any) -> Any:
            contract = original_artifact(*artifact_args, **artifact_kwargs)
            if contract.base_source_kind != "DAPT_MERGED_FP32":
                return contract
            return replace(
                contract,
                base_source={**contract.base_source, "merged_directory": str(declared)},
            )

        # 후보 검증 완료 후 예측 load에만 누락 필드를 주입한다.
        module.validate_source_hierarchical_artifact = validate_artifact_with_recovery
        return candidate_lock, attestation

    def predict_no_k_with_recursive_manifest(*args: Any, **kwargs: Any) -> Any:
        original_verifier = module._verify_file_manifest
        module._verify_file_manifest = lambda directory, manifest: _verify_recursive_manifest(
            module, directory, manifest
        )
        try:
            return original_no_k(*args, **kwargs)
        finally:
            module._verify_file_manifest = original_verifier

    module.validate_attested_candidate = validate_attested_with_recovery
    module.load_legacy_diagnostic = load_legacy_with_disclosure_target
    module.predict_v6_no_k_ablation = predict_no_k_with_recursive_manifest
    module.main()


if __name__ == "__main__":
    main()
