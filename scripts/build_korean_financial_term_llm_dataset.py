import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import KoreanFinancialTermExplainRequest
from hannah_montana_ai.services.korean_financial_terms import (
    MODEL_PROMPT_VERSION,
    GeneratedTermExplanation,
    LocalQwenTermExplanationProvider,
    _context_evidence,
    _load_entries,
)

DEFAULT_OUTPUT_PATH = Path("data/training/korean_financial_term_explanation_sft.jsonl")
DEFAULT_REPORT_PATH = Path("reports/korean-financial-term-llm-readiness.json")

CONTEXT_TEMPLATES = (
    "{term}가 정책 기대감과 개인 투자자 수급이 겹치며 장중 강세를 보였다.",
    "시장에서는 {term} 관련 종목이 테마성 매수세로 부각됐다고 해석했다.",
    "증권가에서는 {term} 표현이 실제 실적보다 투자자 관심과 기사 맥락을 설명하는 말이라고 봤다.",
    "{term}에 대한 관심은 관련 산업 뉴스와 수급 변화가 동시에 나오면서 커졌다.",
    "외국인 투자자는 {term}가 별도 회사명이 아니라 한국 시장에서 쓰는 분류 표현인지 확인해야 한다.",
    "{term} 강세가 보도됐지만 기사에서는 투자 판단보다 용어의 시장 맥락을 설명하는 데 초점이 있다.",
    "최근 뉴스에서 {term}는 특정 테마에 묶인 종목군을 가리키는 표현으로 반복 등장했다.",
    "{term}라는 표현은 한국 개인투자자 커뮤니티와 증권 기사에서 함께 쓰이는 경우가 많다.",
)


@dataclass(frozen=True)
class CuratedTerm:
    normalized_term: str
    english_term: str
    category: str
    definition: str
    explanation: str
    example: str
    contexts: tuple[str, ...]


CURATED_TERMS = (
    CuratedTerm(
        normalized_term="우주항공주",
        english_term="aerospace-themed stock",
        category="theme_stock",
        definition=(
            "\"우주항공주\" means a Korean stock grouped under the aerospace investment "
            "theme."
        ),
        explanation=(
            "\"우주항공주\" is used when articles link stocks to satellites, launch systems, "
            "defense aerospace, or space policy. In this article, the term is grounded by "
            "references to policy expectations and satellite investment."
        ),
        example="우주항공주 강세 means aerospace-themed stocks rallied.",
        contexts=(
            "우주항공주가 정부 정책 기대감과 위성 투자 확대로 강세를 보였다.",
            "우주항공주 관련 종목이 발사체 예산 확대 기대감으로 상승했다.",
        ),
    ),
    CuratedTerm(
        normalized_term="양자컴퓨팅밈주",
        english_term="quantum-computing meme stock",
        category="theme_stock",
        definition=(
            "\"양자컴퓨팅밈주\" means a Korean stock framed by investors as a speculative "
            "quantum-computing meme theme."
        ),
        explanation=(
            "\"양자컴퓨팅밈주\" describes a stock moving on online attention around quantum "
            "computing rather than verified earnings impact. In this article, the term is "
            "grounded by references to online demand and theme trading."
        ),
        example="양자컴퓨팅밈주 급등 means quantum-computing meme stocks surged.",
        contexts=(
            "양자컴퓨팅밈주라는 표현이 온라인 수급과 함께 언급됐다.",
            "양자컴퓨팅밈주가 커뮤니티 관심과 테마성 매수세로 급등했다.",
        ),
    ),
    CuratedTerm(
        normalized_term="HBM주",
        english_term="HBM-themed stock",
        category="theme_stock",
        definition=(
            "\"HBM주\" means a Korean stock associated with high-bandwidth memory demand "
            "or the AI memory supply chain."
        ),
        explanation=(
            "\"HBM주\" is used when Korean articles tie a company to high-bandwidth memory "
            "or AI server memory demand. In this article, the term is grounded by memory-chip "
            "supply-chain context rather than a promise of future returns."
        ),
        example="HBM주 강세 means HBM-themed stocks rose.",
        contexts=(
            "HBM주가 AI 서버 메모리 수요 기대감으로 상승했다.",
            "HBM주 관련 종목이 반도체 공급망 기대와 함께 부각됐다.",
        ),
    ),
    CuratedTerm(
        normalized_term="원전주",
        english_term="nuclear-power-themed stock",
        category="theme_stock",
        definition=(
            "\"원전주\" means a Korean stock grouped under the nuclear power construction, "
            "equipment, or policy theme."
        ),
        explanation=(
            "\"원전주\" appears when articles connect stocks to nuclear plant projects, "
            "equipment orders, or energy policy. In this article, the term is grounded by "
            "project and policy expectations rather than direct investment advice."
        ),
        example="원전주 강세 means nuclear-power-themed stocks rose.",
        contexts=(
            "원전주가 해외 프로젝트 수주 기대감으로 강세를 보였다.",
            "원전주 관련 종목이 에너지 정책 변화와 함께 상승했다.",
        ),
    ),
    CuratedTerm(
        normalized_term="방산주",
        english_term="defense-themed stock",
        category="theme_stock",
        definition=(
            "\"방산주\" means a Korean stock associated with defense equipment, weapons "
            "systems, or military export themes."
        ),
        explanation=(
            "\"방산주\" is used when Korean market articles group companies by defense "
            "orders, exports, or geopolitical demand. In this article, the term is grounded "
            "by defense-contract expectations, not by a recommendation."
        ),
        example="방산주 강세 means defense-themed stocks rallied.",
        contexts=(
            "방산주가 수출 계약 기대감과 지정학적 긴장으로 강세를 보였다.",
            "방산주 관련 종목이 국방 예산 확대 기대에 상승했다.",
        ),
    ),
)


