import json
from itertools import product
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl"

STOCKS = [
    ("005930", "삼성전자", "반도체"),
    ("000660", "SK하이닉스", "메모리"),
    ("005380", "현대차", "자동차"),
    ("035420", "NAVER", "플랫폼"),
    ("035720", "카카오", "모빌리티"),
    ("207940", "삼성바이오로직스", "바이오"),
    ("068270", "셀트리온", "제약"),
    ("105560", "KB금융", "금융"),
]

TEMPLATES = [
    ("{name} {sector} 수요 회복으로 영업이익 증가 전망", ["EARNINGS"], "POSITIVE", "HIGH"),
    ("{name} 분기 실적 부진과 적자 확대 우려", ["EARNINGS", "RISK"], "NEGATIVE", "HIGH"),
    ("{name} 비용 증가로 분기 순이익 감소 전망", ["EARNINGS"], "NEGATIVE", "HIGH"),
    ("{name} 잠정 실적 공시 제출", ["EARNINGS", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 매출액 손익구조 변경사항 공시", ["EARNINGS", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 원가 부담 확대로 수익성 하락 우려", ["EARNINGS"], "NEGATIVE", "HIGH"),
    ("{name} 대규모 공급계약 체결로 매출 성장 기대", ["CONTRACT"], "POSITIVE", "HIGH"),
    ("{name} 주요 납품 계약 해지 가능성 제기", ["CONTRACT", "RISK"], "NEGATIVE", "HIGH"),
    ("{name} 단일판매 공급계약 체결 사실 공시", ["CONTRACT", "DISCLOSURE"], "POSITIVE", "HIGH"),
    (
        "{name} 단일판매ㆍ공급계약체결 자율공시",
        ["CONTRACT", "DISCLOSURE"],
        "POSITIVE",
        "HIGH",
    ),
    ("{name} 유상증자 결정으로 재무구조 개선 추진", ["CAPITAL_ACTION"], "NEUTRAL", "HIGH"),
    ("{name} 주요사항보고서 유상증자결정", ["CAPITAL_ACTION", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 주주환원 확대 위해 자사주 매입과 배당 검토", ["CAPITAL_ACTION"], "POSITIVE", "HIGH"),
    (
        "{name} 주요사항보고서 자기주식처분결정",
        ["CAPITAL_ACTION", "DISCLOSURE"],
        "NEUTRAL",
        "HIGH",
    ),
    (
        "{name} 자기주식취득신탁계약체결결정",
        ["CAPITAL_ACTION", "DISCLOSURE"],
        "POSITIVE",
        "HIGH",
    ),
    ("{name} 감자 결정 이후 주가 하락 위험 부각", ["CAPITAL_ACTION", "RISK"], "NEGATIVE", "HIGH"),
    (
        "{name} 감자 검토 소식에 투자자 우려 확대",
        ["CAPITAL_ACTION", "RISK"],
        "NEGATIVE",
        "HIGH",
    ),
    ("{name} 전환사채 발행 결정 공시", ["CAPITAL_ACTION", "DISCLOSURE"], "NEUTRAL", "HIGH"),
    ("{name} 계열사 합병 결정으로 사업 재편 본격화", ["CORPORATE_ACTION"], "NEUTRAL", "HIGH"),
    ("{name} 해외 법인 매각으로 현금흐름 개선 기대", ["CORPORATE_ACTION"], "POSITIVE", "MEDIUM"),
    ("{name} 비핵심 자회사 매각으로 재무 여력 개선", ["CORPORATE_ACTION"], "POSITIVE", "MEDIUM"),
    ("{name} 물적분할 추진으로 지배구조 변화 예상", ["CORPORATE_ACTION"], "NEUTRAL", "HIGH"),
    (
        "{name} 최대주주 변경 관련 주식 양수도 계약 체결",
        ["CORPORATE_ACTION", "DISCLOSURE"],
        "NEUTRAL",
        "HIGH",
    ),
    (
        "{name} 최대주주 변경 지연으로 불확실성 확대",
        ["CORPORATE_ACTION", "RISK"],
        "NEGATIVE",
        "MEDIUM",
    ),
    (
        "{name} 타법인주식및출자증권취득결정",
        ["CORPORATE_ACTION", "DISCLOSURE"],
        "NEUTRAL",
        "HIGH",
    ),
    (
        "{name} 타법인주식및출자증권처분결정",
        ["CORPORATE_ACTION", "DISCLOSURE"],
        "NEUTRAL",
        "HIGH",
    ),
    (
        "{name} 주요사항보고서 회사합병결정",
        ["CORPORATE_ACTION", "DISCLOSURE"],
        "NEUTRAL",
        "HIGH",
    ),
    ("{name} 횡령 배임 혐의 발생으로 거래정지 가능성", ["RISK"], "NEGATIVE", "CRITICAL"),
    (
        "{name} 횡령ㆍ배임사실확인 자회사의 주요경영사항",
        ["RISK", "DISCLOSURE"],
        "NEGATIVE",
        "CRITICAL",
    ),
    ("{name} 감사의견 거절로 상장폐지 사유 발생", ["RISK", "DISCLOSURE"], "NEGATIVE", "CRITICAL"),
    ("{name} 불성실공시법인 지정 예고", ["RISK", "DISCLOSURE"], "NEGATIVE", "CRITICAL"),
    ("{name} 주요 소송 패소 가능성으로 충당금 부담 확대", ["RISK"], "NEGATIVE", "HIGH"),
    (
        "{name} 소송등의제기ㆍ신청 일정금액이상의청구",
        ["RISK", "DISCLOSURE"],
        "NEGATIVE",
        "CRITICAL",
    ),
    ("{name} 소송등의판결ㆍ결정", ["RISK", "DISCLOSURE"], "NEGATIVE", "HIGH"),
    ("{name} 거래정지 사유 발생 공시", ["RISK", "DISCLOSURE"], "NEGATIVE", "CRITICAL"),
    (
        "{name} 주권매매거래정지기간변경 상장폐지사유발생",
        ["RISK", "DISCLOSURE"],
        "NEGATIVE",
        "CRITICAL",
    ),
    ("{name} 정기보고서 제출 일정 안내", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 임원ㆍ주요주주 소유상황 보고서 제출", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 임원ㆍ주요주주특정증권등소유상황보고서", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 주주총회소집공고", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 임시주주총회결과", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 주주총회소집결의 임시주주총회", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 주식등의대량보유상황보고서", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 최대주주등소유주식변동신고서", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 기업설명회 IR 개최 안내", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 감사보고서제출", ["DISCLOSURE"], "NEUTRAL", "LOW"),
    ("{name} 조회공시 요구 답변 제출", ["DISCLOSURE"], "NEUTRAL", "MEDIUM"),
    ("{name} 대규모 신규 투자계획 공시", ["DISCLOSURE"], "POSITIVE", "HIGH"),
    ("{name} 대규모 투자 계획 공시로 중장기 성장성 부각", ["DISCLOSURE"], "POSITIVE", "HIGH"),
    ("{name} 설비투자 확대 계획 공시로 미래 성장동력 강화", ["DISCLOSURE"], "POSITIVE", "HIGH"),
    ("{name} 신사업 투자계획 공시 제출로 성장 기대 확대", ["DISCLOSURE"], "POSITIVE", "HIGH"),
    ("{name} 투자계획 정정 공시에도 성장성 전망 유지", ["DISCLOSURE"], "POSITIVE", "MEDIUM"),
    ("환율 상승으로 {sector} 수출 기업 수익성 개선 기대", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("원화 약세로 {sector} 수출주 실적 기대감 확대", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("원화 약세 수혜로 {sector} 업종 매출 개선 전망", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("금리 인상 부담으로 {sector} 업종 투자심리 위축", ["MACRO"], "NEGATIVE", "MEDIUM"),
    ("코스피 외국인 순매수 전환에 {name} 관심 확대", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("금융 투자 확대 정책으로 {name} 성장 기대", ["MACRO"], "POSITIVE", "MEDIUM"),
    ("금리와 환율 변동으로 {sector} 업종 변동성 확대", ["MACRO"], "NEUTRAL", "MEDIUM"),
    ("코스피 변동성 확대에 {name} 주가 흐름 관망", ["MACRO"], "NEUTRAL", "MEDIUM"),
    ("외국인 수급 변화로 {sector} 업종 등락 반복", ["MACRO"], "NEUTRAL", "MEDIUM"),
    ("{sector} 업황 부진과 수출 둔화로 실적 하향 전망", ["EARNINGS", "MACRO"], "NEGATIVE", "HIGH"),
    ("{name} {sector} 업황 부진으로 실적 하향 전망", ["EARNINGS", "MACRO"], "NEGATIVE", "HIGH"),
    ("원화 약세와 수출 둔화로 {sector} 업종 투자심리 위축", ["MACRO"], "NEGATIVE", "MEDIUM"),
    ("해외 공급계약 체결로 {sector} 수출 증가 기대", ["CONTRACT", "MACRO"], "POSITIVE", "HIGH"),
    ("{name} 단기 주가 변동성 확대 전망", ["GENERAL_MARKET"], "NEUTRAL", "MEDIUM"),
    ("{name} 외국인 매도세로 단기 조정 압력", ["GENERAL_MARKET"], "NEGATIVE", "MEDIUM"),
    ("{name} 기관 순매수 유입으로 주가 반등 기대", ["GENERAL_MARKET"], "POSITIVE", "MEDIUM"),
    ("{name} 거래량 증가 속 주가 등락 반복", ["GENERAL_MARKET"], "NEUTRAL", "MEDIUM"),
]

SNIPPETS = [
    "외국인 투자자는 공시와 뉴스 원문을 확인해야 한다.",
    "시장 변동성이 커져 보유자와 관심 종목 등록자에게 알림이 필요하다.",
    "현지 투자자는 한국어 원문 이해가 어려워 요약 정보가 중요하다.",
]


def main() -> None:
    rows = []
    for (code, name, sector), (template, tags, sentiment, importance), snippet in product(
        STOCKS,
        TEMPLATES,
        SNIPPETS,
    ):
        source_type = "DISCLOSURE" if "DISCLOSURE" in tags else "NEWS"
        has_stock_reference = "{name}" in template
        rows.append(
            {
                "text": f"{template.format(name=name, sector=sector)}. {snippet}",
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
    print(json.dumps({"augmented_count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
