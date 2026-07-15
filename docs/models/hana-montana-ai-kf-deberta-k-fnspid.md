# Hana Montana AI(KF-DeBERTa + K-FNSPID) Model Card

## 모델 개요

Hana Montana AI(KF-DeBERTa + K-FNSPID)는 한국 뉴스·공시를 종목 인텔리전스로 변환하는 복합 모델이다. 단일 신경망 이름이 아니라 다음 검증된 구성의 서비스 표기명이다.

- 금융 감성: KF-DeBERTa LoRA + TF-IDF Logistic Regression 확률 앙상블
- 의미 중요도·이벤트: 공시 약지도 Validation 선택 Logistic Regression과 제한적 존속위험 정책
- 시장영향 등급: K-FNSPID v3로 학습한 KF-DeBERTa LoRA 또는 fail-closed TF-IDF 기준선
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
- 서빙 결합: Transformer 0.8 + TF-IDF 기준선 0.2
- stacker 실험: 공개 Validation 932건으로만 학습했으나 독립 Test·실제 뉴스 Gold에서 열세라 비활성화

### 평가

| 모델 | 공개 Test 933 macro F1 |
| --- | ---: |
| Hana TF-IDF | 0.4423 |
| KR-FinBERT-SC | 0.7272 |
| KF-DeBERTa LoRA | 0.8850 |
| 배포 80:20 앙상블 | 0.8840 |
| Logistic stacker | 0.8820 |

배포 앙상블은 실제 뉴스 Gold 80건에서 accuracy 0.9000 / macro F1 0.8642, 학습 URL과 겹치지 않는 공시 Gold 600건에서 accuracy 0.9233 / macro F1 0.8344를 기록해 강화된 운영 gate도 만족한다. 공개 Test와 운영 Gold의 분포가 다르므로 한 지표로 합산하지 않는다.

## 공시 의미 중요도 모델

약지도 실공시 8,302건과 Gold 문장을 복제하지 않는 치명위험 템플릿 400건으로 제목, 제목+요약, 제목+요약+전문 뷰를 같은 시간 분할에서 학습한다. Gold는 선택에 사용하지 않고 2026 Validation macro F1과 Brier score로 제목+요약 뷰를 선택했다. 모델 단독 기본 Gold 600건은 accuracy 0.9850 / macro F1 0.9470 / CRITICAL F1 0.8163이다. 상장폐지·횡령/배임·감사의견거절·부도·회생·파산 안전 floor를 포함하면 기본 Gold 1.0000 / 1.0000, 학습·기본 Gold와 URL이 겹치지 않는 스트레스 Gold까지 합친 910건은 0.9989 / 0.9962다. 거래정지·불성실공시 단독은 코드북대로 HIGH다. 기본 Gold URL 401건은 학습 전에 제외해 post-filter 중복이 0이며, 시장영향은 의미 라벨과 confidence를 모두 변경하지 않는다. 전문 포함 ablation의 기본 Gold 0.9433 / 0.8699는 전문의 길이·보일러플레이트가 선형 모델을 악화시킴을 보여주므로 실제 전문은 데이터셋과 후속 장문 모델 연구에 보존한다.

## K-FNSPID 시장영향 모델

### 데이터

- K-FNSPID v3 문서 550,662건
- 시세 10,691,998행, 2,800종목
- 비혼입 대표행 Train 107,175 / Validation 6,975 / Test 10,750
- 공시 25,966건 중 실제 원문 8,972건
- 평가 Gold 뉴스 80 + 공시 600

### 입력 feature

- `[SOURCE=NEWS]` 또는 `[SOURCE=DISCLOSURE]`
- 제목 + snippet + 전문 + 대표 종목명
- 가격, 거래량, 미래 수익률은 입력하지 않는다.

### Transformer 목적함수

- class-balanced focal cross entropy, gamma 1.5
- ordinal CDF MSE, weight 0.30
- label smoothing 0.02
- max length 256
- device batch 8, gradient accumulation 4, 유효 batch 32
- learning rate 2e-4, cosine scheduler, warmup 8%, weight decay 0.01
- LoRA r=16, alpha=32, dropout=0.1
- class-balanced loss의 소수 등급 과대 예측을 줄이기 위해 log class-prior 강도 0.00~2.00을 Validation에서만 선택한다. raw·보정 지표를 모두 보존하고 서빙에 같은 offset을 적용한다.

### 평가

공정한 TF-IDF 기준선은 Train만 적합해 Test accuracy 0.4643, macro F1 0.3429, quadratic kappa 0.3141다.

<!-- K_FNSPID_FINAL_MODEL_METRICS -->

