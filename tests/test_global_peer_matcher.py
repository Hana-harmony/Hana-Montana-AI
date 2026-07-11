from pathlib import Path

import joblib
import pytest

from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest
from hannah_montana_ai.services.global_peer_explainer import (
    GlobalPeerExplanationContext,
    GlobalPeerExplanationGenerator,
)
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.services.model import ModelArtifactInvalidError
from hannah_montana_ai.training.global_peer_trainer import (
    CURATED_GLOBAL_BRAND_TIERS,
    KoreaCompanyProfile,
    clean_security_name,
    infer_business_tags_from_company_summary,
    load_korea_company_profiles,
    load_us_stock_universe,
    write_korea_company_profiles,
)

MODEL_PATH = Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib")


def test_us_stock_universe_covers_listed_symbol_directory() -> None:
    entries = load_us_stock_universe(Path("data/reference/us_stock_universe.csv"))

    assert len(entries) >= 5_000
    assert any(entry.ticker == "HALO" for entry in entries)


def test_security_name_removes_share_class_and_legal_suffixes() -> None:
    assert clean_security_name("Alphabet Inc. Class A Common Stock") == "Alphabet"


def test_global_peer_model_matches_core_korean_stocks() -> None:
    matcher = GlobalPeerMatcher(MODEL_PATH)
    cases = [
        ("005930", "삼성전자", "Samsung Electronics", "KOSPI", "MU"),
        ("000660", "SK하이닉스", "SK hynix", "KOSPI", "MU"),
        ("035420", "NAVER", "NAVER", "KOSPI", "GOOGL"),
        ("017670", "SK텔레콤", "SK Telecom", "KOSPI", "VZ"),
        ("066570", "LG전자", "LG Electronics", "KOSPI", "WHR"),
        ("373220", "LG에너지솔루션", "LG Energy Solution", "KOSPI", "TSLA"),
    ]

    for code, name, english_name, market, expected_ticker in cases:
        response = matcher.match(
            GlobalPeerMatchRequest(
                stock_code=code,
                stock_name=name,
                stock_name_en=english_name,
                market=market,
            )
        )
        assert response.primary_peer.ticker == expected_ticker
        assert response.primary_peer.matched_factors


def test_alteogen_uses_curated_halozyme_template() -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code="196170",
            stock_name="알테오젠",
            stock_name_en="Alteogen",
            market="KOSDAQ",
        )
    )

    assert response.primary_peer.ticker == "HALO"
    assert "Alteogen Is The 'Halozyme Therapeutics'" in response.headline
    assert "drug-delivery technology" in response.summary
    assert response.explanation_source == "GROUNDED_TEMPLATE_STRUCTURED_RAG"


def test_samsung_comparison_uses_familiar_companies_and_four_strengths() -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code="005930",
            stock_name="삼성전자",
            stock_name_en="Samsung Electronics",
            market="KOSPI",
        )
    )

    assert [item.dimension for item in response.comparisons] == [
        "overall_business",
        "semiconductor_ds",
        "foundry",
    ]
    assert [item.peer.ticker for item in response.comparisons] == ["AAPL", "INTC", "TSM"]
    assert [item.icon_key for item in response.key_strengths] == [
        "memory",
        "foundry",
        "ecosystem",
        "ai",
    ]
    assert len({item.title for item in response.key_strengths}) == 4
    assert all("both companies" not in item.description.lower() for item in response.comparisons)
    assert all("both companies" not in item.description.lower() for item in response.key_strengths)


def test_non_curated_comparison_is_complete_and_unique() -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code="035420",
            stock_name="NAVER",
            stock_name_en="NAVER",
            market="KOSPI",
        )
    )

    assert len(response.comparisons) == 3
    assert len({item.dimension for item in response.comparisons}) == 3
    assert len({item.peer.ticker for item in response.comparisons}) == 3
    assert len(response.key_strengths) == 4


def test_company_summary_drives_non_samsung_strengths_and_familiar_peers() -> None:
    matcher = GlobalPeerMatcher(MODEL_PATH)
    cases = [
        (
            "035720",
            "카카오",
            "Kakao",
            "KOSPI",
            {"Digital Platform", "Content Portfolio", "Mobility Portfolio", "Payments and Cards"},
        ),
        (
            "005380",
            "현대자동차",
            "Hyundai Motor",
            "KOSPI",
            {
                "Industrial Solutions",
                "Vehicle Manufacturing",
                "Mobility Portfolio",
                "Subsidiary Portfolio",
            },
        ),
        (
            "247540",
            "에코프로비엠",
            "EcoPro BM",
            "KOSDAQ",
            {
                "Battery Technology",
                "Advanced Materials",
                "Product Portfolio",
                "Industrial Solutions",
            },
        ),
    ]

    for code, name, english_name, market, expected_titles in cases:
        response = matcher.match(
            GlobalPeerMatchRequest(
                stock_code=code,
                stock_name=name,
                stock_name_en=english_name,
                market=market,
            )
        )

        assert {strength.title for strength in response.key_strengths} == expected_titles
        assert all(
            comparison.peer.ticker in CURATED_GLOBAL_BRAND_TIERS
            for comparison in response.comparisons
        )
        assert all("core operating area" not in item.description for item in response.key_strengths)


