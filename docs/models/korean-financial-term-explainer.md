# 한국 금융 용어 dictionary

## 목적

한국 증시 고유어·신조어의 원 표현을 보존하고 영어 설명을 제공한다.

## Serving

- `POST /api/v1/korean-financial-terms/explain`
- 단일 원천: `data/reference/korean_financial_terms_seed.json`
- API와 뉴스 분석 glossary가 같은 loader를 사용한다.
- LLM 생성, web fallback, 별도 glossary 복제본은 없다.

## 표기 원칙

- 일반 용어는 직접 영어로 표기한다. 예: `물타기 → averaging down`.
- 한국 고유어·축약어는 로마자 표기를 사용한다. 예: `개미 → Ant`, `대장주 → Daejangju`, `따상 → Ttasang`.
- 동학개미와 서학개미처럼 의미가 다른 합성어는 별도 항목으로 유지한다.
- 설명과 예문이 의미를 제공하므로 영어 표면형을 임의의 일반 투자자 용어로 치환하지 않는다.

## 응답 정책

- 등록 용어: `DICTIONARY`, HIGH confidence, 30일 cache
- 미등록 한글 용어: `REVIEW_REQUIRED`, cache 금지
- 일반 영어 금융 단어: `TEXT_ONLY`; 한국 고유어의 명시적 로마자 alias만 dictionary 조회 허용

