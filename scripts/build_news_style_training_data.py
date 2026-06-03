import json
from itertools import product
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data/training/financial_alert_news_style_augmented.jsonl"

STOCKS = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("009450", "경동나비엔"),
    ("000270", "기아"),
    ("005380", "현대차"),
    ("329180", "HD현대중공업"),
    ("034020", "두산에너빌리티"),
    ("066570", "LG전자"),
]

SUFFIXES = [
    "외국인 투자자 관심이 커지고 있다",
    "증권가가 목표주가와 실적 전망을 다시 점검하고 있다",
    "보유자와 watchlist 등록자가 확인할 필요가 있다",
    "시장 변동성이 커진 가운데 단기 반응이 주목된다",
]

TEMPLATES = [
    {
        "texts": [
            "코스피 외국인 순매수 전환으로 {stock} 수급 개선",
            "외국인 매수세 유입에 {stock} 수급 여건 개선",
            "환율 안정과 외국인 순매수에 {stock} 투자심리 회복",
            "코스피 수급 개선 속 {stock} 외국인 매수세 부각",
        ],
        "tags": ["MACRO"],
        "sentiment": "POSITIVE",
        "importance": "MEDIUM",
    },
    {
        "texts": [
            "{stock} 2분기 영업이익 개선 기대…턴어라운드 시동",
            "{stock} 판매실적 반등에 수익성 회복 전망",
            "{stock} 호황에 매출 증가세 지속…실적 눈높이 상향",
            "{stock} 비용 부담 완화로 분기 실적 개선 가능성",
            "{stock} AI 부품 호황에 몸값 들썩…실적 기대 확대",
            "{stock} 출하 충격 끝나고 턴어라운드 기대감 부각",
        ],
        "tags": ["EARNINGS"],
        "sentiment": "POSITIVE",
        "importance": "MEDIUM",
    },
    {
        "texts": [
            "{stock} 판매실적 감소…수익성 부담 확대",
            "{stock} 비용 증가로 영업이익 둔화 우려",
            "{stock} 출하 물량 급감 충격에 실적 회복 지연",
            "{stock} 목표주가 하향…분기 실적 부진 전망",
        ],
        "tags": ["EARNINGS"],
        "sentiment": "NEGATIVE",
        "importance": "MEDIUM",
    },
    {
        "texts": [
            "{stock} 대형 수주 목표 조기 달성…공급계약 기대",
            "{stock} 해외 고객사와 장기 공급계약 체결 전망",
            "{stock} 신규 수주 증가로 하반기 매출 가시성 확대",
            "{stock} 공급계약 물량 확대에 주가 반등 기대",
        ],
        "tags": ["CONTRACT"],
        "sentiment": "POSITIVE",
        "importance": "HIGH",
    },
    {
        "texts": [
            "{stock} 기존 공급계약 해지 우려…매출 공백 가능성",
            "{stock} 수주 지연에 실적 변동성 확대",
            "{stock} 납품 일정 차질로 공급계약 리스크 부각",
            "{stock} 주요 고객사 발주 축소 가능성에 투자심리 위축",
            "{stock} 수주 목표 미달 우려…하반기 매출 불확실성 확대",
        ],
        "tags": ["CONTRACT", "RISK"],
        "sentiment": "NEGATIVE",
        "importance": "HIGH",
    },
    {
        "texts": [
            "{stock} 자사주 매입 검토…주주환원 기대 확대",
            "{stock} 배당 확대 가능성에 주주가치 제고 기대",
            "{stock} 시가총액 급증에 배당·자사주 기대 부각",
        ],
        "tags": ["CAPITAL_ACTION"],
        "sentiment": "POSITIVE",
        "importance": "HIGH",
    },
    {
        "texts": [
            "{stock} 유상증자 자금으로 재무구조 개선 추진",
            "{stock} 대규모 자금 수혈로 재무개선 도화선 마련",
            "{stock} 전환사채 발행으로 운영자금 확보",
            "{stock} 자본확충 계획에 재무 안정성 개선 기대",
        ],
        "tags": ["CAPITAL_ACTION"],
        "sentiment": "NEUTRAL",
        "importance": "HIGH",
    },
    {
        "texts": [
            "{stock} 회사합병 추진…사업재편 속도",
            "{stock} 핵심 자회사 지분취득 검토…성장축 강화",
            "{stock} 비핵심 계열사 지분처분으로 재무 여력 개선",
            "{stock} 비핵심 자회사 매각으로 재무 여력 개선",
            "{stock} 회사분할 가능성에 지배구조 개편 주목",
            "{stock} 해외 법인 인수 추진…신사업 확장 기대",
            "{stock} 사업부 매각 검토…구조조정 본격화",
        ],
        "tags": ["CORPORATE_ACTION"],
        "sentiment": "POSITIVE",
        "importance": "MEDIUM",
    },
    {
        "texts": [
            "{stock} 회계장부 열람 가처분 신청…지배구조 리스크 부각",
            "{stock} 노사협상 안갯속…생산 차질 우려",
            "{stock} 소송 가능성에 투자심리 위축",
            "{stock} 평판 리스크 확대…관리 체계 도마 위",
            "{stock} 투자 경고성 리포트 확산…주가 변동성 주의",
            "{stock} 고액 보상 갈등 복병…임단협 타결 안갯속",
        ],
        "tags": ["RISK"],
        "sentiment": "NEGATIVE",
        "importance": "HIGH",
    },
    {
        "texts": [
            "{stock} 상장폐지 우려에 거래정지 가능성 확대",
            "{stock} 감사의견 거절 가능성에 투자자 피해 우려",
            "{stock} 횡령·배임 의혹 확산…내부통제 치명상",
            "{stock} 주권매매거래정지 장기화 가능성 부각",
            "{stock} 대규모 소송 패소 가능성에 재무위험 급등",
            "{stock} 관리종목 지정 우려에 상장 유지 불확실성 확대",
        ],
        "tags": ["RISK"],
        "sentiment": "NEGATIVE",
        "importance": "CRITICAL",
    },
    {
        "texts": [
            "{stock} 판매 감소에도 해외 성장세로 실적 평가 엇갈려",
            "{stock} 업황 둔화와 신시장 확장이 맞물리며 전망 혼조",
            "{stock} 업계 판매 감소에도 일부 지역 성장세로 평가 엇갈려",
            "{stock} 판매 감소와 해외 확장이 동시에 나타나며 실적 해석 분분",
            "{stock} 주가 급등 이후 변동성 주의…추가 상승 여력은 남아",
            "{stock} 목표주가 상회 후 차익 실현 가능성도 거론",
        ],
        "tags": ["EARNINGS"],
        "sentiment": "NEUTRAL",
        "importance": "MEDIUM",
    },
]

