# 글로벌 피어 전종목 현재 결과

## 성능 요약
- 모델 버전: `global-peer-dynamic-similarity-20260712095157`
- 시도/성공/실패: 2752 / 2752 / 0
- 성공률: 1.0
- confidence 분포: {'HIGH': 2, 'LOW': 12, 'MEDIUM': 2738}
- LOW confidence 비율: 0.00436
- domain match 분포: {'generic_or_mismatch': 12, 'industry': 1296, 'industry_and_business_model': 514, 'sector': 930}
- confidence root cause 분포: {'domain_mismatch': 12, 'not_low_confidence': 2740}
- generic/mismatch 비율: 0.00436
- financial context 분포: {'direct_financial_similarity': 70, 'not_available': 169, 'partial_direct_similarity': 1007, 'us_market_relative_proxy': 1506}
- specific profile 품질: {'profile_definition': 'source sector/industry가 generic legacy fallback이 아닌 종목', 'minimum_profile_count': 2500, 'actual_profile_count': 2752, 'maximum_low_confidence_ratio': 0.02, 'actual_low_confidence_ratio': 0.00436, 'low_confidence_count': 12, 'status': 'pass'}
- 동일회사 중복 노이즈: 0
- 구조화 표시 계약 실패: 0
- quality status: `pass`

