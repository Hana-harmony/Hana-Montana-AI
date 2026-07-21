# Hana Montana AI(KF-DeBERTa + K-FNSPID)

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
- `translation_mode`: 기본 `FULL`. 스케줄러 초기 적재는 `DEFERRED`를 사용해 전체 본문 생성형 번역과 분석 처리량을 분리한다.

## 출력
- 대표 종목
- 이벤트 태그
- 감성: `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- 중요도: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- What/Why/Impact 요약
- 중복 제거 키
- confidence와 model version
- 요약 품질 gate: 생략부호, 문장 중간 잘림, 중요도·감성 메타 문구를 사용자 payload에서 제거한다.
- `DEFERRED` 응답은 종목 연결·이벤트·감성·중요도·시장영향과 Qwen 영문 제목·What/Why/Impact를 생성하고 전문 번역만 비워 `SOURCE_LANGUAGE_FALLBACK`으로 표시한다. `FULL` 응답은 같은 Qwen 요약과 원문 전문 번역을 함께 완료한다.

## 모델
- 서비스 표기명: `Hana Montana AI(KF-DeBERTa + K-FNSPID)`
- 버전: `financial-ml-tfidf-logreg-20260714023257`
- 이벤트 구조: TF-IDF char/word n-gram, `source_type`, 한국 금융 token feature를 결합한 One-vs-Rest Logistic Regression multilabel classifier
- 감성 구조: `kakaobank/kf-deberta-base` 고정 리비전 + LoRA r=16 다중분류. 외부 Test·artifact SHA gate 통과 시 우선하고, 실패 시 TF-IDF Logistic Regression으로 fallback한다.
- 중요도 구조: `source_type`, TF-IDF char n-gram, 한국 금융 token feature, Logistic Regression 다중분류
- 시장영향 보조 구조: 파일 기반 K-FNSPID의 실제 1·3·5거래일 반응으로 학습한 모델을 품질 gate 뒤에 결합한다.
- stock linker: `stock_linker_ml.joblib`의 TF-IDF char n-gram nearest-neighbor entity linker와 선두 term 검증
- 전문 v2: 제목/snippet 모델을 baseline으로 유지하고, 권리 확인된 전문이 있으면 full content summary와 content hash를 추가한다.
- Qwen3가 한국어 원문과 KF-DeBERTa 감성·K-FNSPID 시장영향·이벤트·중요도 신호를 받아 영문 제목과 What/Why/Impact를 생성한다. 신호는 관점 설정에만 사용하고 원문 사실처럼 인용하지 않는다. 필수 필드 누락, 중복 문장, 한국어 잔존, 원문에 없는 숫자, 4단어 미만 조각 문장, 종결부호 누락, 종목코드로 시작하는 문장은 최대 1회 재생성 후 분석 실패로 처리하며 규칙 기반 요약으로 후퇴하지 않는다.
- pseudo-label은 teacher confidence gate와 라벨 quota를 통과한 샘플만 사용한다.
- 사람이 검수하지 않은 실제 공시 전문 약한 중요도 라벨은 Gold URL을 제거한 뒤 의미 중요도 후보 학습에만 사용한다. 감성 학습과 holdout Gold 정답에는 사용하지 않는다.
- 실제 뉴스 Gold 80건과 OpenDART 기본 공시 Gold 600건, 스트레스 Gold 310건은 Codex 검수 상태, 검수 근거, 발표 시각, 원천 해시를 보존한다. 기본 Gold와 겹치는 원천 전문 401건은 모델 학습 입력에서 제외하고, 스트레스 Gold는 원천 전문과도 중복이 없다.
- [공개 금융 감성 데이터](https://huggingface.co/datasets/mssongit/finance-task) `mssongit/finance-task:fnsentiment` 고정 리비전의 원본 Train 7,464 / Validation 933 / Test 933에서 정규화 중복·충돌과 분할 간 중복을 제거한 유효 7,407 / 932 / 932건을 사용한다.
- 공개·운영형 14,443건의 1차 다중 도메인 학습 뒤 실제 뉴스 63건 반복 노출, 공개 1,866건과 기타 운영형 1,200건 replay로 3,696건의 2차 도메인 적응을 수행한다. 누적 학습 노출은 18,139건이며 모든 운영 평가 문장과 공개 Validation/Test 중복은 제외한다.

## K-FNSPID 도입 전후 로직

비교 기준은 K-FNSPID 도입 직전 `main` commit `076e97f8`과 현재 모델이다.

| 단계 | 도입 전 | 현재 |
| --- | --- | --- |
| 이벤트 | TF-IDF char/word n-gram + One-vs-Rest Logistic Regression + 라벨별 규칙 보강 | 변경 없음 |
| 감성 | TF-IDF Logistic Regression 확률 + 금융 규칙 보강 | Validation Selection에서 잠근 KF-DeBERTa LoRA 후보. 공개·운영 gate 실패 시 기존 모델로 fallback |
| 의미 중요도 | `source_type`·TF-IDF·금융 token 기반 Logistic Regression + 규칙 보강 | Gold 비중복 공시 약지도에서 Validation으로 제목+요약 뷰를 선택하고 존속위험 코드북 floor로 강화. 시장영향과 분리해 의미 등급을 보존 |
| 시장영향 | 사용하지 않음 | DB가 아닌 일별 시세 Parquet 10,691,998행과 뉴스·공시 1,247,685건으로 1·3·5거래일 초과수익·거래량·변동성 등급 생성. 뉴스·공시 전문가를 분리하고 출처가 일치할 때만 등급·점수·confidence를 독립 출력 |
| 시간 처리 | 기사 텍스트 평가만 수행 | 장전·장중·장후·비거래일 세션별 유효 거래일, 7일 embargo, 시간 외삽 Test 적용 |
| 교란 억제 | 없음 | 동일 종목·거래일 다중 사건 제외, 사건 cluster 대표 기사 선택, 시장 평균 수익률 차감 |
| 배포 안전성 | 단일 joblib 모델 version | 고정 base revision, `safetensors`, artifact SHA-256·크기·독립 보고서 검증, 실패 시 기존 모델로 fail closed |
| model version | `financial_nlp_ml` 단일 version | 기존 version + 실제 활성 sentiment·impact version을 합성해 반환 |

도입 전후 상세 수치와 연구 주장 범위는 [K-FNSPID 도입 전후·연구 준비도](k-fnspid-research-readiness.md)를 단일 비교 문서로 사용한다.

## 학습/추론 구성
- 학습 스크립트: `scripts/train_ml_model.py`
- 모델 trainer: `src/hannah_montana_ai/training/ml_trainer.py`
- Serving loader: `src/hannah_montana_ai/services/model.py`
- 종목 linker trainer: `src/hannah_montana_ai/training/stock_linker_trainer.py`
- 종목 universe: `data/reference/korea_stock_universe.csv`의 국내 3,967개 종목
- 이벤트 threshold: 기본 0.30, 실제 뉴스 gold 기준 라벨별 calibration 적용

## 평가

아래 표는 `financial_nlp_ml` 통합 기준 모델의 기존 고정 평가이며 현재 KF-DeBERTa 후보 승격 결과가 아니다. 현재 Transformer 후보의 공개·운영 평가는 다음 문단과 `reports/korean-finance-sentiment-benchmark.json`을 정본으로 사용한다.
| 평가셋 | 샘플 | 이벤트 macro F1 | 이벤트 recall | 감성 accuracy | 중요도 accuracy | 종목 accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Benchmark | 768 | 0.9844 | 1.0000 | 0.9492 | 0.9323 | 1.0000 |
| Real disclosure Gold | 600 | 0.9979 | 0.9967 | 0.9233 | 1.0000 | 1.0000 |
| Real news Gold | 80 | 0.9184 | 0.9875 | 0.9000 | 0.9500 | 1.0000 |
| Stock review Gold | 500 | 0.7110 | 0.9280 | 0.7880 | 0.8060 | 0.9900 |

정규화 중복·충돌과 분할 간 중복을 제거한 공개 Test 932건에서 잠근 KF-DeBERTa LoRA는 accuracy 0.8852 / macro F1 0.8849, 기존 Hana TF-IDF는 0.4775 / 0.4415, `snunlp/KR-FinBERT-SC`는 0.7361 / 0.7266이다. KR-FinBERT-SC 대비 Macro-F1 차이의 paired bootstrap 95% CI는 `[0.1265, 0.1899]`이고 McNemar `p=9.81e-19`다. 그러나 이 Test는 과거 반복 조회되었으므로 독립 SOTA 근거가 아니다. 실제 공시 Gold 600건은 0.9150 / 0.8084, 뉴스 Gold 80건은 0.8625 / 0.8308이며 뉴스 accuracy gate 실패로 신규 후보를 배포하지 않는다.

공시 의미 중요도는 제목·요약·전문 뷰를 같은 시간 분할로 비교한 뒤 Gold를 보지 않고 제목+요약을 선택한다. 모델 단독 기본 Gold 600건은 accuracy 0.9850 / macro F1 0.9470이고, 존속위험 코드북 floor를 포함한 운영 파이프라인은 기본·스트레스 Gold 910건에서 0.9989 / 0.9962다. 시장영향은 의미 중요도 등급과 confidence를 변경하지 않으며 `market_impact_importance`, `market_impact_score`, `market_impact_confidence`로 별도 반환한다.

과거 v3 통합 스냅샷은 감성 정확도가 Benchmark `0.9688→0.9492`, 실제 뉴스 Gold `0.9750→0.9000`, Stock review Gold `0.9180→0.7880`으로 하락했다. 현재 누수 감사 프로토콜의 KF-DeBERTa 후보는 실제 뉴스 Gold 0.8625, 공시 Gold 0.9150이며 뉴스 gate 실패로 미승격이다. 중요도는 v3에서 `거래정지·불성실공시 단독=HIGH`로 코드북을 바꿔 Benchmark 수치를 직접 증감으로 해석하지 않는다. 코드북이 유지된 실제 뉴스 Gold는 `0.9625→0.9500`, Stock review Gold는 `0.8480→0.8060`으로 하락했다. 대신 독립 공시 중요도 파이프라인은 910건에서 0.9989 / 0.9962를 기록한다. 공개 감성 재현 Test와 공시 의미 중요도 개선, 기존 운영 분포 회귀가 동시에 존재하므로 모든 분포에서 우월하다고 주장하지 않는다.

## 산출물
- Artifact: `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`
- Stock linker artifact: `src/hannah_montana_ai/model_store/stock_linker_ml.joblib`
- Release report: `reports/model-release-report.json`
- Evaluation report: `reports/ml-model-evaluation.json`
- Confidence calibration: `reports/model-confidence-calibration.json`
- K-FNSPID artifact: `src/hannah_montana_ai/model_store/k_fnspid_impact_ml.joblib`
- K-FNSPID report: `reports/k-fnspid-impact-training-report.json`
- KF-DeBERTa 감성 artifact: `src/hannah_montana_ai/model_store/kf_deberta_sentiment/`
- KF-DeBERTa 학습 report: `reports/kf-deberta-sentiment-training-report.json`
- 금융 감성 SOTA 비교: `reports/korean-finance-sentiment-benchmark.json`
- SOTA report: `reports/financial-alert-sota-benchmark.json`

## 한계
- Stock review gold에서 희소 이벤트 라벨 macro F1이 낮다.
- 감성은 공개 균형 재현 Test에서 기존 모델과 KR-FinBERT-SC를 크게 상회하지만 과거 Test 반복 사용과 실제 뉴스 Gold gate 실패 때문에 독립 SOTA 또는 신규 배포 우위로 주장하지 않는다.
- 운영 Gold는 뉴스 80건·공시 600건으로 확대했지만 단일 Codex 검수이므로 독립 다중 평가자 합의를 대신하지 않는다.
- 운영 로그 기반 gold 확장과 라벨별 calibration 보강이 필요하다.
- K-FNSPID 시장영향은 텍스트로 미래 가격 충격을 예측하는 불확실성이 크므로 의미 기반 중요도를 대체하지 않고 보조 신호로만 사용한다.
