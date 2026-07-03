# 뉴스·공시 분석 모델

## 목적
한국 주식 뉴스와 공시를 종목별 인텔리전스 이벤트로 변환한다.

## Serving
- `POST /api/v1/alerts/analyze`
- `POST /api/v1/intelligence/events`

## 입력
- `sourceType`: `NEWS` 또는 `DISCLOSURE`
- 제목, snippet, 전문
- 후보 종목 목록
- 내부 한국 종목 universe

## 출력
- 대표 종목
- 이벤트 태그
- 감성: `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- 중요도: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- What/Why/Impact 요약
- 중복 제거 키
- confidence와 model version

## 모델
- 버전: `financial-ml-tfidf-logreg-20260622090407`
- 구조: TF-IDF char/word n-gram + Logistic Regression
- stock linker: 전체 한국 종목 universe 기반 종목명/종목코드 매핑
- pseudo-label은 teacher confidence gate와 라벨 quota를 통과한 샘플만 사용한다.

## 평가
| 평가셋 | 샘플 | 이벤트 macro F1 | 이벤트 recall | 감성 accuracy | 중요도 accuracy | 종목 accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Benchmark | 768 | 0.9844 | 1.0000 | 0.9688 | 0.9583 | 1.0000 |
| Real disclosure gold | 30 | 0.9867 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Real news gold | 80 | 0.9221 | 0.9875 | 0.9750 | 0.9625 | 1.0000 |
| Stock review gold | 500 | 0.7307 | 0.9320 | 0.9180 | 0.8480 | 0.9940 |

## 산출물
- Artifact: `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`
- Release report: `reports/model-release-report.json`
- Evaluation report: `reports/ml-model-evaluation.json`

## 한계
- Stock review gold에서 희소 이벤트 라벨 macro F1이 낮다.
- 운영 로그 기반 gold 확장과 라벨별 calibration 보강이 필요하다.
