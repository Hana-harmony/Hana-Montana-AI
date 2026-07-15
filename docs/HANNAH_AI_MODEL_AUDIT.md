# Hana Montana AI 모델 감사

## 서비스 표기

공식 서비스명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`이다. 단일 신경망이 아니라 금융 감성, 공시 의미 중요도, 뉴스·공시 시장영향, 이벤트·종목 연결과 근거 요약을 결합한 검증 파이프라인이다.

## 배포 모델

| 과제 | 배포 구성 | 독립 평가 | 상태 |
| --- | --- | --- | --- |
| 금융 감성 | KF-DeBERTa LoRA 80% + TF-IDF 20% | 공개 Test Macro-F1 0.8840, 뉴스 Gold Accuracy 0.9000 | pass |
| 공시 의미 중요도 | Validation 선택 제목+요약 모델 + 제한적 존속위험 정책 | 모델 단독 Gold Macro-F1 0.9470, 운영 Gold 0.9962 | pass |
| 뉴스 시장영향 | K-FNSPID v4 뉴스 KF-DeBERTa 전문가 | Test 9,560건 Accuracy 0.5247 / Macro-F1 0.3745 / QWK 0.4754 | pass |
| 공시 시장영향 | K-FNSPID v4 공시 KF-DeBERTa 전문가 seed 17 | Test 4,615건 Accuracy 0.4750 / Macro-F1 0.3216 / QWK 0.1550 | pass |

## K-FNSPID v4

- 뉴스 524,696건·공시 722,989건, 총 1,247,685문서
- 문서–종목 관계 1,136,118건, 시장영향 715,015건, 비혼입 대표 시장영향 255,168건
- 파일 기반 일별 시세 10,691,998행·2,800종목
- 공시 실제 원문 8,972건, 뉴스 실제 전문 13,310건 연결
- manifest SHA-256 `80b08190c538c1baeef418e4b50d5d9cb2ff9980ceb784a85b2988048ccc91c4`
- 운영 DB의 `market_daily_price`를 데이터셋 입력으로 사용하지 않음

## 시장영향 전후 비교

| 출처 | 지표 | TF-IDF 기준선 | 출처별 KF-DeBERTa | 차이 |
| --- | --- | ---: | ---: | ---: |
| 뉴스 | Accuracy | 0.4715 | 0.5247 | +0.0531 |
| 뉴스 | Macro-F1 | 0.3484 | 0.3745 | +0.0262 |
| 뉴스 | QWK | 0.3421 | 0.4754 | +0.1333 |
| 공시 | Accuracy | 0.3675 | 0.4750 | +0.1075 |
| 공시 | Macro-F1 | 0.2677 | 0.3216 | +0.0539 |
| 공시 | QWK | 0.1125 | 0.1550 | +0.0424 |
| 통합 | Macro-F1 | 0.3210 | 0.3690 | +0.0479 |
| 통합 | QWK | 0.2552 | 0.3975 | +0.1422 |

거래일 cluster bootstrap 2,000회에서 뉴스·공시·통합 Accuracy, Macro-F1, QWK 차이의 95% CI 하한이 모두 0보다 크다. 통합 exact McNemar `p=2.29e-55`다. 공시 QWK 차이 구간은 `[0.0046, 0.0794]`로 하한이 작아 다른 기간 재현을 계속 요구한다.

## 공시 다중 시드

- 동일 설정 seed: 17, 42, 73
- 선택 규칙: Test 미사용, Validation Macro-F1 최대
- 선택 seed: 17, Validation Macro-F1 0.2471
- Test Macro-F1 평균±표본표준편차: `0.3170±0.0052`
- seed 42는 Test ECE가 기준선보다 높아 독립 배포 gate를 통과하지 못했으며 선택되지 않음

## 런타임 안전성

- 요청 `source_type`과 artifact `source_type`이 다르면 추론을 거부한다.
- model report의 dataset version, gate, 파일 크기와 SHA-256이 실제 artifact와 모두 일치해야 로드한다.
- Transformer는 `safetensors`와 고정 base revision을 사용하고 remote code를 비활성화한다.
- 뉴스 기준선은 독립 gate를 통과해 같은 출처 장애 시에만 fallback할 수 있다.
- 공시 TF-IDF 기준선은 Macro-F1 gate 미달이므로 공시 Transformer 장애 시 시장영향 필드만 생략한다. 의미 중요도·감성·이벤트·요약은 계속 제공한다.

## Gold 검수

Gold는 Codex가 공개 코드북, 원문 제목, 대상 종목과 근거 필드를 대조해 검수했다. 사람 금융전문가 다중 주석이나 평가자 간 합의도로 표현하지 않는다. 정책 floor와 같은 코드북의 높은 운영 Gold 점수는 내부 일관성 결과이며 외부 전문가 타당성이나 SOTA 근거가 아니다.

## SOTA 판정

동일 한국 종목·동일 시장영향 라벨·동일 시간 Test의 외부 leaderboard가 없다. FNSPID, FINKRX, FININ, KRX-Bench, CARAG와 FinKario는 규모 또는 과제가 다르므로 직접 점수 순위를 만들지 않는다. 현재 모델은 최신 방법론과 논문 수준 평가 harness를 갖췄고 내부 기준선을 유의하게 넘지만, 외부 SOTA보다 뛰어나다고 주장하지 않는다.

## 정본 산출물

- `reports/hannah-ai-model-audit-report.json`
- `reports/k-fnspid-research-evaluation.json`
- `reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json`
- `reports/k-fnspid-impact-news-transformer-training-report.json`
- `reports/k-fnspid-impact-disclosure-transformer-training-report.json`
- `data/k_fnspid/v4/manifest.json`
