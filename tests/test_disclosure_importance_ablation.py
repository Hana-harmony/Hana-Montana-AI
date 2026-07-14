from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_script() -> ModuleType:
    scripts = str(Path("scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = Path("scripts/ablate_disclosure_importance.py")
    spec = importlib.util.spec_from_file_location("ablate_disclosure_importance", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_project_rows_uses_only_declared_fields() -> None:
    module = _load_script()
    rows = [
        {
            "title": "제목",
            "snippet": "요약",
            "full_content": "전문",
            "text": "fallback",
            "importance": "HIGH",
        }
    ]

    title = module._project_rows(rows, ("title",))
    full = module._project_rows(rows, ("title", "snippet", "full_content"))

    assert title[0]["text"] == "제목"
    assert full[0]["text"] == "제목 요약 전문"
    assert "full_content" not in title[0]
