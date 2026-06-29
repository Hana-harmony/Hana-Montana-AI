from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, cast

import joblib
from sklearn.metrics.pairwise import cosine_similarity

from hannah_montana_ai.domain.schemas import (
    GlobalPeerMatch,
    GlobalPeerMatchRequest,
    GlobalPeerMatchResponse,
)
from hannah_montana_ai.services.model import (
    ModelArtifactInvalidError,
    ModelArtifactNotFoundError,
)
from hannah_montana_ai.training.global_peer_trainer import (
    GLOBAL_PEER_SCHEMA_VERSION,
    KOREA_ANCHORS,
    build_korea_profile,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry

ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]


class GlobalPeerMatcher:
    def __init__(self, model_path: Path) -> None:
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
        self._eligible_us_profiles = list(payload["eligible_us_profiles"])
        self._korea_profiles = dict(payload["korea_profiles"])

    def match(self, request: GlobalPeerMatchRequest) -> GlobalPeerMatchResponse:
        stock_profile = self._stock_profile(request)
        query_vector = self._vectorizer.transform([str(stock_profile["profile_text"])])
        similarities = cosine_similarity(query_vector, self._eligible_us_matrix)[0]
        ranked_indices = similarities.argsort()[::-1]

        preferred_ticker = KOREA_ANCHORS.get(request.stock_code)
        selected_indices = self._selected_indices(
            ranked_indices=[int(index) for index in ranked_indices],
            preferred_ticker=preferred_ticker.preferred_peer_ticker if preferred_ticker else "",
            similarities=similarities,
            limit=max(1, request.peer_count),
        )
        peers = [
            self._to_peer_match(
                rank=rank,
                profile=self._eligible_us_profiles[index],
                score=float(similarities[index]),
                request=request,
                stock_profile=stock_profile,
            )
            for rank, index in enumerate(selected_indices, start=1)
        ]
        primary_peer = peers[0]
        headline = self._headline(request, primary_peer)
        summary = self._summary(request, primary_peer)
        confidence_score = max(0.0, min(1.0, primary_peer.similarity_score))
        return GlobalPeerMatchResponse(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            stock_name_en=request.stock_name_en or str(stock_profile["display_name"]),
            headline=headline,
            summary=summary,
            primary_peer=primary_peer,
            peers=peers,
            confidence_score=round(confidence_score, 4),
            confidence_level=self._confidence_level(confidence_score),
            model_version=self.version,
            source="HANNAH_GLOBAL_PEER_TFIDF",
        )

    def _stock_profile(self, request: GlobalPeerMatchRequest) -> dict[str, object]:
        existing = self._korea_profiles.get(request.stock_code)
        if existing is not None and not request.description:
            return cast(dict[str, object], existing)
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
        return profile

    def _selected_indices(
        self,
        ranked_indices: list[int],
        preferred_ticker: str,
        similarities: Any,
        limit: int,
    ) -> list[int]:
        selected: list[int] = []
        if preferred_ticker:
            for index, profile in enumerate(self._eligible_us_profiles):
                if str(profile["identifier"]) == preferred_ticker:
                    selected.append(index)
                    break
        for index in ranked_indices:
            if index not in selected:
                selected.append(index)
            if len(selected) >= limit:
                break
        return sorted(selected, key=lambda index: float(similarities[index]), reverse=True)[:limit]

    def _to_peer_match(
        self,
        rank: int,
        profile: dict[str, object],
        score: float,
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
        matched_factors = self._matched_factors(
            request=request,
            stock_profile=stock_profile,
            peer_profile=profile,
            score=score,
        )
        rationale = (
            f"Both companies map to the global {primary_tag} peer group based on "
            "sector, industry, business model, scale, and trained cross-market profile similarity."
        )
        if request.stock_code == "196170" and profile.get("identifier") == "HALO":
            rationale = (
                "Both companies are biotech platform providers centered on drug-delivery "
                "technology, subcutaneous formulation conversion, and royalty-style licensing."
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
            matched_factors=matched_factors,
            rationale=rationale,
        )

    def _matched_factors(
        self,
        request: GlobalPeerMatchRequest,
        stock_profile: dict[str, object],
        peer_profile: dict[str, object],
        score: float,
    ) -> list[str]:
        if request.stock_code == "196170" and peer_profile.get("identifier") == "HALO":
            return [
                "Sector: both are Health Care companies.",
                "Industry: both operate in Biotechnology.",
                (
                    "Business model: both monetize platform drug-delivery technology "
                    "through licensing, milestones, and royalties."
                ),
                (
                    "Technology: both are associated with hyaluronidase-enabled "
                    "IV-to-SC formulation conversion."
                ),
                (
                    "Scale: both are treated as mid-cap biotech platform peers in the "
                    "curated anchor set."
                ),
            ]

        factors: list[str] = []
        stock_sector = str(stock_profile.get("sector") or "Unclassified")
        peer_sector = str(peer_profile.get("sector") or "Unclassified")
        if stock_sector == peer_sector and stock_sector != "Unclassified":
            factors.append(f"Sector: both are mapped to {stock_sector}.")
        else:
            factors.append(f"Sector: source={stock_sector}, peer={peer_sector}.")

        stock_industry = str(stock_profile.get("industry") or "Unclassified")
        peer_industry = str(peer_profile.get("industry") or "Unclassified")
        if stock_industry == peer_industry and stock_industry != "Unclassified":
            factors.append(f"Industry: both are mapped to {stock_industry}.")
        else:
            factors.append(f"Industry: source={stock_industry}, peer={peer_industry}.")

        stock_model = str(stock_profile.get("business_model") or "Operating company")
        peer_model = str(peer_profile.get("business_model") or "Operating company")
        if stock_model == peer_model:
            factors.append(f"Business model: both are mapped to {stock_model}.")
        else:
            factors.append(f"Business model: source={stock_model}, peer={peer_model}.")

        stock_scale = str(stock_profile.get("scale_bucket") or "UNKNOWN")
        peer_scale = str(peer_profile.get("scale_bucket") or "UNKNOWN")
        if stock_scale != "UNKNOWN" and stock_scale == peer_scale:
            factors.append(f"Scale: both are mapped to {stock_scale}.")
        else:
            factors.append(f"Scale: source={stock_scale}, peer={peer_scale}.")

        factors.append(f"Model similarity: TF-IDF cross-market profile score {score:.4f}.")
        return factors

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
        return f"{stock_name} Is South Korea's '{primary_peer.company_name}' — A {tag.title()} Peer"

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
        if score >= 0.45:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _validate_payload(payload: dict[str, Any], model_path: Path) -> None:
        required_keys = {
            "schema_version",
            "version",
            "vectorizer",
            "eligible_us_matrix",
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
