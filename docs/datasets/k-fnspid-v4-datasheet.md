# K-FNSPID v4 Datasheet

## 요약

K-FNSPID v4는 한국 상장시장 뉴스·공시와 파일 기반 일별 시세를 연결한 연구·학습 데이터셋이다. 문서 발표 시각을 한국 거래 세션에 맞춰 유효 거래일로 정규화하고, 문서–종목 관계, 사건 cluster, 1·3·5거래일 시장반응, 시간 분할을 별도 Parquet으로 보존한다.

| 항목 | 값 |
| --- | ---: |
| 문서 | 1,247,685 |
| 뉴스 / OpenDART 공시 | 524,696 / 722,989 |
| 문서–종목 관계 | 1,136,118 |
| 시장영향 행 | 715,015 |
| 비혼입 대표 시장영향 행 | 255,168 |
| 일별 시세 | 10,691,998행, 2,800종목 |
| 문서 기간 | 2000-02-03~2026-07-13 |
| 시세 기간 | 2000-01-04~2026-07-13 |
| 평가 Gold | 뉴스 80 + 공시 600 = 680 |

정본 manifest는 `data/k_fnspid/v4/manifest.json`이며 모든 원천·Parquet 파일의 byte 크기와 SHA-256을 기록한다.

공시 Gold의 등급·우선순위·감성 override·제외 기준은 [K-FNSPID v4 공시 주석 코드북](k-fnspid-v4-annotation-codebook.md)에 고정한다.

## 생성 목적

- 한국 금융 뉴스 감성, 공시 중요도, 문서–종목 연결 연구
- 발표 세션과 시장조정 수익률을 반영한 가격반응 중요도 연구
- 과거 문서에서 미래 기간으로 외삽하는 금융 NLP 평가
- Hana Montana AI(KF-DeBERTa + K-FNSPID)의 학습·평가 재현

수익 보장, 자동 주문, 인과효과 추정용 데이터셋이 아니다.

## 원천과 수집

### 뉴스

- 원천: Naver News Search API가 반환한 한국 뉴스 문서
- 보존 필드: 제목, snippet, 원 URL, provider, 발표시각, content hash
- 전문: 권리·수집 정책을 기록한 13,310건
- 검색 API의 질의·최대 반환량 특성 때문에 전체 한국 금융 보도를 완전 열거하지 않는다.

### 공시

- 원천: OpenDART 목록·원문 API
- 문서: 722,989건
- K-FNSPID 연결 원문: 8,972건, 공시 전체의 1.2410%
- 전문 학습셋 공시 원문: 8,976건(내부 정본 4건 포함), 중앙값 2,428자, 평균 6,659.04자, p95 20,000자
- 원문은 32MB 응답 상한, 8초 timeout, 재시도와 ZIP·DART 상태 검증을 적용했다.
- 최종 추가 회수는 5,082건을 시도해 4,976건을 저장했다. 실패 106건은 본문 부족 51건, DART 상태 013 1건, 상태 014 37건, 공개 뷰어 metadata 부재 17건이다.

### 시세

- 정본: `data/market/market_daily_price.parquet`
- DB export를 사용하지 않고 파일 스냅샷만 입력으로 사용한다.
- 종목코드, 시장, 거래일, 수정 OHLCV를 보존한다.

## 구성 파일

| 파일 | 역할 |
| --- | --- |
| `documents.parquet` | 정규화 문서, 발표시각·세션·유효 거래일·전문·사건 cluster |
| `document_entities.parquet` | 문서–종목 관계, 대표/관련 구분과 매칭 근거 |
| `prices_daily.parquet` | 파일 기반 일별 시세 정본 복제본 |
| `market_impacts.parquet` | 초과수익·거래량·변동성·순서형 중요도와 교란 플래그 |
| `annotations.parquet` | 평가 Gold의 감성·중요도·이벤트 근거 |
| `splits.parquet` | 사건 cluster 단위 시간 Train/Validation/Embargo/Test |

## 시간·거래 세션 정규화

