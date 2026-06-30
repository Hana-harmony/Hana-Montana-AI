# 금융 NLP ML 모델 카드

## 모델명
`financial-ml-tfidf-logreg-20260622090407`

## 목적
- 한국 주식 뉴스·공시의 이벤트 태그, 감성, 중요도를 자체 ML 모델로 분류한다.
- Hana-OmniLens-API의 Watchlist News & Disclosure Alert API payload 생성에 사용한다.
- ChatGPT API나 외부 LLM에 의존하지 않는다.

## 외국인 보유/취득 수량 예측 모델
- 모델 버전: `hannah-foreign-owned-quantity-ml-v1`
- 목적: OmniLens가 저장한 전날까지의 일별 `foreign_owned_quantity`만 사용해 다음 거래일 외국인 보유/취득 수량을 예측한다. 한도수량은 예측 타깃이 아니라 한도소진율 계산의 분모로만 사용한다.
- 입력: 종목코드, 전날까지의 외국인 보유수량 시계열. 주문수량, 장중 거래량, 시세, 거래대금은 모델 입력에서 제외한다.
- 학습 방식: 전체 종목을 하나로 뭉개지 않고 `stock_code`를 범주 feature로 포함한 panel/global regression으로 학습한다. walk-forward 검증에서 종목별 MAE/RMSE/MAPE를 persistence baseline 대비 정규화한 composite score로 ML 후보와 blend alpha를 선택하되, persistence baseline보다 MAPE가 나빠지는 후보/runtime은 종목별 MAPE guard로 보정하는 stock-routed ML ensemble을 운영 artifact에 저장한다.
- 후보 모델: Ridge, HistGradientBoostingRegressor 2종, ExtraTreesRegressor, log-delta ratio 회귀 2종, 절대 delta quantity 회귀 4종, target quantity 회귀 1종, residual 회귀 18종, hurdle HistGradientBoosting classifier+regressor. residual 후보에는 squared-error, absolute-error, MAPE-weighted HistGradientBoosting을 포함한다. 각 후보는 lag, 변화율, rolling mean/std/range, 40/60/120/240 관측치 장기 흐름, 최근 일별 delta 분포, 날짜, 변화 간격, 관측치 수 feature로 다음 거래일 보유수량 delta ratio, log-delta ratio, 절대 delta, target quantity, 또는 heuristic residual을 예측한다. baseline이 마지막으로 이기던 종목은 `micro_median_delta_3` 정책으로 대체했다.
- 검증 방식: random split을 쓰지 않고 날짜 기준 walk-forward 검증을 수행한다. champion baseline은 `전일 외국인 보유수량 유지`이다.
- 최신 평가 데이터: KRX Data Marketplace 기반 외국인 보유수량 CSV는 2019-01-02부터 2026-06-26까지 현재 상장 제한 32종목의 58,784개 관측치만 포함한다. 비제한 종목 history는 운영 목적과 맞지 않아 학습 데이터에서 제거한다.
- 운영 universe: 외국인 취득한도 제한이 있는 종목만 학습/평가/promotion 대상이다. 금융위 2023-01-25 붙임4의 33개 법령 제한 종목을 현재 stock master와 조인해 32개 현재 상장 제한 종목을 확정했다. `SBS콘텐츠허브(046140)`는 현재 stock master에 없어 제외 사유를 리포트에 남긴다.
- 최신 평가 결과: 제한 32종목, 관측치 58,784행, 학습 샘플 52,693개로 재학습했다. 선택 후보는 `stock_routed_ml_ensemble`이며, persistence baseline MAE 53,912.99 / RMSE 152,521.80 / MAPE 0.046983에서 순수 stock-routed ML MAE 51,539.19 / RMSE 147,477.74 / MAPE 0.044908, guarded runtime MAE 51,539.19 / RMSE 147,477.74 / MAPE 0.044908로 개선되어 `promoted`로 기록했다. guarded runtime 기준 MAE 개선율은 4.4030%, RMSE 개선율은 3.3071%, MAPE 개선율은 4.4167%다.
- 제한 종목 목록: `reports/foreign-ownership-restricted-universe-report.json`, `data/training/foreign_ownership_restricted_stock_codes.csv`에 저장한다.
- 과거 full-universe 진단: 전체 국내주식 full-universe 학습 결과는 한도 경고 목적과 맞지 않아 운영 champion 근거로 사용하지 않는다.
- serving 정책: `release_status=promoted`이면 종목별 검증 gate를 적용한다. 현재 운영 runtime은 ML 29종목, persistence baseline 0종목을 선택한다. 검증상 ML이 이긴 종목은 artifact 내부 `model_by_stock`, `blend_alpha_by_stock`, `model_prediction_modes`에 저장된 종목별 ML 후보를 사용한다.
- SOTA 비교: `reports/foreign-ownership-quantity-sota-benchmark.json`은 제한 universe의 동일 walk-forward fold/test sample 기준으로 재생성했다. 0% 취득불허 3종목은 양수 보유수량 학습 샘플이 없어 SOTA/ML sample 비교에서는 제외되고, 나머지 29종목 21,895개 test sample을 비교한다. `hannah_promoted_guarded_runtime` MAE 51,539.19 / RMSE 147,477.74 / MAPE 0.044908이 persistence baseline MAE 53,912.99 / RMSE 152,521.80 / MAPE 0.046983, N-HiTS MAE 52,863.38 / RMSE 150,345.74 / MAPE 0.046955, PatchTST MAE 54,521.01 / RMSE 154,153.91 / MAPE 0.049739보다 낮다.
- 발표자료용 성능 요약: `docs/FOREIGN_OWNERSHIP_MODEL_PRESENTATION.md`에 baseline/SOTA 비교 표와 핵심 메시지를 별도로 정리한다.
- 장기 window 실험: 2015-01-02부터 2026-06-26까지 확장한 87,240개 관측치 실험은 `reports/foreign-ownership-quantity-training-report-2015-2026-experiment.json`, `reports/foreign-ownership-quantity-sota-benchmark-2015-2026-experiment.json`에 보존한다. 이 실험은 guarded runtime MAE 55,357.24로 2019~2026 champion보다 나빠 운영 artifact로 채택하지 않는다.
- 출력: 예측 외국인 보유수량 `min/base/max`, 예측 순취득수량, 이를 현재 한도수량으로 나눈 한도소진율 `min/base/max`, 관측치 수, confidence, model version.
- 한계: 현재 모델은 전날까지의 외국인 보유수량만 사용한다. 보유수량은 종목별 수급 이벤트와 리밸런싱에 영향을 받으므로, 더 높은 정확도를 위해서는 향후 가격/거래대금/시장 전체 외국인 순매수 같은 추가 feature가 필요하다.

