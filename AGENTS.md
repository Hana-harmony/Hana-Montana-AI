# AGENTS.md

## 공통 지침
- 업계 실제 서비스에서 사용하는 최신 안정 방식과 보안 기준을 우선 적용한다.
- 시크릿과 외부 API credential은 코드와 문서 예시에 원문으로 남기지 않는다.
- 주석은 한글로 작성하되 중요한 로직 설명만 짧게 남긴다.
- 모델 변경은 구현 기록과 모델 카드에 함께 남긴다.
- 변경 후 가능한 범위에서 테스트, 타입 검사, 정적 검사, 보안 검사를 실행하고 결과를 기록한다.

## 서비스 경계
- 이 레포는 Hannah-Montana-AI 모델 API 서버다.
- 뉴스·공시의 종목 매핑, 이벤트 분류, 감성 분류, 중요도 분류, 요약, 중복 제거 키 생성을 담당한다.
- 전문 번역은 Papago/DeepL adapter를 가진 Hana-OmniLens-API가 orchestration하되, 이 레포는 향후 번역 품질 보조나 금융 용어 normalization 모델을 제공할 수 있다.
- 세무 문서 OCR/위변조 검증은 최신 기능정의의 planned 영역이며, 구현 시 별도 OCR service로 분리할지 이 레포의 모델 API로 둘지 ADR을 먼저 작성한다.
- 협력사 REST/WebSocket API는 Hana-OmniLens-API 레포 책임이다.
- 협력사용 `OMNILENS_API_KEY`를 요구하거나 저장하지 않는다.
- 별도 서비스 토큰 인증을 구현하지 않고 배포 네트워크 격리로 접근을 제한한다.
- 실제 주문, 모의 투자, 사용자 알림 저장은 구현하지 않는다.
- 최종투자자 세무 파일 저장, 환급금 지급/환수 실행도 구현하지 않는다.

## 구현 원칙
- Python 3.12, FastAPI, uv 기준을 유지한다.
- ChatGPT API에 의존하지 않고 자체 Rule Engine과 자체 금융 NLP 모델을 사용한다.
- 학습 데이터, 모델 버전, 한계, 평가 결과를 문서화한다.
- 분석 계약 변경 시 API schema, 테스트, 모델 문서를 함께 갱신한다.
- 번역, OCR, 세무 케이스 판정 등 고위험 모델 계약을 추가할 때는 데이터 출처, 평가 지표, 수동 검수 경로, 실패 시 fallback을 문서화한다.

## 필수 확인
- `uv run ruff check .`
- `uv run mypy`
- `uv run bandit -c pyproject.toml -r src`
- `uv run pytest`
