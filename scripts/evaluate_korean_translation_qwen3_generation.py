# ruff: noqa: E501
import argparse
import json
from pathlib import Path

from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm
from hannah_montana_ai.services.korean_translation_generator import (
    KoreanTranslationContext,
    KoreanTranslationGenerator,
    MlxQwenKoreanTranslationClient,
)

DEFAULT_MODEL = "mlx-community/Qwen3-0.6B-4bit"
DEFAULT_ADAPTER_DIR = Path("src/hannah_montana_ai/model_store/korean_translation_qwen3_lora")
DEFAULT_REPORT_PATH = Path("reports/korean-translation-qwen3-generation-eval.json")


def main() -> None:
    args = parse_args()
    client = MlxQwenKoreanTranslationClient(
        model=args.model,
        adapter_path=args.adapter_dir,
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name=f"local-llm:{args.model}",
        max_tokens=args.max_tokens,
    )
    rows = []
    for sample in eval_samples():
        result = generator.translate(sample["context"])
        translated = result.translated_text
        pass_gate = (
            result.status == "TRANSLATED"
            and not result.quality_flags
            and all(term.lower() in translated.lower() for term in sample["required_terms"])
        )
        rows.append(
            {
                "id": sample["id"],
                "status": result.status,
                "quality_flags": result.quality_flags,
                "translated_text": translated,
                "required_terms": sample["required_terms"],
                "pass": pass_gate,
            }
        )
    pass_count = sum(1 for row in rows if row["pass"])
    report = {
        "schema_version": "korean-translation-qwen3-generation-eval/v1",
        "model": args.model,
        "adapter_dir": str(args.adapter_dir),
        "sample_count": len(rows),
        "pass_count": pass_count,
        "pass_rate": round(pass_count / len(rows), 6) if rows else 0.0,
        "rows": rows,
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["pass_rate"] < args.min_pass_rate:
        raise SystemExit(
            f"Korean translation Qwen3 pass rate {report['pass_rate']} below {args.min_pass_rate}"
        )


def eval_samples() -> list[dict[str, object]]:
    return [
        {
            "id": "samsung-treasury-share",
            "context": KoreanTranslationContext(
                text="삼성전자는 14조5800억원 규모 자사주 소각을 결정했다고 공시했다.",
                source_type="DISCLOSURE",
                title="삼성전자 자사주 소각",
            ),
            "required_terms": ["Samsung Electronics", "treasury", "cancellation"],
        },
        {
            "id": "samjeon-nix-localism",
            "context": KoreanTranslationContext(
                text="개미가 삼전닉스를 순매수하며 반도체 대장주에 대한 관심이 높아졌다.",
                source_type="NEWS",
                title="삼전닉스 순매수",
                glossary_terms=[
                    FinancialGlossaryTerm(
                        source_term="개미",
                        normalized_term="개미",
                        english_term="retail investors",
                        category="market_slang",
                    ),
                    FinancialGlossaryTerm(
                        source_term="삼전닉스",
                        normalized_term="삼전닉스",
                        english_term="Samsung Electronics and SK hynix",
                        category="market_slang",
                    ),
                    FinancialGlossaryTerm(
                        source_term="대장주",
                        normalized_term="대장주",
                        english_term="bellwether stock",
                        category="market_slang",
                    ),
                ],
            ),
            "required_terms": ["Ants", "Samjeon Nix", "bellwether"],
        },
        {
            "id": "samsung-operating-profit-recovery",
            "context": KoreanTranslationContext(
                text=(
                    "삼성전자는 반도체 수요 회복과 공급계약 증가로 영업이익 개선이 "
                    "예상된다고 밝혔다."
                ),
                source_type="NEWS",
                title="삼성전자 2분기 영업이익 증가",
                glossary_terms=[
                    FinancialGlossaryTerm(
                        source_term="삼성전자",
                        normalized_term="삼성전자",
                        english_term="Samsung Electronics",
                        category="stock",
                    ),
                    FinancialGlossaryTerm(
                        source_term="공급계약",
                        normalized_term="공급계약",
                        english_term="supply contract",
                        category="event",
                    ),
                    FinancialGlossaryTerm(
                        source_term="영업이익",
                        normalized_term="영업이익",
                        english_term="operating profit",
                        category="metric",
                    ),
                ],
            ),
            "required_terms": ["Samsung Electronics", "operating profit", "semiconductor"],
        },
        {
            "id": "exchange-rate-exporters",
            "context": KoreanTranslationContext(
                text=(
                    "원달러 환율이 1500원대에서 머물면서 수출기업의 비용 부담이 커지고 있다. "
                    "달러 표시 원재료와 외화 부채 비중이 높은 기업은 환율 상승에 따른 손익 변동성이 커질 수 있다."
                ),
                source_type="NEWS",
                title="환율 부담",
            ),
            "required_terms": ["exchange rate", "raw materials", "foreign-currency debt"],
        },
        {
            "id": "delisting-trigger",
            "context": KoreanTranslationContext(
                text=(
                    "레드우즈는 감사의견 거절로 상장폐지 사유가 발생했다고 공시했다. "
                    "거래소는 주권 매매거래정지 기간을 변경하고 개선계획 제출 여부를 확인할 예정이다."
                ),
                source_type="DISCLOSURE",
                title="상장폐지 사유 발생",
            ),
            "required_terms": ["delisting", "trading-halt", "remediation plan"],
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--min-pass-rate", type=float, default=1.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
