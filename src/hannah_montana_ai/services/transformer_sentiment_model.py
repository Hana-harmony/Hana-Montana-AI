from __future__ import annotations

import hmac
import json
import math
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.services.model import ModelArtifactInvalidError
from hannah_montana_ai.services.model_artifact_integrity import (
    verify_artifact_manifest,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    ARTIFACT_MANIFEST_SCHEMA_VERSION as V6_ARTIFACT_MANIFEST_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    ARTIFACT_SCHEMA_VERSION as V6_ARTIFACT_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    BENCHMARK_SCHEMA_VERSION as V6_BENCHMARK_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    TRAINING_SCHEMA_VERSION as V6_TRAINING_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    validate_source_hierarchical_activation,
    validate_source_hierarchical_artifact,
    validate_source_hierarchical_base_directory,
)
from hannah_montana_ai.services.sentiment_input import (
    encode_sentiment_input,
    sentiment_source_domain,
    validated_sentiment_logit_biases,
)
from hannah_montana_ai.services.sentiment_release import (
    LOCAL_ATTESTATION_MODE,
    SentimentReleaseError,
    validate_strict_sentiment_gate,
    verify_sentiment_release,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    SentimentInputContractError,
    SentimentPrediction,
    SourceHierarchicalSentimentRuntime,
    load_source_hierarchical_runtime,
    prediction_from_probabilities,
)

BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
BENCHMARK_SCHEMA_VERSION = "korean-finance-sentiment-benchmark/v4"
TRAINING_SCHEMA_VERSION = "kf-deberta-sentiment-training/v2"
ARTIFACT_SCHEMA_VERSION = "kf-deberta-sentiment-artifact/v2"
LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v1"
INPUT_FEATURE_VERSION = "source-target-prefix-head-tail/v2"
SUPPORTED_SOURCES = frozenset({"NEWS", "DISCLOSURE"})
SUPPORTED_CANDIDATES = frozenset({"kf_deberta_lora_locked"})
MAX_MODEL_VERSION_LENGTH = 240
MIN_MAX_LENGTH = 16
MAX_MAX_LENGTH = 512
MAX_JSON_REPORT_BYTES = 64 * 1024 * 1024
TRAINING_ARTIFACT_FILES = frozenset(
    {
        "adapter_config.json",
        "adapter_model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    }
)
LOCKED_ARTIFACT_FILES = TRAINING_ARTIFACT_FILES | {"hannah_metadata.json"}


class KfDebertaSentimentModel:
    def __init__(
        self,
        adapter_path: Path,
        training_report_path: Path,
        benchmark_report_path: Path,
        local_base_model_path: Path,
        *,
        release_current_path: Path | None = None,
        project_root: Path = Path("."),
        runtime_environment: str = "local",
        release_attestation_mode: str = LOCAL_ATTESTATION_MODE,
        release_public_key_path: Path | None = None,
        release_signer_key_id: str = "",
        expected_release_id: str = "",
        expected_git_commit: str = "",
    ) -> None:
        self.enabled = False
        self.version = "kf-deberta-sentiment-unavailable"
        self.max_length = 192
        self.transformer_weight = 1.0
        self.release_id = ""
        self.model_family = "kf-deberta-sequence-classification/v2"
        self._input_feature_version = ""
        self._logit_bias_by_domain: dict[str, tuple[float, ...]] = {}
        self._eligible_sources: frozenset[str] = frozenset()
        self._torch: Any = None
        self._tokenizer: Any = None
        self._model: Any = None
        self._v6_runtime: SourceHierarchicalSentimentRuntime | None = None
        release_active = False
        if release_current_path is not None and (
            release_current_path.exists() or release_current_path.is_symlink()
        ):
            try:
                release = verify_sentiment_release(
                    release_current_path,
                    local_base_model_path,
                    project_root=project_root,
                    runtime_environment=runtime_environment,
                    attestation_mode=release_attestation_mode,
                    public_key_path=release_public_key_path,
                    signer_key_id=release_signer_key_id,
                    expected_release_id=expected_release_id,
                    expected_git_commit=expected_git_commit,
                )
            except SentimentReleaseError as exception:
                raise ModelArtifactInvalidError(
                    f"활성 sentiment release 검증 실패: {exception}"
                ) from exception
            adapter_path = release.artifact_path
            training_report_path = release.training_report_path
            benchmark_report_path = release.benchmark_report_path
            local_base_model_path = release.base_model_path
            self.release_id = release.release_id
            release_active = True
        elif runtime_environment == "production":
            raise ModelArtifactInvalidError(
                "production에는 검증 가능한 sentiment current release가 필요합니다."
            )
        artifact_metadata = _read_json_object(adapter_path / "hannah_metadata.json")
        v6_artifact_declared = _declares_v6_artifact(adapter_path, artifact_metadata)
        preloaded_training_report = _read_json_object(training_report_path)
        preloaded_benchmark_report = _read_json_object(benchmark_report_path)
        v6_report_declared = bool(
            preloaded_training_report is not None
            and preloaded_training_report.get("schema_version") == V6_TRAINING_SCHEMA_VERSION
        ) or bool(
            preloaded_benchmark_report is not None
            and preloaded_benchmark_report.get("schema_version") == V6_BENCHMARK_SCHEMA_VERSION
        )
        if not all(
            path.exists() for path in (adapter_path, training_report_path, benchmark_report_path)
        ):
            if release_active or v6_artifact_declared or v6_report_declared:
                raise ModelArtifactInvalidError("활성 sentiment release 파일이 없습니다.")
            return
        training_report = preloaded_training_report
        benchmark_report = preloaded_benchmark_report
        if training_report is None or benchmark_report is None:
            if release_active or v6_artifact_declared:
                raise ModelArtifactInvalidError(
                    "활성 sentiment release report가 올바르지 않습니다."
                )
            return
        v6_requested = v6_artifact_declared or any(
            (
                training_report.get("schema_version") == V6_TRAINING_SCHEMA_VERSION,
                benchmark_report.get("schema_version") == V6_BENCHMARK_SCHEMA_VERSION,
                artifact_metadata is not None
                and artifact_metadata.get("schema_version") == V6_ARTIFACT_SCHEMA_VERSION,
            )
        )
        if v6_requested:
            try:
                contract = validate_source_hierarchical_artifact(
                    adapter_path,
                    training_report,
                )
                validate_source_hierarchical_activation(benchmark_report, contract)
                verified_base = validate_source_hierarchical_base_directory(local_base_model_path)
                runtime = load_source_hierarchical_runtime(
                    artifact_dir=contract.artifact_dir,
                    base_model_dir=verified_base,
                    max_length=contract.max_length,
                    calibration_by_domain=contract.calibration_by_domain,
                )
                post_load_contract = validate_source_hierarchical_artifact(
                    adapter_path,
                    training_report,
                )
                if not hmac.compare_digest(
                    contract.locked_manifest_sha256,
                    post_load_contract.locked_manifest_sha256,
                ):
                    raise ValueError("v6 sentiment artifact가 load 중 변경됐습니다.")
            except Exception as exception:
                raise ModelArtifactInvalidError(
                    f"v6 sentiment artifact 활성화 검증 실패: {exception}"
                ) from exception
            self._v6_runtime = runtime
            self.max_length = contract.max_length
            self.version = contract.version
            self.model_family = V6_MODEL_FAMILY
            self._input_feature_version = INPUT_FEATURE_VERSION
            self._eligible_sources = SUPPORTED_SOURCES
            self.enabled = True
            return
        if not _deployment_gate_passed(training_report, benchmark_report):
            if release_active:
                raise ModelArtifactInvalidError("활성 sentiment release gate 검증에 실패했습니다.")
            return

        training_manifest = training_report["artifact_files"]
        candidate_lock = benchmark_report["candidate_lock"]
        locked_manifest = _candidate_lock_value(candidate_lock, "artifact_files")
        if (
            not isinstance(locked_manifest, dict)
            or artifact_metadata is None
            or not verify_artifact_manifest(adapter_path, training_manifest)
            or not verify_artifact_manifest(adapter_path, locked_manifest)
            or not _artifact_metadata_matches(artifact_metadata, training_report)
        ):
            if release_active:
                raise ModelArtifactInvalidError("활성 sentiment release artifact가 다릅니다.")
            return

        # 기본 설치에서는 선택 의존성이 없으므로 기존 모델로 안전하게 축소 운용한다.
        try:
            import torch
            from peft import PeftModel
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ModuleNotFoundError as exception:
            if exception.name not in {"torch", "peft", "transformers"}:
                raise
            if release_active:
                raise ModelArtifactInvalidError(
                    "활성 sentiment release 실행 의존성이 없습니다."
                ) from exception
            return

        local_base = local_base_model_path.is_dir()
        base_reference = str(local_base_model_path) if local_base else BASE_MODEL
        base_options: dict[str, Any] = {
            "trust_remote_code": False,
            "local_files_only": local_base,
        }
        # 어댑터 경로는 배포 gate를 통과한 로컬 디렉터리만 허용한다.
        tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
            adapter_path,
            revision="local-verified-artifact",
            trust_remote_code=False,
            local_files_only=True,
        )
        base = AutoModelForSequenceClassification.from_pretrained(
            base_reference,
            revision=BASE_MODEL_REVISION if not local_base else "local-safe-artifact",
            num_labels=len(LABEL_ORDER),
            id2label={index: label for index, label in enumerate(LABEL_ORDER)},
            label2id={label: index for index, label in enumerate(LABEL_ORDER)},
            use_safetensors=local_base,
            **base_options,
        )
        model = PeftModel.from_pretrained(
            base,
            adapter_path,
            is_trainable=False,
            use_safetensors=True,
        )
        model.eval()
        self._torch = torch
        self._tokenizer = tokenizer
        self._model = model
        self.max_length = int(training_report["max_length"])
        self.version = str(artifact_metadata["version"])
        self._input_feature_version = str(artifact_metadata["input_feature_version"])
        self._logit_bias_by_domain = validated_sentiment_logit_biases(
            artifact_metadata["logit_bias_by_domain"]
        )
        self._eligible_sources = SUPPORTED_SOURCES
        self.enabled = True

    def predict(
        self,
        text: str,
        source_type: str = "NEWS",
        target_security: str = "",
    ) -> SentimentPrediction | None:
        if not self.enabled:
            return None
        v6_runtime = cast(
            SourceHierarchicalSentimentRuntime | None,
            getattr(self, "_v6_runtime", None),
        )
        if v6_runtime is not None:
            try:
                return v6_runtime.predict(text, source_type, target_security)
            except SentimentInputContractError:
                raise
            except Exception as exception:
                raise ModelArtifactInvalidError("v6 sentiment 추론에 실패했습니다.") from exception
        probabilities = self._legacy_probabilities(text, source_type, target_security)
        if probabilities is None:
            return None
        return prediction_from_probabilities(probabilities, source_type, target_security)

    def probabilities(
        self,
        text: str,
        source_type: str = "NEWS",
        target_security: str = "",
    ) -> dict[str, float] | None:
        prediction = self.predict(text, source_type, target_security)
        if prediction is None:
            return None
        return {
            str(label): probability
            for label, probability in prediction.calibrated_probabilities.items()
        }

    def _legacy_probabilities(
        self,
        text: str,
        source_type: str,
        target_security: str,
    ) -> dict[str, float] | None:
        if not self.enabled or self._model is None:
            return None
        normalized_source = source_type.strip().upper()
        if (
            normalized_source not in self._eligible_sources
            or self._input_feature_version != INPUT_FEATURE_VERSION
            or (normalized_source == "DISCLOSURE" and not target_security.strip())
        ):
            return None
        token_values = encode_sentiment_input(
            self._tokenizer,
            text,
            normalized_source,
            self.max_length,
            target_security,
        )
        encoded = {name: self._torch.tensor([values]) for name, values in token_values.items()}
        with self._torch.inference_mode():
            logits = self._model(**encoded).logits[0]
            domain = sentiment_source_domain(normalized_source, target_security)
            logits = logits + logits.new_tensor(self._logit_bias_by_domain[domain])
            values = self._torch.softmax(logits, dim=-1).cpu().tolist()
        probabilities = {
            label: float(probability)
            for label, probability in zip(LABEL_ORDER, values, strict=True)
        }
        return probabilities


