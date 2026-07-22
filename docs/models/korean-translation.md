# 한국어 전문 번역 모델

## 목적과 API

한국 주식 뉴스·공시의 전문을 영어로 번역한다. `POST /api/v1/translation/ko-en`과 intelligence event 생성 경로에서 사용하며, 같은 Qwen 런타임이 영문 제목과 What/Why/Impact도 strict JSON으로 생성한다.

## 구현

- 모델: 로컬 `Qwen3-4B-GGUF-Q4`(`Qwen/Qwen3-4B-GGUF`, `Qwen3-4B-Q4_K_M.gguf`)
- artifact: 공식 revision `bc640142c66e1fdd12af0bd68f40445458f3869b`과 SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` 고정
- serving: llama.cpp ARM64 image digest 고정, 4K context, 병렬 요청 2개, reasoning 비활성화, Qwen CPU 상한 3 OCPU
- provider: `local-llm`
- 입력: 원문, `NEWS`/`DISCLOSURE` 유형, 제목, 검증 glossary
- 출력: 번역문, provider, model version, 상태, prompt version, 품질 플래그
- 뉴스 전문 분할은 AI 서비스가 단독으로 담당한다. 본문은 최대 700자 단위로 나누고 llama.cpp의 병렬 슬롯 2개를 사용해 순서를 보존한 채 처리한다.
- 각 조각의 품질 재시도는 최대 2회로 제한하고, 900자를 넘는 본문은 전체 본문 재시도를 하지 않아 중복 추론 적재를 방지한다.
- 운영 HTTP timeout은 저사양 ARM CPU의 최악 지연을 수용하도록 600초로 둔다. 공개 API는 완성된 전문만 노출하고 상세 조회 요청 중에 번역하지 않는다.
- OpenDART 공시는 표·항목 구조를 보존하는 structured 경로를 사용한다.
- 단일 금융 용어 사전의 표면형을 prompt와 후처리에 적용한다.
- 전문 번역의 endpoint 오류, 누락, 반복, 미번역 한글, 잘린 문장 등 품질 gate 실패는 원문과 `SOURCE_LANGUAGE_FALLBACK`으로 반환하고 공개 발행에서 제외한다. 제목·What/Why/Impact의 품질 재시도는 실패한 이전 JSON과 구체적인 교정 조건을 Qwen에 다시 제공한다. 종결부호 누락만 의미를 바꾸지 않는 형식 정규화로 보완하며, 나머지 실패는 대체 문구 없이 분석 요청 자체를 실패 처리한다.

## 보안과 한계

- 원문 대신 SHA-256 축약 hash, 길이, 상태와 제한된 품질 플래그만 운영 로그에 남긴다.
- 외부 생성형 API나 원격 fallback을 사용하지 않는다.
- 번역은 투자·세무 자문이 아니며 원문 링크와 함께 제공해야 한다.

## 검증

- `tests/test_korean_translation_generator.py`
- `tests/test_news_summary_quality.py`
- `tests/test_omni_connect_contract.py`
