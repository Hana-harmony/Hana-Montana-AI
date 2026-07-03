# 뉴스·공시 요약 LLM readiness

## 결론
현재 live 뉴스·공시 What/Why/Impact 요약에는 Qwen을 기본 적용하지 않는다. 이번 결함은 생성 모델 부재가 아니라 전문 입력 누락, snippet 생략부호, 글자 수 hard cut, impact 메타 문장 노출이 원인이었으므로 기존 입력·rule·postprocessing 경로를 먼저 수정했다.

## 현재 live 경로
- 전문이 있으면 full content를 우선 사용한다.
- 문장 경계 기반 truncate로 중간 잘림을 피한다.
- `...`, `…`, 중요도·감성·classification 메타 문장은 요약 후보에서 제외한다.
- impact는 투자자가 확인해야 할 실제 영향 또는 점검 문장으로 fallback한다.

## Qwen 후보 조건
- 학습 후보: `mlx-community/Qwen3-0.6B-4bit` LoRA.
- 기존 실측: `reports/global-peer-qwen3-explainer-training.json`에서 batch size 1, max seq 2048, peak memory 2.238GB를 기록했다.
- 운영 후보: `Qwen3-0.6B GGUF Q4`를 API 프로세스 안에 적재하지 않고 llama.cpp OpenAI-compatible sidecar로만 연결한다.
- 운영 guard: batch size 1, timeout 1200ms, 입력 1200자 제한, JSON schema 검증, grounding 검증, rule engine fallback.

## 승격 기준
Qwen 요약은 `SummaryLines {what, why, impact}` JSON만 반환해야 하며, 각 line은 원문 근거가 있어야 한다. 생략부호, 문장 중간 잘림, 중요도·감성 메타, 투자 조언 문구가 나오면 즉시 rule engine 결과로 fallback한다.

## 로컬 번역 모델
현재 구현된 로컬 번역 baseline은 `local-financial-glossary-v2`다. GPT 번역과의 비교는 OmniLens의 `reports/openai-translation-smoke-report.json`에 기록하며, 숫자·날짜·종목코드·한국 금융 고유어 보존율과 CPU 메모리/속도 예산이 통과되기 전까지 live 기본 번역은 OpenAI GPT 경로로 둔다.