## 전체 종목 결과
| 종목코드 | 종목명 | 원천 세부 분야 | primary peer | confidence | domain match | confidence root cause | financial context |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 000020 | 동화약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000040 | KR모터스 | Automobiles | F Ford Motor | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000050 | 경방 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000070 | 삼양홀딩스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 000080 | 하이트진로 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6546 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000087 | 하이트진로2우B | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6538 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000100 | 유한양행 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000105 | 유한양행우 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000120 | CJ대한통운 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6227 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000140 | 하이트진로홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6423 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000145 | 하이트진로홀딩스우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6415 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000150 | 두산 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000155 | 두산우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000157 | 두산2우B | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000180 | 성창기업지주 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 000210 | DL | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000215 | DL우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000220 | 유유제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000225 | 유유제약1우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000227 | 유유제약2우B | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000230 | 일동홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000240 | 한국앤컴퍼니 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000250 | 삼천당제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000270 | 기아 | Automobiles | GM General Motors | MEDIUM 0.635 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000300 | DH오토넥스 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000320 | 노루홀딩스 | Telecommunications | T AT&T | MEDIUM 0.4837 | industry | not_low_confidence | us_market_relative_proxy |
| 000325 | 노루홀딩스우 | Telecommunications | T AT&T | MEDIUM 0.4837 | industry | not_low_confidence | us_market_relative_proxy |
| 000370 | 한화손해보험 | Insurance | GSHD Goosehead Insurance | MEDIUM 0.6428 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000390 | SP삼화 | Logistics and Transportation | AXP American Express | MEDIUM 0.5171 | industry | not_low_confidence | us_market_relative_proxy |
| 000400 | 롯데손해보험 | Insurance | GSHD Goosehead Insurance | MEDIUM 0.6477 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000430 | 대원강업 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000440 | 중앙에너비스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000480 | CR홀딩스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000490 | 대동 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000500 | 가온전선 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000520 | 삼일제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 000540 | 흥국화재 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6168 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000545 | 흥국화재우 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6168 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000590 | CS홀딩스 | Shipbuilding | GD General Dynamics | MEDIUM 0.5058 | industry | not_low_confidence | us_market_relative_proxy |
| 000640 | 동아쏘시오홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 000650 | 천일고속 | Logistics and Transportation | VIA Via Transportation | MEDIUM 0.631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000660 | SK하이닉스 | Semiconductors | INTC Intel | MEDIUM 0.5371 | industry | not_low_confidence | partial_direct_similarity |
| 000670 | 영풍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000680 | LS네트웍스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 000700 | 유수홀딩스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.603 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000720 | 현대건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000725 | 현대건설우 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000760 | 이화산업 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 000810 | 삼성화재 | Insurance | HIG The Hartford Insurance Group | MEDIUM 0.6432 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000815 | 삼성화재우 | Insurance | HIG The Hartford Insurance Group | MEDIUM 0.6442 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000850 | 화천기공 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000860 | 강남제비스코 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000880 | 한화 | Shipbuilding | GD General Dynamics | MEDIUM 0.506 | industry | not_low_confidence | us_market_relative_proxy |
| 000890 | 보해양조 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6294 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000910 | 유니온 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 000950 | 전방 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.571 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000970 | 한국주철관 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 000990 | DB하이텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001000 | 신라섬유 | Real Estate | WPC W. P. Carey . REIT | MEDIUM 0.567 | industry | not_low_confidence | us_market_relative_proxy |
| 001020 | 페이퍼코리아 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4962 | industry | not_low_confidence | partial_direct_similarity |
| 001040 | CJ | Logistics and Transportation | GXO GXO Logistics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 001045 | CJ우 | Logistics and Transportation | GXO GXO Logistics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 001060 | JW중외제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001065 | JW중외제약우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001067 | JW중외제약2우B | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001070 | 대한방직 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6057 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001080 | 만호제강 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001120 | LX인터내셔널 | Logistics and Transportation | AXP American Express | MEDIUM 0.5564 | industry | not_low_confidence | us_market_relative_proxy |
| 001130 | 대한제분 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6053 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001200 | 유진투자증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001210 | 금호전기 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001230 | 동국홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001250 | GS글로벌 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001260 | 남광토건 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5694 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001270 | 부국증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001275 | 부국증권우 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001290 | 상상인증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001340 | PKC | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001360 | 삼성제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001380 | SG글로벌 | Automobiles | GM General Motors | MEDIUM 0.5404 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001390 | KG케미칼 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001420 | 태원물산 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.5279 | industry | not_low_confidence | us_market_relative_proxy |
| 001430 | 세아베스틸지주 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001440 | 대한전선 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001450 | 현대해상 | Software | MSFT Microsoft | MEDIUM 0.4998 | industry | not_low_confidence | us_market_relative_proxy |
| 001460 | BYC | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5138 | industry | not_low_confidence | us_market_relative_proxy |
| 001465 | BYC우 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5138 | industry | not_low_confidence | us_market_relative_proxy |
| 001470 | 삼부토건 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.559 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001500 | 현대차증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001510 | SK증권 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001515 | SK증권우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001520 | 동양 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5404 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001525 | 동양우 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5402 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001527 | 동양2우B | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5402 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001530 | DI동일 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001540 | 안국약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001550 | 조비 | Specialty Chemicals | DOW Dow | MEDIUM 0.5696 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001560 | 제일연마 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001570 | 금양 | Specialty Chemicals | DOW Dow | MEDIUM 0.5956 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001620 | 케이비아이동국실업 | Automobiles | GM General Motors | MEDIUM 0.5485 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001630 | 종근당홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 001680 | 대상 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6169 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001685 | 대상우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6156 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001720 | 신영증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001740 | SK네트웍스 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5426 | industry | not_low_confidence | us_market_relative_proxy |
| 001750 | 한양증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001755 | 한양증권우 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 001770 | SHD | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001780 | 알루코 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 001790 | 대한제당 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6068 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001795 | 대한제당우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6068 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001800 | 오리온홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6372 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001810 | 무림SP | Logistics and Transportation | AXP American Express | MEDIUM 0.4856 | industry | not_low_confidence | partial_direct_similarity |
| 001820 | 삼화콘덴서 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 001840 | 이화공영 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001940 | KISCO홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002020 | 코오롱 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002025 | 코오롱우 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002030 | 아세아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002070 | 비비안 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5551 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002100 | 경농 | Specialty Chemicals | DOW Dow | MEDIUM 0.559 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002140 | 고려산업 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002150 | 도화엔지니어링 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5721 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002170 | SYTS | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002200 | 한국수출포장 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002210 | 동성제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002220 | 한일철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002230 | 피에스텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002240 | 고려제강 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002290 | 삼일기업공사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002310 | 아세아제지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002320 | 한진 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6086 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002350 | 넥센타이어 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.612 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002355 | 넥센타이어1우B | Food and Beverage | MNST Monster Beverage | MEDIUM 0.612 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002360 | SH에너지화학 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002380 | KCC | Specialty Chemicals | DOW Dow | MEDIUM 0.5573 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002390 | 한독 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002410 | 범양건영 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5451 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002420 | 세기상사 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.5344 | industry | not_low_confidence | us_market_relative_proxy |
| 002450 | 삼익악기 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002460 | HS화성 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5661 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002600 | 조흥 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6307 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002620 | 제일파마홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002630 | 오리엔트바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002680 | 한탑 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002690 | 동일제강 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002700 | 신일전자 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.566 | industry | not_low_confidence | us_market_relative_proxy |
| 002710 | TCC스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002720 | 국제약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002760 | 보락 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6303 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002780 | 진흥기업 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5468 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002785 | 진흥기업우B | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5468 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002787 | 진흥기업2우B | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5468 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002790 | 아모레퍼시픽홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002795 | 아모레퍼시픽홀딩스우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6229 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002800 | 신신제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002810 | 삼영무역 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002820 | SUN&L | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002840 | 미원상사 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 002870 | 신풍 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002880 | 디와이에이 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002900 | TYM | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 002920 | 유성기업 | Automobiles | F Ford Motor | MEDIUM 0.5354 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002960 | 한국쉘석유 | Shipbuilding | GD General Dynamics | MEDIUM 0.4918 | industry | not_low_confidence | us_market_relative_proxy |
| 002990 | 금호건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002995 | 금호건설우 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003000 | 부광약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003010 | 혜인 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003030 | 세아제강지주 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003060 | 에이프로젠바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 003070 | 코오롱글로벌 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5377 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003075 | 코오롱글로벌우 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5374 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003080 | SB성보 | Specialty Chemicals | DOW Dow | MEDIUM 0.5542 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003090 | 대웅 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003100 | 선광 | Logistics and Transportation | AXP American Express | MEDIUM 0.4963 | industry | not_low_confidence | us_market_relative_proxy |
| 003120 | 일성아이에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003160 | 디아이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003200 | 일신방직 | Logistics and Transportation | AXP American Express | MEDIUM 0.5018 | industry | not_low_confidence | us_market_relative_proxy |
| 003220 | 대원제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003230 | 삼양식품 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6697 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003240 | 태광산업 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003280 | 흥아해운 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003300 | 한일홀딩스 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.6136 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003310 | 대주산업 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003350 | 한국화장품제조 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6444 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003380 | 하림지주 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6444 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003460 | 유화증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003465 | 유화증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003470 | 유안타증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003475 | 유안타증권우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003480 | 한진중공업홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003490 | 대한항공 | Retail | DAL Delta Air Lines | LOW 0.333 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 003495 | 대한항공우 | Retail | DAL Delta Air Lines | LOW 0.3327 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 003520 | 영진약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 003530 | 한화투자증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003535 | 한화투자증권우 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003540 | 대신증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003545 | 대신증권우 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003547 | 대신증권2우B | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003550 | LG | Telecommunications | T AT&T | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 003555 | LG우 | Telecommunications | T AT&T | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 003570 | SNT다이내믹스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 003580 | HLB글로벌 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6231 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003610 | 방림 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003620 | KG모빌리티 | Automobiles | GM General Motors | MEDIUM 0.5789 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003650 | 미창석유 | Shipbuilding | GD General Dynamics | MEDIUM 0.5067 | industry | not_low_confidence | us_market_relative_proxy |
| 003670 | 포스코퓨처엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003680 | 한성기업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6404 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003690 | 코리안리 | Insurance | NP Neptune Insurance Holdings | MEDIUM 0.6244 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003720 | 삼영 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003780 | 진양산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003800 | 에이스침대 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6186 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003830 | 대한화섬 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 003850 | 보령 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 003920 | 남양유업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6467 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003925 | 남양유업우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6467 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003960 | 사조대림 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6168 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004000 | 롯데정밀화학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004020 | 현대제철 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004060 | SG세계물산 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5788 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004080 | 신흥 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004090 | 한국석유 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004100 | 태양금속 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004105 | 태양금속우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004140 | 동방 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6015 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004150 | 한솔홀딩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004170 | 신세계 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 004250 | NPC | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5624 | industry | not_low_confidence | us_market_relative_proxy |
| 004255 | NPC우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5634 | industry | not_low_confidence | us_market_relative_proxy |
| 004270 | 남성 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 004310 | 현대약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004360 | 세방 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5914 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004365 | 세방우 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5907 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004370 | 농심 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6737 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004380 | 삼익THK | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004410 | 서울식품 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004415 | 서울식품우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004430 | 송원산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004440 | 삼일씨엔에스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4961 | industry | not_low_confidence | us_market_relative_proxy |
| 004450 | 삼화왕관 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004490 | 세방전지 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004540 | 깨끗한나라 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004545 | 깨끗한나라우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004560 | 현대비앤지스틸 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004590 | 한국가구 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6249 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004650 | 창해에탄올 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4996 | industry | not_low_confidence | us_market_relative_proxy |
| 004690 | 삼천리 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004700 | 조광피혁 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6174 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004710 | 한솔테크닉스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004720 | 팜젠사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 004770 | 써니전자 | Consumer Electronics and Appliances | DAL Delta Air Lines | LOW 0.2191 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 004780 | 대륙제관 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004800 | 효성 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.6284 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 004830 | 덕성 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6269 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004835 | 덕성우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6269 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004840 | DRB동일 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004870 | 티웨이홀딩스 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 004890 | 동일산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 004910 | 조광페인트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004920 | 씨아이테크 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 004960 | 한신공영 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.567 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004970 | 신라교역 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 004980 | 성신양회 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004985 | 성신양회우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 004990 | 롯데지주 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4811 | industry | not_low_confidence | partial_direct_similarity |
| 005010 | 휴스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005030 | 부산주공 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005070 | 코스모신소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005090 | SGC에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005110 | 한창 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5227 | industry | not_low_confidence | partial_direct_similarity |
| 005160 | 동국산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005180 | 빙그레 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6565 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005250 | 녹십자홀딩스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005257 | 녹십자홀딩스2우 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005290 | 동진쎄미켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005300 | 롯데칠성 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6379 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005305 | 롯데칠성우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.638 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005320 | 온타이드 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5683 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005360 | 모나미 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005380 | 현대차 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4948 | industry | not_low_confidence | us_market_relative_proxy |
| 005385 | 현대차우 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4953 | industry | not_low_confidence | us_market_relative_proxy |
| 005387 | 현대차2우B | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4953 | industry | not_low_confidence | us_market_relative_proxy |
| 005389 | 현대차3우B | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4953 | industry | not_low_confidence | us_market_relative_proxy |
| 005420 | 코스모화학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 005430 | 한국공항 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 005440 | 현대지에프홀딩스 | Biotechnology | BIIB Biogen | MEDIUM 0.487 | industry | not_low_confidence | us_market_relative_proxy |
| 005490 | POSCO홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005500 | 삼진제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005610 | 삼립 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6599 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005670 | 푸드웰 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6453 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005680 | 삼영전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005690 | 파미셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005710 | 대원산업 | Automobiles | GM General Motors | MEDIUM 0.5394 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005720 | 넥센 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005725 | 넥센우 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005740 | 크라운해태홀딩스 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6376 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005745 | 크라운해태홀딩스우 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.6376 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005750 | 대림바스 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5181 | industry | not_low_confidence | us_market_relative_proxy |
| 005800 | 신영와코루 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6298 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005810 | 풍산홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005820 | 원림 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005830 | DB손해보험 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6838 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005850 | 에스엘 | Automobiles | GM General Motors | MEDIUM 0.5497 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005860 | 한일사료 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005870 | 휴니드 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005880 | 대한해운 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.628 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005930 | 삼성전자 | Semiconductors | INTC Intel | MEDIUM 0.5345 | industry | not_low_confidence | partial_direct_similarity |
| 005935 | 삼성전자우 | Semiconductors | INTC Intel | MEDIUM 0.5386 | industry | not_low_confidence | partial_direct_similarity |
| 005940 | NH투자증권 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005945 | NH투자증권우 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 005950 | 이수화학 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 005960 | 동부건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.579 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005965 | 동부건설우 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.579 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005990 | 매일홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6427 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006040 | 동원산업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5775 | industry | not_low_confidence | us_market_relative_proxy |
| 006050 | 국영지앤엠 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006060 | 화승인더 | Retail | WMT Walmart | MEDIUM 0.5072 | industry | not_low_confidence | us_market_relative_proxy |
| 006090 | 사조오양 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6406 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006110 | 삼아알미늄 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 006120 | SK디스커버리 | Biotechnology | BIIB Biogen | MEDIUM 0.491 | industry | not_low_confidence | us_market_relative_proxy |
| 006125 | SK디스커버리우 | Biotechnology | BIIB Biogen | MEDIUM 0.4911 | industry | not_low_confidence | us_market_relative_proxy |
| 006140 | 피제이전자 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006200 | 한국전자홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 006220 | 제주은행 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 006260 | LS | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 006280 | 녹십자 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 006340 | 대원전선 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006345 | 대원전선우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006360 | GS건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5907 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006370 | 대구백화점 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 006380 | 카프로 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006400 | 삼성SDI | Metals and Materials | ALB Albemarle | MEDIUM 0.62 | sector | not_low_confidence | direct_financial_similarity |
| 006405 | 삼성SDI우 | Metals and Materials | ALB Albemarle | MEDIUM 0.62 | sector | not_low_confidence | direct_financial_similarity |
| 006490 | 프리티 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6037 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006570 | 대림통상 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 006620 | 동구바이오제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006650 | 대한유화 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006660 | 삼성공조 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006730 | 서부T&D | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.5604 | industry | not_low_confidence | us_market_relative_proxy |
| 006740 | 블루산업개발 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006800 | 미래에셋증권 | Financial Services | C Citigroup | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006805 | 미래에셋증권우 | Financial Services | C Citigroup | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006840 | AK홀딩스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.5338 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006880 | 신송홀딩스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5633 | industry | not_low_confidence | us_market_relative_proxy |
| 006890 | 태경케미컬 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006910 | 보성파워텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 006920 | 모헨즈 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5562 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006980 | 우성 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6266 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007070 | GS리테일 | Retail | WMT Walmart | MEDIUM 0.5135 | industry | not_low_confidence | us_market_relative_proxy |
| 007110 | 일신석재 | Logistics and Transportation | AXP American Express | MEDIUM 0.4802 | industry | not_low_confidence | partial_direct_similarity |
| 007120 | 미래아이앤지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 007160 | 사조산업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5986 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007210 | 벽산 | Retail | WMT Walmart | MEDIUM 0.5016 | industry | not_low_confidence | us_market_relative_proxy |
| 007280 | 한국특강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007310 | 오뚜기 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6534 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007330 | 푸른저축은행 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 007340 | DN오토모티브 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 007370 | 진양제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 007390 | 네이처셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 007460 | 에이프로젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 007530 | 와이엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007540 | 샘표 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007570 | 일양약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 007575 | 일양약품우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 007590 | 동방아그로 | Specialty Chemicals | DOW Dow | MEDIUM 0.5606 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007610 | 선도전기 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 007660 | 이수페타시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 007680 | 대원 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5521 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007690 | 국도화학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007700 | F&F홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6335 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007720 | 소노스퀘어 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 007770 | 한일화학 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 007810 | 코리아써키트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 007815 | 코리아써우 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 007820 | 엠엑스로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007860 | 서연 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 007980 | TP | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.629 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008040 | 사조동아원 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6099 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008060 | 대덕 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 008250 | 이건산업 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008260 | NI스틸 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4946 | industry | not_low_confidence | us_market_relative_proxy |
| 008290 | 원풍물산 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 008350 | 남선알미늄 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 008355 | 남선알미우 | Investment Holding Companies | IESC IES Holdings | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 008370 | 원풍 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4954 | industry | not_low_confidence | us_market_relative_proxy |
| 008420 | 문배철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008470 | 부스타 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008490 | 서흥 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5049 | industry | not_low_confidence | us_market_relative_proxy |
| 008600 | 윌비스 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 008700 | 아남전자 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 008730 | 율촌화학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008770 | 호텔신라 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.5479 | industry | not_low_confidence | us_market_relative_proxy |
| 008775 | 호텔신라우 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.5478 | industry | not_low_confidence | us_market_relative_proxy |
| 008830 | 대동기어 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 008870 | 금비 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5329 | industry | not_low_confidence | us_market_relative_proxy |
| 008930 | 한미사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 008970 | KBI동양철관 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009070 | KCTC | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5913 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009140 | 경인전자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009150 | 삼성전기 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009155 | 삼성전기우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009160 | SIMPAC | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009180 | 한솔로지스틱스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6121 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009190 | 대양금속 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009200 | 무림페이퍼 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009240 | 한샘 | Retail | WMT Walmart | MEDIUM 0.518 | industry | not_low_confidence | us_market_relative_proxy |
| 009270 | 신원 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6083 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009290 | 광동제약 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009300 | 삼아제약 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009310 | 참엔지니어링 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009320 | 아진전자부품 | Automobiles | GM General Motors | MEDIUM 0.5428 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009410 | 태영건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009415 | 태영건설우 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009420 | 한올바이오파마 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009440 | KC그린홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009450 | 경동나비엔 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009460 | 한창제지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009470 | 삼화전기 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009520 | 포스코엠텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009540 | HD한국조선해양 | Shipbuilding | GD General Dynamics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 009580 | 무림P&P | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009620 | 삼보산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009680 | 모토닉 | Automobiles | GM General Motors | MEDIUM 0.5412 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009730 | 이렘 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009770 | 삼정펄프 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 009780 | 엠에스씨 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6526 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009810 | 플레이그램 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 009830 | 한화솔루션 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009835 | 한화솔루션우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 009900 | 명신산업 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009970 | 영원무역홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6338 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010040 | 한국내화 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 010060 | OCI홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 010100 | 한국무브넥스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010120 | LS ELECTRIC | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010130 | 고려아연 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 010140 | 삼성중공업 | Shipbuilding | GD General Dynamics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 010170 | 대한광통신 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 010240 | 흥국 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010280 | 아이티센엔텍 | Logistics and Transportation | AXP American Express | MEDIUM 0.4872 | industry | not_low_confidence | us_market_relative_proxy |
| 010400 | 우진아이엔에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010470 | 오리콤 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5673 | industry | not_low_confidence | us_market_relative_proxy |
| 010580 | 에스엠벡셀 | Automobiles | GM General Motors | MEDIUM 0.5347 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010640 | 진양폴리 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 010660 | 화천기계 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010690 | 화신 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.4815 | industry | not_low_confidence | us_market_relative_proxy |
| 010770 | 평화홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010780 | 아이에스동서 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5353 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010820 | 퍼스텍 | Machinery and Industrial Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010950 | S-Oil | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010955 | S-Oil우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 010960 | 삼호개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5742 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011000 | 진원생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 011040 | 경동제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 011070 | LG이노텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011080 | 형지I&C | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011090 | 에넥스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 011150 | CJ씨푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.603 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011155 | CJ씨푸드1우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.603 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011170 | 롯데케미칼 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 011200 | HMM | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6786 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011210 | 현대위아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011230 | 삼화전자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 011280 | 태림포장 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 011300 | 우성머티리얼스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5573 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011320 | 유니크 | Automobiles | GM General Motors | MEDIUM 0.5379 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011330 | 유니켐 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 011370 | 서한 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5674 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011390 | 부산산업 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5569 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011420 | 갤럭시아에스엠 | Retail | WMT Walmart | MEDIUM 0.5122 | industry | not_low_confidence | us_market_relative_proxy |
| 011500 | 한농화성 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.4963 | industry | not_low_confidence | us_market_relative_proxy |
| 011560 | 세보엠이씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011690 | 와이투솔루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 011700 | 한신기계 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 011760 | 현대코퍼레이션 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 011780 | 금호석유화학 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 011785 | 금호석유화학우 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 011790 | SKC | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 011810 | STX | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 011930 | 신성이엔지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012030 | DB | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012160 | 영흥 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012170 | 아센디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 012200 | 계양전기 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012205 | 계양전기우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012210 | 삼미금속 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012280 | 영화금속 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012320 | 경동인베스트 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5901 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012330 | 현대모비스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012340 | 뉴인텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012450 | 한화에어로스페이스 | Shipbuilding | DAL Delta Air Lines | MEDIUM 0.62 | sector | not_low_confidence | direct_financial_similarity |
| 012510 | 더존비즈온 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012610 | 경인양행 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012620 | 원일특강 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012630 | HDC | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5919 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012690 | 모나리자 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012700 | 리드코프 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 012750 | 에스원 | Telecommunications | T AT&T | MEDIUM 0.6143 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012790 | 신일제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012800 | 대창 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 012860 | 모베이스전자 | Automobiles | GM General Motors | MEDIUM 0.5454 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013000 | 세우글로벌 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 013030 | 하이록코리아 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 013120 | 동원개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.582 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013310 | 아진산업 | Automobiles | GM General Motors | MEDIUM 0.5394 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013360 | 일성건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013520 | 화승코퍼레이션 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 013570 | 디와이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013580 | 계룡건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5818 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013700 | 까뮤이앤씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5666 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013720 | 청보 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013810 | 스페코 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5433 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013870 | 지엠비코리아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 013890 | 지누스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5841 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013990 | 아가방컴퍼니 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6302 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014100 | 메디앙스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 014130 | 한익스프레스 | Logistics and Transportation | ULH Universal Logistics Holdings | MEDIUM 0.5639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014160 | 대영포장 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014190 | 원익큐브 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014280 | 금강공업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014285 | 금강공업우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014440 | 영보화학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014470 | 부방 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5747 | industry | not_low_confidence | us_market_relative_proxy |
| 014530 | 극동유화 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014570 | 고려제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 014580 | 태경비케이 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014620 | 성광벤드 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5545 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014680 | 한솔케미칼 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014710 | 사조씨푸드 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 014790 | HL D&I | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5748 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014820 | 동원시스템즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014825 | 동원시스템즈우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 014830 | 유니드 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014910 | 성문전자 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014915 | 성문전자우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 014940 | 오리엔탈정공 | Shipbuilding | GD General Dynamics | MEDIUM 0.523 | industry | not_low_confidence | us_market_relative_proxy |
| 014950 | 삼익제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 014970 | 삼륭물산 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6319 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014990 | 인디에프 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5849 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 015020 | 이스타코 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.6246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015230 | 대창단조 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 015260 | 에이엔피 | Telecommunications | T AT&T | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 015360 | INVENI | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015590 | DKME | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 015710 | 코콤 | Software | MSFT Microsoft | MEDIUM 0.4803 | industry | not_low_confidence | us_market_relative_proxy |
| 015750 | 성우하이텍 | Automobiles | GM General Motors | MEDIUM 0.5423 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015760 | 한국전력 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015860 | 일진홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 015890 | 태경산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 016090 | 대현 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016100 | 리더스코스메틱 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 016250 | SGC E&C | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 016360 | 삼성증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016380 | KG스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 016450 | 한세예스24홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5755 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 016580 | 환인제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016590 | 신대양제지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016600 | 큐캐피탈 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 016610 | DB증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016670 | 디모아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016710 | 대성홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 016740 | 두올 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 016790 | 현대사료 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6457 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016800 | 퍼시스 | Retail | WMT Walmart | MEDIUM 0.5157 | industry | not_low_confidence | us_market_relative_proxy |
| 016880 | 웅진 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 016920 | 카스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 017000 | 신원종합개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017040 | 광명전기 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 017180 | 명문제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 017250 | 인터엠 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4806 | industry | not_low_confidence | us_market_relative_proxy |
| 017370 | 우신시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017390 | 서울가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017480 | 삼현철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 017510 | 세명전기 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017550 | 수산세보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017650 | 대림제지 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 017670 | SK텔레콤 | Telecommunications | T AT&T | MEDIUM 0.6356 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 017800 | 현대엘리베이터 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017810 | 풀무원 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6564 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017860 | DS단석 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 017890 | 한국알콜 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 017900 | 광전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 017940 | E1 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 017960 | 한국카본 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 018000 | 유니슨 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 018120 | 진로발효 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6544 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018250 | 애경산업 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5404 | industry | not_low_confidence | us_market_relative_proxy |
| 018260 | 삼성에스디에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 018290 | 브이티 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6381 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018310 | 삼목에스폼 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4959 | industry | not_low_confidence | us_market_relative_proxy |
| 018470 | 조일알미늄 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 018500 | 동원금속 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 018620 | 우진비앤지 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 018670 | SK가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 018680 | 서울제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 018700 | 졸스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 018880 | 한온시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 019010 | 베뉴지 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.5622 | industry | not_low_confidence | us_market_relative_proxy |
| 019170 | 신풍제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 019175 | 신풍제약우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 019180 | 티에이치엔 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5545 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019210 | 와이지-원 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 019490 | 엑시큐어하이트론 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 019540 | 일지테크 | Automobiles | GM General Motors | MEDIUM 0.5417 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019550 | SBI인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 019570 | 플루토스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 019660 | 글로본 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 019680 | 대교 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 019685 | 대교우B | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 019770 | 서연탑메탈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 019990 | 에너토크 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020000 | 한섬 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020120 | 키다리스튜디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.576 | industry | not_low_confidence | us_market_relative_proxy |
| 020150 | 롯데에너지머티리얼즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 020180 | 대신정보통신 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 020400 | 대동금속 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 020560 | 아시아나항공 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 020710 | 시공테크 | Media and Entertainment | NFLX Netflix | MEDIUM 0.5252 | industry | not_low_confidence | us_market_relative_proxy |
| 020760 | 일진디스플 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 021040 | 대호특수강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 021045 | 대호특수강우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 021050 | 서원 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 021080 | 에이티넘인베스트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 021240 | 코웨이 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 021320 | KCC건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5826 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021650 | 한국큐빅 | Automobiles | GM General Motors | MEDIUM 0.5463 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021820 | 세원정공 | Automobiles | GM General Motors | MEDIUM 0.546 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021880 | 메이슨캐피탈 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 022100 | 포스코DX | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 022220 | 티케이지애강 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 023000 | 삼원강재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 023150 | MH에탄올 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 023160 | 태광 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023350 | 한국종합기술 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023410 | 유진기업 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 023440 | 제이스코홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023450 | 동남합성 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 023530 | 롯데쇼핑 | Retail | WMT Walmart | MEDIUM 0.5095 | industry | not_low_confidence | us_market_relative_proxy |
| 023590 | 다우기술 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 023600 | 삼보판지 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6284 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023760 | 한국캐피탈 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 023770 | 플레이위드 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 023790 | 동일스틸럭스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023800 | 인지컨트롤스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023810 | 인팩 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023900 | 풍국주정 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 023910 | 대한약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 023960 | 에쓰씨엔지니어링 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5758 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024060 | 흥구석유 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 024070 | WISCOM | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 024090 | 디씨엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 024110 | 기업은행 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 024120 | KB오토시스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 024720 | 콜마홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 024740 | 한일단조 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 024800 | 유성티엔에스 | Logistics and Transportation | AXP American Express | MEDIUM 0.6126 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024830 | 세원물산 | Automobiles | GM General Motors | MEDIUM 0.537 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024840 | KBI메탈 | Logistics and Transportation | AXP American Express | MEDIUM 0.4981 | industry | not_low_confidence | us_market_relative_proxy |
| 024850 | HLB이노베이션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 024880 | 케이피에프 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 024890 | 대원화성 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 024900 | 디와이덕양 | Automobiles | GM General Motors | MEDIUM 0.5364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024910 | 경창산업 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 024940 | PN풍년 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5661 | industry | not_low_confidence | us_market_relative_proxy |
| 024950 | 삼천리자전거 | Retail | WMT Walmart | MEDIUM 0.5066 | industry | not_low_confidence | us_market_relative_proxy |
| 025000 | KPX케미칼 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025320 | 시노펙스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 025440 | DH오토웨어 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025530 | SJM홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 025540 | 한국단자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 025550 | 한국선재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025560 | 미래산업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 025620 | 차AI헬스케어 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.4944 | industry | not_low_confidence | partial_direct_similarity |
| 025750 | 한솔홈데코 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025770 | 한국정보통신 | Telecommunications | T AT&T | MEDIUM 0.5857 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025820 | 이구산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025860 | 남해화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5673 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025870 | 신라에스지 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 025880 | 케이씨피드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025890 | 한국주강 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 025900 | 동화기업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 025950 | 동신건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5248 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025980 | 아난티 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.6305 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026040 | 제이에스티나 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6195 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026150 | 특수건설 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026890 | 스틱인베스트먼트 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 026910 | 광진실업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 026940 | 부국철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 026960 | 동서 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6384 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027040 | 서울전자통신 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 027050 | 코리아나 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5403 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 027360 | 아주IB투자 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 027410 | BGF | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 027580 | 상보 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 027710 | 팜스토리 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.651 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027740 | 마니커 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 027830 | 대성창투 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4845 | industry | not_low_confidence | us_market_relative_proxy |
| 027970 | 한국제지 | Telecommunications | T AT&T | MEDIUM 0.5829 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 028050 | 삼성E&A | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 028080 | 휴맥스홀딩스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 028100 | 동아지질 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5656 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 028260 | 삼성물산 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5517 | industry | not_low_confidence | us_market_relative_proxy |
| 028300 | HLB | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 028670 | 팬오션 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6331 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029460 | 케이씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 029480 | 광무 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 029530 | 신도리코 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5789 | industry | not_low_confidence | us_market_relative_proxy |
| 029780 | 삼성카드 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 030000 | 제일기획 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.569 | industry | not_low_confidence | us_market_relative_proxy |
| 030190 | NICE평가정보 | Software | MSFT Microsoft | MEDIUM 0.4839 | industry | not_low_confidence | us_market_relative_proxy |
| 030200 | KT | Telecommunications | T AT&T | MEDIUM 0.6232 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030210 | 다올투자증권 | Telecommunications | T AT&T | MEDIUM 0.6057 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030350 | 드래곤플라이 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 030520 | 한글과컴퓨터 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 030530 | 원익홀딩스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 030610 | 교보증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030720 | 동원수산 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030960 | 양지사 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 031210 | 서울보증보험 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 031310 | 아이즈비전 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 031330 | 에스에이엠티 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 031430 | 신세계인터내셔날 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5954 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 031440 | 신세계푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6508 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031510 | 오스템 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 031820 | 아이티센씨티에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 031860 | 디에이치엑스컴퍼니 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 031980 | 피에스케이홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 032080 | 아즈텍WB | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 032190 | 다우데이타 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 032280 | 삼일 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.5975 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032300 | 한국파마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032350 | 롯데관광개발 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.5646 | industry | not_low_confidence | us_market_relative_proxy |
| 032500 | 케이엠더블유 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 032540 | TJ미디어 | Media and Entertainment | NFLX Netflix | MEDIUM 0.5139 | industry | not_low_confidence | us_market_relative_proxy |
| 032560 | 황금에스티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 032580 | 피델릭스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032620 | GC메디아이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 032640 | LG유플러스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.6025 | industry | not_low_confidence | us_market_relative_proxy |
| 032680 | 소프트센 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 032685 | 소프트센우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 032750 | 삼진 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 032790 | 엠젠솔루션 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 032800 | 판타지오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 032820 | 우리기술 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 032830 | 삼성생명 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.5484 | industry_and_business_model | not_low_confidence | not_available |
| 032850 | 비트컴퓨터 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4819 | industry | not_low_confidence | us_market_relative_proxy |
| 032860 | 더라미 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 032940 | 원익 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6378 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032960 | 동일기연 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033050 | 제이엠아이 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5676 | industry | not_low_confidence | us_market_relative_proxy |
| 033100 | 제룡전기 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 033130 | 디지틀조선 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033160 | 엠케이전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033170 | 시그네틱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033200 | 모아텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033230 | 인성정보 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033240 | 자화전자 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033250 | 체시스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 033270 | 유나이티드제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033290 | 로젠 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6192 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033310 | 엠투엔 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033320 | 제이씨현시스템 | Retail | WMT Walmart | MEDIUM 0.5049 | industry | not_low_confidence | us_market_relative_proxy |
| 033340 | 좋은사람들 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 033500 | 동성화인텍 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5586 | industry | not_low_confidence | us_market_relative_proxy |
| 033530 | SJG세종 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 033540 | 파라텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 033560 | 블루콤 | Real Estate | WPC W. P. Carey . REIT | MEDIUM 0.652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033640 | 네패스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 033780 | KT&G | Biotechnology | BIIB Biogen | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 033790 | 피노 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6243 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 033830 | 티비씨 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5247 | industry | not_low_confidence | us_market_relative_proxy |
| 033920 | 무학 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.648 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034020 | 두산에너빌리티 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 034120 | SBS | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5255 | industry | not_low_confidence | us_market_relative_proxy |
| 034220 | LG디스플레이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 034230 | 파라다이스 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5592 | industry | not_low_confidence | us_market_relative_proxy |
| 034310 | NICE | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 034590 | 인천도시가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 034730 | SK | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 034810 | 해성산업 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 034830 | 한국토지신탁 | Real Estate | CTRE CareTrust REIT | MEDIUM 0.6485 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034940 | 조아제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 034950 | 한국기업평가 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 035000 | HS애드 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5698 | industry | not_low_confidence | us_market_relative_proxy |
| 035080 | 그래디언트 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 035150 | 백산 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5669 | industry | not_low_confidence | us_market_relative_proxy |
| 035200 | 프럼파스트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 035250 | 강원랜드 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.6878 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 035290 | 골드앤에스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 035420 | NAVER | Software | MSFT Microsoft | MEDIUM 0.4913 | industry | not_low_confidence | us_market_relative_proxy |
| 035460 | 기산텔레콤 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 035510 | 신세계 I&C | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035600 | KG이니시스 | Retail | WMT Walmart | MEDIUM 0.4884 | industry | not_low_confidence | us_market_relative_proxy |
| 035610 | 솔본 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4881 | industry | not_low_confidence | us_market_relative_proxy |
| 035620 | 바른손이앤에이 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 035720 | 카카오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 035760 | CJ ENM | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5218 | industry | not_low_confidence | us_market_relative_proxy |
| 035810 | 이지홀딩스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035890 | 서희건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5849 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035900 | JYP Ent. | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5291 | industry | not_low_confidence | us_market_relative_proxy |
| 036000 | 예림당 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.5926 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036010 | 아비코전자 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5584 | industry | not_low_confidence | us_market_relative_proxy |
| 036030 | 케이티알파 | Retail | WMT Walmart | MEDIUM 0.5195 | industry | not_low_confidence | us_market_relative_proxy |
| 036090 | 위지트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036120 | 서울평가정보 | Software | MSFT Microsoft | MEDIUM 0.4881 | industry | not_low_confidence | us_market_relative_proxy |
| 036170 | 에이치엠넥스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036190 | 금화피에스시 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5755 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036200 | 유니셈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036220 | 오상헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 036420 | 콘텐트리중앙 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036460 | 한국가스공사 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036480 | 대성미생물 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 036530 | SNT홀딩스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036540 | SFA반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036560 | KZ정밀 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036570 | NC | Interactive Entertainment | GME GameStop | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 036580 | 팜스코 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6489 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036620 | 감성코퍼레이션 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6377 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036630 | 세종텔레콤 | Semiconductors | INTC Intel | MEDIUM 0.484 | industry | not_low_confidence | us_market_relative_proxy |
| 036640 | HRS | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 036670 | 삼양케이씨아이 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 036690 | 코맥스 | Telecommunications | T AT&T | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 036710 | 심텍홀딩스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 036800 | 나이스정보통신 | Software | MSFT Microsoft | MEDIUM 0.4862 | industry | not_low_confidence | us_market_relative_proxy |
| 036810 | 에프에스티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036830 | 솔브레인홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 036890 | 진성티이씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 036930 | 주성엔지니어링 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037030 | 파워넷 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037070 | 파세코 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5682 | industry | not_low_confidence | us_market_relative_proxy |
| 037230 | 한국팩키지 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037270 | YG PLUS | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037330 | 인지디스플레 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037350 | 성도이엔지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037370 | EG | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 037400 | 우리엔터프라이즈 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5715 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 037440 | 희림 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6398 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037460 | 삼지전자 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037560 | LG헬로비전 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5252 | industry | not_low_confidence | us_market_relative_proxy |
| 037710 | 광주신세계 | Retail | WMT Walmart | MEDIUM 0.5055 | industry | not_low_confidence | us_market_relative_proxy |
| 037760 | 쎄니트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 037950 | 엘컴텍 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5437 | industry | not_low_confidence | us_market_relative_proxy |
| 038010 | 제일테크노스 | Shipbuilding | GD General Dynamics | MEDIUM 0.5118 | industry | not_low_confidence | us_market_relative_proxy |
| 038060 | 루멘스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 038070 | 서린바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038110 | 에코플라스틱 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 038290 | 마크로젠 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 038390 | 레드캡투어 | Media and Entertainment | DAL Delta Air Lines | LOW 0.2505 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 038460 | 바이오스마트 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 038500 | 삼표시멘트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 038530 | 케이바이오랩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 038540 | 상상인 | Telecommunications | T AT&T | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 038620 | 위즈코프 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038680 | 에스넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 038870 | 에코심플렉스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 038880 | 아이에이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 038950 | 파인디지털 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 039010 | 현대에이치티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039020 | 이건홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 039030 | 이오테크닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039130 | 하나투어 | Logistics and Transportation | AXP American Express | MEDIUM 0.5177 | industry | not_low_confidence | us_market_relative_proxy |
| 039200 | 오스코텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039240 | 경남스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 039290 | 인포뱅크 | Media and Entertainment | NFLX Netflix | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039310 | 세중 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039340 | 한국경제TV | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4866 | industry | not_low_confidence | partial_direct_similarity |
| 039420 | 케이엘넷 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6054 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039440 | 에스티아이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 039490 | 키움증권 | Banks | C Citigroup | MEDIUM 0.5579 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039560 | 다산네트웍스 | Telecommunications | VZ Verizon Communications | MEDIUM 0.4928 | industry | not_low_confidence | us_market_relative_proxy |
| 039570 | HDC랩스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5694 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039610 | 화성밸브 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 039740 | 한국정보공학 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039830 | 오로라 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039840 | 디오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 039860 | 나노엔텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 039980 | 폴라리스AI | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 040160 | 누리플렉스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 040300 | YTN | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 040350 | 크레오에스지 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 040420 | 정상제이엘에스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 040610 | SG&G | Logistics and Transportation | AXP American Express | MEDIUM 0.5991 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 040910 | 아이씨디 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 041020 | 폴라리스오피스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041190 | 우리기술투자 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 041440 | 현대에버다임 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 041460 | 한국전자인증 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041510 | 에스엠 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5241 | industry | not_low_confidence | us_market_relative_proxy |
| 041520 | 이엘씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 041590 | 플래스크 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 041650 | 상신브레이크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 041830 | 인바디 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041910 | 폴라리스AI파마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041920 | 메디아나 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 041930 | SY동아 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5537 | industry | not_low_confidence | us_market_relative_proxy |
| 041960 | 코미팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 042000 | 카페24 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042040 | 케이피엠테크 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 042110 | 에스씨디 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 042370 | 비츠로테크 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 042420 | 네오위즈홀딩스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5588 | industry | not_low_confidence | us_market_relative_proxy |
| 042500 | 링네트 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042510 | 라온시큐어 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 042520 | 한스바이오메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 042600 | 새로닉스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 042660 | 한화오션 | Shipbuilding | GD General Dynamics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 042700 | 한미반도체 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 042940 | 상지건설 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5516 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043090 | 더테크놀로지 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 043100 | 알파AI | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 043150 | 바텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 043200 | 파루 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 043220 | 티에스넥스젠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 043260 | 성호전자 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 043340 | 에쎈테크 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 043360 | 디지아이 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6261 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043370 | 피에이치에이 | Automobiles | GM General Motors | MEDIUM 0.5391 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043590 | 웰킵스하이텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 043610 | KT지니뮤직 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.492 | industry | not_low_confidence | partial_direct_similarity |
| 043650 | 국순당 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5993 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 043710 | 코스리거글로벌 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 043910 | 자연과환경 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 044180 | KD | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5477 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044340 | 위닉스 | Consumer Electronics and Appliances | DAL Delta Air Lines | LOW 0.1296 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 044380 | 주연테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 044450 | KSS해운 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.636 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044480 | 빌리언스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 044490 | 태웅 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 044780 | 에이치케이 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 044820 | 코스맥스비티아이 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5357 | industry | not_low_confidence | us_market_relative_proxy |
| 044960 | 이글벳 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 044990 | 에이치엔에스하이텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 045060 | 오공 | Specialty Chemicals | DOW Dow | MEDIUM 0.566 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 045100 | 한양이엔지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 045300 | 성우테크론 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 045340 | 토탈소프트 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.5095 | industry | not_low_confidence | us_market_relative_proxy |
| 045390 | 대아티아이 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6498 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045510 | 정원엔시스 | Retail | WMT Walmart | MEDIUM 0.4857 | industry | not_low_confidence | us_market_relative_proxy |
| 045520 | 크린앤사이언스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 045660 | 에이텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 045970 | 코아시아 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046070 | 코다코 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 046120 | 오르비텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 046210 | HLB파나진 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046310 | 백금T&A | Software | MSFT Microsoft | MEDIUM 0.484 | industry | not_low_confidence | us_market_relative_proxy |
| 046390 | 삼화네트웍스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046440 | KG파이낸셜 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 046890 | 서울반도체 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 046940 | 우원개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5705 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046970 | 우리로 | Telecommunications | T AT&T | MEDIUM 0.5584 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 047040 | 대우건설 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5406 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 047050 | 포스코인터내셔널 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 047080 | 한빛소프트 | Software | MSFT Microsoft | MEDIUM 0.482 | industry | not_low_confidence | us_market_relative_proxy |
| 047310 | 파워로직스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 047400 | 유니온머티리얼 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 047560 | 이스트소프트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 047770 | 코데즈컴바인 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6157 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047810 | 한국항공우주 | Telecommunications | DAL Delta Air Lines | LOW 0.3565 | generic_or_mismatch | domain_mismatch | direct_financial_similarity |
| 047820 | 초록뱀미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5288 | industry | not_low_confidence | us_market_relative_proxy |
| 047920 | HLB제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 048410 | 현대바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 048430 | 유라테크 | Automobiles | GM General Motors | MEDIUM 0.5402 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048470 | 대동스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 048530 | 인트론바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 048550 | SM C&C | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.498 | industry | not_low_confidence | partial_direct_similarity |
| 048770 | TPC로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 048830 | 엔피케이 | Specialty Chemicals | DOW Dow | MEDIUM 0.5666 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 048870 | 시너지이노베이션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 048910 | 대원미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5318 | industry | not_low_confidence | us_market_relative_proxy |
| 049070 | 인탑스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 049080 | 기가레인 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 049120 | 파인디앤씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049180 | 셀루메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049430 | 코메론 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.557 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049470 | 비트플래닛 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049480 | 오픈베이스 | Telecommunications | T AT&T | MEDIUM 0.4905 | industry | not_low_confidence | us_market_relative_proxy |
| 049520 | 유아이엘 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 049550 | 잉크테크 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 049630 | 재영솔루텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 049720 | 고려신용정보 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 049800 | 우진플라임 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 049830 | 승일 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5404 | industry | not_low_confidence | us_market_relative_proxy |
| 049950 | 미래컴퍼니 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 049960 | 쎌바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 050090 | 비케이홀딩스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4855 | industry | not_low_confidence | us_market_relative_proxy |
| 050110 | 캠시스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 050120 | ES큐브 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 050760 | 에스폴리텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.6028 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050860 | 아세아텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 050890 | 쏠리드 | Machinery and Industrial Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 050960 | 수산아이앤티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 051160 | 지어소프트 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 051360 | 토비스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 051370 | 인터플렉스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 051380 | 피씨디렉트 | Retail | WMT Walmart | MEDIUM 0.5148 | industry | not_low_confidence | us_market_relative_proxy |
| 051390 | YW | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 051490 | 나라엠앤디 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5253 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051500 | CJ프레시웨이 | Retail | WMT Walmart | MEDIUM 0.5146 | industry | not_low_confidence | us_market_relative_proxy |
| 051600 | 한전KPS | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 051630 | 진양화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5666 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051780 | 큐로홀딩스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4839 | industry | not_low_confidence | partial_direct_similarity |
| 051900 | LG생활건강 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6419 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051905 | LG생활건강우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051910 | LG화학 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 051915 | LG화학우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 051980 | 중앙첨단소재 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052020 | 에스티큐브 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 052220 | iMBC | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052260 | 현대바이오랜드 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 052300 | 오션인더블유 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 052330 | 코텍 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5679 | industry | not_low_confidence | us_market_relative_proxy |
| 052400 | 코나아이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052420 | 오성첨단소재 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 052460 | 아이크래프트 | Telecommunications | T AT&T | MEDIUM 0.5631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052600 | 한네트 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052690 | 한전기술 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 052710 | 아모텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 052770 | 아이톡시 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 052790 | 액토즈소프트 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052860 | 아이앤씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 052900 | KX하이텍 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4881 | industry | not_low_confidence | us_market_relative_proxy |
| 052960 | 태양3C | Automobiles | GM General Motors | MEDIUM 0.5243 | industry_and_business_model | not_low_confidence | not_available |
| 053030 | 바이넥스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053050 | 지에스이 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053060 | 세동 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 053080 | 케이엔솔 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 053160 | 프리엠스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053210 | 스카이라이프 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5298 | industry | not_low_confidence | us_market_relative_proxy |
| 053260 | 금강철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 053270 | 구영테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053280 | 예스24 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5276 | industry | not_low_confidence | partial_direct_similarity |
| 053290 | NE능률 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 053300 | 한국정보인증 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5452 | industry | not_low_confidence | us_market_relative_proxy |
| 053350 | 이니텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053450 | 세코닉스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053580 | 웹케시 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053610 | 프로텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053620 | 태양 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 053690 | 한미글로벌 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5793 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053700 | 삼보모터스 | Telecommunications | T AT&T | MEDIUM 0.5658 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053800 | 안랩 | Software | MSFT Microsoft | MEDIUM 0.4843 | industry | not_low_confidence | us_market_relative_proxy |
| 053950 | 경남제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 053980 | 오상자이엘 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.587 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054040 | 한국컴퓨터 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5554 | industry | not_low_confidence | us_market_relative_proxy |
| 054050 | NH농우바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054090 | 삼진엘앤디 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 054180 | 메디콕스 | Shipbuilding | GD General Dynamics | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 054210 | 이랜텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054220 | 비츠로시스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 054300 | 팬스타엔터프라이즈 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054410 | 케이피티유 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 054450 | 텔레칩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054540 | 삼영엠텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 054620 | APS | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 054670 | 대한뉴팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054780 | 키이스트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 054800 | 아이디스홀딩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054920 | 한컴위드 | Retail | WMT Walmart | MEDIUM 0.503 | industry | not_low_confidence | us_market_relative_proxy |
| 054930 | 유신 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054940 | 엑사이엔씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054950 | 제이브이엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 055490 | 테이팩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 055550 | 신한지주 | Financial Services | C Citigroup | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 056080 | 유진로봇 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 056090 | 시지메드텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 056190 | SFA | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 056360 | 코위버 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 056700 | 신화인터텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 056730 | CNT85 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 057030 | YBM넷 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5657 | industry | not_low_confidence | us_market_relative_proxy |
| 057050 | 현대홈쇼핑 | Biotechnology | BIIB Biogen | MEDIUM 0.495 | industry | not_low_confidence | us_market_relative_proxy |
| 057540 | 옴니시스템 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 057680 | 티사이언티픽 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058110 | 멕아이씨에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058400 | KNN | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5238 | industry | not_low_confidence | us_market_relative_proxy |
| 058430 | 포스코스틸리온 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 058450 | 한주에이알티 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 058470 | 리노공업 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 058610 | 에스피지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 058630 | 엠게임 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5648 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058650 | 세아홀딩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 058730 | 다스코 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 058820 | CMG제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 058850 | KTcs | Retail | WMT Walmart | MEDIUM 0.5149 | industry | not_low_confidence | us_market_relative_proxy |
| 058860 | KTis | Retail | WMT Walmart | MEDIUM 0.5175 | industry | not_low_confidence | us_market_relative_proxy |
| 058970 | 엠로 | Software | MSFT Microsoft | MEDIUM 0.4843 | industry | not_low_confidence | us_market_relative_proxy |
| 059090 | 미코 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 059100 | 아이컴포넌트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 059120 | 아진엑스텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 059180 | 엔더블유시 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 059210 | 메타바이오메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 059270 | 해성에어로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060150 | 인선이엔티 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5654 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 060230 | 제이케이시냅스 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 060240 | 스타코링크 | Shipbuilding | GD General Dynamics | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 060250 | NHN KCP | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060260 | 뉴보텍 | Retail | WMT Walmart | MEDIUM 0.508 | industry | not_low_confidence | us_market_relative_proxy |
| 060280 | 큐렉소 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 060310 | 3S | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 060370 | LS마린솔루션 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5714 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060380 | 동양에스텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060480 | 국일신동 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060540 | 에스에이티 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5434 | industry | not_low_confidence | us_market_relative_proxy |
| 060560 | HC홈센타 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5954 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060570 | 드림어스컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5037 | industry | not_low_confidence | us_market_relative_proxy |
| 060590 | 씨티씨바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060720 | KH바텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060850 | 영림원소프트랩 | Logistics and Transportation | AXP American Express | MEDIUM 0.5878 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060900 | 에이전트AI | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 060980 | HL홀딩스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 061040 | 알에프텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 061090 | 세나테크놀로지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 061250 | 화일약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 061970 | LB세미콘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 062040 | 산일전기 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 062970 | 한국첨단소재 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 063080 | 컴투스홀딩스 | Interactive Entertainment | GAME GameSquare Holdings | MEDIUM 0.5415 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 063160 | 종근당바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 063170 | 서울옥션 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.6122 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063440 | SM Life Design | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5218 | industry | not_low_confidence | us_market_relative_proxy |
| 063570 | NICE인프라 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 063760 | 이엘피 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 064090 | 인크레더블버즈 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 064240 | 홈캐스트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064260 | 다날 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064290 | 인텍플러스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 064350 | 현대로템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 064400 | LG씨엔에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064480 | 브리지텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064520 | 테크엘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064550 | 바이오니아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064760 | 티씨케이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 064800 | 포니링크 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.4809 | industry | not_low_confidence | partial_direct_similarity |
| 064820 | 케이프 | Shipbuilding | GD General Dynamics | MEDIUM 0.5152 | industry | not_low_confidence | us_market_relative_proxy |
| 064850 | 에프앤가이드 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 064960 | SNT모티브 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 065060 | 지엔코 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5601 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 065130 | 탑엔지니어링 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 065150 | 대산F&B | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6398 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065170 | 비엘팜텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 065350 | 신성델타테크 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5762 | industry | not_low_confidence | us_market_relative_proxy |
| 065370 | 위세아이텍 | Software | MSFT Microsoft | MEDIUM 0.4838 | industry | not_low_confidence | us_market_relative_proxy |
| 065420 | 에스아이리소스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065440 | 이루온 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 065450 | 빅텍 | Machinery and Industrial Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 065500 | 오리엔트정공 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 065510 | 휴비츠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065530 | 와이어블 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 065570 | 삼영이엔씨 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065650 | 하이퍼코퍼레이션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065660 | 안트로젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065680 | 우주일렉트로 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065690 | 파커스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065710 | 서호전기 | Shipbuilding | BWXT BWX Technologies | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 065770 | CS | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 065950 | 웰크론 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066130 | 하츠 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 066310 | 큐에스아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 066360 | 체리부로 | Retail | WMT Walmart | MEDIUM 0.5051 | industry | not_low_confidence | us_market_relative_proxy |
| 066410 | 버킷스튜디오 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 066430 | 아이로보틱스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 066570 | LG전자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 066575 | LG전자우 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 066590 | 스모트로닉 | Telecommunications | T AT&T | MEDIUM 0.5391 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 066620 | 국보디자인 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6336 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066670 | 디티씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 066700 | 테라젠이텍스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 066790 | 씨씨에스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 066830 | 제노텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5867 | industry_and_business_model | not_low_confidence | not_available |
| 066900 | 디에이피 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4717 | industry | not_low_confidence | us_market_relative_proxy |
| 066910 | 손오공 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 066970 | 엘앤에프 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 066980 | 한성크린텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 067000 | 조이시티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 067010 | 이씨에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 067080 | 대화제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067160 | SOOP | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5719 | industry | not_low_confidence | us_market_relative_proxy |
| 067170 | 오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 067280 | 멀티캠퍼스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5664 | industry | not_low_confidence | us_market_relative_proxy |
| 067290 | JW신약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067310 | 하나마이크론 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 067370 | 선바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067390 | 아스트 | Software | DAL Delta Air Lines | LOW 0.2177 | generic_or_mismatch | domain_mismatch | partial_direct_similarity |
| 067570 | 엔브이에이치코리아 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 067630 | HLB생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 067730 | 로지시스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 067770 | 세진티에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067830 | 세이브존I&C | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5245 | industry | not_low_confidence | us_market_relative_proxy |
| 067900 | 와이엔텍 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6341 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067920 | 이글루 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 067990 | 도이치모터스 | Automobiles | GM General Motors | MEDIUM 0.5746 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068050 | 팬엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 068100 | 케이웨더 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 068240 | 다원시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 068270 | 셀트리온 | Biotechnology | BIIB Biogen | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 068290 | 삼성출판사 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5262 | industry | not_low_confidence | partial_direct_similarity |
| 068330 | 일신바이오 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 068760 | 셀트리온제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 068790 | DMS | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 068930 | 디지털대성 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5743 | industry | not_low_confidence | us_market_relative_proxy |
| 068940 | 셀피글로벌 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 069080 | 웹젠 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5529 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069140 | 누리플랜 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5737 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069260 | TKG휴켐스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 069330 | 유아이디 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 069410 | 엔텔스 | Software | MSFT Microsoft | MEDIUM 0.4876 | industry | not_low_confidence | us_market_relative_proxy |
| 069460 | 대호에이엘 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 069510 | 에스텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 069540 | 빛과전자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 069620 | 대웅제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 069640 | 한세엠케이 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5653 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069730 | DSR제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 069920 | 엑시온그룹 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 069960 | 현대백화점 | Retail | WMT Walmart | MEDIUM 0.5162 | industry | not_low_confidence | us_market_relative_proxy |
| 070300 | 엑스큐어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 070590 | 인티큐브 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 070960 | 모나용평 | Hotels, Restaurants, and Leisure | H Hyatt Hotels | MEDIUM 0.6319 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071050 | 한국금융지주 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071055 | 한국금융지주우 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071090 | 하이스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 071200 | 인피니트헬스케어 | Software | MSFT Microsoft | MEDIUM 0.487 | industry | not_low_confidence | us_market_relative_proxy |
| 071280 | 로체시스템즈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 071320 | 지역난방공사 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 071670 | 에이테크솔루션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 071840 | 롯데하이마트 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5354 | industry | not_low_confidence | partial_direct_similarity |
| 071850 | 캐스텍코리아 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4675 | industry | not_low_confidence | us_market_relative_proxy |
| 071950 | 코아스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 071970 | HD현대마린엔진 | Shipbuilding | GD General Dynamics | MEDIUM 0.5095 | industry | not_low_confidence | us_market_relative_proxy |
| 072020 | 중앙백신 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 072130 | 유엔젤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 072470 | 우리산업홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5349 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072710 | 농심홀딩스 | Food and Beverage | USFD US Foods Holding | MEDIUM 0.669 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072770 | 멤레이비티 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 072870 | 메가스터디 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 072950 | 빛샘전자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 072990 | 에이치시티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 073010 | 케이에스피 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 073110 | 엘엠에스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 073190 | 듀오백 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 073240 | 금호타이어 | Telecommunications | T AT&T | MEDIUM 0.5812 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073490 | LIG아큐버 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 073540 | 에프알텍 | Telecommunications | T AT&T | MEDIUM 0.6075 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073560 | 우리손에프앤지 | Retail | WMT Walmart | MEDIUM 0.5043 | industry | not_low_confidence | us_market_relative_proxy |
| 073570 | 리튬포어스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 073640 | 테라사이언스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 074430 | 아미노로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 074600 | 원익QnC | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 074610 | 이엔플러스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 075130 | 플랜티넷 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5322 | industry | not_low_confidence | us_market_relative_proxy |
| 075180 | 새론오토모티브 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 075580 | 세진중공업 | Shipbuilding | GD General Dynamics | MEDIUM 0.5042 | industry | not_low_confidence | us_market_relative_proxy |
| 075970 | 동국알앤에스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 076080 | 웰크론한텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.578 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 076340 | 지에이이노더스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5335 | industry_and_business_model | not_low_confidence | not_available |
| 076610 | 해성옵틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 077360 | 덕산하이메탈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 077500 | 유니퀘스트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 077970 | STX엔진 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 078000 | 텔코웨어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078020 | LS증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078070 | 유비쿼스홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078130 | 국일제지 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 078140 | 대봉엘에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078150 | HB테크놀러지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 078160 | 메디포스트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 078340 | 컴투스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5507 | industry | not_low_confidence | us_market_relative_proxy |
| 078350 | 한양디지텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 078520 | 에이블씨엔씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6397 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078590 | 휴림에이텍 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 078600 | 대주전자재료 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5449 | industry | not_low_confidence | us_market_relative_proxy |
| 078860 | 아이오케이이엔엠 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 078890 | 가온그룹 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 078930 | GS | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 078935 | GS우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079000 | 와토스코리아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 079160 | CJ CGV | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4916 | industry | not_low_confidence | partial_direct_similarity |
| 079170 | 한창산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 079190 | 케스피온 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 079370 | 제우스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 079430 | 현대리바트 | Retail | WMT Walmart | MEDIUM 0.5137 | industry | not_low_confidence | us_market_relative_proxy |
| 079550 | LIG디펜스앤에어로스페이스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079650 | 서산 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 079810 | APS이노베이션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079900 | 전진건설로봇 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 079940 | 가비아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 079950 | 인베니아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 079960 | 동양이엔피 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5646 | industry | not_low_confidence | us_market_relative_proxy |
| 079970 | 투비소프트 | Software | MSFT Microsoft | MEDIUM 0.4806 | industry | not_low_confidence | us_market_relative_proxy |
| 079980 | 휴비스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 080010 | 이상네트웍스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 080160 | 모두투어 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6496 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080220 | 제주반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 080420 | 모다이노칩 | Retail | WMT Walmart | MEDIUM 0.4859 | industry | not_low_confidence | partial_direct_similarity |
| 080470 | 성창오토텍 | Automobiles | GM General Motors | MEDIUM 0.5506 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080520 | 오디텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 080530 | 코디 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6079 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080580 | 오킨스전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 080720 | 한국유니온제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 081000 | 일진다이아 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 081150 | 티플랙스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 081180 | 쎄크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 081580 | 성우전자 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 081660 | 미스토홀딩스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 082210 | 옵트론텍 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5258 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 082270 | 젬백스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 082640 | 동양생명 | Insurance | THG Hanover Insurance Group | MEDIUM 0.6355 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 082660 | 코스나인 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 082740 | 한화엔진 | Shipbuilding | GD General Dynamics | MEDIUM 0.5192 | industry | not_low_confidence | us_market_relative_proxy |
| 082800 | 비보존 제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 082850 | 우리바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 082920 | 비츠로셀 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 083310 | 엘오티베큠 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083420 | 그린케미칼 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 083450 | GST | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083470 | 이엠앤아이 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 083500 | 에프엔에스테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 083550 | 케이엠 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083640 | 인콘 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083650 | 비에이치아이 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 083660 | CSA 코스믹 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 083790 | CG인바이츠 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 083930 | 아바코 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 084010 | 대한제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 084110 | 휴온스글로벌 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 084180 | 수성웹툰 | Logistics and Transportation | AXP American Express | MEDIUM 0.5146 | industry | not_low_confidence | us_market_relative_proxy |
| 084370 | 유진테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 084440 | 유비온 | Software | MSFT Microsoft | MEDIUM 0.4837 | industry | not_low_confidence | us_market_relative_proxy |
| 084650 | 랩지노믹스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 084670 | 동양고속 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084680 | 이월드 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5498 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 084690 | 대상홀딩스 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 084695 | 대상홀딩스우 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 084730 | 팅크웨어 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5383 | industry | not_low_confidence | partial_direct_similarity |
| 084850 | 아이티엠반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 084870 | TBH글로벌 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084990 | 헬릭스미스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 085310 | 엔케이 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 085620 | 미래에셋생명 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 085660 | 차바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 085670 | 뉴프렉스 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5656 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085810 | 알티캐스트 | Media and Entertainment | NFLX Netflix | MEDIUM 0.5148 | industry | not_low_confidence | us_market_relative_proxy |
| 085910 | 네오티스 | Automobiles | GM General Motors | MEDIUM 0.556 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086040 | 바이오톡스텍 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086060 | 진바이오텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 086220 | 광동헬스바이오 | Food and Beverage | TSN Tyson Foods | MEDIUM 0.6207 | industry | not_low_confidence | partial_direct_similarity |
| 086280 | 현대글로비스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6623 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 086390 | 유니테스트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 086450 | 동국제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086520 | 에코프로 | Specialty Chemicals | DOW Dow | MEDIUM 0.6625 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 086670 | 비엠티 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 086710 | 선진뷰티사이언스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 086790 | 하나금융지주 | Telecommunications | T AT&T | MEDIUM 0.5857 | industry_and_business_model | not_low_confidence | not_available |
| 086820 | 바이오솔루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086890 | 이수앱지스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 086900 | 메디톡스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086960 | MDS테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 086980 | 쇼박스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 087010 | 펩트론 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 087260 | 모바일어플라이언스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 087600 | 픽셀플러스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 088130 | 동아엘텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 088280 | 쏘닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 088290 | 이원컴포텍 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 088340 | 유라클 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 088350 | 한화생명 | Financial Services | C Citigroup | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 088390 | 이녹스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 088790 | 진도 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6187 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088800 | 에이스테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 088910 | 동우팜투테이블 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6517 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089010 | 켐트로닉스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089030 | 테크윙 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 089140 | 넥스턴앤롤코리아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089150 | 케이씨티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 089230 | THE E&M | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4604 | industry | not_low_confidence | us_market_relative_proxy |
| 089470 | HDC현대EP | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089590 | 제주항공 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089600 | KT나스미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5746 | industry | not_low_confidence | us_market_relative_proxy |
| 089790 | 제이티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 089850 | 유비벨록스 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5332 | industry | not_low_confidence | partial_direct_similarity |
| 089860 | 롯데렌탈 | Retail | WMT Walmart | MEDIUM 0.5139 | industry | not_low_confidence | us_market_relative_proxy |
| 089890 | 코세스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 089970 | 브이엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 089980 | 상아프론테크 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 090080 | 평화산업 | Automobiles | GM General Motors | MEDIUM 0.5427 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090150 | 아이윈 | Automobiles | GM General Motors | MEDIUM 0.5463 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090350 | 노루페인트 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090355 | 노루페인트우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090360 | 로보스타 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090370 | 메타랩스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 090410 | 덕신이피씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5449 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 090430 | 아모레퍼시픽 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6497 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 090435 | 아모레퍼시픽우 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6486 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 090460 | 비에이치 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 090470 | 제이스로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 090710 | 휴림로봇 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 090850 | 현대이지웰 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 091120 | 이엠텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 091340 | S&K폴리텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 091440 | 한울소재과학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 091580 | 상신이디피 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6498 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091590 | 남화토건 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091700 | 파트론 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 091810 | 트리니티항공 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 091970 | LSK아이로봇 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 092040 | 아미코젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 092070 | 디엔에프 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 092130 | 이크레더블 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 092190 | 서울바이오시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 092200 | 디아이씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 092220 | KEC | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 092230 | KPX홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5688 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 092300 | 현우산업 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 092440 | 기신정기 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 092460 | 한라IMS | Shipbuilding | GD General Dynamics | MEDIUM 0.5053 | industry | not_low_confidence | us_market_relative_proxy |
| 092590 | 럭스피아 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 092600 | 앤씨앤 | Semiconductors | INTC Intel | MEDIUM 0.4869 | industry | not_low_confidence | us_market_relative_proxy |
| 092730 | 네오팜 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6287 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092780 | DYP | Automobiles | GM General Motors | MEDIUM 0.5457 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092790 | 넥스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 092870 | 엑시콘 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 093050 | LF | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6464 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093190 | 빅솔론 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093240 | 형지엘리트 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.604 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 093320 | 케이아이엔엑스 | Retail | WMT Walmart | MEDIUM 0.483 | industry | not_low_confidence | us_market_relative_proxy |
| 093370 | 후성 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 093380 | 풍강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 093510 | 엔지브이아이 | Automobiles | GM General Motors | MEDIUM 0.5243 | industry_and_business_model | not_low_confidence | not_available |
| 093520 | 매커스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 093640 | 케이알엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 093920 | 서원인텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 094170 | 동운아나텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 094280 | 효성ITX | Retail | WMT Walmart | MEDIUM 0.5098 | industry | not_low_confidence | us_market_relative_proxy |
| 094360 | 칩스앤미디어 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 094480 | 갤럭시아머니트리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 094820 | 일진파워 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 094840 | 슈프리마에이치큐 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 094850 | 참좋은여행 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5985 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094860 | 네오리진 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 094940 | 푸른로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 094970 | 제이엠티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 095190 | 신화프리텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 095270 | 웨이브일렉트로 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 095340 | ISC | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095500 | 미래나노텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 095570 | AJ네트웍스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 095610 | 테스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 095660 | 네오위즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5576 | industry | not_low_confidence | us_market_relative_proxy |
| 095700 | 제넥신 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 095720 | 웅진씽크빅 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 095910 | 에스에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096240 | 크레버스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5674 | industry | not_low_confidence | us_market_relative_proxy |
| 096250 | 와이즈넛 | Software | MSFT Microsoft | MEDIUM 0.4868 | industry | not_low_confidence | us_market_relative_proxy |
| 096350 | 대창솔루션 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096530 | 씨젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 096610 | 알에프세미 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 096630 | 에스코넥 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096690 | 에이루트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 096760 | JW홀딩스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 096770 | SK이노베이션 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096775 | SK이노베이션우 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 096870 | 엘디티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 097230 | HJ중공업 | Shipbuilding | GD General Dynamics | MEDIUM 0.4866 | industry | not_low_confidence | us_market_relative_proxy |
| 097520 | 엠씨넥스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 097780 | 에코볼트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 097800 | 윈팩 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 097870 | 효성오앤비 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 097950 | CJ제일제당 | Food and Beverage | SFD Smithfield Foods | MEDIUM 0.672 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 097955 | CJ제일제당 우 | Food and Beverage | SFD Smithfield Foods | MEDIUM 0.6623 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 098070 | 한텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 098120 | 마이크로컨텍솔 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 098460 | 고영 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 098660 | 에스티오 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5621 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 099190 | 아이센스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 099220 | SDN | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 099320 | 쎄트렉아이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 099390 | 브레인즈컴퍼니 | Software | MSFT Microsoft | MEDIUM 0.4856 | industry | not_low_confidence | us_market_relative_proxy |
| 099410 | 동방선기 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 099430 | 바이오플러스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 099440 | 스맥 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 099520 | DGI | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 099750 | 이지케어텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100030 | 인지소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100090 | SK오션플랜트 | Shipbuilding | BWXT BWX Technologies | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100120 | 뷰웍스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100130 | 동국S&C | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 100220 | 비상교육 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5684 | industry | not_low_confidence | us_market_relative_proxy |
| 100250 | 진양홀딩스 | Automobiles | GM General Motors | MEDIUM 0.5383 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100590 | 머큐리 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 100660 | 서암기계공업 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 100700 | 세운메디칼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100790 | 미래에셋벤처투자 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 100840 | SNT에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 101000 | KS인더스트리 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101140 | 인바이오젠 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101160 | 월덱스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101170 | 우림피티에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 101240 | 씨큐브 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5007 | industry | not_low_confidence | us_market_relative_proxy |
| 101330 | 모베이스 | Automobiles | GM General Motors | MEDIUM 0.5373 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101360 | 에코앤드림 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 101400 | 엔시트론 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.5175 | industry | not_low_confidence | us_market_relative_proxy |
| 101490 | 에스앤에스텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 101530 | 해태제과식품 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6518 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101670 | 하이드로리튬 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 101680 | 한국정밀기계 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 101730 | 위메이드맥스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 101930 | 인화정공 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 101970 | 우양에이치씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102120 | 어보브반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102260 | 동성케미컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 102370 | 케이옥션 | Art and Collectibles Marketplace | ACVA ACV Auctions | MEDIUM 0.61 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 102460 | 이연제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102710 | 이엔에프테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 102940 | 코오롱생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 102950 | 아하 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 103140 | 풍산 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 103230 | 에스앤더블류 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4974 | industry | not_low_confidence | us_market_relative_proxy |
| 103590 | 일진전기 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 103660 | 씨앗 | Specialty Chemicals | DOW Dow | MEDIUM 0.5747 | industry_and_business_model | not_low_confidence | not_available |
| 103840 | 우양 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6426 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104040 | 디에스엠 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 104200 | NHN벅스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 104460 | 디와이피엔에프 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5629 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104480 | 티케이케미칼 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5687 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104540 | 코렌텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 104620 | 노랑풍선 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5866 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104700 | 한국철강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 104830 | 원익머트리얼즈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 105330 | 케이엔더블유 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 105550 | 엣지파운드리 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 105560 | KB금융 | Financial Services | C Citigroup | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 105630 | 한세실업 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6438 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105740 | 디케이락 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 105760 | 포스뱅크 | Telecommunications | T AT&T | MEDIUM 0.6076 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105840 | 우진 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 106080 | 케이이엠텍 | Food and Beverage | LSF Laird Superfood | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 106190 | 하이텍팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 106240 | 파인테크닉스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 107590 | 미원홀딩스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 107600 | 새빗켐 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 107640 | 한중엔시에스 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5886 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 108230 | 톱텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 108320 | LX세미콘 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 108380 | 대양전기공업 | Shipbuilding | BWXT BWX Technologies | MEDIUM 0.4835 | industry | not_low_confidence | us_market_relative_proxy |
| 108490 | 로보티즈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 108670 | LX하우시스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 108675 | LX하우시스우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 108860 | 셀바스AI | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 109070 | 주성코퍼레이션 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6345 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109080 | 옵티시스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5743 | industry | not_low_confidence | us_market_relative_proxy |
| 109610 | 에스와이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 109670 | 씨싸이트 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.604 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 109740 | 디에스케이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 109820 | 진매트릭스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 109860 | 동일금속 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5663 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109960 | 앱토크롬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 110020 | 전진바이오팜 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 110790 | 크리스에프앤씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5576 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 110990 | 디아이티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 111110 | 호전실업 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111380 | 동인기연 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6408 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111710 | 남화산업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6695 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111770 | 영원무역 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 112040 | 위메이드 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 112190 | KC산업 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5351 | industry_and_business_model | not_low_confidence | not_available |
| 112290 | 와이씨켐 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 112610 | 씨에스윈드 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6548 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 113810 | 디젠스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 114090 | GKL | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6008 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114190 | 강원에너지 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 114450 | 그린생명과학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 114630 | 폴라리스우노 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6072 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114810 | 한솔아이원스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 114840 | 아이패밀리에스씨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6271 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114920 | 대주이엔티 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 115160 | 휴맥스 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4914 | industry | not_low_confidence | us_market_relative_proxy |
| 115180 | 큐리언트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 115310 | 인포바인 | Telecommunications | T AT&T | MEDIUM 0.594 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115440 | 우리넷 | Telecommunications | T AT&T | MEDIUM 0.4906 | industry | not_low_confidence | us_market_relative_proxy |
| 115450 | HLB테라퓨틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 115480 | 씨유메디칼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 115500 | 케이씨에스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 115530 | 씨엔플러스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 115570 | 스타플렉스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4995 | industry | not_low_confidence | us_market_relative_proxy |
| 115610 | 이미지스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 116100 | 태양기계 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 117580 | 대성에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 117670 | 알파칩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 117730 | 티로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 118000 | 메타케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 118990 | 모트렉스 | Automobiles | GM General Motors | MEDIUM 0.5545 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119500 | 포메탈 | Machinery and Industrial Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 119610 | 인터로조 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 119650 | KC코트렐 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 119830 | 아이텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 119850 | 지엔씨에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 120030 | 조선선재 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 120110 | 코오롱인더 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 120115 | 코오롱인더우 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 120240 | 대정화금 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 121060 | 유니포인트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 121440 | 골프존홀딩스 | Retail | WMT Walmart | MEDIUM 0.5134 | industry | not_low_confidence | us_market_relative_proxy |
| 121600 | 나노신소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 121800 | 비덴트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 121850 | 코이즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 121890 | 에스디시스템 | Software | MSFT Microsoft | MEDIUM 0.4885 | industry | not_low_confidence | us_market_relative_proxy |
| 122310 | 제노레이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 122350 | 삼기 | Telecommunications | T AT&T | MEDIUM 0.5318 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 122450 | KX | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 122640 | 예스티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 122690 | 서진오토모티브 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 122830 | 원포유 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 122870 | 와이지엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5296 | industry | not_low_confidence | us_market_relative_proxy |
| 122900 | 아이마켓코리아 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 122990 | 와이솔 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 123010 | 알엔티엑스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 123040 | 엠에스오토텍 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 123330 | 제닉 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 123410 | 코리아에프티 | Automobiles | GM General Motors | MEDIUM 0.5443 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123420 | 위메이드플레이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 123570 | 이엠넷 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5618 | industry | not_low_confidence | us_market_relative_proxy |
| 123690 | 한국화장품 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123700 | SJM | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.568 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123750 | 알톤 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.556 | industry | not_low_confidence | us_market_relative_proxy |
| 123840 | 뉴온 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 123860 | 아나패스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 123890 | 한국자산신탁 | Real Estate | RYN Rayonier . REIT | MEDIUM 0.6682 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 124500 | 아이티센글로벌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 124560 | 태웅로직스 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.5882 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 125020 | 티씨머티리얼즈 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 125210 | 아모그린텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 125490 | 한라캐스트 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 126340 | 비나텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 126560 | 현대퓨처넷 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5098 | industry | not_low_confidence | us_market_relative_proxy |
| 126600 | BGF에코머티리얼즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 126640 | 화신정공 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 126700 | 하이비젼시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 126720 | 수산인더스트리 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 126730 | 코칩 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 126880 | 제이엔케이글로벌 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 127120 | 제이에스링크 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 127710 | 아시아경제 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5617 | industry | not_low_confidence | us_market_relative_proxy |
| 127980 | 화인써키트 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 128540 | 에코캡 | Logistics and Transportation | VIA Via Transportation | MEDIUM 0.6015 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 128660 | 피제이메탈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 128820 | 대성산업 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 128940 | 한미약품 | Biotechnology | BIIB Biogen | MEDIUM 0.4888 | industry | not_low_confidence | us_market_relative_proxy |
| 129260 | 인터지스 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6267 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 129890 | 앱코 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5723 | industry | not_low_confidence | us_market_relative_proxy |
| 129920 | 대성하이텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.56 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 130500 | GH신소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 130580 | 나이스디앤비 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5824 | industry | not_low_confidence | us_market_relative_proxy |
| 130660 | 한전산업 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 130740 | 티피씨글로벌 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 131030 | 옵투스제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131090 | 시큐브 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131100 | 티엔엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5337 | industry | not_low_confidence | us_market_relative_proxy |
| 131180 | 딜리 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 131220 | 대한과학 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131290 | 티에스이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 131370 | 알서포트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 131400 | 이브이첨단소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 131760 | 파인텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 131970 | 두산테스나 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 133750 | 메가엠디 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 133820 | 화인베스틸 | Shipbuilding | GD General Dynamics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 134060 | 이퓨쳐 | Software | MSFT Microsoft | MEDIUM 0.4856 | industry | not_low_confidence | us_market_relative_proxy |
| 134380 | 미원화학 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 134580 | 탑코미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5426 | industry | not_low_confidence | partial_direct_similarity |
| 134790 | 시디즈 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5569 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 136150 | 원일티엔아이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 136410 | 아셈스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5941 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136480 | 하림 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6439 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136490 | 선진 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136540 | 윈스테크넷 | Telecommunications | T AT&T | MEDIUM 0.594 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136660 | 큐엠씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 137080 | 나래나노텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 137310 | 에스디바이오센서 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 137400 | 피엔티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 137940 | 넥스트아이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 137950 | 제이씨케미칼 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 138040 | 메리츠금융지주 | Banks | C Citigroup | MEDIUM 0.5316 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 138070 | 신진에스엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 138080 | 오이솔루션 | Telecommunications | T AT&T | MEDIUM 0.5397 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 138360 | 앤로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 138610 | 나이벡 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 138930 | BNK금융지주 | Banks | C Citigroup | MEDIUM 0.5552 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 139130 | iM금융지주 | Banks | C Citigroup | MEDIUM 0.5468 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 139480 | 이마트 | Retail | WMT Walmart | MEDIUM 0.5115 | industry | not_low_confidence | us_market_relative_proxy |
| 139670 | 키네마스터 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 139990 | 아주스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 140070 | 서플러스글로벌 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 140410 | 메지온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 140430 | 카티스 | Telecommunications | T AT&T | MEDIUM 0.5436 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 140520 | 대창스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 140610 | 엔솔바이오사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 140660 | 위월드 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 140670 | 알에스오토메이션 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 140860 | 파크시스템스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 141000 | 비아트론 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 141080 | 리가켐바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 142210 | 유니트론텍 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 142280 | 녹십자엠에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 142760 | 모아라이프플러스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 143160 | 아이디스 | Electrical Equipment | AEP American Electric Power | MEDIUM 0.5678 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 143210 | 핸즈코퍼레이션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 143240 | 사람인 | Software | MSFT Microsoft | MEDIUM 0.4814 | industry | not_low_confidence | us_market_relative_proxy |
| 143540 | 영우디에스피 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 144510 | 지씨셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 144960 | 뉴파워프라즈마 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 145020 | 휴젤 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 145170 | 노브랜드 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6325 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145210 | 다이나믹디자인 | Automobiles | F Ford Motor | MEDIUM 0.5298 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145720 | 덴티움 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 145990 | 삼양사 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6079 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 145995 | 삼양사우 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6077 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 146060 | 율촌 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 146320 | 비씨엔씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 147760 | 피엠티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 147830 | 제룡산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 148150 | 세경하이테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 148250 | 알엔투테크놀로지 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 148780 | 비큐AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 148930 | 에이치와이티씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 149010 | 아이케이세미콘 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 149950 | 아바텍 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5524 | industry | not_low_confidence | us_market_relative_proxy |
| 149980 | 하이로닉 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 150900 | 파수AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 151860 | KG에코솔루션 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 153460 | 네이블 | Software | MSFT Microsoft | MEDIUM 0.4908 | industry | not_low_confidence | us_market_relative_proxy |
| 153490 | 우리이앤엘하루틴 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5101 | industry | not_low_confidence | partial_direct_similarity |
| 153710 | 옵티팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 153890 | 져스텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 154030 | 아시아종묘 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6172 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 154040 | 다산솔루에타 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 155650 | 와이엠씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 155660 | DSR | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 156100 | 엘앤케이바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 158430 | 아톤 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 159010 | 아스플로 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 159580 | 제로투세븐 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6127 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 159910 | 에코글로우 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 160190 | 하이젠알앤엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 160550 | NEW | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5201 | industry | not_low_confidence | us_market_relative_proxy |
| 160980 | 싸이맥스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 161000 | 애경케미칼 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 161390 | 한국타이어앤테크놀로지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 161580 | 필옵틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 161890 | 한국콜마 | Biotechnology | BIIB Biogen | MEDIUM 0.4805 | industry | not_low_confidence | us_market_relative_proxy |
| 162120 | 루켄테크놀러지스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5485 | industry_and_business_model | not_low_confidence | not_available |
| 162300 | 신스틸 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 163280 | 에어레인 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 163560 | 동일고무벨트 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4828 | industry | not_low_confidence | us_market_relative_proxy |
| 163730 | 핑거 | Retail | WMT Walmart | MEDIUM 0.4822 | industry | not_low_confidence | us_market_relative_proxy |
| 166090 | 하나머티리얼즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 166480 | 코아스템켐온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 168330 | 내츄럴엔도텍 | Biotechnology | HALO Halozyme Therapeutics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 168360 | 펨트론 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 169330 | 엠브레인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 169670 | 코스텍시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 170030 | 현대공업 | Automobiles | TM Toyota Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 170790 | 파이오링크 | Telecommunications | T AT&T | MEDIUM 0.6127 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 170900 | 동아에스티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 170920 | 엘티씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 171010 | 램테크놀러지 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 171090 | 선익시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 171120 | 라이온켐텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 172670 | 에이엘티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 173130 | 오파스넷 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 173940 | 에프엔씨엔터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 174900 | 앱클론 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 175140 | 휴먼테크놀로지 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 175250 | 아이큐어 | Biotechnology | HALO Halozyme Therapeutics | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 175330 | JB금융지주 | Banks | C Citigroup | MEDIUM 0.532 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 176590 | 코나솔 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 176750 | 듀켐바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 177350 | 베셀 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 177830 | 파버나인 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 177900 | 쓰리에이로직스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 178320 | 서진시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 178600 | 대동고려삼 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6331 | industry_and_business_model | not_low_confidence | not_available |
| 178780 | 일월지엠엘 | Retail | WMT Walmart | MEDIUM 0.5143 | industry | not_low_confidence | us_market_relative_proxy |
| 178920 | PI첨단소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.5712 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 179290 | 엠아이텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 179530 | 애드바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 179720 | 머니무브 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 179900 | 유티아이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 180060 | 탑선 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5543 | industry_and_business_model | not_low_confidence | not_available |
| 180400 | DXVX | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 180640 | 한진칼 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 181710 | NHN | Retail | WMT Walmart | MEDIUM 0.4909 | industry | not_low_confidence | us_market_relative_proxy |
| 182360 | 큐브엔터 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 182400 | 엔케이젠바이오텍코리아 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 183190 | 아세아시멘트 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 183300 | 코미코 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 183490 | 엔지켐생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 184230 | SGA솔루션즈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 185190 | 수프로 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 185490 | 아이진 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 185750 | 종근당 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 186230 | 그린플러스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5864 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 187220 | 디티앤씨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 187270 | 신화콘텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 187420 | HLB제넥스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 187660 | 페니트리움바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 187790 | 나노 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 187870 | 디바이스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 188040 | 바이오포트 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5984 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 188260 | 세니젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 189300 | 인텔리안테크 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 189330 | 씨이랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 189350 | 코셋 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 189690 | 포시에스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 189860 | 서전기전 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 189980 | 흥국에프엔비 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.635 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 190510 | 나무가 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 190650 | 코리아에셋투자증권 | Banks | JPM JP Morgan Chase & | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 191410 | 육일씨엔에쓰 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5282 | industry | not_low_confidence | partial_direct_similarity |
| 191420 | 테고사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 191600 | 블루탑 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 192080 | 더블유게임즈 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5371 | industry | not_low_confidence | us_market_relative_proxy |
| 192250 | 케이사인 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 192390 | 윈하이텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 192400 | 쿠쿠홀딩스 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5645 | industry | not_low_confidence | us_market_relative_proxy |
| 192410 | 오늘이엔엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 192440 | 슈피겐코리아 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 192650 | 드림텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 192820 | 코스맥스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 193250 | 링크드 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 194370 | 제이에스코퍼레이션 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.627 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194480 | 데브시스터즈 | Retail | WMT Walmart | MEDIUM 0.5144 | industry | not_low_confidence | us_market_relative_proxy |
| 194700 | 노바렉스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 195500 | 마니커에프앤지 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6449 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 195870 | 해성디에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 195940 | HK이노엔 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 195990 | 루트K | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 196170 | 알테오젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 196300 | HLB펩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 196450 | 코아시아씨엠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 196490 | 디에이테크놀로지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 196700 | 웹스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 197140 | 디지캡 | Media and Entertainment | NFLX Netflix | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 198080 | 캐프 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 198440 | 강동씨앤엘 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 198940 | 한주라이트메탈 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 199150 | 데이터스트림즈 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 199290 | 바이오프로테크 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 199430 | 케이엔알시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 199480 | 뱅크웨어글로벌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 199550 | 레이저옵텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 199730 | 바이오인프라 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 199800 | 툴젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 199820 | 제일일렉트릭 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 200130 | 콜마비앤에이치 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5076 | industry | not_low_confidence | partial_direct_similarity |
| 200230 | 텔콘RF제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200350 | 아티스트스튜디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4723 | industry | not_low_confidence | us_market_relative_proxy |
| 200470 | 에이팩트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200580 | 메디쎄이 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 200670 | 휴메딕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 200710 | 에이디테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200780 | 비씨월드제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 200880 | 서연이화 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 201490 | 미투온 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6037 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 202960 | 판도라티비 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 203400 | 에이비온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 203450 | 유니온바이오메트릭스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 203650 | 드림시큐리티 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 203690 | 아크솔루션스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 204020 | 그리티 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6371 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204270 | 제이앤티씨 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 204320 | HL만도 | Automobiles | GM General Motors | MEDIUM 0.5542 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204610 | 티쓰리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 204620 | 글로벌텍스프리 | Banks | JPM JP Morgan Chase & | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204840 | 지엘팜텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 205100 | 엑셈 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 205470 | 휴마시스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 205500 | 넥써쓰 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 206400 | 베노티앤알 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5523 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 206560 | 덱스터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 206640 | 바디텍메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 206650 | 유바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 206950 | 볼빅 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 207490 | 에이펙스인텍 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5543 | industry_and_business_model | not_low_confidence | not_available |
| 207760 | 미스터블루 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4895 | industry | not_low_confidence | partial_direct_similarity |
| 207940 | 삼성바이오로직스 | Biotechnology | BIIB Biogen | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 208140 | 정다운 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6398 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 208350 | 지란지교시큐리티 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 208370 | 셀바스헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 208640 | 썸에이지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 208710 | 포톤 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 208850 | 이비테크 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5381 | industry_and_business_model | not_low_confidence | not_available |
| 208860 | 다산디엠씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 208890 | 미래엔에듀파트너 | Education Services | LAUR Laureate Education | MEDIUM 0.6303 | industry_and_business_model | not_low_confidence | not_available |
| 209640 | 와이제이링크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 210120 | 캔버스엔 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 210540 | 디와이파워 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 210980 | SK디앤디 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 211050 | 인카금융서비스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 211270 | AP위성 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 212310 | 오건에코텍 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 212560 | 네오오토 | Automobiles | GM General Motors | MEDIUM 0.5472 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 212710 | 아이에스티이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 213420 | 덕산네오룩스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 213500 | 한솔제지 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 214150 | 클래시스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214180 | 헥토이노베이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214260 | 라파스 | Biotechnology | HALO Halozyme Therapeutics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 214270 | FSN | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 214320 | 이노션 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5653 | industry | not_low_confidence | us_market_relative_proxy |
| 214330 | 금호에이치티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 214370 | 케어젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4628 | industry | not_low_confidence | not_available |
| 214390 | 경보제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214420 | 토니모리 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6241 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214430 | 아이쓰리시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 214450 | 파마리서치 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 214610 | 롤링스톤 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 214680 | 디알텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 215000 | 골프존 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5997 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215090 | 솔디펜스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 215100 | 로보로보 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 215200 | 메가스터디교육 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 215360 | 우리산업 | Automobiles | GM General Motors | MEDIUM 0.5503 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215380 | 우정바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 215480 | 토박스코리아 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5736 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 215570 | 크로넥스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 215600 | 신라젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 215790 | 이노인스트루먼트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 216050 | 인크로스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.565 | industry | not_low_confidence | us_market_relative_proxy |
| 216080 | 제테마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 216400 | 인바이츠바이오코아 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 217190 | 제너셈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 217270 | 넵튠 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.515 | industry | not_low_confidence | partial_direct_similarity |
| 217320 | 썬테크 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5381 | industry_and_business_model | not_low_confidence | not_available |
| 217330 | 싸이토젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 217480 | 에스디생명공학 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5493 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 217500 | 러셀 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 217590 | 티엠씨 | Shipbuilding | GD General Dynamics | MEDIUM 0.485 | industry | not_low_confidence | partial_direct_similarity |
| 217730 | 강스템바이오텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 217820 | 원익피앤이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 217880 | 틸론 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 217910 | 에스제이켐 | Specialty Chemicals | DOW Dow | MEDIUM 0.5867 | industry_and_business_model | not_low_confidence | not_available |
| 217950 | 파마리서치바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.4844 | industry | not_low_confidence | us_market_relative_proxy |
| 218150 | 미래생명자원 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6362 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 218410 | RFHIC | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 219130 | 타이거일렉 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 219420 | 링크제니시스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 219550 | 디와이디 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 219750 | 한국비티비 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 220100 | 퓨쳐켐 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 220180 | 핸디소프트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 220260 | 켐트로스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 221800 | 지구홀딩스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 221840 | 하이즈항공 | Software | DAL Delta Air Lines | LOW 0.2869 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 221980 | 케이디켐 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6247 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222040 | 코스맥스엔비티 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5226 | industry | not_low_confidence | partial_direct_similarity |
| 222080 | SFA넥셀 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 222110 | 팬젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 222160 | NPX | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 222420 | 쎄노텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 222670 | 플럼라인생명과학 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 222800 | 심텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 222980 | 한국맥널티 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 223220 | 로지스몬 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.6175 | industry_and_business_model | not_low_confidence | not_available |
| 223250 | 드림씨아이에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 223310 | 사토시홀딩스 | Household and Personal Products | UAL United Airlines Holdings | LOW 0.125 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 224060 | 더코디 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4921 | industry | not_low_confidence | partial_direct_similarity |
| 224110 | 에이텍모빌리티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 224760 | 엔에스컴퍼니 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5335 | industry_and_business_model | not_low_confidence | not_available |
| 224810 | 엄지하우스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5335 | industry_and_business_model | not_low_confidence | not_available |
| 225190 | LK삼양 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5261 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 225220 | 제놀루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 225430 | 케이엠제약 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 225530 | HC보광산업 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 225570 | 넥슨게임즈 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 225590 | 패션플랫폼 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6134 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226320 | 잇츠한불 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226330 | 신테카바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 226340 | 본느 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 226400 | 오스테오닉 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 226590 | 엠디바이스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 226950 | 올릭스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 227420 | 도부 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6056 | industry_and_business_model | not_low_confidence | not_available |
| 227610 | 아우딘퓨쳐스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5567 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 227840 | 현대코퍼레이션홀딩스 | Telecommunications | T AT&T | MEDIUM 0.4894 | industry | not_low_confidence | us_market_relative_proxy |
| 227950 | 엔투텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 228340 | 동양파일 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5779 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 228670 | 레이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 228760 | 지노믹트리 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 228850 | 레이언스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 229000 | 젠큐릭스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 229500 | 노브메타파마 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 229640 | LS에코에너지 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 230240 | 에치에프알 | Telecommunications | VZ Verizon Communications | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 232140 | 와이씨 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 232530 | 이엠티 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5543 | industry_and_business_model | not_low_confidence | not_available |
| 232680 | 라온로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 232830 | 아이티센피엔에스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 233250 | 메디안디노스틱 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 233990 | 질경이 | Specialty Chemicals | DOW Dow | MEDIUM 0.5965 | industry_and_business_model | not_low_confidence | not_available |
| 234030 | 싸이닉솔루션 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 234070 | 에이원큐브텍 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6269 | industry_and_business_model | not_low_confidence | not_available |
| 234080 | JW생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234100 | 폴라리스세원 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 234300 | 에스트래픽 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234340 | 헥토파이낸셜 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234690 | 녹십자웰빙 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 234920 | 자이글 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4642 | industry | not_low_confidence | us_market_relative_proxy |
| 235980 | 메드팩토 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 236030 | 씨알푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6289 | industry_and_business_model | not_low_confidence | not_available |
| 236200 | 슈프리마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 236340 | 메디젠휴먼케어 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 236810 | 엔비티 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.493 | industry | not_low_confidence | partial_direct_similarity |
| 237690 | 에스티팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 237750 | 피앤씨테크 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 237820 | 플레이디 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5773 | industry | not_low_confidence | us_market_relative_proxy |
| 237880 | 클리오 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6291 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238090 | 앤디포스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 238120 | 얼라인드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 238200 | 비피도 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 238490 | 힘스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 238500 | 솔루믹스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 239340 | 이스트에이드 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4819 | industry | not_low_confidence | us_market_relative_proxy |
| 239610 | 에이치엘사이언스 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.5554 | industry | not_low_confidence | us_market_relative_proxy |
| 239890 | 피엔에이치테크 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 240550 | 동방메디컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 240600 | 유진테크놀로지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 240810 | 원익IPS | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 241520 | DSC인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 241560 | 두산밥캣 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 241590 | 화승엔터프라이즈 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6044 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 241690 | 유니테크노 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 241710 | 코스메카코리아 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6443 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241770 | 메카로 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 241790 | 티이엠씨씨엔에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 241820 | 피씨엘 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 241840 | 에이스토리 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 242040 | 나무기술 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 243070 | 휴온스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 243840 | 신흥에스이씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 243870 | 아이티센코어 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 244460 | 올리패스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 244880 | 나눔테크 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 244920 | 에이플러스에셋 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 245450 | 씨앤에스링크 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 245620 | EDGC | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 246250 | 에스엘에스바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 246690 | TS인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 246710 | 티앤알바이오팹 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 246720 | 아스타 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 246960 | SCL사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 247540 | 에코프로비엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 247660 | 나노씨엠에스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 248070 | 솔루엠 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 248170 | 샘표식품 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6493 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 249420 | 일동제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 250000 | 보라티알 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 250030 | 진코스텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.6554 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 250060 | 모비스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 250930 | 예선테크 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 251120 | 바이오에프디엔씨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4859 | industry | not_low_confidence | us_market_relative_proxy |
| 251270 | 넷마블 | Interactive Entertainment | GME GameStop | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 251280 | 안지오랩 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 251370 | 와이엠티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 251630 | 브이원텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 251970 | 펌텍코리아 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5417 | industry | not_low_confidence | us_market_relative_proxy |
| 252500 | 세화피앤씨 | Retail | WMT Walmart | MEDIUM 0.5106 | industry | not_low_confidence | us_market_relative_proxy |
| 252990 | 샘씨엔에스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 253450 | 스튜디오드래곤 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5268 | industry | not_low_confidence | us_market_relative_proxy |
| 253590 | 네오셈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 253610 | 루트락 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 253840 | 수젠텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 254120 | 자비스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 254160 | 제이엠멀티 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 254490 | 미래반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 255220 | SG | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5462 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 255440 | 야스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 256150 | 한독크린텍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 256630 | 포인트엔지니어링 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 256840 | 한국비엔씨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 256940 | 킵스파마 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 257370 | 피엔티엠에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 257720 | 실리콘투 | Retail | WMT Walmart | MEDIUM 0.5001 | industry | not_low_confidence | us_market_relative_proxy |
| 258050 | 테크트랜스 | Metals and Materials | ALB Albemarle | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 258610 | 케일럼 | Machinery and Industrial Equipment | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 258790 | 소프트캠프 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 258830 | 세종메디칼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 259630 | 엠플러스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 259960 | 크래프톤 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5739 | industry | not_low_confidence | us_market_relative_proxy |
| 260660 | 알리코제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 260870 | SK시그넷 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5671 | industry_and_business_model | not_low_confidence | not_available |
| 260930 | 씨티케이 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5554 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 260970 | 에스앤디 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6662 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 261200 | 덴티스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 261520 | 이지스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 261780 | 아리바이오랩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 262260 | 에이프로 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 262840 | 아이퀘스트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263020 | 디케이앤디 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263050 | 유틸렉스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 263600 | 덕우전자 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 263690 | 디알젬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263700 | 케어랩스 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.4807 | industry | not_low_confidence | partial_direct_similarity |
| 263720 | 디앤씨미디어 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5855 | industry | not_low_confidence | us_market_relative_proxy |
| 263750 | 펄어비스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 263770 | 유에스티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 263800 | 데이타솔루션 | Software | MSFT Microsoft | MEDIUM 0.4855 | industry | not_low_confidence | us_market_relative_proxy |
| 263810 | 상신전자 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5553 | industry | not_low_confidence | us_market_relative_proxy |
| 263860 | 지니언스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 263920 | 휴엠앤씨 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6047 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 264450 | 유비쿼스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 264660 | 씨앤지하이테크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 264850 | 이랜시스 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.5481 | industry | not_low_confidence | us_market_relative_proxy |
| 264900 | 크라운제과 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6368 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 265520 | AP시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 265560 | 영화테크 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 265740 | 엔에프씨 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 266170 | 레드우즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5185 | industry | not_low_confidence | us_market_relative_proxy |
| 266350 | 팡스카이 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 266470 | 바이오인프라생명과학 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 267080 | 세븐브로이맥주 | Food and Beverage | TAP Molson Coors Beverage | HIGH 0.7444 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267250 | HD현대 | Shipbuilding | GD General Dynamics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 267260 | HD현대일렉트릭 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 267270 | HD건설기계 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 267290 | 경동도시가스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 267320 | 나인테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 267790 | 배럴 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6145 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267850 | 아시아나IDT | Telecommunications | T AT&T | MEDIUM 0.5503 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267980 | 매일유업 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.66 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 268280 | 미원에스씨 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 269620 | 시스웍 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 270210 | 에스알바이오텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.4652 | industry | not_low_confidence | not_available |
| 270520 | 앱튼 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 270660 | 에브리봇 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 270870 | 뉴트리 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.5691 | industry | not_low_confidence | us_market_relative_proxy |
| 271560 | 오리온 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6585 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271830 | 팸텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 271940 | 일진하이솔루스 | Logistics and Transportation | VIA Via Transportation | MEDIUM 0.5995 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271980 | 제일약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 272110 | 케이엔제이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 272210 | 한화시스템 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 272290 | 이녹스첨단소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 272450 | 진에어 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 272550 | 삼양패키징 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6421 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 273060 | 와이즈버즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5768 | industry | not_low_confidence | us_market_relative_proxy |
| 273640 | 와이엠텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 274090 | 켄코아에어로스페이스 | Metals and Materials | DAL Delta Air Lines | LOW 0.1308 | generic_or_mismatch | domain_mismatch | partial_direct_similarity |
| 274400 | 이노시뮬레이션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 275630 | 에스에스알 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 276040 | 스코넥 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4639 | industry | not_low_confidence | us_market_relative_proxy |
| 276240 | 엘리비젼 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 276730 | 한울앤제주 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 277070 | 린드먼아시아 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 277410 | 인산가 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6341 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 277810 | 레인보우로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 277880 | 티에스아이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 278280 | 천보 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 278470 | 에이피알 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6575 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 278650 | HLB바이오스텝 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 278990 | EMB | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.6358 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 279060 | 이노벡스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 279570 | 케이뱅크 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 279600 | 미디어젠 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 280360 | 롯데웰푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6574 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 281740 | 레이크머티리얼즈 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 281820 | 케이씨텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 282330 | BGF리테일 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6463 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 282720 | 금양그린파워 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 282880 | 코윈테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 284620 | 카이노스메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 284740 | 쿠쿠홈시스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 285130 | SK케미칼 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 285490 | 노바텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 285800 | 진영 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 286750 | 나노실리칸첨단소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 286940 | 롯데이노베이트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 287840 | 인투셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 288180 | 케이피항공산업 | Software | DAL Delta Air Lines | LOW 0.2886 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 288330 | 파라택시스코리아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 288620 | 에스프리즘 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 288980 | 모아데이타 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 289010 | 아이스크림에듀 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.49 | industry | not_low_confidence | partial_direct_similarity |
| 289080 | SV인베스트먼트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 289170 | 바이오텐 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5156 | industry | not_low_confidence | not_available |
| 289220 | 자이언트스텝 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4924 | industry | not_low_confidence | us_market_relative_proxy |
| 289930 | 웨이비스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290090 | 트윔 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.5179 | industry | not_low_confidence | us_market_relative_proxy |
| 290120 | DH오토리드 | Automobiles | GM General Motors | MEDIUM 0.5456 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290270 | 휴네시온 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 290520 | 신도기연 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 290550 | 디케이티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 290560 | 파라택시스이더리움 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.6176 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290650 | 엘앤씨바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290660 | 다이나믹솔루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290670 | 대보마그네틱 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 290690 | 소룩스 | Telecommunications | T AT&T | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290720 | 푸드나무 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 290740 | 액트로 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 291230 | 엔피 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.493 | industry | not_low_confidence | partial_direct_similarity |
| 291650 | 압타머사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 291810 | 핀텔 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 293480 | 하나제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 293490 | 카카오게임즈 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 293580 | 나우IB | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 293780 | 압타바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 294090 | 이오플로우 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 294140 | 레몬 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 294570 | 쿠콘 | Telecommunications | T AT&T | MEDIUM 0.5805 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294630 | 서남 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 294870 | IPARK현대산업개발 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5843 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 295310 | 에이치브이엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 296160 | 프로젠 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 296520 | 가이아코퍼레이션 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 296640 | 이노에이엑스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 297090 | 씨에스베어링 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 297570 | 아틀라스링크 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5766 | industry | not_low_confidence | us_market_relative_proxy |
| 297890 | HB솔루션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 298000 | 효성화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.5642 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 298020 | 효성티앤씨 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 298040 | 효성중공업 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.4893 | industry | not_low_confidence | us_market_relative_proxy |
| 298050 | HS효성첨단소재 | Specialty Chemicals | DOW Dow | MEDIUM 0.5593 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 298060 | 풍전약품 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 298380 | 에이비엘바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 298540 | 더네이쳐홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6322 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298690 | 에어부산 | Logistics and Transportation | DAL Delta Air Lines | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 298830 | 슈어소프트테크 | Software | MSFT Microsoft | MEDIUM 0.4968 | industry | not_low_confidence | us_market_relative_proxy |
| 299030 | 하나기술 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 299170 | 더블유에스아이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 299480 | 지앤이헬스케어 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.4656 | industry | not_low_confidence | not_available |
| 299660 | 셀리드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 299900 | 위지윅스튜디오 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 300080 | 플리토 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 300120 | 라온피플 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 300720 | 한일시멘트 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 301300 | 바이브컴퍼니 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 302430 | 이노메트리 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 302440 | SK바이오사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 302550 | 리메드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 302920 | 더콘텐츠온 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5037 | industry | not_low_confidence | not_available |
| 303030 | 지니틱스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 303360 | 프로티아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 303530 | 이노뎁 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 303810 | 동국생명과학 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 304100 | 솔트룩스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 304360 | 에스바이오메딕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 304840 | 피플바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 305090 | 마이크로디지탈 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 306040 | 에스제이그룹 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5657 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 306200 | 세아제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 306620 | 지아이에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 307180 | 아이엘 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 307280 | 원바이오젠 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 307750 | 국전 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 307870 | 비투엔 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 307930 | 컴퍼니케이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 307950 | 현대오토에버 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 308080 | 바이젠셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 308100 | 형지글로벌 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 308170 | 씨티알모빌리티 | Automobiles | GM General Motors | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 308430 | 셀비온 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 309710 | 아이티켐 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 309930 | 조이웍스앤코 | Household and Personal Products | DAL Delta Air Lines | LOW 0.1226 | generic_or_mismatch | domain_mismatch | us_market_relative_proxy |
| 309960 | LB인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 310200 | 애니플러스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5275 | industry | not_low_confidence | us_market_relative_proxy |
| 310210 | 보로노이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 310870 | 디와이씨 | Automobiles | GM General Motors | MEDIUM 0.5464 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311060 | 엘에이티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 311320 | 지오엘리먼트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 311390 | 네오크레마 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6446 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311690 | CJ 바이오사이언스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 311960 | 인터로이드 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 312610 | 에이에프더블류 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 313760 | 캐리 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 314130 | 지놈앤컴퍼니 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 314140 | 알피바이오 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5467 | industry | not_low_confidence | us_market_relative_proxy |
| 314930 | 바이오다인 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 315640 | 딥노이드 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 316140 | 우리금융지주 | Telecommunications | T AT&T | MEDIUM 0.6233 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 317120 | 라닉스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 317240 | TS트릴리온 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5735 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317330 | 덕산테코피아 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 317400 | 자이에스앤디 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5719 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317450 | 명인제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 317530 | 에피소드컴퍼니 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 317690 | 퀀타매트릭스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 317770 | 엑스페릭스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5211 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317830 | 에스피시스템스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 317850 | 대모 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5666 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317860 | 노드메이슨 | Specialty Chemicals | DOW Dow | MEDIUM 0.7151 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317870 | 엔바이오니아 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 318000 | KBG | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 318010 | 팜스빌 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5361 | industry | not_low_confidence | partial_direct_similarity |
| 318020 | 포인트모바일 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 318060 | 그래피 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 318160 | 셀바이오휴먼텍 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5271 | industry | not_low_confidence | us_market_relative_proxy |
| 318410 | 비비씨 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 318660 | 타임기술 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 319400 | 현대무벡스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 319660 | 피에스케이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 320000 | 한울반도체 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 321260 | 프로이천 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 321370 | 센서뷰 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 321550 | 티움바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 321820 | 아티스트컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 322000 | HD현대에너지솔루션 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 322180 | LS티라유텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 322310 | 오로스테크놀로지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 322510 | 제이엘케이 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 322780 | 코퍼스코리아 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 322970 | 무진메디 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 323280 | 태성 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 323350 | 다원넥스뷰 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 323410 | 카카오뱅크 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 323990 | 박셀바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 326030 | SK바이오팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.504 | industry | not_low_confidence | us_market_relative_proxy |
| 327260 | RF머트리얼즈 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 327610 | 펨토바이오메드 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 328130 | 루닛 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 328380 | 솔트웨어 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 329180 | HD현대중공업 | Shipbuilding | GD General Dynamics | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 330350 | 위더스제약 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 330730 | 스톤브릿지벤처스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 330860 | 네패스아크 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 331380 | 포커스에이아이 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 331520 | 밸로프 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 331660 | 한국미라클피플사 | Specialty Chemicals | DOW Dow | MEDIUM 0.594 | industry_and_business_model | not_low_confidence | not_available |
| 331740 | 아우토크립트 | Telecommunications | T AT&T | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 331920 | 셀레믹스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 332190 | 오션스바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 332290 | 누보 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6272 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 332370 | 아이디피 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 332570 | PS일렉트로닉스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 333050 | 이노테나 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 333430 | 일승 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 333620 | 엔시스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 334970 | 프레스티지바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 335810 | 프리시젼바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 335870 | 윙스풋 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 336040 | 타스컴 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 336060 | 웨이버스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 336260 | 두산퓨얼셀 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 336370 | 솔루스첨단소재 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 336570 | 원텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 336680 | 탑런토탈솔루션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 337840 | 유엑스엔 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 337930 | 젝시믹스 | Hotels, Restaurants, and Leisure | TRV The Travelers Companies | MEDIUM 0.5506 | industry | not_low_confidence | us_market_relative_proxy |
| 338220 | 뷰노 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 338840 | 와이바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 339770 | 교촌에프앤비 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 339950 | 아이비김영 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.5726 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 340360 | 다보링크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 340440 | 세림B&G | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5631 | industry | not_low_confidence | us_market_relative_proxy |
| 340450 | 지씨지놈 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 340570 | 티앤엘 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 340810 | 시선AI | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 340930 | 성원에너텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 341170 | 퓨쳐메디신 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 342870 | 오아 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 344820 | KCC글라스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 344860 | 이노진 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 346010 | 타이드 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 347000 | 센코 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 347700 | 스피어 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 347740 | 피엔케이피부임상연구센타 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5126 | industry | not_low_confidence | us_market_relative_proxy |
| 347770 | 핌스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 347850 | 디앤디파마텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 347860 | 알체라 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 347890 | 엠엑스온 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 348030 | 모비릭스 | Interactive Entertainment | GME GameStop | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 348080 | 큐라티스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 348150 | 고바이오랩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 348210 | 넥스틴 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 348340 | 뉴로메카 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 348350 | 위드텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 348370 | 엔켐 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 351020 | 미쥬 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7233 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 351320 | 넥사다이내믹스 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 351330 | 이삭엔지니어링 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 351870 | 차이커뮤니케이션 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5633 | industry | not_low_confidence | us_market_relative_proxy |
| 352090 | 스톰테크 | Retail | WMT Walmart | MEDIUM 0.4971 | industry | not_low_confidence | us_market_relative_proxy |
| 352480 | 씨앤씨인터내셔널 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.633 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352700 | 씨앤투스 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 352770 | 셀레스트라 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 352820 | 하이브 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4922 | industry | not_low_confidence | partial_direct_similarity |
| 352910 | 오비고 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 352940 | 인바이오 | Retail | WMT Walmart | MEDIUM 0.4932 | industry | not_low_confidence | us_market_relative_proxy |
| 353190 | 휴럼 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5664 | industry | not_low_confidence | us_market_relative_proxy |
| 353200 | 대덕전자 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 353590 | 오토앤 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 353810 | 이지바이오 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 354200 | 엔젠바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 354320 | 알멕 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 354390 | 바스칸바이오제약 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 355150 | 코스텍시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 355390 | 크라우드웍스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 355690 | 에이텀 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 356680 | 엑스게이트 | Telecommunications | T AT&T | MEDIUM 0.5886 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 356860 | 티엘비 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 356890 | 싸이버원 | Telecommunications | T AT&T | MEDIUM 0.5397 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 357230 | 에이치피오 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5288 | industry | not_low_confidence | us_market_relative_proxy |
| 357550 | 석경에이티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 357580 | 아모센스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 357780 | 솔브레인 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 357880 | SKAI | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 358570 | 지아이이노베이션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 359090 | 씨엔알리서치 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 360070 | 탑머티리얼 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 360350 | 코셈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 361390 | 제노코 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 361570 | 알비더블유 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 361610 | SK아이이테크놀로지 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.5768 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 361670 | 삼영에스앤씨 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 362320 | 청담글로벌 | Retail | WMT Walmart | MEDIUM 0.5236 | industry | not_low_confidence | us_market_relative_proxy |
| 362990 | 드림인사이트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4968 | industry | not_low_confidence | partial_direct_similarity |
| 363250 | 진시스템 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 363260 | 모비데이즈 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5668 | industry | not_low_confidence | us_market_relative_proxy |
| 363280 | 티와이홀딩스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 364950 | 에이아이코리아 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 365270 | 큐라클 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 365330 | 에스와이스틸텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 365340 | 성일하이텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 365590 | 하이딥 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 365660 | 레몬헬스케어 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 365900 | 브이씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 366030 | 나인앤컴퍼니 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.63 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 367000 | 플래티어 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 368600 | 아이씨에이치 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 368770 | 파이버프로 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 368970 | 오에스피 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6389 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 369370 | 블리츠웨이엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 370090 | 퓨런티어 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 371950 | 풍원정밀 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 372170 | 윤성에프앤씨 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 372320 | 큐로셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 372800 | 아이티아이즈 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 372910 | 한컴라이프케어 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 373110 | 엑셀세라퓨틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 373160 | 데이원컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5685 | industry | not_low_confidence | us_market_relative_proxy |
| 373170 | 엠아이큐브솔루션 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 373200 | 엑스플러스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 373220 | LG에너지솔루션 | Telecommunications | T AT&T | MEDIUM 0.6211 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 375500 | DL이앤씨 | Construction and Engineering | ECG Everus Construction Group | MEDIUM 0.5906 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376180 | 피코그램 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 376270 | HEM파마 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 376290 | 씨유테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 376300 | 디어유 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5668 | industry | not_low_confidence | us_market_relative_proxy |
| 376900 | 로킷헬스케어 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 376930 | 노을 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 376980 | 원티드랩 | Software | MSFT Microsoft | MEDIUM 0.4898 | industry | not_low_confidence | us_market_relative_proxy |
| 377030 | 비트맥스 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 377220 | 프롬바이오 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 377300 | 카카오페이 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 377330 | 이지트로닉스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 377450 | 리파인 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 377460 | 큐에이드 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 377480 | 마음AI | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 377740 | 바이오노트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 378340 | 필에너지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 378800 | 샤페론 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 378850 | 화승알앤에이 | Automobiles | GM General Motors | MEDIUM 0.5451 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 379390 | 이성씨엔아이 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 380540 | 옵티코어 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 380550 | 뉴로핏 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 381620 | 제닉스로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 381970 | 케이카 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 382150 | 온코크로스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 382480 | 지아이텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 382800 | 지앤비에스 에코 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 382840 | 원준 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 382900 | 범한퓨얼셀 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 383220 | F&F | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6752 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 383310 | 에코프로에이치엔 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 383800 | LX홀딩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 383930 | 디티앤씨알오 | Biotechnology | BIIB Biogen | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 384470 | 코어라인소프트 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 387570 | 파인메딕스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 388050 | 지투파워 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 388210 | 씨엠티엑스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 388610 | 지에프씨생명과학 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5275 | industry | not_low_confidence | us_market_relative_proxy |
| 388720 | 유일로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 388790 | 라이콤 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 388870 | 파로스아이바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389020 | 자람테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 389030 | 지니너스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389140 | 포바이포 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 389260 | 대명에너지 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 389470 | 인벤티지랩 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 389500 | 에스비비테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 389650 | 넥스트바이오메디컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 389680 | 유디엠텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 390110 | 애니메디솔루션 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 391710 | 코닉오토메이션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 393210 | 토마토시스템 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 393890 | 더블유씨피 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 393970 | 대진첨단소재 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 394280 | 오픈엣지테크놀로지 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 394420 | 리센스메디컬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 394800 | 쓰리빌리언 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 396270 | 넥스트칩 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 396300 | 세아메카닉스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 396470 | 워트 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 397030 | 에이프릴바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 397810 | 애드포러스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5307 | industry | not_low_confidence | partial_direct_similarity |
| 398120 | 에스지헬스케어 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 399720 | 가온칩스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 402030 | 코난테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 402340 | SK스퀘어 | Retail | WMT Walmart | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 402420 | 켈스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 402490 | 그린리소스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 403360 | 라피치 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 403490 | 우듬지팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 403550 | 쏘카 | Logistics and Transportation | CVLG Covenant Logistics Group | MEDIUM 0.6264 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 403810 | 아이엘로보틱스 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 403850 | 더핑크퐁컴퍼니 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.532 | industry | not_low_confidence | us_market_relative_proxy |
| 403870 | HPSP | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 405000 | 플라즈맵 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 405100 | 큐알티 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 405920 | 나라셀라 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 406820 | 뷰티스킨 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.5589 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 407400 | 꿈비 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 408470 | 한패스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 408900 | 스튜디오미르 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 408920 | 메쎄이상 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 411080 | 샌즈랩 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 412350 | 레이저쎌 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 412540 | 제일엠앤에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 413300 | 티엘엔지니어링 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 413390 | 엠오티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 413630 | 씨피시스템 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 413640 | 비아이매트릭스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 415380 | 스튜디오삼익 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 416180 | 신성에스티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 417010 | 나노팀 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 417180 | 핑거스토리 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5945 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417200 | LS머트리얼즈 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 417500 | 제이아이테크 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 417790 | 트루엔 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 417840 | 저스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 417860 | 오브젠 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 417970 | 모델솔루션 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 418250 | 시큐레터 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 418420 | 라온텍 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 418470 | KT밀리의서재 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.574 | industry | not_low_confidence | us_market_relative_proxy |
| 418550 | 제이오 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 418620 | E8 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5425 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 419050 | 삼기에너지솔루션즈 | Automobiles | TM Toyota Motor | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 419080 | 엔젯 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 419120 | 산돌 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 419530 | SAMG엔터 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5405 | industry | not_low_confidence | us_market_relative_proxy |
| 419540 | 비스토스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 420570 | 제이투케이바이오 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5421 | industry | not_low_confidence | us_market_relative_proxy |
| 420770 | 기가비스 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 424760 | 벨로크 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 424870 | 이뮨온시아 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 424960 | 스마트레이더시스템 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 424980 | 마이크로투나노 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 425040 | 티이엠씨 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 425420 | 티에프이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 429270 | 시지트로닉스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 430690 | 한싹 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 431190 | 케이쓰리아이 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 432430 | 와이랩 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4831 | industry | not_low_confidence | us_market_relative_proxy |
| 432470 | 케이엔에스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 432720 | 퀄리타스반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 432980 | 엠에프씨 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 434190 | 탈로스 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.5543 | industry_and_business_model | not_low_confidence | not_available |
| 434480 | 모니터랩 | Software | MSFT Microsoft | MEDIUM 0.4802 | industry | not_low_confidence | us_market_relative_proxy |
| 435570 | 에르코스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 437730 | 삼현 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 438700 | 버넥트 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 439090 | 마녀공장 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6119 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 439260 | 대한조선 | Shipbuilding | GD General Dynamics | MEDIUM 0.5077 | industry | not_low_confidence | us_market_relative_proxy |
| 439580 | 블루엠텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 439960 | 코스모로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 440110 | 파두 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 440290 | HB인베스트먼트 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 440320 | 오픈놀 | Consumer Electronics and Appliances | AAPL Apple | MEDIUM 0.4909 | industry | not_low_confidence | partial_direct_similarity |
| 441270 | 파인엠텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 443060 | HD현대마린솔루션 | Shipbuilding | GD General Dynamics | MEDIUM 0.5068 | industry | not_low_confidence | us_market_relative_proxy |
| 443250 | 레뷰코퍼레이션 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5794 | industry | not_low_confidence | us_market_relative_proxy |
| 443670 | 에스피소프트 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 444530 | 심플랫폼 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 445090 | 에이직랜드 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 445180 | 퓨릿 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 445680 | 큐리옥스바이오시스템즈 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 446070 | 유니드비티플러스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 446440 | 에피바이오텍 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 446540 | 메가터치 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 446840 | 지슨 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 447690 | 아이오바이오 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 448280 | 에코아이 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 448710 | 코츠테크놀로지 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 448780 | 마이크로엔엑스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 448900 | 한국피아이엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 450080 | 에코프로머티 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 450330 | 하스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 450520 | 인스웨이브 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 450950 | 아스테라시스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 451220 | 아이엠티 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 451250 | 삐아 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6117 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 451760 | 컨텍 | Telecommunications | T AT&T | MEDIUM 0.5301 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452160 | 제이엔비 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 452190 | 한빛레이저 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 452200 | 민테크 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452260 | 한화갤러리아 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.627 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452280 | 한선엔지니어링 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452300 | 캡스톤파트너스 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 452400 | 이닉스 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 452430 | 사피엔반도체 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452450 | 피아이이 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 453340 | 현대그린푸드 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.6645 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 453450 | 그리드위즈 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 453860 | 에이에스텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 454910 | 두산로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 455180 | 케이지에이 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 455900 | 엔젤로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 456010 | 아이씨티케이 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456040 | OCI | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 456070 | 이엔셀 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 456160 | 지투지바이오 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456190 | 큐라켐 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 456570 | 아이엠지티 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 457190 | 이수스페셜티케미컬 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 457370 | 한켐 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 457550 | 우진엔텍 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 457600 | 벡트 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 458350 | 에스팀 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5286 | industry | not_low_confidence | us_market_relative_proxy |
| 458650 | 성우 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 458870 | 씨어스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.4804 | industry | not_low_confidence | us_market_relative_proxy |
| 459100 | 위츠 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 459510 | 나우로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 459550 | 알트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5086 | industry | not_low_confidence | us_market_relative_proxy |
| 460470 | 아이빔테크놀로지 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 460850 | 동국씨엠 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 460860 | 동국제강 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 460870 | 에스엠씨지 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5248 | industry | not_low_confidence | us_market_relative_proxy |
| 460930 | 현대힘스 | Shipbuilding | GD General Dynamics | MEDIUM 0.5143 | industry | not_low_confidence | us_market_relative_proxy |
| 460940 | 피앤에스로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 461030 | 아이엠비디엑스 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 461300 | 아이스크림미디어 | Retail | WMT Walmart | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 462310 | 뉴키즈온 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.5769 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 462350 | 이노스페이스 | Machinery and Industrial Equipment | DAL Delta Air Lines | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 462510 | 라메디텍 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 462520 | 조선내화 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5012 | industry | not_low_confidence | us_market_relative_proxy |
| 462860 | 더즌 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 462870 | 시프트업 | Interactive Entertainment | GLPI Gaming and Leisure Properties | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 462980 | 아이지넷 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 463020 | 뉴엔AI | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 463480 | 모티브링크 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 464080 | 에스오에스랩 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | not_available |
| 464280 | 티디에스팜 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 464490 | 쿼드메디슨 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 464500 | 아이언디바이스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 464580 | 닷밀 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5202 | industry | not_low_confidence | us_market_relative_proxy |
| 465320 | 교보15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 465480 | 인스피언 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 465770 | STX그린로지스 | Logistics and Transportation | VIA Via Transportation | MEDIUM 0.642 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 466100 | 클로봇 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 466410 | 사이냅소프트 | Software | MSFT Microsoft | MEDIUM 0.4828 | industry | not_low_confidence | us_market_relative_proxy |
| 466690 | 키움히어로제1호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 467930 | IBKS제23호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 468530 | 프로티나 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 468760 | 유진스팩10호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 469480 | IBKS제24호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 469610 | 이노테크 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 469750 | 아이비젼웍스 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 469880 | 하나30호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 469900 | 하나31호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 471050 | 대신밸런스제17호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 471820 | 셀로맥스사이언스 | Food and Beverage | MNST Monster Beverage | MEDIUM 0.5493 | industry | not_low_confidence | us_market_relative_proxy |
| 472220 | 신영스팩10호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 472230 | 에스케이증권제11호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 472850 | 폰드그룹 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6496 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 473000 | 에스케이증권제12호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 473050 | 유안타제15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 473950 | 에스케이증권제13호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 473980 | 노머스 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.5299 | industry | not_low_confidence | us_market_relative_proxy |
| 474170 | 루미르 | Shipbuilding | GD General Dynamics | MEDIUM 0.5065 | industry | not_low_confidence | partial_direct_similarity |
| 474490 | 유안타제16호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 474610 | RF시스템즈 | Software | MSFT Microsoft | MEDIUM 0.4843 | industry | not_low_confidence | us_market_relative_proxy |
| 474650 | 링크솔루션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 474660 | 신한제12호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 474930 | 신한제13호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475040 | 스트라드비젼 | Semiconductors | INTC Intel | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 475150 | SK이터닉스 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 475230 | 엔알비 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475240 | 하나32호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475250 | 하나33호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475400 | 씨메스로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 475430 | 키스트론 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 475460 | 미트박스 | Retail | WMT Walmart | MEDIUM 0.5157 | industry | not_low_confidence | us_market_relative_proxy |
| 475560 | 더본코리아 | Food and Beverage | TAP Molson Coors Beverage | MEDIUM 0.6221 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475580 | 에이럭스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 475660 | 에스켐 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
| 475830 | 오름테라퓨틱 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 475960 | 토모큐브 | Biotechnology | BIIB Biogen | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 476040 | 오가노이드사이언스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 476060 | 온코닉테라퓨틱스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 476080 | M83 | Telecommunications | T AT&T | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 476710 | 타조이엔터테인먼트 | Media and Entertainment | DIS Walt Disney (The) | MEDIUM 0.4954 | industry | not_low_confidence | not_available |
| 476830 | 알지노믹스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 477340 | 에이치엠씨제7호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477380 | 미래에셋비전스팩4호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477470 | 미래에셋비전스팩5호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477760 | DB금융스팩12호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 477850 | 마키나락스 | Semiconductors | TSM Taiwan Semiconductor Manufacturing | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 478110 | 이베스트스팩6호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 478340 | 나라스페이스테크놀로지 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 478390 | KB제29호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 478440 | 미래에셋비전스팩6호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 478560 | 블랙야크아이앤씨 | Software | MSFT Microsoft | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 479880 | 한국제15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 479960 | 위너스일렉 | Electrical Equipment | POR Portland General Electric | MEDIUM 0.6118 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 480370 | 씨케이솔루션 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.42 | sector | not_low_confidence | us_market_relative_proxy |
| 481070 | 에이유브랜즈 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.6389 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 481890 | 엔에이치스팩31호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482520 | 교보16호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482630 | 삼양엔씨켐 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482680 | 미래에셋비전스팩7호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 482690 | 대신밸런스제19호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 483650 | 달바글로벌 | Household and Personal Products | ELF e.l.f. Beauty | MEDIUM 0.661 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 484120 | 도우인시스 | Semiconductors | INTC Intel | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 484130 | 하나34호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 484590 | 삼양컴텍 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 484810 | 티엑스알로보틱스 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 484870 | 엠앤씨솔루션 | Software | MSFT Microsoft | MEDIUM 0.485 | industry | not_low_confidence | us_market_relative_proxy |
| 486630 | KB제30호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 486990 | 노타 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 487360 | 신한제14호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 487570 | HS효성 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 487580 | 폴레드 | Logistics and Transportation | JBHT J.B. Hunt Transport Services | MEDIUM 0.5774 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 487720 | 키움제10호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 487830 | 신한제15호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 488060 | 유진스팩11호 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 488280 | 에스투더블유 | Software | MSFT Microsoft | MEDIUM 0.46 | industry | not_low_confidence | us_market_relative_proxy |
| 488900 | 비츠로넥스텍 | Energy Infrastructure | XOM Exxon Mobil | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489210 | 교보17호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489460 | 바이오비쥬 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 489480 | 키움제11호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489500 | 엘케이켐 | Metals and Materials | ALB Albemarle | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489730 | 디비금융제13호스팩 | Financial Services | JPM JP Morgan Chase & | MEDIUM 0.48 | sector | not_low_confidence | partial_direct_similarity |
| 489790 | 한화비전 | Machinery and Industrial Equipment | CAT Caterpillar | MEDIUM 0.48 | sector | not_low_confidence | us_market_relative_proxy |
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
| 499790 | GS피앤엘 | Hotels, Restaurants, and Leisure | WH Wyndham Hotels & Resorts | MEDIUM 0.6686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
