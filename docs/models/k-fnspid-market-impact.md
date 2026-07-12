# K-FNSPID 시장영향 모델

## 목적

한국 뉴스·공시와 파일 기반 일별 시세를 결합해 1·3·5거래일 시장 반응을 재현하고, 텍스트 중요도 분류의 보조 신호를 제공한다.

## 데이터셋

- 버전: `k-fnspid-v1`
- 문서: 81,689건
- 문서–종목 관계: 124,491건
- 시장영향 행: 50,972건
- 일별 시세: 1,239,658행, KOSPI 948종목, 2021-01-04~2026-07-10
- Gold: Codex가 원문 제목과 대상 종목 관점으로 검수한 실제 뉴스 80건
- 저장: `data/k_fnspid/v1/*.parquet`, Zstandard 압축
- 원천·정규화 파일은 DB와 독립적으로 생성하며 `manifest.json`에 파일 해시를 남긴다.

## 라벨

- `abnormal_return_1d/3d/5d`: 종목 수정종가 수익률에서 동일 시장 일별 평균 수익률을 차감한다.
- `abnormal_volume_z`: 뉴스 이전 최대 60거래일 로그 거래량 기준 z-score다.
- `volatility_shock`: 당일 고저 범위를 이전 20거래일 평균과 비교한다.
- `materiality_score`: 수익률, 거래량, 변동성 신호를 결합한 0~1 점수다.
- 미래 시장값은 정답 생성에만 사용하며 모델 입력에는 포함하지 않는다.

## 시간 분할

- Train: 2025-12-24 이전
- Embargo: 각 경계 전 7일
- Validation: 2026-01-01~2026-05-24
- Test: 2026-06-01 이후
- 최종 모델은 설정 선택이 끝난 뒤 Train+Validation으로 다시 적합하고 Test는 한 번만 평가한다.

## 모델과 평가

- Artifact: `src/hannah_montana_ai/model_store/k_fnspid_impact_ml.joblib`
- 모델: TF-IDF char n-gram + class-balanced One-vs-Rest Logistic Regression
- Test: accuracy 0.4307, macro F1 0.3014, quadratic kappa 0.2144
- 품질 gate: Test 1,000건 이상, macro F1 0.30 이상, quadratic kappa 0.20 이상
- gate를 통과한 모델만 기존 의미 기반 중요도와 결합한다. 두 모델이 불일치하면 confidence를 낮추고, 시장 모델이 높은 confidence로 더 높은 중요도를 예측할 때도 한 단계만 올린다.

## SOTA 비교

- 대상별 한국 금융 감성은 독립 Gold에서 Hannah 모델과 `snunlp/KR-FinBERT-SC`를 비교한다.
- 학습 Gold와 URL이 겹치는 20건은 평가에서 제외한다.
- 실제 중복 URL 20건을 제외한 독립 Gold 60건에서 Hannah accuracy 0.9333, macro F1 0.9093이고 KR-FinBERT-SC는 accuracy 0.7000, macro F1 0.6493이다.
- 결과는 `reports/financial-alert-sota-benchmark.json`에 저장한다.
- 시장 중요도에는 공인 공개 leaderboard가 없으므로, 시간 외삽 Test와 다수 클래스 macro F1·quadratic kappa를 승격 기준으로 사용한다.

## 한계

- 장중 분봉이 아닌 일봉이므로 즉시 반응과 장중 교란을 분리하지 못한다.
- 현재 장기 시세는 KOSPI 중심이어서 KOSDAQ 시장영향 coverage가 낮다.
- 텍스트만으로 미래 가격 충격을 맞히는 문제는 불확실성이 크므로 시장영향 모델을 단독 투자 신호로 사용하지 않는다.
