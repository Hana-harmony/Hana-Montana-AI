# 보안

## 현재 기준
- 애플리케이션 레벨 토큰 인증을 구현하지 않는다.
- 운영 배포에서 AI 컨테이너 포트를 외부에 공개하지 않는다.
- Spring 컨테이너에서만 AI 컨테이너에 접근 가능한 내부 네트워크를 사용한다.
- 협력사용 `OMNILENS_API_KEY`는 요구하거나 저장하지 않는다.

## 시크릿 관리
- 현재 AI 서비스는 로컬 실행에 필요한 시크릿이 없다.
- 외부 뉴스·공시 수집 credential은 학습 데이터 수집 스크립트에서만 사용한다.
- 로컬 수집 credential은 gitignore된 `secrets.local.env`에서만 읽는다.
- `secrets.local.env.example`에는 변수명만 기록하고 실제 credential 값은 넣지 않는다.
- 운영 credential은 GitHub Secrets 또는 배포 환경 Secret Manager에서 주입한다.
- `scripts/verify_secret_hygiene.py`는 추적 파일에 `.env`, `secrets.local.env`, key material, credential assignment가 포함되는지 CI에서 검사한다.
- credential 누락 오류는 변수명만 노출하고 credential 값은 출력하지 않는다.

## 모델 보안
- 모델 artifact는 버전과 학습 데이터 경로를 명시한다.
- 학습 데이터에 개인정보와 비공개 정보를 넣지 않는다.
- 모델 변경은 모델 카드와 구현 기록에 남긴다.
- 추론 요청 audit log는 원문 제목, snippet, URL을 저장하지 않고 SHA-256 hash만 저장한다.

## 향후 강화
- 네트워크 정책과 보안 그룹 검증
- 컨테이너 간 mTLS가 필요한 환경인지 평가
- 모델 입력 abuse detection
