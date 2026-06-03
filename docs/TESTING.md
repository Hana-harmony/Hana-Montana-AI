# 테스트

## 로컬 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
```

## 현재 테스트 범위
- 분석 API 정상 응답
- health endpoint 정상 응답
- 분석 API의 종목 매핑, 감성, 이벤트 태그 응답
- 수집·증강 데이터 기반 ML artifact 생성
- 평가 데이터셋 기준 이벤트 recall, 이벤트 macro F1, 감성, 중요도, 종목 매핑 지표
- 이벤트 라벨별 precision, recall, F1 리포트 생성
- 감성·중요도 confusion matrix 리포트 생성
- 수집 실패 시 기존 raw 코퍼스 축소 덮어쓰기 방지

## 추가 예정
- 모델 artifact 누락 시 실패 처리
- 라벨별 golden dataset 테스트
- 중복 제거 키 안정성 테스트
- Hana-OmniLens-API 연동 contract test
- 배포 네트워크에서 외부 접근 차단 확인
- 사람이 검수한 500건 이상 gold evaluation set 구축
