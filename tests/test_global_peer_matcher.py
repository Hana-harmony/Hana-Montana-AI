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
    infer_business_tags,
    infer_business_tags_from_company_summary,
    infer_business_tags_from_ksic,
    load_korea_company_profiles,
    load_us_stock_universe,
    write_korea_company_profiles,
)
from hannah_montana_ai.training.stock_universe import load_stock_universe

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
        ("005930", "삼성전자", "Samsung Electronics", "KOSPI"),
        ("000660", "SK하이닉스", "SK hynix", "KOSPI"),
        ("035420", "NAVER", "NAVER", "KOSPI"),
        ("017670", "SK텔레콤", "SK Telecom", "KOSPI"),
        ("066570", "LG전자", "LG Electronics", "KOSPI"),
        ("373220", "LG에너지솔루션", "LG Energy Solution", "KOSPI"),
    ]

    for code, name, english_name, market in cases:
        response = matcher.match(
            GlobalPeerMatchRequest(
                stock_code=code,
                stock_name=name,
                stock_name_en=english_name,
                market=market,
            )
        )
        assert response.primary_peer.ticker == response.comparisons[0].peer.ticker
        assert response.peers[0].ticker == response.primary_peer.ticker
        assert len(response.comparisons) == 3
        assert len(response.key_strengths) == 4
        assert response.primary_peer.matched_factors


@pytest.mark.parametrize(
    ("stock_code", "stock_name", "stock_name_en", "sector", "industry"),
    [
        ("003550", "LG", "LG", "Financials", "Investment Holding Companies"),
        ("086790", "하나금융지주", "Hana Financial Group", "Financials", "Banks"),
        ("316140", "우리금융지주", "Woori Financial Group", "Financials", "Banks"),
        (
            "373220",
            "LG에너지솔루션",
            "LG Energy Solution",
            "Industrials",
            "Battery and Energy Storage",
        ),
        ("000320", "노루홀딩스", "Noroo Holdings", "Materials", "Metals and Materials"),
        (
            "017670",
            "SK텔레콤",
            "SK Telecom",
            "Communication Services",
            "Telecommunications",
        ),
    ],
)
def test_global_peer_model_preserves_authoritative_comparison_domain(
    stock_code: str,
    stock_name: str,
    stock_name_en: str,
    sector: str,
    industry: str,
) -> None:
    matcher = GlobalPeerMatcher(MODEL_PATH)
    response = matcher.match(
        GlobalPeerMatchRequest(
            stock_code=stock_code,
            stock_name=stock_name,
            stock_name_en=stock_name_en,
            market="KOSPI",
        )
    )
    profile = matcher._korea_profiles[stock_code]

    assert profile["sector"] == sector
    assert profile["industry"] == industry
    assert response.source_sector == sector
    assert response.source_industry == industry
    assert response.primary_peer.sector == sector
    assert response.primary_peer.industry == industry
    if stock_code != "017670":
        assert response.primary_peer.ticker != "T"


def test_alteogen_uses_the_same_dynamic_matching_path() -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code="196170",
            stock_name="알테오젠",
            stock_name_en="Alteogen",
            market="KOSDAQ",
        )
    )

    assert response.primary_peer.company_name in response.headline
    assert response.primary_peer.ticker == response.comparisons[0].peer.ticker
    assert "Is The" not in response.headline
    assert response.explanation_source == "GROUNDED_TEMPLATE_STRUCTURED_RAG"


@pytest.mark.parametrize(
    ("stock_code", "stock_name", "stock_name_en"),
    [
        ("207940", "삼성바이오로직스", "Samsung Biologics"),
        ("068270", "셀트리온", "Celltrion"),
    ],
)
def test_biotechnology_stocks_do_not_select_cross_sector_primary_peers(
    stock_code: str,
    stock_name: str,
    stock_name_en: str,
) -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code=stock_code,
            stock_name=stock_name,
            stock_name_en=stock_name_en,
            market="KOSPI",
        )
    )

    assert response.primary_peer.sector == "Health Care"
    assert response.primary_peer.industry == "Biotechnology"


def test_samsung_comparison_uses_familiar_companies_and_four_strengths() -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code="005930",
            stock_name="삼성전자",
            stock_name_en="Samsung Electronics",
            market="KOSPI",
        )
    )

    assert len(response.comparisons) == 3
    assert len({item.peer.ticker for item in response.comparisons}) == 3
    assert all(item.peer.ticker in CURATED_GLOBAL_BRAND_TIERS for item in response.comparisons)
    assert {"memory", "foundry", "ai"}.issubset({item.icon_key for item in response.key_strengths})
    assert len({item.title for item in response.key_strengths}) == 4
    assert all("both companies" not in item.description.lower() for item in response.comparisons)
    assert all("both companies" not in item.description.lower() for item in response.key_strengths)


