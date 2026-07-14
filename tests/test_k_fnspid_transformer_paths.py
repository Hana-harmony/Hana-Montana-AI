from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_module() -> ModuleType:
    scripts = str(Path("scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = Path("scripts/train_k_fnspid_transformer.py")
    spec = importlib.util.spec_from_file_location("train_k_fnspid_transformer_paths", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_project_path_resolves_relative_cli_path_from_project_root() -> None:
    module = _load_module()

    assert module._project_path(Path("reports/result.json")) == (
        module.PROJECT_ROOT / "reports/result.json"
    ).resolve()


def test_project_path_accepts_absolute_path_inside_project() -> None:
    module = _load_module()
    absolute = module.PROJECT_ROOT / "reports/result.json"

    assert module._project_path(absolute) == absolute.resolve()


def test_project_path_rejects_path_outside_project(tmp_path: Path) -> None:
    module = _load_module()

    with pytest.raises(ValueError, match="프로젝트 밖"):
        module._project_path(tmp_path / "result.json")
