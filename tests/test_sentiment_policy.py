from hannah_montana_ai.services.sentiment_policy import apply_financial_sentiment_policy


def test_sentiment_policy_prioritizes_severe_financial_risk() -> None:
    assert apply_financial_sentiment_policy("생산차질 우려가 확대됐다", "POSITIVE") == "NEGATIVE"


def test_sentiment_policy_neutralizes_mixed_market_direction() -> None:
    text = "코스피는 반등한 반면 코스닥은 순매도로 하락했다"

    assert apply_financial_sentiment_policy(text, "NEGATIVE") == "NEUTRAL"
