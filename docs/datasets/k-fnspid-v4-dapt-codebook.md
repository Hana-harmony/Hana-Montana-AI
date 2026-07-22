# K-FNSPID v4 KF-DeBERTa DAPT 코드북

## 현재 상태

이 문서는 `kakaobank/kf-deberta-base`의 고정 revision
`363b171d71443b0874b0bf9cea053eb5b1650633`을 K-FNSPID v4 뉴스·공시에 적응시키는
masked language modeling 절차를 고정한다. 2026-07-17 현재 Arrow boolean zero-copy loader
결함을 수정한 semantic recipe `4d62557b…e1c7c4`로 AllPairs fuzzy v3 전체 inventory와 pack
oracle을 다시 산출하고 각각 독립 검토해 잠갔다. 새 prepared corpus를 전량 재생성·검증했고,
FP32/BF16 1,024-pack pilot을 거쳐 FP32를 선택한 뒤 3,908-update 전체 학습을 실행 중이다.

| 단계 | source 상태 | 실행 여부 |
| --- | --- | --- |
| inventory oracle | `LOCKED` | derivation v4와 독립 review v4 승인 |
| pack oracle | `LOCKED` | derivation v3와 독립 review v3 승인 |
| prepared corpus | `VERIFIED` | manifest SHA-256 `09112ccd…59f5` |
| precision pilot | `PRECISION_SELECTED` | FP32 선택, report SHA-256 `b467d997…04bf` |
| DAPT 학습 | `RUNNING` | 3,908 update, 128 update 안전 checkpoint |

수정 전 receipt와 prepared corpus는 superseded 기록으로만 보존한다. 현재 실행은 inventory
derivation `ee3a65f5…6ba`, review `3a587027…521f`, pack derivation
`106fb01f…b67`, review `fd3a51e4…ff9`가 현재 recipe와 일치할 때만 허용된다.

## 시간 경계와 보호 자료

- `published_at_kst < 2026-04-01T00:00:00+09:00`과
  `effective_trade_date < 2026-04-01`을 동시에 만족해야 학습 후보가 된다.
- 뉴스·공시 development Gold와 라벨이 봉인된 confirmatory reservation을 보호 seed로 사용한다.
- reservation은 고정 partition과 `NEEDS_BLIND_REVIEW`를 유지해야 한다.
  `final_sentiment`, reviewer, review time, review note는 빈 값이어야 하며, weak label, sampling
  stratum, 확률·가중치 필드가 노출되면 즉시 실패한다.
- 공개 Test와 confirmatory 감성 정답은 읽지 않는다.
- 입력 Parquet, dataset manifest, 보호 파일, base model 파일은 고정 SHA-256과 대조한다. hash
  계산 전·후의 device, inode, size, mtime, ctime이 바뀌면 실패한다.
- 전체 inventory의 네 번 Parquet 순회는 하나의 고정 file descriptor를 재사용한다. 마지막
  순회 뒤 descriptor와 현재 경로의 identity를 다시 비교해 경로 교체와 실행 중 수정을 차단한다.

## exact·identity 연결요소

전체 corpus에서 다음 typed key 중 하나라도 공유하는 문서를 union-find로 연결한다. 전체 범위
계산은 cutoff 밖의 동일 문서나 동일 사건을 매개로 한 평가 오염을 보수적으로 제거하기 위한
것이며, cutoff 밖 텍스트를 MLM 입력으로 사용한다는 뜻은 아니다.

1. `document_id`
2. canonical URL
3. `content_hash`
4. `event_cluster_id`
5. 정보량 gate를 통과한 normalized exact-text hash

정규화 exact text에는 NFKC, case-folding, 단일 공백 정규화를 적용한다. 영숫자 32자 이상,
서로 다른 영숫자 12자 이상이어야 한다. 전문 영숫자가 128자 미만이면 제목과 요약이 모두
필요하고, 한 필드가 다른 필드를 포함하면서 길이 차이가 24자 이하인 반복 제목·요약은
보일러플레이트로 제외한다.

## AllPairs fuzzy v3 그래프

### 범위와 정규화

fuzzy 그래프에는 다음 문서만 포함한다.

- dual-cutoff 내부 문서
- cutoff와 무관하게 exact·identity 보호 성분에 속한 문서
- 보호 seed의 가상 signature

따라서 cutoff 이후의 비보호 문서는 fuzzy document-frequency, 후보 생성, 분할 구조에 영향을
주지 않는다. 뉴스와 공시는 분리하지 않고 같은 전역 그래프에서 비교한다. 정보량 gate를 통과한
제목·요약을 NFKC·case-fold·공백 정규화한 뒤 512자 head-tail로 제한하고, 고유 4-character
shingle set을 만든다. 텍스트 32자 미만 또는 고유 shingle 24개 미만은 fuzzy 대상에서 제외한다.

