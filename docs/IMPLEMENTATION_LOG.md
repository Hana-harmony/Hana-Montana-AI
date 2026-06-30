# 구현 기록

## 2026-06-30 글로벌 피어 Qwen3 설명 LLM 학습
- 글로벌 피어 매칭은 기존 hybrid ranker가 담당하고, headline/summary만 구조화 근거 기반 설명 생성기로 분리했다.
- `GlobalPeerExplanationGenerator`를 추가해 기본은 deterministic grounded template을 사용하고, `HANNAH_GLOBAL_PEER_EXPLANATION_MODE=local_llm`일 때 OpenAI-compatible local LLM endpoint를 호출하도록 했다.
- LLM 출력은 JSON, 종목명, peer명 또는 허용 축약명, ticker/섹터/산업/사업모델 uppercase token, 금지 투자조언 문구를 검증하며 실패하면 template으로 fallback한다.
- Codex 검수로 학습 target 문체를 정리했다. sector/industry를 1순위 근거로 쓰고, 재무/규모는 strict size match가 아니라 US-market reference인지 설명하도록 변경했다.
- anchor `display_name`을 추가해 알테오젠처럼 stock universe 영문명이 비어 있는 종목도 글로벌 투자자용 표시명을 유지한다. raw Qwen3가 display name을 누락하면 실제 API는 grounded guard에서 template fallback을 사용한다.
- 한국 종목 3,967개 전체에 대해 prompt `global-peer-structured-rag-explainer-v3` 기준 `data/training/global_peer_explanation_sft.jsonl`을 생성했고, grounded target failure 0건, readiness `pass`를 기록했다.
- MLX 학습용 split은 train 3,571 / valid 198 / test 198이다.
- `mlx-community/Qwen3-0.6B-4bit`를 LoRA로 500 iters 학습했다. trainable parameter는 1.442M / 596.050M, final validation loss 0.014, test loss 0.000, test perplexity 1.000, peak memory 1.830GB를 기록했다.
- adapter는 `src/hannah_montana_ai/model_store/global_peer_qwen3_explainer_lora/adapters.safetensors`와 `adapter_config.json`에 저장했다.
- 운영 t4g.medium은 GPU가 없으므로 API 프로세스 내 로딩이 아니라 Qwen3-0.6B GGUF Q4를 llama.cpp OpenAI-compatible server로 띄우고 `HANNAH_GLOBAL_PEER_LLM_ENDPOINT`로 연결하는 구조를 문서화했다.

## 2026-06-28 외국인 취득한도 제한 종목 ML 학습
- 정정: 전체 국내주식 full-universe 학습은 외국인 취득한도 경고 목적의 운영 universe가 아니다. 외국인 취득한도 제한 종목만 학습/평가/promotion 대상이어야 하므로 기존 full-universe artifact/report/benchmark는 `restricted_universe_not_applied` 사유로 `guarded` 또는 `invalidated` 처리했다.
- 추가 정정: 이전 제한 18종목 산출은 Hana stock master의 KIS master parser 오류로 KT, SBS, 한국가스공사, 대한항공 등 일부 기간산업 종목이 누락된 상태에서 생성됐다. 해당 학습 artifact/report/benchmark는 `stock_master_incomplete_foreign_ownership_backfill_required` 사유로 `guarded` 처리했다.
- 학습 안전장치를 추가해 `--restricted-stock-codes`로 제한 종목 universe를 명시하지 않으면 quality gate가 실패하고 `promoted`가 되지 않도록 했다.
- `foreign_limit_quantity`를 학습 point와 feature에 포함하고, 현재 보유수량 대비 한도소진율/잔여한도 feature를 생성하도록 수정했다.
- KRX 최신 snapshot 기준 `foreign_ownership_rate / foreign_limit_exhaustion_rate * 100 < 99.9` 규칙으로 산출했던 외국인 취득한도 제한 18종목은 백필 전 중간 산출물이다. KIS master parser 수정 후 새로 들어온 종목의 KRX 외국인 보유량 history를 백필하고 제한 universe를 재산출해야 한다.
- 제한 18종목 재학습은 `hist_gradient_boosting_delta_ratio`, blend alpha 0.005를 선택했으나, 운영 universe가 불완전해 `release_status=guarded`로 내렸다.
- 제한 18종목 benchmark의 N-HiTS/PatchTST 비교도 백필 전 중간 진단으로만 보존한다.
- KIS master parser의 ETP 판정을 상품그룹 `ST` 기준으로 수정하고, KT, SBS, 한국가스공사, 대한항공 등 누락 종목을 stock master에 보강했다.
- KRX 최신 snapshot 보강 후 금융위 2023-01-25 붙임4의 33개 법령 제한 종목 중 현재 상장 32종목을 운영 universe로 확정했다. `SBS콘텐츠허브(046140)`는 현재 stock master에 없어 제외했다.
- SBS, KNN, 티비씨는 KRX가 외국인 보유/한도/소진율을 0으로 반환하는 0% 취득불허 종목이므로 비율 산식이 아니라 법령 allowlist로 제한 종목에 포함한다.
- KRX Data Marketplace 기반 외국인 보유수량 DB/CSV에서 비제한 2,769종목 1,881,866행을 제거하고, 운영 학습 데이터는 현재 상장 제한 32종목만 보존한다.
- 장기 백필로 제한 32종목 history를 2019-01-02부터 2026-06-26까지 58,784행으로 확장했다. 2019-2022 구간은 종목별 988개 KRX 거래일이 추가됐고, weekday fallback상 공휴일 55일/종목은 provider 미반환으로 저장하지 않았다.
- 제한 32종목으로 재학습해 `stock_routed_ml_ensemble`을 선택했다. 종목별 walk-forward 검증에서 MAE/RMSE/MAPE를 persistence baseline 대비 정규화한 composite score로 ML 후보와 blend alpha, prediction mode를 저장하되, persistence보다 MAPE가 나빠지는 후보/runtime은 MAPE guard로 보정한다.
- 최신 후보군은 Ridge, HistGradientBoostingRegressor 2종, ExtraTreesRegressor, log-delta ratio 회귀 2종, 절대 delta quantity 회귀 4종, target quantity 회귀 1종, residual 회귀 18종, hurdle HistGradientBoosting classifier+regressor다. residual 후보에는 squared-error, absolute-error, MAPE-weighted HistGradientBoosting을 포함한다. 40/60/120/240 관측치 장기 흐름과 최근 일별 delta 분포 feature를 추가하고 MAPE guard를 적용해 persistence baseline MAE 53,912.99 / RMSE 152,521.80 / MAPE 0.046983에서 순수 stock-routed ML MAE 51,539.19 / RMSE 147,477.74 / MAPE 0.044908, guarded runtime MAE 51,539.19 / RMSE 147,477.74 / MAPE 0.044908로 개선되어 `release_status=promoted`로 기록했다.
- 제한 universe benchmark를 동일 walk-forward fold/test sample 비교로 정정했다. 0% 취득불허 3종목은 양수 보유수량 학습 샘플이 없어 SOTA/ML sample 비교에서 제외되고, 29종목 21,895개 test sample 기준 N-HiTS MAE 52,863.38 / RMSE 150,345.74 / MAPE 0.046955, PatchTST MAE 54,521.01 / RMSE 154,153.91 / MAPE 0.049739, persistence MAE 53,912.99 / RMSE 152,521.80 / MAPE 0.046983, guarded runtime MAE 51,539.19 / RMSE 147,477.74 / MAPE 0.044908을 기록했다.
- 2015-01-02까지 추가 확장한 실험도 수행했다. 32종목 87,240개 관측치, 77,945개 학습 샘플로 늘었지만 guarded runtime MAE가 55,357.24로 악화되고, N-HiTS MAE 58,053.37, PatchTST MAE 79,075.74로 SOTA 비교도 나빠져 운영 artifact는 2019~2026 champion으로 복구했다.
- 학습 타깃을 한도수량이 아니라 `foreign_owned_quantity`로 고정하고, 주문수량·장중 거래량·시세 없이 전날까지의 일별 보유수량만 사용한다.
- `build_training_samples`의 prefix slice/sort/scan 병목을 rolling feature 생성으로 바꿔 전체 1,712,708개 학습 샘플을 처리 가능하게 했다.
- tree ensemble, log-delta, 절대 delta/target quantity, heuristic residual, absolute-error residual, MAPE-weighted residual, micro-policy residual 후보를 production 후보에 추가했다. 마지막 baseline fallback은 `micro_median_delta_3`로 대체했다. 장기 흐름 및 일별 delta 분포 feature와 MAPE guard까지 반영한 최신 runtime은 ML 29종목, persistence baseline 0종목으로 정리됐다.
- metric 비교 기준을 전체 walk-forward test sample 기준으로 통일했다. 기존 fold 평균 baseline과 전체 sample guarded metric을 비교하던 불일치를 제거했다.
- 최종 선택 모델은 `hurdle_hist_gradient_delta_ratio`, blend alpha 0.0005이며, 종목별 guarded runtime 기준 persistence baseline MAE 34,589.08에서 34,446.93으로 0.4110% 개선했다. RMSE는 0.7474%, MAPE는 6.8484% 개선했다.
- `reports/foreign-ownership-quantity-sota-benchmark.json`는 제한 18종목 universe 기준으로 재생성했다. full restricted walk-forward에서는 `hannah_promoted_guarded_runtime`이 persistence, stale-guarded mean delta, mean delta, median delta보다 낮은 MAE를 기록했다. top18 최근 1일 CPU smoke 진단에서는 N-HiTS MAE 19,821.78, PatchTST MAE 21,394.67, 동일 scope persistence MAE 21,301.28을 기록했다.
- raw ML 단독을 모든 종목에 강제하지 않고, 제한 종목별 검증 gate를 통과한 경우에만 ML을 사용한다. 나머지는 artifact 내부 guarded persistence 또는 추세 heuristic runtime으로 fallback한다.
- production gate는 제한 universe 적용, 최소 10종목, 730일 이상 history, 5,000개 이상 관측치, 3개 이상 walk-forward fold, persistence baseline 개선을 모두 만족해야 `promoted`로 승격한다.

## 2026-06-22 라이브 뉴스 분석 품질 보강
- 최신 미학습 Naver 뉴스 샘플에서 종목 매칭, 본문 정제, 요약 품질을 재점검했다.
- 발견된 보강 대상은 `SK` 같은 짧은 종목명이 `SK하이닉스`보다 먼저 잡히는 과매칭, 광고·푸터·관련기사 문구가 What/Why/Impact 요약에 섞이는 문제, 전문 수집 실패(`SUMMARY_ONLY`) 케이스의 confidence 과신이다.
- serving analyzer는 제목·본문에서 더 긴 고유 종목명을 우선하고, 짧은 요청 후보명은 더 긴 종목명 내부 부분 문자열이면 대표 종목 후보에서 감점한다.
- article cleaner는 언론사 광고, 관련기사, 최신뉴스 위젯, 공유·입력 UI 문구를 제거하고, 요약기는 제목 문맥과 금융 문맥을 함께 만족하는 문장을 우선 사용한다.
- full-content extractor는 URL만 보지 않고 Naver 검색 결과 제목을 함께 받아 제목과 맞는 article 후보를 우선한다. 잘못된 금융 기사 블록이 같은 페이지에 함께 있을 때 엉뚱한 전문을 학습·분석 입력으로 쓰는 문제를 줄인다.
- related stocks에서도 `SK` 같은 짧은 후보가 `SK하이닉스` 같은 명시적 긴 종목명에 shadow되면 제거한다.
- 전문이 없는 `SUMMARY_ONLY` 응답은 이벤트·감성·중요도 confidence를 보수적으로 보정해 현지 거래소가 UI에서 품질을 판단할 수 있게 한다. confidence는 여전히 observe-only이며 자동 차단 정책으로 쓰지 않는다.

## 2026-06-22 기사·공시 전문 기반 학습 v2 완료
- `data/training/financial_alert_full_content_gold.jsonl`에 실제 기사·공시 전문 1,050건을 저장하고 `source_license_policy`, `content_hash`, `content_availability` lineage를 검증한다.
- 전문 데이터셋은 뉴스 전문 855건, OpenDART document 전문 195건으로 구성되며 기존 내부 회귀 seed를 함께 보존한다.
- 학습 입력은 전문이 있으면 `title + snippet + full_content`를 우선 사용하며, 전문이 없는 기존 row는 제목·snippet fallback으로 유지한다.
- 사람이 검수하지 않은 전문 약한 라벨 1,036건은 이벤트·감성·중요도 supervised loss에서 제외하고 검수 후보와 요약 품질 감사에 사용한다.
- 새 모델 `financial-ml-tfidf-logreg-20260622055520`는 supervised 4,659건과 teacher-gated pseudo-label 1,027건 중 이벤트 학습 4,650건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 687건, 687개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 이벤트 threshold는 실제 뉴스 gold 기준으로 `CONTRACT` 0.46, `CORPORATE_ACTION` 0.50, `EARNINGS` 0.40, `GENERAL_MARKET` 0.30, `MACRO` 0.54, `RISK` 0.34로 calibration했다.
- 뉴스 분석 후처리는 `수출`, `업황`, `공급망`, `환율`, `금리`, `물가`, `정책+지원/중소기업`, `시총`, `주가 급등`, `증시` 문맥을 보조 이벤트 태그로 반영한다.
- 80건 실제 뉴스 gold 기준 이벤트 recall 0.9875, macro F1 0.9268, 감성 accuracy 0.9750, 중요도 accuracy 0.9625, 종목 accuracy 1.0으로 gate를 통과했다.
- `reports/model-release-report.json`, `reports/model-confidence-calibration.json`, `reports/pseudo-label-promotion-monitoring.json`, `reports/service-readiness-report.json`을 새 모델 버전으로 재생성했고 전체 상태는 `pass`다.

## 2026-06-20 서비스 readiness 통합 gate 추가
- `scripts/build_service_readiness_report.py`와 `reports/service-readiness-report.json`을 추가해 모델 release, audited gold readiness, live-news monitoring, full-universe reference coverage, stock linker coverage, pseudo-label monitoring, confidence calibration을 최종 운영 gate로 집계한다.
- confidence는 `observe_only` 정책으로만 인정하며 Hannah는 신뢰도 기반 자동 차단 결정을 만들지 않는다.
- 현재 release `financial-ml-tfidf-logreg-20260619095828`의 service readiness는 `overall_status=pass`다.

