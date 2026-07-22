from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
import torch
from safetensors.torch import save_file
from torch import nn

from hannah_montana_ai.api import routes
from hannah_montana_ai.api.exceptions import ApiException, ErrorCode
from hannah_montana_ai.domain.schemas import AlertAnalysisRequest
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model import ModelArtifactInvalidError
from hannah_montana_ai.services.sentiment_artifact_contract import (
    ARTIFACT_MANIFEST_SCHEMA_VERSION,
    ARTIFACT_SCHEMA_VERSION,
    BASE_MODEL,
    BASE_MODEL_REVISION,
    BASE_MODEL_WEIGHT_FILENAME,
    BASE_MODEL_WEIGHT_SHA256,
    CANDIDATE_MODEL,
    EXPECTED_HEAD_ARCHITECTURE,
    EXPECTED_HEAD_TENSOR_CONTRACT,
    MODEL_FAMILY,
    RUNTIME_LOADER_SCHEMA_VERSION,
    TRAINING_SCHEMA_VERSION,
    SentimentArtifactContractError,
    canonical_manifest_sha256,
    validate_source_hierarchical_artifact,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    DOMAIN_ORDER,
    HEAD_ARTIFACT_FILENAME,
    DomainCalibration,
    SentimentInputContractError,
    SentimentPrediction,
    SourceHierarchicalRuntimeError,
    build_source_hierarchical_classifier,
    calibrated_sentiment_prediction,
    compose_hierarchical_log_probabilities,
    load_source_hierarchical_heads,
    source_hierarchical_head_state_dict,
    strict_sentiment_domain,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    KfDebertaSentimentModel,
)


class TinyEncoder(nn.Module):
    def __init__(self, hidden_size: int = 4) -> None:
        super().__init__()
        self.embedding = nn.Embedding(32, hidden_size)
        self.config = SimpleNamespace(hidden_size=hidden_size)

    def forward(self, input_ids: torch.Tensor, **_kwargs: Any) -> Any:
        return SimpleNamespace(last_hidden_state=self.embedding(input_ids))


class TinyTokenizer:
    cls_token_id = 1
    sep_token_id = 2
    model_input_names = ["input_ids", "attention_mask"]

    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        assert add_special_tokens is False
        return [3 + ord(character) % 20 for character in text]

    def num_special_tokens_to_add(self, *, pair: bool) -> int:
        assert pair is False
        return 2


def _training_module() -> ModuleType:
    name = "train_kf_deberta_sentiment_v6"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = Path("scripts/train_kf_deberta_sentiment_v6.py")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _calibration() -> dict[str, dict[str, float | int | str]]:
    return {
        domain: {
            "temperature": 1.0,
            "neutral_threshold": 0.5,
            "sample_count": 30,
            "fit_status": "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK",
        }
        for domain in DOMAIN_ORDER
    }


def _base_source() -> dict[str, Any]:
    return {
        "repository": BASE_MODEL,
        "revision": BASE_MODEL_REVISION,
        "source_weight_filename": BASE_MODEL_WEIGHT_FILENAME,
        "source_weight_sha256": BASE_MODEL_WEIGHT_SHA256,
        "verified_cache_path": None,
        "weights_only": True,
        "trust_remote_code": False,
    }


def _commitments() -> dict[str, dict[str, int | str]]:
    names = (
        "TRAIN",
        "CHECKPOINT",
        "CALIBRATION",
        "SELECTION",
        "NEWS_CONFIRMATORY_RESERVATION",
        "DISCLOSURE_CONFIRMATORY_RESERVATION",
    )
    return {
        name: {"row_count": index + 1, "sha256": f"{index + 1:064x}"}
        for index, name in enumerate(names)
    }


def _file_record(path: Path) -> dict[str, int | str]:
    content = path.read_bytes()
    return {"bytes": len(content), "sha256": sha256(content).hexdigest()}


