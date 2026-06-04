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
uv run uvicorn hannah_montana_ai.main:app --reload
```

## 학습 파이프라인
```bash
uv run python scripts/collect_training_data.py --reuse-existing-raw --max-news-per-query 1000 --dart-days 365 --dart-pages 10
uv run python scripts/build_augmented_training_data.py
uv run python scripts/build_gold_evaluation_data.py
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
```

로컬 외부 API 키는 커밋하지 않는 `secrets.local.env`에서만 읽는다.
수집 실패나 rate limit으로 새 raw 수가 기존보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
수집된 대량 weak-label 후보는 supervised teacher 모델의 confidence gate와 라벨별 quota를 통과한 pseudo-label만 이벤트 모델 학습에 승격한다.
학습 결과는 `reports/ml-training-report.json`의 80:20 holdout 검증과 `reports/ml-model-evaluation.json`의 gold 평가셋 지표로 기록한다.

AI 서비스는 협력사용 `OMNILENS_API_KEY`나 별도 서비스 토큰을 요구하지 않는다. 배포 환경에서는 외부에 포트를 공개하지 않고 Spring 컨테이너에서만 접근 가능한 내부 네트워크로 격리한다.

## 주요 엔드포인트
- `GET /health`
- `POST /api/v1/alerts/analyze`

## 문서
- [기여 가이드](CONTRIBUTING.md)
- [아키텍처](docs/ARCHITECTURE.md)
- [운영](docs/OPERATIONS.md)
- [보안](docs/SECURITY.md)
- [테스트](docs/TESTING.md)
- [구현 기록](docs/IMPLEMENTATION_LOG.md)
- [모델 카드](docs/MODEL_CARD.md)
- [로드맵](docs/ROADMAP.md)
- [깃 전략](docs/GIT_STRATEGY.md)