def _declares_v6_artifact(
    adapter_path: Path,
    metadata: dict[str, Any] | None,
) -> bool:
    if metadata is not None and metadata.get("schema_version") == V6_ARTIFACT_SCHEMA_VERSION:
        return True
    manifest = _read_json_object(adapter_path / "manifest.json")
    return (
        manifest is not None
        and manifest.get("schema_version") == V6_ARTIFACT_MANIFEST_SCHEMA_VERSION
    )


def _deployment_gate_passed(
    training_report: dict[str, Any],
    benchmark_report: dict[str, Any],
) -> bool:
    try:
        validate_strict_sentiment_gate(benchmark_report)
    except SentimentReleaseError:
        return False
    gate = _mapping(benchmark_report.get("deployment_gate"))
    candidate_lock = _mapping(benchmark_report.get("candidate_lock"))
    source_gold = _mapping(benchmark_report.get("source_sealed_gold"))
    public_test = _mapping(benchmark_report.get("public_test"))
    if gate is None or candidate_lock is None or source_gold is None or public_test is None:
        return False
    if (
        training_report.get("schema_version") != TRAINING_SCHEMA_VERSION
        or benchmark_report.get("schema_version") != BENCHMARK_SCHEMA_VERSION
        or training_report.get("input_feature_version") != INPUT_FEATURE_VERSION
        or benchmark_report.get("input_feature_version") != INPUT_FEATURE_VERSION
        or training_report.get("base_model") != BASE_MODEL
        or training_report.get("base_model_revision") != BASE_MODEL_REVISION
        or not _label_order_matches(training_report.get("label_order"))
        or gate.get("eligible") is not True
        or gate.get("candidate_model") not in SUPPORTED_CANDIDATES
        or candidate_lock.get("schema_version") != LOCK_SCHEMA_VERSION
        or candidate_lock.get("selection_only") is not True
    ):
        return False

    version = training_report.get("version")
    locked_version = _candidate_lock_value(candidate_lock, "version")
    if (
        not isinstance(version, str)
        or not version
        or len(version) > MAX_MODEL_VERSION_LENGTH
        or locked_version != version
        or gate.get("candidate_version") != version
    ):
        return False
    max_length = training_report.get("max_length")
    if (
        isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not MIN_MAX_LENGTH <= max_length <= MAX_MAX_LENGTH
    ):
        return False

    training_biases = _validated_logit_biases_or_none(training_report.get("logit_bias_by_domain"))
    locked_biases = _validated_logit_biases_or_none(
        _candidate_lock_value(candidate_lock, "logit_bias_by_domain")
    )
    if training_biases is None or locked_biases != training_biases:
        return False

    training_manifest = _mapping(training_report.get("artifact_files"))
    locked_manifest = _mapping(_candidate_lock_value(candidate_lock, "artifact_files"))
    if (
        training_manifest is None
        or locked_manifest is None
        or not _valid_artifact_manifest(training_manifest, TRAINING_ARTIFACT_FILES)
        or not _valid_artifact_manifest(locked_manifest, LOCKED_ARTIFACT_FILES)
        or any(training_manifest[name] != locked_manifest[name] for name in TRAINING_ARTIFACT_FILES)
    ):
        return False
    computed_manifest_hash = _artifact_manifest_sha256(locked_manifest)
    declared_lock_hash = candidate_lock.get("artifact_manifest_sha256")
    declared_gate_hash = gate.get("candidate_artifact_manifest_sha256")
    if (
        not isinstance(declared_lock_hash, str)
        or not isinstance(declared_gate_hash, str)
        or not hmac.compare_digest(computed_manifest_hash, declared_lock_hash)
        or not hmac.compare_digest(computed_manifest_hash, declared_gate_hash)
    ):
        return False

    if not all(
        _source_gold_gate_passed(source_gold.get(source_type)) for source_type in SUPPORTED_SOURCES
    ):
        return False
    return True


