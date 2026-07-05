# ruff: noqa: E501
import argparse
import json
from pathlib import Path

from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm
from hannah_montana_ai.services.korean_translation_generator import (
    KOREAN_TRANSLATION_PROMPT_VERSION,
    KoreanTranslationContext,
    KoreanTranslationGenerator,
)

DEFAULT_SFT_PATH = Path("data/training/korean_translation_sft.jsonl")
DEFAULT_MLX_DIR = Path("data/training/korean_translation_mlx")
DEFAULT_REPORT_PATH = Path("reports/korean-translation-qwen3-readiness.json")


def main() -> None:
    args = parse_args()
    samples = build_samples()
    write_jsonl(args.sft_path, [to_record(sample) for sample in samples])
    split_counts = write_mlx_splits(args.mlx_dir, [to_record(sample) for sample in samples])
    report = {
        "schema_version": "korean-translation-qwen3-readiness/v1",
        "prompt_version": KOREAN_TRANSLATION_PROMPT_VERSION,
        "sample_count": len(samples),
        "split_counts": split_counts,
        "coverage": {
            "news": sum(1 for sample in samples if sample["source_type"] == "NEWS"),
            "disclosure": sum(1 for sample in samples if sample["source_type"] == "DISCLOSURE"),
            "localism_samples": sum(
                1
                for sample in samples
                if any(term in sample["ko"] for term in ("개미", "대장주", "따따블", "삼전닉스"))
            ),
            "full_content_samples": sum(1 for sample in samples if len(sample["ko"]) > 100),
        },
        "quality_gate": {
            "requires_json_translation_key": True,
            "rejects_hangul_residue": True,
            "rejects_summary_instead_of_translation": True,
            "rejects_truncated_ellipsis": True,
        },
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def build_samples() -> list[dict[str, str]]:
    base = [
        (
            "NEWS",
            "삼성전자 2분기 영업이익 증가",
            "삼성전자는 AI 서버 투자 확대로 반도체 실적 개선 기대가 커졌다.",
            "Samsung Electronics saw stronger expectations for semiconductor earnings improvement as AI server investment expanded.",
        ),
        (
            "NEWS",
            "SK하이닉스, HBM 수요에 시가총액 1위 등극",
            "SK하이닉스는 HBM 공급 우위와 외국인 순매수에 힘입어 시가총액 1위에 올랐다.",
            "SK hynix became Korea's largest company by market cap, supported by its HBM supply lead and foreign-investor net buying.",
        ),
        (
            "DISCLOSURE",
            "삼성전자, 자사주 소각 결정",
            "삼성전자는 14조5800억원 규모 자사주 소각을 결정했다고 공시했다.",
            "Samsung Electronics disclosed a KRW 14.58 trillion treasury-share cancellation.",
        ),
        (
            "DISCLOSURE",
            "한화솔루션 유상증자",
            "한화솔루션은 유상증자를 통해 운영자금과 시설투자 자금을 확보한다고 공시했다.",
            "Hanwha Solutions disclosed that it will secure operating and facility-investment funds through a capital increase.",
        ),
        (
            "DISCLOSURE",
            "레드우즈 거래정지 기간 변경",
            "레드우즈는 감사의견 거절로 상장폐지 사유가 발생해 주권 매매거래정지 기간이 변경됐다고 공시했다.",
            "Redwoods disclosed that a delisting trigger occurred after an adverse audit opinion and that the share trading-halt period was changed.",
        ),
        (
            "NEWS",
            "코스피 상승",
            "코스피는 반도체 대형주 강세와 기관 순매수에 힘입어 상승 마감했다.",
            "The KOSPI closed higher, supported by strength in large-cap semiconductor stocks and institutional net buying.",
        ),
        (
            "NEWS",
            "환율 부담",
            "원달러 환율이 1500원대에서 머물면서 수출기업의 비용 부담이 커지고 있다.",
            "Korean exporters face rising cost pressure as the won-dollar exchange rate stays near KRW 1,500.",
        ),
        (
            "NEWS",
            "개미 순매수",
            "개미가 삼성전자를 순매수하며 반도체 대장주에 대한 관심이 높아졌다.",
            "Ants net bought Samsung Electronics, lifting attention on the semiconductor bellwether stock.",
        ),
        (
            "NEWS",
            "삼전닉스 강세",
            "삼전닉스가 외국인 러브콜에 힘입어 동반 강세를 보였다.",
            "Samjeon Nix moved higher together, supported by foreign-investor love calls.",
        ),
        (
            "NEWS",
            "삼전닉스 순매수",
            "개미가 삼전닉스를 순매수하며 반도체 대장주에 대한 관심이 높아졌다.",
            "Ants net bought Samjeon Nix, lifting attention on the semiconductor bellwether stock.",
        ),
        (
            "NEWS",
            "삼전닉스 수급",
            "외국인과 개미의 동반 순매수로 삼전닉스 대장주 흐름이 강해졌다.",
            "Foreign investors and Ants both net bought Samjeon Nix, strengthening the bellwether-stock flow.",
        ),
        (
            "NEWS",
            "IPO 따따블",
            "신규 상장주는 공모가 대비 따따블에 성공하며 투자자 관심을 끌었다.",
            "The newly listed stock drew investor attention after achieving a dda-dda-ble move from its IPO price.",
        ),
        (
            "NEWS",
            "품절주 급등",
            "유통주식 수가 적은 품절주가 수급 쏠림으로 급등했다.",
            "A low-float stock with limited tradable shares surged on concentrated supply-demand flows.",
        ),
        (
            "NEWS",
            "현대차 판매",
            "현대차는 북미 전기차 판매 증가와 우호적인 환율 효과로 수익성 개선 기대가 커졌다.",
            "Hyundai Motor's profitability expectations improved on higher North American EV sales and a favorable exchange-rate effect.",
        ),
        (
            "NEWS",
            "셀트리온 허가 기대",
            "셀트리온은 신규 바이오시밀러의 미국 허가 기대가 커지며 실적 눈높이가 높아졌다.",
            "Celltrion's earnings expectations rose as hopes grew for US approval of a new biosimilar.",
        ),
        (
            "NEWS",
            "HD현대중공업 수주",
            "HD현대중공업은 LNG선 수주 증가로 매출 가시성이 확대됐다는 평가를 받았다.",
            "HD Hyundai Heavy Industries was seen as gaining better revenue visibility from more LNG-carrier orders.",
        ),
        (
            "DISCLOSURE",
            "전환사채 발행",
            "회사는 운영자금 확보를 위해 전환사채 발행을 결정했다고 공시했다.",
            "The company disclosed that it decided to issue convertible bonds to secure operating funds.",
        ),
        (
            "DISCLOSURE",
            "공급계약 체결",
            "한화에어로스페이스는 해외 고객사와 방산 장비 공급계약을 체결했다고 공시했다.",
            "Hanwha Aerospace disclosed that it signed a defense-equipment supply contract with an overseas customer.",
        ),
    ]
    samples: list[dict[str, str]] = []
    for source_type, title, ko, en in base:
        samples.append({"source_type": source_type, "title": title, "ko": ko, "en": en})
        samples.append(
            {
                "source_type": source_type,
                "title": title,
                "ko": f"{ko} 투자자는 실제 일정과 실적 반영 속도를 함께 확인해야 한다.",
                "en": f"{en} Investors should also check the actual schedule and the pace of earnings recognition.",
            }
        )
    samples.extend(full_content_samples())
    return samples


def full_content_samples() -> list[dict[str, str]]:
    return [
        {
            "source_type": "NEWS",
            "title": "삼성전자 HBM 수요",
            "ko": (
                "삼성전자는 AI 서버 투자 확대로 반도체 실적 개선 기대가 커졌다. "
                "기사에서는 HBM 수요 확대와 메모리 가격 반등이 주요 배경으로 거론됐다. "
                "투자자는 영업이익 회복 속도와 고부가 메모리 제품 비중을 확인해야 한다."
            ),
            "en": (
                "Samsung Electronics saw stronger expectations for semiconductor earnings improvement as AI server investment expanded. "
                "The article cited stronger HBM demand and a rebound in memory prices as key drivers. "
                "Investors should monitor the pace of operating-profit recovery and the mix of high-value memory products."
            ),
        },
        {
            "source_type": "DISCLOSURE",
            "title": "레드우즈 상장폐지 사유",
            "ko": (
                "레드우즈는 감사의견 거절로 상장폐지 사유가 발생했다고 공시했다. "
                "거래소는 주권 매매거래정지 기간을 변경하고 개선계획 제출 여부를 확인할 예정이다. "
                "투자자는 거래 재개 가능성과 정리매매 절차, 상장 유지 조건을 점검해야 한다."
            ),
            "en": (
                "Redwoods disclosed a delisting trigger after an adverse audit opinion. "
                "The exchange will change the share trading-halt period and check whether the company submits a remediation plan. "
                "Investors should review the possibility of trading resumption, liquidation trading procedures, and listing-maintenance conditions."
            ),
        },
        {
            "source_type": "NEWS",
            "title": "환율과 수출기업",
            "ko": (
                "원달러 환율이 1500원대에서 머물면서 수출기업의 비용 부담이 커지고 있다. "
                "달러 표시 원재료와 외화 부채 비중이 높은 기업은 환율 상승에 따른 손익 변동성이 커질 수 있다. "
                "시장에서는 반도체와 조선 등 수출 업종의 가격 전가력과 헤지 전략을 확인해야 한다고 봤다."
            ),
            "en": (
                "Korean exporters face rising cost pressure as the won-dollar exchange rate stays near KRW 1,500. "
                "Companies with high exposure to dollar-priced raw materials and foreign-currency debt may see greater earnings volatility from the stronger exchange rate. "
                "The market said investors should check pricing power and hedging strategies in export sectors such as semiconductors and shipbuilding."
            ),
        },
    ]


def to_record(sample: dict[str, str]) -> dict[str, object]:
    generator = KoreanTranslationGenerator(enabled=False)
    context = KoreanTranslationContext(
        text=sample["ko"],
        source_type=sample["source_type"],  # type: ignore[arg-type]
        title=sample["title"],
        glossary_terms=glossary_terms_for(sample["ko"]),
    )
    return {
        "messages": [
            *generator._messages(sample["ko"], context),
            {
                "role": "assistant",
                "content": json.dumps(
                    {"translation": sample["en"]},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            },
        ]
    }


def glossary_terms_for(text: str) -> list[FinancialGlossaryTerm]:
    seed = {
        "개미": ("retail investors", "market_slang"),
        "삼전닉스": ("Samsung Electronics and SK hynix", "market_slang"),
        "대장주": ("bellwether stock", "market_slang"),
        "따따블": ("IPO quadruple jump", "market_slang"),
        "품절주": ("low-float stock", "market_slang"),
    }
    return [
        FinancialGlossaryTerm(
            source_term=term,
            normalized_term=term,
            english_term=english_term,
            category=category,
        )
        for term, (english_term, category) in seed.items()
        if term in text
    ]


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_mlx_splits(data_dir: Path, rows: list[dict[str, object]]) -> dict[str, int]:
    data_dir.mkdir(parents=True, exist_ok=True)
    valid_indexes = {index for index in range(1, len(rows), 10)}
    test_indexes = {index for index in range(5, len(rows), 10)}
    valid = [row for index, row in enumerate(rows) if index in valid_indexes][:4]
    test = [row for index, row in enumerate(rows) if index in test_indexes][:4]
    holdout_indexes = valid_indexes | test_indexes
    train = [row for index, row in enumerate(rows) if index not in holdout_indexes]
    write_jsonl(data_dir / "train.jsonl", train)
    write_jsonl(data_dir / "valid.jsonl", valid)
    write_jsonl(data_dir / "test.jsonl", test)
    return {"train": len(train), "valid": len(valid), "test": len(test)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sft-path", type=Path, default=DEFAULT_SFT_PATH)
    parser.add_argument("--mlx-dir", type=Path, default=DEFAULT_MLX_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