### 완전 후보 생성과 exact 검증

전역 shingle 순서는 document frequency 오름차순, 동률이면 UTF-8 byte 오름차순이다. Dice
임계값 0.92는 Jaccard 임계값 `23/27`과 같다. shingle 수가 `n`인 집합은 다음 길이의 prefix를
색인한다.

```text
n - ceil(23n / 27) + 1
```

후보 길이 `m`은 `23n/27 <= m <= 27n/23`을 만족해야 한다. 최종 판정은 부동소수점이 아닌
정렬 shingle의 exact 교집합과 다음 정수 부등식으로 수행한다.

```text
20000 * intersection >= 9200 * (left_size + right_size)
```

후보를 임의로 자르지 않는다. 한 문서의 후보가 100,000건을 초과하면 결과를 축약하지 않고
전체 derivation을 실패시킨다. 현재 test는 작은 합성 집합에서 prefix filter 결과와 brute-force
Dice 결과의 완전 일치, cross-source edge, 보호 seed를 거치는 전이 폐쇄, scope mask,
후보 한도 fail-closed를 검증한다. 이는 수학적·구현 속성 검증이지 전체 corpus 성능 측정 결과는
아니다.

### purge와 split 순서

exact·identity edge와 모든 검증된 fuzzy edge를 먼저 union한다. 이후 보호 seed와 직접 또는
전이적으로 연결된 root 전체를 제거하고, 남은 component의 최소 salted typed-key digest로 1%
Validation을 결정한다. 이 순서 때문에 하나의 fuzzy component가 Train과 Validation으로
갈라지지 않는다.

전체 derivation은 Parquet를 네 차례 순회한다. exact graph 구성, fuzzy scope와 전역 frequency
산출, AllPairs graph 구성, 최종 purge·split 집계 순서다. 1,247,685건 실측은 389.75초,
최대 RSS 2.61 GiB였다. 전체 보호 성분 2,826건 중 dual-cutoff 내 NEWS 709건과
DISCLOSURE 782건을 purge했다. 남은 eligible NEWS 419,260건과 DISCLOSURE 699,031건은
Train 1,107,212건과 Validation 11,079건으로 나뉘며, Train–Validation duplicate/fuzzy overlap은 0이다.

loader 수정 후 최종 v4 source recipe로 다시 수행한 inventory 실측은 409.261초, 최대 RSS
2,667,151,360 bytes였다. 이전 독립 재현과 count·hash·candidate SHA-256
`24e678aee83dcde4b3ad7d74d5d22a14b6198ed957c80b27eb007c9d6922240d`가 모두 일치했다.

## inventory oracle 상태 전이

inventory oracle은 다음 단방향 절차로 고정한다.

1. `PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3`: read-only derivation으로 새 count·hash와
   fuzzy 성능 계측을 no-clobber report에 기록한다. prepared·pack·pilot·model artifact는
   생성하지 않는다.
2. `DERIVED_PENDING_INDEPENDENT_REVIEW`: derivation actor와 다른 reviewer가 입력·recipe·
   runtime fingerprint, AllPairs 완전성, brute-force property test, cross-source 전이 폐쇄,
   zero-overlap, 성능·메모리 자료를 검토한다. self-review는 거부한다.
3. `LOCKED`: 검토된 `EXPECTED`, `EXPECTED_HASHES`, review receipt SHA-256을 source의 mutable
   oracle block에 반영한다. 같은 변경에서 pack 상태를
   `PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3`로 전환한다.

```bash
uv run python scripts/train_k_fnspid_dapt.py \
  --derive-inventory-oracle \
  --actor-id codex:dapt-inventory-derivation

uv run python scripts/train_k_fnspid_dapt.py \
  --record-inventory-oracle-review \
  --reviewer-id codex:dapt-inventory-independent-review \
  --review-note "AllPairs 완전성, 전이 폐쇄, zero-overlap, 성능 계측을 독립 검토함"
```

report와 receipt가 생겨도 자동으로 `LOCKED`가 되지 않는다. source lock PR에서 후보 값,
receipt hash, oracle 값 블록을 제외한 semantic recipe hash가 유지되는지 다시 확인한다.

## packing·masking·attention 계약

- 최대 길이 256, singleton `[CLS]`를 제외한 pack 용량은 255 token이다.
- Train과 Validation, NEWS와 DISCLOSURE를 같은 pack에 섞지 않고 source별 best-fit decreasing을
  적용한다.
