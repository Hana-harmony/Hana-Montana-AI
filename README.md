# Hannah-Montana-AI

Hana-OmniLens-API의 뉴스·공시 알림 분석을 담당하는 FastAPI 기반 자체 금융 NLP 서비스다.

## 범위
- 종목 매핑
- 이벤트 분류
- 감성 분류
- 중요도 분류
- 중복 제거 키 생성

## 빠른 시작
```bash
uv sync --all-groups
uv run pytest
uv run python scripts/verify_secret_hygiene.py
uv run uvicorn hannah_montana_ai.main:app --reload
```

로컬 Docker 실행:
```bash
docker compose -f compose.local.yml up --build
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## 학습 파이프라인
```bash
uv run python scripts/collect_training_data.py --reuse-existing-raw --max-news-per-query 1000 --dart-days 365 --dart-pages 10
uv run python scripts/build_augmented_training_data.py
uv run python scripts/build_gold_evaluation_data.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_release_report.py
uv run python scripts/build_pseudo_label_monitoring_report.py
```

로컬 외부 API 키는 `secrets.local.env.example`을 복사한 뒤 커밋하지 않는 `secrets.local.env`에서만 작성해 읽는다.
수집 credential은 학습 데이터 수집 스크립트에서만 사용하며, AI 런타임은 provider credential이나 협력사용 API key를 요구하지 않는다.
수집 실패나 rate limit으로 새 raw 수가 기존보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
수집된 대량 weak-label 후보는 supervised teacher 모델의 confidence gate와 라벨별 quota를 통과한 pseudo-label만 이벤트 모델 학습에 승격한다.
학습 결과는 `reports/ml-training-report.json`의 80:20 holdout 검증, `reports/ml-model-evaluation.json`의 gold 평가셋 지표, `reports/model-release-report.json`의 버전별 release gate, `reports/pseudo-label-promotion-monitoring.json`의 pseudo-label 운영 상태로 기록한다.

AI 서비스는 협력사용 `OMNILENS_API_KEY`나 별도 서비스 토큰을 요구하지 않는다. 배포 환경에서는 외부에 포트를 공개하지 않고 Spring 컨테이너에서만 접근 가능한 내부 네트워크로 격리한다.

## 주요 엔드포인트
- `GET /health`
- `POST /api/v1/alerts/analyze`

분석 API는 응답 계약을 유지하면서 내부 audit log에 모델 버전, latency, 예측 라벨, 입력 hash를 남긴다.

## 문서
- [기여 가이드](CONTRIBUTING.md)
- [아키텍처](docs/ARCHITECTURE.md)
- [운영](docs/OPERATIONS.md)
- [보안](docs/SECURITY.md)
- [테스트](docs/TESTING.md)
- [구현 기록](docs/IMPLEMENTATION_LOG.md)
- [API 표준](docs/API_STANDARD.md)
- [전체 구현 순서](docs/IMPLEMENTATION_SEQUENCE.md)
- [모델 카드](docs/MODEL_CARD.md)
- [기능 분류와 레포 책임](docs/FEATURE_CLASSIFICATION.md)
- [로드맵](docs/ROADMAP.md)
- [깃 전략](docs/GIT_STRATEGY.md)
