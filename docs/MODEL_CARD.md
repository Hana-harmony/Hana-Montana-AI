# 모델 문서 인덱스

Hannah-Montana-AI의 모델 상세는 기능별 문서로 관리한다. README에는 전체 기능만 요약하고, 지표·학습 데이터·한계는 아래 문서에 남긴다.

| 모델 | 핵심 스택 | Serving API | 상세 문서 |
| --- | --- | --- | --- |
| 뉴스·공시 분석 | TF-IDF + Logistic Regression + TF-IDF stock linker | `POST /api/v1/alerts/analyze`, `POST /api/v1/intelligence/events` | [financial-alert-analysis.md](models/financial-alert-analysis.md) |
| 외국인 보유 예측 | stock-routed ML ensemble + N-HiTS/PatchTST SOTA 진단 | `POST /api/v1/market/foreign-ownership/predict` | [foreign-ownership-forecast.md](models/foreign-ownership-forecast.md) |
| 글로벌 피어 매칭 | bounded TF-IDF/SVD + pairwise LogisticRegression + profile quality/MMR + optional Qwen3 LoRA | `POST /api/v1/market/global-peers/match` | [global-peer-matcher.md](models/global-peer-matcher.md) |
| 한국 금융 용어 해설 | seed dictionary + Qwen3-4B GGUF Q4 | `POST /api/v1/korean-financial-terms/explain` | [korean-financial-term-explainer.md](models/korean-financial-term-explainer.md) |
| 뉴스·공시 요약 Qwen3 LLM | Qwen3-4B GGUF Q4 + strict summary gate | `POST /api/v1/alerts/analyze`, `POST /api/v1/intelligence/events` | [news-summary-llm-readiness.md](models/news-summary-llm-readiness.md) |
| 한국어 전문 번역 Qwen3 LLM | Qwen3-4B GGUF Q4 + strict translation gate | `POST /api/v1/translation/ko-en` | [korean-translation-qwen3.md](models/korean-translation-qwen3.md) |
| 세무 서류 OCR 검증 | hanah_tax_ocr parser/reviewer + optional PaddleOCR runtime | `POST /api/v1/tax/documents/verify` | [ADR-002](adr/ADR-002-tax-document-ocr.md) |

## 공통 원칙
- ChatGPT API에 의존하지 않고 자체 artifact와 규칙/RAG 계층을 우선 사용한다.
- 모델 버전, 평가 리포트, 학습 데이터 경로를 문서에 남긴다.
- 자동 주문 차단이나 투자 판단을 모델이 직접 결정하지 않는다.
- 외부 credential과 협력사 API key는 모델 런타임에 저장하지 않는다.
