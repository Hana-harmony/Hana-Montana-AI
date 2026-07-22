# Hana Montana AI(KF-DeBERTa + K-FNSPID) Model Card

## 모델 개요

Hana Montana AI(KF-DeBERTa + K-FNSPID)는 한국 뉴스·공시를 종목 인텔리전스로 변환하는 복합 모델이다. 단일 신경망 이름이 아니라 다음 검증된 구성의 서비스 표기명이다.

- 금융 감성: K-FNSPID로 학습한 target-aware KF-DeBERTa LoRA 후보와 잠금·확증·승격 절차
- 의미 중요도·이벤트: 공시 약지도 Validation 선택 Logistic Regression과 제한적 존속위험 정책
- 시장영향 등급: K-FNSPID v4로 각각 학습한 뉴스·공시 KF-DeBERTa LoRA 전문가
- 종목 연결: 한국 종목 master·alias 문맥 링커
- 요약: What/Why/Impact 검증 규칙

## 의도한 사용

- 해외 증권사·파트너의 한국 시장 뉴스·공시 피드
- 보유·관심종목 이벤트 우선순위
- 금융 감성·시장반응 중요도 보조 분류
- 분석 근거, confidence, model version이 필요한 내부 API

자동 주문, 수익 보장, 투자 자문, 인과효과 판정, 법적 공시 심사에 단독 사용하지 않는다.

## 입력과 출력

### 입력

- `source_type`: `NEWS` 또는 `DISCLOSURE`
- 제목, snippet, 선택적 전문
- 선택적 후보 종목 universe

### 출력

- 대표/관련 종목
- 이벤트 다중 라벨
- 감성 `NEGATIVE/NEUTRAL/POSITIVE`
- 의미 중요도 `LOW/MEDIUM/HIGH/CRITICAL`
- 독립 시장영향 등급·점수·confidence
- What/Why/Impact 요약
- confidence, 중복·cluster key, 복합 model version

## 감성 모델

### 학습 데이터

| 역할 | 데이터 | 건수 |
| --- | --- | ---: |
| 주 학습 Gold | K-FNSPID 감성 Gold | 596 |
| 뉴스 보조 Gold | 최초 합의 571건, 불일치 재심 확정 27건, 미해결 제외 2건 | 598 |
| 공시 보조 Gold | 최초 합의 554건, 불일치 재심 확정 46건 | 600 |
| Silver | 뉴스 30,000건 + 공시 2,700건 | 32,700 |
| 개발 Gold | 뉴스 448건 + 공시 447건 | 895 |
| 실제 trainer 준비 학습행 | 중복·충돌·역할 제한 적용 후 | 32,907 |

5개 packet 전체를 두 개의 독립 AI review context와 별도 adjudicator context에서 다시 검수했다. 주 학습 뉴스, 보조 뉴스, 보조 공시, 개발 뉴스, 개발 공시의 미해결 제외 건수는 각각 4, 2, 0, 2, 3건이다. 모든 결정은 packet·코드북·프롬프트·모델 버전·run/context와 blindness commitment를 묶은 receipt로 검증한다. 596+598+600 Gold와 32,700 Silver의 단순 합이 준비 학습행과 다른 이유는 정규화 중복·충돌, 출처별 적격성, holdout 보호와 표본 가중치를 실제 trainer가 적용하기 때문이다. 공시 약한 중요도 라벨은 감성 Gold로 전용하지 않는다.

### 구조와 최적화

- base model: `kakaobank/kf-deberta-base`
- 고정 revision: `363b171d71443b0874b0bf9cea053eb5b1650633`
- domain-adaptive pretraining: 보호 자료와 fuzzy 연결요소를 제거한 K-FNSPID v4
  1,118,291건으로 sparse MLM LoRA DAPT를 수행하고 안전 병합한 FP32 base를 후보 입력으로 사용
- supervised parameter-efficient tuning: 12개 encoder layer의 query/key/value/dense LoRA,
  rank 16, alpha 32, dropout 0.08
- 입력: 대상 종목 prefix와 본문 head-tail을 결합한 최대 256 token
- head: 공유 중립/방향 계층형 head와 NEWS·DISCLOSURE·PUBLIC residual head. residual은 정확한 0으로
  초기화하고 알려지지 않은 domain은 실패 처리
