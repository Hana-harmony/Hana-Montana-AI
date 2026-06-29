import json
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher

SMOKE_CASES = [
    ("005930", "삼성전자", "Samsung Electronics", "KOSPI"),
    ("000660", "SK하이닉스", "SK hynix", "KOSPI"),
    ("035420", "NAVER", "NAVER", "KOSPI"),
    ("005380", "현대차", "Hyundai Motor", "KOSPI"),
    ("373220", "LG에너지솔루션", "LG Energy Solution", "KOSPI"),
    ("207940", "삼성바이오로직스", "Samsung Biologics", "KOSPI"),
    ("068270", "셀트리온", "Celltrion", "KOSPI"),
    ("105560", "KB금융", "KB Financial Group", "KOSPI"),
    ("055550", "신한지주", "Shinhan Financial Group", "KOSPI"),
    ("086790", "하나금융지주", "Hana Financial Group", "KOSPI"),
    ("051910", "LG화학", "LG Chem", "KOSPI"),
    ("006400", "삼성SDI", "Samsung SDI", "KOSPI"),
    ("066570", "LG전자", "LG Electronics", "KOSPI"),
    ("017670", "SK텔레콤", "SK Telecom", "KOSPI"),
    ("196170", "알테오젠", "Alteogen", "KOSDAQ"),
]


def build_global_peer_ai_smoke_report(model_path: Path, report_path: Path) -> dict[str, object]:
    matcher = GlobalPeerMatcher(model_path)
    cases: list[dict[str, object]] = []
    for stock_code, stock_name, stock_name_en, market in SMOKE_CASES:
        response = matcher.match(
            GlobalPeerMatchRequest(
                stock_code=stock_code,
                stock_name=stock_name,
                stock_name_en=stock_name_en,
                market=market,
                peer_count=5,
            )
        )
        cases.append(
            {
                "stock_code": response.stock_code,
                "stock_name": response.stock_name,
                "stock_name_en": response.stock_name_en,
                "market": market,
                "primary_peer": response.primary_peer.model_dump(),
                "peer_tickers": [peer.ticker for peer in response.peers],
                "headline": response.headline,
                "summary": response.summary,
                "confidence_score": response.confidence_score,
                "confidence_level": response.confidence_level,
                "model_version": response.model_version,
                "source": response.source,
            }
        )

    report = {
        "schema_version": "global-peer-ai-smoke/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "model_version": matcher.version,
        "sample_count": len(cases),
        "cases": cases,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


if __name__ == "__main__":
    settings = get_settings()
    smoke = build_global_peer_ai_smoke_report(
        model_path=settings.global_peer_model_path,
        report_path=settings.global_peer_ai_smoke_report_path,
    )
    print(
        "글로벌 피어 AI smoke 완료: "
        f"{smoke['sample_count']}개, model={smoke['model_version']}"
    )
