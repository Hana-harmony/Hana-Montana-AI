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

# Hana Montana AI K-FNSPID v4 뉴스 시장영향 전문가

K-FNSPID v4의 뉴스 요청만 처리하는 KF-DeBERTa LoRA 순서형 분류 artifact다. `source_type=NEWS`가 아니면 런타임이 추론을 거부한다.

- 서비스명: Hana Montana AI(KF-DeBERTa + K-FNSPID)
- 라벨: LOW, MEDIUM, HIGH, CRITICAL
- Validation 선택 보정: log-prior 0.35, temperature 0.90
- 시간 Test 9,560건: Accuracy 0.5247, Macro-F1 0.3745, QWK 0.4754, ECE 0.0182
- 뉴스 TF-IDF 기준선: Accuracy 0.4715, Macro-F1 0.3484, QWK 0.3421, ECE 0.0453
- 거래일 cluster bootstrap 95% CI: Macro-F1 `[0.0120, 0.0409]`, QWK `[0.1090, 0.1558]`

가격·거래량·미래 수익률은 입력에 포함하지 않는다. 출력은 사후 가격반응의 확률적 보조 등급이며 의미 중요도, 인과효과, 투자 권유 또는 자동 주문 신호가 아니다. `hannah_metadata.json`과 학습 report의 파일 크기·SHA-256·dataset version·배포 gate가 모두 일치할 때만 활성화한다.
