# 운영

## 실행
```bash
uv sync --all-groups
uv run uvicorn hannah_montana_ai.main:app --reload
```

## 컨테이너
```bash
docker build -t hannah-montana-ai .
docker run --rm --network hana-internal hannah-montana-ai
```

## 네트워크 경계
- 협력사용 `OMNILENS_API_KEY`는 Hana-OmniLens-API에서만 검증한다.
- Hannah-Montana-AI는 별도 토큰을 받지 않는다.
- 운영 배포에서는 AI 컨테이너 포트를 외부에 publish하지 않는다.
- Spring 컨테이너와 AI 컨테이너만 같은 내부 네트워크에 둔다.

## 헬스체크
- `GET /health`

## 추론 audit log
- 분석 API는 요청마다 `hannah_montana_ai.audit.analysis` logger에 JSON audit log를 남긴다.
- 로그에는 `model_version`, `latency_ms`, 예측 이벤트·감성·중요도, 종목코드, 결과 상태를 기록한다.
- 원문 제목, snippet, URL은 로그에 남기지 않고 SHA-256 hash만 기록한다.
- 모델 artifact 누락 같은 실패도 `outcome=failure`, `failure_reason`으로 기록한다.

## 재학습 운영
- 외부 API 키는 `secrets.local.env`에서만 읽고 커밋하지 않는다.
- `scripts/collect_training_data.py`는 Naver News Search와 OpenDART에서 제목·snippet·링크만 수집한다.
- `data/raw`, `data/processed`는 학습 재현성에 필요한 데이터이므로 커밋한다.
- 외부 API 키, access token, 로컬 실행 비밀값은 학습 데이터에 포함하지 않는다.
- weak-label 후보는 teacher confidence gate와 라벨별 quota를 통과한 경우에만 pseudo-label로 승격한다.
- 현재 artifact는 37,278건 수집 후보 중 `RISK`, `CONTRACT`, `CORPORATE_ACTION` 360건 pseudo-label을 이벤트 모델 학습에 반영했다.
- 감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 supervised corpus만으로 학습한다.

## 모델 release report
```bash
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_release_report.py
```

- `reports/model-release-report.json`은 모델 버전, 학습 샘플 수, pseudo-label 승격 내역, holdout·benchmark·실공시·실뉴스 quality gate를 한 파일로 묶는다.
- `overall_status`는 모든 quality gate와 pseudo-label consistency check가 통과할 때만 `pass`가 된다.
- release report는 `reports/ml-training-report.json`, `reports/ml-model-evaluation.json`, `reports/weak-distillation-report.json`에서 결정적으로 생성한다.

## 운영 전 보강
- drift 감시
- 재학습 기준과 rollback 절차
- 배포 환경별 Secret Manager 연동
