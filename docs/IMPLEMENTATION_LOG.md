# 구현 기록

## 2026-06-03 하네스 구축
- FastAPI 0.136.1, Python 3.12, uv 기반 프로젝트 생성
- `/api/v1/alerts/analyze` 분석 API 구현
- 자체 Rule Engine과 키워드 기준 금융 NLP 모델 구현
- AI 서비스 토큰 검증 제거
- Spring 컨테이너 전용 내부 네트워크 접근 모델로 문서화
- Git 전략, PR 템플릿, CI 하네스 추가

## 2026-06-04 불필요한 로컬 env 제거
- 모델 artifact 경로는 민감정보가 아니므로 env 파일 관리 대상에서 제거
- 로컬 uvicorn 실행 명령에서 `--env-file .env` 제거

## 2026-06-04 금융 NLP 학습·평가 파이프라인 구축
- 학습 데이터 18건과 평가 데이터 6건으로 확장
- 이벤트, 감성, 중요도 키워드 프로필을 학습하는 trainer 추가
- 평가 스크립트와 `reports/model-evaluation.json` 추가
- 평가셋 기준 이벤트, 감성, 중요도, 종목 매핑 지표 1.0 달성

## 2026-06-04 종목 매핑·중복 제거 보강
- 종목 후보에 `aliases` 필드 추가
- 종목코드, 한글명, 영문명, 별칭 기반 매핑 지원
- 텍스트 등장 순서 기준 대표 종목과 관련 종목 순서 산출
- 공백, 기호, 대소문자 차이를 제거한 중복 키 생성

## 2026-06-04 실제 ML 기반 금융 NLP 전환
- Naver News Search, OpenDART 수집 파이프라인 추가
- 수집 raw와 약지도 라벨 데이터는 gitignore된 `data/raw`, `data/processed`에만 저장
- OpenDART 공시검색에서 12,967건을 수집하고 약지도 라벨링 수행
- 저작권 문제가 없는 합성 금융 문장 증강 corpus 486건 생성
- TF-IDF char n-gram + Logistic Regression 기반 supervised ML 모델 학습
- 이벤트 태그는 One-vs-Rest multilabel classifier로 전환
- 감성·중요도는 keyword scoring이 아닌 학습 모델 추론으로 전환
- 모델 artifact를 `financial_nlp_ml.joblib`로 저장하고 FastAPI 분석 경로에서 로드
- 18건 확장 평가셋 기준 이벤트, 감성, 중요도, 종목 매핑 지표 1.0 달성

## 2026-06-04 뉴스 코퍼스 수집 안정화와 재학습
- Naver News Search 수집에 요청 간격, 재시도, 지수 백오프를 추가
- 429 rate limit 또는 일시 장애로 수집량이 줄어들면 기존 raw 코퍼스를 기본값으로 덮어쓰지 않도록 보호
- provider별 요청 수, 성공 수, rate limit 수, 수집 건수, 완료 여부를 `reports/dataset-collection.json`에 기록
- Naver News Search 1,134건과 OpenDART 12,967건을 병합해 raw 14,101건 구성
- 약지도 라벨 14,101건과 curated·증강 corpus를 사용해 11,898개 중복 제거 학습 샘플로 재학습
- 이벤트 태그 probability threshold를 0.35로 튜닝해 과잉 `GENERAL_MARKET` 예측을 줄임
- 평가 리포트에 이벤트 라벨별 precision, recall, F1과 감성·중요도 confusion matrix 추가
- 18건 평가셋 기준 이벤트 recall 1.0, 이벤트 macro F1 0.9403, 감성 accuracy 1.0, 중요도 accuracy 0.9444, 종목 accuracy 1.0 기록

