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

## 외국인 보유 시계열 예측
- `POST /api/v1/market/foreign-ownership/predict`는 OmniLens가 저장한 외국인 보유수량, 보유율, 한도소진율 snapshot과 일별 시계열을 입력으로 받는다. 요청 수량과 장중 누적 거래량 필드는 호환용으로만 수신하며 예측식에는 반영하지 않는다.
- 응답은 금일 외국인 취득 수량의 한도 도달 가능성을 나타내는 한도소진율 `min/base/max`, 일별 추세, 관측치 수, window, confidence, model version을 공통 envelope으로 반환한다. 호환 필드인 주문수량 영향도와 레거시 불확실성 값은 0으로 반환한다.
- confidence는 품질 관측과 UI 표시용이며 Hannah는 주문 차단, orderable 판정, 신뢰도 기반 자동 차단 결정을 만들지 않는다.
- OmniLens는 Hannah 장애 시 자체 시계열 fallback을 사용한다. 외국인 한도 예측은 프론트 사전 고지용이며 주문 차단 결정을 만들지 않는다.
- `POST /api/v1/market/foreign-ownership/model/retrain`은 OmniLens가 export한 제한 종목 전체 외국인 보유 history를 받아 임시 artifact로 학습한다. `HANNAH_AI_MAINTENANCE_TOKEN`이 설정된 환경에서는 `X-HANNAH-AI-MAINTENANCE-TOKEN` 헤더가 일치해야 한다.
- 재학습 결과가 `promoted`이면 `data/training/foreign_ownership_quantity_history.csv`, `data/training/foreign_ownership_restricted_stock_codes.csv`, `src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib`, `reports/foreign-ownership-quantity-training-report.json`을 원자적으로 교체하고 예측 서비스 cache를 비워 다음 요청부터 새 모델을 로드한다.
- quality gate가 실패해 `guarded`이면 운영 model artifact는 유지하고 후보 리포트만 `reports/foreign-ownership-quantity-training-candidate-report.json`에 저장한다.
- 학습은 외국인 취득한도 제한 종목 allowlist를 지정해 `uv run python scripts/train_foreign_ownership_quantity_model.py --restricted-stock-codes <csv>`로 실행한다. allowlist 없이 실행하면 quality gate가 `restricted_universe_not_applied`로 실패하고 `promoted`되지 않는다.
- `data/training/foreign_ownership_quantity_history.csv`는 제한 32종목 history만 포함한다. 비제한 종목 KRX 외국인 보유 history는 학습/promotion 대상이 아니므로 CSV에 보존하지 않는다.
- SOTA/benchmark 비교는 제한 종목 universe로 재학습한 report를 기준으로 `uv run python scripts/benchmark_foreign_ownership_quantity_models.py`로 실행한다. N-HiTS/PatchTST 진단까지 실행하려면 `uv pip install -e '.[sota]'` 후 `--include-neural-sota`를 붙인다.

