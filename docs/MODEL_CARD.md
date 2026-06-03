# 금융 NLP 기준 모델 카드

## 모델명
`financial-keyword-baseline-2026-06-04`

## 목적
- 한국 주식 뉴스·공시의 이벤트 태그, 감성, 중요도를 빠르게 분류한다.
- Hana-OmniLens-API의 Watchlist News & Disclosure Alert API payload 생성에 사용한다.

## 입력
- source type: `NEWS` 또는 `DISCLOSURE`
- 제목
- snippet
- 후보 종목 목록

## 출력
- 대표 종목
- 이벤트 태그
- 감성: `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- 중요도: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- 중복 제거 키

## 학습 데이터
- 위치: `data/training/financial_alert_corpus.jsonl`
- 형식: JSONL
- 현재 샘플 수: 18
- 라벨: `EARNINGS`, `DISCLOSURE`, `CAPITAL_ACTION`, `CORPORATE_ACTION`, `CONTRACT`, `RISK`, `MACRO`

## 학습 방식
- 라벨 데이터의 태그를 기준으로 seed keyword를 집계한다.
- 생성 결과는 `src/hannah_montana_ai/model_store/financial_nlp_baseline.json`에 저장한다.
- 현재 방식은 설명 가능성과 구현 속도를 위한 기준 모델이다.

## 평가 결과
- 위치: `reports/model-evaluation.json`
- 평가 샘플 수: 6
- 이벤트 태그 recall: 1.0
- 감성 accuracy: 1.0
- 중요도 accuracy: 1.0
- 종목 매핑 accuracy: 1.0

## 한계
- 형태소 분석을 사용하지 않아 표현 변형에 취약하다.
- 뉴스 본문 전문을 사용하지 않아 문맥 이해가 제한된다.
- 실제 투자 판단을 위한 추천 모델이 아니다.

## 운영 전 필수 보강
- 라벨 데이터 1,000건 이상 확보
- 종목명 동음이의어 처리
- precision, recall, F1 리포트 추가
- drift 감시와 재학습 기준 정의
