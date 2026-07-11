# 구현 기록

## 2026-07-11 전 종목 글로벌 피어·glossary 경계 보강

- 거래소 서빙 59종목 전체의 Key Strength 4개를 종목별 사업요약 근거로 생성하며, 증거가 4개 미만이면 더미 카드 대신 명시적 실패를 반환한다.
- 삼성전자 전용 anchor 외 종목도 사업요약의 반도체·배터리·자동차·금융·플랫폼·바이오·항공·미디어 증거를 각각 다른 강점으로 매핑한다.
- 비교 종목은 실제 사업 차원 적합도와 글로벌 인지도 catalog를 함께 사용하며 거래소 서빙 전체에서 3개 비교·4개 강점 계약을 검증했다.
- 영문 glossary alias는 영숫자 token 경계를 만족할 때만 인식하므로 `participant`의 부분 문자열 `ant`를 고유어로 처리하지 않는다.

## 2026-07-11 기능별 고정 실행 경로

- 한국 금융 용어는 단일 dictionary, 글로벌 피어 설명은 grounded template, 뉴스 What/Why/Impact는 rule, 한국어 번역은 로컬 Qwen 4B GGUF HTTP로 고정했다.
- 네 기능의 mode 설정을 제거하고 알 수 없는 Settings 필드는 fail-fast 처리한다.
- 글로벌 피어·뉴스·금융 용어용 Qwen/MLX 클라이언트, LoRA adapter, 학습 데이터·스크립트·평가 리포트와 `mlx-lm` 의존성을 삭제했다.
- 한국어 번역의 직접 MLX와 local glossary 분기를 삭제해 로컬 Docker와 배포 서버가 같은 Qwen endpoint 계약을 사용한다.
- 금융 용어 seed를 분석 glossary의 단일 원천으로 연결하고 30개 이상으로 확장했다.
- 표면형을 `개미 → Ant`, `대장주 → Daejangju`로 정정하고 동학개미·서학개미·빚투·영끌·존버·물타기·불타기·상따·하따 등을 분리했다.
- Qwen 번역과 rule 요약 모두 `Ant`, `Daejangju`, `Bittu` 표면형을 유지한다.
- Qwen 번역기도 동일한 seed를 직접 로드해 호출자가 glossary를 누락해도 dictionary 표기를 프롬프트·후처리에 강제한다.
- `개미`를 `Insects`, `대장주`를 `blue chips`로 바꾸는 Qwen 의역도 각각 `Ant`, `Daejangju`로 정규화한다.

## 2026-07-08 세무 서류 OCR

- `/api/v1/tax/documents/verify`가 이미지/PDF payload를 공통 `TaxDocumentPipeline`으로 검증한다.
- Tesseract `kor+eng` OCR, 문서별 parser/reviewer, 위변조·필수필드 gate를 사용한다.
- OCR 불가 입력은 임의 통과시키지 않고 명시적 실패 사유를 반환한다.

## 2026-07-03 글로벌 피어 비교 강화

- 글로벌 비교는 3개 고유 비교 차원과 인지도 높은 peer를 반환한다.
- 삼성전자는 Apple/Intel/TSMC 비교와 memory/foundry/ecosystem/AI 네 강점을 제공한다.
- 핵심 강점은 비교 문구가 아니라 한국 기업 자체의 강점으로 구성한다.
