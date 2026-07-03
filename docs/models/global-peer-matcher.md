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
- 설명 생성은 deterministic structured template이 기본이며, local LLM 모드는 strict gate 실패 시 template으로 fallback한다.

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
- Training report: `reports/global-peer-training-report.json`
- Full coverage report: `reports/global-peer-full-coverage-report.json`
- All results: `reports/global-peer-all-results.json`, `reports/global-peer-all-results.csv`
- Human-readable all results: `docs/GLOBAL_PEER_ALL_RESULTS.md`

## 한계
- 글로벌 피어에는 공개 표준 SOTA leaderboard가 없어 curated anchor와 전종목 coverage gate를 운영 기준으로 둔다.
- LOW confidence 종목은 사업 profile 보강과 수동 anchor 확장이 필요하다.
