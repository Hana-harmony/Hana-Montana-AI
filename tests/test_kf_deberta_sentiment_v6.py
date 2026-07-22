from __future__ import annotations

import importlib.util
import inspect
import json
import sys
from contextlib import contextmanager
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import numpy as np
import pytest
import torch
from safetensors.torch import load_file, save_file
from torch import nn

from hannah_montana_ai.services.source_hierarchical_sentiment import (
    SourceHierarchicalSentimentRuntime,
    validate_domain_calibration,
)


def _module() -> ModuleType:
    name = "train_kf_deberta_sentiment_v6"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = Path("scripts/train_kf_deberta_sentiment_v6.py")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TinyEncoder(nn.Module):
    def __init__(self, hidden_size: int = 4) -> None:
        super().__init__()
        self.embedding = nn.Embedding(16, hidden_size)
        self.config = SimpleNamespace(hidden_size=hidden_size)

    def forward(self, input_ids: torch.Tensor, **_kwargs: Any) -> Any:
        return SimpleNamespace(last_hidden_state=self.embedding(input_ids))


class ArtifactEncoder(TinyEncoder):
    def save_pretrained(self, directory: Path, *, safe_serialization: bool) -> None:
        assert safe_serialization is True
        directory.mkdir(parents=True)
        (directory / "adapter_config.json").write_text("{}\n", encoding="utf-8")
        save_file({"adapter": torch.ones(1)}, directory / "adapter_model.safetensors")


class TinyTokenizer:
    cls_token_id = 1
    sep_token_id = 2
    model_input_names = ["input_ids", "attention_mask"]

    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        assert add_special_tokens is False
        return [3 + ord(character) % 12 for character in text]

    def num_special_tokens_to_add(self, *, pair: bool) -> int:
        assert pair is False
        return 2

    def save_pretrained(self, directory: Path) -> None:
        (directory / "tokenizer.json").write_text("{}\n", encoding="utf-8")
        (directory / "tokenizer_config.json").write_text("{}\n", encoding="utf-8")


def _hierarchical_output(
    module: ModuleType,
    boundary: torch.Tensor,
    direction: torch.Tensor,
) -> Any:
    return module.HierarchicalOutput(
        module.compose_hierarchical_log_probabilities(boundary, direction),
        boundary,
        direction,
    )


def _domain_mass(
    module: ModuleType,
    labels: torch.Tensor,
    weights: torch.Tensor,
    domains: torch.Tensor,
) -> Any:
    return module.domain_mass_objective_from_features(
        [
            {
                "labels": int(label),
                "sample_weight": float(weight),
                "domain_ids": int(domain),
            }
            for label, weight, domain in zip(labels, weights, domains, strict=True)
        ]
    )


def test_hierarchical_composition_is_exactly_normalized() -> None:
    module = _module()
    boundary = torch.tensor([-5.0, 0.0, 4.0])
    direction = torch.tensor([[3.0, -2.0], [0.0, 0.0], [-1.0, 2.0]])

    log_probabilities = module.compose_hierarchical_log_probabilities(
        boundary,
        direction,
    )

    assert log_probabilities.shape == (3, 3)
    assert torch.allclose(log_probabilities.exp().sum(dim=-1), torch.ones(3), atol=1e-6)


def test_zero_residual_initialization_is_exact_shared_fallback() -> None:
    module = _module()
    model = module.SourceHierarchicalClassifier(TinyEncoder(), hidden_size=4, dropout=0.0)
    model.eval()

    for residual in model.domain_residuals.values():
        assert all(torch.count_nonzero(parameter) == 0 for parameter in residual.parameters())

    output = model(
        input_ids=torch.tensor([[1, 2], [1, 2], [1, 2]]),
        attention_mask=torch.ones(3, 2, dtype=torch.long),
        domain_ids=torch.tensor([0, 1, 2]),
    )

    assert torch.allclose(output.boundary_logits[0], output.boundary_logits[1], atol=1e-6, rtol=0)
    assert torch.allclose(output.boundary_logits[0], output.boundary_logits[2], atol=1e-6, rtol=0)
    assert torch.allclose(output.direction_logits[0], output.direction_logits[1], atol=1e-6, rtol=0)
    assert torch.allclose(output.direction_logits[0], output.direction_logits[2], atol=1e-6, rtol=0)
    assert torch.allclose(output.logits[0], output.logits[1], atol=1e-6, rtol=0)
    assert torch.allclose(output.logits[0], output.logits[2], atol=1e-6, rtol=0)


def test_shared_anchor_and_domain_residuals_route_each_row() -> None:
    module = _module()
    model = module.SourceHierarchicalClassifier(TinyEncoder(), hidden_size=4, dropout=0.0)
    with torch.no_grad():
        model.shared_head.boundary.weight.zero_()
        model.shared_head.boundary.bias.fill_(4.0)
        model.shared_head.direction.weight.zero_()
        model.shared_head.direction.bias.copy_(torch.tensor([4.0, -4.0]))
        news_residual = model.domain_residuals["NEWS_TARGETED"]
        news_residual.boundary.bias.fill_(-8.0)
        disclosure_residual = model.domain_residuals["DISCLOSURE_TARGETED"]
        disclosure_residual.direction.bias.copy_(torch.tensor([-8.0, 8.0]))
    output = model(
        input_ids=torch.tensor([[1, 2], [1, 2], [1, 2]]),
        attention_mask=torch.ones(3, 2, dtype=torch.long),
        domain_ids=torch.tensor([0, 1, 2]),
    )

    assert output.logits.argmax(dim=-1).tolist() == [0, 1, 2]
    with pytest.raises(ValueError, match="source domain"):
        model(
            input_ids=torch.tensor([[1, 2]]),
            attention_mask=torch.ones(1, 2, dtype=torch.long),
        )
    with pytest.raises(ValueError, match="domain id"):
        model(
            input_ids=torch.tensor([[1, 2]]),
            attention_mask=torch.ones(1, 2, dtype=torch.long),
            domain_ids=torch.tensor([3]),
        )


def test_selected_residual_and_shared_head_receive_isolated_gradients() -> None:
    module = _module()
    model = module.SourceHierarchicalClassifier(TinyEncoder(), hidden_size=4, dropout=0.0)
    output = model(
        input_ids=torch.tensor([[1, 2], [3, 4]]),
        attention_mask=torch.ones(2, 2, dtype=torch.long),
        domain_ids=torch.tensor([1, 1]),
    )

    (-output.logits[:, 0].sum()).backward()

    assert model.shared_head.boundary.weight.grad is not None
    assert torch.count_nonzero(model.shared_head.boundary.weight.grad) > 0
    assert model.domain_residuals["NEWS_TARGETED"].boundary.weight.grad is not None
    assert torch.count_nonzero(model.domain_residuals["NEWS_TARGETED"].boundary.weight.grad) > 0
    assert all(
        parameter.grad is None
        for parameter in model.domain_residuals["DISCLOSURE_TARGETED"].parameters()
    )


