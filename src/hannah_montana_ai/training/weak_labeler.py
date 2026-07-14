from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

from hannah_montana_ai.domain.schemas import Importance, Sentiment, SourceType
from hannah_montana_ai.training.dataset import LabeledAlert

EVENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "EARNINGS": ("실적", "매출", "영업이익", "순이익", "흑자", "적자", "어닝", "컨센서스"),
    "DISCLOSURE": ("공시", "보고서", "제출", "정정", "주요사항", "잠정", "결정"),
    "CAPITAL_ACTION": ("유상증자", "무상증자", "감자", "배당", "자사주", "전환사채", "신주"),
    "CORPORATE_ACTION": ("합병", "분할", "인수", "매각", "최대주주", "지분", "계열사"),
    "CONTRACT": ("공급계약", "수주", "계약", "납품", "양산", "공급"),
    "RISK": ("거래정지", "상장폐지", "횡령", "배임", "소송", "제재", "과징금", "감사의견", "리콜"),
    "MACRO": ("환율", "금리", "물가", "수출", "반도체", "코스피", "코스닥", "외국인"),
}

SENTIMENT_PATTERNS: dict[Sentiment, tuple[str, ...]] = {
    "POSITIVE": (
        "상승",
        "급등",
        "흑자",
        "증가",
        "수주",
        "계약",
        "배당",
        "호실적",
        "개선",
        "상향",
        "승인",
        "최대",
    ),
    "NEUTRAL": ("공시", "제출", "결정", "예정", "안내", "변경", "조회공시", "개최"),
    "NEGATIVE": (
        "하락",
        "급락",
        "손실",
        "적자",
        "감소",
        "리콜",
        "제재",
        "과징금",
        "부진",
        "하향",
        "위험",
        "거절",
    ),
}

IMPORTANCE_PATTERNS: dict[Importance, tuple[str, ...]] = {
    "LOW": ("안내", "변경", "일정", "개최"),
    "MEDIUM": ("관심", "업황", "전망", "변동", "투자", "외국인"),
    "HIGH": ("실적", "공급계약", "유상증자", "합병", "분할", "자사주", "배당", "수주"),
    "CRITICAL": ("상장폐지", "거래정지", "횡령", "배임", "감사의견 거절", "불성실공시"),
}

DISCLOSURE_CRITICAL_PATTERNS = (
    "상장폐지",
    "횡령",
    "배임",
    "감사의견거절",
    "감사의견 거절",
    "부도",
    "회생절차",
    "파산",
)
DISCLOSURE_HIGH_PATTERNS = (
    "주요사항보고서",
    "단일판매ㆍ공급계약",
    "단일판매·공급계약",
    "공급계약체결",
    "유상증자",
    "무상증자",
    "감자결정",
    "전환사채",
    "신주인수권부사채",
    "자기주식취득",
    "자기주식처분",
    "현금ㆍ현물배당",
    "회사합병",
    "회사분할",
    "영업양수",
    "영업양도",
    "타법인주식",
    "매출액또는손익구조",
    "영업실적",
    "소송등의제기",
    "소송등의판결",
    "거래정지",
)
DISCLOSURE_LOW_PATTERNS = (
    "임원ㆍ주요주주특정증권등소유상황보고서",
    "임원·주요주주특정증권등소유상황보고서",
    "주식등의대량보유상황보고서",
    "주주총회소집공고",
    "주주총회소집결의",
    "기업설명회개최",
    "감사보고서제출",
    "사업보고서",
    "분기보고서",
    "반기보고서",
    "증권발행실적보고서",
    "투자설명서",
    "일괄신고서",
)
DISCLOSURE_MEDIUM_PATTERNS = (
    "최대주주등소유주식변동",
    "주주총회결과",
    "조회공시",
    "정정신고",
    "기재정정",
    "대표이사변경",
)


@dataclass(frozen=True)
class RawCollectedAlert:
    source_type: SourceType
    title: str
    snippet: str
    original_url: str
    published_at: str
    provider: str

    @property
    def text(self) -> str:
        return normalize_text(f"{self.title} {self.snippet}")

    @property
    def content_hash(self) -> str:
        return sha256(f"{self.source_type}:{self.title}:{self.original_url}".encode()).hexdigest()


def weak_label(alert: RawCollectedAlert) -> LabeledAlert | None:
    text = alert.text
    tags = _labels_by_score(text, EVENT_PATTERNS)
    if not tags:
        tags = ["GENERAL_MARKET"]

    sentiment = _single_label_by_score(text, SENTIMENT_PATTERNS, "NEUTRAL")
    importance = _single_label_by_score(text, IMPORTANCE_PATTERNS, "MEDIUM")
    if alert.source_type == "DISCLOSURE":
        sentiment = _disclosure_sentiment(text, sentiment)
        importance = _disclosure_importance(text, importance)

    return LabeledAlert(
        text=text,
        tags=tags,
        sentiment=sentiment,
        importance=importance,
        source_type=alert.source_type,
        provider=alert.provider,
        published_at=alert.published_at,
        source_url=alert.original_url,
        content_hash=alert.content_hash,
    )


def _disclosure_sentiment(text: str, default: Sentiment) -> Sentiment:
    compact = re.sub(r"\s+", "", text)
    if any(pattern.replace(" ", "") in compact for pattern in DISCLOSURE_CRITICAL_PATTERNS):
        return "NEGATIVE"
    if any(pattern in compact for pattern in ("계약해지", "결정취소", "계획철회")):
        return "NEGATIVE"
    if any(
        pattern in compact
        for pattern in ("손실감소", "적자폭감소", "흑자전환", "이익증가", "매출증가")
    ):
        return "POSITIVE"
    if any(
        pattern in compact
        for pattern in ("손실증가", "적자전환", "이익감소", "매출감소", "실적하락")
    ):
        return "NEGATIVE"
    if any(pattern in compact for pattern in ("자기주식취득", "현금ㆍ현물배당", "공급계약체결")):
        return "POSITIVE"
    if any(
        pattern in compact
        for pattern in (
            "임원ㆍ주요주주특정증권등소유상황보고서",
            "주주총회소집",
            "기업설명회개최",
            "유상증자",
            "자기주식처분",
        )
    ):
        return "NEUTRAL"
    return default


def _disclosure_importance(text: str, default: Importance) -> Importance:
    compact = re.sub(r"\s+", "", text)
    ordered_patterns: tuple[tuple[Importance, tuple[str, ...]], ...] = (
        ("CRITICAL", DISCLOSURE_CRITICAL_PATTERNS),
        ("HIGH", DISCLOSURE_HIGH_PATTERNS),
        ("LOW", DISCLOSURE_LOW_PATTERNS),
        ("MEDIUM", DISCLOSURE_MEDIUM_PATTERNS),
    )
    for importance, patterns in ordered_patterns:
        if any(pattern.replace(" ", "") in compact for pattern in patterns):
            return importance
    return default


def normalize_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", without_tags).strip()


def _labels_by_score(text: str, patterns: dict[str, tuple[str, ...]]) -> list[str]:
    scores = {
        label: sum(1 for pattern in keywords if pattern in text)
        for label, keywords in patterns.items()
    }
    return [label for label, score in sorted(scores.items()) if score > 0]


def _single_label_by_score[Label: (Sentiment, Importance)](
    text: str,
    patterns: dict[Label, tuple[str, ...]],
    default: Label,
) -> Label:
    scores = {
        label: sum(1 for pattern in keywords if pattern in text)
        for label, keywords in patterns.items()
    }
    label, score = max(scores.items(), key=lambda item: item[1])
    return label if score > 0 else default
