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

## 재학습 운영
- 외부 API 키는 `secrets.local.env`에서만 읽고 커밋하지 않는다.
- `scripts/collect_training_data.py`는 Naver News Search와 OpenDART에서 제목·snippet·링크만 수집한다.
- `data/raw`, `data/processed`는 gitignore 상태로 유지한다.
- weak-label 후보는 teacher confidence gate와 라벨별 quota를 통과한 경우에만 pseudo-label로 승격한다.
- 현재 artifact는 37,278건 수집 후보 중 320건 pseudo-label을 이벤트 모델 학습에 반영했다.
- 감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 supervised corpus만으로 학습한다.

## 운영 전 보강
- 모델 latency와 오류율 모니터링
- 모델 버전별 audit log
- drift 감시
- 재학습 기준과 rollback 절차
- 배포 환경별 Secret Manager 연동