def test_unknown_source_and_untargeted_disclosure_fail_closed() -> None:
    module = _module()

    with pytest.raises(ValueError, match="source_type"):
        module.strict_source_domain("BLOG", "하나금융지주")
    with pytest.raises(ValueError, match="target_security"):
        module.strict_source_domain("DISCLOSURE", "")
    assert module.strict_source_domain("NEWS", "") == "NEWS_UNTARGETED"
    assert module.strict_source_domain("NEWS", "하나금융지주") == "NEWS_TARGETED"


def test_calibrated_hierarchical_loss_rewards_correct_boundary_and_direction() -> None:
    module = _module()
    labels = torch.tensor([0, 1, 2] * 3)
    weights = torch.ones(9)
    domains = torch.repeat_interleave(torch.arange(3), 3)
    correct = _hierarchical_output(
        module,
        torch.tensor([4.0, -4.0, 4.0] * 3),
        torch.tensor([[4.0, -4.0], [0.0, 0.0], [-4.0, 4.0]] * 3),
    )
    wrong = _hierarchical_output(
        module,
        torch.tensor([-4.0, 4.0, -4.0] * 3),
        torch.tensor([[-4.0, 4.0], [0.0, 0.0], [4.0, -4.0]] * 3),
    )
    mass = _domain_mass(module, labels, weights, domains)

    assert module.hierarchical_calibrated_loss(
        correct, labels, weights, domains, mass
    ) < module.hierarchical_calibrated_loss(wrong, labels, weights, domains, mass)


def test_fixed_domain_mass_objective_is_order_and_batch_partition_invariant() -> None:
    module = _module()
    values = torch.tensor([1.0, 7.0, 2.0, 5.0, 11.0, 3.0, 13.0, 17.0, 19.0])
    weights = torch.tensor([1.0, 2.0, 1.5, 1.0, 0.5, 3.0, 1.0, 2.5, 1.0])
    domains = torch.repeat_interleave(torch.arange(3), 3)
    labels = torch.tensor([0, 1, 2] * 3)
    mass = _domain_mass(module, labels, weights, domains)

    def aggregate(order: list[int], batch_sizes: list[int], *, directional: bool) -> Any:
        result = torch.tensor(0.0)
        offset = 0
        for size in batch_sizes:
            selected = torch.tensor(order[offset : offset + size])
            mask = labels[selected] != 1 if directional else None
            cell_ids = (labels[selected] == 2).long() if directional else labels[selected]
            cell_mass = mass.direction_cell_mass if directional else mass.composite_cell_mass
            estimate = module._fixed_task_cell_mass_mean(
                values[selected],
                weights[selected],
                domains[selected],
                cell_ids,
                cell_mass,
                mass,
                mask,
            )
            result += estimate * (size / len(values))
            offset += size
        assert offset == len(values)
        return result

    full = aggregate(list(range(len(values))), [len(values)], directional=False)
    split = aggregate([6, 1, 4, 0, 8, 5, 2, 7, 3], [1, 3, 2, 3], directional=False)
    directional_full = aggregate(list(range(len(values))), [len(values)], directional=True)
    directional_split = aggregate([3, 6, 2, 5, 0, 8, 4, 1, 7], [2, 1, 1, 5], directional=True)

    assert torch.allclose(full, split, atol=1e-6)
    assert torch.allclose(directional_full, directional_split, atol=1e-6)


def test_domain_mass_objective_fails_closed_on_empty_or_unsafe_class_cell() -> None:
    module = _module()
    with pytest.raises(ValueError, match="task-class cell"):
        module.domain_mass_objective_from_features(
            [{"labels": label, "sample_weight": 1.0, "domain_ids": 0} for label in (0, 1)]
        )
    with pytest.raises(ValueError, match="질량 비율"):
        module.domain_mass_objective_from_features(
            [
                {"labels": 0, "sample_weight": 11.0, "domain_ids": 0},
                {"labels": 1, "sample_weight": 1.0, "domain_ids": 0},
                {"labels": 2, "sample_weight": 1.0, "domain_ids": 0},
            ]
        )


def test_domain_mass_objective_allows_supported_natural_class_imbalance() -> None:
    module = _module()
    features = []
    for label, weight in ((0, 1.0), (1, 14.0), (2, 2.0)):
        features.extend(
            {"labels": label, "sample_weight": weight, "domain_ids": 1}
            for _ in range(30)
        )

    objective = module.domain_mass_objective_from_features(features)

    assert objective.minimum_active_cell_count == 30
    assert objective.minimum_active_cell_mass == 30.0
    assert objective.maximum_active_cell_mass_ratio == 14.0


def test_domain_mass_objective_rejects_extreme_ratio_even_with_support() -> None:
    module = _module()
    features = []
    for label, weight in ((0, 1.0), (1, 26.0), (2, 2.0)):
        features.extend(
            {"labels": label, "sample_weight": weight, "domain_ids": 1}
            for _ in range(30)
        )

    with pytest.raises(ValueError, match="질량 비율"):
        module.domain_mass_objective_from_features(features)


def test_rdrop_applies_to_boundary_and_direction_outputs() -> None:
    module = _module()
    first = _hierarchical_output(
        module,
        torch.tensor([1.0, -1.0, 1.0] * 3),
        torch.tensor([[2.0, -1.0], [0.0, 0.0], [-1.0, 2.0]] * 3),
    )
    changed_boundary = _hierarchical_output(
        module,
        torch.tensor([-1.0, -1.0, 1.0] * 3),
        first.direction_logits,
    )
    changed_direction = _hierarchical_output(
        module,
        first.boundary_logits,
        torch.tensor([[-1.0, 2.0], [0.0, 0.0], [-1.0, 2.0]] * 3),
    )
    weights = torch.ones(9)
    domains = torch.repeat_interleave(torch.arange(3), 3)
    labels = torch.tensor([0, 1, 2] * 3)
    mass = _domain_mass(module, labels, weights, domains)

    identical = module.hierarchical_rdrop_consistency(first, first, weights, domains, mass)
    boundary_difference = module.hierarchical_rdrop_consistency(
        first, changed_boundary, weights, domains, mass
    )
    direction_difference = module.hierarchical_rdrop_consistency(
        first, changed_direction, weights, domains, mass
    )

    assert abs(float(identical)) < 1e-7
    assert float(boundary_difference) > 0.0
    assert float(direction_difference) > 0.0


