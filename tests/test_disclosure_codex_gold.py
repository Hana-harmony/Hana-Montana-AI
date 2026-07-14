import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from hannah_montana_ai.training.weak_labeler import RawCollectedAlert


def _load_script() -> ModuleType:
    path = Path("scripts/build_disclosure_codex_gold.py")
    spec = importlib.util.spec_from_file_location("build_disclosure_codex_gold", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _alert(title: str) -> RawCollectedAlert:
    return RawCollectedAlert(
        source_type="DISCLOSURE",
        title=f"테스트기업 {title}",
        snippet=title,
        original_url="https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260617000001",
        published_at="20260617",
        provider="open-dart",
    )


def test_codebook_prioritizes_terminal_risk() -> None:
    module = _load_script()

    rule, evidence = module.annotate_disclosure(_alert("주권매매거래정지(상장폐지사유발생)"))

    assert rule.importance == "CRITICAL"
    assert rule.sentiment == "NEGATIVE"
    assert evidence == "상장폐지"


def test_codebook_separates_routine_and_material_disclosures() -> None:
    module = _load_script()

    routine, _ = module.annotate_disclosure(_alert("임원ㆍ주요주주특정증권등소유상황보고서"))
    material, _ = module.annotate_disclosure(_alert("주요사항보고서(유상증자결정)"))

    assert routine.importance == "LOW"
    assert material.importance == "HIGH"


def test_earnings_sentiment_uses_directional_title_evidence() -> None:
    module = _load_script()

    assert module.sentiment_for_title("영업이익 증가", "NEUTRAL") == "POSITIVE"
    assert module.sentiment_for_title("영업손실 감소", "NEUTRAL") == "POSITIVE"
    assert module.sentiment_for_title("영업이익 감소", "NEUTRAL") == "NEGATIVE"
    assert module.sentiment_for_title("공급계약 해지", "POSITIVE") == "NEGATIVE"
