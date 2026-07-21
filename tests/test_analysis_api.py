import json
import logging
import urllib.error
import urllib.request

import pytest
from fastapi.testclient import TestClient

from hannah_montana_ai.api import routes
from hannah_montana_ai.api.routes import (
    get_analyzer,
    get_audit_logger,
    get_korean_translation_service,
)
from hannah_montana_ai.core.config import Settings, get_settings
from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate
from hannah_montana_ai.main import _translation_provider_ready, app
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.korean_translation_generator import (
    KoreanTranslationContext,
    KoreanTranslationResult,
)
from hannah_montana_ai.services.model import ModelArtifactNotFoundError


def test_analyze_alert_returns_financial_labels() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "original_url": "https://example.com/news/1",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status"] == 200
    assert payload["code"] == "COMMON_000"
    assert payload["data"]["stock_code"] == "005930"
    assert payload["data"]["sentiment"] == "POSITIVE"
    assert "EARNINGS" in payload["data"]["event_tags"]
    assert 0.0 <= payload["data"]["event_confidence"] <= 1.0
    assert 0.0 <= payload["data"]["sentiment_confidence"] <= 1.0
    assert 0.0 <= payload["data"]["importance_confidence"] <= 1.0
    assert payload["data"]["stock_match_confidence"] == 1.0
    assert payload["data"]["content_availability"] == "SUMMARY_ONLY"
    assert payload["data"]["original_content"] == "반도체 수요 회복으로 실적 개선 기대가 커졌다."


def test_deferred_analysis_does_not_call_generation_translation() -> None:
    class TranslationMustNotRun:
        def translate_alert_fields(self, *_args, **_kwargs):
            raise AssertionError("deferred analysis must not invoke translation")

        def translate(self, *_args, **_kwargs):
            raise AssertionError("deferred analysis must not invoke translation")

    analyzer = AlertAnalyzer(translation_generator=TranslationMustNotRun())
    result = analyzer.analyze(AlertAnalysisRequest(
        source_type="NEWS",
        title="삼성전자 2분기 영업이익 증가",
        snippet="반도체 수요 회복으로 실적 개선 기대가 커졌다.",
        content="삼성전자는 HBM 수요 회복으로 영업이익 증가를 전망했다.",
        original_url="https://example.com/news/deferred",
        stock_universe=[StockCandidate(
            stock_code="005930",
            stock_name="삼성전자",
            stock_name_en="Samsung Electronics",
        )],
        translation_mode="DEFERRED",
    ))

    assert result.stock_code == "005930"
    assert result.summary_lines.what
    assert result.translated_title == ""
    assert result.translated_content == ""
    assert result.translation_provider == "deferred-full-text-translation"
    assert result.translation_status == "SOURCE_LANGUAGE_FALLBACK"


def test_full_analysis_translates_only_original_content() -> None:
    class CountingTranslationGenerator:
        def __init__(self) -> None:
            self.contexts: list[KoreanTranslationContext] = []

        def translate(self, context: KoreanTranslationContext) -> KoreanTranslationResult:
            self.contexts.append(context)
            return KoreanTranslationResult(
                translated_text=(
                    "Samsung Electronics expects operating profit to improve as HBM demand "
                    "recovers. Investors should monitor the next earnings release."
                ),
                provider="test-qwen",
                model_version="test-qwen-v1",
                status="TRANSLATED",
                prompt_version="test-prompt",
                quality_flags=[],
            )

    translation_generator = CountingTranslationGenerator()
    analyzer = AlertAnalyzer(translation_generator=translation_generator)
    source_content = (
        "삼성전자는 HBM 수요 회복으로 영업이익 증가를 전망했다. "
        "투자자는 다음 실적 발표를 확인해야 한다."
    )

    result = analyzer.analyze(AlertAnalysisRequest(
        source_type="NEWS",
        title="삼성전자 HBM 실적 개선 전망",
        snippet="HBM 수요 회복으로 실적 개선 기대가 커졌다.",
        content=source_content,
        original_url="https://example.com/news/full-translation",
        stock_universe=[StockCandidate(
            stock_code="005930",
            stock_name="삼성전자",
            stock_name_en="Samsung Electronics",
        )],
        translation_mode="FULL",
    ))

    assert [context.text for context in translation_generator.contexts] == [source_content]
    assert result.translated_title == result.summary_lines.what
    assert result.translated_summary == result.summary
    assert result.translated_content.startswith("Samsung Electronics")
    assert result.translation_status == "TRANSLATED"