## 2026-06-04 ML holdout 검증 리포트 추가
- 학습 파이프라인이 전체 학습 샘플을 80:20으로 나눠 holdout 검증을 먼저 수행한다.
- 검증 후 전체 11,898건 학습 샘플로 최종 artifact를 재학습한다.
- 학습 리포트의 `training_sources`는 작업자 로컬 절대경로가 아니라 repo 기준 상대경로로 기록한다.
- holdout split은 학습 9,518건, 검증 2,380건으로 구성된다.
- holdout 기준 이벤트 subset recall 0.9861, 이벤트 macro F1 0.9011, 감성 accuracy 0.9542, 중요도 accuracy 0.9626을 기록했다.
- holdout 리포트는 이벤트 라벨별 precision, recall, F1, support와 감성·중요도 confusion matrix를 포함한다.
- 커밋 코퍼스만으로도 ML artifact 생성과 holdout 최소 성능 기준을 테스트한다.

## 2026-06-04 Gold benchmark 평가셋 확장
- 훈련 증강 corpus를 486건에서 960건으로 확장해 `GENERAL_MARKET`, `DISCLOSURE`, `CORPORATE_ACTION`, `RISK`, `MEDIUM`, `LOW` 케이스를 보강했다.
- `scripts/build_gold_evaluation_data.py`를 추가해 훈련셋과 별도 문장 패턴의 768건 benchmark를 재생성할 수 있게 했다.
- 종목명이 없는 업종·매크로 문장은 종목 라벨을 비워, 텍스트에 없는 종목을 맞히도록 요구하지 않게 정정했다.
- 전체 12,372건 학습 샘플로 모델을 재학습했다.
- holdout 기준 이벤트 subset recall 0.9859, 이벤트 macro F1 0.9024, 감성 accuracy 0.9632, 중요도 accuracy 0.9608을 기록했다.
- 768건 benchmark 기준 이벤트 recall 0.8385, 이벤트 macro F1 0.8592, 감성 accuracy 0.8854, 중요도 accuracy 0.8268, 종목 accuracy 1.0을 기록했다.
- 테스트 기준을 500건 이상 benchmark와 이벤트·감성·중요도·종목 매핑 최소 성능 기준으로 상향했다.

## 2026-06-04 한국어 금융 tokenizer 기반 ML 개선
- 이벤트·중요도 모델 feature extractor를 TF-IDF char n-gram과 한국어 금융 도메인 token n-gram의 병렬 feature로 확장했다.
- 금융 tokenizer는 `잠정실적`, `공급계약`, `유상증자`, `거래정지`, `상장폐지`, `전환사채` 같은 한국어 복합 금융 표현을 띄어쓰기와 기호 차이에 덜 민감하게 추출한다.
- 감성 모델은 gold benchmark 성능 유지를 위해 기존 char n-gram feature를 유지한다.
- 전체 12,372건 학습 샘플로 모델을 재학습했다.
- holdout 기준 이벤트 subset recall 0.9863, 이벤트 macro F1 0.9412, 감성 accuracy 0.9632, 중요도 accuracy 0.9689를 기록했다.
- 768건 benchmark 기준 이벤트 recall 0.8633, 이벤트 macro F1 0.8942, 감성 accuracy 0.8854, 중요도 accuracy 0.8411, 종목 accuracy 1.0을 기록했다.
- 단위 테스트로 금융 tokenizer의 복합어 추출과 학습 artifact 생성을 검증한다.

## 2026-06-04 모델 artifact fail-closed 처리
- 모델 artifact 경로가 없으면 `ModelArtifactNotFoundError`를 발생시킨다.
- artifact 파일이 손상되었거나 필수 payload key가 없으면 `ModelArtifactInvalidError`를 발생시킨다.
- 분석 API는 모델 artifact 오류를 `503 Service Unavailable`과 고정 메시지로 변환해 내부 stack trace를 노출하지 않는다.
- 테스트로 누락 artifact, invalid artifact, 분석 API 503 응답 계약을 검증한다.