- 1단계: 32,907개 준비행에서 domain/task cell mass를 고정한 전체 LoRA+head 학습 2 epoch
- 2단계: receipt-bound Gold만 사용해 encoder를 동결하고 head를 4 epoch 정제
- 정규화: 서로 다른 dropout 경로의 양방향 KL을 사용하는 R-Drop
- 손실: source·task cell의 실제 sample-weight mass를 고정한 계층형 cross entropy v3
- target-swap: 공식 종목명뿐 아니라 종목코드와 모든 alias가 제거됐는지 검증한 반사실 표본만 허용
- 데이터 선택 seed: `20260715`; 모델 seed: `17`, `42`, `73`

개발 pool은 개발 적격 공개 Validation 932건과 receipt-bound 개발 Gold 895건으로 구성한다. 중복·보호 group 제거와 고정 group key 배정 결과는 Checkpoint 911건, Calibration 455건, Selection 461건이다. Checkpoint는 epoch/checkpoint 선택에만, Calibration은 domain별 temperature·중립 임계값 보정에만, Selection은 seed·최종 후보 선택에만 사용한다. 같은 원문·사건 group이 두 역할에 들어갈 수 없으며 공개 Test와 확증 Gold는 세 역할 어디에도 포함하지 않는다.

### DAPT 상태와 연결 계약

- inventory oracle v4·pack oracle v3는 서로 다른 검토 context에서 재현·승인되어 `LOCKED`다.
- prepared manifest SHA-256은 `09112ccd…59f5`, precision pilot report는
  `b467d997…04bf`다.
- FP32 pilot 고정 NLL은 `3.124770 → 3.111651`로 감소했다. BF16은 MPS memory-slope gate
  실패로 사용하지 않는다.
- 전체 3,908-update DAPT를 완료했다. validation NLL은 `3.119393 → 1.335785`, perplexity는
  `22.63 → 3.803`이며 최종 manifest SHA-256은 `50155de7…ef2a`다.
- supervised trainer는 DAPT artifact v2의 input·dependency·prepared·pilot·두 oracle·merged
  FP32 file hash·종료 validation NLL을 현재 source와 다시 대조해야만 DAPT base를 허용한다.
- DAPT의 supervised 성능 개선은 no-DAPT 3-seed paired 평가 전까지 주장하지 않는다.

### 공정 기준선

`snunlp/KR-FinBert-SC` 공정 기준선은 분류 head만 비교하는 고정 추론이 아니라 전체 parameter를 fine-tuning한다. 후보와 동일한 원천행, group split, 데이터 선택 seed, 모델 seed 17/42/73, epoch 수와 optimizer update 일정을 사용한다. 모델 구조에 맞는 learning rate와 trainable parameter 수만 다르며, 이 차이를 “동일 정규화”로 표현하지 않는다. 원본 KR-FinBERT-SC와 K-FNSPID 도입 전 서비스 모델은 별도 진단 기준선으로 유지한다.

제거 실험의 `FULL`은 같은 seed의 잠긴 후보 artifact를 참조군으로 사용한다. 후보 report·입력·분할·DAPT base·구조·hyperparameter·optimizer step·CPU roundtrip과 manifest의 byte·SHA-256을 다시 확인한 영수증이 있어야만 집계한다. artifact를 복사하거나 symlink로 가장하지 않으며 원본이 변조되면 실패한다. 후보의 실제 minibatch 순서는 보존하고 stable-order 제거군과 bitwise 동일한 실행 순서였다고 주장하지 않는다.

### 잠금 평가 상태

| 평가 | NEWS | DISCLOSURE | 해석 |
| --- | ---: | ---: | --- |
| 공개 재현 Test | 진단 전용 | 진단 전용 | 과거 반복 조회로 확증 주장 금지 |
| 새 확증 Gold 층화가중 Accuracy / Macro-F1 | 0.7503 / 0.5530 | 0.8646 / 0.6024 | 잠금 후 각 600건 단 1회 평가 |
| KR-FinBERT-SC 공정 full-FT 가중 Macro-F1 | 0.5771, 후보 -0.0241점 | 0.5647, 후보 +0.0376점 | 두 출처 모두 Holm 우월성 미확인 |
| 원본 KR-FinBERT-SC 가중 Macro-F1 | 0.4937, 후보 +0.0594점 | 0.6146, 후보 -0.0123점 | 두 출처 동시 우월성 미확인 |
| 최종 승격 | 미승격 | 미승격 | `KEEP_CURRENT_MODEL` |

