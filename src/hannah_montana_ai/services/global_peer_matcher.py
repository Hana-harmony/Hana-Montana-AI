from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal, cast

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from hannah_montana_ai.domain.schemas import (
    GlobalPeerComparison,
    GlobalPeerComparisonDimension,
    GlobalPeerKeyStrength,
    GlobalPeerMatch,
    GlobalPeerMatchRequest,
    GlobalPeerMatchResponse,
    GlobalPeerStrengthIconKey,
)
from hannah_montana_ai.services.global_peer_explainer import (
    GlobalPeerExplanationContext,
    GlobalPeerExplanationGenerator,
)
from hannah_montana_ai.services.model import (
    ModelArtifactInvalidError,
    ModelArtifactNotFoundError,
)
from hannah_montana_ai.training.global_peer_trainer import (
    CURATED_GLOBAL_BRAND_TIERS,
    GENERIC_LISTED_INDUSTRY,
    GENERIC_LISTED_SECTOR,
    GLOBAL_PEER_SCHEMA_VERSION,
    KOREA_ANCHORS,
    PAIRWISE_FEATURE_NAMES,
    build_korea_profile,
    has_financial_signal,
    infer_business_model,
    infer_business_tags,
    infer_industry,
    infer_sector,
    normalize_profile_text,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry

ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]
PAIRWISE_CANDIDATE_POOL_SIZE = 512
COMPARISON_LIMIT = 3
StrengthSignal = tuple[
    str,
    str,
    GlobalPeerStrengthIconKey,
    tuple[str, ...],
]
STRENGTH_SIGNALS: tuple[StrengthSignal, ...] = (
    (
        "Memory Technology",
        "Its disclosed portfolio includes DRAM, NAND, HBM, or next-generation memory products.",
        "memory",
        ("dram", "nand", "hbm", "memory", "메모리"),
    ),
    (
        "Foundry Capability",
        "The company discloses foundry or advanced semiconductor manufacturing capabilities.",
        "foundry",
        ("foundry", "파운드리", "선단 공정", "선단공정"),
    ),
    (
        "AI Technology",
        "AI products, infrastructure, or AI-led technology development are stated priorities.",
        "ai",
        ("artificial intelligence", " ai ", "ai ", " ai", "인공지능"),
    ),
    (
        "Consumer Devices",
        "Its disclosed product portfolio spans consumer devices, electronics, or appliances.",
        "consumer_electronics",
        ("스마트폰", "가전", "tv", "consumer device", "전자 제품"),
    ),
    (
        "Battery Technology",
        "Battery cells, energy storage, or rechargeable-battery technology anchors the business.",
        "battery",
        ("이차전지", "2차전지", "배터리", "battery", "energy storage"),
    ),
    (
        "Advanced Materials",
        "The disclosed portfolio includes advanced materials or critical production inputs.",
        "materials",
        ("양극소재", "양극활물질", "nca", "ncm", "첨단소재", "신소재"),
    ),
    (
        "Vehicle Manufacturing",
        "Vehicle manufacturing and new-model execution are identified as core operations.",
        "automotive",
        ("자동차 제조", "자동차제조", "차량부문", "automobile manufacturing"),
    ),
    (
        "Mobility Portfolio",
        "Mobility services, vehicle technology, or transportation solutions broaden its reach.",
        "automotive",
        ("모빌리티", "mobility", "전기차", " ev ", "전동화"),
    ),
    (
        "Banking Network",
        "Banking operations and a domestic or global branch network underpin the franchise.",
        "financial_services",
        ("은행업", "은행", "banking", "금융지주"),
    ),
    (
        "Capital Markets",
        "Securities, investment, trust, or asset-management operations diversify earnings.",
        "financial_services",
        (
            "금융투자",
            "증권업",
            "증권 사업",
            "증권사",
            "하나증권",
            "자산운용",
            "자산신탁",
            "capital-market",
        ),
    ),
    (
        "Payments and Cards",
        "Payments, cards, or consumer-finance services extend the customer ecosystem.",
        "payments",
        ("신용카드", "카드업", "결제", "payments", "할부금융", "페이"),
    ),
    (
        "Insurance Services",
        "Life or non-life insurance operations add recurring financial-service exposure.",
        "financial_services",
        ("생명보험", "손해보험", "보험업", "insurance"),
    ),
    (
        "Digital Platform",
        "A software, messaging, portal, or cloud platform forms a core customer channel.",
        "software_platform",
        (
            "플랫폼 부문",
            "플랫폼 사업",
            "소프트웨어 플랫폼",
            "온라인 플랫폼",
            "디지털 플랫폼",
            "메신저",
            "포털",
            "software platform",
            "cloud",
        ),
    ),
    (
        "Commerce Ecosystem",
        "Commerce, merchant, advertising, or marketplace services expand monetization.",
        "commerce",
        ("커머스", "톡비즈", "광고", "marketplace", "merchant", "commerce"),
    ),
    (
        "Content Portfolio",
        "Music, story, media, gaming, or entertainment content diversifies the platform.",
        "media",
        ("콘텐츠", "뮤직", "스토리", "게임", "엔터테인먼트", "media content"),
    ),
    (
        "Biotechnology Platform",
        "Biotechnology, biologics, or pharmaceutical capabilities support the growth pipeline.",
        "biotechnology",
        ("바이오", "의약품", "신약", "biotech", "biologics", "pharma"),
    ),
    (
        "Drug-Delivery Technology",
        "Drug-delivery, formulation, or licensing technology is a disclosed platform strength.",
        "drug_delivery",
        ("약물전달", "피하주사", "제형", "drug delivery", "subcutaneous", "licensing"),
    ),
    (
        "Telecom Network",
        "Telecommunications and network infrastructure provide recurring service reach.",
        "telecommunications",
        ("통신", "5g", "무선", "telecom", "network infrastructure"),
    ),
    (
        "Energy Infrastructure",
        "Power, generation, renewable-energy, or energy infrastructure anchors operations.",
        "energy",
        ("발전", "전력", "신재생", "에너지", "power generation", "renewable"),
    ),
    (
        "Industrial Solutions",
        "Manufacturing, machinery, defense, rail, or plant capabilities support industrial demand.",
        "industrial",
        ("제조", "기계", "디펜스", "레일", "플랜트", "industrial"),
    ),
    (
        "Product Portfolio",
        "Portfolio expansion or business diversification broadens the addressable market.",
        "ecosystem",
        ("제품 포트폴리오", "포트폴리오 다각화", "사업 다각화", "다각화된"),
    ),
    (
        "Biomanufacturing Scale",
        "CDMO, contract manufacturing, or disclosed production capacity supports global supply.",
        "biotechnology",
        ("cdmo", "위탁생산", "생산능력", "cmo", "공정 개발"),
    ),
    (
        "Aviation Network",
        "Domestic and international routes provide a scaled passenger-transport network.",
        "global_business",
        ("항공운송", "항공 여객", "국제항공", "취항", "노선개설"),
    ),
    (
        "Passenger and Cargo",
        "Passenger and cargo services diversify aviation revenue and network utilization.",
        "commerce",
        ("여객·화물", "여객 및 화물", "여객운송", "화물 운송", "화물사업"),
    ),
    (
        "Fleet Operations",
        "A disclosed aircraft fleet and operating model support route capacity and efficiency.",
        "industrial",
        ("항공기", "여객기", "기대", "lcc", "안전 운항"),
    ),
    (
        "Aerospace Capability",
        "Aerospace, aircraft maintenance, drones, or defense programs extend technical depth.",
        "industrial",
        ("항공우주", "군용기", "무인기", "드론", "mro", "항공기체"),
    ),
    (
        "Broadcast Network",
        "Broadcast channels, satellite, cable, or nationwide distribution provide audience reach.",
        "media",
        ("방송서비스", "위성방송", "유선방송", "방송채널", "방송사업자"),
    ),
    (
        "Digital Broadcasting",
        "HD, UHD, or digital broadcasting technology differentiates the viewing service.",
        "media",
        ("uhd", " hd ", "h.264", "디지털방송", "다채널"),
    ),
    (
        "Wireless Connectivity",
        "Mobile, wireless-data, or 5G services anchor recurring connectivity demand.",
        "telecommunications",
        ("이동통신", "이동전화", "무선데이터", "5g 가입자", "무선통신"),
    ),
    (
        "Broadband and IPTV",
        "Broadband, IPTV, or fixed-line services diversify the communications portfolio.",
        "telecommunications",
        ("초고속인터넷", "iptv", "유선통신", "유선 통신", "브로드밴드"),
    ),
    (
        "Cloud Infrastructure",
        "Cloud, compute, storage, network, or GPU infrastructure supports enterprise workloads.",
        "software_platform",
        ("클라우드", "cpu", "gpu", "storage", "인프라 서비스", "ito"),
    ),
    (
        "IT Services",
        "System integration, managed IT, or enterprise services provide recurring demand.",
        "software_platform",
        ("it서비스", "it 서비스", " si ", "시스템 통합", "기업용 소프트웨어"),
    ),
    (
        "Logistics Network",
        "Logistics, distribution, or fulfillment capabilities support end-to-end delivery.",
        "industrial",
        ("물류", "지상조업", "배송", "풀필먼트", "logistics"),
    ),
    (
        "Electronic Components",
        "Electronic components, modules, substrates, or passive devices anchor the product mix.",
        "consumer_electronics",
        ("전자부품", "카메라모듈", "패키지기판", "수동소자", "광학솔루션"),
    ),
    (
        "Power Grid",
        "Generation, transmission, distribution, or electricity sales form "
        "essential infrastructure.",
        "energy",
        ("송전", "변전", "배전", "전기판매", "전력자원", "스마트그리드"),
    ),
    (
        "Energy Transition",
        "Hydrogen, ammonia, ESS, renewables, or carbon-neutral projects expand future options.",
        "energy",
        ("수소", "암모니아", "ess", "탄소중립", "수소경제", "원전 수출"),
    ),
    (
        "LNG Infrastructure",
        "LNG supply, pipelines, storage, or resource development supports "
        "national energy delivery.",
        "energy",
        ("천연가스", "lng", "배관망", "탱크로리", "자원개발", "벙커링"),
    ),
    (
        "Protection Products",
        "Life-stage protection products cover death, illness, disability, or accidents.",
        "financial_services",
        ("보장성 보험", "사망", "질병", "장애", "사고", "보험상품"),
    ),
    (
        "Retirement Solutions",
        "Pension, savings, or senior-living products address long-duration customer needs.",
        "financial_services",
        ("연금", "저축성", "노후대비", "시니어리빙", "생애 단계"),
    ),
    (
        "Subsidiary Portfolio",
        "A disclosed subsidiary portfolio broadens operating capabilities across adjacent markets.",
        "ecosystem",
        ("종속회사", "자회사", "연결대상 종속회사", "연결대상종속회사"),
    ),
    (
        "Market Leadership",
        "Disclosed market leadership, share, or competitive positioning supports brand strength.",
        "global_business",
        ("국내 1위", "시장을 선도", "시장 선도", "시장을 선도", "시장 경쟁력", "점유"),
    ),
    (
        "Production Expansion",
        "Capacity expansion, acquisitions, or new facilities support future production growth.",
        "operational_scale",
        ("생산능력을", "생산능력 ", "생산 능력", "증설", "사업을 확장", "사업 확장"),
    ),
    (
        "Advanced Modalities",
        "Next-generation modalities or process technologies extend the development pipeline.",
        "biotechnology",
        ("mrna", "adc", "세포주", "차세대 모달리티", "바이오시밀러"),
    ),
    (
        "Biosimilar Portfolio",
        "Approved biosimilars and direct commercialization broaden global product reach.",
        "biotechnology",
        ("바이오시밀러", "품목허가", "항체", "자가면역질환", "종양 치료"),
    ),
    (
        "Robotics Growth",
        "Robotics, actuators, or intelligent-home initiatives create adjacent growth options.",
        "industrial",
        ("로봇", "액추에이터", "ai홈", "양자컴퓨터"),
    ),
    (
        "Advertising Revenue",
        "Advertising, sponsorship, or retransmission provides monetization for media reach.",
        "media",
        ("방송광고", "협찬", "재송신", "광고 수익", "광고수익"),
    ),
    (
        "Content Production",
        "Content production, investment, distribution, or channel operations support the slate.",
        "media",
        ("콘텐트 제작", "영화 제작", "투자 배급", "채널운영", "프로그램"),
    ),
    (
        "Cinema Network",
        "Cinema sites and theatrical distribution provide direct consumer reach.",
        "media",
        ("멀티플렉스", "영화관", "메가박스", "흥행작"),
    ),
    (
        "Leisure Operations",
        "Leisure venues or experience-based businesses diversify the operating portfolio.",
        "commerce",
        ("레저", "골프장", "놀이터", "공연·행사", "문화사업"),
    ),
    (
        "Security Services",
        "Security monitoring or security software adds enterprise-service exposure.",
        "software_platform",
        ("보안관제", "보안소프트웨어", "security monitoring"),
    ),
    (
        "Low-Cost Operations",
        "A low-cost carrier model and efficiency program support competitive unit economics.",
        "operational_scale",
        ("저비용항공사", "lcc 운영", "저비용 구조", "연료 효율"),
    ),
    (
        "Sales Channels",
        "Direct, digital, and partner sales channels broaden customer acquisition.",
        "commerce",
        ("직접 판매", "간접 판매", "온라인 채널", "대리점 파트너십", "판매법인"),
    ),
    (
        "Regional Audience",
        "A defined regional footprint and network agreements support local audience reach.",
        "media",
        ("방송권역", "시청권역", "지역 민영방송", "네트워크 협정"),
    ),
    (
        "Petrochemical Portfolio",
        "Petrochemicals, industrial resins, or agricultural inputs diversify material demand.",
        "materials",
        ("석유화학", " pvc", " abs", "작물보호제", "종자", "비료 사업"),
    ),
    (
        "Multi-Division Operations",
        "Multiple disclosed business divisions provide a diversified operating base.",
        "ecosystem",
        ("사업부문으로", "사업부문을", "사업부문에서", "사업본부", "개 사업부문"),
    ),
    (
        "Global Reach",
        "The disclosed operating footprint includes global customers, exports, "
        "or overseas networks.",
        "global_business",
        ("글로벌", "전세계", "해외", "수출", "global network"),
    ),
    (
        "Technology Innovation",
        "Product innovation, advanced technology, or research and development "
        "supports differentiation.",
        "global_business",
        ("기술력", "기술 개발", "연구개발", "innovation", "r&d", "제품 차별화"),
    ),
)


