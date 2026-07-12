from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

import ahocorasick

from hannah_montana_ai.training.k_fnspid.schema import DocumentEntity
from hannah_montana_ai.training.stock_universe import StockUniverseEntry

_HANGUL = re.compile(r"[가-힣]")
_COMMON_TERMS = {"AI", "IT", "VC", "ST", "대상", "보통주", "스팩", "리츠"}


@dataclass(frozen=True)
class EntityLinkResult:
    links: tuple[DocumentEntity, ...]
    rejected_ambiguous_terms: tuple[str, ...]


class ExactContextEntityLinker:
    def __init__(self, stocks: list[StockUniverseEntry]) -> None:
        self._stocks = stocks
        term_stocks: dict[str, list[int]] = defaultdict(list)
        self._rejected_terms: list[str] = []
        self._stock_index_by_code = {stock.stock_code: index for index, stock in enumerate(stocks)}
        for index, stock in enumerate(stocks):
            for term in stock.terms():
                clean = term.strip().lower()
                if self._safe_term(clean):
                    term_stocks[clean].append(index)
                else:
                    self._rejected_terms.append(clean)
        self._automaton = ahocorasick.Automaton()
        for term, stock_indices in term_stocks.items():
            self._automaton.add_word(term, (term, tuple(stock_indices)))
        self._automaton.make_automaton()

    def link(
        self,
        *,
        document_id: str,
        title: str,
        body: str,
        source_type: str,
        query_stock_code: str = "",
    ) -> EntityLinkResult:
        text = f"{title} {body}"
        lowered = text.lower()
        title_length = len(title)
        candidate_hits: dict[int, list[tuple[str, bool]]] = defaultdict(list)
        for end, (term, stock_indices) in self._automaton.iter(lowered):
            start = end - len(term) + 1
            if not self._has_boundary(lowered, start, end + 1, term):
                continue
            for stock_index in stock_indices:
                candidate_hits[stock_index].append((term, start < title_length))

        query_index = self._stock_index_by_code.get(query_stock_code)
        if query_index is not None:
            candidate_hits.setdefault(query_index, [])

        candidates: list[tuple[float, StockUniverseEntry, tuple[str, ...], str]] = []
        for stock_index, hits in candidate_hits.items():
            stock = self._stocks[stock_index]
            evidence = list(dict.fromkeys(term for term, _ in hits))
            score = 0.72 if any(in_title for _, in_title in hits) else 0.38
            method = "EXACT_CONTEXT"
            if query_stock_code and query_stock_code == stock.stock_code:
                score += 0.3
                method = "QUERY_AND_EXACT_CONTEXT"
            if source_type == "DISCLOSURE" and title.startswith(stock.stock_name):
                score = max(score, 0.99)
                method = "DART_CORPORATE_PREFIX"
                evidence.append(stock.stock_name)
            if score >= 0.38:
                candidates.append(
                    (min(score, 0.99), stock, tuple(dict.fromkeys(evidence)), method)
                )

        candidates.sort(key=lambda item: (-item[0], item[1].stock_code))
        links = tuple(
            DocumentEntity(
                document_id=document_id,
                stock_code=stock.stock_code,
                stock_name=stock.stock_name,
                market=stock.market,
                relation="PRIMARY" if index == 0 else "RELATED",
                confidence=round(score, 6),
                evidence=evidence,
                mapping_method=method,
            )
            for index, (score, stock, evidence, method) in enumerate(candidates[:8])
        )
        return EntityLinkResult(
            links=links,
            rejected_ambiguous_terms=tuple(dict.fromkeys(self._rejected_terms)),
        )

    def _safe_term(self, term: str) -> bool:
        if not term or term.upper() in _COMMON_TERMS:
            return False
        if _HANGUL.search(term):
            return len(term) >= 2
        return len(term) >= 4

    def _has_boundary(self, text: str, start: int, stop: int, term: str) -> bool:
        alphabet = "0-9A-Za-z가-힣" if _HANGUL.search(term) else "0-9A-Za-z"
        previous = text[start - 1] if start > 0 else ""
        following = text[stop] if stop < len(text) else ""
        return not re.match(rf"[{alphabet}]", previous) and not re.match(
            rf"[{alphabet}]", following
        )
