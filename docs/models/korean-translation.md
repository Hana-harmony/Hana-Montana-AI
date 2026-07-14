# 한국어 전문 번역 모델

## 목적과 API

한국 주식 뉴스·공시의 제목, 요약, 전문을 영어로 번역한다. `POST /api/v1/translation/ko-en`과 intelligence event 생성 경로에서 사용한다.

## 구현

- 모델: 로컬 `Qwen3-4B-GGUF-Q4`(`Qwen/Qwen3-4B-GGUF`, `Qwen3-4B-Q4_K_M.gguf`)
- artifact: 공식 revision `bc640142c66e1fdd12af0bd68f40445458f3869b`과 SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` 고정
- serving: llama.cpp ARM64 image digest 고정, 8K context, 병렬 요청 2개, reasoning 비활성화
- provider: `local-llm`
- 입력: 원문, `NEWS`/`DISCLOSURE` 유형, 제목, 검증 glossary
- 출력: 번역문, provider, model version, 상태, prompt version, 품질 플래그
- 뉴스 전문은 길이에 따라 분할하고 제목·본문의 문맥과 문장 완결성을 검증한다.
- OpenDART 공시는 표·항목 구조를 보존하는 structured 경로를 사용한다.
- 단일 금융 용어 사전의 표면형을 prompt와 후처리에 적용한다.
- endpoint 오류, 누락, 반복, 미번역 한글, 잘린 문장 등 품질 gate 실패는 원문과 `SOURCE_LANGUAGE_FALLBACK`으로 반환한다.

## 보안과 한계

- 원문 대신 SHA-256 축약 hash, 길이, 상태와 제한된 품질 플래그만 운영 로그에 남긴다.
- 외부 생성형 API나 원격 fallback을 사용하지 않는다.
- 번역은 투자·세무 자문이 아니며 원문 링크와 함께 제공해야 한다.

## 검증

- `tests/test_korean_translation_generator.py`
- `tests/test_news_summary_quality.py`
- `tests/test_omnilens_contract.py`
