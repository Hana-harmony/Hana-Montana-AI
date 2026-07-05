from __future__ import annotations

import importlib
import json
import re
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm, SourceType, TranslationStatus

KOREAN_TRANSLATION_PROMPT_VERSION = "ko-en-qwen3-financial-translation-v1"
LOCAL_TRANSLATION_PROVIDER = "local-open-source-qwen3-translation"
SOURCE_LANGUAGE_FALLBACK_PROVIDER = "source-language-fallback"
STATUS_TRANSLATED: TranslationStatus = "TRANSLATED"
STATUS_PARTIAL_SOURCE_LANGUAGE_FALLBACK: TranslationStatus = "PARTIAL_SOURCE_LANGUAGE_FALLBACK"
STATUS_SOURCE_LANGUAGE_FALLBACK: TranslationStatus = "SOURCE_LANGUAGE_FALLBACK"


@dataclass(frozen=True)
class KoreanTranslationContext:
    text: str
    source_type: SourceType = "NEWS"
    title: str = ""
    glossary_terms: list[FinancialGlossaryTerm] | None = None


@dataclass(frozen=True)
class KoreanTranslationResult:
    translated_text: str
    provider: str
    model_version: str
    status: TranslationStatus
    prompt_version: str
    quality_flags: list[str]


class TranslationClient(Protocol):
    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        pass


type MlxModelLoader = Callable[[str, Path | None], tuple[Any, Any]]
type MlxTextGenerator = Callable[[Any, Any, str, int, float], str]


