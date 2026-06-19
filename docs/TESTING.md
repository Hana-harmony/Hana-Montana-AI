# 테스트

## 로컬 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run python scripts/verify_secret_hygiene.py
uv run python scripts/verify_message_conventions.py --pr-title "feat(model): 기능정의서 모델 계약 추가" --pr-body "$(cat .github/PULL_REQUEST_TEMPLATE.md)"
uv run pytest
uv run python scripts/build_gold_evaluation_data.py
uv run python scripts/build_augmented_training_data.py
uv run python scripts/build_news_style_training_data.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_confidence_calibration_report.py
uv run python scripts/build_stock_candidate_quota_experiment.py
uv run python scripts/build_model_release_report.py
uv run python scripts/build_pseudo_label_monitoring_report.py
uv run python scripts/sync_stock_universe.py
uv run python scripts/build_stock_coverage_report.py
uv run python scripts/build_stock_training_candidate_queue.py
uv run python scripts/build_stock_gold_review_batch.py
uv run python scripts/validate_stock_gold_review_batch.py
uv run python scripts/build_stock_gold_active_review_report.py
uv run python scripts/promote_stock_gold_review_batch.py
uv run python scripts/train_stock_linker_model.py
uv run python scripts/build_live_news_evaluation_batch.py --stock-sample-size 5 --max-news-per-query 2 --sample-limit 10
```

## 현재 테스트 범위
- 분석 API 정상 응답
- health endpoint 정상 응답
- 분석 API의 종목 매핑, 감성, 이벤트 태그 응답
- 요청 후보가 비어 있어도 내부 국내주식 universe master로 종목을 매핑하는지 검증
- 수집·증강 데이터 기반 ML artifact 생성
- 약지도 대량 후보 distillation 필터와 노이즈 제거
- supervised teacher confidence gate를 통과한 pseudo-label 승격 학습
- 한국어 금융 tokenizer 복합어 추출
- 학습 단계의 80:20 holdout 검증 리포트 생성
- 768건 benchmark 평가셋 기준 이벤트 recall, 이벤트 macro F1, 감성, 중요도, 종목 매핑 지표
- benchmark·real gold 평가셋 기준 이벤트 확률, 감성·중요도 confidence calibration 리포트 생성
- 이벤트 라벨별 precision, recall, F1 리포트 생성
- 이벤트 라벨별 golden quality gate
- 감성·중요도 라벨별 golden confusion matrix gate
- 사람이 검수한 30건 OpenDART 실공시 gold evaluation gate
- 사람이 검수한 80건 Naver 실제 뉴스 gold evaluation gate
- 실제 뉴스 gold set의 라벨 support, 종목 다양성, raw source URL traceability 검증
- 실제 뉴스 학습 gold와 평가 gold의 문장 중복 방지
- 감성·중요도 confusion matrix 리포트 생성
- 수집 실패 시 기존 raw 코퍼스 축소 덮어쓰기 방지
- 약지도 distillation 후보 중 teacher confidence와 gold gate를 통과한 후보만 이벤트 모델 학습에 승격하는지 검증
- stock candidate pseudo-label quota 실험이 이전 release, risk/contract 확장 profile, calibrated current release를 gate 결과와 함께 기록하는지 검증
- 모델 artifact 누락·손상 시 명시적 오류와 API 503 fail-closed 응답
- 분석 API 성공·실패 audit log와 원문 비노출
- 외부 provider credential 누락 시 값 비노출 오류와 네트워크 호출 전 fail-fast
- 국내주식 universe 파일이 3,000개 이상 공개 종목 메타데이터를 포함하는지 검증
- 내부 universe master의 전체 6자리 종목코드가 종목 매핑 경로에서 누락 없이 매칭되는지 검증
- stock linker ML artifact가 전 종목코드와 trainable 종목명 템플릿 기준 정확도를 통과하는지 검증
- stock linker ML artifact 누락·손상 시 명시적 오류를 반환하는지 검증
- 종목 universe 기반 Naver 수집 쿼리 생성과 coverage report 산출 검증
- 누락 종목 우선 stock collection shard plan이 candidate/gold가 없는 종목을 먼저 수집 대상으로 잡는지 검증
- 종목·라벨 균형 학습 승격 후보 큐가 5,000건 이상, 2,000개 이상 종목을 포함하고 `needs_human_review` 상태인지 검증
- 학습 300개 종목, 평가 100개 종목 검수 배치가 라벨 균형과 학습·평가 종목 분리 조건을 만족하고 `needs_human_review` 상태인지 검증
- 검수 validation report가 승인 0건 상태를 `fail`로 기록하고, `human_review_approved` 또는 `codex_review_approved` 승인 row가 목표치를 채우면 `pass`가 되는지 검증
- active review report가 모델 제안 라벨, 신뢰도, disagreement 기반 우선순위를 생성하는지 검증
- 검수 배치 승격은 `human_review_approved` 또는 `codex_review_approved` row 중 검수자 메타데이터와 최종 라벨이 있는 row만 학습·평가 gold 파일로 출력하고 `needs_human_review` row는 제외하는지 검증
- `codex_review_approved` row는 committed reference/evaluation coverage로 유지하되 supervised loss에는 직접 투입하지 않아 실제 뉴스 gold gate를 회귀시키지 않는지 검증
- 승인 상태지만 검수자 메타데이터나 최종 라벨이 누락된 row를 승격하지 않고 사유를 리포트에 남기는지 검증
- 짧은 종목명 오탐을 줄이기 위해 coverage matcher가 2자 명칭을 제외하고 6자리 종목코드는 유지하는지 검증
- 추적 파일에 로컬 secret 파일, key material, provider credential assignment가 포함되지 않는지 CI 검사
- 모델 release report가 학습·평가·distillation 리포트와 동기화되어 있고 모든 gate가 통과하는지 검증
- 모델 confidence calibration report가 평가셋별 확률 calibration과 고신뢰 오답을 결정적으로 기록하는지 검증
- pseudo-label promotion monitoring report가 distillation·release 리포트와 동기화되어 있고 라벨별 확장 결정을 고정하는지 검증
- 중복 제거 키가 뉴스 라벨·언론사·기자 꼬리표를 제거하면서 종목·출처 경계를 유지하는지 검증
- 실시간 Naver 뉴스 표본 배치가 라벨 없는 smoke/drift row와 provider status, confidence 분포를 기록하는지 검증
- Hana-OmniLens-API Spring client가 사용하는 request·response JSON 필드명과 무토큰 내부 호출 계약 검증
- 기능정의서 기반 국내주식 주문 상태, 뉴스·공시 인텔리전스 이벤트, 세무 환급 선지급 JSON 계약 검증
- 주문 상태 API가 외국인 한도 잔여 수량, 한도 사용 상태, 매수/매도 가능 여부, 주문 제한 사유를 산출하는지 검증
- 세무 환급 API가 정부 참조번호, 국세/지방세 분해, 환급 진행 상태, 다음 조치, 사후 환수 고지를 산출하는지 검증
- 세무 서류 검증 API가 OCR confidence, 위변조 risk, 필수 field 누락 여부로 검증 상태와 manual review 여부를 산출하는지 검증
- KIS 종목 마스터, KIS 실시간 패킷, KRX 외국인 보유 row, Naver/OpenDART 인텔리전스 row, 세무 서류·거래 row 파싱 검증
- 인텔리전스 provider row가 모델 입력, API/WebSocket 중복키, 종목·출처별 중복키 경계, 번역·요약 응답, WebSocket 이벤트 패킷으로 연결되는지 검증

## 현재 ML 검증 기준
- `reports/ml-training-report.json`은 3,609건 supervised 샘플, 1,125건 pseudo-label 샘플, 722건 supervised holdout 검증 결과를 기록한다.
- `reports/weak-distillation-report.json`은 68,710건 약지도 후보 중 5,204건을 고신호 후보로 선별하고, teacher gate를 통과한 weak-label 344건과 종목 후보 781건을 이벤트 모델 학습에 승격한 결과를 기록한다.
- holdout 최소 기준은 이벤트 macro F1 0.8, 감성 accuracy 0.8, 중요도 accuracy 0.8 이상이다.
- 현재 holdout 결과는 이벤트 macro F1 0.9881, 감성 accuracy 0.9889, 중요도 accuracy 0.9931이다.
- `reports/ml-model-evaluation.json`은 768건 benchmark 평가셋 결과를 별도로 기록한다.
- benchmark 최소 기준은 이벤트 recall 0.8, 이벤트 macro F1 0.8, 감성 accuracy 0.85, 중요도 accuracy 0.8, 종목 accuracy 1.0이다.
- 현재 benchmark 결과는 이벤트 recall 0.9922, 이벤트 macro F1 0.9939, 감성 accuracy 1.0, 중요도 accuracy 0.9375, 종목 accuracy 1.0이다.
- `reports/model-confidence-calibration.json`은 benchmark 768건, 이벤트 멀티라벨 결정 6,144건의 calibration과 감성·중요도 고신뢰 오답을 기록한다.
- 실공시 gold 최소 기준은 이벤트 recall 0.9, 이벤트 macro F1 0.9, 감성 accuracy 0.9, 중요도 accuracy 0.9, 종목 accuracy 1.0이다.
- 현재 실공시 gold 결과는 이벤트 recall 1.0, 이벤트 macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0이다.
- 실제 뉴스 gold 최소 기준은 이벤트 recall 0.9, 이벤트 macro F1 0.9, 감성 accuracy 0.9, 중요도 accuracy 0.9, 종목 accuracy 1.0이다.
- 현재 실제 뉴스 gold 결과는 이벤트 recall 0.9625, 이벤트 macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0이다.
- `reports/model-release-report.json`은 현재 모델 버전 `financial-ml-tfidf-logreg-20260619095828`의 전체 release gate와 pseudo-label consistency check를 `overall_status=pass`로 기록한다.
- `reports/model-release-report.json`은 bootstrap service readiness와 `human_review_approved`/`codex_review_approved` coverage gold 기반 audited readiness를 모두 `pass`로 기록한다.
- `reports/pseudo-label-promotion-monitoring.json`은 고신호 후보 5,204건, teacher 탈락 4,007건, quota 보류 72건, 최종 승격 1,125건을 `overall_status=pass`로 기록한다.
- `reports/stock-coverage-report.json`은 universe 3,967개, raw 매칭 3,613개 종목, training/reference 3,422개 종목, evaluation/reference 557개 종목을 기록한다.
- `reports/stock-coverage-report.json`은 event-model-only pseudo 학습 coverage 781건, 781개 종목도 별도 섹션으로 기록한다.
- `reports/full-universe-codex-coverage-report.json`은 유효 6자리 국내주식 3,920개, Codex reference 보강 1,920건, 전체 coverage 3,920개, 누락 0개를 기록한다.
- `reports/stock-collection-shard-plan.json`은 후보 큐와 gold가 없는 458개 종목, 5개 shard, 2,290개 Naver 쿼리를 기록한다.
- stock collection shard plan은 351개 `no_raw_no_candidate` 종목을 raw가 이미 있는 종목보다 먼저 수집 대상으로 둔다.
- `reports/stock-candidate-quota-experiment.json`은 calibrated current release 781건/781종목이 gate를 통과했고, risk/contract 확장 profile은 895건/709종목까지 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못했음을 기록한다.
- `reports/stock-training-candidate-report.json`은 검수 대기 후보 15,720건, 3,506개 종목을 기록하며 coverage gate를 `pass`로 기록한다.
- `reports/stock-gold-review-batch-report.json`은 학습 검수 배치 300개 종목, 평가 검수 배치 100개 종목, 학습·평가 종목 disjoint check를 `pass`로 기록한다.
- `reports/stock-gold-review-validation-report.json`은 현재 승인 가능 학습 0개 종목, 평가 0개 종목이라 `overall_status=fail`로 기록한다.
- `reports/stock-gold-active-review-report.json`은 학습·평가 검수 배치 각각 상위 50개 우선 검수 row를 기록한다.
- `reports/stock-gold-promotion-report.json`은 승인된 검수 row 중 최종 검수 필드를 통과한 row만 학습·평가 gold 출력으로 편입했는지 기록한다.
- `reports/stock-linker-training-report.json`은 stock linker 학습 term 7,649건, 3,967개 종목을 기록하며 coverage gate를 `pass`로 기록한다.
- stock linker ML은 전체 종목코드 템플릿 accuracy 1.0, trainable 종목명 템플릿 accuracy 0.9921을 기록한다.
- `reports/live-news-evaluation-report.json`은 실시간 뉴스 표본의 provider status, 모델 confidence, 종목 매칭률을 기록한다. 이 배치는 아직 라벨이 없으므로 F1 계산 대상이 아니다.
- 전 종목 reference coverage gate는 현재 `pass`이며, 다음 확장은 운영 알림 로그와 사람 검수 gold 품질 보강을 기준선으로 사용한다.

## 추가 예정
- 배포 네트워크에서 외부 접근 차단 확인
- 실제 뉴스 gold 월별 증분 수집과 drift 모니터링