def test_missing_master_english_name_never_leaks_hangul_into_peer_copy() -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code="000050",
            stock_name="경방",
            stock_name_en="",
            market="KOSPI",
        )
    )

    assert response.stock_name_en == "Gyeongbang"
    assert "경방" not in response.headline
    assert "경방" not in response.summary


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
        ("035720", "카카오", "Kakao", "KOSPI"),
        ("005380", "현대자동차", "Hyundai Motor", "KOSPI"),
        ("247540", "에코프로비엠", "EcoPro BM", "KOSDAQ"),
    ]

    for code, name, english_name, market in cases:
        response = matcher.match(
            GlobalPeerMatchRequest(
                stock_code=code,
                stock_name=name,
                stock_name_en=english_name,
                market=market,
            )
        )

        assert len({strength.title for strength in response.key_strengths}) == 4
        stock_profile = matcher._korea_profiles[code]
        for comparison in response.comparisons:
            peer_profile = matcher._eligible_us_profiles[
                matcher._eligible_us_index_by_ticker[comparison.peer.ticker]
            ]
            assert matcher._comparison_domain_compatible(
                stock_profile,
                peer_profile,
                "overall_business",
                matcher._overall_business_fit(stock_profile, peer_profile),
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
    assert MODEL_PATH.stat().st_mode & 0o444 == 0o444
    assert "korea_business_profile_classifier" not in payload
    assert "pairwise_ranker" not in payload
    assert "korea_peer_training_labels" not in payload
    assert payload["schema_version"] == "global-peer-dynamic-similarity/v5"
    assert payload["eligible_us_matrix"].shape[1] <= 100_000
    assert payload["semantic_reducer"].components_.shape[0] <= 192


def test_business_summary_tagger_extracts_domain_without_noise() -> None:
    tags = infer_business_tags_from_company_summary(
        "동사는 전자상거래 플랫폼과 유통사업을 영위하며 화장품 브랜드를 판매한다."
    )

    assert tags[:2] == ("retail", "consumer brands")
    assert "software platform" not in tags
    assert "semiconductors" not in tags


def test_business_summary_tagger_does_not_treat_generic_network_as_telecom() -> None:
    tags = infer_business_tags_from_company_summary(
        "전세계 27개 지역의 글로벌 네트워크와 연구개발 네트워크를 운영한다."
    )

    assert "telecommunications" not in tags
    assert "telecommunications" in infer_business_tags_from_company_summary(
        "이동통신과 유무선 통신서비스 및 통신 네트워크를 운영한다."
    )


def test_business_summary_tagger_separates_telecom_operators_and_equipment() -> None:
    operator_tags = infer_business_tags_from_company_summary(
        "MVNO 알뜰폰 이동통신서비스를 제공한다."
    )
    equipment_tags = infer_business_tags_from_company_summary(
        "이동통신 기지국 장비와 RF중계기, 광전송장비를 제조한다."
    )
    software_tags = infer_business_tags_from_company_summary(
        "정보통신사업부를 양수해 IT 서비스와 시스템 구축, 디지털 전환을 제공한다."
    )

    assert operator_tags[0] == "telecommunications"
    assert equipment_tags[0] == "telecom equipment"
    assert "telecommunications" not in equipment_tags
    assert software_tags[0] == "software platform"
    assert "telecommunications" not in software_tags


def test_business_summary_tagger_separates_airlines_from_aerospace_manufacturers() -> None:
    airline_tags = infer_business_tags_from_company_summary(
        "국내외 정기항공 여객운송과 화물 사업을 영위하며 42개 도시에 취항한다."
    )
    manufacturer_tags = infer_business_tags_from_company_summary(
        "항공기 엔진과 우주발사체, 자주포 및 유도무기를 개발·생산한다."
    )

    assert airline_tags[0] == "passenger transportation"
    assert "aerospace" not in airline_tags
    assert manufacturer_tags[0] == "aerospace"
    assert "passenger transportation" not in manufacturer_tags


def test_company_name_tagger_requires_english_keyword_boundaries() -> None:
    assert "battery" not in infer_business_tags("TransDigm Group", "TransDigm Group")
    assert "aerospace" not in infer_business_tags("Fair Isaac", "Fair Isaac")
    assert "energy" not in infer_business_tags("Las Vegas Sands", "Las Vegas Sands")
    assert "holding company" not in infer_business_tags(
        "Zimmer Biomet Holdings", "Zimmer Biomet Holdings"
    )
    assert "battery" in infer_business_tags("Samsung SDI", "Samsung SDI")


def test_shipbuilding_summary_does_not_treat_offshore_platform_as_software() -> None:
    tags = infer_business_tags_from_company_summary(
        "LNG 운반선과 컨테이너선, FPSO, 해양플랫폼을 건조하고 해양플랜트를 수행한다."
    )

    assert tags[0] == "shipbuilding"
    assert "software platform" not in tags


def test_generic_formulation_and_auction_terms_do_not_create_narrow_domains() -> None:
    formulation_tags = infer_business_tags_from_company_summary(
        "유액제와 수화제 등 다양한 제형의 농약 및 비료를 생산한다."
    )
    auction_tags = infer_business_tags_from_company_summary(
        "기업 소모성 자재 구매대행과 일반 경매사업을 운영한다."
    )

    assert "drug delivery" not in formulation_tags
    assert "art auction" not in auction_tags


@pytest.mark.parametrize(
    ("stock_code", "expected_industry"),
    [
        ("007590", "Specialty Chemicals"),
        ("007720", "Retail"),
        ("039740", "Retail"),
        ("044960", "Biotechnology"),
        ("051160", "Retail"),
        ("092130", "Software"),
        ("092730", "Household and Personal Products"),
    ],
)
def test_narrow_domain_false_positives_are_grounded_by_company_evidence(
    stock_code: str,
    expected_industry: str,
) -> None:
    payload = joblib.load(MODEL_PATH)

    assert payload["korea_profiles"][stock_code]["industry"] == expected_industry


@pytest.mark.parametrize(
    ("stock_code", "stock_name", "stock_name_en"),
    [
        ("042660", "한화오션", "Hanwha Ocean"),
        ("009540", "HD한국조선해양", "HD Korea Shipbuilding"),
        ("329180", "HD현대중공업", "HD Hyundai Heavy Industries"),
        ("010140", "삼성중공업", "Samsung Heavy Industries"),
    ],
)
def test_shipbuilders_match_grounded_shipbuilding_peers(
    stock_code: str,
    stock_name: str,
    stock_name_en: str,
) -> None:
    response = GlobalPeerMatcher(MODEL_PATH).match(
        GlobalPeerMatchRequest(
            stock_code=stock_code,
            stock_name=stock_name,
            stock_name_en=stock_name_en,
            market="KOSPI",
        )
    )

    assert response.primary_peer.industry == "Shipbuilding"
    assert len(response.comparisons) == 3
    assert all(item.peer.industry == "Shipbuilding" for item in response.comparisons)
    assert {item.peer.ticker for item in response.comparisons} == {"HII", "GD", "BWXT"}


def test_ksic_tags_cover_konex_business_domains_without_stock_overrides() -> None:
    assert infer_business_tags_from_ksic("213") == ("biotech",)
    assert infer_business_tags_from_ksic("58221") == ("software platform",)
    assert infer_business_tags_from_ksic("30399") == ("automotive",)
    assert infer_business_tags_from_ksic("31321") == ("aerospace",)
    assert infer_business_tags_from_ksic("51100") == ("passenger transportation",)


@pytest.mark.parametrize(
    ("stock_code", "expected_industry"),
    [
        ("003490", "Airlines"),
        ("012450", "Aerospace and Defense"),
        ("047810", "Aerospace and Defense"),
    ],
)
def test_air_transport_and_aerospace_profiles_are_separated(
    stock_code: str,
    expected_industry: str,
) -> None:
    payload = joblib.load(MODEL_PATH)

    assert payload["korea_profiles"][stock_code]["industry"] == expected_industry


@pytest.mark.parametrize(
    ("stock_code", "expected_industry"),
    [
        ("004920", "Software"),
        ("025770", "Payments"),
        ("030200", "Telecommunications"),
        ("032500", "Communications Equipment"),
        ("036630", "Construction and Engineering"),
        ("039980", "Software"),
        ("050890", "Communications Equipment"),
        ("065530", "Communications Equipment"),
        ("148250", "Communications Equipment"),
        ("211270", "Communications Equipment"),
        ("267850", "Software"),
        ("356890", "Software"),
        ("456010", "Semiconductors"),
    ],
)
def test_telecom_operator_false_positives_use_company_operating_domain(
    stock_code: str,
    expected_industry: str,
) -> None:
    payload = joblib.load(MODEL_PATH)

    assert payload["korea_profiles"][stock_code]["industry"] == expected_industry


def test_artifact_covers_the_entire_active_kis_equity_universe() -> None:
    payload = joblib.load(MODEL_PATH)
    active_codes = {
        stock.stock_code
        for stock in load_stock_universe(Path("data/reference/korea_stock_universe.csv"))
    }

    assert len(active_codes) == 2_752
    assert set(payload["korea_profiles"]) == active_codes


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
    with pytest.raises(ModelArtifactInvalidError, match="synchronized KIS equity model universe"):
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
    assert len(response.comparisons) == 3
    assert len({item.peer.ticker for item in response.comparisons}) == 3
    assert response.primary_peer.ticker == response.comparisons[0].peer.ticker
    assert response.peers[0].ticker == response.primary_peer.ticker
    assert response.primary_peer.company_name in response.headline


def test_request_accepts_krx_alphanumeric_codes() -> None:
    request = GlobalPeerMatchRequest(
        stock_code="0001A0",
        stock_name="덕양에너젠",
        market="KOSPI",
    )

    assert request.stock_code == "0001A0"
