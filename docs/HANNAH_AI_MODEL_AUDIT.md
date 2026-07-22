# Hana Montana AI 모델 감사

## 서비스 표기

공식 서비스명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`이다. 단일 신경망이 아니라 금융 감성, 공시 의미 중요도, 뉴스·공시 시장영향, 이벤트·종목 연결과 근거 요약을 결합한 검증 파이프라인이다.

## 배포 모델

| 과제 | 배포 구성 | 독립 평가 | 상태 |
| --- | --- | --- | --- |
| 금융 감성 | 현행 운영 모델 유지; v6 후보는 K-FNSPID DAPT FP32 base + all-12 LoRA r16 + 공유/출처 residual 계층형 head | 확증 1,200건 층화가중 NEWS 0.7503/0.5530, DISCLOSURE 0.8646/0.6024 | `KEEP_CURRENT_MODEL`, 미승격 |
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

## 시장영향 KR-FinBERT-SC 비교

| 출처 | 지표 | KR-FinBERT-SC | Hana Montana AI | 차이 |
| --- | --- | ---: | ---: | ---: |
| 국내 뉴스 | Accuracy | 0.4902 | 0.5247 | +7.04% (+0.0345점) |
| 국내 뉴스 | Macro-F1 | 0.3506 | 0.3745 | +6.82% (+0.0239점) |
| 국내 뉴스 | QWK | 0.3962 | 0.4754 | +19.99% (+0.0792점) |
| 국내 공시 | Accuracy | 0.4319 | 0.4750 | +9.99% (+0.0431점) |
| 국내 공시 | Macro-F1 | 0.3131 | 0.3216 | +2.72% (+0.0085점) |
| 국내 공시 | QWK | 0.1611 | 0.1550 | -3.79% (-0.0061점) |

거래일 군집 bootstrap 2,000회와 두 출처 Holm 보정에서 국내 뉴스 Macro-F1 차이의 95% 신뢰구간은 `[0.0090, 0.0383]`, QWK 차이는 `[0.0622, 0.0960]`로 우위 gate를 통과했다. 국내 공시 Macro-F1 차이는 `[-0.0126, 0.0317]`, QWK 차이는 `[-0.0384, 0.0266]`이므로 점수 차이만으로 우위를 주장하지 않는다. TF-IDF는 전통 진단 기준선으로 보존하되 SOTA급 비교군으로 표현하지 않는다.

## 공시 다중 시드

- 동일 설정 seed: 17, 42, 73
- 선택 규칙: Test 미사용, Validation Macro-F1 최대
- 선택 seed: 17, Validation Macro-F1 0.2471
- Test Macro-F1 평균±표본표준편차: `0.3170±0.0052`
- seed 42는 Test ECE가 기준선보다 높아 독립 배포 gate를 통과하지 못했으며 선택되지 않음

## 런타임 안전성

- 요청 `source_type`과 artifact `source_type`이 다르면 추론을 거부한다.
- model report의 dataset version, gate, 파일 크기와 SHA-256이 실제 artifact와 모두 일치해야 로드한다.
- upstream base weight는 고정 revision·고정 SHA-256으로 검증하고 `weights_only=True`로 읽은 뒤 배포용 `safetensors`로 변환한다. 운영 로더는 변환본과 서명을 검증하고 remote code를 비활성화한다.
- 뉴스 기준선은 독립 gate를 통과해 같은 출처 장애 시에만 fallback할 수 있다.
- 공시 TF-IDF 기준선은 Macro-F1 gate 미달이므로 공시 Transformer 장애 시 시장영향 필드만 생략한다. 의미 중요도·감성·이벤트·요약은 계속 제공한다.

## 감성 데이터와 Gold 검수

| 구성 | 건수 | 역할 |
| --- | ---: | --- |
| 주 학습 Gold | 596 | 최초 합의 574·재심 확정 22·미해결 제외 4 |
| 뉴스 보조 Gold | 598 | 최초 합의 571·재심 확정 27·미해결 제외 2 |
| 공시 보조 Gold | 600 | 최초 합의 554·재심 확정 46 |
| Silver | 32,700 | 뉴스 30,000 + 공시 2,700 |
| 개발 Gold | 895 | 뉴스 448 + 공시 447, 미해결 5건 제외 |
| trainer 준비 학습행 | 32,907 | 중복·충돌·역할 제한 적용 결과 |

검수 주체는 Codex AI이며 사람 금융전문가로 표현하지 않는다. 2026-07-16 감사에서 receipt가 없던 기존 라벨은 `LEGACY_UNVERIFIED`로 보존했다. 2026-07-17 두 독립 review context와 별도 adjudicator context에서 5개 packet 전체를 다시 판정했으며 packet·codebook·prompt·decision 해시, 모델 버전, run/context ID와 blindness commitment를 receipt로 결합했다. 5개 provenance manifest는 모두 `VERIFIED_BLIND_PROVENANCE`이고 미해결 11건은 제외했다. 이는 AI context 사이의 절차적 분리 근거이며 사람 금융전문가 외적 타당도를 대체하지 않는다.

## 금융 감성 방법론 감사

- 공식 서비스명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`로 고정한다.
- 데이터 선택은 seed `20260715`로 고정하고, 모델 변동성은 seed `17`, `42`, `73`의 독립 반복으로 분리한다. 모델 seed를 바꾸어도 학습·개발 문서와 분할 commitment는 같아야 한다.
- 개발 적격 공개 Validation 932건과 receipt-bound 개발 Gold 895건을 중복·보호 group 제거 후 Checkpoint 911 / Calibration 455 / Selection 461로 분리한다. 각 역할은 checkpoint 선택, domain별 보정, seed·후보 선택에만 각각 사용한다.
- DAPT는 보호 fuzzy 연결요소를 제거한 K-FNSPID 1,118,291건, 62,468,526 non-padding token으로 KF-DeBERTa의 all-12 query/value LoRA를 3,908 update 학습한다. FP32/BF16 1,024-pack pilot에서 BF16 memory-slope gate가 실패해 FP32를 선택했다.
- supervised 후보는 검증·병합된 DAPT FP32 base의 12개 layer query/key/value/dense에 rank-16 LoRA를 적용한다. 대상 종목 prefix와 본문 head-tail을 최대 256 token으로 결합하고, R-Drop과 fixed domain/task-cell mass 계층형 CE를 사용한다.
- 공유 중립/방향 head에 NEWS·DISCLOSURE·PUBLIC residual을 더하며 residual은 정확한 0으로 초기화한다. 1단계 전체행 2 epoch 뒤 2단계 receipt-bound Gold head 정제 4 epoch를 수행한다.
- target-swap은 공식명, 종목코드와 alias가 교체 문맥에 남아 있지 않은 표본만 허용한다. 단순 이름 문자열 한 개 제거를 target 제거로 간주하지 않는다.
- 공정 기준선은 `snunlp/KR-FinBert-SC` 전체 parameter를 fine-tuning하며 후보와 동일한 원천행·group split·data seed·model seeds·epoch·optimizer update 일정을 사용한다. 모델별 learning rate와 trainable parameter 수의 차이는 보고서에 남긴다.
- 공개 감성 Test는 과거 반복 조회됐으므로 회귀 진단 전용이다. 그 결과를 신규 후보 선택, 확증 유의성 또는 SOTA 주장에 사용하지 않는다.
- 학습 recipe·후보·평가계획을 원격 Git 커밋으로 증명한 뒤 확증 Gold를 완성한다. 확증 평가는 NEWS와 DISCLOSURE를 분리해 단 한 번 수행하고 receipt를 남긴다.
- DAPT base는 artifact v2 manifest, merged FP32 safetensors, 입력·dependency·prepared·pilot·두 oracle·종료 validation NLL을 현재 source와 모두 재검증할 때만 supervised trainer가 허용한다.

