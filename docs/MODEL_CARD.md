# 금융 NLP ML 모델 카드

## 모델명
`financial-ml-tfidf-logreg-20260605002536`

## 목적
- 한국 주식 뉴스·공시의 이벤트 태그, 감성, 중요도를 자체 ML 모델로 분류한다.
- Hana-OmniLens-API의 Watchlist News & Disclosure Alert API payload 생성에 사용한다.
- ChatGPT API나 외부 LLM에 의존하지 않는다.

## 입력
- source type: `NEWS` 또는 `DISCLOSURE`
- 제목
- snippet
- 후보 종목 목록
- 내부 국내주식 universe master
- 전 종목 stock linker 학습 term

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
- 이번 artifact 학습 샘플 수: 4,602
- supervised 학습 샘플 수: 3,609
- teacher-gated pseudo-label 학습 샘플 수: 993
- 실제 수집 raw 총량: 48,992건
- 실제 수집 원천: OpenDART 공시검색 25,966건
- 실제 수집 원천: Naver News Search 23,026건
- 합성 증강 샘플 수: 1,656건
- 뉴스 제목체 증강 샘플 수: 1,872건
- 실제 뉴스 학습 gold 샘플 수: 63건
- gold benchmark 샘플 수: 768건
- 실공시 gold 샘플 수: 30건
- 실제 뉴스 gold 샘플 수: 80건
- 약지도 후보 수: 48,992건
- distillation 통과 후보 수: 4,978건
- teacher confidence gate 통과 후 artifact 학습 승격 후보 수: 993건
- weak-label distillation 승격 수: 360건
- 종목 후보 큐 승격 수: 633건
- 종목 후보 큐 승격 종목 수: 633개
- 수집기는 429 rate limit과 5xx 장애에 대해 재시도와 지수 백오프를 수행한다.
- 수집 실패로 새 결과가 기존 raw 수보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
- 수집 raw와 약지도 라벨은 학습 재현성 때문에 커밋하지만, 외부 API 키와 비공개 credential은 포함하지 않는다.
- 국내주식 universe: `data/reference/korea_stock_universe.csv`
- stock universe sync 리포트: `reports/stock-universe-sync.json`
- stock coverage 리포트: `reports/stock-coverage-report.json`
- 종목·라벨 균형 학습 승격 후보 큐: `data/curation/stock_training_candidate_queue.jsonl`
- 학습 승격 후보 큐 리포트: `reports/stock-training-candidate-report.json`
- 학습 gold 검수 배치: `data/curation/stock_gold_training_review_batch.jsonl`
- 평가 gold 검수 배치: `data/curation/stock_gold_evaluation_review_batch.jsonl`
- gold 검수 배치 리포트: `reports/stock-gold-review-batch-report.json`
- gold 검수 validation 리포트: `reports/stock-gold-review-validation-report.json`
- gold active review 리포트: `reports/stock-gold-active-review-report.json`
- gold coverage review plan: `data/curation/stock_gold_coverage_review_plan.jsonl`
- gold coverage review plan 리포트: `reports/stock-gold-coverage-plan-report.json`
- gold coverage active review packet: `data/curation/stock_gold_coverage_active_review_packet.jsonl`
- gold coverage active review 리포트: `reports/stock-gold-coverage-active-review-report.json`
- gold coverage promotion 리포트: `reports/stock-gold-coverage-promotion-report.json`
- gold coverage validation 리포트: `reports/stock-gold-coverage-validation-report.json`
- confidence calibration 리포트: `reports/model-confidence-calibration.json`
- stock candidate quota experiment 리포트: `reports/stock-candidate-quota-experiment.json`
- 승인된 학습 gold 승격 파일: `data/training/financial_alert_stock_review_gold.jsonl`
- 승인된 평가 gold 승격 파일: `data/evaluation/financial_alert_stock_review_gold.jsonl`
- gold 승격 리포트: `reports/stock-gold-promotion-report.json`
- OpenDART 고유번호 기반 universe 종목 수: 3,967개
- 분석 API는 요청 후보 종목이 비어 있거나 50개 이하 후보에 포함되지 않은 종목도 내부 universe master로 매핑한다.
- 전체 universe 3,967개 종목의 6자리 종목코드 매핑을 회귀 테스트로 검증한다.
- stock linker ML 학습 데이터: `data/training/stock_linker_training.jsonl`
- stock linker ML artifact: `src/hannah_montana_ai/model_store/stock_linker_ml.joblib`
- stock linker 학습 리포트: `reports/stock-linker-training-report.json`
- raw 후보에서 보수적 종목명·종목코드 매칭으로 확인한 종목 수: 2,987개
- 학습 승격 후보 큐 샘플 수: 10,226건
- 학습 승격 후보 큐 종목 수: 2,804개
- 학습 gold 검수 배치 종목 수: 300개
- 평가 gold 검수 배치 종목 수: 100개
- coverage review plan 학습 목표 종목 수: 1,500개
- coverage review plan 평가 목표 종목 수: 500개
- coverage review plan 전체 계획 종목 수: 2,000개
- coverage review plan과 기존 supervised/evaluation 종목을 합친 후보 큐 커버 종목 수: 2,068개
- coverage active review packet row 수: 2,000건
- coverage active review 학습 wave 수: 13개
- coverage active review 평가 wave 수: 5개
- coverage packet 승인 승격 row 수: 학습 0건, 평가 0건
- coverage packet validation 상태: `fail`
- coverage packet validation 목표: 학습 1,500종목, 평가 500종목, wave별 승인 100종목
- release service readiness 상태: `fail`
- 현재 검수 validation 승인 가능 종목 수: 학습 0개, 평가 0개
- supervised 학습 데이터 종목 수: 38개
- evaluation 데이터 종목 수: 57개
- 전 종목 실서비스 coverage gate는 현재 `fail`이며, 이는 raw 후보 폭에 비해 사람이 검수한 supervised/gold 종목 커버리지가 아직 부족하다는 뜻이다.
- 학습 승격 후보 큐는 `needs_human_review` 상태이며, 사람이 검수해 승격하기 전까지 gold label이나 supervised 정답셋으로 취급하지 않는다.
- gold 검수 배치도 `needs_human_review` 상태이며, 사람이 승인하기 전까지 supervised 학습셋이나 evaluation gold로 편입하지 않는다.
- gold coverage review plan도 `needs_human_review` 상태이며, 장기 검수 순서를 정하는 산출물이지 자동 정답셋이 아니다.
- coverage active review packet의 모델 제안 라벨과 confidence도 검수 보조 정보이며 자동 정답셋이 아니다.
- `human_review_approved` 상태와 검수자 메타데이터, 최종 이벤트·감성·중요도 라벨이 모두 있는 검수 row만 별도 stock review gold 파일로 승격된다.
- coverage packet에서 승격된 gold row는 source review wave/stage/reason과 모델 제안 lineage를 함께 보존한다.
- validation 리포트는 승격 전 승인 가능 row가 학습 300개 종목과 평가 100개 종목 목표를 채우는지 검사한다.
- active review 리포트는 모델 제안 라벨, 신뢰도, disagreement를 검수 보조 정보로 제공하며 자동 정답으로 쓰지 않는다.
- confidence calibration 리포트는 평가셋별 확률 calibration과 고신뢰 오답을 release monitoring 신호로 기록하며 라벨을 생성하거나 승격하지 않는다.
- 학습·평가 스크립트는 승인된 stock review gold 파일이 존재할 때만 포함한다.
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
- 종목 매핑은 request 후보를 먼저 사용하고, 같은 종목코드가 없으면 내부 universe master를 fallback으로 사용한다.
- 내부 universe fallback은 TF-IDF char n-gram stock linker가 예측한 종목코드를 먼저 확인한 뒤, 대표 종목 오탐 방지를 위해 실제 선두 종목 term 매칭 여부를 검증한다.
- stock linker는 전체 universe 3,967개 종목코드와 trainable 종목명을 학습 term으로 사용한다. 현재 전 종목코드 템플릿 정확도는 1.0, trainable 종목명 템플릿 정확도는 0.9921이다.
- 이벤트 태그 probability threshold는 기본 0.30으로 두고, 실제 뉴스 gold 기준으로 `CONTRACT` 0.42, `CORPORATE_ACTION` 0.18, `EARNINGS` 0.36, `GENERAL_MARKET` 0.32, `MACRO` 0.36, `RISK` 0.50을 label별 calibration했다.
- 학습 시 검수·균형 코퍼스를 80:20 holdout으로 나눠 검증한 뒤 전체 코퍼스로 최종 artifact를 재학습한다.
- 약지도 후보 중 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건을 이벤트 모델 학습에 승격했다.
- 종목 후보 큐에서는 teacher gate와 종목별 quota를 통과한 `RISK` 225건, `CONTRACT` 210건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 21건, `MACRO` 12건을 이벤트 모델 학습에 추가했다.
- 종목 후보의 per-stock quota는 1건으로 제한해 633건이 633개 종목에 분산되도록 했다.
- `stock-candidate-quota-experiment`에서 이전 release profile은 500건/500종목으로 통과했고, risk/contract per-stock 2 profile은 773건/589종목까지 늘었지만 실제 뉴스 gold recall gate를 통과하지 못했다. current release는 633건/633종목으로 실제 뉴스 gold gate를 통과해 best profile로 선택했다.
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
- 이벤트 태그 recall: 0.9500
- 이벤트 태그 macro F1: 0.9181
- 감성 accuracy: 0.9125
- 중요도 accuracy: 0.9250
- 종목 매핑 accuracy: 1.0

