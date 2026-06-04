# 테스트

## 로컬 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
uv run python scripts/build_gold_evaluation_data.py
uv run python scripts/build_augmented_training_data.py
uv run python scripts/build_news_style_training_data.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_release_report.py
```

## 현재 테스트 범위
- 분석 API 정상 응답
- health endpoint 정상 응답
- 분석 API의 종목 매핑, 감성, 이벤트 태그 응답
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
- 사람이 검수한 56건 Naver 실제 뉴스 gold evaluation gate
- 실제 뉴스 학습 gold와 평가 gold의 문장 중복 방지
- 감성·중요도 confusion matrix 리포트 생성
- 수집 실패 시 기존 raw 코퍼스 축소 덮어쓰기 방지
- 약지도 distillation 후보 중 teacher confidence와 gold gate를 통과한 후보만 이벤트 모델 학습에 승격하는지 검증
- 모델 artifact 누락·손상 시 명시적 오류와 API 503 fail-closed 응답
- 분석 API 성공·실패 audit log와 원문 비노출
- 모델 release report가 학습·평가·distillation 리포트와 동기화되어 있고 모든 gate가 통과하는지 검증
- 중복 제거 키가 뉴스 라벨·언론사·기자 꼬리표를 제거하면서 종목·출처 경계를 유지하는지 검증
- Hana-OmniLens-API Spring client가 사용하는 request·response JSON 필드명과 무토큰 내부 호출 계약 검증

## 현재 ML 검증 기준
- `reports/ml-training-report.json`은 3,589건 supervised 샘플, 360건 pseudo-label 샘플, 718건 supervised holdout 검증 결과를 기록한다.
- `reports/weak-distillation-report.json`은 37,278건 약지도 후보 중 4,845건을 고신호 후보로 선별하고, teacher gate를 통과한 360건을 이벤트 모델 학습에 승격한 결과를 기록한다.
- holdout 최소 기준은 이벤트 macro F1 0.8, 감성 accuracy 0.8, 중요도 accuracy 0.8 이상이다.
- 현재 holdout 결과는 이벤트 macro F1 0.9970, 감성 accuracy 0.9930, 중요도 accuracy 0.9875이다.
- `reports/ml-model-evaluation.json`은 768건 benchmark 평가셋 결과를 별도로 기록한다.
- benchmark 최소 기준은 이벤트 recall 0.8, 이벤트 macro F1 0.8, 감성 accuracy 0.85, 중요도 accuracy 0.8, 종목 accuracy 1.0이다.
- 현재 benchmark 결과는 이벤트 recall 1.0, 이벤트 macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9427, 종목 accuracy 1.0이다.
- 실공시 gold 최소 기준은 이벤트 recall 0.9, 이벤트 macro F1 0.9, 감성 accuracy 0.9, 중요도 accuracy 0.9, 종목 accuracy 1.0이다.
- 현재 실공시 gold 결과는 이벤트 recall 1.0, 이벤트 macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0이다.
- 실제 뉴스 gold 최소 기준은 이벤트 recall 0.9, 이벤트 macro F1 0.9, 감성 accuracy 0.9, 중요도 accuracy 0.9, 종목 accuracy 1.0이다.
- 현재 실제 뉴스 gold 결과는 이벤트 recall 0.9821, 이벤트 macro F1 0.9525, 감성 accuracy 0.9821, 중요도 accuracy 0.9643, 종목 accuracy 1.0이다.
- `reports/model-release-report.json`은 현재 모델 버전 `financial-ml-tfidf-logreg-20260604122101`의 전체 release gate와 pseudo-label consistency check를 `overall_status=pass`로 기록한다.

## 추가 예정
- 배포 네트워크에서 외부 접근 차단 확인
- 사람이 검수한 뉴스 도메인 gold evaluation set 확대
