from __future__ import annotations

import importlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import Importance, Sentiment, SourceType, SummaryLines
from hannah_montana_ai.services.model import require_lora_adapter_artifact

NEWS_SUMMARY_PROMPT_VERSION = "news-summary-qwen3-wwi-v1"


@dataclass(frozen=True)
class NewsSummaryContext:
    title: str
    snippet: str
    content: str
    source_type: SourceType
    importance: Importance
    sentiment: Sentiment
    event_tags: list[str]
    stock_code: str | None
    stock_name: str | None
    stock_name_en: str
    fallback: SummaryLines


class NewsSummaryClient(Protocol):
    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        pass


type MlxModelLoader = Callable[[str, Path | None], tuple[Any, Any]]
type MlxTextGenerator = Callable[[Any, Any, str, int, float], str]


class OpenAiCompatibleNewsSummaryClient:
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


class MlxQwenNewsSummaryClient:
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
                "mlx_lm is required for direct news summary Qwen3 local generation"
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
                "mlx_lm is required for direct news summary Qwen3 local generation"
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


class NewsSummaryGenerator:
    _META_TERMS = (
        "importance",
        "sentiment",
        "classified",
        "classification",
        "priority",
        "중요도",
        "감성",
        "분류",
    )
    _ADVICE_TERMS = (
        "guaranteed",
        "outperform",
        "price target",
        "must buy",
        "should buy",
        "must sell",
        "should sell",
    )
    _KOREAN_TO_ENGLISH_TERMS = {
        "반도체": ("semiconductor", "chip", "memory"),
        "메모리": ("memory",),
        "HBM": ("hbm",),
        "데이터센터": ("data center", "data-center"),
        "AI": ("ai", "artificial intelligence"),
        "서버": ("server",),
        "영업이익": ("operating profit", "earnings"),
        "실적": ("earnings", "results", "profit"),
        "수익성": ("profitability", "margin"),
        "주가": ("stock price", "shares"),
        "시가총액": ("market cap", "market capitalization"),
        "시총": ("market cap", "market capitalization"),
        "외국인": ("foreign investor", "foreign investors"),
        "기관": ("institutional investors", "institutions"),
        "순매수": ("net buying", "net purchase"),
        "순매도": ("net selling"),
        "코스피": ("kospi",),
        "코스닥": ("kosdaq",),
        "환율": ("exchange rate", "currency"),
        "금리": ("interest rate", "rates"),
        "수주": ("order", "orders", "contract"),
        "계약": ("contract", "deal"),
        "공급": ("supply",),
        "자사주": ("treasury share", "treasury-share", "buyback"),
        "소각": ("cancellation", "retirement"),
        "배당": ("dividend",),
        "유상증자": ("capital increase", "share issuance"),
        "전환사채": ("convertible bond",),
        "상장폐지": ("delisting",),
        "거래정지": ("trading halt",),
        "감사의견": ("audit opinion",),
        "소송": ("lawsuit", "litigation"),
        "리스크": ("risk",),
        "변동성": ("volatility",),
        "방산": ("defense",),
        "조선": ("shipbuilding",),
        "배터리": ("battery",),
        "바이오": ("biotech", "bio"),
        "인수": ("acquisition",),
        "합병": ("merger",),
        "분할": ("spin-off", "split"),
    }
    _ENGLISH_FALLBACK_TOPICS = (
        (("삼전닉스",), "Samsung Electronics and SK hynix trading"),
        (("영업이익",), "earnings recovery expectations"),
        (("실적",), "earnings recovery expectations"),
        (("어닝",), "earnings recovery expectations"),
        (("HBM", "메모리", "반도체"), "semiconductor and HBM demand"),
        (("외국인", "순매수"), "foreign-investor net buying"),
        (("외국인", "순매도"), "foreign-investor net selling"),
        (("기관", "순매수"), "institutional net buying"),
        (("기관", "순매도"), "institutional net selling"),
        (("코스피",), "the KOSPI market move"),
        (("코스닥",), "the KOSDAQ market move"),
        (("환율",), "exchange-rate pressure"),
        (("금리",), "interest-rate pressure"),
        (("수주", "계약"), "order and contract momentum"),
        (("공급",), "supply conditions"),
        (("자사주", "소각"), "treasury-share cancellation"),
        (("유상증자",), "paid-in capital increase"),
        (("배당",), "dividend policy"),
        (("상장폐지", "거래정지"), "listing and trading-risk issues"),
    )
    _ENGLISH_FALLBACK_DRIVERS = (
        (("HBM",), "HBM demand"),
        (("메모리",), "memory-market conditions"),
        (("데이터센터",), "data-center investment"),
        (("외국인",), "foreign-investor flow"),
        (("기관",), "institutional flow"),
        (("환율",), "currency moves"),
        (("금리",), "interest-rate expectations"),
        (("수주",), "new orders"),
        (("공급",), "supply changes"),
        (("정책",), "policy expectations"),
        (("공시",), "the company disclosure"),
    )
    _ENGLISH_FALLBACK_WATCH_ITEMS = (
        (("영업이익",), "operating-profit recovery and earnings guidance"),
        (("실적",), "operating-profit recovery and earnings guidance"),
        (("HBM", "메모리"), "memory pricing and HBM shipment momentum"),
        (("외국인", "기관"), "whether investor flows continue"),
        (("외국인",), "whether investor flows continue"),
        (("기관",), "whether investor flows continue"),
        (("코스피", "코스닥"), "index breadth and follow-through buying"),
        (("환율",), "currency sensitivity and foreign flow"),
        (("금리",), "rate expectations and valuation pressure"),
        (("수주", "계약"), "order backlog and revenue timing"),
        (("유상증자",), "dilution risk and funding use"),
        (("자사주", "소각"), "shareholder-return execution"),
        (("상장폐지", "거래정지"), "trading restrictions and disclosure follow-up"),
    )

    def __init__(
        self,
        *,
        enabled: bool = False,
        model_name: str = "Qwen3-0.6B-GGUF-Q4",
        max_tokens: int = 260,
        client: NewsSummaryClient | None = None,
    ) -> None:
        self._enabled = enabled
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._client = client

    @classmethod
    def from_settings(cls, settings: Settings) -> NewsSummaryGenerator:
        enabled = settings.news_summary_generation_mode == "local_llm"
        client: NewsSummaryClient | None = None
        if enabled:
            if settings.news_summary_llm_endpoint:
                client = OpenAiCompatibleNewsSummaryClient(
                    endpoint=settings.news_summary_llm_endpoint,
                    model=settings.news_summary_llm_model,
                    timeout_seconds=settings.news_summary_llm_timeout_seconds,
                )
            else:
                client = MlxQwenNewsSummaryClient(
                    model=settings.news_summary_mlx_model,
                    adapter_path=require_lora_adapter_artifact(
                        settings.news_summary_mlx_adapter_path,
                        "News summary Qwen3 LoRA adapter",
                    ),
                )
        return cls(
            enabled=enabled,
            model_name=(
                settings.news_summary_llm_model
                if settings.news_summary_llm_endpoint
                else settings.news_summary_mlx_model
            ),
            max_tokens=settings.news_summary_llm_max_tokens,
            client=client,
        )

    def generate(self, context: NewsSummaryContext) -> SummaryLines:
        if not self._enabled or self._client is None:
            return context.fallback
        if not self._has_usable_full_text(context.content):
            return self._english_fallback(context)

        try:
            raw_content = self._client.generate(
                self.messages(context),
                max_tokens=self._max_tokens,
            )
            candidate = self._parse_llm_output(raw_content)
            summary = SummaryLines(
                what=self._sanitize(candidate.get("what", "")),
                why=self._sanitize(candidate.get("why", "")),
                impact=self._sanitize(candidate.get("impact", "")),
            )
            if not self._is_quality_output(summary, context):
                return self._english_fallback(context)
            return summary
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError):
            return self._english_fallback(context)

    @classmethod
    def messages(cls, context: NewsSummaryContext) -> list[dict[str, str]]:
        payload = {
            "task": "Write three investor-facing analysis lines from the article body.",
            "schema": {
                "what": "one complete English sentence describing what happened",
                "why": "one complete English sentence explaining the article-backed reason",
                "impact": "one complete English sentence explaining the investor impact",
            },
            "rules": [
                "Return only compact JSON with keys what, why, impact.",
                "Use only evidence from article_text, title, snippet, event_tags, and labels.",
                "Write every value in English.",
                "Each value must be exactly one complete sentence.",
                "Do not use ellipses, bullet points, Korean sentences, or truncated fragments.",
                "Do not mention importance, sentiment, priority, or classification labels.",
                "Do not give buy, sell, price-target, or guaranteed-return advice.",
            ],
            "labels": {
                "source_type": context.source_type,
                "importance": context.importance,
                "sentiment": context.sentiment,
                "event_tags": context.event_tags,
            },
            "entity": {
                "stock_code": context.stock_code or "",
                "stock_name": context.stock_name or "",
                "stock_name_en": context.stock_name_en,
            },
            "title": context.title,
            "snippet": context.snippet,
            "article_text": cls._truncate_context(context.content),
        }
        return [
            {
                "role": "system",
                "content": (
                    "You are a Korean financial-news analyst for foreign retail investors. "
                    "You ground every sentence in the provided Korean article and output "
                    "strict JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            },
        ]

    @classmethod
    def training_example(
        cls,
        context: NewsSummaryContext,
        target: SummaryLines,
    ) -> dict[str, object]:
        return {
            "schema_version": "news-summary-wwi-sft/v1",
            "prompt_version": NEWS_SUMMARY_PROMPT_VERSION,
            "messages": [
                *cls.messages(context),
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "what": target.what,
                            "why": target.why,
                            "impact": target.impact,
                        },
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                },
            ],
            "target": {
                "what": target.what,
                "why": target.why,
                "impact": target.impact,
            },
        }

    @staticmethod
    def _parse_llm_output(raw_content: str) -> dict[str, str]:
        cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("LLM response does not contain a JSON object")
        parsed = json.loads(match.group(0))
        if not isinstance(parsed, dict):
            raise ValueError("LLM JSON response must be an object")
        return {
            key: value
            for key, value in parsed.items()
            if key in {"what", "why", "impact"} and isinstance(value, str)
        }

    @classmethod
    def _sanitize(cls, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = normalized.strip("`'\" ")
        return normalized

    @classmethod
    def _is_quality_output(cls, summary: SummaryLines, context: NewsSummaryContext) -> bool:
        lines = [summary.what, summary.why, summary.impact]
        if any(not cls._is_valid_sentence(line) for line in lines):
            return False
        normalized_lines = {line.lower() for line in lines}
        if len(normalized_lines) != 3:
            return False
        combined = " ".join(lines)
        lower_combined = combined.lower()
        if any(term in lower_combined for term in cls._META_TERMS):
            return False
        if any(term in lower_combined for term in cls._ADVICE_TERMS):
            return False
        if re.search(r"[가-힣]", combined):
            return False
        if not cls._mentions_relevant_subject(combined, context):
            return False
        return cls._has_grounded_financial_terms(combined, context)

    @classmethod
    def _is_valid_sentence(cls, line: str) -> bool:
        if not line or "\n" in line:
            return False
        if len(line) > 320:
            return False
        if "..." in line or "…" in line:
            return False
        if line.startswith(("-", "*", "•")):
            return False
        if not re.search(r"[.!?]$", line):
            return False
        chunks = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
        if len([chunk for chunk in chunks if chunk.strip()]) != 1:
            return False
        return len(re.findall(r"[A-Za-z0-9%$]+", line)) >= 7

    @classmethod
    def _mentions_relevant_subject(cls, combined: str, context: NewsSummaryContext) -> bool:
        lower = combined.lower()
        if context.stock_name_en and context.stock_name_en.lower() in lower:
            return True
        if context.stock_code and context.stock_code in combined:
            return True
        title_context = f"{context.title} {context.snippet} {context.content}"
        market_terms = ("코스피", "코스닥", "증시", "시장", "환율", "금리")
        if any(term in title_context for term in market_terms):
            return any(
                term in lower
                for term in (
                    "kospi",
                    "kosdaq",
                    "korean market",
                    "stock market",
                    "market",
                    "exchange rate",
                    "interest rate",
                )
            )
        return "the company" in lower or "the issuer" in lower

    @classmethod
    def _has_grounded_financial_terms(cls, combined: str, context: NewsSummaryContext) -> bool:
        evidence = f"{context.title} {context.snippet} {context.content}"
        lower = combined.lower()
        matched = 0
        for korean_term, english_terms in cls._KOREAN_TO_ENGLISH_TERMS.items():
            if korean_term not in evidence:
                continue
            if any(english_term in lower for english_term in english_terms):
                matched += 1
        if matched >= 2:
            return True
        if matched == 1 and any(
            tag.lower().replace("_", " ") in lower for tag in context.event_tags
        ):
            return True
        if matched == 1 and len(context.content) >= 200:
            return True
        return False

    @staticmethod
    def _has_usable_full_text(content: str) -> bool:
        normalized = re.sub(r"\s+", " ", content).strip()
        if len(normalized) < 120:
            return False
        return "..." not in normalized and "…" not in normalized

    @staticmethod
    def _truncate_context(content: str) -> str:
        normalized = re.sub(r"\s+", " ", content).strip()
        if len(normalized) <= 6500:
            return normalized
        return normalized[:6500].rsplit(" ", 1)[0].strip()

    @classmethod
    def _english_fallback(cls, context: NewsSummaryContext) -> SummaryLines:
        evidence = " ".join((context.title, context.snippet, context.content))
        subject = cls._english_subject(context, evidence)
        topic = cls._first_fallback_phrase(
            evidence, cls._ENGLISH_FALLBACK_TOPICS, "the reported event"
        )
        drivers = cls._fallback_driver_phrase(evidence)
        watch_item = cls._first_fallback_phrase(
            evidence,
            cls._ENGLISH_FALLBACK_WATCH_ITEMS,
            "the next disclosure and market reaction",
        )
        return SummaryLines(
            what=f"{subject} drew attention in the article around {topic}.",
            why=f"The article links the move to {drivers}.",
            impact=f"Investors should track {watch_item} as the story develops.",
        )

    @classmethod
    def _english_subject(cls, context: NewsSummaryContext, evidence: str) -> str:
        if context.stock_name_en:
            return context.stock_name_en
        if context.stock_code:
            return context.stock_code
        if "코스피" in evidence and "코스닥" in evidence:
            return "KOSPI and KOSDAQ"
        if "코스피" in evidence:
            return "KOSPI"
        if "코스닥" in evidence:
            return "KOSDAQ"
        if context.source_type == "DISCLOSURE":
            return "The issuer"
        return "The article"

    @classmethod
    def _fallback_driver_phrase(cls, evidence: str) -> str:
        drivers = [
            phrase
            for required_terms, phrase in cls._ENGLISH_FALLBACK_DRIVERS
            if all(term in evidence for term in required_terms)
        ]
        if not drivers:
            return "the article-backed market context"
        return ", ".join(dict.fromkeys(drivers[:3]))

    @staticmethod
    def _first_fallback_phrase(
        evidence: str,
        candidates: tuple[tuple[tuple[str, ...], str], ...],
        fallback: str,
    ) -> str:
        for required_terms, phrase in candidates:
            if all(term in evidence for term in required_terms):
                return phrase
        return fallback
