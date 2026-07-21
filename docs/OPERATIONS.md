# 운영

## 실행과 상태 확인

```bash
uv sync --all-groups
uv run uvicorn hannah_montana_ai.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

`/health`는 프로세스 liveness를, `/ready`는 모델 warm-up과 로컬 Qwen3 `/health`를 확인한다. 의존성이 준비되지 않으면 readiness는 503을 반환한다.

## 네트워크와 시크릿

- 운영 포트는 공개하지 않고 Hana-Omni-Connect-API와 같은 private network에서만 접근시킨다.
- 협력사 API key는 이 서비스로 전달하지 않는다.
- 뉴스·공시 수집 credential은 학습 수집 작업에서 gitignore된 환경 파일 또는 Secret Manager로 주입한다.
- 운영의 `HANNAH_AI_MAINTENANCE_TOKEN`은 OCI 최초 배포에서 생성한 `/opt/hana-runtime/root-secret`과 `hana/ai/maintenance-auth/v1` 라벨로 자동 파생한다. OmniConnect API도 같은 호스트 루트와 라벨을 사용하므로 GitHub에 공유 토큰을 등록하지 않는다. 로컬은 명시적으로 설정한 환경에서 외국인 모델 재학습 요청의 `X-HANNAH-AI-MAINTENANCE-TOKEN`을 검증한다.
- 세무 원본 파일과 뉴스 원문을 운영 로그에 기록하지 않는다.

## Serving 구성

- 뉴스·공시 분류와 stock linker는 versioned joblib artifact를 startup에 로드한다. 누락·손상 시 503으로 종료한다.
- What/Why/Impact는 검증 규칙으로 생성한다.
- 한국어→영어 번역은 같은 Docker 내부망의 `http://hannah-qwen:8080` Qwen3-4B GGUF 서버를 사용한다. Qwen은 3 OCPU 상한과 병렬 슬롯 2개로 운영하고 장문 요청 timeout은 600초로 둔다.
- Qwen 모델은 공식 revision과 SHA-256을 고정해 최초 배포 시 내려받고, 병렬 번역의 실측 최대 사용량을 수용하는 10GB 메모리 한도와 번역 청크에 충분한 4K context로 운영한다.
- 글로벌 피어는 동적 similarity artifact와 `grounded-template-structured-rag-v3` 설명 템플릿을 사용한다.
- 한국 금융 용어는 `data/reference/korean_financial_terms_seed.json` 단일 사전을 사용한다.
- 외국인 보유 예측은 제한 종목 allowlist와 보유수량 시계열 artifact를 사용한다.
- 세무 OCR은 `hanah_tax_ocr` pipeline에서 형식 검사, OCR, parser, reviewer를 순서대로 실행한다.

환경별 조정값은 endpoint, timeout, token 수, 동시성, artifact 경로다. 모델 유형을 런타임 플래그로 교체하지 않는다.

## 외국인 보유 모델 재학습

`POST /api/v1/market/foreign-ownership/model/retrain`은 OmniConnect가 보낸 제한 종목 history를 임시 위치에서 학습한다.

- walk-forward와 persistence guard를 통과한 후보만 `promoted`로 처리한다.
- promotion은 학습 CSV, 제한 종목 목록, joblib artifact와 training report를 원자적으로 교체한다.
- promotion 후 prediction service cache를 비운다.
- gate 실패는 `guarded` 후보 report만 저장하고 운영 artifact를 유지한다.
- 학습 중 동시 요청은 lock으로 직렬화한다.

## 데이터·모델 갱신

| 대상 | 명령 |
| --- | --- |
| 국내 종목 universe | `uv run python scripts/sync_stock_universe.py` |
| 미국 종목 universe·재무 | `sync_us_stock_universe.py`, `sync_global_peer_fundamentals.py` |
| 국내 업종·사업 프로필 | `sync_korea_stock_industries.py`, `sync_korea_company_profiles.py` |
| 뉴스·공시 모델 | `train_ml_model.py`, `evaluate_ml_model.py`, `build_model_release_report.py` |
| stock linker | `train_stock_linker_model.py` |
| 글로벌 피어 | `train_global_peer_model.py`, `build_global_peer_full_coverage_report.py` |
| 외국인 보유 | `train_foreign_ownership_quantity_model.py`, `benchmark_foreign_ownership_quantity_models.py` |
| 금융 용어 | `evaluate_korean_financial_term_explainer.py` |

동기화·학습 작업은 기존 artifact를 직접 덮어쓰기 전에 생성 report와 diff를 검토한다. 활성 KIS universe 수, 모델 universe 수와 전종목 coverage가 일치해야 글로벌 피어 artifact를 승격한다.

## 관측과 실패 처리

- 분석 audit는 요청 원문 대신 SHA-256 hash, model version, latency, 성공·실패 사유를 기록한다.
- 번역 로그는 원문 hash, 입력·출력 길이, provider, 상태와 제한된 품질 플래그를 기록한다.
- model version, provider, confidence와 fallback 상태는 API payload에 포함한다.
- 번역 품질 실패는 `SOURCE_LANGUAGE_FALLBACK`, OCR 불가 입력은 수동 검수 또는 거절 상태, 모델 artifact 장애는 503으로 노출한다.
- 글로벌 피어는 더미 peer를 생성하지 않는다.

## 배포와 rollback

CI의 ruff, mypy, bandit, secret hygiene와 pytest가 모두 통과한 이미지를 배포한다. 서버의 GHCR pull 인증은 GitHub Secret `GHCR_TOKEN`만 사용하며 배포가 GitHub API로 token 소유자를 검증해 사용자명을 자동 결정한다. `GHCR_USERNAME` Secret은 등록하지 않는다. OCI SSH는 `PROD_SSH_KEY` 인증 뒤 `PROD_SSH_PASSWORD`를 요구하고 `PROD_HOST_KEY`로 서버를 고정한다. 비밀번호는 배포 단계의 마스킹된 환경변수와 OpenSSH `SSH_ASKPASS`로만 전달하며 파일·명령 인자·로그에 기록하지 않는다. container는 non-root 사용자로 실행하고 artifact는 read-only로 제공한다. 운영 앱은 단일 컨테이너로 교체하며 readiness 실패 시 직전 이미지를 자동 복구한다. Nginx는 Ubuntu 호스트의 systemd 서비스로 운영한다.

rollback은 이전에 검증을 통과한 이미지와 그 이미지에 포함된 model artifact·report를 함께 복원한다. 코드와 artifact version을 따로 되돌리지 않는다.

`/opt/hana-runtime/root-secret`은 재배포 시 유지하고 권한을 `600`으로 제한한다. 해당 파일을 잃으면 OmniConnect 포털 암호화 데이터와 연계된 파생키도 복구할 수 없으므로 OCI 암호화 볼륨 백업에 포함한다.