## 글로벌 피어 종목 매칭
- `POST /api/v1/market/global-peers/match`는 OmniLens가 넘긴 한국 종목 metadata를 입력으로 받아 미국 상장 peer 후보를 반환한다.
- 응답은 외국인 투자자용 영어 headline, summary, primary peer, 후보 peer 목록, confidence, model version을 포함한다.
- 각 peer는 `sector`, `industry`, `business_model`, `scale_bucket`, `market_cap_usd`, `revenue_usd`, `operating_income_usd`, `net_income_usd`, `financial_data_source`, `financial_similarity_score`, `matched_factors`, `rationale`을 포함해 왜 해당 글로벌 peer로 매칭됐는지 설명한다.
- 현재 운영 artifact는 한국 종목 3,967개와 미국 symbol 12,916개를 학습한 `src/hannah_montana_ai/model_store/global_peer_ml.joblib`다.
- 미국 universe 갱신은 NASDAQ Trader symbol directory를 사용한다. 재무/규모 dataset은 OpenDART, KRX Open API, Naver mobile stock JSON, SEC companyfacts, NASDAQ quote summary를 사용한다.
- 전체 fundamentals 수집은 resume/checkpoint 방식이다. 이미 성공한 row는 건너뛰고, 실패하거나 원천에 없는 row만 다시 시도한다.
```bash
uv run python scripts/sync_us_stock_universe.py
uv run python scripts/sync_global_peer_fundamentals.py
uv run python scripts/sync_korea_stock_industries.py
uv run python scripts/train_global_peer_model.py
uv run python scripts/build_global_peer_ai_smoke_report.py
uv run python scripts/build_global_peer_full_coverage_report.py
uv run python scripts/build_global_peer_all_results_report.py
uv run python scripts/build_hannah_ai_model_audit_report.py
uv run pytest tests/test_global_peer_matcher.py tests/test_global_peer_api.py -q
```
- 실제 AI 품질 smoke 결과는 `reports/global-peer-ai-smoke-report.json`과 `docs/GLOBAL_PEER_AI_SMOKE.md`에 저장한다. 전종목 coverage 결과는 `reports/global-peer-full-coverage-report.json`에 저장하며, API 계약 테스트와 별도로 전체 한국 master 3,967개가 추론 가능한지 확인한다. 전종목별 현재 primary peer 결과와 성능은 `docs/GLOBAL_PEER_ALL_RESULTS.md`, `reports/global-peer-all-results.json`, `reports/global-peer-all-results.csv`에 저장한다. 전체 AI 기능 감사는 `reports/hannah-ai-model-audit-report.json`과 `docs/HANNAH_AI_MODEL_AUDIT.md`에 저장한다.

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
- `scripts/collect_training_data.py`는 v1 기준 Naver News Search와 OpenDART에서 제목·snippet·링크를 수집한다.
- full-content v2 학습 데이터는 Hana-OmniLens-API가 사용 허가된 뉴스 원문과 OpenDART document 전문을 저장한 export를 사용한다. export는 `FULL_TEXT`, `source_license_policy`, `content_hash`, 원문 링크, 이미지 metadata를 포함해야 한다.
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
- `reports/live-news-monitoring-status.json`은 `reports/live-news-evaluation-report.json`이 현재 release 모델 버전, row/report schema, confidence summary를 만족하는지 검증한다. `overall_status=pass`일 때만 최신 live-news smoke/drift 근거로 사용하고, `stale`이면 운영 credential이 있는 환경에서 실시간 뉴스 배치를 다시 생성한다.
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
- 현재 artifact는 83,105건 수집 후보 중 weak-label 339건과 종목 후보 큐 687건을 이벤트 모델 학습에 반영했다.
- 종목 후보 큐 승격분은 per-stock quota 1건으로 제한해 687건이 687개 종목에 분산되도록 한다.
- 실제 원문 전문 학습 데이터는 `scripts/build_real_full_content_training_data.py`로 생성하며, 현재 뉴스 전문 19,727건과 OpenDART document 전문 273건을 포함한 20,000건이다.
- 이벤트·감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 사람이 검수하지 않은 실제 전문 약한 라벨 1,036건을 supervised loss에서 제외한다.
- 실시간 최신 뉴스 품질 감사는 `scripts/build_live_news_quality_audit.py`로 실행하며, 라벨 없는 최신 Naver 표본에서 query-relevant pass rate와 본문 추출 품질을 관측한다.

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
uv run python scripts/build_service_readiness_report.py
uv run python scripts/build_live_news_quality_audit.py \
  --stock-sample-size 60 \
  --max-news-per-query 2 \
  --sample-limit 160 \
  --require-query-stock-match
