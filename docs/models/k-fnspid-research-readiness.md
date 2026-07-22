# K-FNSPID 도입 전후와 연구 준비도

## 판정

K-FNSPID v4 시장영향은 고정 데이터, 시간 외삽 Test, 출처별 기준선, calibration, paired 통계 검정, ablation, Datasheet, 코드북과 재현 가능한 artifact를 갖췄다. 감성 v6도 receipt 미보유 라벨을 승격 근거에서 제외하고 2,689건의 receipt-bound 개발·학습 Gold, 1,118,291문서 K-FNSPID DAPT, 출처 계층형 분류 head, 사전 고정 3-seed·공정 기준선·no-K ablation과 확증 1,200건 one-shot 평가를 완료했다.

동일 한국 시장영향·target-aware 뉴스/공시 감성 코드북의 외부 leaderboard가 없고 Gold 검수 주체가 인간 금융전문가가 아니므로 외부 SOTA 초과나 인간 전문가 수준을 주장할 수 없다. 시장영향은 동일 시간 Test의 KR-FinBERT-SC 대비 국내 뉴스 우위만 주장하며 국내 공시 우위는 주장하지 않는다. 감성 v6는 확증 gate를 통과하지 못해 `KEEP_CURRENT_MODEL`로 판정했으며 개선·통계적 우월성·배포 승격을 주장하지 않는다.

### 2026-07-15 시장영향 v4 판정

K-FNSPID v4는 학회 제출본에 필요한 고정 데이터, 시간 외삽 Test, 출처별 강한 기준선, 공시 3개 시드, calibration, paired 통계 검정, ablation, Datasheet, 코드북과 재현 가능한 artifact를 갖췄다. 뉴스와 공시를 하나의 시장영향 모델로 합쳤던 v3의 공시 회귀를 v4 출처별 전문가가 제거했다.

다만 동일 한국 시장영향 코드북의 외부 leaderboard가 없고 Gold가 독립 금융전문가 다중 주석이 아니므로 외부 SOTA 초과나 인간 전문가 수준을 주장할 수 없다. 감성 공개 Test도 과거 반복 사용됐다. 논문에서 허용되는 주장은 시장영향의 동일 시간 Test 기준선 우위와 감성의 동일 공개셋 재현 우위까지다.

## 데이터와 로직 변화

| 영역 | K-FNSPID 도입 전 | v3 공유 모델 | v4 출처별 전문가 |
| --- | --- | --- | --- |
| 문서 | 소규모 supervised·pseudo label | 뉴스·공시 550,662건 | 뉴스 524,696건·공시 722,989건, 총 1,247,685건 |
| 시세 | 시장영향 학습에 미사용 | 파일 기반 10,691,998행 | 같은 파일 정본 유지, 운영 DB 연결 없음 |
| 시장영향 | 없음 | 공유 TF-IDF·KF-DeBERTa, 출처 prefix만 사용 | 뉴스·공시 기준선·Transformer·보정·gate·artifact 완전 분리 |
| 공시 Test | 없음 | 590건, Transformer macro F1 0.2211로 기준선 0.3006보다 낮음 | 4,615건, 전문가 0.3216으로 기준선 0.2677보다 높음 |
| 라우팅 | 없음 | 하나의 artifact | 요청 `source_type`과 artifact 출처가 다르면 추론 거부 |
| 장애 처리 | 없음 | 공유 기준선 fallback | 같은 출처의 적격 기준선만 fallback. 공시 기준선은 gate 미달이라 시장영향만 생략 |
| 누수 통제 | 텍스트 holdout 중심 | 시간 split·embargo·사건 cluster | 같은 통제 유지, 출처별 분할 수와 report를 manifest에 고정 |
| 보정 | 없음 | Validation log-prior | Validation log-prior + temperature를 출처별 선택 |

## 고정 Test 결과

