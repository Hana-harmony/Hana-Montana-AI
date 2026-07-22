from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
import torch
from torch import nn
from transformers import BertConfig, BertModel, BertTokenizerFast

from hannah_montana_ai.services.kr_finbert_sc_v6_baseline import (
    ARTIFACT_SCHEMA_VERSION,
    BASE_MODEL,
    BASE_MODEL_FILES_SHA256,
    BASE_MODEL_REVISION,
    MODEL_FAMILY,
    RUNTIME_SCHEMA_VERSION,
    KrFinBertBaselineArtifactError,
    load_kr_finbert_sc_v6_runtime,
    validate_kr_finbert_sc_v6_artifact,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    ANCHOR_DOMAIN,
    DOMAIN_ORDER,
    HEAD_ARCHITECTURE_VERSION,
    HEAD_ARTIFACT_FILENAME,
    INPUT_FEATURE_VERSION,
    LABEL_ORDER,
    RESIDUAL_DOMAINS,
    build_source_hierarchical_classifier,
)
from hannah_montana_ai.training.sentiment_gold_provenance import (
    DEFAULT_DISCLOSURE_AUXILIARY_PROVENANCE,
    DEFAULT_DISCLOSURE_DEVELOPMENT_PROVENANCE,
    DEFAULT_NEWS_AUXILIARY_PROVENANCE,
    DEFAULT_NEWS_DEVELOPMENT_PROVENANCE,
    DEFAULT_TRAIN_PROVENANCE,
)
from hannah_montana_ai.training.sentiment_v6_baseline_commitment import (
    BASELINE_MODEL_NAME,
    validate_v6_kr_finbert_sc_baseline_commitment,
)


def _module() -> ModuleType:
    name = "train_kr_finbert_sc_sentiment_v6"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = Path("scripts/train_kr_finbert_sc_sentiment_v6.py").resolve()
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _calibration() -> dict[str, dict[str, float | int | str]]:
    return {
        domain: {
            "temperature": 1.0,
            "neutral_threshold": 0.5,
            "sample_count": 0,
            "fit_status": "INSUFFICIENT_CALIBRATION_ROWS_DEFAULTED",
        }
        for domain in DOMAIN_ORDER
    }


def _tokenizer(tmp_path: Path) -> BertTokenizerFast:
    tmp_path.mkdir(parents=True, exist_ok=True)
    vocab = tmp_path / "vocab.txt"
    vocab.write_text(
        "[PAD]\n[UNK]\n[CLS]\n[SEP]\n[MASK]\n",
        encoding="utf-8",
    )
    return BertTokenizerFast(vocab_file=str(vocab), do_lower_case=False)


def _tiny_model() -> nn.Module:
    encoder = BertModel(
        BertConfig(
            vocab_size=5,
            hidden_size=8,
            num_hidden_layers=1,
            num_attention_heads=2,
            intermediate_size=16,
            max_position_embeddings=512,
        )
    )
    return build_source_hierarchical_classifier(encoder, hidden_size=8, dropout=0.0)


def _metadata(module: ModuleType, *, version: str = "fixture-v1") -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "model_family": MODEL_FAMILY,
        "version": version,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": list(LABEL_ORDER),
        "prepared_partition_commitments": {
            "TRAIN": {"row_count": 3, "sha256": "a" * 64}
        },
        "candidate_matching_contract": module.candidate_matching_contract(
            prepared_partition_commitments={
                "TRAIN": {"row_count": 3, "sha256": "a" * 64}
            },
            input_artifacts={"fixture": {"sha256": "b" * 64}},
            stage1_optimizer_steps=2,
            stage2_optimizer_steps=4,
            stage1_planned_optimizer_steps=2,
            stage2_planned_optimizer_steps=4,
            gradient_checkpointing=False,
        ),
        "runtime_loader_contract": {
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "encoder_path": "encoder",
            "heads_path": HEAD_ARTIFACT_FILENAME,
            "tokenizer_source": "artifact-root",
            "domain_order": list(DOMAIN_ORDER),
            "label_order": list(LABEL_ORDER),
            "domain_required": True,
            "unknown_domain_behavior": "FAIL_CLOSED",
            "head_architecture": {
                "version": HEAD_ARCHITECTURE_VERSION,
                "anchor_domain": ANCHOR_DOMAIN,
                "residual_domains": list(RESIDUAL_DOMAINS),
                "residual_initialization": "EXACT_ZERO",
                "known_untrained_domain_fallback": "SHARED_HEAD_ZERO_RESIDUAL",
                "unknown_domain_behavior": "FAIL_CLOSED",
            },
            "pooling": "last_hidden_state_cls",
            "calibration": _calibration(),
            "input_feature_version": INPUT_FEATURE_VERSION,
            "max_length": module.MAX_LENGTH,
        },
        "recipe_commitment_sha256": module.recipe_commitment_sha256(),
        "selected_stage": "STAGE1_DOMAIN_BALANCED_FULL_ENCODER",
        "trained_at": "2026-07-16T00:00:00+00:00",
    }


