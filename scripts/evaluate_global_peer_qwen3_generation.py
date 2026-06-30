import argparse
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest, MarketType
from hannah_montana_ai.services.global_peer_explainer import (
    EXPLANATION_PROMPT_VERSION,
    GlobalPeerExplanation,
    GlobalPeerExplanationContext,
    GlobalPeerExplanationGenerator,
)
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.training.stock_universe import load_stock_universe

DEFAULT_MODEL = "mlx-community/Qwen3-0.6B-4bit"
DEFAULT_ADAPTER_DIR = Path("src/hannah_montana_ai/model_store/global_peer_qwen3_explainer_lora")
DEFAULT_MODEL_PATH = Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib")
DEFAULT_STOCK_UNIVERSE_PATH = Path("data/reference/korea_stock_universe.csv")
DEFAULT_REPORT_PATH = Path("reports/global-peer-qwen3-generation-eval.json")
DEFAULT_SAMPLE_CODES = (
    "196170",
    "035420",
    "005930",
    "000660",
    "005380",
    "373220",
    "207940",
    "068270",
    "105560",
    "055550",
    "017670",
    "066570",
    "006400",
    "000270",
    "012330",
    "035720",
    "251270",
    "352820",
    "033780",
    "015760",
    "032640",
    "051910",
    "028260",
    "010130",
    "086520",
    "247540",
    "090430",
    "018260",
    "003550",
    "096770",
)


