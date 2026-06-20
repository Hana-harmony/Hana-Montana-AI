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
- 로컬에서는 `secrets.local.env.example`을 기준으로 `secrets.local.env`를 만들고 실제 credential은 해당 파일에만 작성한다.
- 필요한 수집 변수명은 `NAVER_NEWS_CLIENT_ID`, `NAVER_NEWS_CLIENT_SECRET`, `OPEN_DART_API_KEY`다.
- 수집 credential이 없으면 네트워크 요청 전에 실패하며, 오류에는 변수명만 남긴다.
- `scripts/collect_training_data.py`는 Naver News Search와 OpenDART에서 제목·snippet·링크만 수집한다.
- 국내주식 universe는 로컬 `OPEN_DART_API_KEY`로 동기화한다.
- 분석 API는 `data/reference/korea_stock_universe.csv`를 내부 종목 master로 로드하므로 배포 artifact에 이 파일을 포함해야 한다.
- 분석 API는 `src/hannah_montana_ai/model_store/stock_linker_ml.joblib`도 함께 로드하므로 배포 artifact에 stock linker 모델을 포함해야 한다.
- Spring client가 넘기는 `stock_universe`는 후보 우선순위와 alias 보강 용도이며, 전체 종목 master를 매 요청마다 전달하지 않는다.
```bash
uv run python scripts/sync_stock_universe.py
uv run python scripts/build_stock_coverage_report.py
uv run python scripts/build_stock_collection_shard_plan.py
uv run python scripts/build_stock_training_candidate_queue.py
uv run python scripts/build_stock_gold_review_batch.py
uv run python scripts/validate_stock_gold_review_batch.py
uv run python scripts/build_stock_gold_active_review_report.py
uv run python scripts/promote_stock_gold_review_batch.py
uv run python scripts/train_stock_linker_model.py
```
- 실시간 뉴스 smoke/drift 배치는 라벨 없는 운영 표본을 만든다. 이 결과는 `final_*` 라벨을 채워 gold로 승격하기 전까지 F1이 아니라 confidence, 종목 매칭, drift 점검용이다.
```bash
uv run python scripts/build_live_news_evaluation_batch.py \
  --stock-sample-size 50 \
  --max-news-per-query 3
uv run python scripts/build_live_news_monitoring_status.py
uv run python scripts/build_translation_sample_report.py --sample-limit-per-source 5
```
- `reports/live-news-monitoring-status.json`은 `reports/live-news-evaluation-report.json`이 현재 release 모델 버전, row/report schema, confidence summary를 만족하는지 검증한다. `overall_status=stale`이면 최신 모델 품질 근거로 쓰지 않고 운영 credential이 있는 환경에서 실시간 뉴스 배치를 다시 생성한다.
- 종목 universe 기반 Naver 수집은 아래처럼 실행한다. 전체 universe를 한 번에 수집하면 provider rate limit이 커지므로 운영에서는 일 단위 shard로 나눠 실행한다.
```bash
uv run python scripts/collect_training_data.py \
  --reuse-existing-raw \
  --use-stock-universe-news-queries \
  --stock-query-limit 200
```
- 누락 종목 우선 shard 수집은 아래 순서로 실행한다. shard plan은 supervised/evaluation gold와 후보 큐가 모두 비어 있는 종목을 먼저 골라 Naver 쿼리 묶음으로 만든다.
```bash
uv run python scripts/build_stock_collection_shard_plan.py
uv run python scripts/collect_training_data.py \
  --reuse-existing-raw \
  --stock-collection-plan data/curation/stock_collection_shard_plan.jsonl \
  --stock-collection-plan-shard-index 0
```
- `reports/stock-collection-shard-plan.json`은 현재 누락 후보 458개 종목, 5개 shard, 2,290개 Naver 쿼리를 기록한다.
- `data/raw`, `data/processed`는 학습 재현성에 필요한 데이터이므로 커밋한다.
- `data/curation/stock_training_candidate_queue.jsonl`은 사람 검수 전 후보 큐이며, 검수 없이 gold label로 승격하지 않는다.
- `data/curation/stock_gold_training_review_batch.jsonl`와 `data/curation/stock_gold_evaluation_review_batch.jsonl`은 후보 큐에서 뽑은 사람 검수용 배치다.
- `reports/translation-sample-report.json`은 실제 뉴스·공시 gold 표본의 원문, Hannah 로컬 금융용어 번역 보조, AI 분석 결과, glossary, review finding을 함께 기록한다. DeepL/Papago live provider 결과는 Hana-OmniLens-API smoke 산출물과 `external_translation_join_key`로 조인해 비교한다.
- 검수 배치는 학습 300개 종목, 평가 100개 종목 목표로 생성하지만 `review_status=needs_human_review`인 동안 supervised/gold 정답셋으로 사용하지 않는다.
- 사람이 승인한 row는 `review_status=human_review_approved`, Codex 대리 검수 row는 `review_status=codex_review_approved`로 두고 `reviewer_id`, `reviewed_at`, `final_tags`, `final_sentiment`, `final_importance`를 모두 채운 뒤 승격 스크립트를 실행한다.
- coverage packet은 `scripts/approve_stock_gold_coverage_with_codex.py`로 Codex 대리 승인할 수 있으며, 6자리 숫자 종목코드가 아닌 row는 같은 split/wave의 유효 종목 후보로 backfill한다.
- `scripts/validate_stock_gold_review_batch.py`를 먼저 실행해 승인 가능한 학습 300개 종목, 평가 100개 종목 목표를 만족하는지 확인한다.
- `scripts/build_stock_gold_active_review_report.py`는 모델 제안 라벨과 불확실성으로 사람이 먼저 볼 row를 정렬한다.
- 승격 스크립트는 승인 row만 `data/training/financial_alert_stock_review_gold.jsonl`와 `data/evaluation/financial_alert_stock_review_gold.jsonl`에 기록한다.
- 유효 6자리 국내주식 전체 reference coverage는 `scripts/build_full_universe_codex_stock_review_gold.py`로 보강한다. 이 스크립트는 stock review gold train/eval 합집합에 없는 종목만 `codex_review_approved` reference row로 추가하고 `reports/full-universe-codex-coverage-report.json`에 누락 수를 기록한다.
- 외부 API 키, access token, 로컬 실행 비밀값은 학습 데이터에 포함하지 않는다.
- weak-label 후보는 teacher confidence gate와 라벨별 quota를 통과한 경우에만 pseudo-label로 승격한다.
- 현재 artifact는 68,710건 수집 후보 중 weak-label 344건과 종목 후보 큐 781건을 이벤트 모델 학습에 반영했다.
- 종목 후보 큐 승격분은 per-stock quota 1건으로 제한해 781건이 781개 종목에 분산되도록 한다.
- 감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 supervised corpus만으로 학습한다.

