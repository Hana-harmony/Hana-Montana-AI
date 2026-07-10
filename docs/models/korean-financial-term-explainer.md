# 한국 금융 용어 해설 모델

## 목적
한국 뉴스·공시의 고유 금융 용어를 영어권 투자자가 이해할 수 있는 짧은 설명으로 변환한다.

## Serving
- `POST /api/v1/korean-financial-terms/explain`

## 입력
- 한국어 용어
- 문맥
- source type
- locale

## 출력
- 정규화 용어
- 영어 표현
- 짧은 설명
- evidence
- confidence
- cache 가능 여부

## 모델
- 버전: `k-finance-term-qwen3-rag-v1`
- 우선순위: seed dictionary -> local Qwen3 RAG -> review required
- 고빈도 테마/정책 표현은 dictionary-backed explanation으로 승격한다.
- `HANNAH_KOREAN_FINANCIAL_TERM_GENERATION_MODE=local_llm`이면 Qwen3 설명기를 실제 serving 경로에 연결한다.
- 로컬 개발은 endpoint 없이 `mlx-community/Qwen3-0.6B-4bit`와 `src/hannah_montana_ai/model_store/korean_term_qwen3_explainer_lora`를 직접 로드한다.
- 운영은 Qwen3-4B GGUF Q4를 띄우고 `HANNAH_KOREAN_FINANCIAL_TERM_LLM_ENDPOINT`로 연결한다.
- confidence 0.70 미만 또는 근거 부족 용어는 `REVIEW_REQUIRED`로 반환하고 cache하지 않는다.
- 일반 영어 금융 단어와 투자자 유형은 Qwen 후보로 보내지 않고 review 경로로 둔다.

## Retrieval/Review 정책
- `DICTIONARY`: 검증된 seed 용어를 즉시 반환하고 30일 cache 대상으로 둔다.
- `LOCAL_OPEN_SOURCE_LLM_RAG`: 기사 제목과 전문 evidence만으로 strict JSON 설명 후보를 생성한다.
- `UNVERIFIED_CONTEXT`: 근거 부족 용어는 텍스트만 보여주거나 검수 대상으로 보낸다.

## 평가
| 항목 | 값 |
| --- | ---: |
| 샘플 | 11 |
| 정확도 | 1.0000 |
| 사전 커버리지 | 0.9091 |
| Cache 가능률 | 0.9091 |
| Qwen3 SFT 샘플 | 362 |
| Qwen3 raw generation pass rate | 1.0000 |

## 산출물
- Evaluation report: `reports/korean-financial-term-explanation-eval.json`
- LLM readiness report: `reports/korean-financial-term-llm-readiness.json`
- Qwen3 training report: `reports/korean-term-qwen3-explainer-training.json`
- Qwen3 generation eval: `reports/korean-term-qwen3-generation-eval.json`
- Seed dictionary: `data/reference/korean_financial_terms_seed.json`
- Qwen3 SFT dataset: `data/training/korean_financial_term_explanation_sft.jsonl`
- Qwen3 MLX adapter: `src/hannah_montana_ai/model_store/korean_term_qwen3_explainer_lora/`
- Evaluation gold: `data/evaluation/korean_financial_term_explanation_gold.jsonl`
- Detailed design: `docs/KOREAN_FINANCIAL_TERM_RAG.md`

## 한계
- 신규 밈/테마 용어는 confidence가 낮으면 `REVIEW_REQUIRED`로 둔다.
- 검증되지 않은 문맥 해설은 cache하지 않는다.