def _source_gold_gate_passed(raw_metrics: object) -> bool:
    metrics = _mapping(raw_metrics)
    if metrics is None or not _sample_count_at_least(metrics.get("sample_count"), 500):
        return False
    accuracy = _score(metrics.get("accuracy"))
    macro_f1 = _score(metrics.get("macro_f1"))
    baseline = _mapping(metrics.get("baseline"))
    baseline_accuracy = _score(
        metrics.get("baseline_accuracy") if baseline is None else baseline.get("accuracy")
    )
    baseline_macro_f1 = _score(
        metrics.get("baseline_macro_f1") if baseline is None else baseline.get("macro_f1")
    )
    reference_accuracy = _score(metrics.get("kr_finbert_sc_accuracy"))
    reference_macro_f1 = _score(metrics.get("kr_finbert_sc_macro_f1"))
    pre_k_fnspid_macro_f1 = _score(metrics.get("pre_k_fnspid_macro_f1"))
    return (
        accuracy is not None
        and macro_f1 is not None
        and baseline_accuracy is not None
        and baseline_macro_f1 is not None
        and reference_accuracy is not None
        and reference_macro_f1 is not None
        and pre_k_fnspid_macro_f1 is not None
        and accuracy >= 0.90
        and macro_f1 >= 0.85
        and accuracy >= baseline_accuracy
        and macro_f1 >= baseline_macro_f1
        and accuracy >= reference_accuracy
        and macro_f1 >= reference_macro_f1
        and macro_f1 > pre_k_fnspid_macro_f1
    )