def test_calibration_is_sequential_shrunk_and_domain_specific() -> None:
    module = _module()
    labels = np.tile(np.repeat(np.arange(3), 15), 3).astype(np.int64)
    domains = np.repeat(np.arange(3), 45).astype(np.int64)
    logits = np.full((135, 3), -2.0, dtype=np.float64)
    logits[np.arange(135), labels] = 1.5
    neutral_rows = labels == 1
    logits[neutral_rows, 1] = 0.2
    logits[neutral_rows, 0] = 0.1
    logits[neutral_rows, 2] = 0.0
    logits -= np.log(np.exp(logits).sum(axis=1, keepdims=True))

    calibration = module.fit_calibration(logits, labels, domains)
    predicted = module.calibrated_predictions(logits, domains, calibration)

    assert set(calibration) == set(module.DOMAIN_ORDER)
    assert all(
        entry["temperature"] in module.TEMPERATURE_GRID
        and entry["neutral_threshold"] in module.NEUTRAL_THRESHOLD_GRID
        and entry["fit_status"] == "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK"
        for entry in calibration.values()
    )
    assert predicted.shape == labels.shape
    assert float((predicted == labels).mean()) > 0.9


def test_calibration_defaults_instead_of_overfitting_small_domain() -> None:
    module = _module()
    logits = np.log(np.full((9, 3), 1 / 3, dtype=np.float64))
    labels = np.tile(np.arange(3), 3).astype(np.int64)
    domains = np.repeat(np.arange(3), 3).astype(np.int64)

    calibration = module.fit_calibration(logits, labels, domains)

    assert all(entry["temperature"] == 1.0 for entry in calibration.values())
    assert all(entry["neutral_threshold"] == 0.5 for entry in calibration.values())
    assert all("INSUFFICIENT" in str(entry["fit_status"]) for entry in calibration.values())


@pytest.mark.parametrize("failure", ["shape", "nan", "label", "domain", "missing"])
def test_calibration_fit_fails_closed_on_invalid_rows(failure: str) -> None:
    module = _module()
    logits = np.log(np.full((9, 3), 1 / 3, dtype=np.float64))
    labels = np.tile(np.arange(3), 3).astype(np.int64)
    domains = np.repeat(np.arange(3), 3).astype(np.int64)
    if failure == "shape":
        logits = logits[:, :2]
    elif failure == "nan":
        logits[0, 0] = np.nan
    elif failure == "label":
        labels[0] = 3
    elif failure == "domain":
        domains[0] = 3
    else:
        domains[:] = 0

    with pytest.raises(ValueError):
        module.fit_calibration(logits, labels, domains)


@pytest.mark.parametrize("tamper", ["temperature", "threshold", "status", "fields"])
def test_calibrated_predictions_reject_tampered_grid_contract(tamper: str) -> None:
    module = _module()
    logits = np.log(np.full((9, 3), 1 / 3, dtype=np.float64))
    labels = np.tile(np.arange(3), 3).astype(np.int64)
    domains = np.repeat(np.arange(3), 3).astype(np.int64)
    calibration = module.fit_calibration(logits, labels, domains)
    config = calibration[module.DOMAIN_ORDER[0]]
    config["fit_status"] = "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK"
    if tamper == "temperature":
        config["temperature"] = 0.81
    elif tamper == "threshold":
        config["neutral_threshold"] = 0.333
    elif tamper == "status":
        config["fit_status"] = "UNRECOGNIZED"
    else:
        config["unexpected"] = 1

    with pytest.raises(ValueError):
        module.calibrated_predictions(logits, domains, calibration)


def test_calibrated_predictions_assign_every_valid_row() -> None:
    module = _module()
    fit_logits = np.log(np.full((9, 3), 1 / 3, dtype=np.float64))
    fit_labels = np.tile(np.arange(3), 3).astype(np.int64)
    fit_domains = np.repeat(np.arange(3), 3).astype(np.int64)
    calibration = module.fit_calibration(fit_logits, fit_labels, fit_domains)
    logits = np.log(np.array([[0.7, 0.2, 0.1], [0.1, 0.2, 0.7]], dtype=np.float64))
    domains = np.array([0, 2], dtype=np.int64)

    predictions = module.calibrated_predictions(logits, domains, calibration)

    assert predictions.shape == (2,)
    assert set(predictions.tolist()) <= {0, 1, 2}
    invalid_domains = domains.copy()
    invalid_domains[1] = 3
    with pytest.raises(ValueError, match="domain"):
        module.calibrated_predictions(logits, invalid_domains, deepcopy(calibration))


def test_weakest_source_f1_is_primary_for_checkpoint_and_seed_selection() -> None:
    module = _module()
    metrics = {
        "OVERALL": {"macro_f1": 0.90},
        "NEWS_UNTARGETED": {"macro_f1": 0.91},
        "NEWS_TARGETED": {"macro_f1": 0.54},
        "DISCLOSURE_TARGETED": {"macro_f1": 0.76},
    }

    assert module.weakest_source_score(metrics) == (0.54, 0.90)
    parameters = inspect.signature(module.train_stage).parameters
    assert "checkpoint_dataset" in parameters
    assert "calibration_dataset" not in parameters
    assert "selection_dataset" not in parameters