- source·field marker는 구조 위치에서만 masking에서 제외한다. 본문에 자연스럽게 나타난 같은
  token ID는 일반 MLM 후보다.
- 특수 token과 tokenizer의 `[unusedN]`은 random replacement 후보에서 제외한다.
- 각 문서 segment와 singleton `[CLS]`는 서로 다른 block으로 구성한다. 3차원 block-diagonal
  attention mask로 pack 내부 문서 간 attention을 금지한다.
- base config의 `relative_attention=True`, `position_biased_input=False`, `pos_att_type=[p2c,c2p]`,
  convolution 없음 조건을 검사한다. position ID는 pack offset을 사용하지만, block 내부 상대
  거리는 offset 이동에 불변이다. 실제 축소 DeBERTa test로 block 격리와 offset 불변성을 확인한다.
- retained lineage에는 document ID, split, source, pack ID, offset, length, segment SHA-256을
  기록하고 pack·mask·lineage를 다시 읽어 semantic hash를 재계산한다.

## pack oracle 상태 전이

inventory oracle이 `LOCKED`된 뒤에만 pack derivation을 허용한다.

최종 pack은 Train NEWS 147,532개·공시 102,526개, Validation NEWS 1,457개·공시
1,050개이며 non-padding token 62,468,526개를 포함한다. unmasked pack, lineage, Train epoch-0
mask, 고정 Validation mask의 네 SHA-256과 candidate SHA-256
`99d6070784fc9ccc141bab54d35100aae55a9ab24639e02e64684fd45dc689b4`는 최초 산출,
독립 전체 재현, loader 수정 후 최종 v3 재산출에서 동일했다. 전체 schedule은 3,908 update와
196 warmup update로 잠갔다.

1. `PENDING_REDERIVATION_AFTER_ALLPAIRS_FUZZY_V3`: 임시 pack을 만들고 별도 재독해한 뒤
   scratch를 삭제한다. count, pack·mask·lineage hash, update·warmup 후보만 report에 남긴다.
2. `DERIVED_PENDING_INDEPENDENT_REVIEW`: 다른 reviewer가 결정적 count·hash, semantic reread,
   schedule 산술, 비승격·비학습 사실을 검토한다.
3. `LOCKED`: 검토된 count·hash, `TOTAL_UPDATES`, `WARMUP_UPDATES`, receipt SHA-256을 source에
   반영한다. inventory와 pack 두 lock receipt가 현재 입력·recipe에 연결될 때만
   prepare·pilot·train을 허용한다.

```bash
uv run python scripts/train_k_fnspid_dapt.py \
  --derive-pack-oracle \
  --actor-id codex:dapt-pack-derivation

uv run python scripts/train_k_fnspid_dapt.py \
  --record-pack-oracle-review \
  --reviewer-id codex:dapt-pack-independent-review \
  --review-note "pack, mask, lineage, schedule과 비승격 계약을 독립 검토함"
```

## 학습과 artifact 안전 계약

- KF-DeBERTa base, embedding, MLM head를 동결하고 12개 layer의 query/value projection에
  LoRA rank 16, alpha 32, dropout 0.05를 적용한다.
- FP16은 금지한다. 동일 초기 adapter의 FP32/BF16 1,024-pack pilot을 원시 측정값에서
  재계산하고 gate를 통과한 precision만 선택한다.
- 현재 pilot에서 FP32 고정 NLL은 `3.124770`에서 `3.111651`로 감소했다. BF16도 손실은
  감소했지만 MPS memory-slope gate를 통과하지 못했으므로 전체 학습에는 FP32만 사용한다.
- 128 update마다 model, optimizer, scheduler, RNG를 safetensors와 strict JSON으로 원자 저장한다.
- 생성·resume artifact에서 pickle과 `.bin`, symlink, overwrite를 금지한다. hash가 고정된 base
  `.bin`은 `weights_only=True`로만 읽는다.
- 최종 adapter와 선택적 `merged_fp32`를 fsync, no-clobber rename, publish 후 hash 재검증한다.
- prepared manifest v2와 final artifact manifest v2에는 inventory derivation report, 독립 review
  receipt, 후보 digest를 포함한 `inventory_oracle` lock record와 pack lock record를 함께 기록한다.

두 oracle이 현재 source와 receipt에 고정됐는지는 다음 명령으로 fail-close 검증한다.

```bash
uv run python scripts/train_k_fnspid_dapt.py --validate-only
```

DAPT의 downstream 감성 성능 향상은 no-DAPT와의 사전 고정 paired multi-seed 평가가 끝나기
전까지 주장하지 않는다.
