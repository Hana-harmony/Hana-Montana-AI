# 구현 기록

## 2026-07-15 09:20 KST · 저자 공개본·한글 논문 분리

- ARR 익명 심사용 원고는 저자 정보를 계속 제거하고, 같은 영문 본문을 입력하는 `Sunghyun Choi` 저자 공개본을 추가해 실험 수치 drift를 차단했다.
- 학교 공식 표기에 맞춰 한국공학대학교 SW대학 컴퓨터공학부 소프트웨어전공과 4학년 학부생 신분을 저자 메타데이터에 기록했다. 제공되지 않은 이메일·ORCID는 생성하지 않았다.
- 동일 실험·실패 분석·한계·윤리·재현성을 담은 4쪽 A4 2단 한글 논문을 추가했다. 세 PDF 총 18쪽의 렌더링과 폰트 내장 여부를 검수했다.
- 빌드가 세 PDF의 byte·쪽수·SHA-256을 제출 manifest와 대조하도록 fail-closed 검증을 추가했다.

## 2026-07-14 11:20 KST · v3 코드북·공시 이벤트·종목 연결 일치화

- 과거 합성 학습·평가의 거래정지·불성실공시 CRITICAL 라벨을 v3 코드북의 HIGH로 재생성하고 TF-IDF 기준 artifact를 실제 55만 건 약지도 원천에서 재학습했다.
- 구조화 DART 제목의 이벤트는 v3 코드북 우선순위로 분리해 뉴스용 광범위 키워드 오탐을 차단했다. 공시 Gold 600건은 event macro F1 0.9979, stock accuracy 1.0이며 release gate를 통과한다.
- 회사명에 포함된 `리서치`를 증권사 인용으로 오인하던 span 문맥 버그를 수정해 씨엔알리서치·파마리서치바이오 종목 연결 누락을 제거했다.
- 기존 운영 평가 회귀를 숨기지 않고 실제 뉴스·Stock review 이벤트·중요도 하락과 v3 코드북 변경으로 직접 비교할 수 없는 지표를 모델 문서에 분리했다.
- 약지도 파생 shard는 Git 추적 raw 12개와 종목 universe에서 오프라인 재생성하는 스크립트를 추가하고 release lineage의 잘못된 `processed tracked` 표현을 수정했다.

## 2026-07-14 10:43 KST · 논문급 다중 seed·통계 평가 확정

- 전체 Train 107,175건으로 seed 17/42/73 KF-DeBERTa LoRA를 동일 설정에서 학습하고 Validation macro F1로 seed 73을 선택했다. 시간 Test 10,750건은 accuracy 0.5095 / macro F1 0.3820 / QWK 0.4694다.
- 거래일 cluster bootstrap 2,000회에서 TF-IDF 대비 accuracy·macro F1·QWK 차이 95% CI가 모두 0을 넘고 exact McNemar p=1.70e-20임을 확인했다. 공시 하위집합 macro F1 회귀와 ECE 악화도 함께 기록했다.
- 통계 evaluator가 중복 document ID, paired 종목·출처·거래일 불일치, 잘못된 확률벡터를 거부하도록 강화하고 우월성 gate에 세 군집 지표와 McNemar를 모두 포함했다.
- 장시간 학습 CLI 경로를 프로젝트 내부 절대경로로 정규화하고 checkpoint 재개를 지원해 마지막 report 기록 실패를 전체 재학습 없이 검증된 상태에서 복구했다.

## 2026-07-14 03:30 KST · 논문 provenance·독립 신호·통계 gate 강화

