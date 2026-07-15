# Hana Montana AI(KF-DeBERTa + K-FNSPID) Model Card

## 모델 개요

Hana Montana AI(KF-DeBERTa + K-FNSPID)는 한국 뉴스·공시를 종목 인텔리전스로 변환하는 복합 모델이다. 단일 신경망 이름이 아니라 다음 검증된 구성의 서비스 표기명이다.

- 금융 감성: Validation Selection으로 잠근 KF-DeBERTa LoRA 후보와 fail-closed 기존 TF-IDF 모델
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

### 구조

- base model: `kakaobank/kf-deberta-base`
- revision: `363b171d71443b0874b0bf9cea053eb5b1650633`
- LoRA: r=16, alpha=32, dropout=0.1
- 분할: 정규화 중복·충돌 제거 후 공개 Train 7,407 / Validation 932 / Test 932건
- 선택: Validation을 Calibration 467 / Selection 465로 분리하고 Test·운영 Gold를 보지 않은 Selection에서 단독 LoRA를 잠금
- stacker·80:20 ensemble·source logit bias: Validation 비교에서 단독 LoRA를 넘지 못하거나 운영 gate를 통과하지 못해 미승격

### 평가

| 모델 | 중복 제거 공개 Test 932 macro F1 |
| --- | ---: |
| Hana TF-IDF | 0.4415 |
| KR-FinBERT-SC | 0.7266 |
| 잠근 KF-DeBERTa LoRA | 0.8849 |
| 80:20 앙상블 | 0.8838 |
| Source-bias 후보 | 0.8724 |
| Logistic stacker | 0.8331 |

잠근 LoRA와 KR-FinBERT-SC의 동일 문서 paired bootstrap Macro-F1 차이는 0.1580이고 고정 예측 구간은 `[0.1265, 0.1899]`, exact McNemar의 계산값은 `p=9.81e-19`다. 그러나 Test를 과거 후보 선택과 개발 중 반복 조회했으므로 이 구간과 p값의 명목 오류율은 보장되지 않는다. 따라서 기술적 동일셋 재현 차이만 보고하며 확증적 통계 우위, 독립 확증시험 또는 한국 금융 감성 전역 SOTA로 해석하지 않는다.

운영 평가는 실제 뉴스 Gold 80건 Accuracy 0.8625 / Macro-F1 0.8308, 공시 Gold 600건 0.9150 / 0.8084다. 뉴스 Accuracy가 0.90 gate에 미달하므로 신규 Transformer 후보는 `KEEP_CURRENT_MODEL`이고 기존 서비스 모델로 fail closed한다. 공시 적응·균형 replay·보존 학습을 실제 수행했지만 한 운영 분포를 개선할 때 다른 분포가 회귀해 어느 후보도 승격하지 않았다.

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

<!-- K_FNSPID_FINAL_MODEL_METRICS -->

출처별 고정 시간 Test에서 뉴스 전문가는 9,560건 accuracy 0.5247 / macro F1 0.3745 / QWK 0.4754 / ECE 0.0182, 공시 전문가는 4,615건 0.4750 / 0.3216 / 0.1550 / 0.0441이다. 통합 14,175건은 기준선 0.4377 / 0.3210 / 0.2552에서 출처별 전문가 0.5085 / 0.3690 / 0.3975로 개선됐다. 거래일 cluster bootstrap 2,000회의 Macro-F1 차이 95% CI는 뉴스 [0.0120, 0.0409], 공시 [0.0264, 0.0806], 통합 [0.0351, 0.0608]이며 exact McNemar p=2.29e-55이다.

공시 Transformer는 seed 17/42/73을 같은 설정으로 반복하고 Validation에서 checkpoint·class-prior·temperature 보정과 배포 run을 선택한다. Test superiority는 행 단위 paired bootstrap과 거래일 cluster bootstrap 각 2,000회, exact McNemar, QWK, ECE, Brier score로 별도 판정하며 우월성 gate에는 더 보수적인 거래일 cluster 구간을 사용한다.

## 배포 gate

### 감성

- 공개 Test 900건 이상
- macro F1 0.85 이상
- KR-FinBERT-SC 이상
- 뉴스·공시 운영 Gold 각각 30건 이상, accuracy 0.90·macro F1 0.80 이상
- 후보를 Test 전에 Validation Selection에서 잠그고 Test·운영 Gold를 선택에 사용하지 않음

### 가격반응

- 뉴스: 시간 Test 5,000건 이상, macro F1 0.35 이상, QWK 0.30 이상, ECE 0.20 이하
- 공시: 시간 Test 500건 이상, macro F1 0.30 이상, QWK 0.08 이상, ECE 0.20 이하
- 각 출처 TF-IDF 기준선의 macro F1·QWK 이상이고 ECE가 악화되지 않아야 한다.

### artifact 무결성

- Transformer는 `safetensors`만 사용하고, scikit-learn artifact는 report SHA-256·크기를 역직렬화 전에 검증
- report의 byte 크기·SHA-256과 실제 파일이 모두 일치해야 활성화
- 고정 base revision, remote code 비활성화
- gate나 hash 검증 실패 시 같은 출처의 적격 기준선만 사용한다. 공시 기준선은 독립 gate 미달이므로 공시 시장영향만 생략한다.

## 데이터와 라벨 안전성

- OpenDART·Naver 자격증명은 로컬 secret 파일에서만 읽고 report에 기록하지 않는다.
- 검수되지 않은 공시 전문 약한 중요도 라벨은 Gold URL을 제거한 뒤 의미 중요도 후보 학습에만 사용한다. 감성 학습과 Gold 평가 정답에는 사용하지 않는다.
- 공시 Gold와 전문 학습 URL 중복은 0건이다.
- 현재 파이프라인은 시간 Test를 threshold·전처리·후보 선택에 사용하지 않는다. 단, 공개 감성 Test는 과거 버전에서 반복 사용했으므로 새 독립 확증셋으로 표현하지 않는다.
- 같은 종목·거래일 다중 사건은 가격반응 학습에서 제외한다.
- Parquet 6개뿐 아니라 raw/full-content/종목/시세/Gold 원천의 경로·byte·개별/복합 SHA-256이 모두 일치해야 재학습을 허용한다.

## 알려진 한계

- 가격반응 중요도는 의미 중요도·인과효과가 아니다.
- 전체 공시 대비 실제 전문 연결률은 1.24%다. 전문 8,972건은 보존하지만 시장영향 제목·snippet ablation이 더 강했던 결과를 숨기지 않는다.
- 일봉은 장중 즉시 반응을 분리하지 못한다.
- 공개 감성 Test의 우위가 모든 실제 뉴스 분포에서 유지되지는 않는다.
- Gold는 Codex가 코드북과 근거를 검수했으므로 인간 전문가 간 합의도를 제공하지 않는다.
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
