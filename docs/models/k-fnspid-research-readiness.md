# K-FNSPID 도입 전후와 연구 준비도

## 판정

- 데이터셋·시스템 논문의 기반은 갖췄지만 현재 상태 그대로는 논문 제출 준비 완료가 아니다.
- K-FNSPID는 한국 시장용 대규모 뉴스·공시–시세 결합 데이터와 재현 파이프라인이라는 연구 가치가 있다.
- 시장영향 모델은 TF-IDF 기준선보다 좋아졌지만 macro F1 개선폭이 `+0.0051`이고 기존 중요도 Gold 정확도는 개선되지 않았다.
- 감성 모델은 공개 균형 Test에서 크게 개선됐지만 기존 운영형 평가셋에서 회귀했다. 따라서 현재 증거로 전 분포 SOTA를 주장할 수 없다.

## 비교 기준

- 도입 전: K-FNSPID 최초 병합 전 `main` commit `076e97f8`, `reports/ml-model-evaluation.json`
- 현재: `reports/ml-model-evaluation.json`, `reports/korean-finance-sentiment-benchmark.json`, `reports/k-fnspid-transformer-training-report.json`
- 비교 원칙: 동일 평가셋의 동일 지표만 전후 비교한다. 공개 Test와 운영 Gold는 분포와 표본이 다르므로 하나의 개선율로 합치지 않는다.

## 데이터와 로직 변화

| 영역 | 도입 전 | 현재 |
| --- | --- | --- |
| 데이터 | 소규모 supervised·pseudo label과 뉴스 80건·공시 30건 Gold | K-FNSPID 문서 550,662건, 문서–종목 관계 814,205건, 시장영향 397,863건, 비혼입 시장영향 130,311건 추가 |
| 시세 | 뉴스 분류 학습에 미사용 | 파일 기반 일별 시세 10,691,998행·2,800종목, 2000-01-04~2026-07-13 |
| 감성 | TF-IDF Logistic Regression + 규칙 | KF-DeBERTa LoRA 80% + 기존 모델 20% 확률 앙상블, 독립 gate 실패 시 기존 모델 fallback |
| 중요도 | 텍스트 의미·출처·규칙만 사용 | 기존 판정 뒤에 K-FNSPID 시장영향 확률을 제한적으로 결합 |
| 라벨 | 사람이 정의한 감성·중요도 | 감성은 공개·운영 라벨, 시장영향은 1·3·5일 초과수익·거래량·변동성으로 생성한 약한 순서형 라벨 |
| 시간 누수 | 텍스트 holdout 중심 | 거래 세션별 유효일, 시간순 Train/Validation/Embargo/Test, 미래 시세는 라벨 생성에만 사용 |
| 사건 교란 | 별도 제어 없음 | 같은 종목·거래일 다중 사건 제외, cluster 대표 선택, 시장 평균 수익률 차감 |
| 배포 | 단일 joblib | 고정 base revision·LoRA `safetensors`·SHA-256·보고서 gate·fail-closed fallback |

## 동일 운영 평가 전후

| 평가셋 | 지표 | 도입 전 | 현재 | 변화 |
| --- | --- | ---: | ---: | ---: |
| Benchmark 768 | 감성 accuracy | 0.9688 | 0.9492 | -0.0195 |
| 실제 공시 Gold 30 | 감성 accuracy | 1.0000 | 1.0000 | 0.0000 |
| 실제 뉴스 Gold 80 | 감성 accuracy | 0.9750 | 0.9000 | -0.0750 |
| Stock review Gold 500 | 감성 accuracy | 0.9180 | 0.7880 | -0.1300 |
| Benchmark 768 | 중요도 accuracy | 0.9583 | 0.9583 | 0.0000 |
| 실제 공시 Gold 30 | 중요도 accuracy | 1.0000 | 1.0000 | 0.0000 |
| 실제 뉴스 Gold 80 | 중요도 accuracy | 0.9625 | 0.9625 | 0.0000 |
| Stock review Gold 500 | 중요도 accuracy | 0.8480 | 0.8480 | 0.0000 |

이벤트 모델은 변경하지 않아 event macro F1은 네 평가셋에서 동일하다. Stock review 종목 정확도는 `0.9940→0.9900`으로 `-0.0040` 하락했다.

## 새 평가에서 확인된 개선

### 한국 금융 감성

균형 공개 Test 933건에서 기존 Hannah TF-IDF macro F1은 `0.4423`, KR-FinBERT-SC는 `0.7272`, KF-DeBERTa LoRA 단독은 `0.8850`, 실제 서빙 80:20 앙상블은 `0.8840`이다. 이 결과는 공개 평가 분포에서 모델 표현력이 개선됐다는 증거지만 기존 운영형 회귀를 무효화하지 않는다.

