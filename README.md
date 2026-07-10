# Hannah-Montana-AI

Hana OmniLens의 AI·규칙 처리 서버다. 뉴스·공시 분석, 글로벌 피어, 한국 금융 용어, 한국어→영어 번역, 외국인 보유 예측, 세무 OCR 검증을 제공한다.

## 고정 실행 경로

| 기능 | 실행 경로 | 주요 산출물 |
| --- | --- | --- |
| 한국 금융 용어 | 단일 검증 dictionary | `data/reference/korean_financial_terms_seed.json` |
| 글로벌 피어 설명 | grounded template | `global_peer_ml.joblib` |
| 뉴스 What/Why/Impact | rule engine | 코드 내 검증 규칙 |
| 한국어→영어 번역 | 로컬 Qwen 4B GGUF HTTP | `Qwen3-4B-GGUF-Q4` |
| 외국인 보유 예측 | stock-routed ML ensemble | `foreign_ownership_quantity_ml.joblib` |
| 세무 문서 OCR | Tesseract OCR + 문서별 parser/reviewer | `src/hanah_tax_ocr` |

실행 모드 선택값은 없다. 로컬 Docker와 배포 환경은 같은 경로를 사용한다. 번역 endpoint만 환경에 맞게 `HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT`로 지정한다.

## 주요 API

- `GET /health`
- `GET /ready`
- `POST /api/v1/alerts/analyze`
- `POST /api/v1/translation/ko-en`
- `POST /api/v1/market/global-peers/match`
- `POST /api/v1/korean-financial-terms/explain`
- `POST /api/v1/market/foreign-ownership/predict`
- `POST /api/v1/tax/documents/verify`

응답은 `success/status/code/message/data/timestamp` envelope을 사용한다.

## 로컬 실행

```bash
uv sync --all-groups
./scripts/run_qwen3_4b_gguf.sh
docker compose -f compose.local.yml up --build
curl http://localhost:8000/ready
```

Qwen GGUF 기본 경로는 `~/.cache/hana/models/Qwen3-4B-Q4_K_M.gguf`, 기본 endpoint는 `http://127.0.0.1:18081`이다.

## 검증

```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
```

## 문서

- [아키텍처](docs/ARCHITECTURE.md)
- [운영](docs/OPERATIONS.md)
- [테스트](docs/TESTING.md)
- [보안](docs/SECURITY.md)
- [모델 문서](docs/MODEL_CARD.md)
- [구현 기록](docs/IMPLEMENTATION_LOG.md)

