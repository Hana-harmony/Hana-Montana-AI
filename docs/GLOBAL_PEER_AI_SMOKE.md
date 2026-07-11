# 글로벌 피어 AI Smoke 테스트

## 목적
- 실제 한국 종목 입력에서 투자자가 이해할 수 있는 peer가 생성되는지 점검한다.
- 동일 회사의 미국 ADR이 peer로 잡히는 중복 상장 노이즈를 배제하고, 섹터/산업/사업모델/규모/재무 유사도 근거가 함께 나오는지 확인한다.

## 최신 실행
- 리포트: `reports/global-peer-ai-smoke-report.json`
- 모델 버전: `global-peer-dynamic-similarity-20260711050601`
- 모델 구조: TF-IDF retrieval + SVD semantic embedding + 재무·업종·프로필 충실도·글로벌 인지도 동적 유사도
- 국내 universe: KIS 활성 KOSPI·KOSDAQ·KONEX 일반주식 2,752개, 종목별 고정 peer/anchor 없음
- 샘플 수: 15개 한국 대형/대표 종목
- 전종목 coverage 리포트: `reports/global-peer-full-coverage-report.json`
- 전종목 coverage 결과: 2,752/2,752개 추론 성공, failure 0개, 동일회사 중복 0개, 비교·강점 계약 실패 0개, quality gate `pass`
- monitoring 결과: LOW confidence 0.5451%, specific profile 2,752개, specific profile quality `pass`

| 한국 종목 | AI primary peer | confidence | 핵심 근거 |
| --- | --- | --- | --- |
| Samsung Electronics | Intel | MEDIUM 0.5352 | Information Technology / Semiconductors |
| SK hynix | Intel | MEDIUM 0.5403 | Information Technology / Semiconductors |
| NAVER | Microsoft | MEDIUM 0.48 | Information Technology / Software |
| Hyundai Motor | General Motors | MEDIUM 0.6577 | Consumer Discretionary / Automobiles |
| LG Energy Solution | Tesla | MEDIUM 0.6586 | Industrials / Battery and Energy Storage |
| Samsung Biologics | Biogen | MEDIUM 0.62 | Health Care / Biotechnology |
| Celltrion | Biogen | MEDIUM 0.62 | Health Care / Biotechnology |
| KB Financial Group | Citigroup | MEDIUM 0.5374 | Financials / Banks |
| Shinhan Financial Group | Citigroup | MEDIUM 0.5352 | Financials / Banks |
| Hana Financial Group | JP Morgan Chase | MEDIUM 0.52 | Financials / Banks |
| LG Chem | Dow | MEDIUM 0.672 | Materials / Specialty Chemicals |
| Samsung SDI | Tesla | MEDIUM 0.5674 | Industrials / Battery and Energy Storage |
| LG Electronics | Apple | MEDIUM 0.5468 | Consumer Discretionary / Consumer Electronics and Appliances |
| SK Telecom | AT&T | MEDIUM 0.6526 | Communication Services / Telecommunications |
| Alteogen | Thermo Fisher Scientific | MEDIUM 0.46 | Health Care / Biotechnology |

## 품질 기준
- `tests/test_global_peer_matcher.py`의 core smoke regression은 primary·comparison 정합성, 3개 고유 비교, 4개 근거 강점, sector/industry 적합성을 검증한다.
- 전종목 coverage regression은 `reports/global-peer-full-coverage-report.json`의 quality gate가 `pass`인지 확인한다.
- 특정 종목의 top1 정답을 release gate로 고정하지 않는다.
- 각 응답은 `matched_factors`에 섹터, 산업, 사업모델, 규모, 재무 유사도, 모델 유사도를 포함한다.

## 남은 한계
- 국내 master에는 섹터/업종 컬럼이 없지만, Naver 동일업종 비교 데이터와 Naver industry code taxonomy 보정을 별도 reference로 반영한다.
- LOW confidence는 15개, 0.5451%로 monitoring target 35%를 통과한다.
- peer universe는 미국 상장 보통주 중심이라 CATL, Panasonic, Lonza처럼 더 직관적인 비미국/비상장/해외거래소 peer는 후보에 없다.