def main() -> None:
    args = _parse_args()
    settings = get_settings()
    rows = build_dataset(settings.korean_financial_terms_seed_path)
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "schema_version": "korean-financial-term-llm-readiness/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_version": MODEL_PROMPT_VERSION,
        "recommended_train_model": "Qwen/Qwen3-0.6B-MLX-4bit LoRA",
        "recommended_serving_model": "Qwen3-0.6B GGUF Q4",
        "dataset_path": str(args.output_path),
        "sample_count": len(rows),
        "seed_term_count": len(_load_entries(settings.korean_financial_terms_seed_path)),
        "curated_unknown_term_count": len(CURATED_TERMS),
        "quality_status": "pass" if len(rows) >= 100 else "fail",
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["quality_status"] != "pass":
        raise SystemExit(1)


def build_dataset(seed_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for entry in _load_entries(seed_path):
        terms = _training_terms(entry.normalized_term, entry.aliases)
        for term in terms:
            for index, template in enumerate(CONTEXT_TEMPLATES):
                request = KoreanFinancialTermExplainRequest(
                    term=term,
                    title=f"{term} 관련 한국 증시 용어 설명",
                    context=template.format(term=term),
                    allow_web_search=True,
                )
                evidence = _context_evidence(request)
                target = GeneratedTermExplanation(
                    english_term=entry.english_term,
                    category=entry.category,
                    definition=entry.definition,
                    explanation=_two_sentence_explanation(entry.plain_explanation, term),
                    example=entry.example,
                    confidence_score=0.9,
                    evidence=evidence,
                    source="LOCAL_OPEN_SOURCE_LLM_RAG",
                )
                rows.append(
                    {
                        "term": term,
                        "sample_variant": index,
                        **LocalQwenTermExplanationProvider.training_example(
                            request,
                            evidence,
                            target,
                        ),
                    }
                )

    for term in CURATED_TERMS:
        contexts = (
            *term.contexts,
            *(template.format(term=term.normalized_term) for template in CONTEXT_TEMPLATES),
        )
        for index, context in enumerate(contexts):
            request = KoreanFinancialTermExplainRequest(
                term=term.normalized_term,
                title=f"{term.normalized_term} 관련 한국 증시 신조어 설명",
                context=context,
                allow_web_search=True,
            )
            evidence = _context_evidence(request)
            target = GeneratedTermExplanation(
                english_term=term.english_term,
                category=term.category,
                definition=term.definition,
                explanation=term.explanation,
                example=term.example,
                confidence_score=0.86,
                evidence=evidence,
                source="LOCAL_OPEN_SOURCE_LLM_RAG",
            )
            rows.append(
                {
                    "term": term.normalized_term,
                    "sample_variant": index,
                    **LocalQwenTermExplanationProvider.training_example(request, evidence, target),
                }
            )
    return rows


def _training_terms(normalized_term: str, aliases: tuple[str, ...]) -> tuple[str, ...]:
    terms = [normalized_term]
    terms.extend(alias for alias in aliases if _has_hangul(alias))
    deduped = []
    for term in terms:
        if term not in deduped:
            deduped.append(term)
    return tuple(deduped[:3])


def _two_sentence_explanation(explanation: str, term: str) -> str:
    sentences = [sentence.strip() for sentence in explanation.split(".") if sentence.strip()]
    if len(sentences) >= 2:
        return ". ".join(sentences[:2]) + "."
    return (
        f"{explanation.rstrip('.')} "
        f"In this article, \"{term}\" should be read as a Korean local-market term, "
        "not as a standalone investment recommendation."
    )


def _has_hangul(value: str) -> bool:
    return any("가" <= char <= "힣" for char in value)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Korean term Qwen3 SFT dataset.")
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