## 모델 release report
```bash
uv run python scripts/sync_stock_universe.py
uv run python scripts/build_stock_coverage_report.py
uv run python scripts/build_stock_collection_shard_plan.py
uv run python scripts/build_stock_training_candidate_queue.py
uv run python scripts/build_stock_gold_review_batch.py
uv run python scripts/validate_stock_gold_review_batch.py
uv run python scripts/build_stock_gold_active_review_report.py
uv run python scripts/promote_stock_gold_review_batch.py
uv run python scripts/build_full_universe_codex_stock_review_gold.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_confidence_calibration_report.py
uv run python scripts/build_stock_candidate_quota_experiment.py
uv run python scripts/build_model_release_report.py
uv run python scripts/build_pseudo_label_monitoring_report.py
```

- `reports/model-release-report.json`은 모델 버전, 학습 샘플 수, pseudo-label 승격 내역, holdout·benchmark·실공시·실뉴스 quality gate를 한 파일로 묶는다.
- `reports/model-confidence-calibration.json`은 평가셋별 이벤트 확률 calibration, 감성·중요도 top confidence calibration, 고신뢰 오답을 기록한다.
- `reports/stock-candidate-quota-experiment.json`은 stock candidate pseudo-label quota profile별 임시 재학습 결과와 gold gate 통과 여부를 기록한다.
- `overall_status`는 모든 quality gate와 pseudo-label consistency check가 통과할 때만 `pass`가 된다.
- release report는 `reports/ml-training-report.json`, `reports/ml-model-evaluation.json`, `reports/weak-distillation-report.json`에서 결정적으로 생성한다.

