---
base_model: kakaobank/kf-deberta-base
library_name: peft
language: ko
tags:
  - finance
  - deberta
  - lora
  - ordinal-classification
  - k-fnspid
---

# Hana Montana AI K-FNSPID v4 공시 시장영향 전문가

K-FNSPID v4의 공시 요청만 처리하는 KF-DeBERTa LoRA 순서형 분류 artifact다. `source_type=DISCLOSURE`가 아니면 런타임이 추론을 거부한다.

- 서비스명: Hana Montana AI(KF-DeBERTa + K-FNSPID)
- 라벨: LOW, MEDIUM, HIGH, CRITICAL
- 선택 seed: 17. seed 17/42/73의 Validation macro F1만으로 선택
- Validation 선택 보정: log-prior 0.05, temperature 0.50
- 시간 Test 4,615건: Accuracy 0.4750, Macro-F1 0.3216, QWK 0.1550, ECE 0.0441
- 공시 TF-IDF 기준선: Accuracy 0.3675, Macro-F1 0.2677, QWK 0.1125, ECE 0.0444
- 3-seed Test Macro-F1: 0.3170±0.0052
- 거래일 cluster bootstrap 95% CI: Macro-F1 `[0.0264, 0.0806]`, QWK `[0.0046, 0.0794]`

가격·거래량·미래 수익률은 입력에 포함하지 않는다. 출력은 사후 가격반응의 확률적 보조 등급이며 공시 의미 중요도, 인과효과, 투자 권유 또는 자동 주문 신호가 아니다. `hannah_metadata.json`과 학습 report의 파일 크기·SHA-256·dataset version·출처·배포 gate가 모두 일치할 때만 활성화한다.