def _artifact(tmp_path: Path) -> tuple[ModuleType, Path, nn.Module, BertTokenizerFast]:
    module = _module()
    model = _tiny_model()
    tokenizer = _tokenizer(tmp_path)
    artifact = tmp_path / "artifact"
    module.save_artifact(model, tokenizer, artifact, _metadata(module))
    return module, artifact, model, tokenizer


def test_pinned_base_and_fair_recipe_are_explicit() -> None:
    module = _module()
    recipe = module.recipe_contract()

    assert module.MODEL_SEEDS == (17, 42, 73)
    assert BASE_MODEL == "snunlp/KR-FinBert-SC"
    assert len(BASE_MODEL_REVISION) == 40
    assert set(BASE_MODEL_FILES_SHA256) == {
        "config.json",
        "model.safetensors",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt",
    }
    assert all(len(value) == 64 for value in BASE_MODEL_FILES_SHA256.values())
    assert recipe["data"]["public_test_opened"] is False
    assert recipe["data"]["confirmatory_labels_opened"] is False
    assert recipe["encoder"]["fine_tuning"] == "FULL_ENCODER"
    assert recipe["schedule"] == {
        "stage1_epochs": 2,
        "stage2_epochs": 4,
        "batch_size": 8,
        "eval_batch_size": 16,
        "gradient_accumulation_steps": 2,
        "optimizer": "AdamW",
        "scheduler": "cosine-with-8pct-warmup",
        "gradient_clip_norm": 1.0,
        "checkpoint_rule": "fixed-full-epoch; best-in-stage-checkpoint-selected",
        "stage2_scope": "SOURCE_HEADS_ONLY_GOLD_REFINEMENT",
        "rdrop_alpha": module.v6.R_DROP_ALPHA,
        "weight_decay": 0.01,
    }


def test_parser_includes_candidate_gold_provenance_contract() -> None:
    module = _module()
    args = module.parser().parse_args([])

    assert args.train_gold_provenance_path == DEFAULT_TRAIN_PROVENANCE
    assert (
        args.news_auxiliary_gold_provenance_path
        == DEFAULT_NEWS_AUXILIARY_PROVENANCE
    )
    assert (
        args.disclosure_auxiliary_gold_provenance_path
        == DEFAULT_DISCLOSURE_AUXILIARY_PROVENANCE
    )
    assert (
        args.news_development_gold_provenance_path
        == DEFAULT_NEWS_DEVELOPMENT_PROVENANCE
    )
    assert (
        args.disclosure_development_gold_provenance_path
        == DEFAULT_DISCLOSURE_DEVELOPMENT_PROVENANCE
    )


def test_model_builder_loads_only_pinned_safetensors_and_unfreezes_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    calls: list[tuple[str, dict[str, Any]]] = []

    class TinyEncoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.projection = nn.Linear(2, 2)
            self.config = SimpleNamespace(hidden_size=2, use_cache=True)
            self.checkpointing = False

        def gradient_checkpointing_enable(self) -> None:
            self.checkpointing = True

        def forward(self, input_ids: torch.Tensor, **_kwargs: Any) -> Any:
            hidden = torch.nn.functional.one_hot(input_ids % 2, num_classes=2).float()
            return SimpleNamespace(last_hidden_state=self.projection(hidden))

    class Factory:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> TinyEncoder:
            calls.append((name, kwargs))
            encoder = TinyEncoder()
            for parameter in encoder.parameters():
                parameter.requires_grad = False
            return encoder

    monkeypatch.setattr(module, "AutoModel", Factory)
    model = module.build_model(gradient_checkpointing=True)

    assert calls == [
        (
            BASE_MODEL,
            {
                "revision": BASE_MODEL_REVISION,
                "trust_remote_code": False,
                "local_files_only": False,
                "use_safetensors": True,
                "weights_only": True,
            },
        )
    ]
    assert all(parameter.requires_grad for parameter in model.parameters())
    assert model.encoder.checkpointing is True
    assert model.encoder.config.use_cache is False