class OpenAiCompatibleKoreanTranslationClient:
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
            "temperature": 0.0,
            "top_p": 0.8,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(  # noqa: S310
            f"{self._endpoint}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
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


class MlxQwenKoreanTranslationClient:
    def __init__(
        self,
        *,
        model: str,
        adapter_path: Path | None,
        temperature: float = 0.0,
        model_loader: MlxModelLoader | None = None,
        text_generator: MlxTextGenerator | None = None,
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
        return self._text_generator(model, tokenizer, prompt, max_tokens, self._temperature)

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
                "mlx_lm is required for direct Korean translation generation"
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
                "mlx_lm is required for direct Korean translation generation"
            ) from exception
        sample_utils = importlib.import_module("mlx_lm.sample_utils")
        make_sampler = cast(Callable[..., Callable[[Any], Any]], sample_utils.make_sampler)
        sampler = make_sampler(temp=temperature)
        generate = cast(Callable[..., str], mlx_lm.generate)
        return generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
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


class KoreanTranslationGenerator:
    _HANGUL_PATTERN = re.compile("[가-힣]")
    _BAD_OUTPUT_TERMS = (
        "as an ai",
        "i cannot",
        "i can't",
        "cannot translate",
        "please provide",
        "summary:",
        "translation:",
        "korean financial news",
    )
    _LOCALISM_REPLACEMENTS = {
        "개미": (
            "Ants",
            (
                "retail investor",
                "retail investors",
                "individual investor",
                "individual investors",
                "ant investor",
                "ant investors",
                "small investor",
                "small investors",
                "mom-and-pop investor",
                "mom-and-pop investors",
                "mom and pop investor",
                "mom and pop investors",
                "Triangunxi's",
                "Triangunxi",
                "Gaemi's",
                "Gaemi",
                "country-investor",
                "country-investors",
                "country investor",
                "country investors",
            ),
        ),
        "대장주": (
            "bellwether stock",
            (
                "sector leader stock",
                "sector leader stocks",
                "market leader stock",
                "market leader stocks",
                "leading stock",
                "leading stocks",
                "leading share",
                "leading shares",
                "flagship stock",
                "flagship stocks",
                "flagship share",
                "flagship shares",
                "bellwether stocks",
                "semiconductor leader",
                "semiconductor leaders",
                "semiconductor bellwether",
                "semiconductor bellwethers",
                "semiconductor bellwether stocks",
                "large-cap stock",
                "large-cap stocks",
                "large cap stock",
                "large cap stocks",
                "blue-chip stock",
                "blue-chip stocks",
                "blue chip stock",
                "blue chip stocks",
            ),
        ),
        "따따블": (
            "dda-dda-ble",
            (
                "IPO quadruple jump",
                "IPO quadruple jumps",
                "quadruple IPO jump",
                "quadruple IPO jumps",
                "fourfold IPO jump",
                "fourfold IPO jumps",
            ),
        ),
        "품절주": (
            "low-float stock",
            (
                "thin-float stock",
                "thin-float stocks",
                "scarce-float stock",
                "scarce-float stocks",
                "low float stock",
                "low float stocks",
            ),
        ),
        "삼전닉스": (
            "Samjeon Nix",
            (
                "Samsung Electronics and SK Hynix",
                "Samsung Electronics-SK Hynix",
                "Samsung Electronics/SK Hynix",
                "Samsung Electronics & SK Hynix",
                "Samsung Electronics + SK Hynix",
                "Samsung Electronics, SK Hynix",
                "Samsung Electronics and SK hynix",
                "Samsung Electronics-SK hynix",
                "Samsung Electronics/SK hynix",
                "Samsung Electronics & SK hynix",
                "Samsung Electronics + SK hynix",
                "Samsung Electronics, SK hynix",
                "Samsung Electronics and SK Hynix basket",
                "Samsung Electronics and SK hynix basket",
            ),
        ),
    }

    def __init__(
        self,
        *,
        enabled: bool = False,
        client: TranslationClient | None = None,
        model_name: str = "Qwen3-0.6B-GGUF-Q4",
        max_tokens: int = 900,
    ) -> None:
        self._enabled = enabled
        self._client = client
        self._model_name = model_name
        self._max_tokens = max_tokens

    @classmethod
    def from_settings(cls, settings: Settings) -> KoreanTranslationGenerator:
        mode = settings.korean_translation_generation_mode.strip().lower()
        if mode not in {"local_llm", "qwen", "open_source"}:
            return cls(enabled=False, model_name=settings.korean_translation_llm_model)
        if settings.korean_translation_llm_endpoint.strip():
            client: TranslationClient = OpenAiCompatibleKoreanTranslationClient(
                endpoint=settings.korean_translation_llm_endpoint,
                model=settings.korean_translation_llm_model,
                timeout_seconds=settings.korean_translation_llm_timeout_seconds,
            )
            model_name = f"local-llm:{settings.korean_translation_llm_model}"
        else:
            adapter_path = (
                settings.korean_translation_mlx_adapter_path
                if settings.korean_translation_mlx_adapter_path.exists()
                else None
            )
            client = MlxQwenKoreanTranslationClient(
                model=settings.korean_translation_mlx_model,
                adapter_path=adapter_path,
            )
            model_name = f"local-llm:{settings.korean_translation_mlx_model}"
        return cls(
            enabled=True,
            client=client,
            model_name=model_name,
            max_tokens=settings.korean_translation_llm_max_tokens,
        )

    def translate(self, context: KoreanTranslationContext) -> KoreanTranslationResult:
        source_text = self._normalize_text(context.text)
        if not source_text:
            return self._fallback("", ["EMPTY_SOURCE"])
        if not self._enabled or self._client is None:
            return self._fallback("", ["LOCAL_TRANSLATION_DISABLED"])

        chunks = self._chunks(source_text)
        translated_chunks: list[str] = []
        flags: list[str] = []
        for chunk in chunks:
            result = self._translate_chunk(chunk, context)
            translated_chunks.append(result.translated_text)
            flags.extend(result.quality_flags)

        translated_text = "\n".join(part for part in translated_chunks if part)
        status: TranslationStatus = (
            STATUS_TRANSLATED
            if translated_text and not flags
            else STATUS_PARTIAL_SOURCE_LANGUAGE_FALLBACK
            if translated_text
            else STATUS_SOURCE_LANGUAGE_FALLBACK
        )
        provider = (
            LOCAL_TRANSLATION_PROVIDER if translated_text else SOURCE_LANGUAGE_FALLBACK_PROVIDER
        )
        return KoreanTranslationResult(
            translated_text=translated_text,
            provider=provider,
            model_version=self._model_name,
            status=status,
            prompt_version=KOREAN_TRANSLATION_PROMPT_VERSION,
            quality_flags=sorted(set(flags)),
        )

    def _translate_chunk(
        self,
        chunk: str,
        context: KoreanTranslationContext,
    ) -> KoreanTranslationResult:
        if self._client is None:
            return self._fallback("", ["LOCAL_TRANSLATION_DISABLED"])
        active_glossary_terms = self._active_glossary_terms(
            chunk,
            context.glossary_terms or [],
        )
        try:
            output = self._client.generate(
                self._messages(chunk, context, active_glossary_terms),
                self._max_tokens,
            )
            translated = self._parse_translation(output)
        except Exception:
            return self._fallback("", ["LOCAL_TRANSLATION_PROVIDER_ERROR"])

        translated = self._apply_glossary_surfaces(
            self._normalize_text(translated),
            active_glossary_terms,
        )
        quality_flags = self._quality_flags(chunk, translated)
        quality_flags.extend(self._glossary_quality_flags(translated, active_glossary_terms))
        if quality_flags:
            return self._fallback("", quality_flags)
        return KoreanTranslationResult(
            translated_text=translated,
            provider=LOCAL_TRANSLATION_PROVIDER,
            model_version=self._model_name,
            status=STATUS_TRANSLATED,
            prompt_version=KOREAN_TRANSLATION_PROMPT_VERSION,
            quality_flags=[],
        )

    def _messages(
        self,
        text: str,
        context: KoreanTranslationContext,
        glossary_terms: list[FinancialGlossaryTerm],
    ) -> list[dict[str, str]]:
        glossary = [
            {
                "source_term": term.source_term,
                "normalized_term": term.normalized_term,
                "english_term": term.english_term,
                "category": term.category,
            }
            for term in glossary_terms
        ]
        payload = {
            "task": "Translate Korean financial news or disclosures into English.",
            "schema": {"translation": "complete English translation of source_text"},
            "rules": [
                "Return only compact JSON with key translation.",
                "Translate every sentence; do not summarize, omit, or add facts.",
                "Use natural English for foreign retail investors.",
                "Preserve stock codes, numbers, dates, URLs, currencies, and company names.",
                "Use glossary terms when provided.",
                "When glossary includes Korean market slang, use the glossary surface exactly.",
                "Do not leave Korean Hangul characters in the translation.",
            ],
            "source_type": context.source_type,
            "title": context.title,
            "glossary": glossary,
            "source_text": text,
        }
        return [
            {
                "role": "system",
                "content": (
                    "You are a Korean-to-English financial translator. "
                    "You translate the complete source text and output strict JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            },
        ]

    def _active_glossary_terms(
        self,
        source_text: str,
        glossary_terms: list[FinancialGlossaryTerm],
    ) -> list[FinancialGlossaryTerm]:
        return [
            term
            for term in glossary_terms
            if self._contains_source_term(source_text, term.source_term)
            or self._contains_source_term(source_text, term.normalized_term)
        ]

    def _contains_source_term(self, source_text: str, term: str) -> bool:
        candidate = term.strip()
        return bool(candidate) and candidate in source_text

    def _parse_translation(self, raw_output: str) -> str:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            value = parsed.get("translation")
            if isinstance(value, str):
                return value
        parsed = json.loads(cleaned)
        value = parsed.get("translation")
        if not isinstance(value, str):
            raise ValueError("translation is missing")
        return value

    def _quality_flags(self, source_text: str, translated_text: str) -> list[str]:
        flags: list[str] = []
        if not translated_text:
            flags.append("EMPTY_TRANSLATION")
        if self._HANGUL_PATTERN.search(translated_text):
            flags.append("HANGUL_REMAINS")
        if source_text.strip() == translated_text.strip() and self._HANGUL_PATTERN.search(
            source_text
        ):
            flags.append("SOURCE_LANGUAGE_FALLBACK")
        if translated_text.endswith(("...", "…")):
            flags.append("TRUNCATED_TRANSLATION")
        lowered = translated_text.lower()
        if any(term in lowered for term in self._BAD_OUTPUT_TERMS):
            flags.append("META_OR_REFUSAL_TEXT")
        if self._looks_like_summary(source_text, translated_text):
            flags.append("POSSIBLE_SUMMARY_INSTEAD_OF_TRANSLATION")
        return flags

    def _looks_like_summary(self, source_text: str, translated_text: str) -> bool:
        source_sentences = self._sentence_count(source_text)
        translated_sentences = self._sentence_count(translated_text)
        if source_sentences >= 3 and translated_sentences <= 1:
            return True
        if len(source_text) >= 260 and len(translated_text) < max(80, int(len(source_text) * 0.18)):
            return True
        return False

    def _sentence_count(self, text: str) -> int:
        return len(
            [part for part in re.split(r"[.!?。]|다(?=\s|$)|요(?=\s|$)", text) if part.strip()]
        )

    def _apply_glossary_surfaces(
        self,
        translated_text: str,
        glossary_terms: list[FinancialGlossaryTerm],
    ) -> str:
        result = translated_text
        terms_by_normalized = {term.normalized_term: term for term in glossary_terms}
        for normalized_term, (preferred, alternatives) in self._LOCALISM_REPLACEMENTS.items():
            if normalized_term not in terms_by_normalized:
                continue
            result = self._replace_localism_surface(result, preferred, (preferred,))
            if self._contains_phrase(result, preferred):
                continue
            term = terms_by_normalized[normalized_term]
            result = self._replace_localism_surface(
                result,
                preferred,
                (*alternatives, term.english_term),
            )
        return result

    def _replace_localism_surface(
        self,
        text: str,
        preferred: str,
        alternatives: tuple[str, ...],
    ) -> str:
        result = text
        for alternative in sorted(set(alternatives), key=len, reverse=True):
            candidate = alternative.strip()
            if not candidate:
                continue
            pattern = re.compile(
                r"\b(?:(?:a|an|the)\s+)?"
                + re.escape(candidate).replace(r"\ ", r"\s+")
                + r"\b",
                re.IGNORECASE | re.UNICODE,
            )
            replacement = preferred + "'" if candidate.lower().endswith("'s") else preferred
            result = pattern.sub(replacement, result)
        return result

    def _glossary_quality_flags(
        self,
        translated_text: str,
        glossary_terms: list[FinancialGlossaryTerm],
    ) -> list[str]:
        flags: list[str] = []
        normalized_terms = {term.normalized_term for term in glossary_terms}
        for normalized_term, (preferred, _) in self._LOCALISM_REPLACEMENTS.items():
            if normalized_term in normalized_terms and not self._contains_phrase(
                translated_text,
                preferred,
            ):
                flags.append(f"GLOSSARY_TERM_MISSING:{normalized_term}")
        return flags

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        pattern = re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE | re.UNICODE)
        return bool(pattern.search(text))

    def _fallback(self, translated_text: str, flags: list[str]) -> KoreanTranslationResult:
        return KoreanTranslationResult(
            translated_text=translated_text,
            provider=SOURCE_LANGUAGE_FALLBACK_PROVIDER,
            model_version=self._model_name,
            status=STATUS_SOURCE_LANGUAGE_FALLBACK,
            prompt_version=KOREAN_TRANSLATION_PROMPT_VERSION,
            quality_flags=sorted(set(flags)),
        )

    def _chunks(self, text: str) -> list[str]:
        max_chars = 1_200
        if len(text) <= max_chars:
            return [text]
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            split = self._split_point(text, start, end, max_chars)
            chunks.append(text[start:split].strip())
            start = split
            while start < len(text) and text[start].isspace():
                start += 1
        return chunks

    def _split_point(self, text: str, start: int, end: int, max_chars: int) -> int:
        if end >= len(text):
            return len(text)
        for index in range(end, start + max_chars // 2, -1):
            current = text[index - 1]
            if current in {".", "!", "?", "\n"} or current in {"다", "요"}:
                return index
        return end

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[ \t]+", " ", text).strip()
