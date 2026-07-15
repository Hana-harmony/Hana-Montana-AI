# K-FNSPID v4: 한국 뉴스·공시와 시장반응을 연결한 시간 외삽 금융 NLP 데이터셋

> 제출 상태: ACL Rolling Review 장문 익명 심사용 PDF, 최성현 저자 공개 영문 PDF와 별도 한글 논문 PDF를 `docs/paper/acl/`과 `output/pdf/`에 관리한다. 저자 소속은 한국공학대학교 SW대학 컴퓨터공학부 소프트웨어전공이며 4학년 학부생이다. 이 문서는 한국어 기술 근거본이고, 학회 형식 한글본은 `docs/paper/acl/k-fnspid-v4-ko.tex`이며 공개 모델명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`다.

## 초록

한국 금융 NLP에는 장기간 뉴스·공시를 국내 전 종목 시세와 연결하고 발표 세션·사건 중복·미래 누수를 함께 통제한 공개 연구 자원이 부족하다. 본 연구는 Naver 뉴스 524,696건, OpenDART 공시 722,989건, 한국 상장종목 일별 시세 10,691,998행을 연결한 K-FNSPID v4를 제시한다. 데이터셋은 1,247,685개 문서, 1,136,118개 문서–종목 관계, 715,015개 시장영향 행과 255,168개 비혼입 사건 대표행으로 구성된다. 본 연구는 발표시각을 한국 거래 세션의 유효 거래일로 정규화하고 7일 embargo를 둔 시간순 Train/Validation/Test를 사용한다. 본 실험을 통해 KF-DeBERTa LoRA의 공개 감성 macro-F1이 KR-FinBERT-SC의 0.7272에서 0.8850으로 향상됨을 확인했다. 또한 출처별 가격반응 전문가는 통합 macro-F1을 0.3210에서 0.3690으로, QWK를 0.2552에서 0.3975로 향상시켰다. 모든 비교는 동일 Test 문서 집합에서 수행하며 paired bootstrap, exact McNemar와 calibration error를 함께 보고한다. 가격반응 라벨은 의미 중요도와 분리하고, 인과적 중요도나 수익 신호가 아닌 관측 시장 충격의 약한 순서형 대리변수로 제한해 해석한다.

## 1. 연구 질문

1. 한국 뉴스·공시와 일별 시세를 파일 기반으로 재현 가능하게 연결할 수 있는가?
2. 발표 세션, 시간 embargo, 사건 cluster, 동일 종목·거래일 다중 사건 제외가 미래 누수를 줄이는가?
3. 금융 도메인 Transformer와 순서형 목적함수가 강한 TF-IDF 기준선보다 미래 기간 시장충격 분류를 개선하는가?
4. 공개 감성 Test의 개선이 실제 뉴스·공시 운영 Gold에서도 유지되는가?

## 2. 관련 연구

- FNSPID는 대규모 미국 뉴스–주가 연결 데이터 설계의 직접 비교 대상이다.
- KRX-Bench는 한국 금융 벤치마크 구성과 한국어 금융 모델 평가 범위를 제공한다.
- FINKRX는 한국 금융 LLM의 공개 instruction data와 leaderboard 운영 사례를 제공하지만, 평가 과제는 금융 QA·주가 방향 선택형 문제이므로 본 연구의 문서별 사후 시장충격 등급과 직접 비교하지 않는다.
- KF-DeBERTa는 한국 금융 말뭉치 사전학습 표현을 제공한다.
- 금융 감성의 시간 분포 이동 연구는 무작위 분할보다 시간 외삽 평가가 필요함을 보인다.
- FININ과 2026년 뉴스 융합 주가예측 연구는 뉴스 상호작용·과거 시세·종목 관계를 함께 쓰는 다중모달 예측이 텍스트 단독 분류보다 강한 최신 방향임을 보여준다. K-FNSPID v4의 현재 가격반응 실험은 텍스트 단독 보조 신호이므로 이들 수익률·MAE 결과와 수치 순위를 주장하지 않는다.
- 2026년 FinTextSim은 공시 문맥에 특화된 표현이 일반·감성 임베딩보다 예측적 주제 추출에 유리할 수 있음을 보이며, 단순히 감성 모델을 가격반응 과제에 재사용하는 한계를 지적한다.
- ExAnte는 미래 사건 예측에서 cutoff 이후 정보의 암기·누출을 별도 검증해야 함을 보인다. K-FNSPID는 생성형 모델의 cutoff 준수 과제와는 다르지만, 발표시각 정규화·시간 embargo·미래 Test 동결을 같은 위험에 대한 데이터 수준 통제로 사용한다.
- ACL 2026 MultiFinBen은 뉴스·공시를 포함한 다언어·다중모달 금융 평가에서 전문가 검증과 난이도 균형을 강조한다. 현재 K-FNSPID는 한국어 텍스트와 일봉에 한정되므로 해당 benchmark와 점수를 직접 비교하지 않고 후속 다중모달 확장 기준으로만 참조한다.

K-FNSPID는 미국 종목 중심 FNSPID를 단순 번역하지 않고 한국 거래 세션, OpenDART 공시, 한국 종목 alias, KOSPI·KOSDAQ·KONEX 시장조정에 맞게 다시 설계한다.

| 자원 | 주된 과제 | 공개 규모 | 본 연구와의 직접 비교 가능성 |
| --- | --- | ---: | --- |
| FNSPID | 미국 뉴스–주가 시계열 연결 | 뉴스 1,570만, 시세 2,970만 | 데이터 설계·규모만 비교 가능 |
| KRX-Bench-POC | 한·미·일 기업 금융 QA | 질문 1,002 | 과제가 달라 성능 비교 불가 |
| FINKRX | 한국 금융 LLM QA·주가 방향 지식 평가 | 공개 instruction 8만, 비공개 benchmark 1,119회 제출 | 과제·평가셋이 달라 성능 비교 불가 |
| FININ | 뉴스 상호작용+시세 시장예측 | 미국 뉴스 270만 이상, 15년 | 다중모달 Sharpe 과제로 직접 비교 불가 |
| KF-DeBERTa | 한국 금융 PLM | 금융 downstream 7종 | base encoder와 공개 벤치마크 참고 |
| FinTextSim | 영문 공시 주제·기업성과 예측 | LR F1 59.9 / ROC-AUC 70.8 | 언어·정답·과제가 달라 방법론만 비교 |
| ExAnte | cutoff 준수 미래 추론·누출 평가 | 주가 사례 1,757 | 누출 통제 방법론만 비교 |
| MultiFinBen | 5개 언어·텍스트/이미지/오디오 금융 추론 | 공개 expert-annotated benchmark | 과제·모달리티가 달라 성능 비교 불가 |
| KR-FinBERT-SC | 한국 금융 감성 | 본 연구 Test 933 재평가 | 동일 문서·라벨에서 직접 비교 |
| K-FNSPID v4 | 한국 뉴스·공시–주가 연결 | 문서 1,247,685, 시세 10,691,998 | 동일 Test에서 자체 기준선과 비교 |

FNSPID보다 절대 문서 규모는 작다. 대신 공시, 발표 세션, 사건 중복·교란 플래그, 시간 embargo, 한국 전 종목 alias를 제공한다. KRX-Bench와 최신 한국 금융 LLM 벤치마크는 QA·지식 평가이므로 감성 또는 가격반응 수치를 섞지 않는다. 시장영향 중요도는 동일 라벨 정의의 외부 leaderboard가 없어 “외부 SOTA”가 아니라 동일 Test의 강한 TF-IDF 기준선 대비 우월성만 검정한다.

## 3. 데이터

### 3.1 규모

| 항목 | K-FNSPID v4 |
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
| 기본 Gold | 680 (뉴스 80 + 공시 600) |
| 공시 스트레스 포함 Gold | 910 |

세부 원천, schema, 편향, 삭제·버전 정책은 [K-FNSPID v4 Datasheet](../datasets/k-fnspid-v4-datasheet.md)에 고정한다.

### 3.2 공시 원문 확장

OpenDART 원문 API를 전체 pagination 목록과 연결하고, 32MB 응답 상한, timeout, 재시도, ZIP 검증과 DART 상태 분류를 적용해 전문 학습셋의 공시 원문 8,976건을 확보했다. 이 중 K-FNSPID raw 문서 URL과 연결되는 OpenDART 원문은 8,972건으로, 전체 배포 공시 722,989건의 1.24%다. 최종 추가 수집 대상 5,082건 중 4,976건을 저장했으며, 실패 106건은 본문 부족 51건, DART 상태 013 1건, 상태 014 37건, 공개 뷰어 metadata 부재 17건으로 보존했다.

수집 원문 라벨은 Gold가 아니며 `RULE_WEAK_SUPERVISION_V2`와 `UNREVIEWED_WEAK_LABEL`로 표시한다. Gold URL을 제거한 실제 공시 8,302건은 의미 중요도 후보의 supervised 학습에만 사용하고 감성 학습·평가 정답에는 사용하지 않는다. 기존의 모든 공시 HIGH 강제 규칙은 정기/행정 LOW, 지배구조 MEDIUM, 계약·자본·실적 HIGH, 치명 위험 CRITICAL 코드북으로 교체했다.

### 3.3 Gold

- 실제 뉴스 Gold: 80건
- OpenDART 공시 Gold: 600건, 480종목
- 공시 중요도: LOW 250 / MEDIUM 34 / HIGH 287 / CRITICAL 29
- 공시 감성: NEGATIVE 55 / NEUTRAL 475 / POSITIVE 70
- 원문 학습 URL 중복: 0

공시 Gold는 [공개 코드북](../datasets/k-fnspid-v4-annotation-codebook.md)으로 판정 가능한 사례만 Codex가 검수했다. 등급 우선순위, 감성 override, 근거 필드, 모호 사례 제외, 종목당 상한을 고정했다. 단일 Codex 검수이므로 사람 전문가 간 일치도를 주장하지 않는다.

## 4. 시장반응 라벨

문서의 유효 거래일을 (t), 수정종가를 (P), 동일 시장 평균 수익률을 (r_m)이라 할 때 1·3·5일 종목 복리수익률에서 시장 복리수익률을 차감한다. 과거 60거래일 로그 거래량 z-score와 과거 20거래일 대비 장중 변동성 충격을 추가한다.

materiality score는 다음 가중 합을 0~1로 제한한다.

- 1일 절대 초과수익: 0.50
- 3일 절대 초과수익: 0.20
- 거래량 충격: 0.15
- 변동성 충격: 0.15

합성 점수는 `0 <= s < 0.20`이면 LOW, `0.20 <= s < 0.45`이면 MEDIUM, `0.45 <= s < 0.75`이면 HIGH, `0.75 <= s <= 1`이면 CRITICAL이다. 미래 관측값은 정답 생성에만 사용하므로 이 등급은 인과적 중요도나 거래 신호가 아니다.

## 5. 누수와 교란 통제

본 문서에서 시간 경계 누수는 분할 경계 이후의 문서, 같은 사건의 중복 문서 또는 미래 구간에서 계산한 통계가 이전 구간의 전처리·보정·모델 선택에 영향을 주는 현상을 뜻한다.

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
- LoRA: r=16, alpha=32, dropout=0.1
- 실제 서빙: KF-DeBERTa 0.8 + TF-IDF Logistic Regression 0.2
- 승격: 공개 Test macro F1 0.85 이상, KR-FinBERT-SC 이상, 뉴스·공시 운영 Gold accuracy 0.90 이상

공개 Validation으로 학습한 Logistic stacker도 평가하지만 독립 Test와 운영 Gold gate를 통과하지 못하면 서빙하지 않는다.

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
- 통계: 2,000회 행 단위 paired bootstrap과 거래일 cluster bootstrap 95% 구간, exact McNemar
- source 분석: NEWS와 DISCLOSURE 분리
- 감성 외부 비교: Hana TF-IDF, KR-FinBERT-SC, KF-DeBERTa LoRA, 고정 앙상블, stacker
- 운영 Gold: 감성·의미 중요도 accuracy, macro F1, 클래스별 precision/recall/F1

## 8. 결과

### 8.1 감성 독립 Test

| 모델 | Test | accuracy | macro F1 |
| --- | ---: | ---: | ---: |
| Hana TF-IDF Logistic | 933 | 0.4780 | 0.4423 |
| KR-FinBERT-SC | 933 | 0.7363 | 0.7272 |
| KF-DeBERTa LoRA | 933 | 0.8853 | 0.8850 |
| KF-DeBERTa 80% + TF-IDF 20% | 933 | 0.8842 | 0.8840 |
| Logistic stacker | 933 | 0.8821 | 0.8820 |

Stacker는 독립 Test와 실제 뉴스·공시 Gold에서 고정 앙상블보다 나빠 배포하지 않았다. 고정 앙상블은 뉴스 Gold 80건에서 accuracy 0.9000 / macro F1 0.8642, 공시 Gold 600건에서 accuracy 0.9233 / macro F1 0.8344를 기록했다. 후보와 KR-FinBERT-SC의 paired bootstrap macro F1 차이는 0.1566, 95% CI [0.1262, 0.1877]이며 exact McNemar p=1.51e-18이다. 기존 TF-IDF 대비 차이는 0.4420, 95% CI [0.4033, 0.4802], p=2.37e-73이다. 공개 Test에서 KF-DeBERTa 계열은 비교 모델보다 통계적으로 높지만 이 한 데이터셋만으로 한국 금융 감성 전 분포 SOTA를 주장하지 않는다.

### 8.2 공시 의미 중요도 Gold

| 모델 | Gold | accuracy | macro F1 | CRITICAL F1 |
| --- | ---: | ---: | ---: | ---: |
| 도입 전 통합 중요도 | 600 | 0.7150 | 0.4489 | 0.2619 |
| 제목 전용 ablation | 600 | 0.9700 | 0.8820 | 0.5854 |
| 제목+요약 선택 모델 | 600 | 0.9850 | 0.9470 | 0.8163 |
| 제목+요약+전문 ablation | 600 | 0.9433 | 0.8699 | 0.7188 |
| 선택 모델+코드북 floor | 600 | 1.0000 | 1.0000 | 1.0000 |

제목+요약과 제목 단독은 Validation macro F1 0.9894로 같았고 Brier score가 0.00134 대 0.00156으로 낮은 제목+요약을 선택했다. 전문 포함 뷰의 Validation macro F1은 0.9815였으며 Test에서 성능도 낮았다. 수집한 전문은 데이터셋·시장영향 모델·후속 장문 모델 연구에 보존하되 현재 의미 모델에는 억지로 투입하지 않는다. 기본·스트레스 Gold 910건에서 운영 후보는 accuracy 0.9989 / macro F1 0.9962이며 기존 분석기 대비 accuracy 차이 0.0935, paired bootstrap 95% CI [0.0747, 0.1132], macro F1 차이 0.1764의 CI [0.1420, 0.2132], exact McNemar p=1.14e-24다. ECE는 0.0225, Brier score는 0.0063이다. 다만 Gold는 동일 코드북을 따르는 Codex 단일 판정이므로 완전한 금융전문가 외부 검증이나 독립 다중 평가자 일치도로 해석하지 않는다. 구형 stock-review Gold의 배당 LOW 정의는 v3 코드북의 주주환원 HIGH 정의와 충돌하므로 동일 평가로 합산하지 않는다.

### 8.3 K-FNSPID v4 출처별 시간 Test

| 출처·모델 | Test | accuracy | macro F1 | QWK | ECE |
| --- | ---: | ---: | ---: | ---: | ---: |
| 뉴스 TF-IDF | 9,560 | 0.4715 | 0.3484 | 0.3421 | 0.0453 |
| 뉴스 KF-DeBERTa LoRA | 9,560 | 0.5247 | 0.3745 | 0.4754 | 0.0182 |
| 공시 TF-IDF | 4,615 | 0.3675 | 0.2677 | 0.1125 | 0.0444 |
| 공시 KF-DeBERTa LoRA seed 17 | 4,615 | 0.4750 | 0.3216 | 0.1550 | 0.0441 |
| 출처 라우팅 TF-IDF | 14,175 | 0.4377 | 0.3210 | 0.2552 | 0.0369 |
| 출처 라우팅 KF-DeBERTa LoRA | 14,175 | 0.5085 | 0.3690 | 0.3975 | 0.0259 |

공시 3-seed Test는 accuracy 0.4534±0.0216, macro F1 0.3170±0.0052, QWK 0.1556±0.0007이다. seed 17의 Validation macro F1 0.2471이 seed 42의 0.2419와 seed 73의 0.2419보다 높아 Test를 보지 않고 승격했다. 뉴스 후보 추가 학습 seed 17은 Validation macro F1 0.3770으로 동결 adapter의 0.3823보다 낮아 Test 평가 전에 중단했다.

거래일 cluster bootstrap 2,000회에서 Transformer-minus-baseline macro F1 95% CI는 뉴스 [0.0120, 0.0409], 공시 [0.0264, 0.0806]이고 QWK는 각각 [0.1090, 0.1558], [0.0046, 0.0794]다. 통합 CI는 accuracy [0.0594, 0.0818], macro F1 [0.0351, 0.0608], QWK [0.1178, 0.1649]이며 exact McNemar p=2.29e-55다. 따라서 v3 공유 모델에서 나타났던 공시 회귀를 숨기지 않고 제거했지만, 공시 QWK 하한은 0에 가까워 추가 기간 반복이 필요하다.

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
| 고정 감성 앙상블 vs stacker | 독립 Test·운영 Gold로 결합기 선택 |

모든 ablation은 같은 시간 경계와 동일 Test document ID를 사용해야 하며, 다른 Test 집합의 수치를 한 개선율로 합치지 않는다.

## 10. 재현성·보안

- Python 3.12, `uv.lock`, 고정 base revision
- 모든 실행 seed, 학습률, 유효 batch, scheduler, LoRA 설정, 목적함수, 완료 epoch와 최적 Validation을 report에 기록
- 같은 거래일의 상관 오차를 독립 표본으로 과대 계산하지 않도록 거래일 cluster bootstrap을 우월성 gate로 사용
- artifact는 `safetensors`, 보고서·파일 크기·SHA-256이 모두 일치할 때만 로드
- Hugging Face remote code 비활성화
- 비밀키는 `secrets.local.env`, 로그·report·dataset에 포함하지 않음
- 운영 로더는 gate 실패 시 검증된 TF-IDF 모델로 fail closed

## 11. 한계

- Naver Search 반환 제한과 질의 구성에 따른 선택 편향
- 공시 전문 커버리지 1.24%
- 일봉 사용으로 장중 즉시 반응 분리 불가
- 시장 평균 차감 이후에도 업종·규모·거시 교란 잔존
- 가격반응 중요도는 의미 중요도·인과효과·투자 수익성과 다름
- 공시 Gold는 단일 Codex 검수이며 인간 평가자 간 합의도 없음
- 한국 시장의 동일 라벨 정의를 사용하는 공인 leaderboard 부재

따라서 현재 산출물은 형식·실험·재현성 측면에서 학회 심사 제출이 가능한 데이터셋·시스템 논문이다. 다만 독립 금융 전문가 2인 이상 주석과 외부 DOI 저장소 동결 전에는 외부 Gold 타당성, 공시 가격반응 SOTA 또는 최종 출판 준비 완료를 주장하지 않는다.

## 12. 산출물

- dataset manifest: `data/k_fnspid/v4/manifest.json`
- datasheet: `docs/datasets/k-fnspid-v4-datasheet.md`
- source baseline report/predictions: `reports/k-fnspid-impact-{news,disclosure}-*`
- source Transformer report/predictions: `reports/k-fnspid-impact-{news,disclosure}-transformer-*`
- 공시 반복실험: `reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json`
- paired statistics: `reports/k-fnspid-research-evaluation.json`
- sentiment benchmark: `reports/korean-finance-sentiment-benchmark.json`
- disclosure importance statistics: `reports/disclosure-importance-training-report.json`, `reports/disclosure-importance-research-evaluation.json`
- code and environment: repository commit, `pyproject.toml`, `uv.lock`

## 참고 문헌

- Dong, Z., Fan, X., & Peng, Z. (2024). [FNSPID: A Comprehensive Financial News Dataset in Time Series](https://arxiv.org/abs/2402.06698).
- Son, G., Jeon, H., Hwang, C., & Jung, H. (2024). [KRX Bench: Automating Financial Benchmark Creation via Large Language Models](https://aclanthology.org/2024.finnlp-1.2/). FinNLP 2024.
- Jeon, E., Kim, J., Song, M., & Ryu, J. (2023). [KF-DeBERTa: Financial Domain-specific Pre-trained Language Model](https://huggingface.co/kakaobank/kf-deberta-base). HCLT 2023.
- Son, G., Ko, H., Jung, H., & Hwang, C. (2025). [FINKRX: Establishing Best Practices for Korean Financial NLP](https://aclanthology.org/2025.acl-industry.81/). ACL Industry Track 2025.
- Hwang, B. et al. (2025). [KFinEval-Pilot: A Comprehensive Benchmark Suite for Korean Financial Language Understanding](https://arxiv.org/abs/2504.13216).
- Wang, M., Cohen, S. B., & Ma, T. (2024). [Modeling News Interactions and Influence for Financial Market Prediction](https://aclanthology.org/2024.findings-emnlp.189/). Findings of EMNLP 2024.
- Liao, P.-J. et al. (2026). [Generalized Stock Price Prediction for Multiple Stocks Combined with News Fusion](https://arxiv.org/abs/2603.19286).
- Sun, Y. et al. (2026). [FinTextSim: a domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures](https://doi.org/10.3389/frai.2026.1752103). Frontiers in Artificial Intelligence.
- Liu, Y. et al. (2026). [ExAnte: A Benchmark for Ex-Ante Inference in Large Language Models](https://aclanthology.org/2026.eacl-long.72/). EACL 2026.
- Peng, B. et al. (2026). [MultiFinBen: Benchmarking Large Language Models for Multilingual and Multimodal Financial Application](https://aclanthology.org/2026.acl-long.770/). ACL 2026.
