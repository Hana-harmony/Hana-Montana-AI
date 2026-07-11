# 글로벌 피어 매칭

## 목적

한국 상장사를 외국인 투자자가 이해하기 쉬운 미국 상장 reference peer와 연결한다.

## Serving

- `POST /api/v1/market/global-peers/match`
- 설명은 항상 `GROUNDED_TEMPLATE_STRUCTURED_RAG` template을 사용한다.
- LLM 모드, endpoint, LoRA fallback은 없다.

## 모델과 출력

- universe: KIS 공식 마스터의 활성 KOSPI·KOSDAQ·KONEX 일반주식 2,752개
- ranker: bounded TF-IDF retrieval, SVD semantic embedding, profile/재무 feature, 사업 도메인, 프로필 충실도, 글로벌 인지도 신호의 동적 점수
- 모델 prefix: `global-peer-dynamic-similarity`
- 출력: headline, summary, primary peer, 3개 비교 차원, 4개 핵심 강점, matched factors, confidence
- 한국 종목별 정답 peer, 서빙 anchor, pairwise 정답 라벨은 사용하지 않는다.
- 후보 인지도와 시가총액 신뢰도를 반영해 소규모·저인지도 후보의 노출을 억제한다.

## 검증

- 현재 KIS 활성 universe 전체와 모델 universe 수가 일치해야 하며 전종목 100% 추론 coverage를 요구한다.
- 비교 차원과 peer ticker는 중복될 수 없다.
- 핵심 강점은 서로 다른 제목과 설명, 분야별 `icon_key`를 가져야 한다.
- headline/summary에는 내부 similarity score, confidence, 투자 조언을 노출하지 않는다.

## 산출물

- `src/hannah_montana_ai/model_store/global_peer_ml.joblib`
- `reports/global-peer-training-report.json`
- `reports/global-peer-full-coverage-report.json`
- `reports/global-peer-all-results.json`
