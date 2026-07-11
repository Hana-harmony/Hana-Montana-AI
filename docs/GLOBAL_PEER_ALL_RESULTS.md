# 글로벌 피어 전종목 현재 결과

## 성능 요약
- 모델 버전: `global-peer-dynamic-similarity-20260711050601`
- 시도/성공/실패: 2752 / 2752 / 0
- 성공률: 1.0
- confidence 분포: {'HIGH': 2, 'LOW': 15, 'MEDIUM': 2735}
- LOW confidence 비율: 0.005451
- domain match 분포: {'generic_or_mismatch': 15, 'industry': 1323, 'industry_and_business_model': 914, 'sector': 500}
- confidence root cause 분포: {'domain_mismatch': 15, 'not_low_confidence': 2737}
- generic/mismatch 비율: 0.005451
- financial context 분포: {'direct_financial_similarity': 73, 'not_available': 169, 'partial_direct_similarity': 1031, 'us_market_relative_proxy': 1479}
- specific profile 품질: {'profile_definition': 'source sector/industry가 generic legacy fallback이 아닌 종목', 'minimum_profile_count': 2500, 'actual_profile_count': 2752, 'maximum_low_confidence_ratio': 0.02, 'actual_low_confidence_ratio': 0.005451, 'low_confidence_count': 15, 'status': 'pass'}
- 동일회사 중복 노이즈: 0
- 구조화 표시 계약 실패: 0
- quality status: `pass`

