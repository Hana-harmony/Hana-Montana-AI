# 글로벌 피어 AI Smoke 테스트

## 목적
- API 계약 테스트가 아니라 실제 한국 종목을 넣었을 때 AI 매칭 결과가 투자자가 이해할 수 있는 peer인지 점검한다.
- 동일 회사의 미국 ADR이 peer로 잡히는 중복 상장 노이즈를 배제하고, 섹터/산업/사업모델/규모/재무 유사도 근거가 함께 나오는지 확인한다.

## 최신 실행
- 리포트: `reports/global-peer-ai-smoke-report.json`
- 모델 버전: `global-peer-hybrid-ranker-20260629214642`
- 모델 구조: TF-IDF retrieval + SVD semantic embedding + 재무/규모 feature + pairwise LogisticRegression reranker
- serving calibration: pairwise ranker 60%, base text/semantic/financial score 40%
- 샘플 수: 15개 한국 대형/대표 종목
- 전종목 coverage 리포트: `reports/global-peer-full-coverage-report.json`
- 전종목 coverage 결과: 3,967/3,967개 추론 성공, failure 0개, 동일회사 중복 0개, 근거 누락 0개, quality gate `pass`
- monitoring 결과: LOW confidence 75.4726%, generic sector 68.8177%, confidence monitoring `needs_improvement`

| 한국 종목 | AI primary peer | confidence | 핵심 근거 |
| --- | --- | --- | --- |
| Samsung Electronics | Micron Technology | HIGH 0.7667 | 반도체, 메모리/전자 제조, 메가캡 |
| SK hynix | Micron Technology | HIGH 0.8894 | 메모리 반도체, DRAM/NAND/HBM |
| NAVER | Alphabet | HIGH 0.7449 | 검색/광고/플랫폼, 인터넷 플랫폼 |
| Hyundai Motor | Toyota Motor | HIGH 0.8138 | 완성차 제조, 글로벌 자동차 peer |
| LG Energy Solution | Tesla | HIGH 0.8027 | EV 배터리/에너지 저장 proxy, 대형 배터리 생태계 |
| Samsung Biologics | Thermo Fisher Scientific | MEDIUM 0.6606 | 바이오 CDMO/생명과학 제조 서비스 |
| Celltrion | Biogen | MEDIUM 0.6961 | 바이오의약품/바이오시밀러 |
| KB Financial Group | Citigroup | MEDIUM 0.6681 | 은행/금융지주, 대형 금융서비스 |
| Shinhan Financial Group | Citigroup | MEDIUM 0.6424 | 은행/금융지주, 대형 금융서비스 |
| Hana Financial Group | Citigroup | MEDIUM 0.6844 | 은행/금융지주, 대형 금융서비스 |
| LG Chem | Dow | HIGH 0.8833 | 화학/첨단소재 |
| Samsung SDI | QuantumScape | HIGH 0.8257 | 배터리/에너지 저장 |
| LG Electronics | Whirlpool | HIGH 0.8640 | 가전/소비자 전자 |
| SK Telecom | Verizon Communications | HIGH 0.7997 | 통신 네트워크/무선 가입 서비스 |
| Alteogen | Halozyme Therapeutics | HIGH 0.8574 | 약물전달 플랫폼/로열티 라이선싱 |

## 품질 기준
- `tests/test_global_peer_matcher.py`의 core smoke regression은 Samsung Electronics, SK hynix, NAVER, SK Telecom, LG Electronics, LG Energy Solution의 primary peer를 고정해 품질 퇴행을 막는다.
- 전종목 coverage regression은 `reports/global-peer-full-coverage-report.json`의 quality gate가 `pass`인지 확인한다.
- pairwise ranker 평가는 curated peer 14개 기준 top1 accuracy 1.0, top3 accuracy 1.0, MRR 1.0이다.
- 알테오젠은 Halozyme top1을 별도 release gate로 유지한다.
- 각 응답은 `matched_factors`에 섹터, 산업, 사업모델, 규모, 재무 유사도, 모델 유사도를 포함한다.

## 남은 한계
- 현재 국내 master에는 섹터/업종 컬럼이 없어 전종목 confidence는 한국어 사명 키워드와 재무 feature에 의존한다.
- LOW confidence 비율은 75.4726%로 monitoring target 35%를 넘는다. 추론 실패가 아니라 “근거 feature 부족” 신호로 운영 문서와 감사 리포트에 남긴다.
- 다음 개선은 KRX/WICS/GICS 또는 사업보고서 기반 국내 업종 feature를 학습 데이터에 추가하는 것이다.
- peer universe는 미국 상장 보통주 중심이라 CATL, Panasonic, Lonza처럼 더 직관적인 비미국/비상장/해외거래소 peer는 후보에 없다.
