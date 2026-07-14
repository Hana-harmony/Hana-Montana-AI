# K-FNSPID 시장영향 모델

## 목적

한국 뉴스·공시와 파일 기반 일별 시세를 결합해 1·3·5거래일 시장 반응을 재현하고, 텍스트 중요도 분류의 보조 신호를 제공한다.

## K-FNSPID v3 데이터셋

- 원천: Naver News Search 524,696건, OpenDART 25,966건
- 문서: 550,662건, 2000-02-03~2026-07-13
- 문서–종목 관계: 819,772건, 대표 종목 2,720개
- 시장영향 행: 398,942건
- 비혼입 시장영향: 130,566건
- 시세: 10,691,998행, 2,800종목, 2000-01-04~2026-07-13
- 시장별 종목: KOSPI 948, KOSDAQ 1,752, KONEX 100
- 공시 실제 원문: 8,972건, 공시 25,966건의 34.5529%
- Gold: Codex가 원문 제목·대상 종목·라벨 근거를 검수한 실제 뉴스 80건 + 공시 600건
- 저장: `data/k_fnspid/v3/*.parquet`, Zstandard 압축
- 시세 정본: `data/market/market_daily_price.parquet`, 236,508,054 bytes
- 원천·정규화 파일은 DB와 독립적으로 생성하며 manifest에 크기·SHA-256·고정 원천 리비전을 남긴다.

48MB 이하 JSONL shard는 Git에 포함하고, GitHub 단일 파일 제한을 넘는 Parquet은 실제 파일 6개와 동일 manifest를 K-FNSPID v3.0.0 Release 자산으로 게시한다. `restore_k_fnspid_release.py`가 6개 자산의 크기·SHA-256을 확인한 뒤 `prices_daily.parquet`을 파일 기반 시세 정본 경로에 원자적으로 복원하며, 로컬 학습·Docker 검증은 이 스냅샷만 사용한다.

## 시간 정규화·누수 방지

- 발표 시각은 UTC·KST를 모두 보존하고 `PRE_MARKET/REGULAR/AFTER_CLOSE/NON_TRADING` 세션을 기록한다.
- 장 시작 전·장중 뉴스는 당일, 장 마감 후·비거래일 뉴스는 다음 거래일을 유효일로 사용한다.
- 시세 시작일보다 이른 기사를 첫 거래일에 연결하지 않고 제외한다.
- 사건 cluster key에 유효 거래일을 포함해 다른 날의 반복 제목이 같은 cluster로 합쳐지지 않게 한다.
- 같은 종목·거래일에 서로 다른 사건 cluster가 두 개 이상이면 시장영향 학습에서 제외한다.
- 같은 cluster·종목·거래일의 중복 기사는 정보가 가장 많은 한 건만 대표 학습행으로 사용한다.

## 라벨

- `abnormal_return_1d/3d/5d`: 종목 수정종가 수익률에서 같은 시장의 일별 평균 복리수익률을 차감한다. 1일 반응은 유효일 전일 종가→유효일 종가다.
- `abnormal_volume_z`: 뉴스 이전 최대 60거래일 로그 거래량 기준 z-score다.
- `volatility_shock`: 당일 고저 범위를 이전 20거래일 평균과 비교한다.
- `materiality_score`: 1일 절대 초과수익 50%, 3일 20%, 거래량 15%, 변동성 15%를 결합한 0~1 점수다.
- 중요도: `<0.20 LOW`, `<0.45 MEDIUM`, `<0.75 HIGH`, `>=0.75 CRITICAL`.
- 미래 시장값은 정답 생성에만 사용하고 모델 입력에는 포함하지 않는다.

## 시간 분할

- Train: 2025-12-24 이전
- Embargo: 2026-01-01·2026-04-01 경계 전 7일
- Validation: 2026-01-01~2026-03-24
- Test: 2026-04-01 이후
- 비혼입 대표 학습행: Train 107,175 / Validation 6,975 / Test 10,750
- 시간순 Test는 설정 선택에 사용하지 않고 마지막에 한 번 평가한다.

## 모델·배포 gate

