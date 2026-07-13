# Hannah Montana AI 모델 감사

## 결론
- 리포트: `reports/hannah-ai-model-audit-report.json`
- 감사 상태: `pass`
- 감사 대상: 뉴스·공시 분석, 종목 링커, 외국인 보유수량 예측, 글로벌 피어 매칭
- 모든 serving 핵심 기능은 실제 ML artifact를 사용한다. 글로벌 피어 confidence는 국내 동일업종 feature 보강 후 monitoring gate를 통과한다.

| 기능 | 모델 | 최신 성능 | 상태 |
| --- | --- | --- | --- |
| 뉴스·공시 이벤트 | TF-IDF + supervised LogisticRegression | benchmark event macro F1 0.9844, real news event macro F1 0.9221 | pass |
| 한국 금융 감성 | KF-DeBERTa LoRA + TF-IDF 확률 앙상블 | 공개 Test 933건 macro F1 0.8840, 실제 뉴스 Gold accuracy 0.9000 | pass |
| K-FNSPID 시장영향 | 55만 문서·1069만 시세 파일 + KF-DeBERTa LoRA | Test 10,728건 accuracy 0.5006, macro F1 0.3664, quadratic kappa 0.4186 | promoted |
| 종목 링커 | TF-IDF nearest-neighbor entity linker | 전체 종목코드 template accuracy 1.0, 종목명 template accuracy 0.9921 | pass |
| 외국인 보유수량 예측 | stock-routed panel time-series ML ensemble | MAE 51,539.19, RMSE 147,477.74, MAPE 0.044908, persistence 대비 MAPE 4.4167% 개선 | promoted |
| 글로벌 피어 매칭 | Business profile ML classifier + TF-IDF + SVD semantic + 재무·업종·인지도 동적 유사도 | KIS 활성 일반주식 2,752/2,752 추론 성공, 종목별 정답·anchor 없음, LOW confidence 0.5451% | pass |

## SOTA/Baseline 비교
- 외국인 보유수량 예측은 같은 제한 종목 universe와 같은 walk-forward sample에서 persistence baseline, N-HiTS, PatchTST와 비교한다.
- 현재 모델 MAPE 0.044908은 persistence 0.046983, N-HiTS 0.046955, PatchTST 0.049739보다 낮다.
- 글로벌 피어 매칭은 공개 표준 SOTA leaderboard가 없어 KIS 활성 universe 전체 coverage와 도메인·표시 계약 gate를 운영 기준으로 둔다.
- 공개 금융 감성 균형 Test 933건에서 KF-DeBERTa LoRA 앙상블 macro F1 0.8840, KF-DeBERTa 단독 0.8850, KR-FinBERT-SC 0.7272, 기존 Hannah TF-IDF 0.4423이다. 실제 공시 Gold accuracy 1.0000과 실제 뉴스 Gold accuracy 0.9000도 동일 보고서의 배포 gate에 고정한다.
- K-FNSPID 시간 외삽 Test에서 KF-DeBERTa LoRA는 TF-IDF 기준선 대비 accuracy +0.0463, macro F1 +0.0051, quadratic kappa +0.0671을 기록해 승격했다.
- 시장영향은 같은 라벨 정의의 공개 SOTA leaderboard가 없어 2026년 4월 이후 시간 외삽 Test 10,728건의 macro F1·quadratic kappa와 TF-IDF 기준선 동시 상회로 Transformer 승격을 제한한다.

## K-FNSPID 도입 전후 감사

| 평가셋 | 지표 | 도입 전 | 현재 | 변화 |
| --- | --- | ---: | ---: | ---: |
| Benchmark 768 | 감성 accuracy | 0.9688 | 0.9492 | -0.0195 |
| 실제 공시 Gold 30 | 감성 accuracy | 1.0000 | 1.0000 | 0.0000 |
| 실제 뉴스 Gold 80 | 감성 accuracy | 0.9750 | 0.9000 | -0.0750 |
| Stock review Gold 500 | 감성 accuracy | 0.9180 | 0.7880 | -0.1300 |
| 네 기존 평가셋 | 중요도 accuracy | 0.9583/1.0000/0.9625/0.8480 | 동일 | 0.0000 |
| K-FNSPID Test 10,728 | 시장영향 accuracy | 0.4542 | 0.5006 | +0.0463 |
| K-FNSPID Test 10,728 | 시장영향 macro F1 | 0.3613 | 0.3664 | +0.0051 |
| K-FNSPID Test 10,728 | quadratic kappa | 0.3515 | 0.4186 | +0.0671 |

- 도입 전 기준은 `main` commit `076e97f8`의 `reports/ml-model-evaluation.json`이다.
- K-FNSPID는 중요도에 실제 가격 반응 근거를 추가했지만 기존 중요도 Gold 정확도를 개선하지는 않았다.
- 감성은 공개 균형 Test에서 기존 TF-IDF macro F1 `0.4423→0.8840`으로 개선됐으나 기존 운영형 평가셋에서는 회귀했다. 두 결과는 평가 분포가 달라 직접 상쇄할 수 없다.
- 현재 `pass/promoted`는 정의된 배포 gate 통과를 뜻하며 SOTA 또는 논문 준비 완료를 뜻하지 않는다.
- 전체 근거와 후속 연구 gate는 [K-FNSPID 도입 전후·연구 준비도](models/k-fnspid-research-readiness.md)에 기록한다.

## 남은 개선
- 활성 2,752종목 전체가 specific profile로 서빙되며 LOW confidence는 15개, 0.5451%다.
- Naver 동일업종·OpenDART·WiseReport·KSIC를 결합하고, business profile ML classifier는 holdout macro F1 0.995282를 기록한다.
- 뉴스·공시 이벤트 모델은 stock review gold에서 희소 이벤트 라벨 macro F1이 낮아, 운영 로그 기반 gold 확장이 필요하다.
- 시장영향은 동일 다중 사건을 제외했어도 거시경제·업종 교란이 남으므로 단독 투자 신호로 사용하지 않는다.
- 뉴스 감성의 운영 회귀를 해소하고 독립 다중 평가자 Gold에서 재검증하기 전에는 전 분포 SOTA를 주장하지 않는다.
