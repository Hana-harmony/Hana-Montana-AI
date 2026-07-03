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
- Training report: `reports/foreign-ownership-quantity-training-report.json`
- SOTA report: `reports/foreign-ownership-quantity-sota-benchmark.json`
- Restricted universe report: `reports/foreign-ownership-restricted-universe-report.json`

## 한계
- 현재 feature는 외국인 보유수량 시계열 중심이다.
- 가격, 거래대금, 시장 전체 외국인 순매수 feature는 아직 운영 artifact에 포함하지 않는다.
- 논문 수준 주장을 위해서는 Diebold-Mariano test, bootstrap confidence interval, ablation study가 추가로 필요하다.
