from hannah_montana_ai.domain.schemas import Sentiment

NEGATIVE_TERMS = (
    "감소", "경계", "리스크", "변동성", "생산차질", "손실", "압박", "우려",
    "적자", "차질", "철회", "하락", "흔들",
)
NEUTRAL_TERMS = ("될까", "변수", "압박", "재검토", "정체", "흔들림")
SEVERE_NEGATIVE_TERMS = (
    "감사의견 거절", "거래정지", "생산차질", "손실", "소송", "우려", "적자",
    "차질", "철회", "하락",
)
POSITIVE_TERMS = (
    "개선", "계약", "성장", "수주", "증가", "들썩", "등극", "청신호", "주목",
    "지분 인수", "지분인수", "지분투자", "턴어라운드", "호실적", "흑자",
)


def apply_financial_sentiment_policy(text: str, sentiment: Sentiment) -> Sentiment:
    negative_score = sum(1 for term in NEGATIVE_TERMS if term in text)
    positive_score = sum(1 for term in POSITIVE_TERMS if term in text)
    has_severe_negative = any(term in text for term in SEVERE_NEGATIVE_TERMS)
    if _has_mixed_market_sentiment(text):
        return "NEUTRAL"
    if negative_score > positive_score and (has_severe_negative or negative_score >= 2):
        return "NEGATIVE"
    has_neutral_context = any(term in text for term in NEUTRAL_TERMS)
    if sentiment == "POSITIVE" and has_neutral_context and not has_severe_negative:
        return "NEUTRAL"
    if positive_score > negative_score and sentiment != "NEGATIVE":
        return "POSITIVE"
    return sentiment


def _has_mixed_market_sentiment(text: str) -> bool:
    if not ("코스피" in text and "코스닥" in text):
        return False
    has_positive_axis = any(
        term in text for term in ("회복", "반등", "상승 전환", "순매수", "유입")
    )
    has_negative_axis = any(
        term in text for term in ("하락", "약세", "순매도", "내렸다", "밀렸다")
    )
    return has_positive_axis and has_negative_axis and "반면" in text