def test_analysis_and_translation_routes_share_one_qwen_capacity_guard() -> None:
    get_analyzer.cache_clear()
    get_korean_translation_service.cache_clear()

    analyzer = get_analyzer()

    assert analyzer.translation_generator is get_korean_translation_service()


def test_analyze_alert_accepts_full_disclosure_above_legacy_60000_chars() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    long_content = " ".join(
        f"삼성전자는 제{i}항 자기주식 처분과 실적 전망을 공시했다. "
        f"투자자는 제{i}항 공시 원문과 수급 영향을 확인해야 한다."
        for i in range(1_250)
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "DISCLOSURE",
            "title": "삼성전자 주요사항보고서",
            "snippet": "자기주식 처분 결정",
            "content": long_content,
            "original_url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260706000444",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert len(long_content) > 60000
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["content_availability"] == "FULL_TEXT"
    assert len(payload["original_content"]) > 60000
    assert payload["stock_code"] == "005930"


def test_analyze_alert_extracts_korean_market_glossary_terms() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 개미 순매수에 대장주 강세",
            "snippet": "개미 투자자들이 삼성전자를 사들이며 대장주 흐름이 이어졌다.",
            "original_url": "https://example.com/news/glossary",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    terms = {term["normalized_term"]: term["english_term"] for term in payload["glossary_terms"]}
    descriptions = {
        term["normalized_term"]: term["description"]
        for term in payload["glossary_terms"]
    }
    assert terms["개미"] == "Ant"
    assert terms["대장주"] == "Daejangju"
    assert "individual retail investors" in descriptions["개미"]
    assert "leading or most influential" in descriptions["대장주"]
    assert "FINANCIAL_GLOSSARY_APPLIED" in payload["translation_quality_flags"]


def test_analyze_alert_explains_samjeon_nix_market_slang() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": '"삼전닉스" 수익률 안부럽다',
            "snippet": "외국인 순매수에 삼성전자와 SK하이닉스가 함께 강세를 보였다.",
            "original_url": "https://example.com/news/samjeon-nix",
            "stock_universe": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    samjeon_nix = next(
        term for term in payload["glossary_terms"] if term["normalized_term"] == "삼전닉스"
    )
    assert samjeon_nix["source_term"] == "삼전닉스"
    assert samjeon_nix["english_term"] == "Samsung Electronics and SK hynix basket"
    assert "Samsung Electronics and SK hynix" in samjeon_nix["description"]
    assert "FINANCIAL_GLOSSARY_APPLIED" in payload["translation_quality_flags"]


def test_analyze_alert_does_not_emit_generic_financial_words_as_glossary() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 실적 개선에 외국인 순매수",
            "snippet": "기관과 개인 투자자도 공시 이후 반도체 실적 전망을 확인했다.",
            "content": (
                "삼성전자는 반도체 실적 개선 기대가 커졌다고 밝혔다. "
                "외국인과 기관 수급 변화가 시장 관심을 모았다. "
                "투자자는 공시 이후 영업이익 전망을 확인해야 한다."
            ),
            "original_url": "https://example.com/news/generic-glossary",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    normalized_terms = {term["normalized_term"] for term in payload["glossary_terms"]}
    assert normalized_terms.isdisjoint({"실적", "외국인", "기관", "개인", "공시"})
    assert "FINANCIAL_GLOSSARY_APPLIED" not in payload["translation_quality_flags"]


def test_analyze_alert_rejects_tangential_sponsor_sports_stock_match() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "[mhn포토] 이지민, 남몰래 브이",
            "snippet": "이지민(KB금융그룹)이 18번홀 경기를 펼치고 있다.",
            "content": (
                "홈 골프 [mhn포토] 이지민, 남몰래 브이. 제16회 롯데 오픈 최종 "
                "4라운드가 열렸다. 이지민(KB금융그룹)이 18번홀 경기를 펼치고 있다."
            ),
            "original_url": "https://example.com/sports-photo",
            "stock_universe": [
                {
                    "stock_code": "105560",
                    "stock_name": "KB금융",
                    "stock_name_en": "KB Financial Group",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stock_code"] is None
    assert payload["stock_match_confidence"] == 0.0


def test_analyze_alert_rejects_tangential_galaxy_watch_sleep_study_match() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "40대가 전 연령 중 수면 최단",
            "snippet": "삼성 갤럭시 워치를 착용한 미국 성인 수면 데이터를 분석했다.",
            "content": (
                "성신여자대학교 심리학과와 미국 하버드 의대 공동 연구팀은 "
                "삼성 갤럭시 워치를 착용한 미국 성인 27만 명의 수면 데이터를 "
                "분석했다. 모든 사람에게 통용되는 단일 수면 기준은 없다고 밝혔다."
            ),
            "original_url": "https://example.com/sleep-study",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stock_code"] is None
    assert payload["stock_match_confidence"] == 0.0


def test_validation_error_returns_common_error_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "",
            "original_url": "not-a-url",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["status"] == 422
    assert payload["code"] == "COMMON_002"
    assert payload["errors"]


def test_analyze_alert_uses_internal_stock_universe_when_request_candidates_are_empty() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "original_url": "https://example.com/news/internal-stock-universe",
            "stock_universe": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["stock_code"] == "005930"
    assert payload["data"]["stock_name"] == "삼성전자"


def test_analyze_alert_writes_structured_audit_log_without_raw_content(caplog) -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()
    caplog.set_level(logging.INFO, logger="hannah_montana_ai.audit.analysis")

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "original_url": "https://example.com/news/audit-success",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    audit_payload = json.loads(caplog.records[-1].message)
    assert audit_payload["event"] == "analysis_audit"
    assert audit_payload["outcome"] == "success"
    assert audit_payload["model_version"] == response.json()["data"]["model_version"]
    assert audit_payload["stock_code"] == "005930"
    assert audit_payload["stock_match_confidence"] == 1.0
    assert "event_confidence" in audit_payload
    assert audit_payload["latency_ms"] >= 0
    assert "title_hash" in audit_payload
    assert "original_url_hash" in audit_payload
    assert "삼성전자 2분기 영업이익 증가" not in caplog.text
    assert "https://example.com/news/audit-success" not in caplog.text


def test_health_endpoint_is_available() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_detects_unavailable_translation_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(*_args: object, **_kwargs: object) -> object:
        raise urllib.error.URLError("unavailable")

    monkeypatch.setattr(urllib.request, "urlopen", unavailable)

    assert (
        _translation_provider_ready(
            Settings(
                korean_translation_llm_endpoint="http://127.0.0.1:18081",
            )
        )
        is False
    )


def test_openapi_docs_expose_analysis_contract() -> None:
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"] == "Hannah-Montana-AI"
    assert "/api/v1/alerts/analyze" in payload["paths"]
    assert "/api/v1/market/foreign-ownership/predict" in payload["paths"]


def test_analyze_alert_detects_critical_disclosure_risk() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "DISCLOSURE",
            "title": "위험기업 감사의견 거절로 상장폐지 위험 발생",
            "original_url": "https://example.com/disclosure/1",
            "stock_universe": [
                {
                    "stock_code": "123456",
                    "stock_name": "위험기업",
                    "stock_name_en": "Risk Company",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["stock_code"] == "123456"
    assert payload["data"]["sentiment"] == "NEGATIVE"
    assert payload["data"]["importance"] == "CRITICAL"
    assert payload["data"]["holder_target"] is True


def test_analyze_alert_fails_closed_when_model_artifact_is_unavailable(monkeypatch, caplog) -> None:
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()
    caplog.set_level(logging.INFO, logger="hannah_montana_ai.audit.analysis")

    def unavailable_analyzer():
        raise ModelArtifactNotFoundError("missing artifact")

    monkeypatch.setattr(routes, "get_analyzer", unavailable_analyzer)

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 실적 개선",
            "original_url": "https://example.com/news/model-missing",
            "stock_universe": [],
        },
    )

    assert response.status_code == 503
    payload = response.json()
    assert payload["success"] is False
    assert payload["status"] == 503
    assert payload["code"] == "AI_001"
    assert payload["message"] == "ML model artifact is unavailable"
    audit_payload = json.loads(caplog.records[-1].message)
    assert audit_payload["event"] == "analysis_audit"
    assert audit_payload["outcome"] == "failure"
    assert audit_payload["failure_reason"] == "model_artifact_unavailable"
    assert audit_payload["latency_ms"] >= 0
