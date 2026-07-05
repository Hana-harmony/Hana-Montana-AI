# 글로벌 피어 매칭 모델

## 목적
한국 상장사를 외국인 투자자가 이해하기 쉬운 미국 상장 reference peer와 연결한다.

## Serving
- `POST /api/v1/market/global-peers/match`

## 입력
- 한국 종목코드
- 한글명, 영문명, alias
- 시장, 섹터, 산업, 사업모델, 선택 설명문

## 출력
- headline
- summary
- primary peer
- 후보 peer 목록
- matched factors
- confidence와 model version

## 모델
- 버전 prefix: `global-peer-hybrid-ranker`
- 한국 universe: 3,967개
- 미국 universe: 12,916개
- Eligible US company peer: 4,714개
- 구조: TF-IDF retrieval, SVD semantic embedding, business profile classifier, 재무/업종/규모 feature, pairwise LogisticRegression reranker
- Business profile classifier: `FeatureUnion(TfidfVectorizer(char_wb 2-5), TfidfVectorizer(word 1-2)) + LogisticRegression(class_weight=balanced)`
- Pairwise ranker: curated peer pair를 positive label로 쓰는 `LogisticRegression(class_weight=balanced)`
- Ranking feature: text similarity, semantic similarity, financial similarity, same sector/industry/business model/scale bucket, market cap/revenue gap, operating margin gap

## 설명 생성
- 기본 serving: deterministic structured template
- Optional local LLM: `HANNAH_GLOBAL_PEER_EXPLANATION_MODE=local_llm`에서 endpoint가 없으면 `mlx-community/Qwen3-0.6B-4bit`와 LoRA adapter를 MLX로 직접 로드한다. endpoint가 있으면 Qwen3-0.6B GGUF Q4를 OpenAI-compatible local server로 연결한다.
- LoRA adapter: `src/hannah_montana_ai/model_store/global_peer_qwen3_explainer_lora`
- Prompt version: `global-peer-structured-rag-explainer-v7`
- 학습 split: train 3,571 / valid 198 / test 198
- 학습 설정: 500 iters, batch size 1, learning rate 1e-5, 8 layers, trainable 1.442M / total 596.050M params
- 검증: raw Qwen3 generation 30종목 기준 JSON valid 30/30, exact headline 30/30, exact summary 30/30, grounded 30/30, pass rate 1.0
- Fallback: endpoint 장애, 비정상 JSON, display name 누락, peer 근거 불일치, headline/summary exact mismatch, 점수 노출, 투자조언 문구는 template으로 대체한다.

## 평가
| 항목 | 값 |
| --- | ---: |
| Anchor top1 accuracy | 0.9286 |
| Pairwise top1 accuracy | 0.9286 |
| Pairwise top3 accuracy | 1.0000 |
| MRR | 0.9643 |
| 전종목 추론 성공 | 3,967 / 3,967 |
| LOW confidence | 878 |
| Business profile classifier accuracy | 0.9735 |
| Business profile classifier macro F1 | 0.9672 |

## 산출물
- Artifact: `src/hannah_montana_ai/model_store/global_peer_ml.joblib`
- Qwen3 LoRA adapter: `src/hannah_montana_ai/model_store/global_peer_qwen3_explainer_lora/`
- Training report: `reports/global-peer-training-report.json`
- Qwen3 training report: `reports/global-peer-qwen3-explainer-training.json`
- Qwen3 generation eval: `reports/global-peer-qwen3-generation-eval.json`
- Full coverage report: `reports/global-peer-full-coverage-report.json`
- All results: `reports/global-peer-all-results.json`, `reports/global-peer-all-results.csv`
- Human-readable all results: `docs/GLOBAL_PEER_ALL_RESULTS.md`

## 한계
- 글로벌 피어에는 공개 표준 SOTA leaderboard가 없어 curated anchor와 전종목 coverage gate를 운영 기준으로 둔다.
- LOW confidence 종목은 사업 profile 보강과 수동 anchor 확장이 필요하다.
