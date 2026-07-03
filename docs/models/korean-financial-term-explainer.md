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

## 평가
| 항목 | 값 |
| --- | ---: |
| 샘플 | 11 |
| 정확도 | 1.0000 |
| 사전 커버리지 | 0.9091 |
| Cache 가능률 | 0.9091 |

## 산출물
- Evaluation report: `reports/korean-financial-term-explanation-eval.json`
- Detailed design: `docs/KOREAN_FINANCIAL_TERM_RAG.md`

## 한계
- 신규 밈/테마 용어는 confidence가 낮으면 `REVIEW_REQUIRED`로 둔다.
- 검증되지 않은 문맥 해설은 cache하지 않는다.