| 출처 | 모델 | 표본 | Accuracy | Macro-F1 | QWK | ECE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 뉴스 | TF-IDF | 9,560 | 0.4715 | 0.3484 | 0.3421 | 0.0453 |
| 뉴스 | KF-DeBERTa | 9,560 | 0.5247 | 0.3745 | 0.4754 | 0.0182 |
| 공시 | TF-IDF | 4,615 | 0.3675 | 0.2677 | 0.1125 | 0.0444 |
| 공시 | KF-DeBERTa seed 17 | 4,615 | 0.4750 | 0.3216 | 0.1550 | 0.0441 |
| 통합 | TF-IDF | 14,175 | 0.4377 | 0.3210 | 0.2552 | 0.0369 |
| 통합 | 출처별 KF-DeBERTa | 14,175 | 0.5085 | 0.3690 | 0.3975 | 0.0259 |

공시 동일 설정 seed 17/42/73의 Test 평균±표본표준편차는 Accuracy `0.4534±0.0216`, Macro-F1 `0.3170±0.0052`, QWK `0.1556±0.0007`이다. Test를 보지 않고 Validation Macro-F1이 가장 높은 seed 17을 선택했다. seed 42는 ECE 비회귀 gate를 통과하지 못했고 선택되지 않았다.

2,000회 거래일 cluster bootstrap에서 Transformer−기준선 차이 95% CI는 다음과 같다.

- 뉴스: Accuracy `[0.0427, 0.0637]`, Macro-F1 `[0.0120, 0.0409]`, QWK `[0.1090, 0.1558]`
- 공시: Accuracy `[0.0847, 0.1323]`, Macro-F1 `[0.0264, 0.0806]`, QWK `[0.0046, 0.0794]`
- 통합: Accuracy `[0.0594, 0.0818]`, Macro-F1 `[0.0351, 0.0608]`, QWK `[0.1178, 0.1649]`
- exact McNemar `p=2.29e-55`

## 의미 중요도와 감성

### 현재 감성 v6

- 새 학습 Gold는 주 뉴스 596건, 보조 뉴스 598건, 보조 공시 600건이다. 개발 Gold는 뉴스 448건과 공시 447건으로 CHECKPOINT 911·CALIBRATION 455·SELECTION 461건과 논리 중복이 없다.
- DAPT는 확증·Gold 보호 연결요소를 제외한 1,118,291문서·62,468,526 토큰을 사용했다. 전체 3,908 update의 validation NLL은 `3.119393→1.335785`이며 최종 manifest SHA-256은 `50155de7…ef2a`다.
- v6 확증 층화가중 Accuracy/Macro-F1은 NEWS 0.7503/0.5530, DISCLOSURE 0.8646/0.6024다. 배포 판정은 `KEEP_CURRENT_MODEL`이다.

### 과거 회귀 진단과 현재 중요도

- 정규화 중복·충돌 제거 감성 공개 Test 932건: 잠근 KF-DeBERTa LoRA Macro-F1 0.8849, 80:20 앙상블 0.8838, KR-FinBERT-SC 0.7266, Hana TF-IDF 0.4415
- 동일 932개 문서의 LoRA−KR-FinBERT-SC paired bootstrap Macro-F1 차이 0.1580, 95% CI `[0.1265, 0.1899]`, exact McNemar `p=9.81e-19`
- 실제 뉴스 Gold: Accuracy 0.8625 / Macro-F1 0.8308
- 공시 감성 Gold 600건: Accuracy 0.9150 / Macro-F1 0.8084
- 뉴스 Accuracy 0.90 gate 미달로 감성 신규 후보는 미승격하고 기존 모델로 fail closed
- 공시 의미 중요도 모델 단독 Gold 600건: Accuracy 0.9850 / Macro-F1 0.9470
- 존속위험 정책 포함 운영 Gold 910건: Accuracy 0.9989 / Macro-F1 0.9962

시장영향은 의미 중요도 라벨과 confidence를 수정하지 않는다. 운영 API는 `importance`와 `marketImpactImportance/Score/Confidence`를 별도 필드로 보존한다.

## SOTA 비교