def test_script_reuses_v6_partition_training_loss_calibration_and_selection() -> None:
    module = _module()
    source = inspect.getsource(module)

    assert "v6.prepare_partitions(args)" in source
    assert source.count("v6.train_stage(") == 2
    assert "v6.fit_calibration(" in source
    assert "v6.calibrated_predictions(" in source
    assert "v6.weakest_source_score(" in source
    assert "ratings_test.csv" not in source
    assert "confirmatory_sealed_gold" not in source
    report_fragment = source[
        source.index("    report = {") : source.index("    report_path.parent")
    ]
    assert report_fragment.index("**metadata") < report_fragment.index(
        '"schema_version": TRAINING_SCHEMA_VERSION'
    )
    assert '"model_family": MODEL_FAMILY' in source
    assert '"gradient_checkpointing": bool(args.gradient_checkpointing)' in source


def test_optimizer_steps_are_fixed_full_epoch_and_planned_equals_executed() -> None:
    module = _module()
    planned_stage1 = module.expected_optimizer_steps(32_907, 2)
    planned_stage2 = module.expected_optimizer_steps(1_794, 4)
    contract = module.candidate_matching_contract(
        prepared_partition_commitments={"TRAIN": {"row_count": 32_907}},
        input_artifacts={"input": {"sha256": "a" * 64}},
        stage1_optimizer_steps=planned_stage1,
        stage2_optimizer_steps=planned_stage2,
        stage1_planned_optimizer_steps=planned_stage1,
        stage2_planned_optimizer_steps=planned_stage2,
        gradient_checkpointing=False,
    )

    assert planned_stage1 == 4_114
    assert planned_stage2 == 452
    assert contract["planned_optimizer_steps"] == contract["executed_optimizer_steps"]
    assert contract["matching_semantics"][
        "planned_equals_executed_optimizer_steps"
    ] is True


def test_validation_plan_never_claims_independent_or_unsealed_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    prepared = SimpleNamespace(
        train_rows=[{}] * 3,
        checkpoint_rows=[{}] * 3,
        calibration_rows=[{}] * 3,
        selection_rows=[{}] * 3,
        gold_refinement_rows=[{}] * 3,
        commitments={"TRAIN": {"row_count": 3, "sha256": "a" * 64}},
    )
    monkeypatch.setattr(module.v6, "prepare_partitions", lambda _args: prepared)

    plan = module.validation_plan(argparse.Namespace(seed=17))

    assert plan["public_test_opened"] is False
    assert plan["confirmatory_labels_opened"] is False
    assert plan["required_model_seeds"] == [17, 42, 73]
    assert plan["base_hash_verification"].startswith("REQUIRED")


