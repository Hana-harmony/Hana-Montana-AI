# K-FNSPID v4 시장영향 모델

## 목적

한국 뉴스·공시와 파일 기반 일별 시세를 결합해 1·3·5거래일 가격반응을 재현한다. Hana Montana AI(KF-DeBERTa + K-FNSPID)는 의미 기반 공시 중요도와 사후 시장영향을 별도 신호로 제공하며, 시장영향을 인과 효과나 단독 투자 신호로 사용하지 않는다.

## 데이터셋

- 문서 1,247,685건: Naver 뉴스 524,696건, OpenDART 공시 722,989건
- 문서–종목 관계 1,136,118건
- 시장영향 715,015건, 다중 사건 교란을 제외한 대표 행 255,168건
- 일별 시세 10,691,998행, 2,800종목, `data/market/market_daily_price.parquet`
- 실제 전문 28,703건: 뉴스 19,727건, 공시 8,976건. K-FNSPID 문서에는 뉴스 13,310건과 공시 8,972건이 연결된다.
- 원천 JSONL shard와 Parquet 6개를 모두 Git 이력에 고정한다. 대용량 Parquet은 Git LFS pointer·객체 hash를 사용하고 manifest가 원본 byte·SHA-256을 독립적으로 검증한다. `k-fnspid-v4.0.0` Release는 복구용 미러로만 유지한다.
- 정본 manifest: `data/k_fnspid/v4/manifest.json`, SHA-256 `80b08190c538c1baeef418e4b50d5d9cb2ff9980ceb784a85b2988048ccc91c4`
- 운영 DB의 `market_daily_price`를 데이터셋 입력으로 연결하지 않는다. 복원 스크립트는 Release 자산의 크기와 SHA-256을 확인한 뒤 파일을 원자적으로 교체한다.

## 시간 정규화와 누수 방지

- 발표 시각의 UTC·KST와 `PRE_MARKET/REGULAR/AFTER_CLOSE/NON_TRADING` 세션을 보존한다.
- 장 시작 전·장중 문서는 당일, 장 마감 후·비거래일 문서는 다음 거래일을 유효일로 사용한다.
- 같은 종목·유효 거래일의 서로 다른 사건이 둘 이상이면 학습에서 제외한다.
- 같은 사건 cluster의 반복 문서는 정보량이 가장 큰 한 건만 대표로 사용한다.
- Train과 Validation/Test 경계에 7일 embargo를 두고, Test는 모델·보정·시드 선택에 사용하지 않는다.
- 대표 분할은 뉴스 Train 99,826 / Validation 6,391 / Test 9,560, 공시 Train 119,146 / Validation 584 / Test 4,615다.

## 라벨

- `abnormal_return_1d/3d/5d`: 종목 수정종가 수익률에서 같은 시장의 일별 평균 복리수익률을 차감한다.
- `abnormal_volume_z`: 이전 최대 60거래일 로그 거래량 기준 z-score다.
- `volatility_shock`: 당일 고저 범위를 이전 20거래일 평균과 비교한다.
- `materiality_score`: 1일 절대 초과수익 50%, 3일 20%, 거래량 15%, 변동성 15%를 결합한다.
- 등급은 `<0.20 LOW`, `<0.45 MEDIUM`, `<0.75 HIGH`, `>=0.75 CRITICAL`이다.
- 미래 시장값은 정답 생성에만 사용하고 텍스트 모델 입력에는 포함하지 않는다.

## 출처별 전문가

- 공통 구조: 고정 리비전 `kakaobank/kf-deberta-base` + LoRA r=16, class-balanced focal cross entropy, ordinal CDF loss
- 통합 NEWS+DISCLOSURE adapter를 seed 17·42·73으로 학습하고, 뉴스는 동결된 seed 42 통합 adapter를 평가한다. 공시는 같은 seed 42 adapter에서 출처별 추가학습한다.
- 뉴스와 공시의 문체·라벨 분포 차이를 고려해 평가 artifact, 기준선, 배포 gate, Validation 보정을 분리한다.
- Validation에서 log class-prior offset과 temperature를 공동 선택하고 Test에는 고정 적용한다.
- 런타임은 요청 `source_type`과 artifact의 `source_type`이 다르면 추론을 거부한다.
- 출처별 Transformer가 gate를 통과해야 활성화한다. 공시 TF-IDF 기준선은 독립 gate 미달이므로 Transformer 장애 시 부적격 기준선으로 후퇴하지 않고 시장영향 필드를 생략한다.

