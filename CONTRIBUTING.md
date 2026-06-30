# 기여 가이드

## 개발 흐름
- 브랜치와 커밋 규칙은 [Git 전략](docs/GIT_STRATEGY.md)을 따른다.
- 일반 작업은 최신 `feature`에서 작업 브랜치를 생성한다.
- PR은 `feature` 대상으로 생성하고, 운영 반영은 `feature`에서 `main`으로 릴리스 PR을 만든다.
- 작업 완료 전 `uv run python scripts/verify_harness_git_flow.py --pr-base feature`로 브랜치와 PR 대상이 하네스를 따르는지 확인한다.

## 커밋 템플릿
```bash
git config commit.template .gitmessage.txt
```

## 변경 기준
- 분석 API 계약 변경은 README, 아키텍처 문서, 테스트를 함께 갱신한다.
- 모델 변경은 구현 기록과 모델 카드를 함께 갱신한다.
- 학습 데이터 변경은 데이터 출처와 라벨 기준을 문서화한다.

## 로컬 검증
```bash
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run pytest
uv run python scripts/verify_harness_git_flow.py --pr-base feature
```
