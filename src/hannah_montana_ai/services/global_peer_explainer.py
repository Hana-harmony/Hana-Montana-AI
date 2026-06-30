from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import GlobalPeerMatch, GlobalPeerMatchRequest
from hannah_montana_ai.training.global_peer_trainer import KOREA_ANCHORS

EXPLANATION_PROMPT_VERSION = "global-peer-structured-rag-explainer-v6"
TEMPLATE_EXPLANATION_MODEL_VERSION = "grounded-template-structured-rag-v1"


@dataclass(frozen=True)
class GlobalPeerExplanation:
    headline: str
    summary: str
    source: str
    model_version: str
    prompt_version: str = EXPLANATION_PROMPT_VERSION


@dataclass(frozen=True)
class GlobalPeerExplanationContext:
    request: GlobalPeerMatchRequest
    primary_peer: GlobalPeerMatch
    confidence_level: str
    confidence_score: float


class PeerExplanationClient(Protocol):
    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        pass


class OpenAiCompatiblePeerExplanationClient:
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
            "temperature": 0.2,
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


class GlobalPeerExplanationGenerator:
    def __init__(
        self,
        *,
        enabled: bool = False,
        model_name: str = "Qwen3-0.6B-GGUF-Q4",
        max_tokens: int = 220,
        client: PeerExplanationClient | None = None,
    ) -> None:
        self._enabled = enabled
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._client = client

    @classmethod
    def from_settings(cls, settings: Settings) -> GlobalPeerExplanationGenerator:
        enabled = (
            settings.global_peer_explanation_mode == "local_llm"
            and bool(settings.global_peer_explanation_llm_endpoint)
        )
        client: PeerExplanationClient | None = None
        if enabled:
            client = OpenAiCompatiblePeerExplanationClient(
                endpoint=settings.global_peer_explanation_llm_endpoint,
                model=settings.global_peer_explanation_llm_model,
                timeout_seconds=settings.global_peer_explanation_llm_timeout_seconds,
            )
        return cls(
            enabled=enabled,
            model_name=settings.global_peer_explanation_llm_model,
            max_tokens=settings.global_peer_explanation_llm_max_tokens,
            client=client,
        )

    def generate(self, context: GlobalPeerExplanationContext) -> GlobalPeerExplanation:
        fallback = self.template(context)
        if not self._enabled or self._client is None:
            return fallback

        try:
            raw_content = self._client.generate(
                self._messages(context),
                max_tokens=self._max_tokens,
            )
            candidate = self._parse_llm_output(raw_content)
            headline = self._sanitize(candidate.get("headline", ""), max_length=300)
            summary = self._sanitize(candidate.get("summary", ""), max_length=1200)
            if not self._is_grounded(headline, summary, context) or not self._is_quality_output(
                headline=headline,
                summary=summary,
                expected=fallback,
                context=context,
            ):
                return fallback
            return GlobalPeerExplanation(
                headline=headline,
                summary=summary,
                source="LOCAL_OPEN_SOURCE_LLM_GROUNDED_RAG",
                model_version=f"local-llm:{self._model_name}",
            )
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError):
            return fallback

    def template(self, context: GlobalPeerExplanationContext) -> GlobalPeerExplanation:
        request = context.request
        peer = context.primary_peer
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and anchor.headline_template and anchor.summary:
            stock_name_en = self._stock_display_name(request)
            return GlobalPeerExplanation(
                headline=anchor.headline_template.format(
                    stock_name_en=stock_name_en,
                    peer_name=peer.company_name,
                ),
                summary=anchor.summary,
                source="GROUNDED_TEMPLATE_STRUCTURED_RAG",
                model_version=TEMPLATE_EXPLANATION_MODEL_VERSION,
            )
        stock_name = self._stock_display_name(request)
        peer_name = self._display_peer_name(peer.company_name)
        business_label = self._business_label(peer)
        headline = (
            f"{stock_name} Is South Korea's '{peer_name}' — "
            f"{self._article_for(business_label)} {business_label}"
        )
        summary = (
            f"{stock_name} is best understood as a Korean {business_label.lower()} with a "
            f"similar role to {peer_name}. {self._domain_sentence(peer)} "
            f"{self._financial_sentence(peer)} "
            f"Hannah's global peer ranker assigns {context.confidence_level.lower()} "
            f"confidence with a similarity score of {context.confidence_score:.4f}."
        )
        return GlobalPeerExplanation(
            headline=headline,
            summary=summary,
            source="GROUNDED_TEMPLATE_STRUCTURED_RAG",
            model_version=TEMPLATE_EXPLANATION_MODEL_VERSION,
        )

    def training_example(self, context: GlobalPeerExplanationContext) -> dict[str, object]:
        template = self.template(context)
        messages = self._messages(context)
        return {
            "schema_version": "global-peer-explanation-sft/v1",
            "prompt_version": EXPLANATION_PROMPT_VERSION,
            "messages": [
                *messages,
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "headline": template.headline,
                            "summary": template.summary,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "target": {
                "headline": template.headline,
                "summary": template.summary,
            },
        }

    def _messages(self, context: GlobalPeerExplanationContext) -> list[dict[str, str]]:
        facts = self._grounding_facts(context)
        return [
            {
                "role": "system",
                "content": (
                    "Return a JSON object with exactly two keys: headline and summary. "
                    "Use only the provided facts. Do not invent products, partnerships, "
                    "financial figures, tickers, recommendations, or names. The headline "
                    "value must equal writing_contract.canonical_title_text. The summary "
                    "value must equal writing_contract.canonical_summary_text. Copy "
                    "writing_contract.use_company and writing_contract.use_peer exactly. "
                    "Every peer-company reference in the summary must use "
                    "writing_contract.use_peer exactly; never shorten, repeat, or partially "
                    "rename it. "
                    "Never output keys from writing_contract."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "task": "Write the final investor-friendly peer explanation JSON.",
                        "facts": facts,
                        "required_output_keys": ["headline", "summary"],
                        "style": {
                            "summary": "2 to 4 sentences, no investment advice",
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    @staticmethod
    def _grounding_facts(context: GlobalPeerExplanationContext) -> dict[str, object]:
        request = context.request
        peer = context.primary_peer
        display_name = GlobalPeerExplanationGenerator._stock_display_name(request)
        peer_display_name = GlobalPeerExplanationGenerator._display_peer_name(peer.company_name)
        business_label = GlobalPeerExplanationGenerator._business_label(peer)
        canonical_title_text = GlobalPeerExplanationGenerator._expected_headline(
            request=request,
            peer=peer,
            display_name=display_name,
            peer_display_name=peer_display_name,
            business_label=business_label,
        )
        canonical_summary_text = GlobalPeerExplanationGenerator.template(
            GlobalPeerExplanationGenerator(),
            context,
        ).summary
        return {
            "korean_stock": {
                "code": request.stock_code,
                "display_name": display_name,
                "market": request.market,
            },
            "primary_peer": {
                "ticker": peer.ticker,
                "display_name": peer_display_name,
                "exchange": peer.exchange,
                "sector": peer.sector,
                "industry": peer.industry,
                "business_model": peer.business_model,
                "scale_bucket": peer.scale_bucket,
                "market_cap_usd": peer.market_cap_usd,
                "revenue_usd": peer.revenue_usd,
                "operating_income_usd": peer.operating_income_usd,
                "financial_similarity_score": peer.financial_similarity_score,
            },
            "ranker": {
                "confidence_level": context.confidence_level,
                "confidence_score": context.confidence_score,
                "matched_factors": peer.matched_factors,
            },
            "writing_contract": {
                "use_company": display_name,
                "use_peer": peer_display_name,
                "use_business_label": business_label,
                "canonical_title_text": canonical_title_text,
                "canonical_summary_text": canonical_summary_text,
                "forbidden_display_names": [
                    value
                    for value in (request.stock_name, request.stock_name_en, peer.company_name)
                    if value and value not in {display_name, peer_display_name}
                ],
            },
        }

    @staticmethod
    def _parse_llm_output(raw_content: str) -> dict[str, str]:
        stripped = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        payload = json.loads(stripped)
        if not isinstance(payload, dict):
            raise ValueError("LLM output is not a JSON object")
        headline = payload.get("headline")
        summary = payload.get("summary")
        if not isinstance(headline, str) or not isinstance(summary, str):
            raise ValueError("LLM output misses headline or summary")
        return {"headline": headline, "summary": summary}

    @staticmethod
    def _sanitize(value: str, *, max_length: int) -> str:
        sanitized = re.sub(r"\s+", " ", value).strip()
        return sanitized[:max_length].strip()

    @staticmethod
    def _is_grounded(
        headline: str,
        summary: str,
        context: GlobalPeerExplanationContext,
    ) -> bool:
        if len(headline) < 20 or len(summary) < 80:
            return False
        combined = f"{headline} {summary}".lower()
        request = context.request
        peer = context.primary_peer
        stock_terms = [request.stock_name.lower()]
        if request.stock_name_en:
            stock_terms.append(request.stock_name_en.lower())
        display_name = GlobalPeerExplanationGenerator._stock_display_name(request).lower()
        if display_name:
            stock_terms.append(display_name)
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and anchor.display_name and anchor.display_name.lower() not in combined:
            return False
        if not any(term and term in combined for term in stock_terms):
            return False
        peer_terms = {peer.company_name.lower()}
        display_peer_name = GlobalPeerExplanationGenerator._display_peer_name(
            peer.company_name
        ).lower()
        if display_peer_name:
            peer_terms.add(display_peer_name)
        first_peer_word = re.split(r"[\s.,]+", peer.company_name.strip())[0].lower()
        if len(first_peer_word) >= 4:
            peer_terms.add(first_peer_word)
        if not any(term and term in combined for term in peer_terms):
            return False
        allowed_tokens = {
            request.stock_code.lower(),
            request.stock_name.lower(),
            request.stock_name_en.lower(),
            peer.ticker.lower(),
            peer.sector.lower(),
            peer.industry.lower(),
            peer.business_model.lower(),
            peer.scale_bucket.lower(),
            GlobalPeerExplanationGenerator._display_peer_name(peer.company_name).lower(),
            "us",
        }
        display_tokens = re.findall(
            r"[0-9a-z]+",
            GlobalPeerExplanationGenerator._stock_display_name(request).lower(),
        )
        peer_display_tokens = re.findall(
            r"[0-9a-z]+",
            GlobalPeerExplanationGenerator._display_peer_name(peer.company_name).lower(),
        )
        allowed_tokens.update(token for token in [*display_tokens, *peer_display_tokens] if token)
        uppercase_tokens = set(re.findall(r"\b[A-Z]{2,6}\b", f"{headline} {summary}"))
        for token in uppercase_tokens:
            normalized = token.lower()
            if normalized not in allowed_tokens and normalized != "korea":
                return False
        banned_phrases = {
            "buy rating",
            "sell rating",
            "price target",
            "guaranteed",
            "will outperform",
            "undervalued",
        }
        return not any(phrase in combined for phrase in banned_phrases)

    @staticmethod
    def _is_quality_output(
        *,
        headline: str,
        summary: str,
        expected: GlobalPeerExplanation,
        context: GlobalPeerExplanationContext,
    ) -> bool:
        if headline != expected.headline:
            return False
        if GlobalPeerExplanationGenerator._has_repeated_adjacent_word(summary):
            return False
        if summary != expected.summary:
            return False
        peer_display_name = GlobalPeerExplanationGenerator._display_peer_name(
            context.primary_peer.company_name
        )
        expected_peer_mentions = GlobalPeerExplanationGenerator._phrase_count(
            expected.summary,
            peer_display_name,
        )
        actual_peer_mentions = GlobalPeerExplanationGenerator._phrase_count(
            summary,
            peer_display_name,
        )
        return actual_peer_mentions >= expected_peer_mentions

    @staticmethod
    def _has_repeated_adjacent_word(value: str) -> bool:
        words = re.findall(r"\b[A-Za-z][A-Za-z0-9'-]*\b", value.lower())
        return any(
            left == right and len(left) > 2
            for left, right in zip(words, words[1:], strict=False)
        )

    @staticmethod
    def _phrase_count(text: str, phrase: str) -> int:
        if not phrase:
            return 0
        return len(re.findall(re.escape(phrase.lower()), text.lower()))

    @staticmethod
    def _business_label(peer: GlobalPeerMatch) -> str:
        if peer.industry and peer.industry not in {"Unclassified", "Listed Operating Company"}:
            return f"{GlobalPeerExplanationGenerator._short_industry_label(peer.industry)} Peer"
        if peer.business_model and peer.business_model != "Operating company":
            business_model = GlobalPeerExplanationGenerator._short_business_model(
                peer.business_model
            )
            return f"{business_model} Peer"
        if peer.business_tags:
            return peer.business_tags[0].title()
        return "Global Peer"

    @staticmethod
    def _stock_display_name(request: GlobalPeerMatchRequest) -> str:
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and anchor.display_name:
            return anchor.display_name
        return request.stock_name_en or request.stock_name

    @staticmethod
    def _display_peer_name(company_name: str) -> str:
        cleaned = re.sub(r"\s+\.\s+", " ", company_name).strip()
        cleaned = re.sub(r"\s+,", "", cleaned).strip()
        cleaned = re.sub(r"\s+Class\s+[A-Z]$", "", cleaned).strip()
        cleaned = re.sub(r"\s+When-Issued$", "", cleaned).strip()
        return cleaned.rstrip(" ,")

    @staticmethod
    def _domain_sentence(peer: GlobalPeerMatch) -> str:
        sector = peer.sector if peer.sector != "Unclassified" else "its sector"
        industry = peer.industry if peer.industry != "Unclassified" else "its industry"
        business_model = GlobalPeerExplanationGenerator._short_business_model(peer.business_model)
        if peer.industry not in {"Unclassified", "Listed Operating Company"}:
            return (
                f"The match is driven first by sector and industry fit: both companies sit "
                f"in {sector} and operate around {industry.lower()}."
            )
        if peer.business_model != "Operating company":
            return (
                f"The match is driven first by business-model fit: both companies are "
                f"mapped to {business_model.lower()}."
            )
        return (
            "The match is mainly a broad listed-company reference because detailed "
            "industry data is limited."
        )

    @staticmethod
    def _financial_sentence(peer: GlobalPeerMatch) -> str:
        peer_name = GlobalPeerExplanationGenerator._display_peer_name(peer.company_name)
        if peer.financial_similarity_score is None:
            return (
                f"Financial context is limited, so {peer_name} is used primarily "
                "as a business-domain proxy."
            )
        scale = peer.scale_bucket.replace("_", " ").lower()
        return (
            f"Financial context is included with a similarity score of "
            f"{peer.financial_similarity_score:.4f}; {peer_name} is treated as a "
            f"{scale} US-market reference rather than a strict size match."
        )

    @staticmethod
    def _short_business_model(value: str) -> str:
        normalized = value.strip()
        replacements = {
            "Banking, spread income, fees, and capital-market services": "Banking",
            "Platform software, search advertising, and commerce": "Digital Platform",
            "Biotech platform licensing": "Biotech Platform",
            "Automobile manufacturing and mobility supply chain": "Automotive Manufacturing",
            "Packaged food, beverage, and consumer staples": "Food and Beverage",
            "Insurance underwriting and financial services": "Insurance",
            "Chemical and advanced materials manufacturing": "Specialty Chemicals",
            "Investment holding and portfolio management": "Investment Holding",
        }
        return replacements.get(normalized, GlobalPeerExplanationGenerator._title_label(normalized))

    @staticmethod
    def _short_industry_label(value: str) -> str:
        normalized = value.strip()
        replacements = {
            "Banks": "Banking",
            "Automobiles": "Automotive",
            "Investment Holding Companies": "Investment Holding",
            "Food and Beverage": "Food and Beverage",
        }
        return replacements.get(normalized, GlobalPeerExplanationGenerator._title_label(normalized))

    @staticmethod
    def _article_for(value: str) -> str:
        first = value.strip()[:1].lower()
        return "An" if first in {"a", "e", "i", "o", "u"} else "A"

    @staticmethod
    def _canonical_title_text(
        *,
        display_name: str,
        peer_display_name: str,
        business_label: str,
    ) -> str:
        return (
            f"{display_name} Is South Korea's '{peer_display_name}' — "
            f"{GlobalPeerExplanationGenerator._article_for(business_label)} {business_label}"
        )

    @staticmethod
    def _expected_headline(
        *,
        request: GlobalPeerMatchRequest,
        peer: GlobalPeerMatch,
        display_name: str,
        peer_display_name: str,
        business_label: str,
    ) -> str:
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and anchor.headline_template and anchor.summary:
            return anchor.headline_template.format(
                stock_name_en=display_name,
                peer_name=peer_display_name,
            )
        return GlobalPeerExplanationGenerator._canonical_title_text(
            display_name=display_name,
            peer_display_name=peer_display_name,
            business_label=business_label,
        )

    @staticmethod
    def _title_label(value: str) -> str:
        minor_words = {"and", "or", "of", "for", "to", "in"}
        words = re.split(r"\s+", value.replace("_", " ").strip())
        titled = [
            word.lower() if index > 0 and word.lower() in minor_words else word.capitalize()
            for index, word in enumerate(words)
            if word
        ]
        return " ".join(titled)
