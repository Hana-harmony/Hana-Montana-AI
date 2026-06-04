# 운영

## 실행
```bash
uv sync --all-groups
uv run uvicorn hannah_montana_ai.main:app --reload
```

## 컨테이너
```bash
docker build -t hannah-montana-ai .
docker run --rm --network hana-internal hannah-montana-ai
```

## 네트워크 경계
- 협력사용 `OMNILENS_API_KEY`는 Hana-OmniLens-API에서만 검증한다.
- Hannah-Montana-AI는 별도 토큰을 받지 않는다.
- 운영 배포에서는 AI 컨테이너 포트를 외부에 publish하지 않는다.
- Spring 컨테이너와 AI 컨테이너만 같은 내부 네트워크에 둔다.

## 헬스체크
- `GET /health`

## 추론 audit log
- 분석 API는 요청마다 `hannah_montana_ai.audit.analysis` logger에 JSON audit log를 남긴다.
- 로그에는 `model_version`, `latency_ms`, 예측 이벤트·감성·중요도, 종목코드, 결과 상태를 기록한다.
- 원문 제목, snippet, URL은 로그에 남기지 않고 SHA-256 hash만 기록한다.
- 모델 artifact 누락 같은 실패도 `outcome=failure`, `failure_reason`으로 기록한다.

## 재학습 운영
- 외부 API 키는 `secrets.local.env`에서만 읽고 커밋하지 않는다.
- 필요한 수집 변수명은 `NAVER_NEWS_CLIENT_ID`, `NAVER_NEWS_CLIENT_SECRET`, `OPEN_DART_API_KEY`다.
- 수집 credential이 없으면 네트워크 요청 전에 실패하며, 오류에는 변수명만 남긴다.
- `scripts/collect_training_data.py`는 Naver News Search와 OpenDART에서 제목·snippet·링크만 수집한다.
- 국내주식 universe는 로컬 `OPEN_DART_API_KEY`로 동기화한다.
```bash
uv run python scripts/sync_stock_universe.py
uv run python scripts/build_stock_coverage_report.py
uv run python scripts/build_stock_training_candidate_queue.py
```
- 종목 universe 기반 Naver 수집은 아래처럼 실행한다. 전체 universe를 한 번에 수집하면 provider rate limit이 커지므로 운영에서는 일 단위 shard로 나눠 실행한다.
```bash
uv run python scripts/collect_training_data.py \
  --reuse-existing-raw \
  --use-stock-universe-news-queries \
  --stock-query-limit 200
```
- `data/raw`, `data/processed`는 학습 재현성에 필요한 데이터이므로 커밋한다.
- `data/curation/stock_training_candidate_queue.jsonl`은 사람 검수 전 후보 큐이며, 검수 없이 gold label로 승격하지 않는다.
- 외부 API 키, access token, 로컬 실행 비밀값은 학습 데이터에 포함하지 않는다.
- weak-label 후보는 teacher confidence gate와 라벨별 quota를 통과한 경우에만 pseudo-label로 승격한다.
- 현재 artifact는 37,278건 수집 후보 중 weak-label 360건과 종목 후보 큐 220건을 이벤트 모델 학습에 반영했다.
- 종목 후보 큐 승격분은 per-stock quota 1건으로 제한해 220건이 220개 종목에 분산되도록 한다.
- 감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 supervised corpus만으로 학습한다.

## 모델 release report
```bash
uv run python scripts/sync_stock_universe.py
uv run python scripts/build_stock_coverage_report.py
uv run python scripts/build_stock_training_candidate_queue.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_release_report.py
uv run python scripts/build_pseudo_label_monitoring_report.py
```

- `reports/model-release-report.json`은 모델 버전, 학습 샘플 수, pseudo-label 승격 내역, holdout·benchmark·실공시·실뉴스 quality gate를 한 파일로 묶는다.
- `overall_status`는 모든 quality gate와 pseudo-label consistency check가 통과할 때만 `pass`가 된다.
- release report는 `reports/ml-training-report.json`, `reports/ml-model-evaluation.json`, `reports/weak-distillation-report.json`에서 결정적으로 생성한다.

## Pseudo-label gate 모니터링
- `reports/pseudo-label-promotion-monitoring.json`은 raw 후보, 고신호 후보, teacher 탈락, quota 보류, 최종 승격 수를 funnel 형태로 기록한다.
- 현재 37,278건 raw 후보 중 4,845건이 고신호 후보이고, teacher gate에서 3,124건이 탈락하며 weak-label 360건과 종목 후보 220건만 student 이벤트 모델 학습에 승격된다.
- `RISK`, `CONTRACT`, `CORPORATE_ACTION`은 현재 effective quota가 채워진 active label이다.
- `CAPITAL_ACTION`, `DISCLOSURE`, `EARNINGS`, `MACRO`는 고신호 후보가 충분하지만 실제 뉴스 gold gate 실험 전까지 학습 투입을 보류한다.
- `GENERAL_MARKET`은 고신호 후보 풀이 작아 현재 확장 대상이 아니다.

## Coverage report 해석
- `reports/stock-coverage-report.json`의 `training_stock_count`와 `evaluation_stock_count`는 사람이 검수한 supervised/gold coverage다.
- `event_model_pseudo_training_coverage`는 teacher-gated event-model-only pseudo-label coverage다.
- 현재 event model pseudo training coverage는 220건, 220개 종목이며 supervised gold coverage로 간주하지 않는다.

## 운영 전 보강
- drift 감시
- supervised 학습 데이터 300개 이상 종목 coverage 확보
- evaluation gold 100개 이상 종목 coverage 확보
- 후보 큐 2,127개 종목에서 종목·라벨별 human review batch 운영
- 재학습 기준과 rollback 절차
- 배포 환경별 Secret Manager 연동 완료 후 secret rotation runbook 작성