class GlobalPeerMatcher:
    def __init__(
        self,
        model_path: Path,
        explainer: GlobalPeerExplanationGenerator | None = None,
    ) -> None:
        if not model_path.exists():
            raise ModelArtifactNotFoundError(f"Global peer model artifact not found: {model_path}")
        try:
            payload: dict[str, Any] = joblib.load(model_path)
        except Exception as exception:
            message = f"Global peer model artifact cannot be loaded: {model_path}"
            raise ModelArtifactInvalidError(message) from exception

        self._validate_payload(payload, model_path)
        self.version = str(payload["version"])
        self._vectorizer = payload["vectorizer"]
        self._eligible_us_matrix = payload["eligible_us_matrix"]
        self._semantic_reducer = payload["semantic_reducer"]
        self._eligible_us_semantic_matrix = np.array(payload["eligible_us_semantic_matrix"])
        self._eligible_us_financial_matrix = payload.get("eligible_us_financial_matrix")
        self._pairwise_ranker = payload["pairwise_ranker"]
        self._pairwise_feature_names = tuple(payload["pairwise_feature_names"])
        self._eligible_us_profiles = list(payload["eligible_us_profiles"])
        self._eligible_us_index_by_ticker = {
            str(profile.get("identifier") or ""): index
            for index, profile in enumerate(self._eligible_us_profiles)
        }
        self._us_market_cap_percentiles = self._market_cap_percentiles(self._eligible_us_profiles)
        self._korea_profiles = dict(payload["korea_profiles"])
        self._korea_profile_by_name = {
            str(profile.get("display_name") or "").strip(): profile
            for profile in self._korea_profiles.values()
            if str(profile.get("display_name") or "").strip()
        }
        self._explainer = explainer or GlobalPeerExplanationGenerator()

    def match(self, request: GlobalPeerMatchRequest) -> GlobalPeerMatchResponse:
        stock_profile = self._stock_profile(request)
        query_vector = self._vectorizer.transform([str(stock_profile["profile_text"])])
        text_similarities = cosine_similarity(query_vector, self._eligible_us_matrix)[0]
        semantic_similarities = self._semantic_similarities(query_vector)
        financial_similarities = self._financial_similarities(stock_profile)
        base_similarities = self._base_similarities(
            stock_profile,
            text_similarities,
            semantic_similarities,
            financial_similarities,
        )
        candidate_indices = self._candidate_indices(
            stock_profile=stock_profile,
            base_similarities=base_similarities,
            limit=max(PAIRWISE_CANDIDATE_POOL_SIZE, request.peer_count * 96),
        )
        similarities = self._combined_similarities(
            stock_profile,
            base_similarities,
            text_similarities,
            semantic_similarities,
            financial_similarities,
            candidate_indices,
        )
        ranked_indices = sorted(
            candidate_indices,
            key=lambda index: float(similarities[index]),
            reverse=True,
        )

        selected_indices = self._selected_indices(
            ranked_indices=[int(index) for index in ranked_indices],
            limit=max(1, request.peer_count),
        )
        peers = [
            self._to_peer_match(
                rank=rank,
                profile=self._eligible_us_profiles[index],
                score=float(similarities[index]),
                financial_score=financial_similarities[index],
                request=request,
                stock_profile=stock_profile,
            )
            for rank, index in enumerate(selected_indices, start=1)
        ]
        primary_peer = peers[0]
        comparisons = self._build_comparisons(
            request=request,
            stock_profile=stock_profile,
            ranked_indices=[int(index) for index in ranked_indices],
            similarities=similarities,
            financial_similarities=financial_similarities,
        )
        key_strengths = self._build_key_strengths(request, stock_profile)
        confidence_score = self._calibrated_confidence_score(
            stock_profile=stock_profile,
            primary_peer=primary_peer,
        )
        confidence_level = self._confidence_level(confidence_score)
        explanation = self._explainer.generate(
            GlobalPeerExplanationContext(
                request=request,
                primary_peer=primary_peer,
                confidence_level=confidence_level,
                confidence_score=confidence_score,
            )
        )
        return GlobalPeerMatchResponse(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            stock_name_en=GlobalPeerExplanationGenerator._stock_display_name(request),
            headline=explanation.headline,
            summary=explanation.summary,
            primary_peer=primary_peer,
            peers=peers,
            comparisons=comparisons,
            key_strengths=key_strengths,
            confidence_score=round(confidence_score, 4),
            confidence_level=confidence_level,
            model_version=self.version,
            source="HANNAH_GLOBAL_PEER_HYBRID_RANKER",
            explanation_source=explanation.source,
            explanation_model_version=explanation.model_version,
            explanation_prompt_version=explanation.prompt_version,
        )

    def _build_comparisons(
        self,
        *,
        request: GlobalPeerMatchRequest,
        stock_profile: dict[str, object],
        ranked_indices: list[int],
        similarities: np.ndarray,
        financial_similarities: np.ndarray,
    ) -> list[GlobalPeerComparison]:
        anchor = KOREA_ANCHORS.get(request.stock_code)
        comparisons: list[GlobalPeerComparison] = []
        selected_indices: list[int] = []

        if anchor and anchor.comparison_dimensions:
            for spec in anchor.comparison_dimensions[:COMPARISON_LIMIT]:
                index = self._eligible_us_index_by_ticker.get(spec.preferred_peer_ticker)
                if index is None or index in selected_indices:
                    continue
                selected_indices.append(index)
                comparisons.append(
                    GlobalPeerComparison(
                        dimension=cast(GlobalPeerComparisonDimension, spec.dimension),
                        description=spec.description,
                        peer=self._to_peer_match(
                            rank=len(comparisons) + 1,
                            profile=self._eligible_us_profiles[index],
                            score=float(similarities[index]),
                            financial_score=float(financial_similarities[index]),
                            request=request,
                            stock_profile=stock_profile,
                        ),
                    )
                )

        if len(comparisons) < COMPARISON_LIMIT:
            dimensions = self._general_comparison_dimensions(stock_profile)
            used_dimensions = {comparison.dimension for comparison in comparisons}
            for dimension in dimensions:
                if dimension in used_dimensions:
                    continue
                index = self._select_comparison_index(
                    dimension=dimension,
                    stock_profile=stock_profile,
                    ranked_indices=ranked_indices,
                    selected_indices=selected_indices,
                    similarities=similarities,
                )
                if index is None:
                    continue
                selected_indices.append(index)
                used_dimensions.add(dimension)
                peer = self._to_peer_match(
                    rank=len(comparisons) + 1,
                    profile=self._eligible_us_profiles[index],
                    score=float(similarities[index]),
                    financial_score=float(financial_similarities[index]),
                    request=request,
                    stock_profile=stock_profile,
                )
                comparisons.append(
                    GlobalPeerComparison(
                        dimension=dimension,
                        description=self._comparison_description(request, dimension, peer),
                        peer=peer,
                    )
                )
                if len(comparisons) == COMPARISON_LIMIT:
                    break
        return comparisons

    def _select_comparison_index(
        self,
        *,
        dimension: GlobalPeerComparisonDimension,
        stock_profile: dict[str, object],
        ranked_indices: list[int],
        selected_indices: list[int],
        similarities: np.ndarray,
    ) -> int | None:
        selected_families = {
            self._company_family(self._eligible_us_profiles[index])
            for index in selected_indices
        }
        candidate_indices = list(ranked_indices[:PAIRWISE_CANDIDATE_POOL_SIZE])
        for ticker in CURATED_GLOBAL_BRAND_TIERS:
            index = self._eligible_us_index_by_ticker.get(ticker)
            if index is not None and index not in candidate_indices:
                candidate_indices.append(index)
        for curated_only in (True, False):
            for strict in (True, False):
                best_index: int | None = None
                best_score = float("-inf")
                for index in candidate_indices:
                    if index in selected_indices:
                        continue
                    profile = self._eligible_us_profiles[index]
                    if self._company_family(profile) in selected_families:
                        continue
                    ticker = str(profile.get("identifier") or "")
                    brand_tier = CURATED_GLOBAL_BRAND_TIERS.get(ticker, 0.0)
                    if curated_only and brand_tier <= 0.0:
                        continue
                    dimension_fit = (
                        self._overall_business_fit(stock_profile, profile)
                        if dimension == "overall_business"
                        else self._dimension_fit(dimension, profile)
                    )
                    if strict and not self._comparison_domain_compatible(
                        stock_profile,
                        profile,
                        dimension,
                        dimension_fit,
                    ):
                        continue
                    if not strict and dimension != "overall_business" and dimension_fit < 0.5:
                        continue
                    familiarity = self._score(profile.get("familiarity_score"))
                    completeness = self._score(profile.get("profile_completeness_score"))
                    reliability = self._score(profile.get("market_cap_reliability_score"))
                    redundancy = max(
                        (
                            self._profile_redundancy(
                                profile,
                                self._eligible_us_profiles[selected],
                            )
                            for selected in selected_indices
                        ),
                        default=0.0,
                    )
                    score = (
                        float(similarities[index])
                        + (0.18 * dimension_fit)
                        + (0.12 * familiarity)
                        + (0.30 * brand_tier)
                        + (0.06 * completeness)
                        + (0.02 * reliability)
                        - (0.16 * redundancy)
                    )
                    if score > best_score:
                        best_index = index
                        best_score = score
                if best_index is not None:
                    return best_index
        return None

    @staticmethod
    def _overall_business_fit(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
    ) -> float:
        business_dimension = GlobalPeerMatcher._dimension_for(
            str(stock_profile.get("business_model") or "")
        )
        if business_dimension != "operational_scale":
            return GlobalPeerMatcher._dimension_fit(business_dimension, peer_profile)
        dimensions = [
            GlobalPeerMatcher._dimension_for_icon(signal[2])
            for _, _, signal in GlobalPeerMatcher._profile_strength_signals(stock_profile)[:2]
        ]
        domain_dimensions = [
            dimension
            for dimension in dimensions
            if dimension not in {"overall_business", "operational_scale"}
        ]
        if not domain_dimensions:
            return GlobalPeerMatcher._dimension_fit("overall_business", peer_profile)
        return max(
            GlobalPeerMatcher._dimension_fit(dimension, peer_profile)
            for dimension in domain_dimensions
        )

    @staticmethod
    def _comparison_domain_compatible(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
        dimension: GlobalPeerComparisonDimension,
        dimension_fit: float,
    ) -> bool:
        generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
        generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        if (
            stock_sector not in generic_sectors
            and peer_sector not in generic_sectors
            and stock_sector != peer_sector
        ):
            if dimension != "overall_business" or not stock_profile.get("business_summary"):
                return False
        if dimension in {"overall_business", "operational_scale"}:
            if dimension == "overall_business" and stock_profile.get("business_summary"):
                return dimension_fit >= 0.5
            return stock_industry in generic_industries or peer_industry == stock_industry
        return dimension_fit >= 0.5

    @staticmethod
    def _company_family(profile: dict[str, object]) -> str:
        normalized = normalize_profile_text(str(profile.get("display_name") or ""))
        tokens = normalized.split()
        if "class" in tokens:
            tokens = tokens[: tokens.index("class")]
        ignored_tokens = {"class", "a", "b", "c", "common", "stock"}
        return " ".join(token for token in tokens if token not in ignored_tokens)

    @staticmethod
    def _general_comparison_dimensions(
        stock_profile: dict[str, object],
    ) -> list[GlobalPeerComparisonDimension]:
        dimensions: list[GlobalPeerComparisonDimension] = ["overall_business"]
        for _, _, (_, _, icon_key, _) in GlobalPeerMatcher._profile_strength_signals(
            stock_profile
        ):
            dimension = GlobalPeerMatcher._dimension_for_icon(icon_key)
            if dimension not in dimensions:
                dimensions.append(dimension)
        if len(dimensions) == 1:
            dimension = GlobalPeerMatcher._dimension_for(
                str(stock_profile.get("industry") or "")
            )
            if dimension not in dimensions:
                dimensions.append(dimension)
        if "operational_scale" not in dimensions:
            dimensions.append("operational_scale")
        return dimensions

    @staticmethod
    def _dimension_for_icon(
        icon_key: GlobalPeerStrengthIconKey,
    ) -> GlobalPeerComparisonDimension:
        mappings: dict[GlobalPeerStrengthIconKey, GlobalPeerComparisonDimension] = {
            "memory": "memory",
            "foundry": "foundry",
            "ai": "semiconductor",
            "ecosystem": "overall_business",
            "semiconductor": "semiconductor",
            "consumer_electronics": "consumer_electronics",
            "software_platform": "software_platform",
            "financial_services": "financial_services",
            "payments": "payments",
            "biotechnology": "biotechnology",
            "drug_delivery": "drug_delivery",
            "battery": "battery",
            "automotive": "automotive",
            "telecommunications": "telecommunications",
            "energy": "energy",
            "materials": "materials",
            "industrial": "industrial",
            "commerce": "commerce",
            "media": "media",
            "global_business": "operational_scale",
            "operational_scale": "operational_scale",
        }
        return mappings[icon_key]

    @staticmethod
    def _dimension_for(value: str) -> GlobalPeerComparisonDimension:
        normalized = value.lower()
        mappings: tuple[tuple[tuple[str, ...], GlobalPeerComparisonDimension], ...] = (
            (("memory", "dram", "nand", "hbm"), "memory"),
            (("foundry", "fab"), "foundry"),
            (("semiconductor", "chip"), "semiconductor"),
            (("consumer electronics", "appliance"), "consumer_electronics"),
            (("payment",), "payments"),
            (("bank", "financial", "insurance", "holding"), "financial_services"),
            (("drug delivery",), "drug_delivery"),
            (("bio", "pharma", "health"), "biotechnology"),
            (("software", "platform", "internet", "cloud"), "software_platform"),
            (("battery",), "battery"),
            (("auto", "vehicle", "mobility"), "automotive"),
            (("telecom", "communication"), "telecommunications"),
            (("energy", "power", "oil", "gas"), "energy"),
            (("material", "chemical", "steel", "metal"), "materials"),
            (("industrial", "machinery", "construction", "engineering"), "industrial"),
            (("retail", "commerce", "food", "consumer brand"), "commerce"),
            (("media", "gaming", "entertainment", "content", "advertising"), "media"),
        )
        return next(
            (
                dimension
                for keywords, dimension in mappings
                if any(keyword in normalized for keyword in keywords)
            ),
            "operational_scale",
        )

    @staticmethod
    def _dimension_fit(
        dimension: GlobalPeerComparisonDimension,
        profile: dict[str, object],
    ) -> float:
        if dimension == "overall_business":
            return GlobalPeerMatcher._score(profile.get("profile_completeness_score"))
        raw_tags = profile.get("business_tags", [])
        tags = raw_tags if isinstance(raw_tags, list) else []
        searchable = " ".join(
            [
                str(profile.get("profile_text") or ""),
                " ".join(str(tag) for tag in tags),
                str(profile.get("industry") or ""),
                str(profile.get("business_model") or ""),
            ]
        ).lower()
        dimension_terms = {
            "semiconductor": ("semiconductor", "chip"),
            "semiconductor_ds": ("semiconductor", "logic", "data center"),
            "memory": ("memory", "dram", "nand", "hbm"),
            "foundry": ("foundry", "contract chip", "fab"),
            "consumer_electronics": ("consumer electronics", "device", "appliance"),
            "software_platform": ("software", "platform", "cloud", "internet"),
            "financial_services": ("bank", "financial", "insurance", "holding"),
            "payments": ("payment", "wallet", "checkout"),
            "biotechnology": ("biotech", "biologics", "pharma"),
            "drug_delivery": ("drug delivery", "hyaluronidase", "subcutaneous"),
            "battery": ("battery", "energy storage"),
            "automotive": ("automotive", "vehicle", "mobility"),
            "telecommunications": ("telecom", "wireless", "network"),
            "energy": ("energy", "power", "oil", "gas"),
            "materials": ("material", "chemical", "steel", "metal"),
            "industrial": ("industrial", "machinery", "construction", "engineering"),
            "commerce": ("retail", "commerce", "merchant", "consumer"),
            "media": ("media", "content", "gaming", "entertainment"),
            "operational_scale": ("mega cap", "large cap", "mid cap", "scale"),
            "overall_business": (),
        }[dimension]
        matches = sum(term in searchable for term in dimension_terms)
        return min(1.0, matches / max(1, min(2, len(dimension_terms))))

    @staticmethod
    def _profile_redundancy(
        left: dict[str, object],
        right: dict[str, object],
    ) -> float:
        left_raw_tags = left.get("business_tags", [])
        right_raw_tags = right.get("business_tags", [])
        left_values = left_raw_tags if isinstance(left_raw_tags, list) else []
        right_values = right_raw_tags if isinstance(right_raw_tags, list) else []
        left_tags = {str(tag).lower() for tag in left_values}
        right_tags = {str(tag).lower() for tag in right_values}
        union = left_tags | right_tags
        tag_overlap = len(left_tags & right_tags) / len(union) if union else 0.0
        same_industry = str(left.get("industry")) == str(right.get("industry"))
        return min(1.0, (0.6 * tag_overlap) + (0.4 if same_industry else 0.0))

    @staticmethod
    def _comparison_description(
        request: GlobalPeerMatchRequest,
        dimension: GlobalPeerComparisonDimension,
        peer: GlobalPeerMatch,
    ) -> str:
        subject = GlobalPeerExplanationGenerator._stock_display_name(request)
        label = dimension.replace("_", " ")
        industry = (
            peer.industry
            if peer.industry not in {"", "Unclassified", GENERIC_LISTED_INDUSTRY}
            else peer.business_model
        )
        return (
            f"{peer.company_name} provides the {label} reference for {subject}; "
            f"its {industry.lower()} profile is the strongest quality-adjusted fit "
            "for this comparison dimension."
        )

    @staticmethod
    def _build_key_strengths(
        request: GlobalPeerMatchRequest,
        stock_profile: dict[str, object],
    ) -> list[GlobalPeerKeyStrength]:
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and len(anchor.key_strengths) == 4:
            return [
                GlobalPeerKeyStrength(
                    title=item.title,
                    description=item.description,
                    icon_key=cast(GlobalPeerStrengthIconKey, item.icon_key),
                )
                for item in anchor.key_strengths
            ]

        subject = GlobalPeerExplanationGenerator._stock_display_name(request)
        strengths: list[GlobalPeerKeyStrength] = []
        seen_titles: set[str] = set()
        seen_descriptions: set[str] = set()

        def add(title: str, description: str, source_value: str) -> None:
            if len(strengths) == 4:
                return
            title_key = title.strip().lower()
            description_key = " ".join(description.lower().split())
            if not title_key or not description_key:
                return
            if title_key in seen_titles or description_key in seen_descriptions:
                return
            seen_titles.add(title_key)
            seen_descriptions.add(description_key)
            strengths.append(
                GlobalPeerKeyStrength(
                    title=title.strip(),
                    description=" ".join(description.split()),
                    icon_key=GlobalPeerMatcher._strength_icon_key(source_value),
                )
            )

        for _, _, (
            title,
            description,
            icon_key,
            _,
        ) in GlobalPeerMatcher._profile_strength_signals(stock_profile):
            add(title, description, icon_key)

        if len(strengths) != 4:
            raise ModelArtifactInvalidError(
                f"Company evidence is insufficient for four key strengths: {subject}"
            )
        return strengths

    @staticmethod
    def _profile_strength_signals(
        stock_profile: dict[str, object],
    ) -> list[tuple[int, int, StrengthSignal]]:
        business_summary = str(stock_profile.get("business_summary") or "").strip()
        raw_tags = stock_profile.get("business_tags", [])
        tags = [str(tag) for tag in raw_tags] if isinstance(raw_tags, list) else []
        evidence = " ".join(
            value
            for value in (
                business_summary,
                str(stock_profile.get("industry") or ""),
                str(stock_profile.get("business_model") or ""),
                "" if business_summary else " ".join(tags),
            )
            if value
        ).lower()
        ranked: list[tuple[int, int, StrengthSignal]] = []
        for index, signal in enumerate(STRENGTH_SIGNALS):
            matches = sum(keyword.lower() in evidence for keyword in signal[3])
            if matches:
                ranked.append((matches, -index, signal))
        return sorted(ranked, reverse=True)

    @staticmethod
    def _title_label(value: str) -> str:
        return " ".join(part.capitalize() for part in value.replace("_", " ").split())

    @staticmethod
    def _strength_icon_key(value: str) -> GlobalPeerStrengthIconKey:
        normalized = value.lower().replace("_", " ")
        direct_keys = {
            "memory",
            "foundry",
            "ai",
            "ecosystem",
            "semiconductor",
            "consumer electronics",
            "software platform",
            "financial services",
            "payments",
            "biotechnology",
            "drug delivery",
            "battery",
            "automotive",
            "telecommunications",
            "energy",
            "materials",
            "industrial",
            "commerce",
            "media",
            "global business",
            "operational scale",
        }
        if normalized in direct_keys:
            return cast(GlobalPeerStrengthIconKey, normalized.replace(" ", "_"))
        mappings: tuple[tuple[tuple[str, ...], GlobalPeerStrengthIconKey], ...] = (
            (("memory", "dram", "nand", "hbm"), "memory"),
            (("foundry", "fab"), "foundry"),
            (("artificial intelligence", " ai ", "data center"), "ai"),
            (("ecosystem",), "ecosystem"),
            (("semiconductor", "chip"), "semiconductor"),
            (("consumer electronics", "appliance", "device"), "consumer_electronics"),
            (("payment", "wallet", "checkout"), "payments"),
            (("bank", "financial", "insurance", "holding"), "financial_services"),
            (("drug delivery", "subcutaneous"), "drug_delivery"),
            (("bio", "pharma", "health"), "biotechnology"),
            (("software", "platform", "cloud", "internet"), "software_platform"),
            (("battery", "energy storage"), "battery"),
            (("auto", "vehicle", "mobility"), "automotive"),
            (("telecom", "wireless", "network"), "telecommunications"),
            (("energy", "power", "oil", "gas"), "energy"),
            (("material", "chemical", "steel", "metal"), "materials"),
            (("industrial", "machinery", "construction", "engineering"), "industrial"),
            (("retail", "commerce", "consumer", "food"), "commerce"),
            (("media", "content", "gaming", "entertainment", "advertising"), "media"),
            (("scale", "mega cap", "large cap", "mid cap"), "operational_scale"),
        )
        return next(
            (
                icon
                for keywords, icon in mappings
                if any(keyword in normalized for keyword in keywords)
            ),
            "global_business",
        )

    @classmethod
    def _calibrated_confidence_score(
        cls,
        *,
        stock_profile: dict[str, object],
        primary_peer: GlobalPeerMatch,
    ) -> float:
        score = max(0.0, min(1.0, primary_peer.similarity_score))
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        stock_model = str(stock_profile.get("business_model") or "Operating company")
        stock_scale = str(stock_profile.get("scale_bucket") or "UNKNOWN")
        generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
        generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
        stock_has_specific_domain = (
            stock_sector not in generic_sectors and stock_industry not in generic_industries
        )
        if not stock_has_specific_domain:
            return min(score, 0.39)

        same_sector = stock_sector == primary_peer.sector
        same_industry = stock_industry == primary_peer.industry
        same_model = stock_model == primary_peer.business_model
        same_scale = stock_scale != "UNKNOWN" and stock_scale == primary_peer.scale_bucket
        financial_score = primary_peer.financial_similarity_score or 0.0

        if same_industry and same_model:
            score = max(score, 0.52)
        elif same_industry:
            score = max(score, 0.46)
        elif same_sector:
            score = max(score, 0.42)
        else:
            return min(score, 0.39)

        if financial_score >= 0.88 and same_scale:
            score = max(score, 0.62)
        elif financial_score >= 0.55:
            score = max(score, 0.48)
        return max(0.0, min(1.0, score))

    def _stock_profile(self, request: GlobalPeerMatchRequest) -> dict[str, object]:
        existing = self._korea_profiles.get(request.stock_code)
        if existing is None:
            base_name = re.sub(r"(?:\d+)?우B?$", "", request.stock_name).strip()
            existing = self._korea_profile_by_name.get(base_name)
        if existing is not None:
            profile = cast(dict[str, object], existing).copy()
            enrichment = " ".join(
                value
                for value in [
                    request.stock_name,
                    request.stock_name_en,
                    " ".join(request.aliases),
                    request.description,
                ]
                if value
            )
            if enrichment:
                tags = infer_business_tags(request.stock_name, request.stock_name_en)
                profile["profile_text"] = normalize_profile_text(
                    f"{profile['profile_text']} {enrichment} {' '.join(tags)}"
                )
                if str(profile.get("sector") or "Unclassified") in {
                    "Unclassified",
                    GENERIC_LISTED_SECTOR,
                }:
                    profile["business_tags"] = tags
                    profile["sector"] = infer_sector(tags)
                    profile["industry"] = infer_industry(tags)
                    profile["business_model"] = infer_business_model(tags)
            profile["request_stock_name"] = request.stock_name
            profile["request_stock_name_en"] = request.stock_name_en
            return profile
        entry = StockUniverseEntry(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            stock_name_en=request.stock_name_en,
            market=request.market,
            aliases=tuple(request.aliases),
        )
        profile = build_korea_profile(entry).to_dict()
        if request.description:
            profile["profile_text"] = f"{profile['profile_text']} {request.description}".strip()
        profile["request_stock_name"] = request.stock_name
        profile["request_stock_name_en"] = request.stock_name_en
        return profile

    def _financial_similarities(self, stock_profile: dict[str, object]) -> np.ndarray:
        matrix = self._eligible_us_financial_matrix
        if matrix is None:
            return np.zeros(len(self._eligible_us_profiles), dtype=float)
        query_raw = stock_profile.get("financial_feature_vector", [])
        if not isinstance(query_raw, list) or not query_raw:
            return np.zeros(len(self._eligible_us_profiles), dtype=float)
        query = np.array([float(value) for value in query_raw], dtype=float)
        if not has_financial_signal(query.tolist()):
            return np.zeros(len(self._eligible_us_profiles), dtype=float)
        candidate_matrix = np.array(matrix, dtype=float)
        raw_scores = cosine_similarity(query.reshape(1, -1), candidate_matrix)[0]
        return np.array([max(0.0, min(1.0, (float(score) + 1.0) / 2.0)) for score in raw_scores])

    def _semantic_similarities(self, query_vector: object) -> np.ndarray:
        query_semantic = self._semantic_reducer.transform(query_vector)
        norm = np.linalg.norm(query_semantic)
        if norm > 0:
            query_semantic = query_semantic / norm
        return np.asarray(
            cosine_similarity(query_semantic, self._eligible_us_semantic_matrix)[0],
            dtype=float,
        )

    def _base_similarities(
        self,
        stock_profile: dict[str, object],
        text_similarities: np.ndarray,
        semantic_similarities: np.ndarray,
        financial_similarities: np.ndarray,
    ) -> np.ndarray:
        base_scores = np.asarray(
            (0.50 * text_similarities)
            + (0.30 * semantic_similarities)
            + (0.20 * financial_similarities)
        )
        for index in range(len(self._eligible_us_profiles)):
            base_scores[index] *= self._same_company_penalty(
                stock_profile,
                self._eligible_us_profiles[index],
            )
        return base_scores

    def _combined_similarities(
        self,
        stock_profile: dict[str, object],
        base_scores: np.ndarray,
        text_similarities: np.ndarray,
        semantic_similarities: np.ndarray,
        financial_similarities: np.ndarray,
        candidate_indices: list[int],
    ) -> np.ndarray:
        combined = np.array(base_scores, dtype=float)
        if not candidate_indices:
            return combined
        feature_rows = np.array(
            [
                self._pairwise_feature_vector(
                    stock_profile,
                    self._eligible_us_profiles[index],
                    text_similarities[index],
                    semantic_similarities[index],
                    financial_similarities[index],
                )
                for index in candidate_indices
            ],
            dtype=float,
        )
        ranker_scores = self._pairwise_ranker.predict_proba(feature_rows)[:, 1]
        for position, index in enumerate(candidate_indices):
            financial_score = financial_similarities[index]
            peer_profile = self._eligible_us_profiles[index]
            familiarity = float(peer_profile.get("familiarity_score") or 0.0)
            completeness = float(peer_profile.get("profile_completeness_score") or 0.0)
            combined[index] = (
                (0.55 * ranker_scores[position])
                + (0.35 * base_scores[index])
                + (0.06 * familiarity)
                + (0.04 * completeness)
            )
            combined[index] *= self._domain_priority_multiplier(stock_profile, peer_profile)
            candidate_vector = self._eligible_us_profiles[index].get("financial_feature_vector", [])
            if (
                financial_similarities.any()
                and isinstance(candidate_vector, list)
                and has_financial_signal(candidate_vector)
            ):
                combined[index] = max(
                    combined[index],
                    (0.10 * base_scores[index]) + (0.03 * financial_score),
                )
        return np.asarray(combined, dtype=float)

    def _candidate_indices(
        self,
        *,
        stock_profile: dict[str, object],
        base_similarities: np.ndarray,
        limit: int,
    ) -> list[int]:
        pool_size = min(len(self._eligible_us_profiles), max(1, limit))
        if pool_size >= len(self._eligible_us_profiles):
            base_top_indices = list(range(len(self._eligible_us_profiles)))
        else:
            partition = np.argpartition(base_similarities, -pool_size)[-pool_size:]
            base_top_indices = [
                int(index)
                for index in sorted(
                    partition,
                    key=lambda candidate: float(base_similarities[int(candidate)]),
                    reverse=True,
                )
            ]
        domain_indices = self._domain_candidate_indices(stock_profile, base_similarities, pool_size)
        return list(dict.fromkeys([*domain_indices, *base_top_indices]))

    def _domain_candidate_indices(
        self,
        stock_profile: dict[str, object],
        base_similarities: np.ndarray,
        limit: int,
    ) -> list[int]:
        compatible = [
            index
            for index, peer_profile in enumerate(self._eligible_us_profiles)
            if self._is_domain_compatible(stock_profile, peer_profile)
        ]
        compatible.sort(key=lambda index: float(base_similarities[index]), reverse=True)
        return compatible[: min(limit, len(compatible))]

    @staticmethod
    def _is_domain_compatible(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
    ) -> bool:
        generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
        generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        if stock_industry not in generic_industries and peer_industry == stock_industry:
            return True
        return stock_sector not in generic_sectors and peer_sector == stock_sector

    @staticmethod
    def _domain_priority_multiplier(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
    ) -> float:
        generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
        generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        multiplier = 1.0
        if stock_sector not in generic_sectors:
            if peer_sector in generic_sectors:
                multiplier *= 0.60
            elif stock_sector != peer_sector:
                multiplier *= 0.20
        if stock_industry not in generic_industries:
            if peer_industry in generic_industries:
                multiplier *= 0.75
            elif stock_industry != peer_industry:
                multiplier *= 0.45
        return multiplier

    @staticmethod
    def _sector_penalty(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
    ) -> float:
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
        if stock_sector not in generic_sectors and peer_sector not in generic_sectors:
            return 1.0 if stock_sector == peer_sector else 0.45
        if stock_sector not in generic_sectors and peer_sector in generic_sectors:
            return 0.75
        return 1.0

    @staticmethod
    def _industry_penalty(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
    ) -> float:
        generic_industries = {"Unclassified", "Listed Operating Company"}
        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        if stock_industry not in generic_industries and peer_industry not in generic_industries:
            return 1.0 if stock_industry == peer_industry else 0.65
        if stock_industry not in generic_industries and peer_industry in generic_industries:
            return 0.85
        return 1.0

    def _pairwise_feature_vector(
        self,
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
        text_similarity: float,
        semantic_similarity: float,
        financial_similarity: float,
    ) -> list[float]:
        generic_sectors = {"Unclassified", GENERIC_LISTED_SECTOR}
        generic_industries = {"Unclassified", GENERIC_LISTED_INDUSTRY}
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        stock_model = str(stock_profile.get("business_model") or "Operating company")
        peer_model = str(peer_profile.get("business_model") or "Operating company")
        stock_scale = str(stock_profile.get("scale_bucket") or "UNKNOWN")
        peer_scale = str(peer_profile.get("scale_bucket") or "UNKNOWN")
        same_sector = stock_sector == peer_sector and stock_sector not in generic_sectors
        same_industry = stock_industry == peer_industry and stock_industry not in generic_industries
        specific_sector_mismatch = (
            stock_sector not in generic_sectors
            and peer_sector not in generic_sectors
            and stock_sector != peer_sector
        )
        specific_industry_mismatch = (
            stock_industry not in generic_industries
            and peer_industry not in generic_industries
            and stock_industry != peer_industry
        )
        values = [
            float(text_similarity),
            float(semantic_similarity),
            float(financial_similarity),
            1.0 if same_sector else 0.0,
            1.0 if same_industry else 0.0,
            1.0 if stock_model == peer_model else 0.0,
            1.0 if stock_scale != "UNKNOWN" and stock_scale == peer_scale else 0.0,
            1.0 if specific_sector_mismatch else 0.0,
            1.0 if specific_industry_mismatch else 0.0,
            self._normalized_log_feature(peer_profile.get("market_cap_usd")),
            self._normalized_log_feature(peer_profile.get("revenue_usd")),
            self._log_gap(
                stock_profile.get("market_cap_usd"),
                peer_profile.get("market_cap_usd"),
            ),
            self._log_gap(
                stock_profile.get("revenue_usd"),
                peer_profile.get("revenue_usd"),
            ),
            abs(
                self._margin_feature(
                    stock_profile.get("operating_income_usd"),
                    stock_profile.get("revenue_usd"),
                )
                - self._margin_feature(
                    peer_profile.get("operating_income_usd"),
                    peer_profile.get("revenue_usd"),
                )
            ),
            self._score(peer_profile.get("familiarity_score")),
            self._score(peer_profile.get("profile_completeness_score")),
            self._score(peer_profile.get("market_cap_reliability_score")),
        ]
        if len(values) != len(self._pairwise_feature_names):
            raise ModelArtifactInvalidError("Global peer pairwise feature count mismatch")
        return values

    @staticmethod
    def _same_company_penalty(
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
    ) -> float:
        source_names = [
            str(stock_profile.get("display_name") or ""),
            str(stock_profile.get("request_stock_name") or ""),
            str(stock_profile.get("request_stock_name_en") or ""),
        ]
        peer_name = str(peer_profile.get("display_name") or "")
        normalized_peer = normalize_profile_text(peer_name)
        for source_name in source_names:
            normalized_source = normalize_profile_text(source_name)
            if len(normalized_source) >= 4 and (
                normalized_source == normalized_peer
                or normalized_source in normalized_peer
                or normalized_peer in normalized_source
            ):
                return 0.01
        return 1.0

    def _selected_indices(
        self,
        ranked_indices: list[int],
        limit: int,
    ) -> list[int]:
        selected: list[int] = []
        for index in ranked_indices:
            if index not in selected:
                selected.append(index)
            if len(selected) >= limit:
                break
        return selected[:limit]

    def _to_peer_match(
        self,
        rank: int,
        profile: dict[str, object],
        score: float,
        financial_score: float,
        request: GlobalPeerMatchRequest,
        stock_profile: dict[str, object],
    ) -> GlobalPeerMatch:
        raw_tags = profile.get("business_tags", [])
        tags = [str(tag) for tag in raw_tags] if isinstance(raw_tags, list) else []
        primary_tag = tags[0] if tags else "business model"
        sector = str(profile.get("sector") or "Unclassified")
        industry = str(profile.get("industry") or "Unclassified")
        business_model = str(profile.get("business_model") or "Operating company")
        scale_bucket = str(profile.get("scale_bucket") or "UNKNOWN")
        financial_score = self._calibrated_financial_similarity_score(
            stock_profile,
            profile,
            financial_score,
        )
        matched_factors = self._matched_factors(
            request=request,
            stock_profile=stock_profile,
            peer_profile=profile,
            score=score,
            financial_score=financial_score,
        )
        subject_name = GlobalPeerExplanationGenerator._stock_display_name(request)
        rationale = (
            f"{profile['display_name']} is selected as the global {primary_tag} reference for "
            f"{subject_name} based on sector, industry, business model, scale, and "
            "trained cross-market profile similarity."
        )
        if request.stock_code == "196170" and profile.get("identifier") == "HALO":
            rationale = (
                "Halozyme Therapeutics is the drug-delivery platform reference for Alteogen "
                "because its hyaluronidase-enabled formulation and licensing model is comparable."
            )
        return GlobalPeerMatch(
            rank=rank,
            ticker=str(profile["identifier"]),
            company_name=str(profile["display_name"]),
            exchange=str(profile["exchange"]),
            country=str(profile["country"]),
            similarity_score=round(score, 4),
            business_tags=tags,
            sector=sector,
            industry=industry,
            business_model=business_model,
            scale_bucket=scale_bucket,
            fiscal_year=self._optional_int(profile.get("fiscal_year")),
            market_cap_usd=self._optional_float(profile.get("market_cap_usd")),
            revenue_usd=self._optional_float(profile.get("revenue_usd")),
            operating_income_usd=self._optional_float(profile.get("operating_income_usd")),
            net_income_usd=self._optional_float(profile.get("net_income_usd")),
            financial_data_source=str(profile.get("financial_data_source") or ""),
            financial_similarity_score=round(financial_score, 4) if financial_score > 0 else None,
            matched_factors=matched_factors,
            rationale=rationale,
        )

    def _matched_factors(
        self,
        request: GlobalPeerMatchRequest,
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
        score: float,
        financial_score: float,
    ) -> list[str]:
        subject_name = GlobalPeerExplanationGenerator._stock_display_name(request)
        peer_name = str(
            peer_profile.get("display_name") or peer_profile.get("identifier") or "peer"
        )
        if request.stock_code == "196170" and peer_profile.get("identifier") == "HALO":
            return [
                "Sector: Alteogen and Halozyme Therapeutics are Health Care companies.",
                "Industry: Alteogen and Halozyme Therapeutics operate in Biotechnology.",
                (
                    "Business model: Alteogen and Halozyme Therapeutics monetize platform "
                    "drug-delivery technology through licensing, milestones, and royalties."
                ),
                (
                    "Technology: Alteogen and Halozyme Therapeutics are associated with "
                    "hyaluronidase-enabled IV-to-SC formulation conversion."
                ),
                (
                    "Scale: Alteogen and Halozyme Therapeutics are treated as mid-cap "
                    "biotech platform references in the curated anchor set."
                ),
                (
                    "Financial similarity: market cap, revenue, and profitability "
                    f"score {financial_score:.4f}."
                ),
            ]

        factors: list[str] = []
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        if stock_sector == peer_sector and stock_sector != "Unclassified":
            factors.append(f"Sector: {subject_name} and {peer_name} map to {stock_sector}.")
        else:
            factors.append(f"Sector: source={stock_sector}, peer={peer_sector}.")

        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        if stock_industry == peer_industry and stock_industry != "Unclassified":
            factors.append(f"Industry: {subject_name} and {peer_name} map to {stock_industry}.")
        else:
            factors.append(f"Industry: source={stock_industry}, peer={peer_industry}.")

        stock_model = str(stock_profile.get("business_model") or "Operating company")
        peer_model = str(peer_profile.get("business_model") or "Operating company")
        if stock_model == peer_model:
            factors.append(f"Business model: {subject_name} and {peer_name} map to {stock_model}.")
        else:
            factors.append(f"Business model: source={stock_model}, peer={peer_model}.")

        stock_scale = str(stock_profile.get("scale_bucket") or "UNKNOWN")
        peer_scale = str(peer_profile.get("scale_bucket") or "UNKNOWN")
        if stock_scale != "UNKNOWN" and stock_scale == peer_scale:
            factors.append(f"Scale: {subject_name} and {peer_name} map to {stock_scale}.")
        else:
            factors.append(f"Scale: source={stock_scale}, peer={peer_scale}.")

        factors.extend(
            self._financial_context_factors(
                stock_profile=stock_profile,
                peer_profile=peer_profile,
                financial_score=financial_score,
            )
        )
        factors.append(f"Model similarity: blended peer score {score:.4f}.")
        return factors

    def _financial_context_factors(
        self,
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
        financial_score: float,
    ) -> list[str]:
        factors: list[str] = []
        if financial_score <= 0:
            return factors
        stock_scale = str(stock_profile.get("scale_bucket") or "UNKNOWN")
        peer_scale = str(peer_profile.get("scale_bucket") or "UNKNOWN")
        same_scale = stock_scale != "UNKNOWN" and stock_scale == peer_scale
        if self._has_market_cap_outlier(stock_profile) or self._has_market_cap_outlier(
            peer_profile
        ):
            factors.append(
                "Financial comparability: market-cap input is treated as directional "
                f"because the source value looks high relative to revenue; adjusted score "
                f"{financial_score:.4f}."
            )
            return factors
        if financial_score >= 0.88:
            if same_scale:
                factors.append(
                    "Financial comparability: direct market cap, revenue, and "
                    f"profitability similarity score {financial_score:.4f}."
                )
            else:
                factors.append(
                    "Financial comparability: strong financial-vector similarity, but "
                    f"scale differs ({stock_scale} vs {peer_scale}); use as a "
                    "US-market proxy rather than a strict size match."
                )
        elif financial_score >= 0.55:
            factors.append(
                "Financial comparability: partial direct similarity; the peer is used as "
                f"a business-domain proxy with financial score {financial_score:.4f}."
            )
        else:
            factors.append(
                "Financial comparability: not a direct balance-sheet match; the peer is "
                f"selected mainly for domain fit with financial score {financial_score:.4f}."
            )

        peer_identifier = str(peer_profile.get("identifier") or "")
        percentile = self._us_market_cap_percentiles.get(peer_identifier)
        if percentile is not None:
            top_percent = max(0.1, round((1.0 - percentile) * 100.0, 1))
            if stock_scale != "UNKNOWN" and stock_scale == peer_scale:
                factors.append(
                    f"US peer-universe position: {peer_scale} peer, around the top "
                    f"{top_percent}% by market cap among eligible US peers."
                )
            else:
                factors.append(
                    f"US peer-universe position: {peer_scale} peer, around the top "
                    f"{top_percent}% among eligible US peers; size is interpreted as "
                    "relative US-market positioning rather than a strict Korean-size match."
                )
        return factors

    @classmethod
    def _calibrated_financial_similarity_score(
        cls,
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
        financial_score: float,
    ) -> float:
        if cls._has_market_cap_outlier(stock_profile) or cls._has_market_cap_outlier(peer_profile):
            return min(financial_score, 0.54)
        return financial_score

    @classmethod
    def _has_market_cap_outlier(cls, profile: dict[str, object]) -> bool:
        market_cap = cls._optional_float(profile.get("market_cap_usd"))
        revenue = cls._optional_float(profile.get("revenue_usd"))
        if market_cap is None or revenue is None or revenue <= 0:
            return False
        return market_cap / revenue >= 30.0

    @staticmethod
    def _market_cap_percentiles(
        profiles: list[dict[str, object]],
    ) -> dict[str, float]:
        values: list[tuple[str, float]] = []
        for profile in profiles:
            identifier = str(profile.get("identifier") or "")
            market_cap = profile.get("market_cap_usd")
            reliability = GlobalPeerMatcher._score(
                profile.get("market_cap_reliability_score")
            )
            if (
                not identifier
                or not isinstance(market_cap, int | float)
                or market_cap <= 0
                or reliability < 0.5
            ):
                continue
            values.append((identifier, float(market_cap)))
        values.sort(key=lambda item: item[1])
        if len(values) <= 1:
            return {identifier: 1.0 for identifier, _ in values}
        denominator = len(values) - 1
        return {identifier: rank / denominator for rank, (identifier, _) in enumerate(values)}

    @staticmethod
    def _optional_float(value: object) -> float | None:
        if value is None or value == "":
            return None
        if isinstance(value, int | float | str):
            return float(value)
        raise TypeError("optional float field must be numeric")

    @staticmethod
    def _score(value: object) -> float:
        if isinstance(value, int | float | str):
            return float(value)
        return 0.0

    @staticmethod
    def _optional_int(value: object) -> int | None:
        if value is None or value == "":
            return None
        if isinstance(value, int | float | str):
            return int(value)
        raise TypeError("optional int field must be numeric")

    @classmethod
    def _log_gap(cls, left: object, right: object) -> float:
        left_value = cls._log_feature(left)
        right_value = cls._log_feature(right)
        if left_value == 0.0 or right_value == 0.0:
            return 1.0
        return abs(left_value - right_value)

    @staticmethod
    def _log_feature(value: object) -> float:
        if value is None or value == "":
            return 0.0
        if isinstance(value, int | float | str):
            number = float(value)
            if number <= 0:
                return 0.0
            return float(np.log10(number))
        return 0.0

    @classmethod
    def _normalized_log_feature(cls, value: object) -> float:
        log_value = cls._log_feature(value)
        if log_value <= 0:
            return 0.0
        return max(0.0, min(1.0, log_value / 12.0))

    @staticmethod
    def _margin_feature(numerator: object, denominator: object) -> float:
        if numerator is None or denominator is None or numerator == "" or denominator == "":
            return 0.0
        if not isinstance(numerator, int | float | str) or not isinstance(
            denominator,
            int | float | str,
        ):
            return 0.0
        denominator_float = float(denominator)
        if denominator_float <= 0:
            return 0.0
        return max(-1.0, min(1.0, float(numerator) / denominator_float))

    def _headline(self, request: GlobalPeerMatchRequest, primary_peer: GlobalPeerMatch) -> str:
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and anchor.headline_template:
            stock_name_en = request.stock_name_en or "Alteogen"
            return anchor.headline_template.format(
                stock_name_en=stock_name_en,
                peer_name=primary_peer.company_name,
            )
        stock_name = request.stock_name_en or request.stock_name
        tag = primary_peer.business_tags[0] if primary_peer.business_tags else "Global Peer"
        return f"{stock_name} Maps Closest To '{primary_peer.company_name}' — A {tag.title()} Peer"

    def _summary(self, request: GlobalPeerMatchRequest, primary_peer: GlobalPeerMatch) -> str:
        anchor = KOREA_ANCHORS.get(request.stock_code)
        if anchor and anchor.summary:
            return anchor.summary
        stock_name = request.stock_name_en or request.stock_name
        tag = primary_peer.business_tags[0] if primary_peer.business_tags else "business model"
        return (
            f"{stock_name} is positioned in a similar global {tag} value chain as "
            f"{primary_peer.company_name}. The match is generated from a model trained on the "
            "full Korean stock universe and the full United States listed symbol universe."
        )

    @staticmethod
    def _confidence_level(score: float) -> ConfidenceLevel:
        if score >= 0.72:
            return "HIGH"
        if score >= 0.40:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _validate_payload(payload: dict[str, Any], model_path: Path) -> None:
        required_keys = {
            "schema_version",
            "version",
            "vectorizer",
            "eligible_us_matrix",
            "semantic_reducer",
            "eligible_us_semantic_matrix",
            "pairwise_ranker",
            "pairwise_feature_names",
            "eligible_us_profiles",
            "korea_profiles",
        }
        missing_keys = sorted(required_keys - set(payload))
        if missing_keys:
            joined_keys = ", ".join(missing_keys)
            raise ModelArtifactInvalidError(
                f"Global peer model artifact is missing required keys: {joined_keys} ({model_path})"
            )
        if payload["schema_version"] != GLOBAL_PEER_SCHEMA_VERSION:
            raise ModelArtifactInvalidError(
                f"Unsupported global peer schema version: {payload['schema_version']}"
            )
        if tuple(payload["pairwise_feature_names"]) != PAIRWISE_FEATURE_NAMES:
            raise ModelArtifactInvalidError("Unsupported global peer pairwise feature schema")
