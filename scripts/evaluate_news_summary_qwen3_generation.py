import argparse
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hannah_montana_ai.domain.schemas import SummaryLines
from hannah_montana_ai.services.news_summary_generator import (
    NEWS_SUMMARY_PROMPT_VERSION,
    NewsSummaryContext,
    NewsSummaryGenerator,
)

DEFAULT_MODEL = "mlx-community/Qwen3-0.6B-4bit"
DEFAULT_ADAPTER_DIR = Path("src/hannah_montana_ai/model_store/news_summary_qwen3_lora")
DEFAULT_REPORT_PATH = Path("reports/news-summary-qwen3-generation-eval.json")

DEFAULT_EVAL_SAMPLES = (
    {
        "case_id": "samsung_hbm_recovery",
        "context": NewsSummaryContext(
            title="삼성전자, AI 서버 투자 확대에 반도체 실적 회복 기대",
            snippet="HBM 수요와 메모리 가격 반등이 실적 회복의 배경으로 꼽힌다.",
            content=(
                "삼성전자는 AI 서버 투자 확대로 HBM과 메모리 수요가 늘며 반도체 실적 "
                "회복 기대가 커졌다. 메모리 가격 반등과 주요 고객사의 데이터센터 투자가 "
                "이번 회복의 핵심 배경으로 거론된다. 투자자는 영업이익 회복 속도와 "
                "고부가 제품 비중 확대 여부를 확인해야 한다."
            ),
            source_type="NEWS",
            importance="HIGH",
            sentiment="POSITIVE",
            event_tags=["EARNINGS"],
            stock_code="005930",
            stock_name="삼성전자",
            stock_name_en="Samsung Electronics",
            fallback=SummaryLines(),
        ),
        "required_terms": ("Samsung Electronics", "HBM", "operating"),
    },
    {
        "case_id": "kospi_institutional_rebound",
        "context": NewsSummaryContext(
            title="코스피, 기관 매수세에 장중 7800선 회복",
            snippet="반도체주를 중심으로 기관 자금이 유입되며 지수가 반등했다.",
            content=(
                "코스피가 장중 기관의 대규모 매수세에 힘입어 상승 전환하며 7800선을 "
                "회복했다. 장 초반 미국 기술주 약세 영향으로 밀렸지만 반도체주를 "
                "중심으로 기관 자금이 유입되면서 분위기가 반전됐다. 외국인은 "
                "순매도했지만 기관 순매수가 지수 반등을 이끌었다."
            ),
            source_type="NEWS",
            importance="MEDIUM",
            sentiment="POSITIVE",
            event_tags=["GENERAL_MARKET"],
            stock_code=None,
            stock_name=None,
            stock_name_en="",
            fallback=SummaryLines(),
        ),
        "required_terms": ("KOSPI", "institutional", "semiconductor"),
    },
    {
        "case_id": "samsung_buyback_disclosure",
        "context": NewsSummaryContext(
            title="삼성전자, 14조5800억원 규모 자사주 소각 결정",
            snippet="주주환원 정책 강화 목적의 자기주식 소각 공시가 나왔다.",
            content=(
                "삼성전자는 14조5800억원 규모 자사주 소각을 결정했다고 공시했다. "
                "회사는 주주환원 정책 강화와 자본 효율성 제고가 이번 결정의 목적이라고 "
                "설명했다. 투자자는 실제 소각 일정과 주당 가치 변화, 추가 주주환원 "
                "가능성을 확인해야 한다."
            ),
            source_type="DISCLOSURE",
            importance="HIGH",
            sentiment="POSITIVE",
            event_tags=["CAPITAL_ACTION"],
            stock_code="005930",
            stock_name="삼성전자",
            stock_name_en="Samsung Electronics",
            fallback=SummaryLines(),
        ),
        "required_terms": ("Samsung Electronics", "treasury", "cancellation"),
    },
    {
        "case_id": "trading_halt_delisting",
        "context": NewsSummaryContext(
            title="레드우즈, 상장폐지 사유 발생으로 거래정지 기간 변경",
            snippet="감사의견 거절에 따른 상장 유지 리스크가 부각됐다.",
            content=(
                "레드우즈는 감사의견 거절로 상장폐지 사유가 발생했다고 공시했다. "
                "거래소는 주권 매매거래정지 기간을 변경하고 개선계획 제출 여부를 확인할 예정이다. "
                "투자자는 거래 재개 가능성과 정리매매 절차, 상장 유지 조건을 점검해야 한다."
            ),
            source_type="DISCLOSURE",
            importance="CRITICAL",
            sentiment="NEGATIVE",
            event_tags=["RISK"],
            stock_code="123456",
            stock_name="레드우즈",
            stock_name_en="Redwoods",
            fallback=SummaryLines(),
        ),
        "required_terms": ("Redwoods", "delisting", "trading"),
    },
    {
        "case_id": "foreign_net_selling_market",
        "context": NewsSummaryContext(
            title="외국인 순매도에 코스피 하락, 반도체 대형주 약세",
            snippet="달러 강세와 미국 금리 부담이 외국인 수급을 압박했다.",
            content=(
                "코스피는 외국인 순매도에 하락 마감했고 반도체 대형주가 약세를 보였다. "
                "달러 강세와 미국 금리 부담이 위험자산 선호를 낮추며 외국인 수급을 압박했다. "
                "시장에서는 환율과 금리 방향에 따라 대형주 변동성이 커질 수 있다고 봤다."
            ),
            source_type="NEWS",
            importance="MEDIUM",
            sentiment="NEGATIVE",
            event_tags=["GENERAL_MARKET", "MACRO"],
            stock_code=None,
            stock_name=None,
            stock_name_en="",
            fallback=SummaryLines(),
        ),
        "required_terms": ("KOSPI", "foreign investors", "interest"),
    },
)


