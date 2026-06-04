# 금융 NLP ML 모델 카드

## 모델명
`financial-ml-tfidf-logreg-20260604122101`

## 목적
- 한국 주식 뉴스·공시의 이벤트 태그, 감성, 중요도를 자체 ML 모델로 분류한다.
- Hana-OmniLens-API의 Watchlist News & Disclosure Alert API payload 생성에 사용한다.
- ChatGPT API나 외부 LLM에 의존하지 않는다.

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
- 모델 버전

## 학습 데이터
- 수집 raw 위치: `data/raw/collected_alerts.jsonl`
- 약지도 라벨 위치: `data/processed/weak_labeled_alerts.jsonl`
- 약지도 distillation 리포트: `reports/weak-distillation-report.json`
- 버전별 release 리포트: `reports/model-release-report.json`
- 수동 curated corpus: `data/training/financial_alert_corpus.jsonl`
- 합성 증강 corpus: `data/training/financial_alert_augmented.jsonl`
- 뉴스 제목체 증강 corpus: `data/training/financial_alert_news_style_augmented.jsonl`
- 사람이 검수한 실제 뉴스 학습 gold: `data/training/financial_alert_real_news_gold.jsonl`
- curated gold benchmark: `data/evaluation/financial_alert_eval.jsonl`
- 사람이 검수한 실공시 gold: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 사람이 검수한 실제 뉴스 평가 gold: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 이번 artifact 학습 샘플 수: 3,949
- supervised 학습 샘플 수: 3,589
- teacher-gated pseudo-label 학습 샘플 수: 360
- 실제 수집 raw 총량: 37,278건
- 실제 수집 원천: OpenDART 공시검색 25,966건
- 실제 수집 원천: Naver News Search 11,312건
- 합성 증강 샘플 수: 1,656건
- 뉴스 제목체 증강 샘플 수: 1,872건
- 실제 뉴스 학습 gold 샘플 수: 43건
- gold benchmark 샘플 수: 768건
- 실공시 gold 샘플 수: 30건
- 실제 뉴스 gold 샘플 수: 56건
- 약지도 후보 수: 37,278건
- distillation 통과 후보 수: 4,845건
- teacher confidence gate 통과 후 artifact 학습 승격 후보 수: 360건
- 수집기는 429 rate limit과 5xx 장애에 대해 재시도와 지수 백오프를 수행한다.
- 수집 실패로 새 결과가 기존 raw 수보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
- 수집 raw와 약지도 라벨은 학습 재현성 때문에 커밋하지만, 외부 API 키와 비공개 credential은 포함하지 않는다.
- 약지도 라벨은 후보 풀로 유지하고 teacher confidence gate와 라벨별 quota를 통과한 pseudo-label만 이벤트 모델 학습에 승격한다.
- 감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 검수·균형 corpus만으로 학습한다.
- 실제 뉴스 학습 gold와 실제 뉴스 평가 gold는 동일 문장을 공유하지 않는다.

## 학습 방식
- `scripts/collect_training_data.py`가 Naver News Search와 OpenDART에서 원문 제목·snippet·링크를 수집한다.
- `weak_labeler.py`가 수집 원문에 약지도 라벨을 부여해 학습 후보를 만든다.
- `weak_distiller.py`가 약지도 후보의 노이즈를 제거하고 고신호 후보를 선별한다.
- supervised teacher 모델이 distillation 후보를 다시 예측하고, 이벤트·감성·중요도 confidence와 weak-label 합의 기준을 통과한 후보만 pseudo-label로 승격한다.
- `scripts/build_augmented_training_data.py`가 저작권 문제가 없는 금융 문장 증강 corpus를 생성한다.
- `scripts/build_news_style_training_data.py`가 실제 Naver 뉴스 제목체를 반영한 저작권 안전 증강 corpus를 생성한다.
- `scripts/build_gold_evaluation_data.py`가 훈련셋과 별도 문장 패턴의 768건 benchmark를 생성한다.
- `scripts/train_ml_model.py`가 TF-IDF feature와 Logistic Regression 기반 supervised ML 모델과 teacher-gated student 이벤트 모델을 학습한다.
- 이벤트 태그는 char n-gram과 한국어 금융 token n-gram을 결합한 One-vs-Rest multilabel classifier로 학습한다.
- 이벤트 태그 모델은 `source_type`을 feature로 함께 사용해 공시 입력의 `DISCLOSURE` 라벨 누락을 줄인다.
- 감성은 char n-gram과 한국어 금융 token n-gram을 결합한 다중 클래스 Logistic Regression으로 학습한다.
- 중요도는 source type, char n-gram, 한국어 금융 token n-gram을 결합한 다중 클래스 Logistic Regression으로 학습한다.
- 금융 tokenizer는 `잠정실적`, `공급계약`, `유상증자`, `타법인주식`, `자기주식처분`, `주주총회`, `소송등`, `상장폐지`, `주주환원`, `주식병합`, `지분투자`, `생산차질` 같은 한국어 복합 금융 표현을 도메인 token으로 추가한다.
- 이벤트 태그 probability threshold는 기본 0.30으로 두고, 중립 시황의 `RISK` 과잉 태깅을 줄이기 위해 `RISK`만 0.42로 calibration했다.
- 학습 시 검수·균형 코퍼스를 80:20 holdout으로 나눠 검증한 뒤 전체 코퍼스로 최종 artifact를 재학습한다.
- 약지도 후보 중 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건만 `promoted_to_student_training` 상태로 이벤트 모델 학습에 승격했다.
- 생성 artifact는 `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`이다.

