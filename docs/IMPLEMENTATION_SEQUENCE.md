# 변경 구현 순서

이 문서는 Hannah-Montana-AI 모델·규칙 변경 순서다. 기능과 현재 모델 목록은 README를 기준으로 한다.

1. API schema, 모델 artifact, 데이터 lineage, 평가 report와 호출 저장소 계약을 확인한다.
2. 실패 상태, confidence 의미, 수동 검수 경로와 개인정보 처리 경계를 먼저 정의한다.
3. serving·학습 코드를 변경하고 재현 가능한 단위·계약·품질 gate 테스트를 추가한다.
4. 해당 모델만 재학습·평가해 versioned artifact와 JSON report를 생성한다.
5. release gate 통과 여부를 검토하고 `docs/models/` 상세 문서와 구현 기록을 갱신한다.
6. ruff, mypy, bandit, secret hygiene, pytest를 실행한다.
7. `feature`에서 작업 브랜치를 만들고 PR 체크 통과 후 `feature`, 이어서 `main`에 병합한다.

번역·OCR·세무 규칙은 실패를 성공 값으로 대체하지 않는다. 모델 변경으로 자동 주문·세무 지급 결정을 추가하지 않는다.
