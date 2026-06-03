# 금융 NLP ML 모델 카드

## 모델명
`financial-ml-tfidf-logreg-20260603215338`

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
- 수집 raw 위치: `data/raw/collected_alerts.jsonl` (gitignore)
- 약지도 라벨 위치: `data/processed/weak_labeled_alerts.jsonl` (gitignore)
- 수동 curated corpus: `data/training/financial_alert_corpus.jsonl`
- 합성 증강 corpus: `data/training/financial_alert_augmented.jsonl`
- 뉴스 제목체 증강 corpus: `data/training/financial_alert_news_style_augmented.jsonl`
- 사람이 검수한 실제 뉴스 학습 gold: `data/training/financial_alert_real_news_gold.jsonl`
- curated gold benchmark: `data/evaluation/financial_alert_eval.jsonl`
- 사람이 검수한 실공시 gold: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 사람이 검수한 실제 뉴스 평가 gold: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 이번 artifact 학습 샘플 수: 3,571
- 실제 수집 raw 총량: 14,169건
- 실제 수집 원천: OpenDART 공시검색 12,967건
- 실제 수집 원천: Naver News Search 1,202건
- 합성 증강 샘플 수: 1,656건
- 뉴스 제목체 증강 샘플 수: 1,872건
- 실제 뉴스 학습 gold 샘플 수: 25건
- gold benchmark 샘플 수: 768건
- 실공시 gold 샘플 수: 30건
- 실제 뉴스 gold 샘플 수: 36건
- 수집기는 429 rate limit과 5xx 장애에 대해 재시도와 지수 백오프를 수행한다.
- 수집 실패로 새 결과가 기존 raw 수보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
- 약지도 라벨은 후보 풀로 유지하되, 현재 artifact는 검수·균형 corpus로 학습한다.
- 실제 뉴스 학습 gold와 실제 뉴스 평가 gold는 동일 문장을 공유하지 않는다.

## 학습 방식
- `scripts/collect_training_data.py`가 Naver News Search와 OpenDART에서 원문 제목·snippet·링크를 수집한다.
- `weak_labeler.py`가 수집 원문에 약지도 라벨을 부여해 학습 후보를 만든다.
- `scripts/build_augmented_training_data.py`가 저작권 문제가 없는 금융 문장 증강 corpus를 생성한다.
- `scripts/build_news_style_training_data.py`가 실제 Naver 뉴스 제목체를 반영한 저작권 안전 증강 corpus를 생성한다.
- `scripts/build_gold_evaluation_data.py`가 훈련셋과 별도 문장 패턴의 768건 benchmark를 생성한다.
- `scripts/train_ml_model.py`가 TF-IDF feature와 Logistic Regression 기반 supervised ML 모델을 학습한다.
- 이벤트 태그는 char n-gram과 한국어 금융 token n-gram을 결합한 One-vs-Rest multilabel classifier로 학습한다.
- 이벤트 태그 모델은 `source_type`을 feature로 함께 사용해 공시 입력의 `DISCLOSURE` 라벨 누락을 줄인다.
- 감성은 char n-gram과 한국어 금융 token n-gram을 결합한 다중 클래스 Logistic Regression으로 학습한다.
- 중요도는 source type, char n-gram, 한국어 금융 token n-gram을 결합한 다중 클래스 Logistic Regression으로 학습한다.
- 금융 tokenizer는 `잠정실적`, `공급계약`, `유상증자`, `타법인주식`, `자기주식처분`, `주주총회`, `소송등`, `상장폐지` 같은 한국어 복합 금융 표현을 도메인 token으로 추가한다.
- 이벤트 태그 probability threshold는 평가셋 기준 과잉 태그를 줄이기 위해 0.35로 튜닝했다.
- 학습 시 전체 코퍼스를 80:20 holdout으로 나눠 검증한 뒤 전체 코퍼스로 최종 artifact를 재학습한다.
- 생성 artifact는 `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`이다.

## Holdout 검증 결과
- 위치: `reports/ml-training-report.json`
- 학습 split: 2,856건
- 검증 split: 715건
- 이벤트 subset recall: 0.9972
- 이벤트 macro F1: 0.9941
- 감성 accuracy: 0.9958
- 중요도 accuracy: 0.9930
- 라벨별 F1: `DISCLOSURE` 0.9970, `RISK` 0.9973, `CAPITAL_ACTION` 0.9941, `GENERAL_MARKET` 0.9851, `EARNINGS` 1.0, `CONTRACT` 1.0, `CORPORATE_ACTION` 0.9944, `MACRO` 0.9852
- 감성·중요도 confusion matrix를 함께 기록한다.

## Gold 평가 결과
- 위치: `reports/ml-model-evaluation.json`
- 평가 샘플 수: 768
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 1.0
- 감성 accuracy: 1.0
- 중요도 accuracy: 0.9414
- 종목 매핑 accuracy: 1.0
- 라벨별 precision, recall, F1과 감성·중요도 confusion matrix를 함께 기록한다.

## 실공시 Gold 평가 결과
- 위치: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 평가 샘플 수: 30
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 1.0
- 감성 accuracy: 1.0
- 중요도 accuracy: 0.9333
- 종목 매핑 accuracy: 1.0

## 실제 뉴스 Gold 평가 결과
- 위치: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 평가 샘플 수: 36
- 이벤트 태그 recall: 0.9444
- 이벤트 태그 macro F1: 0.9075
- 감성 accuracy: 0.9167
- 중요도 accuracy: 0.8889
- 종목 매핑 accuracy: 1.0

## 한계
- Naver 뉴스 gold set을 추가했지만 아직 36건 규모라 종목·업종·기간을 넓혀 계속 확장해야 한다.
- 약지도 라벨은 대규모 bootstrapping 용도이며, 검수되지 않은 상태로 artifact 학습에 직접 투입하지 않는다.
- 사람이 검수한 실데이터 gold label set은 현재 실공시 30건, 실제 뉴스 36건이므로 주기적으로 확대해야 한다.
- 본문 전문을 저장·재배포하지 않고 제목·snippet 중심으로 학습한다.
- 실제 투자 판단을 위한 추천 모델이 아니다.

## 운영 전 필수 보강
- Naver 뉴스 수집 쿼리 확대와 일 단위 증분 수집
- 사람이 검수한 gold label과 약지도 label의 품질 비교
- 모델 drift 감시와 재학습 기준 정의