## Holdout 검증 결과
- 위치: `reports/ml-training-report.json`
- supervised 학습 split: 2,871건
- supervised 검증 split: 718건
- 이벤트 subset recall: 0.9958
- 이벤트 macro F1: 0.9970
- 감성 accuracy: 0.9930
- 중요도 accuracy: 0.9875
- 라벨별 F1: `DISCLOSURE` 1.0, `RISK` 0.9868, `CAPITAL_ACTION` 0.9941, `GENERAL_MARKET` 1.0, `EARNINGS` 1.0, `CONTRACT` 1.0, `CORPORATE_ACTION` 1.0, `MACRO` 0.9950
- 감성·중요도 confusion matrix를 함께 기록한다.

## Gold 평가 결과
- 위치: `reports/ml-model-evaluation.json`
- 평가 샘플 수: 768
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 1.0
- 감성 accuracy: 1.0
- 중요도 accuracy: 0.9427
- 종목 매핑 accuracy: 1.0
- 라벨별 precision, recall, F1과 감성·중요도 confusion matrix를 함께 기록한다.

## 실공시 Gold 평가 결과
- 위치: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 평가 샘플 수: 30
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 1.0
- 감성 accuracy: 1.0
- 중요도 accuracy: 0.9667
- 종목 매핑 accuracy: 1.0

## 실제 뉴스 Gold 평가 결과
- 위치: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 평가 샘플 수: 56
- 이벤트 태그 recall: 0.9821
- 이벤트 태그 macro F1: 0.9525
- 감성 accuracy: 0.9821
- 중요도 accuracy: 0.9643
- 종목 매핑 accuracy: 1.0

## Release gate
- 위치: `reports/model-release-report.json`
- 현재 모델 버전: `financial-ml-tfidf-logreg-20260604122101`
- 전체 상태: `pass`
- release gate는 holdout, 768건 benchmark, 30건 OpenDART 실공시 gold, 56건 Naver 실제 뉴스 gold 평가를 모두 포함한다.
- pseudo-label consistency check는 distillation 리포트의 승격 수와 학습 리포트의 pseudo-label 학습 수가 일치하는지 검증한다.

## 한계
- Naver 뉴스 gold set을 56건으로 확대했지만 종목·업종·기간을 넓혀 계속 확장해야 한다.
- 약지도 라벨은 대규모 bootstrapping 용도이며, teacher confidence gate를 통과한 일부 후보만 artifact 이벤트 모델 학습에 투입한다.
- 현재 distillation 후보는 supervised teacher가 다시 검증해야 하는 후보 풀이지 최종 정답셋이 아니다.
- pseudo-label은 `RISK`, `CONTRACT`, `CORPORATE_ACTION`처럼 gold gate를 유지한 라벨만 승격했다. 다른 라벨은 후보는 존재하지만 현재 artifact 학습에는 투입하지 않는다.
- 사람이 검수한 실데이터 gold label set은 현재 실공시 30건, 실제 뉴스 56건이므로 주기적으로 확대해야 한다.
- 본문 전문을 저장·재배포하지 않고 제목·snippet 중심으로 학습한다.
- 실제 투자 판단을 위한 추천 모델이 아니다.

## 운영 전 필수 보강
- Naver 뉴스 수집 쿼리 확대와 일 단위 증분 수집
- 사람이 검수한 gold label과 약지도 label의 품질 비교
- 사람이 검수한 뉴스 gold label set 확대
- 모델 drift 감시와 재학습 기준 정의