def main() -> None:
    args = _parse_args()
    report = evaluate_generation(
        model=args.model,
        adapter_dir=args.adapter_dir,
        report_path=args.report_path,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        min_pass_rate=args.min_pass_rate,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["quality_status"] != "pass":
        raise SystemExit(1)


def evaluate_generation(
    *,
    model: str,
    adapter_dir: Path,
    report_path: Path,
    max_tokens: int,
    temperature: float,
    min_pass_rate: float,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for sample in DEFAULT_EVAL_SAMPLES:
        context = sample["context"]
        if not isinstance(context, NewsSummaryContext):
            raise TypeError("context must be NewsSummaryContext")
        raw_output = _generate_raw_output(
            context=context,
            model=model,
            adapter_dir=adapter_dir,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parsed = NewsSummaryGenerator._parse_llm_output(raw_output)
        validation = _validate_generation(
            parsed=parsed,
            context=context,
            required_terms=tuple(str(term) for term in sample["required_terms"]),
        )
        rows.append(
            {
                "case_id": sample["case_id"],
                "raw_output": raw_output,
                "parsed": parsed,
                **validation,
            }
        )

    attempted = len(rows)
    passed = sum(1 for row in rows if row.get("status") == "pass")
    pass_rate = passed / attempted if attempted else 0.0
    report = {
        "schema_version": "news-summary-qwen3-generation-eval/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_version": NEWS_SUMMARY_PROMPT_VERSION,
        "model": model,
        "adapter_dir": str(adapter_dir),
        "sample_count": attempted,
        "pass_count": passed,
        "pass_rate": round(pass_rate, 6),
        "json_valid_count": sum(1 for row in rows if row.get("json_valid") is True),
        "english_sentence_count": sum(1 for row in rows if row.get("english_sentences") is True),
        "grounded_count": sum(1 for row in rows if row.get("grounded") is True),
        "required_term_count": sum(1 for row in rows if row.get("required_terms_present") is True),
        "min_pass_rate": min_pass_rate,
        "quality_status": "pass" if pass_rate >= min_pass_rate else "fail",
        "results": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def _generate_raw_output(
    *,
    context: NewsSummaryContext,
    model: str,
    adapter_dir: Path,
    max_tokens: int,
    temperature: float,
) -> str:
    messages = NewsSummaryGenerator.messages(context)
    executable = shutil.which("mlx_lm.generate")
    if executable is None:
        raise RuntimeError("mlx_lm.generate executable is required for raw generation eval")
    completed = subprocess.run(  # noqa: S603
        [
            executable,
            "--model",
            model,
            "--adapter-path",
            str(adapter_dir),
            "--system-prompt",
            messages[0]["content"],
            "--prompt",
            messages[1]["content"],
            "--max-tokens",
            str(max_tokens),
            "--temp",
            str(temperature),
            "--verbose",
            "False",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return re.sub(r"<think>.*?</think>", "", completed.stdout, flags=re.DOTALL).strip()


def _validate_generation(
    *,
    parsed: dict[str, str],
    context: NewsSummaryContext,
    required_terms: tuple[str, ...],
) -> dict[str, Any]:
    reasons: list[str] = []
    json_valid = set(parsed) == {"what", "why", "impact"} and all(parsed.values())
    if not json_valid:
        reasons.append("invalid_json_schema")
    summary = SummaryLines(
        what=str(parsed.get("what", "")).strip(),
        why=str(parsed.get("why", "")).strip(),
        impact=str(parsed.get("impact", "")).strip(),
    )
    english_sentences = NewsSummaryGenerator._is_quality_output(summary, context)
    if not english_sentences:
        reasons.append("english_sentence_quality_failed")
    combined = f"{summary.what} {summary.why} {summary.impact}"
    lower_combined = combined.lower()
    required_terms_present = all(term.lower() in lower_combined for term in required_terms)
    if not required_terms_present:
        reasons.append("required_terms_missing")
    grounded = _grounded_in_expected_context(summary, context)
    if not grounded:
        reasons.append("grounding_failed")
    return {
        "status": "pass" if not reasons else "fail",
        "json_valid": json_valid,
        "english_sentences": english_sentences,
        "required_terms_present": required_terms_present,
        "grounded": grounded,
        "failure_reasons": reasons,
    }


def _grounded_in_expected_context(summary: SummaryLines, context: NewsSummaryContext) -> bool:
    combined = f"{summary.what} {summary.why} {summary.impact}".lower()
    if context.stock_name_en and context.stock_name_en.lower() not in combined:
        return False
    evidence_markers = {
        "반도체": ("semiconductor", "chip"),
        "HBM": ("hbm",),
        "영업이익": ("operating", "earnings"),
        "코스피": ("kospi",),
        "기관": ("institutional",),
        "외국인": ("foreign",),
        "자사주": ("treasury",),
        "소각": ("cancellation",),
        "상장폐지": ("delisting",),
        "거래정지": ("trading",),
        "환율": ("exchange", "currency"),
        "금리": ("interest", "rate"),
    }
    evidence = f"{context.title} {context.snippet} {context.content}"
    matched = 0
    for korean_marker, english_markers in evidence_markers.items():
        if korean_marker in evidence and any(marker in combined for marker in english_markers):
            matched += 1
    return matched >= 2


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate news summary Qwen3 raw generation.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--max-tokens", type=int, default=260)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--min-pass-rate", type=float, default=1.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