## 2026-06-04 라벨별 golden quality gate
- 768건 gold benchmark 평가셋에 이벤트 라벨별 precision, recall, F1, support 하한선을 추가했다.
- `CAPITAL_ACTION`, `CONTRACT`, `CORPORATE_ACTION`, `DISCLOSURE`, `EARNINGS`, `GENERAL_MARKET`, `MACRO`, `RISK` 전 라벨을 개별 gate로 검증한다.
- 감성은 `NEGATIVE`, `NEUTRAL`, `POSITIVE`별 정답 confusion count를 검증한다.
- 중요도는 `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`별 정답 confusion count를 검증한다.
- 평균 지표가 통과해도 특정 이벤트나 중요도 라벨이 무너지는 회귀를 CI에서 차단한다.

## 2026-06-04 중복 제거 키 정규화 개선
- 중복 제거 키 생성 전에 뉴스 제목을 canonical title로 변환한다.
- `[속보]`, `(종합)`, `특징주:` 같은 제목 라벨과 언론사·기자·이메일 꼬리표를 제거한다.
- 같은 이벤트가 매체별 제목 포장 차이로 여러 알림이 되는 문제를 줄인다.
- source type과 종목코드는 해시 입력에 유지해 뉴스·공시 경계와 종목 경계가 섞이지 않게 한다.
- 테스트로 라벨·꼬리표 제거, source type 경계, 종목 경계를 검증한다.

## 2026-06-04 Hana-OmniLens-API 연동 계약 테스트
- Spring `HannahAiAnalysisRequest`, `HannahAiStockCandidate`, `HannahAiAnalysisResponse` record의 JSON 필드명을 AI schema 테스트로 고정했다.
- `POST /api/v1/alerts/analyze`가 별도 `X-HANNAH-AI-SERVICE-TOKEN` 없이 내부 호출 payload를 처리하는지 검증한다.
- 계약 샘플은 공시 기반 공급계약 문장과 `stock_universe` alias를 포함한다.
- 응답 필드 전체, 종목 매핑, `CONTRACT` 이벤트 태그, related stocks, boolean target flag, SHA-256 duplicate key, model version을 검증한다.

## 현재 구현 로직
- 종목 매핑은 전달받은 `stock_universe`에서 종목코드, 한글명, 영문명 포함 여부로 판단한다.
- 이벤트 태그는 한국어 금융 tokenizer feature를 포함한 학습된 multilabel classifier가 산출한다.
- 감성은 char n-gram 기반 학습된 다중 클래스 ML 모델이 분류한다.
- 중요도는 한국어 금융 tokenizer feature를 포함한 학습된 다중 클래스 ML 모델이 분류한다.
- 모델 artifact 누락·손상 시 분석 API는 fail-closed 방식으로 `503`을 반환한다.
- 모델은 Naver 뉴스와 OpenDART 공시에서 수집한 제목·snippet·링크 기반 코퍼스와 사람이 작성한 curated·증강 corpus로 학습된다.
- 중복 제거 키는 source type, 종목코드, 뉴스 라벨·꼬리표를 제거한 정규화 제목을 SHA-256으로 해시한다.

## 학습 방식
- `data/training/financial_alert_corpus.jsonl`에 뉴스·공시 예시와 라벨을 기록한다.
- `scripts/collect_training_data.py`가 외부 공급자에서 raw 후보 데이터를 수집한다.
- 수집기는 장애 시 기존 raw 코퍼스를 보존하고 provider별 수집 상태를 리포트로 남긴다.
- `weak_labeler.py`가 수집 raw에 약지도 라벨을 부여한다.
- `scripts/build_augmented_training_data.py`가 균형 보강용 합성 금융 corpus를 생성한다.
- `scripts/build_gold_evaluation_data.py`가 훈련셋과 별도 문장 패턴의 benchmark 평가셋을 생성한다.
- `scripts/train_ml_model.py`가 80:20 holdout 검증 후 전체 코퍼스로 최종 학습 artifact를 생성한다.
- 이벤트·중요도 모델은 char n-gram과 한국어 금융 token n-gram을 함께 사용한다.