## 시간 외삽 Test

| 출처 | 모델 | 표본 | Accuracy | Macro-F1 | QWK | ECE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 뉴스 | TF-IDF 기준선 | 9,560 | 0.4715 | 0.3484 | 0.3421 | 0.0453 |
| 뉴스 | KF-DeBERTa 전문가 | 9,560 | 0.5247 | 0.3745 | 0.4754 | 0.0182 |
| 공시 | TF-IDF 기준선 | 4,615 | 0.3675 | 0.2677 | 0.1125 | 0.0444 |
| 공시 | KF-DeBERTa 전문가 | 4,615 | 0.4750 | 0.3216 | 0.1550 | 0.0441 |
| 통합 | TF-IDF 기준선 | 14,175 | 0.4377 | 0.3210 | 0.2552 | 0.0369 |
| 통합 | 출처별 KF-DeBERTa | 14,175 | 0.5085 | 0.3690 | 0.3975 | 0.0259 |

뉴스 전문가는 v4 Test 이전에 동결한 검증 adapter를 뉴스 전용으로 재평가했다. 공시 전문가는 동일 설정 seed 17/42/73 가운데 Test를 보지 않고 Validation Macro-F1로 seed 17을 선택했다. 공시 3-seed Test 평균±표본표준편차는 Accuracy `0.4534±0.0216`, Macro-F1 `0.3170±0.0052`, QWK `0.1556±0.0007`이다.

2,000회 거래일 cluster bootstrap의 Transformer−기준선 95% CI는 다음과 같다.

- 뉴스: Accuracy `[0.0427, 0.0637]`, Macro-F1 `[0.0120, 0.0409]`, QWK `[0.1090, 0.1558]`
- 공시: Accuracy `[0.0847, 0.1323]`, Macro-F1 `[0.0264, 0.0806]`, QWK `[0.0046, 0.0794]`
- 통합: Accuracy `[0.0594, 0.0818]`, Macro-F1 `[0.0351, 0.0608]`, QWK `[0.1178, 0.1649]`
- 통합 exact McNemar `p=2.29e-55`

## 배포 gate

- 뉴스: Test 5,000건 이상, Macro-F1 0.35 이상, QWK 0.30 이상, ECE 0.20 이하, 기준선 대비 Macro-F1·QWK·ECE 비회귀
- 공시: Test 500건 이상, Macro-F1 0.30 이상, QWK 0.08 이상, ECE 0.20 이하, 기준선 대비 Macro-F1·QWK·ECE 비회귀
- 논문 우월성: 10,000건 이상, 두 출처 모두 Macro-F1·QWK 비회귀, 거래일 cluster bootstrap의 Accuracy·Macro-F1·QWK 차이 95% CI가 모두 0 초과, exact McNemar `p<0.05`
- artifact 크기·SHA-256, manifest version, source type, report gate가 모두 맞을 때만 로더가 모델을 활성화한다.

## SOTA 비교 범위

