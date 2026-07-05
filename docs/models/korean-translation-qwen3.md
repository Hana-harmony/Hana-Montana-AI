# 한국어 전문 번역 Qwen3 LLM

## 결론
한국 뉴스·공시 전문 번역은 기본값으로 꺼져 있으며, `HANNAH_KOREAN_TRANSLATION_GENERATION_MODE=local_llm`에서 실제 Qwen3-0.6B LoRA 번역기를 사용한다.
이 모드에서는 한국어 원문 전체와 glossary terms를 입력으로 받아 영어 JSON `{translation}`을 생성한다.

## Serving
- `POST /api/v1/translation/ko-en`
- 로컬 개발: `mlx-community/Qwen3-0.6B-4bit`와 `src/hannah_montana_ai/model_store/korean_translation_qwen3_lora`를 MLX로 직접 로드한다.
- 운영 CPU 환경: Qwen3-0.6B GGUF Q4를 llama.cpp OpenAI-compatible sidecar로 띄우고 `HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT`로 연결한다.
- endpoint가 없으면 direct MLX client를 사용하고, endpoint가 있으면 sidecar client를 사용한다.

## 품질 gate
Qwen 출력은 다음 조건을 통과해야 `TRANSLATED`로 채택된다.
- strict JSON key: `translation`.
- 한국어 한글 잔존 금지.
- 원문 그대로 반환하거나 요약문으로 축약하는 출력 금지.
- 말줄임표와 중간 잘림 fragment 금지.
- model meta text, refusal, 투자 조언 문구 금지.
- glossary localism은 지정된 영어 표면형을 유지한다.

## 학습·검증 결과
- SFT 데이터셋: `data/training/korean_translation_sft.jsonl`, 39 samples.
- MLX split: `data/training/korean_translation_mlx`, train 31 / valid 4 / test 4.
- Adapter: `src/hannah_montana_ai/model_store/korean_translation_qwen3_lora/adapters.safetensors`.
- 학습 report: `reports/korean-translation-qwen3-training.json`, final train loss 0.019, final validation loss 0.025.
- raw generation 평가: `reports/korean-translation-qwen3-generation-eval.json`, 4/4 pass.

## 운영 변수
```bash
HANNAH_KOREAN_TRANSLATION_GENERATION_MODE=local_llm
HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT=
HANNAH_KOREAN_TRANSLATION_MLX_MODEL=mlx-community/Qwen3-0.6B-4bit
HANNAH_KOREAN_TRANSLATION_MLX_ADAPTER_PATH=src/hannah_montana_ai/model_store/korean_translation_qwen3_lora
HANNAH_KOREAN_TRANSLATION_LLM_MODEL=Qwen3-0.6B-GGUF-Q4
HANNAH_KOREAN_TRANSLATION_LLM_TIMEOUT_SECONDS=8.0
HANNAH_KOREAN_TRANSLATION_LLM_MAX_TOKENS=900
```

## 재현 명령
```bash
uv run python scripts/build_korean_translation_qwen3_dataset.py
uv run --extra llm-training python scripts/train_korean_translation_qwen3.py
uv run --extra llm-training python scripts/evaluate_korean_translation_qwen3_generation.py --min-pass-rate 1.0
```
