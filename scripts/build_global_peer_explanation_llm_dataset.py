import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import GlobalPeerMatchRequest, MarketType
from hannah_montana_ai.services.global_peer_explainer import (
    EXPLANATION_PROMPT_VERSION,
    GlobalPeerExplanationContext,
    GlobalPeerExplanationGenerator,
)
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.training.global_peer_trainer import KOREA_ANCHORS
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, load_stock_universe

VALID_MARKETS: set[str] = {"KOSPI", "KOSDAQ", "KONEX", "OTHER"}


def build_global_peer_explanation_llm_dataset(
    *,
    stock_universe_path: Path,
    model_path: Path,
    dataset_path: Path,
    report_path: Path,
) -> dict[str, object]:
    stocks = load_stock_universe(stock_universe_path)
    matcher = GlobalPeerMatcher(model_path)
    generator = GlobalPeerExplanationGenerator()
    rows: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    confidence_counts: Counter[str] = Counter()
    grounded_failures = 0

    for stock in stocks:
        try:
            request = _request_for(stock)
            response = matcher.match(request)
            context = GlobalPeerExplanationContext(
                request=request,
                primary_peer=response.primary_peer,
                confidence_level=response.confidence_level,
                confidence_score=response.confidence_score,
            )
            example = generator.training_example(context)
            target = cast(dict[str, str], example["target"])
            if not _target_is_grounded(target, stock, response.primary_peer.company_name):
                grounded_failures += 1
            confidence_counts[response.confidence_level] += 1
            rows.append(
                {
                    "stock_code": stock.stock_code,
                    "stock_name": stock.stock_name,
                    "stock_name_en": response.stock_name_en,
                    "primary_peer_ticker": response.primary_peer.ticker,
                    "primary_peer_name": response.primary_peer.company_name,
                    "confidence_level": response.confidence_level,
                    "confidence_score": response.confidence_score,
                    **example,
                }
            )
        except Exception as exception:  # pragma: no cover - 배치 실패는 리포트에 남긴다.
            failures.append(
                {
                    "stock_code": stock.stock_code,
                    "stock_name": stock.stock_name,
                    "error": type(exception).__name__,
                    "message": str(exception),
                }
            )

    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with dataset_path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "schema_version": "global-peer-explanation-llm-readiness/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_version": EXPLANATION_PROMPT_VERSION,
        "recommended_train_model": "Qwen/Qwen3-0.6B-MLX-4bit LoRA",
        "recommended_serving_model": "Qwen3-0.6B GGUF Q4",
        "serving_runtime": "llama.cpp OpenAI-compatible server",
        "serving_constraint": "AWS t4g.medium CPU-only, 2 vCPU, 4 GiB RAM",
        "dataset_path": str(dataset_path),
        "stock_universe_path": str(stock_universe_path),
        "model_path": str(model_path),
        "sample_count": len(rows),
        "failure_count": len(failures),
        "confidence_distribution": dict(sorted(confidence_counts.items())),
        "grounded_target_failure_count": grounded_failures,
        "quality_status": (
            "pass" if len(rows) >= 3000 and not failures and grounded_failures == 0 else "fail"
        ),
        "failures": failures[:50],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def _request_for(stock: StockUniverseEntry) -> GlobalPeerMatchRequest:
    market = stock.market if stock.market in VALID_MARKETS else "KOSPI"
    return GlobalPeerMatchRequest(
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        stock_name_en=stock.stock_name_en,
        market=cast(MarketType, market),
        aliases=list(stock.aliases),
        peer_count=5,
    )


def _target_is_grounded(
    target: dict[str, str],
    stock: StockUniverseEntry,
    peer_name: str,
) -> bool:
    text = f"{target.get('headline', '')} {target.get('summary', '')}".lower()
    stock_terms = [stock.stock_name.lower()]
    if stock.stock_name_en:
        stock_terms.append(stock.stock_name_en.lower())
    anchor = KOREA_ANCHORS.get(stock.stock_code)
    if anchor and anchor.display_name:
        stock_terms.append(anchor.display_name.lower())

    peer_terms = {peer_name.lower(), _display_peer_name(peer_name).lower()}
    first_peer_word = re.split(r"[\s.,]+", peer_name.strip())[0].lower()
    if len(first_peer_word) >= 4:
        peer_terms.add(first_peer_word)

    return any(term and term in text for term in stock_terms) and any(
        term and term in text for term in peer_terms
    )


def _display_peer_name(company_name: str) -> str:
    cleaned = re.sub(r"\s+\.\s+", " ", company_name).strip()
    cleaned = re.sub(r"\s+,", "", cleaned).strip()
    cleaned = re.sub(r"\s+Class\s+[A-Z]$", "", cleaned).strip()
    cleaned = re.sub(r"\s+When-Issued$", "", cleaned).strip()
    return cleaned.rstrip(" ,")


def main() -> None:
    settings = get_settings()
    report = build_global_peer_explanation_llm_dataset(
        stock_universe_path=settings.stock_universe_path,
        model_path=settings.global_peer_model_path,
        dataset_path=settings.global_peer_explanation_training_path,
        report_path=settings.global_peer_explanation_readiness_report_path,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
