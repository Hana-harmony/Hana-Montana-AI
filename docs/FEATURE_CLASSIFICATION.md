# 기능 분류와 저장소 책임

| 기능 | 이 저장소의 책임 | 상태 |
| --- | --- | --- |
| 뉴스·공시 | 종목 linker, 이벤트·감성·중요도 분류, What/Why/Impact, 중복 키, confidence | 운영 artifact·평가 gate 적용 |
| 한국어→영어 번역 | 로컬 Qwen3 호출, 문서 유형별 prompt, glossary·완결성 품질 gate | 적용 |
| 금융 용어 | 단일 검증 사전, evidence, alias 경계, review 상태 | 적용 |
| 글로벌 피어 | 활성 종목 universe, 동적 similarity ranker, 설명·비교·강점 계약 | 전종목 coverage gate 적용 |
| 외국인 보유 | 제한 종목 시계열 학습·예측, 재학습 promotion gate | 적용 |
| 주문 상태 | 외국인 boundary와 VI·가격 제한 규칙 모델 | 적용 |
| 세무 OCR | 파일 형식, OCR, 문서별 parser/reviewer, 위변조 위험 | 적용 |
| 세무 환급 | 검증 문서·모의 거래 기반 미국 조세조약 sandbox 규칙 | 적용 |

## 외부 책임

- KIS·KRX·Naver·OpenDART 수집과 협력사 API 인증·송신: Hana-Omni-Connect-API
- 사용자·계좌·모의 원장·세무 파일 저장·알림 매칭: Stock-exchange-BE
- iOS/Android 화면과 파일 선택: Stock-exchange-FE
- 실제 주문·체결·정산·세무 신고·정부 승인·환급 지급·환수: 외부 거래·세무·지급 시스템

AI 응답은 model version, confidence 또는 결정 규칙 version, 실패·검수 상태를 포함한다. 모델이 실제 주문이나 세무 지급을 승인하지 않는다.
