# Hannah-Montana-AI

Hana OmniLens의 AI 모델 API 서버다. 뉴스·공시 분석만 담당하는 NLP 서버가 아니라, 외국인 보유 예측, 글로벌 피어 매칭, 한국 금융 용어 해설, 세무/문서 규칙 모델까지 제공한다.

## 핵심 기능
- 뉴스·공시 분석: 종목 매핑, 이벤트 태그, 감성, 중요도, What/Why/Impact 요약, 중복 키
- 외국인 보유 예측: 제한 종목의 다음 거래일 외국인 보유수량과 한도소진율 boundary 예측
- 글로벌 피어: 한국 상장사와 유사한 미국 상장 peer, headline, summary, matched factors 생성
- 한국 금융 용어: 사전/RAG 기반 영어 해설, evidence, confidence, cache 정책
- 주문/세무 보조: order status, tax refund status, Hana Tax OCR 기반 tax document verification 응답

## 모델 스택
| 기능 | 주요 모델/기법 | Artifact |
| --- | --- | --- |
| 뉴스·공시 분석 | TF-IDF char/word n-gram, 한국 금융 token, One-vs-Rest/다중분류 Logistic Regression, TF-IDF stock linker | `financial_nlp_ml.joblib`, `stock_linker_ml.joblib` |
| 외국인 보유 예측 | `stock_routed_ml_ensemble`, Ridge/HistGradientBoosting/ExtraTrees/residual/hurdle 후보, walk-forward validation, N-HiTS/PatchTST SOTA 진단 | `foreign_ownership_quantity_ml.joblib` |
| 글로벌 피어 매칭 | TF-IDF retrieval, SVD semantic embedding, business profile Logistic Regression, pairwise LogisticRegression reranker, optional Qwen3-0.6B MLX/sidecar LoRA 설명기 | `global_peer_ml.joblib`, `global_peer_qwen3_explainer_lora/` |
| 한국 금융 용어 | seed dictionary, 내부 문맥 RAG, OpenAI web search fallback, Qwen 로컬/배치 후보 생성 | `k-finance-term-rag-v2` |
| 세무 문서 OCR | `hanah_tax_ocr` parser/reviewer, 문서별 필드 추출, 위변조/필수필드 gate, 텍스트 payload fallback | `src/hanah_tax_ocr/` |

## API
- `GET /health`
- `GET /ready`
- `POST /api/v1/alerts/analyze`
- `POST /api/v1/market/foreign-ownership/predict`
- `POST /api/v1/market/foreign-ownership/model/retrain`
- `POST /api/v1/market/global-peers/match`
- `POST /api/v1/korean-financial-terms/explain`
- `POST /api/v1/intelligence/events`
- `POST /api/v1/stocks/order-status`
- `POST /api/v1/tax/documents/verify`
- `POST /api/v1/tax/refund-status`

응답은 `success/status/code/message/data/timestamp` 공통 envelope을 사용한다.

## 실행
```bash
uv sync --all-groups
uv run pytest
uv run uvicorn hannah_montana_ai.main:app --reload
```

Docker:
```bash
docker compose -f compose.local.yml up --build
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
```

## 모델 문서
- [뉴스·공시 분석 모델](docs/models/financial-alert-analysis.md)
- [외국인 보유 예측 모델](docs/models/foreign-ownership-forecast.md)
- [글로벌 피어 매칭 모델](docs/models/global-peer-matcher.md)
- [한국 금융 용어 해설 모델](docs/models/korean-financial-term-explainer.md)
- [모델 문서 인덱스](docs/MODEL_CARD.md)

## 보안 경계
- 협력사용 `OMNILENS_API_KEY`를 요구하거나 저장하지 않는다.
- 외부 provider credential은 학습/수집 스크립트의 로컬 secret 파일에서만 읽고 커밋하지 않는다.
- 운영에서는 외부에 포트를 직접 공개하지 않고 Spring 서비스가 접근하는 내부 네트워크에 둔다.

## 문서
- [아키텍처](docs/ARCHITECTURE.md)
- [운영](docs/OPERATIONS.md)
- [테스트](docs/TESTING.md)
- [보안](docs/SECURITY.md)
- [구현 기록](docs/IMPLEMENTATION_LOG.md)
- [AI 모델 감사](docs/HANNAH_AI_MODEL_AUDIT.md)