## 잠긴 통계분석계획

- 가족별 유의수준은 0.05다.
- 신규 후보와 `원본 KR-FinBERT-SC`, `K-FNSPID 도입 전 모델`, `공정 full-FT KR-FinBERT-SC`를 NEWS·DISCLOSURE 각각에서 비교하는 6개 가설에 Holm 보정을 적용한다.
- 확증 표본의 층별 비복원추출 설계를 반영해 paired stratified SRSWOR 가중치와 finite-population correction을 사용한다.
- 1차 분산은 paired delete-one jackknife, 보조 구간·민감도 분석은 seed `20260715`의 paired bootstrap 2,000회로 산출한다.
- 가중 Macro-F1은 비선형 plug-in 추정량이다. 불편성을 주장하지 않으며, Holm 보정된 p값의 family-wise error control을 개별 구간의 동시 coverage로 확대 해석하지 않는다.

| 신규 감성 판정 | NEWS | DISCLOSURE |
| --- | ---: | ---: |
| 층화가중 Accuracy / Macro-F1 | 0.7503 / 0.5530 | 0.8646 / 0.6024 |
| 비가중 600건 Accuracy / Macro-F1 | 0.7433 / 0.6636 | 0.7000 / 0.6056 |
| 공정 full-FT 기준선 가중 Macro-F1 | 0.5771, 후보 -0.0241점 | 0.5647, 후보 +0.0376점 |
| 원본 KR-FinBERT-SC 가중 Macro-F1 | 0.4937, 후보 +0.0594점 | 0.6146, 후보 -0.0123점 |
| Holm 보정 결론 | 공정·원본 기준선 우월성 미확인 | 공정·원본 기준선 우월성 미확인 |
| 배포 승격 | 미승격 | 미승격 |

