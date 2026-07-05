import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.domain.schemas import SummaryLines
from hannah_montana_ai.services.news_summary_generator import (
    NEWS_SUMMARY_PROMPT_VERSION,
    NewsSummaryContext,
    NewsSummaryGenerator,
)

DEFAULT_OUTPUT_PATH = Path("data/training/news_summary_wwi_sft.jsonl")
DEFAULT_REPORT_PATH = Path("reports/news-summary-qwen3-readiness.json")


@dataclass(frozen=True)
class NewsSummaryCase:
    case_id: str
    source_type: str
    title: str
    snippet: str
    content: str
    event_tags: tuple[str, ...]
    importance: str
    sentiment: str
    stock_code: str | None
    stock_name: str | None
    stock_name_en: str
    target: SummaryLines


CASES = (
    NewsSummaryCase(
        case_id="samsung_hbm_recovery",
        source_type="NEWS",
        title="삼성전자, AI 서버 투자 확대에 반도체 실적 회복 기대",
        snippet="HBM 수요와 메모리 가격 반등이 실적 회복의 배경으로 꼽힌다.",
        content=(
            "삼성전자는 AI 서버 투자 확대로 HBM과 메모리 수요가 늘며 반도체 실적 "
            "회복 기대가 커졌다. 메모리 가격 반등과 주요 고객사의 데이터센터 투자가 "
            "이번 회복의 핵심 배경으로 거론된다. 투자자는 영업이익 회복 속도와 "
            "고부가 제품 비중 확대 여부를 확인해야 한다."
        ),
        event_tags=("EARNINGS",),
        importance="HIGH",
        sentiment="POSITIVE",
        stock_code="005930",
        stock_name="삼성전자",
        stock_name_en="Samsung Electronics",
        target=SummaryLines(
            what=(
                "Samsung Electronics said AI-server investment is lifting semiconductor "
                "earnings expectations."
            ),
            why="The article cites stronger HBM demand and a rebound in memory prices as drivers.",
            impact=(
                "The investor impact is to track operating-profit recovery speed and "
                "the mix of high-value memory products."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="sk_hynix_market_cap",
        source_type="NEWS",
        title="SK하이닉스, HBM 수요에 시가총액 1위 등극",
        snippet="외국인 순매수와 HBM 공급 우위가 주가 상승 배경으로 거론된다.",
        content=(
            "SK하이닉스는 AI 인프라 투자 확대의 최대 수혜 기업으로 평가받으며 "
            "시가총액 1위에 올라섰다. HBM 공급 우위와 메모리 반도체 수요 증가가 "
            "주가 상승의 핵심 배경이다. 외국인 투자자의 순매수가 이어지며 시장 "
            "쏠림 현상도 커지고 있다."
        ),
        event_tags=("EARNINGS", "GENERAL_MARKET"),
        importance="HIGH",
        sentiment="POSITIVE",
        stock_code="000660",
        stock_name="SK하이닉스",
        stock_name_en="SK hynix",
        target=SummaryLines(
            what="SK hynix became Korea's largest company by market cap on HBM demand.",
            why=(
                "The article links the rally to memory-chip demand and foreign-investor "
                "net buying."
            ),
            impact=(
                "The investor impact is heightened sensitivity to memory prices and "
                "large-cap semiconductor flows."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="kospi_institutional_rebound",
        source_type="NEWS",
        title="코스피, 기관 매수세에 장중 7800선 회복",
        snippet="반도체주를 중심으로 기관 자금이 유입되며 지수가 반등했다.",
        content=(
            "코스피가 장중 기관의 대규모 매수세에 힘입어 상승 전환하며 7800선을 "
            "회복했다. 장 초반 미국 기술주 약세 영향으로 밀렸지만 반도체주를 "
            "중심으로 기관 자금이 유입되면서 분위기가 반전됐다. 외국인은 "
            "순매도했지만 기관 순매수가 지수 반등을 이끌었다."
        ),
        event_tags=("GENERAL_MARKET",),
        importance="MEDIUM",
        sentiment="POSITIVE",
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        target=SummaryLines(
            what="KOSPI recovered the 7,800 level intraday on institutional net buying.",
            why=(
                "The article says semiconductor inflows offset early weakness from "
                "US technology shares."
            ),
            impact=(
                "The investor impact is a market rebound still dependent on semiconductor "
                "leadership and foreign flows."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="lg_energy_battery_order",
        source_type="NEWS",
        title="LG에너지솔루션, 북미 배터리 공급계약 확대",
        snippet="전기차 고객사의 장기 발주가 매출 가시성을 높였다는 평가가 나온다.",
        content=(
            "LG에너지솔루션은 북미 전기차 고객사와 배터리 장기 공급계약을 확대했다. "
            "현지 생산능력 증설과 고객사의 전기차 플랫폼 전환이 계약 확대의 배경이다. "
            "시장에서는 중장기 매출 가시성이 높아졌지만 원재료 가격과 환율 변동성은 "
            "계속 점검해야 한다고 봤다."
        ),
        event_tags=("CONTRACT",),
        importance="HIGH",
        sentiment="POSITIVE",
        stock_code="373220",
        stock_name="LG에너지솔루션",
        stock_name_en="LG Energy Solution",
        target=SummaryLines(
            what="LG Energy Solution expanded long-term battery supply contracts in North America.",
            why=(
                "The article points to local capacity expansion and customer "
                "EV-platform transitions."
            ),
            impact=(
                "The investor impact is better revenue visibility with continued exposure "
                "to raw-material and currency volatility."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="hanwha_aerospace_defense",
        source_type="NEWS",
        title="한화에어로스페이스, 중동 방산 수주 기대 확대",
        snippet="국방 예산 증액과 수출 협상이 주가 상승 배경으로 꼽힌다.",
        content=(
            "한화에어로스페이스는 중동 방산 수요 확대에 따라 수주 기회가 늘고 있다. "
            "국방 예산 증액과 현지 정부의 무기체계 현대화가 주요 배경으로 거론된다. "
            "투자자는 실제 계약 체결 시점과 영업이익 기여 규모를 확인해야 한다."
        ),
        event_tags=("CONTRACT",),
        importance="HIGH",
        sentiment="POSITIVE",
        stock_code="012450",
        stock_name="한화에어로스페이스",
        stock_name_en="Hanwha Aerospace",
        target=SummaryLines(
            what="Hanwha Aerospace is seeing stronger expectations for Middle East defense orders.",
            why="The article cites larger defense budgets and modernization demand as drivers.",
            impact=(
                "The investor impact is to track contract timing and the contribution "
                "to operating profit."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="samsung_buyback_disclosure",
        source_type="DISCLOSURE",
        title="삼성전자, 14조5800억원 규모 자사주 소각 결정",
        snippet="주주환원 정책 강화 목적의 자기주식 소각 공시가 나왔다.",
        content=(
            "삼성전자는 14조5800억원 규모 자사주 소각을 결정했다고 공시했다. "
            "회사는 주주환원 정책 강화와 자본 효율성 제고가 이번 결정의 목적이라고 "
            "설명했다. 투자자는 실제 소각 일정과 주당 가치 변화, 추가 주주환원 "
            "가능성을 확인해야 한다."
        ),
        event_tags=("CAPITAL_ACTION",),
        importance="HIGH",
        sentiment="POSITIVE",
        stock_code="005930",
        stock_name="삼성전자",
        stock_name_en="Samsung Electronics",
        target=SummaryLines(
            what="Samsung Electronics disclosed a KRW 14.58 trillion treasury-share cancellation.",
            why=(
                "The filing says the decision is meant to strengthen shareholder "
                "returns and capital efficiency."
            ),
            impact=(
                "The investor impact is to track the cancellation schedule and per-share "
                "value effects."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="capital_increase_financing",
        source_type="DISCLOSURE",
        title="한화솔루션, 유상증자로 운영자금 확보 추진",
        snippet="신주 발행을 통한 재무구조 개선 계획이 공시됐다.",
        content=(
            "한화솔루션은 유상증자를 통해 운영자금과 시설투자 자금을 확보한다고 공시했다. "
            "회사는 차입 부담을 낮추고 신사업 투자를 이어가기 위한 자본확충이라고 설명했다. "
            "시장에서는 재무 안정성 개선 기대와 기존 주주 지분 희석 우려가 동시에 제기됐다."
        ),
        event_tags=("CAPITAL_ACTION", "RISK"),
        importance="HIGH",
        sentiment="NEUTRAL",
        stock_code="009830",
        stock_name="한화솔루션",
        stock_name_en="Hanwha Solutions",
        target=SummaryLines(
            what="Hanwha Solutions disclosed a capital increase to fund operations and facilities.",
            why=(
                "The company says the share issuance supports debt reduction and "
                "new-business investment."
            ),
            impact=(
                "The investor impact is a trade-off between balance-sheet improvement "
                "and shareholder dilution risk."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="trading_halt_delisting",
        source_type="DISCLOSURE",
        title="레드우즈, 상장폐지 사유 발생으로 거래정지 기간 변경",
        snippet="감사의견 거절에 따른 상장 유지 리스크가 부각됐다.",
        content=(
            "레드우즈는 감사의견 거절로 상장폐지 사유가 발생했다고 공시했다. "
            "거래소는 주권 매매거래정지 기간을 변경하고 개선계획 제출 여부를 확인할 예정이다. "
            "투자자는 거래 재개 가능성과 정리매매 절차, 상장 유지 조건을 점검해야 한다."
        ),
        event_tags=("RISK",),
        importance="CRITICAL",
        sentiment="NEGATIVE",
        stock_code="123456",
        stock_name="레드우즈",
        stock_name_en="Redwoods",
        target=SummaryLines(
            what="Redwoods disclosed a delisting trigger after an adverse audit opinion.",
            why=(
                "The exchange changed the trading-halt period while it reviews the "
                "company's remediation plan."
            ),
            impact=(
                "The investor impact is severe liquidity risk tied to trading resumption "
                "and delisting procedures."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="exchange_rate_exporters",
        source_type="NEWS",
        title="환율 1500원대 지속에 수출기업 비용 부담 확대",
        snippet="고환율이 원재료와 달러 부채 부담을 키운다는 분석이 나왔다.",
        content=(
            "원달러 환율이 1500원대에서 머물면서 수출기업의 비용 부담이 커지고 있다. "
            "달러 표시 원재료와 외화 부채 비중이 높은 기업은 환율 상승에 따른 손익 "
            "변동성이 커질 수 있다. 시장에서는 반도체와 조선 등 수출 업종의 가격 전가력과 "
            "헤지 전략을 확인해야 한다고 봤다."
        ),
        event_tags=("MACRO", "RISK"),
        importance="HIGH",
        sentiment="NEGATIVE",
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        target=SummaryLines(
            what=(
                "Korean exporters face rising cost pressure as the exchange rate stays "
                "near KRW 1,500."
            ),
            why=(
                "The article cites dollar-priced inputs and foreign-currency debt as "
                "sources of volatility."
            ),
            impact=(
                "The investor impact is greater focus on pricing power and currency-hedging "
                "policies by sector."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="hyundai_ev_sales",
        source_type="NEWS",
        title="현대차, 전기차 판매 반등에 수익성 개선 기대",
        snippet="미국 보조금 개편 이후 신차 판매 흐름이 회복되고 있다.",
        content=(
            "현대차는 전기차 판매 반등과 하이브리드 수요 증가로 수익성 개선 기대가 커졌다. "
            "미국 보조금 개편 이후 신차 출시 효과가 나타나고 환율도 수출 채산성에 우호적으로 "
            "작용했다. 투자자는 판매 믹스와 인센티브 비용, 영업이익률 변화를 확인해야 한다."
        ),
        event_tags=("EARNINGS",),
        importance="MEDIUM",
        sentiment="POSITIVE",
        stock_code="005380",
        stock_name="현대차",
        stock_name_en="Hyundai Motor",
        target=SummaryLines(
            what="Hyundai Motor is expected to improve profitability as EV sales rebound.",
            why=(
                "The article cites new-model effects, subsidy changes, and a supportive "
                "exchange rate."
            ),
            impact=(
                "The investor impact is to watch the sales mix, incentive costs, "
                "and operating-margin trend."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="naver_ai_cost",
        source_type="NEWS",
        title="NAVER, AI 인프라 투자 확대에 비용 부담 우려",
        snippet="데이터센터와 생성형 AI 서비스 투자가 단기 수익성을 압박하고 있다.",
        content=(
            "NAVER는 생성형 AI 서비스와 데이터센터 투자를 확대하면서 비용 부담 우려가 커졌다. "
            "클라우드 인프라와 연구개발 비용이 늘어 단기 영업이익률을 압박할 수 있다는 분석이다. "
            "다만 AI 검색과 광고 효율 개선이 중장기 성장 동력으로 평가된다."
        ),
        event_tags=("EARNINGS", "RISK"),
        importance="MEDIUM",
        sentiment="NEUTRAL",
        stock_code="035420",
        stock_name="NAVER",
        stock_name_en="NAVER",
        target=SummaryLines(
            what=(
                "NAVER faces cost concerns as it expands generative-AI and "
                "data-center investment."
            ),
            why=(
                "The article says cloud infrastructure and research spending may "
                "pressure near-term margins."
            ),
            impact=(
                "The investor impact is a balance between margin pressure and longer-term "
                "AI advertising upside."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="kakao_litigation",
        source_type="NEWS",
        title="카카오, 플랫폼 규제와 소송 리스크에 투자심리 위축",
        snippet="과징금 가능성과 지배구조 논란이 주가 변동성을 키우고 있다.",
        content=(
            "카카오는 플랫폼 규제와 소송 리스크가 겹치며 투자심리가 위축됐다. "
            "공정거래 조사와 과징금 가능성, 지배구조 논란이 주가 변동성을 키우는 배경이다. "
            "시장에서는 규제 결과와 비용 반영 시점, 주요 서비스 성장률을 확인해야 한다고 봤다."
        ),
        event_tags=("RISK",),
        importance="HIGH",
        sentiment="NEGATIVE",
        stock_code="035720",
        stock_name="카카오",
        stock_name_en="Kakao",
        target=SummaryLines(
            what="Kakao's investor sentiment weakened on platform regulation and litigation risk.",
            why="The article cites antitrust probes, possible fines, and governance controversy.",
            impact=(
                "The investor impact is higher stock-price volatility until regulatory "
                "costs and service growth become clearer."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="celltrion_biosimilar",
        source_type="NEWS",
        title="셀트리온, 바이오시밀러 허가 기대에 실적 눈높이 상향",
        snippet="미국 판매 승인 가능성과 원가율 개선이 긍정적으로 평가됐다.",
        content=(
            "셀트리온은 신규 바이오시밀러의 미국 허가 기대가 커지며 실적 눈높이가 높아졌다. "
            "판매 승인 가능성과 생산 효율 개선, 원가율 하락이 수익성 개선의 배경으로 거론된다. "
            "투자자는 실제 허가 시점과 미국 처방 확대 속도를 확인해야 한다."
        ),
        event_tags=("EARNINGS",),
        importance="MEDIUM",
        sentiment="POSITIVE",
        stock_code="068270",
        stock_name="셀트리온",
        stock_name_en="Celltrion",
        target=SummaryLines(
            what="Celltrion's earnings expectations rose on a potential US biosimilar approval.",
            why=(
                "The article cites approval prospects, production efficiency, and "
                "lower cost ratios."
            ),
            impact=(
                "The investor impact is to track approval timing and the pace of US "
                "prescription growth."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="hd_shipbuilding_orders",
        source_type="NEWS",
        title="HD현대중공업, LNG선 수주 증가로 매출 가시성 확대",
        snippet="고부가 선박 발주와 선가 상승이 조선 업황 개선을 이끌고 있다.",
        content=(
            "HD현대중공업은 LNG선 수주 증가로 매출 가시성이 확대됐다는 평가를 받았다. "
            "고부가 선박 발주와 선가 상승, 노후 선박 교체 수요가 업황 개선의 배경이다. "
            "투자자는 수주잔고의 이익 전환 시점과 원가 부담 변화를 확인해야 한다."
        ),
        event_tags=("CONTRACT", "EARNINGS"),
        importance="HIGH",
        sentiment="POSITIVE",
        stock_code="329180",
        stock_name="HD현대중공업",
        stock_name_en="HD Hyundai Heavy Industries",
        target=SummaryLines(
            what=(
                "HD Hyundai Heavy Industries gained better revenue visibility from "
                "more LNG-carrier orders."
            ),
            why=(
                "The article points to high-value vessel demand, higher ship prices, "
                "and replacement demand."
            ),
            impact=(
                "The investor impact is to monitor when the order backlog converts into earnings."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="foreign_net_selling_market",
        source_type="NEWS",
        title="외국인 순매도에 코스피 하락, 반도체 대형주 약세",
        snippet="달러 강세와 미국 금리 부담이 외국인 수급을 압박했다.",
        content=(
            "코스피는 외국인 순매도에 하락 마감했고 반도체 대형주가 약세를 보였다. "
            "달러 강세와 미국 금리 부담이 위험자산 선호를 낮추며 외국인 수급을 압박했다. "
            "시장에서는 환율과 금리 방향에 따라 대형주 변동성이 커질 수 있다고 봤다."
        ),
        event_tags=("GENERAL_MARKET", "MACRO"),
        importance="MEDIUM",
        sentiment="NEGATIVE",
        stock_code=None,
        stock_name=None,
        stock_name_en="",
        target=SummaryLines(
            what="KOSPI fell as foreign investors sold large semiconductor stocks.",
            why="The article links the selling to dollar strength and US interest-rate pressure.",
            impact=(
                "The investor impact is higher large-cap volatility tied to exchange-rate "
                "and rate moves."
            ),
        ),
    ),
    NewsSummaryCase(
        case_id="kb_financial_dividend",
        source_type="NEWS",
        title="KB금융, 배당 확대 기대에 은행주 투자심리 개선",
        snippet="자본비율 안정과 주주환원 정책이 배당 여력을 높였다는 평가다.",
        content=(
            "KB금융은 배당 확대 기대가 커지며 은행주 투자심리 개선을 이끌었다. "
            "안정적인 자본비율과 주주환원 정책 강화가 배당 여력을 높이는 배경으로 꼽혔다. "
            "투자자는 대손비용과 금리 하락이 순이자마진에 미치는 영향을 함께 확인해야 한다."
        ),
        event_tags=("CAPITAL_ACTION", "EARNINGS"),
        importance="MEDIUM",
        sentiment="POSITIVE",
        stock_code="105560",
        stock_name="KB금융",
        stock_name_en="KB Financial Group",
        target=SummaryLines(
            what=(
                "KB Financial Group improved bank-stock sentiment on dividend "
                "expansion expectations."
            ),
            why="The article cites stable capital ratios and stronger shareholder-return policies.",
            impact=(
                "The investor impact is to balance dividend upside against credit costs "
                "and net-interest-margin pressure."
            ),
        ),
    ),
)

VARIANTS = (
    ("plain", "{title}", "{snippet}", "{content}"),
    ("snippet_ellipsis", "{title}", "{snippet}...", "{content}"),
    ("breaking_prefix", "[속보] {title}", "{snippet}", "{content}"),
    ("feature_prefix", "[특징주] {title}", "{snippet}", "{content}"),
    (
        "navigation_cleaned",
        "{title}",
        "{snippet}",
        "로그인 회원가입 전체 메뉴 열기 검색 열기. {content} 최신 기사 오늘의 증시일정.",
    ),
    (
        "byline_cleaned",
        "{title}",
        "{snippet}",
        "이석호 기자 {content} 관련기사 추천 키워드 많이 본 뉴스.",
    ),
    (
        "market_tail",
        "{title}",
        "{snippet}",
        "{content} 코스피와 코스닥 주요 지수는 장중 변동성을 보였다.",
    ),
    (
        "short_snippet",
        "{title}",
        "",
        "{content}",
    ),
)


def main() -> None:
    args = _parse_args()
    rows = build_dataset()
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = _build_report(rows, args.output_path)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["quality_status"] != "pass":
        raise SystemExit(1)


def build_dataset() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in CASES:
        for variant_index, (
            variant_name,
            title_template,
            snippet_template,
            content_template,
        ) in enumerate(VARIANTS):
            context = _context_for_case(
                case,
                title_template=title_template,
                snippet_template=snippet_template,
                content_template=content_template,
            )
            rows.append(
                {
                    "case_id": case.case_id,
                    "sample_variant": variant_name,
                    "variant_index": variant_index,
                    **NewsSummaryGenerator.training_example(context, case.target),
                }
            )
    return rows


def _context_for_case(
    case: NewsSummaryCase,
    *,
    title_template: str,
    snippet_template: str,
    content_template: str,
) -> NewsSummaryContext:
    return NewsSummaryContext(
        title=title_template.format(title=case.title),
        snippet=snippet_template.format(snippet=case.snippet),
        content=content_template.format(content=case.content),
        source_type=case.source_type,  # type: ignore[arg-type]
        importance=case.importance,  # type: ignore[arg-type]
        sentiment=case.sentiment,  # type: ignore[arg-type]
        event_tags=list(case.event_tags),
        stock_code=case.stock_code,
        stock_name=case.stock_name,
        stock_name_en=case.stock_name_en,
        fallback=SummaryLines(
            what="원문은 해당 공시·뉴스 관련 최신 시장·기업 이벤트를 다룹니다.",
            why="해당 공시·뉴스의 배경은 원문에서 확인된 최신 시장·기업 이벤트입니다.",
            impact="투자자는 보유·관심 종목의 수급, 실적 전망, 변동성을 확인해야 합니다.",
        ),
    )


def _build_report(rows: list[dict[str, object]], output_path: Path) -> dict[str, object]:
    failure_rows = []
    for row in rows:
        target = row["target"]
        if not isinstance(target, dict):
            failure_rows.append({"case_id": row.get("case_id"), "reason": "target_not_object"})
            continue
        context_messages = row["messages"]
        if not isinstance(context_messages, list) or len(context_messages) < 2:
            failure_rows.append({"case_id": row.get("case_id"), "reason": "messages_missing"})
            continue
        if _target_has_bad_shape(target):
            failure_rows.append({"case_id": row.get("case_id"), "reason": "target_shape_failed"})

    return {
        "schema_version": "news-summary-qwen3-readiness/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_version": NEWS_SUMMARY_PROMPT_VERSION,
        "recommended_train_model": "Qwen/Qwen3-0.6B-MLX-4bit LoRA",
        "recommended_serving_model": "Qwen3-0.6B GGUF Q4",
        "dataset_path": str(output_path),
        "sample_count": len(rows),
        "case_count": len(CASES),
        "variant_count": len(VARIANTS),
        "target_failure_count": len(failure_rows),
        "target_failures": failure_rows[:20],
        "quality_status": "pass" if len(rows) >= 100 and not failure_rows else "fail",
    }


def _target_has_bad_shape(target: dict[str, object]) -> bool:
    for key in ("what", "why", "impact"):
        value = target.get(key)
        if not isinstance(value, str) or not value.strip():
            return True
        if "..." in value or "…" in value:
            return True
        if any("가" <= char <= "힣" for char in value):
            return True
        if value.count(".") > 1 and "KRW" not in value:
            return True
        if not value.endswith("."):
            return True
    return False


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Qwen3 news What/Why/Impact SFT data.")
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