- UTC와 KST 발표시각을 모두 보존한다.
- 장 시작 전·정규장 문서는 당일, 장 마감 후·비거래일 문서는 다음 거래일에 연결한다.
- 날짜만 있는 공시는 시각 정밀도를 `DATE`, 세션을 `UNKNOWN`으로 명시한다.
- 시세 시작일보다 이른 문서를 임의로 첫 거래일에 붙이지 않는다.

분할 경계는 다음과 같다.

| 분할 | 범위 | 전체 문서 |
| --- | --- | ---: |
| Train | 2025-12-24 이전 | 395,591 |
| Embargo | 경계 전 7일 | 7,179 |
| Validation | 2026-01-01~2026-03-24 | 40,303 |
| Test | 2026-04-01 이후 | 107,589 |

시장영향 학습은 문서 전체가 아니라 비혼입 사건 대표행을 사용한다. 실제 학습·평가 대표 분할은 뉴스 Train 99,826 / Validation 6,391 / Test 9,560, 공시 Train 119,146 / Validation 584 / Test 4,615다.

## 종목 연결과 사건 교란

- 한국 종목 master의 종목명·alias와 문맥을 사용해 대표/관련 종목을 연결한다.
- 동일 사건의 반복 기사는 title fingerprint와 유효 거래일로 cluster화한다.
- 같은 종목·거래일에 서로 다른 사건 cluster가 둘 이상이면 `confounded=true`로 제외한다.
- 동일 cluster·종목·거래일에서는 정보량이 가장 큰 문서 한 건만 학습 대표로 선택한다.
- 대표 종목 연결 문서는 전체의 72.4076%, 시장영향이 생성된 대표 문서는 94.1199%다.

## 시장영향 라벨

- 1·3·5일 수정종가 수익률에서 같은 시장의 일별 평균 복리수익률을 차감한다.
- 과거 60거래일 로그 거래량 z-score와 과거 20거래일 대비 장중 변동성 충격을 계산한다.
- materiality score는 1일 절대 초과수익 50%, 3일 20%, 거래량 15%, 변동성 15%를 결합한다.
- `<0.20 LOW`, `<0.45 MEDIUM`, `<0.75 HIGH`, `>=0.75 CRITICAL`로 변환한다.
- 미래 시세는 정답 생성에만 사용하고 모델 입력에는 넣지 않는다.

가격반응 라벨은 의미적 중요도나 인과적 효과가 아니라 관측된 시장 충격의 약한 순서형 대리변수다.

## Gold 주석

### 뉴스 Gold

- 실제 뉴스 80건
- 감성·의미 중요도·이벤트·대상 종목 평가에 사용한다.

### 공시 Gold

- 실제 OpenDART 공시 600건, 480종목, 2023~2026년
- 중요도: LOW 250 / MEDIUM 34 / HIGH 287 / CRITICAL 29
- 감성: NEGATIVE 55 / NEUTRAL 475 / POSITIVE 70
- 전문 원천과 겹치는 401건은 의미 중요도 모델 학습 전에 제외해 실제 모델 학습 입력과의 URL 중복은 0건이다.
- 엄격한 제목 코드북으로 판정 가능한 공시만 포함하고 라벨 근거를 각 행에 보존한다.
- Codex 단일 검수이므로 독립 인간 평가자 간 합의도나 전문가 adjudication을 대신하지 않는다.

### 보조 스트레스 Gold

- K-FNSPID v4 정본 annotation 수 680에는 포함하지 않는 별도 연구 평가 파일이다.
- 기본 공시 Gold·전문 원천과 겹치지 않는 실제 공시 310건이며 HIGH 300 / CRITICAL 4 / LOW 6으로 구성된다.
- 기본 Gold 600건의 클래스 균형 평가를 대체하지 않고 중요 공시 분포의 스트레스 평가에만 사용한다.

## 약한 라벨과 Gold 분리