```

## 전문 분석·요약 추가 학습 원칙
- 실제 뉴스 전문 추가 학습은 최소 1,000건 이상을 목표로 하되, 관련 종목이 제목·snippet·전문 중 하나에서 확인되지 않는 row는 live 품질 gate와 학습 승격 후보에서 제외한다.
- 서비스급 대량 학습 반복은 전문 뉴스·공시 5,000건 이상을 1차 기준선으로 삼고, 최신 release는 종목·업종·이벤트가 더 분산된 20,000건 gold/검수 후보를 기준으로 관리한다.
- 20,000건 확장 배치는 기존 5,000건 재사용 가능한 전문 row를 보존하고, 신규 기사 전문 fetch 실패·중복·종목 불일치·라벨 quota 제외 사유를 별도 리포트에 남겼다.
- 대량 반복에서 목표 row 수를 채우지 못하면 수집 실패 수, 중복 URL 재사용 수, 본문 추출 실패 수, 종목 불일치 제외 수를 리포트에 남기고 다음 shard 수집 기준으로 사용한다.
- live quality audit은 서비스 승격 전 최소 1,000건 이상 최신 미학습 표본으로 실행하고, query-relevant pass rate, full-content rate, sampled stock model match rate를 함께 본다.
- 기사 원문은 요약 품질 개선과 검수 후보 생성에 사용하고, 이벤트·감성·중요도 정답 라벨은 `human_review_approved`, `codex_review_approved`, teacher confidence gate를 통과한 pseudo label만 학습에 반영한다.
- live audit은 전체 pass rate와 query-relevant pass rate를 분리해 기록한다. 운영 판단은 검색 provider 노이즈가 제거된 query-relevant pass rate를 우선 보되, 전체 pass rate는 수집기 검색 품질 개선 지표로 추적한다.
- What/Why/Impact 요약은 LLM 없이 rule engine과 금융 ML 결과로 생성한다. 요약 3줄이 중복, boilerplate 포함, fallback 문구, 18자 미만, 종목 불일치, 낮은 confidence를 보이면 quality finding으로 기록한다.
- 최신 라이브 표본에서는 짧은 종목명 과매칭, 본문 boilerplate 유입, `SUMMARY_ONLY` 과신을 우선 확인한다. 대표 종목이 긴 고유 종목명보다 짧은 요청 후보명으로 치우치거나, 요약에 광고·푸터·관련기사 문구가 들어가면 release 후보에서 제외한다.
- 새 모델 artifact는 `reports/model-release-report.json`, `reports/service-readiness-report.json`, `reports/live-news-quality-audit-report.json`이 모두 pass 기준을 만족할 때만 승격한다.

- `reports/model-release-report.json`은 모델 버전, 학습 샘플 수, pseudo-label 승격 내역, holdout·benchmark·실공시·실뉴스 quality gate를 한 파일로 묶는다.
- `reports/model-confidence-calibration.json`은 평가셋별 이벤트 확률 calibration, 감성·중요도 top confidence calibration, 고신뢰 오답을 기록한다.
- `reports/stock-candidate-quota-experiment.json`은 stock candidate pseudo-label quota profile별 임시 재학습 결과와 gold gate 통과 여부를 기록한다.
- `overall_status`는 모든 quality gate와 pseudo-label consistency check가 통과할 때만 `pass`가 된다.
- release report는 `reports/ml-training-report.json`, `reports/ml-model-evaluation.json`, `reports/weak-distillation-report.json`에서 결정적으로 생성한다.

## Pseudo-label gate 모니터링
- `reports/pseudo-label-promotion-monitoring.json`은 raw 후보, 고신호 후보, teacher 탈락, quota 보류, 최종 승격 수를 funnel 형태로 기록한다.
- 현재 83,105건 raw 후보 중 5,250건이 고신호 후보이고, teacher gate에서 4,388건이 탈락하며 weak-label 339건과 종목 후보 687건만 student 이벤트 모델 학습에 승격된다.
- `RISK`, `CONTRACT`, `CORPORATE_ACTION`, `EARNINGS`, `MACRO`는 현재 active label이며 quota 여유가 남아 추가 후보 품질을 모니터링한다.
- `CAPITAL_ACTION`은 현재 quota를 채웠고, `DISCLOSURE`는 실제 뉴스 gold gate 실험 전까지 학습 투입을 보류한다.
- `GENERAL_MARKET`은 고신호 후보 풀이 작아 현재 확장 대상이 아니다.

## Coverage report 해석
- `reports/stock-coverage-report.json`의 `training_stock_count`와 `evaluation_stock_count`는 승인된 stock review gold를 포함한 supervised/reference coverage다.
- `reports/full-universe-codex-coverage-report.json`은 유효 6자리 국내주식 3,920개가 stock review gold train/eval reference coverage에 모두 포함되는지 검증한다.
- `codex_review_approved` full-universe reference row는 커밋된 coverage lineage로 쓰지만, self-training feedback loop를 막기 위해 supervised loss에서는 제외한다.
- `event_model_pseudo_training_coverage`는 teacher-gated event-model-only pseudo-label coverage다.
- 현재 event model pseudo training coverage는 687건, 687개 종목이며 supervised/reference coverage와 별도로 해석한다.
- `reports/model-release-report.json`의 `service_readiness`는 bootstrap 운영 판단이며, release quality gate와 stock-candidate pseudo coverage를 기준으로 한다.
- `audited_gold_readiness`는 `human_review_approved` 또는 `codex_review_approved` coverage gold 기준이며, bootstrap 운영 판단과 별도로 관리한다.
- `reports/service-readiness-report.json`은 release gate, audited gold readiness, live-news monitoring, full-universe reference coverage, stock linker coverage, pseudo-label monitoring, confidence calibration을 최종 운영 readiness gate로 집계한다.
- service readiness gate는 confidence 값을 `observe_only` 정책으로만 인정하며 Hannah가 신뢰도 기반 자동 차단 결정을 만들면 실패해야 한다.
- `reports/stock-collection-shard-plan.json`은 candidate queue, supervised training gold, evaluation gold가 모두 없는 종목을 shard 단위 수집 대상으로 기록한다.
- 현재 shard plan은 351개 `no_raw_no_candidate` 종목과 107개 `raw_without_candidate` 종목을 우선 수집 대상으로 둔다.
- `reports/stock-candidate-quota-experiment.json`은 quota 탐색 참고 리포트이며, 현재 release는 full-content v2 재학습 리포트의 687건/687종목 bootstrap coverage와 실제 뉴스 gold gate 통과를 기준으로 한다.
- `reports/stock-gold-review-batch-report.json`은 학습 검수 배치 300개 종목과 평가 검수 배치 100개 종목을 기록한다.
- 검수 배치의 학습·평가 종목은 서로 겹치지 않으며, 사람이 승인하기 전까지 coverage gate 통과 수치에 포함하지 않는다.
- `reports/stock-gold-review-validation-report.json`은 현재 검수 배치에서 승격 가능한 승인 row가 학습 300개 종목, 평가 100개 종목 목표를 만족하는지 기록한다.
- `reports/stock-gold-active-review-report.json`은 모델 제안 라벨과 신뢰도 기반 검수 우선순위를 기록하지만, 사람 승인 없이 gold로 승격하지 않는다.
- `reports/stock-gold-promotion-report.json`은 `human_review_approved` 또는 `codex_review_approved` row 중 검수자 메타데이터와 최종 라벨이 모두 있는 row만 supervised/evaluation gold 출력으로 승격했는지 기록한다.
- 승인 상태지만 필수 검수 필드가 빠진 row는 `rejected_approved_count_by_reason`에 사유별로 집계한다.

## 운영 readiness gate
- `reports/service-readiness-report.json`의 `overall_status=pass`를 release 전 최종 gate로 사용한다.
- gate가 `fail`이면 실패한 check를 수정하고 관련 하위 리포트를 재생성한 뒤 다시 실행한다.
- rollback은 `model-release-report`와 `service-readiness-report`가 모두 `pass`였던 직전 model artifact로 되돌린다.

## 지속 운영 관리
- live-news smoke/drift 리포트가 `stale` 또는 `attention`이면 운영 credential 환경에서 배치를 재생성한다.
- full-universe Codex reference coverage 누락 0을 유지한다.
- 사람이 검수한 supervised/evaluation gold label을 월별로 증분 확대한다.
- 후보 큐 3,506개 종목에서 종목·라벨별 human review batch를 운영한다.
- 배포 환경별 Secret Manager 연동 완료 후 secret rotation runbook을 유지한다.
