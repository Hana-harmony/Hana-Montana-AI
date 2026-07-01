# 한국 금융 용어 해설 RAG 엔진

## 목적

현지 거래소 앱에서 한국 뉴스 전문의 고유 금융 용어를 클릭했을 때 외국인 투자자가 이해할 수 있는 짧은 영어 설명을 제공한다. LLM은 매 요청마다 호출하지 않고 사전, 내부 문맥 RAG, 웹검색 RAG, 캐시 정책을 순서대로 적용해 비용과 지연을 낮춘다.

## Serving 경로

1. `DICTIONARY`
   - `data/reference/korean_financial_terms_seed.json`의 검증된 seed 용어를 즉시 반환한다.
   - `cacheable=true`, TTL 30일이다.
2. `INTERNAL_CONTEXT_RAG`
   - 기사 제목과 전문에서 클릭 용어가 포함된 문장을 evidence로 붙인다.
   - 사전 미등록이고 외부 provider가 없으면 확정 설명을 제공하지 않는다.
3. `OPENAI_WEB_SEARCH_RAG`
   - `HANNAH_OPENAI_TERM_EXPLANATION_ENABLED=true`와 `OPENAI_API_KEY`가 있을 때만 사용한다.
   - OpenAI Responses API web search 결과와 기사 문맥을 근거로 설명을 생성한다.
   - confidence 0.70 이상만 사용자 설명으로 노출하고, 그 미만은 검수 대상으로 둔다.
4. `UNVERIFIED_CONTEXT`
   - 근거가 부족한 신조어는 `REVIEW_REQUIRED`로 반환한다.
   - OmniLens API는 이 응답을 사용자 확정 툴팁으로 캐시하지 않는다.

## 운영 원칙

- known term은 LLM 호출 없이 사전/캐시로 응답한다.
- unknown term은 클릭 로그와 문맥을 모은 뒤 웹검색 RAG로 후보 설명을 생성한다.
- 투자 조언성 표현은 품질 게이트에서 낮은 confidence로 강등한다.
- t4g.medium 운영 서버는 자체 LLM 실시간 추론을 하지 않는다. Qwen은 로컬/배치 검수와 사전 확장 후보 생성에 사용한다.
- OpenAI web search는 신규 신조어 최초 설명 생성과 근거 수집에만 사용한다.

## API

`POST /api/v1/korean-financial-terms/explain`

요청 핵심 필드:

- `term`: 클릭된 한국어 용어
- `title`: 뉴스/공시 제목
- `context`: 용어가 등장한 주변 전문
- `stock_code`, `stock_name`: 종목 상세 문맥
- `article_id`, `article_url`: 로그와 evidence 연결키
- `allow_web_search`: 신조어 fallback 허용 여부

응답 핵심 필드:

- `explanation`: 외국인 투자자용 해설
- `source`: `DICTIONARY`, `INTERNAL_CONTEXT_RAG`, `OPENAI_WEB_SEARCH_RAG`, `UNVERIFIED_CONTEXT`
- `display_mode`: `EXPLANATION`, `REVIEW_REQUIRED`, `TEXT_ONLY`
- `cacheable`, `cache_ttl_seconds`: OmniLens 캐시 정책
- `evidence`: 사전 또는 기사/웹검색 근거
- `quality_flags`: 운영 검수 플래그

## 평가

평가 명령:

```bash
uv run python scripts/evaluate_korean_financial_term_explainer.py
```

현재 리포트:

- `reports/korean-financial-term-explanation-eval.json`
- 샘플 수: 8
- 정확도: 1.0
- 사전 커버리지: 0.875
- 캐시 가능률: 0.875
- 품질 게이트: pass

## 한계와 다음 개선

- seed 사전은 초기 high-frequency 용어 중심이다.
- 실제 신조어 품질은 OmniLens 클릭 로그와 OpenAI web search evidence가 축적된 뒤 평가해야 한다.
- 다음 단계에서 OmniLens API가 클릭 카운트, 캐시, unknown 후보 승격 정책을 영속화한다.