def _public_test_gate_passed(public_test: dict[str, Any]) -> bool:
    candidate = _mapping(public_test.get("candidate"))
    reference = _mapping(public_test.get("kr_finbert_sc"))
    macro_f1 = _score(
        public_test.get("macro_f1") if candidate is None else candidate.get("macro_f1")
    )
    reference_macro_f1 = _score(
        public_test.get("kr_finbert_sc_macro_f1")
        if reference is None
        else reference.get("macro_f1")
    )
    pre_k_fnspid_macro_f1 = _score(public_test.get("pre_k_fnspid_macro_f1"))
    return (
        _sample_count_at_least(public_test.get("sample_count"), 900)
        and macro_f1 is not None
        and reference_macro_f1 is not None
        and pre_k_fnspid_macro_f1 is not None
        and macro_f1 >= 0.85
        and macro_f1 >= reference_macro_f1
        and macro_f1 >= pre_k_fnspid_macro_f1
    )


def _artifact_metadata_matches(
    metadata: dict[str, Any],
    training_report: dict[str, Any],
) -> bool:
    metadata_biases = _validated_logit_biases_or_none(metadata.get("logit_bias_by_domain"))
    training_biases = _validated_logit_biases_or_none(training_report.get("logit_bias_by_domain"))
    return (
        metadata.get("schema_version") == ARTIFACT_SCHEMA_VERSION
        and metadata.get("version") == training_report.get("version")
        and metadata.get("base_model") == BASE_MODEL
        and metadata.get("base_model_revision") == BASE_MODEL_REVISION
        and _label_order_matches(metadata.get("label_order"))
        and metadata.get("max_length") == training_report.get("max_length")
        and metadata.get("input_feature_version") == INPUT_FEATURE_VERSION
        and metadata.get("artifact_files") == training_report.get("artifact_files")
        and metadata_biases is not None
        and metadata_biases == training_biases
    )


def _validated_logit_biases_or_none(
    value: object,
) -> dict[str, tuple[float, ...]] | None:
    try:
        return validated_sentiment_logit_biases(value)
    except ValueError:
        return None


def _candidate_lock_value(candidate_lock: dict[str, Any], name: str) -> object:
    if name in candidate_lock:
        return candidate_lock[name]
    winner = _mapping(candidate_lock.get("winner"))
    return None if winner is None else winner.get(name)


def _valid_artifact_manifest(
    manifest: dict[str, Any],
    required_files: frozenset[str],
) -> bool:
    if not required_files.issubset(manifest):
        return False
    for name, details in manifest.items():
        file_details = _mapping(details)
        if (
            not isinstance(name, str)
            or not name
            or file_details is None
            or isinstance(file_details.get("bytes"), bool)
            or not isinstance(file_details.get("bytes"), int)
            or file_details["bytes"] < 0
            or not _is_sha256(file_details.get("sha256"))
        ):
            return False
    return True


def _artifact_manifest_sha256(manifest: dict[str, Any]) -> str:
    canonical = json.dumps(
        manifest,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_JSON_REPORT_BYTES:
            return None
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    return _mapping(value)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"중복 JSON key는 허용하지 않습니다: {key}")
        result[key] = value
    return result


def _mapping(value: object) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _sample_count_at_least(value: object, minimum: int) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value >= minimum


def _label_order_matches(value: object) -> bool:
    return isinstance(value, list | tuple) and tuple(value) == LABEL_ORDER


def _score(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    score = float(value)
    return score if math.isfinite(score) and 0.0 <= score <= 1.0 else None


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(character in "0123456789abcdef" for character in value)


@lru_cache(maxsize=1)
def load_kf_deberta_sentiment_model(
    adapter_path: Path,
    training_report_path: Path,
    benchmark_report_path: Path,
    local_base_model_path: Path,
    *,
    release_current_path: Path | None = None,
    project_root: Path = Path("."),
    runtime_environment: str = "local",
    release_attestation_mode: str = LOCAL_ATTESTATION_MODE,
    release_public_key_path: Path | None = None,
    release_signer_key_id: str = "",
    expected_release_id: str = "",
    expected_git_commit: str = "",
) -> KfDebertaSentimentModel:
    return KfDebertaSentimentModel(
        adapter_path,
        training_report_path,
        benchmark_report_path,
        local_base_model_path,
        release_current_path=release_current_path,
        project_root=project_root,
        runtime_environment=runtime_environment,
        release_attestation_mode=release_attestation_mode,
        release_public_key_path=release_public_key_path,
        release_signer_key_id=release_signer_key_id,
        expected_release_id=expected_release_id,
        expected_git_commit=expected_git_commit,
    )