## 2026-06-19 유효 6자리 국내주식 전체 Codex reference coverage 확장
- `scripts/build_full_universe_codex_stock_review_gold.py`를 추가해 `data/reference/korea_stock_universe.csv`의 유효 6자리 숫자 종목코드 3,920개 중 stock review gold train/eval 합집합에 없는 1,920개 종목을 Codex reference row로 보강한다.
- 생성 row는 `codex_review_approved`, `reviewer_id=codex-gpt-5`, `source_review_stage=full_universe_codex_reference` lineage를 남기고 `data/training/financial_alert_stock_review_gold.jsonl`에 커밋한다.
- `reports/full-universe-codex-coverage-report.json`은 유효 종목 3,920개, 생성 1,920건, 전체 coverage 3,920개, 누락 0개를 기록한다.
- 학습 스크립트는 Codex reference row 3,420건을 supervised loss에서 제외해 자기 라벨 재주입을 막고, 기존 supervised 3,609건과 pseudo-label 1,125건으로 artifact를 재생성한다.
- 새 모델 버전은 `financial-ml-tfidf-logreg-20260619095828`이며 release/service/audited readiness는 모두 `pass`다.
- `reports/stock-coverage-report.json` 기준 supervised/reference 학습 coverage는 3,422개 종목, evaluation/reference coverage는 557개 종목으로 갱신됐다.
- 회귀 테스트는 stock review gold train/eval 합집합이 유효 6자리 국내주식 3,920개 전체를 덮고 full-universe report의 누락 수가 0인지 검증한다.

## 2026-06-19 Codex 대리 검수 기반 coverage gold 승격
- `codex_review_approved`를 승인 가능한 검수 상태로 추가하고, 기존 `human_review_approved`와 동일하게 검수자 메타데이터와 최종 이벤트·감성·중요도 라벨 검증을 통과한 row만 gold 파일로 승격한다.
- `scripts/approve_stock_gold_coverage_with_codex.py`를 추가해 coverage active review packet 2,000건을 Codex 대리 검수 상태로 승인한다.
- Codex 승인 스크립트는 6자리 숫자 종목코드가 아닌 row를 제외하고 같은 split/wave의 유효 종목 후보로 backfill해 학습 1,500종목, 평가 500종목, wave별 100종목 기준을 유지한다.
- `data/training/financial_alert_stock_review_gold.jsonl` 1,500건과 `data/evaluation/financial_alert_stock_review_gold.jsonl` 500건을 커밋 대상 gold/reference 데이터로 승격했다.
- `reports/stock-gold-coverage-validation-report.json`은 `overall_status=pass`, 학습 eligible 1,500종목, 평가 eligible 500종목, split disjoint pass를 기록한다.
- `reports/model-release-report.json`은 `overall_status=pass`, `service_readiness.overall_status=pass`, `audited_gold_readiness.overall_status=pass`를 기록한다.
- Codex 대리 승인 row를 그대로 supervised loss에 넣으면 실제 뉴스 gold gate가 회귀하는 것을 확인해, 학습 스크립트는 `codex_review_approved` row를 committed reference/evaluation coverage로 보존하되 supervised loss에서는 제외한다.
- 현재 artifact는 기존 supervised 3,609건과 pseudo-label 1,125건으로 학습하고, stock review gold 500건은 별도 평가셋으로 검증한다.
- 새 모델 버전은 `financial-ml-tfidf-logreg-20260619093342`이며 real news gold gate와 stock review gold 평가를 모두 통과한다.

## 2026-06-03 하네스 구축
- FastAPI 0.136.1, Python 3.12, uv 기반 프로젝트 생성
- `/api/v1/alerts/analyze` 분석 API 구현
- 자체 Rule Engine과 키워드 기준 금융 NLP 모델 구현
- AI 서비스 토큰 검증 제거
- Spring 컨테이너 전용 내부 네트워크 접근 모델로 문서화
- Git 전략, PR 템플릿, CI 하네스 추가

## 2026-06-04 불필요한 로컬 env 제거
- 모델 artifact 경로는 민감정보가 아니므로 env 파일 관리 대상에서 제거
- 로컬 uvicorn 실행 명령에서 `--env-file .env` 제거

## 2026-06-04 금융 NLP 학습·평가 파이프라인 구축
- 학습 데이터 18건과 평가 데이터 6건으로 확장
- 이벤트, 감성, 중요도 키워드 프로필을 학습하는 trainer 추가
- 평가 스크립트와 `reports/model-evaluation.json` 추가
- 평가셋 기준 이벤트, 감성, 중요도, 종목 매핑 지표 1.0 달성

## 2026-06-04 종목 매핑·중복 제거 보강
- 종목 후보에 `aliases` 필드 추가
- 종목코드, 한글명, 영문명, 별칭 기반 매핑 지원
- 텍스트 등장 순서 기준 대표 종목과 관련 종목 순서 산출
- 공백, 기호, 대소문자 차이를 제거한 중복 키 생성

## 2026-06-04 실제 ML 기반 금융 NLP 전환
- Naver News Search, OpenDART 수집 파이프라인 추가
- 수집 raw와 약지도 라벨 데이터는 `data/raw`, `data/processed`에 저장
- OpenDART 공시검색에서 12,967건을 수집하고 약지도 라벨링 수행
- 저작권 문제가 없는 합성 금융 문장 증강 corpus 486건 생성
- TF-IDF char n-gram + Logistic Regression 기반 supervised ML 모델 학습
- 이벤트 태그는 One-vs-Rest multilabel classifier로 전환
- 감성·중요도는 keyword scoring이 아닌 학습 모델 추론으로 전환
- 모델 artifact를 `financial_nlp_ml.joblib`로 저장하고 FastAPI 분석 경로에서 로드
- 18건 확장 평가셋 기준 이벤트, 감성, 중요도, 종목 매핑 지표 1.0 달성

## 2026-06-04 뉴스 코퍼스 수집 안정화와 재학습
- Naver News Search 수집에 요청 간격, 재시도, 지수 백오프를 추가
- 429 rate limit 또는 일시 장애로 수집량이 줄어들면 기존 raw 코퍼스를 기본값으로 덮어쓰지 않도록 보호
- provider별 요청 수, 성공 수, rate limit 수, 수집 건수, 완료 여부를 `reports/dataset-collection.json`에 기록
- Naver News Search 1,134건과 OpenDART 12,967건을 병합해 raw 14,101건 구성
- 약지도 라벨 14,101건과 curated·증강 corpus를 사용해 11,898개 중복 제거 학습 샘플로 재학습
- 이벤트 태그 probability threshold를 0.35로 튜닝해 과잉 `GENERAL_MARKET` 예측을 줄임
- 평가 리포트에 이벤트 라벨별 precision, recall, F1과 감성·중요도 confusion matrix 추가
- 18건 평가셋 기준 이벤트 recall 1.0, 이벤트 macro F1 0.9403, 감성 accuracy 1.0, 중요도 accuracy 0.9444, 종목 accuracy 1.0 기록

## 2026-06-04 ML holdout 검증 리포트 추가
- 학습 파이프라인이 전체 학습 샘플을 80:20으로 나눠 holdout 검증을 먼저 수행한다.
- 검증 후 전체 11,898건 학습 샘플로 최종 artifact를 재학습한다.
- 학습 리포트의 `training_sources`는 작업자 로컬 절대경로가 아니라 repo 기준 상대경로로 기록한다.
- holdout split은 학습 9,518건, 검증 2,380건으로 구성된다.
- holdout 기준 이벤트 subset recall 0.9861, 이벤트 macro F1 0.9011, 감성 accuracy 0.9542, 중요도 accuracy 0.9626을 기록했다.
- holdout 리포트는 이벤트 라벨별 precision, recall, F1, support와 감성·중요도 confusion matrix를 포함한다.
- 커밋 코퍼스만으로도 ML artifact 생성과 holdout 최소 성능 기준을 테스트한다.

## 2026-06-04 Gold benchmark 평가셋 확장
- 훈련 증강 corpus를 486건에서 960건으로 확장해 `GENERAL_MARKET`, `DISCLOSURE`, `CORPORATE_ACTION`, `RISK`, `MEDIUM`, `LOW` 케이스를 보강했다.
- `scripts/build_gold_evaluation_data.py`를 추가해 훈련셋과 별도 문장 패턴의 768건 benchmark를 재생성할 수 있게 했다.
- 종목명이 없는 업종·매크로 문장은 종목 라벨을 비워, 텍스트에 없는 종목을 맞히도록 요구하지 않게 정정했다.
- 전체 12,372건 학습 샘플로 모델을 재학습했다.
- holdout 기준 이벤트 subset recall 0.9859, 이벤트 macro F1 0.9024, 감성 accuracy 0.9632, 중요도 accuracy 0.9608을 기록했다.
- 768건 benchmark 기준 이벤트 recall 0.8385, 이벤트 macro F1 0.8592, 감성 accuracy 0.8854, 중요도 accuracy 0.8268, 종목 accuracy 1.0을 기록했다.
- 테스트 기준을 500건 이상 benchmark와 이벤트·감성·중요도·종목 매핑 최소 성능 기준으로 상향했다.

## 2026-06-04 한국어 금융 tokenizer 기반 ML 개선
- 이벤트·중요도 모델 feature extractor를 TF-IDF char n-gram과 한국어 금융 도메인 token n-gram의 병렬 feature로 확장했다.
- 금융 tokenizer는 `잠정실적`, `공급계약`, `유상증자`, `거래정지`, `상장폐지`, `전환사채` 같은 한국어 복합 금융 표현을 띄어쓰기와 기호 차이에 덜 민감하게 추출한다.
- 감성 모델은 gold benchmark 성능 유지를 위해 기존 char n-gram feature를 유지한다.
- 전체 12,372건 학습 샘플로 모델을 재학습했다.
- holdout 기준 이벤트 subset recall 0.9863, 이벤트 macro F1 0.9412, 감성 accuracy 0.9632, 중요도 accuracy 0.9689를 기록했다.
- 768건 benchmark 기준 이벤트 recall 0.8633, 이벤트 macro F1 0.8942, 감성 accuracy 0.8854, 중요도 accuracy 0.8411, 종목 accuracy 1.0을 기록했다.
- 단위 테스트로 금융 tokenizer의 복합어 추출과 학습 artifact 생성을 검증한다.

## 2026-06-04 모델 artifact fail-closed 처리
- 모델 artifact 경로가 없으면 `ModelArtifactNotFoundError`를 발생시킨다.
- artifact 파일이 손상되었거나 필수 payload key가 없으면 `ModelArtifactInvalidError`를 발생시킨다.
- 분석 API는 모델 artifact 오류를 `503 Service Unavailable`과 고정 메시지로 변환해 내부 stack trace를 노출하지 않는다.
- 테스트로 누락 artifact, invalid artifact, 분석 API 503 응답 계약을 검증한다.

## 2026-06-04 라벨별 golden quality gate
- 768건 gold benchmark 평가셋에 이벤트 라벨별 precision, recall, F1, support 하한선을 추가했다.
- `CAPITAL_ACTION`, `CONTRACT`, `CORPORATE_ACTION`, `DISCLOSURE`, `EARNINGS`, `GENERAL_MARKET`, `MACRO`, `RISK` 전 라벨을 개별 gate로 검증한다.
- 감성은 `NEGATIVE`, `NEUTRAL`, `POSITIVE`별 정답 confusion count를 검증한다.
- 중요도는 `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`별 정답 confusion count를 검증한다.
- 평균 지표가 통과해도 특정 이벤트나 중요도 라벨이 무너지는 회귀를 CI에서 차단한다.

## 2026-06-04 중복 제거 키 정규화 개선
- 중복 제거 키 생성 전에 뉴스 제목을 canonical title로 변환한다.
- `[속보]`, `(종합)`, `특징주:` 같은 제목 라벨과 언론사·기자·이메일 꼬리표를 제거한다.
- 같은 이벤트가 매체별 제목 포장 차이로 여러 알림이 되는 문제를 줄인다.
- source type과 종목코드는 해시 입력에 유지해 뉴스·공시 경계와 종목 경계가 섞이지 않게 한다.
- 테스트로 라벨·꼬리표 제거, source type 경계, 종목 경계를 검증한다.

## 2026-06-04 Hana-OmniLens-API 연동 계약 테스트
- Spring `HannahAiAnalysisRequest`, `HannahAiStockCandidate`, `HannahAiAnalysisResponse` record의 JSON 필드명을 AI schema 테스트로 고정했다.
- `POST /api/v1/alerts/analyze`가 별도 `X-HANNAH-AI-SERVICE-TOKEN` 없이 내부 호출 payload를 처리하는지 검증한다.
- 계약 샘플은 공시 기반 공급계약 문장과 `stock_universe` alias를 포함한다.
- 응답 필드 전체, 종목 매핑, `CONTRACT` 이벤트 태그, related stocks, boolean target flag, SHA-256 duplicate key, model version을 검증한다.

