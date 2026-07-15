# K-FNSPID 도입 전후와 연구 준비도

## 판정

- K-FNSPID v3는 데이터셋·시스템 논문에 필요한 고정 데이터, 시간 외삽 평가, 강한 기준선, 반복 시드, 통계 검정, calibration, ablation을 재현 가능하게 제공한다.
- 공시 원문은 기존 273건에서 K-FNSPID 연결 8,972건으로 확장했고, 모델 학습 입력에서 URL을 제외한 기본 공시 Codex Gold 600건과 완전 비중복 스트레스 Gold 310건을 고정했다.
- 감성은 공개 균형 Test 933건과 뉴스·공시 운영 Gold를 분리해 평가한다. 공개 Test 한 개의 우위만으로 전 분포 SOTA를 주장하지 않는다.
- 시장영향은 동일한 한국어 가격반응 라벨의 외부 leaderboard가 없으므로 동일 시간 Test의 TF-IDF 기준선 대비 거래일 cluster bootstrap 통계적 우월성만 주장한다.
- ACL Rolling Review 장문 익명 심사용 LaTeX·BibTeX·Limitations·Ethics·재현성 부록과 검증 PDF를 완성했다. 최성현 저자 공개 영문본과 한국공학대학교 공식 소속을 표기한 한글 논문도 별도 생성한다. 독립 금융 전문가 다중 주석과 DOI 동결은 제출을 막는 형식 요건이 아니라 논문이 공개한 과학적 한계다. 현재 결과를 투자 수익성이나 인과효과로 해석하지 않는다.

## 비교 기준

- 도입 전: K-FNSPID 최초 병합 전 `main` commit `076e97f8`, `reports/ml-model-evaluation.json`
- 현재: K-FNSPID v3 manifest와 `reports/ml-model-evaluation.json`, `reports/korean-finance-sentiment-benchmark.json`, `reports/k-fnspid-impact-training-report.json`, `reports/k-fnspid-transformer-multiseed-report.json`, `reports/k-fnspid-research-evaluation.json`
- 비교 원칙: 동일 평가셋의 동일 지표만 전후 비교한다. 공개 Test와 운영 Gold는 분포와 표본이 다르므로 하나의 개선율로 합치지 않는다.

## 데이터와 로직 변화

| 영역 | 도입 전 | 현재 |
| --- | --- | --- |
| 데이터 | 소규모 supervised·pseudo label과 뉴스 80건·공시 30건 Gold | K-FNSPID v3 문서 550,662건, 문서–종목 관계 819,772건, 시장영향 398,942건, 비혼입 시장영향 130,566건 |
| 시세 | 뉴스 분류 학습에 미사용 | 파일 기반 일별 시세 10,691,998행·2,800종목, 2000-01-04~2026-07-13 |
| 감성 | TF-IDF Logistic Regression + 규칙 | KF-DeBERTa LoRA 80% + 기존 모델 20% 확률 앙상블, 독립 gate 실패 시 기존 모델 fallback |
| 의미 중요도 | 텍스트 의미·출처·규칙만 사용 | Validation으로 선택한 제목+요약 약지도 모델과 존속위험 floor를 추가해 기본 Gold 모델 단독 macro F1 0.9470, 운영 전체 910건 accuracy 0.9989 / macro F1 0.9962. 시장영향과 등급 분리 |
| 시장영향 | 없음 | 시세 약지도 등급·점수·confidence를 별도 API 필드로 제공 |
| 라벨 | 사람이 정의한 감성·중요도 | 감성은 공개·운영 라벨, 시장영향은 1·3·5일 초과수익·거래량·변동성으로 생성한 약한 순서형 라벨 |
| 시간 누수 | 텍스트 holdout 중심 | 거래 세션별 유효일, 시간순 Train/Validation/Embargo/Test, 미래 시세는 라벨 생성에만 사용 |
| 사건 교란 | 별도 제어 없음 | 같은 종목·거래일 다중 사건 제외, cluster 대표 선택, 시장 평균 수익률 차감 |
| 배포 | 단일 joblib | 고정 base revision·LoRA `safetensors`·파일별 SHA-256·검증 시드 선택·원자적 승격·fail-closed fallback |

## 평가 원칙

- 도입 전후 비교는 같은 평가셋과 같은 지표끼리만 수행한다.
- 기본 공시 Gold 600과 겹치는 원천 전문 401건은 의미 중요도 모델 학습 전에 제외해 실제 학습 입력 중복을 0으로 만든다. 스트레스 Gold 310은 원천 전문·기본 Gold와 모두 중복이 0이다.
- 가격반응 등급 Test 10,750은 2026-04-01 이후의 시간 외삽 집합이며 모델 선택에 쓰지 않는다.
- 반복 시드 17/42/73 중 배포 시드는 Validation macro F1로만 선택한다. Test는 세 시드 평균·표준편차와 선택 모델의 고정 평가를 보고한다.
- accuracy 외에 macro F1, 클래스별 precision/recall/F1, quadratic kappa, ECE, Brier score를 함께 본다.