def test_execution_snapshot_detects_input_toctou(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    source = tmp_path / "input.jsonl"
    source.write_text("{\"row\":1}\n", encoding="utf-8")
    monkeypatch.setattr(
        module,
        "pinned_base_snapshot",
        lambda: {"model.safetensors": {"sha256": "a" * 64}},
    )
    snapshot = module.capture_execution_snapshot({"fixture": source})

    source.write_text("{\"row\":2}\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="변경"):
        module.assert_execution_snapshot_unchanged(snapshot, {"fixture": source})


def test_safe_artifact_loads_through_production_runtime_and_matches_cpu(
    tmp_path: Path,
) -> None:
    module, artifact, model, tokenizer = _artifact(tmp_path)
    rows = [
        {"text": "시장 뉴스", "source_type": "NEWS", "target_security": ""},
        {
            "text": "하나금융 뉴스",
            "source_type": "NEWS",
            "target_security": "하나금융지주",
        },
        {
            "text": "매출 공시",
            "source_type": "DISCLOSURE",
            "target_security": "하나금융지주",
        },
    ]

    contract = validate_kr_finbert_sc_v6_artifact(artifact)
    runtime = load_kr_finbert_sc_v6_runtime(artifact)
    parity = module.verify_production_cpu_roundtrip(
        model=model,
        tokenizer=tokenizer,
        artifact_dir=artifact,
        calibration=_calibration(),
        canary_rows=rows,
    )

    assert contract.version == "fixture-v1"
    assert runtime.predict("뉴스", "NEWS").domain == "NEWS_UNTARGETED"
    assert parity["status"] == "PASS"
    assert parity["domains"] == list(DOMAIN_ORDER)
    assert parity["exact_final_threshold_label_agreement"] is True


def test_artifact_rejects_pickle_and_manifest_tampering(tmp_path: Path) -> None:
    _, artifact, _, _ = _artifact(tmp_path)
    (artifact / "optimizer.pt").write_bytes(b"not-safe")

    with pytest.raises(KrFinBertBaselineArtifactError, match="허용되지 않은"):
        validate_kr_finbert_sc_v6_artifact(artifact)

    (artifact / "optimizer.pt").unlink()
    head = artifact / HEAD_ARTIFACT_FILENAME
    head.write_bytes(head.read_bytes() + b"tamper")
    with pytest.raises(KrFinBertBaselineArtifactError, match="commitment"):
        validate_kr_finbert_sc_v6_artifact(artifact)


def test_runtime_fails_closed_for_untargeted_disclosure(tmp_path: Path) -> None:
    _, artifact, _, _ = _artifact(tmp_path)
    runtime = load_kr_finbert_sc_v6_runtime(artifact)

    with pytest.raises(ValueError, match="target_security"):
        runtime.predict("공시", "DISCLOSURE", "")


def test_three_seed_aggregate_emits_winner_and_sap_commitment(tmp_path: Path) -> None:
    module, source_artifact, _, _ = _artifact(tmp_path / "fixture")
    output_root = tmp_path / "artifacts"
    report_root = tmp_path / "reports"
    output_root.mkdir()
    report_root.mkdir()
    metrics = {17: (0.61, 0.72), 42: (0.68, 0.70), 73: (0.68, 0.74)}
    for seed in module.MODEL_SEEDS:
        artifact = output_root / f"seed{seed}"
        shutil.copytree(source_artifact, artifact)
        primary, secondary = metrics[seed]
        report = {
            "schema_version": module.TRAINING_SCHEMA_VERSION,
            "seed": seed,
            "baseline_model_name": BASELINE_MODEL_NAME,
            "public_test_opened": False,
            "confirmatory_labels_opened": False,
            "recipe_commitment_sha256": module.recipe_commitment_sha256(),
            "prepared_partition_commitments": {
                "TRAIN": {"row_count": 3, "sha256": "a" * 64}
            },
            "candidate_matching_contract": module.candidate_matching_contract(
                prepared_partition_commitments={
                    "TRAIN": {"row_count": 3, "sha256": "a" * 64}
                },
                input_artifacts={"fixture": {"sha256": "b" * 64}},
                stage1_optimizer_steps=2,
                stage2_optimizer_steps=4,
                stage1_planned_optimizer_steps=2,
                stage2_planned_optimizer_steps=4,
                gradient_checkpointing=False,
            ),
            "production_cpu_roundtrip": {"status": "PASS"},
            "candidate_selection": {
                "primary_value": primary,
                "secondary_overall_macro_f1": secondary,
            },
            "parameter_counts": {"total": 1_000},
            "test": {"sample_count": 0, "status": "SEALED_UNTIL_CANDIDATE_LOCK"},
        }
        (report_root / f"seed{seed}.json").write_text(
            json.dumps(report, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    result = module.aggregate_runs(
        output_root=output_root,
        report_root=report_root,
        project_root=tmp_path,
    )
    commitment = json.loads(
        (report_root / "sap-baseline-commitment.json").read_text(encoding="utf-8")
    )

    assert result["selected_seed"] == 73
    assert (report_root / "winner.json").is_file()
    assert set(commitment["seed_runs"]) == {"17", "42", "73"}
    assert validate_v6_kr_finbert_sc_baseline_commitment(
        commitment, project_root=tmp_path
    ) == commitment

    reused = module.aggregate_runs(
        output_root=output_root,
        report_root=report_root,
        project_root=tmp_path,
    )

    assert reused["selected_seed"] == 73
    assert reused["reuse_status"] == "VERIFIED_EXACT_ARTIFACT_REUSE"


def test_seed_cli_is_fixed_to_prespecified_set() -> None:
    module = _module()

    assert module.parser().parse_args(["--seed", "42"]).seed == 42
    with pytest.raises(SystemExit):
        module.parser().parse_args(["--seed", "99"])