## Pseudo-label gate 모니터링
- `reports/pseudo-label-promotion-monitoring.json`은 raw 후보, 고신호 후보, teacher 탈락, quota 보류, 최종 승격 수를 funnel 형태로 기록한다.
- 현재 68,710건 raw 후보 중 5,204건이 고신호 후보이고, teacher gate에서 4,007건이 탈락하며 weak-label 344건과 종목 후보 781건만 student 이벤트 모델 학습에 승격된다.
- `RISK`, `CONTRACT`, `CORPORATE_ACTION`, `EARNINGS`, `MACRO`는 현재 active label이며 quota 여유가 남아 추가 후보 품질을 모니터링한다.
- `CAPITAL_ACTION`은 현재 quota를 채웠고, `DISCLOSURE`는 실제 뉴스 gold gate 실험 전까지 학습 투입을 보류한다.
- `GENERAL_MARKET`은 고신호 후보 풀이 작아 현재 확장 대상이 아니다.

## Coverage report 해석
- `reports/stock-coverage-report.json`의 `training_stock_count`와 `evaluation_stock_count`는 승인된 stock review gold를 포함한 supervised/reference coverage다.
- `reports/full-universe-codex-coverage-report.json`은 유효 6자리 국내주식 3,920개가 stock review gold train/eval reference coverage에 모두 포함되는지 검증한다.
- `codex_review_approved` full-universe reference row는 커밋된 coverage lineage로 쓰지만, self-training feedback loop를 막기 위해 supervised loss에서는 제외한다.
- `event_model_pseudo_training_coverage`는 teacher-gated event-model-only pseudo-label coverage다.
- 현재 event model pseudo training coverage는 781건, 781개 종목이며 supervised/reference coverage와 별도로 해석한다.
- `reports/model-release-report.json`의 `service_readiness`는 bootstrap 운영 판단이며, release quality gate와 stock-candidate pseudo coverage를 기준으로 한다.
- `audited_gold_readiness`는 `human_review_approved` 또는 `codex_review_approved` coverage gold 기준이며, bootstrap 운영 판단과 별도로 관리한다.
- `reports/stock-collection-shard-plan.json`은 candidate queue, supervised training gold, evaluation gold가 모두 없는 종목을 shard 단위 수집 대상으로 기록한다.
- 현재 shard plan은 351개 `no_raw_no_candidate` 종목과 107개 `raw_without_candidate` 종목을 우선 수집 대상으로 둔다.
- `reports/stock-candidate-quota-experiment.json`은 calibrated current release 781건/781종목이 gate를 통과했고, risk/contract 확장 profile은 895건/709종목까지 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못했음을 기록한다.
- `reports/stock-gold-review-batch-report.json`은 학습 검수 배치 300개 종목과 평가 검수 배치 100개 종목을 기록한다.
- 검수 배치의 학습·평가 종목은 서로 겹치지 않으며, 사람이 승인하기 전까지 coverage gate 통과 수치에 포함하지 않는다.
- `reports/stock-gold-review-validation-report.json`은 현재 검수 배치에서 승격 가능한 승인 row가 학습 300개 종목, 평가 100개 종목 목표를 만족하는지 기록한다.
- `reports/stock-gold-active-review-report.json`은 모델 제안 라벨과 신뢰도 기반 검수 우선순위를 기록하지만, 사람 승인 없이 gold로 승격하지 않는다.
- `reports/stock-gold-promotion-report.json`은 `human_review_approved` 또는 `codex_review_approved` row 중 검수자 메타데이터와 최종 라벨이 모두 있는 row만 supervised/evaluation gold 출력으로 승격했는지 기록한다.
- 승인 상태지만 필수 검수 필드가 빠진 row는 `rejected_approved_count_by_reason`에 사유별로 집계한다.

## 운영 전 보강
- drift 감시
- full-universe Codex reference coverage 누락 0 유지
- 사람이 검수한 supervised/evaluation gold label 증분 확대
- 후보 큐 3,506개 종목에서 종목·라벨별 human review batch 운영
- 재학습 기준과 rollback 절차
- 배포 환경별 Secret Manager 연동 완료 후 secret rotation runbook 작성
