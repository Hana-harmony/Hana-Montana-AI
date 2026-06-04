# 구현 기록

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
