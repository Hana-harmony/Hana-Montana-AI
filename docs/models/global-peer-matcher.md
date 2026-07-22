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
- 출력: 기준 종목의 sector·industry·business model·business tags, headline, summary, primary peer, 1~3개 비교 차원, 4개 핵심 강점, matched factors, confidence
- 종목 표시명은 검증된 영문명을 우선하고, 비었거나 한글명으로 오염된 경우 AI 계약 경계에서 영문 표시명을 생성해 `stock_name_en`, headline, summary에 동일하게 적용한다.
- 한국 종목별 정답 peer, 서빙 anchor, pairwise 정답 라벨은 사용하지 않는다.
- 후보 인지도와 시가총액 신뢰도를 반영해 소규모·저인지도 후보의 노출을 억제한다.
- Naver 업종 비교·업종코드로 확정된 분류를 기준으로 사용하고 WiseReport 기업 사업 설명과 OpenDART KSIC는 같은 섹터의 보조 태그만 추가한다. 단, 항공운송·항공우주는 회사별 사업 설명과 KSIC 511·252·313 근거로 재검증해 동종업계 회사명의 일부 키워드가 전체 업종을 오염시키지 못하게 한다.
- `네트워크`·`정보통신` 같은 일반 표현은 통신 서비스업 근거로 사용하지 않고 MVNO·MNO·알뜰폰·통신서비스처럼 사업자 문맥이 명시된 표현만 사용한다. `해양플랫폼`처럼 업종 문맥이 있는 표현도 소프트웨어 플랫폼으로 분류하지 않는다.
- 통신 서비스 사업자는 MVNO·MNO·알뜰폰·통신서비스 근거로 식별하고, 기지국·중계기·광전송장비 제조사는 `Communications Equipment`, 정보보안·SI·디지털 전환 기업은 `Software`로 분리한다. AT&T 같은 통신사는 서비스 사업자의 피어로만 사용한다.
- 미국 종목명의 영문 키워드는 단어·구문 경계가 맞을 때만 업종 근거로 인정한다. 예를 들어 `TransDigm` 내부 문자열을 `SDI` 배터리 신호로 취급하지 않는다. 법인명의 일반적인 `Holdings`도 투자지주업 근거로 쓰지 않고, Berkshire Hathaway·Loews·Markel·Icahn Enterprises·Brookfield처럼 실제 사업이 확인된 기준군만 투자지주 피어 후보로 사용한다.
- primary peer와 비교 peer는 동일 업종 또는 실제 사업 태그가 겹치는 후보로 제한한다. 같은 섹터라는 이유만으로 무관한 회사를 채우지 않는다.
- 근거 있는 미국 peer가 3개보다 적은 좁은 업종은 1~2개만 반환한다. presentation 개수를 맞추기 위해 무관한 회사를 추가하지 않는다.
- 조선업 미국 기준군은 선박 건조·해군 함정·추진체계 사업 근거가 있는 HII, GD, BWXT를 포함한다.

## 검증

- 현재 KIS 활성 universe 전체와 모델 universe 수가 일치해야 하며 전종목 100% 추론 coverage를 요구한다.
- 전 종목 coverage에서 모델에 저장된 기준 종목 sector·industry를 업종 기준 CSV와 대조하며, 구체 분류가 하나라도 달라지면 품질 게이트를 실패시킨다.
- 비교 차원과 peer ticker는 중복될 수 없다.
- 핵심 강점은 서로 다른 제목과 설명, 분야별 `icon_key`를 가져야 한다.
- headline/summary에는 내부 similarity score, confidence, 투자 조언을 노출하지 않는다.
- LG, 하나금융지주, 우리금융지주, LG에너지솔루션, 노루홀딩스는 기준 업종을 보존하고 AT&T를 선택하지 않아야 하며, SK텔레콤은 통신업 회귀 기준을 유지한다.
- 한화오션 및 국내 조선 3사 회귀 테스트에서 source 업종과 모든 비교 peer 업종이 `Shipbuilding`이어야 한다.
- 대한항공은 `Airlines`, 한화에어로스페이스·한국항공우주는 `Aerospace and Defense`로 분리하며, 항공기 제조 표현만으로 Delta·United·American 같은 항공사를 선택하지 않아야 한다.
- 한국정보통신은 `Payments`, 케이엠더블유는 `Communications Equipment`, 폴라리스AI·아시아나IDT·싸이버원은 `Software`, 아이씨티케이는 `Semiconductors` 회귀 기준을 유지한다.

## 산출물

- `src/hannah_montana_ai/model_store/global_peer_ml.joblib`
- `reports/global-peer-training-report.json`
- `reports/global-peer-full-coverage-report.json`
- `reports/global-peer-all-results.json`
