# Git 전략

## 브랜치

- `main`: 운영 release 기준
- `feature`: 검증된 모델·코드 변경 통합
- 작업 브랜치: 최신 `feature`에서 생성한 `<type>/<kebab-case-description>`
- type: `feat`, `fix`, `hotfix`, `refactor`, `docs`, `test`, `security`, `chore`, `release`

```bash
git switch feature
git pull --ff-only origin feature
git switch -c docs/refresh-current-implementation
uv run python scripts/verify_harness_git_flow.py --pr-base feature
```

작업 브랜치 → `feature` PR을 체크 후 병합하고, 이어서 `feature` → `main` release PR을 체크 후 병합한다. 보호 브랜치에 직접 push하지 않는다.

## 커밋과 PR

- 커밋과 PR 제목: `type(scope): 한글 제목`
- 단일 커밋 PR 제목은 커밋 제목과 일치시킨다.
- 본문은 배경, 변경 사항, 검증 결과, 영향 범위, rollback과 체크리스트를 포함한다.
- `.gitmessage.txt`와 `.github/PULL_REQUEST_TEMPLATE.md`를 사용한다.
- 모델 변경 PR은 artifact·report diff, 데이터 lineage, 평가 gate와 rollback model version을 명시한다.
- CI와 message convention 검사가 통과한 PR만 squash merge한다.