## 글로벌 피어 종목 매칭 모델
- 모델 버전 prefix: `global-peer-hybrid-ranker`
- 목적: 외국인 투자자가 낯선 한국 상장사를 볼 때 익숙한 미국 상장 peer와 함께 이해할 수 있도록 headline, 설명, primary peer, 후보 peer 목록을 생성한다.
- 입력: 한국 종목코드, 한글명, 영문명, 시장구분, alias, 선택 설명문.
- 학습 universe: `data/reference/korea_stock_universe.csv`의 한국 종목 3,967개와 `data/reference/us_stock_universe.csv`의 미국 listed symbol 12,916개를 함께 학습한다. 미국 universe는 NASDAQ Trader symbol directory의 `nasdaqlisted.txt`, `otherlisted.txt`를 정규화해 생성한다.
- 모델 구조: 한국·미국 종목명, 시장, 거래소, business keyword, 섹터, 산업, 사업모델, 규모 버킷, 동일업종 비교 종목, 매출, 영업이익, 순이익, anchor profile을 cross-market profile corpus로 만들고 TF-IDF retrieval, TruncatedSVD semantic embedding, 재무/업종/규모 feature, supervised pairwise LogisticRegression reranker를 저장한다.
- 재무/규모 feature: `data/reference/global_peer_fundamentals.csv`의 `market_cap_usd`, `revenue_usd`, `operating_income_usd`, `net_income_usd`를 로그 스케일 feature로 변환한다. 추론 ranking은 pairwise ranker 60%, base text/semantic/financial score 40%로 calibration한다.
- 재무 데이터 원천: 한국 재무는 OpenDART `fnlttSinglAcntAll`, 한국 시가총액은 KRX Open API 일별매매정보 `MKTCAP` 또는 Naver mobile stock JSON `marketValue`, 미국 재무는 SEC `companyfacts`와 ticker-CIK mapping, 미국 시가총액은 NASDAQ quote summary `MarketCap`을 사용한다.
- 최신 fundamentals coverage: `data/reference/global_peer_fundamentals.csv`는 한국 2,916개, 미국 5,585개, 총 8,501개 row를 포함한다. 시가총액은 7,967개, 매출은 6,837개, 영업이익은 6,986개, 순이익은 7,695개 row에 채워져 있다.
- 최신 국내 업종 coverage: `data/reference/korea_stock_industries.csv`는 Naver 동일업종 비교 데이터 2,649개를 포함하며, 이 중 2,451개가 specific sector/industry feature를 제공한다.
- eligible peer: 미국 universe 전체를 학습 corpus에 포함하되, ETF/ETN/fund/right/unit/warrant/preferred/note/test issue는 company peer 후보에서 제외한다.
- 평가: curated anchor top1 accuracy는 0.8571이고, supervised pairwise ranker benchmark는 top1 accuracy 0.9286, top3 accuracy 1.0, MRR 0.9643이다.
- 출력: `"Alteogen Is The 'Halozyme Therapeutics' of South Korea — A Global Biotech Platform Leader"` 같은 팝업 headline, business summary, peer rationale, 섹터, 산업, 사업모델, 규모 버킷, 매출/영업이익/순이익, 재무 데이터 출처, 매칭 근거 배열, confidence, model version.
- 설명 가능성: `matched_factors`는 섹터, 산업, 사업모델, 규모, 재무 유사도, 모델 유사도 기준으로 생성한다. 검증된 anchor는 기술·수익모델 같은 세부 근거를 함께 제공한다.
- AI smoke 테스트: `reports/global-peer-ai-smoke-report.json`과 `docs/GLOBAL_PEER_AI_SMOKE.md`에 15개 대표 한국 종목의 실제 primary peer 결과를 남긴다. 최신 smoke에서는 Samsung Electronics→Micron, SK hynix→Micron, NAVER→Alphabet, Hyundai Motor→Toyota, LG Electronics→Whirlpool, SK Telecom→Verizon, Alteogen→Halozyme을 확인했다.
- 전종목 coverage 테스트: `reports/global-peer-full-coverage-report.json`은 한국 master 3,967개 전부를 실제 matcher에 넣어 추론 성공률, 동일회사 중복, matched factor 누락, LOW confidence, generic sector 비율을 검증한다. 최신 quality gate는 3,967/3,967개 성공으로 `pass`이고 LOW confidence 29.2664%도 confidence monitoring `pass`다.
- 전종목 현재 결과: `docs/GLOBAL_PEER_ALL_RESULTS.md`는 3,967개 전 종목의 primary peer, confidence, domain match, financial context를 표로 남긴다. 동일 내용은 기계 검증용 `reports/global-peer-all-results.json`, 분석용 `reports/global-peer-all-results.csv`에도 저장한다.
- 산출물: `src/hannah_montana_ai/model_store/global_peer_ml.joblib`, `reports/global-peer-training-report.json`, `reports/global-peer-ai-smoke-report.json`, `reports/global-peer-korea-industry-sync-report.json`, `reports/global-peer-fundamentals-sync-report.json`, `reports/global-peer-full-coverage-report.json`, `reports/global-peer-all-results.json`, `reports/global-peer-all-results.csv`, `docs/GLOBAL_PEER_ALL_RESULTS.md`, `data/reference/us_stock_universe.csv`, `data/reference/global_peer_fundamentals.csv`, `data/reference/korea_stock_industries.csv`
- 재학습: `uv run python scripts/sync_us_stock_universe.py`로 미국 universe를 갱신하고, `uv run python scripts/sync_global_peer_fundamentals.py`, `uv run python scripts/sync_korea_stock_industries.py`로 한국·미국 재무/규모/업종 dataset을 갱신한 뒤, `uv run python scripts/train_global_peer_model.py`, `uv run python scripts/build_global_peer_ai_smoke_report.py`, `uv run python scripts/build_global_peer_full_coverage_report.py`, `uv run python scripts/build_global_peer_all_results_report.py`로 artifact와 report를 재생성한다.