- 재샤딩 전 전문 4개 파일을 가리키던 K-FNSPID 최상위 manifest를 실제 raw 12개·전문 7개 shard로 재생성했다. 6개 Parquet SHA가 모두 동일함을 확인하고 Test 10,750건의 문서 ID·정답·예측 SHA를 대조한 provenance 정정 이력을 기준선과 seed 42 보고서에 남겼다.
- dataset verifier가 Parquet뿐 아니라 raw/full-content/종목/시세/Gold 원천의 경로 탈출·symlink·byte·개별 및 복합 SHA를 검증하도록 강화했다. 작업트리 시세 symlink도 동일 SHA의 실제 226MB 파일로 교체했다.
- 시장영향이 의미 중요도 라벨뿐 아니라 confidence도 변경하지 않도록 완전히 분리하고, 부도·파산·상장폐지 등 코드북상 치명위험 표현에만 CRITICAL 안전 floor를 적용해 기존 운영 평가 회귀를 차단했다.
- 시장영향 학습 입력의 대표 종목명이 서빙에서 빠지고 summary-only snippet이 두 번 들어가던 feature skew를 제거해 제목·요약·전문·대표 종목명·source prefix 순서를 KF-DeBERTa와 TF-IDF 모두 동일하게 맞췄다.
- 논문 우월성 gate를 행 단위 paired bootstrap에서 70개 거래일 cluster bootstrap으로 강화했다. seed 42 예비 200회 검정에서 macro F1 차이 95% CI는 [0.0365, 0.0639]였으며 최종 보고는 Validation 선택 다중 seed와 2,000회 검정을 사용한다.
- 반복 seed 표준편차는 population이 아닌 sample 표준편차로 교정하고, 제목·요약·전문 입력별 공시 중요도 ablation을 독립 재현하는 스크립트를 추가했다.
- 공시 입력 ablation에서 제목+요약이 기본 Gold accuracy 0.9850 / macro F1 0.9470으로 전문 포함 0.9433 / 0.8699보다 높았다. Gold는 선택에 쓰지 않고 2026 Validation macro F1 동률 뒤 Brier score가 낮은 제목+요약 뷰를 선택하는 v3 artifact로 재학습했다.
- 거래정지·불성실공시 단독을 CRITICAL로 올리던 규칙을 코드북의 HIGH 정의에 맞췄다. 상장폐지·횡령/배임·감사의견거절·부도·회생·파산만 안전 floor로 유지한 운영 파이프라인은 비중복 기본·스트레스 Gold 910건에서 accuracy 0.9989 / macro F1 0.9962, 기존 분석기 대비 paired accuracy 차이 95% CI [0.0747, 0.1132], McNemar p=1.14e-24를 기록했다.
- Release 복원기가 6개 Parquet의 byte·SHA-256을 검증하고 `prices_daily.parquet`을 DB가 아닌 `data/market/market_daily_price.parquet` 실제 파일로 원자 복원하도록 추가했다.
- AI와 API 양쪽에서 시장영향 등급·점수·confidence가 모두 있거나 모두 없도록 계약을 강화하고, 기계 판독 모델 감사가 공시 중요도·다중 seed·날짜군집 연구 gate를 실제 report에서 집계하도록 v2로 확장했다.

## 2026-07-14 02:05 KST · 논문 재현 데이터 공급망 강화

- 28,703행 실제 전문 학습셋을 행 손실 없이 최대 48MB의 7개 JSONL shard로 재분할해 Git 추적과 PR 검토를 유지했다.
- raw 12개·전문 7개 shard manifest에 파일 byte·SHA-256을 기록하고, 로더가 경로 탈출·symlink·중복 경로·누락된 무결성 항목·변조 파일을 fail closed하도록 강화했다.
- FINKRX, FININ, 2026년 뉴스·가격 융합 연구를 최신 비교군에 추가하고 과제·시장·지표가 다른 결과를 직접 SOTA 순위로 사용하지 않도록 논문 주장 범위를 고정했다.

## 2026-07-13 23:55 KST · K-FNSPID v3 공시 전문·의미 중요도 고도화

- OpenDART 전문 추가 후보 5,065건을 병렬·재개 가능 수집해 4,976건을 추가했고, K-FNSPID 연결 공시 전문을 8,972건(34.55%)으로 확장했다.
- K-FNSPID v3 정본은 문서 550,662건, 문서–종목 819,772건, 시장영향 398,942건, 비혼입 대표행 130,566건이며 manifest의 byte·SHA-256 gate를 통과했다.
- 공시 의미 중요도 모델을 Gold URL을 제외한 약지도 실공시 8,302건과 치명위험 어휘 템플릿 400건으로 학습했다. 제목 전용 입력 결함을 제거하고 전문까지 연결한 v2는 기본 Gold 600건에서 accuracy 0.9433 / macro F1 0.8699를 기록했다. Validation temperature 0.6으로 Gold ECE를 0.1444까지 교정했다.
- 학습 입력·기본 Gold와 겹치지 않는 실제 공시 스트레스 Gold 310건을 추가했다. 통합 910건 accuracy는 기존 0.9055 대비 0.9538이며 McNemar p=0.000125다.
- 의미 중요도와 시세 기반 시장영향을 분리했다. 시장영향은 `market_impact_importance`, `market_impact_score`, `market_impact_confidence`로 독립 전달하며 의미 등급을 변경하지 않는다.
- 감성 후보는 공개 Test에서 KR-FinBERT-SC 대비 macro F1 차이 0.1566, paired bootstrap 95% CI [0.1262, 0.1877], exact McNemar p=1.51e-18을 기록했다.
- 아래 18:30 기록의 공시 Gold 1.0000과 이전 시장영향 Test 수치는 당시 소규모 평가·v2 스냅샷의 역사적 결과다. 현재 주장은 v3 Gold 600건 0.9233과 시간 Test 10,750건 보고서를 사용한다.