## Confidence calibration
- 위치: `reports/model-confidence-calibration.json`
- benchmark 샘플 수: 768
- benchmark 이벤트 멀티라벨 결정 수: 6,144
- benchmark 이벤트 expected calibration error: 0.068000
- benchmark 이벤트 Brier score: 0.011187
- benchmark 감성 top confidence ECE: 0.149164
- benchmark 중요도 top confidence ECE: 0.118967
- 실제 뉴스 gold 이벤트 expected calibration error: 0.112869
- confidence 리포트는 고신뢰 오답을 따로 기록해 운영 알림 노출 전 threshold 재보정과 human review 우선순위 판단에 사용한다.

## Release gate
- 위치: `reports/model-release-report.json`
- 현재 모델 버전: `financial-ml-tfidf-logreg-20260605002536`
- 전체 상태: `pass`
- release gate는 holdout, 768건 benchmark, 30건 OpenDART 실공시 gold, 80건 Naver 실제 뉴스 gold 평가를 모두 포함한다.
- pseudo-label consistency check는 distillation 리포트의 승격 수와 학습 리포트의 pseudo-label 학습 수가 일치하는지 검증한다.
- `overall_status=pass`는 모델 품질 release gate 통과를 뜻하며, 전 종목 실서비스 준비 완료를 뜻하지 않는다.
- `service_readiness.overall_status=fail`은 사람이 승인한 coverage packet gold가 아직 학습 1,500종목, 평가 500종목, wave별 100종목 기준을 충족하지 못했다는 뜻이다.

