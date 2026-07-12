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
- 요약 품질 gate: 생략부호, 문장 중간 잘림, 중요도·감성 메타 문구를 사용자 payload에서 제거한다.

## 모델
- 버전: `financial-ml-tfidf-logreg-20260622090407`
- 이벤트 구조: TF-IDF char/word n-gram, `source_type`, 한국 금융 token feature를 결합한 One-vs-Rest Logistic Regression multilabel classifier
- 감성 구조: TF-IDF char n-gram, 한국 금융 token feature, Logistic Regression 다중분류
- 중요도 구조: `source_type`, TF-IDF char n-gram, 한국 금융 token feature, Logistic Regression 다중분류
- 시장영향 보조 구조: 파일 기반 K-FNSPID의 실제 1·3·5거래일 반응으로 학습한 모델을 품질 gate 뒤에 결합한다.
- stock linker: `stock_linker_ml.joblib`의 TF-IDF char n-gram nearest-neighbor entity linker와 선두 term 검증
- 전문 v2: 제목/snippet 모델을 baseline으로 유지하고, 권리 확인된 전문이 있으면 full content summary와 content hash를 추가한다.
- What/Why/Impact는 검증 규칙으로 생성한다. Qwen3는 한국어→영어 번역에만 사용한다.
- pseudo-label은 teacher confidence gate와 라벨 quota를 통과한 샘플만 사용한다.
- 사람이 검수하지 않은 실제 전문 약한 라벨은 supervised loss와 holdout 정답에서 제외한다.
- 실제 뉴스 Gold 80건은 Codex 검수 상태, 검수 근거, 발표 시각, 원천 해시를 보존한다.

## 학습/추론 구성
- 학습 스크립트: `scripts/train_ml_model.py`
- 모델 trainer: `src/hannah_montana_ai/training/ml_trainer.py`
- Serving loader: `src/hannah_montana_ai/services/model.py`
- 종목 linker trainer: `src/hannah_montana_ai/training/stock_linker_trainer.py`
- 종목 universe: `data/reference/korea_stock_universe.csv`의 국내 3,967개 종목
- 이벤트 threshold: 기본 0.30, 실제 뉴스 gold 기준 라벨별 calibration 적용

## 평가
| 평가셋 | 샘플 | 이벤트 macro F1 | 이벤트 recall | 감성 accuracy | 중요도 accuracy | 종목 accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Benchmark | 768 | 0.9844 | 1.0000 | 0.9688 | 0.9583 | 1.0000 |
| Real disclosure gold | 30 | 0.9867 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Real news gold | 80 | 0.9221 | 0.9875 | 0.9750 | 0.9625 | 1.0000 |
| Stock review gold | 500 | 0.7307 | 0.9320 | 0.9180 | 0.8480 | 0.9940 |

## 산출물
- Artifact: `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`
- Stock linker artifact: `src/hannah_montana_ai/model_store/stock_linker_ml.joblib`
- Release report: `reports/model-release-report.json`
- Evaluation report: `reports/ml-model-evaluation.json`
- Confidence calibration: `reports/model-confidence-calibration.json`
- K-FNSPID artifact: `src/hannah_montana_ai/model_store/k_fnspid_impact_ml.joblib`
- K-FNSPID report: `reports/k-fnspid-impact-training-report.json`
- SOTA report: `reports/financial-alert-sota-benchmark.json`

## 한계
- Stock review gold에서 희소 이벤트 라벨 macro F1이 낮다.
- 운영 로그 기반 gold 확장과 라벨별 calibration 보강이 필요하다.
- K-FNSPID 시장영향 Test macro F1은 0.3014이므로 의미 기반 중요도를 대체하지 않고 보조 신호로만 사용한다.
