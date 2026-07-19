# 주문 상태 해석 모델

## 목적과 API

`POST /api/v1/stocks/order-status`에서 외국인 취득한도와 KRX 거래 상태를 조합해 협력사 주문 화면용 제한 신호를 만든다.

## 모델

- 외국인 boundary: `foreign-ownership-boundary-v1`
- 거래 상태: `krx-vi-price-limit-state-v1`
- 입력: 발행주식수, 외국인 보유·한도 수량, 현재가·전일종가·상하한가, VI·거래 상태, 환율
- 출력: 보유율·한도소진율, 예측 범위, VI·가격제한 상태, 매수·매도 가능 표시, 제한 사유와 model version

결정 규칙은 입력 스냅샷에서 재현 가능하며 confidence를 임의 생성하지 않는다. 결과는 참고 신호이고 실제 주문 승인·체결을 수행하지 않는다.

## 검증

- `tests/test_feature_definition_contracts.py`
- `tests/test_omni_connect_contract.py`
