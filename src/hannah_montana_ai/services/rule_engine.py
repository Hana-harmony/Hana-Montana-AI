import re

from hannah_montana_ai.domain.schemas import Importance, Sentiment


class FinancialRuleEngine:
    critical_keywords = (
        "상장폐지",
        "횡령",
        "배임",
        "감사의견 거절",
        "감사의견거절",
        "부도",
        "회생절차",
        "파산",
    )
    high_keywords = (
        "유상증자",
        "합병",
        "분할",
        "실적",
        "공급계약",
        "소송",
        "자사주",
        "거래정지",
        "불성실공시",
    )
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
        "기술",
        "서비스",
        "솔루션",
        "고객",
        "공시",
        "공개",
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
        "코스피",
        "코스닥",
        "지수",
        "쏠림",
    )
    summary_meta_keywords = (
        "classified",
        "importance",
        "sentiment",
        "중요도",
        "감성",
        "분류",
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
        "캡처",
        "관련종목",
        "추천 키워드",
        "유료콘텐츠서비스",
        "표출된 기사입니다",
        "연재물",
        "회원용",
        "나만의 AI 비서",
        "증권 홈",
        "오늘 나온 보고서",
        "본 기사는",
        "투자 권유",
        "최종 판단",
        "투자자 본인",
        "네티즌 어워즈",
        "투표하러 가기",
        "돈 되는 뉴스",
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
        cleaned_sentences: list[str] = []
        current_length = 0
        for sentence in sentences:
            if sentence not in selected:
                continue
            next_length = current_length + len(sentence) + (1 if cleaned_sentences else 0)
            if next_length > 60_000:
                break
            cleaned_sentences.append(sentence)
            current_length = next_length
        # 기사 문맥 순서를 보존해 모델 입력이 자연스럽게 이어지도록 한다.
        return " ".join(cleaned_sentences)

    def holder_target(self, importance: Importance) -> bool:
        return importance in {"HIGH", "CRITICAL"}

    def watchlist_target(self, importance: Importance) -> bool:
        return importance in {"MEDIUM", "HIGH", "CRITICAL"}

    def _contains_any(self, text: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _count_keywords(self, text: str, keywords: tuple[str, ...]) -> int:
        return sum(1 for keyword in keywords if keyword in text)

    def _sentences(self, text: str) -> list[str]:
        chunks = [
            re.sub(r"\s+", " ", chunk).strip()
            for chunk in re.split(r"[\r\n]+", text)
            if re.sub(r"\s+", " ", chunk).strip()
        ]
        if not chunks:
            return []
        sentences: list[str] = []
        for chunk in chunks:
            sentences.extend(
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?。])\s+|(?<=다)\s+", chunk)
                if sentence.strip()
            )
        return sentences

    def _article_sentences(self, text: str) -> list[str]:
        return [
            candidate
            for sentence in self._sentences(text)
            if (candidate := self._article_sentence_candidate(sentence))
        ]

    def _is_article_sentence(self, sentence: str) -> bool:
        return bool(self._article_sentence_candidate(sentence))

    def _article_sentence_candidate(self, sentence: str) -> str:
        normalized = re.sub(r"\s+", " ", sentence).strip()
        normalized = self._strip_photo_credit(normalized)
        normalized = self._strip_byline(normalized)
        if len(normalized) < 24 or len(normalized) > 500:
            return ""
        if normalized.startswith(("/", "\\")):
            return ""
        if len(re.findall(r"\[[^\]]{2,24}\]", normalized)) >= 2:
            return ""
        if self._is_low_quality_summary_line(normalized):
            return ""
        if not self._has_sentence_completion(normalized):
            return ""
        if re.search(r"\S+@\S+", normalized):
            return ""
        if any(keyword in normalized for keyword in self.boilerplate_keywords):
            return ""
        if normalized.count(" ") > 38 and not self._contains_any(
            normalized,
            self.financial_context_keywords,
        ):
            return ""
        return normalized

    def _sentence_score(self, sentence: str, title_terms: set[str]) -> int:
        score = min(len(sentence), 180)
        score += self._count_keywords(sentence, self.financial_context_keywords) * 60
        score += sum(1 for term in title_terms if term in sentence) * 35
        if title_terms and not any(term in sentence for term in title_terms):
            score -= 90
        score -= self._count_keywords(sentence, self.boilerplate_keywords) * 120
        return score

    def _title_terms(self, title: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", title)
            if token not in {"단독", "종합", "속보", "특징주"}
            and token not in self.generic_title_terms
        }

    def _strip_photo_credit(self, text: str) -> str:
        return re.sub(r"^\(?/?사진\s*=[^)]+\)?\s*", "", text).strip()

    def _strip_byline(self, text: str) -> str:
        normalized = re.sub(
            r"^[가-힣A-Za-z0-9_. -]{2,24}=[가-힣]{2,4}\s*기자\s*",
            "",
            text,
        ).strip()
        normalized = re.sub(
            r"^\[[^\]]{1,30}\s+[가-힣]{2,4}\s*기자\]\s*",
            "",
            normalized,
        ).strip()
        normalized = re.sub(r"^[가-힣]{2,4}\s*기자\s+", "", normalized).strip()
        return normalized

    def _is_low_quality_summary_line(self, text: str) -> bool:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return True
        if len(normalized) > 120 and not re.search(r"\s", normalized):
            return True
        if "..." in normalized or "…" in normalized:
            return True
        lower = normalized.lower()
        return any(keyword in lower for keyword in self.summary_meta_keywords)

    def _has_sentence_completion(self, text: str) -> bool:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return False
        return bool(
            re.search(
                r"([.!?。]|다|요|니다|습니다|한다|했다|됐다|된다|였다|이다|합니다|했습니다|됩니다|입니다)$",
                normalized,
            )
        )
