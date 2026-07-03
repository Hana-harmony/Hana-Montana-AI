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
- 버전: `k-finance-term-rag-v2`
- 우선순위: seed dictionary -> 내부 문맥 RAG -> web search fallback -> review required
- 고빈도 테마/정책 표현은 dictionary-backed explanation으로 승격한다.
- 운영 실시간 serving은 자체 LLM을 직접 로드하지 않는다.
- Qwen은 로컬/배치 검수와 seed dictionary 확장 후보 생성에만 사용한다.
- OpenAI web search fallback은 `HANNAH_OPENAI_TERM_EXPLANATION_ENABLED=true`와 `OPENAI_API_KEY`가 있을 때만 사용한다.
- confidence 0.70 미만 또는 근거 부족 용어는 `REVIEW_REQUIRED`로 반환하고 cache하지 않는다.

## Retrieval/Fallback 정책
- `DICTIONARY`: 검증된 seed 용어를 즉시 반환하고 30일 cache 대상으로 둔다.
- `INTERNAL_CONTEXT_RAG`: 기사 제목과 전문에서 용어 포함 문장을 evidence로 붙인다.
- `OPENAI_WEB_SEARCH_RAG`: 신규 신조어 설명 후보를 만들되 confidence gate를 통과한 경우만 노출한다.
- `UNVERIFIED_CONTEXT`: 근거 부족 용어는 텍스트만 보여주거나 검수 대상으로 보낸다.

## 평가
| 항목 | 값 |
| --- | ---: |
| 샘플 | 11 |
| 정확도 | 1.0000 |
| 사전 커버리지 | 0.9091 |
| Cache 가능률 | 0.9091 |

## 산출물
- Evaluation report: `reports/korean-financial-term-explanation-eval.json`
- Seed dictionary: `data/reference/korean_financial_terms_seed.json`
- Evaluation gold: `data/evaluation/korean_financial_term_explanation_gold.jsonl`
- Detailed design: `docs/KOREAN_FINANCIAL_TERM_RAG.md`

## 한계
- 신규 밈/테마 용어는 confidence가 낮으면 `REVIEW_REQUIRED`로 둔다.
- 검증되지 않은 문맥 해설은 cache하지 않는다.
