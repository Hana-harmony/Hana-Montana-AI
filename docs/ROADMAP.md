# 품질 로드맵

## 현재 운영 기준

- 뉴스·공시 ML release gate, 실제 뉴스·공시 gold, confidence calibration과 stock linker를 운영 artifact에 적용했다.
- 로컬 Qwen3 전문 번역과 금융 용어 단일 사전을 적용했다.
- KIS 활성 일반주식 2,752개 글로벌 피어 추론 coverage와 구조 gate를 통과했다.
- 외국인 제한 32종목 보유수량 모델을 walk-forward와 persistence guard로 승격했다.
- 세무 3문서 OCR pipeline과 미국 조세조약 환급 sandbox 규칙을 API로 제공한다.

## 다음 품질 기준

- 실제 운영 뉴스·공시의 월별 사람 검수 gold와 종목·이벤트별 drift를 누적한다.
- 번역 문서 유형별 회귀 corpus와 긴 전문 완결성·용어 보존 지표를 강화한다.
- 글로벌 피어의 generic profile 106건과 재무 coverage 공백을 줄이고 전종목 gate를 유지한다.
- 외국인 예측에 대해 종목별 오차 구간, 계절성 ablation, 통계적 유의성 검정을 추가한다.
- 세무 OCR의 실제 서식·스캔 품질·다국어·위변조 adversarial 표본을 확장한다.
- 모델 artifact provenance, 서명, SBOM과 container 취약점 검증을 release gate에 연결한다.

각 항목은 코드, versioned report, 테스트와 `docs/models/` 상세 문서를 함께 변경한 경우에만 완료 처리한다.