- 기준선: TF-IDF char 2~5-gram + class-balanced One-vs-Rest Logistic Regression
- 기준선 Test: Train 전용 모델로 평가한 10,750건, accuracy 0.4643, macro F1 0.3429, quadratic kappa 0.3141
- 제목+snippet만 사용한 TF-IDF ablation은 Test macro F1 0.3505 / quadratic kappa 0.3271로 전문 입력보다 높았다. 공시 전문 확대 자체를 시장영향 성능 개선으로 해석하지 않는다.
- Transformer 후보: `kakaobank/kf-deberta-base` 고정 리비전 + LoRA r=16, class-balanced focal cross entropy + ordinal CDF loss
- Transformer 후처리: Validation에서만 선택한 log class-prior offset을 raw logits에 적용하고 raw·보정 지표와 설정을 report에 함께 보존
<!-- K_FNSPID_FINAL_TRANSFORMER_RESULT -->
- seed 17/42/73의 Test 평균±표본표준편차는 accuracy 0.5105±0.0080, macro F1 0.3824±0.0102, quadratic kappa 0.4675±0.0042다.
- Validation macro F1로 선택한 seed 73은 Test 10,750건에서 accuracy 0.5095, macro F1 0.3820, quadratic kappa 0.4694를 기록했다. raw logits는 0.4842 / 0.3794 / 0.4468이고 Validation 선택 prior 강도는 0.15다.
- 기준선 대비 거래일 cluster bootstrap 2,000회 차이 95% CI는 accuracy [0.0351, 0.0557], macro F1 [0.0256, 0.0536], quadratic kappa [0.1331, 0.1776]이며 exact McNemar p=1.70e-20이다.
- 전체 Brier score는 0.6450→0.6129로 개선됐지만 ECE는 0.0491→0.0662로 악화됐다. 뉴스 10,160건은 macro F1 0.3436→0.3847, 공시 590건은 0.3006→0.2211이므로 공시 가격반응은 후속 외삽 검증 대상이다.
- Transformer 배포 조건: Test 1,000건 이상, macro F1 0.35 이상, quadratic kappa 0.20 이상, 그리고 두 지표 모두 기준선 이상
- 논문 우월성 조건: 2,000회 거래일 cluster bootstrap에서 accuracy·macro F1·quadratic kappa 차이 95% 구간이 모두 0 초과이고 exact McNemar p<0.05
- 보고서·artifact 크기·SHA-256가 모두 맞을 때만 로더가 Transformer를 활성화한다. 실패 시 기준선으로 fail closed한다.
- seed 17/42/73을 같은 설정으로 반복하고 Validation에서 보정 강도와 배포 run을 선택한다. Test는 paired bootstrap·exact McNemar·ECE·Brier 평가에만 사용한다.
- 두 시장영향 모델 모두 의미 기반 중요도를 대체하지 않고 보조 신호로만 사용한다.

## SOTA 비교

- 원 설계 비교: [FNSPID 논문](https://arxiv.org/abs/2402.06698)의 뉴스–시세 시계열 결합 구조를 한국 시장 발표 세션·종목 관계·embargo에 맞게 재설계했다.
- 절대 규모는 원 FNSPID의 뉴스 1,570만·시세 2,970만·4,775종목보다 작다. K-FNSPID v3는 한국 공개 원천으로 재현한 뉴스·공시 55만·시세 1,069만·2,800종목 규모이며, 50만 문서·300만 시세·2,000종목 내부 대규모 gate를 통과했다.
- 베이스 모델: [KF-DeBERTa 공식 모델 card](https://huggingface.co/kakaobank/kf-deberta-base)의 금융 도메인 사전학습 모델과 고정 commit `363b171d...`를 사용한다.
- 한국 금융 벤치마크 설계 참고: [KRX-Bench, FinNLP 2024](https://aclanthology.org/2024.finnlp-1.2/).
- 한국 금융 감성은 균형 공개 Test 933건에서 KF-DeBERTa LoRA 앙상블 macro F1 0.8840, KF-DeBERTa 단독 0.8850, `snunlp/KR-FinBERT-SC` 0.7272, 기존 Hana TF-IDF 0.4423이다. 운영 Gold는 뉴스 accuracy 0.9000 / macro F1 0.8642, 공시 accuracy 0.9233 / macro F1 0.8344로 별도 gate를 통과한다.
- 시장영향 중요도에는 동일한 한국 종목·라벨 정의의 공인 leaderboard가 없다. 따라서 시간 외삽 Test의 macro F1·quadratic kappa와 강한 텍스트 기준선을 배포 비교로 사용한다.
- KF-DeBERTa 원 모델 card의 FN-Sentiment 성능은 외부 참고치이며, K-FNSPID 테스트 결과로 재주장하지 않는다.

## 산출물

- 공개 데이터셋: `k-fnspid-v3.0.0` Release
- 데이터 manifest: `data/k_fnspid/v3/manifest.json`
- Datasheet: `docs/datasets/k-fnspid-v3-datasheet.md`
- 시세 manifest: `data/market/manifest.json`
- 기준선 artifact: `src/hannah_montana_ai/model_store/k_fnspid_impact_ml.joblib`
- 기준선 report: `reports/k-fnspid-impact-training-report.json`
- Transformer artifact: `src/hannah_montana_ai/model_store/k_fnspid_impact_transformer/`
- Transformer report: `reports/k-fnspid-transformer-training-report.json`
- 감성 SOTA 비교: `reports/korean-finance-sentiment-benchmark.json`

## 한계

- 장중 분봉이 아닌 일봉이므로 즉시 반응과 장중 교란을 분리하지 못한다.
- 시세가 있는 2,800종목 중 문서 대표 종목으로 연결된 종목은 2,720개다.
- 동일 종목·날짜의 다중 사건을 제외해 교란을 줄였지만, 거시경제·업종·미관측 사건의 영향은 완전히 제거할 수 없다.
- 텍스트만으로 미래 가격 충격을 맞히는 문제는 불확실성이 크므로 단독 투자 신호로 사용하지 않는다.
- 기존 4개 legacy 운영 평가셋의 중요도 정확도는 도입 전후 동일하다. 별도로 구축한 v3 코드북 비중복 공시 Gold 910건에서는 기존 분석기 accuracy 0.9055 / macro F1 0.8206에서 후보 운영 파이프라인 0.9989 / 0.9962로 개선됐다. 평가 정의가 다르므로 두 결과를 합쳐 하나의 전 분포 개선율로 주장하지 않는다.
- 반복 seed·신뢰구간·통계 검정은 v3 연구 harness로 수행한다. 독립 인간 다중 평가자 Gold와 기간·시장 국면별 추가 외삽은 여전히 남아 있으며 상세 판정은 [도입 전후·연구 준비도](k-fnspid-research-readiness.md)에 고정한다.
