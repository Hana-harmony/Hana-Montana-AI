from collections import defaultdict
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.dataset import load_labeled_alerts

EVENT_SEED_KEYWORDS = {
    "EARNINGS": ["실적", "매출", "영업이익", "순이익", "흑자", "적자", "어닝"],
    "DISCLOSURE": ["공시", "보고서", "제출", "정정", "주요사항"],
    "CAPITAL_ACTION": ["유상증자", "무상증자", "감자", "배당", "자사주", "전환사채"],
    "CORPORATE_ACTION": ["합병", "분할", "인수", "매각", "최대주주", "지분"],
    "CONTRACT": ["공급계약", "수주", "계약", "납품", "양산"],
    "RISK": ["거래정지", "상장폐지", "횡령", "배임", "소송", "제재", "과징금", "감사의견"],
    "MACRO": ["환율", "금리", "물가", "수출", "반도체 업황", "코스피"],
}

SENTIMENT_SEED_KEYWORDS = {
    "POSITIVE": ["상승", "흑자", "증가", "수주", "계약", "배당", "호실적", "개선", "상향", "승인"],
    "NEUTRAL": ["공시", "제출", "결정", "예정", "안내", "변경"],
    "NEGATIVE": ["하락", "손실", "적자", "감소", "리콜", "제재", "과징금", "부진", "하향", "위험"],
}

IMPORTANCE_SEED_KEYWORDS = {
    "LOW": ["안내", "변경", "일정"],
    "MEDIUM": ["관심", "업황", "전망", "변동"],
    "HIGH": ["실적", "공급계약", "유상증자", "합병", "분할", "자사주", "배당"],
    "CRITICAL": ["상장폐지", "거래정지", "횡령", "배임", "감사의견 거절"],
}


def train_keyword_model(training_path: Path) -> dict[str, Any]:
    samples = load_labeled_alerts(training_path)
    event_keywords = _collect_keywords(samples, EVENT_SEED_KEYWORDS, "tags")
    sentiment_keywords = _collect_keywords(samples, SENTIMENT_SEED_KEYWORDS, "sentiment")
    importance_keywords = _collect_keywords(samples, IMPORTANCE_SEED_KEYWORDS, "importance")

    return {
        "version": MODEL_VERSION,
        "trained_at": TRAINED_AT,
        "training_data": "data/training/financial_alert_corpus.jsonl",
        "sample_count": len(samples),
        "event_keywords": event_keywords,
        "sentiment_keywords": sentiment_keywords,
        "importance_keywords": importance_keywords,
    }


def _collect_keywords(
    samples: list[Any],
    seed_keywords: dict[str, list[str]],
    label_field: str,
) -> dict[str, list[str]]:
    collected: dict[str, set[str]] = defaultdict(set)
    for label, keywords in seed_keywords.items():
        collected[label].update(keywords)

    for sample in samples:
        labels = getattr(sample, label_field)
        if isinstance(labels, str):
            labels = [labels]
        for label in labels:
            for keyword in seed_keywords.get(label, []):
                if keyword in sample.text:
                    collected[label].add(keyword)

    return {label: sorted(keywords) for label, keywords in sorted(collected.items())}
MODEL_VERSION = "financial-keyword-baseline-2026-06-04"
TRAINED_AT = "2026-06-04T00:00:00+09:00"