## 2026-07-13 20:42 KST · K-FNSPID 도입 전후·연구 주장 감사

- K-FNSPID 도입 직전 `main` commit `076e97f8`을 비교 기준으로 고정하고 현재 평가 보고서와 동일 평가셋끼리 대조했다.
- 공개 금융 감성 Test 개선과 기존 운영형 감성 회귀를 분리해 기록하고, 중요도 운영 Gold 정확도가 변하지 않았음을 명시했다.
- K-FNSPID 시장영향의 정확도·macro F1·quadratic kappa 기준선 개선과 최종 중요도 정확도 미개선을 구분했다.
- 독립 다중 평가자 Gold, 반복 seed·신뢰구간·통계 검정, 강한 ablation, 시계열·시장 국면 외삽 검증 전에는 논문 준비 완료나 전 분포 SOTA를 주장하지 않도록 연구 gate를 문서화했다.

## 2026-07-13 18:30 KST · K-FNSPID v2 대규모·KF-DeBERTa 승격 파이프라인

- Naver 뉴스 528,520건과 OpenDART 25,966건을 12개 JSONL shard로 수집하고, K-FNSPID v2 정본 550,662건을 생성했다.
- KOSPI·KOSDAQ·KONEX 2,800종목의 2000-01-04~2026-07-13 일별 시세 10,691,998행을 DB가 아닌 236.5MB Parquet 파일로 고정했다.
- 시세 이전 기사의 첫 거래일 오연결, 장 마감 후 오라벨, 다른 날의 반복 제목 cluster 합침, 동일 다중 사건 혼입을 차단했다.
- 비혼입 시장영향 130,311건에서 중복 사건 대표를 고르고 7일 embargo 시간 분할을 생성했다.
- `mssongit/finance-task` 고정 리비전과 운영형 학습 자료로 KF-DeBERTa LoRA 금융 감성을 다중 도메인 학습하고 공개 replay 기반 2차 적응을 수행했다. 누적 학습 노출 18,139건이며, 80:20 확률 앙상블은 공개 Test 933건 macro F1 0.8840, 실제 공시 Gold accuracy 1.0000, 실제 뉴스 Gold accuracy 0.9000으로 KR-FinBERT-SC 0.7272와 기존 TF-IDF 0.4423을 상회했다.
- K-FNSPID 영향도 KF-DeBERTa LoRA는 시간순 Test 10,728건에서 macro F1 0.3664, quadratic kappa 0.4186으로 TF-IDF 기준선 0.3613, 0.3515를 모두 상회해 서빙으로 승격했다.
- 모델 리비전, `safetensors`, artifact SHA-256, 독립 벤치마크 gate를 모두 통과해야 Transformer를 서빙하고 실패 시 기존 모델로 fail closed하게 했다.
- Docker는 non-root, read-only root filesystem, capability 전체 제거, no-new-privileges, PID 제한, noexec tmpfs, runtime offline model 로딩으로 강화했다.

## 2026-07-13 06:30 KST · K-FNSPID Docker 품질 gate 패키징

- Docker 이미지에 시장영향 모델뿐 아니라 독립 Test 품질 gate 보고서를 읽기 전용으로 함께 포함한다.
- 런타임 패키징 회귀 테스트로 보고서 누락 시 시장영향 모델이 비활성화되는 배포 오류를 차단한다.

## 2026-07-13 06:00 KST · 파일 기반 K-FNSPID와 시장영향 결합