## 입력
- source type: `NEWS` 또는 `DISCLOSURE`
- 제목
- snippet
- 후보 종목 목록
- 내부 국내주식 universe master
- 전 종목 stock linker 학습 term

## 출력
- 대표 종목
- 이벤트 태그
- 감성: `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- 중요도: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- 중복 제거 키
- 모델 버전

## 학습 데이터
- 수집 raw 위치: `data/raw/collected_alerts.jsonl`
- 약지도 라벨 위치: `data/processed/weak_labeled_alerts.jsonl`
- 약지도 distillation 리포트: `reports/weak-distillation-report.json`
- 버전별 release 리포트: `reports/model-release-report.json`
- pseudo-label promotion monitoring 리포트: `reports/pseudo-label-promotion-monitoring.json`
- 수동 curated corpus: `data/training/financial_alert_corpus.jsonl`
- 합성 증강 corpus: `data/training/financial_alert_augmented.jsonl`
- 뉴스 제목체 증강 corpus: `data/training/financial_alert_news_style_augmented.jsonl`
- 사람이 검수한 실제 뉴스 학습 gold: `data/training/financial_alert_real_news_gold.jsonl`
- 실제 원문 기사·공시 전문 학습 gold: `data/training/financial_alert_full_content_gold.jsonl`
- curated gold benchmark: `data/evaluation/financial_alert_eval.jsonl`
- 사람이 검수한 실공시 gold: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 사람이 검수한 실제 뉴스 평가 gold: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 이번 artifact 이벤트 학습 샘플 수: 4,649
- supervised 학습 샘플 수: 8,607
- teacher-gated pseudo-label 학습 샘플 수: 1,026
- 실제 수집 raw 총량: 83,105건
- 실제 수집 원천: OpenDART 공시검색 25,966건
- 실제 수집 원천: Naver News Search 57,139건
- 합성 증강 샘플 수: 1,656건
- 뉴스 제목체 증강 샘플 수: 1,872건
- 실제 뉴스 학습 gold 샘플 수: 63건
- 실제 원문 기사·공시 전문 학습 gold 샘플 수: 20,000건
- 전문 학습 gold 구성: 뉴스 전문 19,727건, OpenDART document 전문 273건, 기존 내부 회귀 seed
- 전문 학습 source license policy: `licensed_naver_original_full_text_v1`, `opendart_public_disclosure_text_v1`, 내부 회귀 seed
- 전문 확장 학습 정책: 관련 종목이 제목·snippet·전문에서 확인된 기사만 live query-relevant gate와 학습 승격 후보에 포함한다.
- 요약 품질 정책: What/Why/Impact 3줄은 중복, boilerplate, fallback, 종목 불일치, 낮은 confidence를 별도 quality finding으로 기록하고 release 판단에서 관측한다.
- 라이브 품질 보강 정책: serving 단계에서 짧은 종목명 과매칭, 광고·푸터·관련기사 노이즈, 전문 수집 실패 과신을 보정한다. `SUMMARY_ONLY` 응답은 정보량이 제한된 상태이므로 confidence를 보수적으로 cap하고, 운영 감사에서 별도 finding으로 추적한다.
- 약한 전문 라벨 정책: 사람이 검수하지 않은 전문 수집 라벨은 원문 분석·요약 입력과 검수 후보 생성에는 사용하지만 이벤트·감성·중요도 supervised loss에는 넣지 않는다.
- gold benchmark 샘플 수: 768건
- 실공시 gold 샘플 수: 30건
- 실제 뉴스 gold 샘플 수: 80건
- 약지도 후보 수: 83,105건
- distillation 통과 후보 수: 5,250건
- teacher confidence gate 통과 후 artifact 학습 승격 후보 수: 1,026건
- weak-label distillation 승격 수: 339건
- 종목 후보 큐 승격 수: 687건
- 종목 후보 큐 승격 종목 수: 687개
- 수집기는 429 rate limit, 5xx 장애, 일시적 read timeout과 네트워크 오류에 대해 재시도와 지수 백오프를 수행한다.
- 수집 실패로 새 결과가 기존 raw 수보다 줄어들면 기본값으로 기존 코퍼스를 덮어쓰지 않는다.
- 수집 raw와 약지도 라벨은 학습 재현성 때문에 커밋하지만, 외부 API 키와 비공개 credential은 포함하지 않는다.
- 국내주식 universe: `data/reference/korea_stock_universe.csv`
- stock universe sync 리포트: `reports/stock-universe-sync.json`
- stock coverage 리포트: `reports/stock-coverage-report.json`
- 종목·라벨 균형 학습 승격 후보 큐: `data/curation/stock_training_candidate_queue.jsonl`
- 학습 승격 후보 큐 리포트: `reports/stock-training-candidate-report.json`
- 학습 gold 검수 배치: `data/curation/stock_gold_training_review_batch.jsonl`
- 평가 gold 검수 배치: `data/curation/stock_gold_evaluation_review_batch.jsonl`
- gold 검수 배치 리포트: `reports/stock-gold-review-batch-report.json`
- gold 검수 validation 리포트: `reports/stock-gold-review-validation-report.json`
- gold active review 리포트: `reports/stock-gold-active-review-report.json`
- gold coverage review plan: `data/curation/stock_gold_coverage_review_plan.jsonl`
- gold coverage review plan 리포트: `reports/stock-gold-coverage-plan-report.json`
- gold coverage active review packet: `data/curation/stock_gold_coverage_active_review_packet.jsonl`
- gold coverage active review 리포트: `reports/stock-gold-coverage-active-review-report.json`
- gold coverage promotion 리포트: `reports/stock-gold-coverage-promotion-report.json`
- gold coverage validation 리포트: `reports/stock-gold-coverage-validation-report.json`
- full-universe Codex reference coverage 리포트: `reports/full-universe-codex-coverage-report.json`
- confidence calibration 리포트: `reports/model-confidence-calibration.json`
- stock candidate quota experiment 리포트: `reports/stock-candidate-quota-experiment.json`
- 실시간 뉴스 smoke/drift 리포트: `reports/live-news-evaluation-report.json`
- 실시간 뉴스 최신성 status 리포트: `reports/live-news-monitoring-status.json`
- 실시간 뉴스 전문 요약 품질 감사 리포트: `reports/live-news-quality-audit-report.json`
- 승인된 학습 gold 승격 파일: `data/training/financial_alert_stock_review_gold.jsonl`
- 승인된 평가 gold 승격 파일: `data/evaluation/financial_alert_stock_review_gold.jsonl`
- gold 승격 리포트: `reports/stock-gold-promotion-report.json`
- OpenDART 고유번호 기반 universe 종목 수: 3,967개
- 분석 API는 요청 후보 종목이 비어 있거나 50개 이하 후보에 포함되지 않은 종목도 내부 universe master로 매핑한다.
- 전체 universe 3,967개 종목의 6자리 종목코드 매핑을 회귀 테스트로 검증한다.
- stock linker ML 학습 데이터: `data/training/stock_linker_training.jsonl`
- stock linker ML artifact: `src/hannah_montana_ai/model_store/stock_linker_ml.joblib`
- stock linker 학습 리포트: `reports/stock-linker-training-report.json`
- raw 후보에서 보수적 종목명·종목코드 매칭으로 확인한 종목 수: 3,613개
- 학습 승격 후보 큐 샘플 수: 15,720건
- 학습 승격 후보 큐 종목 수: 3,506개
- 학습 gold 검수 배치 종목 수: 300개
- 평가 gold 검수 배치 종목 수: 100개
- coverage review plan 학습 목표 종목 수: 1,500개
- coverage review plan 평가 목표 종목 수: 500개
- coverage review plan 전체 계획 종목 수: 2,000개
- coverage review plan과 기존 supervised/evaluation 종목을 합친 후보 큐 커버 종목 수: 2,068개
- coverage active review packet row 수: 2,000건
- coverage active review 학습 wave 수: 13개
- coverage active review 평가 wave 수: 5개
- coverage packet 승인 승격 row 수: 학습 1,500건, 평가 500건
- full-universe Codex reference 보강 row 수: 1,920건
- 유효 6자리 국내주식 stock review reference coverage 수: 3,920개
- 유효 6자리 국내주식 stock review reference 누락 수: 0개
- coverage packet validation 상태: `pass`
- coverage packet validation 목표: 학습 1,500종목, 평가 500종목, wave별 승인 100종목
- release service readiness 상태: `pass`
- 외국인 보유/취득 수량 학습 데이터: `data/training/foreign_ownership_quantity_history.csv`
- 외국인 보유/취득 수량 ML artifact: `src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib`
- 외국인 보유/취득 수량 학습 리포트: `reports/foreign-ownership-quantity-training-report.json`
- 외국인 보유/취득 수량 후보 리포트: `reports/foreign-ownership-quantity-training-candidate-report.json`
- 외국인 보유/취득 수량 SOTA 비교 리포트: `reports/foreign-ownership-quantity-sota-benchmark.json`
- 외국인 취득한도 제한 종목 리포트: `reports/foreign-ownership-restricted-universe-report.json`
- audited gold readiness 상태: `pass`
- 현재 coverage validation 승인 가능 종목 수: 학습 1,500개, 평가 500개
- supervised/reference 학습 coverage 종목 수: 3,422개
- evaluation/reference coverage 종목 수: 557개
- stock review gold train/eval 합집합 기준 유효 6자리 국내주식 coverage 종목 수: 3,920개
- bootstrap 실서비스 readiness는 현재 `pass`이며, 모델 quality gate와 stock-candidate pseudo coverage 기준을 충족했다.
- audited gold coverage gate는 현재 `pass`이며, `codex_review_approved` coverage packet이 학습 1,500종목, 평가 500종목, wave별 100종목 기준을 충족한다.
- 학습 승격 후보 큐는 `needs_human_review` 상태이며, 사람이 검수해 승격하기 전까지 gold label이나 supervised 정답셋으로 취급하지 않는다.
- gold 검수 배치도 `needs_human_review` 상태이며, 사람이 승인하기 전까지 supervised 학습셋이나 evaluation gold로 편입하지 않는다.
- gold coverage review plan도 `needs_human_review` 상태이며, 장기 검수 순서를 정하는 산출물이지 자동 정답셋이 아니다.
- coverage active review packet의 모델 제안 라벨과 confidence는 Codex 대리 검수의 입력 신호로 사용되며, 승인 lineage를 함께 보존한다.
- 실시간 뉴스 evaluation batch도 라벨 없는 운영 표본이므로 drift와 confidence 점검에만 쓰고, `final_*` 라벨 승인 전까지 F1이나 supervised gold로 취급하지 않는다.
- 실시간 뉴스 quality audit batch도 라벨 없는 운영 표본이다. 전체 pass rate와 별도로 `QUERY_STOCK_ABSENT`를 제외한 query-relevant pass rate를 운영 후보 필터 품질 지표로 본다.
- serving 응답은 이벤트·감성·중요도·종목 매핑 confidence를 함께 반환한다. 이 값은 품질 관측과 UI 표시용 메타데이터이며, Hannah가 신뢰도 기반 자동 차단 여부를 결정하지 않는다.
- `human_review_approved` 또는 `codex_review_approved` 상태와 검수자 메타데이터, 최종 이벤트·감성·중요도 라벨이 모두 있는 검수 row만 별도 stock review gold 파일로 승격된다.
- coverage packet에서 승격된 gold row는 source review wave/stage/reason과 모델 제안 lineage를 함께 보존한다.
- coverage validation 리포트는 승격 전 승인 가능 row가 학습 1,500개 종목, 평가 500개 종목, wave별 100개 종목 목표를 채우는지 검사한다.
- active review 리포트는 모델 제안 라벨, 신뢰도, disagreement를 검수 보조 정보로 제공하며 자동 정답으로 쓰지 않는다.
- confidence calibration 리포트는 평가셋별 확률 calibration과 고신뢰 오답을 release monitoring 신호로 기록하며 라벨을 생성하거나 승격하지 않는다.
- 평가와 coverage 스크립트는 승인된 stock review gold 파일을 포함한다.
- 학습 스크립트는 `codex_review_approved` row를 committed reference/evaluation coverage로 기록하되, 자기 라벨 재주입으로 인한 self-training feedback loop를 막기 위해 supervised loss에서는 제외한다.
- 현재 `codex_review_approved` reference row 3,420건은 supervised loss에서 제외되고, 전 종목 대응 coverage와 평가/운영 추적용 lineage로만 사용한다.
- 약지도 라벨은 후보 풀로 유지하고 teacher confidence gate와 라벨별 quota를 통과한 pseudo-label만 이벤트 모델 학습에 승격한다.
- 이벤트·감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 사람이 검수하지 않은 실제 전문 약한 라벨 4,984건을 supervised loss와 holdout 정답에서 제외한다.
- 실제 뉴스 학습 gold와 실제 뉴스 평가 gold는 동일 문장을 공유하지 않는다.

## 학습 방식
- `scripts/collect_training_data.py`가 Naver News Search와 OpenDART에서 원문 제목·snippet·링크를 수집한다.
- full-content v2 학습 파이프라인은 Naver News Search를 발견 단계로 사용하고, Hana-OmniLens-API가 사용 허가된 원문 URL에서 저장한 기사 전문/이미지 metadata와 OpenDART document 전문을 모델 입력 feature로 사용한다.
- `LabeledAlert`는 `title`, `snippet`, `full_content`, `content_availability`, `source_license_policy`, `content_hash`를 보존하며, 학습·평가 시 전문이 있으면 `title + snippet + full_content`를 우선 사용한다.
- 기존 제목/snippet v1 artifact는 폐기하지 않고 full-content v2의 fallback, 회귀 비교, teacher 후보로 유지한다.
- `weak_labeler.py`가 수집 원문에 약지도 라벨을 부여해 학습 후보를 만든다.
- `weak_distiller.py`가 약지도 후보의 노이즈를 제거하고 고신호 후보를 선별한다.
- supervised teacher 모델이 distillation 후보를 다시 예측하고, 이벤트·감성·중요도 confidence와 weak-label 합의 기준을 통과한 후보만 pseudo-label로 승격한다.
- `scripts/build_augmented_training_data.py`가 저작권 문제가 없는 금융 문장 증강 corpus를 생성한다.
- `scripts/build_news_style_training_data.py`가 실제 Naver 뉴스 제목체를 반영한 저작권 안전 증강 corpus를 생성한다.
- `scripts/build_gold_evaluation_data.py`가 훈련셋과 별도 문장 패턴의 768건 benchmark를 생성한다.
- `scripts/train_ml_model.py`가 TF-IDF feature와 Logistic Regression 기반 supervised ML 모델과 teacher-gated student 이벤트 모델을 학습한다.
- 이벤트 태그는 char n-gram과 한국어 금융 token n-gram을 결합한 One-vs-Rest multilabel classifier로 학습한다.
- 이벤트 태그 모델은 `source_type`을 feature로 함께 사용해 공시 입력의 `DISCLOSURE` 라벨 누락을 줄인다.
- 감성은 char n-gram과 한국어 금융 token n-gram을 결합한 다중 클래스 Logistic Regression으로 학습한다.
- 중요도는 source type, char n-gram, 한국어 금융 token n-gram을 결합한 다중 클래스 Logistic Regression으로 학습한다.
- 금융 tokenizer는 `잠정실적`, `공급계약`, `유상증자`, `무상증자`, `타법인주식`, `자기주식처분`, `주주총회`, `소송등`, `상장폐지`, `주주환원`, `주식교환`, `지분인수`, `지분매각`, `리밸런싱`, `공급망`, `생산차질` 같은 한국어 복합 금융 표현을 도메인 token으로 추가한다.
- 종목 매핑은 request 후보를 먼저 사용하고, 같은 종목코드가 없으면 내부 universe master를 fallback으로 사용한다.
- 내부 universe fallback은 TF-IDF char n-gram stock linker가 예측한 종목코드를 먼저 확인한 뒤, 대표 종목 오탐 방지를 위해 실제 선두 종목 term 매칭 여부를 검증한다.
- 종목명 매칭은 같은 위치에서 발견된 후보 중 더 긴 고유 종목명을 우선한다. 예를 들어 `SK하이닉스` 기사에서 `SK`가 요청 후보로 들어와도 `SK하이닉스` 전체명이 본문에 있으면 짧은 후보명은 대표 종목으로 승격하지 않는다.
- 번역 품질 보조 모델은 `local-financial-glossary-v2`이며, 실제 공시에서 반복되는 매매거래정지, 상장폐지 사유, 소송 청구, 타법인 주식 취득, 자기주식, 전환사채, 관리·투자주의 환기 용어를 우선 glossary/fallback rule로 정규화한다.
- `reports/translation-sample-report.json`은 실제 뉴스·공시 gold 표본 기준 원문, 로컬 번역 보조 결과, AI 분석 결과, glossary, review finding을 함께 보존한다.
- stock linker는 전체 universe 3,967개 종목코드와 trainable 종목명을 학습 term으로 사용한다. 현재 전 종목코드 템플릿 정확도는 1.0, trainable 종목명 템플릿 정확도는 0.9921이다.
- 이벤트 태그 probability threshold는 기본 0.30으로 두고, 실제 뉴스 gold 기준으로 `CONTRACT` 0.46, `CORPORATE_ACTION` 0.50, `EARNINGS` 0.40, `GENERAL_MARKET` 0.30, `MACRO` 0.54, `RISK` 0.34를 label별 calibration했다.
- 분석기는 실제 뉴스에서 반복되는 `수출`, `업황`, `공급망`, `환율`, `금리`, `물가`, `정책+지원/중소기업`, `시총`, `주가 급등`, `증시` 문맥을 이벤트 태그 보조 규칙으로 반영한다.
- 학습 시 검수·균형 코퍼스를 80:20 holdout으로 나눠 검증한 뒤 전체 코퍼스로 최종 artifact를 재학습한다.
- 종목 후보 큐에서는 teacher gate와 종목별 quota를 통과한 687건을 이벤트 모델 학습에 추가했다.
- 종목 후보의 per-stock quota는 1건으로 제한해 687건이 687개 종목에 분산되도록 했다.
- `stock-candidate-quota-experiment`는 quota 탐색 참고 리포트이며, current release artifact는 full-content v2 재학습 리포트의 687건/687종목 bootstrap coverage를 기준으로 pass했다.
- 생성 artifact는 `src/hannah_montana_ai/model_store/financial_nlp_ml.joblib`이다.

## Holdout 검증 결과
- 위치: `reports/ml-training-report.json`
- 이벤트 학습 split: 2,898건
- 검증 split: 725건
- 이벤트 subset recall: 0.9931
- 이벤트 macro F1: 0.9944
- 감성 accuracy: 0.9945
- 중요도 accuracy: 0.9945
- 라벨별 F1 최저 구간: `MACRO` 0.9851, `CAPITAL_ACTION` 0.9885, `EARNINGS` 0.9932, `CONTRACT` 0.9942
- 감성·중요도 confusion matrix를 함께 기록한다.

## Gold 평가 결과
- 위치: `reports/ml-model-evaluation.json`
- 평가 샘플 수: 768
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 0.9844
- 감성 accuracy: 0.9688
- 중요도 accuracy: 0.9583
- 종목 매핑 accuracy: 1.0
- 라벨별 precision, recall, F1과 감성·중요도 confusion matrix를 함께 기록한다.

## 실공시 Gold 평가 결과
- 위치: `data/evaluation/financial_alert_real_disclosure_gold.jsonl`
- 평가 샘플 수: 30
- 이벤트 태그 recall: 1.0
- 이벤트 태그 macro F1: 0.9867
- 감성 accuracy: 1.0
- 중요도 accuracy: 1.0
- 종목 매핑 accuracy: 1.0

## 실제 뉴스 Gold 평가 결과
- 위치: `data/evaluation/financial_alert_real_news_gold.jsonl`
- 평가 샘플 수: 80
- 이벤트 태그 recall: 0.9875
- 이벤트 태그 macro F1: 0.9221
- 감성 accuracy: 0.9750
- 중요도 accuracy: 0.9625
- 종목 매핑 accuracy: 1.0

## Confidence calibration
- 위치: `reports/model-confidence-calibration.json`
- benchmark 샘플 수: 768
- benchmark 이벤트 멀티라벨 결정 수: 6,144
- benchmark 이벤트 expected calibration error: 0.074827
- benchmark 이벤트 Brier score: 0.01309
- benchmark 감성 top confidence ECE: 0.164898
- benchmark 중요도 top confidence ECE: 0.129593
- 실제 뉴스 gold 이벤트 expected calibration error: 0.117664
- confidence 리포트는 고신뢰 오답을 따로 기록해 운영 알림 노출 전 threshold 재보정과 human review 우선순위 판단에 사용한다.

## Release gate
- 위치: `reports/model-release-report.json`
- 현재 모델 버전: `financial-ml-tfidf-logreg-20260622090407`
- 전체 상태: `pass`
- release gate는 holdout, 768건 benchmark, 30건 OpenDART 실공시 gold, 80건 Naver 실제 뉴스 gold 평가를 모두 포함한다.
- pseudo-label consistency check는 distillation 리포트의 승격 수와 학습 리포트의 pseudo-label 학습 수가 일치하는지 검증한다.
- `overall_status=pass`는 모델 품질 release gate 통과를 뜻한다.
- `service_readiness.overall_status=pass`는 release quality gate, consistency check, 500종목 이상 stock-candidate pseudo coverage를 충족한 bootstrap 실서비스 readiness를 뜻한다.
- `audited_gold_readiness.overall_status=pass`는 `human_review_approved` 또는 `codex_review_approved` coverage packet gold가 학습 1,500종목, 평가 500종목, wave별 100종목 기준을 충족했다는 뜻이다.

## Pseudo-label promotion gate
- 위치: `reports/pseudo-label-promotion-monitoring.json`
- 83,105건 raw 후보 중 5,250건이 고신호 후보로 남았다.
- teacher confidence 또는 weak-label 합의 기준에서 4,388건이 탈락했다.
- weak-label distillation에서는 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 19건을 student 이벤트 모델 학습에 승격했다.
- 종목 후보 큐에서는 `RISK` 256건, `CONTRACT` 242건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 42건, `EARNINGS` 17건, `MACRO` 10건을 teacher gate로 추가 승격했다.
- `CAPITAL_ACTION`은 현재 quota를 채웠고, `EARNINGS`, `MACRO`, `CONTRACT`, `RISK`, `CORPORATE_ACTION`은 gate 통과 후보 품질을 계속 모니터링한다. `DISCLOSURE`는 공시 라벨 과잉 투입을 막기 위해 gold gate 실험 전까지 quota 0으로 유지한다.

## 한계
- Naver 뉴스 gold set을 80건으로 확대하고 종목코드 30개를 포함했지만, 분기별 증분 수집과 업종별 샘플 균형은 계속 관리해야 한다.
- 국내주식 universe 3,967개 중 유효 6자리 숫자 종목코드 3,920개는 stock review reference coverage로 모두 포함한다.
- 다만 full-universe Codex reference row는 supervised loss에 넣지 않으므로, 실제 종목별 모델 품질은 운영 로그와 사람 검수 gold로 계속 보강해야 한다.
- raw 후보는 3,613개 종목까지 매칭되므로 다음 단계는 raw 후보를 종목별·라벨별로 검수해 사람이 승인한 supervised/gold 데이터로 승격하는 것이다.
- 후보 큐는 3,506개 종목을 포함하지만 약지도 기반 검수 대기 데이터이므로 gold label로 직접 사용하지 않는다.
- coverage review plan은 2,000개 종목의 검수 과제였고, 현재 Codex 대리 승인 기준으로 audited readiness는 통과했다.
- 현재 artifact는 후보 큐 중 687개 종목의 687건만 teacher gate를 통과한 event-model-only pseudo-label로 제한 투입했다.
- 약지도 라벨은 대규모 bootstrapping 용도이며, teacher confidence gate를 통과한 일부 후보만 artifact 이벤트 모델 학습에 투입한다.
- 현재 distillation 후보는 supervised teacher가 다시 검증해야 하는 후보 풀이지 최종 정답셋이 아니다.
- pseudo-label은 teacher confidence와 release gate를 통과한 라벨만 제한 승격한다. `DISCLOSURE`와 `GENERAL_MARKET`은 후보가 있어도 현재 artifact 학습에는 투입하지 않는다.
- 사람이 검수한 실데이터 gold label set은 현재 실공시 30건, 실제 뉴스 80건이므로 주기적으로 확대해야 한다.
- 현재 release artifact는 실제 원문 기사·공시 전문 export와 내부 회귀 seed를 supervised 입력으로 사용한다. 저장 허가가 없는 provider를 추가할 경우 학습 원문 저장을 비활성화하고 feature hash와 사람이 검수한 label lineage만 남긴다.
- 실제 투자 판단을 위한 추천 모델이 아니다.

## 서비스 readiness gate
- `reports/service-readiness-report.json`은 현재 release, audited gold readiness, live-news monitoring, full-universe reference coverage, stock linker coverage, pseudo-label monitoring, confidence calibration, confidence observe-only 정책을 집계한다.
- 최신 `reports/service-readiness-report.json`은 `overall_status=pass`이며, 모델 버전 `financial-ml-tfidf-logreg-20260622090407` 기준 전체 readiness check가 통과한다.
- `reports/full-universe-codex-coverage-report.json` 기준 유효 6자리 국내주식 reference coverage 누락은 0이다.
- `reports/stock-coverage-report.json` 기준 supervised/reference coverage는 3,422개 종목, evaluation/reference coverage는 559개 종목이다.
- 최신 `reports/live-news-monitoring-status.json`은 `overall_status=pass`이며, live-news smoke 표본 100건 기준 `sampled_stock_model_match_rate=0.8`을 기록한다. 이 리포트는 라벨 없는 검색 노이즈 포함 drift 관측용이다.
- 최신 `reports/live-news-quality-audit-report.json`은 1,000건 최신 query-relevant Naver 표본에서 전체 quality pass rate 0.991, query-relevant quality pass rate 0.991, full-content rate 0.69, sampled stock model match rate 0.999를 기록한다.
- service readiness gate는 confidence를 품질 관측과 UI 표시용 메타데이터로만 인정하며, Hannah는 신뢰도 기반 자동 차단 결정을 만들지 않는다.

## 지속 운영 관리
- 실제 뉴스 gold label set을 월별로 증분 확대하고 drift를 감시한다.
- Naver 뉴스 수집 쿼리와 일 단위 shard 수집을 운영 credential 환경에서 계속 수행한다.
- 사람이 검수한 gold label과 약지도 label 품질을 비교해 사람 검수 supervised/evaluation gold를 보강한다.
- live-news report가 `stale`이면 최신 release 품질 근거에서 제외하고 운영 Naver credential로 배치를 다시 생성한다.
- 최신 대량 학습 배치는 5,000건 전문 기준선을 20,000건 전문 후보로 확장했고, 재학습 후 live quality audit 1,000건과 release/readiness gate를 다시 통과했다.