## Pseudo-label promotion gate
- 위치: `reports/pseudo-label-promotion-monitoring.json`
- 48,992건 raw 후보 중 4,978건이 고신호 후보로 남았다.
- teacher confidence 또는 weak-label 합의 기준에서 3,587건이 탈락했다.
- weak-label distillation에서는 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건을 student 이벤트 모델 학습에 승격했다.
- 종목 후보 큐에서는 `RISK` 225건, `CONTRACT` 210건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 21건, `MACRO` 12건을 teacher gate로 추가 승격했다.
- `CAPITAL_ACTION`, `DISCLOSURE`, `EARNINGS`, `MACRO`는 고신호 후보가 충분하지만 gold gate 실험 전까지 quota 0으로 유지한다.

## 한계
- Naver 뉴스 gold set을 80건으로 확대하고 종목코드 30개를 포함했지만, 분기별 증분 수집과 업종별 샘플 균형은 계속 관리해야 한다.
- 국내주식 universe 3,967개를 추적하지만 현재 artifact의 supervised 학습 종목 커버리지는 38개라 전 종목급 실서비스 모델로 보기에는 부족하다.
- raw 후보는 2,987개 종목까지 매칭되므로 다음 단계는 raw 후보를 종목별·라벨별로 검수해 supervised/gold 데이터로 승격하는 것이다.
- 후보 큐는 2,804개 종목을 포함하지만 약지도 기반 검수 대기 데이터이므로 gold label로 직접 사용하지 않는다.
- coverage review plan은 2,000개 종목의 검수 과제를 만들지만 아직 검수자 승인이 없으므로 supervised coverage gate를 통과시키지 않는다.
- 현재 artifact는 후보 큐 중 633개 종목의 633건만 teacher gate를 통과한 event-model-only pseudo-label로 제한 투입했다.
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
- `data/curation/stock_gold_training_review_batch.jsonl`와 `data/curation/stock_gold_evaluation_review_batch.jsonl`의 사람 검수 승인, 최종 라벨 확정, 정답셋 승격
- `data/curation/stock_gold_coverage_review_plan.jsonl`의 wave 단위 검수 승인과 stock review gold 증분 승격
- `data/curation/stock_gold_coverage_active_review_packet.jsonl`의 모델 제안 라벨을 참고한 사람 검수와 최종 라벨 확정
- `scripts/promote_stock_gold_coverage_review_packet.py` 실행 후 승인된 stock review gold를 포함한 재학습
- `scripts/validate_stock_gold_coverage_review_packet.py` 기준 coverage packet 승인 gate 통과
- 사람이 검수한 gold label과 약지도 label의 품질 비교
- 실제 뉴스 gold label set 월별 증분 확대와 drift 감시
- 모델 drift 감시와 재학습 기준 정의