비가중 표본 Macro-F1은 NEWS 0.6636, DISCLOSURE 0.6056이지만 이는 기술통계다. 사전 지정 1차 판정은 모집단 층화가중 Macro-F1과 FPC delete-one jackknife·Holm 보정을 사용한다. 그 결과 후보는 배포 gate를 통과하지 못했으며, 전역 SOTA나 두 출처 동시 개선을 주장하지 않는다.

### 사전 지정 통계분석계획

- 유의수준 0.05에서 `원본 KR-FinBERT-SC`, `K-FNSPID 도입 전 모델`, `공정 full-FT KR-FinBERT-SC` 각각에 대한 NEWS·DISCLOSURE 비교 6개를 하나의 Holm family로 보정한다.
- 확증 표본은 출처·감성 층별 단순무작위 비복원추출(SRSWOR)로 설계한다.
- 1차 분산 추정은 finite-population correction(FPC)을 포함한 paired stratified delete-one jackknife를 사용한다.
- 고정 seed `20260715`의 paired bootstrap 2,000회는 구간·민감도 분석에 사용한다.
- 가중 Macro-F1은 비선형 plug-in 추정량이므로 정확한 불편추정량이라고 주장하지 않는다. Holm 보정은 6개 p값의 family-wise error rate에 적용되며 개별 신뢰구간을 동시 신뢰구간으로 바꾸지 않는다.

## 공시 의미 중요도 모델

약지도 실공시 8,302건과 Gold 문장을 복제하지 않는 치명위험 템플릿 400건으로 제목, 제목+요약, 제목+요약+전문 뷰를 같은 시간 분할에서 학습한다. Gold는 선택에 사용하지 않고 2026 Validation macro F1과 Brier score로 제목+요약 뷰를 선택했다. 모델 단독 기본 Gold 600건은 accuracy 0.9850 / macro F1 0.9470 / CRITICAL F1 0.8163이다. 상장폐지·횡령/배임·감사의견거절·부도·회생·파산 안전 floor를 포함하면 기본 Gold 1.0000 / 1.0000, 학습·기본 Gold와 URL이 겹치지 않는 스트레스 Gold까지 합친 910건은 0.9989 / 0.9962다. 거래정지·불성실공시 단독은 코드북대로 HIGH다. 기본 Gold URL 401건은 학습 전에 제외해 post-filter 중복이 0이며, 시장영향은 의미 라벨과 confidence를 모두 변경하지 않는다. 전문 포함 ablation의 기본 Gold 0.9433 / 0.8699는 전문의 길이·보일러플레이트가 선형 모델을 악화시킴을 보여주므로 실제 전문은 데이터셋과 후속 장문 모델 연구에 보존한다.

## K-FNSPID 시장영향 모델

### 데이터

- K-FNSPID v4 문서 1,247,685건: 뉴스 524,696건, 공시 722,989건
- 문서–종목 관계 1,136,118건, 비혼입 시장영향 대표행 255,168건
- 파일 기반 시세 10,691,998행, 2,800종목
- 대표 분할: 뉴스 Train 99,826 / Validation 6,391 / Test 9,560, 공시 Train 119,146 / Validation 584 / Test 4,615
- 공시 실제 원문 연결 8,972건, 뉴스 실제 전문 연결 13,310건

### 입력 feature

- `[SOURCE=NEWS]` 또는 `[SOURCE=DISCLOSURE]`
- 제목 + snippet + 전문 + 대표 종목명
- 가격, 거래량, 미래 수익률은 입력하지 않는다.

### Transformer 목적함수

