from hannah_montana_ai.training.weak_labeler import RawCollectedAlert, weak_label


def _disclosure(title: str) -> RawCollectedAlert:
    return RawCollectedAlert(
        source_type="DISCLOSURE",
        title=f"테스트기업 {title}",
        snippet=title,
        original_url="https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260617000001",
        published_at="20260617",
        provider="open-dart",
    )


def test_routine_disclosure_is_not_forced_to_high_importance() -> None:
    labeled = weak_label(_disclosure("임원ㆍ주요주주특정증권등소유상황보고서"))

    assert labeled is not None
    assert labeled.importance == "LOW"
    assert labeled.sentiment == "NEUTRAL"


def test_material_disclosure_keeps_high_importance() -> None:
    labeled = weak_label(_disclosure("주요사항보고서(유상증자결정)"))

    assert labeled is not None
    assert labeled.importance == "HIGH"
    assert labeled.sentiment == "NEUTRAL"


def test_terminal_risk_disclosure_is_critical_and_negative() -> None:
    labeled = weak_label(_disclosure("주권매매거래정지(상장폐지사유발생)"))

    assert labeled is not None
    assert labeled.importance == "CRITICAL"
    assert labeled.sentiment == "NEGATIVE"


def test_shareholder_return_disclosure_is_positive() -> None:
    labeled = weak_label(_disclosure("주요사항보고서(자기주식취득결정)"))

    assert labeled is not None
    assert labeled.importance == "HIGH"
    assert labeled.sentiment == "POSITIVE"


def test_loss_decrease_disclosure_is_positive() -> None:
    labeled = weak_label(_disclosure("매출액또는손익구조변경(영업손실 감소)"))

    assert labeled is not None
    assert labeled.sentiment == "POSITIVE"
