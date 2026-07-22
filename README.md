# Hannah-Montana-AI

Hana Harmony의 자체 금융 AI·규칙 추론 서버다. FastAPI로 뉴스·공시 분석, 한국어→영어 번역, 한국 금융 용어 해설, 글로벌 피어 매칭, 외국인 보유 예측, 거래 상태 해석, 세무 문서 OCR과 환급 케이스 판정을 제공한다. ChatGPT API에 의존하지 않는다.

운영 메트릭과 Discord 모델 이벤트는 [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md)를 따른다.

## 기능 및 모델

| 기능 | 현재 모델·엔진 | Serving API | 상세 문서 |
| --- | --- | --- | --- |
| 뉴스·공시 분석 | Hana Montana AI(KF-DeBERTa + K-FNSPID) + `financial_nlp_ml`, stock linker, 규칙 기반 What/Why/Impact | `POST /api/v1/alerts/analyze`, `/api/v1/intelligence/events` | [뉴스·공시 분석](docs/models/financial-alert-analysis.md), [K-FNSPID](docs/models/k-fnspid-market-impact.md), [도입 전후·연구 준비도](docs/models/k-fnspid-research-readiness.md) |
| 한국어→영어 번역 | 로컬 `Qwen3-4B-GGUF-Q4`, 문서 유형별 prompt와 완결성·용어 품질 gate | `POST /api/v1/translation/ko-en` | [한국어 전문 번역](docs/models/korean-translation.md) |
| 한국 금융 용어 | `k-finance-term-dictionary-v3`, 검증된 단일 사전과 evidence | `POST /api/v1/korean-financial-terms/explain` | [금융 용어 해설](docs/models/korean-financial-term-explainer.md) |
| 글로벌 피어 | `global-peer-dynamic-similarity-20260712095157`, 기업 설명 근거형 TF-IDF/SVD + 사업·재무·인지도 동적 랭커 | `POST /api/v1/market/global-peers/match` | [글로벌 피어](docs/models/global-peer-matcher.md) |
| 외국인 보유 예측 | `hannah-foreign-owned-quantity-ml-v2`, 종목별 walk-forward 선택 ensemble + 종목별 경험적 90% 예측 구간 | `POST /api/v1/market/foreign-ownership/predict` | [외국인 보유 예측](docs/models/foreign-ownership-forecast.md) |
| 주문 상태 해석 | `foreign-ownership-boundary-v1` + `krx-vi-price-limit-state-v1` 규칙 모델 | `POST /api/v1/stocks/order-status` | [주문 상태 모델](docs/models/order-status.md) |
| 세무 문서 OCR | `hanah-tax-ocr-e2e-review-v2`, Tesseract + 문서별 parser/reviewer + fraud gate | `POST /api/v1/tax/documents/verify` | [세무 OCR](docs/models/tax-document-ocr.md) |
| 세무 환급 케이스 | `us-treaty-refund-case-engine-v1`, 검증 문서·거래 입력 기반 결정 규칙 | `POST /api/v1/tax/refund-status` | [세무 환급 규칙](docs/models/tax-refund-case.md) |

## 핵심 동작

