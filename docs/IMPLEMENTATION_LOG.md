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

## 현재 구현 로직
- 종목 매핑은 전달받은 `stock_universe`에서 종목코드, 한글명, 영문명 포함 여부로 판단한다.
- 이벤트 태그는 학습된 multilabel classifier가 산출한다.
- 감성은 학습된 다중 클래스 ML 모델이 분류한다.
- 중요도는 학습된 다중 클래스 ML 모델이 분류한다.
- 중복 제거 키는 source type, 종목코드, 정규화 제목을 SHA-256으로 해시한다.

## 학습 방식
- `data/training/financial_alert_corpus.jsonl`에 뉴스·공시 예시와 라벨을 기록한다.
- `scripts/collect_training_data.py`가 외부 공급자에서 raw 후보 데이터를 수집한다.
- `weak_labeler.py`가 수집 raw에 약지도 라벨을 부여한다.
- `scripts/build_augmented_training_data.py`가 균형 보강용 합성 금융 corpus를 생성한다.
- `scripts/train_ml_model.py`가 학습 artifact를 생성한다.