- 수집 원문 라벨은 `RULE_WEAK_SUPERVISION_V2`와 `UNREVIEWED_WEAK_LABEL`로 표시한다.
- 이전 구현처럼 모든 공시를 HIGH로 강제하지 않는다. 정기·행정 공시는 LOW, 지배구조 변경은 MEDIUM, 자본·계약·실적은 HIGH, 존속·거래 치명 위험은 CRITICAL로 분리한다.
- 검수되지 않은 전문 약한 라벨 중 Gold URL과 겹치지 않는 실제 공시 8,302건은 의미 중요도 후보의 supervised 학습에만 사용하고 Gold 평가에는 사용하지 않는다.
- 희소 CRITICAL 경계는 Gold 문장을 복제하지 않은 고정 사건 템플릿 400건으로 보강한다. 이 합성 행은 K-FNSPID 문서·annotation 수와 Gold 성능 표본에 포함하지 않는다.
- 시장영향 모델은 Gold 중요도를 사용하지 않고 시세 기반 라벨만 사용한다.

## 품질 검증

- document ID 중복, 고아 종목 관계, 발표일·유효일 누락 검사
- 최소 500,000문서·3,000,000시세행·2,000종목 규모 gate
- 원천·출력 파일 SHA-256과 byte 크기 검증
- 학습–Gold URL 중복 검사
- 사건 cluster 단위 시간 분할과 7일 embargo
- 모델 비교 시 동일 Test 문서 ID·정답 일치 검사

## 편향과 한계

- Naver Search 질의와 반환 제한에 따른 선택 편향이 있다.
- 공시 전문 커버리지는 1.24%이며 공시 유형별로 균등하지 않다. DART 제한을 우회하지 않았고 제목·snippet 기반 시장영향 ablation 결과를 함께 공개한다.
- 날짜만 있는 공시는 장중/장후를 구분할 수 없다.
- 상장폐지 종목, 종목명 변경, 시세 이력 가용성에 따른 생존·연결 편향이 남는다.
- 일봉으로는 장중 즉시 반응과 같은 날의 미관측 사건을 완전히 분리할 수 없다.
- 시장 평균 차감은 업종·규모·요인 위험을 완전히 통제하지 않는다.
- 공시 Gold는 단일 Codex 코드북 검수이며 사람 전문가 간 일치도는 없다.

## 접근·권리·윤리

- 연구용 스냅샷이며 뉴스·공시 원문의 권리는 각 제공자와 작성자에게 남는다. 이 저장소의 코드 라이선스가 제3자 원문에 대한 재라이선스를 의미하지 않는다.
- 문서별 원 URL·provider·수집 정책을 보존하며 정정·삭제 요청은 다음 dataset version에서 반영하고 변경 내역과 이전 manifest를 남긴다.
- 공개 기업 뉴스·공시를 대상으로 하며 개인 신용·계좌·주문·세무 원문은 포함하지 않는다. 기사에 등장하는 임직원 이름은 기업 사건 문맥 이외의 개인 프로파일링에 사용하지 않는다.
- API credential·인증 토큰은 수집 산출물, manifest, 보고서에 기록하지 않고 secret hygiene gate로 검사한다.
- 모델 출력은 관측 시장 충격의 보조 정보이며 자동 주문, 개인화 투자 권유, 수익 보장에 사용하지 않는다.

## 재현과 버전 관리

- Python 3.12와 `uv.lock` 고정 환경을 사용한다.
- 수집·빌드·학습 명령, seed, base model commit, artifact hash를 보고서에 기록한다.
- Parquet 6개는 documents·prices 두 파일이 GitHub 100MB 단일 파일 한도를 넘으므로 부분 누락 없이 고정 버전 Release 자산으로 함께 배포한다. Git에는 모든 원천 JSONL shard와 6개 파일의 byte·SHA-256 manifest를 보존한다.
- raw JSONL과 전문 학습 shard는 48MB 이하로 분할하고 각 파일의 byte·SHA-256을 manifest에서 검증한다.
- 정정·삭제 시 dataset version을 올리고 기존 manifest를 보존한다.

Release 복원 후 다음 검증이 통과해야 학습 입력으로 사용한다.

```bash
gh release download k-fnspid-v4.0.0 --repo Hana-harmony/Hana-Montana-AI --dir data/k_fnspid/v4 --pattern '*.parquet'
uv run python scripts/restore_k_fnspid_release.py
uv run python scripts/verify_k_fnspid_dataset.py
```