def _artifact_records(directory: Path) -> dict[str, dict[str, int | str]]:
    return {
        path.relative_to(directory).as_posix(): _file_record(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _write_v6_fixture(
    root: Path,
) -> tuple[Path, Path, Path, Path, dict[str, Any]]:
    artifact = root / "artifact"
    adapter = artifact / "adapter"
    adapter.mkdir(parents=True)
    adapter_config = {
        "peft_type": "LORA",
        "task_type": "FEATURE_EXTRACTION",
        "inference_mode": True,
        "r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.08,
        "target_modules": ["query_proj", "key_proj", "value_proj", "dense"],
        "layers_to_transform": list(range(12)),
        "layers_pattern": "layer",
        "modules_to_save": None,
    }
    (adapter / "adapter_config.json").write_text(
        json.dumps(adapter_config),
        encoding="utf-8",
    )
    save_file({"adapter": torch.ones(1)}, adapter / "adapter_model.safetensors")
    (artifact / "tokenizer.json").write_text("{}\n", encoding="utf-8")
    (artifact / "tokenizer_config.json").write_text("{}\n", encoding="utf-8")

    torch.manual_seed(7)
    model = build_source_hierarchical_classifier(TinyEncoder(), 4, dropout=0.0)
    save_file(
        {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in source_hierarchical_head_state_dict(model).items()
        },
        artifact / HEAD_ARTIFACT_FILENAME,
    )

    version = "hana-montana-kf-deberta-k-fnspid-sentiment-v6-seed17-test"
    base_source = _base_source()
    runtime_contract = {
        "schema_version": RUNTIME_LOADER_SCHEMA_VERSION,
        "base_source": base_source,
        "adapter_path": "adapter",
        "heads_path": HEAD_ARTIFACT_FILENAME,
        "tokenizer_source": "artifact-root",
        "domain_order": list(DOMAIN_ORDER),
        "domain_required": True,
        "unknown_domain_behavior": "FAIL_CLOSED",
        "pooling": "last_hidden_state_cls",
        "head_tensor_contract": EXPECTED_HEAD_TENSOR_CONTRACT,
        "head_architecture": EXPECTED_HEAD_ARCHITECTURE,
        "composition": {
            "NEGATIVE": "log_sigmoid(boundary)+log_softmax(direction)[0]",
            "NEUTRAL": "log_sigmoid(-boundary)",
            "POSITIVE": "log_sigmoid(boundary)+log_softmax(direction)[1]",
        },
        "calibration": _calibration(),
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "max_length": 64,
    }
    metadata = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "version": version,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "base_source_kind": "PINNED_RAW",
        "label_order": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
        "runtime_loader_contract": runtime_contract,
        "prepared_partition_commitments": _commitments(),
        "selected_stage": "STAGE1_DOMAIN_BALANCED_FULL",
        "trained_at": datetime.now(UTC).isoformat(),
    }
    (artifact / "hannah_metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )
    artifact_files = _artifact_records(artifact)
    manifest_document = {
        "schema_version": ARTIFACT_MANIFEST_SCHEMA_VERSION,
        "status": "ATOMIC_COMPLETE",
        "generated_at": datetime.now(UTC).isoformat(),
        "artifact_files": artifact_files,
        "safe_serialization_only": True,
        "symlinks_allowed": False,
        "overwrite_allowed": False,
    }
    (artifact / "manifest.json").write_text(
        json.dumps(manifest_document),
        encoding="utf-8",
    )

    training = {
        **metadata,
        "schema_version": TRAINING_SCHEMA_VERSION,
        "base_source": base_source,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "artifact_files": artifact_files,
    }
    training_path = root / "training.json"
    training_path.write_text(json.dumps(training), encoding="utf-8")

    locked_manifest = dict(artifact_files)
    locked_manifest["manifest.json"] = _file_record(artifact / "manifest.json")
    locked_hash = canonical_manifest_sha256(locked_manifest)
    benchmark = {
        "schema_version": "korean-finance-sentiment-benchmark/v5",
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "candidate_lock": {
            "schema_version": "sentiment-candidate-lock/v2",
            "selection_only": True,
            "version": version,
            "model_family": MODEL_FAMILY,
            "artifact_files": locked_manifest,
            "artifact_manifest_sha256": locked_hash,
        },
        "source_sealed_gold": {
            source: {"sample_count": 500, "accuracy": 0.91, "macro_f1": 0.86}
            for source in ("NEWS", "DISCLOSURE")
        },
        "deployment_gate": {
            "eligible": True,
            "candidate_model": CANDIDATE_MODEL,
            "candidate_model_family": MODEL_FAMILY,
            "candidate_version": version,
            "candidate_artifact_manifest_sha256": locked_hash,
        },
    }
    benchmark_path = root / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")

    base = root / "base"
    base.mkdir()
    (base / "config.json").write_text("{}\n", encoding="utf-8")
    save_file({"weight": torch.ones(1)}, base / "model.safetensors")
    return artifact, training_path, benchmark_path, base, training


def _refresh_v6_fixture(
    artifact: Path,
    training_path: Path,
    benchmark_path: Path,
) -> None:
    manifest_path = artifact / "manifest.json"
    manifest_path.unlink(missing_ok=True)
    artifact_files = _artifact_records(artifact)
    manifest_document = {
        "schema_version": ARTIFACT_MANIFEST_SCHEMA_VERSION,
        "status": "ATOMIC_COMPLETE",
        "generated_at": datetime.now(UTC).isoformat(),
        "artifact_files": artifact_files,
        "safe_serialization_only": True,
        "symlinks_allowed": False,
        "overwrite_allowed": False,
    }
    manifest_path.write_text(json.dumps(manifest_document), encoding="utf-8")

    training = json.loads(training_path.read_text(encoding="utf-8"))
    training["artifact_files"] = artifact_files
    training_path.write_text(json.dumps(training), encoding="utf-8")
    locked_manifest = dict(artifact_files)
    locked_manifest["manifest.json"] = _file_record(manifest_path)
    locked_hash = canonical_manifest_sha256(locked_manifest)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    benchmark["candidate_lock"]["artifact_files"] = locked_manifest
    benchmark["candidate_lock"]["artifact_manifest_sha256"] = locked_hash
    benchmark["deployment_gate"]["candidate_artifact_manifest_sha256"] = locked_hash
    benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")


def _write_real_v6_fixture(root: Path) -> tuple[Path, Path, Path, Path]:
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import BertTokenizerFast, DebertaV2Config, DebertaV2Model

    artifact, training_path, benchmark_path, base, _ = _write_v6_fixture(root)
    for path in base.iterdir():
        path.unlink()
    base_model = DebertaV2Model(
        DebertaV2Config(
            vocab_size=32,
            hidden_size=12,
            num_hidden_layers=12,
            num_attention_heads=3,
            intermediate_size=16,
        )
    )
    base_model.save_pretrained(base, safe_serialization=True)
    base_model.name_or_path = str(base)
    base_model.config._name_or_path = str(base)
    encoder = get_peft_model(
        base_model,
        LoraConfig(
            task_type=TaskType.FEATURE_EXTRACTION,
            r=16,
            lora_alpha=32,
            lora_dropout=0.08,
            target_modules=["query_proj", "key_proj", "value_proj", "dense"],
            layers_to_transform=list(range(12)),
            layers_pattern="layer",
        ),
    )
    adapter = artifact / "adapter"
    for path in adapter.iterdir():
        path.unlink()
    encoder.save_pretrained(adapter, safe_serialization=True)
    tokenizer = BertTokenizerFast(
        vocab={
            "[PAD]": 0,
            "[UNK]": 1,
            "[CLS]": 2,
            "[SEP]": 3,
            "[MASK]": 4,
            "영업": 5,
            "이익": 6,
            "개선": 7,
        }
    )
    tokenizer.save_pretrained(artifact)
    serving_model = build_source_hierarchical_classifier(encoder, 12, dropout=0.0)
    save_file(
        {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in source_hierarchical_head_state_dict(serving_model).items()
        },
        artifact / HEAD_ARTIFACT_FILENAME,
    )
    _refresh_v6_fixture(artifact, training_path, benchmark_path)
    return artifact, training_path, benchmark_path, base


def test_calibration_threshold_label_is_not_probability_argmax() -> None:
    calibration = {
        domain: DomainCalibration(1.0, 0.5, 30, "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK")
        for domain in DOMAIN_ORDER
    }
    prediction = calibrated_sentiment_prediction(
        [torch.log(torch.tensor(value)).item() for value in (0.3, 0.4, 0.3)],
        "NEWS_UNTARGETED",
        calibration,
    )

    probabilities = prediction.calibrated_probabilities
    assert max(probabilities, key=lambda label: probabilities[label]) == "NEUTRAL"
    assert prediction.label == "NEGATIVE"
    assert prediction.neutral_threshold == 0.5


def test_domain_contract_fails_closed_for_unknown_and_untargeted_disclosure() -> None:
    assert strict_sentiment_domain("NEWS", "") == "NEWS_UNTARGETED"
    assert strict_sentiment_domain("NEWS", "005930") == "NEWS_TARGETED"
    with pytest.raises(SentimentInputContractError, match="target_security"):
        strict_sentiment_domain("DISCLOSURE", "")
    with pytest.raises(SentimentInputContractError, match="source_type"):
        strict_sentiment_domain("BLOG", "005930")


def test_common_model_is_numerically_compatible_with_training_model() -> None:
    training_module = _training_module()

    torch.manual_seed(11)
    training_model = training_module.SourceHierarchicalClassifier(
        TinyEncoder(),
        4,
        dropout=0.0,
    )
    serving_model = build_source_hierarchical_classifier(TinyEncoder(), 4, dropout=0.0)
    serving_model.load_state_dict(training_model.state_dict(), strict=True)
    inputs = {
        "input_ids": torch.tensor([[1, 2, 3], [3, 2, 1], [2, 2, 2]]),
        "attention_mask": torch.ones(3, 3, dtype=torch.long),
        "domain_ids": torch.tensor([0, 1, 2]),
    }

    training_output = training_model(**inputs)
    serving_output = serving_model(**inputs)

    assert torch.equal(training_output.boundary_logits, serving_output.boundary_logits)
    assert torch.equal(training_output.direction_logits, serving_output.direction_logits)
    assert torch.equal(training_output.logits, serving_output.logits)
    assert torch.allclose(
        compose_hierarchical_log_probabilities(
            serving_output.boundary_logits,
            serving_output.direction_logits,
        )
        .exp()
        .sum(dim=-1),
        torch.ones(3),
        atol=1e-6,
    )


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS가 필요합니다.")
def test_source_residual_routing_forward_and_backward_on_mps() -> None:
    device = torch.device("mps")
    model = build_source_hierarchical_classifier(TinyEncoder(), 4, dropout=0.0).to(
        device
    )
    output = model(
        input_ids=torch.tensor([[1, 2, 3], [3, 2, 1], [2, 2, 2]], device=device),
        attention_mask=torch.ones(3, 3, dtype=torch.long, device=device),
        domain_ids=torch.tensor([0, 1, 2], device=device),
    )

    output.logits.sum().backward()

    assert output.logits.shape == (3, 3)
    assert all(
        parameter.grad is not None and bool(torch.isfinite(parameter.grad).all())
        for parameter in model.domain_residuals.parameters()
    )


def test_head_safetensors_roundtrip_and_tamper_rejection(tmp_path: Path) -> None:
    source = build_source_hierarchical_classifier(TinyEncoder(), 4, dropout=0.0)
    target = build_source_hierarchical_classifier(TinyEncoder(), 4, dropout=0.0)
    path = tmp_path / "heads.safetensors"
    source_state = source_hierarchical_head_state_dict(source)
    save_file(source_state, path)

    load_source_hierarchical_heads(target, path)

    assert all(
        torch.equal(source_state[name], source_hierarchical_head_state_dict(target)[name])
        for name in source_state
    )
    save_file({"unexpected": torch.ones(1)}, path)
    with pytest.raises(SourceHierarchicalRuntimeError, match="tensor"):
        load_source_hierarchical_heads(target, path)
    non_finite = {
        name: tensor.detach().clone() for name, tensor in source_state.items()
    }
    first_name = next(iter(non_finite))
    non_finite[first_name].reshape(-1)[0] = torch.nan
    save_file(non_finite, path)
    with pytest.raises(SourceHierarchicalRuntimeError, match="tensor"):
        load_source_hierarchical_heads(target, path)


def test_artifact_contract_rejects_nested_file_tamper(tmp_path: Path) -> None:
    artifact, training_path, _, _, training = _write_v6_fixture(tmp_path)

    contract = validate_source_hierarchical_artifact(artifact, training)

    assert contract.locked_manifest["manifest.json"] == _file_record(artifact / "manifest.json")
    (artifact / "adapter/adapter_config.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(SentimentArtifactContractError, match="hash"):
        validate_source_hierarchical_artifact(
            artifact,
            json.loads(training_path.read_text(encoding="utf-8")),
        )


def test_v1_schema_and_legacy_head_filename_fail_closed(tmp_path: Path) -> None:
    schema_root = tmp_path / "schema"
    artifact, training_path, benchmark_path, _, _ = _write_v6_fixture(schema_root)
    metadata_path = artifact / "hannah_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["schema_version"] = "kf-deberta-source-hierarchical-sentiment-artifact/v1"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _refresh_v6_fixture(artifact, training_path, benchmark_path)

    with pytest.raises(SentimentArtifactContractError, match="metadata"):
        validate_source_hierarchical_artifact(artifact)

    head_root = tmp_path / "head"
    artifact, training_path, benchmark_path, _, _ = _write_v6_fixture(head_root)
    (artifact / HEAD_ARTIFACT_FILENAME).rename(
        artifact / "source_hierarchical_heads.safetensors"
    )
    _refresh_v6_fixture(artifact, training_path, benchmark_path)

    with pytest.raises(SentimentArtifactContractError, match="필수 파일"):
        validate_source_hierarchical_artifact(artifact)


def test_artifact_contract_rejects_symlink_and_traversal(tmp_path: Path) -> None:
    symlink_root = tmp_path / "symlink"
    artifact, _, _, _, training = _write_v6_fixture(symlink_root)
    tokenizer = artifact / "tokenizer.json"
    outside = tmp_path / "outside.json"
    outside.write_bytes(tokenizer.read_bytes())
    tokenizer.unlink()
    tokenizer.symlink_to(outside)
    with pytest.raises(SentimentArtifactContractError, match="symlink"):
        validate_source_hierarchical_artifact(artifact, training)

    traversal_root = tmp_path / "traversal"
    artifact, _, _, _, _ = _write_v6_fixture(traversal_root)
    manifest_path = artifact / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_files"]["../escape"] = {
        "bytes": 0,
        "sha256": "0" * 64,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SentimentArtifactContractError, match="상대 경로"):
        validate_source_hierarchical_artifact(artifact)


def test_v6_runtime_roundtrip_returns_explicit_calibrated_prediction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact, training_path, benchmark_path, base, _ = _write_v6_fixture(tmp_path)
    import peft
    import transformers

    monkeypatch.setattr(
        transformers.AutoTokenizer,
        "from_pretrained",
        staticmethod(lambda *_args, **_kwargs: TinyTokenizer()),
    )
    monkeypatch.setattr(
        transformers.AutoModel,
        "from_pretrained",
        staticmethod(lambda *_args, **_kwargs: TinyEncoder()),
    )
    monkeypatch.setattr(
        peft.PeftModel,
        "from_pretrained",
        staticmethod(lambda encoder, *_args, **_kwargs: encoder),
    )

    model = KfDebertaSentimentModel(
        artifact,
        training_path,
        benchmark_path,
        base,
        runtime_environment="test",
    )
    prediction = model.predict("영업이익이 개선됐다", "NEWS", "삼성전자")

    assert model.enabled is True
    assert model.model_family == MODEL_FAMILY
    assert isinstance(prediction, SentimentPrediction)
    assert prediction.domain == "NEWS_TARGETED"
    assert abs(sum(prediction.calibrated_probabilities.values()) - 1.0) < 1e-6
    assert model.probabilities("영업이익이 개선됐다", "NEWS", "삼성전자") is not None
    with pytest.raises(SentimentInputContractError, match="target_security"):
        model.predict("유상증자 결정", "DISCLOSURE", "")


def test_v6_runtime_real_peft_safetensors_roundtrip(tmp_path: Path) -> None:
    artifact, training_path, benchmark_path, base = _write_real_v6_fixture(tmp_path)

    model = KfDebertaSentimentModel(
        artifact,
        training_path,
        benchmark_path,
        base,
        runtime_environment="test",
    )
    prediction = model.predict("영업 이익 개선", "NEWS", "삼성전자")

    assert model.enabled is True
    assert isinstance(prediction, SentimentPrediction)
    assert prediction.domain == "NEWS_TARGETED"
    assert abs(sum(prediction.calibrated_probabilities.values()) - 1.0) < 1e-6


def test_v6_artifact_missing_report_and_load_failure_do_not_downgrade(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact, training_path, benchmark_path, base, _ = _write_v6_fixture(tmp_path)
    with pytest.raises(ModelArtifactInvalidError, match="파일"):
        KfDebertaSentimentModel(
            artifact,
            tmp_path / "missing-training.json",
            benchmark_path,
            base,
            runtime_environment="test",
        )

    import transformers

    monkeypatch.setattr(
        transformers.AutoTokenizer,
        "from_pretrained",
        staticmethod(lambda *_args, **_kwargs: TinyTokenizer()),
    )
    monkeypatch.setattr(
        transformers.AutoModel,
        "from_pretrained",
        staticmethod(lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("broken"))),
    )
    with pytest.raises(ModelArtifactInvalidError, match="활성화"):
        KfDebertaSentimentModel(
            artifact,
            training_path,
            benchmark_path,
            base,
            runtime_environment="test",
        )


def test_analyzer_respects_explicit_v6_label_without_baseline_or_argmax() -> None:
    analyzer = object.__new__(AlertAnalyzer)
    prediction = SentimentPrediction(
        label="NEGATIVE",
        calibrated_probabilities={"NEGATIVE": 0.20, "NEUTRAL": 0.70, "POSITIVE": 0.10},
        domain="NEWS_UNTARGETED",
        temperature=1.0,
        neutral_threshold=0.8,
    )
    analyzer.sentiment_transformer = SimpleNamespace(
        enabled=True,
        release_id="release-v6",
        model_family=MODEL_FAMILY,
        predict=lambda *_args: prediction,
    )
    analyzer.model = SimpleNamespace(
        sentiment_probabilities=lambda _text: pytest.fail("baseline must not run")
    )
    analyzer.sentiment_stacker = SimpleNamespace(enabled=False)

    actual = analyzer._sentiment_prediction("테스트", "NEWS", "")

    assert actual is prediction
    assert actual.label == "NEGATIVE"
    probabilities = actual.calibrated_probabilities
    assert max(probabilities, key=lambda label: probabilities[label]) == "NEUTRAL"


def test_analyzer_does_not_downgrade_active_v6_none_to_baseline() -> None:
    analyzer = object.__new__(AlertAnalyzer)
    analyzer.sentiment_transformer = SimpleNamespace(
        enabled=True,
        release_id="",
        model_family=MODEL_FAMILY,
        predict=lambda *_args: None,
    )
    analyzer.model = SimpleNamespace(
        sentiment_probabilities=lambda _text: pytest.fail("baseline must not run")
    )
    analyzer.sentiment_stacker = SimpleNamespace(enabled=False)

    with pytest.raises(ModelArtifactInvalidError, match="반환하지 않았"):
        analyzer._sentiment_prediction("테스트", "NEWS", "")


@pytest.mark.parametrize(
    ("exception", "expected_code", "failure_reason"),
    [
        (
            SentimentInputContractError("target_security required"),
            ErrorCode.VALIDATION_FAILED,
            "sentiment_input_contract_error",
        ),
        (
            ModelArtifactInvalidError("runtime failed"),
            ErrorCode.MODEL_UNAVAILABLE,
            "sentiment_runtime_unavailable",
        ),
    ],
)
def test_analysis_api_maps_v6_contract_failures_without_generic_500(
    exception: Exception,
    expected_code: ErrorCode,
    failure_reason: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failures: list[str] = []

    def fail_analysis(_request: AlertAnalysisRequest) -> None:
        raise exception

    monkeypatch.setattr(
        routes,
        "get_analyzer",
        lambda: SimpleNamespace(analyze=fail_analysis),
    )
    monkeypatch.setattr(
        routes,
        "get_audit_logger",
        lambda: SimpleNamespace(
            record_failure=lambda **values: failures.append(values["failure_reason"])
        ),
    )
    request = AlertAnalysisRequest(
        source_type="DISCLOSURE",
        title="유상증자 결정",
        original_url="https://example.com/disclosure/1",
    )

    with pytest.raises(ApiException) as raised:
        routes.analyze_alert(request)

    assert raised.value.error_code is expected_code
    assert failures == [failure_reason]