one-shot 보고서의 배포 판정은 `KEEP_CURRENT_MODEL`이다. 비가중 기술통계에서는 원본 KR-FinBERT-SC보다 NEWS +12.45%p, DISCLOSURE +4.49%p 높지만, 사전 지정 1차 층화가중 지표에서는 NEWS만 +5.94%p이고 DISCLOSURE는 -1.23%p다. 따라서 “두 출처 모두 개선”, “통계적으로 우월” 또는 “SOTA”라고 표현하지 않는다.

## 시간 일반화 한계

개발 Gold는 2025년 6--12월에 집중되고, 보조 공시 Gold와 확증 후보는 2026년 4--7월에 집중된다. 확증 표본은 학습 표본과 문서·commitment 수준으로 분리되지만 학습 자료보다 명확히 뒤선 미래 기간의 out-of-time 표본은 아니다. 따라서 one-shot 결과가 나오더라도 같은 기간의 disjoint confirmatory evidence로만 해석하고 장기 시간 일반화 근거로 표현하지 않는다.

고정 seed는 입력·분할·모델 반복을 통제하지만 Apple MPS와 다른 accelerator 사이의 bitwise 동일성을 보장하지 않는다. 각 run의 실제 device, global step과 runtime을 보존하고 통계적 반복 가능성과 bitwise 재현성을 구분한다.

## SOTA 판정

동일 한국 뉴스·공시, 동일 target-aware 감성 정의와 동일 확증 표본을 사용하는 공인 leaderboard가 없다. FNSPID, FINKRX, FININ, KRX-Bench, CARAG와 FinKario는 규모 또는 과제가 다르므로 직접 점수 순위를 만들지 않는다. 감성 신규 후보는 이름이 명시된 기준선에 대한 잠긴 동일표본 비교만 주장할 수 있다. 시장영향은 사용자 지정에 따라 KR-FinBERT-SC만 동일 K-FNSPID 파이프라인으로 비교했고 KLUE-RoBERTa-large는 제외했다. 국내 뉴스 우위는 확인했지만 국내 공시 우위는 확인하지 못했으며 전역 SOTA를 주장하지 않는다.

## 정본 산출물

- `reports/hannah-ai-model-audit-report.json`
- `reports/k-fnspid-research-evaluation.json`
- `reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json`
- `reports/k-fnspid-impact-news-transformer-training-report.json`
- `reports/k-fnspid-impact-disclosure-transformer-training-report.json`
- `reports/k-fnspid-impact-strong-baseline-study-contract.json`
- `reports/k-fnspid-impact-kr-finbert-sc-matrix.json`
- `reports/k-fnspid-impact-kr-finbert-sc-result-attestation.json`
- `reports/korean-finance-sentiment-benchmark-v4.json` (SHA-256 `be5c9edd…b149`)
- `data/k_fnspid/v4/manifest.json`
