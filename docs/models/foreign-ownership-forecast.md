# 외국인 보유 예측 모델

## 목적
외국인 취득한도 제한 종목의 다음 거래일 `foreign_owned_quantity`를 예측하고, 이를 한도소진율 boundary로 변환한다. 결과는 사전 고지용 리스크 신호이며 주문 차단 결정이 아니다.

## Serving
- `POST /api/v1/market/foreign-ownership/predict`
- `POST /api/v1/market/foreign-ownership/model/retrain`

## 입력
- 종목코드
- 전날까지의 외국인 보유수량 시계열
- 외국인 한도수량

주문수량, 장중 거래량, 시세, 거래대금은 예측 feature로 쓰지 않는다.

## 모델
- 버전: `hannah-foreign-owned-quantity-ml-v1`
- Champion: `stock_routed_ml_ensemble`
- 검증: 날짜 기준 walk-forward validation
- 운영 universe: 현재 상장 외국인 취득한도 제한 32종목
- 학습 샘플: 52,693개
- 관측치: 58,784개
- Release status: `promoted`

## ML 후보와 선택 정책
- 후보군: Ridge, HistGradientBoostingRegressor, ExtraTreesRegressor, log-delta ratio 회귀, delta quantity 회귀, target quantity 회귀, residual 회귀, hurdle HistGradientBoosting classifier+regressor
- 주요 feature: `stock_code`, lag, 변화율, rolling mean/std/range, 40/60/120/240 관측치 장기 흐름, 최근 일별 delta 분포, 날짜, 관측치 수
- 선택 방식: 종목별 walk-forward MAE/RMSE/MAPE를 persistence baseline 대비 정규화한 composite score로 ML 후보와 blend alpha를 선택한다.
- guard: 종목별 runtime MAPE가 persistence보다 나빠지는 후보는 MAPE guard로 보정한다.
- Serving은 전날까지의 외국인 보유수량만 사용하며, 장중 시세·거래량·주문수량은 feature에 넣지 않는다.

## SOTA 비교
동일 제한 종목 universe, 동일 walk-forward fold, 동일 test sample 기준 내부 벤치마크다. N-HiTS와 PatchTST는 optional neural diagnostic이며 `max_steps=20`으로 실행했다.

| 모델 | MAE | RMSE | MAPE | Hannah 대비 |
| --- | ---: | ---: | ---: | --- |
| Hannah stock-routed ensemble | 51,539.19 | 147,477.74 | 0.044908 | 기준 |
| Persistence baseline | 53,912.99 | 152,521.80 | 0.046983 | MAE 4.40%, RMSE 3.31%, MAPE 4.42% 개선 |
| N-HiTS | 52,863.38 | 150,345.74 | 0.046955 | MAE 2.50%, RMSE 1.91%, MAPE 4.36% 개선 |
| PatchTST | 54,521.01 | 154,153.91 | 0.049739 | MAE 5.47%, RMSE 4.33%, MAPE 9.71% 개선 |

## 산출물
- Artifact: `src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib`
- Trainer: `src/hannah_montana_ai/training/foreign_ownership_quantity_trainer.py`
- Training report: `reports/foreign-ownership-quantity-training-report.json`
- SOTA report: `reports/foreign-ownership-quantity-sota-benchmark.json`
- Restricted universe report: `reports/foreign-ownership-restricted-universe-report.json`
- Presentation summary: `docs/FOREIGN_OWNERSHIP_MODEL_PRESENTATION.md`

## 한계
- 현재 feature는 외국인 보유수량 시계열 중심이다.
- 가격, 거래대금, 시장 전체 외국인 순매수 feature는 아직 운영 artifact에 포함하지 않는다.
- 논문 수준 주장을 위해서는 Diebold-Mariano test, bootstrap confidence interval, ablation study가 추가로 필요하다.
