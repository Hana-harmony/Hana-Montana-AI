# K-FNSPID: 시간 경계 누수를 통제한 한국 뉴스·공시 데이터와 대상 종목 금융 감성평가

> 이 문서는 실험 설계와 산출물 추적용 연구 기록이다. 학술 문장과 국내 학회 형식을 적용한 한글 원고의 기준본은 `docs/paper/acl/k-fnspid-v4-ko.tex`, `output/pdf/k-fnspid-v4-ko.pdf`와 `output/docx/k-fnspid-kiise-ko.docx`다. 공개 모델명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`다.

> 검수 정정(2026-07-22): 실행 receipt가 없던 기존 라벨은 `LEGACY_UNVERIFIED`로 보존하고 receipt를 소급 생성하지 않았다. 5개 전체 학습·개발 packet과 잠금 후 확증 NEWS·DISCLOSURE 각 600건을 예측·시장 비노출 context에서 이중검수하고 별도 adjudicator가 불일치를 재심했다. 학습 Gold 1,794건과 개발 Gold 895건은 `VERIFIED_BLIND_PROVENANCE`이며 미해결 11건은 제외했다. 후보 잠금 뒤 one-shot 확증평가를 완료했으나 배포 판정은 `KEEP_CURRENT_MODEL`이다.

## 초록

본 연구는 Naver 뉴스 524,696건, OpenDART 공시 722,989건과 한국 상장종목 일별 시세 10,691,998행을 연결한 K-FNSPID를 제시한다. 동결 데이터셋은 1,247,685개 문서, 1,136,118개 문서–종목 관계, 715,015개 시장영향 행과 255,168개 비혼입 사건 대표행으로 구성된다. 본 연구는 이 자원을 이용해 대상 종목을 명시적으로 조건화하는 `Hana Montana AI(KF-DeBERTa + K-FNSPID)` 감성분류기를 설계하고, 주 학습 Gold 596건, 뉴스 보조 Gold 598건, 공시 보조 Gold 600건과 Silver 32,700건을 결합한다. 보호 연결요소를 제거한 문서 1,118,291건으로 KF-DeBERTa DAPT를 수행하고, 감독학습에서는 all-12 rank-16 LoRA, 공유·출처 residual 계층형 head, R-Drop, target-aware head-tail 입력, 고정 domain×task cell-mass 손실과 alias-safe target-swap을 사용한다. 개발 자료는 group-disjoint Checkpoint/Calibration/Selection으로 분리하고 데이터 선택 seed `20260715`와 모델 seed `17/42/73`을 구분한다. 후보 잠금 뒤 NEWS·DISCLOSURE 각 600건을 one-shot 평가한 층화가중 Accuracy/Macro-F1은 0.7503/0.5530, 0.8646/0.6024였다. 두 출처에서 공정 기준선과 원본 KR-FinBERT-SC에 대한 사전 지정 우월성·절대 성능 gate를 모두 충족하지 못해 후보를 승격하지 않았다. 본 연구는 전역 SOTA나 장기 시간 일반화를 주장하지 않는다.

## 1. 연구 질문

1. 한국 뉴스·공시와 일별 시세를 파일 기반으로 재현 가능하게 연결할 수 있는가?
2. 발표 세션, 시간 embargo, 사건 cluster, 동일 종목·거래일 다중 사건 제외가 미래 누수를 줄이는가?
3. 금융 도메인 Transformer와 순서형 목적함수가 강한 TF-IDF 기준선보다 미래 기간 시장충격 분류를 개선하는가?
4. 잠긴 one-shot 확증평가에서 target-aware 후보가 명시된 세 기준선을 NEWS와 DISCLOSURE 각각에서 개선하는가?

## 2. 관련 연구

FNSPID는 S&P 500 기업의 뉴스와 시세를 장기간 연결한 데이터 자원으로, 문서–기업–가격 관계와 시간축 배포 설계의 비교 대상으로 사용한다 [1]. KRX Bench와 FINKRX는 한국 금융 지식·질의응답 평가와 공개 instruction data를 제공한다 [2, 3]. 두 벤치마크는 문서별 target-aware 감성 또는 사후 시장반응과 정답 정의가 다르므로 성능 수치의 직접 기준선으로 사용하지 않는다.

KF-DeBERTa는 한국 금융 말뭉치에서 사전학습한 표현 모델이며 본 연구의 encoder로 사용한다 [4]. KR-FinBERT-SC는 한국 금융 뉴스와 애널리스트 보고서로 도메인 적응한 감성분류기로, 고정 추론 기준선과 동일 자료 full fine-tuning 기준선을 모두 구성한다 [5]. KorFinASC는 사람 주석 한국어 금융 aspect-level 감성 표본 12,613건을 제공한다 [14]. 확인한 공개 자료 중 한국어 target-aware 감성에 가장 가깝지만 OpenDART 공시와 K-FNSPID의 출처별·종목연결 확증표본을 포함하지 않으므로 교차 데이터셋 점수를 leaderboard 비교로 해석하지 않는다. FinEntity는 한 문장 안의 여러 금융 주체가 서로 다른 감성을 가질 수 있음을 보이고 기업 단위 감성 주석을 제공한다 [6]. EFSA는 기업·산업·사건·감성을 함께 추출하는 사건 단위 금융 감성 과제를 제안한다 [7]. 이들 연구는 target-aware 입력과 대상 종목별 평가 설계의 근거로 활용하되 언어·라벨·평가셋이 달라 직접 점수 비교에서는 제외한다.

LoRA는 적은 수의 저랭크 parameter로 사전학습 모델을 적응시키는 방법을 제시한다 [8]. R-Drop은 동일 입력의 두 dropout 경로 사이 양방향 KL 일관성으로 fine-tuning을 정규화한다 [9]. Effective-number class balancing은 원시 빈도 대신 표본의 한계 기여가 감소하는 유효 표본량으로 불균형 손실을 보정한다 [10]. 각 방법은 후보 구조의 구성요소로 사용되며, 개별 기법의 단독 효과는 잠금 전 ablation에서만 판단한다.

금융 감성의 시간 분포 이동 연구는 무작위 분할 성능이 미래 배포 성능을 과대평가할 수 있음을 보고한다 [11]. Holm의 순차적 기각 절차는 여러 사전 지정 가설의 family-wise error rate를 통제한다 [12]. 본 연구는 이 두 결과를 시간·group 분리와 6개 확증 가설의 다중비교 보정에 각각 적용한다.

| 자원 | 주된 과제 | 공개 규모 | 본 연구와의 직접 비교 가능성 |
| --- | --- | ---: | --- |
| FNSPID | 미국 뉴스–주가 시계열 연결 | 뉴스 1,570만, 시세 2,970만 | 데이터 설계·규모만 비교 가능 |
| KRX-Bench-POC | 한·미·일 기업 금융 QA | 질문 1,002 | 과제가 달라 성능 비교 불가 |
| FINKRX | 한국 금융 LLM QA·주가 방향 지식 평가 | 공개 instruction 8만, 비공개 benchmark 1,119회 제출 | 과제·평가셋이 달라 성능 비교 불가 |
| MultiFinBen | 5개 언어·다중양식 금융 추론 | 전문가 주석 텍스트·이미지·음성 | 후속 확장 참고, 감성 점수 비교 불가 |
| KF-DeBERTa | 한국 금융 PLM | 금융 downstream 7종 | base encoder와 공개 벤치마크 참고 |
| KorFinASC | 한국 금융 aspect-level 감성 | 사람 주석 12,613건 | 가장 가까운 공개 관련 자료, 평가셋이 달라 수치 비교 불가 |
| FinEntity·EFSA | entity/event-level 금융 감성 | 영문·중문 금융 뉴스 | target-aware 설계 참고, 수치 비교 불가 |
| KR-FinBERT-SC | 한국 금융 감성 | 원본 고정 추론 + 동일 자료 full fine-tuning | 잠긴 동일 확증표본에서 직접 비교 |
| K-FNSPID | 한국 뉴스·공시–주가 연결 | 문서 1,247,685, 시세 10,691,998 | 동일 Test에서 자체 기준선과 비교 |

이 표의 자원 간 규모 차이는 품질 순위를 뜻하지 않는다. 과제와 라벨이 다른 벤치마크의 점수를 합치지 않으며, 감성은 잠긴 동일 확증표본의 이름이 명시된 기준선 비교만 허용한다.

## 3. 데이터

### 3.1 규모

| 항목 | K-FNSPID |
| --- | ---: |
| 전체 문서 | 1,247,685 |
| 뉴스 | 524,696 |
| 공시 | 722,989 |
| 공시 실제 원문 | 8,972 |
| 문서–종목 관계 | 1,136,118 |
| 시장영향 | 715,015 |
| 비혼입 대표행 | 255,168 |
| 시세 | 10,691,998 |
| 시세 종목 | 2,800 |
| 주 학습 감성 Gold | 596 |
| 뉴스 보조 감성 Gold | 598 |
| 공시 보조 감성 Gold | 600 |
| 감성 Silver | 32,700 |
| 감성 개발 Gold | 895 |
| 감성 준비 학습행 | 32,907 |
| 기본 의미 중요도 Gold | 600 |
| 공시 stress 포함 의미 Gold | 910 |

세부 원천, schema, 편향, 삭제·버전 정책은 [K-FNSPID Datasheet](../datasets/k-fnspid-v4-datasheet.md)에 고정한다.

### 3.2 공시 원문 확장

OpenDART 원문 API를 전체 pagination 목록과 연결하고, 32MB 응답 상한, timeout, 재시도, ZIP 검증과 DART 상태 분류를 적용해 전문 학습셋의 공시 원문 8,976건을 확보했다. 이 중 K-FNSPID raw 문서 URL과 연결되는 OpenDART 원문은 8,972건으로, 전체 배포 공시 722,989건의 1.24%다. 최종 추가 수집 대상 5,082건 중 4,976건을 저장했으며, 실패 106건은 본문 부족 51건, DART 상태 013 1건, 상태 014 37건, 공개 뷰어 metadata 부재 17건으로 보존했다.

수집 원문 라벨은 Gold가 아니며 `RULE_WEAK_SUPERVISION_V2`와 `UNREVIEWED_WEAK_LABEL`로 표시한다. Gold URL을 제거한 실제 공시 8,302건은 의미 중요도 후보의 supervised 학습에만 사용하고 감성 학습·평가 정답에는 사용하지 않는다. 기존의 모든 공시 HIGH 강제 규칙은 정기/행정 LOW, 지배구조 MEDIUM, 계약·자본·실적 HIGH, 치명 위험 CRITICAL 코드북으로 교체했다.

### 3.3 감성 학습·개발 자료

| 자료 | 건수 | 역할 |
| --- | ---: | --- |
| 주 학습 Gold | 596 | 감독 학습 |
| 뉴스 보조 Gold | 598 | 감독 학습 |
| 공시 보조 Gold | 600 | 감독 학습 |
| 뉴스 Silver | 30,000 | 가중 보조 학습 |
| 공시 Silver | 2,700 | 가중 보조 학습 |
| 개발 Gold | 895 | 뉴스 448 + 공시 447 |
| trainer 준비 학습행 | 32,907 | 적격성·중복·충돌 필터 이후 실제 입력 |

주 학습 뉴스, 보조 뉴스, 보조 공시, 개발 뉴스, 개발 공시 후보는 각각 600, 600, 600, 450, 450건이다. 최초 합의는 574, 571, 554, 434, 444건이고, 별도 adjudicator가 22, 27, 46, 14, 3건을 확정했다. 미해결 4, 2, 0, 2, 3건을 제외해 최종 Gold는 596, 598, 600, 448, 447건이다. 주 학습 Gold와 두 보조 Gold, Silver의 단순 합은 34,494건이지만 실제 trainer는 정규화 중복·충돌, 출처별 적격성, holdout 보호와 표본 가중치를 적용해 32,907개 학습행을 준비한다.

주석자는 공개 코드북, 원문, 대상 종목과 근거 필드를 대조한 Codex 기반 판정자다. 독립 검수와 재심은 단일 판정보다 절차적 오류 통제를 강화하지만 사람 금융전문가 간 일치도나 외부 타당도를 제공하지 않는다. 감성 확증 Gold는 후보 잠금 뒤에만 완성하며 본 원고 작성 시점의 라벨과 결과는 열지 않는다.

### 3.4 의미 중요도 Gold

공시 의미 중요도 Gold는 기본 600건과 stress 310건으로 구성된다. 기본 분포는 LOW 250, MEDIUM 34, HIGH 287, CRITICAL 29이며 공시 전문 학습 URL과 중복되지 않는다. 감성용 보조 Gold와 의미 중요도 Gold는 목적·정답 정의가 다르므로 같은 표본 수로 합산하거나 같은 성능 지표로 비교하지 않는다.

## 4. 시장반응 라벨

문서의 유효 거래일을 (t), 수정종가를 (P), 동일 시장 평균 수익률을 (r_m)이라 할 때 1·3·5일 종목 복리수익률에서 시장 복리수익률을 차감한다. 과거 60거래일 로그 거래량 z-score와 과거 20거래일 대비 장중 변동성 충격을 추가한다.

materiality score는 가중치가 0.50인 1일 절대 초과수익률, 0.20인 3일 절대 초과수익률, 각각 0.15인 거래량 충격과 변동성 충격을 합성해 $[0,1]$로 제한한다. 0, 0.20, 0.45, 0.75, 1을 경계로 `0 <= s < 0.20`은 LOW, `0.20 <= s < 0.45`는 MEDIUM, `0.45 <= s < 0.75`는 HIGH, `0.75 <= s <= 1`은 CRITICAL로 계산한다. 미래 관측값은 정답 생성에만 사용하므로 이 등급은 인과적 중요도나 거래 신호가 아니다.

## 5. 누수와 교란 통제

본 연구는 분할 경계 이후의 문서, 같은 사건의 중복 문서 또는 미래 구간에서 계산한 통계가 이전 구간의 전처리·보정·모델 선택에 영향을 주는 현상을 **시간 경계 누수(temporal-boundary leakage)**라고 조작적으로 정의한다. 이는 새로운 보편 분류체계를 주장하는 용어가 아니라 본 데이터셋에서 통제할 위험의 범위를 명확히 하는 운영 정의다.

### 5.1 시간 분할

| 출처 | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| 뉴스 | 99,826 | 6,391 | 9,560 |
| 공시 | 119,146 | 584 | 4,615 |
| Test 합계 | - | - | 14,175 |

Validation은 2026-01-01, Test는 2026-04-01에 시작하고 각 경계 전 7일을 embargo로 제외한다. Test는 전처리·threshold·모델 선택에 사용하지 않는다.

### 5.2 사건 단위 제어

- 유효 거래일을 포함한 사건 fingerprint로 반복 기사를 cluster화한다.
- 같은 종목·거래일에 다른 사건 cluster가 둘 이상이면 학습에서 제외한다.
- 같은 사건·종목·거래일에서는 정보량이 가장 큰 문서 하나를 선택한다.
- 기준선과 Transformer 예측 파일의 document ID와 정답이 완전히 같아야 통계 평가를 허용한다.

## 6. 모델

### 6.1 감성

- base: `kakaobank/kf-deberta-base`
- 고정 revision: `363b171d71443b0874b0bf9cea053eb5b1650633`
- 누수 제거 K-FNSPID 문서 1,118,291건·62,468,526 non-padding token의 FP32 DAPT
- 12개 encoder layer query/key/value/dense LoRA, rank 16
- 대상 종목 prefix + 본문 head-tail, 최대 256 token
- 서로 다른 dropout 경로 사이 양방향 KL을 포함한 R-Drop
- 공유 중립/방향 head + 정확한 0으로 초기화한 NEWS·DISCLOSURE·PUBLIC residual head
- 1단계 전체행 encoder+head 2 epoch, 2단계 receipt-bound Gold head 정제 4 epoch
- 고정 domain×task cell sample-weight mass 기반 계층형 cross entropy v3
- 공식 종목명·종목코드·모든 alias의 잔존을 검사하는 target-swap
- 데이터 선택 seed `20260715`, 모델 seed `17/42/73`

개발 적격 공개 Validation 932건과 receipt-bound 개발 Gold 895건은 중복·보호 group 제거 뒤 고정 group 단위로 Checkpoint 911건, Calibration 455건, Selection 461건에 상호 배타적으로 분리한다. Checkpoint는 학습 epoch와 checkpoint 선택에만, Calibration은 logit 보정에만, Selection은 seed와 최종 후보 선택에만 사용한다. 공개 Test와 확증 Gold는 이 과정에서 읽지 않는다.

공정 기준선은 `snunlp/KR-FinBert-SC`를 후보와 동일한 원천행, group split, data seed, model seeds, epoch 수와 optimizer update 일정으로 전체 fine-tuning한다. 모델 구조별 learning rate와 trainable parameter 수는 동일하지 않으며 보고서에 별도 기록한다. 추가로 원본 KR-FinBERT-SC 고정 추론과 K-FNSPID 도입 전 서비스 모델을 진단 비교에 포함한다.

### 6.2 의미 중요도

- 공시 전문 약지도 실데이터 8,302건, Gold URL 중복 0건
- 제목, 제목+요약, 제목+요약+전문 TF-IDF Logistic Regression을 같은 시간 분할로 학습
- Gold를 보지 않고 2026 Validation macro F1, Brier score, 문맥량 순으로 입력 뷰를 선택해 제목+요약을 배포
- Gold 문장을 복제하지 않은 치명위험 어휘 템플릿 400건으로 희소 CRITICAL 경계 보강
- 선택 모델 단독 기본 공시 Gold 600건 accuracy 0.9850, macro F1 0.9470
- 코드북 안전 floor 포함 기본 Gold 1.0000 / 1.0000, 스트레스 포함 910건 0.9989 / 0.9962
- 시장영향 신호와 불일치해도 의미 중요도 등급을 변경하지 않고, 양 신호는 API에서 별도 반환
- 상장폐지·횡령/배임·감사의견거절·부도·회생·파산만 CRITICAL 안전 floor를 적용한다. 거래정지·불성실공시 단독은 HIGH이며 일반 등급은 모델 예측을 유지한다.

### 6.3 출처별 가격반응 등급 기준선

- 뉴스와 공시를 섞지 않고 출처마다 독립된 Train-only artifact를 적합
- 입력: `[SOURCE=NEWS|DISCLOSURE]` prefix + 제목 + snippet + 전문 + 종목명
- TF-IDF char 2~5-gram, 최대 180,000 feature
- class-balanced One-vs-Rest Logistic Regression
- 논문 Test는 Train 전용 모델로 평가한다. 배포 artifact만 Train+Validation으로 다시 적합한다.

### 6.4 출처별 가격반응 등급 Transformer

- 공통: KF-DeBERTa base + LoRA r=16, class-balanced focal cross entropy + ordinal CDF MSE
- 뉴스: 최대 256토큰. v4 Test를 보기 전에 Validation으로 동결한 adapter를 뉴스 전용으로 재평가
- 공시: 최대 128토큰, learning rate 5e-5, focal gamma 1.0, ordinal 가중치 0.20, label smoothing 0.01, 유효 batch 32, 1 epoch
- 공시 seed 17/42/73을 같은 설정으로 학습하고 보정된 Validation macro F1만으로 seed 17을 선택
- class-balanced loss의 prior shift를 줄이기 위해 log class-prior 강도 0.00~2.00과 temperature 0.50~3.00을 Validation에서만 선택
- 요청 `source_type`과 artifact의 `source_type`이 다르면 추론을 거부

## 7. 평가

- 분류: accuracy, macro F1
- 순서형: quadratic weighted Cohen's kappa
- 보정: 15-bin ECE, multiclass Brier score
- source 분석: NEWS와 DISCLOSURE 분리

감성의 canonical statistical analysis plan(SAP)은 후보 잠금 전에 다음과 같이 고정한다.

1. NEWS와 DISCLOSURE 각각에서 신규 후보를 원본 KR-FinBERT-SC, K-FNSPID 도입 전 모델, 공정 full-FT KR-FinBERT-SC와 비교해 6개 1차 가설을 정의한다.
2. 가족별 유의수준 0.05에서 Holm 절차로 6개 p값을 보정한다.
3. 출처·감성 층별 단순무작위 비복원추출(SRSWOR)을 반영한 paired weight와 finite-population correction(FPC)을 사용한다.
4. 1차 분산은 paired stratified delete-one jackknife로 추정하고, seed `20260715`의 paired bootstrap 2,000회를 보조 구간·민감도 분석으로 사용한다.
5. 공개 Test는 진단으로만 보고하고, 원격 Git attestation 이후 완성한 확증 Gold의 one-shot 결과만 신규 성능 주장과 승격 판정에 사용한다.

가중 Macro-F1은 비선형 plug-in 추정량이므로 정확히 불편하다고 표현하지 않는다. Holm 절차는 6개 p값의 family-wise error rate를 통제하지만 개별 95% 구간을 동시 신뢰구간으로 만들지는 않는다. 시장반응의 기존 분석은 별도의 거래일 cluster bootstrap과 exact McNemar 절차를 유지하며 감성 SAP와 혼합하지 않는다.

## 8. 결과

### 8.1 감성 확증평가

| 모델·비교 | NEWS Accuracy / Macro-F1 | DISCLOSURE Accuracy / Macro-F1 | Holm 보정 결론 |
| --- | ---: | ---: | --- |
| Hana Montana AI(KF-DeBERTa + K-FNSPID) | 0.7503 / 0.5530 | 0.8646 / 0.6024 | 미승격 |
| 원본 KR-FinBERT-SC | 0.5781 / 0.4937 | 0.8535 / 0.6146 | 두 출처 동시 우월성 미확인 |
| K-FNSPID 도입 전 모델 | 0.4737 / 0.4396 | 0.8480 / 0.5358 | 두 출처 동시 우월성 미확인 |
| 공정 full-FT KR-FinBERT-SC | 0.7677 / 0.5771 | 0.8514 / 0.5647 | 두 출처 동시 우월성 미확인 |

표의 값은 층화가중 Accuracy/Macro-F1이다. 비가중 600건 표본 Macro-F1은 NEWS 0.6636, DISCLOSURE 0.6056이지만 1차 판정에는 모집단 층화가중 추정량을 사용했다. 원본 KR-FinBERT-SC 대비 가중 Macro-F1 차이는 NEWS +0.0594, DISCLOSURE -0.0123이며 두 출처 동시 우월성은 확인되지 않았다. 공개 Test는 회귀 진단 이외에 사용하지 않고 전역 SOTA를 주장하지 않는다.

### 8.2 공시 의미 중요도 Gold

| 모델 | Gold | accuracy | macro F1 | CRITICAL F1 |
| --- | ---: | ---: | ---: | ---: |
| 도입 전 통합 중요도 | 600 | 0.7150 | 0.4489 | 0.2619 |
| 제목 전용 ablation | 600 | 0.9700 | 0.8820 | 0.5854 |
| 제목+요약 선택 모델 | 600 | 0.9850 | 0.9470 | 0.8163 |
| 제목+요약+전문 ablation | 600 | 0.9433 | 0.8699 | 0.7188 |
| 선택 모델+코드북 floor | 600 | 1.0000 | 1.0000 | 1.0000 |

제목+요약과 제목 단독은 Validation macro F1 0.9894로 같았고 Brier score가 0.00134 대 0.00156으로 낮은 제목+요약을 선택했다. 전문 포함 뷰의 Validation macro F1은 0.9815였으며 Test에서 성능도 낮았다. 수집한 전문은 데이터셋·시장영향 모델·후속 장문 모델 연구에 보존하되 현재 의미 모델에는 억지로 투입하지 않는다. 기본·스트레스 Gold 910건에서 운영 후보는 accuracy 0.9989 / macro F1 0.9962이며 기존 분석기 대비 accuracy 차이 0.0935, paired bootstrap 95% CI [0.0747, 0.1132], macro F1 차이 0.1764의 CI [0.1420, 0.2132], exact McNemar p=1.14e-24다. ECE는 0.0225, Brier score는 0.0063이다. 다만 Gold는 동일 코드북을 따르는 Codex 단일 판정이므로 완전한 금융전문가 외부 검증이나 독립 다중 평가자 일치도로 해석하지 않는다. 구형 stock-review Gold의 배당 LOW 정의는 v3 코드북의 주주환원 HIGH 정의와 충돌하므로 동일 평가로 합산하지 않는다.

### 8.3 K-FNSPID 출처별 시간 Test

| 출처·모델 | Test | accuracy | macro F1 | QWK | ECE |
| --- | ---: | ---: | ---: | ---: | ---: |
| 뉴스 TF-IDF | 9,560 | 0.4715 | 0.3484 | 0.3421 | 0.0453 |
| 뉴스 KR-FinBERT-SC | 9,560 | 0.4902 | 0.3506 | 0.3962 | 0.0340 |
| 뉴스 KF-DeBERTa LoRA | 9,560 | 0.5247 | 0.3745 | 0.4754 | 0.0182 |
| 공시 TF-IDF | 4,615 | 0.3675 | 0.2677 | 0.1125 | 0.0444 |
| 공시 KR-FinBERT-SC seed 17 | 4,615 | 0.4319 | 0.3131 | 0.1611 | 0.0404 |
| 공시 KF-DeBERTa LoRA seed 17 | 4,615 | 0.4750 | 0.3216 | 0.1550 | 0.0441 |
| 출처 라우팅 TF-IDF | 14,175 | 0.4377 | 0.3210 | 0.2552 | 0.0369 |
| 출처 라우팅 KF-DeBERTa LoRA | 14,175 | 0.5085 | 0.3690 | 0.3975 | 0.0259 |

공시 3-seed Test는 accuracy 0.4534±0.0216, macro F1 0.3170±0.0052, QWK 0.1556±0.0007이다. seed 17의 Validation macro F1 0.2471이 seed 42의 0.2419와 seed 73의 0.2419보다 높아 Test를 보지 않고 승격했다. 뉴스 후보 추가 학습 seed 17은 Validation macro F1 0.3770으로 동결 adapter의 0.3823보다 낮아 Test 평가 전에 중단했다.

거래일 cluster bootstrap 2,000회에서 Transformer-minus-baseline macro F1 95% CI는 뉴스 [0.0120, 0.0409], 공시 [0.0264, 0.0806]이고 QWK는 각각 [0.1090, 0.1558], [0.0046, 0.0794]다. 통합 CI는 accuracy [0.0594, 0.0818], macro F1 [0.0351, 0.0608], QWK [0.1178, 0.1649]이며 exact McNemar p=2.29e-55다. 따라서 v3 공유 모델에서 나타났던 공시 회귀를 숨기지 않고 제거했지만, 공시 QWK 하한은 0에 가까워 추가 기간 반복이 필요하다.

강한 공개 비교군인 KR-FinBERT-SC와의 동일 조건 비교에서 뉴스 Macro-F1은 0.3506에서 0.3745로 6.82%(+0.0239점), 공시는 0.3131에서 0.3216으로 2.72%(+0.0085점) 높았다. 거래일 군집 95% 신뢰구간은 뉴스 [0.0090, 0.0383], 공시 [-0.0126, 0.0317]이다. 뉴스는 QWK 차이도 [0.0622, 0.0960]으로 우위 gate를 통과했지만, 공시는 QWK가 0.1611에서 0.1550으로 낮아 우위를 확정하지 않는다. 이 비교는 동일 K-FNSPID 시간 Test에 한정되며 전역 SOTA 주장이 아니다.

## 9. Ablation과 도입 전후

### 9.1 과거 공유 TF-IDF 입력·학습량 절제

| 설정 | Test accuracy | Test macro F1 | Test QWK |
| --- | ---: | ---: | ---: |
| 전문 + source prefix, Train 107,175 | 0.4643 | 0.3429 | 0.3141 |
| 전문, source prefix 제거 | 0.4632 | 0.3427 | 0.3127 |
| 제목+snippet + source prefix | 0.4689 | 0.3505 | 0.3271 |
| 전문 + source prefix, Train 20,000 | 0.4802 | 0.3260 | 0.2890 |
| 전문 + source prefix, Train 50,000 | 0.4756 | 0.3446 | 0.3225 |

이 표는 v4 출처별 평가가 아니라 이전 공유 split의 원인 분석이다. 선형 TF-IDF에서는 전문 추가가 제목+snippet보다 낮았다. 수집량 확장이 시장영향 예측을 자동 개선한다는 주장을 배제하며, 전문은 데이터 자원과 후속 장문 모델 연구에 보존한다. 학습량 증가는 2만 대비 macro F1을 높였지만 5만 이후 단조 증가하지 않아 분포 이동과 약한 라벨 잡음이 병목임을 시사한다.

### 9.2 설계 변경

| 변경 | 목적 |
| --- | --- |
| 공시 LOW/MEDIUM→HIGH 강제 제거 | 공시 유형별 중요도 붕괴 방지 |
| 배포 공시 원문 8,972건 연결 | 공시 문맥·종목 연결 범위 명시 |
| source별 독립 기준선·전문가 | 공유 모델의 공시 회귀 제거 |
| 공시 Test 590→4,615 | 출처별 통계 검정력 개선 |
| 뉴스 256 / 공시 128 token | Validation 근거로 출처별 문맥 길이 분리 |
| weighted CE→focal+ordinal CDF | 불균형과 순서형 거리 동시 최적화 |
| Validation log-prior+temperature | Test 미사용 보정과 ECE 관리 |
| 감성 Checkpoint/Calibration/Selection 3-way group split | checkpoint·보정·seed 선택의 역할 중복 제거 |
| data seed와 model seed 분리 | 모델 반복마다 같은 입력·분할 보장 |
| all-12 LoRA r16 + R-Drop | 전층 적응과 dropout 일관성 결합 |
| target prefix + head-tail 256 | 대상 종목과 문서 앞·뒤 근거 보존 |
| 공유·출처 residual 계층형 head | 공통 표현과 뉴스·공시 차이를 분리하고 미학습 residual은 0 유지 |
| fixed cell-mass 계층형 CE | Silver weight와 domain×task cell 불균형 반영 |
| alias-safe target-swap | 공식명·코드·별칭 잔존에 따른 거짓 반사실 차단 |
| KR-FinBERT-SC 공정 full-FT | 동일 자료·분할·seed·update 일정 비교 |
| locked SAP + one-shot confirmatory | 공개 Test 반복 조회와 사후 가설 선택 차단 |

모든 ablation은 같은 시간 경계와 동일 Test document ID를 사용해야 하며, 다른 Test 집합의 수치를 한 개선율로 합치지 않는다.

감성 제거 실험의 `FULL` 참조군은 같은 seed로 이미 학습한 잠긴 후보 artifact를 재학습하지 않고 사용한다. 재사용 영수증은 후보 report, 입력·분할·DAPT base, 학습 예산, CPU roundtrip과 artifact manifest의 byte·SHA-256을 재검증한다. 후보의 실제 minibatch 순서를 보존하므로 stable-order 제거군과 bitwise 동일한 순서를 실행했다고 해석하지 않으며, 비교 가능성은 같은 원천행·노출 수·optimizer update 예산에 한정한다.

## 10. 재현성·보안

- Python 3.12, `uv.lock`, 고정 base revision
- 데이터 seed, 모델 seed, 학습률, 유효 batch, scheduler, LoRA 설정, 목적함수, 완료 epoch와 각 개발 역할의 선택값을 report에 기록
- 같은 거래일의 상관 오차를 독립 표본으로 과대 계산하지 않도록 거래일 cluster bootstrap을 우월성 gate로 사용
- upstream base의 고정 PyTorch weight SHA-256을 `weights_only=True`로 검증한 뒤 배포용 `safetensors`로 변환하며, 운영 로더는 변환본·보고서·파일 크기·SHA-256이 모두 일치할 때만 활성화
- Hugging Face remote code 비활성화
- 비밀키는 `secrets.local.env`, 로그·report·dataset에 포함하지 않음
- 감성 확증은 원격 Git lock attestation과 one-shot receipt가 없으면 실행·승격하지 않음

## 11. 논의

시장영향 분류에서 KF-DeBERTa는 출처별 TF-IDF 진단 기준선을 상회했다. 강한 비교군인 KR-FinBERT-SC 대비 우위는 국내 뉴스에서만 확인됐고 국내 공시에서는 확인되지 않았다. 서로 다른 언어와 정답 정의를 사용하는 외부 데이터셋의 점수를 직접 비교해 전역 최고 성능을 주장하지 않는다.

### 연구의 한계

- Naver Search 반환 제한과 질의 구성에 따른 선택 편향
- 공시 전문 커버리지 1.24%
- 일봉 사용으로 장중 즉시 반응 분리 불가
- 시장 평균 차감 이후에도 업종·규모·거시 교란 잔존
- 가격반응 중요도는 의미 중요도·인과효과·투자 수익성과 다름
- 뉴스 보조 Gold의 독립 이중검수·재심과 공시 보조 Gold는 Codex 기반이며 인간 금융전문가 합의도가 아님
- 공개 감성 Test는 과거 후보 선택과 개발 중 반복 조회되어 새 미열람 확증셋이 아님
- 개발 Gold는 2025년 6--12월, 보조 공시 Gold와 확증 후보는 2026년 4--7월에 집중됨. 문서 수준 분리는 했지만 확증 표본이 명확한 미래 out-of-time 기간은 아님
- seed 고정은 입력·분할 재현성을 제공하지만 Apple MPS와 다른 accelerator 사이의 bitwise 동일성을 보장하지 않음
- 한국 시장의 동일 라벨 정의를 사용하는 공인 leaderboard 부재

따라서 감성 비교가 완료되기 전에는 성능 우위나 최고 성능을 주장하지 않는다. 이후에도 독립 금융 전문가 주석, 더 미래 기간의 외부 반복실험과 공인 동일과제 평가가 없으면 외부 Gold 타당성, 장기 일반화 또는 전역 SOTA를 주장하지 않는다.

## 12. 결론

K-FNSPID는 국내 뉴스와 OpenDART 공시를 대상 종목 및 일별 시세에 연결하고, 거래 세션 정규화와 사건 혼입 통제를 적용한다. 시장영향 중요도 분류는 동일 조건의 KR-FinBERT-SC 대비 국내 뉴스에서 우위를 확인했지만 국내 공시에서는 우위를 확인하지 못했다. 대상 종목 감성분류는 제거실험과 잠긴 확증 평가가 끝난 뒤 최종 결과를 보고한다.

## 13. 산출물

- dataset manifest: `data/k_fnspid/v4/manifest.json`
- datasheet: `docs/datasets/k-fnspid-v4-datasheet.md`
- source baseline report/predictions: `reports/k-fnspid-impact-{news,disclosure}-*`
- source Transformer report/predictions: `reports/k-fnspid-impact-{news,disclosure}-transformer-*`
- 공시 반복실험: `reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json`
- paired statistics: `reports/k-fnspid-research-evaluation.json`
- KR-FinBERT-SC 강한 비교군: `reports/k-fnspid-impact-kr-finbert-sc-matrix.json`, `reports/k-fnspid-impact-kr-finbert-sc-result-attestation.json`
- sentiment benchmark: `reports/korean-finance-sentiment-benchmark.json`
- locked sentiment SAP: `src/hannah_montana_ai/training/sentiment_evaluation_plan.py`
- candidate lock·Git attestation·one-shot receipt: 완료, 보고서 SHA-256 `be5c9edd…b149`
- disclosure importance statistics: `reports/disclosure-importance-training-report.json`, `reports/disclosure-importance-research-evaluation.json`
- code and environment: repository commit, `pyproject.toml`, `uv.lock`

## 참고 문헌

1. Dong, Z., Fan, X., & Peng, Z. (2024). [FNSPID: A Comprehensive Financial News Dataset in Time Series](https://doi.org/10.1145/3637528.3671629). KDD 2024.
2. Son, G., Jeon, H., Hwang, C., & Jung, H. (2024). [KRX Bench: Automating Financial Benchmark Creation via Large Language Models](https://aclanthology.org/2024.finnlp-1.2/). FinNLP 2024.
3. Son, G., Ko, H., Jung, H., & Hwang, C. (2025). [FINKRX: Establishing Best Practices for Korean Financial NLP](https://aclanthology.org/2025.acl-industry.81/). ACL Industry Track 2025.
4. Jeon, E., Kim, J., Song, M., & Ryu, J. (2023). [KF-DeBERTa: Financial Domain-specific Pre-trained Language Model](https://huggingface.co/kakaobank/kf-deberta-base). HCLT 2023.
5. Kim, E., & Shin, H. (2022). [KR-FinBERT-SC: Fine-tuning KR-FinBERT for Sentiment Analysis](https://huggingface.co/snunlp/KR-FinBert-SC).
6. Tang, Y., Yang, Y., Huang, A., Tam, A., & Tang, J. (2023). [FinEntity: Entity-level Sentiment Classification for Financial Texts](https://doi.org/10.18653/v1/2023.emnlp-main.956). EMNLP 2023.
7. Chen, T. et al. (2024). [EFSA: Towards Event-Level Financial Sentiment Analysis](https://doi.org/10.18653/v1/2024.acl-long.402). ACL 2024.
8. Hu, E. J. et al. (2022). [LoRA: Low-Rank Adaptation of Large Language Models](https://openreview.net/forum?id=nZeVKeeFYf9). ICLR 2022.
9. Liang, X. et al. (2021). [R-Drop: Regularized Dropout for Neural Networks](https://proceedings.neurips.cc/paper/2021/hash/5a66b9200f29ac3fa0ae244cc2a51b39-Abstract.html). NeurIPS 2021.
10. Cui, Y., Jia, M., Lin, T.-Y., Song, Y., & Belongie, S. (2019). [Class-Balanced Loss Based on Effective Number of Samples](https://doi.org/10.1109/CVPR.2019.00949). CVPR 2019.
11. Guo, Y., Hu, C., & Yang, Y. (2023). [Predict the Future from the Past? On the Temporal Data Distribution Shift in Financial Sentiment Classifications](https://doi.org/10.18653/v1/2023.emnlp-main.65). EMNLP 2023.
12. Holm, S. (1979). [A Simple Sequentially Rejective Multiple Test Procedure](https://www.jstor.org/stable/4615733). Scandinavian Journal of Statistics, 6(2), 65–70.
13. Peng, X. et al. (2026). [MultiFinBen: Benchmarking Large Language Models for Multilingual and Multimodal Financial Application](https://doi.org/10.18653/v1/2026.acl-long.770). ACL 2026.
14. Son, G., Lee, H., Kang, N., & Hahm, M. (2023). [Removing Non-Stationary Knowledge From Pre-Trained Language Models for Entity-Level Sentiment Classification in Finance](https://doi.org/10.48550/arXiv.2301.03136). AAAI 2023 Workshop on Multimodal AI for Financial Forecasting.
