from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.domain.schemas import (
    FinancialTermEvidence,
    KoreanFinancialTermExplainRequest,
    KoreanFinancialTermExplainResponse,
)

RESPONSE_CACHE_TTL_SECONDS = 30 * 24 * 60 * 60
REVIEW_CACHE_TTL_SECONDS = 24 * 60 * 60
ENGLISH_LOCALISM_LOOKUP_TERMS = frozenset(
    {
        "ant",
        "ants",
        "gaemi",
        "gaemee",
        "daejangju",
        "donghakant",
        "donghakants",
        "seohakant",
        "seohakants",
        "samjeonnix",
    }
)
_TOKEN_PATTERN = re.compile(r"[0-9A-Za-z가-힣%+.\-]+")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?。！？])\s+|(?<=[다요음임됨함했다였다])\.\s*")


@dataclass(frozen=True)
class FinancialTermEntry:
    normalized_term: str
    english_term: str
    category: str
    aliases: tuple[str, ...]
    definition: str
    plain_explanation: str
    example: str
    source: str

    def terms(self) -> tuple[str, ...]:
        return (self.normalized_term, self.english_term, *self.aliases)


class KoreanFinancialTermExplanationService:
    def __init__(self, *, seed_path: Path, model_version: str) -> None:
        self._entries = load_financial_term_entries(seed_path)
        self._index = _build_index(self._entries)
        self._model_version = model_version

    def explain(
        self,
        request: KoreanFinancialTermExplainRequest,
    ) -> KoreanFinancialTermExplainResponse:
        matched_entry = self._index.get(_normalize_term(request.term))
        context_evidence = _context_evidence(request)
        if not _contains_hangul(request.term) and not _is_allowed_english_localism_lookup(
            request.term,
            matched_entry,
        ):
            return self._from_non_korean_generic_term(request, context_evidence)
        if matched_entry:
            return self._from_dictionary(request, matched_entry, context_evidence)
        return self._from_unverified_context(request, context_evidence)

    def _from_non_korean_generic_term(
        self,
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> KoreanFinancialTermExplainResponse:
        normalized_term = _normalize_display_term(request.term)
        return KoreanFinancialTermExplainResponse(
            term=request.term,
            normalized_term=normalized_term,
            english_term="",
            category="not_glossary",
            definition="",
            explanation=(
                f'"{normalized_term}" is not a Korean local-market glossary term. '
                "Only Korean slang, policy themes, IPO slang, disclosure terms, risk terms, "
                "and explicit local-market romanizations are eligible for explanation."
            ),
            example="",
            confidence_score=0.0,
            confidence_level="LOW",
            display_mode="TEXT_ONLY",
            source="INTERNAL_CONTEXT_RAG",
            cacheable=False,
            cache_ttl_seconds=REVIEW_CACHE_TTL_SECONDS,
            evidence=list(context_evidence[:3]),
            quality_flags=["NON_KOREAN_GLOSSARY_TERM_IGNORED"],
            model_version=self._model_version,
            generated_at=datetime.now(UTC),
        )

    def _from_dictionary(
        self,
        request: KoreanFinancialTermExplainRequest,
        entry: FinancialTermEntry,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> KoreanFinancialTermExplainResponse:
        flags = ["DICTIONARY_HIT", "CACHEABLE"]
        if context_evidence:
            flags.append("ARTICLE_CONTEXT_ATTACHED")
        explanation = entry.plain_explanation
        example = entry.example
        if _is_english_display_term(request.term, entry):
            explanation = _english_dictionary_explanation(request.term, entry)
            example = _english_dictionary_example(request.term, entry)
        return KoreanFinancialTermExplainResponse(
            term=request.term,
            normalized_term=entry.normalized_term,
            english_term=entry.english_term,
            category=entry.category,
            definition=entry.definition,
            explanation=explanation,
            example=example,
            confidence_score=0.94,
            confidence_level="HIGH",
            display_mode="EXPLANATION",
            source="DICTIONARY",
            cacheable=True,
            cache_ttl_seconds=RESPONSE_CACHE_TTL_SECONDS,
            evidence=[
                FinancialTermEvidence(
                    title="Hannah Korean financial term dictionary",
                    snippet=entry.definition,
                    url="",
                    source_type=entry.source,
                ),
                *context_evidence[:3],
            ],
            quality_flags=flags,
            model_version=self._model_version,
            generated_at=datetime.now(UTC),
        )

    def _from_unverified_context(
        self,
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> KoreanFinancialTermExplainResponse:
        explanation = (
            f'"{request.term}" is not verified in the Korean financial term dictionary yet. '
            "The term should be reviewed with recent article context before showing a "
            "definitive explanation."
        )
        if context_evidence:
            explanation = (
                f'"{request.term}" appears in this Korean market article, but the system '
                "does not yet have enough verified evidence to provide a definitive "
                "foreign-investor explanation."
            )
        return KoreanFinancialTermExplainResponse(
            term=request.term,
            normalized_term=_normalize_display_term(request.term),
            english_term="",
            category="unknown",
            definition="",
            explanation=explanation,
            example="",
            confidence_score=0.36 if context_evidence else 0.18,
            confidence_level="LOW",
            display_mode="REVIEW_REQUIRED",
            source="UNVERIFIED_CONTEXT" if context_evidence else "INTERNAL_CONTEXT_RAG",
            cacheable=False,
            cache_ttl_seconds=REVIEW_CACHE_TTL_SECONDS,
            evidence=list(context_evidence),
            quality_flags=["UNKNOWN_TERM_REVIEW_REQUIRED"],
            model_version=self._model_version,
            generated_at=datetime.now(UTC),
        )


def load_financial_term_entries(path: Path) -> tuple[FinancialTermEntry, ...]:
    seed_path = _resolve_seed_path(path)
    rows = json.loads(seed_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("financial term seed must be a list")
    entries: list[FinancialTermEntry] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        aliases = row.get("aliases", [])
        entries.append(
            FinancialTermEntry(
                normalized_term=str(row.get("normalized_term", "")).strip(),
                english_term=str(row.get("english_term", "")).strip(),
                category=str(row.get("category", "")).strip(),
                aliases=tuple(str(alias).strip() for alias in aliases if str(alias).strip()),
                definition=str(row.get("definition", "")).strip(),
                plain_explanation=str(row.get("plain_explanation", "")).strip(),
                example=str(row.get("example", "")).strip(),
                source=str(row.get("source", "HANNAH_SEED_GLOSSARY")).strip(),
            )
        )
    return tuple(entry for entry in entries if entry.normalized_term and entry.plain_explanation)


def _resolve_seed_path(path: Path) -> Path:
    if path.exists():
        return path
    project_root_path = Path(__file__).resolve().parents[3] / path
    if project_root_path.exists():
        return project_root_path
    raise FileNotFoundError(f"financial term seed file not found: {path}")


def _build_index(entries: tuple[FinancialTermEntry, ...]) -> dict[str, FinancialTermEntry]:
    index: dict[str, FinancialTermEntry] = {}
    for entry in entries:
        for term in entry.terms():
            for variant in _term_variants(term):
                normalized = _normalize_term(variant)
                if normalized and normalized not in index:
                    index[normalized] = entry
    return index


def _term_variants(value: str) -> tuple[str, ...]:
    compact = " ".join(value.split()).strip()
    if not compact:
        return ()
    variants = {compact}
    if compact.lower().endswith("s") and len(compact) > 3:
        variants.add(compact[:-1])
    else:
        variants.add(f"{compact}s")
    return tuple(variants)


def _normalize_term(value: str) -> str:
    return "".join(_TOKEN_PATTERN.findall(value)).lower()


def _normalize_display_term(value: str) -> str:
    compact = " ".join(value.split()).strip()
    return compact[:80] if compact else value[:80]


def _contains_hangul(value: str) -> bool:
    return bool(re.search(r"[가-힣]", value))


def _is_allowed_english_localism_lookup(
    term: str,
    entry: FinancialTermEntry | None,
) -> bool:
    if entry is None:
        return False
    normalized = _normalize_term(term)
    return normalized in ENGLISH_LOCALISM_LOOKUP_TERMS


def _is_english_display_term(term: str, entry: FinancialTermEntry) -> bool:
    normalized_request = _normalize_term(term)
    korean_terms = {entry.normalized_term, *entry.aliases}
    korean_normalized = {
        _normalize_term(value)
        for value in korean_terms
        if any("가" <= char <= "힣" for char in value)
    }
    return bool(re.search(r"[A-Za-z]", term)) and normalized_request not in korean_normalized


def _english_dictionary_explanation(term: str, entry: FinancialTermEntry) -> str:
    display_term = " ".join(term.split()).strip() or entry.english_term
    definition = entry.definition.rstrip(".")
    return (
        f'The term "{display_term}" refers to {definition}. '
        "In Korean market news, it preserves the local-market expression while the "
        "explanation supplies its meaning."
    )


def _english_dictionary_example(term: str, entry: FinancialTermEntry) -> str:
    display_term = " ".join(term.split()).strip() or entry.english_term
    return f'In a translated article, "{display_term}" is the clickable local-market term.'


def _context_evidence(
    request: KoreanFinancialTermExplainRequest,
) -> tuple[FinancialTermEvidence, ...]:
    term = request.term.strip()
    text = "\n".join(part for part in (request.title, request.context) if part)
    if not term or not text:
        return ()
    sentences = _split_sentences(text)
    matched = [sentence for sentence in sentences if term in sentence]
    if not matched and request.context:
        matched = sentences[:2]
    return tuple(
        FinancialTermEvidence(
            title=(request.title or f"Article context for {term}")[:180],
            snippet=sentence[:800],
            url=request.article_url[:1000],
            source_type="article_context",
        )
        for sentence in matched[:4]
    )


def _split_sentences(text: str) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    return [
        candidate.strip()
        for candidate in _SENTENCE_SPLIT_PATTERN.split(cleaned)
        if candidate.strip()
    ]


def term_cache_key(term: str, locale: str, context: str) -> str:
    normalized = f"{_normalize_term(term)}|{locale}|{context[:500]}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
