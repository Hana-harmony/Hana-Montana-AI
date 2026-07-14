# Hana Montana AI(KF-DeBERTa + K-FNSPID) 모델 감사

## 결론
- 리포트: `reports/hannah-ai-model-audit-report.json`
- 감사 상태: `pass`
- 감사 대상: 뉴스·공시 분석, 종목 링커, 외국인 보유수량 예측, 글로벌 피어 매칭
- 모든 serving 핵심 기능은 실제 ML artifact를 사용한다. 글로벌 피어 confidence는 국내 동일업종 feature 보강 후 monitoring gate를 통과한다.

| 기능 | 모델 | 최신 성능 | 상태 |
| --- | --- | --- | --- |
| 뉴스·공시 이벤트 | TF-IDF + supervised LogisticRegression | benchmark event macro F1 0.9844, real news event macro F1 0.9221 | pass |
| 한국 금융 감성 | KF-DeBERTa LoRA + TF-IDF 확률 앙상블 | 공개 Test 933건 macro F1 0.8840, 실제 뉴스 Gold accuracy 0.9000 | pass |
| 공시 의미 중요도 | Validation 선택 제목+요약 TF-IDF Logistic Regression + 존속위험 floor | 모델 단독 기본 Gold 0.9850 / 0.9470, 운영 전체 910건 accuracy 0.9989 / macro F1 0.9962 | pass |
| K-FNSPID 시장영향 | v3 문서 550,662건·시세 10,691,998행 + KF-DeBERTa LoRA | seed 73, Test accuracy 0.5095 / macro F1 0.3820 / QWK 0.4694 | pass |
| 종목 링커 | TF-IDF nearest-neighbor entity linker | 전체 종목코드 template accuracy 1.0, 종목명 template accuracy 0.9921 | pass |
| 외국인 보유수량 예측 | stock-routed panel time-series ML ensemble | MAE 51,539.19, RMSE 147,477.74, MAPE 0.044908, persistence 대비 MAPE 4.4167% 개선 | promoted |
| 글로벌 피어 매칭 | Business profile ML classifier + TF-IDF + SVD semantic + 재무·업종·인지도 동적 유사도 | KIS 활성 일반주식 2,752/2,752 추론 성공, 종목별 정답·anchor 없음, LOW confidence 0.5451% | pass |

## SOTA/Baseline 비교
- 외국인 보유수량 예측은 같은 제한 종목 universe와 같은 walk-forward sample에서 persistence baseline, N-HiTS, PatchTST와 비교한다.
- 현재 모델 MAPE 0.044908은 persistence 0.046983, N-HiTS 0.046955, PatchTST 0.049739보다 낮다.
- 글로벌 피어 매칭은 공개 표준 SOTA leaderboard가 없어 KIS 활성 universe 전체 coverage와 도메인·표시 계약 gate를 운영 기준으로 둔다.
- 공개 금융 감성 균형 Test 933건에서 KF-DeBERTa LoRA 앙상블 macro F1 0.8840, KF-DeBERTa 단독 0.8850, KR-FinBERT-SC 0.7272, 기존 Hana TF-IDF 0.4423이다. 실제 공시 Gold accuracy 0.9233과 실제 뉴스 Gold accuracy 0.9000도 동일 보고서의 배포 gate에 고정한다.
- K-FNSPID v3 시간 외삽 Test의 TF-IDF 기준선은 accuracy 0.4643, macro F1 0.3429, quadratic kappa 0.3141이고 선택 seed 73은 0.5095 / 0.3820 / 0.4694다. 거래일 cluster 95% CI가 세 차이 모두 0을 넘고 McNemar p=1.70e-20이어서 승격했다.
- 시장영향은 같은 라벨 정의의 공개 SOTA leaderboard가 없어 2026년 4월 이후 시간 외삽 Test 10,750건의 macro F1·quadratic kappa, 보정 지표와 TF-IDF 기준선 대비 paired 검정을 함께 통과할 때만 Transformer를 승격한다.

