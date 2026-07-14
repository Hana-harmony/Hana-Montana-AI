import json
from itertools import product
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl"

STOCKS = [
    ("005930", "삼성전자", "반도체"),
    ("000660", "SK하이닉스", "메모리"),
    ("005380", "현대차", "자동차"),
    ("035420", "NAVER", "플랫폼"),
    ("035720", "카카오", "인터넷"),
    ("207940", "삼성바이오로직스", "바이오"),
    ("068270", "셀트리온", "제약"),
    ("105560", "KB금융", "금융"),
]

SCENARIOS = [
    ("{name} {sector} 부문 매출 증가와 영업이익률 개선", ["EARNINGS"], "POSITIVE", "HIGH"),
    ("{name} 비용 증가로 분기 순이익 감소 전망", ["EARNINGS"], "NEGATIVE", "HIGH"),
    ("{name} 잠정실적 정정공시 제출", ["EARNINGS", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 해외 고객사와 장기 공급계약 체결", ["CONTRACT"], "POSITIVE", "HIGH"),
    ("{name} 기존 공급계약 해지 통보 수령", ["CONTRACT", "RISK"], "NEGATIVE", "HIGH"),
    ("{name} 단일판매 공급계약 체결 공시", ["CONTRACT", "DISCLOSURE"], "POSITIVE", "HIGH"),
    ("{name} 유상증자 일정 확정", ["CAPITAL_ACTION", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 배당 확대와 자사주 취득 계획 발표", ["CAPITAL_ACTION"], "POSITIVE", "HIGH"),
    ("{name} 감자 검토 소식에 투자자 우려 확대", ["CAPITAL_ACTION", "RISK"], "NEGATIVE", "HIGH"),
    ("{name} 물적분할 후 신설법인 설립 추진", ["CORPORATE_ACTION"], "NEUTRAL", "HIGH"),
    ("{name} 계열사 흡수합병 이사회 결의", ["CORPORATE_ACTION", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 비핵심 자회사 매각으로 재무 여력 개선", ["CORPORATE_ACTION"], "POSITIVE", "MEDIUM"),
    ("{name} 횡령 혐의 발생으로 내부통제 리스크 부각", ["RISK"], "NEGATIVE", "CRITICAL"),
    (
        "{name} 감사의견 비적정 가능성으로 상장폐지 우려",
        ["RISK", "DISCLOSURE"],
        "NEGATIVE",
        "CRITICAL",
    ),
    ("{name} 거래정지 사유 발생 안내", ["RISK", "DISCLOSURE"], "NEGATIVE", "HIGH"),
    ("{name} 사업보고서 제출 완료", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 임원 주요주주 특정증권 소유상황 보고", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 조회공시 요구에 대한 답변 제출", ["DISCLOSURE"], "NEUTRAL", "MEDIUM"),
    ("원화 약세로 {sector} 수출주 실적 기대감 확대", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("기준금리 인상 부담으로 {sector} 업종 투자심리 둔화", ["MACRO"], "NEGATIVE", "MEDIUM"),
    ("코스피 외국인 순매수 전환으로 {name} 수급 개선", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("환율과 금리 변동으로 {sector} 업종 등락 확대", ["MACRO"], "NEUTRAL", "MEDIUM"),
    ("국내 증시 변동성 확대 속 {name} 주가 관망세", ["GENERAL_MARKET"], "NEUTRAL", "MEDIUM"),
    ("외국인 매도세 확대에 {name} 단기 조정 압력", ["GENERAL_MARKET"], "NEGATIVE", "MEDIUM"),
    ("기관 순매수 유입으로 {name} 주가 반등 기대", ["GENERAL_MARKET"], "POSITIVE", "MEDIUM"),
    (
        "{sector} 업황 둔화와 수출 감소로 {name} 실적 우려",
        ["EARNINGS", "MACRO"],
        "NEGATIVE",
        "HIGH",
    ),
    ("{sector} 투자 확대 정책으로 {name} 성장 기대", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("{name} 불성실공시법인 지정 예고", ["RISK", "DISCLOSURE"], "NEGATIVE", "HIGH"),
    ("{name} 주요 소송 패소로 충당부채 증가 가능성", ["RISK"], "NEGATIVE", "HIGH"),
    ("{name} 대규모 투자 계획 공시로 중장기 성장성 부각", ["DISCLOSURE"], "POSITIVE", "HIGH"),
    ("{name} 매출액 또는 손익구조 변경 공시", ["EARNINGS", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    (
        "{name} 최대주주 변경을 수반하는 주식양수도 계약",
        ["CORPORATE_ACTION", "DISCLOSURE"],
        "NEUTRAL",
        "HIGH",
    ),
]

CONTEXTS = [
    "알림 대상은 보유자와 watchlist 등록자다.",
    "현지 투자자는 번역 제목과 요약으로 먼저 확인한다.",
    "원문 링크와 제출 시각을 함께 제공한다.",
]


def main() -> None:
    rows = []
    for (code, name, sector), (template, tags, sentiment, importance), context in product(
        STOCKS,
        SCENARIOS,
        CONTEXTS,
    ):
        source_type = "DISCLOSURE" if "DISCLOSURE" in tags else "NEWS"
        has_stock_reference = "{name}" in template
        rows.append(
            {
                "text": f"{template.format(name=name, sector=sector)}. {context}",
                "tags": tags,
                "sentiment": sentiment,
                "importance": importance,
                "source_type": source_type,
                "stock_code": code if has_stock_reference else None,
                "stock_name": name if has_stock_reference else None,
            }
        )

    OUTPUT_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({"gold_evaluation_count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