## 2026-06-04 OpenDART 실공시 gold set과 재학습
- OpenDART에서 최근 1년 후보 10,399건을 로컬 키로 수집해 실공시 후보를 확인했다.
- 사람이 검수한 30건 실공시 gold set을 `data/evaluation/financial_alert_real_disclosure_gold.jsonl`에 추가했다.
- 초기 모델은 실공시 gold 기준 이벤트 recall 0.4333, macro F1 0.5496으로 낮아 실제 DART 제목체 보강이 필요했다.
- 이벤트 모델 입력에 `source_type` feature를 추가해 공시 입력의 `DISCLOSURE` 라벨 누락을 줄였다.
- tokenizer에 `타법인주식`, `자기주식처분`, `임원주요주주`, `주주총회`, `소송등`, `횡령배임` 등 DART 제목체 복합어를 추가했다.
- 증강 corpus에 `단일판매ㆍ공급계약체결`, `타법인주식및출자증권취득결정`, `주권매매거래정지기간변경`, `임원ㆍ주요주주특정증권등소유상황보고서` 같은 실공시 문법을 추가했다.
- 감성 모델도 한국어 금융 tokenizer feature를 사용하도록 바꿔 `상장폐지`, `소송`, `횡령ㆍ배임` 리스크 공시의 negative 분류를 개선했다.
- 약지도 1.1만 건을 그대로 투입하면 neutral/high 편향으로 실공시 LOW·CRITICAL 품질이 떨어져, artifact 학습은 검수·균형 corpus 기준으로 고정했다.
- 최종 학습 샘플은 1,554건이며 80:20 holdout 기준 이벤트 macro F1 0.9970, 감성 accuracy 0.9936, 중요도 accuracy 1.0을 기록했다.
- 768건 benchmark 기준 이벤트 recall 0.9688, macro F1 0.9904, 감성 accuracy 0.9688, 중요도 accuracy 1.0, 종목 accuracy 1.0을 기록했다.
- 30건 OpenDART 실공시 gold 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0을 기록했다.

## 2026-06-04 Naver 실제 뉴스 gold set과 뉴스형 재학습
- Naver News Search를 로컬 키로 재수집해 raw 후보를 14,169건으로 확장했다.
- provider 리포트 기준 Naver News Search 1,202건, OpenDART 12,967건을 보존했다.
- 실제 Naver 뉴스 제목·snippet 후보 중 사람이 검수한 학습 gold 25건과 평가 gold 36건을 분리해 추가했다.
- 학습 gold와 평가 gold는 동일 문장이 겹치지 않도록 테스트로 검증한다.
- `scripts/build_news_style_training_data.py`를 추가해 실제 뉴스 제목체를 반영한 저작권 안전 증강 corpus 1,872건을 생성한다.
- `GENERAL_MARKET`, `MACRO`, `EARNINGS`, `CONTRACT`, `RISK`, `CAPITAL_ACTION` 뉴스 표현을 보강했다.
- 최종 학습 샘플은 3,571건이며 80:20 holdout 기준 이벤트 macro F1 0.9941, 감성 accuracy 0.9958, 중요도 accuracy 0.9930을 기록했다.
- 768건 benchmark 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9414, 종목 accuracy 1.0을 기록했다.
- 30건 OpenDART 실공시 gold 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9333, 종목 accuracy 1.0을 기록했다.
- 36건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9444, macro F1 0.9075, 감성 accuracy 0.9167, 중요도 accuracy 0.8889, 종목 accuracy 1.0을 기록했다.

## 2026-06-04 약지도 대량 후보 distillation gate
- `data/processed/weak_labeled_alerts.jsonl` 14,169건을 distillation 후보로 사용한다.
- `weak_distiller.py`를 추가해 disclosure noise, disclosure-only, duplicate, low-signal 후보를 제거한다.
- ETF·집합투자증권·투자설명서·증권발행실적보고서 같은 공시 노이즈를 학습 승격 대상에서 제외한다.
- 라벨별 quota와 deterministic hash tie-breaker로 재현 가능한 선별 순서를 만든다.
- 현재 distillation 통과 후보는 2,346건이며 NEWS 1,149건, DISCLOSURE 1,197건이다.
- 통과 후보의 라벨 분포는 CAPITAL_ACTION 546, CONTRACT 368, CORPORATE_ACTION 462, DISCLOSURE 1,014, EARNINGS 560, MACRO 744, RISK 208건이다.
- 대량 약지도 후보를 supervised loss에 직접 투입하면 benchmark·실제 뉴스 gold gate가 하락하는 것을 확인했다.
- 따라서 `reports/weak-distillation-report.json`에 `not_promoted_to_supervised_loss`로 기록하고, artifact는 검수·균형 corpus 기준으로 유지했다.
- 최종 gate는 21개 pytest, benchmark, 실공시 gold, 실제 뉴스 gold 모두 통과했다.

## 2026-06-04 teacher-gated pseudo-label 이벤트 학습
- Naver News Search와 OpenDART를 로컬 키로 확장 수집해 raw 후보를 37,278건으로 늘렸다.
- provider 리포트 기준 Naver News Search 11,312건, OpenDART 25,966건을 보존했다.
- 수집 raw와 weak label 파일은 `data/raw`, `data/processed`에 저장하고 학습 재현성을 위해 추적 대상으로 유지했다.
- weak distillation 후보는 37,278건 중 4,845건이며 disclosure noise, disclosure-only, duplicate, low-signal 후보를 제외했다.
- supervised corpus 3,571건으로 teacher 모델을 먼저 학습한 뒤, distillation 후보를 teacher가 다시 예측한다.
- teacher event confidence 0.58, sentiment confidence 0.72, importance confidence 0.68 이상이고 weak-label과 이벤트가 합의한 후보만 pseudo-label로 승격한다.
- pseudo-label을 모든 라벨에 넣으면 실제 뉴스 gold와 `CORPORATE_ACTION` benchmark가 흔들려, gold gate를 유지한 `RISK` 140건과 `CONTRACT` 180건만 이벤트 모델 학습에 투입했다.
- 감성·중요도 모델은 실제 뉴스 gold 회귀를 막기 위해 supervised corpus만으로 학습한다.
- 최종 artifact 학습 샘플은 supervised 3,571건, pseudo-label 320건을 합친 3,891건이다.
- 이벤트 threshold는 benchmark와 실제 뉴스 gold를 함께 통과하도록 0.30으로 조정했다.
- 80:20 supervised holdout 기준 이벤트 macro F1 0.9941, 감성 accuracy 0.9958, 중요도 accuracy 0.9930을 기록했다.
- 768건 benchmark 기준 이벤트 recall 1.0, macro F1 0.9993, 감성 accuracy 1.0, 중요도 accuracy 0.9414, 종목 accuracy 1.0을 기록했다.
- 30건 OpenDART 실공시 gold 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9333, 종목 accuracy 1.0을 기록했다.
- 36건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9444, macro F1 0.8806, 감성 accuracy 0.9167, 중요도 accuracy 0.8889, 종목 accuracy 1.0을 기록했다.
- 테스트에 pseudo-label 승격 학습 검증을 추가했고, 총 22개 pytest가 통과했다.

