import argparse
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hannah_montana_ai.domain.schemas import (
    FinancialTermEvidence,
    KoreanFinancialTermExplainRequest,
)
from hannah_montana_ai.services.korean_financial_terms import (
    MODEL_PROMPT_VERSION,
    TERM_GENERATION_CATEGORIES,
    LocalQwenTermExplanationProvider,
    _context_evidence,
    _parse_json_object,
    _strip_thinking,
)

DEFAULT_MODEL = "mlx-community/Qwen3-0.6B-4bit"
DEFAULT_ADAPTER_DIR = Path("src/hannah_montana_ai/model_store/korean_term_qwen3_explainer_lora")
DEFAULT_REPORT_PATH = Path("reports/korean-term-qwen3-generation-eval.json")

DEFAULT_EVAL_SAMPLES = (
    {
        "term": "우주항공주",
        "title": "우주항공주 강세",
        "context": "우주항공주가 정부 정책 기대감과 위성 투자 확대로 강세를 보였다.",
        "expected_category": "theme_stock",
        "expected_english_term": "aerospace-themed stock",
    },
    {
        "term": "양자컴퓨팅밈주",
        "title": "양자컴퓨팅밈주 급등",
        "context": "양자컴퓨팅밈주라는 표현이 온라인 수급과 함께 언급됐다.",
        "expected_category": "theme_stock",
        "expected_english_term": "quantum-computing meme stock",
    },
    {
        "term": "HBM주",
        "title": "HBM주 반등",
        "context": "HBM주가 AI 서버 메모리 수요 기대감으로 상승했다.",
        "expected_category": "theme_stock",
        "expected_english_term": "HBM-themed stock",
    },
    {
        "term": "원전주",
        "title": "원전주 수주 기대",
        "context": "원전주가 해외 프로젝트 수주 기대감으로 강세를 보였다.",
        "expected_category": "theme_stock",
        "expected_english_term": "nuclear-power-themed stock",
    },
    {
        "term": "방산주",
        "title": "방산주 수출 기대",
        "context": "방산주가 수출 계약 기대감과 지정학적 긴장으로 강세를 보였다.",
        "expected_category": "theme_stock",
        "expected_english_term": "defense-themed stock",
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
        request = KoreanFinancialTermExplainRequest(
            term=str(sample["term"]),
            title=str(sample["title"]),
            context=str(sample["context"]),
        )
        evidence = _context_evidence(request)
        raw_output = _generate_raw_output(
            request=request,
            evidence=evidence,
            model=model,
            adapter_dir=adapter_dir,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parsed = _parse_json_object(_strip_thinking(raw_output))
        validation = _validate_generation(
            parsed=parsed,
            term=request.term,
            expected_category=str(sample["expected_category"]),
            expected_english_term=str(sample["expected_english_term"]),
        )
        rows.append(
            {
                "term": request.term,
                "expected_category": sample["expected_category"],
                "expected_english_term": sample["expected_english_term"],
                "raw_output": raw_output,
                "parsed": parsed,
                **validation,
            }
        )

    attempted = len(rows)
    passed = sum(1 for row in rows if row.get("status") == "pass")
    pass_rate = passed / attempted if attempted else 0.0
    report = {
        "schema_version": "korean-term-qwen3-generation-eval/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_version": MODEL_PROMPT_VERSION,
        "model": model,
        "adapter_dir": str(adapter_dir),
        "sample_count": attempted,
        "pass_count": passed,
        "pass_rate": round(pass_rate, 6),
        "json_valid_count": sum(1 for row in rows if row.get("json_valid") is True),
        "category_match_count": sum(1 for row in rows if row.get("category_match") is True),
        "english_term_match_count": sum(
            1 for row in rows if row.get("english_term_match") is True
        ),
        "grounded_count": sum(1 for row in rows if row.get("grounded") is True),
        "min_pass_rate": min_pass_rate,
        "quality_status": "pass" if pass_rate >= min_pass_rate else "fail",
        "results": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def _generate_raw_output(
    *,
    request: KoreanFinancialTermExplainRequest,
    evidence: tuple[FinancialTermEvidence, ...],
    model: str,
    adapter_dir: Path,
    max_tokens: int,
    temperature: float,
) -> str:
    messages = LocalQwenTermExplanationProvider.messages(request, evidence)
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
    parsed: dict[str, object],
    term: str,
    expected_category: str,
    expected_english_term: str,
) -> dict[str, Any]:
    reasons: list[str] = []
    required_keys = {
        "english_term",
        "category",
        "definition",
        "explanation",
        "example",
        "confidence_score",
    }
    json_valid = bool(parsed) and required_keys.issubset(parsed)
    if not json_valid:
        reasons.append("invalid_json_schema")
    english_term = str(parsed.get("english_term", "")).strip()
    category = str(parsed.get("category", "")).strip()
    definition = str(parsed.get("definition", "")).strip()
    explanation = str(parsed.get("explanation", "")).strip()
    example = str(parsed.get("example", "")).strip()
    category_match = category == expected_category and category in TERM_GENERATION_CATEGORIES
    english_term_match = english_term == expected_english_term
    if not category_match:
        reasons.append("category_mismatch")
    if not english_term_match:
        reasons.append("english_term_mismatch")
    grounded = term in f"{definition} {explanation} {example}" and len(explanation) >= 80
    if not grounded:
        reasons.append("grounding_failed")
    if re.search(r"\b(buy|sell|hold|price target)\b|매수|매도|목표가", explanation, re.I):
        reasons.append("investment_advice")
    if english_term.lower() in {"earnings", "foreign investors", "institutions"}:
        reasons.append("generic_english_term")
    return {
        "status": "pass" if not reasons else "fail",
        "json_valid": json_valid,
        "category_match": category_match,
        "english_term_match": english_term_match,
        "grounded": grounded,
        "failure_reasons": reasons,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Korean term Qwen3 raw generation.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--max-tokens", type=int, default=320)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--min-pass-rate", type=float, default=1.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
