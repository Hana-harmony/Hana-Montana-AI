# 글로벌 피어 AI Smoke 테스트

## 목적
- API 계약 테스트가 아니라 실제 한국 종목을 넣었을 때 AI 매칭 결과가 투자자가 이해할 수 있는 peer인지 점검한다.
- 동일 회사의 미국 ADR이 peer로 잡히는 중복 상장 노이즈를 배제하고, 섹터/산업/사업모델/규모/재무 유사도 근거가 함께 나오는지 확인한다.

## 최신 실행
- 리포트: `reports/global-peer-ai-smoke-report.json`
- 모델 버전: `global-peer-hybrid-ranker-20260630171118`
- 모델 구조: TF-IDF retrieval + SVD semantic embedding + 재무/규모 feature + pairwise LogisticRegression reranker
- serving calibration: pairwise ranker 60%, base text/semantic/financial score 40%
- 국내 업종 feature: Naver 동일업종 비교 profile 2,649개, taxonomy 보정 후 Naver specific profile 2,637개, 전종목 specific profile 3,068개
- 샘플 수: 15개 한국 대형/대표 종목
- 전종목 coverage 리포트: `reports/global-peer-full-coverage-report.json`
- 전종목 coverage 결과: 3,967/3,967개 추론 성공, failure 0개, 동일회사 중복 0개, 근거 누락 0개, quality gate `pass`
- monitoring 결과: LOW confidence 22.6620%, generic sector 22.6620%, specific profile LOW 0개, confidence monitoring `pass`

| 한국 종목 | AI primary peer | confidence | 핵심 근거 |
| --- | --- | --- | --- |
| Samsung Electronics | Micron Technology | HIGH 0.7493 | Information Technology / Semiconductors |
| SK hynix | Micron Technology | HIGH 0.8723 | Information Technology / Semiconductors |
| NAVER | Alphabet | HIGH 0.7789 | Information Technology / Internet Platforms |
| Hyundai Motor | Toyota Motor | HIGH 0.8178 | Consumer Discretionary / Automobiles |
| LG Energy Solution | Tesla | HIGH 0.8294 | Industrials / Battery and Energy Storage |
| Samsung Biologics | Thermo Fisher Scientific | MEDIUM 0.6364 | Health Care / Biotechnology |
| Celltrion | Biogen | MEDIUM 0.6897 | Health Care / Biotechnology |
| KB Financial Group | Citigroup | HIGH 0.7489 | Financials / Banks |
| Shinhan Financial Group | Citigroup | HIGH 0.7295 | Financials / Banks |
| Hana Financial Group | Citigroup | HIGH 0.7248 | Financials / Banks |
| LG Chem | Dow | HIGH 0.8344 | Materials / Specialty Chemicals |
| Samsung SDI | Tesla | MEDIUM 0.6716 | Industrials / Battery and Energy Storage |
| LG Electronics | Whirlpool | HIGH 0.8628 | Consumer Discretionary / Consumer Electronics and Appliances |
| SK Telecom | Verizon Communications | HIGH 0.8199 | Communication Services / Telecommunications |
| Alteogen | Halozyme Therapeutics | HIGH 0.8046 | Health Care / Biotechnology |

## 품질 기준
- `tests/test_global_peer_matcher.py`의 core smoke regression은 Samsung Electronics, SK hynix, NAVER, SK Telecom, LG Electronics, LG Energy Solution의 primary peer를 고정해 품질 퇴행을 막는다.
- 전종목 coverage regression은 `reports/global-peer-full-coverage-report.json`의 quality gate가 `pass`인지 확인한다.
- pairwise ranker 평가는 curated peer 14개 기준 top1 accuracy 0.9286, top3 accuracy 1.0, MRR 0.9643이다.
- 알테오젠은 Halozyme top1을 별도 release gate로 유지한다.
- 각 응답은 `matched_factors`에 섹터, 산업, 사업모델, 규모, 재무 유사도, 모델 유사도를 포함한다.

## 남은 한계
- 국내 master에는 섹터/업종 컬럼이 없지만, Naver 동일업종 비교 데이터와 Naver industry code taxonomy 보정을 별도 reference로 반영한다.
- LOW confidence 비율은 22.6620%로 monitoring target 35%를 통과한다. specific profile 기준 LOW confidence는 0개다.
- peer universe는 미국 상장 보통주 중심이라 CATL, Panasonic, Lonza처럼 더 직관적인 비미국/비상장/해외거래소 peer는 후보에 없다.
