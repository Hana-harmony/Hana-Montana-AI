---
base_model: kakaobank/kf-deberta-base
library_name: peft
language:
- ko
tags:
- finance
- text-classification
- lora
- k-fnspid
---

# Hana Montana AI(KF-DeBERTa + K-FNSPID) 공유 초기화 어댑터

이 디렉터리는 v3 공유 모델의 동결 아카이브이며 v4 출처별 전문가의 초기화에만 사용한다. 운영 추론에는 뉴스 전용 `k_fnspid_impact_news_transformer`와 공시 전용 `k_fnspid_impact_disclosure_transformer`만 사용하고, 요청 출처와 artifact 출처가 다르면 거부한다.

## 아티팩트

- 기반 모델: `kakaobank/kf-deberta-base`
- 고정 revision: `363b171d71443b0874b0bf9cea053eb5b1650633`
- 선택 seed: `73`
- 입력 규격: `k-fnspid-text-v2`, 최대 256 token
- 학습 방식: LoRA(r=16, alpha=32, dropout=0.1), focal loss와 ordinal CDF 보조 손실
- 후처리: Validation에서만 선택한 log-prior correction strength `0.15`
- 버전: `k-fnspid-impact-kf-deberta-lora-20260714013051-prior0.15`

`hannah_metadata.json`에 기반 모델 revision, 라벨 순서, 아티팩트별 SHA-256와 byte 크기를 저장한다. 런타임은 로드 전에 이 값을 검증한다.

## 과거 데이터와 평가

아래 수치는 v3 공유 split의 역사적 결과이며 v4 현재 성능이나 운영 gate로 사용하지 않는다. K-FNSPID v3는 문서 550,662건, 종목 연결 819,772건, 시장영향 398,942건, 일별 시세 10,691,998건으로 구성됐다.

| 모델 | Accuracy | Macro-F1 | Quadratic Kappa |
| --- | ---: | ---: | ---: |
| TF-IDF 기준선 | 0.4643 | 0.3429 | 0.3141 |
| KF-DeBERTa LoRA seed 73 | 0.5095 | 0.3820 | 0.4694 |

3개 seed의 Test 평균±표준편차는 Accuracy `0.5105±0.0080`, Macro-F1 `0.3824±0.0102`, QWK `0.4675±0.0042`다. 거래일 단위 클러스터 부트스트랩 95% 신뢰구간 기준 개선폭은 Accuracy `[0.0351, 0.0557]`, Macro-F1 `[0.0256, 0.0536]`, QWK `[0.1331, 0.1776]`이며 McNemar exact p-value는 `1.70e-20`이다.

공시 590건 부분집합의 회귀가 v4 출처 분리의 직접 원인이었다. v4 공시 Test 4,615건에서는 공시 전문가가 기준선 macro F1 0.2677을 0.3216으로, QWK 0.1125를 0.1550으로 개선했다.

## 사용 범위와 한계

- 이 공유 artifact를 운영 추론에 직접 사용하지 않는다.
- 외부 동일 라벨·동일 시간 split 리더보드가 없어 외부 SOTA를 주장하지 않는다.
- 수익 또는 가격 방향을 예측하지 않으며 매수·매도 신호가 아니다.
- 중복 제거, 종목 연결, 시간 split, 데이터 manifest를 유지하지 않은 재평가는 비교할 수 없다.
- 새 시기·새 출처에는 분포 변화와 calibration을 다시 검증해야 한다.

상세 재현 절차, ablation, 통계 검정과 출처별 결과는 `docs/models/k-fnspid-market-impact.md` 및 `reports/k-fnspid-research-evaluation.json`을 따른다.
