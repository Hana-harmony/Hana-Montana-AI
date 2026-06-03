# 테스트

## 로컬 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
```

## 현재 테스트 범위
- 분석 API 정상 응답
- health endpoint 정상 응답
- 분석 API의 종목 매핑, 감성, 이벤트 태그 응답
- 수집·증강 데이터 기반 ML artifact 생성
- 학습 단계의 80:20 holdout 검증 리포트 생성
- 평가 데이터셋 기준 이벤트 recall, 이벤트 macro F1, 감성, 중요도, 종목 매핑 지표
- 이벤트 라벨별 precision, recall, F1 리포트 생성
- 감성·중요도 confusion matrix 리포트 생성
- 수집 실패 시 기존 raw 코퍼스 축소 덮어쓰기 방지

## 현재 ML 검증 기준
- `reports/ml-training-report.json`은 11,898건 학습 샘플 중 2,380건 holdout 검증 결과를 기록한다.
- holdout 최소 기준은 이벤트 macro F1 0.8, 감성 accuracy 0.8, 중요도 accuracy 0.8 이상이다.
- 현재 holdout 결과는 이벤트 macro F1 0.9011, 감성 accuracy 0.9542, 중요도 accuracy 0.9626이다.
- `reports/ml-model-evaluation.json`은 사람이 검수한 gold 평가셋 결과를 별도로 기록한다.

## 추가 예정
- 모델 artifact 누락 시 실패 처리
- 라벨별 golden dataset 테스트
- 중복 제거 키 안정성 테스트
- Hana-OmniLens-API 연동 contract test
- 배포 네트워크에서 외부 접근 차단 확인
- 사람이 검수한 500건 이상 gold evaluation set 구축