def test_explanation_generator_is_always_template_backed() -> None:
    request = GlobalPeerMatchRequest(
        stock_code="035420",
        stock_name="NAVER",
        stock_name_en="NAVER",
        market="KOSPI",
    )
    response = GlobalPeerMatcher(MODEL_PATH).match(request)
    context = GlobalPeerExplanationContext(
        request=request,
        primary_peer=response.primary_peer,
        confidence_level=response.confidence_level,
        confidence_score=response.confidence_score,
    )
    generator = GlobalPeerExplanationGenerator()

    assert generator.generate(context) == generator.template(context)
    assert generator.generate(context).source == "GROUNDED_TEMPLATE_STRUCTURED_RAG"


def test_us_peer_profiles_have_quality_signals() -> None:
    matcher = GlobalPeerMatcher(MODEL_PATH)
    profiles = {
        profile["identifier"]: profile
        for profile in matcher._eligible_us_profiles
        if profile["identifier"] in {"AAPL", "INTC", "TSM", "MU"}
    }

    assert set(profiles) == {"AAPL", "INTC", "TSM", "MU"}
    assert all(float(profiles[ticker]["familiarity_score"]) > 0.7 for ticker in profiles)
    assert profiles["TSM"]["business_model"] == "Pure-play semiconductor foundry manufacturing"


def test_global_peer_artifact_is_serving_only_and_github_safe() -> None:
    payload = joblib.load(MODEL_PATH)

    assert MODEL_PATH.stat().st_size < 95_000_000
    assert "korea_business_profile_classifier" not in payload
    assert payload["eligible_us_matrix"].shape[1] <= 100_000
    assert payload["semantic_reducer"].components_.shape[0] <= 192


def test_business_summary_tagger_extracts_domain_without_noise() -> None:
    tags = infer_business_tags_from_company_summary(
        "동사는 전자상거래 플랫폼과 유통사업을 영위하며 화장품 브랜드를 판매한다."
    )

    assert tags[:3] == ("retail", "consumer brands", "software platform")
    assert "semiconductors" not in tags


def test_korea_company_profile_roundtrip_preserves_summary(tmp_path: Path) -> None:
    path = tmp_path / "profiles.csv"
    write_korea_company_profiles(
        path,
        [
            KoreaCompanyProfile(
                stock_code="052020",
                corp_code="00273110",
                corp_name="에스티큐브",
                corp_name_eng="STCUBE",
                stock_name="에스티큐브",
                corp_cls="K",
                induty_code="465",
                est_dt="19890816",
                acc_mt="12",
                business_summary_text="항암 면역 치료제를 개발한다.",
                source="OPEN_DART_COMPANY+WISE_REPORT_BUSINESS_SUMMARY",
            )
        ],
    )

    assert load_korea_company_profiles(path)["052020"].business_summary_text == (
        "항암 면역 치료제를 개발한다."
    )


def test_unknown_english_name_does_not_leak_korean_or_internal_score() -> None:
    with pytest.raises(ModelArtifactInvalidError, match="Company evidence is insufficient"):
        GlobalPeerMatcher(MODEL_PATH).match(
            GlobalPeerMatchRequest(
                stock_code="000010",
                stock_name="신한은행",
                market="KOSPI",
            )
        )


def test_preferred_share_reuses_issuer_company_evidence() -> None:
    matcher = GlobalPeerMatcher(MODEL_PATH)
    response = matcher.match(
        GlobalPeerMatchRequest(
            stock_code="003495",
            stock_name="대한항공우",
            stock_name_en="Korean Air Preferred",
            market="KOSPI",
        )
    )
    issuer_response = matcher.match(
        GlobalPeerMatchRequest(
            stock_code="003490",
            stock_name="대한항공",
            stock_name_en="Korean Air",
            market="KOSPI",
        )
    )

    assert len(response.key_strengths) == 4
    assert [item.title for item in response.key_strengths] == [
        item.title for item in issuer_response.key_strengths
    ]


def test_request_accepts_krx_alphanumeric_codes() -> None:
    request = GlobalPeerMatchRequest(
        stock_code="0001A0",
        stock_name="덕양에너젠",
        market="KOSPI",
    )

    assert request.stock_code == "0001A0"
