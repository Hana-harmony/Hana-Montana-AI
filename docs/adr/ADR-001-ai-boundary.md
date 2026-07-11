# ADR-001 AI 서비스 경계

## 결정
Hannah-Montana-AI는 뉴스·공시 분석 중심의 FastAPI 모델 API 서비스로 분리한다.

## 이유
- Hana-OmniLens-API는 협력사 연동 REST/WebSocket API를 담당한다.
- AI 모델 학습, 평가, 배포는 API 게이트웨이성 서비스와 변경 주기가 다르다.
- Naver/OpenDART 같은 외부 credential과 협력사 전송 경계는 Hana-OmniLens-API에 두고, 한국어 번역은 Hannah 내부망의 로컬 Qwen endpoint만 사용한다.

## 영향
- 이 레포는 주문, 모의 투자, 사용자 알림 저장을 구현하지 않는다.
- 분석 결과는 Hana-OmniLens-API가 알림 payload에 포함해 협력사로 전송한다.
- 한국어→영어 번역은 내부망의 로컬 Qwen3 endpoint를 이 레포가 호출하고, Hana-OmniLens-API가 해당 모델 API를 orchestration한다.
- 세무 OCR/위변조 검증 모델은 ADR-002에 따라 Hannah-Montana-AI의 모델 API 경계에서 처리한다.
