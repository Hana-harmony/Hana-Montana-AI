# K-FNSPID 감성 Gold provenance 감사

- 최초 감사일: 2026-07-16
- 재검수 완료일: 2026-07-17
- 적용 계약: `k-fnspid-sentiment-review-receipt/v1`
- 결론: **기존 파일은 `LEGACY_UNVERIFIED`로 보존하고, 5개 packet을 새로 이중 블라인드
  검수해 `VERIFIED_BLIND_PROVENANCE` 산출물로 승격함**
- 데이터 변경: 미해결 판정 11건을 강제 라벨링하지 않고 제외했으며 합의·재심 결과를 반영함

## 감사 결과

2026-07-16 작업트리의 `data/` 및 `reports/` 아래에서 reviewer별 review receipt, stage manifest,
dual-review provenance manifest를 탐색했으나 검증 가능한 파일은 0개였다. 기존 decision의
`reviewer_id`, `model_blind=true`, `market_blind=true`는 자체 신고된 필드일 뿐이며, 다음
사실을 복원하거나 검증하지 못했다.

- reviewer가 실제로 받은 packet의 byte 내용과 행 범위
- 실제 코드북·프롬프트 해시
- 사용한 AI 모델명·버전과 독립 run/context ID
- candidate·teacher 예측과 사후 시장 반응의 실제 비노출 여부
- review 후 packet·decision mutation 여부

따라서 기존 라벨을 그대로 두고 receipt만 소급 생성하지 않았다. 대신 동일 원본 packet을
새로운 독립 run/context에서 처음부터 다시 검수했다. 승격 script는 provenance manifest가
없거나 packet 범위·결정 순서·receipt chain·blindness commitment가 하나라도 다르면
`LEGACY_UNVERIFIED`로 fail-close한다.

## 2026-07-17 재검수 결과

| 용도·출처 | 후보 | 최초 합의 | 불일치 | 재심 확정 | 미해결 제외 | 최종 학습·개발 Gold |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 주 학습 NEWS | 600 | 574 | 26 | 22 | 4 | 596 |
| 보조 학습 NEWS | 600 | 571 | 29 | 27 | 2 | 598 |
| 보조 학습 DISCLOSURE | 600 | 554 | 46 | 46 | 0 | 600 |
| 개발 NEWS | 450 | 434 | 16 | 14 | 2 | 448 |
| 개발 DISCLOSURE | 450 | 444 | 6 | 3 | 3 | 447 |

두 reviewer와 adjudicator는 서로 다른 run/context ID를 사용했고 candidate·teacher 예측,
시장 반응과 reviewer 상호 결정을 보지 않았다. 모든 packet은 입력 범위와 행 순서를 receipt로
잠갔으며, adjudicator receipt는 `reviewer_decision_visibility=false`를 요구한다. 최종 5개
manifest의 상태는 모두 `VERIFIED_BLIND_PROVENANCE`다.

| 검수 세트 | final decision SHA-256 | dual-review manifest SHA-256 |
| --- | --- | --- |
| 주 학습 NEWS | `426611d2…4c828` | `c1f25aaf…203d3` |
| 보조 학습 NEWS | `3d945076…956d` | `91136273…ac3` |
| 보조 학습 DISCLOSURE | `9ac5b087…40a7` | `dc92f5e8…803` |
| 개발 NEWS | `9170e76e…148e3` | `4dc88be3…aa50` |
| 개발 DISCLOSURE | `9ff970c0…b3da9` | `cb7fa0a3…8b8d` |

승격 후 실제 trainer partition은 TRAIN 32,907, CHECKPOINT 911, CALIBRATION 455,
SELECTION 461행이다. 6개 partition의 15개 쌍에 대해 provenance-group overlap은 모두 0이며,
NEWS·DISCLOSURE confirmatory reservation 600건씩은 행 수와 SHA-256이 변하지 않았다.

## 역사적 파일

| review packet | 행 | SHA-256 | dual decision | 행 | SHA-256 |
| --- | ---: | --- | --- | ---: | --- |
| `train_review.jsonl` | 600 | `af82d375b3566e914d20c6c40064f8a79ce373ad9db9c1cd5ba9b1b17e10647d` | `train_codex_decisions_dual.jsonl` | 600 | `f35ec2b06fa8c5eaa8064dba05a9acf79901bdf418bd50d7e47327eafe5c86d1` |
| `development_review.jsonl` | 450 | `62eaf5a2730ab3381b1b943ce75bd1cb3932b303b78d67b9f5974b6fce417bfa` | `development_codex_decisions_dual.jsonl` | 450 | `b454d5e8d10d1978917d88ccf3730ecf7785326589cd030c871159e3b8b90fa4` |
| `disclosure_development_review.jsonl` | 450 | `c09d712e575182120e1be36bfcd2e659a10311e51374b0159bfc85699728d171` | `disclosure_development_codex_decisions_dual.jsonl` | 450 | `a57cd1b8ad4690fbb26edc71746507aa7fb91a09ff6dac65c5ab6b59bef4eb61` |
| `prevalence_sealed_test_review.jsonl` | 600 | `2411b503eb4ba7fccae6c3995ce68e750433d3cf15846fc6fb578ab583ca042e` | `prevalence_aux_training_codex_decisions_dual.jsonl` | 600 | `5c0a903f476db9320719d9b87fde6620ca36231db0e18fb13b35c1d909d58f90` |
| `disclosure_prevalence_sealed_test_review.jsonl` | 600 | `be82dfccb5dc44204052a705a3cd0bbb1ff41d87c7cc8632624c6923f768852e` | `disclosure_prevalence_sealed_test_codex_decisions_dual.jsonl` | 600 | `a72b4e014fe7fedd8e1b2af6398ba4bf49102860e041d1ff9a4f447b4a01f2ba` |

이 표의 해시는 감사 시점의 상태를 식별하기 위한 것이며 receipt를 대체하지 않는다.

## 적용한 재검수 절차

1. review packet을 현재 byte 단위로 고정하고, 재검수 전에 candidate·teacher·시장 반응 필드가 없는지 재귀 검사한다.
2. reviewer마다 새 Codex run과 새 context를 생성하고, 오직 packet·코드북·`k-fnspid-sentiment-review-prompt/v1`만 제공한다.
3. 각 reviewer가 판정을 완료한 즉시 `scripts/k_fnspid_sentiment_review_provenance.py`로 receipt를 생성한다.
4. part decision은 receipt와 함께 `merge_k_fnspid_sentiment_decisions.py`로 병합해 stage manifest를 생성한다.
5. 두 stage의 reviewer·run·context ID 전역 고유성을 확인한 뒤 불일치 packet만 생성한다.
6. adjudicator를 또 다른 새 run·context에서 실행하고 receipt를 남긴다.
7. dual merge manifest와 전체 산출물을 다시 검증한 뒤에만 Gold 승격을 실행한다.
8. 파일·receipt·manifest를 원격 Git 잠금 커밋에 포함하고, 그 커밋 이후에만 확증 평가를 1회 실행한다. 이 마지막 원격 잠금·확증 평가는 아직 수행 전이다.

AI receipt는 절차적 분리를 감사 가능하게 할 뿐, 사람 금융전문가 다중 주석이나 외적 타당성을 대체하지 않는다.