- class-balanced focal cross entropy + ordinal CDF MSE
- 공시 전문가는 gamma 1.0, ordinal weight 0.20, label smoothing 0.01, max length 128을 사용한다.
- 뉴스 전문가는 검증된 K-FNSPID adapter를 출처 전용으로 평가·승격한다.
- device batch 16, 공시 gradient accumulation 2, 유효 batch 32
- 공시 learning rate 5e-5, cosine scheduler, warmup 8%, weight decay 0.01
- LoRA r=16, alpha=32, dropout=0.1
- class-balanced loss의 소수 등급 과대 예측을 줄이기 위해 log class-prior 강도 0.00~2.00과 temperature 0.50~3.00을 Validation에서만 선택한다. raw·보정 지표를 모두 보존하고 서빙에 같은 값을 적용한다.

### 평가

공정한 TF-IDF 기준선은 각 출처 Train에만 적합한다. 뉴스 Test는 accuracy 0.4715 / macro F1 0.3484 / QWK 0.3421, 공시 Test는 0.3675 / 0.2677 / 0.1125다.

동일 K-FNSPID 시간 Test와 학습 절차를 적용한 KR-FinBERT-SC 비교에서 국내 뉴스 Macro-F1은 0.3506, 국내 공시는 0.3131이다. Hana Montana AI는 각각 0.3745와 0.3216으로 6.82%(+0.0239점), 2.72%(+0.0085점) 높다. 거래일 군집 bootstrap과 Holm 보정 결과 국내 뉴스만 우위 gate를 통과했다. 국내 공시는 Macro-F1 신뢰구간이 0을 포함하고 QWK가 0.1611에서 0.1550으로 낮아 우위를 주장하지 않는다. 이 결과는 동일 시간 Test의 명시적 비교군에 한정되며 전역 SOTA를 뜻하지 않는다.

<!-- K_FNSPID_FINAL_MODEL_METRICS -->

출처별 고정 시간 Test에서 뉴스 전문가는 9,560건 accuracy 0.5247 / macro F1 0.3745 / QWK 0.4754 / ECE 0.0182, 공시 전문가는 4,615건 0.4750 / 0.3216 / 0.1550 / 0.0441이다. 통합 14,175건은 기준선 0.4377 / 0.3210 / 0.2552에서 출처별 전문가 0.5085 / 0.3690 / 0.3975로 개선됐다. 거래일 cluster bootstrap 2,000회의 Macro-F1 차이 95% CI는 뉴스 [0.0120, 0.0409], 공시 [0.0264, 0.0806], 통합 [0.0351, 0.0608]이며 exact McNemar p=2.29e-55이다.

공시 Transformer는 seed 17/42/73을 같은 설정으로 반복하고 Validation에서 checkpoint·class-prior·temperature 보정과 배포 run을 선택한다. Test superiority는 행 단위 paired bootstrap과 거래일 cluster bootstrap 각 2,000회, exact McNemar, QWK, ECE, Brier score로 별도 판정하며 우월성 gate에는 더 보수적인 거래일 cluster 구간을 사용한다.

## 배포 gate

### 감성

- 데이터·학습 recipe·모델·통계분석계획의 원격 Git attestation 완료
- NEWS·DISCLOSURE 확증 Gold를 후보 잠금 뒤에 완성하고 one-shot 평가 receipt 생성
- 출처별 Accuracy·Macro-F1 절대 gate와 공정 full-FT 기준선 비회귀 gate 통과
- 6개 사전 지정 비교에 Holm 보정을 적용하고, 결과를 출처별로 분리 보고
- 공개 Test는 회귀 진단에만 사용하며 승격·통계 우위·SOTA 주장에 사용하지 않음

### 가격반응

- 뉴스: 시간 Test 5,000건 이상, macro F1 0.35 이상, QWK 0.30 이상, ECE 0.20 이하
- 공시: 시간 Test 500건 이상, macro F1 0.30 이상, QWK 0.08 이상, ECE 0.20 이하
- 각 출처 TF-IDF 기준선의 macro F1·QWK 이상이고 ECE가 악화되지 않아야 한다.

### artifact 무결성

- upstream KF-DeBERTa는 고정 revision의 공식 PyTorch weight SHA-256을 `weights_only=True`로 검증한 뒤 배포 과정에서 `safetensors`로 변환한다. 운영 로더는 변환된 `safetensors`만 활성화한다.
- scikit-learn artifact는 report SHA-256·크기를 역직렬화 전에 검증한다.
- report의 byte 크기·SHA-256과 실제 파일이 모두 일치해야 활성화
- 고정 base revision, remote code 비활성화
- gate나 hash 검증 실패 시 같은 출처의 적격 기준선만 사용한다. 공시 기준선은 독립 gate 미달이므로 공시 시장영향만 생략한다.

