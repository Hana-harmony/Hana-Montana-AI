from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_script() -> ModuleType:
    scripts_path = str(Path("scripts").resolve())
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    path = Path("scripts/evaluate_disclosure_importance_research.py")
    spec = importlib.util.spec_from_file_location("evaluate_disclosure_importance_research", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_evaluate_rows_requires_paper_scale_gold() -> None:
    module = _load_script()

    try:
        module.evaluate_rows([], bootstrap_samples=10, seed=1)
    except ValueError as error:
        assert "500건" in str(error)
    else:
        raise AssertionError("소규모 Gold가 연구 평가를 통과했습니다.")