- 뉴스·공시는 종목 매핑, 이벤트 다중분류, 감성·중요도, confidence, 중복 키, What/Why/Impact, glossary를 생성한다.
- 감성 v6 후보는 K-FNSPID v4의 보호 연결요소를 제외한 1,118,291문서·62,468,526 토큰으로 KF-DeBERTa를 도메인 사전학습한 뒤, 이중 블라인드 receipt가 있는 학습 Gold 1,794건과 개발 Gold 895건을 사용한다. 원격 recipe·후보 잠금 뒤 NEWS 600건·DISCLOSURE 600건을 one-shot 평가한 층화가중 Accuracy/Macro-F1은 각각 0.7503/0.5530, 0.8646/0.6024다. 절대 gate와 공정 기준선·Holm 우월성 gate를 모두 통과하지 못해 `KEEP_CURRENT_MODEL`로 판정했으며 운영 모델은 바꾸지 않는다. 과거 공개 Test 932건의 0.8849는 반복 조회된 회귀 진단일 뿐 승격·통계적 우월성·SOTA 근거로 사용하지 않는다.
- 공시 의미 중요도는 Gold를 보지 않고 2026 Validation의 macro F1·Brier score로 제목+요약 입력을 선택한다. 모델 단독은 학습 URL 비중복 Gold 600건에서 accuracy 0.9850 / macro F1 0.9470, 코드북의 존속위험 floor를 포함한 운영 파이프라인은 기본·스트레스 Gold 910건에서 accuracy 0.9989 / macro F1 0.9962다. K-FNSPID v4 시장영향은 의미 등급과 confidence를 변경하지 않고 별도 제공한다.
- 시장영향은 국내 뉴스·국내 공시 KF-DeBERTa LoRA 전문가를 따로 학습·보정하고 요청 출처가 다르면 추론을 거부한다. 동일 K-FNSPID 시간 Test의 KR-FinBERT-SC 대비 Macro-F1은 국내 뉴스 0.3745 대 0.3506로 6.82%(+0.0239점) 높고 거래일 군집 신뢰구간으로 우위를 확인했다. 국내 공시는 0.3216 대 0.3131로 2.72%(+0.0085점) 높지만 신뢰구간이 0을 포함하고 QWK가 낮아 우위를 확정하지 않는다.
- K-FNSPID v4는 뉴스 524,696건·공시 722,989건, 총 1,247,685문서와 파일 기반 일별 시세 10,691,998행을 포함한다. 공시 실제 원문 8,972건을 연결하고 `data/k_fnspid/v4/manifest.json`에 파일 크기·SHA-256을 고정한다.
- 번역은 제목·요약·전문과 OpenDART 구조를 보존하며 실패나 품질 저하는 `SOURCE_LANGUAGE_FALLBACK`과 품질 플래그로 명시한다.
- 글로벌 피어는 KIS 활성 KOSPI·KOSDAQ·KONEX 일반주식 2,752개를 동적으로 추론하고 고정 종목별 peer anchor를 사용하지 않는다.
- 외국인 예측은 제한 종목의 전날까지 보유수량 시계열만 사용하며 결과를 주문 차단이 아닌 사전 고지 신호로 제공한다.
- 세무 OCR은 거주자 증명서, 아포스티유, 제한세율 적용신청서를 검증하고 제한세율 신청서의 생년월일·전화번호를 포함한 경정청구 공통 필드, 누락 필드·일관성·위변조 위험·수동 검수 필요 여부를 반환한다.
- 세무 환급 규칙은 모의 거래 입력에 대한 샌드박스 상태를 계산하며 실제 신고·정부 승인·지급·환수를 수행하지 않는다.

## API와 운영 경계

- 상태 확인: `GET /health`, `GET /ready`
- 공통 응답: `success/status/code/message/data/timestamp`
- 모델 학습·추론과 유지보수 재학습은 이 저장소가 담당한다.
- KIS·KRX·뉴스·공시 수집, 협력사 인증, 외부 REST/WebSocket 제공은 Hana-OmniLens-API가 담당한다.
- 최종투자자 파일 저장과 상태 관리는 Stock-exchange-BE가 담당한다.
- 운영 접근은 private network로 제한하고 외국인 모델 재학습 API에는 설정 시 유지보수 토큰을 요구한다.

## 로컬 실행과 검증

```bash
uv sync --all-groups
./scripts/run_qwen3_4b_gguf.sh
docker compose -f compose.local.yml up --build
curl http://localhost:8000/ready

uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
```

K-FNSPID v1–v4 Parquet, 파일 기반 일별 시세, DAPT pack과 외부 고정 원천은 Git에서 제외하지 않고 Git LFS pointer·객체 hash로 버전화한다. `data/k_fnspid/v4/manifest.json`의 원본 byte·SHA-256 검증을 추가로 통과해야 완전한 데이터셋으로 간주한다. `k-fnspid-v4.0.0` Release는 복구용 미러이며 Git/LFS 추적을 대체하지 않는다.

```bash
gh release download k-fnspid-v4.0.0 --repo Hana-harmony/Hana-Montana-AI --dir data/k_fnspid/v4 --pattern '*.parquet'
uv run python scripts/restore_k_fnspid_release.py
uv run python scripts/verify_k_fnspid_dataset.py
```

로컬과 운영 모두 Docker 내부망의 `http://hannah-qwen:8080`을 사용한다. 로컬 실행 전 `./scripts/download-qwen-model.sh ./models`로 hash 검증된 모델을 준비하고 공용 Docker network `hana-omnilens-internal`을 생성한다.

## 문서

- [아키텍처](docs/ARCHITECTURE.md)
- [API 표준](docs/API_STANDARD.md)
- [운영](docs/OPERATIONS.md)
- [보안](docs/SECURITY.md)
- [테스트](docs/TESTING.md)
- [모델 감사](docs/HANNAH_AI_MODEL_AUDIT.md)
- [K-FNSPID 도입 전후·연구 준비도](docs/models/k-fnspid-research-readiness.md)
- [K-FNSPID v4 Datasheet](docs/datasets/k-fnspid-v4-datasheet.md)
- [K-FNSPID v4 공시 주석 코드북](docs/datasets/k-fnspid-v4-annotation-codebook.md)
- [Hana Montana AI(KF-DeBERTa + K-FNSPID) Model Card](docs/models/hana-montana-ai-kf-deberta-k-fnspid.md)
- [구현 기록](docs/IMPLEMENTATION_LOG.md)

모델 상세는 `docs/models/`에서 기능별로 관리한다. 학습 데이터, artifact, 평가 지표 또는 serving 계약을 바꾸면 해당 상세 문서와 구현 기록을 함께 갱신한다.
