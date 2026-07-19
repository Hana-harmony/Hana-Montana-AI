# 아키텍처

## 목적
- Hana-Omni-Connect-API가 수집한 뉴스·공시 제목과 snippet을 분석한다.
- v2에서는 권리 확인이 끝난 뉴스·공시 전문을 추가 입력으로 받아 What/Why/Impact 3줄 요약과 전문 기반 중복 키를 생성한다.
- 뉴스·공시 분석, 종목 링커, 외국인 보유 예측, 글로벌 피어 매칭, 한국 금융 용어 해설을 독립 모델 또는 검증된 룰 조합으로 제공한다.

## 서비스 구성
- `api`: 분석 API route
- `core`: 환경 설정
- `domain`: request, response schema
- `services`: 모델 로더, 분석 orchestration, 예측·해설 서비스
- `model_store`: 배포 가능한 모델 artifact

## API 경계
- 공개 endpoint: `GET /health`, `GET /ready`
- 내부 endpoint: `POST /api/v1/alerts/analyze`
- 내부 endpoint: `POST /api/v1/stocks/order-status`
- 내부 endpoint: `POST /api/v1/intelligence/events`
- 내부 endpoint: `POST /api/v1/tax/documents/verify`
- 내부 endpoint: `POST /api/v1/tax/refund-status`
- 모든 내부 비즈니스 endpoint는 `ApiResponse` 공통 envelope로 성공/상태/코드/메시지/본문을 함께 반환한다.
- AI 서비스는 협력사용 `OMNI_CONNECT_API_KEY`를 요구하지 않는다.
- AI 서비스는 별도 토큰을 검증하지 않고 Spring 컨테이너 전용 내부 네트워크에서만 접근 가능해야 한다.

## 현재 구현 상태
- 종목 매핑은 요청 `stock_universe`를 우선 사용하고, 누락된 종목은 내부 `data/reference/korea_stock_universe.csv` master에서 종목코드, 한글명, 영문명, alias 포함 여부로 판단한다.
- 내부 master fallback은 `stock_linker_ml.joblib`의 TF-IDF stock linker 예측을 먼저 확인하고, 대표 종목 오탐 방지를 위해 실제 선두 term 매칭 여부를 함께 검증한다.
- 이벤트 태그는 `financial_nlp_ml.joblib`의 source type과 한국어 금융 token feature 포함 One-vs-Rest multilabel classifier로 예측한다.
- 감성은 고정 리비전 `kakaobank/kf-deberta-base` + LoRA 모델을 artifact SHA·독립 benchmark gate 뒤에서 서빙한다. gate 실패 시 기존 TF-IDF Logistic Regression으로 fallback한다.
- 중요도는 source type, TF-IDF char n-gram, 한국어 금융 token feature를 결합한 Logistic Regression 모델이 분류한다.
- `data/k_fnspid/v4`는 뉴스 524,696건·공시 722,989건, 총 1,247,685문서와 1,136,118건 종목 관계, 715,015건 시장반응, 10,691,998행 일별 시세를 Parquet 스냅샷으로 보관한다. 공시 8,972건과 뉴스 13,310건은 실제 전문을 연결한다. 데이터셋 빌드는 운영 DB를 읽지 않는다.
- 시장영향은 KF-DeBERTa LoRA와 TF-IDF OVR을 같은 시간 외삽 Test에서 비교한다. Transformer가 macro F1·quadratic kappa gate와 기준선을 모두 넘을 때만 승격하고, 아니면 검증된 TF-IDF artifact를 계속 서빙한다.
- 중복 제거 키는 source type, 종목코드, 뉴스 라벨·꼬리표를 제거한 canonical title을 SHA-256으로 해시한다.
- 주문 상태 계약은 외부 KIS/PredictEngine 입력값을 받아 외국인 보유율, 한도소진율, 예측 지분율 구간, VI, 상·하한가, 즉시체결 가능 여부를 계산한다.
- 인텔리전스 이벤트 계약은 기존 분석 결과에 번역 제목·요약, 금융 용어집 정규화 결과, 번역 품질 플래그를 붙여 현지 MTS WebSocket 패킷 형태로 패킹한다.
- full-content v2 계약은 제목/snippet 모델을 baseline으로 유지하면서 전문이 있는 경우 전문 기반 요약, content hash, duplicate key, image URL metadata를 추가한다. 전문이 없으면 v1 출력과 `content_availability=SUMMARY_ONLY`로 응답한다.
- 세무 서류 검증 계약은 하네스와 API가 공유하는 템플릿·영역 OCR 파이프라인과 위변조 signal을 표준 `VERIFIED/PENDING/REJECTED` 결과로 판정한다. 내부 계정 ID는 문서 진위의 필수 증거로 사용하지 않는다.
- 세무 환급 계약은 OCR/위변조 검증 결과와 거래 원장을 입력받아 CASE_01 여부, 환급 가능액, 선지급 수수료, 사후 환수 플래그를 계산한다.
