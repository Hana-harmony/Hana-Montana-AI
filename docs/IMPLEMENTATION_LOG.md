# 구현 기록

## 2026-07-11 활성 일반주식 전체 글로벌 피어·glossary 경계 보강

- KIS 공식 마스터의 KOSPI·KOSDAQ·KONEX 활성 일반주식 2,752개를 모델 universe의 단일 기준으로 사용한다.
- 한국 종목별 고정 peer·headline·비교·강점 anchor와 14개 pairwise 정답 라벨을 제거했다. 모든 요청은 사업 태그, KSIC 업종, 사업 요약, TF-IDF, 잠재 의미, 재무 규모, 글로벌 인지도 신호를 실시간 조합해 후보를 점수화한다.
- 활성 2,752종목 전체 추론으로 2,752/2,752 성공, 고유한 3개 비교, 근거가 있는 4개 Key Strength, 동일 회사 중복 0건을 검증한다.
- 영문 glossary alias 전체에 양쪽 영숫자 단어 경계를 적용한다. `ant`는 `participant`, `significant`, `antitrust`에서, 다른 alias도 더 긴 영문 단어 내부에서 인식되지 않는다.
- 재학습 아티팩트는 `0644`로 교체하고 이미지 빌드 시 `0444`로 고정해 non-root serving 계정의 읽기 실패를 방지한다.
- `primaryPeer`·headline·peers 첫 항목을 Global Comparison 1순위와 동일하게 구성해 대표 피어와 실제 비교 카드가 엇갈리지 않게 한다.

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