def test_train_stage_executes_the_entire_fixed_epoch_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    class TinyStageDataset(torch.utils.data.Dataset[dict[str, torch.Tensor]]):
        def __init__(self) -> None:
            self.features = [
                {
                    "input_ids": torch.tensor([index + 1]),
                    "attention_mask": torch.tensor([1]),
                    "labels": torch.tensor(index % 3),
                    "sample_weight": torch.tensor(1.0),
                    "domain_ids": torch.tensor(index // 3),
                }
                for index in range(9)
            ]

        def __len__(self) -> int:
            return len(self.features)

        def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
            return self.features[index]

        def domain_mass_objective(self) -> Any:
            return module.domain_mass_objective_from_features(
                [
                    {
                        "labels": int(row["labels"]),
                        "sample_weight": float(row["sample_weight"]),
                        "domain_ids": int(row["domain_ids"]),
                    }
                    for row in self.features
                ]
            )

    def collate(rows: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
        return {name: torch.stack([row[name] for row in rows]) for name in rows[0]}

    fixed_logits = np.eye(3, dtype=np.float64)
    fixed_labels = np.arange(3, dtype=np.int64)
    fixed_domains = np.arange(3, dtype=np.int64)
    monkeypatch.setattr(
        module,
        "predict",
        lambda *_args, **_kwargs: (fixed_logits, fixed_labels, fixed_domains),
    )
    model = module.SourceHierarchicalClassifier(TinyEncoder(), hidden_size=4, dropout=0.0)
    dataset = TinyStageDataset()

    result = module.train_stage(
        model,
        dataset,
        dataset,
        collate,
        stage="FIXED_BUDGET_TEST",
        epochs=3,
        learning_rate=1e-3,
        weight_decay=0.0,
        batch_size=9,
        eval_batch_size=3,
        gradient_accumulation_steps=2,
        rdrop_alpha=0.0,
        seed=17,
        device=torch.device("cpu"),
        state_names={
            name for name, parameter in model.named_parameters() if parameter.requires_grad
        },
    )

    assert len(result.history) == 3
    assert result.planned_optimizer_steps == 3
    assert result.optimizer_steps == result.planned_optimizer_steps
    assert result.active_parameter_provenance["inactive_residual_bitwise_preserved"] is True
    assert all(result.active_parameter_provenance["residual_optimizer_membership"].values())


def test_no_k_stage_excludes_and_bitwise_preserves_both_residuals() -> None:
    module = _module()
    model = module.SourceHierarchicalClassifier(TinyEncoder(), hidden_size=4, dropout=0.0)
    objective = module.domain_mass_objective_from_features(
        [{"labels": label, "sample_weight": 1.0, "domain_ids": 0} for label in range(3)]
    )

    provenance, before = module._configure_stage_residuals(model, objective)
    optimizer = module._optimizer(model, learning_rate=1e-3, weight_decay=0.1)
    output = model(
        input_ids=torch.tensor([[1], [2], [3]]),
        attention_mask=torch.ones(3, 1, dtype=torch.long),
        domain_ids=torch.zeros(3, dtype=torch.long),
    )
    output.logits.sum().backward()
    optimizer.step()
    verified = module._verify_inactive_residuals_preserved(model, before, provenance)

    assert verified["residual_optimizer_membership"] == {
        "NEWS_TARGETED": False,
        "DISCLOSURE_TARGETED": False,
    }
    assert verified["inactive_residual_bitwise_preserved"] is True
    assert verified["inactive_residual_exact_zero_before"] is True
    assert verified["inactive_residual_exact_zero_after"] is True
    assert (
        verified["inactive_residual_state_sha256_before"]
        == verified["inactive_residual_state_sha256_after"]
    )


def test_selection_is_disclosed_as_adaptive_not_independent() -> None:
    module = _module()
    source = inspect.getsource(module.main)

    assert module.ADAPTIVE_SELECTION_ROLE == "ADAPTIVE_DEVELOPMENT_SELECTION"
    assert '"fit_partition": "SELECTION_ONLY"' not in source
    assert "confirmatory_is_only_independent_generalization_evidence" in source


def test_execution_snapshot_aborts_on_any_material_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    base = module.BaseSource("PINNED_RAW", "base", {"revision": "fixed"})
    snapshot = {
        "schema_version": "kf-deberta-training-execution-snapshot/v1",
        "captured_at": "2026-01-01T00:00:00+00:00",
        "material": {"input_artifacts": {"x": {"sha256": "before"}}},
    }
    monkeypatch.setattr(module, "resolve_base_source", lambda *_args, **_kwargs: base)
    monkeypatch.setattr(
        module,
        "_execution_snapshot_material",
        lambda *_args, **_kwargs: {"input_artifacts": {"x": {"sha256": "after"}}},
    )

    with pytest.raises(RuntimeError, match="변경"):
        module.assert_execution_snapshot_unchanged(snapshot, {}, "pinned")


def test_interruption_provenance_states_observability_limit() -> None:
    module = _module()
    audit = module.TrainingInterruptionAudit()
    audit.mark_progress()
    audit._on_continue(0, None)

    report = audit.report()

    assert report["wall_seconds"] >= 0.0
    assert report["process_cpu_seconds"] >= 0.0
    assert len(report["sigcont_resume_events"]) == 1
    assert report["exact_pause_duration_available"] is False
    assert "SIGSTOP" in report["limitation"]


def test_all_layers_lora_and_loss_recipe_are_fixed() -> None:
    module = _module()

    assert module.LORA_LAYERS == tuple(range(12))
    assert module.LORA_RANK == 16
    assert module.LORA_TARGET_MODULES == (
        "query_proj",
        "key_proj",
        "value_proj",
        "dense",
    )
    assert module.BOUNDARY_LOSS_WEIGHT > module.DIRECTION_LOSS_WEIGHT
    assert module.COMPOSITE_LOSS_WEIGHT > 0.0
    assert "focal" not in inspect.getsource(module.hierarchical_calibrated_loss).casefold()
    assert "build_source_hierarchical_classifier" in inspect.getsource(
        module.SourceHierarchicalClassifier
    )
    assert "calibrated_sentiment_prediction" in inspect.getsource(module.calibrated_predictions)
    assert {
        "source_hierarchical_sentiment",
        "sentiment_artifact_contract",
    } <= set(module._training_code_paths())


def _runtime_calibration(module: ModuleType) -> dict[str, dict[str, float | int | str]]:
    return {
        domain: {
            "temperature": 1.0,
            "neutral_threshold": 0.5,
            "sample_count": 30,
            "fit_status": "CALIBRATION_ONLY_SEQUENTIAL_1D_SHRUNK",
        }
        for domain in module.DOMAIN_ORDER
    }


def _roundtrip_canaries() -> list[dict[str, Any]]:
    return [
        {"text": "시장 전망", "source_type": "NEWS", "label": "NEUTRAL"},
        {
            "text": "영업이익 개선",
            "source_type": "NEWS",
            "stock_name": "삼성전자",
            "label": "POSITIVE",
        },
        {
            "text": "유상증자 결정",
            "source_type": "DISCLOSURE",
            "stock_name": "삼성전자",
            "label": "NEGATIVE",
        },
    ]


def test_saved_candidate_contract_runs_production_cpu_roundtrip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _module()
    tokenizer = TinyTokenizer()
    model = module.SourceHierarchicalClassifier(TinyEncoder(), 4, dropout=0.0)
    loaded_model = deepcopy(model)
    calibration = _runtime_calibration(module)
    runtime = SourceHierarchicalSentimentRuntime(
        model=loaded_model,
        tokenizer=tokenizer,
        torch_module=torch,
        max_length=32,
        calibration_by_domain=validate_domain_calibration(calibration),
    )
    called = {"loader": False}

    def loader(**_kwargs: Any) -> Any:
        called["loader"] = True
        return runtime

    @contextmanager
    def base_directory(_base_source: Any) -> Any:
        yield tmp_path

    monkeypatch.setattr(module, "load_source_hierarchical_runtime", loader)
    monkeypatch.setattr(module, "_runtime_parity_base_directory", base_directory)

    evidence = module.verify_production_cpu_roundtrip(
        model=model,
        tokenizer=tokenizer,
        artifact_dir=tmp_path,
        base_source=module.BaseSource("PINNED_RAW", "base", {}),
        calibration=calibration,
        canary_rows=_roundtrip_canaries(),
        max_length=32,
        validate_deployable_artifact=False,
    )

    assert called["loader"] is True
    assert evidence["status"] == "PASS"
    assert evidence["canary_count"] == 3
    assert evidence["logits_max_abs_error"] == 0.0
    assert evidence["probability_max_abs_error"] == 0.0
    assert evidence["exact_final_threshold_label_agreement"] is True


def test_production_cpu_roundtrip_fails_closed_on_loaded_logit_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _module()
    tokenizer = TinyTokenizer()
    model = module.SourceHierarchicalClassifier(TinyEncoder(), 4, dropout=0.0)
    loaded_model = deepcopy(model)
    with torch.no_grad():
        loaded_model.shared_head.boundary.bias.add_(0.1)
    calibration = _runtime_calibration(module)
    runtime = SourceHierarchicalSentimentRuntime(
        model=loaded_model,
        tokenizer=tokenizer,
        torch_module=torch,
        max_length=32,
        calibration_by_domain=validate_domain_calibration(calibration),
    )

    @contextmanager
    def base_directory(_base_source: Any) -> Any:
        yield tmp_path

    monkeypatch.setattr(
        module,
        "load_source_hierarchical_runtime",
        lambda **_kwargs: runtime,
    )
    monkeypatch.setattr(module, "_runtime_parity_base_directory", base_directory)

    with pytest.raises(RuntimeError, match="logit parity"):
        module.verify_production_cpu_roundtrip(
            model=model,
            tokenizer=tokenizer,
            artifact_dir=tmp_path,
            base_source=module.BaseSource("PINNED_RAW", "base", {}),
            calibration=calibration,
            canary_rows=_roundtrip_canaries(),
            max_length=32,
            validate_deployable_artifact=False,
        )


def test_real_saved_peft_artifact_passes_production_cpu_loader_roundtrip(
    tmp_path: Path,
) -> None:
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import BertTokenizerFast, DebertaV2Config, DebertaV2Model

    module = _module()
    base_directory = tmp_path / "base"
    base_model = DebertaV2Model(
        DebertaV2Config(
            vocab_size=32,
            hidden_size=12,
            num_hidden_layers=12,
            num_attention_heads=3,
            intermediate_size=16,
        )
    )
    base_model.save_pretrained(base_directory, safe_serialization=True)
    encoder = get_peft_model(
        base_model,
        LoraConfig(
            task_type=TaskType.FEATURE_EXTRACTION,
            r=module.LORA_RANK,
            lora_alpha=module.LORA_ALPHA,
            lora_dropout=module.LORA_DROPOUT,
            target_modules=list(module.LORA_TARGET_MODULES),
            layers_to_transform=list(module.LORA_LAYERS),
            layers_pattern="layer",
        ),
    )
    model = module.SourceHierarchicalClassifier(encoder, 12)
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
    calibration = _runtime_calibration(module)
    base_source = module.BaseSource(
        "DAPT_MERGED_FP32",
        base_directory,
        {
            "schema_version": "kf-deberta-dapt-base-source/v2",
            "artifact_manifest": {
                "path": "dapt/manifest.json",
                "bytes": 1,
                "sha256": "a" * 64,
            },
            "merged_fp32_artifact_files": {
                "merged_fp32/config.json": {"bytes": 1, "sha256": "b" * 64},
                "merged_fp32/model.safetensors": {"bytes": 1, "sha256": "c" * 64},
            },
            "training_report": {"bytes": 1, "sha256": "d" * 64},
            "prepared_manifest": {
                "path": "data/prepared/manifest.json",
                "bytes": 1,
                "sha256": "e" * 64,
            },
            "pilot_report": {
                "path": "reports/pilot.json",
                "bytes": 1,
                "sha256": "f" * 64,
            },
            "inventory_oracle": {"status": "LOCKED", "candidate_sha256": "1" * 64},
            "pack_oracle": {"status": "LOCKED", "candidate_sha256": "2" * 64},
            "base_model": module.v5.BASE_MODEL,
            "base_revision": module.v5.BASE_MODEL_REVISION,
            "precision": "FP32",
            "validation_nll": {"frozen_base": 3.1, "end_of_epoch": 1.3},
        },
    )
    runtime_contract = {
        "schema_version": module.RUNTIME_LOADER_SCHEMA_VERSION,
        "base_source": base_source.provenance,
        "adapter_path": "adapter",
        "heads_path": module.HEAD_ARTIFACT_FILENAME,
        "tokenizer_source": "artifact-root",
        "domain_order": list(module.DOMAIN_ORDER),
        "domain_required": True,
        "unknown_domain_behavior": "FAIL_CLOSED",
        "pooling": "last_hidden_state_cls",
        "head_tensor_contract": module.EXPECTED_HEAD_TENSOR_CONTRACT,
        "head_architecture": module.EXPECTED_HEAD_ARCHITECTURE,
        "composition": {
            "NEGATIVE": "log_sigmoid(boundary)+log_softmax(direction)[0]",
            "NEUTRAL": "log_sigmoid(-boundary)",
            "POSITIVE": "log_sigmoid(boundary)+log_softmax(direction)[1]",
        },
        "calibration": calibration,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "max_length": 32,
    }
    metadata = {
        "schema_version": module.ARTIFACT_SCHEMA_VERSION,
        "version": "hana-montana-kf-deberta-k-fnspid-sentiment-v6-seed17-roundtrip",
        "base_model": module.v5.BASE_MODEL,
        "base_model_revision": module.v5.BASE_MODEL_REVISION,
        "base_source_kind": base_source.kind,
        "label_order": list(module.LABEL_ORDER),
        "runtime_loader_contract": runtime_contract,
        "prepared_partition_commitments": module.EXPECTED_FULL_COMMITMENTS,
        "selected_stage": "STAGE1_DOMAIN_BALANCED_FULL",
        "trained_at": datetime.now(UTC).isoformat(),
    }
    artifact = tmp_path / "artifact"
    module.save_artifact(model, tokenizer, artifact, metadata)

    evidence = module.verify_production_cpu_roundtrip(
        model=model,
        tokenizer=tokenizer,
        artifact_dir=artifact,
        base_source=base_source,
        calibration=calibration,
        canary_rows=_roundtrip_canaries(),
        max_length=32,
        validate_deployable_artifact=True,
    )

    assert evidence["status"] == "PASS"
    assert evidence["logits_max_abs_error"] <= module.RUNTIME_PARITY_LOGIT_ATOL
    assert evidence["probability_max_abs_error"] <= (module.RUNTIME_PARITY_PROBABILITY_ATOL)
    assert evidence["exact_final_threshold_label_agreement"] is True


@pytest.mark.parametrize(
    "path",
    [
        Path("data/external/kf_deberta_benchmark/ratings_test.csv"),
        Path("data/evaluation/k_fnspid_sentiment_confirmatory_sealed_gold.jsonl"),
        Path("reports/confirmatory_sealed_gold-promotion-report.json"),
    ],
)
def test_public_test_and_confirmatory_gold_paths_are_hard_blocked(path: Path) -> None:
    module = _module()

    with pytest.raises(SystemExit, match="평가 경로"):
        module.assert_training_path_allowed(path, "forbidden")


def test_unlabeled_reservation_path_cannot_be_redirected() -> None:
    module = _module()
    args = module.parser().parse_args(
        ["--news-sealed-review-path", "data/evaluation/redirected.jsonl"]
    )

    with pytest.raises(SystemExit, match="고정된 무라벨"):
        module._validate_reservation_paths(args)


def test_full_prepared_input_matches_all_v5_commitments() -> None:
    module = _module()
    args = module.parser().parse_args(["--validate-only", "--seed", "17"])

    prepared = module.prepare_partitions(args)

    assert prepared.commitments == module.EXPECTED_FULL_COMMITMENTS
    assert len(prepared.train_rows) == 32_907
    assert len(prepared.gold_refinement_rows) == 1_794
    assert all("GOLD" in str(row["dataset"]) for row in prepared.gold_refinement_rows)
    assert prepared.audit["public_test_opened"] is False
    assert prepared.audit["confirmatory_labels_opened"] is False


def _write_dapt_artifact(module: ModuleType, directory: Path) -> None:
    merged = directory / "merged_fp32"
    merged.mkdir(parents=True)
    (merged / "config.json").write_text("{}\n", encoding="utf-8")
    save_file({"weight": torch.ones(1)}, merged / "model.safetensors")
    training_report = {
        "schema_version": "k-fnspid-kf-deberta-dapt-training/v1",
        "base_model": module.v5.BASE_MODEL,
        "base_revision": module.v5.BASE_MODEL_REVISION,
        "public_test_opened": False,
        "confirmatory_sentiment_labels_opened": False,
        "merged_fp32": "merged_fp32",
    }
    (directory / "training_report.json").write_text(json.dumps(training_report), encoding="utf-8")
    artifact_files = module._artifact_records(directory)
    manifest = {
        "schema_version": "k-fnspid-kf-deberta-dapt-artifact-manifest/v1",
        "status": "ATOMIC_COMPLETE",
        "merged_fp32_included": True,
        "adapter_safe_serialization": True,
        "overwrite_allowed": False,
        "symlinks_allowed": False,
        "base_model_provenance": {
            "repository": module.v5.BASE_MODEL,
            "revision": module.v5.BASE_MODEL_REVISION,
            "weights_only": True,
            "trust_remote_code": False,
            "file_hashes": {
                module.v5.BASE_MODEL_WEIGHT_FILENAME: module.v5.BASE_MODEL_WEIGHT_SHA256
            },
        },
        "artifact_files": artifact_files,
    }
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_legacy_dapt_artifact_is_rejected_by_v2_merged_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    directory = tmp_path / "dapt"
    directory.mkdir()
    _write_dapt_artifact(module, directory)

    with pytest.raises(RuntimeError, match="manifest 계약"):
        module.verify_dapt_base(directory)
    with pytest.raises(RuntimeError, match="manifest 계약"):
        module.resolve_base_source(str(directory), verify_pinned=False)
    assert module.DAPT_BASE_SOURCE_FAIL_CLOSED is False
    assert "validation NLL" in module.DAPT_VERIFIER_CONTRACT


def test_dapt_v2_merged_artifact_is_verified_and_tamper_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    import scripts.train_k_fnspid_dapt as dapt

    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(dapt, "PROJECT_ROOT", tmp_path)

    prepared = tmp_path / "prepared"
    prepared.mkdir()
    for name in (
        "manifest.json",
        "train_packs.parquet",
        "validation_packs.parquet",
        "validation_fixed_masks.parquet",
        "pack_lineage.parquet",
    ):
        (prepared / name).write_bytes(b"{}" if name.endswith(".json") else name.encode())
    prepared_record = dapt.artifact_record(prepared / "manifest.json")
    prepared_files = dapt.prepared_snapshot(prepared)

    pilot_path = tmp_path / "pilot.json"
    pilot_path.write_text(
        json.dumps({"status": "PRECISION_SELECTED", "selected_precision": "FP32"}),
        encoding="utf-8",
    )
    pilot_record = dapt.artifact_record(pilot_path)
    inputs = {"documents": {"path": "data/documents.parquet", "bytes": 1, "sha256": "a" * 64}}
    dependencies = {"trainer": {"path": "scripts/train.py", "bytes": 1, "sha256": "b" * 64}}
    inventory_oracle = {"status": "LOCKED", "candidate_sha256": "c" * 64}
    pack_oracle = {"status": "LOCKED", "candidate_sha256": "d" * 64}
    monkeypatch.setattr(dapt, "verify_source_inputs", lambda: (inputs, object()))
    monkeypatch.setattr(dapt, "dependency_records", lambda: dependencies)
    monkeypatch.setattr(dapt, "inventory_oracle_lock_record", lambda: inventory_oracle)
    monkeypatch.setattr(dapt, "pack_oracle_lock_record", lambda: pack_oracle)

    artifact = tmp_path / "artifact"
    (artifact / "adapter").mkdir(parents=True)
    (artifact / "merged_fp32").mkdir()
    (artifact / "adapter/adapter_config.json").write_text("{}", encoding="utf-8")
    (artifact / "adapter/adapter_model.safetensors").write_bytes(b"safe-adapter")
    (artifact / "merged_fp32/config.json").write_text("{}", encoding="utf-8")
    (artifact / "merged_fp32/model.safetensors").write_bytes(b"safe-merged")
    training_report = {
        "schema_version": "k-fnspid-kf-deberta-dapt-training/v2",
        "status": "TRAINED_PENDING_ATOMIC_MANIFEST",
        "public_test_opened": False,
        "confirmatory_sentiment_labels_opened": False,
        "precision": "FP32",
        "merged_fp32": "merged_fp32",
        "prepared_manifest": prepared_record,
        "prepared_artifacts": prepared_files,
        "pilot_report": pilot_record,
        "inventory_oracle": inventory_oracle,
        "pack_oracle": pack_oracle,
        "validation": {
            "nll_improved": True,
            "frozen_base": {"mean_nll": 3.2},
            "end_of_epoch": {"mean_nll": 2.9},
        },
        "optimizer": {
            "total_updates": dapt.TOTAL_UPDATES,
            "warmup_updates": dapt.WARMUP_UPDATES,
        },
        "training": {"update_count": dapt.TOTAL_UPDATES},
    }
    (artifact / "training_report.json").write_text(
        json.dumps(training_report),
        encoding="utf-8",
    )
    artifact_files = dapt.directory_artifact_manifest(artifact)
    merged_files = {
        name: record for name, record in artifact_files.items() if name.startswith("merged_fp32/")
    }
    manifest = {
        "schema_version": "k-fnspid-kf-deberta-dapt-artifact-manifest/v2",
        "status": "ATOMIC_COMPLETE",
        "generated_at": "2026-07-17T00:00:00+00:00",
        "input_artifacts": inputs,
        "prepared_manifest": prepared_record,
        "prepared_artifacts": prepared_files,
        "pilot_report": pilot_record,
        "dependency_artifacts": dependencies,
        "hardware": {},
        "base_model_provenance": {
            "repository": dapt.BASE_MODEL,
            "revision": dapt.BASE_REVISION,
            "file_hashes": dapt.BASE_FILE_HASHES,
            "weights_only": True,
            "trust_remote_code": False,
        },
        "corpus_commitments": dapt.EXPECTED_HASHES,
        "inventory_oracle": inventory_oracle,
        "pack_commitments": pack_oracle,
        "bundled_oracle_provenance": {},
        "artifact_files": artifact_files,
        "adapter_safe_serialization": True,
        "merged_fp32_included": True,
        "merged_fp32": {
            "included": True,
            "path": "merged_fp32",
            "artifact_files": merged_files,
        },
        "overwrite_allowed": False,
        "symlinks_allowed": False,
    }
    (artifact / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    base = module.verify_dapt_base(artifact)
    assert base.kind == "DAPT_MERGED_FP32"
    assert Path(base.model_path) == artifact / "merged_fp32"
    assert base.provenance["validation_nll"] == {
        "frozen_base": 3.2,
        "end_of_epoch": 2.9,
    }

    (artifact / "merged_fp32/model.safetensors").write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="file hash"):
        module.verify_dapt_base(artifact)


def test_pinned_base_retains_weights_only_sha_contract() -> None:
    module = _module()

    base = module.resolve_base_source("pinned", verify_pinned=False)

    assert base.kind == "PINNED_RAW"
    assert base.provenance["source_weight_sha256"] == (
        "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
    )
    assert base.provenance["weights_only"] is True
    assert base.provenance["trust_remote_code"] is False


def test_custom_heads_and_adapter_are_safe_atomic_artifacts(tmp_path: Path) -> None:
    module = _module()
    model = module.SourceHierarchicalClassifier(
        ArtifactEncoder(),
        hidden_size=4,
        dropout=0.0,
    )
    output = tmp_path / "candidate"

    records = module.save_artifact(
        model,
        TinyTokenizer(),
        output,
        {
            "runtime_loader_contract": {
                "domain_required": True,
                "unknown_domain_behavior": "FAIL_CLOSED",
            }
        },
    )

    assert (output / "adapter/adapter_model.safetensors").is_file()
    heads = load_file(output / module.HEAD_ARTIFACT_FILENAME)
    assert set(heads) == set(module.source_hierarchical_head_state_dict(model))
    assert not list(output.rglob("*.bin"))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["artifact_files"] == records
    actual_files = {
        path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()
    }
    assert actual_files == {
        *records,
        "manifest.json",
    }


def test_stage_checkpoint_roundtrip_restores_model_optimizer_scheduler_and_rng(
    tmp_path: Path,
) -> None:
    module = _module()
    torch.manual_seed(17)
    model = nn.Linear(3, 2)
    state_names = set(dict(model.named_parameters()))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = module.get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=1,
        num_training_steps=4,
    )
    loss = model(torch.ones(2, 3)).square().mean()
    loss.backward()
    optimizer.step()
    scheduler.step()
    optimizer.zero_grad(set_to_none=True)
    generator = torch.Generator().manual_seed(73)
    torch.randperm(10, generator=generator)
    best_state = module._capture_state(model, state_names)
    context = "a" * 64

    checkpoint = module._save_stage_checkpoint(
        checkpoint_directory=tmp_path / "checkpoints",
        context_sha256=context,
        stage="TEST_STAGE",
        completed_epoch=1,
        epochs=2,
        model=model,
        state_names=state_names,
        best_state=best_state,
        best_epoch=1,
        best_score=(0.6, 0.7),
        best_metrics={"OVERALL": {"macro_f1": 0.7}},
        history=[{"epoch": 1}],
        optimizer=optimizer,
        scheduler=scheduler,
        generator=generator,
        optimizer_steps=1,
        best_optimizer_step=1,
        elapsed_wall_seconds=12.5,
        device=torch.device("cpu"),
    )

    restored_model = nn.Linear(3, 2)
    restored_optimizer = torch.optim.AdamW(restored_model.parameters(), lr=1e-3)
    restored_scheduler = module.get_cosine_schedule_with_warmup(
        restored_optimizer,
        num_warmup_steps=1,
        num_training_steps=4,
    )
    restored_generator = torch.Generator().manual_seed(1)
    resumed = module._load_latest_stage_checkpoint(
        checkpoint_directory=checkpoint.parent,
        context_sha256=context,
        stage="TEST_STAGE",
        epochs=2,
        model=restored_model,
        state_names=state_names,
        optimizer=restored_optimizer,
        scheduler=restored_scheduler,
        generator=restored_generator,
        device=torch.device("cpu"),
    )

    assert resumed is not None
    assert resumed.completed_epoch == 1
    assert resumed.best_score == (0.6, 0.7)
    assert restored_scheduler.state_dict() == scheduler.state_dict()
    assert restored_generator.get_state().equal(generator.get_state())
    assert restored_optimizer.state_dict()["param_groups"] == optimizer.state_dict()["param_groups"]
    for name, tensor in model.state_dict().items():
        assert torch.equal(restored_model.state_dict()[name], tensor)
    for parameter_id, values in optimizer.state_dict()["state"].items():
        restored_values = restored_optimizer.state_dict()["state"][parameter_id]
        for name, value in values.items():
            assert torch.equal(restored_values[name], value)


def test_stage_checkpoint_rejects_tampered_state(tmp_path: Path) -> None:
    module = _module()
    model = nn.Linear(2, 2)
    state_names = set(dict(model.named_parameters()))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = module.get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=1,
        num_training_steps=2,
    )
    generator = torch.Generator().manual_seed(17)
    checkpoint = module._save_stage_checkpoint(
        checkpoint_directory=tmp_path / "checkpoints",
        context_sha256="b" * 64,
        stage="TEST_STAGE",
        completed_epoch=1,
        epochs=1,
        model=model,
        state_names=state_names,
        best_state=module._capture_state(model, state_names),
        best_epoch=1,
        best_score=(0.5, 0.5),
        best_metrics={},
        history=[{"epoch": 1}],
        optimizer=optimizer,
        scheduler=scheduler,
        generator=generator,
        optimizer_steps=0,
        best_optimizer_step=0,
        elapsed_wall_seconds=1.0,
        device=torch.device("cpu"),
    )
    (checkpoint / "state.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="manifest/context"):
        module._load_latest_stage_checkpoint(
            checkpoint_directory=checkpoint.parent,
            context_sha256="b" * 64,
            stage="TEST_STAGE",
            epochs=1,
            model=nn.Linear(2, 2),
            state_names=state_names,
            optimizer=torch.optim.AdamW(nn.Linear(2, 2).parameters(), lr=1e-3),
            scheduler=scheduler,
            generator=torch.Generator(),
            device=torch.device("cpu"),
        )


def _write_completed_stage_context_migration_fixture(
    module: ModuleType,
    tmp_path: Path,
    *,
    completed_epoch: int = 2,
    epochs: int = 2,
) -> tuple[Path, Path, Path, dict[str, Any]]:
    checkpoint = tmp_path / "stage1" / f"epoch-{completed_epoch:03d}"
    checkpoint.mkdir(parents=True)
    manifest_path = checkpoint / "manifest.json"
    tensor_path = checkpoint / "training_state.safetensors"
    manifest_path.write_text('{"checkpoint":"fixed"}\n', encoding="utf-8")
    tensor_path.write_bytes(b"immutable-safe-tensor-payload")
    record = {
        "schema_version": module.CHECKPOINT_CONTEXT_MIGRATION_SCHEMA_VERSION,
        "scope": module.CHECKPOINT_CONTEXT_MIGRATION_SCOPE,
        "stage": "STAGE1_DOMAIN_BALANCED_FULL",
        "completed_epoch": completed_epoch,
        "epochs": epochs,
        "old_context_sha256": "a" * 64,
        "new_context_sha256": "b" * 64,
        "checkpoint_manifest_sha256": module._sha256_file(manifest_path),
        "training_state_sha256": module._sha256_file(tensor_path),
        "tensor_payload_unchanged": True,
        "reason": "완료된 1단계 이후 2단계 질량 안전 규칙만 수정했다.",
        "rule_change": "고표본 자연 불균형을 계층형 안전 한도로 검증한다.",
        "verified_tests": ["tests/test_kf_deberta_sentiment_v6.py"],
    }
    migration_path = checkpoint / "context-migration.json"
    migration_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return checkpoint, manifest_path, tensor_path, record


def test_completed_stage_context_migration_is_hash_bound(tmp_path: Path) -> None:
    module = _module()
    checkpoint, manifest_path, tensor_path, record = (
        _write_completed_stage_context_migration_fixture(module, tmp_path)
    )

    validated = module._validate_completed_stage_context_migration(
        migration_path=checkpoint / "context-migration.json",
        checkpoint=checkpoint,
        manifest_path=manifest_path,
        tensor_path=tensor_path,
        checkpoint_context_sha256="a" * 64,
        expected_context_sha256="b" * 64,
        stage="STAGE1_DOMAIN_BALANCED_FULL",
        completed_epoch=2,
        epochs=2,
    )

    assert validated["training_state_sha256"] == record["training_state_sha256"]
    assert validated["tensor_payload_unchanged"] is True
    assert len(validated["sha256"]) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("training_state_sha256", "0" * 64),
        ("checkpoint_manifest_sha256", "0" * 64),
        ("new_context_sha256", "c" * 64),
        ("tensor_payload_unchanged", False),
    ],
)
def test_completed_stage_context_migration_rejects_tampering(
    tmp_path: Path,
    field: str,
    value: Any,
) -> None:
    module = _module()
    checkpoint, manifest_path, tensor_path, record = (
        _write_completed_stage_context_migration_fixture(module, tmp_path)
    )
    record[field] = value
    migration_path = checkpoint / "context-migration.json"
    migration_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(RuntimeError, match="migration 계약"):
        module._validate_completed_stage_context_migration(
            migration_path=migration_path,
            checkpoint=checkpoint,
            manifest_path=manifest_path,
            tensor_path=tensor_path,
            checkpoint_context_sha256="a" * 64,
            expected_context_sha256="b" * 64,
            stage="STAGE1_DOMAIN_BALANCED_FULL",
            completed_epoch=2,
            epochs=2,
        )


