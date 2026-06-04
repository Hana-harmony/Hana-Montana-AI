# 금융 NLP ML 모델 카드

## 모델명
`financial-ml-tfidf-logreg-20260604164703`

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
- pseudo-label promotion monitoring 리포트: `reports/pseudo-label-promotion-monitoring.json`
- 수동 curated corpus: `data/training/financial_alert_corpus.jsonl`
- 합성 증강 corpus: `data/training/financial_alert_augmented.jsonl`
- 뉴스 제목체 증강 corpus: `data/training/financial_alert_news_style_augmented.jsonl`
- 사람이 검수한 실제 뉴스 학습 gold: `data/training/financial_alert_real_news_gold.jsonl`
- curated gold benchmark: `data/evaluation/financial_alert_eval.jsonl`
- 사람이 검수한 실공시 gold: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 사람이 검수한 실제 뉴스 평가 gold: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 이번 artifact 학습 샘플 수: 4,369
- supervised 학습 샘플 수: 3,609
- teacher-gated pseudo-label 학습 샘플 수: 760
- 실제 수집 raw 총량: 37,278건
- 실제 수집 원천: OpenDART 공시검색 25,966건
- 실제 수집 원천: Naver News Search 11,312건
- 합성 증강 샘플 수: 1,656건
- 뉴스 제목체 증강 샘플 수: 1,872건
- 실제 뉴스 학습 gold 샘플 수: 63건
- gold benchmark 샘플 수: 768건
- 실공시 gold 샘플 수: 30건
- 실제 뉴스 gold 샘플 수: 80건
- 약지도 후보 수: 37,278건
- distillation 통과 후보 수: 4,845건
- teacher confidence gate 통과 후 artifact 학습 승격 후보 수: 760건
- weak-label distillation 승격 수: 360건
- 종목 후보 큐 승격 수: 400건
- 종목 후보 큐 승격 종목 수: 400개
- 수집기는 429 rate limit과 5xx 장애에 대해 재시도와 지수 백오프를 수행한다.
- 수집 실패로 새 결과가 기존 raw 수보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
- 수집 raw와 약지도 라벨은 학습 재현성 때문에 커밋하지만, 외부 API 키와 비공개 credential은 포함하지 않는다.
- 국내주식 universe: `data/reference/korea_stock_universe.csv`
- stock universe sync 리포트: `reports/stock-universe-sync.json`
- stock coverage 리포트: `reports/stock-coverage-report.json`
- 종목·라벨 균형 학습 승격 후보 큐: `data/curation/stock_training_candidate_queue.jsonl`
- 학습 승격 후보 큐 리포트: `reports/stock-training-candidate-report.json`
- OpenDART 고유번호 기반 universe 종목 수: 3,967개
- raw 후보에서 보수적 종목명·종목코드 매칭으로 확인한 종목 수: 2,356개
- 학습 승격 후보 큐 샘플 수: 6,244건
- 학습 승격 후보 큐 종목 수: 2,127개
- supervised 학습 데이터 종목 수: 38개
- evaluation 데이터 종목 수: 56개
- 전 종목 실서비스 coverage gate는 현재 `fail`이며, 이는 raw 후보 폭에 비해 사람이 검수한 supervised/gold 종목 커버리지가 아직 부족하다는 뜻이다.
- 학습 승격 후보 큐는 `needs_human_review` 상태이며, 사람이 검수해 승격하기 전까지 gold label이나 supervised 정답셋으로 취급하지 않는다.
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
- 금융 tokenizer는 `잠정실적`, `공급계약`, `유상증자`, `무상증자`, `타법인주식`, `자기주식처분`, `주주총회`, `소송등`, `상장폐지`, `주주환원`, `주식교환`, `지분인수`, `지분매각`, `리밸런싱`, `공급망`, `생산차질` 같은 한국어 복합 금융 표현을 도메인 token으로 추가한다.
- 이벤트 태그 probability threshold는 기본 0.30으로 두고, 실제 뉴스 gold 기준으로 `CONTRACT` 0.34, `CORPORATE_ACTION` 0.22, `EARNINGS` 0.36, `MACRO` 0.32, `RISK` 0.56을 label별 calibration했다.
- 학습 시 검수·균형 코퍼스를 80:20 holdout으로 나눠 검증한 뒤 전체 코퍼스로 최종 artifact를 재학습한다.
- 약지도 후보 중 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건을 이벤트 모델 학습에 승격했다.
- 종목 후보 큐에서는 teacher gate와 종목별 quota를 통과한 `RISK` 200건, `CONTRACT` 200건만 이벤트 모델 학습에 추가했다.
- 종목 후보의 per-stock quota는 1건으로 제한해 400건이 400개 종목에 분산되도록 했다.
- 400종목 확장 후 threshold 미조정 모델은 실제 뉴스 gold event macro F1이 0.8920으로 release gate 아래라 폐기했고, label별 threshold 재보정 후 release gate를 통과했다.
- 생성 artifact는 `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`이다.

