# Hannah Montana AI 모델 감사

## 결론
- 리포트: `reports/hannah-ai-model-audit-report.json`
- 감사 상태: `conditional_pass`
- 감사 대상: 금융 뉴스/공시 NLP, 종목 링커, 외국인 보유수량 예측, 글로벌 피어 매칭
- 모든 serving 핵심 기능은 실제 ML artifact를 사용한다. 단, 글로벌 피어 전종목 confidence는 국내 업종 feature 부족으로 추가 개선이 필요하다.

| 기능 | 모델 | 최신 성능 | 상태 |
| --- | --- | --- | --- |
| 금융 뉴스/공시 NLP | TF-IDF + supervised LogisticRegression | benchmark event macro F1 0.9844, sentiment accuracy 0.9688, real news event macro F1 0.9221 | pass |
| 종목 링커 | TF-IDF nearest-neighbor entity linker | 전체 종목코드 template accuracy 1.0, 종목명 template accuracy 0.9921 | pass |
| 외국인 보유수량 예측 | stock-routed panel time-series ML ensemble | MAE 51,539.19, RMSE 147,477.74, MAPE 0.044908, persistence 대비 MAPE 4.4167% 개선 | promoted |
| 글로벌 피어 매칭 | TF-IDF + SVD semantic + 재무 feature + pairwise LogisticRegression reranker | curated pairwise top1 1.0, 전종목 3,967/3,967 추론 성공, smoke 15개 통과 | conditional_pass |

## SOTA/Baseline 비교
- 외국인 보유수량 예측은 같은 제한 종목 universe와 같은 walk-forward sample에서 persistence baseline, N-HiTS, PatchTST와 비교한다.
- 현재 모델 MAPE 0.044908은 persistence 0.046983, N-HiTS 0.046955, PatchTST 0.049739보다 낮다.
- 글로벌 피어 매칭은 공개 표준 SOTA leaderboard가 없어 curated peer benchmark와 전종목 coverage gate를 운영 기준으로 둔다.

## 남은 개선
- 글로벌 피어 LOW confidence 비율은 75.4726%로 monitoring target 35%보다 높다.
- 원인은 국내 master의 섹터/업종 컬럼 부재다. 다음 학습 개선은 KRX/WICS/GICS 또는 사업보고서 기반 업종 feature를 수집해 한국 profile corpus에 넣는 것이다.
- 금융 NLP는 stock review gold에서 희소 이벤트 라벨 macro F1이 낮아, 운영 로그 기반 gold 확장이 필요하다.
