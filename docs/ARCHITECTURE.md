# 아키텍처

## 목적
- Hana-OmniLens-API가 수집한 뉴스·공시 제목과 snippet을 분석한다.
- ChatGPT API에 의존하지 않고 자체 학습한 금융 NLP ML 모델을 사용한다.

## 서비스 구성
- `api`: 분석 API route
- `core`: 환경 설정
- `domain`: request, response schema
- `services`: Rule Engine, 모델 로더, 분석 orchestration
- `model_store`: 배포 가능한 모델 artifact

## API 경계
- 공개 endpoint: `GET /health`
- 내부 endpoint: `POST /api/v1/alerts/analyze`
- AI 서비스는 협력사용 `OMNILENS_API_KEY`를 요구하지 않는다.
- AI 서비스는 별도 토큰을 검증하지 않고 Spring 컨테이너 전용 내부 네트워크에서만 접근 가능해야 한다.

## 현재 구현 상태
- 종목 매핑은 전달받은 `stock_universe`에서 종목코드, 한글명, 영문명 포함 여부로 판단한다.
- 이벤트 태그는 `financial_nlp_ml.joblib`의 source type과 한국어 금융 token feature 포함 One-vs-Rest multilabel classifier로 예측한다.
- 감성은 TF-IDF char n-gram, 한국어 금융 token feature, Logistic Regression 모델로 분류한다.
- 중요도는 source type, TF-IDF char n-gram, 한국어 금융 token feature를 결합한 Logistic Regression 모델이 분류한다.
- 중복 제거 키는 source type, 종목코드, 뉴스 라벨·꼬리표를 제거한 canonical title을 SHA-256으로 해시한다.