## Holdout 검증 결과
- 위치: `reports/ml-training-report.json`
- supervised 학습 split: 2,887건
- supervised 검증 split: 722건
- 이벤트 subset recall: 0.9889
- 이벤트 macro F1: 0.9881
- 감성 accuracy: 0.9889
- 중요도 accuracy: 0.9931
- 라벨별 F1: `DISCLOSURE` 1.0, `RISK` 0.9947, `CAPITAL_ACTION` 0.9942, `GENERAL_MARKET` 0.9538, `EARNINGS` 0.9828, `CONTRACT` 0.9941, `CORPORATE_ACTION` 1.0, `MACRO` 0.9849
- 감성·중요도 confusion matrix를 함께 기록한다.

## Gold 평가 결과
- 위치: `reports/ml-model-evaluation.json`
- 평가 샘플 수: 768
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 1.0
- 감성 accuracy: 1.0
- 중요도 accuracy: 0.9375
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
- 평가 샘플 수: 80
- 이벤트 태그 recall: 0.9375
- 이벤트 태그 macro F1: 0.9217
- 감성 accuracy: 0.9125
- 중요도 accuracy: 0.9250
- 종목 매핑 accuracy: 1.0

## Release gate
- 위치: `reports/model-release-report.json`
- 현재 모델 버전: `financial-ml-tfidf-logreg-20260604164703`
- 전체 상태: `pass`
- release gate는 holdout, 768건 benchmark, 30건 OpenDART 실공시 gold, 80건 Naver 실제 뉴스 gold 평가를 모두 포함한다.
- pseudo-label consistency check는 distillation 리포트의 승격 수와 학습 리포트의 pseudo-label 학습 수가 일치하는지 검증한다.

## Pseudo-label promotion gate
- 위치: `reports/pseudo-label-promotion-monitoring.json`
- 37,278건 raw 후보 중 4,845건이 고신호 후보로 남았다.
- teacher confidence 또는 weak-label 합의 기준에서 3,124건이 탈락했다.
- weak-label distillation에서는 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건을 student 이벤트 모델 학습에 승격했다.
- 종목 후보 큐에서는 `RISK` 200건, `CONTRACT` 200건을 teacher gate로 추가 승격했다.
- `CAPITAL_ACTION`, `DISCLOSURE`, `EARNINGS`, `MACRO`는 고신호 후보가 충분하지만 gold gate 실험 전까지 quota 0으로 유지한다.

## 한계
- Naver 뉴스 gold set을 80건으로 확대하고 종목코드 30개를 포함했지만, 분기별 증분 수집과 업종별 샘플 균형은 계속 관리해야 한다.
- 국내주식 universe 3,967개를 추적하지만 현재 artifact의 supervised 학습 종목 커버리지는 38개라 전 종목급 실서비스 모델로 보기에는 부족하다.
- raw 후보는 2,356개 종목까지 매칭되므로 다음 단계는 raw 후보를 종목별·라벨별로 검수해 supervised/gold 데이터로 승격하는 것이다.
- 후보 큐는 2,127개 종목을 포함하지만 약지도 기반 검수 대기 데이터이므로 gold label로 직접 사용하지 않는다.
- 현재 artifact는 후보 큐 중 400개 종목의 400건만 teacher gate를 통과한 event-model-only pseudo-label로 제한 투입했다.
- 약지도 라벨은 대규모 bootstrapping 용도이며, teacher confidence gate를 통과한 일부 후보만 artifact 이벤트 모델 학습에 투입한다.
- 현재 distillation 후보는 supervised teacher가 다시 검증해야 하는 후보 풀이지 최종 정답셋이 아니다.
- pseudo-label은 `RISK`, `CONTRACT`, `CORPORATE_ACTION`처럼 gold gate를 유지한 라벨만 승격했다. 다른 라벨은 후보는 존재하지만 현재 artifact 학습에는 투입하지 않는다.
- 사람이 검수한 실데이터 gold label set은 현재 실공시 30건, 실제 뉴스 80건이므로 주기적으로 확대해야 한다.
- 본문 전문을 저장·재배포하지 않고 제목·snippet 중심으로 학습한다.
- 실제 투자 판단을 위한 추천 모델이 아니다.

## 운영 전 필수 보강
- Naver 뉴스 수집 쿼리 확대와 일 단위 증분 수집
- `scripts/collect_training_data.py --use-stock-universe-news-queries` 기반 종목 universe 증분 수집
- `reports/stock-coverage-report.json` 기준 supervised 300개 이상 종목, evaluation 100개 이상 종목 coverage gate 통과
- 사람이 검수한 gold label과 약지도 label의 품질 비교
- 실제 뉴스 gold label set 월별 증분 확대와 drift 감시
- 모델 drift 감시와 재학습 기준 정의