def main() -> None:
    args = _parse_args()
    report = evaluate_generation(
        stock_codes=tuple(args.stock_codes or DEFAULT_SAMPLE_CODES),
        model=args.model,
        adapter_dir=args.adapter_dir,
        matcher_model_path=args.matcher_model_path,
        stock_universe_path=args.stock_universe_path,
        report_path=args.report_path,
        min_pass_rate=args.min_pass_rate,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def evaluate_generation(
    *,
    stock_codes: tuple[str, ...],
    model: str,
    adapter_dir: Path,
    matcher_model_path: Path,
    stock_universe_path: Path,
    report_path: Path,
    min_pass_rate: float,
    max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    universe_by_code = {
        stock.stock_code: stock for stock in load_stock_universe(stock_universe_path)
    }
    matcher = GlobalPeerMatcher(matcher_model_path)
    generator = GlobalPeerExplanationGenerator()
    rows: list[dict[str, Any]] = []

    for stock_code in stock_codes:
        stock = universe_by_code.get(stock_code)
        if stock is None:
            rows.append(
                {
                    "stock_code": stock_code,
                    "status": "fail",
                    "failure_reasons": ["stock_not_found"],
                }
            )
            continue
        request = GlobalPeerMatchRequest(
            stock_code=stock.stock_code,
            stock_name=stock.stock_name,
            stock_name_en=stock.stock_name_en,
            market=_market_for(stock.market),
            aliases=list(stock.aliases),
            peer_count=5,
        )
        response = matcher.match(request)
        context = GlobalPeerExplanationContext(
            request=request,
            primary_peer=response.primary_peer,
            confidence_level=response.confidence_level,
            confidence_score=response.confidence_score,
        )
        raw_output = _generate_raw_output(
            generator=generator,
            context=context,
            model=model,
            adapter_dir=adapter_dir,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parsed, parse_error = _parse_json_object(raw_output)
        expected = generator.template(context)
        validation = _validate_generation(
            parsed=parsed,
            parse_error=parse_error,
            expected=expected,
            context=context,
            generator=generator,
        )
        rows.append(
            {
                "stock_code": stock.stock_code,
                "stock_name": stock.stock_name,
                "stock_name_en": stock.stock_name_en,
                "primary_peer_ticker": response.primary_peer.ticker,
                "primary_peer_name": response.primary_peer.company_name,
                "confidence_level": response.confidence_level,
                "confidence_score": response.confidence_score,
                "expected_headline": expected.headline,
                "raw_output": raw_output,
                "parsed": parsed,
                **validation,
            }
        )

    attempted = len(rows)
    passed = sum(1 for row in rows if row.get("status") == "pass")
    json_valid = sum(1 for row in rows if row.get("json_valid") is True)
    exact_headline = sum(1 for row in rows if row.get("exact_headline") is True)
    grounded = sum(1 for row in rows if row.get("grounded") is True)
    pass_rate = passed / attempted if attempted else 0.0
    report = {
        "schema_version": "global-peer-qwen3-generation-eval/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_version": EXPLANATION_PROMPT_VERSION,
        "model": model,
        "adapter_dir": str(adapter_dir),
        "stock_count": attempted,
        "pass_count": passed,
        "pass_rate": round(pass_rate, 6),
        "json_valid_count": json_valid,
        "exact_headline_count": exact_headline,
        "exact_summary_count": sum(1 for row in rows if row.get("exact_summary") is True),
        "grounded_count": grounded,
        "min_pass_rate": min_pass_rate,
        "quality_status": "pass" if pass_rate >= min_pass_rate else "fail",
        "results": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def _generate_raw_output(
    *,
    generator: GlobalPeerExplanationGenerator,
    context: GlobalPeerExplanationContext,
    model: str,
    adapter_dir: Path,
    max_tokens: int,
    temperature: float,
) -> str:
    messages = generator.training_example(context)["messages"][:-1]
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


def _parse_json_object(raw_output: str) -> tuple[dict[str, str], str]:
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError as exception:
        return {}, f"json_decode_error:{exception.msg}"
    if not isinstance(payload, dict):
        return {}, "not_json_object"
    headline = payload.get("headline")
    summary = payload.get("summary")
    if not isinstance(headline, str) or not isinstance(summary, str):
        return {}, "missing_headline_or_summary"
    extra_keys = sorted(set(payload) - {"headline", "summary"})
    if extra_keys:
        return {"headline": headline, "summary": summary}, f"extra_keys:{','.join(extra_keys)}"
    return {"headline": headline, "summary": summary}, ""


def _validate_generation(
    *,
    parsed: dict[str, str],
    parse_error: str,
            expected: GlobalPeerExplanation,
    context: GlobalPeerExplanationContext,
    generator: GlobalPeerExplanationGenerator,
) -> dict[str, Any]:
    reasons: list[str] = []
    if parse_error:
        reasons.append(parse_error)
    headline = parsed.get("headline", "")
    summary = parsed.get("summary", "")
    exact_headline = headline == expected.headline
    exact_summary = summary == expected.summary
    if not exact_headline:
        reasons.append("headline_mismatch")
    grounded = generator._is_grounded(headline, summary, context)
    if not grounded:
        reasons.append("grounding_failed")
    if not generator._is_quality_output(
        headline=headline,
        summary=summary,
        expected=expected,
        context=context,
    ):
        reasons.append("quality_failed")
    if _has_repeated_sentence(summary):
        reasons.append("repeated_sentence")
    return {
        "status": "pass" if not reasons else "fail",
        "json_valid": not parse_error,
        "exact_headline": exact_headline,
        "exact_summary": exact_summary,
        "grounded": grounded,
        "failure_reasons": reasons,
    }


def _has_repeated_sentence(summary: str) -> bool:
    sentences = [
        sentence.strip().lower()
        for sentence in re.split(r"(?<=[.!?])\s+", summary)
        if sentence.strip()
    ]
    return len(sentences) != len(set(sentences))


def _market_for(value: str) -> MarketType:
    market = value if value in {"KOSPI", "KOSDAQ", "KONEX", "OTHER"} else "KOSPI"
    return cast(MarketType, market)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate raw Qwen3 peer explanation generation.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    parser.add_argument("--matcher-model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--stock-universe-path", type=Path, default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--stock-codes", nargs="*")
    parser.add_argument("--min-pass-rate", type=float, default=0.9)
    parser.add_argument("--max-tokens", type=int, default=220)
    parser.add_argument("--temperature", type=float, default=0.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
