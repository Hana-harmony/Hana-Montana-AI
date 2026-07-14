# 운영 관측성

Hannah Montana AI는 `/metrics`에서 요청 수·지연 시간·오류 로그·업무 이벤트·Discord 전송 결과를 Prometheus 형식으로 제공한다. OCI의 OmniLens 관측성 스택이 이 엔드포인트와 Docker 로그를 수집한다.

모델 재학습 시작과 완료는 `HANNAH_DISCORD_WEBHOOK_URL`로 비동기 전송한다. 요청 처리 스레드는 Discord 응답을 기다리지 않으며 큐가 포화되거나 전송이 실패하면 ERROR 로그와 실패 메트릭을 남긴다. 운영에서는 `HANNAH_RUNTIME_ENVIRONMENT=production`과 웹훅 URL이 모두 필수다.

오류 알림과 Grafana 접속 방법은 Hana-OmniLens-API의 `docs/OBSERVABILITY.md`를 따른다. 알림에는 학습 데이터 원문, 인증 토큰, 모델 파일 경로의 민감 정보가 포함되지 않는다.

필수 GitHub Secret:

- `HANNAH_DISCORD_WEBHOOK_URL`
