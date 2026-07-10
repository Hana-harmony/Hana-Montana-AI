import hashlib
import importlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Protocol, cast

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import (
    FinancialTermConfidenceLevel,
    FinancialTermDisplayMode,
    FinancialTermEvidence,
    FinancialTermSourceType,
    KoreanFinancialTermExplainRequest,
    KoreanFinancialTermExplainResponse,
)
from hannah_montana_ai.services.model import require_lora_adapter_artifact

MODEL_PROMPT_VERSION = "k-finance-term-qwen3-rag-prompt-v1"
RESPONSE_CACHE_TTL_SECONDS = 30 * 24 * 60 * 60
REVIEW_CACHE_TTL_SECONDS = 24 * 60 * 60
LOCAL_QWEN_TERM_SOURCE = "LOCAL_OPEN_SOURCE_LLM_RAG"
ALLOWED_GENERATED_SOURCES = {LOCAL_QWEN_TERM_SOURCE}
ENGLISH_LOCALISM_LOOKUP_TERMS = frozenset(
    {
        "ant",
        "ants",
        "gaemi",
        "gaemee",
        "samjeonnix",
    }
)
TERM_GENERATION_CATEGORIES = {
    "market_slang",
    "ipo_slang",
    "policy_theme",
    "capital_market",
    "risk_slang",
    "metric",
    "theme_stock",
    "capital_action",
    "valuation_metric",
    "unknown",
}
_TOKEN_PATTERN = re.compile(r"[0-9A-Za-z가-힣%+.\-]+")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?。！？])\s+|(?<=[다요음임됨함했다였다])\.\s*")
_INVESTMENT_ADVICE_PATTERN = re.compile(
    r"\b(buy|sell|hold|strong buy|target price|price target)\b|매수|매도|보유|목표가",
    re.IGNORECASE,
)


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


@dataclass(frozen=True)
class GeneratedTermExplanation:
    english_term: str
    category: str
    definition: str
    explanation: str
    example: str
    confidence_score: float
    evidence: tuple[FinancialTermEvidence, ...]
    source: str


class TermExplanationProvider(Protocol):
    def generate(
        self,
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> GeneratedTermExplanation | None:
        pass


class TermGenerationClient(Protocol):
    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        pass


type MlxTermModelLoader = Callable[[str, Path | None], tuple[Any, Any]]
type MlxTermTextGenerator = Callable[[Any, Any, str, int, float], str]


class QwenHttpTermExplanationClient:
    def __init__(self, endpoint: str, model: str, timeout_seconds: float) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        parsed_url = urllib.parse.urlparse(self._endpoint)
        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("LLM endpoint must use http or https")
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.1,
            "top_p": 0.8,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(  # noqa: S310
            f"{self._endpoint}/v1/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(  # noqa: S310  # nosec B310
            request,
            timeout=self._timeout_seconds,
        ) as response:
            body = json.loads(response.read().decode("utf-8"))
        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("LLM response has no choices")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise ValueError("LLM response has no message")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response content is empty")
        return content


class MlxQwenTermExplanationClient:
    def __init__(
        self,
        *,
        model: str,
        adapter_path: Path | None,
        temperature: float = 0.0,
        model_loader: MlxTermModelLoader | None = None,
        text_generator: MlxTermTextGenerator | None = None,
    ) -> None:
        self._model_name = model
        self._adapter_path = adapter_path
        self._temperature = temperature
        self._model_loader = model_loader or self._load_mlx_model
        self._text_generator = text_generator or self._generate_mlx_text
        self._pipeline: tuple[Any, Any] | None = None

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        model, tokenizer = self._load_pipeline()
        prompt = self._format_chat_prompt(messages, tokenizer)
        return self._text_generator(
            model,
            tokenizer,
            prompt,
            max_tokens,
            self._temperature,
        )

    def _load_pipeline(self) -> tuple[Any, Any]:
        if self._pipeline is None:
            self._pipeline = self._model_loader(self._model_name, self._adapter_path)
        return self._pipeline

    @staticmethod
    def _load_mlx_model(model_name: str, adapter_path: Path | None) -> tuple[Any, Any]:
        try:
            mlx_lm = importlib.import_module("mlx_lm")
        except ImportError as exception:
            raise ValueError(
                "mlx_lm is required for direct Korean term Qwen3 local generation"
            ) from exception
        load = cast(Callable[..., tuple[Any, Any]], mlx_lm.load)
        return load(
            model_name,
            adapter_path=str(adapter_path) if adapter_path is not None else None,
        )

    @staticmethod
    def _generate_mlx_text(
        model: Any,
        tokenizer: Any,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        try:
            mlx_lm = importlib.import_module("mlx_lm")
        except ImportError as exception:
            raise ValueError(
                "mlx_lm is required for direct Korean term Qwen3 local generation"
            ) from exception
        sample_utils = importlib.import_module("mlx_lm.sample_utils")
        make_sampler = cast(Callable[..., Callable[[Any], Any]], sample_utils.make_sampler)
        generate = cast(Callable[..., str], mlx_lm.generate)
        return generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=make_sampler(temp=temperature),
            verbose=False,
        )

    @staticmethod
    def _format_chat_prompt(messages: list[dict[str, str]], tokenizer: Any) -> str:
        apply_chat_template = getattr(tokenizer, "apply_chat_template", None)
        if callable(apply_chat_template):
            try:
                return cast(
                    str,
                    apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=False,
                    ),
                )
            except TypeError:
                return cast(
                    str,
                    apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                    ),
                )

        rendered_messages = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            rendered_messages.append(f"<|im_start|>{role}\n{content}<|im_end|>")
        rendered_messages.append("<|im_start|>assistant\n")
        return "\n".join(rendered_messages)