def test_completed_stage_context_migration_rejects_incomplete_stage(tmp_path: Path) -> None:
    module = _module()
    checkpoint, manifest_path, tensor_path, _ = _write_completed_stage_context_migration_fixture(
        module,
        tmp_path,
        completed_epoch=1,
        epochs=2,
    )

    with pytest.raises(RuntimeError, match="migration 계약"):
        module._validate_completed_stage_context_migration(
            migration_path=checkpoint / "context-migration.json",
            checkpoint=checkpoint,
            manifest_path=manifest_path,
            tensor_path=tensor_path,
            checkpoint_context_sha256="a" * 64,
            expected_context_sha256="b" * 64,
            stage="STAGE1_DOMAIN_BALANCED_FULL",
            completed_epoch=1,
            epochs=2,
        )


def test_context_mismatch_without_migration_stays_fail_closed(tmp_path: Path) -> None:
    module = _module()
    checkpoint, manifest_path, tensor_path, _ = _write_completed_stage_context_migration_fixture(
        module,
        tmp_path,
    )

    with pytest.raises(RuntimeError, match="migration이 없습니다"):
        module._validate_completed_stage_context_migration(
            migration_path=None,
            checkpoint=checkpoint,
            manifest_path=manifest_path,
            tensor_path=tensor_path,
            checkpoint_context_sha256="a" * 64,
            expected_context_sha256="b" * 64,
            stage="STAGE1_DOMAIN_BALANCED_FULL",
            completed_epoch=2,
            epochs=2,
        )
