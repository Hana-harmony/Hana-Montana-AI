# 테스트

## 로컬 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run python scripts/verify_secret_hygiene.py
uv run pytest
uv run python scripts/build_gold_evaluation_data.py
uv run python scripts/build_augmented_training_data.py
uv run python scripts/build_news_style_training_data.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_release_report.py
uv run python scripts/build_pseudo_label_monitoring_report.py
uv run python scripts/sync_stock_universe.py
uv run python scripts/build_stock_coverage_report.py
uv run python scripts/build_stock_training_candidate_queue.py
uv run python scripts/build_stock_gold_review_batch.py
uv run python scripts/train_stock_linker_model.py
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
- 모델 artifact 누락·손상 시 명시적 오류와 API 503 fail-closed 응답
- 분석 API 성공·실패 audit log와 원문 비노출
- 외부 provider credential 누락 시 값 비노출 오류와 네트워크 호출 전 fail-fast
- 국내주식 universe 파일이 3,000개 이상 공개 종목 메타데이터를 포함하는지 검증
- 내부 universe master의 전체 6자리 종목코드가 종목 매핑 경로에서 누락 없이 매칭되는지 검증
- stock linker ML artifact가 전 종목코드와 trainable 종목명 템플릿 기준 정확도를 통과하는지 검증
- stock linker ML artifact 누락·손상 시 명시적 오류를 반환하는지 검증
- 종목 universe 기반 Naver 수집 쿼리 생성과 coverage report 산출 검증
- 종목·라벨 균형 학습 승격 후보 큐가 5,000건 이상, 2,000개 이상 종목을 포함하고 `needs_human_review` 상태인지 검증
- 학습 300개 종목, 평가 100개 종목 검수 배치가 라벨 균형과 학습·평가 종목 분리 조건을 만족하고 `needs_human_review` 상태인지 검증
- 짧은 종목명 오탐을 줄이기 위해 coverage matcher가 2자 명칭을 제외하고 6자리 종목코드는 유지하는지 검증
- 추적 파일에 로컬 secret 파일, key material, provider credential assignment가 포함되지 않는지 CI 검사
- 모델 release report가 학습·평가·distillation 리포트와 동기화되어 있고 모든 gate가 통과하는지 검증
- pseudo-label promotion monitoring report가 distillation·release 리포트와 동기화되어 있고 라벨별 확장 결정을 고정하는지 검증
- 중복 제거 키가 뉴스 라벨·언론사·기자 꼬리표를 제거하면서 종목·출처 경계를 유지하는지 검증
- Hana-OmniLens-API Spring client가 사용하는 request·response JSON 필드명과 무토큰 내부 호출 계약 검증

## 현재 ML 검증 기준
- `reports/ml-training-report.json`은 3,609건 supervised 샘플, 824건 pseudo-label 샘플, 722건 supervised holdout 검증 결과를 기록한다.
- `reports/weak-distillation-report.json`은 37,278건 약지도 후보 중 4,845건을 고신호 후보로 선별하고, teacher gate를 통과한 weak-label 360건과 종목 후보 464건을 이벤트 모델 학습에 승격한 결과를 기록한다.
- holdout 최소 기준은 이벤트 macro F1 0.8, 감성 accuracy 0.8, 중요도 accuracy 0.8 이상이다.
- 현재 holdout 결과는 이벤트 macro F1 0.9881, 감성 accuracy 0.9889, 중요도 accuracy 0.9931이다.
- `reports/ml-model-evaluation.json`은 768건 benchmark 평가셋 결과를 별도로 기록한다.
- benchmark 최소 기준은 이벤트 recall 0.8, 이벤트 macro F1 0.8, 감성 accuracy 0.85, 중요도 accuracy 0.8, 종목 accuracy 1.0이다.
- 현재 benchmark 결과는 이벤트 recall 0.9948, 이벤트 macro F1 0.9979, 감성 accuracy 1.0, 중요도 accuracy 0.9375, 종목 accuracy 1.0이다.
- 실공시 gold 최소 기준은 이벤트 recall 0.9, 이벤트 macro F1 0.9, 감성 accuracy 0.9, 중요도 accuracy 0.9, 종목 accuracy 1.0이다.
- 현재 실공시 gold 결과는 이벤트 recall 1.0, 이벤트 macro F1 0.9846, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0이다.
- 실제 뉴스 gold 최소 기준은 이벤트 recall 0.9, 이벤트 macro F1 0.9, 감성 accuracy 0.9, 중요도 accuracy 0.9, 종목 accuracy 1.0이다.
- 현재 실제 뉴스 gold 결과는 이벤트 recall 0.9375, 이벤트 macro F1 0.9116, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0이다.
- `reports/model-release-report.json`은 현재 모델 버전 `financial-ml-tfidf-logreg-20260604173957`의 전체 release gate와 pseudo-label consistency check를 `overall_status=pass`로 기록한다.
- `reports/pseudo-label-promotion-monitoring.json`은 고신호 후보 4,845건, teacher 탈락 3,124건, quota 보류 897건, 최종 승격 824건을 `overall_status=pass`로 기록한다.
- `reports/stock-coverage-report.json`은 universe 3,967개, raw 매칭 2,356개 종목, supervised 38개 종목, evaluation 57개 종목을 기록한다.
- `reports/stock-coverage-report.json`은 event-model-only pseudo 학습 coverage 464건, 464개 종목도 별도 섹션으로 기록한다.
- `reports/stock-training-candidate-report.json`은 검수 대기 후보 6,244건, 2,127개 종목을 기록하며 coverage gate를 `pass`로 기록한다.
- `reports/stock-gold-review-batch-report.json`은 학습 검수 배치 300개 종목, 평가 검수 배치 100개 종목, 학습·평가 종목 disjoint check를 `pass`로 기록한다.
- `reports/stock-linker-training-report.json`은 stock linker 학습 term 7,649건, 3,967개 종목을 기록하며 coverage gate를 `pass`로 기록한다.
- stock linker ML은 전체 종목코드 템플릿 accuracy 1.0, trainable 종목명 템플릿 accuracy 0.9921을 기록한다.
- 전 종목 실서비스 coverage gate는 현재 `fail`이며, 다음 데이터 확장 PR의 기준선으로 사용한다.

## 추가 예정
- 배포 네트워크에서 외부 접근 차단 확인
- 실제 뉴스 gold 월별 증분 수집과 drift 모니터링