- FNSPID는 미국 뉴스 15.7M건·시세 29.7M행·4,775종목으로 K-FNSPID보다 크다. K-FNSPID는 한국 공시, 거래 세션, 종목 alias, 사건 교란과 embargo를 추가한다.
- FINKRX, FININ, KRX-Bench, CARAG, FinKario는 QA, instruction, information extraction 또는 RAG 과제라 시장영향 4등급과 직접 점수 비교할 수 없다.
- KF-DeBERTa 금융 감성의 동일 공개 Test 대응비교는 유효하지만 해당 Test를 과거 후보 선택과 개발 중 반복 조회해 새 독립 확증 결과로 볼 수 없다. 시장영향에는 동일 라벨·동일 기간의 공인 외부 모델도 없다.
- 따라서 `동일 공개셋의 고정 예측에서 KR-FinBERT-SC보다 0.1583 높은 재현 결과`는 타당하지만, `통계적으로 유의하게 우월`, `독립 검증된 SOTA` 또는 `외부 SOTA보다 높다`는 표현은 부정확하다. 과거 적응적 Test 사용 때문에 bootstrap 구간과 McNemar p값의 명목 오류율이 보장되지 않는다.

## 연구 gate

| gate | 상태 | 근거 |
| --- | --- | --- |
| 감성 receipt-bound Gold | 완료 | 학습 1,794건·개발 895건, 미해결 11건 제외, partition overlap 0 |
| 감성 DAPT | 완료 | 1,118,291문서·62,468,526 토큰, FP32 3,908 update |
| 감성 3-seed·공정 기준선·ablation | 완료 | 후보 seed 42, 공정 기준선과 no-K 잠금 artifact 검증 |
| 감성 one-shot 확증 | 완료·미승격 | NEWS·DISCLOSURE 각 600건, `KEEP_CURRENT_MODEL` |
| 대규모 공개 원천 | 완료 | 1,247,685문서·10,691,998 시세행 |
| 시간 외삽·embargo | 완료 | 2026-04 이후 Test, 경계 7일 제외 |
| 출처별 강한 기준선 | 완료 | 뉴스·공시 Train-only TF-IDF |
| 출처별 비회귀 | 완료 | 뉴스·공시 Macro-F1·QWK 모두 개선 |
| 공시 반복 시드 | 완료 | seed 17/42/73, Validation 선택 |
| 통계 검정 | 완료 | 2,000회 행·거래일 bootstrap, exact McNemar |
| 감성 후보 선택 누수 차단 | 완료 | Validation Calibration/Selection 분리, Test·Gold 선택 금지 |
| 감성 확증 평가 | 완료 | one-shot report SHA-256 `be5c9edd…b149` |
| calibration | 완료 | ECE·Brier, Validation temperature |
| artifact 무결성 | 완료 | safetensors, 크기·SHA-256, source metadata |
| Datasheet·코드북 | 완료 | v4 문서와 release manifest |
| 독립 전문가 다중 주석 | 한계 | Codex 코드북 검수이며 인간 합의도 없음 |
| 외부 동일 과제 leaderboard | 없음 | 외부 SOTA 직접 주장 금지 |
| DOI 익명 보관 | 외부 절차 | GitHub Release는 본 작업에서 고정 |

## 제출물

- 익명 ACL Rolling Review 원고: `docs/paper/acl/k-fnspid-v4-arr-review.tex`
- 저자 공개 영문본: `docs/paper/acl/k-fnspid-v4-author-preprint.tex`
- 최성현 저자 한글본: `docs/paper/acl/k-fnspid-v4-ko.tex`
- 저자: Sunghyun Choi / 최성현, 한국공학대학교 SW대학 컴퓨터공학부 소프트웨어전공 4학년 학부생
- 통계 정본: `reports/k-fnspid-research-evaluation.json`
- 공시 다중 시드 정본: `reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json`

## 남은 과학적 한계

- 공시 QWK 개선 CI 하한이 0.0046으로 작아 다른 시장 국면·기간 재현이 필요하다.
- 일봉 라벨은 장중 반응과 미관측 거시·업종 사건을 분리하지 못한다.
- 실제 전문 연결은 공시 8,972건으로 전체 공시의 1.24%다. DART 제한을 우회하지 않았고 전문 미수집 편향을 공개한다.
- Gold는 Codex 단일 코드북 검수다. 독립 금융전문가 주석으로 표현하거나 인간 수준을 주장하지 않는다.
- 모델은 투자 권유, 수익 보장, 자동 주문 또는 인과적 중요도 판정에 사용하지 않는다.