- FNSPID는 미국 뉴스 1,570만건·시세 2,970만행·4,775종목 규모의 원 설계 참고 자료다. K-FNSPID v4는 한국 공개 뉴스·공시 124만건과 시세 1,069만행·2,800종목으로 규모는 작지만 한국 발표 세션, 공시, 종목 관계, embargo를 추가한다.
- FINKRX, FININ, KRX-Bench, CARAG, FinKario는 각각 한국 금융 instruction, information extraction, QA·RAG 등 과제가 달라 동일 라벨·동일 Test의 직접 순위 비교가 아니다.
- 동일한 한국 종목·시장영향 코드북의 공인 leaderboard가 없으므로 외부 전역 SOTA 초과를 주장하지 않는다. 사용자 지정에 따라 금융 특화 공개 encoder `KR-FinBERT-SC`만 이름이 명시된 강한 비교군으로 사용하고 `KLUE RoBERTa-large`는 제외했다.
- KR-FinBERT-SC도 Hana 모델과 동일하게 공유 3-seed 학습, 공유 seed 42 재사용, 국내 뉴스 동결평가, 국내 공시 추가학습 순서를 따랐다. 데이터 manifest, 모델 revision, recipe, artifact와 예측 파일의 byte·SHA-256이 모두 일치하는 경우만 재사용했다.
- 비교 계약과 수정 계약을 학습·평가 전에 잠갔으며, 국내 뉴스·국내 공시별 Macro-F1과 QWK 거래일 군집 bootstrap 2,000회와 exact McNemar p값 Holm 보정을 적용했다.

| 동일 K-FNSPID 시간 Test 비교군 | 국내 뉴스 Macro-F1 | 국내 공시 Macro-F1 | 판정 |
| --- | ---: | ---: | --- |
| Hana Montana AI(KF-DeBERTa + K-FNSPID) | 0.3745 | 0.3216 | 고정 후보 |
| KR-FinBERT-SC 동일 파이프라인 | 0.3506 | 0.3131 | 강한 비교군 |
| 상대 차이 | +6.82% (+0.0239점) | +2.72% (+0.0085점) | 뉴스 우위·공시 미확정 |

국내 뉴스는 Macro-F1 군집 95% 신뢰구간 `[0.0090, 0.0383]`과 QWK 비열등 조건을 모두 통과했다. 국내 공시는 Macro-F1 구간 `[-0.0126, 0.0317]`이 0을 포함하고 QWK가 0.1611에서 0.1550으로 낮아 우위를 확정하지 않는다. TF-IDF는 재현 가능한 전통 기준선이며 SOTA 모델로 호칭하지 않는다.

## 산출물

- 데이터셋: `data/k_fnspid/v4/manifest.json`, `k-fnspid-v4.0.0` Release
- 기준선: `k_fnspid_impact_news_ml.joblib`, `k_fnspid_impact_disclosure_ml.joblib`
- Transformer: `k_fnspid_impact_news_transformer/`, `k_fnspid_impact_disclosure_transformer/`
- 학습 보고서: `reports/k-fnspid-impact-{news,disclosure}-transformer-training-report.json`
- 통계 보고서: `reports/k-fnspid-research-evaluation.json`
- 공개 강한 비교군 계약·결과: `reports/k-fnspid-impact-strong-baseline-study-contract.json`, `reports/k-fnspid-impact-strong-baseline-study-contract-amendment-002.json`, `reports/k-fnspid-impact-kr-finbert-sc-matrix.json`, `reports/k-fnspid-impact-kr-finbert-sc-result-attestation.json`
- Datasheet와 코드북: `docs/datasets/k-fnspid-v4-datasheet.md`, `docs/datasets/k-fnspid-v4-annotation-codebook.md`

## 한계

- 일봉으로 정답을 생성하므로 장중 즉시 반응과 미관측 거시·업종 사건을 완전히 분리하지 못한다.
- 공시 전문 연결은 8,972건으로 전체 공시보다 적다. DART 문서 API 제한과 공개 viewer 차단 시 재시도 폭주를 막아 수집을 중단했으며, 제목·요약 ablation이 시장영향에서는 전문보다 강했던 기존 결과도 함께 공개한다.
- 현재 Gold 검수는 Codex 기반 일관성·근거 검수다. 독립 다중 평가자 합의도는 확보하지 못했으므로 사람 평가자 기반 Gold로 표현하지 않는다.
- 모델은 가격반응의 확률적 보조 신호이며 투자 권유·인과 추론에 사용하지 않는다.