MARKET_TEMPLATES = [
    (
        ["GENERAL_MARKET"],
        "POSITIVE",
        "MEDIUM",
        "코스피 목표치 상향…강한 실적 모멘텀에 증시 기대감 확대",
    ),
    (
        ["GENERAL_MARKET"],
        "POSITIVE",
        "MEDIUM",
        "코스피 사상 최고치 경신…반도체와 AI 업종이 랠리 주도",
    ),
    (
        ["GENERAL_MARKET"],
        "POSITIVE",
        "MEDIUM",
        "미 증시 내려도 반도체는 올랐다…국내 대형주 향배 주목",
    ),
    (["GENERAL_MARKET"], "POSITIVE", "LOW", "ETF 500조 시대…1조 클럽 상품도 빠르게 증가"),
    (
        ["GENERAL_MARKET", "RISK"],
        "NEUTRAL",
        "HIGH",
        "코스피 급등에도 빚투와 레버리지 ETF 과열 경고",
    ),
    (
        ["GENERAL_MARKET", "RISK"],
        "NEUTRAL",
        "HIGH",
        "AI 투자 상투 논란에도 지수 상승…빚투 경계 필요",
    ),
    (
        ["GENERAL_MARKET", "RISK"],
        "NEUTRAL",
        "HIGH",
        "AI 투자 아직 유효하지만 빚투는 경계해야 한다는 분석",
    ),
    (["GENERAL_MARKET", "RISK"], "NEUTRAL", "HIGH", "종목 급등에도 변동성 주의…단기 과열 경계"),
    (
        ["GENERAL_MARKET", "RISK"],
        "NEGATIVE",
        "MEDIUM",
        "코스피 뛰었지만 업종별 디커플링 확대…쏠림 장세 주의",
    ),
    (["GENERAL_MARKET"], "NEUTRAL", "MEDIUM", "지방선거 이후 증시 향방과 과세 개편에 시장 관심"),
    (
        ["GENERAL_MARKET", "MACRO"],
        "NEUTRAL",
        "MEDIUM",
        "코스피와 환율 동행 장세…외환 지표 점검 필요",
    ),
    (["GENERAL_MARKET"], "NEUTRAL", "LOW", "ETF 시장 500조 시대…자금 흐름 다변화"),
    (["GENERAL_MARKET"], "NEUTRAL", "LOW", "반도체 랠리 이후 업종 순환 가능성 주목"),
    (["GENERAL_MARKET"], "NEUTRAL", "LOW", "기자의 눈으로 본 업종 순환…바이오 후속 주도주 가능성"),
]