seed 17/42/73 중 Validation macro F1가 가장 높은 seed 73을 선택했다. 선택 모델은 시간 Test 10,750건에서 accuracy 0.5095, macro F1 0.3820, quadratic kappa 0.4694다. 세 seed Test 평균±표본표준편차는 각각 0.5105±0.0080, 0.3824±0.0102, 0.4675±0.0042다. TF-IDF 대비 거래일 cluster bootstrap 95% CI는 accuracy [0.0351, 0.0557], macro F1 [0.0256, 0.0536], QWK [0.1331, 0.1776]이고 exact McNemar p=1.70e-20이다. Brier score는 0.6450→0.6129로 개선됐지만 ECE는 0.0491→0.0662로 악화됐다. NEWS 10,160건에서는 macro F1 0.3436→0.3847이나 DISCLOSURE 590건에서는 0.3006→0.2211이므로 공시 가격반응은 의미 중요도와 합치거나 외부 SOTA로 주장하지 않는다.

Transformer는 seed 17/42/73을 같은 설정으로 반복하고 Validation에서 checkpoint·class-prior 보정과 배포 run을 선택한다. Test superiority는 행 단위 paired bootstrap과 70개 거래일 cluster bootstrap 각 2,000회, exact McNemar, quadratic kappa, ECE, Brier score로 별도 판정하며 우월성 gate에는 더 보수적인 거래일 cluster 구간을 사용한다.

## 배포 gate

### 감성

- 공개 Test 900건 이상
- macro F1 0.85 이상
- KR-FinBERT-SC 이상
- 뉴스·공시 운영 Gold 각각 30건 이상, accuracy 0.90·macro F1 0.80 이상

### 가격반응

- 시간 Test 1,000건 이상
- macro F1 0.35 이상
- quadratic kappa 0.20 이상
- TF-IDF 기준선의 macro F1·kappa 이상

### artifact 무결성

- Transformer는 `safetensors`만 사용하고, scikit-learn artifact는 report SHA-256·크기를 역직렬화 전에 검증
- report의 byte 크기·SHA-256과 실제 파일이 모두 일치해야 활성화
- 고정 base revision, remote code 비활성화
- gate나 hash 검증 실패 시 TF-IDF 기준선으로 fail closed

## 데이터와 라벨 안전성

- OpenDART·Naver 자격증명은 로컬 secret 파일에서만 읽고 report에 기록하지 않는다.
- 검수되지 않은 공시 전문 약한 중요도 라벨은 Gold URL을 제거한 뒤 의미 중요도 후보 학습에만 사용한다. 감성 학습과 Gold 평가 정답에는 사용하지 않는다.
- 공시 Gold와 전문 학습 URL 중복은 0건이다.
- 시간 Test는 threshold·전처리 선택에 사용하지 않는다.
- 같은 종목·거래일 다중 사건은 가격반응 학습에서 제외한다.
- Parquet 6개뿐 아니라 raw/full-content/종목/시세/Gold 원천의 경로·byte·개별/복합 SHA-256이 모두 일치해야 재학습을 허용한다.

## 알려진 한계

- 가격반응 중요도는 의미 중요도·인과효과가 아니다.
- 공시 전문 커버리지는 34.55%다.
- 일봉은 장중 즉시 반응을 분리하지 못한다.
- 공개 감성 Test의 우위가 모든 실제 뉴스 분포에서 유지되지는 않는다.
- 공시 Gold는 단일 Codex 검수라 인간 전문가 간 합의도를 제공하지 않는다.
- 동일 K-FNSPID 라벨 정의의 외부 공인 leaderboard가 없다.

## 모니터링

- source별 라벨·confidence·fallback 비율
- 운영 Gold 회귀
- Test와 운영 분포별 ECE
- 공시/뉴스 원문 가용률
- artifact hash·base revision 변화
- 종목 linker coverage와 request stock mismatch

## 관련 산출물

- [K-FNSPID v3 Datasheet](../datasets/k-fnspid-v3-datasheet.md)
- [한국어 기술 근거본](../paper/k-fnspid-v3-paper-draft.md)
- [ACL Rolling Review 익명 심사 원고](../paper/acl/k-fnspid-v3-arr-review.tex)
- [저자 공개 영문 원고](../paper/acl/k-fnspid-v3-author-preprint.tex)
- [최성현 저자 한글 논문](../paper/acl/k-fnspid-v3-ko.tex)
- [저자·소속 메타데이터](../paper/acl/author-metadata.json)
- [제출·책임 있는 NLP 체크리스트](../paper/acl/responsible-nlp-checklist.md)
- [제출 manifest](../paper/acl/submission-manifest.json)
- `reports/korean-finance-sentiment-benchmark.json`
- `reports/disclosure-importance-training-report.json`
- `reports/disclosure-importance-research-evaluation.json`
- `reports/k-fnspid-transformer-multiseed-report.json`
- `reports/k-fnspid-research-evaluation.json`