## 전체 종목 결과
| 종목코드 | 종목명 | 원천 세부 분야 | primary peer | confidence | domain match | confidence root cause | financial context |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 000020 | 동화약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000040 | KR모터스 | Automobiles | F Ford Motor | MEDIUM 0.573 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000050 | 경방 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6363 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000070 | 삼양홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5932 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000080 | 하이트진로 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6613 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000087 | 하이트진로2우B | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6605 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000100 | 유한양행 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000105 | 유한양행우 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000120 | CJ대한통운 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6268 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000140 | 하이트진로홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6494 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000145 | 하이트진로홀딩스우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000150 | 두산 | Investment Holding Companies | IQV IQVIA Holdings | MEDIUM 0.6487 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000155 | 두산우 | Investment Holding Companies | IQV IQVIA Holdings | MEDIUM 0.648 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000157 | 두산2우B | Investment Holding Companies | IQV IQVIA Holdings | MEDIUM 0.648 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000180 | 성창기업지주 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000210 | DL | Specialty Chemicals | DOW Dow | MEDIUM 0.593 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000215 | DL우 | Specialty Chemicals | DOW Dow | MEDIUM 0.5929 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000220 | 유유제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000225 | 유유제약1우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000227 | 유유제약2우B | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000230 | 일동홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000240 | 한국앤컴퍼니 | Automobiles | GM General Motors | MEDIUM 0.5261 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000250 | 삼천당제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000270 | 기아 | Automobiles | GM General Motors | MEDIUM 0.6253 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000300 | DH오토넥스 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000320 | 노루홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000325 | 노루홀딩스우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000370 | 한화손해보험 | Insurance | GSHD Goosehead Insurance | MEDIUM 0.6408 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000390 | SP삼화 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000400 | 롯데손해보험 | Insurance | GSHD Goosehead Insurance | MEDIUM 0.6457 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000430 | 대원강업 | Automobiles | GM General Motors | MEDIUM 0.5273 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000440 | 중앙에너비스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000480 | CR홀딩스 | Investment Holding Companies | QTWO Q2 Holdings | MEDIUM 0.5669 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000490 | 대동 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000500 | 가온전선 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000520 | 삼일제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 000540 | 흥국화재 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6152 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000545 | 흥국화재우 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6152 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000590 | CS홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000640 | 동아쏘시오홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000650 | 천일고속 | Logistics and Transportation | VIA Via Transportation | MEDIUM 0.6381 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000660 | SK하이닉스 | Semiconductors | INTC Intel | MEDIUM 0.5406 | industry | not_low_confidence | partial_direct_similarity |
| 000670 | 영풍 | Semiconductors | INTC Intel | MEDIUM 0.4854 | industry | not_low_confidence | us_market_relative_proxy |
| 000680 | LS네트웍스 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000700 | 유수홀딩스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6078 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000720 | 현대건설 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000725 | 현대건설우 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000760 | 이화산업 | Specialty Chemicals | DOW Dow | MEDIUM 0.5897 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000810 | 삼성화재 | Insurance | HIG The Hartford Insurance Group | MEDIUM 0.6418 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000815 | 삼성화재우 | Insurance | HIG The Hartford Insurance Group | MEDIUM 0.6427 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000850 | 화천기공 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000860 | 강남제비스코 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000880 | 한화 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.6548 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000890 | 보해양조 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.65 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000910 | 유니온 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000950 | 전방 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5739 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000970 | 한국주철관 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000990 | DB하이텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001000 | 신라섬유 | Real Estate | WPC W. P. Carey . REIT | MEDIUM 0.5626 | industry | not_low_confidence | us_market_relative_proxy |
| 001020 | 페이퍼코리아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001040 | CJ | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.6423 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 001045 | CJ우 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.645 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 001060 | JW중외제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001065 | JW중외제약우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001067 | JW중외제약2우B | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001070 | 대한방직 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6089 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001080 | 만호제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001120 | LX인터내셔널 | Retail | WMT Walmart | MEDIUM 0.5296 | industry | not_low_confidence | us_market_relative_proxy |
| 001130 | 대한제분 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.616 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001200 | 유진투자증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001210 | 금호전기 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001230 | 동국홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001250 | GS글로벌 | Retail | WMT Walmart | MEDIUM 0.5328 | industry | not_low_confidence | us_market_relative_proxy |
| 001260 | 남광토건 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001270 | 부국증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001275 | 부국증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001290 | 상상인증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001340 | PKC | Specialty Chemicals | DOW Dow | MEDIUM 0.5632 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001360 | 삼성제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001380 | SG글로벌 | Automobiles | GM General Motors | MEDIUM 0.5259 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001390 | KG케미칼 | Automobiles | GM General Motors | MEDIUM 0.5527 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001420 | 태원물산 | Automobiles | F Ford Motor | MEDIUM 0.525 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001430 | 세아베스틸지주 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001440 | 대한전선 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001450 | 현대해상 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6494 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 001460 | BYC | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6273 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001465 | BYC우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6272 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001470 | 삼부토건 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 001500 | 현대차증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001510 | SK증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001515 | SK증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001520 | 동양 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001525 | 동양우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001527 | 동양2우B | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001530 | DI동일 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5711 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001540 | 안국약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001550 | 조비 | Specialty Chemicals | DOW Dow | MEDIUM 0.5644 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001560 | 제일연마 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5685 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001570 | 금양 | Specialty Chemicals | DOW Dow | MEDIUM 0.5939 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001620 | 케이비아이동국실업 | Automobiles | GM General Motors | MEDIUM 0.5366 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001630 | 종근당홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001680 | 대상 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6263 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001685 | 대상우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6249 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001720 | 신영증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001740 | SK네트웍스 | Investment Holding Companies | PUMP ProPetro Holding | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 001750 | 한양증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001755 | 한양증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001770 | SHD | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001780 | 알루코 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5636 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001790 | 대한제당 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6172 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001795 | 대한제당우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6172 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001800 | 오리온홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6482 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001810 | 무림SP | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001820 | 삼화콘덴서 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001840 | 이화공영 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001940 | KISCO홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002020 | 코오롱 | Investment Holding Companies | XPRO Expro Group Holdings N.V | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 002025 | 코오롱우 | Investment Holding Companies | XPRO Expro Group Holdings N.V | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 002030 | 아세아 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002070 | 비비안 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.559 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002100 | 경농 | Specialty Chemicals | DOW Dow | MEDIUM 0.5505 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002140 | 고려산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002150 | 도화엔지니어링 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002170 | SYTS | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6268 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002200 | 한국수출포장 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002210 | 동성제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002220 | 한일철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002230 | 피에스텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6278 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002240 | 고려제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002290 | 삼일기업공사 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002310 | 아세아제지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002320 | 한진 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6122 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002350 | 넥센타이어 | Automobiles | GM General Motors | MEDIUM 0.5268 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002355 | 넥센타이어1우B | Automobiles | GM General Motors | MEDIUM 0.5268 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002360 | SH에너지화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.6113 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002380 | KCC | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002390 | 한독 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002410 | 범양건영 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 002420 | 세기상사 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002450 | 삼익악기 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.574 | industry | not_low_confidence | us_market_relative_proxy |
| 002460 | HS화성 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002600 | 조흥 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6419 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002620 | 제일파마홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002630 | 오리엔트바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002680 | 한탑 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.65 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002690 | 동일제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002700 | 신일전자 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002710 | TCC스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002720 | 국제약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002760 | 보락 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.642 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002780 | 진흥기업 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002785 | 진흥기업우B | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002787 | 진흥기업2우B | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002790 | 아모레퍼시픽홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6199 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002795 | 아모레퍼시픽홀딩스우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6193 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002800 | 신신제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002810 | 삼영무역 | Specialty Chemicals | DOW Dow | MEDIUM 0.5578 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002820 | SUN&L | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002840 | 미원상사 | Specialty Chemicals | DOW Dow | MEDIUM 0.562 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002870 | 신풍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002880 | 디와이에이 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002900 | TYM | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002920 | 유성기업 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002960 | 한국쉘석유 | Specialty Chemicals | DOW Dow | MEDIUM 0.549 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002990 | 금호건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002995 | 금호건설우 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003000 | 부광약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003010 | 혜인 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003030 | 세아제강지주 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003060 | 에이프로젠바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 003070 | 코오롱글로벌 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003075 | 코오롱글로벌우 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003080 | SB성보 | Specialty Chemicals | DOW Dow | MEDIUM 0.5475 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003090 | 대웅 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003100 | 선광 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6221 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003120 | 일성아이에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003160 | 디아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003200 | 일신방직 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.63 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003220 | 대원제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003230 | 삼양식품 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6819 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003240 | 태광산업 | Specialty Chemicals | DOW Dow | MEDIUM 0.5475 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003280 | 흥아해운 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6411 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003300 | 한일홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003310 | 대주산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003350 | 한국화장품제조 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6415 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003380 | 하림지주 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6528 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003460 | 유화증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003465 | 유화증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003470 | 유안타증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003475 | 유안타증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003480 | 한진중공업홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003490 | 대한항공 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003495 | 대한항공우 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003520 | 영진약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003530 | 한화투자증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003535 | 한화투자증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003540 | 대신증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003545 | 대신증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003547 | 대신증권2우B | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003550 | LG | Investment Holding Companies | IESC IES Holdings | MEDIUM 0.631 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 003555 | LG우 | Investment Holding Companies | IESC IES Holdings | MEDIUM 0.6312 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 003570 | SNT다이내믹스 | Automobiles | GM General Motors | MEDIUM 0.5375 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003580 | HLB글로벌 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5899 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003610 | 방림 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6197 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003620 | KG모빌리티 | Automobiles | GM General Motors | MEDIUM 0.5698 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003650 | 미창석유 | Specialty Chemicals | DOW Dow | MEDIUM 0.5609 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003670 | 포스코퓨처엠 | Specialty Chemicals | DOW Dow | MEDIUM 0.636 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003680 | 한성기업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6519 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003690 | 코리안리 | Insurance | NP Neptune Insurance Holdings | MEDIUM 0.6239 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003720 | 삼영 | Specialty Chemicals | DOW Dow | MEDIUM 0.5645 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003780 | 진양산업 | Specialty Chemicals | DOW Dow | MEDIUM 0.5526 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003800 | 에이스침대 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003830 | 대한화섬 | Specialty Chemicals | DOW Dow | MEDIUM 0.556 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003850 | 보령 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003920 | 남양유업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6572 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003925 | 남양유업우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6572 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003960 | 사조대림 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6244 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004000 | 롯데정밀화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5634 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004020 | 현대제철 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004060 | SG세계물산 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5825 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004080 | 신흥 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004090 | 한국석유 | Specialty Chemicals | DOW Dow | MEDIUM 0.5623 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004100 | 태양금속 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004105 | 태양금속우 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004140 | 동방 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6067 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004150 | 한솔홀딩스 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5846 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004170 | 신세계 | Retail | WMT Walmart | MEDIUM 0.5206 | industry | not_low_confidence | us_market_relative_proxy |
| 004250 | NPC | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004255 | NPC우 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004270 | 남성 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5623 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004310 | 현대약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004360 | 세방 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5943 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004365 | 세방우 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5937 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004370 | 농심 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6797 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004380 | 삼익THK | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004410 | 서울식품 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6366 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004415 | 서울식품우 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.638 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004430 | 송원산업 | Specialty Chemicals | DOW Dow | MEDIUM 0.5572 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004440 | 삼일씨엔에스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004450 | 삼화왕관 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004490 | 세방전지 | Automobiles | TM Toyota Motor | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004540 | 깨끗한나라 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004545 | 깨끗한나라우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004560 | 현대비앤지스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004590 | 한국가구 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004650 | 창해에탄올 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004690 | 삼천리 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004700 | 조광피혁 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6195 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004710 | 한솔테크닉스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.573 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004720 | 팜젠사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 004770 | 써니전자 | Electrical Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004780 | 대륙제관 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004800 | 효성 | Investment Holding Companies | LNTH Lantheus Holdings | MEDIUM 0.6331 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 004830 | 덕성 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6285 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004835 | 덕성우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6285 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004840 | DRB동일 | Specialty Chemicals | DOW Dow | MEDIUM 0.5692 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004870 | 티웨이홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004890 | 동일산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004910 | 조광페인트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004920 | 씨아이테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004960 | 한신공영 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004970 | 신라교역 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6176 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004980 | 성신양회 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004985 | 성신양회우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004990 | 롯데지주 | Investment Holding Companies | IQV IQVIA Holdings | MEDIUM 0.5811 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005010 | 휴스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005030 | 부산주공 | Automobiles | GM General Motors | MEDIUM 0.5285 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005070 | 코스모신소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.5954 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005090 | SGC에너지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.603 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005110 | 한창 | Real Estate | CTRE CareTrust REIT | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005160 | 동국산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005180 | 빙그레 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6675 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005250 | 녹십자홀딩스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005257 | 녹십자홀딩스2우 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005290 | 동진쎄미켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005300 | 롯데칠성 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.644 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005305 | 롯데칠성우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6441 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005320 | 온타이드 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5658 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005360 | 모나미 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005380 | 현대차 | Automobiles | GM General Motors | MEDIUM 0.6543 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005385 | 현대차우 | Automobiles | GM General Motors | MEDIUM 0.6555 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005387 | 현대차2우B | Automobiles | GM General Motors | MEDIUM 0.6555 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005389 | 현대차3우B | Automobiles | GM General Motors | MEDIUM 0.6555 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005420 | 코스모화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5983 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005430 | 한국공항 | Electrical Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 005440 | 현대지에프홀딩스 | Investment Holding Companies | PUMP ProPetro Holding | MEDIUM 0.6229 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005490 | POSCO홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005500 | 삼진제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005610 | 삼립 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6703 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005670 | 푸드웰 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005680 | 삼영전자 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005690 | 파미셀 | Specialty Chemicals | DOW Dow | MEDIUM 0.5613 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005710 | 대원산업 | Automobiles | GM General Motors | MEDIUM 0.527 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005720 | 넥센 | Automobiles | GM General Motors | MEDIUM 0.5271 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005725 | 넥센우 | Automobiles | GM General Motors | MEDIUM 0.5271 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005740 | 크라운해태홀딩스 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6485 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005745 | 크라운해태홀딩스우 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6485 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005750 | 대림바스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 005800 | 신영와코루 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6292 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005810 | 풍산홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005820 | 원림 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005830 | DB손해보험 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6818 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005850 | 에스엘 | Automobiles | GM General Motors | MEDIUM 0.5358 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005860 | 한일사료 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6561 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005870 | 휴니드 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005880 | 대한해운 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005930 | 삼성전자 | Semiconductors | INTC Intel | MEDIUM 0.5356 | industry | not_low_confidence | partial_direct_similarity |
| 005935 | 삼성전자우 | Semiconductors | INTC Intel | MEDIUM 0.5393 | industry | not_low_confidence | partial_direct_similarity |
| 005940 | NH투자증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005945 | NH투자증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005950 | 이수화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.6056 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005960 | 동부건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 005965 | 동부건설우 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 005990 | 매일홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006040 | 동원산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006050 | 국영지앤엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006060 | 화승인더 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6305 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006090 | 사조오양 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6512 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006110 | 삼아알미늄 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006120 | SK디스커버리 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006125 | SK디스커버리우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006140 | 피제이전자 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006200 | 한국전자홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 006220 | 제주은행 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006260 | LS | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006280 | 녹십자 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 006340 | 대원전선 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006345 | 대원전선우 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006360 | GS건설 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006370 | 대구백화점 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 006380 | 카프로 | Specialty Chemicals | DOW Dow | MEDIUM 0.5939 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006400 | 삼성SDI | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5678 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006405 | 삼성SDI우 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5664 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006490 | 프리티 | Telecommunications | T AT&T | MEDIUM 0.5864 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006570 | 대림통상 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 006620 | 동구바이오제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006650 | 대한유화 | Specialty Chemicals | DOW Dow | MEDIUM 0.5532 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006660 | 삼성공조 | Automobiles | GM General Motors | MEDIUM 0.5282 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006730 | 서부T&D | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6061 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006740 | 블루산업개발 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 006800 | 미래에셋증권 | Banks | C Citigroup | MEDIUM 0.5424 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006805 | 미래에셋증권우 | Banks | C Citigroup | MEDIUM 0.5436 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006840 | AK홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5781 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006880 | 신송홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006890 | 태경케미컬 | Specialty Chemicals | DOW Dow | MEDIUM 0.5659 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006910 | 보성파워텍 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006920 | 모헨즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006980 | 우성 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6393 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007070 | GS리테일 | Retail | WMT Walmart | MEDIUM 0.532 | industry | not_low_confidence | us_market_relative_proxy |
| 007110 | 일신석재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007120 | 미래아이앤지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 007160 | 사조산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007210 | 벽산 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007280 | 한국특강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007310 | 오뚜기 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6649 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007330 | 푸른저축은행 | Banks | JPM JP Morgan Chase & | MEDIUM 0.5203 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007340 | DN오토모티브 | Automobiles | GM General Motors | MEDIUM 0.5426 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007370 | 진양제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 007390 | 네이처셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 007460 | 에이프로젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 007530 | 와이엠 | Automobiles | GM General Motors | MEDIUM 0.5344 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007540 | 샘표 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6415 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007570 | 일양약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 007575 | 일양약품우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 007590 | 동방아그로 | Specialty Chemicals | DOW Dow | MEDIUM 0.5605 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007610 | 선도전기 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 007660 | 이수페타시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 007680 | 대원 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007690 | 국도화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5707 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007700 | F&F홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6348 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007720 | 소노스퀘어 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5637 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007770 | 한일화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.6014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007810 | 코리아써키트 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5934 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007815 | 코리아써우 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 007820 | 엠엑스로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007860 | 서연 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007980 | TP | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6308 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008040 | 사조동아원 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6186 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008060 | 대덕 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5738 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008250 | 이건산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 008260 | NI스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008290 | 원풍물산 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 008350 | 남선알미늄 | Investment Holding Companies | FRHC Freedom Holding | MEDIUM 0.585 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008355 | 남선알미우 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 008370 | 원풍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5543 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008420 | 문배철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008470 | 부스타 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 008490 | 서흥 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 008600 | 윌비스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 008700 | 아남전자 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5372 | industry | not_low_confidence | not_available |
| 008730 | 율촌화학 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 008770 | 호텔신라 | Retail | WMT Walmart | MEDIUM 0.4922 | industry | not_low_confidence | partial_direct_similarity |
| 008775 | 호텔신라우 | Retail | WMT Walmart | MEDIUM 0.492 | industry | not_low_confidence | partial_direct_similarity |
| 008830 | 대동기어 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008870 | 금비 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 008930 | 한미사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 008970 | KBI동양철관 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009070 | KCTC | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5919 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009140 | 경인전자 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5471 | industry | not_low_confidence | us_market_relative_proxy |
| 009150 | 삼성전기 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 009155 | 삼성전기우 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 009160 | SIMPAC | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009180 | 한솔로지스틱스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6175 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009190 | 대양금속 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009200 | 무림페이퍼 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009240 | 한샘 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6382 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009270 | 신원 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6099 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009290 | 광동제약 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009300 | 삼아제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009310 | 참엔지니어링 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009320 | 아진전자부품 | Automobiles | GM General Motors | MEDIUM 0.5276 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009410 | 태영건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009415 | 태영건설우 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009420 | 한올바이오파마 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009440 | KC그린홀딩스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 009450 | 경동나비엔 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009460 | 한창제지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009470 | 삼화전기 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5678 | industry | not_low_confidence | us_market_relative_proxy |
| 009520 | 포스코엠텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009540 | HD한국조선해양 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009580 | 무림P&P | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009620 | 삼보산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009680 | 모토닉 | Automobiles | GM General Motors | MEDIUM 0.5281 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009730 | 이렘 | Investment Holding Companies | MARA MARA Holdings | MEDIUM 0.562 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009770 | 삼정펄프 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5842 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009780 | 엠에스씨 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6641 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009810 | 플레이그램 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.6211 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009830 | 한화솔루션 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5485 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009835 | 한화솔루션우 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5473 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009900 | 명신산업 | Automobiles | GM General Motors | MEDIUM 0.5312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009970 | 영원무역홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6332 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010040 | 한국내화 | Investment Holding Companies | QTWO Q2 Holdings | MEDIUM 0.5547 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010060 | OCI홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5869 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010100 | 한국무브넥스 | Automobiles | GM General Motors | MEDIUM 0.5361 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010120 | LS ELECTRIC | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010130 | 고려아연 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 010140 | 삼성중공업 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 010170 | 대한광통신 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 010240 | 흥국 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010280 | 아이티센엔텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 010400 | 우진아이엔에스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010470 | 오리콤 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.575 | industry | not_low_confidence | us_market_relative_proxy |
| 010580 | 에스엠벡셀 | Automobiles | GM General Motors | MEDIUM 0.5205 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010640 | 진양폴리 | Specialty Chemicals | DOW Dow | MEDIUM 0.556 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010660 | 화천기계 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010690 | 화신 | Automobiles | GM General Motors | MEDIUM 0.529 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010770 | 평화홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5229 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010780 | 아이에스동서 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 010820 | 퍼스텍 | Software | DAL Delta Air Lines | LOW 0.2652 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 010950 | S-Oil | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010955 | S-Oil우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010960 | 삼호개발 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011000 | 진원생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 011040 | 경동제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 011070 | LG이노텍 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.6537 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011080 | 형지I&C | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011090 | 에넥스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5986 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011150 | CJ씨푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6123 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011155 | CJ씨푸드1우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6123 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011170 | 롯데케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.6376 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011200 | HMM | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6874 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011210 | 현대위아 | Automobiles | GM General Motors | MEDIUM 0.5283 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011230 | 삼화전자 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011280 | 태림포장 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 011300 | 우성머티리얼스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011320 | 유니크 | Automobiles | GM General Motors | MEDIUM 0.5257 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011330 | 유니켐 | Automobiles | F Ford Motor | MEDIUM 0.5212 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011370 | 서한 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011390 | 부산산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011420 | 갤럭시아에스엠 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5734 | industry | not_low_confidence | us_market_relative_proxy |
| 011500 | 한농화성 | Specialty Chemicals | DOW Dow | MEDIUM 0.5647 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011560 | 세보엠이씨 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011690 | 와이투솔루션 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5258 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011700 | 한신기계 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 011760 | 현대코퍼레이션 | Retail | WMT Walmart | MEDIUM 0.5173 | industry | not_low_confidence | us_market_relative_proxy |
| 011780 | 금호석유화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5559 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011785 | 금호석유화학우 | Specialty Chemicals | DOW Dow | MEDIUM 0.5527 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011790 | SKC | Specialty Chemicals | DOW Dow | MEDIUM 0.5949 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011810 | STX | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 011930 | 신성이엔지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 012030 | DB | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012160 | 영흥 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012170 | 아센디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4606 | industry | not_low_confidence | us_market_relative_proxy |
| 012200 | 계양전기 | Automobiles | F Ford Motor | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012205 | 계양전기우 | Automobiles | F Ford Motor | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012210 | 삼미금속 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012280 | 영화금속 | Automobiles | GM General Motors | MEDIUM 0.5368 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012320 | 경동인베스트 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012330 | 현대모비스 | Automobiles | GM General Motors | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 012340 | 뉴인텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.561 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 012450 | 한화에어로스페이스 | Software | DAL Delta Air Lines | LOW 0.39 | generic_or_mismatch | domain_mismatch | direct_financial_similarity |
| 012510 | 더존비즈온 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012610 | 경인양행 | Specialty Chemicals | DOW Dow | MEDIUM 0.5577 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 012620 | 원일특강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012630 | HDC | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012690 | 모나리자 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6057 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012700 | 리드코프 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012750 | 에스원 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012790 | 신일제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012800 | 대창 | Investment Holding Companies | CELH Celsius Holdings | MEDIUM 0.5838 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012860 | 모베이스전자 | Automobiles | GM General Motors | MEDIUM 0.5335 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013000 | 세우글로벌 | Specialty Chemicals | DOW Dow | MEDIUM 0.5686 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013030 | 하이록코리아 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013120 | 동원개발 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013310 | 아진산업 | Automobiles | GM General Motors | MEDIUM 0.5272 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013360 | 일성건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013520 | 화승코퍼레이션 | Automobiles | GM General Motors | MEDIUM 0.5328 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013570 | 디와이 | Automobiles | GM General Motors | MEDIUM 0.5316 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013580 | 계룡건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013700 | 까뮤이앤씨 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013720 | 청보 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013810 | 스페코 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 013870 | 지엠비코리아 | Automobiles | GM General Motors | MEDIUM 0.534 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013890 | 지누스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5852 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013990 | 아가방컴퍼니 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6308 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014100 | 메디앙스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 014130 | 한익스프레스 | Logistics and Transportation | ULH Universal Logistics Holdings | MEDIUM 0.5671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014160 | 대영포장 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014190 | 원익큐브 | Specialty Chemicals | DOW Dow | MEDIUM 0.5585 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 014280 | 금강공업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014285 | 금강공업우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014440 | 영보화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5573 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 014470 | 부방 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014530 | 극동유화 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014570 | 고려제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014580 | 태경비케이 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5638 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014620 | 성광벤드 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014680 | 한솔케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.562 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 014710 | 사조씨푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6182 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 014790 | HL D&I | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014820 | 동원시스템즈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014825 | 동원시스템즈우 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014830 | 유니드 | Specialty Chemicals | DOW Dow | MEDIUM 0.548 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 014910 | 성문전자 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6292 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014915 | 성문전자우 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6292 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014940 | 오리엔탈정공 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014950 | 삼익제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 014970 | 삼륭물산 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014990 | 인디에프 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5868 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 015020 | 이스타코 | Real Estate | FVR FrontView REIT | MEDIUM 0.6255 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015230 | 대창단조 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015260 | 에이엔피 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5242 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 015360 | INVENI | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015590 | DKME | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 015710 | 코콤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 015750 | 성우하이텍 | Automobiles | GM General Motors | MEDIUM 0.529 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015760 | 한국전력 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015860 | 일진홀딩스 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015890 | 태경산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 016090 | 대현 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6353 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016100 | 리더스코스메틱 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 016250 | SGC E&C | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 016360 | 삼성증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016380 | KG스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 016450 | 한세예스24홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5759 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 016580 | 환인제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016590 | 신대양제지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016600 | 큐캐피탈 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 016610 | DB증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016670 | 디모아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016710 | 대성홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 016740 | 두올 | Automobiles | GM General Motors | MEDIUM 0.525 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016790 | 현대사료 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6549 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016800 | 퍼시스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6248 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016880 | 웅진 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5766 | industry | not_low_confidence | us_market_relative_proxy |
| 016920 | 카스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5365 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 017000 | 신원종합개발 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017040 | 광명전기 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 017180 | 명문제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 017250 | 인터엠 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5779 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017370 | 우신시스템 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017390 | 서울가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017480 | 삼현철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 017510 | 세명전기 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017550 | 수산세보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017650 | 대림제지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 017670 | SK텔레콤 | Telecommunications | VZ Verizon Communications | MEDIUM 0.6459 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 017800 | 현대엘리베이터 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017810 | 풀무원 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6613 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017860 | DS단석 | Specialty Chemicals | DOW Dow | MEDIUM 0.6079 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017890 | 한국알콜 | Specialty Chemicals | DOW Dow | MEDIUM 0.5604 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 017900 | 광전자 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5849 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017940 | E1 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017960 | 한국카본 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 018000 | 유니슨 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5499 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 018120 | 진로발효 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6717 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018250 | 애경산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 018260 | 삼성에스디에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 018290 | 브이티 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6355 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018310 | 삼목에스폼 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 018470 | 조일알미늄 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5744 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018500 | 동원금속 | Automobiles | GM General Motors | MEDIUM 0.5257 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018620 | 우진비앤지 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 018670 | SK가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 018680 | 서울제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 018700 | 졸스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 018880 | 한온시스템 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 019010 | 베뉴지 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5961 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019170 | 신풍제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 019175 | 신풍제약우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 019180 | 티에이치엔 | Automobiles | GM General Motors | MEDIUM 0.5282 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019210 | 와이지-원 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 019490 | 엑시큐어하이트론 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 019540 | 일지테크 | Automobiles | GM General Motors | MEDIUM 0.5282 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019550 | SBI인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 019570 | 플루토스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 019660 | 글로본 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.6014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019680 | 대교 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 019685 | 대교우B | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 019770 | 서연탑메탈 | Automobiles | GM General Motors | MEDIUM 0.5335 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019990 | 에너토크 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 020000 | 한섬 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6475 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020120 | 키다리스튜디오 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 020150 | 롯데에너지머티리얼즈 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5281 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 020180 | 대신정보통신 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 020400 | 대동금속 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 020560 | 아시아나항공 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 020710 | 시공테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 020760 | 일진디스플 | Consumer Electronics and Appliances | SONY Sony Group | MEDIUM 0.5505 | industry | not_low_confidence | partial_direct_similarity |
| 021040 | 대호특수강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 021045 | 대호특수강우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 021050 | 서원 | Investment Holding Companies | NVST Envista Holdings | MEDIUM 0.5419 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021080 | 에이티넘인베스트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 021240 | 코웨이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 021320 | KCC건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 021650 | 한국큐빅 | Automobiles | GM General Motors | MEDIUM 0.5317 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021820 | 세원정공 | Automobiles | GM General Motors | MEDIUM 0.5318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021880 | 메이슨캐피탈 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 022100 | 포스코DX | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 022220 | 티케이지애강 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 023000 | 삼원강재 | Automobiles | GM General Motors | MEDIUM 0.5327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023150 | MH에탄올 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6216 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023160 | 태광 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023350 | 한국종합기술 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023410 | 유진기업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 023440 | 제이스코홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023450 | 동남합성 | Specialty Chemicals | DOW Dow | MEDIUM 0.5623 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023530 | 롯데쇼핑 | Retail | WMT Walmart | MEDIUM 0.5304 | industry | not_low_confidence | us_market_relative_proxy |
| 023590 | 다우기술 | Banks | C Citigroup | MEDIUM 0.5453 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023600 | 삼보판지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 023760 | 한국캐피탈 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023770 | 플레이위드 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023790 | 동일스틸럭스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023800 | 인지컨트롤스 | Automobiles | GM General Motors | MEDIUM 0.5257 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023810 | 인팩 | Automobiles | GM General Motors | MEDIUM 0.5301 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023900 | 풍국주정 | Specialty Chemicals | DOW Dow | MEDIUM 0.5565 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023910 | 대한약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 023960 | 에쓰씨엔지니어링 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 024060 | 흥구석유 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 024070 | WISCOM | Specialty Chemicals | DOW Dow | MEDIUM 0.5644 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 024090 | 디씨엠 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5834 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024110 | 기업은행 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 024120 | KB오토시스 | Automobiles | GM General Motors | MEDIUM 0.5344 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024720 | 콜마홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024740 | 한일단조 | Automobiles | GM General Motors | MEDIUM 0.528 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024800 | 유성티엔에스 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6285 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024830 | 세원물산 | Automobiles | GM General Motors | MEDIUM 0.524 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024840 | KBI메탈 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 024850 | HLB이노베이션 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 024880 | 케이피에프 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 024890 | 대원화성 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6136 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024900 | 디와이덕양 | Automobiles | GM General Motors | MEDIUM 0.522 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024910 | 경창산업 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 024940 | PN풍년 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 024950 | 삼천리자전거 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5648 | industry | not_low_confidence | us_market_relative_proxy |
| 025000 | KPX케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.5681 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025320 | 시노펙스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 025440 | DH오토웨어 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025530 | SJM홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5332 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025540 | 한국단자 | Automobiles | GM General Motors | MEDIUM 0.5246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025550 | 한국선재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025560 | 미래산업 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 025620 | 차AI헬스케어 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 025750 | 한솔홈데코 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025770 | 한국정보통신 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 025820 | 이구산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 025860 | 남해화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5643 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025870 | 신라에스지 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.64 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025880 | 케이씨피드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6545 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025890 | 한국주강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 025900 | 동화기업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 025950 | 동신건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025980 | 아난티 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.57 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 026040 | 제이에스티나 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6218 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026150 | 특수건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 026890 | 스틱인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 026910 | 광진실업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 026940 | 부국철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 026960 | 동서 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6586 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027040 | 서울전자통신 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5271 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 027050 | 코리아나 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5412 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 027360 | 아주IB투자 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 027410 | BGF | Specialty Chemicals | DOW Dow | MEDIUM 0.5623 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 027580 | 상보 | Specialty Chemicals | DOW Dow | MEDIUM 0.5914 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027710 | 팜스토리 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6624 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027740 | 마니커 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6228 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 027830 | 대성창투 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 027970 | 한국제지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 028050 | 삼성E&A | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 028080 | 휴맥스홀딩스 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 028100 | 동아지질 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 028260 | 삼성물산 | Investment Holding Companies | IQV IQVIA Holdings | MEDIUM 0.6789 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 028300 | HLB | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 028670 | 팬오션 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6436 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029460 | 케이씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 029480 | 광무 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 029530 | 신도리코 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.56 | industry | not_low_confidence | us_market_relative_proxy |
| 029780 | 삼성카드 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 030000 | 제일기획 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5742 | industry | not_low_confidence | us_market_relative_proxy |
| 030190 | NICE평가정보 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 030200 | KT | Telecommunications | T AT&T | MEDIUM 0.634 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030210 | 다올투자증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030350 | 드래곤플라이 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 030520 | 한글과컴퓨터 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 030530 | 원익홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 030610 | 교보증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030720 | 동원수산 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6549 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030960 | 양지사 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 031210 | 서울보증보험 | Insurance | NP Neptune Insurance Holdings | MEDIUM 0.655 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 031310 | 아이즈비전 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 031330 | 에스에이엠티 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5935 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031430 | 신세계인터내셔날 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5975 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 031440 | 신세계푸드 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5833 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031510 | 오스템 | Automobiles | GM General Motors | MEDIUM 0.5374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031820 | 아이티센씨티에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 031860 | 디에이치엑스컴퍼니 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 031980 | 피에스케이홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032080 | 아즈텍WB | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.615 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032190 | 다우데이타 | Banks | C Citigroup | MEDIUM 0.5212 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 032280 | 삼일 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6004 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032300 | 한국파마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032350 | 롯데관광개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6092 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032500 | 케이엠더블유 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032540 | TJ미디어 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5461 | industry | not_low_confidence | us_market_relative_proxy |
| 032560 | 황금에스티 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5609 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032580 | 피델릭스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032620 | GC메디아이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 032640 | LG유플러스 | Telecommunications | T AT&T | MEDIUM 0.6362 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032680 | 소프트센 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032685 | 소프트센우 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032750 | 삼진 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5477 | industry | not_low_confidence | us_market_relative_proxy |
| 032790 | 엠젠솔루션 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 032800 | 판타지오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 032820 | 우리기술 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032830 | 삼성생명 | Insurance | NP Neptune Insurance Holdings | MEDIUM 0.593 | industry_and_business_model | not_low_confidence | not_available |
| 032850 | 비트컴퓨터 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4841 | industry | not_low_confidence | us_market_relative_proxy |
| 032860 | 더라미 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5946 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032940 | 원익 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6385 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032960 | 동일기연 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5701 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033050 | 제이엠아이 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6128 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033100 | 제룡전기 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 033130 | 디지틀조선 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033160 | 엠케이전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033170 | 시그네틱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033200 | 모아텍 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5262 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 033230 | 인성정보 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033240 | 자화전자 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033250 | 체시스 | Automobiles | GM General Motors | MEDIUM 0.5271 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033270 | 유나이티드제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033290 | 로젠 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6032 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033310 | 엠투엔 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 033320 | 제이씨현시스템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033340 | 좋은사람들 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 033500 | 동성화인텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5686 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 033530 | SJG세종 | Automobiles | GM General Motors | MEDIUM 0.5267 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033540 | 파라텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 033560 | 블루콤 | Real Estate | WPC W. P. Carey . REIT | MEDIUM 0.6486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033640 | 네패스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033780 | KT&G | Food and Beverage | MNST Monster Beverage | MEDIUM 0.7106 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 033790 | 피노 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6013 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 033830 | 티비씨 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5301 | industry | not_low_confidence | us_market_relative_proxy |
| 033920 | 무학 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034020 | 두산에너빌리티 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 034120 | SBS | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5332 | industry | not_low_confidence | us_market_relative_proxy |
| 034220 | LG디스플레이 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5505 | industry | not_low_confidence | us_market_relative_proxy |
| 034230 | 파라다이스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6096 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034310 | NICE | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 034590 | 인천도시가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 034730 | SK | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 034810 | 해성산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 034830 | 한국토지신탁 | Real Estate | CTRE CareTrust REIT | MEDIUM 0.6473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034940 | 조아제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 034950 | 한국기업평가 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035000 | HS애드 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5755 | industry | not_low_confidence | us_market_relative_proxy |
| 035080 | 그래디언트 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 035150 | 백산 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6362 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035200 | 프럼파스트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 035250 | 강원랜드 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.6479 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 035290 | 골드앤에스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 035420 | NAVER | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035460 | 기산텔레콤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035510 | 신세계 I&C | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035600 | KG이니시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035610 | 솔본 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4886 | industry | not_low_confidence | us_market_relative_proxy |
| 035620 | 바른손이앤에이 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 035720 | 카카오 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035760 | CJ ENM | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5274 | industry | not_low_confidence | us_market_relative_proxy |
| 035810 | 이지홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035890 | 서희건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 035900 | JYP Ent. | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5362 | industry | not_low_confidence | us_market_relative_proxy |
| 036000 | 예림당 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5387 | industry | not_low_confidence | partial_direct_similarity |
| 036010 | 아비코전자 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6328 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036030 | 케이티알파 | Retail | WMT Walmart | MEDIUM 0.5389 | industry | not_low_confidence | us_market_relative_proxy |
| 036090 | 위지트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036120 | 서울평가정보 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 036170 | 에이치엠넥스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036190 | 금화피에스시 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036200 | 유니셈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036220 | 오상헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 036420 | 콘텐트리중앙 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.486 | industry | not_low_confidence | partial_direct_similarity |
| 036460 | 한국가스공사 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036480 | 대성미생물 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 036530 | SNT홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5385 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036540 | SFA반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036560 | KZ정밀 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036570 | NC | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036580 | 팜스코 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6557 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036620 | 감성코퍼레이션 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036630 | 세종텔레콤 | Telecommunications | T AT&T | MEDIUM 0.5857 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036640 | HRS | Specialty Chemicals | DOW Dow | MEDIUM 0.5549 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036670 | 삼양케이씨아이 | Specialty Chemicals | DOW Dow | MEDIUM 0.5636 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036690 | 코맥스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 036710 | 심텍홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036800 | 나이스정보통신 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 036810 | 에프에스티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036830 | 솔브레인홀딩스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6347 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036890 | 진성티이씨 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036930 | 주성엔지니어링 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 037030 | 파워넷 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6307 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037070 | 파세코 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037230 | 한국팩키지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037270 | YG PLUS | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5207 | industry | not_low_confidence | us_market_relative_proxy |
| 037330 | 인지디스플레 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 037350 | 성도이엔지 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037370 | EG | Investment Holding Companies | MARA MARA Holdings | MEDIUM 0.5646 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037400 | 우리엔터프라이즈 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 037440 | 희림 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037460 | 삼지전자 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037560 | LG헬로비전 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.53 | industry | not_low_confidence | us_market_relative_proxy |
| 037710 | 광주신세계 | Retail | WMT Walmart | MEDIUM 0.5263 | industry | not_low_confidence | us_market_relative_proxy |
| 037760 | 쎄니트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037950 | 엘컴텍 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5664 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038010 | 제일테크노스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038060 | 루멘스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 038070 | 서린바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038110 | 에코플라스틱 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038290 | 마크로젠 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 038390 | 레드캡투어 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 038460 | 바이오스마트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038500 | 삼표시멘트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 038530 | 케이바이오랩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 038540 | 상상인 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 038620 | 위즈코프 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6101 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038680 | 에스넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038870 | 에코심플렉스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5546 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 038880 | 아이에이 | Automobiles | F Ford Motor | MEDIUM 0.5207 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038950 | 파인디지털 | Consumer Electronics and Appliances | SONY Sony Group | MEDIUM 0.5544 | industry | not_low_confidence | partial_direct_similarity |
| 039010 | 현대에이치티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039020 | 이건홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 039030 | 이오테크닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039130 | 하나투어 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039200 | 오스코텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039240 | 경남스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 039290 | 인포뱅크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039310 | 세중 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039340 | 한국경제TV | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4926 | industry | not_low_confidence | partial_direct_similarity |
| 039420 | 케이엘넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039440 | 에스티아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039490 | 키움증권 | Banks | C Citigroup | MEDIUM 0.543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039560 | 다산네트웍스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039570 | HDC랩스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 039610 | 화성밸브 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 039740 | 한국정보공학 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039830 | 오로라 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5665 | industry | not_low_confidence | us_market_relative_proxy |
| 039840 | 디오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039860 | 나노엔텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039980 | 폴라리스AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 040160 | 누리플렉스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 040300 | YTN | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 040350 | 크레오에스지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 040420 | 정상제이엘에스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 040610 | SG&G | Automobiles | GM General Motors | MEDIUM 0.5396 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 040910 | 아이씨디 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 041020 | 폴라리스오피스 | Automobiles | GM General Motors | MEDIUM 0.5256 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041190 | 우리기술투자 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 041440 | 현대에버다임 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 041460 | 한국전자인증 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041510 | 에스엠 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5296 | industry | not_low_confidence | us_market_relative_proxy |
| 041520 | 이엘씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041590 | 플래스크 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 041650 | 상신브레이크 | Automobiles | F Ford Motor | MEDIUM 0.5243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041830 | 인바디 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041910 | 폴라리스AI파마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041920 | 메디아나 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041930 | SY동아 | Automobiles | GM General Motors | MEDIUM 0.5361 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041960 | 코미팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 042000 | 카페24 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042040 | 케이피엠테크 | Specialty Chemicals | DOW Dow | MEDIUM 0.5877 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042110 | 에스씨디 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042370 | 비츠로테크 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6354 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042420 | 네오위즈홀딩스 | Interactive Entertainment | GME GameStop | MEDIUM 0.5497 | industry | not_low_confidence | us_market_relative_proxy |
| 042500 | 링네트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042510 | 라온시큐어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042520 | 한스바이오메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 042600 | 새로닉스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 042660 | 한화오션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042700 | 한미반도체 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 042940 | 상지건설 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 043090 | 더테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 043100 | 알파AI | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 043150 | 바텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 043200 | 파루 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5503 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 043220 | 티에스넥스젠 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 043260 | 성호전자 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043340 | 에쎈테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 043360 | 디지아이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 043370 | 피에이치에이 | Automobiles | GM General Motors | MEDIUM 0.5248 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043590 | 웰킵스하이텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5639 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 043610 | KT지니뮤직 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4968 | industry | not_low_confidence | partial_direct_similarity |
| 043650 | 국순당 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6116 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 043710 | 코스리거글로벌 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 043910 | 자연과환경 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 044180 | KD | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 044340 | 위닉스 | Software | UAL United Airlines Holdings | LOW 0.1362 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 044380 | 주연테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 044450 | KSS해운 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6491 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044480 | 빌리언스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 044490 | 태웅 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6361 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044780 | 에이치케이 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 044820 | 코스맥스비티아이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 044960 | 이글벳 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 044990 | 에이치엔에스하이텍 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5823 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045060 | 오공 | Specialty Chemicals | DOW Dow | MEDIUM 0.562 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 045100 | 한양이엔지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 045300 | 성우테크론 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 045340 | 토탈소프트 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6319 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045390 | 대아티아이 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6568 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045510 | 정원엔시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 045520 | 크린앤사이언스 | Specialty Chemicals | DOW Dow | MEDIUM 0.6025 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045660 | 에이텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 045970 | 코아시아 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046070 | 코다코 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 046120 | 오르비텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5819 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 046210 | HLB파나진 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046310 | 백금T&A | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 046390 | 삼화네트웍스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046440 | KG파이낸셜 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 046890 | 서울반도체 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046940 | 우원개발 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 046970 | 우리로 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 047040 | 대우건설 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 047050 | 포스코인터내셔널 | Retail | WMT Walmart | MEDIUM 0.5237 | industry | not_low_confidence | us_market_relative_proxy |
| 047080 | 한빛소프트 | Interactive Entertainment | GME GameStop | MEDIUM 0.5672 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047310 | 파워로직스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 047400 | 유니온머티리얼 | Automobiles | GM General Motors | MEDIUM 0.5358 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047560 | 이스트소프트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 047770 | 코데즈컴바인 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6141 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047810 | 한국항공우주 | Software | DAL Delta Air Lines | LOW 0.3617 | generic_or_mismatch | domain_mismatch | direct_financial_similarity |
| 047820 | 초록뱀미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5367 | industry | not_low_confidence | us_market_relative_proxy |
| 047920 | HLB제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 048410 | 현대바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 048430 | 유라테크 | Automobiles | GM General Motors | MEDIUM 0.5259 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048470 | 대동스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 048530 | 인트론바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 048550 | SM C&C | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5043 | industry | not_low_confidence | partial_direct_similarity |
| 048770 | TPC로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 048830 | 엔피케이 | Specialty Chemicals | DOW Dow | MEDIUM 0.5626 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 048870 | 시너지이노베이션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 048910 | 대원미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5397 | industry | not_low_confidence | us_market_relative_proxy |
| 049070 | 인탑스 | Semiconductors | INTC Intel | MEDIUM 0.4806 | industry | not_low_confidence | us_market_relative_proxy |
| 049080 | 기가레인 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 049120 | 파인디앤씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049180 | 셀루메드 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 049430 | 코메론 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 049470 | 비트플래닛 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 049480 | 오픈베이스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 049520 | 유아이엘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049550 | 잉크테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 049630 | 재영솔루텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049720 | 고려신용정보 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 049800 | 우진플라임 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 049830 | 승일 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 049950 | 미래컴퍼니 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049960 | 쎌바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 050090 | 비케이홀딩스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4944 | industry | not_low_confidence | us_market_relative_proxy |
| 050110 | 캠시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 050120 | ES큐브 | Hotels, Restaurants, and Leisure | PK Park Hotels & Resorts | MEDIUM 0.5489 | industry | not_low_confidence | us_market_relative_proxy |
| 050760 | 에스폴리텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5952 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050860 | 아세아텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 050890 | 쏠리드 | Software | UAL United Airlines Holdings | LOW 0.2356 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 050960 | 수산아이앤티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 051160 | 지어소프트 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5211 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051360 | 토비스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 051370 | 인터플렉스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5789 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051380 | 피씨디렉트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 051390 | YW | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051490 | 나라엠앤디 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 051500 | CJ프레시웨이 | Biotechnology | BIIB Biogen | MEDIUM 0.4944 | industry | not_low_confidence | us_market_relative_proxy |
| 051600 | 한전KPS | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 051630 | 진양화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5631 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051780 | 큐로홀딩스 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6303 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051900 | LG생활건강 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6395 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051905 | LG생활건강우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6379 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051910 | LG화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.6725 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 051915 | LG화학우 | Specialty Chemicals | DOW Dow | MEDIUM 0.6708 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 051980 | 중앙첨단소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 052020 | 에스티큐브 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5763 | industry_and_business_model | not_low_confidence | not_available |
| 052220 | iMBC | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052260 | 현대바이오랜드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052300 | 오션인더블유 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 052330 | 코텍 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5519 | industry | not_low_confidence | us_market_relative_proxy |
| 052400 | 코나아이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052420 | 오성첨단소재 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052460 | 아이크래프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052600 | 한네트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052690 | 한전기술 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 052710 | 아모텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052770 | 아이톡시 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 052790 | 액토즈소프트 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5538 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052860 | 아이앤씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052900 | KX하이텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052960 | 태양3C | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 053030 | 바이넥스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053050 | 지에스이 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053060 | 세동 | Automobiles | GM General Motors | MEDIUM 0.5336 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053080 | 케이엔솔 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 053160 | 프리엠스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053210 | 스카이라이프 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5346 | industry | not_low_confidence | us_market_relative_proxy |
| 053260 | 금강철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 053270 | 구영테크 | Automobiles | GM General Motors | MEDIUM 0.5275 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053280 | 예스24 | Retail | WMT Walmart | MEDIUM 0.4973 | industry | not_low_confidence | partial_direct_similarity |
| 053290 | NE능률 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 053300 | 한국정보인증 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 053350 | 이니텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053450 | 세코닉스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5695 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053580 | 웹케시 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 053610 | 프로텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053620 | 태양 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6244 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053690 | 한미글로벌 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053700 | 삼보모터스 | Automobiles | GM General Motors | MEDIUM 0.5425 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053800 | 안랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 053950 | 경남제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053980 | 오상자이엘 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054040 | 한국컴퓨터 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054050 | NH농우바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054090 | 삼진엘앤디 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5263 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 054180 | 메디콕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 054210 | 이랜텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054220 | 비츠로시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054300 | 팬스타엔터프라이즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5108 | industry | not_low_confidence | partial_direct_similarity |
| 054410 | 케이피티유 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5785 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054450 | 텔레칩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054540 | 삼영엠텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054620 | APS | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054670 | 대한뉴팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054780 | 키이스트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054800 | 아이디스홀딩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054920 | 한컴위드 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5557 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054930 | 유신 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 054940 | 엑사이엔씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054950 | 제이브이엠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 055490 | 테이팩스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5791 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 055550 | 신한지주 | Banks | C Citigroup | MEDIUM 0.534 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 056080 | 유진로봇 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 056090 | 시지메드텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 056190 | SFA | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 056360 | 코위버 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 056700 | 신화인터텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 056730 | CNT85 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 057030 | YBM넷 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 057050 | 현대홈쇼핑 | Retail | WMT Walmart | MEDIUM 0.5404 | industry | not_low_confidence | us_market_relative_proxy |
| 057540 | 옴니시스템 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5238 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 057680 | 티사이언티픽 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058110 | 멕아이씨에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058400 | KNN | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5291 | industry | not_low_confidence | us_market_relative_proxy |
| 058430 | 포스코스틸리온 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 058450 | 한주에이알티 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 058470 | 리노공업 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058610 | 에스피지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058630 | 엠게임 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058650 | 세아홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 058730 | 다스코 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 058820 | CMG제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058850 | KTcs | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 058860 | KTis | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 058970 | 엠로 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 059090 | 미코 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 059100 | 아이컴포넌트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 059120 | 아진엑스텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 059180 | 엔더블유시 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 059210 | 메타바이오메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 059270 | 해성에어로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060150 | 인선이엔티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 060230 | 제이케이시냅스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5284 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 060240 | 스타코링크 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 060250 | NHN KCP | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060260 | 뉴보텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 060280 | 큐렉소 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060310 | 3S | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060370 | LS마린솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060380 | 동양에스텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060480 | 국일신동 | Investment Holding Companies | FRHC Freedom Holding | MEDIUM 0.5798 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060540 | 에스에이티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 060560 | HC홈센타 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 060570 | 드림어스컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5087 | industry | not_low_confidence | us_market_relative_proxy |
| 060590 | 씨티씨바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060720 | KH바텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 060850 | 영림원소프트랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060900 | 에이전트AI | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060980 | HL홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5315 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 061040 | 알에프텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 061090 | 세나테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 061250 | 화일약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 061970 | LB세미콘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 062040 | 산일전기 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 062970 | 한국첨단소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 063080 | 컴투스홀딩스 | Interactive Entertainment | GAME GameSquare Holdings | MEDIUM 0.5555 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 063160 | 종근당바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 063170 | 서울옥션 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5996 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063440 | SM Life Design | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5285 | industry | not_low_confidence | us_market_relative_proxy |
| 063570 | NICE인프라 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 063760 | 이엘피 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064090 | 인크레더블버즈 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.588 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064240 | 홈캐스트 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064260 | 다날 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064290 | 인텍플러스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064350 | 현대로템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064400 | LG씨엔에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064480 | 브리지텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064520 | 테크엘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064550 | 바이오니아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064760 | 티씨케이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064800 | 포니링크 | Retail | WMT Walmart | MEDIUM 0.4881 | industry | not_low_confidence | partial_direct_similarity |
| 064820 | 케이프 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064850 | 에프앤가이드 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064960 | SNT모티브 | Automobiles | GM General Motors | MEDIUM 0.5434 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065060 | 지엔코 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5605 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 065130 | 탑엔지니어링 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065150 | 대산F&B | Food and Beverage | MNST Monster Beverage | MEDIUM 0.649 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065170 | 비엘팜텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 065350 | 신성델타테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 065370 | 위세아이텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 065420 | 에스아이리소스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 065440 | 이루온 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 065450 | 빅텍 | Software | DAL Delta Air Lines | LOW 0.2624 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 065500 | 오리엔트정공 | Automobiles | GM General Motors | MEDIUM 0.5286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065510 | 휴비츠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065530 | 와이어블 | Telecommunications | T AT&T | MEDIUM 0.6381 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065570 | 삼영이엔씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065650 | 하이퍼코퍼레이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065660 | 안트로젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065680 | 우주일렉트로 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065690 | 파커스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065710 | 서호전기 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6361 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065770 | CS | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065950 | 웰크론 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 066130 | 하츠 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 066310 | 큐에스아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 066360 | 체리부로 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.651 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066410 | 버킷스튜디오 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 066430 | 아이로보틱스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5618 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 066570 | LG전자 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5402 | industry | not_low_confidence | us_market_relative_proxy |
| 066575 | LG전자우 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5392 | industry | not_low_confidence | us_market_relative_proxy |
| 066590 | 스모트로닉 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 066620 | 국보디자인 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 066670 | 디티씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 066700 | 테라젠이텍스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 066790 | 씨씨에스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 066830 | 제노텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5619 | industry_and_business_model | not_low_confidence | not_available |
| 066900 | 디에이피 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 066910 | 손오공 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5147 | industry | not_low_confidence | partial_direct_similarity |
| 066970 | 엘앤에프 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5621 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 066980 | 한성크린텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 067000 | 조이시티 | Interactive Entertainment | GME GameStop | MEDIUM 0.5437 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 067010 | 이씨에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 067080 | 대화제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067160 | SOOP | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067170 | 오텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 067280 | 멀티캠퍼스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 067290 | JW신약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067310 | 하나마이크론 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 067370 | 선바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067390 | 아스트 | Software | DAL Delta Air Lines | LOW 0.215 | generic_or_mismatch | domain_mismatch | partial_direct_similarity |
| 067570 | 엔브이에이치코리아 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067630 | HLB생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 067730 | 로지시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067770 | 세진티에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067830 | 세이브존I&C | Retail | WMT Walmart | MEDIUM 0.533 | industry | not_low_confidence | us_market_relative_proxy |
| 067900 | 와이엔텍 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067920 | 이글루 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067990 | 도이치모터스 | Automobiles | GM General Motors | MEDIUM 0.5643 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068050 | 팬엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 068100 | 케이웨더 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 068240 | 다원시스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 068270 | 셀트리온 | Biotechnology | BIIB Biogen | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 068290 | 삼성출판사 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.533 | industry | not_low_confidence | partial_direct_similarity |
| 068330 | 일신바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.4861 | industry | not_low_confidence | us_market_relative_proxy |
| 068760 | 셀트리온제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 068790 | DMS | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 068930 | 디지털대성 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 068940 | 셀피글로벌 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 069080 | 웹젠 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5894 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069140 | 누리플랜 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 069260 | TKG휴켐스 | Specialty Chemicals | DOW Dow | MEDIUM 0.555 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 069330 | 유아이디 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 069410 | 엔텔스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 069460 | 대호에이엘 | Investment Holding Companies | QTWO Q2 Holdings | MEDIUM 0.5608 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069510 | 에스텍 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5746 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069540 | 빛과전자 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 069620 | 대웅제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 069640 | 한세엠케이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 069730 | DSR제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 069920 | 엑시온그룹 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 069960 | 현대백화점 | Retail | WMT Walmart | MEDIUM 0.5365 | industry | not_low_confidence | us_market_relative_proxy |
| 070300 | 엑스큐어 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 070590 | 인티큐브 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 070960 | 모나용평 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5731 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071050 | 한국금융지주 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071055 | 한국금융지주우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071090 | 하이스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 071200 | 인피니트헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 071280 | 로체시스템즈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 071320 | 지역난방공사 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 071670 | 에이테크솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 071840 | 롯데하이마트 | Retail | WMT Walmart | MEDIUM 0.5054 | industry | not_low_confidence | partial_direct_similarity |
| 071850 | 캐스텍코리아 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071950 | 코아스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 071970 | HD현대마린엔진 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 072020 | 중앙백신 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 072130 | 유엔젤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 072470 | 우리산업홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5227 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072710 | 농심홀딩스 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6791 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072770 | 멤레이비티 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 072870 | 메가스터디 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 072950 | 빛샘전자 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5848 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072990 | 에이치시티 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.577 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073010 | 케이에스피 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 073110 | 엘엠에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 073190 | 듀오백 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 073240 | 금호타이어 | Automobiles | GM General Motors | MEDIUM 0.5338 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073490 | LIG아큐버 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 073540 | 에프알텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 073560 | 우리손에프앤지 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6484 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073570 | 리튬포어스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 073640 | 테라사이언스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 074430 | 아미노로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 074600 | 원익QnC | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 074610 | 이엔플러스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 075130 | 플랜티넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 075180 | 새론오토모티브 | Automobiles | F Ford Motor | MEDIUM 0.5237 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 075580 | 세진중공업 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 075970 | 동국알앤에스 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 076080 | 웰크론한텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 076340 | 지에이이노더스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 076610 | 해성옵틱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 077360 | 덕산하이메탈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 077500 | 유니퀘스트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 077970 | STX엔진 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078000 | 텔코웨어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078020 | LS증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078070 | 유비쿼스홀딩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078130 | 국일제지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 078140 | 대봉엘에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078150 | HB테크놀러지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 078160 | 메디포스트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 078340 | 컴투스 | Interactive Entertainment | GME GameStop | MEDIUM 0.5684 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078350 | 한양디지텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 078520 | 에이블씨엔씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6369 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078590 | 휴림에이텍 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 078600 | 대주전자재료 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5712 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078860 | 아이오케이이엔엠 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 078890 | 가온그룹 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5456 | industry | not_low_confidence | us_market_relative_proxy |
| 078930 | GS | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 078935 | GS우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079000 | 와토스코리아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 079160 | CJ CGV | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4936 | industry | not_low_confidence | partial_direct_similarity |
| 079170 | 한창산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079190 | 케스피온 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 079370 | 제우스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 079430 | 현대리바트 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6294 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079550 | LIG디펜스앤에어로스페이스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 079650 | 서산 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079810 | APS이노베이션 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6323 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079900 | 전진건설로봇 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079940 | 가비아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 079950 | 인베니아 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 079960 | 동양이엔피 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6405 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079970 | 투비소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 079980 | 휴비스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6313 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080010 | 이상네트웍스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 080160 | 모두투어 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.607 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080220 | 제주반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 080420 | 모다이노칩 | Retail | WMT Walmart | MEDIUM 0.5039 | industry | not_low_confidence | partial_direct_similarity |
| 080470 | 성창오토텍 | Automobiles | GM General Motors | MEDIUM 0.5377 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080520 | 오디텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 080530 | 코디 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6084 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080580 | 오킨스전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 080720 | 한국유니온제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 081000 | 일진다이아 | Investment Holding Companies | FRHC Freedom Holding | MEDIUM 0.5827 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 081150 | 티플랙스 | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5712 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 081180 | 쎄크 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5337 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 081580 | 성우전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 081660 | 미스토홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6416 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 082210 | 옵트론텍 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5248 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 082270 | 젬백스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 082640 | 동양생명 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6346 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 082660 | 코스나인 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 082740 | 한화엔진 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 082800 | 비보존 제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 082850 | 우리바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 082920 | 비츠로셀 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083310 | 엘오티베큠 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083420 | 그린케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.5828 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 083450 | GST | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083470 | 이엠앤아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083500 | 에프엔에스테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083550 | 케이엠 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.594 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 083640 | 인콘 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.544 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 083650 | 비에이치아이 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6332 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083660 | CSA 코스믹 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 083790 | CG인바이츠 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 083930 | 아바코 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084010 | 대한제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 084110 | 휴온스글로벌 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 084180 | 수성웹툰 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5713 | industry | not_low_confidence | us_market_relative_proxy |
| 084370 | 유진테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 084440 | 유비온 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 084650 | 랩지노믹스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 084670 | 동양고속 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6434 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084680 | 이월드 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5496 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 084690 | 대상홀딩스 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.594 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 084695 | 대상홀딩스우 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.594 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 084730 | 팅크웨어 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5224 | industry | not_low_confidence | partial_direct_similarity |
| 084850 | 아이티엠반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 084870 | TBH글로벌 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6361 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084990 | 헬릭스미스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 085310 | 엔케이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 085620 | 미래에셋생명 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6204 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 085660 | 차바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 085670 | 뉴프렉스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5846 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085810 | 알티캐스트 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 085910 | 네오티스 | Automobiles | GM General Motors | MEDIUM 0.5449 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086040 | 바이오톡스텍 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086060 | 진바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086220 | 광동헬스바이오 | Food and Beverage | TSN Tyson Foods | MEDIUM 0.6303 | industry | not_low_confidence | partial_direct_similarity |
| 086280 | 현대글로비스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6633 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 086390 | 유니테스트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086450 | 동국제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086520 | 에코프로 | Specialty Chemicals | DOW Dow | MEDIUM 0.6591 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 086670 | 비엠티 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 086710 | 선진뷰티사이언스 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6117 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086790 | 하나금융지주 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 086820 | 바이오솔루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086890 | 이수앱지스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086900 | 메디톡스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086960 | MDS테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086980 | 쇼박스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 087010 | 펩트론 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 087260 | 모바일어플라이언스 | Automobiles | F Ford Motor | MEDIUM 0.5246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 087600 | 픽셀플러스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 088130 | 동아엘텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 088280 | 쏘닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 088290 | 이원컴포텍 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 088340 | 유라클 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 088350 | 한화생명 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6502 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 088390 | 이녹스 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5683 | industry | not_low_confidence | us_market_relative_proxy |
| 088790 | 진도 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6216 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088800 | 에이스테크 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 088910 | 동우팜투테이블 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6601 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089010 | 켐트로닉스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.572 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089030 | 테크윙 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 089140 | 넥스턴앤롤코리아 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089150 | 케이씨티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 089230 | THE E&M | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 089470 | HDC현대EP | Automobiles | GM General Motors | MEDIUM 0.5403 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089590 | 제주항공 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089600 | KT나스미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5838 | industry | not_low_confidence | us_market_relative_proxy |
| 089790 | 제이티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 089850 | 유비벨록스 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5179 | industry | not_low_confidence | partial_direct_similarity |
| 089860 | 롯데렌탈 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6424 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089890 | 코세스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 089970 | 브이엠 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 089980 | 상아프론테크 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5724 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090080 | 평화산업 | Automobiles | GM General Motors | MEDIUM 0.5295 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090150 | 아이윈 | Automobiles | GM General Motors | MEDIUM 0.5325 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090350 | 노루페인트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090355 | 노루페인트우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090360 | 로보스타 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090370 | 메타랩스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 090410 | 덕신이피씨 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090430 | 아모레퍼시픽 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6472 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 090435 | 아모레퍼시픽우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6463 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 090460 | 비에이치 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5937 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090470 | 제이스로보틱스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 090710 | 휴림로봇 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090850 | 현대이지웰 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 091120 | 이엠텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 091340 | S&K폴리텍 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5707 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091440 | 한울소재과학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 091580 | 상신이디피 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6241 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091590 | 남화토건 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 091700 | 파트론 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 091810 | 트리니티항공 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 091970 | LSK아이로봇 | Specialty Chemicals | DOW Dow | MEDIUM 0.6054 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092040 | 아미코젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 092070 | 디엔에프 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 092130 | 이크레더블 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 092190 | 서울바이오시스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 092200 | 디아이씨 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 092220 | KEC | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 092230 | KPX홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5622 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 092300 | 현우산업 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 092440 | 기신정기 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 092460 | 한라IMS | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 092590 | 럭스피아 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 092600 | 앤씨앤 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.51 | industry | not_low_confidence | partial_direct_similarity |
| 092730 | 네오팜 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6258 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092780 | DYP | Automobiles | GM General Motors | MEDIUM 0.5308 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092790 | 넥스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 092870 | 엑시콘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 093050 | LF | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6446 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093190 | 빅솔론 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 093240 | 형지엘리트 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6033 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 093320 | 케이아이엔엑스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 093370 | 후성 | Specialty Chemicals | DOW Dow | MEDIUM 0.5584 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 093380 | 풍강 | Automobiles | GM General Motors | MEDIUM 0.5338 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093510 | 엔지브이아이 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 093520 | 매커스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 093640 | 케이알엠 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 093920 | 서원인텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 094170 | 동운아나텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 094280 | 효성ITX | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 094360 | 칩스앤미디어 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 094480 | 갤럭시아머니트리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 094820 | 일진파워 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 094840 | 슈프리마에이치큐 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5976 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094850 | 참좋은여행 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6012 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094860 | 네오리진 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 094940 | 푸른로보틱스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 094970 | 제이엠티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095190 | 신화프리텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 095270 | 웨이브일렉트로 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095340 | ISC | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095500 | 미래나노텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095570 | AJ네트웍스 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6409 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095610 | 테스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095660 | 네오위즈 | Interactive Entertainment | GME GameStop | MEDIUM 0.5746 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095700 | 제넥신 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 095720 | 웅진씽크빅 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 095910 | 에스에너지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.552 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 096240 | 크레버스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 096250 | 와이즈넛 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 096350 | 대창솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 096530 | 씨젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 096610 | 알에프세미 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 096630 | 에스코넥 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 096690 | 에이루트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 096760 | JW홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 096770 | SK이노베이션 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096775 | SK이노베이션우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096870 | 엘디티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 097230 | HJ중공업 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 097520 | 엠씨넥스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 097780 | 에코볼트 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 097800 | 윈팩 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 097870 | 효성오앤비 | Specialty Chemicals | DOW Dow | MEDIUM 0.5597 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 097950 | CJ제일제당 | Food and Beverage | SFD Smithfield Foods | MEDIUM 0.6785 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 097955 | CJ제일제당 우 | Food and Beverage | SFD Smithfield Foods | MEDIUM 0.6686 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 098070 | 한텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6176 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 098120 | 마이크로컨텍솔 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 098460 | 고영 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5607 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 098660 | 에스티오 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5603 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 099190 | 아이센스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 099220 | SDN | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5931 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 099320 | 쎄트렉아이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 099390 | 브레인즈컴퍼니 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 099410 | 동방선기 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 099430 | 바이오플러스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 099440 | 스맥 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 099520 | DGI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 099750 | 이지케어텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100030 | 인지소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100090 | SK오션플랜트 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6274 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100120 | 뷰웍스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100130 | 동국S&C | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5945 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 100220 | 비상교육 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 100250 | 진양홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5261 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100590 | 머큐리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 100660 | 서암기계공업 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 100700 | 세운메디칼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100790 | 미래에셋벤처투자 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 100840 | SNT에너지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101000 | KS인더스트리 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 101140 | 인바이오젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101160 | 월덱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101170 | 우림피티에스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 101240 | 씨큐브 | Specialty Chemicals | DOW Dow | MEDIUM 0.5534 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 101330 | 모베이스 | Automobiles | GM General Motors | MEDIUM 0.5267 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101360 | 에코앤드림 | Specialty Chemicals | DOW Dow | MEDIUM 0.602 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101400 | 엔시트론 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101490 | 에스앤에스텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101530 | 해태제과식품 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6643 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101670 | 하이드로리튬 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5497 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101680 | 한국정밀기계 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 101730 | 위메이드맥스 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 101930 | 인화정공 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 101970 | 우양에이치씨 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 102120 | 어보브반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102260 | 동성케미컬 | Specialty Chemicals | DOW Dow | MEDIUM 0.5706 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 102370 | 케이옥션 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.5994 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 102460 | 이연제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102710 | 이엔에프테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102940 | 코오롱생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 102950 | 아하 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 103140 | 풍산 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 103230 | 에스앤더블류 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 103590 | 일진전기 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 103660 | 씨앗 | Specialty Chemicals | DOW Dow | MEDIUM 0.5619 | industry_and_business_model | not_low_confidence | not_available |
| 103840 | 우양 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6554 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104040 | 디에스엠 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 104200 | NHN벅스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 104460 | 디와이피엔에프 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 104480 | 티케이케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.5565 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 104540 | 코렌텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 104620 | 노랑풍선 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5939 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104700 | 한국철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 104830 | 원익머트리얼즈 | Specialty Chemicals | DOW Dow | MEDIUM 0.5569 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 105330 | 케이엔더블유 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 105550 | 엣지파운드리 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 105560 | KB금융 | Banks | C Citigroup | MEDIUM 0.5373 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 105630 | 한세실업 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6446 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105740 | 디케이락 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 105760 | 포스뱅크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 105840 | 우진 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 106080 | 케이이엠텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 106190 | 하이텍팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 106240 | 파인테크닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 107590 | 미원홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5582 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 107600 | 새빗켐 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5606 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 107640 | 한중엔시에스 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 108230 | 톱텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 108320 | LX세미콘 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 108380 | 대양전기공업 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 108490 | 로보티즈 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 108670 | LX하우시스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 108675 | LX하우시스우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 108860 | 셀바스AI | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 109070 | 주성코퍼레이션 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6472 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109080 | 옵티시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 109610 | 에스와이 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 109670 | 씨싸이트 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6083 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 109740 | 디에스케이 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5268 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 109820 | 진매트릭스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 109860 | 동일금속 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 109960 | 앱토크롬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 110020 | 전진바이오팜 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 110790 | 크리스에프앤씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5571 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 110990 | 디아이티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 111110 | 호전실업 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6339 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111380 | 동인기연 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111710 | 남화산업 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 111770 | 영원무역 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6565 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 112040 | 위메이드 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 112190 | KC산업 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 112290 | 와이씨켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 112610 | 씨에스윈드 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 113810 | 디젠스 | Automobiles | GM General Motors | MEDIUM 0.536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114090 | GKL | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6075 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114190 | 강원에너지 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 114450 | 그린생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 114630 | 폴라리스우노 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6076 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114810 | 한솔아이원스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 114840 | 아이패밀리에스씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6244 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114920 | 대주이엔티 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 115160 | 휴맥스 | Consumer Electronics and Appliances | SONY Sony Group | MEDIUM 0.545 | industry | not_low_confidence | partial_direct_similarity |
| 115180 | 큐리언트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 115310 | 인포바인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 115440 | 우리넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 115450 | HLB테라퓨틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 115480 | 씨유메디칼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 115500 | 케이씨에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 115530 | 씨엔플러스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5953 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 115570 | 스타플렉스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5583 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 115610 | 이미지스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 116100 | 태양기계 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 117580 | 대성에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 117670 | 알파칩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 117730 | 티로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 118000 | 메타케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 118990 | 모트렉스 | Automobiles | GM General Motors | MEDIUM 0.5428 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119500 | 포메탈 | Metals and Materials | DAL Delta Air Lines | LOW 0.2331 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 119610 | 인터로조 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 119650 | KC코트렐 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 119830 | 아이텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 119850 | 지엔씨에너지 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 120030 | 조선선재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 120110 | 코오롱인더 | Specialty Chemicals | DOW Dow | MEDIUM 0.5501 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 120115 | 코오롱인더우 | Specialty Chemicals | DOW Dow | MEDIUM 0.5501 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 120240 | 대정화금 | Specialty Chemicals | DOW Dow | MEDIUM 0.5625 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 121060 | 유니포인트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 121440 | 골프존홀딩스 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5831 | industry | not_low_confidence | us_market_relative_proxy |
| 121600 | 나노신소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.5711 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 121800 | 비덴트 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5141 | industry | not_low_confidence | partial_direct_similarity |
| 121850 | 코이즈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 121890 | 에스디시스템 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5933 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122310 | 제노레이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 122350 | 삼기 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 122450 | KX | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5692 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122640 | 예스티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 122690 | 서진오토모티브 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 122830 | 원포유 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 122870 | 와이지엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5352 | industry | not_low_confidence | us_market_relative_proxy |
| 122900 | 아이마켓코리아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 122990 | 와이솔 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 123010 | 알엔티엑스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 123040 | 엠에스오토텍 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 123330 | 제닉 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123410 | 코리아에프티 | Automobiles | GM General Motors | MEDIUM 0.5295 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123420 | 위메이드플레이 | Interactive Entertainment | GME GameStop | MEDIUM 0.5648 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123570 | 이엠넷 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5675 | industry | not_low_confidence | us_market_relative_proxy |
| 123690 | 한국화장품 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6221 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123700 | SJM | Automobiles | GM General Motors | MEDIUM 0.5393 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123750 | 알톤 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5663 | industry | not_low_confidence | us_market_relative_proxy |
| 123840 | 뉴온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 123860 | 아나패스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 123890 | 한국자산신탁 | Real Estate | RYN Rayonier . REIT | MEDIUM 0.6654 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 124500 | 아이티센글로벌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 124560 | 태웅로직스 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.596 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 125020 | 티씨머티리얼즈 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 125210 | 아모그린텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5571 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 125490 | 한라캐스트 | Automobiles | GM General Motors | MEDIUM 0.5265 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126340 | 비나텍 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 126560 | 현대퓨처넷 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6234 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126600 | BGF에코머티리얼즈 | Specialty Chemicals | DOW Dow | MEDIUM 0.5704 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 126640 | 화신정공 | Automobiles | GM General Motors | MEDIUM 0.5353 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126700 | 하이비젼시스템 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 126720 | 수산인더스트리 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6277 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126730 | 코칩 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6282 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126880 | 제이엔케이글로벌 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 127120 | 제이에스링크 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 127710 | 아시아경제 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5672 | industry | not_low_confidence | us_market_relative_proxy |
| 127980 | 화인써키트 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5248 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 128540 | 에코캡 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 128660 | 피제이메탈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 128820 | 대성산업 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 128940 | 한미약품 | Biotechnology | BIIB Biogen | MEDIUM 0.4905 | industry | not_low_confidence | us_market_relative_proxy |
| 129260 | 인터지스 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6341 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 129890 | 앱코 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 129920 | 대성하이텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 130500 | GH신소재 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 130580 | 나이스디앤비 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 130660 | 한전산업 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 130740 | 티피씨글로벌 | Automobiles | F Ford Motor | MEDIUM 0.5236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131030 | 옵투스제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131090 | 시큐브 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131100 | 티엔엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5407 | industry | not_low_confidence | us_market_relative_proxy |
| 131180 | 딜리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131220 | 대한과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131290 | 티에스이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 131370 | 알서포트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131400 | 이브이첨단소재 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5227 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 131760 | 파인텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 131970 | 두산테스나 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 133750 | 메가엠디 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 133820 | 화인베스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 134060 | 이퓨쳐 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 134380 | 미원화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5624 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 134580 | 탑코미디어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 134790 | 시디즈 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5566 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 136150 | 원일티엔아이 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5588 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 136410 | 아셈스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5515 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 136480 | 하림 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6521 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136490 | 선진 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6609 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136540 | 윈스테크넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 136660 | 큐엠씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 137080 | 나래나노텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 137310 | 에스디바이오센서 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 137400 | 피엔티 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6287 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 137940 | 넥스트아이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 137950 | 제이씨케미칼 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 138040 | 메리츠금융지주 | Banks | C Citigroup | MEDIUM 0.5221 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 138070 | 신진에스엠 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 138080 | 오이솔루션 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 138360 | 앤로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 138610 | 나이벡 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 138930 | BNK금융지주 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 139130 | iM금융지주 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 139480 | 이마트 | Retail | WMT Walmart | MEDIUM 0.5295 | industry | not_low_confidence | us_market_relative_proxy |
| 139670 | 키네마스터 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 139990 | 아주스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 140070 | 서플러스글로벌 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 140410 | 메지온 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6189 | industry_and_business_model | not_low_confidence | not_available |
| 140430 | 카티스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 140520 | 대창스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 140610 | 엔솔바이오사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 140660 | 위월드 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 140670 | 알에스오토메이션 | Automobiles | F Ford Motor | MEDIUM 0.5326 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 140860 | 파크시스템스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5937 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 141000 | 비아트론 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 141080 | 리가켐바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 142210 | 유니트론텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 142280 | 녹십자엠에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 142760 | 모아라이프플러스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 143160 | 아이디스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5864 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 143210 | 핸즈코퍼레이션 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 143240 | 사람인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 143540 | 영우디에스피 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 144510 | 지씨셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 144960 | 뉴파워프라즈마 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 145020 | 휴젤 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 145170 | 노브랜드 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6315 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145210 | 다이나믹디자인 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145720 | 덴티움 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 145990 | 삼양사 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6153 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 145995 | 삼양사우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6151 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 146060 | 율촌 | Automobiles | GM General Motors | MEDIUM 0.5332 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 146320 | 비씨엔씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 147760 | 피엠티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 147830 | 제룡산업 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 148150 | 세경하이테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 148250 | 알엔투테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 148780 | 비큐AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 148930 | 에이치와이티씨 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5919 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 149010 | 아이케이세미콘 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 149950 | 아바텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 149980 | 하이로닉 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 150900 | 파수AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 151860 | KG에코솔루션 | Automobiles | GM General Motors | MEDIUM 0.5633 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 153460 | 네이블 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 153490 | 우리이앤엘하루틴 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 153710 | 옵티팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 153890 | 져스텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 154030 | 아시아종묘 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 154040 | 다산솔루에타 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5554 | industry | not_low_confidence | us_market_relative_proxy |
| 155650 | 와이엠씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 155660 | DSR | Investment Holding Companies | OSK Oshkosh (Holding ) | MEDIUM 0.5686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 156100 | 엘앤케이바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 158430 | 아톤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 159010 | 아스플로 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 159580 | 제로투세븐 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6111 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 159910 | 에코글로우 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 160190 | 하이젠알앤엠 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 160550 | NEW | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5247 | industry | not_low_confidence | us_market_relative_proxy |
| 160980 | 싸이맥스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 161000 | 애경케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.5971 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 161390 | 한국타이어앤테크놀로지 | Automobiles | GM General Motors | MEDIUM 0.5393 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 161580 | 필옵틱스 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 161890 | 한국콜마 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6302 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 162120 | 루켄테크놀러지스 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 162300 | 신스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 163280 | 에어레인 | Specialty Chemicals | DOW Dow | MEDIUM 0.5555 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 163560 | 동일고무벨트 | Specialty Chemicals | DOW Dow | MEDIUM 0.5652 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 163730 | 핑거 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 166090 | 하나머티리얼즈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 166480 | 코아스템켐온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 168330 | 내츄럴엔도텍 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 168360 | 펨트론 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5523 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 169330 | 엠브레인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 169670 | 코스텍시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 170030 | 현대공업 | Automobiles | GM General Motors | MEDIUM 0.5228 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 170790 | 파이오링크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 170900 | 동아에스티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 170920 | 엘티씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 171010 | 램테크놀러지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 171090 | 선익시스템 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 171120 | 라이온켐텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 172670 | 에이엘티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 173130 | 오파스넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 173940 | 에프엔씨엔터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 174900 | 앱클론 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 175140 | 휴먼테크놀로지 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4846 | industry | not_low_confidence | us_market_relative_proxy |
| 175250 | 아이큐어 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 175330 | JB금융지주 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 176590 | 코나솔 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 176750 | 듀켐바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 177350 | 베셀 | Specialty Chemicals | DOW Dow | MEDIUM 0.5627 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 177830 | 파버나인 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 177900 | 쓰리에이로직스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 178320 | 서진시스템 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 178600 | 대동고려삼 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6282 | industry_and_business_model | not_low_confidence | not_available |
| 178780 | 일월지엠엘 | Retail | WMT Walmart | MEDIUM 0.5327 | industry | not_low_confidence | us_market_relative_proxy |
| 178920 | PI첨단소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.5627 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 179290 | 엠아이텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 179530 | 애드바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 179720 | 머니무브 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 179900 | 유티아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 180060 | 탑선 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 180400 | DXVX | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 180640 | 한진칼 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 181710 | NHN | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 182360 | 큐브엔터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 182400 | 엔케이젠바이오텍코리아 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 183190 | 아세아시멘트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 183300 | 코미코 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 183490 | 엔지켐생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 184230 | SGA솔루션즈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 185190 | 수프로 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 185490 | 아이진 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 185750 | 종근당 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 186230 | 그린플러스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 187220 | 디티앤씨 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5335 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 187270 | 신화콘텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 187420 | HLB제넥스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 187660 | 페니트리움바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 187790 | 나노 | Specialty Chemicals | DOW Dow | MEDIUM 0.5521 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 187870 | 디바이스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 188040 | 바이오포트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 188260 | 세니젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 189300 | 인텔리안테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 189330 | 씨이랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 189350 | 코셋 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 189690 | 포시에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 189860 | 서전기전 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 189980 | 흥국에프엔비 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6502 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 190510 | 나무가 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 190650 | 코리아에셋투자증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 191410 | 육일씨엔에쓰 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5111 | industry | not_low_confidence | partial_direct_similarity |
| 191420 | 테고사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 191600 | 블루탑 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 192080 | 더블유게임즈 | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 192250 | 케이사인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 192390 | 윈하이텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 192400 | 쿠쿠홀딩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 192410 | 오늘이엔엠 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 192440 | 슈피겐코리아 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 192650 | 드림텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 192820 | 코스맥스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6404 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 193250 | 링크드 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 194370 | 제이에스코퍼레이션 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194480 | 데브시스터즈 | Interactive Entertainment | GME GameStop | MEDIUM 0.579 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194700 | 노바렉스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 195500 | 마니커에프앤지 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6511 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 195870 | 해성디에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 195940 | HK이노엔 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 195990 | 루트K | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 196170 | 알테오젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 196300 | HLB펩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 196450 | 코아시아씨엠 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 196490 | 디에이테크놀로지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5581 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 196700 | 웹스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5566 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 197140 | 디지캡 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 198080 | 캐프 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 198440 | 강동씨앤엘 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 198940 | 한주라이트메탈 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 199150 | 데이터스트림즈 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 199290 | 바이오프로테크 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 199430 | 케이엔알시스템 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 199480 | 뱅크웨어글로벌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 199550 | 레이저옵텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 199730 | 바이오인프라 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 199800 | 툴젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 199820 | 제일일렉트릭 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 200130 | 콜마비앤에이치 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200230 | 텔콘RF제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200350 | 아티스트스튜디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4784 | industry | not_low_confidence | us_market_relative_proxy |
| 200470 | 에이팩트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200580 | 메디쎄이 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 200670 | 휴메딕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 200710 | 에이디테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200780 | 비씨월드제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200880 | 서연이화 | Automobiles | GM General Motors | MEDIUM 0.5266 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 201490 | 미투온 | Interactive Entertainment | GME GameStop | MEDIUM 0.5813 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 202960 | 판도라티비 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 203400 | 에이비온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 203450 | 유니온바이오메트릭스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 203650 | 드림시큐리티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 203690 | 아크솔루션스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 204020 | 그리티 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6365 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204270 | 제이앤티씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 204320 | HL만도 | Automobiles | GM General Motors | MEDIUM 0.5388 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204610 | 티쓰리 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5863 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204620 | 글로벌텍스프리 | Banks | JPM JP Morgan Chase & | MEDIUM 0.5236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204840 | 지엘팜텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 205100 | 엑셈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 205470 | 휴마시스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 205500 | 넥써쓰 | Interactive Entertainment | GME GameStop | MEDIUM 0.5361 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 206400 | 베노티앤알 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 206560 | 덱스터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 206640 | 바디텍메드 | Biotechnology | BIIB Biogen | MEDIUM 0.4866 | industry | not_low_confidence | us_market_relative_proxy |
| 206650 | 유바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 206950 | 볼빅 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 207490 | 에이펙스인텍 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 207760 | 미스터블루 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 207940 | 삼성바이오로직스 | Biotechnology | BIIB Biogen | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 208140 | 정다운 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6493 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 208350 | 지란지교시큐리티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 208370 | 셀바스헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 208640 | 썸에이지 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 208710 | 포톤 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 208850 | 이비테크 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 208860 | 다산디엠씨 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 208890 | 미래엔에듀파트너 | Education Services | LAUR Laureate Education | MEDIUM 0.6283 | industry_and_business_model | not_low_confidence | not_available |
| 209640 | 와이제이링크 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5242 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 210120 | 캔버스엔 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 210540 | 디와이파워 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 210980 | SK디앤디 | Real Estate | WPC W. P. Carey . REIT | MEDIUM 0.6479 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 211050 | 인카금융서비스 | Insurance | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 211270 | AP위성 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 212310 | 오건에코텍 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 212560 | 네오오토 | Automobiles | GM General Motors | MEDIUM 0.5324 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 212710 | 아이에스티이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 213420 | 덕산네오룩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 213500 | 한솔제지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 214150 | 클래시스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214180 | 헥토이노베이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214260 | 라파스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5433 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 214270 | FSN | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 214320 | 이노션 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5688 | industry | not_low_confidence | us_market_relative_proxy |
| 214330 | 금호에이치티 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 214370 | 케어젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4631 | industry | not_low_confidence | not_available |
| 214390 | 경보제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214420 | 토니모리 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6218 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214430 | 아이쓰리시스템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214450 | 파마리서치 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214610 | 롤링스톤 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 214680 | 디알텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 215000 | 골프존 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6009 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215090 | 솔디펜스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 215100 | 로보로보 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 215200 | 메가스터디교육 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 215360 | 우리산업 | Automobiles | GM General Motors | MEDIUM 0.536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215380 | 우정바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 215480 | 토박스코리아 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5726 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 215570 | 크로넥스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 215600 | 신라젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 215790 | 이노인스트루먼트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 216050 | 인크로스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.571 | industry | not_low_confidence | us_market_relative_proxy |
| 216080 | 제테마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 216400 | 인바이츠바이오코아 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 217190 | 제너셈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 217270 | 넵튠 | Interactive Entertainment | GME GameStop | MEDIUM 0.536 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 217320 | 썬테크 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 217330 | 싸이토젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 217480 | 에스디생명공학 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 217500 | 러셀 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 217590 | 티엠씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 217730 | 강스템바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 217820 | 원익피앤이 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6346 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217880 | 틸론 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 217910 | 에스제이켐 | Specialty Chemicals | DOW Dow | MEDIUM 0.5501 | industry_and_business_model | not_low_confidence | not_available |
| 217950 | 파마리서치바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.4832 | industry | not_low_confidence | us_market_relative_proxy |
| 218150 | 미래생명자원 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6451 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 218410 | RFHIC | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 219130 | 타이거일렉 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 219420 | 링크제니시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 219550 | 디와이디 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.547 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 219750 | 한국비티비 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 220100 | 퓨쳐켐 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 220180 | 핸디소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 220260 | 켐트로스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5988 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 221800 | 지구홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 221840 | 하이즈항공 | Software | DAL Delta Air Lines | LOW 0.2845 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 221980 | 케이디켐 | Specialty Chemicals | DOW Dow | MEDIUM 0.5545 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 222040 | 코스맥스엔비티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 222080 | SFA넥셀 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6329 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222110 | 팬젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 222160 | NPX | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 222420 | 쎄노텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5525 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 222670 | 플럼라인생명과학 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 222800 | 심텍 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 222980 | 한국맥널티 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 223220 | 로지스몬 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6127 | industry_and_business_model | not_low_confidence | not_available |
| 223250 | 드림씨아이에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 223310 | 사토시홀딩스 | Biotechnology | UAL United Airlines Holdings | LOW 0.1295 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 224060 | 더코디 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5724 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 224110 | 에이텍모빌리티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 224760 | 엔에스컴퍼니 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 224810 | 엄지하우스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 225190 | LK삼양 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5239 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 225220 | 제놀루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 225430 | 케이엠제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 225530 | HC보광산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 225570 | 넥슨게임즈 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.5392 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 225590 | 패션플랫폼 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6125 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226320 | 잇츠한불 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6295 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226330 | 신테카바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 226340 | 본느 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 226400 | 오스테오닉 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 226590 | 엠디바이스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 226950 | 올릭스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 227420 | 도부 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5897 | industry_and_business_model | not_low_confidence | not_available |
| 227610 | 아우딘퓨쳐스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5527 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 227840 | 현대코퍼레이션홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 227950 | 엔투텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 228340 | 동양파일 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 228670 | 레이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 228760 | 지노믹트리 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 228850 | 레이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 229000 | 젠큐릭스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 229500 | 노브메타파마 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 229640 | LS에코에너지 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 230240 | 에치에프알 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 232140 | 와이씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 232530 | 이엠티 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 232680 | 라온로보틱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 232830 | 아이티센피엔에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 233250 | 메디안디노스틱 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 233990 | 질경이 | Specialty Chemicals | DOW Dow | MEDIUM 0.558 | industry_and_business_model | not_low_confidence | not_available |
| 234030 | 싸이닉솔루션 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 234070 | 에이원큐브텍 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6248 | industry_and_business_model | not_low_confidence | not_available |
| 234080 | JW생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234100 | 폴라리스세원 | Automobiles | GM General Motors | MEDIUM 0.5294 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234300 | 에스트래픽 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234340 | 헥토파이낸셜 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234690 | 녹십자웰빙 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234920 | 자이글 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 235980 | 메드팩토 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 236030 | 씨알푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6268 | industry_and_business_model | not_low_confidence | not_available |
| 236200 | 슈프리마 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5975 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 236340 | 메디젠휴먼케어 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 236810 | 엔비티 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4982 | industry | not_low_confidence | partial_direct_similarity |
| 237690 | 에스티팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 237750 | 피앤씨테크 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 237820 | 플레이디 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.583 | industry | not_low_confidence | us_market_relative_proxy |
| 237880 | 클리오 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6252 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238090 | 앤디포스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 238120 | 얼라인드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 238200 | 비피도 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 238490 | 힘스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 238500 | 솔루믹스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 239340 | 이스트에이드 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 239610 | 에이치엘사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 239890 | 피엔에이치테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 240550 | 동방메디컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 240600 | 유진테크놀로지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5581 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 240810 | 원익IPS | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 241520 | DSC인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 241560 | 두산밥캣 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 241590 | 화승엔터프라이즈 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6019 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 241690 | 유니테크노 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 241710 | 코스메카코리아 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6409 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241770 | 메카로 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 241790 | 티이엠씨씨엔에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 241820 | 피씨엘 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 241840 | 에이스토리 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 242040 | 나무기술 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 243070 | 휴온스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 243840 | 신흥에스이씨 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6008 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 243870 | 아이티센코어 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 244460 | 올리패스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 244880 | 나눔테크 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 244920 | 에이플러스에셋 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6267 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 245450 | 씨앤에스링크 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 245620 | EDGC | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 246250 | 에스엘에스바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 246690 | TS인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 246710 | 티앤알바이오팹 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 246720 | 아스타 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 246960 | SCL사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 247540 | 에코프로비엠 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6462 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 247660 | 나노씨엠에스 | Specialty Chemicals | DOW Dow | MEDIUM 0.6002 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 248070 | 솔루엠 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5906 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 248170 | 샘표식품 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6585 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 249420 | 일동제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 250000 | 보라티알 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 250030 | 진코스텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.6193 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 250060 | 모비스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 250930 | 예선테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 251120 | 바이오에프디엔씨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.487 | industry | not_low_confidence | us_market_relative_proxy |
| 251270 | 넷마블 | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 251280 | 안지오랩 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 251370 | 와이엠티 | Specialty Chemicals | DOW Dow | MEDIUM 0.5594 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 251630 | 브이원텍 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 251970 | 펌텍코리아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 252500 | 세화피앤씨 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6131 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 252990 | 샘씨엔에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 253450 | 스튜디오드래곤 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5329 | industry | not_low_confidence | us_market_relative_proxy |
| 253590 | 네오셈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 253610 | 루트락 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 253840 | 수젠텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 254120 | 자비스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5281 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 254160 | 제이엠멀티 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 254490 | 미래반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 255220 | SG | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 255440 | 야스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 256150 | 한독크린텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 256630 | 포인트엔지니어링 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 256840 | 한국비엔씨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 256940 | 킵스파마 | Investment Holding Companies | QTWO Q2 Holdings | MEDIUM 0.5592 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 257370 | 피엔티엠에스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5525 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 257720 | 실리콘투 | Retail | WMT Walmart | MEDIUM 0.5187 | industry | not_low_confidence | us_market_relative_proxy |
| 258050 | 테크트랜스 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 258610 | 케일럼 | Semiconductors | DAL Delta Air Lines | LOW 0.1251 | generic_or_mismatch | domain_mismatch | partial_direct_similarity |
| 258790 | 소프트캠프 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 258830 | 세종메디칼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 259630 | 엠플러스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6362 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 259960 | 크래프톤 | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 260660 | 알리코제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 260870 | SK시그넷 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 260930 | 씨티케이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 260970 | 에스앤디 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6752 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 261200 | 덴티스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 261520 | 이지스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 261780 | 아리바이오랩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 262260 | 에이프로 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5201 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 262840 | 아이퀘스트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263020 | 디케이앤디 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6359 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263050 | 유틸렉스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 263600 | 덕우전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 263690 | 디알젬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263700 | 케어랩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 263720 | 디앤씨미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5934 | industry | not_low_confidence | us_market_relative_proxy |
| 263750 | 펄어비스 | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 263770 | 유에스티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 263800 | 데이타솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263810 | 상신전자 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5875 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263860 | 지니언스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263920 | 휴엠앤씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 264450 | 유비쿼스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 264660 | 씨앤지하이테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 264850 | 이랜시스 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5786 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 264900 | 크라운제과 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6472 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 265520 | AP시스템 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 265560 | 영화테크 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 265740 | 엔에프씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.615 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 266170 | 레드우즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5267 | industry | not_low_confidence | us_market_relative_proxy |
| 266350 | 팡스카이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 266470 | 바이오인프라생명과학 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 267080 | 세븐브로이맥주 | Food and Beverage | TAP Molson Coors Beverage | HIGH 0.7525 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267250 | HD현대 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 267260 | HD현대일렉트릭 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 267270 | HD건설기계 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 267290 | 경동도시가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 267320 | 나인테크 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5585 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 267790 | 배럴 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6141 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267850 | 아시아나IDT | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 267980 | 매일유업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.672 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 268280 | 미원에스씨 | Specialty Chemicals | DOW Dow | MEDIUM 0.5608 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 269620 | 시스웍 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5235 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 270210 | 에스알바이오텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 270520 | 앱튼 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5474 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 270660 | 에브리봇 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 270870 | 뉴트리 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 271560 | 오리온 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6657 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271830 | 팸텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 271940 | 일진하이솔루스 | Automobiles | F Ford Motor | MEDIUM 0.5224 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271980 | 제일약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 272110 | 케이엔제이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 272210 | 한화시스템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 272290 | 이녹스첨단소재 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 272450 | 진에어 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 272550 | 삼양패키징 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 273060 | 와이즈버즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5824 | industry | not_low_confidence | us_market_relative_proxy |
| 273640 | 와이엠텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6362 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 274090 | 켄코아에어로스페이스 | Software | DAL Delta Air Lines | LOW 0.1441 | generic_or_mismatch | domain_mismatch | partial_direct_similarity |
| 274400 | 이노시뮬레이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 275630 | 에스에스알 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 276040 | 스코넥 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 276240 | 엘리비젼 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 276730 | 한울앤제주 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6367 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 277070 | 린드먼아시아 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 277410 | 인산가 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6492 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 277810 | 레인보우로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 277880 | 티에스아이 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5767 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 278280 | 천보 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6056 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 278470 | 에이피알 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6565 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 278650 | HLB바이오스텝 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 278990 | EMB | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 279060 | 이노벡스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 279570 | 케이뱅크 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 279600 | 미디어젠 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 280360 | 롯데웰푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 281740 | 레이크머티리얼즈 | Specialty Chemicals | DOW Dow | MEDIUM 0.564 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 281820 | 케이씨텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 282330 | BGF리테일 | Retail | WMT Walmart | MEDIUM 0.5318 | industry | not_low_confidence | us_market_relative_proxy |
| 282720 | 금양그린파워 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6239 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 282880 | 코윈테크 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 284620 | 카이노스메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 284740 | 쿠쿠홈시스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 285130 | SK케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.5782 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 285490 | 노바텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 285800 | 진영 | Specialty Chemicals | DOW Dow | MEDIUM 0.5991 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 286750 | 나노실리칸첨단소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.598 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 286940 | 롯데이노베이트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 287840 | 인투셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 288180 | 케이피항공산업 | Software | DAL Delta Air Lines | LOW 0.2872 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 288330 | 파라택시스코리아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 288620 | 에스프리즘 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5568 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 288980 | 모아데이타 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 289010 | 아이스크림에듀 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 289080 | SV인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 289170 | 바이오텐 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5353 | industry | not_low_confidence | not_available |
| 289220 | 자이언트스텝 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 289930 | 웨이비스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 290090 | 트윔 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290120 | DH오토리드 | Automobiles | GM General Motors | MEDIUM 0.5316 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290270 | 휴네시온 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 290520 | 신도기연 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290550 | 디케이티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290560 | 파라택시스이더리움 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 290650 | 엘앤씨바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290660 | 다이나믹솔루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290670 | 대보마그네틱 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 290690 | 소룩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290720 | 푸드나무 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6292 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 290740 | 액트로 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 291230 | 엔피 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4989 | industry | not_low_confidence | partial_direct_similarity |
| 291650 | 압타머사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 291810 | 핀텔 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 293480 | 하나제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 293490 | 카카오게임즈 | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 293580 | 나우IB | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 293780 | 압타바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 294090 | 이오플로우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 294140 | 레몬 | Specialty Chemicals | DOW Dow | MEDIUM 0.6069 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294570 | 쿠콘 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 294630 | 서남 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 294870 | IPARK현대산업개발 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 295310 | 에이치브이엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 296160 | 프로젠 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 296520 | 가이아코퍼레이션 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 296640 | 이노에이엑스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 297090 | 씨에스베어링 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 297570 | 아틀라스링크 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5605 | industry | not_low_confidence | us_market_relative_proxy |
| 297890 | HB솔루션 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 298000 | 효성화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5573 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 298020 | 효성티앤씨 | Retail | WMT Walmart | MEDIUM 0.5334 | industry | not_low_confidence | us_market_relative_proxy |
| 298040 | 효성중공업 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 298050 | HS효성첨단소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.5546 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 298060 | 풍전약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 298380 | 에이비엘바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 298540 | 더네이쳐홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6319 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298690 | 에어부산 | Aerospace and Defense | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 298830 | 슈어소프트테크 | Software | MSFT Microsoft | MEDIUM 0.4841 | industry | not_low_confidence | us_market_relative_proxy |
| 299030 | 하나기술 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 299170 | 더블유에스아이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 299480 | 지앤이헬스케어 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.4643 | industry | not_low_confidence | not_available |
| 299660 | 셀리드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 299900 | 위지윅스튜디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4635 | industry | not_low_confidence | us_market_relative_proxy |
| 300080 | 플리토 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 300120 | 라온피플 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 300720 | 한일시멘트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 301300 | 바이브컴퍼니 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 302430 | 이노메트리 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.558 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 302440 | SK바이오사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 302550 | 리메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 302920 | 더콘텐츠온 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5123 | industry | not_low_confidence | not_available |
| 303030 | 지니틱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 303360 | 프로티아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 303530 | 이노뎁 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 303810 | 동국생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 304100 | 솔트룩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 304360 | 에스바이오메딕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 304840 | 피플바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 305090 | 마이크로디지탈 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 306040 | 에스제이그룹 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 306200 | 세아제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 306620 | 지아이에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 307180 | 아이엘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 307280 | 원바이오젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 307750 | 국전 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 307870 | 비투엔 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 307930 | 컴퍼니케이 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 307950 | 현대오토에버 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 308080 | 바이젠셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 308100 | 형지글로벌 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 308170 | 씨티알모빌리티 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 308430 | 셀비온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 309710 | 아이티켐 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 309930 | 조이웍스앤코 | Household and Personal Products | DAL Delta Air Lines | LOW 0.1228 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 309960 | LB인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 310200 | 애니플러스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5323 | industry | not_low_confidence | us_market_relative_proxy |
| 310210 | 보로노이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 310870 | 디와이씨 | Automobiles | GM General Motors | MEDIUM 0.5309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311060 | 엘에이티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 311320 | 지오엘리먼트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 311390 | 네오크레마 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6559 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311690 | CJ 바이오사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 311960 | 인터로이드 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 312610 | 에이에프더블류 | Automobiles | F Ford Motor | MEDIUM 0.5203 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 313760 | 캐리 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5546 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 314130 | 지놈앤컴퍼니 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 314140 | 알피바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 314930 | 바이오다인 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 315640 | 딥노이드 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 316140 | 우리금융지주 | Banks | C Citigroup | MEDIUM 0.5394 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317120 | 라닉스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 317240 | TS트릴리온 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5726 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317330 | 덕산테코피아 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 317400 | 자이에스앤디 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 317450 | 명인제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 317530 | 에피소드컴퍼니 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 317690 | 퀀타매트릭스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 317770 | 엑스페릭스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5208 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317830 | 에스피시스템스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 317850 | 대모 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 317860 | 노드메이슨 | Specialty Chemicals | DOW Dow | MEDIUM 0.6756 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317870 | 엔바이오니아 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 318000 | KBG | Specialty Chemicals | DOW Dow | MEDIUM 0.553 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 318010 | 팜스빌 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 318020 | 포인트모바일 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 318060 | 그래피 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 318160 | 셀바이오휴먼텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 318410 | 비비씨 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6047 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 318660 | 타임기술 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 319400 | 현대무벡스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 319660 | 피에스케이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 320000 | 한울반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 321260 | 프로이천 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 321370 | 센서뷰 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 321550 | 티움바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 321820 | 아티스트컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4806 | industry | not_low_confidence | partial_direct_similarity |
| 322000 | HD현대에너지솔루션 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6352 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 322180 | LS티라유텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 322310 | 오로스테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 322510 | 제이엘케이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 322780 | 코퍼스코리아 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 322970 | 무진메디 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 323280 | 태성 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 323350 | 다원넥스뷰 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 323410 | 카카오뱅크 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 323990 | 박셀바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 326030 | SK바이오팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.5041 | industry | not_low_confidence | us_market_relative_proxy |
| 327260 | RF머트리얼즈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 327610 | 펨토바이오메드 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 328130 | 루닛 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 328380 | 솔트웨어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 329180 | HD현대중공업 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 330350 | 위더스제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 330730 | 스톤브릿지벤처스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 330860 | 네패스아크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 331380 | 포커스에이아이 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 331520 | 밸로프 | Interactive Entertainment | GME GameStop | MEDIUM 0.5746 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 331660 | 한국미라클피플사 | Specialty Chemicals | DOW Dow | MEDIUM 0.5559 | industry_and_business_model | not_low_confidence | not_available |
| 331740 | 아우토크립트 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 331920 | 셀레믹스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 332190 | 오션스바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 332290 | 누보 | Specialty Chemicals | DOW Dow | MEDIUM 0.5593 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 332370 | 아이디피 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 332570 | PS일렉트로닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 333050 | 이노테나 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 333430 | 일승 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 333620 | 엔시스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5226 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 334970 | 프레스티지바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 335810 | 프리시젼바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 335870 | 윙스풋 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5483 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 336040 | 타스컴 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 336060 | 웨이버스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 336260 | 두산퓨얼셀 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5462 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 336370 | 솔루스첨단소재 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 336570 | 원텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 336680 | 탑런토탈솔루션 | Automobiles | GM General Motors | MEDIUM 0.5226 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 337840 | 유엑스엔 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 337930 | 젝시믹스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6394 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 338220 | 뷰노 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 338840 | 와이바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 339770 | 교촌에프앤비 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 339950 | 아이비김영 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 340360 | 다보링크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 340440 | 세림B&G | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 340450 | 지씨지놈 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 340570 | 티앤엘 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 340810 | 시선AI | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 340930 | 성원에너텍 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 341170 | 퓨쳐메디신 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 342870 | 오아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 344820 | KCC글라스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 344860 | 이노진 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6133 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 346010 | 타이드 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 347000 | 센코 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.585 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 347700 | 스피어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 347740 | 피엔케이피부임상연구센타 | Biotechnology | BIIB Biogen | MEDIUM 0.4837 | industry | not_low_confidence | us_market_relative_proxy |
| 347770 | 핌스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 347850 | 디앤디파마텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 347860 | 알체라 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 347890 | 엠엑스온 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5295 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 348030 | 모비릭스 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 348080 | 큐라티스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 348150 | 고바이오랩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 348210 | 넥스틴 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 348340 | 뉴로메카 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 348350 | 위드텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 348370 | 엔켐 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.557 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 351020 | 미쥬 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 351320 | 넥사다이내믹스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 351330 | 이삭엔지니어링 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 351870 | 차이커뮤니케이션 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5686 | industry | not_low_confidence | us_market_relative_proxy |
| 352090 | 스톰테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 352480 | 씨앤씨인터내셔널 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352700 | 씨앤투스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 352770 | 셀레스트라 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 352820 | 하이브 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4971 | industry | not_low_confidence | partial_direct_similarity |
| 352910 | 오비고 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 352940 | 인바이오 | Specialty Chemicals | DOW Dow | MEDIUM 0.5596 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 353190 | 휴럼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 353200 | 대덕전자 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6326 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 353590 | 오토앤 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 353810 | 이지바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 354200 | 엔젠바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 354320 | 알멕 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 354390 | 바스칸바이오제약 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 355150 | 코스텍시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 355390 | 크라우드웍스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 355690 | 에이텀 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 356680 | 엑스게이트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 356860 | 티엘비 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 356890 | 싸이버원 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 357230 | 에이치피오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 357550 | 석경에이티 | Specialty Chemicals | DOW Dow | MEDIUM 0.5561 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 357580 | 아모센스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 357780 | 솔브레인 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 357880 | SKAI | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 358570 | 지아이이노베이션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 359090 | 씨엔알리서치 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 360070 | 탑머티리얼 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 360350 | 코셈 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5329 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 361390 | 제노코 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 361570 | 알비더블유 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4831 | industry | not_low_confidence | partial_direct_similarity |
| 361610 | SK아이이테크놀로지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5531 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 361670 | 삼영에스앤씨 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 362320 | 청담글로벌 | Retail | WMT Walmart | MEDIUM 0.5435 | industry | not_low_confidence | us_market_relative_proxy |
| 362990 | 드림인사이트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5039 | industry | not_low_confidence | partial_direct_similarity |
| 363250 | 진시스템 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 363260 | 모비데이즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5757 | industry | not_low_confidence | us_market_relative_proxy |
| 363280 | 티와이홀딩스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5657 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 364950 | 에이아이코리아 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.5508 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 365270 | 큐라클 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 365330 | 에스와이스틸텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 365340 | 성일하이텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5603 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 365590 | 하이딥 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 365660 | 레몬헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 365900 | 브이씨 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.5395 | industry | not_low_confidence | us_market_relative_proxy |
| 366030 | 나인앤컴퍼니 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6303 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 367000 | 플래티어 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 368600 | 아이씨에이치 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5215 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 368770 | 파이버프로 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5629 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 368970 | 오에스피 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6455 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 369370 | 블리츠웨이엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 370090 | 퓨런티어 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 371950 | 풍원정밀 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 372170 | 윤성에프앤씨 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5206 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 372320 | 큐로셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 372800 | 아이티아이즈 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 372910 | 한컴라이프케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 373110 | 엑셀세라퓨틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 373160 | 데이원컴퍼니 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 373170 | 엠아이큐브솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 373200 | 엑스플러스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 373220 | LG에너지솔루션 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6592 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 375500 | DL이앤씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 376180 | 피코그램 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 376270 | HEM파마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 376290 | 씨유테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 376300 | 디어유 | Software | MSFT Microsoft | MEDIUM 0.4986 | industry | not_low_confidence | us_market_relative_proxy |
| 376900 | 로킷헬스케어 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 376930 | 노을 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 376980 | 원티드랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 377030 | 비트맥스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 377220 | 프롬바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 377300 | 카카오페이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 377330 | 이지트로닉스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5562 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377450 | 리파인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 377460 | 큐에이드 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 377480 | 마음AI | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 377740 | 바이오노트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 378340 | 필에너지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5565 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 378800 | 샤페론 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 378850 | 화승알앤에이 | Automobiles | GM General Motors | MEDIUM 0.5299 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 379390 | 이성씨엔아이 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 380540 | 옵티코어 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 380550 | 뉴로핏 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 381620 | 제닉스로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 381970 | 케이카 | Automobiles | GM General Motors | MEDIUM 0.5731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 382150 | 온코크로스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 382480 | 지아이텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 382800 | 지앤비에스 에코 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 382840 | 원준 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5972 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 382900 | 범한퓨얼셀 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6322 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 383220 | F&F | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6713 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 383310 | 에코프로에이치엔 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 383800 | LX홀딩스 | Retail | WMT Walmart | MEDIUM 0.5189 | industry | not_low_confidence | us_market_relative_proxy |
| 383930 | 디티앤씨알오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 384470 | 코어라인소프트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 387570 | 파인메딕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 388050 | 지투파워 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 388210 | 씨엠티엑스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 388610 | 지에프씨생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 388720 | 유일로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 388790 | 라이콤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 388870 | 파로스아이바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389020 | 자람테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389030 | 지니너스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389140 | 포바이포 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389260 | 대명에너지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.626 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389470 | 인벤티지랩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 389500 | 에스비비테크 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 389650 | 넥스트바이오메디컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 389680 | 유디엠텍 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 390110 | 애니메디솔루션 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 391710 | 코닉오토메이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 393210 | 토마토시스템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 393890 | 더블유씨피 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5547 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 393970 | 대진첨단소재 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5523 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 394280 | 오픈엣지테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 394420 | 리센스메디컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 394800 | 쓰리빌리언 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 396270 | 넥스트칩 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 396300 | 세아메카닉스 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 396470 | 워트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 397030 | 에이프릴바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 397810 | 애드포러스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5364 | industry | not_low_confidence | partial_direct_similarity |
| 398120 | 에스지헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 399720 | 가온칩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 402030 | 코난테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 402340 | SK스퀘어 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 402420 | 켈스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 402490 | 그린리소스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 403360 | 라피치 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 403490 | 우듬지팜 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6355 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 403550 | 쏘카 | Logistics and Transportation | CVLG Covenant Logistics Group | MEDIUM 0.6345 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 403810 | 아이엘로보틱스 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 403850 | 더핑크퐁컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5354 | industry | not_low_confidence | us_market_relative_proxy |
| 403870 | HPSP | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 405000 | 플라즈맵 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 405100 | 큐알티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 405920 | 나라셀라 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6562 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 406820 | 뷰티스킨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5547 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 407400 | 꿈비 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 408470 | 한패스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 408900 | 스튜디오미르 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 408920 | 메쎄이상 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 411080 | 샌즈랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 412350 | 레이저쎌 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 412540 | 제일엠앤에스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5475 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 413300 | 티엘엔지니어링 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 413390 | 엠오티 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 413630 | 씨피시스템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 413640 | 비아이매트릭스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 415380 | 스튜디오삼익 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5793 | industry | not_low_confidence | us_market_relative_proxy |
| 416180 | 신성에스티 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6315 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417010 | 나노팀 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5623 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417180 | 핑거스토리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 417200 | LS머트리얼즈 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5717 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 417500 | 제이아이테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 417790 | 트루엔 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6013 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417840 | 저스템 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 417860 | 오브젠 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 417970 | 모델솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 418250 | 시큐레터 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 418420 | 라온텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 418470 | KT밀리의서재 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5783 | industry | not_low_confidence | us_market_relative_proxy |
| 418550 | 제이오 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 418620 | E8 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 419050 | 삼기에너지솔루션즈 | Automobiles | TM Toyota Motor | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 419080 | 엔젯 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 419120 | 산돌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 419530 | SAMG엔터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5479 | industry | not_low_confidence | us_market_relative_proxy |
| 419540 | 비스토스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 420570 | 제이투케이바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 420770 | 기가비스 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 424760 | 벨로크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 424870 | 이뮨온시아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 424960 | 스마트레이더시스템 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 424980 | 마이크로투나노 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 425040 | 티이엠씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 425420 | 티에프이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 429270 | 시지트로닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 430690 | 한싹 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 431190 | 케이쓰리아이 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 432430 | 와이랩 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4893 | industry | not_low_confidence | us_market_relative_proxy |
| 432470 | 케이엔에스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5656 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 432720 | 퀄리타스반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 432980 | 엠에프씨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 434190 | 탈로스 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 434480 | 모니터랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 435570 | 에르코스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6078 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 437730 | 삼현 | Automobiles | GM General Motors | MEDIUM 0.5459 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 438700 | 버넥트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 439090 | 마녀공장 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6108 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 439260 | 대한조선 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 439580 | 블루엠텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 439960 | 코스모로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 440110 | 파두 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 440290 | HB인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 440320 | 오픈놀 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 441270 | 파인엠텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 443060 | HD현대마린솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 443250 | 레뷰코퍼레이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 443670 | 에스피소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 444530 | 심플랫폼 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 445090 | 에이직랜드 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 445180 | 퓨릿 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 445680 | 큐리옥스바이오시스템즈 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 446070 | 유니드비티플러스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 446440 | 에피바이오텍 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 446540 | 메가터치 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 446840 | 지슨 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 447690 | 아이오바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 448280 | 에코아이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 448710 | 코츠테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 448780 | 마이크로엔엑스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 448900 | 한국피아이엠 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 450080 | 에코프로머티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 450330 | 하스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 450520 | 인스웨이브 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 450950 | 아스테라시스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 451220 | 아이엠티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 451250 | 삐아 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6097 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 451760 | 컨텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452160 | 제이엔비 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452190 | 한빛레이저 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452200 | 민테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452260 | 한화갤러리아 | Retail | WMT Walmart | MEDIUM 0.5263 | industry | not_low_confidence | us_market_relative_proxy |
| 452280 | 한선엔지니어링 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 452300 | 캡스톤파트너스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 452400 | 이닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 452430 | 사피엔반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452450 | 피아이이 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 453340 | 현대그린푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6759 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 453450 | 그리드위즈 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 453860 | 에이에스텍 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5921 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 454910 | 두산로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 455180 | 케이지에이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 455900 | 엔젤로보틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456010 | 아이씨티케이 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456040 | OCI | Specialty Chemicals | DOW Dow | MEDIUM 0.6003 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 456070 | 이엔셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 456160 | 지투지바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456190 | 큐라켐 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456570 | 아이엠지티 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 457190 | 이수스페셜티케미컬 | Specialty Chemicals | DOW Dow | MEDIUM 0.5825 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 457370 | 한켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 457550 | 우진엔텍 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6228 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 457600 | 벡트 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 458350 | 에스팀 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5667 | industry | not_low_confidence | us_market_relative_proxy |
| 458650 | 성우 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 458870 | 씨어스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4815 | industry | not_low_confidence | us_market_relative_proxy |
| 459100 | 위츠 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 459510 | 나우로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 459550 | 알트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 460470 | 아이빔테크놀로지 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 460850 | 동국씨엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 460860 | 동국제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 460870 | 에스엠씨지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 460930 | 현대힘스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 460940 | 피앤에스로보틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 461030 | 아이엠비디엑스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 461300 | 아이스크림미디어 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 462310 | 뉴키즈온 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5757 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 462350 | 이노스페이스 | Software | DAL Delta Air Lines | LOW 0.0938 | generic_or_mismatch | domain_mismatch | not_available |
| 462510 | 라메디텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 462520 | 조선내화 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 462860 | 더즌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 462870 | 시프트업 | Interactive Entertainment | NFLX Netflix | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 462980 | 아이지넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 463020 | 뉴엔AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 463480 | 모티브링크 | Automobiles | F Ford Motor | MEDIUM 0.5262 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 464080 | 에스오에스랩 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 464280 | 티디에스팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 464490 | 쿼드메디슨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 464500 | 아이언디바이스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 464580 | 닷밀 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5255 | industry | not_low_confidence | us_market_relative_proxy |
| 465320 | 교보15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 465480 | 인스피언 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 465770 | STX그린로지스 | Logistics and Transportation | VIA Via Transportation | MEDIUM 0.6494 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 466100 | 클로봇 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 466410 | 사이냅소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 466690 | 키움히어로제1호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 467930 | IBKS제23호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 468530 | 프로티나 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 468760 | 유진스팩10호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 469480 | IBKS제24호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 469610 | 이노테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 469750 | 아이비젼웍스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 469880 | 하나30호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 469900 | 하나31호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 471050 | 대신밸런스제17호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 471820 | 셀로맥스사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 472220 | 신영스팩10호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 472230 | 에스케이증권제11호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 472850 | 폰드그룹 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6501 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 473000 | 에스케이증권제12호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 473050 | 유안타제15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 473950 | 에스케이증권제13호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 473980 | 노머스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5363 | industry | not_low_confidence | us_market_relative_proxy |
| 474170 | 루미르 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 474490 | 유안타제16호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 474610 | RF시스템즈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 474650 | 링크솔루션 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 474660 | 신한제12호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 474930 | 신한제13호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475040 | 스트라드비젼 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 475150 | SK이터닉스 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6329 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475230 | 엔알비 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475240 | 하나32호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475250 | 하나33호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475400 | 씨메스로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 475430 | 키스트론 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 475460 | 미트박스 | Retail | WMT Walmart | MEDIUM 0.5351 | industry | not_low_confidence | us_market_relative_proxy |
| 475560 | 더본코리아 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6058 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475580 | 에이럭스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475660 | 에스켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 475830 | 오름테라퓨틱 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 475960 | 토모큐브 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 476040 | 오가노이드사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 476060 | 온코닉테라퓨틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 476080 | M83 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 476710 | 타조이엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4968 | industry | not_low_confidence | not_available |
| 476830 | 알지노믹스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 477340 | 에이치엠씨제7호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477380 | 미래에셋비전스팩4호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477470 | 미래에셋비전스팩5호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477760 | DB금융스팩12호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477850 | 마키나락스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 478110 | 이베스트스팩6호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 478340 | 나라스페이스테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 478390 | KB제29호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 478440 | 미래에셋비전스팩6호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 478560 | 블랙야크아이앤씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5895 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 479880 | 한국제15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 479960 | 위너스일렉 | Electrical Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 480370 | 씨케이솔루션 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 481070 | 에이유브랜즈 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.635 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 481890 | 엔에이치스팩31호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482520 | 교보16호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482630 | 삼양엔씨켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 482680 | 미래에셋비전스팩7호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482690 | 대신밸런스제19호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 483650 | 달바글로벌 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6541 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 484120 | 도우인시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 484130 | 하나34호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 484590 | 삼양컴텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 484810 | 티엑스알로보틱스 | Construction and Engineering | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 484870 | 엠앤씨솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 486630 | KB제30호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 486990 | 노타 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 487360 | 신한제14호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 487570 | HS효성 | Investment Holding Companies | CELH Celsius Holdings | MEDIUM 0.6073 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 487580 | 폴레드 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 487720 | 키움제10호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 487830 | 신한제15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 488060 | 유진스팩11호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 488280 | 에스투더블유 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 488900 | 비츠로넥스텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 489210 | 교보17호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489460 | 바이오비쥬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 489480 | 키움제11호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489500 | 엘케이켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 489730 | 디비금융제13호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489790 | 한화비전 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 490470 | 세미파이브 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 491000 | 리브스메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 492220 | KB제31호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 493280 | 아이엠바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 493330 | 지에프아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 493790 | 유안타제17호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 494120 | 큐리오시스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 495810 | 유비씨 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 496070 | 신한제16호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 496320 | 본시스템즈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 498390 | 한화플러스제5호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 499790 | GS피앤엘 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6072 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
