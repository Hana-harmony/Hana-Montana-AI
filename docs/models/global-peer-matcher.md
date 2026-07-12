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
- 종목 표시명은 검증된 영문명을 우선하고, 비었거나 한글명으로 오염된 경우 AI 계약 경계에서 영문 표시명을 생성해 `stock_name_en`, headline, summary에 동일하게 적용한다.
- 한국 종목별 정답 peer, 서빙 anchor, pairwise 정답 라벨은 사용하지 않는다.
- 후보 인지도와 시가총액 신뢰도를 반영해 소규모·저인지도 후보의 노출을 억제한다.
- WiseReport 기업 사업 설명에서 확인된 구체 사업 태그를 비교업종 분류기보다 우선한다. `해양플랫폼`처럼 업종 문맥이 있는 표현은 소프트웨어 플랫폼으로 분류하지 않는다.
- primary peer와 비교 peer는 동일 업종 또는 실제 사업 태그가 겹치는 후보로 제한한다. 같은 섹터라는 이유만으로 무관한 회사를 채우지 않는다.
- 근거 있는 미국 peer가 3개보다 적은 좁은 업종은 1~2개만 반환한다. presentation 개수를 맞추기 위해 무관한 회사를 추가하지 않는다.
- 조선업 미국 기준군은 선박 건조·해군 함정·추진체계 사업 근거가 있는 HII, GD, BWXT를 포함한다.

## 검증

- 현재 KIS 활성 universe 전체와 모델 universe 수가 일치해야 하며 전종목 100% 추론 coverage를 요구한다.
- 비교 차원과 peer ticker는 중복될 수 없다.
- 핵심 강점은 서로 다른 제목과 설명, 분야별 `icon_key`를 가져야 한다.
- headline/summary에는 내부 similarity score, confidence, 투자 조언을 노출하지 않는다.
- 한화오션 및 국내 조선 3사 회귀 테스트에서 source 업종과 모든 비교 peer 업종이 `Shipbuilding`이어야 한다.

## 산출물

- `src/hannah_montana_ai/model_store/global_peer_ml.joblib`
- `reports/global-peer-training-report.json`
- `reports/global-peer-full-coverage-report.json`
- `reports/global-peer-all-results.json`
