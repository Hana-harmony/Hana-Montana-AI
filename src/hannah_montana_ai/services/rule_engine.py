import re

from hannah_montana_ai.domain.schemas import Importance, Sentiment, SummaryLines


class FinancialRuleEngine:
    critical_keywords = ("상장폐지", "거래정지", "횡령", "배임", "감사의견 거절")
    high_keywords = ("유상증자", "합병", "분할", "실적", "공급계약", "소송", "자사주")
    negative_keywords = ("하락", "손실", "적자", "감소", "리콜", "제재", "과징금")
    positive_keywords = ("상승", "흑자", "증가", "수주", "계약", "배당", "호실적")

    def classify_sentiment(self, text: str) -> Sentiment:
        negative_score = self._count_keywords(text, self.negative_keywords)
        positive_score = self._count_keywords(text, self.positive_keywords)
        if negative_score > positive_score:
            return "NEGATIVE"
        if positive_score > negative_score:
            return "POSITIVE"
        return "NEUTRAL"

    def classify_importance(self, text: str, source_type: str) -> Importance:
        if self._contains_any(text, self.critical_keywords):
            return "CRITICAL"
        if source_type == "DISCLOSURE" or self._contains_any(text, self.high_keywords):
            return "HIGH"
        if len(text) > 80:
            return "MEDIUM"
        return "LOW"

    def summarize(self, title: str, snippet: str) -> str:
        normalized = re.sub(r"\s+", " ", f"{title}. {snippet}").strip()
        return normalized[:220]

    def summarize_what_why_impact(
        self,
        title: str,
        snippet: str,
        content: str,
        importance: Importance,
        sentiment: Sentiment,
    ) -> SummaryLines:
        body = self._sentences(content or snippet)
        what = body[0] if body else self.summarize(title, snippet)
        why = self._first_matching_sentence(
            body,
            ("때문", "영향", "증가", "감소", "계약", "실적", "공시", "수주", "투자", "소송"),
        )
        impact_sentence = self._first_matching_sentence(
            body,
            ("주가", "매출", "영업이익", "손익", "리스크", "전망", "시장", "투자자", "거래"),
        )
        if not why:
            why = f"{title}와 관련된 핵심 배경은 원문에서 확인된 최신 공시·뉴스 맥락입니다."
        if not impact_sentence:
            impact_sentence = (
                f"영향은 {importance.lower()} 중요도와 {sentiment.lower()} 감성으로 분류되어 "
                "보유·관심 종목 사용자 확인이 필요합니다."
            )
        return SummaryLines(
            what=self._line(what),
            why=self._line(why),
            impact=self._line(impact_sentence),
        )

    def holder_target(self, importance: Importance) -> bool:
        return importance in {"HIGH", "CRITICAL"}

    def watchlist_target(self, importance: Importance) -> bool:
        return importance in {"MEDIUM", "HIGH", "CRITICAL"}

    def _contains_any(self, text: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _count_keywords(self, text: str, keywords: tuple[str, ...]) -> int:
        return sum(1 for keyword in keywords if keyword in text)

    def _sentences(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?。])\s+|(?<=[다요음])\.\s*", normalized)
            if sentence.strip()
        ]

    def _first_matching_sentence(self, sentences: list[str], keywords: tuple[str, ...]) -> str:
        for sentence in sentences:
            if self._contains_any(sentence, keywords):
                return sentence
        return ""

    def _line(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        return normalized[:300]
