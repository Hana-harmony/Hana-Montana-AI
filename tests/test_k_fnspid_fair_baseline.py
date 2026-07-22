from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import torch


def _module() -> ModuleType:
    scripts = Path("scripts").resolve()
    path = scripts / "train_k_fnspid_fair_baseline.py"
    sys.path.insert(0, str(scripts))
    try:
        spec = importlib.util.spec_from_file_location(
            "train_k_fnspid_fair_baseline",
            path,
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(scripts))


def _row(text: str, label: str, *, source_type: str = "NEWS") -> dict[str, Any]:
    return {
        "text": text,
        "label": label,
        "source_type": source_type,
        "source_url": f"https://example.com/{text}",
        "content_hash": f"hash-{text}",
        "event_cluster_id": f"event-{text}",
        "sample_weight": 1.0,
    }


def _prepared(module: ModuleType, path: Path) -> Any:
    reservation = [
        {
            "text": "봉인 항목",
            "source_url": "https://example.com/sealed",
            "content_hash": "sealed-hash",
            "event_cluster_id": "sealed-event",
        }
    ]
    return module.PreparedTrainingData(
        train_rows=[{**_row("학습", "POSITIVE"), "dataset": "PUBLIC_TRAIN"}],
        checkpoint_rows=[{**_row("체크포인트", "POSITIVE"), "dataset": "PUBLIC_CHECKPOINT"}],
        calibration_rows=[{**_row("보정", "NEUTRAL"), "dataset": "PUBLIC_CALIBRATION"}],
        selection_rows=[{**_row("선택", "NEGATIVE"), "dataset": "PUBLIC_SELECTION"}],
        news_confirmatory_reservation=reservation,
        disclosure_confirmatory_reservation=[
            {**reservation[0], "text": "공시 봉인", "content_hash": "disclosure-hash"}
        ],
        input_paths={"fixture": path},
        gold_provenance={"fixture": {"status": "VERIFIED_BLIND_PROVENANCE"}},
        public_audit={},
        silver_audit={},
        disclosure_silver_audit={},
        final_overlap_audit={},
    )


