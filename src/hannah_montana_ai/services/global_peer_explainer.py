from __future__ import annotations

import re
from dataclasses import dataclass

from hannah_montana_ai.domain.schemas import GlobalPeerMatch, GlobalPeerMatchRequest

EXPLANATION_PROMPT_VERSION = "global-peer-structured-rag-explainer-v8"
TEMPLATE_EXPLANATION_MODEL_VERSION = "grounded-template-structured-rag-v3"
KOREA_ENGLISH_DISPLAY_NAMES = {
    "000270": "Kia",
    "000660": "SK hynix",
    "003550": "LG Corp.",
    "005380": "Hyundai Motor",
    "005930": "Samsung Electronics",
    "006400": "Samsung SDI",
    "010130": "Korea Zinc",
    "012330": "Hyundai Mobis",
    "015760": "Korea Electric Power",
    "017670": "SK Telecom",
    "018260": "Samsung SDS",
    "028260": "Samsung C&T",
    "032640": "LG Uplus",
    "033780": "KT&G",
    "035420": "NAVER",
    "035720": "Kakao",
    "051910": "LG Chem",
    "055550": "Shinhan Financial Group",
    "066570": "LG Electronics",
    "068270": "Celltrion",
    "086520": "EcoPro",
    "086790": "Hana Financial Group",
    "090430": "Amorepacific",
    "096770": "SK Innovation",
    "105560": "KB Financial Group",
    "196170": "Alteogen",
    "207940": "Samsung Biologics",
    "247540": "EcoPro BM",
    "251270": "Netmarble",
    "352820": "HYBE",
    "373220": "LG Energy Solution",
}


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


class GlobalPeerExplanationGenerator:
    def generate(self, context: GlobalPeerExplanationContext) -> GlobalPeerExplanation:
        return self.template(context)

    def template(self, context: GlobalPeerExplanationContext) -> GlobalPeerExplanation:
        request = context.request
        peer = context.primary_peer
        stock_name = self._stock_display_name(request)
        peer_name = self._display_peer_name(peer.company_name)
        business_label = self._business_label(peer)
        business_phrase = self._summary_business_phrase(business_label)
        headline = (
            f"{stock_name} Maps Closest To '{peer_name}' — "
            f"{self._article_for(business_label)} {business_label}"
        )
        summary = (
            f"{stock_name} is matched with {peer_name} as the closest US-listed reference "
            f"peer for this Korean {business_phrase}. {self._domain_sentence(peer)} "
            f"{self._financial_sentence(peer)}"
        )
        return GlobalPeerExplanation(
            headline=headline,
            summary=summary,
            source="GROUNDED_TEMPLATE_STRUCTURED_RAG",
            model_version=TEMPLATE_EXPLANATION_MODEL_VERSION,
        )
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
    def _summary_business_phrase(business_label: str) -> str:
        normalized = re.sub(r"\s+Peer$", "", business_label).strip()
        replacements = {
            "Semiconductors": "semiconductor business",
            "Internet Platforms": "internet-platform business",
            "Automotive": "automotive business",
            "Telecommunications": "telecommunications business",
            "Software": "software business",
        }
        phrase = replacements.get(normalized, normalized.lower())
        return phrase or "listed company"

    @staticmethod
    def _stock_display_name(request: GlobalPeerMatchRequest) -> str:
        curated_name = KOREA_ENGLISH_DISPLAY_NAMES.get(request.stock_code)
        if curated_name:
            return curated_name
        if request.stock_name_en and not GlobalPeerExplanationGenerator._contains_hangul(
            request.stock_name_en
        ):
            return request.stock_name_en
        if request.stock_name and not GlobalPeerExplanationGenerator._contains_hangul(
            request.stock_name
        ):
            return request.stock_name
        return request.stock_name or f"Korean stock {request.stock_code}"

    @staticmethod
    def _contains_hangul(value: str) -> bool:
        return bool(re.search(r"[가-힣]", value))

    @staticmethod
    def _display_peer_name(company_name: str) -> str:
        cleaned = re.sub(r"\s+\.\s+", " ", company_name).strip()
        cleaned = re.sub(r"\s+,", "", cleaned).strip()
        cleaned = re.sub(r"\s+Class\s+[A-Z]$", "", cleaned).strip()
        cleaned = re.sub(r"\s+When-Issued$", "", cleaned).strip()
        return cleaned.rstrip(" ,")

    @staticmethod
    def _domain_sentence(peer: GlobalPeerMatch) -> str:
        peer_name = GlobalPeerExplanationGenerator._display_peer_name(peer.company_name)
        sector = peer.sector if peer.sector != "Unclassified" else "its sector"
        industry = peer.industry if peer.industry != "Unclassified" else "its industry"
        business_model = GlobalPeerExplanationGenerator._short_business_model(peer.business_model)
        if peer.industry not in {"Unclassified", "Listed Operating Company"}:
            return (
                f"{peer_name} provides a {industry.lower()} reference within {sector}, "
                "which is the primary domain signal used for this match."
            )
        if peer.business_model != "Operating company":
            return (
                f"{peer_name} provides the closest mapped business-model reference in "
                f"{business_model.lower()}."
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
        scale = peer.scale_bucket.replace("_", "-").lower()
        return (
            f"Scale and financial data are used as secondary context: {peer_name} is treated "
            f"as a {scale} US-market reference, not as a one-for-one size match."
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
    def _title_label(value: str) -> str:
        minor_words = {"and", "or", "of", "for", "to", "in"}
        words = re.split(r"\s+", value.replace("_", " ").strip())
        titled = [
            word.lower() if index > 0 and word.lower() in minor_words else word.capitalize()
            for index, word in enumerate(words)
            if word
        ]
        return " ".join(titled)
