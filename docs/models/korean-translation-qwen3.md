# 한국어 전문 번역 Qwen3 LLM

## 결론
한국 뉴스·공시 전문 번역은 기본값으로 꺼져 있으며, `HANNAH_KOREAN_TRANSLATION_GENERATION_MODE=local_llm`에서 실제 Qwen3 번역기를 사용한다.
전문 번역 운영 기본값은 Qwen3-4B GGUF Q4다. Qwen3-0.6B LoRA는 짧은 검증 샘플에서는 통과했지만 실제 뉴스 전문에서는 제목 오역, 원문 일부 잔존, 요약 축약이 발생해 운영 전문 번역 기본값에서 제외한다.
이 모드에서는 한국어 원문 전체와 glossary terms를 입력으로 받아 영어 JSON `{translation}`을 생성한다.

## Serving
- `POST /api/v1/translation/ko-en`
- 로컬 Mac 검증: `scripts/run_qwen3_4b_gguf.sh`로 Qwen3-4B GGUF Q4를 띄운다.
- 운영 CPU 환경: Qwen3-4B GGUF Q4만 띄우고 `HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT`로 연결한다.
- MLX 0.6B LoRA 경로는 회귀 테스트와 소형 샘플 재현용으로만 남긴다.
- endpoint가 없으면 direct MLX client를 사용하고, endpoint가 있으면 Qwen3 4B GGUF 런타임을 호출한다.

## 품질 gate
Qwen 출력은 다음 조건을 통과해야 `TRANSLATED`로 채택된다.
- strict JSON key: `translation`.
- 한국어 한글 잔존 금지.
- 원문 그대로 반환하거나 요약문으로 축약하는 출력 금지.
- 말줄임표와 중간 잘림 fragment 금지.
- model meta text, refusal, 투자 조언 문구 금지.
- glossary localism은 지정된 영어 표면형을 유지한다.
- `조·억·만·천`을 포함한 원화·달러 복합 금액은 Decimal 환산으로 원값과 영문 단위를 대조한다.
- 429/502/503/504와 일시 네트워크 오류는 지수 백오프로 최대 4회 재시도한다.

## 학습·검증 결과
- SFT 데이터셋: `data/training/korean_translation_sft.jsonl`, 39 samples.
- MLX split: `data/training/korean_translation_mlx`, train 31 / valid 4 / test 4.
- Adapter: `src/hannah_montana_ai/model_store/korean_translation_qwen3_lora/adapters.safetensors`.
- 학습 report: `reports/korean-translation-qwen3-training.json`, final train loss 0.019, final validation loss 0.025.
- raw generation 평가: `reports/korean-translation-qwen3-generation-eval.json`, 4/4 pass.

## 운영 변수
```bash
HANNAH_KOREAN_TRANSLATION_GENERATION_MODE=local_llm
HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT=http://127.0.0.1:18081
HANNAH_KOREAN_TRANSLATION_MLX_MODEL=mlx-community/Qwen3-0.6B-4bit
HANNAH_KOREAN_TRANSLATION_MLX_ADAPTER_PATH=src/hannah_montana_ai/model_store/korean_translation_qwen3_lora
HANNAH_KOREAN_TRANSLATION_LLM_MODEL=Qwen3-4B-GGUF-Q4
HANNAH_KOREAN_TRANSLATION_LLM_TIMEOUT_SECONDS=300
HANNAH_KOREAN_TRANSLATION_LLM_MAX_TOKENS=2048
HANNAH_KOREAN_TRANSLATION_MAX_CONCURRENCY=4
HANNAH_QWEN3_4B_GGUF_PATH=$HOME/.cache/hana/models/Qwen3-4B-Q4_K_M.gguf
HANNAH_QWEN3_CONTEXT_SIZE=16384
HANNAH_QWEN3_PARALLEL=4
```

## 재현 명령
```bash
scripts/run_qwen3_4b_gguf.sh
uv run python scripts/build_korean_translation_qwen3_dataset.py
uv run --extra llm-training python scripts/train_korean_translation_qwen3.py
uv run --extra llm-training python scripts/evaluate_korean_translation_qwen3_generation.py --min-pass-rate 1.0
```