MACRO_TEMPLATES = [
    (["MACRO"], "NEUTRAL", "MEDIUM", "환율 1500원대 지속…수출기업 환리스크 관리 부각"),
    (["MACRO", "RISK"], "NEGATIVE", "HIGH", "환율 1500원 뉴노멀 우려…산업군별 지각변동 가능성"),
    (["MACRO", "RISK"], "NEGATIVE", "HIGH", "고환율 뉴노멀 가능성에 산업별 비용 부담 우려"),
    (["MACRO", "RISK"], "NEGATIVE", "HIGH", "고물가·고유가에 고환율까지 지속…기업 비용 부담 확대"),
    (["MACRO"], "NEUTRAL", "HIGH", "한은 기준금리 동결…향후 인상 가능성은 열어둬"),
    (["MACRO"], "NEGATIVE", "HIGH", "한은총재 금리인상 시사…증시와 부동산 부담 확대"),
    (["MACRO"], "NEUTRAL", "HIGH", "성장률 전망 상향에도 중동 리스크와 반도체 변수 안갯속"),
    (["MACRO"], "POSITIVE", "MEDIUM", "반도체 수출 호조에 한국 성장률 전망 상향"),
    (["MACRO", "RISK"], "NEGATIVE", "HIGH", "관세 예고에 한국 수출기업 비상…공급망 리스크 확대"),
    (["MACRO", "RISK"], "NEGATIVE", "HIGH", "강제노동 판정과 관세 예고에 수출기업 비상"),
    (["MACRO", "RISK"], "NEGATIVE", "MEDIUM", "중동 리스크에 물류비 급등…수출기업 부담 가중"),
    (["MACRO"], "NEUTRAL", "LOW", "환율 변동 대응 교육 확대…수출입 아카데미 개최"),
    (["CONTRACT"], "POSITIVE", "MEDIUM", "엔비디아 협력 기대 속 공급 안정화 기업 주목"),
    (["CONTRACT"], "POSITIVE", "MEDIUM", "새 협력사 후보 부각…공급망 안정화 기대"),
]


def main() -> None:
    rows: list[dict[str, str | list[str]]] = []
    for template in TEMPLATES:
        for (stock_code, stock_name), text, suffix in product(
            STOCKS,
            template["texts"],
            SUFFIXES,
        ):
            rows.append(
                {
                    "text": f"{text.format(stock=stock_name)}. {suffix}",
                    "tags": template["tags"],
                    "sentiment": template["sentiment"],
                    "importance": template["importance"],
                    "source_type": "NEWS",
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                }
            )

    for tags, sentiment, importance, text in [*MARKET_TEMPLATES, *MACRO_TEMPLATES]:
        for suffix in SUFFIXES:
            rows.append(
                {
                    "text": f"{text}. {suffix}",
                    "tags": tags,
                    "sentiment": sentiment,
                    "importance": importance,
                    "source_type": "NEWS",
                }
            )

    OUTPUT_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({"path": str(OUTPUT_PATH), "count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
