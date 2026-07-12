from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.collector import read_raw_alerts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
GOLD_PATHS = (
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
)

# 제목의 대상 종목 관점에서 방향이 명확한 행만 교정한다.
OVERRIDES: dict[str, dict[str, Any]] = {
    "완성차 업계 5월 판매 감소… 해외 확장 나선 기아 '나홀로 성장'": {
        "sentiment": "POSITIVE",
        "review_note": "대상 종목 기아는 업계 감소와 달리 성장했으므로 종목 기준 긍정으로 판정.",
    },
    "작년 수퍼갑으로, 올해는 파트너 간택하러 오는 젠슨 황 HBM 납품 공급망 협상": {
        "sentiment": "NEUTRAL",
        "review_note": "특정 공급사 선정 결과가 확정되지 않은 협상 기사이므로 중립으로 판정.",
    },
    "SK 실트론 매각 재검토…반도체 자회사 포트폴리오 전략 흔들림": {
        "sentiment": "NEGATIVE",
        "review_note": "매각 재검토와 전략 불확실성이 대상 기업에 부정적이므로 부정으로 판정.",
    },
}


def main() -> None:
    raw_by_url = {row.original_url: row for row in read_raw_alerts(RAW_PATH)}
    for path in GOLD_PATHS:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        reviewed: list[dict[str, Any]] = []
        for row in rows:
            override = OVERRIDES.get(str(row.get("text", "")), {})
            source_url = str(row.get("source_url", ""))
            raw = raw_by_url.get(source_url)
            reviewed.append(
                row
                | override
                | {
                    "source_review_status": "CODEX_REVIEW_APPROVED",
                    "reviewer_id": "codex-financial-review-v1",
                    "provider": raw.provider if raw else row.get("provider", "naver-news"),
                    "published_at": raw.published_at if raw else row.get("published_at", ""),
                    "content_hash": raw.content_hash if raw else row.get("content_hash", ""),
                }
            )
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in reviewed),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