## 데이터와 라벨 안전성

- OpenDART·Naver 자격증명은 로컬 secret 파일에서만 읽고 report에 기록하지 않는다.
- 검수되지 않은 공시 전문 약한 중요도 라벨은 Gold URL을 제거한 뒤 의미 중요도 후보 학습에만 사용한다. 감성 학습과 Gold 평가 정답에는 사용하지 않는다.
- 공시 Gold와 전문 학습 URL 중복은 0건이다.
- 현재 파이프라인은 공개 Test와 확증 Gold를 threshold·전처리·checkpoint·보정·seed 선택에 사용하지 않는다. 공개 Test는 과거 버전에서 반복 사용했으므로 진단 결과로만 기록한다.
- 확증 후보 원문과 층별 표본 commitment는 라벨링 전에 동결한다. 학습 recipe와 잠금 커밋이 원격 저장소에서 검증되지 않으면 확증 라벨을 열거나 평가하지 않는다.
- 같은 종목·거래일 다중 사건은 가격반응 학습에서 제외한다.
- Parquet 6개뿐 아니라 raw/full-content/종목/시세/Gold 원천의 경로·byte·개별/복합 SHA-256이 모두 일치해야 재학습을 허용한다.

## 알려진 한계

- 가격반응 중요도는 의미 중요도·인과효과가 아니다.
- 전체 공시 대비 실제 전문 연결률은 1.24%다. 전문 8,972건은 보존하지만 시장영향 제목·snippet ablation이 더 강했던 결과를 숨기지 않는다.
- 일봉은 장중 즉시 반응을 분리하지 못한다.
- 공개 감성 Test의 과거 우위는 적응적 반복 조회 때문에 신규 후보의 독립 증거가 아니다.
- 5개 감성 Gold packet은 receipt-bound 이중검수와 불일치 재심을 거쳤지만 사람 금융전문가 주석이 아니며 외부 전문가 타당도를 입증하지 않는다.
- 개발 Gold는 2025년 6--12월, 보조 공시 Gold와 확증 후보는 2026년 4--7월에 집중된다. 확증 표본은 학습 표본과 문서 단위로 분리되지만 더 미래의 out-of-time 표본이 아니므로 장기 시간 일반화를 주장하지 않는다.
- seed 고정은 데이터·실험 절차를 재현하지만 Apple MPS와 다른 accelerator 사이의 bitwise 동일 출력을 보장하지 않는다. 실제 device, global step과 runtime을 report에 기록한다.
- 동일 K-FNSPID 라벨 정의의 외부 공인 leaderboard가 없다.

## 모니터링

- source별 라벨·confidence·fallback 비율
- 운영 Gold 회귀
- Test와 운영 분포별 ECE
- 공시/뉴스 원문 가용률
- artifact hash·base revision 변화
- 종목 linker coverage와 request stock mismatch

## 관련 산출물

- [K-FNSPID v4 Datasheet](../datasets/k-fnspid-v4-datasheet.md)
- [한국어 기술 근거본](../paper/k-fnspid-v4-paper-draft.md)
- [ACL Rolling Review 익명 심사 원고](../paper/acl/k-fnspid-v4-arr-review.tex)
- [저자 공개 영문 원고](../paper/acl/k-fnspid-v4-author-preprint.tex)
- [최성현 저자 한글 논문](../paper/acl/k-fnspid-v4-ko.tex)
- [저자·소속 메타데이터](../paper/acl/author-metadata.json)
- [제출·책임 있는 NLP 체크리스트](../paper/acl/responsible-nlp-checklist.md)
- [제출 manifest](../paper/acl/submission-manifest.json)
- `reports/korean-finance-sentiment-benchmark.json`
- `reports/disclosure-importance-training-report.json`
- `reports/disclosure-importance-research-evaluation.json`
- `reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json`
- `reports/k-fnspid-research-evaluation.json`
