# 한국 금융 용어 해설 RAG 엔진

## 목적

현지 거래소 앱에서 한국 뉴스 전문의 고유 금융 용어를 클릭했을 때 외국인 투자자가 이해할 수 있는 짧은 영어 설명을 제공한다. 검증된 사전은 우선 사용하고, 미등록 한글 용어는 기사 근거를 붙여 Qwen3-0.6B LoRA 설명기로 생성한다.

## Serving 경로

1. `DICTIONARY`
   - `data/reference/korean_financial_terms_seed.json`의 검증된 seed 용어를 즉시 반환한다.
   - `cacheable=true`, TTL 30일이다.
2. `INTERNAL_CONTEXT_RAG`
   - 기사 제목과 전문에서 클릭 용어가 포함된 문장을 evidence로 붙인다.
   - 사전 미등록이고 생성 provider가 없으면 확정 설명을 제공하지 않는다.
3. `LOCAL_OPEN_SOURCE_LLM_RAG`
   - `HANNAH_KOREAN_FINANCIAL_TERM_GENERATION_MODE=local_llm`에서 사용한다.
   - 로컬 개발은 `mlx-community/Qwen3-0.6B-4bit`와 `src/hannah_montana_ai/model_store/korean_term_qwen3_explainer_lora`를 직접 로드한다.
   - 운영 t4g.medium은 Qwen3-0.6B GGUF Q4를 llama.cpp OpenAI-compatible sidecar로 띄우고 `HANNAH_KOREAN_FINANCIAL_TERM_LLM_ENDPOINT`로 연결한다.
   - strict JSON, 한글 클릭 용어 포함, 2문장 설명, 투자 조언 금지, 일반 영어 금융 단어 제외 gate를 통과해야 노출한다.
4. `OPENAI_WEB_SEARCH_RAG`
   - local LLM 모드가 아니고 `HANNAH_OPENAI_TERM_EXPLANATION_ENABLED=true`, `OPENAI_API_KEY`가 있을 때만 사용한다.
   - OpenAI Responses API web search 결과와 기사 문맥을 근거로 설명 후보를 생성한다.
   - confidence 0.70 이상만 사용자 설명으로 노출하고, 그 미만은 검수 대상으로 둔다.
5. `UNVERIFIED_CONTEXT`
   - 근거가 부족한 신조어는 `REVIEW_REQUIRED`로 반환한다.
   - OmniLens API는 이 응답을 사용자 확정 툴팁으로 캐시하지 않는다.

## 운영 원칙

- known term은 LLM 호출 없이 사전/캐시로 응답한다.
- unknown 한글 용어는 클릭 로그와 문맥을 모은 뒤 local Qwen3 RAG로 후보 설명을 생성한다.
- `earnings`, `Foreign investors` 같은 일반 영어 단어와 투자자 유형은 glossary term으로 승격하지 않는다.
- 투자 조언성 표현은 품질 게이트에서 낮은 confidence로 강등한다.
- API 프로세스 안에서 운영 LLM을 직접 적재하지 않는다. t4g.medium에서는 별도 Qwen3 GGUF sidecar를 두고 HTTP endpoint로만 호출한다.
- OpenAI web search는 local LLM 모드를 쓰지 않는 환경의 보조 fallback으로만 남긴다.

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
- `source`: `DICTIONARY`, `LOCAL_OPEN_SOURCE_LLM_RAG`, `OPENAI_WEB_SEARCH_RAG`, `UNVERIFIED_CONTEXT`
- `display_mode`: `EXPLANATION`, `REVIEW_REQUIRED`, `TEXT_ONLY`
- `cacheable`, `cache_ttl_seconds`: OmniLens 캐시 정책
- `evidence`: 사전 또는 기사/웹검색 근거
- `quality_flags`: 운영 검수 플래그

## 평가

평가 명령:

```bash
uv run python scripts/evaluate_korean_financial_term_explainer.py
uv run python scripts/build_korean_financial_term_llm_dataset.py
uv run --extra llm-training python scripts/train_korean_term_qwen3_explainer.py
uv run --extra llm-training python scripts/evaluate_korean_term_qwen3_generation.py --min-pass-rate 1.0
```

현재 리포트:

- `reports/korean-financial-term-explanation-eval.json`
- `reports/korean-financial-term-llm-readiness.json`
- `reports/korean-term-qwen3-explainer-training.json`
- `reports/korean-term-qwen3-generation-eval.json`
- 사전/unknown 계약 샘플 수: 11
- 정확도: 1.0
- 사전 커버리지: 0.909091
- Qwen3 SFT 샘플 수: 362
- Qwen3 raw generation pass rate: 1.0
- 품질 게이트: pass

## 한계와 다음 개선

- seed 사전은 초기 high-frequency 용어 중심이다.
- 실제 신조어 품질은 OmniLens 클릭 로그와 local Qwen3 sidecar 응답을 함께 보며 주기적으로 평가해야 한다.
- 다음 단계에서 OmniLens API가 클릭 카운트, 캐시, unknown 후보 승격 정책을 영속화한다.