- 네이버 뉴스와 OpenDART 원천의 발표 시각을 UTC·KST로 보존하고 거래 세션과 유효 거래일을 계산한다.
- `market_daily_price` DB에 의존하지 않고 공개 시세 원천을 정규화한 Parquet 파일 1,239,658행을 데이터셋에 포함한다.
- K-FNSPID v1은 문서 81,689건, 문서–종목 관계 124,491건, 시장영향 50,972건이며 중복 ID·날짜 누락·고아 관계 품질 gate를 통과한다.
- Aho-Corasick exact-context linker와 한글·영문 경계를 사용해 `VCC`가 `브이씨`로 연결되는 부분 문자열 오탐을 차단한다.
- 동일 기사 군집, 시장조정수익률, 거래량 z-score, 변동성 충격, 7일 embargo 시간 분할을 재현 가능한 스크립트로 생성한다.
- 실제 뉴스 Gold 80건을 Codex가 검수하고 명확한 대상 관점 오류 3건을 교정했으며 발표 시각과 원천 해시를 복원했다.
- K-FNSPID 시장영향 모델은 독립 시간 Test gate를 통과한 경우에만 기존 중요도와 보수적으로 결합한다.
- KR-FinBERT-SC와 동일 Gold 비교를 실행하고 학습 중복 행은 평가에서 제외한다.

## 2026-07-11 14:23 KST · 활성 일반주식 전체 글로벌 피어·glossary 경계 보강

- KIS 공식 마스터의 KOSPI·KOSDAQ·KONEX 활성 일반주식 2,752개를 모델 universe의 단일 기준으로 사용한다.
- 한국 종목별 고정 peer·headline·비교·강점 anchor와 14개 pairwise 정답 라벨을 제거했다. 모든 요청은 사업 태그, KSIC 업종, 사업 요약, TF-IDF, 잠재 의미, 재무 규모, 글로벌 인지도 신호를 실시간 조합해 후보를 점수화한다.
- 활성 2,752종목 전체 추론으로 2,752/2,752 성공, 고유한 3개 비교, 근거가 있는 4개 Key Strength, 동일 회사 중복 0건을 검증한다.
- 영문 glossary alias 전체에 양쪽 영숫자 단어 경계를 적용한다. `ant`는 `participant`, `significant`, `antitrust`에서, 다른 alias도 더 긴 영문 단어 내부에서 인식되지 않는다.
- 재학습 아티팩트는 `0644`로 교체하고 이미지 빌드 시 `0444`로 고정해 non-root serving 계정의 읽기 실패를 방지한다.
- `primaryPeer`·headline·peers 첫 항목을 Global Comparison 1순위와 동일하게 구성해 대표 피어와 실제 비교 카드가 엇갈리지 않게 한다.

## 2026-07-11 06:00 KST · 기능별 serving 계약 단일화

- 한국 금융 용어는 단일 dictionary, 글로벌 피어 설명은 grounded template, 뉴스 What/Why/Impact는 rule, 한국어 번역은 로컬 Qwen 4B GGUF HTTP로 고정했다.
- 네 기능의 mode 설정을 제거하고 알 수 없는 Settings 필드는 fail-fast 처리한다.
- 글로벌 피어·뉴스·금융 용어용 Qwen/MLX 클라이언트, LoRA adapter, 학습 데이터·스크립트·평가 리포트와 `mlx-lm` 의존성을 삭제했다.
- 한국어 번역의 직접 MLX와 local glossary 분기를 삭제해 로컬 Docker와 배포 서버가 같은 Qwen endpoint 계약을 사용한다.
- 금융 용어 seed를 분석 glossary의 단일 원천으로 연결하고 30개 이상으로 확장했다.
- 표면형을 `개미 → Ant`, `대장주 → Daejangju`로 정정하고 동학개미·서학개미·빚투·영끌·존버·물타기·불타기·상따·하따 등을 분리했다.
- Qwen 번역과 rule 요약 모두 `Ant`, `Daejangju`, `Bittu` 표면형을 유지한다.
- Qwen 번역기도 동일한 seed를 직접 로드해 호출자가 glossary를 누락해도 dictionary 표기를 프롬프트·후처리에 강제한다.
- `개미`를 `Insects`, `대장주`를 `blue chips`로 바꾸는 Qwen 의역도 각각 `Ant`, `Daejangju`로 정규화한다.

## 2026-07-08 18:51 KST · 세무 서류 OCR

- `/api/v1/tax/documents/verify`가 이미지/PDF payload를 공통 `TaxDocumentPipeline`으로 검증한다.
- Tesseract `kor+eng` OCR, 문서별 parser/reviewer, 위변조·필수필드 gate를 사용한다.
- OCR 불가 입력은 임의 통과시키지 않고 명시적 실패 사유를 반환한다.
