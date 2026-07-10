# 한국 금융 용어 처리

이 기능은 RAG/LLM 생성 기능이 아니라 검증된 단일 dictionary 기능이다.

1. `data/reference/korean_financial_terms_seed.json`을 시작 시 한 번 읽는다.
2. 동일 loader를 용어 설명 API와 뉴스 분석 glossary 추출이 공유한다.
3. 정규형, 영어 표면형, alias를 하나의 index로 구성한다.
4. 등록 용어만 확정 설명으로 반환한다.
5. 미등록 한글 용어는 기사 문맥 evidence와 함께 `REVIEW_REQUIRED`로 반환한다.

신규 용어는 seed에 정의·설명·예문·표기 원칙을 검수해 추가한다. 별도 glossary 파일이나 LLM 후보를 생성하지 않는다.

