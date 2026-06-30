# Hannah Montana AI 모델 감사

## 결론
- 리포트: `reports/hannah-ai-model-audit-report.json`
- 감사 상태: `pass`
- 감사 대상: 금융 뉴스/공시 NLP, 종목 링커, 외국인 보유수량 예측, 글로벌 피어 매칭
- 모든 serving 핵심 기능은 실제 ML artifact를 사용한다. 글로벌 피어 confidence는 국내 동일업종 feature 보강 후 monitoring gate를 통과한다.

| 기능 | 모델 | 최신 성능 | 상태 |
| --- | --- | --- | --- |
| 금융 뉴스/공시 NLP | TF-IDF + supervised LogisticRegression | benchmark event macro F1 0.9844, sentiment accuracy 0.9688, real news event macro F1 0.9221 | pass |
| 종목 링커 | TF-IDF nearest-neighbor entity linker | 전체 종목코드 template accuracy 1.0, 종목명 template accuracy 0.9921 | pass |
| 외국인 보유수량 예측 | stock-routed panel time-series ML ensemble | MAE 51,539.19, RMSE 147,477.74, MAPE 0.044908, persistence 대비 MAPE 4.4167% 개선 | promoted |
| 글로벌 피어 매칭 | TF-IDF + SVD semantic + 재무/업종 feature + pairwise LogisticRegression reranker | curated pairwise top1 0.9286, top3 1.0, 전종목 3,967/3,967 추론 성공, LOW confidence 22.6620%, specific profile LOW 0개 | pass |

## SOTA/Baseline 비교
- 외국인 보유수량 예측은 같은 제한 종목 universe와 같은 walk-forward sample에서 persistence baseline, N-HiTS, PatchTST와 비교한다.
- 현재 모델 MAPE 0.044908은 persistence 0.046983, N-HiTS 0.046955, PatchTST 0.049739보다 낮다.
- 글로벌 피어 매칭은 공개 표준 SOTA leaderboard가 없어 curated peer benchmark와 전종목 coverage gate를 운영 기준으로 둔다.

## 남은 개선
- 글로벌 피어 LOW confidence 비율은 국내 동일업종 feature 보강 전 75.4726%에서 22.6620%로 낮아졌고 monitoring target 35%를 통과한다.
- 도메인 근거가 있는 specific profile 3,068개에서는 LOW confidence가 0개다. 남은 LOW 899개는 모두 generic/legacy fallback profile이다.
- 국내 업종 profile은 Naver 동일업종 비교 데이터 2,649개를 수집했고, Naver taxonomy 보정 후 2,637개가 specific sector/industry feature를 제공한다.
- 금융 NLP는 stock review gold에서 희소 이벤트 라벨 macro F1이 낮아, 운영 로그 기반 gold 확장이 필요하다.