## 동일 운영 평가 전후

| 평가셋 | 지표 | 도입 전 | 현재 | 변화 |
| --- | --- | ---: | ---: | ---: |
| Benchmark 768 | 감성 accuracy | 0.9688 | 0.9492 | -0.0195 |
| 실제 공시 Gold | 감성 accuracy·macro F1 | 기존 30건 | v3 Codex Gold 600건 | 표본과 코드북이 달라 직접 증감 계산 금지 |
| 실제 뉴스 Gold 80 | 감성 accuracy | 0.9750 | 0.9000 | -0.0750 |
| Stock review Gold 500 | 감성 accuracy | 0.9180 | 0.7880 | -0.1300 |
| Benchmark 768 | 중요도 accuracy | 0.9583 | 0.9323 | v3 코드북 변경으로 직접 증감 금지 |
| 실제 공시 Gold | 중요도 accuracy·macro F1 | 기존 30건 | v3 Codex Gold 600건 | 표본과 코드북이 달라 직접 증감 계산 금지 |
| 실제 뉴스 Gold 80 | 중요도 accuracy | 0.9625 | 0.9500 | -0.0125 |
| Stock review Gold 500 | 중요도 accuracy | 0.8480 | 0.8060 | -0.0420 |

이벤트는 DART 제목에 v3 코드북 우선순위를 적용했다. Benchmark macro F1은 0.9844를 유지했고, 새 공시 Gold 600건은 0.9979다. 실제 뉴스 Gold는 `0.9221→0.9184`, Stock review Gold는 `0.7307→0.7110`으로 하락했다. Stock review 종목 정확도도 `0.9940→0.9900`으로 하락했으므로 운영 분포 회귀를 별도 한계로 유지한다.

## 새 평가에서 확인된 개선

### 한국 금융 감성

균형 공개 Test 933건에서 기존 Hana TF-IDF macro F1은 `0.4423`, KR-FinBERT-SC는 `0.7272`, KF-DeBERTa LoRA 단독은 `0.8850`, 실제 서빙 80:20 앙상블은 `0.8840`이다. 이 결과는 공개 평가 분포에서 모델 표현력이 개선됐다는 증거지만 기존 운영형 회귀를 무효화하지 않는다.

### K-FNSPID v3 시장영향

| 모델 | Test 표본 | accuracy | macro F1 | quadratic kappa |
| --- | ---: | ---: | ---: | ---: |
| TF-IDF Logistic 기준선 | 10,750 | 0.4643 | 0.3429 | 0.3141 |
| KF-DeBERTa LoRA seed 73 선택 모델 | 10,750 | 0.5095 | 0.3820 | 0.4694 |
| KF-DeBERTa LoRA 3-seed 평균±표본표준편차 | 10,750 | 0.5105±0.0080 | 0.3824±0.0102 | 0.4675±0.0042 |

Transformer 결과는 `reports/k-fnspid-transformer-multiseed-report.json`과 `reports/k-fnspid-research-evaluation.json`이 단일 원천이다. 동일 정의의 공개 한국 시장 leaderboard가 없어 이 수치만으로 외부 SOTA를 선언하지 않는다.

## 논문으로 만들 수 있는 주장

- 한국 공개 뉴스·공시와 일별 시세를 연결한 55만 문서 규모의 파일 기반 재현 가능 데이터셋을 구축했다.
- 발표 시각과 거래 세션을 반영한 유효 거래일, 시간 embargo, 사건 cluster, 다중 사건 제외를 결합했다.
- 시장영향 Transformer는 같은 시간 외삽 Test에서 TF-IDF 기준선을 넘는 경우에만 승격하며, 다중 시드 통계 결과를 그대로 보고한다.
- 공개 감성 Test와 실제 운영 Gold를 분리해 평가하면 분포별 성능 차이가 크게 나타난다.

현재 주장하면 안 되는 내용은 `한국 금융 뉴스 감성 전 분포 SOTA`, `가격 반응 등급이 인과적 의미 중요도다`, `이 모델이 수익성 있는 투자 신호다`이다. 공시 910건에서 accuracy와 macro F1 개선 구간은 모두 0을 넘지만, 같은 코드북의 Codex 단일 판정 Gold이므로 독립 금융전문가 다중 평가 결과로 확대 해석하지 않는다.

## 연구 gate 현황

