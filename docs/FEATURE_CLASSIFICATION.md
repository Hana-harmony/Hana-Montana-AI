# 기능 분류와 레포 책임

## 이 레포가 담당하는 기능

| 기능 | 현재 상태 |
| --- | --- |
| 뉴스·공시 종목 매핑 | Implemented, audited gold coverage pending |
| 이벤트 태그 분류 | Implemented, audited gold coverage pending |
| 감성 분류 | Implemented, audited gold coverage pending |
| 중요도 분류 | Implemented, audited gold coverage pending |
| 중복 제거 키 생성 | Implemented |
| 간단 요약 생성 | Implemented |
| 금융 용어 normalization과 번역 품질 보조 | Implemented |
| 세무 OCR/위변조 검증 모델 | Done |

## 이 레포가 담당하지 않는 기능

| 기능 | 담당 레포 |
| --- | --- |
| KIS/KRX/EXIM/Naver/OpenDART/Papago/DeepL credential 관리 | Hana-OmniLens-API |
| 협력사 REST/WebSocket API와 API key 인증 | Hana-OmniLens-API |
| 뉴스·공시 이벤트 수신 후 사용자별 푸시 대상자 매칭 | Stock-exchange-BE |
| MTS 종목 상세, K-News 피드, 알림함 UI | Stock-exchange-FE |
| 실제 주문, 체결, 정산, 환전 | 현지 거래소·브로커 또는 별도 원장 시스템 |
| 세무 서류 업로드 UI와 환급금 신청 화면 | Stock-exchange-FE |

## 최신 기능정의와의 차이

- 기능정의서는 "AI로 번역 및 분석"을 하나의 흐름으로 표현하지만, 현재 설계에서는 분석 모델과 번역 공급자 orchestration을 분리한다.
- 현재 구현된 AI는 외부 번역 API를 호출하지 않고, 로컬 금융 용어집 기반 번역 보조와 품질 플래그를 제공한다.
- 종목 매핑, 이벤트 태그, 감성, 중요도는 ML artifact와 내부 stock universe fallback으로 동작하지만, 모델 카드의 audited gold coverage gate가 아직 fail이므로 모델 품질 상태는 별도로 계속 추적한다.
- 세무 전산화의 OCR/위변조 검증은 외부 OCR 결과와 위변조 signal을 받아 `VERIFIED/PENDING/REJECTED`로 판정하는 내부 모델 API로 구현했다. 실제 문서 원본 저장과 국세청 제출은 외부 백엔드 영역이다.
