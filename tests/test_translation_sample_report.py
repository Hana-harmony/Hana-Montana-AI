import json
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, AlertAnalysisResponse
from hannah_montana_ai.services.feature_contracts import translate_financial_korean_to_english
from hannah_montana_ai.training.translation_sample_report import (
    TRANSLATION_SAMPLE_REPORT_SCHEMA_VERSION,
    build_translation_sample_report,
)


class FakeModel:
    version = "fake-financial-model"


class FakeAnalyzer:
    model = FakeModel()

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        stock_code = request.stock_universe[0].stock_code if request.stock_universe else None
        stock_name = request.stock_universe[0].stock_name if request.stock_universe else None
        event_tags = ["DISCLOSURE", "RISK"] if request.source_type == "DISCLOSURE" else ["EARNINGS"]
        return AlertAnalysisResponse(
            stock_code=stock_code,
            stock_name=stock_name,
            source_type=request.source_type,
            original_title=request.title,
            summary=request.title,
            event_tags=event_tags,
            sentiment="NEGATIVE" if request.source_type == "DISCLOSURE" else "POSITIVE",
            importance="CRITICAL" if request.source_type == "DISCLOSURE" else "MEDIUM",
            related_stocks=[stock_code] if stock_code else [],
            holder_target=True,
            watchlist_target=True,
            duplicate_key="fake-duplicate-key",
            model_version=self.model.version,
            event_confidence=0.9,
            sentiment_confidence=0.86,
            importance_confidence=0.88,
            stock_match_confidence=1.0 if stock_code else 0.0,
            review_required=stock_code is None,
            review_reasons=[] if stock_code else ["STOCK_NOT_MATCHED"],
        )


def test_translation_sample_report_compares_real_sample_shape(tmp_path: Path) -> None:
    news_path = tmp_path / "news.jsonl"
    disclosure_path = tmp_path / "disclosure.jsonl"
    news_path.write_text(
        json.dumps(
            {
                "text": "삼성전자 어닝서프라이즈로 영업이익 증가",
                "tags": ["EARNINGS"],
                "sentiment": "POSITIVE",
                "importance": "MEDIUM",
                "source_type": "NEWS",
                "source_url": "https://example.com/news/1",
                "stock_code": "005930",
                "stock_name": "삼성전자",
                "review_note": "실제 뉴스 gold와 같은 스키마",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    disclosure_path.write_text(
        json.dumps(
            {
                "text": "비덴트 주권매매거래정지기간변경(상장폐지사유발생)",
                "tags": ["DISCLOSURE", "RISK"],
                "sentiment": "NEGATIVE",
                "importance": "CRITICAL",
                "source_type": "DISCLOSURE",
                "source_url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=1",
                "stock_code": "121800",
                "stock_name": "비덴트",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_translation_sample_report(
        news_gold_path=news_path,
        disclosure_gold_path=disclosure_path,
        sample_limit_per_source=1,
        analyzer=FakeAnalyzer(),  # type: ignore[arg-type]
        generated_at=datetime(2026, 6, 20, tzinfo=UTC),
    )

    assert report["schema_version"] == TRANSLATION_SAMPLE_REPORT_SCHEMA_VERSION
    assert report["sample_count"] == 2
    assert report["summary"]["glossary_applied_count"] == 2
    assert report["external_translation_boundary"]["join_key"] == "external_translation_join_key"
    news_row = report["rows"][0]
    disclosure_row = report["rows"][1]
    assert "earnings surprise" in news_row["translation"]["translated_title"]
    assert "operating profit" in news_row["translation"]["translated_title"]
    assert news_row["comparison"]["sentiment_match"] is True
    assert "share trading halt period change" in disclosure_row["translation"]["translated_title"]
    assert "delisting cause occurred" in disclosure_row["translation"]["translated_title"]
    assert disclosure_row["comparison"]["stock_match"] is True


def test_financial_glossary_v2_covers_disclosure_mistranslation_cases() -> None:
    result = translate_financial_korean_to_english(
        "한화시스템 단일판매ㆍ공급계약체결 및 전환사채 발행"
    )

    assert "Hanwha Systems" in result.translated_text
    assert "supply contract" in result.translated_text
    assert "convertible bond" in result.translated_text
    assert {
        term.english_term
        for term in result.glossary_terms
    } >= {"Hanwha Systems", "supply contract", "convertible bond"}
