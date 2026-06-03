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
    if alert.source_type == "DISCLOSURE" and importance in {"LOW", "MEDIUM"}:
        importance = "HIGH"

    return LabeledAlert(
        text=text,
        tags=tags,
        sentiment=sentiment,
        importance=importance,
        source_type=alert.source_type,
    )


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
