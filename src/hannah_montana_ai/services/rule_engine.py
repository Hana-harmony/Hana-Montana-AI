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
    reason_keywords = (
        "때문",
        "영향",
        "배경",
        "목적",
        "위해",
        "따라",
        "증가",
        "감소",
        "계약",
        "실적",
        "공시",
        "수주",
        "소송",
        "주주가치",
        "주주환원",
        "가격 반등",
        "수요",
        "랠리",
        "상승을 이끌",
    )
    strong_reason_keywords = (
        "때문",
        "영향",
        "배경",
        "목적",
        "위해",
        "주주가치",
        "주주환원",
        "가격 반등",
        "수요",
    )
    impact_keywords = (
        "주가",
        "매출",
        "영업이익",
        "손익",
        "리스크",
        "전망",
        "시장",
        "투자자",
        "거래",
        "코스피",
        "코스닥",
        "지수",
        "쏠림",
        "상장폐지",
        "거래정지",
        "지분 희석",
        "배당",
        "일정",
        "확인",
    )
    investor_action_keywords = ("투자자는", "사용자는", "확인해야", "점검해야")
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
        sentences = self._article_sentences(normalized)
        if sentences:
            return self._line(sentences[0])
        return self._fallback_what_sentence(title)

    def summarize_what_why_impact(
        self,
        title: str,
        snippet: str,
        content: str,
        importance: Importance,
        sentiment: Sentiment,
    ) -> SummaryLines:
        content_sentences = self._article_sentences(content)
        article_sentences = (
            content_sentences if content_sentences else self._article_sentences(snippet)
        )
        is_roundup_title = self._is_roundup_title(title)
        context_text = f"{title} {snippet}" if is_roundup_title else title
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
        what = self._first_title_context_sentence(
            article_sentences,
            context_text,
            prefer_title_match=not is_roundup_title,
        )
        if not what:
            fallback_title = "" if is_roundup_title else title
            what = (
                summary_candidates[0]
                if summary_candidates
                else self.summarize(fallback_title, snippet)
            )
        why = self._first_semantic_sentence(
            summary_candidates,
            self.strong_reason_keywords,
            excluded={what},
            reject_keywords=self.investor_action_keywords,
        )
        if not why:
            why = self._first_semantic_sentence(
                summary_candidates,
                self.reason_keywords,
                excluded={what},
                reject_keywords=self.investor_action_keywords,
            )
        if not why or self._line(why) == self._line(what):
            why = self._first_semantic_sentence(
                ranked_sentences,
                self.strong_reason_keywords,
                excluded={what},
                reject_keywords=self.investor_action_keywords,
            )
        if not why or self._line(why) == self._line(what):
            why = self._first_semantic_sentence(
                ranked_sentences,
                self.reason_keywords,
                excluded={what},
                reject_keywords=self.investor_action_keywords,
            )
        if not why or self._line(why) == self._line(what):
            why = self._first_distinct_sentence(summary_candidates, excluded={what})
        impact_sentence = self._first_semantic_sentence(
            summary_candidates,
            self.impact_keywords,
            excluded={what, why},
        )
        if not impact_sentence or self._line(impact_sentence) in {
            self._line(what),
            self._line(why),
        }:
            impact_sentence = self._first_semantic_sentence(
                ranked_sentences,
                self.impact_keywords,
                excluded={what, why},
            )
        if not impact_sentence or self._line(impact_sentence) in {
            self._line(what),
            self._line(why),
        }:
            impact_sentence = self._first_distinct_sentence(
                summary_candidates,
                excluded={what, why},
            )
        article_backed_summary = self._article_backed_summary_lines(
            article_sentences,
            (what, why, impact_sentence),
        )
        if article_backed_summary:
            return article_backed_summary
        fallback_subject = (
            "해당 공시·뉴스"
            if is_roundup_title
            else self._subject_fragment(title) or "해당 공시·뉴스"
        )
        if not why:
            why = (
                f"{fallback_subject}{self._josa(fallback_subject, '과', '와')} 관련된 핵심 배경은 "
                "원문에서 확인된 최신 공시·뉴스 맥락입니다."
            )
        if not impact_sentence:
            impact_sentence = self._investor_check_sentence(fallback_subject)
        if self._line(why) == self._line(what):
            why = (
                f"{fallback_subject}의 배경은 "
                "원문에서 확인된 최신 시장·기업 이벤트입니다."
            )
        if self._line(impact_sentence) in {self._line(what), self._line(why)}:
            impact_sentence = self._investor_check_sentence(fallback_subject)
        what_line = self._line(what)
        if not what_line:
            what_line = self._line(self.summarize(fallback_subject, snippet))
        if not what_line:
            what_line = self._fallback_what_sentence(fallback_subject)
        why_line = self._line(why)
        if not why_line or why_line == what_line:
            why_line = self._line(
                f"{fallback_subject}의 배경은 원문에서 확인된 최신 시장·기업 이벤트입니다."
            )
        impact_line = self._line(impact_sentence)
        if not impact_line or impact_line in {what_line, why_line}:
            impact_line = self._line(self._investor_check_sentence(fallback_subject))
        return SummaryLines(
            what=what_line,
            why=why_line,
            impact=impact_line,
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
        cleaned_sentences: list[str] = []
        current_length = 0
        for sentence in sentences:
            if sentence not in selected:
                continue
            next_length = current_length + len(sentence) + (1 if cleaned_sentences else 0)
            if next_length > 20_000:
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

    def _first_title_context_sentence(
        self,
        sentences: list[str],
        title: str,
        *,
        prefer_title_match: bool = True,
    ) -> str:
        title_terms = self._title_terms(title)
        title_match_threshold = min(2, len(title_terms))
        if prefer_title_match and title_match_threshold:
            for sentence in sentences[:6]:
                matched_terms = sum(1 for term in title_terms if term in sentence)
                if matched_terms >= title_match_threshold:
                    return sentence
        market_axis_terms = {
            term
            for term in title_terms
            if term in {"기관", "외국인", "개인", "매수세", "매도세", "회복", "반등"}
            or term.endswith("선")
        }
        if market_axis_terms:
            for sentence in sentences[:8]:
                if any(term in sentence for term in market_axis_terms) and self._contains_any(
                    sentence,
                    self.financial_context_keywords,
                ):
                    return sentence
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

    def _first_semantic_sentence(
        self,
        sentences: list[str],
        keywords: tuple[str, ...],
        *,
        excluded: set[str],
        reject_keywords: tuple[str, ...] = (),
    ) -> str:
        excluded_lines = {self._line(text) for text in excluded if text}
        for sentence in sentences:
            line = self._line(sentence)
            if not line:
                continue
            if line in excluded_lines:
                continue
            if reject_keywords and self._contains_any(sentence, reject_keywords):
                continue
            if self._contains_any(sentence, keywords):
                return sentence
        return ""

    def _first_distinct_sentence(self, sentences: list[str], excluded: set[str]) -> str:
        excluded_lines = {self._line(text) for text in excluded if text}
        for sentence in sentences:
            line = self._line(sentence)
            if line and line not in excluded_lines:
                return sentence
        return ""

    def _article_backed_summary_lines(
        self,
        article_sentences: list[str],
        candidates: tuple[str, str, str],
    ) -> SummaryLines | None:
        article_lines = [line for sentence in article_sentences if (line := self._line(sentence))]
        if len(article_lines) < 3:
            return None

        selected: list[str] = []
        article_line_set = set(article_lines)
        for candidate in candidates:
            line = self._line(candidate)
            if line and line in article_line_set and line not in selected:
                selected.append(line)

        for line in article_lines:
            if line not in selected:
                selected.append(line)
            if len(selected) == 3:
                return SummaryLines(
                    what=selected[0],
                    why=selected[1],
                    impact=selected[2],
                )
        return None

    def _investor_check_sentence(self, subject: str) -> str:
        display_subject = self._subject_fragment(subject) or "해당 이슈"
        return (
            f"투자자는 {display_subject}{self._josa(display_subject, '이', '가')} "
            "보유·관심 종목의 수급, 실적 전망, "
            "변동성에 미치는 영향을 확인해야 합니다."
        )

    def _fallback_what_sentence(self, subject: str) -> str:
        display_subject = self._subject_fragment(subject) or "해당 공시·뉴스"
        return f"원문은 {display_subject} 관련 최신 시장·기업 이벤트를 다룹니다."

    def _subject_fragment(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = normalized.replace("...", " ").replace("…", " ")
        normalized = re.sub(r"\S+@\S+", "", normalized).strip()
        normalized = self._strip_photo_credit(normalized)
        normalized = self._strip_byline(normalized)
        normalized = re.sub(r"^[.·ㆍ•▲△▶▷\-\s]+", "", normalized).strip()
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if not normalized:
            return ""
        lower = normalized.lower()
        if any(keyword in lower for keyword in self.summary_meta_keywords):
            return ""
        return self._truncate_fragment(normalized, 80)

    def _line(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = re.sub(r"\S+@\S+", "", normalized).strip()
        normalized = self._strip_photo_credit(normalized)
        normalized = self._strip_byline(normalized)
        normalized = re.sub(r"^[.·ㆍ•▲△▶▷/\-\s]+", "", normalized).strip()
        if self._is_low_quality_summary_line(normalized):
            return ""
        if not self._has_sentence_completion(normalized):
            return ""
        return self._truncate_sentence_boundary(normalized, 300)

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

    def _truncate_sentence_boundary(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        boundary_positions = [
            match.end()
            for match in re.finditer(r"[.!?。]|다(?=\s|$)|요(?=\s|$)", text)
            if match.end() <= max_length
        ]
        if not boundary_positions:
            return ""
        return text[: boundary_positions[-1]].strip()

    def _truncate_fragment(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        boundary_positions = [
            match.start()
            for match in re.finditer(r"\s+", text)
            if match.start() <= max_length
        ]
        if not boundary_positions:
            return ""
        return text[: boundary_positions[-1]].strip()

    def _josa(self, text: str, with_final: str, without_final: str) -> str:
        subject = text.strip()
        if not subject:
            return without_final
        last_char = subject[-1]
        if "가" <= last_char <= "힣":
            return with_final if (ord(last_char) - ord("가")) % 28 else without_final
        return without_final
