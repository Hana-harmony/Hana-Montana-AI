from __future__ import annotations

import re

POSITIVE_STRONG = tuple(
    re.compile(pattern)
    for pattern in (
        r"사상\s*(?:최대|최고)",
        r"흑자\s*전환",
        r"어닝\s*서프라이즈",
        r"목표주가\s*(?:상향|올려)",
        r"(?:매출|영업이익|순이익).{0,18}(?:증가|성장|급증|개선)",
        r"(?:대규모|[0-9,.]+\s*(?:억|조)원).{0,18}(?:수주|계약\s*체결)",
        r"(?:신약|품목).{0,12}(?:허가|승인)",
        r"자사주.{0,10}(?:소각|매입)",
        r"배당.{0,10}(?:확대|증액)",
        r"(?:급등|상한가|신고가)",
    )
)
NEGATIVE_STRONG = tuple(
    re.compile(pattern)
    for pattern in (
        r"적자\s*전환",
        r"(?:매출|영업이익|순이익).{0,18}(?:감소|급감|악화)",
        r"목표주가\s*(?:하향|낮춰)",
        r"(?:횡령|배임|분식회계|회계부정)",
        r"(?:부도|파산|회생절차|상장폐지)",
        r"(?:영업|생산|판매).{0,10}(?:중단|정지)",
        r"(?:허가|승인).{0,8}(?:취소|반려|거절)",
        r"(?:리콜|압수수색|과징금|제재)",
        r"(?:급락|하한가|신저가)",
    )
)
NEUTRAL_FACT = re.compile(
    r"(?:주주총회|이사회|대표이사|임원|인사|기업설명회|IR|기준일|명의개서|"
    r"보유상황|지분율|상장예비심사|신규상장|공시|보고서|설명회|출시|개최)"
)
DISCLOSURE_POSITIVE_SAMPLE = re.compile(
    r"(?:단일판매|공급계약|수주|배당|자기주식취득|자기주식소각|특허권취득|"
    r"영업양수|유형자산양도|최대주주변경|합병결정)"
)
DISCLOSURE_NEGATIVE_SAMPLE = re.compile(
    r"(?:소송등의제기|불성실공시|벌금|과징금|영업정지|관리종목|감사의견|"
    r"자본잠식|채무불이행|회생절차|파산|상장폐지|주권매매거래정지|"
    r"투자주의환기|손상차손|횡령|배임|부도|해산)"
)
DISCLOSURE_ADVERSE_AUXILIARY = re.compile(
    r"(?:유상증자|감자결정|주식병합|주식분할|전환사채|신주인수권부사채|"
    r"교환사채|채무보증|담보제공|대출원리금연체|채무인수|금전대여|"
    r"계약해지|계약취소|공급계약해지|전환청구권행사|신주인수권행사|"
    r"교환청구권행사)"
)


def weak_sentiment_label(text: str, source_type: str = "NEWS") -> tuple[str, float]:
    positive = sum(bool(pattern.search(text)) for pattern in POSITIVE_STRONG)
    negative = sum(bool(pattern.search(text)) for pattern in NEGATIVE_STRONG)
    if positive and not negative:
        return "POSITIVE", min(0.98, 0.88 + positive * 0.04)
    if negative and not positive:
        return "NEGATIVE", min(0.98, 0.88 + negative * 0.04)
    if positive and negative:
        return "NEUTRAL", 0.72
    if source_type == "DISCLOSURE" and DISCLOSURE_NEGATIVE_SAMPLE.search(text):
        return "NEGATIVE", 0.80
    if source_type == "DISCLOSURE" and DISCLOSURE_POSITIVE_SAMPLE.search(text):
        return "POSITIVE", 0.80
    if NEUTRAL_FACT.search(text):
        return "NEUTRAL", 0.84
    return "NEUTRAL", 0.70


def prevalence_sampling_stratum(text: str, source_type: str) -> str:
    source = source_type.strip().upper()
    if source not in {"NEWS", "DISCLOSURE"}:
        raise ValueError(f"지원하지 않는 출처입니다: {source_type}")
    label, _ = weak_sentiment_label(text, source)
    if source == "DISCLOSURE" and label == "NEUTRAL" and DISCLOSURE_ADVERSE_AUXILIARY.search(text):
        return "NEGATIVE"
    return label