def test_baseline_contract_is_fixed_safe_and_full_finetune(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _module()
    calls: dict[str, tuple[str, dict[str, Any]]] = {}

    class DummyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = torch.nn.Linear(2, 2)
            self.classifier = torch.nn.Linear(2, 3)

    class TokenizerFactory:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> object:
            calls["tokenizer"] = (name, kwargs)
            return object()

    class ModelFactory:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> DummyModel:
            calls["model"] = (name, kwargs)
            return DummyModel()

    monkeypatch.setattr(module, "AutoTokenizer", TokenizerFactory)
    monkeypatch.setattr(module, "AutoModelForSequenceClassification", ModelFactory)

    _, model = module._load_base_model()

    assert module.FAIR_SEEDS == (17, 42, 73)
    assert module.BASE_MODEL == "snunlp/KR-FinBert-SC"
    assert len(module.BASE_MODEL_REVISION) == 40
    assert calls["tokenizer"][1] == {
        "revision": module.BASE_MODEL_REVISION,
        "trust_remote_code": False,
    }
    assert calls["model"][1]["revision"] == module.BASE_MODEL_REVISION
    assert calls["model"][1]["trust_remote_code"] is False
    assert calls["model"][1]["use_safetensors"] is True
    assert calls["model"][1]["weights_only"] is True
    assert calls["model"][1]["num_labels"] == 3
    assert all(parameter.requires_grad for parameter in model.parameters())


def test_full_finetune_contract_rejects_frozen_encoder() -> None:
    module = _module()

    class FrozenModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = torch.nn.Linear(2, 2)
            self.classifier = torch.nn.Linear(2, 3)
            self.encoder.weight.requires_grad = False

    with pytest.raises(RuntimeError, match="모든 parameter"):
        module._assert_full_finetune(FrozenModel())


def test_training_inputs_exclude_public_test() -> None:
    module = _module()
    args = module._parser().parse_args([])

    paths = module._training_input_paths(args)

    assert "public_train" in paths
    assert "public_validation" in paths
    assert not any("test" in name.casefold() for name in paths if "confirmatory" not in name)
    assert not any(path.name == "ratings_test.csv" for path in paths.values())


def test_prepare_data_reuses_v2_loaders_and_only_unlabeled_reservations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    fixture = tmp_path / "input.jsonl"
    fixture.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(
        module,
        "_training_input_paths",
        lambda args: {
            "public_train": fixture,
            "public_validation": fixture,
            "all_other_inputs": fixture,
        },
    )
    monkeypatch.setattr(module, "validate_all_gold_provenance", lambda args: {})
    public_calls: list[str] = []

    def load_public(path: Path) -> list[dict[str, Any]]:
        public_calls.append(path.name)
        prefix = "train" if len(public_calls) == 1 else "validation"
        return [
            _row(f"{prefix}-{label}-{index}", label)
            for label in module.LABEL_ORDER
                for index in range(20)
        ]

    def load_reviewed(path: Path, partition: str, *, weight: float) -> list[dict[str, Any]]:
        del path
        prefix = partition.casefold()
        source = "DISCLOSURE" if "disclosure" in prefix else "NEWS"
        return [
            {
                **_row(f"{prefix}-{label}-{index}", label, source_type=source),
                "sample_weight": weight,
            }
            for label in module.LABEL_ORDER
            for index in range(20)
        ]

    sealed_calls: list[tuple[str, str]] = []

    def load_sealed(path: Path, partition: str, source: str) -> list[dict[str, Any]]:
        del path
        sealed_calls.append((partition, source))
        return [
            {
                "text": f"{source}-confirmatory-{index}",
                "source_url": f"https://example.com/{source}/sealed/{index}",
                "content_hash": f"{source}-sealed-hash-{index}",
                "event_cluster_id": f"{source}-sealed-event-{index}",
            }
            for index in range(2)
        ]

    def load_silver(
        path: Path,
        protected: list[dict[str, Any]],
        per_label: int,
        seed: int,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        del path, protected, per_label
        source = "DISCLOSURE" if seed == module.DATA_SELECTION_SEED + 11 else "NEWS"
        rows = [
            {
                **_row(f"silver-{source}-{label}", label, source_type=source),
                "sample_weight": 0.5,
            }
            for label in module.LABEL_ORDER
        ]
        return rows, {"seed": seed}

    monkeypatch.setattr(module, "_load_public_rows", load_public)
    monkeypatch.setattr(module, "_load_reviewed_rows", load_reviewed)
    monkeypatch.setattr(
        module,
        "_load_auxiliary_training_rows",
        lambda path, report, source, weight: [
            {
                **_row(
                    f"auxiliary-{source}-{label}-{index}",
                    label,
                    source_type=source,
                ),
                "sample_weight": weight,
            }
            for label in module.LABEL_ORDER
            for index in range(2)
        ],
    )
    monkeypatch.setattr(module, "_load_sealed_reservation_rows", load_sealed)
    monkeypatch.setattr(module, "_load_silver_rows", load_silver)
    monkeypatch.setattr(module, "_load_legacy_protected_rows", lambda: [])
    augmentation_calls: list[tuple[int, int]] = []

    def augment(
        rows: list[dict[str, Any]],
        *,
        per_source: int,
        seed: int,
    ) -> list[dict[str, Any]]:
        del rows
        augmentation_calls.append((per_source, seed))
        return []

    monkeypatch.setattr(module, "build_target_swap_hard_negatives", augment)
    args = module._parser().parse_args(
        [
            "--dataset-dir",
            str(tmp_path),
            "--silver-path",
            str(fixture),
            "--disclosure-silver-path",
            str(fixture),
            "--train-gold-path",
            str(fixture),
            "--development-gold-path",
            str(fixture),
            "--disclosure-development-gold-path",
            str(fixture),
            "--news-confirmatory-reservation",
            str(fixture),
            "--disclosure-confirmatory-reservation",
            str(fixture),
            "--confirmatory-sampling-design",
            str(fixture),
            "--validate-only",
        ]
    )

    prepared = module.prepare_training_data(args)

    assert public_calls == [fixture.name, fixture.name]
    assert sealed_calls == [
        (module.NEWS_CONFIRMATORY_PARTITION, "NEWS"),
        (module.DISCLOSURE_CONFIRMATORY_PARTITION, "DISCLOSURE"),
    ]
    assert augmentation_calls == [(module.TARGET_SWAP_PER_SOURCE, module.DATA_SELECTION_SEED)]
    assert all("label" not in row for row in prepared.news_confirmatory_reservation)
    assert all("label" not in row for row in prepared.disclosure_confirmatory_reservation)
    assert {row["dataset"] for row in prepared.selection_rows} == {
        "PUBLIC_SELECTION",
        "K_FNSPID_DEVELOPMENT_SELECTION",
        "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION",
    }


def test_selection_uses_weakest_source_then_overall_then_lowest_seed(
    tmp_path: Path,
) -> None:
    module = _module()
    report_root = tmp_path / "reports"
    report_root.mkdir()
    reports = []
    for seed, weakest, overall in (
        (17, 0.72, 0.80),
        (42, 0.74, 0.77),
        (73, 0.74, 0.79),
    ):
        (report_root / f"seed{seed}.json").write_text("{}\n", encoding="utf-8")
        reports.append(
            {
                "seed": seed,
                "candidate_selection": {"selection_score": weakest},
                "selection": {"macro_f1": overall},
            }
        )
    args = argparse.Namespace(report_root=report_root)

    summary = module._selection_summary(args, reports)

    assert summary["selected_seed"] == 73
    assert summary["selected_weakest_source_macro_f1"] == 0.74
    assert summary["public_test_labels_used"] is False


def test_write_once_preflight_rejects_existing_output(tmp_path: Path) -> None:
    module = _module()
    output = tmp_path / "artifacts"
    output.mkdir()

    with pytest.raises(SystemExit, match="write-once"):
        module._preflight_output_roots(output, tmp_path / "reports")


def test_validate_only_never_loads_model_or_creates_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _module()
    fixture = tmp_path / "fixture.jsonl"
    fixture.write_text("{}\n", encoding="utf-8")
    prepared = _prepared(module, fixture)
    monkeypatch.setattr(module, "prepare_training_data", lambda args: prepared)

    class ForbiddenModelFactory:
        @staticmethod
        def from_pretrained(*args: Any, **kwargs: Any) -> None:
            raise AssertionError("validate-only에서 모델을 로드하면 안 됩니다.")

    monkeypatch.setattr(module, "AutoModelForSequenceClassification", ForbiddenModelFactory)
    output = tmp_path / "artifacts"
    reports = tmp_path / "reports"

    module.main(
        [
            "--validate-only",
            "--max-train-rows",
            "3",
            "--output-root",
            str(output),
            "--report-root",
            str(reports),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "VALIDATED_WITHOUT_MODEL_LOAD_OR_TRAINING"
    assert payload["training_arguments"]["17"]["rdrop_alpha"] == module.R_DROP_ALPHA
    assert (
        payload["training_arguments"]["17"]["data_selection_seed"]
        == module.DATA_SELECTION_SEED
    )
    assert (
        payload["training_arguments"]["17"]["target_swap_per_source"]
        == module.TARGET_SWAP_PER_SOURCE
    )
    assert payload["public_test_path_accessed"] is False
    assert payload["confirmatory_labels_used"] is False
    commitments = list(payload["prepared_partition_commitments"].values())
    assert all(commitment == commitments[0] for commitment in commitments[1:])
    assert "CHECKPOINT" in commitments[0]
    assert not output.exists()
    assert not reports.exists()