## K-FNSPID 도입 전후 감사

| 평가셋 | 지표 | 도입 전 | 현재 | 변화 |
| --- | --- | ---: | ---: | ---: |
| Benchmark 768 | 감성 accuracy | 0.9688 | 0.9492 | -0.0195 |
| 실제 공시 Gold | 감성 accuracy·macro F1 | 기존 30건 | v3 Codex Gold 600건 | 표본 변경으로 직접 증감 금지 |
| 실제 뉴스 Gold 80 | 감성 accuracy | 0.9750 | 0.9000 | -0.0750 |
| Stock review Gold 500 | 감성 accuracy | 0.9180 | 0.7880 | -0.1300 |
| Benchmark 768 | 중요도 accuracy | 0.9583 | 0.9323 | v3 코드북 변경으로 직접 증감 금지 |
| 실제 뉴스 Gold 80 | 중요도 accuracy | 0.9625 | 0.9500 | -0.0125 |
| Stock review Gold 500 | 중요도 accuracy | 0.8480 | 0.8060 | -0.0420 |
| K-FNSPID v3 Test 10,750 | 시장영향 accuracy | TF-IDF 0.4643 | seed 73 0.5095 | +0.0452 |
| K-FNSPID v3 Test 10,750 | 시장영향 macro F1 | TF-IDF 0.3429 | seed 73 0.3820 | +0.0391 |
| K-FNSPID v3 Test 10,750 | quadratic kappa | TF-IDF 0.3141 | seed 73 0.4694 | +0.1554 |

- 도입 전 기준은 `main` commit `076e97f8`의 `reports/ml-model-evaluation.json`이다.
- 공시 의미 중요도 운영 파이프라인은 기본 Gold 600건에서 기존 분석기 0.9150 / 0.8436을 1.0000 / 1.0000으로, 스트레스 포함 910건에서는 0.9055 / 0.8206을 0.9989 / 0.9962로 개선했다. paired accuracy 95% CI [0.0747, 0.1132], macro F1 차이 CI [0.1420, 0.2132], McNemar p=1.14e-24다. 동일 코드북의 Codex 단일 판정이라는 한계는 별도로 유지한다.
- K-FNSPID 시장영향은 의미 중요도를 덮어쓰지 않고 독립 필드로 노출한다.
- 감성은 공개 균형 Test에서 기존 TF-IDF macro F1 `0.4423→0.8840`으로 개선됐으나 기존 운영형 평가셋에서는 회귀했다. 두 결과는 평가 분포가 달라 직접 상쇄할 수 없다.
- 현재 `pass/promoted`는 정의된 배포 gate 통과를 뜻하며 외부 SOTA 또는 투자 성과를 뜻하지 않는다.
- 전체 근거와 후속 연구 gate는 [K-FNSPID 도입 전후·연구 준비도](models/k-fnspid-research-readiness.md)에 기록한다.

## 남은 개선
- 활성 2,752종목 전체가 specific profile로 서빙되며 LOW confidence는 15개, 0.5451%다.
- Naver 동일업종·OpenDART·WiseReport·KSIC를 결합하고, business profile ML classifier는 holdout macro F1 0.995282를 기록한다.
- 뉴스·공시 이벤트 모델은 stock review gold에서 희소 이벤트 라벨 macro F1이 낮아, 운영 로그 기반 gold 확장이 필요하다.
- 시장영향은 동일 다중 사건을 제외했어도 거시경제·업종 교란이 남으므로 단독 투자 신호로 사용하지 않는다.
- 시장영향의 NEWS 10,160건 macro F1은 0.3436→0.3847로 개선됐으나 DISCLOSURE 590건은 0.3006→0.2211로 회귀했다. 공시 의미 중요도는 별도 모델을 유지하며 공시 가격반응 SOTA를 주장하지 않는다.
- 뉴스 감성의 운영 회귀를 해소하고 독립 다중 평가자 Gold에서 재검증하기 전에는 전 분포 SOTA를 주장하지 않는다.
