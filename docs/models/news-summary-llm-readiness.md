# 뉴스·공시 요약 Qwen3 LLM

## 결론
뉴스·공시 What/Why/Impact 요약은 기본값으로 rule engine을 유지하고,
`HANNAH_NEWS_SUMMARY_GENERATION_MODE=local_llm`에서 실제 Qwen3-0.6B LoRA 생성기를 사용한다.
이 모드에서는 전문 기반 article text를 넣고 Qwen이 영어 JSON `{what, why, impact}`를 생성한다.

## 구현 경로
- 로컬 개발: `mlx-community/Qwen3-0.6B-4bit`와 `src/hannah_montana_ai/model_store/news_summary_qwen3_lora`를 MLX로 직접 로드한다.
- 운영 CPU 환경: Qwen3-0.6B GGUF Q4를 llama.cpp OpenAI-compatible sidecar로 띄우고 `HANNAH_NEWS_SUMMARY_LLM_ENDPOINT`로 연결한다.
- `AlertAnalyzer`는 먼저 rule engine fallback 요약을 만든 뒤, full content가 있을 때만 `NewsSummaryGenerator`를 호출한다.
- Qwen 출력이 실패하면 기존 rule summary를 그대로 반환한다.

## 품질 gate
Qwen 출력은 다음 조건을 모두 통과해야 live 응답의 `summary_lines`로 채택된다.
- strict JSON keys: `what`, `why`, `impact`.
- 각 값은 영어 한 문장이다.
- 말줄임표, 줄바꿈, bullet, 중간 잘림 fragment를 허용하지 않는다.
- 중요도·감성·classification·priority 같은 내부 메타 문구를 허용하지 않는다.
- buy/sell/price target/guaranteed return 같은 투자 조언 문구를 허용하지 않는다.
- 원문 한국어 금융 키워드와 영어 요약 사이의 근거 매칭을 확인한다.

## 학습·검증 결과
- SFT 데이터셋: `data/training/news_summary_wwi_sft.jsonl`, 128 samples.
- MLX split: `data/training/news_summary_wwi_mlx`, train 116 / valid 6 / test 6.
- Adapter: `src/hannah_montana_ai/model_store/news_summary_qwen3_lora/adapters.safetensors`.
- 학습 report: `reports/news-summary-qwen3-training.json`.
- raw generation 평가: `reports/news-summary-qwen3-generation-eval.json`, 5/5 pass.
- API smoke: 뉴스와 공시 full-content 요청에서 영어 What/Why/Impact 세 문장을 반환했다.

## 운영 변수
```bash
HANNAH_NEWS_SUMMARY_GENERATION_MODE=local_llm
HANNAH_NEWS_SUMMARY_LLM_ENDPOINT=
HANNAH_NEWS_SUMMARY_MLX_MODEL=mlx-community/Qwen3-0.6B-4bit
HANNAH_NEWS_SUMMARY_MLX_ADAPTER_PATH=src/hannah_montana_ai/model_store/news_summary_qwen3_lora
HANNAH_NEWS_SUMMARY_LLM_MODEL=Qwen3-0.6B-GGUF-Q4
HANNAH_NEWS_SUMMARY_LLM_TIMEOUT_SECONDS=4.0
HANNAH_NEWS_SUMMARY_LLM_MAX_TOKENS=260
```

## 남은 분리 과제
뉴스·공시 본문 전체 번역은 별도 번역 모델 경로에서 해결한다. 이 문서는 What/Why/Impact 세 줄 요약 생성만 다룬다.
