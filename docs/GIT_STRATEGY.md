# Git 전략

## 브랜치

- `main`: 운영 release 기준
- `feature`: 검증된 모델·코드 변경 통합
- 작업 브랜치: 최신 `feature`에서 생성한 `<type>/<kebab-case-description>`
- type: `feat`, `fix`, `hotfix`, `refactor`, `docs`, `test`, `security`, `chore`, `release`, `research`

```bash
git switch feature
git pull --ff-only origin feature
git switch -c docs/refresh-current-implementation
uv run python scripts/verify_harness_git_flow.py --pr-base feature --head-ref docs/refresh-current-implementation
```

작업 브랜치 → `feature` PR을 체크 후 병합하고, 이어서 `feature` → `main` release PR을 체크 후 병합한다. 보호 브랜치에 직접 push하지 않는다.

GitHub Actions는 PR의 base SHA 조상 관계와 head/base 쌍을 같이 검증한다. 작업 PR은 `<type>/<kebab-case>` → `feature`, release PR은 `feature` → `main`만 허용하며 detached HEAD에서도 GitHub가 제공한 head ref를 사용한다.

`feature → main` 병합 후에는 다음 작업 PR 전 `main`의 승격 커밋을 `feature`가 다시 포함해야 한다. squash/merge로 생긴 분기를 방치하지 않고, 보호 브랜치에 직접 push하지 않는 동기화 PR로 해소한다. 이 조상 관계가 깨지면 release PR 전에 하네스가 실패한다.

## 커밋과 PR

- 커밋과 PR 제목: `type(scope): 한글 제목`
- 단일 커밋 PR 제목은 커밋 제목과 일치시킨다.
- 본문은 배경, 변경 사항, 검증 결과, 영향 범위, rollback과 체크리스트를 포함한다.
- `.gitmessage.txt`와 `.github/PULL_REQUEST_TEMPLATE.md`를 사용한다.
- 모델 변경 PR은 artifact·report diff, 데이터 lineage, 평가 gate와 rollback model version을 명시한다.
- CI와 message convention 검사가 통과한 PR만 squash merge한다.
