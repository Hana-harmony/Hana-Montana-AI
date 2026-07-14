from __future__ import annotations

import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import joblib
import pytest

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.disclosure_importance_model import DisclosureImportanceModel
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine


class _FakeClassifier:
    classes_ = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def predict_proba(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.6, 0.1] for _ in texts]


def _load_training_script() -> ModuleType:
    path = Path("scripts/train_disclosure_importance_model.py")
    spec = importlib.util.spec_from_file_location("train_disclosure_importance_model", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_training_rows_exclude_gold_and_unreviewed_contract_violations() -> None:
    module = _load_training_script()
    valid = {
        "source_type": "DISCLOSURE",
        "label_provenance": "RULE_WEAK_SUPERVISION_V2",
        "source_review_status": "UNREVIEWED_WEAK_LABEL",
        "importance": "HIGH",
        "source_url": "https://dart/valid",
        "content_hash": "1",
    }
    rows = [
        valid,
        {**valid, "source_url": "https://dart/gold", "content_hash": "2"},
        {**valid, "source_url": "https://dart/wrong", "label_provenance": "UNKNOWN"},
    ]

    result = module._training_rows(rows, {"https://dart/gold"})

    assert result == [valid]


def test_model_text_supports_gold_text_contract() -> None:
    module = _load_training_script()

    assert module._model_text({"text": "주요사항보고서"}) == "주요사항보고서"
    assert module._model_text({"title": "제목", "snippet": "요약"}) == "제목 요약"
    assert (
        module._model_text({"title": "제목", "snippet": "요약", "full_content": "공시 전문"})
        == "제목 요약 공시 전문"
    )


def test_critical_augmentation_is_deterministic_and_gold_free() -> None:
    module = _load_training_script()

    first = module._critical_augmentations()
    second = module._critical_augmentations()

    assert first == second
    assert len(first) == 400
    assert {row["importance"] for row in first} == {"CRITICAL"}
    assert all(str(row["source_url"]).startswith("synthetic://") for row in first)


def test_feature_view_selection_uses_validation_metrics_only() -> None:
    module = _load_training_script()
    candidates = {
        "title_only": {
            "fields": ["title"],
            "validation": {"macro_f1": 0.90, "multiclass_brier_score": 0.02},
        },
        "title_and_snippet": {
            "fields": ["title", "snippet"],
            "validation": {"macro_f1": 0.90, "multiclass_brier_score": 0.01},
        },
        "title_snippet_full_content": {
            "fields": ["title", "snippet", "full_content"],
            "validation": {"macro_f1": 0.89, "multiclass_brier_score": 0.005},
        },
    }

    assert module._select_feature_view(candidates) == "title_and_snippet"


def test_disclosure_importance_loader_verifies_artifact_before_joblib(tmp_path: Path) -> None:
    model_path = tmp_path / "model.joblib"
    report_path = tmp_path / "report.json"
    joblib.dump(
        {
            "schema_version": "disclosure-importance-artifact/v1",
            "version": "test-v1",
            "input_feature_version": "disclosure-validation-selected-view-v3",
            "selected_fields": ["title", "snippet"],
            "probability_temperature": 0.8,
            "label_order": ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
            "model": _FakeClassifier(),
        },
        model_path,
    )
    report = {
        "input_feature_version": "disclosure-validation-selected-view-v3",
        "feature_selection": {"selected_fields": ["title", "snippet"]},
        "gold_test": {
            "sample_count": 600,
            "macro_f1": 0.8,
            "label_metrics": {
                label: {"f1": 0.8} for label in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
            },
        },
        "deployment_gate": {"eligible": True, "minimum_gold_label_f1": 0.7},
        "artifact": {
            "bytes": model_path.stat().st_size,
            "sha256": sha256(model_path.read_bytes()).hexdigest(),
        },
    }
    report_path.write_text(json.dumps(report), encoding="utf-8")

    model = DisclosureImportanceModel(model_path, report_path)

    assert model.enabled is True
    prediction = model.predict("대규모 공급계약", "계약 체결")
    assert prediction is not None
    assert prediction.importance == "HIGH"

    model_path.write_bytes(b"tampered")
    assert DisclosureImportanceModel(model_path, report_path).enabled is False


def test_critical_policy_floor_preserves_probability_sum() -> None:
    probabilities = AlertAnalyzer._apply_probability_floor(
        {"LOW": 0.10, "MEDIUM": 0.20, "HIGH": 0.60, "CRITICAL": 0.10},
        "CRITICAL",
        0.90,
    )

    assert probabilities["CRITICAL"] == pytest.approx(0.90)
    assert sum(probabilities.values()) == pytest.approx(1.0)


def test_disclosure_policy_separates_trading_halt_from_terminal_risk() -> None:
    engine = FinancialRuleEngine()

    assert engine.classify_importance("주권매매거래정지", "DISCLOSURE") == "HIGH"
    assert engine.classify_importance("불성실공시법인 지정", "DISCLOSURE") == "HIGH"
    assert engine.classify_importance("상장폐지 사유 발생", "DISCLOSURE") == "CRITICAL"