### K-FNSPID 시장영향

| 모델 | Test 표본 | accuracy | macro F1 | quadratic kappa |
| --- | ---: | ---: | ---: | ---: |
| TF-IDF Logistic 기준선 | 10,728 | 0.4542 | 0.3613 | 0.3515 |
| KF-DeBERTa LoRA | 10,728 | 0.5006 | 0.3664 | 0.4186 |
| 변화 | - | +0.0463 | +0.0051 | +0.0671 |

순서형 일치도와 정확도는 개선됐지만 macro F1 개선은 작다. 동일 정의의 공개 한국 시장 leaderboard가 없어 이 수치만으로 SOTA를 선언하지 않는다.

## 논문으로 만들 수 있는 주장

- 한국 공개 뉴스·공시와 일별 시세를 연결한 55만 문서 규모의 파일 기반 재현 가능 데이터셋을 구축했다.
- 발표 시각과 거래 세션을 반영한 유효 거래일, 시간 embargo, 사건 cluster, 다중 사건 제외를 결합했다.
- 시장영향 Transformer가 같은 시간 외삽 Test에서 TF-IDF 기준선의 accuracy와 quadratic kappa를 개선했다.
- 공개 감성 Test와 실제 운영 Gold를 분리해 평가하면 분포별 성능 차이가 크게 나타난다.

현재 주장하면 안 되는 내용은 `한국 금융 뉴스 감성 전 분포 SOTA`, `K-FNSPID가 운영 중요도 정확도를 개선했다`, `가격 반응 중요도가 인과적 중요도다`, `이 모델이 수익성 있는 투자 신호다`이다.

## 논문 제출 전 필수 gate

1. 뉴스·공시를 시기·시장·업종·라벨별로 층화해 최소 500~1,000건의 완전 미사용 Gold를 만든다.
2. 금융 문맥을 이해하는 독립 평가자 2명 이상이 감성·의미 중요도·대상 종목을 라벨링하고, adjudication 전후 Cohen's kappa 또는 Krippendorff's alpha를 보고한다.
3. 모델별 3~5개 seed, bootstrap 95% 신뢰구간, paired bootstrap·McNemar 또는 permutation 검정으로 개선의 우연 가능성을 검증한다.
4. 월·분기 walk-forward, 상승·하락·고변동 국면, KOSPI·KOSDAQ·KONEX, 업종·시가총액별 OOD 결과와 calibration error를 보고한다.
5. 세션 정규화, 시장조정, 다중 사건 제외, cluster 대표화, LoRA, ordinal loss, 80:20 앙상블을 하나씩 제거하는 ablation을 수행한다.
6. TF-IDF, KR-FinBERT-SC, KF-DeBERTa base/LoRA/full fine-tune와 같은 강한 기준선을 같은 split·전처리·seed에서 비교한다.
7. 시장영향 라벨 threshold 민감도, 장중 데이터 부재, 생존자 편향, 종목 링커 오류, 거시·업종 교란을 정량화한다.
8. 모델 중요도를 의미 기반 중요도와 가격 반응 기반 materiality로 분리 평가하고, 최종 혼합이 운영 Gold에서 개선되는지 입증한다.
9. 데이터 원천·라이선스·재배포 범위·개인정보·삭제 요청·편향을 Datasheet/Data Statement 형식으로 기록한다.
10. GitHub Release에 더해 DOI가 부여되는 고정 저장소에 데이터·코드·환경·seed·artifact hash를 동결한다.

## 투고 현실성

- 현재: 내부 기술 보고서와 공개 데이터셋 release 수준이다.
- 위 gate 완료 후: 한국 금융 NLP 데이터셋·시스템 논문 또는 FinNLP 계열 workshop/resource track은 현실적이다.
- 강한 모델 논문이나 상위권 SOTA 주장은 운영 회귀 해소, 다중 평가자 Gold, 통계적 유의성, 강한 baseline·ablation이 선행돼야 한다.

## 연구 설계 참고

- [FNSPID](https://arxiv.org/abs/2402.06698): 뉴스와 시세를 장기간 연결한 원 데이터셋 설계 비교
- [KRX-Bench](https://aclanthology.org/2024.finnlp-1.2/): 한국 금융 벤치마크와 평가 harness 참고
- [Data Statements for NLP](https://aclanthology.org/Q18-1041/): 언어 데이터 구성·편향 문서화 기준
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010): 데이터셋 동기·구성·수집·유지보수 문서화 기준
- [Temporal Distribution Shifts in Financial Sentiment](https://aclanthology.org/2023.emnlp-main.65/): 금융 감성의 시간 분포 이동 평가 필요성
