import re

from hannah_montana_ai.domain.schemas import Importance, Sentiment, SummaryLines


class FinancialRuleEngine:
    critical_keywords = ("상장폐지", "거래정지", "횡령", "배임", "감사의견 거절")
    high_keywords = ("유상증자", "합병", "분할", "실적", "공급계약", "소송", "자사주")
    negative_keywords = ("하락", "손실", "적자", "감소", "리콜", "제재", "과징금")
    positive_keywords = ("상승", "흑자", "증가", "수주", "계약", "배당", "호실적")
    financial_context_keywords = (
        "주가",
        "시총",
        "증시",
        "시장",
        "매출",
        "영업이익",
        "실적",
        "계약",
        "수주",
        "투자",
        "반도체",
        "배터리",
        "공시",
        "거래",
        "외국인",
        "환율",
        "금리",
        "전망",
        "리스크",
        "상승",
        "하락",
        "급등",
        "급락",
    )
    boilerplate_keywords = (
        "로그인",
        "회원가입",
        "전체 메뉴",
        "메뉴 열기",
        "메뉴 닫기",
        "본문 바로가기",
        "검색 열기",
        "검색 닫기",
        "뉴스스탠드",
        "구독설정",
        "지면PDF",
        "운세",
        "이용약관",
        "개인정보",
        "저작권",
        "기자수첩",
        "오피니언",
        "페이스북",
        "트위터",
        "카카오톡",
        "네이버블로그",
        "네이버라인",
        "URL복사",
        "기사보내기",
        "파이낸셜뉴스 광고",
        "광고 구독하기",
        "구독하기",
        "많이 본 뉴스",
        "핫이슈",
        "부고",
        "NEWS STAND",
        "오늘의 NEWS",
        "대박",
        "소름",
        "폭탄 발언",
        "여중생",
        "불륜",
        "관련기사",
        "관련태그",
        "좋아요",
        "나빠요",
        "©",
        "복사하기",
        "스크롤 이동 상태바",
        "글자크기 설정",
        "기자의 본문 내용",
        "추천키워드",
        "실시간 속보 랭킹뉴스",
        "기자채널 다른기사",
        "전체기사",
        "전체메뉴",
        "전체메뉴닫기",
        "mail to",
        "K-Artprice",
        "프라임뉴시스",
        "위클리뉴시스",
        "제휴 콘텐츠",
        "월드컵24시",
        "더중앙플러스",
        "최신 기사",
        "최신 영상",
        "마켓 최신 뉴스",
        "오늘의 증시일정",
        "오늘의 주요공시",
        "오늘의 IR",
        "기자 이름을 클릭",
        "구글 번역",
        "아래는 위 기사",
        "이투데이 마켓",
        "share flutter_dash",
        "format_size",
        "사진 확대",
        "기자 입력",
        "회원용",
        "나만의 AI 비서",
        "증권 홈",
        "오늘 나온 보고서",
    )
    roundup_title_keywords = (
        "오늘의 주요공시",
        "오늘의 공시",
        "오늘의 증시일정",
        "오늘의 상승종목",
        "상승종목",
    )
    generic_title_terms = {
        "오늘의",
        "주요공시",
        "증시일정",
        "상승종목",
        "장종료",
        "코스피",
        "코스닥",
    }

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
        article_sentences = self._article_sentences(content or snippet)
        context_text = f"{title} {snippet}" if self._is_roundup_title(title) else title
        ranked_sentences = self._ranked_article_sentences(article_sentences, context_text)
        title_terms = self._title_terms(context_text)
        related_ranked_sentences = [
            sentence
            for sentence in ranked_sentences
            if any(term in sentence for term in title_terms)
        ]
        summary_candidates = (
            related_ranked_sentences
            if len(related_ranked_sentences) >= 2
            else ranked_sentences
        )
        what = self._first_title_context_sentence(article_sentences, context_text)
        if not what:
            fallback_title = "" if self._is_roundup_title(title) else title
            what = (
                summary_candidates[0]
                if summary_candidates
                else self.summarize(fallback_title, snippet)
            )
        why = self._first_matching_sentence(
            summary_candidates,
            ("때문", "영향", "증가", "감소", "계약", "실적", "공시", "수주", "투자", "소송"),
        )
        if not why or self._line(why) == self._line(what):
            why = self._first_distinct_sentence(summary_candidates, excluded={what})
        impact_sentence = self._first_matching_sentence(
            summary_candidates,
            ("주가", "매출", "영업이익", "손익", "리스크", "전망", "시장", "투자자", "거래"),
        )
        if not impact_sentence or self._line(impact_sentence) in {
            self._line(what),
            self._line(why),
        }:
            impact_sentence = self._first_distinct_sentence(
                summary_candidates,
                excluded={what, why},
            )
        fallback_subject = "해당 공시·뉴스" if self._is_roundup_title(title) else title
        if not why:
            why = (
                f"{fallback_subject}와 관련된 핵심 배경은 "
                "원문에서 확인된 최신 공시·뉴스 맥락입니다."
            )
        if not impact_sentence:
            impact_sentence = (
                f"영향은 {importance.lower()} 중요도와 {sentiment.lower()} 감성으로 분류되어 "
                "보유·관심 종목 사용자 확인이 필요합니다."
            )
        if self._line(why) == self._line(what):
            why = f"{fallback_subject}의 배경은 원문에서 확인된 최신 시장·기업 이벤트입니다."
        if self._line(impact_sentence) in {self._line(what), self._line(why)}:
            impact_sentence = (
                f"중요도 {importance.lower()}, 감성 {sentiment.lower()}로 분류되어 "
                "보유·관심 종목 사용자에게 노출할 필요가 있습니다."
            )
        return SummaryLines(
            what=self._line(what),
            why=self._line(why),
            impact=self._line(impact_sentence),
        )

    def clean_article_text(self, content: str, title: str) -> str:
        sentences = self._article_sentences(content)
        if not sentences:
            return re.sub(r"\s+", " ", content).strip()
        title_terms = self._title_terms(title)
        ranked = sorted(
            sentences,
            key=lambda sentence: self._sentence_score(sentence, title_terms),
            reverse=True,
        )
        selected = set(ranked[:30])
        # 기사 문맥 순서를 보존해 모델 입력이 자연스럽게 이어지도록 한다.
        return " ".join(sentence for sentence in sentences if sentence in selected)[:20_000]

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
            for sentence in re.split(r"(?<=[.!?。])\s+|(?<=다)\s+", normalized)
            if sentence.strip()
        ]

    def _article_sentences(self, text: str) -> list[str]:
        return [
            sentence
            for sentence in self._sentences(text)
            if self._is_article_sentence(sentence)
        ]

    def _ranked_article_sentences(self, sentences: list[str], title: str) -> list[str]:
        sentences = [
            sentence
            for sentence in sentences
            if self._is_article_sentence(sentence)
        ]
        title_terms = self._title_terms(title)
        return sorted(
            sentences,
            key=lambda sentence: self._sentence_score(sentence, title_terms),
            reverse=True,
        )

    def _first_title_context_sentence(self, sentences: list[str], title: str) -> str:
        title_terms = self._title_terms(title)
        for sentence in sentences:
            if any(term in sentence for term in title_terms) and self._contains_any(
                sentence,
                self.financial_context_keywords,
            ):
                return sentence
        for sentence in sentences:
            if self._contains_any(sentence, self.financial_context_keywords):
                return sentence
        return ""

    def _is_article_sentence(self, sentence: str) -> bool:
        normalized = re.sub(r"\s+", " ", sentence).strip()
        if len(normalized) < 24 or len(normalized) > 500:
            return False
        if len(re.findall(r"\[[^\]]{2,24}\]", normalized)) >= 2:
            return False
        if re.search(r"\S+@\S+", normalized):
            return False
        if any(keyword in normalized for keyword in self.boilerplate_keywords):
            return False
        if normalized.count(" ") > 38 and not self._contains_any(
            normalized,
            self.financial_context_keywords,
        ):
            return False
        return True

    def _sentence_score(self, sentence: str, title_terms: set[str]) -> int:
        score = min(len(sentence), 180)
        score += self._count_keywords(sentence, self.financial_context_keywords) * 60
        score += sum(1 for term in title_terms if term in sentence) * 35
        if title_terms and not any(term in sentence for term in title_terms):
            score -= 90
        score -= self._count_keywords(sentence, self.boilerplate_keywords) * 120
        return score

    def _is_roundup_title(self, title: str) -> bool:
        return self._contains_any(title, self.roundup_title_keywords)

    def _title_terms(self, title: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", title)
            if token not in {"단독", "종합", "속보", "특징주"}
            and token not in self.generic_title_terms
        }

    def _first_matching_sentence(self, sentences: list[str], keywords: tuple[str, ...]) -> str:
        for sentence in sentences:
            if self._contains_any(sentence, keywords):
                return sentence
        return ""

    def _first_distinct_sentence(self, sentences: list[str], excluded: set[str]) -> str:
        excluded_lines = {self._line(text) for text in excluded if text}
        for sentence in sentences:
            if self._line(sentence) not in excluded_lines:
                return sentence
        return ""

    def _line(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = re.sub(r"\S+@\S+", "", normalized).strip()
        normalized = re.sub(r"^/?사진=[^ ]+\s*", "", normalized).strip()
        normalized = re.sub(
            r"^[가-힣A-Za-z0-9_. -]{2,24}=[가-힣]{2,4}\s*기자\s*",
            "",
            normalized,
        ).strip()
        normalized = re.sub(r"^[.·ㆍ•▲△▶▷\-\s]+", "", normalized).strip()
        return normalized[:300]
