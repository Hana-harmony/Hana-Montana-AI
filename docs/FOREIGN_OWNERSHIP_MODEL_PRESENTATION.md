# 외국인 보유/취득 수량 예측 모델 발표자료 요약

## 한 줄 결론
- 제한 종목 universe의 동일 walk-forward 평가에서 Hannah 모델은 persistence baseline, N-HiTS, PatchTST 대비 MAE/RMSE/MAPE를 모두 개선했다.
- 운영 artifact는 `release_status=promoted`이며, 학습 가능한 외국인 취득한도 제한 29종목 전체를 ML runtime으로 예측한다.

## 평가 조건
- 대상 universe: 외국인 취득한도 제한 현재 상장 32종목 중 양수 보유수량 학습 샘플이 있는 29종목
- 평가 샘플: 21,895개 walk-forward test sample
- 학습 데이터: KRX Data Marketplace 기반 일별 외국인 보유수량, 2019-01-02부터 2026-06-26까지 58,784개 관측치
- 예측 타깃: 다음 거래일 `foreign_owned_quantity`
- 입력 feature: 전날까지의 외국인 보유수량 시계열, 한도수량 기반 소진율/잔여한도, lag/rolling/change-interval/date feature
- 제외 입력: 주문수량, 장중 거래량, 시세, 거래대금
- 검증 방식: random split이 아닌 날짜 기준 walk-forward validation

## 성능 비교

| 모델 | MAE | RMSE | MAPE | Hannah 대비 차이 |
| --- | ---: | ---: | ---: | --- |
| Hannah stock-routed ensemble | 51,539.19 | 147,477.74 | 0.044908 | 기준 모델 |
| Persistence baseline | 53,912.99 | 152,521.80 | 0.046983 | MAE 4.40%, RMSE 3.31%, MAPE 4.42% 개선 |
| N-HiTS | 52,863.38 | 150,345.74 | 0.046955 | MAE 2.50%, RMSE 1.91%, MAPE 4.36% 개선 |
| PatchTST | 54,521.01 | 154,153.91 | 0.049739 | MAE 5.47%, RMSE 4.33%, MAPE 9.71% 개선 |

## 모델 구조 요약
- Champion: `stock_routed_ml_ensemble`
- 후보군: Ridge, HistGradientBoostingRegressor, ExtraTreesRegressor, log-delta ratio, delta quantity, target quantity, residual, hurdle classifier+regressor
- Routing: 종목별 walk-forward 검증에서 MAE/RMSE/MAPE를 persistence baseline 대비 정규화한 composite score로 후보와 blend alpha 선택
- Guard: persistence baseline보다 MAPE가 나빠지는 후보/runtime은 종목별 MAPE guard로 보정
- Runtime: ML 29종목, persistence baseline fallback 0종목

## 발표용 핵심 메시지
- 전일값 유지가 강한 금융 시계열 문제에서도 제한 종목별 routing과 MAPE guard를 적용하면 안정적으로 baseline을 개선할 수 있다.
- N-HiTS/PatchTST와 동일 walk-forward sample에서 비교했을 때 Hannah 모델이 MAE/RMSE/MAPE 모두 우수하다.
- 한도수량은 예측 대상이 아니라 예측 보유수량을 한도소진율로 환산하는 분모로만 사용한다.
- 모델 결과는 주문 차단이 아니라 금일 한도 도달 가능성 사전 고지용 risk boundary에 사용한다.

## 산출물
- 학습 리포트: `reports/foreign-ownership-quantity-training-report.json`
- SOTA 비교 리포트: `reports/foreign-ownership-quantity-sota-benchmark.json`
- 제한 종목 universe 리포트: `reports/foreign-ownership-restricted-universe-report.json`
- 운영 artifact: `src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib`

## 주의사항
- N-HiTS/PatchTST 비교는 동일 fold와 동일 sample 기준으로 수행했지만, optional neural diagnostic은 `max_steps=20` 설정이다.
- 논문 제출 수준의 주장을 위해서는 Diebold-Mariano test, bootstrap confidence interval, ablation study, 기간별 robustness 분석을 추가해야 한다.