class LocalQwenTermExplanationProvider:
    def __init__(
        self,
        *,
        model_name: str,
        max_tokens: int,
        client: TermGenerationClient,
    ) -> None:
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._client = client

    def generate(
        self,
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> GeneratedTermExplanation | None:
        if not _contains_hangul(request.term) or not context_evidence:
            return None
        try:
            raw_content = self._client.generate(
                self.messages(request, context_evidence),
                max_tokens=self._max_tokens,
            )
            parsed = _parse_json_object(_strip_thinking(raw_content))
            generated = self._generated_from_payload(
                parsed,
                request=request,
                context_evidence=context_evidence,
            )
            if not generated or not self._is_quality_output(generated, request):
                return None
            return generated
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError):
            return None

    @staticmethod
    def messages(
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "Return strict JSON with exactly these keys: english_term, category, "
                    "definition, explanation, example, confidence_score. Explain only the "
                    "clicked Korean stock-market slang, theme, policy, IPO, risk, or metric "
                    "term. Use only the supplied article evidence and curated category list. "
                    "Do not explain generic English finance words, investor types, or ordinary "
                    "company names as glossary terms. Do not give investment advice. Write the "
                    "definition and explanation in English for foreign investors. The Korean "
                    "clicked term may appear only as the quoted subject."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "term": request.term,
                        "locale": request.locale,
                        "source_type": request.source_type,
                        "article_title": request.title,
                        "article_context_evidence": [
                            evidence.model_dump(mode="json") for evidence in context_evidence
                        ],
                        "stock_code": request.stock_code,
                        "stock_name": request.stock_name,
                        "allowed_categories": sorted(TERM_GENERATION_CATEGORIES),
                        "quality_contract": {
                            "english_term": "short plain English label, not a ticker",
                            "definition": "one sentence under 80 words",
                            "explanation": "2 sentences, grounded in article evidence",
                            "example": "short English example using the clicked term",
                            "confidence_score": "0.70 to 0.92 for evidence-backed outputs",
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    @staticmethod
    def training_example(
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
        target: GeneratedTermExplanation,
    ) -> dict[str, object]:
        return {
            "schema_version": "korean-financial-term-explanation-sft/v1",
            "prompt_version": MODEL_PROMPT_VERSION,
            "messages": [
                *LocalQwenTermExplanationProvider.messages(request, context_evidence),
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "english_term": target.english_term,
                            "category": target.category,
                            "definition": target.definition,
                            "explanation": target.explanation,
                            "example": target.example,
                            "confidence_score": target.confidence_score,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "target": {
                "english_term": target.english_term,
                "category": target.category,
                "definition": target.definition,
                "explanation": target.explanation,
                "example": target.example,
                "confidence_score": target.confidence_score,
            },
        }

    def _generated_from_payload(
        self,
        payload: dict[str, object],
        *,
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> GeneratedTermExplanation | None:
        english_term = str(payload.get("english_term", "")).strip()[:120]
        category = str(payload.get("category", "unknown")).strip()[:60] or "unknown"
        definition = _sanitize_text(str(payload.get("definition", "")), max_length=1000)
        explanation = _sanitize_text(str(payload.get("explanation", "")), max_length=1200)
        example = _sanitize_text(str(payload.get("example", "")), max_length=500)
        score = _bounded_float(payload.get("confidence_score"), default=0.72)
        if category not in TERM_GENERATION_CATEGORIES:
            return None
        if not english_term or not definition or not explanation:
            return None
        if _INVESTMENT_ADVICE_PATTERN.search(f"{definition} {explanation} {example}"):
            return None
        if request.term not in f"{definition} {explanation} {example}":
            return None
        return GeneratedTermExplanation(
            english_term=english_term,
            category=category,
            definition=definition,
            explanation=explanation,
            example=example,
            confidence_score=score,
            evidence=context_evidence[:6],
            source=LOCAL_QWEN_TERM_SOURCE,
        )

    def _is_quality_output(
        self,
        generated: GeneratedTermExplanation,
        request: KoreanFinancialTermExplainRequest,
    ) -> bool:
        combined = f"{generated.definition} {generated.explanation} {generated.example}"
        if _has_repeated_adjacent_word(combined):
            return False
        if generated.english_term.lower() in {"earnings", "foreign investors", "institutions"}:
            return False
        if "not verified" in combined.lower() or "review required" in combined.lower():
            return False
        sentences = [
            sentence
            for sentence in re.split(r"(?<=[.!?])\s+", generated.explanation.strip())
            if sentence.strip()
        ]
        if len(sentences) != 2:
            return False
        return request.term in combined


class KoreanFinancialTermExplanationService:
    def __init__(
        self,
        *,
        seed_path: Path,
        model_version: str,
        provider: TermExplanationProvider | None = None,
    ) -> None:
        self._entries = _load_entries(seed_path)
        self._index = _build_index(self._entries)
        self._model_version = model_version
        self._provider = provider

    def explain(
        self,
        request: KoreanFinancialTermExplainRequest,
    ) -> KoreanFinancialTermExplainResponse:
        normalized_request_term = _normalize_term(request.term)
        matched_entry = self._index.get(normalized_request_term)
        context_evidence = _context_evidence(request)
        if not _contains_hangul(request.term) and not _is_allowed_english_localism_lookup(
            request.term,
            matched_entry,
        ):
            return self._from_non_korean_generic_term(request, context_evidence)
        if matched_entry:
            return self._from_dictionary(request, matched_entry, context_evidence)

        provider_result = None
        if self._provider:
            provider_result = self._provider.generate(request, context_evidence)
        if provider_result:
            return self._from_generated(request, provider_result)

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
                    title="Hannah Korean financial term seed glossary",
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

    def _from_generated(
        self,
        request: KoreanFinancialTermExplainRequest,
        generated: GeneratedTermExplanation,
    ) -> KoreanFinancialTermExplainResponse:
        score = generated.confidence_score
        source = _generated_source(generated.source)
        source_flag = "LOCAL_QWEN_RAG" if source == LOCAL_QWEN_TERM_SOURCE else "WEB_SEARCH_RAG"
        flags = [source_flag, "CACHEABLE_AFTER_REVIEW" if score < 0.82 else "CACHEABLE"]
        if _INVESTMENT_ADVICE_PATTERN.search(generated.explanation):
            flags.append("INVESTMENT_ADVICE_FILTERED")
            score = min(score, 0.39)
        confidence_level: FinancialTermConfidenceLevel = _confidence_level(score)
        display_mode: FinancialTermDisplayMode = (
            "EXPLANATION" if score >= 0.70 else "REVIEW_REQUIRED"
        )
        return KoreanFinancialTermExplainResponse(
            term=request.term,
            normalized_term=_normalize_display_term(request.term),
            english_term=generated.english_term,
            category=generated.category,
            definition=generated.definition,
            explanation=generated.explanation,
            example=generated.example,
            confidence_score=round(score, 4),
            confidence_level=confidence_level,
            display_mode=display_mode,
            source=source,
            cacheable=score >= 0.70,
            cache_ttl_seconds=(
                RESPONSE_CACHE_TTL_SECONDS if score >= 0.82 else REVIEW_CACHE_TTL_SECONDS
            ),
            evidence=list(generated.evidence[:8]),
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
                f'"{request.term}" appears in this Korean market article, '
                "but the system does not "
                "yet have enough verified evidence to provide a definitive foreign-investor "
                "explanation."
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


def build_term_provider_from_settings(settings: Settings) -> TermExplanationProvider | None:
    if settings.korean_financial_term_generation_mode == "local_llm":
        if settings.korean_financial_term_llm_endpoint:
            return LocalQwenTermExplanationProvider(
                model_name=settings.korean_financial_term_llm_model,
                max_tokens=settings.korean_financial_term_llm_max_tokens,
                client=QwenHttpTermExplanationClient(
                    endpoint=settings.korean_financial_term_llm_endpoint,
                    model=settings.korean_financial_term_llm_model,
                    timeout_seconds=settings.korean_financial_term_llm_timeout_seconds,
                ),
            )
        return LocalQwenTermExplanationProvider(
            model_name=settings.korean_financial_term_mlx_model,
            max_tokens=settings.korean_financial_term_llm_max_tokens,
            client=MlxQwenTermExplanationClient(
                model=settings.korean_financial_term_mlx_model,
                adapter_path=require_lora_adapter_artifact(
                    settings.korean_financial_term_mlx_adapter_path,
                    "Korean financial term Qwen3 LoRA adapter",
                ),
            ),
        )
    return None


def _load_entries(path: Path) -> tuple[FinancialTermEntry, ...]:
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
                index[_normalize_term(variant)] = entry
    return index


def _term_variants(value: str) -> tuple[str, ...]:
    compact = " ".join(value.split()).strip()
    if not compact:
        return ()
    variants = {compact}
    lowered = compact.lower()
    if lowered.endswith("s") and len(lowered) > 3:
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
    if normalized not in ENGLISH_LOCALISM_LOOKUP_TERMS:
        return False
    aliases = {_normalize_term(alias) for alias in entry.aliases}
    return normalized in aliases


def _is_english_display_term(term: str, entry: FinancialTermEntry) -> bool:
    normalized_request = _normalize_term(term)
    if not normalized_request:
        return False
    korean_terms = {entry.normalized_term, *entry.aliases}
    if any("가" <= char <= "힣" for value in korean_terms for char in value):
        korean_normalized = {
            _normalize_term(value)
            for value in korean_terms
            if any("가" <= char <= "힣" for char in value)
        }
        if normalized_request in korean_normalized:
            return False
    return bool(re.search(r"[A-Za-z]", term))


def _english_dictionary_explanation(term: str, entry: FinancialTermEntry) -> str:
    display_term = " ".join(term.split()).strip() or entry.english_term
    definition = entry.definition.rstrip(".")
    category_context = {
        "market_slang": "Korean market news",
        "ipo_slang": "Korean IPO news",
        "capital_market": "Korean capital-market news",
        "policy_theme": "Korean policy and market-theme news",
        "risk_slang": "Korean risk-related market news",
        "capital_action": "Korean corporate-action news",
    }.get(entry.category, "Korean market news")
    return (
        f'The term "{display_term}" refers to {definition}. '
        f"In {category_context}, it helps foreign investors understand the local "
        "market role or narrative without relying on a literal translation."
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
    evidence: list[FinancialTermEvidence] = []
    for sentence in matched[:4]:
        title = request.title or f"Article context for {term}"
        evidence.append(
            FinancialTermEvidence(
                title=title[:180],
                snippet=sentence[:800],
                url=request.article_url[:1000],
                source_type="article_context",
            )
        )
    return tuple(evidence)


def _split_sentences(text: str) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    candidates = _SENTENCE_SPLIT_PATTERN.split(cleaned)
    return [candidate.strip() for candidate in candidates if candidate.strip()]


def _parse_json_object(text: str) -> dict[str, object]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        stripped = stripped[start : end + 1]
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return {}
    if isinstance(parsed, dict):
        return parsed
    return {}


def _strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _sanitize_text(value: str, *, max_length: int) -> str:
    sanitized = re.sub(r"\s+", " ", value).strip()
    return sanitized[:max_length].strip()


def _has_repeated_adjacent_word(value: str) -> bool:
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9'-]*\b", value.lower())
    return any(
        left == right and len(left) > 2 for left, right in zip(words, words[1:], strict=False)
    )


def _generated_source(source: str) -> FinancialTermSourceType:
    if source in ALLOWED_GENERATED_SOURCES:
        return cast(FinancialTermSourceType, source)
    return "UNVERIFIED_CONTEXT"


def _bounded_float(value: Any, *, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def _confidence_level(score: float) -> Literal["LOW", "MEDIUM", "HIGH"]:
    if score >= 0.82:
        return "HIGH"
    if score >= 0.60:
        return "MEDIUM"
    return "LOW"


def term_cache_key(term: str, locale: str, context: str) -> str:
    normalized = f"{_normalize_term(term)}|{locale}|{context[:500]}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
