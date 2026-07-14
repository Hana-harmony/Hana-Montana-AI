from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_training_script() -> ModuleType:
    scripts = str(Path("scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = Path("scripts/train_k_fnspid_transformer.py")
    spec = importlib.util.spec_from_file_location("train_k_fnspid_transformer", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_validation_selected_prior_correction_recovers_majority_errors() -> None:
    module = _load_training_script()
    expected = np.asarray([0] * 70 + [1] * 20 + [2] * 8 + [3] * 2)
    logits = np.zeros((len(expected), 4), dtype=np.float64)
    logits[np.arange(len(expected)), expected] = 3.0
    logits[:20, 0] = 1.0
    logits[:20, 1] = 1.1
    training_rows = [
        {"importance": module.LABEL_ORDER[label_index]} for label_index in expected.tolist()
    ]

    selected = module._select_log_prior_correction(logits, expected, training_rows)
    corrected = module._apply_log_prior_correction(logits, selected)

    assert selected["selected_strength"] > 0.0
    assert module._classification_metrics(expected, corrected.argmax(axis=-1))["macro_f1"] == 1.0


def test_prior_correction_rejects_invalid_priors() -> None:
    module = _load_training_script()
    postprocessing = {
        "selected_strength": 0.5,
        "training_class_priors": {label: 0.0 for label in module.LABEL_ORDER},
    }

    with pytest.raises(ValueError, match="올바르지 않습니다"):
        module._apply_log_prior_correction(np.zeros((1, 4)), postprocessing)