| gate | 상태 | 근거 또는 남은 범위 |
| --- | --- | --- |
| 완전 미사용 Gold 500~1,000건 | 완료 | 뉴스 80 + 기본 공시 600, 별도 비중복 공시 stress 310 |
| 독립 전문가 다중 주석·평가자 합의도 | 외부 한계 | 현재 요청 범위대로 Codex 단일 코드북 검수이며 사람 합의도로 표현하지 않음 |
| 3개 seed·bootstrap·McNemar | 완료 | seed 17/42/73, 행·70거래일 cluster 각 2,000회, exact McNemar |
| 시간·source OOD와 calibration | 부분 완료 | 2026-04 이후 시간 Test·NEWS/DISCLOSURE·ECE/Brier 완료, 시장 국면·업종·규모별 OOD는 후속 |
| ablation | 부분 완료 | TF-IDF 입력·source·학습량, 공시 입력 뷰 완료. 모든 목적함수·세션 통제를 하나씩 제거한 실험은 후속 |
| 강한 동일 split 기준선 | 완료 범위 | 시장영향 TF-IDF, 감성 Hana TF-IDF·KR-FinBERT-SC·KF-DeBERTa·stacker 비교. full fine-tune는 자원 한계로 미수행 |
| 라벨·교란 민감도 | 부분 완료 | 세션·시장조정·다중 사건·cluster 통제 완료, 장중·요인모형·threshold 민감도는 후속 |
| 의미 중요도와 가격반응 분리 | 완료 | 모델·API 필드·confidence·평가를 분리하고 시장영향이 의미 등급을 변경하지 않음 |
| Datasheet/Data Statement | 완료 | 원천·권리·개인정보·삭제·편향·manifest·재현 절차 기록 |
| 고정 공개 보관 | 부분 완료 | GitHub Release와 SHA-256 manifest는 본 작업에서 동결, DOI 저장소 등록은 외부 절차 |

## 투고 현실성

- 현재 산출물은 ACL Rolling Review 장문 익명 심사에 업로드 가능한 데이터셋·시스템 논문 제출 패키지다. 본문 5쪽·전체 7쪽, 초록 177단어, A4 2단 review style, 13개 폰트 내장, 7쪽 시각 검수를 완료했다.
- 다중 seed 통계적 유의성과 강한 동일 split 기준선은 확보했지만, DISCLOSURE 시장영향 하위집합 회귀 때문에 전 source 모델 SOTA 주장은 할 수 없다.
- 독립 전문가 다중 주석, 시장 국면·업종별 OOD, DOI 동결을 추가하면 채택 가능성과 카메라레디 완성도가 높아진다. 이는 현재 Codex Gold 결과를 숨기지 않고 Limitations·Ethics 본문에 명시했다.
- 제출 원고와 manifest는 `docs/paper/acl/`에 있다. 검증 PDF는 익명 심사용 `output/pdf/k-fnspid-v3-arr-review.pdf`, 저자 공개 영문 `output/pdf/k-fnspid-v3-author-preprint.pdf`, 한글 `output/pdf/k-fnspid-v3-ko.pdf`로 분리한다. 논문 수치는 `scripts/paper/verify_k_fnspid_submission.py`가 동결 JSON과 대조한다.

## 연구 설계 참고

- [FNSPID](https://arxiv.org/abs/2402.06698): 뉴스와 시세를 장기간 연결한 원 데이터셋 설계 비교
- [KRX-Bench](https://aclanthology.org/2024.finnlp-1.2/): 한국 금융 벤치마크와 평가 harness 참고
- [FINKRX](https://aclanthology.org/2025.acl-industry.81/): 한국 금융 LLM 공개 instruction·leaderboard 운영 참고. QA·주가 방향 지식 과제이므로 본 연구 지표와 직접 순위 비교하지 않음
- [Data Statements for NLP](https://aclanthology.org/Q18-1041/): 언어 데이터 구성·편향 문서화 기준
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010): 데이터셋 동기·구성·수집·유지보수 문서화 기준
- [Temporal Distribution Shifts in Financial Sentiment](https://aclanthology.org/2023.emnlp-main.65/): 금융 감성의 시간 분포 이동 평가 필요성
- [FININ](https://aclanthology.org/2024.findings-emnlp.189/): 뉴스 상호작용과 시세를 결합한 다중모달 시장예측 비교. Sharpe 과제라 직접 수치 비교하지 않음
- [Generalized Stock Price Prediction with News Fusion](https://arxiv.org/abs/2603.19286): 종목 임베딩·뉴스 attention·가격 이력 융합의 최신 방향 참고. MAE 과제라 직접 수치 비교하지 않음
- [FinTextSim](https://doi.org/10.3389/frai.2026.1752103): 공시 특화 표현과 일반·감성 임베딩의 예측 유효성 절제 비교 참고. 언어·라벨이 달라 K-FNSPID 수치와 직접 순위 비교하지 않음
- [ExAnte](https://aclanthology.org/2026.eacl-long.72/): 미래 예측에서 cutoff 이후 지식 누출을 별도 측정해야 한다는 최신 평가 기준 참고
- [MultiFinBen](https://aclanthology.org/2026.acl-long.770/): 전문가 검증 다언어·다중모달 금융 benchmark의 최신 범위 참고. 현재 한국어 텍스트·일봉 과제와 직접 점수 비교하지 않음