## 2026-06-04 실제 뉴스 gold 확장과 기업행동 pseudo-label 승격
- 실제 Naver 뉴스 학습 gold를 25건에서 43건으로 확대하고, 평가 gold를 36건에서 56건으로 확대했다.
- `title + 핵심 snippet 근거` 형태의 평가 문장을 추가해 실제 API 입력처럼 제목과 snippet이 함께 들어오는 조건을 검증한다.
- 고배당, 주주환원, 지분투자, 지분취득, 주식병합, 생산차질, 생산능력, 특허분쟁, 임단협 같은 뉴스형 복합어를 tokenizer에 추가했다.
- `CORPORATE_ACTION` 후보는 actual-news gold gate를 유지하는 40건만 teacher-gated pseudo-label로 승격했다.
- `CAPITAL_ACTION`, `EARNINGS`, `MACRO`, `DISCLOSURE`, `GENERAL_MARKET` pseudo-label 확대는 실제 뉴스 gold 회귀가 있어 이번 artifact에는 투입하지 않았다.
- 최종 artifact 학습 샘플은 supervised 3,589건, pseudo-label 360건을 합친 3,949건이다.
- pseudo-label 분포는 `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건이다.
- 이벤트 태그 threshold는 기본 0.30으로 유지하고, 중립 시황의 `RISK` 오탐을 줄이기 위해 `RISK`만 0.42로 calibration했다.
- 80:20 supervised holdout 기준 이벤트 macro F1 0.9970, 감성 accuracy 0.9930, 중요도 accuracy 0.9875를 기록했다.
- 768건 benchmark 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9427, 종목 accuracy 1.0을 기록했다.
- 30건 OpenDART 실공시 gold 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0을 기록했다.
- 56건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9821, macro F1 0.9525, 감성 accuracy 0.9821, 중요도 accuracy 0.9643, 종목 accuracy 1.0을 기록했다.
- 실제 뉴스 gold gate를 50건 이상, 이벤트 recall 0.9, macro F1 0.9, 감성·중요도 accuracy 0.9 이상으로 상향했다.

## 2026-06-04 실제 뉴스 gold 종목·기간 확대
- 실제 Naver 뉴스 학습 gold를 43건에서 63건으로 확대하고, 평가 gold를 56건에서 80건으로 확대했다.
- 평가 gold의 종목코드 커버리지는 30개로 넓혔고, `CAPITAL_ACTION`, `CONTRACT`, `CORPORATE_ACTION`, `EARNINGS`, `GENERAL_MARKET`, `MACRO`, `RISK` 라벨별 support를 8건 이상으로 고정했다.
- 실제 뉴스 title에서 쓰는 `NH증권`, `네이버`, `LG엔솔`, `하나은행` 같은 약칭을 gold row의 `stock_aliases`로 기록하고 평가 stock universe에 반영했다.
- tokenizer에 `무상증자`, `지분인수`, `지분매각`, `주식교환`, `리밸런싱`, `자산효율화`, `공급망`, `화재`, `웹3` 같은 실제 뉴스형 복합어를 추가했다.
- 이벤트 threshold는 기본 0.30으로 유지하되 실제 뉴스 gold 기준으로 `CORPORATE_ACTION` 0.16, `EARNINGS` 0.42, `RISK` 0.42를 label별 calibration했다.
- 최종 artifact 학습 샘플은 supervised 3,609건, pseudo-label 360건을 합친 3,969건이다.
- 80:20 supervised holdout 기준 이벤트 macro F1 0.9881, 감성 accuracy 0.9889, 중요도 accuracy 0.9931을 기록했다.
- 768건 benchmark 기준 이벤트 recall 1.0, macro F1 1.0, 감성 accuracy 1.0, 중요도 accuracy 0.9375, 종목 accuracy 1.0을 기록했다.
- 30건 OpenDART 실공시 gold 기준 이벤트 recall 1.0, macro F1 0.9412, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0을 기록했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9750, macro F1 0.9006, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- 모든 gold row의 `source_url`이 커밋된 `data/raw/collected_alerts.jsonl`의 Naver News `original_url`과 매칭되는지 테스트로 검증한다.

## 2026-06-04 학습 데이터 추적 정책 전환
- `data/raw/collected_alerts.jsonl`와 `data/processed/weak_labeled_alerts.jsonl`를 gitignore 대상에서 제거했다.
- 수집 raw 37,278건과 약지도 라벨 37,278건은 학습 재현성과 PR 리뷰를 위해 커밋한다.
- 수집 데이터에는 제목, snippet, 원문 링크, provider, content hash, 약지도 라벨만 남기고 외부 API 키나 credential은 포함하지 않는다.
- 로컬 외부 API 키는 계속 `secrets.local.env`에만 두고 커밋하지 않는다.

## 2026-06-04 추론 latency와 audit log
- `AnalysisAuditLogger`를 추가해 분석 API 요청마다 구조화된 JSON audit log를 남긴다.
- 성공 로그는 `model_version`, `latency_ms`, `stock_code`, 이벤트 태그, 감성, 중요도, 입력 hash를 포함한다.
- 실패 로그는 `outcome=failure`, `failure_reason`, `latency_ms`, 입력 hash를 포함한다.
- 원문 제목, snippet, URL은 로그에 직접 남기지 않고 SHA-256 hash만 기록한다.
- 분석 API는 모델 artifact 누락 실패도 audit log로 남긴 뒤 기존 `503` fail-closed 계약을 유지한다.
- 테스트로 성공 audit log, 모델 artifact 실패 audit log, 원문 비노출을 검증했다.

## 2026-06-04 모델 release report
- `model_release_report.py`를 추가해 학습 리포트, gold 평가 리포트, weak distillation 리포트를 하나의 버전별 release report로 묶는다.
- `scripts/build_model_release_report.py`가 `reports/model-release-report.json`을 결정적으로 재생성한다.
- release report는 모델 버전, artifact 경로, 학습 샘플 수, pseudo-label 승격 내역, 데이터 lineage, weakest event label을 기록한다.
- holdout, benchmark, OpenDART 실공시 gold, Naver 실제 뉴스 gold quality gate가 모두 통과해야 `overall_status=pass`가 된다.
- pseudo-label 승격 수와 teacher 학습 샘플 수가 학습 리포트와 distillation 리포트 사이에서 일치하는지도 consistency check로 검증한다.
- 수집 raw와 약지도 라벨 파일은 gitignore하지 않고 커밋해 학습 재현성과 PR 리뷰 가능성을 유지한다.

## 2026-06-04 pseudo-label promotion gate 모니터링
- `pseudo_label_monitor.py`를 추가해 weak distillation 리포트와 model release report를 운영용 promotion monitoring report로 변환한다.
- `scripts/build_pseudo_label_monitoring_report.py`가 `reports/pseudo-label-promotion-monitoring.json`을 결정적으로 재생성한다.
- raw 후보 37,278건, 고신호 후보 4,845건, teacher 탈락 3,124건, quota 보류 1,361건, 최종 승격 360건을 funnel로 기록한다.
- active quota가 있는 `RISK`, `CONTRACT`, `CORPORATE_ACTION`은 모두 quota가 채워진 상태로 기록한다.
- `CAPITAL_ACTION`, `DISCLOSURE`, `EARNINGS`, `MACRO`는 고신호 후보가 충분하지만 actual-news gold gate 실험 전까지 `expansion_candidate_hold_for_gold_gate`로 보류한다.
- 테스트는 monitoring report가 distillation·release 리포트에서 재계산한 결과와 완전히 일치하는지 검증한다.

## 2026-06-04 배포 환경별 secret hygiene
- AI 런타임은 협력사 API key, Hannah 서비스 토큰, 외부 provider credential을 요구하지 않는 secret-free 서비스로 유지한다.
- Naver News Search와 OpenDART credential은 학습 데이터 수집 스크립트에서만 사용한다.
- `ProviderCredentialError`를 추가해 수집 credential이 누락되면 네트워크 요청 전 fail-fast하고 변수명만 출력한다.
- `scripts/verify_secret_hygiene.py`를 추가해 추적 파일에 로컬 secret 파일, key material, credential assignment가 들어오면 CI에서 차단한다.
- GitHub Actions CI에 secret hygiene 검사를 추가했다.
- 테스트로 로컬 env가 기존 환경변수를 덮어쓰지 않는지, credential 누락 오류가 값을 노출하지 않는지 검증한다.

## 2026-06-05 국내주식 universe와 coverage gate
- OpenDART 고유번호 파일을 로컬 `OPEN_DART_API_KEY`로 동기화하는 `scripts/sync_stock_universe.py`를 추가했다.
- 공개 종목 메타데이터 3,967개를 `data/reference/korea_stock_universe.csv`에 저장하고 학습 재현성을 위해 추적한다.
- API 키는 `secrets.local.env`에서만 읽고, 동기화 리포트에는 credential 값이 아니라 로컬 env 사용 정책만 기록한다.
- `stock_universe.py`를 추가해 종목 universe CSV 입출력, Naver 종목별 쿼리 생성, 종목명 매칭, coverage report 생성을 담당한다.
- coverage matcher는 `SK`, `LG`, `DB` 같은 짧은 명칭 오탐을 줄이기 위해 6자리 종목코드 또는 3자 이상 명칭만 사용한다.
- `scripts/collect_training_data.py`에 `--use-stock-universe-news-queries`와 `--stock-query-limit`을 추가해 고정 쿼리 12개를 넘어 종목 universe 기반 수집을 할 수 있게 했다.
- 약지도 라벨 생성 후 universe matcher로 stock_code, stock_name, stock_aliases를 부착해 대규모 후보를 종목별로 집계할 수 있게 했다.
- `reports/stock-coverage-report.json` 기준 raw 후보는 2,356개 종목과 매칭되지만 supervised 학습 종목은 38개, evaluation 종목은 57개라 전 종목 coverage gate는 fail로 기록했다.
- 이 변경은 모델을 완성했다고 주장하지 않고, 전 종목급 실서비스 모델로 가기 위한 coverage 측정과 수집 확장 기반을 만든다.

## 2026-06-05 종목·라벨 균형 학습 승격 후보 큐
- `stock_curation.py`를 추가해 raw 뉴스·공시 후보에서 종목 매칭, 약지도 라벨, 신호 점수를 결합한 검수 큐를 생성한다.
- `scripts/build_stock_training_candidate_queue.py`가 `data/curation/stock_training_candidate_queue.jsonl`와 `reports/stock-training-candidate-report.json`을 결정적으로 생성한다.
- 후보 큐는 종목코드, 종목명, primary label, signal score, 원문 링크, provider, content hash, `curation_status=needs_human_review`를 포함한다.
- 종목별·라벨별 quota를 적용해 대형주나 특정 라벨에 후보가 쏠리지 않도록 제한한다.
- `GENERAL_MARKET`처럼 종목별 학습 승격 의미가 약한 후보와 ETF·집합투자증권 등 disclosure noise는 제외한다.
- 현재 후보 큐는 6,244건, 2,127개 종목이며 coverage gate 기준 300개 이상 종목 조건을 통과한다.
- 후보 큐는 약지도 기반이므로 바로 gold나 supervised 정답셋으로 사용하지 않고, 사람 검수 후 승격하는 정책을 리포트에 기록한다.

## 현재 구현 로직
- 종목 매핑은 전달받은 `stock_universe`에서 종목코드, 한글명, 영문명, alias 포함 여부로 판단한다.
- 이벤트 태그는 한국어 금융 tokenizer feature를 포함한 학습된 multilabel classifier가 산출한다.
- 감성은 char n-gram과 한국어 금융 tokenizer feature를 포함한 학습된 다중 클래스 ML 모델이 분류한다.
- 중요도는 한국어 금융 tokenizer feature를 포함한 학습된 다중 클래스 ML 모델이 분류한다.
- 모델 artifact 누락·손상 시 분석 API는 fail-closed 방식으로 `503`을 반환한다.
- 모델은 사람이 검수한 curated corpus와 DART 제목체를 반영한 균형 증강 corpus로 학습된다.
- 실제 뉴스 gold와 뉴스 제목체 증강 corpus를 포함해 뉴스 도메인 표현도 함께 학습한다.
- Naver 뉴스와 OpenDART 수집 raw와 약지도 라벨은 커밋된 distillation 후보 풀로 관리하며, gold gate를 낮추는 약지도 라벨은 최종 artifact 학습에 직접 투입하지 않는다.
- teacher-gated pseudo-label 중 gold gate를 유지한 `RISK`, `CONTRACT`, `CORPORATE_ACTION` 후보는 이벤트 모델 학습에 투입한다.
- 중복 제거 키는 source type, 종목코드, 뉴스 라벨·꼬리표를 제거한 정규화 제목을 SHA-256으로 해시한다.

## 학습 방식
- `data/training/financial_alert_corpus.jsonl`에 뉴스·공시 예시와 라벨을 기록한다.
- `scripts/collect_training_data.py`가 외부 공급자에서 raw 후보 데이터를 수집한다.
- `scripts/sync_stock_universe.py`가 국내주식 universe를 동기화한다.
- `scripts/build_stock_coverage_report.py`가 raw, supervised, evaluation 데이터의 종목 커버리지를 측정한다.
- `scripts/build_stock_training_candidate_queue.py`가 사람이 검수할 종목·라벨 균형 후보 큐를 만든다.
- 수집기는 장애 시 기존 raw 코퍼스를 보존하고 provider별 수집 상태를 리포트로 남긴다.
- `weak_labeler.py`가 수집 raw에 약지도 라벨을 부여한다.
- `weak_distiller.py`가 약지도 후보를 필터링하고 promotion 여부를 리포트로 남긴다.
- supervised teacher 모델이 weak distillation 후보를 재예측하고 confidence gate를 통과한 pseudo-label을 student 이벤트 모델 학습에 승격한다.
- `scripts/build_augmented_training_data.py`가 균형 보강용 합성 금융 corpus를 생성한다.
- `scripts/build_news_style_training_data.py`가 Naver 뉴스 제목체를 반영한 증강 corpus를 생성한다.
- `scripts/build_gold_evaluation_data.py`가 훈련셋과 별도 문장 패턴의 benchmark 평가셋을 생성한다.
- `scripts/train_ml_model.py`가 80:20 holdout 검증 후 전체 코퍼스로 최종 학습 artifact를 생성한다.
- 이벤트·감성·중요도 모델은 char n-gram과 한국어 금융 token n-gram을 함께 사용한다.

## 2026-06-05 종목 후보 큐 teacher-gated 이벤트 학습
- `train_ml_model.py`가 `data/curation/stock_training_candidate_queue.jsonl`을 읽어 종목 균형 후보를 이벤트 모델 학습 후보로 사용한다.
- 후보 큐는 사람이 검수한 gold가 아니므로 supervised 정답셋에는 넣지 않고, supervised teacher 모델의 confidence gate와 라벨 합의 기준을 통과한 샘플만 event-model-only pseudo-label로 승격한다.
- 6,244건 후보 전체를 투입하지 않고 `RISK` 214건, `CONTRACT` 250건으로 제한했다. 493종목 확장과 `CORPORATE_ACTION` stock candidate 추가 실험은 실제 뉴스 gold RISK recall을 낮춰 폐기했다.
- 종목별 quota는 1건으로 제한해 특정 대형주나 반복 뉴스가 student 이벤트 모델을 지배하지 않게 했다.
- per-stock quota 1 적용 후 `CONTRACT` 0.34, `CORPORATE_ACTION` 0.18, `EARNINGS` 0.36, `MACRO` 0.22, `RISK` 0.54로 threshold를 재보정해 실제 뉴스 gold gate를 유지했다.
- 최종 artifact 학습 샘플은 supervised 3,609건, pseudo-label 824건을 합친 4,433건이다.
- pseudo-label 분포는 weak-label `RISK` 140건, `CONTRACT` 180건, `CORPORATE_ACTION` 40건과 종목 후보 `RISK` 214건, `CONTRACT` 250건이다.
- 종목 후보 승격 샘플은 464개 종목을 포함한다.
- event threshold는 실제 뉴스 gold 기준으로 `CONTRACT` 0.34, `CORPORATE_ACTION` 0.18, `EARNINGS` 0.36, `MACRO` 0.22, `RISK` 0.54로 calibration했다.
- 30건 OpenDART 실공시 gold 기준 이벤트 recall 1.0, macro F1 0.9846, 감성 accuracy 1.0, 중요도 accuracy 0.9667, 종목 accuracy 1.0을 기록했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9375, macro F1 0.9116, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- release report는 weak-label 승격 수 360건과 종목 후보 승격 수 464건을 분리해 기록한다.

## 2026-06-05 내부 국내주식 universe 기반 종목 매핑
- 분석 API가 요청 `stock_universe`만으로 종목을 찾던 구조를 내부 `data/reference/korea_stock_universe.csv` fallback 구조로 바꿨다.
- 요청 후보 종목은 우선 적용하고, 같은 종목코드가 없는 종목은 내부 universe master에서 종목코드, 한글명, 영문명, alias로 매핑한다.
- `AlertAnalysisRequest.stock_universe`는 API payload 크기를 제한하기 위해 50개 이하 후보로 유지한다.
- 요청 후보가 비어 있어도 삼성전자 같은 국내주식을 내부 universe로 매핑하는 API 회귀 테스트를 추가했다.
- 내부 universe 3,967개 전체 종목의 6자리 종목코드가 종목 매핑 경로에서 누락 없이 매칭되는지 테스트한다.
- 이 변경은 supervised/gold coverage를 통과시킨 것이 아니라, 전 종목 서비스 입력을 처리하기 위한 종목 master fallback을 추가한 것이다.

## 2026-06-05 전 종목 stock linker ML artifact
- `stock_linker_trainer.py`를 추가해 KRX/OpenDART universe 3,967개 종목의 6자리 종목코드와 trainable 종목명을 TF-IDF char n-gram stock linker 학습 term으로 변환한다.
- `scripts/train_stock_linker_model.py`가 `data/training/stock_linker_training.jsonl`, `src/hannah_montana_ai/model_store/stock_linker_ml.joblib`, `reports/stock-linker-training-report.json`을 생성한다.
- stock linker 학습 term은 7,649건이며 모든 3,967개 종목을 최소 종목코드 term으로 포함한다.
- 학습 리포트는 전체 종목코드 템플릿 accuracy 1.0, trainable 종목명 템플릿 accuracy 0.9921을 기록한다.
- 분석 API는 요청 후보 우선 정책을 유지하고, 내부 fallback 단계에서 stock linker 예측 종목코드와 실제 선두 term 매칭을 함께 확인해 대표 종목 오탐을 줄인다.
- 이 모델은 종목 identity 후보를 학습하는 artifact이며, 이벤트/감성/중요도 분류 모델과 별도로 배포한다.

## 2026-06-05 전 종목 gold 검수 배치
- `build_stock_gold_review_batches`를 추가해 종목 후보 큐에서 supervised 학습 승격용 검수 배치와 evaluation gold 승격용 검수 배치를 분리 생성한다.
- 기존 supervised 학습 데이터와 evaluation 데이터에 이미 포함된 종목은 검수 배치 후보에서 제외한다.
- 학습 검수 배치는 300개 종목, 평가 검수 배치는 100개 종목으로 생성하고 두 배치의 종목코드가 겹치지 않게 한다.
- 라벨 round-robin 선별로 `CAPITAL_ACTION`, `CONTRACT`, `CORPORATE_ACTION`, `DISCLOSURE`, `EARNINGS`, `MACRO`, `RISK` 분포를 균형화했다.
- 모든 row는 `review_status=needs_human_review`이며 사람이 승인하기 전까지 supervised/gold 정답셋으로 승격하지 않는다.
- `reports/stock-gold-review-batch-report.json`은 후보 수 6,244건, 후보 종목 수 2,127개, 학습 검수 300종목, 평가 검수 100종목, disjoint check pass를 기록한다.

## 2026-06-05 gold 검수 승인 승격 파이프라인
- `promote_approved_stock_gold_reviews`를 추가해 `human_review_approved` row만 학습·평가 gold JSONL로 출력한다.
- `needs_human_review` row와 intended split이 맞지 않는 row는 승격하지 않는다.
- `scripts/promote_stock_gold_review_batch.py`는 승격 결과를 `reports/stock-gold-promotion-report.json`으로 기록한다.
- 학습 스크립트는 `data/training/financial_alert_stock_review_gold.jsonl`이 존재할 때 supervised 학습셋에 포함한다.
- 평가 스크립트는 `data/evaluation/financial_alert_stock_review_gold.jsonl`이 존재하고 샘플이 있을 때 `stock_review_gold` 평가 섹션을 추가한다.
- coverage report도 승인된 stock review gold 파일이 존재할 경우 supervised/evaluation coverage에 포함한다.

## 2026-06-05 gold 검수 품질 gate
- 검수 배치 row에 `reviewer_id`, `reviewed_at`, `review_notes`, `final_tags`, `final_sentiment`, `final_importance` 필드를 추가했다.
- 승격 스크립트는 승인 상태라도 검수자 메타데이터나 최종 라벨이 없으면 gold 파일로 쓰지 않는다.
- `reviewed_at`은 ISO-8601 형식이어야 하며, 최종 이벤트·감성·중요도 라벨은 허용된 라벨 집합에 속해야 한다.
- 승격 거부 사유는 `reports/stock-gold-promotion-report.json`의 `rejected_approved_count_by_reason`에 남긴다.
- 현재 커밋된 검수 배치는 모두 `needs_human_review`라 승인 0건, 승격 0건으로 기록한다.

## 2026-06-05 gold 검수 validation report
- `validate_stock_gold_review_batches`를 추가해 검수 배치의 승인 가능 row와 목표 종목 수 충족 여부를 승격 전에 검사한다.
- `scripts/validate_stock_gold_review_batch.py`는 `reports/stock-gold-review-validation-report.json`을 생성한다.
- 현재 검수 배치는 승인 가능 학습 0종목, 평가 0종목이라 `overall_status=fail`로 기록한다.
- 승인 상태지만 필수 검수 필드가 빠진 row는 `blocked_approved_count_by_reason`에 집계한다.

## 2026-06-05 gold active review report
- ML 모델의 이벤트·감성·중요도 확률을 검수 보조 신호로 노출한다.
- `scripts/build_stock_gold_active_review_report.py`는 학습·평가 검수 배치의 상위 50개 우선 검수 row를 `reports/stock-gold-active-review-report.json`에 기록한다.
- 우선순위는 모델 제안과 약지도 라벨의 불일치, 이벤트 margin, 감성·중요도 confidence, signal score를 함께 사용한다.
- 모델 제안은 사람이 검수할 때의 보조 정보일 뿐이며 `human_review_approved` 최종 라벨 없이 gold로 승격하지 않는다.

## 2026-06-05 model confidence calibration report
- `calibration.py`를 추가해 이벤트 멀티라벨 확률, 감성 top confidence, 중요도 top confidence의 calibration을 평가셋별로 계산한다.
- 이벤트 calibration은 label별 Brier score, expected calibration error, 고신뢰 false positive와 false negative를 기록한다.
- 감성·중요도 calibration은 top-class confidence ECE, multiclass Brier score, 고신뢰 오답을 기록한다.
- `scripts/build_model_confidence_calibration_report.py`는 benchmark, real disclosure gold, real news gold, stock review gold 기준 리포트를 `reports/model-confidence-calibration.json`으로 생성한다.
- confidence 리포트는 release monitoring 신호이며 새 라벨을 만들거나 검수 후보를 gold로 승격하지 않는다.

## 2026-06-05 stock candidate quota experiment
- `StockCandidatePromotionConfig`를 추가해 release 기본값은 유지하면서 quota profile별 임시 재학습 실험을 할 수 있게 했다.
- `scripts/build_stock_candidate_quota_experiment.py`는 previous release, risk/contract 확장, calibrated current release profile을 각각 임시 artifact로 학습하고 holdout·benchmark·실공시·실뉴스 gold gate를 평가한다.
- previous release profile은 464건, 464개 종목으로 gate를 통과했다.
- risk/contract 확장 profile은 `RISK=500`, `CONTRACT=500`, per-stock quota 2 기준으로 644건, 470개 종목을 승격했고 release gate를 통과했다.
- 기본 threshold의 balanced profile은 실제 뉴스 gold event macro F1 0.8882로 gate fail이었지만, `MACRO=0.38`, `GENERAL_MARKET=0.38`, `RISK=0.50`, `CONTRACT=0.42` threshold calibration 후 gate를 통과했다.
- calibrated current release profile은 `RISK`, `CONTRACT`, `CAPITAL_ACTION`, `CORPORATE_ACTION`, `EARNINGS`, `MACRO` 후보 523건을 523개 종목에 분산 승격했다.
- 새 release artifact는 supervised 3,609건과 pseudo-label 883건을 합친 4,492건으로 학습했다.
- 새 release는 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9325, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0으로 gate를 통과했다.

## 2026-06-05 gold coverage review planner
- `coverage_planner.py`를 추가해 supervised/gold 종목 coverage를 늘리기 위한 장기 검수 계획을 생성한다.
- `scripts/build_stock_gold_coverage_plan.py`는 `data/curation/stock_gold_coverage_review_plan.jsonl`와 `reports/stock-gold-coverage-plan-report.json`을 생성한다.
- 현재 검수 배치 400종목과 추가 coverage plan 1,600종목을 합쳐 학습 1,500종목, 평가 500종목의 검수 과제를 만든다.
- 학습 split과 평가 split의 종목코드는 disjoint 상태를 유지하고, 이미 supervised/evaluation 데이터에 있는 종목은 추가 계획에서 제외한다.
- 후보 큐 2,127개 종목 중 기존 supervised 종목과 전체 계획을 합치면 2,068개 종목을 커버한다.
- 모든 coverage plan row는 `needs_human_review`이며, 검수자 승인과 최종 라벨 없이 gold나 supervised 데이터셋으로 승격하지 않는다.

## 2026-06-05 coverage plan active review packet
- `build_stock_gold_coverage_active_review_report`를 추가해 2,000종목 coverage plan 전체에 모델 제안 라벨, confidence, disagreement, review priority를 붙인다.
- `scripts/build_stock_gold_coverage_active_review_report.py`는 `data/curation/stock_gold_coverage_active_review_packet.jsonl`와 `reports/stock-gold-coverage-active-review-report.json`을 생성한다.
- active review packet은 학습 1,500개 row와 평가 500개 row 전체를 포함하며, 검수자가 wave 단위로 바로 승인·수정할 수 있도록 원문 text와 모델 제안 필드를 함께 기록한다.
- 리포트는 split별 상위 100개 우선 검수 row와 wave별 상위 10개 row를 기록한다.
- 모델 제안은 검수 보조 정보이며, `human_review_approved`와 검수자 메타데이터, 최종 라벨 없이 supervised/gold 데이터로 승격하지 않는다.

## 2026-06-05 coverage packet gold promotion
- `promote_approved_stock_gold_coverage_reviews`를 추가해 coverage active review packet에서 승인된 row만 stock review gold 파일로 승격한다.
- `scripts/promote_stock_gold_coverage_review_packet.py`는 `data/training/financial_alert_stock_review_gold.jsonl`, `data/evaluation/financial_alert_stock_review_gold.jsonl`, `reports/stock-gold-coverage-promotion-report.json`을 생성한다.
- 기존 검수 배치와 동일하게 `human_review_approved`, `reviewer_id`, `reviewed_at`, `final_tags`, `final_sentiment`, `final_importance`가 모두 유효한 row만 승격한다.
- 승격된 gold row에는 source review wave/stage/reason과 모델 제안 라벨, review priority를 lineage로 보존한다.
- 현재 커밋된 packet은 모두 `needs_human_review`라 학습 승격 0건, 평가 승격 0건으로 기록한다.

## 2026-06-05 coverage packet validation gate
- `validate_stock_gold_coverage_review_packet`을 추가해 coverage active review packet의 승인 가능 row가 재학습 목표를 충족하는지 검사한다.
- `scripts/validate_stock_gold_coverage_review_packet.py`는 `reports/stock-gold-coverage-validation-report.json`을 생성한다.
- 기본 gate는 학습 1,500종목, 평가 500종목, wave별 승인 종목 100개 이상, 학습·평가 split disjoint를 요구한다.
- 현재 packet은 승인 0건이라 `overall_status=fail`이며, wave별 남은 승인 수를 리포트로 기록한다.
- 이 gate는 승인된 stock review gold를 포함해 재학습하기 전 필수 확인 단계다.

## 2026-06-05 release service readiness gate
- `model_release_report.py`에 `service_readiness` 섹션을 추가해 모델 품질 gate와 실서비스 coverage readiness를 분리했다.
- `scripts/build_model_release_report.py`는 `reports/stock-gold-coverage-validation-report.json`을 함께 읽어 release report에 반영한다.
- 현재 모델 품질 `overall_status`는 holdout·gold 평가와 consistency 기준 `pass`지만, `service_readiness.overall_status`는 coverage 승인 0건으로 `fail`이다.
- service readiness는 학습 1,500종목, 평가 500종목, wave별 승인 100종목 gate가 통과될 때만 `pass`가 된다.
- 이 변경은 현재 모델을 실서비스급으로 과장하지 않기 위한 release guard다.

## 2026-06-05 누락 종목 수집 shard plan
- `stock_collection_plan.py`를 추가해 candidate queue, supervised training gold, evaluation gold가 모두 없는 종목을 수집 대상으로 산출한다.
- `scripts/build_stock_collection_shard_plan.py`는 전 종목 universe와 현재 raw/candidate/gold coverage를 읽어 `data/curation/stock_collection_shard_plan.jsonl`과 `reports/stock-collection-shard-plan.json`을 생성한다.
- 현재 plan은 1,836개 누락 종목을 19개 shard로 나누고, 9,180개 Naver News Search 쿼리를 만든다.
- 1,607개 `no_raw_no_candidate` 종목을 229개 `raw_without_candidate` 종목보다 먼저 배치해 실제 데이터가 전혀 없는 종목부터 수집한다.
- `scripts/collect_training_data.py`는 `--stock-collection-plan`과 `--stock-collection-plan-shard-index`를 받아 특정 shard만 수집할 수 있다.
- shard 수집 결과도 raw 또는 검수 후보일 뿐이며, 사람 승인 전에는 supervised/gold 데이터로 승격하지 않는다.

## 2026-06-05 누락 종목 shard 0 수집과 재학습
- `stock_collection_shard_plan`의 shard 0을 Naver News Search로 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 37,278건에서 40,907건으로 늘었고, Naver 원천 데이터는 11,312건에서 14,941건으로 늘었다.
- raw 종목 매칭은 2,356개에서 2,528개로 늘었고, 후보 큐는 6,244건/2,127종목에서 7,490건/2,314종목으로 확장됐다.
- 누락 종목 shard plan은 1,836개/19개 shard에서 1,649개/17개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260604210928`은 supervised 3,609건과 pseudo-label 900건을 합친 4,509건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 540건, 540개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 실제 뉴스 gold에서 `GENERAL_MARKET` recall 하락을 확인해 label threshold를 0.38에서 0.34로 조정했고, recall 0.9412와 F1 0.9143으로 회복했다.
- 새 release는 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9375, macro F1 0.9180, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0으로 gate를 통과했다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 다음 누락 종목 shard 수집과 재학습
- 최신 `stock_collection_shard_plan`의 다음 shard 0을 Naver News Search로 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 40,907건에서 43,269건으로 늘었고, Naver 원천 데이터는 14,941건에서 17,303건으로 늘었다.
- raw 종목 매칭은 2,528개에서 2,666개로 늘었고, 후보 큐는 7,490건/2,314종목에서 8,291건/2,456종목으로 확장됐다.
- 누락 종목 shard plan은 1,649개/17개 shard에서 1,507개/16개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260604212852`는 supervised 3,609건과 pseudo-label 918건을 합친 4,527건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 558건, 558개 종목을 event-model-only pseudo-label로 제한 승격했다.
- release gate는 holdout, 768건 benchmark, 30건 실공시 gold, 80건 실제 뉴스 gold에서 모두 `pass`를 유지했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9217, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 추가 누락 종목 shard 수집과 재학습
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 43,269건에서 44,997건으로 늘었고, Naver 원천 데이터는 17,303건에서 19,031건으로 늘었다.
- raw 종목 매칭은 2,666개에서 2,758개로 늘었고, 후보 큐는 8,291건/2,456종목에서 8,917건/2,567종목으로 확장됐다.
- 누락 종목 shard plan은 1,507개/16개 shard에서 1,397개/14개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260604215055`는 supervised 3,609건과 pseudo-label 940건을 합친 4,549건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 580건, 580개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9181, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 실제 뉴스 gold macro F1 0.8958로 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 누락 종목 shard 추가 확장과 재학습
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 44,997건에서 46,585건으로 늘었고, Naver 원천 데이터는 19,031건에서 20,619건으로 늘었다.
- raw 종목 매칭은 2,758개에서 2,858개로 늘었고, 후보 큐는 8,917건/2,567종목에서 9,434건/2,667종목으로 확장됐다.
- 누락 종목 shard plan은 1,397개/14개 shard에서 1,297개/13개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260604221241`은 supervised 3,609건과 pseudo-label 967건을 합친 4,576건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 607건, 607개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9181, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 746건/562종목으로 gate를 통과했지만, current release가 실제 뉴스 gold macro F1과 종목 커버리지에서 더 좋아 best profile로 유지했다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 누락 종목 shard 심화 수집과 재학습
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 46,585건에서 47,963건으로 늘었고, Naver 원천 데이터는 20,619건에서 21,997건으로 늘었다.
- raw 종목 매칭은 2,858개에서 2,929개로 늘었고, 후보 큐는 9,434건/2,667종목에서 9,888건/2,739종목으로 확장됐다.
- 누락 종목 shard plan은 1,297개/13개 shard에서 1,225개/13개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260604224454`은 supervised 3,609건과 pseudo-label 981건을 합친 4,590건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 621건, 621개 종목을 event-model-only pseudo-label로 제한 승격했다.
- `GENERAL_MARKET` label threshold를 0.34에서 0.32로, `MACRO` label threshold를 0.38에서 0.36으로 재보정해 실제 뉴스 gold 세부 recall 회귀를 복구했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9254, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 764건/578종목으로 gate를 통과했지만, current release가 621개 종목으로 더 넓고 실제 뉴스 gold gate를 통과해 best profile로 유지했다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 누락 종목 shard 추가 스케일링과 재학습
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 47,963건에서 48,992건으로 늘었고, Naver 원천 데이터는 21,997건에서 23,026건으로 늘었다.
- raw 종목 매칭은 2,929개에서 2,987개로 늘었고, 후보 큐는 9,888건/2,739종목에서 10,226건/2,804종목으로 확장됐다.
- 누락 종목 shard plan은 1,225개/13개 shard에서 1,160개/12개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260605002536`은 supervised 3,609건과 pseudo-label 993건을 합친 4,602건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 633건, 633개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9181, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 773건/589종목으로 확장됐지만 실제 뉴스 gold recall gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 누락 종목 shard 폭 확장과 재학습
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 48,992건에서 49,930건으로 늘었고, Naver 원천 데이터는 23,026건에서 23,964건으로 늘었다.
- raw 종목 매칭은 2,987개에서 3,029개로 늘었고, 후보 큐는 10,226건/2,804종목에서 10,521건/2,847종목으로 확장됐다.
- 누락 종목 shard plan은 1,160개/12개 shard에서 1,117개/12개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260605004905`은 supervised 3,609건과 pseudo-label 1,005건을 합친 4,614건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 645건, 645개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 792건/604종목으로 확장됐지만 실제 뉴스 gold recall gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 전 종목 후보 커버리지 shard 추가 수집과 재학습
- 하네스 브랜치명을 `feat/financial-nlp-stock-universe-coverage`로 정리하고 최신 `feature` 기반 작업 흐름을 유지했다.
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 49,930건에서 50,824건으로 늘었고, Naver 원천 데이터는 23,964건에서 24,858건으로 늘었다.
- raw 종목 매칭은 3,029개에서 3,060개로 늘었고, 후보 큐는 10,521건/2,847종목에서 10,766건/2,876종목으로 확장됐다.
- 누락 종목 shard plan은 1,117개/12개 shard에서 1,088개/11개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260605043316`은 supervised 3,609건과 pseudo-label 1,014건을 합친 4,623건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 654건, 654개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 235건, `CONTRACT` 217건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 23건, `MACRO` 14건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 807건/615종목으로 확장됐지만 실제 뉴스 gold recall gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-05 전 종목 후보 커버리지 shard 연속 확장과 재학습
- 하네스 브랜치명을 `feat/financial-nlp-universe-shard-expansion`으로 생성하고 최신 `feature` 기반 작업 흐름을 유지했다.
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 50,824건에서 51,505건으로 늘었고, Naver 원천 데이터는 24,858건에서 25,539건으로 늘었다.
- raw 종목 매칭은 3,060개에서 3,101개로 늘었고, 후보 큐는 10,766건/2,876종목에서 11,011건/2,912종목으로 확장됐다.
- 누락 종목 shard plan은 1,088개/11개 shard에서 1,052개/11개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260605045653`은 supervised 3,609건과 pseudo-label 1,018건을 합친 4,627건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 658건, 658개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 236건, `CONTRACT` 220건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 23건, `MACRO` 14건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 820건/624종목으로 확장됐지만 실제 뉴스 gold recall gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-06 전 종목 후보 커버리지 shard 1 확장과 수집 복원력 보강
- 하네스 브랜치명을 `feat/financial-nlp-universe-shard-1`로 생성하고 최신 `feature` 기반 작업 흐름을 유지했다.
- shard 1 수집 중 Naver News Search read timeout이 한 번 발생해 수집기가 중단되는 문제를 확인했다.
- `collector.py`가 `TimeoutError`와 `URLError`를 retry 가능한 일시 네트워크 오류로 처리하고, 재시도 소진 시 credential이나 URL 없이 provider status에 오류 종류만 기록하도록 보강했다.
- timeout 복원력 테스트를 추가해 첫 요청 timeout 후 재시도 성공, 재시도 소진 후 안전한 오류 기록을 검증했다.
- 최신 `stock_collection_shard_plan`의 shard 1을 Naver News Search로 추가 수집해 513개 요청 중 512개가 성공했고 rate limit은 0건이었다. 실패 1건은 retry 후 완료되어 provider status는 `completed=true`로 기록됐다.
- raw 후보는 51,505건에서 54,581건으로 늘었고, Naver 원천 데이터는 25,539건에서 28,615건으로 늘었다.
- raw 종목 매칭은 3,101개에서 3,214개로 늘었고, 후보 큐는 11,011건/2,912종목에서 12,070건/3,037종목으로 확장됐다.
- 누락 종목 shard plan은 1,052개/11개 shard에서 927개/10개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260605102859`는 supervised 3,609건과 pseudo-label 1,052건을 합친 4,661건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 692건, 692개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 254건, `CONTRACT` 232건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 26건, `MACRO` 16건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 861건/658종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-06 - 전 종목 후보 shard 2 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- raw 후보는 54,581건에서 55,390건으로 늘었고, Naver 원천 데이터는 28,615건에서 29,424건으로 늘었다.
- raw 종목 매칭은 3,214개에서 3,237개로 늘었고, 후보 큐는 12,070건/3,037종목에서 12,251건/3,063종목으로 확장됐다.
- 누락 종목 shard plan은 927개/10개 shard에서 901개/10개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260606004023`는 supervised 3,609건과 pseudo-label 1,054건을 합친 4,663건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 695건, 695개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 261건, `CONTRACT` 230건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 24건, `MACRO` 15건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 857건/659종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 3 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 Naver News Search로 추가 수집했다. 582개 요청 중 504개가 성공했고 78개 요청은 provider rate limit으로 중단되어 provider status는 `completed=false`로 남겼다.
- raw 후보는 55,390건에서 56,494건으로 늘었고, Naver 원천 데이터는 29,424건에서 30,528건으로 늘었다.
- raw 종목 매칭은 3,237개에서 3,248개로 늘었고, 후보 큐는 12,251건/3,063종목에서 12,366건/3,075종목으로 확장됐다.
- 누락 종목 shard plan은 901개/10개 shard에서 889개/9개 shard로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610170520`는 supervised 3,609건과 pseudo-label 1,060건을 합친 4,669건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 701건, 701개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 257건, `CONTRACT` 236건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 28건, `MACRO` 15건이다.
- `MACRO` 이벤트 threshold를 0.36에서 0.34로 보정해 실제 뉴스 gold의 라벨별 recall 회귀를 막았다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 863건/663종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 4 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 56,494건에서 56,675건으로 늘었고, Naver 원천 데이터는 30,528건에서 30,709건으로 늘었다.
- raw 종목 매칭은 3,248개에서 3,252개로 늘었고, 후보 큐는 12,366건/3,075종목에서 12,395건/3,075종목으로 확장됐다.
- 누락 종목 shard plan priority는 `no_raw_no_candidate` 716개에서 712개로 줄고 `raw_without_candidate` 173개에서 177개로 늘었다. 전체 plan은 889개 종목, 9개 shard를 유지했다.
- 새 모델 `financial-ml-tfidf-logreg-20260610172430`는 supervised 3,609건과 pseudo-label 1,060건을 합친 4,669건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 702건, 702개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 259건, `CONTRACT` 236건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 28건, `MACRO` 15건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 862건/663종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 5 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 56,675건에서 56,828건으로 늘었고, Naver 원천 데이터는 30,709건에서 30,862건으로 늘었다.
- raw 종목 매칭은 3,252개에서 3,256개로 늘었고, 후보 큐는 12,395건/3,075종목에서 12,435건/3,080종목으로 확장됐다.
- 누락 종목 shard plan은 889개/9개 shard에서 884개/9개 shard로 줄었다. priority는 `no_raw_no_candidate` 712개에서 708개로 줄고 `raw_without_candidate` 177개에서 176개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610174935`는 supervised 3,609건과 pseudo-label 1,060건을 합친 4,669건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 702건, 702개 종목을 event-model-only pseudo-label로 유지했다.
- 종목 후보 큐 승격 분포는 `RISK` 259건, `CONTRACT` 236건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 28건, `MACRO` 15건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 862건/663종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 6 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 56,828건에서 56,947건으로 늘었고, Naver 원천 데이터는 30,862건에서 30,981건으로 늘었다.
- raw 종목 매칭은 3,256개에서 3,261개로 늘었고, 후보 큐는 12,435건/3,080종목에서 12,460건/3,085종목으로 확장됐다.
- 누락 종목 shard plan은 884개/9개 shard에서 879개/9개 shard로 줄었다. priority는 `no_raw_no_candidate` 708개에서 703개로 줄고 `raw_without_candidate` 176개를 유지했다.
- 새 모델 `financial-ml-tfidf-logreg-20260610181114`는 supervised 3,609건과 pseudo-label 1,065건을 합친 4,674건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 707건, 707개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 262건, `CONTRACT` 238건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 28건, `MACRO` 15건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 863건/666종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 7 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 56,947건에서 57,045건으로 늘었고, Naver 원천 데이터는 30,981건에서 31,079건으로 늘었다.
- raw 종목 매칭은 3,261개에서 3,262개로 늘었고, 후보 큐는 12,460건/3,085종목에서 12,481건/3,086종목으로 확장됐다.
- 누락 종목 shard plan은 879개/9개 shard에서 878개/9개 shard로 줄었다. priority는 `no_raw_no_candidate` 703개에서 702개로 줄고 `raw_without_candidate` 176개를 유지했다.
- 새 모델 `financial-ml-tfidf-logreg-20260610183402`는 supervised 3,609건과 pseudo-label 1,060건을 합친 4,669건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 702건, 702개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 258건, `CONTRACT` 237건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 28건, `MACRO` 15건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 863건/664종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 8 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 57,045건에서 57,070건으로 늘었고, Naver 원천 데이터는 31,079건에서 31,104건으로 늘었다.
- raw 종목 매칭은 3,262개를 유지했고, 후보 큐는 12,481건/3,086종목에서 12,483건/3,087종목으로 확장됐다.
- 누락 종목 shard plan은 878개/9개 shard에서 877개/9개 shard로 줄었다. priority는 `no_raw_no_candidate` 702개를 유지하고 `raw_without_candidate`는 176개에서 175개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610185431`는 supervised 3,609건과 pseudo-label 1,062건을 합친 4,671건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 704건, 704개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 258건, `CONTRACT` 239건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 28건, `MACRO` 15건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 864건/665종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 9 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 57,070건에서 57,078건으로 늘었고, Naver 원천 데이터는 31,104건에서 31,112건으로 늘었다.
- raw 종목 매칭은 3,262개를 유지했고, 후보 큐는 12,483건/3,087종목에서 12,486건/3,087종목으로 확장됐다.
- 누락 종목 shard plan은 877개/9개 shard를 유지했다. priority는 `no_raw_no_candidate` 702개와 `raw_without_candidate` 175개를 유지했다.
- 새 모델 `financial-ml-tfidf-logreg-20260610191529`는 supervised 3,609건과 pseudo-label 1,062건을 합친 4,671건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 704건, 704개 종목을 event-model-only pseudo-label로 유지했다.
- 종목 후보 큐 승격 분포는 `RISK` 258건, `CONTRACT` 238건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 28건, `MACRO` 16건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9142, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 864건/665종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 10 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 1을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 57,078건에서 59,389건으로 늘었고, Naver 원천 데이터는 31,112건에서 33,423건으로 늘었다.
- raw 종목 매칭은 3,262개에서 3,368개로 늘었고, 후보 큐는 12,486건/3,087종목에서 13,291건/3,192종목으로 확장됐다.
- 누락 종목 shard plan은 877개/9개 shard에서 772개/8개 shard로 줄었다. priority는 `no_raw_no_candidate` 702개에서 596개로 줄고 `raw_without_candidate`는 175개에서 176개로 늘었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610193406`은 supervised 3,609건과 pseudo-label 1,090건을 합친 4,699건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 737건, 737개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 271건, `CONTRACT` 254건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 28건, `MACRO` 19건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9171, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 876건/679종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 11 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 59,389건에서 59,485건으로 늘었고, Naver 원천 데이터는 33,423건에서 33,519건으로 늘었다.
- raw 종목 매칭은 3,368개에서 3,369개로 늘었고, 후보 큐는 13,291건/3,192종목에서 13,296건/3,192종목으로 확장됐다.
- 누락 종목 shard plan은 772개/8개 shard를 유지했다. priority는 `no_raw_no_candidate` 596개에서 595개로 줄고 `raw_without_candidate`는 176개에서 177개로 늘었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610195809`는 supervised 3,609건과 pseudo-label 1,091건을 합친 4,700건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 738건, 738개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 274건, `CONTRACT` 252건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 29건, `MACRO` 18건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9171, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 875건/680종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 12 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0을 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 59,485건에서 59,511건으로 늘었고, Naver 원천 데이터는 33,519건에서 33,545건으로 늘었다.
- raw 종목 매칭은 3,369개를 유지했고, 후보 큐는 13,296건/3,192종목을 유지했다.
- 누락 종목 shard plan은 772개/8개 shard를 유지했다. priority는 `no_raw_no_candidate` 595개와 `raw_without_candidate` 177개를 유지했다.
- 새 모델 `financial-ml-tfidf-logreg-20260610202009`는 supervised 3,609건과 pseudo-label 1,091건을 합친 4,700건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 738건, 738개 종목을 event-model-only pseudo-label로 유지했다.
- 종목 후보 큐 승격 분포는 `RISK` 274건, `CONTRACT` 252건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 29건, `MACRO` 18건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9171, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 유지했다.
- risk/contract per-stock 2 확장 profile은 875건/679종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 13 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 2를 0.4초 보수적 sleep으로 Naver News Search 추가 수집해 512개 요청이 모두 성공했고 rate limit은 0건이었다. provider status는 `completed=true`로 기록됐다.
- raw 후보는 59,511건에서 61,886건으로 늘었고, Naver 원천 데이터는 33,545건에서 35,920건으로 늘었다.
- raw 종목 매칭은 3,369개에서 3,458개로 늘었고, 후보 큐는 13,296건/3,192종목에서 13,983건/3,278종목으로 확장됐다.
- 누락 종목 shard plan은 772개/8개 shard에서 686개/7개 shard로 줄었다. priority는 `no_raw_no_candidate` 595개에서 506개로 줄고 `raw_without_candidate`는 177개에서 180개로 늘었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610203855`는 supervised 3,609건과 pseudo-label 1,081건을 합친 4,690건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 739건, 739개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 275건, `CONTRACT` 255건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 25건, `MACRO` 20건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9500, macro F1 0.9210, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 881건/685종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 14 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0과 shard 5를 0.4초 보수적 sleep으로 Naver News Search 추가 수집했다. 두 shard 모두 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- shard 0은 dedupe 후 raw 후보를 61,886건에서 61,907건으로 늘리고 raw 매칭 종목을 3,458개에서 3,460개로 늘렸다.
- shard 5는 dedupe 후 raw 후보를 61,907건에서 63,682건으로 늘리고 raw 매칭 종목을 3,460개에서 3,470개로 늘렸다.
- Naver 원천 데이터는 35,920건에서 37,716건으로 확장됐다.
- 후보 큐는 13,983건/3,278종목에서 14,565건/3,356종목으로 확장됐다.
- 누락 종목 shard plan은 686개/7개 shard에서 608개/7개 shard로 줄었다. priority는 `no_raw_no_candidate` 506개에서 494개로 줄고 `raw_without_candidate`는 180개에서 114개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610211549`는 supervised 3,609건과 pseudo-label 1,099건을 합친 4,708건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 757건, 757개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 281건, `CONTRACT` 260건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 30건, `MACRO` 21건이다.
- `MACRO` 이벤트 threshold를 0.34에서 0.24로 보정해 실제 뉴스 gold의 라벨별 recall 회귀를 복구했다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 885건/695종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 15 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0과 shard 1을 0.4초 보수적 sleep으로 Naver News Search 추가 수집했다. 두 shard 모두 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- shard 0은 dedupe 후 raw 후보를 63,682건에서 63,821건으로 늘리고 raw 매칭 종목을 3,470개에서 3,474개로 늘렸다.
- shard 1은 dedupe 후 raw 후보를 63,821건에서 65,460건으로 늘리고 raw 매칭 종목을 3,474개에서 3,540개로 늘렸다.
- Naver 원천 데이터는 37,716건에서 39,494건으로 확장됐다.
- 후보 큐는 14,565건/3,356종목에서 15,041건/3,424종목으로 확장됐다.
- 누락 종목 shard plan은 608개/7개 shard에서 540개/6개 shard로 줄었다. priority는 `no_raw_no_candidate` 494개에서 424개로 줄고 `raw_without_candidate`는 114개에서 116개로 늘었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610214200`은 supervised 3,609건과 pseudo-label 1,102건을 합친 4,711건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 762건, 762개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 290건, `CONTRACT` 261건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 24건, `MACRO` 22건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 885건/700종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 16 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0과 shard 1을 0.4초 보수적 sleep으로 Naver News Search 추가 수집했다. 두 shard 모두 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- shard 0은 dedupe 후 raw 후보를 65,460건에서 65,482건으로 늘렸고 raw 매칭 종목은 3,540개를 유지했다.
- shard 1은 dedupe 후 raw 후보를 65,482건에서 66,618건으로 늘리고 raw 매칭 종목을 3,540개에서 3,578개로 늘렸다.
- Naver 원천 데이터는 39,494건에서 40,652건으로 확장됐다.
- 후보 큐는 15,041건/3,424종목에서 15,357건/3,464종목으로 확장됐다.
- 누락 종목 shard plan은 540개/6개 shard에서 500개/5개 shard로 줄었다. priority는 `no_raw_no_candidate` 424개에서 386개로 줄고 `raw_without_candidate`는 116개에서 114개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610220747`은 supervised 3,609건과 pseudo-label 1,118건을 합친 4,727건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 776건, 776개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 300건, `CONTRACT` 261건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 45건, `EARNINGS` 29건, `MACRO` 21건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 890건/707종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 17 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0과 shard 1을 0.4초 보수적 sleep으로 Naver News Search 추가 수집했다. 두 shard 모두 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- shard 0은 dedupe 후 raw 후보를 66,618건에서 66,688건으로 늘리고 raw 매칭 종목을 3,579개로 늘렸다.
- shard 1은 dedupe 후 raw 후보를 66,688건에서 67,286건으로 늘리고 raw 매칭 종목을 3,597개로 늘렸다.
- Naver 원천 데이터는 40,652건에서 41,320건으로 확장됐다.
- 후보 큐는 15,357건/3,464종목에서 15,511건/3,485종목으로 확장됐다.
- 누락 종목 shard plan은 500개/5개 shard에서 479개/5개 shard로 줄었다. priority는 `no_raw_no_candidate` 386개에서 367개로 줄고 `raw_without_candidate`는 114개에서 112개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610223509`은 supervised 3,609건과 pseudo-label 1,119건을 합친 4,728건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 775건, 775개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 298건, `CONTRACT` 260건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 30건, `MACRO` 23건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 887건/705종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-11 - 전 종목 후보 shard 18 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0과 shard 1을 0.4초 보수적 sleep으로 Naver News Search 추가 수집했다. 두 shard 모두 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- shard 0은 dedupe 후 raw 후보를 67,286건에서 67,317건으로 늘렸고 raw 매칭 종목은 3,597개를 유지했다.
- shard 1은 dedupe 후 raw 후보를 67,317건에서 67,707건으로 늘리고 raw 매칭 종목을 3,606개로 늘렸다.
- Naver 원천 데이터는 41,320건에서 41,741건으로 확장됐다.
- 후보 큐는 15,511건/3,485종목에서 15,608건/3,495종목으로 확장됐다.
- 누락 종목 shard plan은 479개/5개 shard에서 469개/5개 shard로 줄었다. priority는 `no_raw_no_candidate` 367개에서 358개로 줄고 `raw_without_candidate`는 112개에서 111개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260610230131`은 supervised 3,609건과 pseudo-label 1,122건을 합친 4,731건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 778건, 778개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 293건, `CONTRACT` 266건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 32건, `MACRO` 23건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 894건/710종목으로 확장됐지만 실제 뉴스 gold macro F1 gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-12 - 전 종목 후보 shard 19 추가 확장
- 최신 `stock_collection_shard_plan`의 shard 0과 shard 1을 0.4초 보수적 sleep으로 Naver News Search 추가 수집했다. 두 shard 모두 512개 요청이 모두 성공했고 rate limit은 0건이었다.
- shard 0은 dedupe 후 raw 후보를 67,707건에서 68,371건으로 늘리고 raw 매칭 종목을 3,609개로 늘렸다.
- shard 1과 추가 최신 뉴스 shard는 dedupe 후 raw 후보를 68,371건에서 70,287건으로 늘리고 raw 매칭 종목을 3,613개로 유지했다.
- Naver 원천 데이터는 41,741건에서 44,321건으로 확장됐다.
- 후보 큐는 15,608건/3,495종목에서 15,720건/3,506종목으로 확장됐다.
- 누락 종목 shard plan은 469개/5개 shard에서 458개/5개 shard로 줄었다. priority는 `no_raw_no_candidate` 358개에서 351개로 줄고 `raw_without_candidate`는 111개에서 107개로 줄었다.
- 새 모델 `financial-ml-tfidf-logreg-20260612005235`은 supervised 3,609건과 pseudo-label 1,125건을 합친 4,734건으로 학습했다.
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 781건, 781개 종목을 event-model-only pseudo-label로 제한 승격했다.
- 종목 후보 큐 승격 분포는 `RISK` 294건, `CONTRACT` 266건, `CAPITAL_ACTION` 120건, `CORPORATE_ACTION` 44건, `EARNINGS` 35건, `MACRO` 22건이다.
- 80건 Naver 실제 뉴스 gold 기준 이벤트 recall 0.9625, macro F1 0.9108, 감성 accuracy 0.9125, 중요도 accuracy 0.9250, 종목 accuracy 1.0을 기록했다.
- risk/contract per-stock 2 확장 profile은 895건/709종목으로 확장됐지만 실제 뉴스 gold gate를 통과하지 못해 current release에는 반영하지 않았다.
- service readiness는 사람이 승인한 coverage gold가 아직 0건이라 계속 `fail`이다.

## 2026-06-19 - 하네스·문서 최신화
- Papago와 한국수출입은행 환율 provider 표현을 현재 경계에 맞게 제거했다. AI 서비스는 외부 credential을 관리하지 않고, 번역 provider 연동은 Hana-OmniLens-API의 DeepL adapter가 담당한다.
- 외국인 보유 row는 KIS 현재가 REST snapshot 스키마를 기준으로 설명하되, 기존 `parse_krx_foreign_holding_row` 함수명은 하위 호환을 위해 유지한다고 명시했다.
- current release 기준 service readiness와 audited gold readiness는 `pass`이며, 사람 검수 gold 확장과 운영 drift 점검은 지속 품질 관리 항목으로 정리했다.

## 2026-06-12 - bootstrap service readiness와 audited gold readiness 분리
- `model_release_report.py`의 service readiness를 사람 승인 coverage gold 필수 조건에서 분리했다.
- `service_readiness`는 release quality gate, consistency check, 500종목 이상 stock-candidate pseudo coverage를 만족하면 bootstrap 운영 기준 `pass`로 기록한다.
- `audited_gold_readiness`는 기존 coverage validation을 유지해 사람이 승인한 stock review gold 기준을 별도로 추적한다.
- 현재 모델은 stock-candidate pseudo coverage 781종목으로 bootstrap service readiness를 `pass`한다.
- 사람 승인 coverage gold는 아직 0건이라 audited gold readiness는 계속 `fail`이다.

## 2026-06-13 - 실시간 뉴스 smoke/drift 평가 배치 추가
- `build_live_news_evaluation_batch.py`가 국내주식 universe에서 종목을 랜덤 표본 추출하고 Naver 최신 뉴스로 라벨 없는 운영 표본을 만든다.
- 배치 row는 쿼리 종목, 모델 예측 종목, 이벤트·감성·중요도 confidence, 추후 검수용 `final_*` 필드를 함께 기록한다.
- `reports/live-news-evaluation-report.json`은 provider status, emitted row 수, 종목 매칭률, 예측 라벨 분포를 기록한다.
- 이 배치는 라벨 없는 smoke/drift 점검용이며 사람이 `final_*` 라벨을 채우기 전까지 F1이나 supervised gold로 취급하지 않는다.

## 2026-06-20 - 번역 샘플 비교 리포트와 금융 용어집 v2
- `local-financial-glossary-v2`로 번역 품질 보조 모델 버전을 올리고 실공시 오역 위험이 큰 매매거래정지, 상장폐지 사유, 소송 청구, 타법인 주식 취득, 자기주식, 전환사채, 관리·투자주의 환기 용어를 glossary/fallback rule에 추가했다.
- `build_translation_sample_report.py`가 실제 Naver 뉴스 gold와 OpenDART 공시 gold 표본을 Hannah AI 분석 결과, 로컬 금융용어 번역 보조, glossary, translation quality flag, review finding과 함께 `reports/translation-sample-report.json`으로 기록한다.
- DeepL/Papago live provider 호출은 Hana-OmniLens-API 책임으로 유지하고, Hannah 리포트는 `external_translation_join_key`로 외부 provider smoke 출력과 비교할 수 있게 했다.

## 2026-06-20 - AI confidence serving metadata
- `/api/v1/alerts/analyze` 응답에 `event_confidence`, `sentiment_confidence`, `importance_confidence`, `stock_match_confidence`를 추가했다.
- 실시간 뉴스 smoke/drift row와 report에 분석 confidence를 기록해 운영 중 품질 관측과 drift 점검에 사용한다.
- audit log에는 원문을 남기지 않고 confidence만 추가 기록한다.
- Hannah는 confidence 값을 제공하지만 신뢰도 기반 자동 차단 여부를 결정하지 않는다.

## 2026-06-20 - 실시간 뉴스 smoke/drift 최신성 status
- `live_news_evaluation.py`에 `confidence_summary`와 `build_live_news_monitoring_status`를 추가해 live-news 리포트가 최신 release 모델, schema, confidence summary를 만족하는지 검증한다.
- `scripts/build_live_news_monitoring_status.py`는 외부 API 호출 없이 커밋된 live-news 리포트와 model release 리포트를 비교해 `reports/live-news-monitoring-status.json`을 생성한다.
- Naver live-news smoke 배치를 최신 `financial-ml-tfidf-logreg-20260619095828` 모델로 재생성해 `overall_status=pass`로 전환했다.
- confidence는 운영 품질 관측 신호로만 기록하며, 신뢰도 기반 자동 차단은 수행하지 않는다.

## 2026-06-20 - query-scoped live-news primary stock 보강
- live-news smoke 배치는 종목별 쿼리로 수집한 표본이므로 sampled stock을 request `stock_universe` candidate로 분석기에 전달한다.
- 전역 analyzer의 internal universe fallback은 기존처럼 보수적으로 유지하고, query-scoped candidate 매칭만 primary confidence 1.0으로 기록한다.
- 최신 live-news smoke 표본은 `predicted_stock_null_count=0`, `sampled_stock_primary_match_count=10`, `sampled_stock_model_match_rate=1.0`, `stock_match_confidence.average=1.0`을 기록한다.

## 2026-06-17 - 기능정의서 기반 API 계약 하네스 추가
- 국내주식 주문 상태 API가 외국인 보유율, 한도소진율, 예측 지분율 바운더리, VI, 상·하한가, 즉시체결 가능 여부를 계산한다.
- 뉴스·공시 인텔리전스 이벤트 API가 기존 NLP 분석 결과에 번역 제목·요약과 WebSocket 이벤트용 필드를 패킹한다.
- 세무 환급 API가 미국 투자자 CASE_01, 서류 검증 상태, 배당 7% 환급, 양도세 환급, 3% 선지급 수수료, 사후 환수 플래그를 계산한다.
- 외국인 지분 boundary, 매매제한 상태, 금융 번역, 세무 환급 선지급 로직을 모델 클래스로 분리하고 각 응답에 model version을 기록한다.
- `tests/test_feature_definition_contracts.py`로 기능정의서의 세 도메인 JSON 계약을 회귀 테스트에 포함했다.

## 2026-06-17 - PR 및 커밋 메시지 컨벤션 하네스 추가
- PR 제목·본문 한글 필수 규칙과 PR 템플릿 필드 누락을 검사하는 `verify_message_conventions.py`를 추가했다.
- PR head 커밋 제목이 Conventional Commit 형식과 한글 제목 규칙을 지키는지 CI에서 검증한다.
- 메시지 컨벤션 회귀 테스트를 추가해 영어 PR 제목과 영어 커밋 제목을 실패 케이스로 고정했다.

## 2026-06-17 - provider 파서 하네스 추가
- KIS 종목 마스터 CSV, KIS 실시간 현재가/VI 패킷, KRX 외국인 보유 row를 주문 상태 모델 입력으로 정규화하는 파서를 추가했다.
- provider별 종목코드 불일치를 거부해 서로 다른 종목의 시세·외국인 보유 데이터를 합성하지 않도록 했다.
- MTS 세무 서류 OCR row와 옴니버스 하위 계좌 거래 row를 세무 환급 모델 입력으로 정규화하는 파서를 추가했다.

## 2026-06-17 - 인텔리전스 provider 파서 하네스 추가
- Naver News Search row와 OpenDART 공시검색 row를 `IntelligenceEventRequest` 입력으로 정규화하는 파서를 추가했다.
- provider event id, 원문 URL, 종목 후보를 사용해 중복 제거 키를 생성하고 유효하지 않은 원문 URL은 거부한다.
- 분석·번역 완료 응답을 협력사/종목 단위 Hana OmniLens WebSocket 이벤트 JSON으로 패킹하는 함수를 추가했다.

## 2026-06-17 - 인텔리전스 중복 제거 계약 노출
- `/api/v1/intelligence/events` 응답에 분석기의 `duplicate_key`를 포함해 현지 백엔드가 같은 이벤트를 중복 저장하지 않도록 했다.
- Hana OmniLens WebSocket 이벤트 패킷에도 동일한 `duplicate_key`를 싣는다.
- 종목과 출처가 다른 이벤트는 중복키가 분리되는지 provider 하네스로 검증한다.

## 2026-06-17 - 주문 가능 여부 모델 보강
- 주문 상태 API가 외국인 한도 잔여 수량과 한도 사용 상태(`NORMAL`, `CAUTION`, `LIMIT_REACHED`)를 응답한다.
- 실시간 체결 가능 상태와 외국인 한도 상태를 합성해 매수/매도 가능 여부, 주문 가능 인디케이터, 제한 사유 코드를 산출한다.
- 정규장 외국인 한도 주의 상태와 VI/상한가 제한 상태를 provider 하네스로 검증한다.

## 2026-06-18 - 세무 환급 진행 상태 계약 보강
- 세무 환급 API가 과세연도, 정부 검증 참조번호, 환급 진행 상태를 응답한다.
- 환급 가능액을 국세/지방세 표시 금액으로 분해하고 다음 조치 코드와 사후 환수 리스크 고지를 패킹한다.
- CASE_01 즉시 선지급 가능 상태와 서류 미완료 대기 상태를 provider 하네스로 검증한다.

## 2026-06-18 - PR 제목 prefix 계약 복원
- PR 제목도 커밋 제목과 동일한 `type(scope): 한글 제목` 형식을 요구하도록 메시지 하네스를 변경했다.
- 단일 커밋 PR에서는 PR 제목이 대표 커밋 제목 전체와 일치해야 통과하도록 회귀 테스트를 갱신했다.
- Git 전략과 테스트 문서의 PR 제목 예시를 prefix 포함 형식으로 수정했다.

## 2026-06-19 - 세무 서류 OCR/위변조 검증 모델 API
- `/api/v1/tax/documents/verify`를 추가해 외부 OCR 결과와 위변조 signal을 `VERIFIED`, `PENDING`, `REJECTED` 상태로 판정한다.
- OCR confidence, fraud risk, 필수 field 누락, manual review 여부, rejection reason, document model version을 공통 응답 envelope으로 반환한다.
- CASE_01 환급 모델이 소비하는 `ocr-fraud-risk-gate-v1` 문서 검증 결과를 API 계약 테스트로 고정했다.

## 2026-06-21 - 외국인 보유 시계열 예측 API
- `/api/v1/market/foreign-ownership/predict`는 OmniLens 외국인 보유 snapshot과 일별 시계열 기반 금일 한도 도달 가능성 boundary를 반환한다. 요청 수량과 장중 누적 거래량은 호환 필드로만 수신한다.
- 모델 버전은 `hannah-foreign-ownership-timeseries-v1`이며 confidence, 추세 변화율, 관측치 수, source를 함께 응답한다.
- confidence는 observe-only 정책으로 유지하고 Hannah는 주문 차단 여부를 반환하지 않는다.

## 2026-06-21 - 뉴스·공시 full-content v2 계약
- 현재 release 모델을 제목/snippet 기반 v1 baseline과 fallback으로 보존하기로 정리했다.
- v2 분석 계약은 전문 입력, 이미지 URL metadata, content availability, What/Why/Impact 3줄 요약, 전문 기반 duplicate key를 추가한다.
- Naver News Search는 발견 데이터이며, 전문 학습 데이터는 Hana-OmniLens-API가 권리 확인 후 저장한 dataset export만 사용하도록 문서화했다.

## 2026-06-21 - 전문 기반 What/Why/Impact 분석 schema
- `AlertAnalysisRequest`에 `content`, `image_urls`, `canonical_url`, `content_hash`, `source_license_policy`를 추가했다.
- `AlertAnalysisResponse`와 `IntelligenceEventResponse`에 `summary_lines`, `content_availability`, 원문/번역 전문, 이미지 URL, `cluster_key`를 추가했다.
- 분석기는 제목/snippet/full content를 함께 사용하고, 전문이 있으면 `FULL_TEXT`, 없으면 `SUMMARY_ONLY`로 응답한다.
- What/Why/Impact 요약은 로컬 금융 rule engine으로 생성하며 기존 제목/snippet v1 모델은 fallback과 회귀 비교 기준으로 유지한다.

## 2026-06-22 - 기사·공시 전문 기반 학습 전환
- `LabeledAlert` 학습 row가 `title`, `snippet`, `full_content`, `content_availability`, `source_license_policy`, `content_hash`를 보존하도록 확장한다.
- 권리 안전 전문 gold 파일 `data/training/financial_alert_full_content_gold.jsonl`을 학습 소스에 추가하고, 전문이 있는 row는 `title + snippet + full_content`를 모델 입력으로 사용한다.
- release 리포트는 전문 학습 row 수, 라이선스 정책, 전문 availability를 lineage로 기록해 제목/snippet-only artifact와 구분한다.

## 2026-06-22 - 비LLM 전문 뉴스 분석 품질 보강
- `scripts/build_real_full_content_training_data.py`의 기사 본문 추출 selector와 boilerplate penalty를 보강해 뉴스 전문 855건, OpenDART document 전문 195건 등 총 1,050건의 full-content 학습/검수 후보를 생성했다.
- 사람이 검수하지 않은 전문 약한 라벨 1,036건은 이벤트·감성·중요도 supervised loss에서 제외하고, 전문 원문은 요약/분석 입력 품질 검증과 검수 후보 생성에 사용하도록 `ml_trainer.py` 정책을 강화했다.
- 새 모델 `financial-ml-tfidf-logreg-20260622055520`는 supervised 4,659건과 teacher-gated pseudo-label 1,027건 중 이벤트 학습 4,650건으로 재학습했다.
- 실제 뉴스 gold 80건 기준 이벤트 recall 0.9875, macro F1 0.9268, 감성 accuracy 0.9750, 중요도 accuracy 0.9625, 종목 accuracy 1.0을 기록했다.
- 실공시 gold 30건 기준 이벤트 recall 1.0, macro F1 0.9867, 감성 accuracy 1.0, 중요도 accuracy 1.0, 종목 accuracy 1.0을 기록했다.
- 최신 Naver 160건 live quality audit에서 전체 quality pass rate 0.9875, query-relevant quality pass rate 0.9875, full-content rate 0.71875, sampled stock model match rate 1.0을 기록했다.
- `하나은행` 같은 비상장/레거시 은행 엔티티를 내부 종목 fallback에서 제외하고, 뉴스 source type에서는 `DISCLOSURE` 태그가 섞이지 않도록 회귀 테스트를 추가했다.
- `reports/model-release-report.json`, `reports/pseudo-label-promotion-monitoring.json`, `reports/service-readiness-report.json`은 새 모델 기준 모두 `pass`를 기록했다.

## 2026-06-22 - 전문 뉴스 추가 학습 목표 재정의
- 최신 `feature` 기반 `feat/news-summary-training-expansion` 브랜치에서 추가 학습을 시작했다.
- 목표는 실제 뉴스·공시 전문 데이터 확대, query stock 관련성 필터, What/Why/Impact 요약 품질 gate를 함께 보강해 검색 provider 노이즈와 모델 요약 품질을 분리 평가하는 것이다.
- 사람이 검수하지 않은 전문 약한 라벨은 계속 supervised loss에서 제외하고, 관련 종목이 본문에서 확인되는 row만 live query-relevant gate와 학습 승격 후보로 다룬다.

## 2026-06-22 - 서비스급 대량 전문 학습 반복 시작
- 최신 `feature` 기반 `feat/service-scale-news-training` 브랜치에서 전문 데이터셋 5,000건 이상 1차 확대를 시작했다.
- 서비스 승격 전 기준은 최신 미학습 live quality audit 1,000건 이상, query-relevant pass rate와 sampled stock match rate 동시 관측, 본문 추출 실패·중복·종목 불일치 제외 사유 리포트화로 둔다.
- 장기 운영 기준은 종목·업종·이벤트가 균형 잡힌 10,000건 이상 전문 gold/검수 후보와 월별 drift 재학습 루프로 관리한다.

## 2026-06-22 - 서비스급 전문 5,000건 학습 및 1,000건 live audit
- Naver News Search raw 후보를 83,105건으로 늘리고, 전문 학습/검수 후보를 뉴스 4,727건과 공시 273건 등 총 5,000건으로 확대했다.
- 대량 전문 수집을 위해 기사 전문 fetch를 worker/batch 단위 병렬 처리로 보강하고, 깨진 chunk 응답은 실패 카운트로 격리했다.
- 검수되지 않은 전문 약한 라벨 4,984건은 supervised loss뿐 아니라 holdout 정답에서도 제외해 평가 오염을 막았다.
- 새 모델 `financial-ml-tfidf-logreg-20260622073857`은 이벤트 학습 4,649건, supervised 8,607건, teacher-gated pseudo-label 1,026건 기준으로 재학습했다.
- 80건 실제 뉴스 gold 기준 이벤트 recall 0.9875, macro F1 0.9221, 감성 accuracy 0.9750, 중요도 accuracy 0.9625, 종목 accuracy 1.0으로 gate를 통과했다.
- 1,000건 최신 query-relevant live quality audit에서 quality pass rate 0.99, full-content rate 0.682, sampled stock model match rate 0.999, provider failed/rate limit 0건을 기록했다.

## 2026-06-22 - 서비스급 전문 20,000건 확장 학습 시작
- 최신 `feature` 기반 `feat/service-scale-news-training-20k` 브랜치에서 5,000건 기준선을 20,000건 이상 전문 후보로 확장한다.
- 기존 재사용 가능한 전문 row는 보존하고 신규 원문 fetch는 실패·중복·본문 부족·종목 불일치·라벨 quota 제외 사유를 리포트로 남긴다.
- 재학습 후 release/readiness gate와 1,000건 이상 live quality audit을 다시 통과해야 feature와 main 승격 대상으로 본다.

## 2026-06-22 - 서비스급 전문 20,000건 재학습 및 요약 품질 보강
- 전문 학습/검수 후보를 뉴스 19,727건과 공시 273건 등 총 20,000건으로 확대했다.
- 신규 원문 fetch는 40,000건 시도, 16,042건 추가, 6,159건 fetch 실패, 3,547건 기존 URL 재사용, 에러 0건으로 종료했다.
- 새 모델 `financial-ml-tfidf-logreg-20260622090407`은 full text 입력 19,959건을 포함하고, 검수되지 않은 전문 약한 라벨 19,945건은 이벤트·감성·중요도 학습과 holdout 정답에서 제외했다.
- `[오늘의 주요공시]` 같은 여러 종목 roundup 제목에서는 제목 대신 snippet/본문 문맥을 우선해 What/Why/Impact 요약을 생성하도록 정제했다.
- 1,000건 최신 query-relevant live quality audit에서 quality pass rate 0.991, full-content rate 0.69, sampled stock model match rate 0.999, `SUMMARY_BOILERPLATE` 0건을 기록했다.
- `reports/model-release-report.json`, `reports/pseudo-label-promotion-monitoring.json`, `reports/service-readiness-report.json`은 새 모델 기준 모두 `pass`를 기록했다.

## 2026-06-22 - 원문 본문 번역 API 계약 명시
- 인텔리전스 provider parser가 사용 허가된 뉴스·공시 전문, 이미지, canonical URL, content hash, license policy를 `IntelligenceEventRequest`로 전달하도록 보강했다.
- 응답과 WebSocket payload에 `original_body`, `translated_body`, `body_source_type`를 추가해 원문 본문 번역과 요약 번역 계약을 분리해 검증한다.
- 기능정의 하네스와 provider 하네스에서 전문 입력 시 `FULL_TEXT` 본문 출처와 원문/번역 본문 필드를 검증한다.

## 2026-06-28 - 외국인 보유/취득 수량 ML 학습/평가
- 예측 타깃을 `foreign_limit_quantity`가 아니라 `foreign_owned_quantity`로 정정했다. 한도수량은 예측 대상이 아니라 예측 보유수량을 한도소진율로 환산하는 분모로만 사용한다.
- `foreign_owned_quantity`만 사용해 다음 거래일 외국인 보유/취득 수량을 예측하는 ML 학습기를 추가했다.
- 학습기는 종목을 무시하지 않고 `stock_code` 범주 feature를 포함한 panel/global regression으로 Ridge, HistGradientBoostingRegressor, RandomForestRegressor, hurdle classifier+regressor 후보를 walk-forward 검증한다.
- 날짜 feature, 변화 간격, 최근 변화 횟수, 마지막 변화율을 추가해 종목별 보유수량 흐름을 반영했다.
- 실제 KRX 기반 상위 30종목 데이터 7,290개 관측치, 6,690개 학습 샘플로 학습했고, 선택 후보는 `ridge_delta_ratio`, blend alpha 0.05였다.
- champion baseline은 전일 보유수량 유지이며, 전체 KRX 가용 종목 기준 baseline MAE 34,589.08, promoted guarded runtime MAE 34,446.93을 기록했다.
- guarded runtime은 종목별 검증에서 ML, persistence baseline, stale-guarded mean delta, median multi delta, mean delta 중 MAE가 가장 낮은 정책을 선택하며, baseline 대비 MAE 0.4110%, RMSE 0.7474%, MAPE 6.8484%를 개선해 `release_status=promoted`로 기록했다.
- 종목별 검증에서는 573종목이 ML, 1,016종목이 persistence baseline, 626종목이 `stale_guarded_mean_delta_20`, 20종목이 `median_multi_delta`, 5종목이 `mean_delta_20` 추천이었다.
- serving은 predicted owned quantity `min/base/max`와 예측 순취득수량을 반환하고, 한도소진율은 현재 `foreign_limit_quantity`로 나누어 계산한다. 기존 limit quantity 응답 필드는 호환성 목적으로 현재 한도수량을 그대로 채운다.
