# 글로벌 피어 전종목 현재 결과

## 성능 요약
- 모델 버전: `global-peer-hybrid-ranker-20260630171118`
- 시도/성공/실패: 3967 / 3967 / 0
- 성공률: 1.0
- confidence 분포: {'HIGH': 775, 'LOW': 899, 'MEDIUM': 2293}
- LOW confidence 비율: 0.22662
- domain match 분포: {'generic_or_mismatch': 899, 'industry': 339, 'industry_and_business_model': 2729}
- confidence root cause 분포: {'not_low_confidence': 3068, 'source_profile_generic_or_legacy': 899}
- generic/mismatch 비율: 0.22662
- financial context 분포: {'direct_financial_similarity': 77, 'domain_first_proxy': 75, 'not_available': 1056, 'partial_direct_similarity': 383, 'us_market_relative_proxy': 2376}
- specific profile 품질: {'profile_definition': 'source sector/industry가 generic legacy fallback이 아닌 종목', 'minimum_profile_count': 2500, 'actual_profile_count': 3068, 'maximum_low_confidence_ratio': 0.02, 'actual_low_confidence_ratio': 0.0, 'low_confidence_count': 0, 'status': 'pass'}
- 동일회사 중복 노이즈: 0
- quality status: `pass`

## 전체 종목 결과
| 종목코드 | 종목명 | 원천 세부 분야 | primary peer | confidence | domain match | confidence root cause | financial context |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 000010 | 신한은행 | Banks | USB U.S. Bancorp | HIGH 0.7527 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000020 | 동화약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6871 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000030 | 우리은행 | Banks | USB U.S. Bancorp | HIGH 0.7527 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000040 | KR모터스 | Automobiles | F Ford Motor | MEDIUM 0.6112 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000050 | 경방 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000060 | 메리츠화재해상보험 | Insurance | NP Neptune Insurance Holdings . Class A | HIGH 0.7297 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000070 | 삼양홀딩스 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6968 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000080 | 하이트진로 | Food and Beverage | FIZZ National Beverage | HIGH 0.849 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000100 | 유한양행 | Biotechnology | ZBH Zimmer Biomet Holdings | HIGH 0.7576 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000110 | 한국스탠다드차타드은행 | Banks | USB U.S. Bancorp | HIGH 0.7522 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000120 | CJ대한통운 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | HIGH 0.7828 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000140 | 하이트진로홀딩스 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8429 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000150 | 두산 | Investment Holding Companies | OSK Oshkosh (Holding ) | HIGH 0.77 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000180 | 성창기업지주 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.5447 | industry | not_low_confidence | partial_direct_similarity |
| 0001A0 | 덕양에너젠 | Energy Infrastructure | OIS Oil States International | MEDIUM 0.6713 | industry | not_low_confidence | us_market_relative_proxy |
| 000210 | DL | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.735 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000220 | 유유제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6787 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000230 | 일동홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6595 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000240 | 한국앤컴퍼니 | Automobiles | GPI Group 1 Automotive | HIGH 0.7727 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000250 | 삼천당제약 | Biotechnology | ZBH Zimmer Biomet Holdings | HIGH 0.7557 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000270 | 기아 | Automobiles | ALV Autoliv | HIGH 0.8052 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000300 | DH오토넥스 | Automobiles | GPI Group 1 Automotive | HIGH 0.76 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000320 | 노루홀딩스 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.752 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000360 | 삼환기업 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 000370 | 한화손해보험 | Insurance | NP Neptune Insurance Holdings . Class A | HIGH 0.7967 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000380 | 대아건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 000390 | SP삼화 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7371 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000400 | 롯데손해보험 | Insurance | THG Hanover Insurance Group | HIGH 0.8039 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000420 | 로케트전기 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | not_available |
| 000430 | 대원강업 | Automobiles | GPI Group 1 Automotive | HIGH 0.7382 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000440 | 중앙에너비스 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.6213 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000470 | 그린손해보험 | Insurance | SIGI Selective Insurance Group | MEDIUM 0.6348 | industry_and_business_model | not_low_confidence | not_available |
| 000480 | 시알홀딩스 | Metals and Materials | OI O-I Glass | HIGH 0.7531 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000490 | 대동 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6611 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0004V0 | 엔비알모션 | Automobiles | F Ford Motor | MEDIUM 0.6606 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0004Y0 | 디비금융제14호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000500 | 가온전선 | Electrical Equipment | LECO Lincoln Electric Holdings, . Common Shares | HIGH 0.7699 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000520 | 삼일제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.618 | industry | not_low_confidence | us_market_relative_proxy |
| 000540 | 흥국화재 | Insurance | GSHD Goosehead Insurance, . Class A | HIGH 0.7841 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000590 | CS홀딩스 | Metals and Materials | KRT Karat Packaging | MEDIUM 0.6771 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000610 | 제일화재해상보험 | Insurance | SIGI Selective Insurance Group | MEDIUM 0.6348 | industry_and_business_model | not_low_confidence | not_available |
| 000640 | 동아쏘시오홀딩스 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7589 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000650 | 천일고속 | Logistics and Transportation | HTLD Heartland Express | HIGH 0.8432 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000660 | SK하이닉스 | Semiconductors | MU Micron Technology | HIGH 0.8857 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 000670 | 영풍 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.6998 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000680 | LS네트웍스 | Banks | FVCB FVCBankcorp | MEDIUM 0.6841 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000700 | 유수홀딩스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.718 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000720 | 현대건설 | Software | AIT Applied Industrial Technologies | HIGH 0.7765 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000760 | 이화산업 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.6135 | industry | not_low_confidence | partial_direct_similarity |
| 000790 | 씨앤상선 | Logistics and Transportation | GXO GXO Logistics | MEDIUM 0.6978 | industry_and_business_model | not_low_confidence | not_available |
| 0007C0 | 아크릴 | Software | PAR PAR Technology | MEDIUM 0.7009 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0007J0 | 인벤테라 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000800 | 경남기업 | Listed Operating Company | TVC Tennessee Valley Authority | LOW 0.2116 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 000810 | 삼성화재해상보험 | Insurance | THG Hanover Insurance Group | HIGH 0.8054 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000830 | 삼성물산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.112 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 000850 | 화천기공 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6635 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000860 | 강남제비스코 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7342 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000880 | 한화 | Investment Holding Companies | CCK Crown Holdings | HIGH 0.764 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000890 | 보해양조 | Food and Beverage | FLO Flowers Foods | HIGH 0.8233 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0008Z0 | 에스엔시스 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6599 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000910 | 유니온 | Metals and Materials | WS Worthington Steel, . Common Shares | MEDIUM 0.667 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000950 | 전방 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6162 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 000970 | 한국주철관공업 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 000990 | DB하이텍 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7111 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0009K0 | 에임드바이오 | Biotechnology | CPRX Catalyst Pharmaceuticals | MEDIUM 0.6633 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001000 | 신라섬유 | Real Estate | CLDT Chatham Lodging Trust (REIT) Common Shares of Beneficial Interest | MEDIUM 0.6402 | industry | not_low_confidence | us_market_relative_proxy |
| 001020 | 페이퍼코리아 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.5593 | industry | not_low_confidence | partial_direct_similarity |
| 001040 | CJ | Investment Holding Companies | CCK Crown Holdings | HIGH 0.7545 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001060 | JW중외제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001070 | 대한방직 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6273 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001080 | 만호제강 | Metals and Materials | OI O-I Glass | MEDIUM 0.704 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0010F0 | 보원케미칼 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6841 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0010V0 | 제이피아이헬스케어 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001120 | LX인터내셔널 | Retail | SPSC SPS Commerce | HIGH 0.794 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001130 | 대한제분 | Food and Beverage | BGS B&G Foods | HIGH 0.857 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001140 | 국보 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1888 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 001150 | 서통 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 001190 | 마이크로닉스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 0011A0 | 액스비스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5514 | industry | not_low_confidence | us_market_relative_proxy |
| 0011T0 | 채비 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5187 | industry | not_low_confidence | partial_direct_similarity |
| 001200 | 유진증권 | Banks | ISBA Isabella Bank | HIGH 0.7239 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001210 | 금호전기 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5086 | industry | not_low_confidence | us_market_relative_proxy |
| 001230 | 동국홀딩스 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7463 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001250 | GS글로벌 | Retail | EVCM EverCommerce | HIGH 0.7614 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001260 | 남광토건 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001270 | 부국증권 | Banks | ISBA Isabella Bank | MEDIUM 0.7077 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001280 | 우리증권 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 001290 | 상상인증권 | Banks | GBFH GBank Financial Holdings | MEDIUM 0.6269 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001300 | 제일모직 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 001310 | 풍림산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 001340 | PKC | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001360 | 삼성제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.5661 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001370 | FnC코오롱 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 001380 | SG글로벌 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001390 | KG케미칼 | Automobiles | SMP Standard Motor Products | HIGH 0.7464 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0013V0 | 삼진식품 | Food and Beverage | FLO Flowers Foods | HIGH 0.8385 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001420 | 태원물산 | Automobiles | F Ford Motor | MEDIUM 0.597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001430 | 세아베스틸지주 | Metals and Materials | KMT Kennametal | HIGH 0.7799 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001440 | 대한전선 | Electrical Equipment | LECO Lincoln Electric Holdings, . Common Shares | HIGH 0.7723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001450 | 현대해상 | Insurance | ACIC American Coastal Insurance | HIGH 0.8094 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001460 | BYC | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001470 | 삼부토건 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6872 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001490 | 천지산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 001500 | 현대차증권 | Banks | MNSB MainStreet Bancshares | MEDIUM 0.6729 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001510 | SK증권 | Banks | MNSB MainStreet Bancshares | MEDIUM 0.6722 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001520 | 동양 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.6815 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001530 | 디아이동일 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | HIGH 0.7312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001540 | 안국약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6954 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001550 | 조비 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6907 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001560 | 제일연마 | Metals and Materials | WS Worthington Steel, . Common Shares | MEDIUM 0.6872 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001570 | 금양 | Specialty Chemicals | DOW Dow | MEDIUM 0.7178 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001580 | 신광기업 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 001590 | 일화모직공업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 0015G0 | 그린광학 | Software | AIRS AirSculpt Technologies | MEDIUM 0.6972 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0015N0 | 아로마티카 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7283 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0015S0 | 페스카로 | Automobiles | GPI Group 1 Automotive | HIGH 0.7376 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001600 | 서광건설산업 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 001620 | 케이비아이동국실업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6688 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001630 | 종근당홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7041 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001670 | 경남모직 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 001680 | 대상 | Food and Beverage | BGS B&G Foods | HIGH 0.8117 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 001720 | 신영증권 | Banks | NBHC National Bank Holdings | HIGH 0.7355 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001740 | SK네트웍스 | Investment Holding Companies | INGM Ingram Micro Holding | HIGH 0.7318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001750 | 한양증권 | Banks | FVCB FVCBankcorp | HIGH 0.7337 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001770 | SHD | Metals and Materials | OI O-I Glass | MEDIUM 0.563 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001780 | 알루코 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7367 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001790 | 대한제당 | Food and Beverage | BGS B&G Foods | HIGH 0.8677 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001800 | 오리온홀딩스 | Food and Beverage | FIZZ National Beverage | HIGH 0.8416 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001810 | 무림SP | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.5961 | industry | not_low_confidence | partial_direct_similarity |
| 001820 | 삼화콘덴서공업 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6302 | industry | not_low_confidence | us_market_relative_proxy |
| 001830 | 동부일렉트로닉스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 001840 | 이화공영 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6517 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001880 | 디엘건설 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.8056 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001890 | 아이파크영창 | Listed Operating Company | CNC Centene | LOW 0.195 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 001940 | KISCO홀딩스 | Metals and Materials | OI O-I Glass | MEDIUM 0.7031 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 001950 | 남한제지 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 001970 | 에스지신성건설 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7219 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 001980 | 대호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 002000 | 생고뱅코리아홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 002020 | 코오롱 | Investment Holding Companies | RAMP LiveRamp Holdings | MEDIUM 0.7048 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002030 | 아세아 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7589 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002070 | 비비안 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 002100 | 경농 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7313 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002140 | 고려산업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7896 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002150 | 도화엔지니어링 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002170 | SYTS | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002200 | 한국수출포장공업 | Software | LSAK Lesaka Technologies | MEDIUM 0.5279 | industry | not_low_confidence | us_market_relative_proxy |
| 002210 | 동성제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5672 | industry | not_low_confidence | us_market_relative_proxy |
| 002220 | 한일철강 | Metals and Materials | OI O-I Glass | HIGH 0.7618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002230 | 피에스텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5761 | industry | not_low_confidence | us_market_relative_proxy |
| 002240 | 고려제강 | Metals and Materials | KMT Kennametal | HIGH 0.7588 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002250 | 알보젠코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 002270 | 롯데푸드 | Food and Beverage | BGS B&G Foods | HIGH 0.7297 | industry_and_business_model | not_low_confidence | not_available |
| 002290 | 삼일기업공사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6325 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002300 | 한국제지 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6398 | industry_and_business_model | not_low_confidence | not_available |
| 002310 | 아세아제지 | Software | ACTG Acacia Research | MEDIUM 0.6019 | industry | not_low_confidence | us_market_relative_proxy |
| 002320 | 한진 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | HIGH 0.7226 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002350 | 넥센타이어 | Automobiles | GPI Group 1 Automotive | HIGH 0.7677 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002360 | SH에너지화학 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5032 | industry | not_low_confidence | us_market_relative_proxy |
| 002380 | 케이씨씨 | Metals and Materials | VMC Vulcan Materials (Holding ) | HIGH 0.7733 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002390 | 한독 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6447 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002410 | 범양건영 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.588 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002420 | 세기상사 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5501 | industry | not_low_confidence | us_market_relative_proxy |
| 002450 | 삼익악기 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.6574 | industry | not_low_confidence | us_market_relative_proxy |
| 002460 | HS화성 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6509 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002480 | 범양사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 002530 | 벽산건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 002540 | 고제 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 002550 | KB손해보험 | Insurance | ACIC American Coastal Insurance | HIGH 0.8045 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002600 | 조흥 | Food and Beverage | FLO Flowers Foods | HIGH 0.8318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002620 | 제일파마홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6811 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002630 | 오리엔트바이오 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5424 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002670 | 미주제강 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 002680 | 한탑 | Food and Beverage | FLO Flowers Foods | HIGH 0.7961 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002690 | 동일제강 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.6466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002700 | 신일전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6484 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002710 | TCC스틸 | Metals and Materials | OI O-I Glass | MEDIUM 0.7184 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 002720 | 국제약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6783 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002760 | 보락 | Food and Beverage | FLO Flowers Foods | HIGH 0.8305 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002780 | 진흥기업 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7201 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002790 | 아모레퍼시픽홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.8043 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002800 | 신신제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6808 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002810 | 삼영무역 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.748 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002820 | SUN&L | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 002840 | 미원상사 | Retail | SPSC SPS Commerce | MEDIUM 0.6291 | industry | not_low_confidence | us_market_relative_proxy |
| 002850 | 영풍산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 002860 | 하나은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5936 | industry_and_business_model | not_low_confidence | not_available |
| 002870 | 신풍 | Software | LX LexinFintech Holdings | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 002880 | 디와이에이 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6421 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002900 | TYM | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6951 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002920 | 유성기업 | Automobiles | F Ford Motor | MEDIUM 0.5737 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 002930 | 삼도물산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 002950 | 두산건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 002960 | 한국쉘석유 | Energy Infrastructure | GASS StealthGas | MEDIUM 0.6599 | industry | not_low_confidence | us_market_relative_proxy |
| 002990 | 금호건설 | Construction and Engineering | GVA Granite Construction Incorporated | MEDIUM 0.7078 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003000 | 부광약품 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7397 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003010 | 혜인 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6407 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003020 | 남양 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003030 | 세아제강지주 | Metals and Materials | KMT Kennametal | HIGH 0.7492 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003040 | 한일약품공업 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 003050 | 링세오코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003060 | 에이프로젠바이오로직스 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.5466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003070 | 코오롱글로벌 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6783 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003080 | SB성보 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.5739 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003090 | 대웅 | Biotechnology | SEM Select Medical Holdings | HIGH 0.761 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0030R0 | 대신밸류리츠 | Real Estate | NNN NNN REIT | HIGH 0.7936 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003100 | 선광 | Electrical Equipment | POR Portland General Electric | HIGH 0.7825 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003120 | 일성아이에스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6398 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003160 | 디아이 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6928 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003190 | 알앤엘재생의학연구소 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003200 | 일신방직 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003220 | 대원제약 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6805 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003230 | 삼양식품 | Food and Beverage | HRL Hormel Foods | HIGH 0.8555 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003240 | 태광산업 | Machinery and Industrial Equipment | STAG Stag Industrial | MEDIUM 0.705 | industry | not_low_confidence | us_market_relative_proxy |
| 003280 | 흥아해운 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8644 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003300 | 한일홀딩스 | Metals and Materials | KMT Kennametal | HIGH 0.7567 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003310 | 대주산업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7958 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003330 | 하나IB증권 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 003350 | 한국화장품제조 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7491 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003380 | 하림지주 | Food and Beverage | FIZZ National Beverage | HIGH 0.8388 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003410 | 쌍용씨앤이 | Listed Operating Company | OLN Olin | LOW 0.1968 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 003450 | 케이비증권 | Financial Services | PRU Prudential Financial | HIGH 0.754 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003460 | 유화증권 | Banks | PEBO Peoples Bancorp | MEDIUM 0.684 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003470 | 유안타증권 | Banks | ISBA Isabella Bank | MEDIUM 0.7129 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003480 | 한진중공업홀딩스 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.571 | industry | not_low_confidence | us_market_relative_proxy |
| 003490 | 대한항공 | Aerospace and Defense | DINO HF Sinclair | HIGH 0.8226 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003520 | 영진약품 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.7049 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003530 | 한화투자증권 | Banks | NBHC National Bank Holdings | MEDIUM 0.7133 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003540 | 대신증권 | Banks | NBHC National Bank Holdings | HIGH 0.7207 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003550 | LG | Investment Holding Companies | OSK Oshkosh (Holding ) | HIGH 0.7686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003560 | 아이에이치큐 | Listed Operating Company | CNC Centene | LOW 0.1899 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 003570 | SNT다이내믹스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7661 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003580 | HLB글로벌 | Listed Operating Company | CSPI CSP | LOW 0.1695 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 003590 | 광덕물산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003600 | SK | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1134 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003610 | 방림 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7541 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003620 | KG모빌리티 | Automobiles | GPI Group 1 Automotive | HIGH 0.7681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003640 | 유니온스틸 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 003650 | 미창석유공업 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.6325 | industry | not_low_confidence | us_market_relative_proxy |
| 003660 | 고려시멘트 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 003670 | 포스코퓨처엠 | Energy Infrastructure | CHRD Chord Energy | MEDIUM 0.6959 | industry | not_low_confidence | us_market_relative_proxy |
| 003680 | 한성기업 | Food and Beverage | BGS B&G Foods | HIGH 0.8146 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003690 | 코리안리 | Insurance | NP Neptune Insurance Holdings . Class A | HIGH 0.8148 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003720 | 삼영 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7528 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003780 | 진양산업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7461 | industry | not_low_confidence | us_market_relative_proxy |
| 0037T0 | KB제32호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003800 | 에이스침대 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7647 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003830 | 대한화섬 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6508 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 003850 | 보령 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7349 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003900 | 동원데어리푸드 | Food and Beverage | BGS B&G Foods | HIGH 0.7297 | industry_and_business_model | not_low_confidence | not_available |
| 003920 | 남양유업 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8568 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003930 | 부흥 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003940 | 삼양제넥스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 003960 | 사조대림 | Food and Beverage | BGS B&G Foods | HIGH 0.8599 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 003990 | BHK | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1263 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004000 | 롯데정밀화학 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004010 | 롯데미도파 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004020 | 현대제철 | Metals and Materials | VMC Vulcan Materials (Holding ) | HIGH 0.7834 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004060 | SG세계물산 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.627 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004080 | 신흥 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004090 | 한국석유공업 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.6034 | industry | not_low_confidence | us_market_relative_proxy |
| 004100 | 태양금속공업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6866 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004130 | 대덕GDS | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004140 | 동방 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6758 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004150 | 한솔홀딩스 | Investment Holding Companies | BXC Bluelinx Holdings | MEDIUM 0.6956 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004170 | 신세계 | Retail | EVCM EverCommerce | HIGH 0.755 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004190 | 스마텔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 0041B0 | 교보18호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0041J0 | 엘에스스팩1호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0041L0 | 하나35호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004200 | 고려개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 004230 | 세신 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004250 | 엔피씨 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5302 | industry | not_low_confidence | us_market_relative_proxy |
| 004270 | 남성 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 004310 | 현대약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7182 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004320 | 호반산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 004360 | 세방 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.7195 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004370 | 농심 | Food and Beverage | FIZZ National Beverage | HIGH 0.8576 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004380 | 삼익THK | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7437 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004410 | 서울식품공업 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.6553 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004430 | 송원산업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7653 | industry | not_low_confidence | us_market_relative_proxy |
| 004440 | 삼일씨엔에스 | Metals and Materials | OI O-I Glass | MEDIUM 0.6929 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004450 | 삼화왕관 | Software | LX LexinFintech Holdings | MEDIUM 0.5078 | industry | not_low_confidence | us_market_relative_proxy |
| 004490 | 세방전지 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6881 | industry | not_low_confidence | us_market_relative_proxy |
| 0044K0 | 삼성스팩10호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004510 | 디와이홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 004530 | 에스와이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.126 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004540 | 깨끗한나라 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.5129 | industry | not_low_confidence | us_market_relative_proxy |
| 004550 | 대우송도개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 004560 | 현대비앤지스틸 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7458 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004590 | 한국가구 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5665 | industry | not_low_confidence | us_market_relative_proxy |
| 004620 | 캠브리지코오롱 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004650 | 창해에탄올 | Food and Beverage | FLO Flowers Foods | HIGH 0.8281 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004660 | 신동방CP | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004690 | 삼천리 | Energy Infrastructure | MNTK Montauk Renewables | MEDIUM 0.6713 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004700 | 조광피혁 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7823 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004710 | 한솔테크닉스 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5114 | industry | not_low_confidence | us_market_relative_proxy |
| 004720 | 팜젠사이언스 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6503 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004740 | 보루네오가구 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6144 | industry_and_business_model | not_low_confidence | not_available |
| 004770 | 써니전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5259 | industry | not_low_confidence | us_market_relative_proxy |
| 004780 | 대륙제관 | Software | LX LexinFintech Holdings | MEDIUM 0.5007 | industry | not_low_confidence | us_market_relative_proxy |
| 004790 | 렉스엘이앤지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 004800 | 효성 | Investment Holding Companies | UHAL U-Haul Holding | HIGH 0.7651 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004820 | 조인에너지 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 004830 | 덕성 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7228 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004840 | DRB동일 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004870 | 티웨이홀딩스 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.5647 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004890 | 동일산업 | Metals and Materials | OI O-I Glass | MEDIUM 0.67 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004910 | 조광페인트 | Metals and Materials | OI O-I Glass | MEDIUM 0.6322 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 004920 | 씨아이테크 | Software | LX LexinFintech Holdings | MEDIUM 0.5977 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004940 | 하나은행 | Banks | PEBO Peoples Bancorp | HIGH 0.7563 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004960 | 한신공영 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6455 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004970 | 신라교역 | Food and Beverage | BJRI BJ's Restaurants | HIGH 0.8317 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004980 | 성신양회 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7529 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 004990 | 롯데지주 | Investment Holding Companies | RAMP LiveRamp Holdings | HIGH 0.7444 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005010 | 휴스틸 | Metals and Materials | OI O-I Glass | HIGH 0.7701 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005030 | 부산주공 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6831 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005070 | 코스모신소재 | Metals and Materials | KMT Kennametal | MEDIUM 0.6592 | industry | not_low_confidence | partial_direct_similarity |
| 005090 | SGC에너지 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.6088 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005110 | 한창 | Real Estate | FVR FrontView REIT | MEDIUM 0.5796 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005160 | 동국산업 | Metals and Materials | OI O-I Glass | HIGH 0.7453 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005180 | 빙그레 | Food and Beverage | FIZZ National Beverage | HIGH 0.8336 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005190 | 동성화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | not_available |
| 005250 | 녹십자홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7045 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005270 | 아이엠뱅크 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 005280 | 부산은행 | Banks | PEBO Peoples Bancorp | HIGH 0.7671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005290 | 동진쎄미켐 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7116 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005300 | 롯데칠성음료 | Food and Beverage | FIZZ National Beverage | HIGH 0.8466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005320 | 온타이드 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6391 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005330 | 카스코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 005350 | 심팩인더스트리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 005360 | 모나미 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6996 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 005380 | 현대자동차 | Automobiles | TM Toyota Motor | HIGH 0.8081 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005390 | 신성통상 | Listed Operating Company | G Genpact | LOW 0.2061 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 005420 | 코스모화학 | Specialty Chemicals | DOW Dow | HIGH 0.7271 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005430 | 한국공항 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7979 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005440 | 현대지에프홀딩스 | Investment Holding Companies | PAY Paymentus Holdings, . Class A | HIGH 0.7384 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005450 | 신한 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1913 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 005490 | POSCO홀딩스 | Metals and Materials | VMC Vulcan Materials (Holding ) | HIGH 0.7593 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 0054V0 | 엔에이치스팩32호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005500 | 삼진제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7214 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005560 | 제이에스전선 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | not_available |
| 005600 | 중앙제지 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 005610 | 삼립 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8439 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005620 | 대성합동지주 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 005670 | 푸드웰 | Food and Beverage | FLO Flowers Foods | HIGH 0.8413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005680 | 삼영전자공업 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6382 | industry | not_low_confidence | us_market_relative_proxy |
| 005690 | 파미셀 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.8047 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005710 | 대원산업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.71 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005720 | 넥센 | Automobiles | GPI Group 1 Automotive | HIGH 0.7352 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005740 | 크라운해태홀딩스 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8189 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005750 | 대림바스 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.8275 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005760 | 위너스인프라인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 005800 | 신영와코루 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7431 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005810 | 풍산홀딩스 | Metals and Materials | VMC Vulcan Materials (Holding ) | HIGH 0.7464 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005820 | 원림 | Software | LX LexinFintech Holdings | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 005830 | DB손해보험 | Insurance | GSHD Goosehead Insurance, . Class A | HIGH 0.7977 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005850 | 에스엘 | Automobiles | GPI Group 1 Automotive | HIGH 0.787 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005860 | 한일사료 | Food and Beverage | FLO Flowers Foods | HIGH 0.8324 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005870 | 휴니드테크놀러지스 | Software | GOTU Gaotu Techedu | MEDIUM 0.6016 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005880 | 대한해운 | Logistics and Transportation | GXO GXO Logistics | HIGH 0.8305 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005890 | 동원증권 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 005900 | 동양건설산업 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 005930 | 삼성전자 | Semiconductors | MU Micron Technology | HIGH 0.7601 | industry | not_low_confidence | direct_financial_similarity |
| 005940 | NH투자증권 | Banks | MTB M&T Bank | MEDIUM 0.699 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005950 | 이수화학 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7129 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 005960 | 동부건설 | Construction and Engineering | GVA Granite Construction Incorporated | MEDIUM 0.6753 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 005980 | 성지건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 005990 | 매일홀딩스 | Food and Beverage | FLO Flowers Foods | HIGH 0.8197 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006040 | 동원산업 | Machinery and Industrial Equipment | REXR Rexford Industrial Realty | HIGH 0.8092 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006050 | 국영지앤엠 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006060 | 화승인더스트리 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006070 | 기린 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 006090 | 사조오양 | Food and Beverage | FLO Flowers Foods | HIGH 0.8311 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006110 | 삼아알미늄 | Metals and Materials | CLW Clearwater Paper | HIGH 0.7744 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006120 | SK디스커버리 | Energy Infrastructure | MUR Murphy Oil | MEDIUM 0.6446 | industry | not_low_confidence | us_market_relative_proxy |
| 006140 | 피제이전자 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5397 | industry | not_low_confidence | us_market_relative_proxy |
| 006150 | 한메엔에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 006200 | 한국전자홀딩스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5824 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006210 | 휴리프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 006220 | 제주은행 | Banks | GBFH GBank Financial Holdings | HIGH 0.731 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006250 | 극동전선 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | not_available |
| 006260 | LS | Electrical Equipment | LECO Lincoln Electric Holdings, . Common Shares | HIGH 0.7902 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006280 | 녹십자 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7377 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006340 | 대원전선 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7851 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006350 | 전북은행 | Banks | USB U.S. Bancorp | HIGH 0.7528 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006360 | GS건설 | Software | HLIO Helios Technologies | HIGH 0.7259 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006370 | 대구백화점 | Retail | NEGG Newegg Commerce, . Common Shares | HIGH 0.7333 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006380 | 카프로 | Specialty Chemicals | DOW Dow | MEDIUM 0.6893 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006390 | 한일현대시멘트 | Metals and Materials | EXP Eagle Materials | HIGH 0.8183 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006400 | 삼성SDI | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6899 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006440 | 한일건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 006490 | 인스코비 | Telecommunications | OPTU Optimum Communications, . Class A | HIGH 0.7663 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006570 | 대림통상 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.678 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006580 | 대양제지공업 | Machinery and Industrial Equipment | IBM International Business Machines | MEDIUM 0.7058 | industry | not_low_confidence | us_market_relative_proxy |
| 006600 | 동신제약 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 006620 | 동구바이오제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.693 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006650 | 대한유화 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006660 | 삼성공조 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.717 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006730 | 서부T&D | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006740 | 블루산업개발 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 006750 | 센추리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 006800 | 미래에셋증권 | Banks | COLB Columbia Banking System | MEDIUM 0.7151 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006840 | AK홀딩스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5926 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006880 | 신송홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.5518 | industry | not_low_confidence | us_market_relative_proxy |
| 006890 | 태경케미컬 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7144 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0068Y0 | 비엔케이제3호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 006910 | 보성파워텍 | Electrical Equipment | POR Portland General Electric | HIGH 0.7661 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006920 | 모헨즈 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6578 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 006980 | 우성 | Food and Beverage | FLO Flowers Foods | HIGH 0.8213 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007050 | 유리이에스 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 007070 | GS리테일 | Retail | SPSC SPS Commerce | HIGH 0.7748 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0070X0 | 에스테크엠 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 007110 | 일신석재 | Metals and Materials | OI O-I Glass | HIGH 0.7458 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007120 | 미래아이앤지 | Software | DXC DXC Technology | MEDIUM 0.6249 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007150 | 동양텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 007160 | 사조산업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7824 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007190 | 한솔아트원제지 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 0071M0 | 삼성스팩11호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007200 | 진흥저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 007210 | 벽산 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7197 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007280 | 한국특강 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7046 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0072Z0 | KB제33호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 007310 | 오뚜기 | Food and Beverage | FIZZ National Beverage | HIGH 0.8559 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007330 | 푸른저축은행 | Banks | PEBO Peoples Bancorp | HIGH 0.7749 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007340 | DN오토모티브 | Automobiles | GPI Group 1 Automotive | HIGH 0.7846 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007370 | 진양제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6663 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007390 | 네이처셀 | Biotechnology | TH Target Hospitality | MEDIUM 0.647 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007460 | 에이프로젠 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.5724 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007480 | 대한은박지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 007490 | 태창기업 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 007530 | 와이엠 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6875 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007540 | 샘표 | Food and Beverage | FLO Flowers Foods | HIGH 0.8376 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007570 | 일양약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7023 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007590 | 동방아그로 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7029 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007610 | 선도전기 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7519 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007630 | 폴루스바이오팜 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 007640 | 애큐온저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 007660 | 이수페타시스 | Semiconductors | ARW Arrow Electronics | HIGH 0.7275 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007680 | 대원 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6707 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007690 | 국도화학 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7658 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007700 | F&F 홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7914 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007720 | 소노스퀘어 | Listed Operating Company | TISI Team | LOW 0.1713 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 007770 | 한일화학 | Specialty Chemicals | DOW Dow | MEDIUM 0.593 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007800 | 솔로몬저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 007810 | 코리아써키트 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6349 | industry | not_low_confidence | us_market_relative_proxy |
| 007820 | 엠엑스로보틱스 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7202 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007830 | 부산저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 007860 | 서연 | Automobiles | SMP Standard Motor Products | MEDIUM 0.7157 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 007910 | 세원화성 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 007980 | TP | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7127 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008000 | 도레이케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | not_available |
| 008020 | 경남에너지 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 008030 | 아이텍스필 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008040 | 사조동아원 | Food and Beverage | BGS B&G Foods | HIGH 0.8548 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008060 | 대덕 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5206 | industry | not_low_confidence | us_market_relative_proxy |
| 008080 | 에스와이코퍼레이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008110 | 대동전자 | Semiconductors | NXPI NXP Semiconductors N.V | HIGH 0.7859 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008120 | 엠소닉 | Listed Operating Company | MCK McKesson | LOW 0.2073 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 008250 | 이건산업 | Metals and Materials | OI O-I Glass | MEDIUM 0.6085 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008260 | NI스틸 | Metals and Materials | KRT Karat Packaging | MEDIUM 0.7039 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008270 | 산은캐피탈 | Financial Services | GNW Genworth Financial | MEDIUM 0.7013 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008290 | 원풍물산 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 0082N0 | 카나프테라퓨틱스 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6974 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008320 | 한국기술산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 008340 | 대주코레스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008350 | 남선알미늄 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.7036 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008370 | 원풍 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008400 | 씨앤중공업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 008420 | 문배철강 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.6536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008470 | 부스타 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6033 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008490 | 서흥 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6987 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008500 | 일정실업 | Listed Operating Company | AXR AMREP | LOW 0.2448 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 008540 | 케이비물산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008560 | 메리츠증권 | Financial Services | ARI Apollo Commercial Real Estate Finance | HIGH 0.7549 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008600 | 윌비스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 008670 | 신한투자증권 | Financial Services | AXS Axis Capital Holdings | HIGH 0.7244 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008700 | 아남전자 | Semiconductors | KE Kimball Electronics | HIGH 0.7208 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008720 | 삼양엔텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008730 | 율촌화학 | Software | ACTG Acacia Research | MEDIUM 0.604 | industry | not_low_confidence | us_market_relative_proxy |
| 008770 | 호텔신라 | Retail | SPSC SPS Commerce | MEDIUM 0.7198 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008780 | 아이인프라 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008800 | 행남사 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.2007 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 008830 | 대동기어 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6742 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 008870 | 금비 | Software | LX LexinFintech Holdings | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 0088D0 | 메리츠제1호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0088M0 | 메쥬 | Biotechnology | VNDA Vanda Pharmaceuticals | MEDIUM 0.5458 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008900 | 티이씨앤코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 008930 | 한미사이언스 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7544 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 008970 | KBI동양철관 | Metals and Materials | OI O-I Glass | MEDIUM 0.7001 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009010 | 에듀언스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 009070 | 케이씨티시 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6881 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009080 | 퍼시픽글라스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 009140 | 경인전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.603 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009150 | 삼성전기 | Semiconductors | MU Micron Technology | MEDIUM 0.5217 | industry | not_low_confidence | us_market_relative_proxy |
| 009160 | SIMPAC | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7595 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009180 | 한솔로지스틱스 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6703 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009190 | 대양금속 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7001 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0091W0 | 신영스팩11호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009200 | 무림페이퍼 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.606 | industry | not_low_confidence | partial_direct_similarity |
| 009220 | 그로웰전자 | Semiconductors | Q Qnity Electronics | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | not_available |
| 009240 | 한샘 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7643 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009270 | 신원 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009280 | 다함이텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 009290 | 광동제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009300 | 삼아제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6897 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009310 | 참엔지니어링 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5746 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009320 | 아진전자부품 | Semiconductors | KE Kimball Electronics | MEDIUM 0.659 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009360 | 베네데스하이텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 009380 | 아세아페이퍼텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 0093G0 | 미래에셋비전스팩8호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009410 | 태영건설 | Construction and Engineering | ROAD Construction Partners | HIGH 0.7257 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009420 | 한올바이오파마 | Biotechnology | AVAH Aveanna Healthcare Holdings | HIGH 0.7247 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009440 | KC그린홀딩스 | Software | LSAK Lesaka Technologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009450 | 경동나비엔 | Software | REZI Resideo Technologies | MEDIUM 0.6795 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009460 | 한창제지 | Software | LSAK Lesaka Technologies | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 009470 | 삼화전기 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5728 | industry | not_low_confidence | us_market_relative_proxy |
| 009520 | 포스코엠텍 | Metals and Materials | KMT Kennametal | HIGH 0.7534 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009540 | HD한국조선해양 | Software | ACMR ACM Research, . Class A | MEDIUM 0.672 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009580 | 무림P&P | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.5497 | industry | not_low_confidence | partial_direct_similarity |
| 009620 | 삼보산업 | Metals and Materials | OI O-I Glass | MEDIUM 0.6345 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009680 | 모토닉 | Automobiles | GPI Group 1 Automotive | HIGH 0.7371 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009690 | 케이엠에이치 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 0096B0 | 삼성스팩12호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0096D0 | 미래에셋비전스팩9호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.636 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009720 | 한국전기초자 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | not_available |
| 009730 | 이렘 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.5432 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009760 | 한국지주 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 009770 | 삼정펄프 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6589 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009780 | 엠에스씨 | Food and Beverage | FLO Flowers Foods | HIGH 0.8303 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009790 | 휴닉스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 0097F0 | 미래에셋비전스팩10호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009810 | 플레이그램 | Listed Operating Company | SRI Stoneridge | LOW 0.171 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 009830 | 한화솔루션 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7818 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009890 | 맥슨텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 0098T0 | 교보19호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 009900 | 명신산업 | Automobiles | GPI Group 1 Automotive | HIGH 0.7399 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 009940 | 대아리드선 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 009970 | 영원무역홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.8315 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0099W0 | 미래에셋비전스팩11호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0099X0 | IBKS제25호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010040 | 한국내화 | Metals and Materials | OI O-I Glass | HIGH 0.7269 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010050 | 우리종합금융 | Financial Services | Z Zillow Group, . Class C Capital Stock | MEDIUM 0.6968 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010060 | OCI홀딩스 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.6555 | industry | not_low_confidence | us_market_relative_proxy |
| 010090 | 이마트에브리데이 | Listed Operating Company | OLN Olin | LOW 0.1985 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 010100 | 한국무브넥스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7078 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010120 | 엘에스일렉트릭 | Electrical Equipment | FELE Franklin Electric | HIGH 0.7793 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010130 | 고려아연 | Metals and Materials | EXP Eagle Materials | HIGH 0.7413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010140 | 삼성중공업 | Software | TTEK Tetra Tech | MEDIUM 0.6892 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010150 | 포스코티엠씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 010170 | 대한광통신 | Semiconductors | AAOI Applied Optoelectronics | MEDIUM 0.6638 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0101C0 | 하나36호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010200 | 극동제혁 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 010240 | 흥국 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6534 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010280 | 아이티센엔텍 | Software | ACTG Acacia Research | MEDIUM 0.6257 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010400 | 우진아이엔에스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5893 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010420 | 한솔피엔에스 | Listed Operating Company | TISI Team | LOW 0.1909 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 010460 | 화인자산관리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 010470 | 오리콤 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7594 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010520 | 현대하이스코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 010580 | 에스엠벡셀 | Automobiles | GPI Group 1 Automotive | HIGH 0.7406 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0105P0 | 유진스팩12호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010600 | 웰바이오텍 | Biotechnology | AMN AMN Healthcare Services | MEDIUM 0.6162 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010620 | 에이치디현대미포 | Listed Operating Company | G Genpact | LOW 0.2017 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 010640 | 진양폴리우레탄 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010660 | 화천기계 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6339 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010670 | 나노트로닉스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 010690 | 화신 | Automobiles | GPI Group 1 Automotive | HIGH 0.748 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010730 | 금강화섬 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 010770 | 평화홀딩스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6634 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 010780 | 아이에스동서 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6746 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010820 | 퍼스텍 | Software | AIRS AirSculpt Technologies | MEDIUM 0.7109 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 010950 | S-Oil | Energy Infrastructure | AEIS Advanced Energy Industries | MEDIUM 0.6951 | industry | not_low_confidence | us_market_relative_proxy |
| 010960 | 삼호개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6537 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011000 | 진원생명과학 | Biotechnology | BNTC Benitec Biopharma | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011020 | 코오롱유화 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 011040 | 경동제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7095 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011050 | 케드콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 011070 | LG이노텍 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.5718 | industry | not_low_confidence | us_market_relative_proxy |
| 011080 | 형지I&C | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011090 | 에넥스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.5532 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011150 | CJ씨푸드 | Food and Beverage | BJRI BJ's Restaurants | HIGH 0.8374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011160 | 두산건설 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.779 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011170 | 롯데케미칼 | Specialty Chemicals | DOW Dow | HIGH 0.789 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011200 | HMM | Logistics and Transportation | GXO GXO Logistics | HIGH 0.8561 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011210 | 현대위아 | Automobiles | GPI Group 1 Automotive | HIGH 0.771 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011230 | 삼화전자공업 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4858 | industry | not_low_confidence | us_market_relative_proxy |
| 011280 | 태림포장 | Software | LSAK Lesaka Technologies | MEDIUM 0.5488 | industry | not_low_confidence | us_market_relative_proxy |
| 011300 | 우성머티리얼스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6726 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 011320 | 유니크 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6967 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011330 | 유니켐 | Automobiles | F Ford Motor | MEDIUM 0.5854 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011370 | 서한 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6247 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011390 | 부산산업 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011400 | 아진카인텍 | Listed Operating Company | MCK McKesson | LOW 0.2098 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 011420 | 갤럭시아에스엠 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.6385 | industry | not_low_confidence | us_market_relative_proxy |
| 011500 | 한농화성 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7401 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011560 | 세보엠이씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6923 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0115H0 | 삼성스팩13호 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 011690 | 와이투솔루션 | Semiconductors | MEI Methode Electronics | MEDIUM 0.544 | industry | not_low_confidence | us_market_relative_proxy |
| 011700 | 한신기계공업 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7193 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011720 | 현대페인트 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 011760 | 현대코퍼레이션 | Retail | EVCM EverCommerce | HIGH 0.7788 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011780 | 금호석유화학 | Energy Infrastructure | NOG Northern Oil and Gas | MEDIUM 0.6907 | industry | not_low_confidence | us_market_relative_proxy |
| 011790 | SKC | Energy Infrastructure | VNOM Viper Energy, . Class A | MEDIUM 0.6406 | industry | not_low_confidence | us_market_relative_proxy |
| 011800 | 배명금속 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 011810 | STX | Retail | NEGG Newegg Commerce, . Common Shares | HIGH 0.7815 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 011930 | 신성이엔지 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6802 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 012030 | DB | Software | ACTG Acacia Research | MEDIUM 0.7178 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012090 | 성원건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 0120G0 | 삼양바이오팜 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.6512 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012160 | 영흥 | Metals and Materials | OI O-I Glass | MEDIUM 0.5942 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 012170 | 아센디오 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | MEDIUM 0.7159 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012200 | 계양전기 | Automobiles | F Ford Motor | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012210 | 삼미금속 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7182 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012250 | 셰프라인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 012280 | 영화금속 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6714 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012320 | 경동인베스트 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7202 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012330 | 현대모비스 | Automobiles | ALV Autoliv | HIGH 0.8014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012340 | 뉴인텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 012400 | 허메스홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 012410 | 글로스텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 012420 | 메리츠종합금융 | Financial Services | ARI Apollo Commercial Real Estate Finance | MEDIUM 0.5678 | industry_and_business_model | not_low_confidence | not_available |
| 012450 | 한화에어로스페이스 | Software | DELL Dell Technologies . Class C | MEDIUM 0.7008 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012460 | 우영 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 012510 | 더존비즈온 | Software | PRGS Progress Software | HIGH 0.7432 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012580 | 신세계톰보이 | Listed Operating Company | QH Quhuo American Depository Shares | LOW 0.2066 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 012600 | 청호ICT | Listed Operating Company | VFC V.F | LOW 0.1933 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 012610 | 경인양행 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7167 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012620 | 원일특강 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.6599 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012630 | HDC | Construction and Engineering | ROAD Construction Partners | HIGH 0.7543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012650 | 쌍용건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 012690 | 모나리자 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7149 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0126Z0 | 삼성에피스홀딩스 | Biotechnology | ZBH Zimmer Biomet Holdings | MEDIUM 0.7024 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 012700 | 리드코프 | Energy Infrastructure | OIS Oil States International | MEDIUM 0.6306 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012720 | 건영 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 012750 | 에스원 | Software | REZI Resideo Technologies | MEDIUM 0.7162 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012760 | 하스코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 012790 | 신일제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.683 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012800 | 대창 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7105 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012860 | 모베이스전자 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.7147 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 012990 | LG석유화학 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 0129K0 | 신한제18호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013000 | 세우글로벌 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6907 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013030 | 하이록코리아 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7013 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0130D0 | 신한제17호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 0130H0 | 엔에이치스팩33호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013120 | 동원개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6991 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 0131D0 | 키움히어로제2호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013200 | 우방 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 013240 | 셀런 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 0132G0 | 교보20호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013310 | 아진산업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6825 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013340 | 뉴아세아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 013360 | 일성건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013450 | 동성하이켐 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 013520 | 화승코퍼레이션 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7121 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013570 | 디와이 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6961 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013580 | 계룡건설산업 | Construction and Engineering | GVA Granite Construction Incorporated | MEDIUM 0.6652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013650 | 데코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 013700 | 까뮤이앤씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6392 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013720 | THE CUBE& | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6713 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013780 | 아큐텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 013810 | 스페코 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6791 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013870 | 지엠비코리아 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6861 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 013890 | 지누스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6958 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 013990 | 아가방컴퍼니 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7521 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014010 | 인터피온반도체 | Semiconductors | Q Qnity Electronics | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | not_available |
| 014100 | 메디앙스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014130 | 한익스프레스 | Logistics and Transportation | ULH Universal Logistics Holdings | HIGH 0.7539 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014160 | 대영포장 | Software | LX LexinFintech Holdings | MEDIUM 0.5213 | industry | not_low_confidence | us_market_relative_proxy |
| 014190 | 원익큐브 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6514 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014200 | 광림 | Listed Operating Company | MCK McKesson | LOW 0.2103 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 014280 | 금강공업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.8026 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 014300 | 선진지주 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 014350 | 신일건업 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 014420 | 프로비타 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 014440 | 영보화학 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7649 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014470 | 부방 | Software | LX LexinFintech Holdings | MEDIUM 0.6728 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014530 | 극동유화 | Energy Infrastructure | OIS Oil States International | MEDIUM 0.6293 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014570 | 고려제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.658 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014580 | 태경비케이 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7128 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014590 | 지앤엘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 014620 | 성광벤드 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7341 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014680 | 한솔케미칼 | Energy Infrastructure | NOG Northern Oil and Gas | MEDIUM 0.6767 | industry | not_low_confidence | us_market_relative_proxy |
| 014710 | 사조씨푸드 | Food and Beverage | BGS B&G Foods | HIGH 0.8686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014790 | HL D&I | Construction and Engineering | GVA Granite Construction Incorporated | MEDIUM 0.648 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014820 | 동원시스템즈 | Software | HDSN Hudson Technologies | MEDIUM 0.6428 | industry | not_low_confidence | us_market_relative_proxy |
| 014830 | 유니드 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7402 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014900 | 에스컴 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 014910 | 성문전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5666 | industry | not_low_confidence | us_market_relative_proxy |
| 014940 | 오리엔탈정공 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6522 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014950 | 삼익제약 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6678 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 014970 | 삼륭물산 | Software | LX LexinFintech Holdings | MEDIUM 0.5104 | industry | not_low_confidence | us_market_relative_proxy |
| 014990 | 인디에프 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6167 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 015020 | 이스타코 | Real Estate | XRN Chiron Real Estate | HIGH 0.7357 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015050 | 엘트온 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 015110 | 중앙건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 015170 | 중앙바이오텍 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 015200 | 성원 | Listed Operating Company | MCK McKesson | LOW 0.2027 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 015230 | 대창단조 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.684 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015260 | 에이엔피 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 015350 | 부산도시가스 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 015360 | INVENI | Energy Infrastructure | VTS Vitesse Energy | MEDIUM 0.6542 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015390 | 엘앤씨피 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 015540 | 에코바이브 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 015590 | DKME | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6412 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 015670 | AP우주통신 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 015710 | 코콤 | Software | LX LexinFintech Holdings | MEDIUM 0.5707 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015750 | 성우하이텍 | Automobiles | GPI Group 1 Automotive | HIGH 0.7467 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015760 | 한국전력공사 | Electrical Equipment | FELE Franklin Electric | HIGH 0.8031 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015860 | 일진홀딩스 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7561 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015890 | 태경산업 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7288 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 015940 | 엘지데이콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 016040 | 디에스피이엔티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 016090 | 대현 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7219 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016100 | 리더스코스메틱 | Software | GOTU Gaotu Techedu | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 016140 | 두함지개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 016160 | 오라바이오틱스 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 016170 | 카카오엠 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 016250 | SGC E&C | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6131 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 016360 | 삼성증권 | Banks | PEBO Peoples Bancorp | MEDIUM 0.6872 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016380 | KG스틸 | Metals and Materials | KMT Kennametal | HIGH 0.767 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016420 | NH농협증권 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 016450 | 한세예스24홀딩스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6819 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 016510 | 현대DSF | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 016560 | 서울상호저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 016570 | 에스트라 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 016580 | 환인제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7135 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016590 | 신대양제지 | Software | ACTG Acacia Research | MEDIUM 0.6058 | industry | not_low_confidence | us_market_relative_proxy |
| 016600 | 큐캐피탈 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.651 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016610 | DB증권 | Banks | FVCB FVCBankcorp | HIGH 0.7423 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016670 | 디모아 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6094 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016710 | 대성홀딩스 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5835 | industry | not_low_confidence | us_market_relative_proxy |
| 016740 | 두올 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7004 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016790 | 현대사료 | Food and Beverage | FLO Flowers Foods | HIGH 0.843 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016800 | 퍼시스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.767 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016830 | 한국씨티은행 | Banks | PEBO Peoples Bancorp | HIGH 0.7607 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016880 | 웅진 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.8101 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 016890 | 대웅바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 016920 | 카스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 016970 | 씨크롭 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 016990 | LG마이크론 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 017000 | 신원종합개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5962 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017010 | 제너비오믹스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 017040 | 광명전기 | Electrical Equipment | IE Ivanhoe Electric | MEDIUM 0.5353 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017050 | 스타맥스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 017160 | 세븐코스프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 017170 | 훈영 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 017180 | 명문제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6493 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017250 | 인터엠 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 017300 | 에이치비이에너지 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 017370 | 우신시스템 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6943 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017390 | 서울도시가스 | Energy Infrastructure | CVI CVR Energy | MEDIUM 0.6314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017480 | 삼현철강 | Metals and Materials | OI O-I Glass | MEDIUM 0.7008 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 017510 | 세명전기 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7261 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017550 | 수산세보틱스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6803 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017650 | 대림제지 | Software | LX LexinFintech Holdings | MEDIUM 0.525 | industry | not_low_confidence | us_market_relative_proxy |
| 017670 | SK텔레콤 | Telecommunications | VZ Verizon Communications | HIGH 0.8359 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 017680 | 데코앤에프 | Listed Operating Company | ACH Accendra Health | LOW 0.1905 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 017800 | 현대엘리베이터 | Construction and Engineering | ROAD Construction Partners | MEDIUM 0.642 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 017810 | 풀무원 | Food and Beverage | FLO Flowers Foods | HIGH 0.845 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017860 | DS단석 | Specialty Chemicals | DOW Dow | MEDIUM 0.69 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017890 | 한국알콜 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.741 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017900 | 광전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6185 | industry | not_low_confidence | us_market_relative_proxy |
| 017940 | E1 | Energy Infrastructure | MNTK Montauk Renewables | MEDIUM 0.6702 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 017960 | 한국카본 | Software | AIT Applied Industrial Technologies | MEDIUM 0.6637 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018000 | 유니슨 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.8002 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018120 | 진로발효 | Food and Beverage | FLO Flowers Foods | HIGH 0.8447 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018180 | 텔슨정보통신 | Software | CMTL Comtech Telecommunications | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 018250 | 애경산업 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.8318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018260 | 삼성에스디에스 | Software | ACMR ACM Research, . Class A | MEDIUM 0.7185 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018290 | 브이티 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7397 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018310 | 삼목에스폼 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.841 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018410 | 현대금속 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 018470 | 조일알미늄 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018500 | 동원금속 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.68 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018620 | 우진비앤지 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.5447 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018670 | SK가스 | Energy Infrastructure | CVI CVR Energy | MEDIUM 0.6924 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018680 | 서울제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.5208 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 018700 | 졸스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 018880 | 한온시스템 | Automobiles | GT The Goodyear Tire & Rubber | HIGH 0.7383 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 018890 | 브이오산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 019010 | 베뉴지 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7126 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019120 | 경윤하이드로에너지 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 019170 | 신풍제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7397 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019180 | 티에이치엔 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6969 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019210 | 와이지-원 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.708 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019260 | 셀텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 019300 | 태림페이퍼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 019430 | 위더스기술금융 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 019440 | 세아특수강 | Listed Operating Company | SSTK Shutterstock | LOW 0.1893 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 019490 | 엑시큐어하이트론 | Software | LOT Lotus Technology | MEDIUM 0.5561 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019540 | 일지테크 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6793 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019550 | SBI인베스트먼트 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.6626 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019560 | 한국투자파트너스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 019570 | 플루토스 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.6071 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 019590 | 에스유앤피 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1896 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 019640 | 희훈디앤지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 019660 | 글로본 | Listed Operating Company | POM POMDOCTOR | LOW 0.17 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 019680 | 대교 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5452 | industry | not_low_confidence | us_market_relative_proxy |
| 019770 | 서연탑메탈 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6654 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 019930 | 기라정보통신 | Software | CMTL Comtech Telecommunications | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 019990 | 에너토크 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7052 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020000 | 한섬 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7601 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020070 | 에버리소스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 020120 | 키다리스튜디오 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5937 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020150 | 롯데에너지머티리얼즈 | Semiconductors | AAOI Applied Optoelectronics | MEDIUM 0.5171 | industry | not_low_confidence | us_market_relative_proxy |
| 020180 | 대신정보통신 | Software | ACTG Acacia Research | MEDIUM 0.6129 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020400 | 대동금속 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6117 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020560 | 아시아나항공 | Aerospace and Defense | JBLU JetBlue Airways | HIGH 0.8083 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020710 | 시공테크 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6149 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 020760 | 일진디스플 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.8218 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 021040 | 대호특수강 | Metals and Materials | OI O-I Glass | MEDIUM 0.6891 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021050 | 서원 | Metals and Materials | OI O-I Glass | MEDIUM 0.6959 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021060 | 한림창업투자 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 021080 | 에이티넘인베스트 | Financial Services | JCAP Jefferson Capital | MEDIUM 0.6607 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021240 | 코웨이 | Software | SSNC SS&C Technologies Holdings | HIGH 0.7413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021320 | KCC건설 | Construction and Engineering | GVA Granite Construction Incorporated | MEDIUM 0.6626 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021570 | 알루코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.126 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 021650 | 한국큐빅 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6695 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021820 | 세원정공 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7181 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 021880 | 메이슨캐피탈 | Banks | GBFH GBank Financial Holdings | MEDIUM 0.5606 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 021960 | 케이비캐피탈 | Financial Services | GNW Genworth Financial | MEDIUM 0.7013 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 022100 | 포스코DX | Software | DXC DXC Technology | HIGH 0.7222 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 022220 | 티케이지애강 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.674 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 022520 | 코오롱아이넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 023000 | 삼원강재 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7043 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023020 | 동양매직 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 023150 | MH에탄올 | Food and Beverage | BGS B&G Foods | HIGH 0.8365 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023160 | 태광 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7395 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023350 | 한국종합기술 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.605 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023410 | 유진기업 | Metals and Materials | OI O-I Glass | HIGH 0.7601 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023420 | 유진종합개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 023430 | 아이이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 023440 | 제이스코홀딩스 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6402 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023450 | 동남합성 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7123 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023460 | 씨앤에이치 | Listed Operating Company | CNC Centene | LOW 0.1917 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 023530 | 롯데쇼핑 | Retail | EVCM EverCommerce | HIGH 0.7756 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023590 | 다우기술 | Banks | NBHC National Bank Holdings | MEDIUM 0.7185 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023600 | 삼보판지 | Software | PRTH Priority Technology Holdings | MEDIUM 0.543 | industry | not_low_confidence | us_market_relative_proxy |
| 023670 | 알이네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 023760 | 한국캐피탈 | Banks | FVCB FVCBankcorp | HIGH 0.7311 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023770 | 플레이위드 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 023790 | 동일스틸럭스 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6177 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023800 | 인지컨트롤스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6893 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023810 | 인팩 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023890 | 한국아트라스비엑스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 023900 | 풍국주정 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.714 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023910 | 대한약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7019 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 023960 | 에쓰씨엔지니어링 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6984 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024060 | 흥구석유 | Energy Infrastructure | EGY VAALCO Energy | MEDIUM 0.5995 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024070 | WISCOM | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.5593 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 024090 | 디씨엠 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7134 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024100 | 제일저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 024110 | 기업은행 | Banks | PEBO Peoples Bancorp | MEDIUM 0.6885 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024120 | KB오토시스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6891 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024660 | 하림홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 024720 | 콜마홀딩스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7589 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024740 | 한일단조 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7109 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024800 | 유성티엔에스 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8472 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024810 | 이화전기공업 | Electrical Equipment | EMR Emerson Electric | HIGH 0.7488 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024830 | 세원물산 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7082 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024840 | KBI메탈 | Electrical Equipment | HE Hawaiian Electric Industries | MEDIUM 0.7197 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024850 | HLB이노베이션 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.676 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024870 | 유성티에스아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 024880 | 케이피에프 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.641 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024890 | 대원화성 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6676 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024900 | 디와이덕양 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6752 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024910 | 경창산업 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024940 | PN풍년 | Software | LX LexinFintech Holdings | MEDIUM 0.6345 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 024950 | 삼천리자전거 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.6153 | industry | not_low_confidence | us_market_relative_proxy |
| 025000 | KPX케미칼 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7277 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025270 | 부산방직공업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 025320 | 시노펙스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7138 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025340 | 그린기술투자 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 025440 | DH오토웨어 | Automobiles | F Ford Motor | MEDIUM 0.5622 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025450 | 한마음상호저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 025460 | 팬텀엔터테인먼트그룹 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 025530 | 에스제이엠홀딩스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6842 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025540 | 한국단자공업 | Automobiles | GPI Group 1 Automotive | HIGH 0.7535 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025550 | 한국선재 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.6863 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025560 | 미래산업 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6907 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025610 | 한국저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 025620 | 차AI헬스케어 | Biotechnology | SPRY ARS Pharmaceuticals | MEDIUM 0.5649 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025690 | 동방라이텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 025750 | 한솔홈데코 | Metals and Materials | OI O-I Glass | MEDIUM 0.6991 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025770 | 한국정보통신 | Software | ACTG Acacia Research | MEDIUM 0.7139 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025820 | 이구산업 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7259 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025830 | 한국합섬 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 025850 | 한화화인케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | not_available |
| 025860 | 남해화학 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7603 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025870 | 신라에스지 | Food and Beverage | UNFI United Natural Foods | HIGH 0.785 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025880 | 케이씨피드 | Food and Beverage | FLO Flowers Foods | HIGH 0.8187 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 025890 | 한국주강 | Metals and Materials | OI O-I Glass | MEDIUM 0.6384 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025900 | 동화기업 | Metals and Materials | OI O-I Glass | MEDIUM 0.7158 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025920 | 우경 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 025930 | 팬택자산관리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 025950 | 동신건설 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6944 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 025970 | 알덱스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 025980 | 아난티 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7288 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 026040 | 제이에스티나 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6944 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026150 | 특수건설 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7067 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026180 | 현대정보기술 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 026220 | 에스티씨라이프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 026230 | 아이디에이치 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 026250 | 삼우이엠씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 026260 | 위너지스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 026540 | 제일창업투자 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 026870 | 코원에너지서비스 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 026890 | 스틱인베스트먼트 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.7137 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026910 | 광진실업 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6358 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026940 | 부국철강 | Metals and Materials | OI O-I Glass | MEDIUM 0.6939 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 026960 | 동서 | Food and Beverage | USFD US Foods Holding | HIGH 0.8466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 026970 | 대백저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 027040 | 서울전자통신 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 027050 | 코리아나 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 027350 | 텔슨전자 | Semiconductors | Q Qnity Electronics | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | not_available |
| 027360 | 아주IB투자 | Financial Services | CNO CNO Financial Group | MEDIUM 0.7184 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027390 | 한화갤러리아타임월드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 027410 | BGF | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7578 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027440 | 코리아이앤디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 027580 | 상보 | Specialty Chemicals | DOW Dow | MEDIUM 0.5614 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027700 | 대백쇼핑 | Retail | BURL Burlington Stores | MEDIUM 0.5588 | industry_and_business_model | not_low_confidence | not_available |
| 027710 | 팜스토리 | Food and Beverage | FLO Flowers Foods | HIGH 0.833 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027740 | 마니커 | Food and Beverage | BGS B&G Foods | HIGH 0.8418 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027830 | 대성창투 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.6825 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 027840 | 한국고덴시 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 027970 | 한국제지 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.6391 | industry | not_low_confidence | partial_direct_similarity |
| 028040 | 미래SCI | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 028050 | 삼성E&A | Software | AIT Applied Industrial Technologies | HIGH 0.757 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 028080 | 휴맥스홀딩스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 028090 | 네오퍼플 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 028100 | 동아지질 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6931 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 028150 | 지에스홈쇼핑 | Retail | BURL Burlington Stores | MEDIUM 0.5588 | industry_and_business_model | not_low_confidence | not_available |
| 028260 | 삼성물산 | Investment Holding Companies | OSK Oshkosh (Holding ) | HIGH 0.751 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 028300 | HLB | Biotechnology | VRDN Viridian Therapeutics | MEDIUM 0.6185 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 028670 | 팬오션 | Logistics and Transportation | GXO GXO Logistics | HIGH 0.8508 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029460 | 케이씨 | Semiconductors | FEIM Frequency Electronics | HIGH 0.7256 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029480 | 광무 | Software | LOT Lotus Technology | MEDIUM 0.655 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029530 | 신도리코 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.9112 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029780 | 삼성카드 | Financial Services | WBS Webster Financial | HIGH 0.7883 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 029960 | 코엔텍 | Listed Operating Company | MSFT Microsoft | LOW 0.2146 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 030000 | 제일기획 | Media and Entertainment | MLCO Melco Resorts & Entertainment | HIGH 0.8035 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030030 | 중앙디자인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 030190 | NICE평가정보 | Software | REZI Resideo Technologies | MEDIUM 0.6576 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030200 | 케이티 | Telecommunications | CHTR Charter Communications, . Class A | HIGH 0.8448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030210 | 다올투자증권 | Banks | FVCB FVCBankcorp | HIGH 0.724 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030270 | 에스마크 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 030350 | 드래곤플라이 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 030390 | 쏠라엔텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 030420 | 디패션 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6144 | industry_and_business_model | not_low_confidence | not_available |
| 030520 | 한글과컴퓨터 | Software | RCMT RCM Technologies | MEDIUM 0.7171 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030530 | 원익홀딩스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6518 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 030610 | 교보증권 | Banks | NBHC National Bank Holdings | MEDIUM 0.7157 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030720 | 동원수산 | Food and Beverage | FLO Flowers Foods | HIGH 0.8157 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 030790 | 비케이탑스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 030950 | 보진재 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 030960 | 양지사 | Software | GOTU Gaotu Techedu | MEDIUM 0.6208 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031150 | 국민은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5937 | industry_and_business_model | not_low_confidence | not_available |
| 031210 | 서울보증보험 | Insurance | GSHD Goosehead Insurance, . Class A | HIGH 0.7929 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031310 | 아이즈비전 | Software | LX LexinFintech Holdings | MEDIUM 0.5468 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031330 | 에스에이엠티 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.5876 | industry | not_low_confidence | us_market_relative_proxy |
| 031390 | 녹십자셀 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 031430 | 신세계인터내셔날 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 031440 | 신세계푸드 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6167 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031510 | 오스템 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6727 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031800 | 에스티앤아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 031820 | 아이티센씨티에스 | Software | ACTG Acacia Research | MEDIUM 0.641 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031860 | 디에이치엑스컴퍼니 | Software | LOT Lotus Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031920 | 조은저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 031950 | 에듀패스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 031960 | 동산진흥 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 031970 | 엠바이엔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 031980 | 피에스케이홀딩스 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6921 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 031990 | 대선조선 | Shipbuilding | ONEW OneWater Marine . Class A | MEDIUM 0.7143 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032030 | 일공공일안경콘택트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032040 | 씨앤에스자산관리 | Listed Operating Company | MCK McKesson | LOW 0.2047 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 032050 | 후야인포넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032080 | 아즈텍WB | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6975 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032150 | 으뜸상호저축은행 | Banks | USB U.S. Bancorp | MEDIUM 0.5872 | industry_and_business_model | not_low_confidence | not_available |
| 032180 | 이수세라믹 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032190 | 다우데이타 | Banks | ISBA Isabella Bank | HIGH 0.7232 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032280 | 삼일 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6226 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032290 | 케이디지엠텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032300 | 한국파마 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.5535 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 032350 | 롯데관광개발 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7472 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032380 | 핸디소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032390 | 케이티프리텔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032420 | 터보테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 032500 | 케이엠더블유 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.692 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032540 | TJ미디어 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6075 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032560 | 황금에스티 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7062 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032570 | 카라반케이디이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032580 | 피델릭스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7016 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032590 | 엔토리노 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032600 | 애드모바일 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032610 | 에스오케이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032620 | GC메디아이 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5756 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032640 | LG유플러스 | Telecommunications | CHTR Charter Communications, . Class A | HIGH 0.8378 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032680 | 소프트센 | Software | LSAK Lesaka Technologies | MEDIUM 0.578 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032710 | 신한카드 | Listed Operating Company | SITC SITE Centers | LOW 0.2044 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 032750 | 삼진 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5552 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032790 | 엠젠솔루션 | Software | PAR PAR Technology | MEDIUM 0.5965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032800 | 판타지오 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7205 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032820 | 우리기술 | Software | OPEN Opendoor Technologies | MEDIUM 0.709 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032830 | 삼성생명 | Insurance | THG Hanover Insurance Group | HIGH 0.744 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032850 | 비트컴퓨터 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.4843 | industry | not_low_confidence | us_market_relative_proxy |
| 032860 | 더라미 | Listed Operating Company | POM POMDOCTOR | LOW 0.1693 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 032930 | 에이스앤파트너스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 032940 | 원익 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7396 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 032960 | 동일기연 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 032980 | 바이온 | Software | GOTU Gaotu Techedu | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033020 | 세아메탈 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 033030 | 지오엠씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033050 | 제이엠아이 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6829 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033100 | 제룡전기 | Electrical Equipment | POR Portland General Electric | HIGH 0.7831 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033110 | 코너스톤네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033130 | 디지틀조선 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033160 | 엠케이전자 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7105 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033170 | 시그네틱스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6139 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033180 | 케이에이치필룩스 | Listed Operating Company | QH Quhuo American Depository Shares | LOW 0.2066 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033190 | 폴켐 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033200 | 모아텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 033210 | 삼화기연 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033220 | 피엔에스커튼월 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033230 | 인성정보 | Software | LSAK Lesaka Technologies | MEDIUM 0.6639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033240 | 자화전자 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.663 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033250 | 체시스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6567 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033260 | 쌈지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033270 | 유나이티드 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7059 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033280 | 어울림엘시스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033290 | 로젠 | Logistics and Transportation | KNX Knight-Swift Transportation Holdings | MEDIUM 0.6719 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033310 | 엠투엔 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033320 | 제이씨현시스템 | Software | ACTG Acacia Research | MEDIUM 0.597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033330 | 두림티앤씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033340 | 좋은사람들 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 033430 | 디에스티 | Listed Operating Company | AMZN Amazon.com | LOW 0.2197 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 033500 | 동성화인텍 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7582 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033530 | SJG세종 | Automobiles | GPI Group 1 Automotive | HIGH 0.7227 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033540 | 파라텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.698 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033550 | 일레덱스홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 033560 | 블루콤 | Real Estate | GEO Geo Group (The) REIT | HIGH 0.7652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033600 | 럭슬 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033630 | 에스케이브로드밴드 | Listed Operating Company | G Genpact | LOW 0.2028 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 033640 | 네패스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6865 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033660 | 우리금융캐피탈 | Financial Services | VOYA Voya Financial | HIGH 0.7618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033720 | 블루스톤디앤아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033780 | 케이티앤지 | Food and Beverage | FIZZ National Beverage | HIGH 0.883 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033790 | 피노 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5433 | industry | not_low_confidence | partial_direct_similarity |
| 033830 | 티비씨 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7492 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 033850 | 지노시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 033880 | 룩소네이트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 033920 | 무학 | Food and Beverage | FLO Flowers Foods | HIGH 0.8481 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034010 | 트라이써클 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 034020 | 두산에너빌리티 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7856 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034120 | SBS | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7707 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034220 | LG디스플레이 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.8804 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 034230 | 파라다이스 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.753 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034300 | 신세계건설 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7831 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034310 | NICE | Software | ACTG Acacia Research | MEDIUM 0.708 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034510 | 무한투자 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 034590 | 인천도시가스 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5943 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 034600 | 글로웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 034660 | 제넥셀세인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 034730 | SK | Energy Infrastructure | MUR Murphy Oil | MEDIUM 0.6286 | industry | not_low_confidence | us_market_relative_proxy |
| 034750 | 현대에이치씨엔동작방송 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 034810 | 해성산업 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.6889 | industry | not_low_confidence | partial_direct_similarity |
| 034830 | 한국토지신탁 | Real Estate | FVR FrontView REIT | HIGH 0.7767 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 034940 | 조아제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.4803 | industry | not_low_confidence | us_market_relative_proxy |
| 034950 | 한국기업평가 | Software | SIGA SIGA Technologies | MEDIUM 0.6693 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035000 | HS애드 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7759 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035010 | 소예 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035080 | 그래디언트 | Retail | NEGG Newegg Commerce, . Common Shares | HIGH 0.7795 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035150 | 백산 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035200 | 프럼파스트 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7638 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 035210 | 티브로드도봉강북방송 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 035250 | 강원랜드 | Construction and Engineering | ROAD Construction Partners | MEDIUM 0.6385 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 035270 | 청람디지탈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035290 | 골드앤에스 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 035400 | 쓰리디넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035420 | NAVER | Internet Platforms | GOOGL Alphabet . Class A | HIGH 0.7834 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035430 | 드림라인 | Listed Operating Company | TISI Team | LOW 0.1924 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 035450 | 지아이바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 035460 | 기산텔레콤 | Software | LX LexinFintech Holdings | MEDIUM 0.5329 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035480 | 글로앤웰 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035500 | 써니트렌드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035510 | 신세계I&C | Software | ACTG Acacia Research | MEDIUM 0.6825 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035600 | KG이니시스 | Software | ACTG Acacia Research | MEDIUM 0.7068 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035610 | 솔본 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035620 | 바른손이앤에이 | Media and Entertainment | IHRT iHeartMedia, . Class A | MEDIUM 0.7189 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035710 | 씨엘엘씨디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035720 | 카카오 | Software | TTEK Tetra Tech | MEDIUM 0.7077 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035760 | CJ ENM | Media and Entertainment | INSE Inspired Entertainment | HIGH 0.7813 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035780 | 그로웰텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 035810 | 이지홀딩스 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035830 | 메카포럼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035870 | 호성 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035890 | 서희건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7096 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035900 | JYP Ent. | Media and Entertainment | VSNT Versant Media Group, . Class A | HIGH 0.7757 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 035910 | 현대멀티캡 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035950 | 케이알 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 035960 | 바이오시스 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 036000 | 예림당 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7725 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036010 | 아비코전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5884 | industry | not_low_confidence | us_market_relative_proxy |
| 036020 | 한아시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 036030 | 케이티알파 | Retail | EVCM EverCommerce | HIGH 0.7806 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036060 | 한강구조조정기금 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036090 | 위지트 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036120 | 서울평가정보 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6142 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036170 | 에이치엠넥스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7009 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036180 | 지더블유바이텍 | Listed Operating Company | CNC Centene | LOW 0.1829 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 036190 | 금화피에스시 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6835 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036200 | 유니셈 | Semiconductors | KE Kimball Electronics | HIGH 0.7301 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036210 | 태산엘시디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036220 | 오상헬스케어 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6198 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036260 | 이매진아시아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036270 | 헤쎄나 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036280 | 남산물산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036360 | 쓰리소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036420 | 콘텐트리중앙 | Media and Entertainment | GTN Gray Media | HIGH 0.7671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036460 | 한국가스공사 | Energy Infrastructure | MAN ManpowerGroup | MEDIUM 0.6978 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036480 | 대성미생물 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.644 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036490 | 에스케이머티리얼즈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036500 | 에스에스컴텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036530 | SNT홀딩스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7551 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036540 | SFA반도체 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.6947 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036550 | 에이스디지텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036560 | KZ정밀 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7108 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036570 | NC | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.6857 | industry | not_low_confidence | partial_direct_similarity |
| 036580 | 팜스코 | Food and Beverage | FLO Flowers Foods | HIGH 0.829 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036590 | 케이엔티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036600 | 지니웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036610 | 지디코프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036620 | 감성코퍼레이션 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7672 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036630 | 세종텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | HIGH 0.8023 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 036640 | HRS | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7579 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036660 | 플러스프로핏 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036670 | 삼양케이씨아이 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6966 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036690 | 코맥스 | Software | GOTU Gaotu Techedu | MEDIUM 0.6293 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036710 | 심텍홀딩스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6823 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036720 | 한빛네트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036760 | 케이엔에스홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 036790 | 자강 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036800 | 나이스정보통신 | Software | ACTG Acacia Research | MEDIUM 0.6725 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036810 | 에프에스티 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.7011 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036820 | 비이티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036830 | 솔브레인홀딩스 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5987 | industry | not_low_confidence | us_market_relative_proxy |
| 036840 | 휴코드홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 036850 | 나리지*온 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1216 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036880 | 맥시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 036890 | 진성티이씨 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7108 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 036900 | 이레아이엔씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036910 | 세원텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 036920 | 지앤에스티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 036930 | 주성엔지니어링 | Semiconductors | ARW Arrow Electronics | HIGH 0.7524 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037010 | 넷컴스토리지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037020 | 한와이어리스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037030 | 파워넷 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5684 | industry | not_low_confidence | us_market_relative_proxy |
| 037060 | 시큐어소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037070 | 파세코 | Software | LX LexinFintech Holdings | MEDIUM 0.7107 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037110 | 제이에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037120 | 한신코퍼레이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037150 | 씨제이인터넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037220 | 넥스텔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037230 | 한국팩키지 | Software | LX LexinFintech Holdings | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 037240 | 평안물산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037250 | 대흥멀티미디어통신 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.5798 | industry_and_business_model | not_low_confidence | not_available |
| 037270 | YG PLUS | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.767 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037320 | 시노펙스그린테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 037330 | 인지디스플레 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5913 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037340 | 에이치씨코퍼레이션 | Listed Operating Company | MCK McKesson | LOW 0.219 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 037350 | 성도이엔지 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6636 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037370 | EG | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6222 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037380 | 에이원마이크로 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037400 | 우리엔터프라이즈 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 037440 | 희림 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037460 | 삼지전자 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037500 | 미래에셋굿라이프혼합형자녀를위한펀드5-1 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037510 | 미래에셋굿라이프혼합형자녀를위한투자회사10-1 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 037540 | 네스테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 037550 | 클라스타 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037560 | LG헬로비전 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7562 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037600 | 씨모스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037620 | 미래에셋증권 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 037630 | 에스비엠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037640 | 지에스엔텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 037650 | 성진산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 037700 | 토자이홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 037710 | 광주신세계 | Retail | SPSC SPS Commerce | HIGH 0.7662 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 037730 | 쓰리알 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037750 | 엔써커뮤니티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037760 | 쎄니트 | Metals and Materials | OI O-I Glass | MEDIUM 0.6774 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 037830 | 글로포스트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 037950 | 엘컴텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5095 | industry | not_low_confidence | us_market_relative_proxy |
| 038010 | 제일테크노스 | Software | LX LexinFintech Holdings | MEDIUM 0.5642 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038050 | 트래픽아이티에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038060 | 루멘스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5994 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038070 | 서린바이오 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038100 | 아이엠아이티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038110 | 에코플라스틱 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6876 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038120 | 에이디모터스 | Automobiles | F Ford Motor | MEDIUM 0.5944 | industry_and_business_model | not_low_confidence | not_available |
| 038160 | 팍스넷 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1955 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 038290 | 마크로젠 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6035 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 038320 | 어울림정보기술 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 038340 | 무궁화인포메이션테크놀로지 | Software | LUMN Lumen Technologies | HIGH 0.7577 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038390 | 레드캡투어 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8487 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038400 | 외환신용카드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038410 | 트라이콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038420 | 씨엔씨엔터프라이즈 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 038460 | 바이오스마트 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.4801 | industry | not_low_confidence | us_market_relative_proxy |
| 038500 | 삼표시멘트 | Metals and Materials | KMT Kennametal | HIGH 0.7656 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038530 | 케이바이오랩스 | Software | DXC DXC Technology | MEDIUM 0.6046 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038540 | 상상인 | Banks | FVCB FVCBankcorp | MEDIUM 0.6973 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 038620 | 위즈코프 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038680 | 에스넷 | Software | ACTG Acacia Research | MEDIUM 0.6233 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038690 | 에이스일렉트로닉스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038710 | 콜마파마 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038720 | 유일엔시스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038810 | 포이보스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038830 | 케이엠에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038870 | 에코심플렉스 | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038880 | 아이에이 | Automobiles | F Ford Motor | MEDIUM 0.5325 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038920 | 에이치에스씨홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 038950 | 파인디지털 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5559 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 038960 | 현주컴퓨터 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038980 | 이지클럽 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 038990 | 넥스콘테크놀러지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 039000 | 써미트테크놀로지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 039010 | 현대에이치티 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5962 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039020 | 이건홀딩스 | Metals and Materials | OI O-I Glass | MEDIUM 0.6451 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 039030 | 이오테크닉스 | Semiconductors | MCHP Microchip Technology Incorporated | HIGH 0.7482 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039040 | 유니텍전자 | Semiconductors | Q Qnity Electronics | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | not_available |
| 039060 | 아이비진 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039110 | 에스피컴텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039130 | 하나투어 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039200 | 오스코텍 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7241 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039230 | 제이앤케이인더스트리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 039240 | 경남스틸 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.6964 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039290 | 인포뱅크 | Software | LSAK Lesaka Technologies | MEDIUM 0.5956 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039310 | 세중 | Software | LSAK Lesaka Technologies | MEDIUM 0.5803 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039340 | 한국경제TV | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7354 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 039350 | 헤파호프코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039390 | 윌텍정보통신 | Software | CMTL Comtech Telecommunications | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 039420 | 케이엘넷 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6472 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039440 | 에스티아이 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6775 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039490 | 키움증권 | Banks | ZION Zions Bancorporation N.A | HIGH 0.7318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039530 | 씨앤케이인터내셔널 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039560 | 다산네트웍스 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6089 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039570 | HDC랩스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6778 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039580 | 피코소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039610 | 화성밸브 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7094 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039670 | 스포츠서울 | Listed Operating Company | CNC Centene | LOW 0.1994 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 039740 | 한국정보공학 | Software | LX LexinFintech Holdings | MEDIUM 0.5469 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039790 | 위노바 | Listed Operating Company | CNC Centene | LOW 0.2051 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 039830 | 오로라 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.6822 | industry | not_low_confidence | us_market_relative_proxy |
| 039840 | 디오 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5929 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039850 | 태창파로스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039860 | 나노엔텍 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6669 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039870 | 피케이엘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 039980 | 폴라리스AI | Software | LSAK Lesaka Technologies | MEDIUM 0.6533 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 039990 | 코아정보시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 040020 | 사라콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 040130 | 엔플렉스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 040160 | 누리플렉스 | Software | LSAK Lesaka Technologies | MEDIUM 0.6621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 040180 | 대양글로벌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 040300 | YTN | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7643 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 040350 | 크레오에스지 | Software | LOT Lotus Technology | MEDIUM 0.6775 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 040420 | 정상제이엘에스 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5426 | industry | not_low_confidence | us_market_relative_proxy |
| 040610 | SG&G | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7121 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 040670 | 와이즈파워 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 040740 | 아인스엠앤엠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 040910 | 아이씨디 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5955 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 041020 | 폴라리스오피스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7284 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041030 | 이루넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041060 | 아라온테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 041140 | 넥슨지티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041190 | 우리기술투자 | Financial Services | JCAP Jefferson Capital | MEDIUM 0.7195 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041310 | 모빌링크텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 041320 | 보홍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041440 | 현대에버다임 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6766 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041450 | 인네트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041460 | 한국전자인증 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6635 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041500 | 디비엘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041510 | 에스엠 | Media and Entertainment | NXST Nexstar Media Group | HIGH 0.7852 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041520 | 이엘씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.629 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 041550 | 쎄라텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041590 | 플래스크 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6988 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 041630 | 인젠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041650 | 상신브레이크 | Automobiles | F Ford Motor | MEDIUM 0.5633 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041800 | 코디콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041830 | 인바디 | Biotechnology | HRMY Harmony Biosciences Holdings | MEDIUM 0.6062 | industry | not_low_confidence | us_market_relative_proxy |
| 041910 | 폴라리스AI파마 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.687 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041920 | 메디아나 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.611 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041930 | SY동아 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 041940 | 한텔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 041960 | 코미팜 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7164 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 042000 | 카페24 | Software | RCMT RCM Technologies | MEDIUM 0.7125 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042040 | 케이피엠테크 | Software | GOTU Gaotu Techedu | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 042100 | 현대오토넷 | Automobiles | F Ford Motor | MEDIUM 0.5944 | industry_and_business_model | not_low_confidence | not_available |
| 042110 | 에스씨디 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5416 | industry | not_low_confidence | us_market_relative_proxy |
| 042340 | 대국 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 042370 | 비츠로테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6024 | industry | not_low_confidence | us_market_relative_proxy |
| 042420 | 네오위즈홀딩스 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.6399 | industry | not_low_confidence | partial_direct_similarity |
| 042500 | 링네트 | Software | ACTG Acacia Research | MEDIUM 0.6497 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042510 | 라온시큐어 | Software | ACTG Acacia Research | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042520 | 한스바이오메드 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.6153 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042570 | 퓨쳐비젼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 042600 | 새로닉스 | Software | LX LexinFintech Holdings | MEDIUM 0.6579 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 042660 | 한화오션 | Software | TTEK Tetra Tech | MEDIUM 0.6816 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042670 | 에이치디현대인프라코어 | Listed Operating Company | G Genpact | LOW 0.2026 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 042700 | 한미반도체 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.666 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 042820 | 어울림네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 042870 | 에코페트로시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 042940 | 상지건설 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.673 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 042950 | 미래에셋새천년코리아벤처펀드일호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 042960 | 창민테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 043090 | 더테크놀로지 | Software | GOTU Gaotu Techedu | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043100 | 알파AI | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043150 | 바텍 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.6297 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043200 | 파루 | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6725 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043220 | 티에스넥스젠 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6455 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043260 | 성호전자 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6618 | industry | not_low_confidence | us_market_relative_proxy |
| 043290 | 케이맥 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 043340 | 에쎈테크 | Software | LX LexinFintech Holdings | MEDIUM 0.5906 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043360 | 디지아이 | Software | LSAK Lesaka Technologies | MEDIUM 0.5657 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043370 | 피에이치에이 | Automobiles | GPI Group 1 Automotive | HIGH 0.7273 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043580 | 에임하이글로벌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 043590 | 웰킵스하이텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 043610 | KT지니뮤직 | Media and Entertainment | GTN Gray Media | HIGH 0.7765 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043630 | 지앤알 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 043650 | 국순당 | Food and Beverage | BJRI BJ's Restaurants | HIGH 0.8202 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043680 | 스톰이앤에프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 043690 | 테크메이트 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 043710 | 코스리거글로벌 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 043790 | 옥션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 043890 | 티브로드한빛방송 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 043910 | 자연과환경 | Software | GOTU Gaotu Techedu | MEDIUM 0.5689 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044060 | 조광아이엘아이 | Listed Operating Company | CNC Centene | LOW 0.198 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 044070 | 한서제약 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 044180 | KD | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5594 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044340 | 위닉스 | Software | GOTU Gaotu Techedu | MEDIUM 0.5771 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044370 | 조이토토 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 044380 | 주연테크 | Software | LSAK Lesaka Technologies | MEDIUM 0.5279 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044440 | 솔빛미디어 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 044450 | KSS해운 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8426 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044480 | 빌리언스 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044490 | 태웅 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.6981 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044640 | 동부씨엔아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 044770 | 에이엠에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 044780 | 에이치케이 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6072 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 044820 | 코스맥스비티아이 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5526 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044960 | 이글벳 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 044990 | 에이치엔에스하이텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5319 | industry | not_low_confidence | us_market_relative_proxy |
| 045050 | 글라소울 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045060 | 오공 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.66 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045100 | 한양이엔지 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045260 | 디에이치패션 | Household and Personal Products | ULTA Ulta Beauty | MEDIUM 0.6144 | industry_and_business_model | not_low_confidence | not_available |
| 045290 | 포네이처 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045300 | 성우테크론 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6298 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045310 | 이레전자산업 | Semiconductors | Q Qnity Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 045340 | 토탈소프트 | Electrical Equipment | POR Portland General Electric | HIGH 0.7636 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045380 | 더존디지털웨어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045390 | 대아티아이 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8571 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045400 | 이롬텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045470 | 에이프로테크놀로지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 045510 | 정원엔시스 | Software | ACTG Acacia Research | MEDIUM 0.5664 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045520 | 크린앤사이언스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5937 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045660 | 에이텍 | Software | ACTG Acacia Research | MEDIUM 0.6091 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 045710 | 온미디어 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 045760 | 한국통신데이타 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 045820 | LG파워콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045880 | 유티엑스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045890 | 금빛 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045920 | 화림모드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 045970 | 코아시아 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6602 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046000 | 모디아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 046070 | 코다코 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.7085 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046110 | 한일네트웍스 | Listed Operating Company | MCK McKesson | LOW 0.1976 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 046120 | 오르비텍 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7494 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 046140 | 스튜디오에스 | Media and Entertainment | MAX MediaAlpha, . Class A | HIGH 0.8325 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046210 | HLB파나진 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.5742 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046240 | 에스브이에이치 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 046310 | 백금T&A | Software | PRTH Priority Technology Holdings | MEDIUM 0.552 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046320 | 엠트론스토리지테크놀로지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 046350 | 에듀아크 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 046390 | 삼화네트웍스 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7483 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046400 | 휴스토리 | Listed Operating Company | VFC V.F | LOW 0.1954 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 046430 | 알에스넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 046440 | KG파이낸셜 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6762 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046720 | 엔하이테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 046810 | 코리언일랙트로닉스파워소스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 046840 | 자유투어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 046890 | 서울반도체 | Biotechnology | ANIK Anika Therapeutics | MEDIUM 0.5817 | industry | not_low_confidence | us_market_relative_proxy |
| 046940 | 우원개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6003 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 046970 | 우리로 | Software | LSAK Lesaka Technologies | MEDIUM 0.6904 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047040 | 대우건설 | Software | U Unity Software | HIGH 0.7243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047050 | 포스코인터내셔널 | Retail | BURL Burlington Stores | HIGH 0.8006 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047060 | 덴소코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047080 | 한빛소프트 | Interactive Entertainment | GME GameStop | MEDIUM 0.6141 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047310 | 파워로직스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6787 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047370 | 에프아이투어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047400 | 유니온머티리얼 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6912 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047420 | 레이더스컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047440 | 디케이씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047450 | 이앤텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047560 | 이스트소프트 | Software | PAR PAR Technology | MEDIUM 0.6413 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047600 | 세계투어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047610 | 월드텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 047710 | 액티투오 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 047730 | 텔라움 | Listed Operating Company | CNC Centene | LOW 0.2094 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 047770 | 코데즈컴바인 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7573 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047810 | 한국항공우주 | Software | REZI Resideo Technologies | MEDIUM 0.7026 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047820 | 초록뱀미디어 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7795 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047920 | HLB제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7378 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 047940 | 비엔디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048130 | 에스피코프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048140 | 태광이엔시 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048150 | 모닷텔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048260 | 오스템임플란트 | Listed Operating Company | TISI Team | LOW 0.1881 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 048270 | 포넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048410 | 현대바이오 | Biotechnology | LAB Standard BioTools | MEDIUM 0.6487 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048430 | 유라테크 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6964 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048460 | 엑큐리스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048470 | 대동스틸 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.617 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048510 | 테스텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048530 | 인트론바이오 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6393 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048540 | 하이콤정보통신 | Software | CMTL Comtech Telecommunications | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 048550 | SM C&C | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.794 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048640 | 엠엔에프씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048760 | 브이케이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 048770 | TPC로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6997 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048830 | 엔피케이 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6123 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048870 | 시너지이노베이션 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5363 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 048910 | 대원미디어 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7637 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049000 | 예당컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 049070 | 인탑스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6771 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 049080 | 기가레인 | Software | CMTL Comtech Telecommunications | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 049120 | 파인디앤씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5677 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049130 | 하우리 | Listed Operating Company | MCK McKesson | LOW 0.2311 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 049180 | 셀루메드 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049370 | 씨제이엔터테인먼트 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 049430 | 코메론 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6887 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049470 | 비트플래닛 | Software | PAR PAR Technology | MEDIUM 0.6093 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049480 | 오픈베이스 | Software | ACTG Acacia Research | MEDIUM 0.5954 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049520 | 유아이엘 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6928 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049550 | 잉크테크 | Software | LX LexinFintech Holdings | MEDIUM 0.6012 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049630 | 재영솔루텍 | Semiconductors | KE Kimball Electronics | HIGH 0.7218 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049690 | 포휴먼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 049720 | 고려신용정보 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049770 | 동원F&B | Listed Operating Company | G Genpact | LOW 0.202 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 049800 | 우진플라임 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.613 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049830 | 승일 | Software | LX LexinFintech Holdings | MEDIUM 0.4927 | industry | not_low_confidence | us_market_relative_proxy |
| 049950 | 미래컴퍼니 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5986 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 049960 | 쎌바이오텍 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5877 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050050 | 유아이에너지 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 050090 | 비케이홀딩스 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | MEDIUM 0.6747 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050110 | 캠시스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5967 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050120 | ES큐브 | Hotels, Restaurants, and Leisure | PK Park Hotels & Resorts | MEDIUM 0.5067 | industry | not_low_confidence | us_market_relative_proxy |
| 050320 | 에스에이치엔엘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 050470 | 씨티앤티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 050540 | 엠피씨플러스 | Listed Operating Company | CNC Centene | LOW 0.1994 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 050600 | 세라온홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 050640 | 이룸지엔지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 050760 | 에스폴리텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.5817 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050860 | 아세아텍 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6393 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050890 | 쏠리드 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.674 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 050960 | 수산아이앤티 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6415 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051160 | 지어소프트 | Listed Operating Company | RGS Regis | LOW 0.1687 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 051170 | 썬코어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 051310 | 플랜텍 | Listed Operating Company | QH Quhuo American Depository Shares | LOW 0.2065 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 051360 | 토비스 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.6879 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051370 | 인터플렉스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5587 | industry | not_low_confidence | us_market_relative_proxy |
| 051380 | 피씨디렉트 | Software | ACTG Acacia Research | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051390 | YW | Listed Operating Company | TRAK ReposiTrak | LOW 0.1707 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 051490 | 나라엠앤디 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6405 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051500 | CJ프레시웨이 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6094 | industry | not_low_confidence | us_market_relative_proxy |
| 051530 | 굿이엠지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 051600 | 한전KPS | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.8319 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051630 | 진양화학 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6241 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051710 | 디에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 051780 | 큐로홀딩스 | Food and Beverage | UNFI United Natural Foods | HIGH 0.7932 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 051810 | 모보 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 051820 | 아이피에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 051900 | LG생활건강 | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.7459 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 051910 | LG화학 | Specialty Chemicals | DOW Dow | HIGH 0.8562 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 051980 | 중앙첨단소재 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.7059 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052020 | 에스티큐브 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1887 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 052190 | 세영디앤씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 052210 | 엠씨티티코어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052220 | iMBC | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7477 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052260 | 현대바이오랜드 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5504 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052270 | 우전 | Listed Operating Company | MCK McKesson | LOW 0.2056 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 052290 | 트레이스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052300 | 오션인더블유 | Machinery and Industrial Equipment | LUNR Intuitive Machines, . Class A | MEDIUM 0.6701 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052310 | 에이치원바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 052330 | 코텍 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.8927 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052350 | 코아에스앤아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052400 | 코나아이 | Software | PAYC Paycom Software | MEDIUM 0.6874 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052420 | 오성첨단소재 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6161 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052460 | 아이크래프트 | Software | ACTG Acacia Research | MEDIUM 0.6013 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052510 | 에코솔루션 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 052560 | 삼성수산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052600 | 한네트 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6315 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052640 | 제네시스엔알디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052650 | 이디디컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052670 | 제일바이오 | Biotechnology | AMN AMN Healthcare Services | MEDIUM 0.6456 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052690 | 한전기술 | Electrical Equipment | PCG Pacific Gas & Electric | HIGH 0.8123 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052710 | 아모텍 | Semiconductors | KE Kimball Electronics | HIGH 0.7371 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052770 | 아이톡시 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 052790 | 액토즈소프트 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5945 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052810 | 아시아미디어홀딩스 | Media and Entertainment | AMC AMC Entertainment Holdings, . Class A | MEDIUM 0.6671 | industry_and_business_model | not_low_confidence | not_available |
| 052860 | 아이앤씨 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6822 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052880 | 모아에스앤에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052900 | KX하이텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.684 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 052960 | 태양3C | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 052970 | 올리브나인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053000 | 우리금융지주 | Banks | GBFH GBank Financial Holdings | MEDIUM 0.5918 | industry_and_business_model | not_low_confidence | not_available |
| 053030 | 바이넥스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.6309 | industry | not_low_confidence | us_market_relative_proxy |
| 053040 | 블루젬디앤씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053050 | 지에스이 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5655 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053060 | 세동 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6531 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053070 | 트리니티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053080 | 케이엔솔 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7277 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053110 | 소리바다 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1873 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 053160 | 프리엠스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.683 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053170 | 코스모스피엘씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053200 | 디이시스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053210 | 케이티스카이라이프 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.769 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053250 | 엔에스아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053260 | 금강철강 | Metals and Materials | OI O-I Glass | HIGH 0.7593 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053270 | 구영테크 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6702 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053280 | 예스24 | Retail | NEGG Newegg Commerce, . Common Shares | MEDIUM 0.7127 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 053290 | NE능률 | Energy Infrastructure | MAN ManpowerGroup | MEDIUM 0.5259 | industry | not_low_confidence | us_market_relative_proxy |
| 053300 | 한국정보인증 | Software | GTM ZoomInfo Technologies | MEDIUM 0.7009 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053320 | 제네시스디벨롭먼트홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 053330 | 영진코퍼레이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053350 | 이니텍 | Software | ARRY Array Technologies | MEDIUM 0.6256 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053440 | 성우몰드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053450 | 세코닉스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.4813 | industry | not_low_confidence | us_market_relative_proxy |
| 053470 | 오페스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053580 | 웹케시 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6528 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053590 | 한국테크놀로지 | Software | RXT Rackspace Technology | HIGH 0.747 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053610 | 프로텍 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6776 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053620 | 태양 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7272 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053660 | 현진소재 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 053690 | 한미글로벌 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.688 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053700 | 삼보모터스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7221 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053740 | 국제엘렉트릭코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053800 | 안랩 | Software | HDSN Hudson Technologies | MEDIUM 0.7058 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 053810 | 아이팩토리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053870 | 지티앤티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 053890 | 미디어코프 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 053950 | 경남제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.4831 | industry | not_low_confidence | us_market_relative_proxy |
| 053980 | 오상자이엘 | Software | DXC DXC Technology | MEDIUM 0.5757 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 054010 | 선팩테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 054020 | 지케이파워 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054040 | 한국컴퓨터 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6367 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054050 | NH농우바이오 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5871 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054080 | 우주통신 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 054090 | 삼진엘앤디 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054120 | 더체인지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054150 | 뉴젠아이씨티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054170 | 엔빅스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054180 | 메디콕스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 054210 | 이랜텍 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.713 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054220 | 비츠로시스 | Software | LX LexinFintech Holdings | MEDIUM 0.5609 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054250 | 예일바이오텍 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 054300 | 팬스타엔터프라이즈 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7899 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054340 | 피앤텔 | Listed Operating Company | ACH Accendra Health | LOW 0.1897 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 054370 | 업필 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054410 | 케이피티유 | Metals and Materials | WS Worthington Steel, . Common Shares | MEDIUM 0.6281 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054440 | 엠텍반도체 | Semiconductors | Q Qnity Electronics | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | not_available |
| 054450 | 텔레칩스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7016 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054530 | 신한SIT | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054540 | 삼영엠텍 | Software | LX LexinFintech Holdings | MEDIUM 0.5832 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054620 | APS | Semiconductors | MEI Methode Electronics | MEDIUM 0.6703 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054630 | 에이디칩스 | Listed Operating Company | CNC Centene | LOW 0.1942 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 054650 | 뉴젠비아이티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054670 | 대한뉴팜 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6777 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054780 | 키이스트 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7348 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054790 | 제이엠피 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 054800 | 아이디스홀딩스 | Software | ACTG Acacia Research | MEDIUM 0.6435 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054920 | 한컴위드 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7166 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054930 | 유신 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6134 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054940 | 엑사이엔씨 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6091 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 054950 | 제이브이엠 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.6083 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 055000 | 동서정보기술 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 055250 | 다휘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 055490 | 테이팩스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5252 | industry | not_low_confidence | us_market_relative_proxy |
| 055550 | 신한지주 | Banks | C Citigroup | HIGH 0.7416 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 055810 | 케이티씨텔레콤 | Telecommunications | OPTU Optimum Communications, . Class A | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | not_available |
| 055970 | 에너윈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056000 | 코원플레이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056010 | 아이스테이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056020 | 쿨투 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056060 | 세니콘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056080 | 유진로봇 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6006 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 056090 | 시지메드텍 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5789 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 056140 | 리더컴 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056190 | 에스에프에이 | Construction and Engineering | ROAD Construction Partners | HIGH 0.7516 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 056200 | 엠넷미디어 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 056340 | 씨유전자 | Semiconductors | Q Qnity Electronics | MEDIUM 0.5244 | industry_and_business_model | not_low_confidence | not_available |
| 056360 | 코위버 | Software | LX LexinFintech Holdings | MEDIUM 0.5955 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 056500 | 슈마일렉트론 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056700 | 신화인터텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6202 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 056710 | 미리넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056730 | CNT85 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6391 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 056810 | 위다스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 056850 | 코어비트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 057030 | YBM넷 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.507 | industry | not_low_confidence | us_market_relative_proxy |
| 057050 | 현대홈쇼핑 | Retail | SPSC SPS Commerce | HIGH 0.8039 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 057100 | 하이스마텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 057110 | 아이티센네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 057330 | 플래닛팔이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 057500 | 에스케이엔펄스 | Listed Operating Company | VFC V.F | LOW 0.192 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 057540 | 옴니시스템 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 057680 | 티사이언티픽 | Software | DXC DXC Technology | MEDIUM 0.6366 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 057880 | 푸른소나무 | Listed Operating Company | CNC Centene | LOW 0.1976 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 058110 | 멕아이씨에스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058220 | 아리온테크놀로지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 058370 | 비엔씨컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058400 | KNN | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7614 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058420 | 제이웨이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058430 | 포스코스틸리온 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7647 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058450 | 한주에이알티 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | MEDIUM 0.7113 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058470 | 리노공업 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058480 | 해원에스티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058530 | 헬스커넥트 | Biotechnology | MDGL Madrigal Pharmaceuticals | MEDIUM 0.5831 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058550 | 네오리소스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058610 | 에스피지 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6422 | industry | not_low_confidence | us_market_relative_proxy |
| 058630 | 엠게임 | Interactive Entertainment | BYD Boyd Gaming | HIGH 0.7273 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058650 | 세아홀딩스 | Metals and Materials | KMT Kennametal | HIGH 0.757 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058680 | 오브제 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058690 | 퓨쳐인포넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058730 | 다스코 | Metals and Materials | OI O-I Glass | HIGH 0.7431 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058820 | CMG제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5829 | industry | not_low_confidence | us_market_relative_proxy |
| 058850 | KTcs | Software | ACTG Acacia Research | MEDIUM 0.6064 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058860 | KTis | Software | ACTG Acacia Research | MEDIUM 0.5865 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 058900 | 투미비티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 058970 | 엠로 | Software | ACTG Acacia Research | MEDIUM 0.67 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 059090 | 미코 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6699 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 059100 | 아이컴포넌트 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5858 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 059120 | 아진엑스텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7073 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 059180 | 엔더블유시 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 059210 | 메타바이오메드 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.5253 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 059270 | 해성에어로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6987 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 059720 | 야호커뮤니케이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 060000 | 국민은행 | Banks | USB U.S. Bancorp | HIGH 0.7562 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 060150 | 인선이엔티 | Software | DXC DXC Technology | MEDIUM 0.6654 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060230 | 제이케이시냅스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 060240 | 스타코링크 | Software | GOTU Gaotu Techedu | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060250 | NHN KCP | Software | HDSN Hudson Technologies | MEDIUM 0.6913 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060260 | 뉴보텍 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.8046 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060280 | 큐렉소 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.6211 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060300 | 레드로버 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 060310 | 3S | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7048 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060370 | LS마린솔루션 | Software | REZI Resideo Technologies | MEDIUM 0.7063 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060380 | 동양에스텍 | Metals and Materials | OI O-I Glass | MEDIUM 0.6452 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 060410 | 베스트플로우 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 060480 | 국일신동 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.6034 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060540 | 에스에이티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6419 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060550 | 우수씨엔에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 060560 | HC홈센타 | Metals and Materials | OI O-I Glass | MEDIUM 0.6295 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 060570 | 드림어스컴퍼니 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7525 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060590 | 씨티씨바이오 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6863 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060660 | 한도하이테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 060670 | 유퍼트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 060720 | KH바텍 | Semiconductors | KE Kimball Electronics | HIGH 0.723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060750 | 제이콤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 060850 | 영림원소프트랩 | Software | DXC DXC Technology | MEDIUM 0.5782 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 060900 | 에이전트AI | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7219 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 060910 | 프리젠 | Listed Operating Company | MCK McKesson | LOW 0.2647 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 060980 | HL홀딩스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7316 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 061040 | 알에프텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6775 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 061050 | 지앤디윈텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 061090 | 세나테크놀로지 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6669 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 061140 | 엘앤피아너스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 061250 | 화일약품 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.532 | industry | not_low_confidence | us_market_relative_proxy |
| 061460 | 한진피앤씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 061970 | LB세미콘 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7128 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 062040 | 산일전기 | Electrical Equipment | LECO Lincoln Electric Holdings, . Common Shares | HIGH 0.7786 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 062580 | 인산가 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 062730 | 케너텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 062860 | 티엘아이 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1869 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 062970 | 한국첨단소재 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6123 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063080 | 컴투스홀딩스 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.5267 | industry | not_low_confidence | partial_direct_similarity |
| 063160 | 종근당바이오 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063170 | 서울옥션 | Listed Operating Company | XGN Exagen | LOW 0.1701 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 063280 | 사이버패스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 063350 | 팬택앤큐리텔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 063440 | SM Life Design | Media and Entertainment | PLAY Dave & Buster's Entertainment | MEDIUM 0.7148 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063510 | 코오롱인터내셔널 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 063570 | NICE인프라 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6005 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063760 | 이엘피 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6005 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 063840 | 닉스테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 064060 | 사이노젠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 064090 | 인크레더블버즈 | Listed Operating Company | AWRE Aware | LOW 0.1662 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 064240 | 홈캐스트 | Retail | NEGG Newegg Commerce, . Common Shares | HIGH 0.7835 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064260 | 다날 | Software | DXC DXC Technology | HIGH 0.7295 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064290 | 인텍플러스 | Semiconductors | MX Magnachip Semiconductor | HIGH 0.721 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064350 | 현대로템 | Software | ESE ESCO Technologies | HIGH 0.7206 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064400 | LG씨엔에스 | Software | GWRE Guidewire Software | HIGH 0.7482 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064420 | 케이피케미칼 | Specialty Chemicals | DOW Dow | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | not_available |
| 064480 | 브리지텍 | Software | LX LexinFintech Holdings | MEDIUM 0.592 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064510 | 유네코 | Listed Operating Company | CNC Centene | LOW 0.2117 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 064520 | 테크엘 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6245 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064550 | 바이오니아 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5956 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064720 | 모델라인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 064760 | 티씨케이 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064800 | 포니링크 | Retail | NEGG Newegg Commerce, . Common Shares | MEDIUM 0.7102 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 064820 | 케이프 | Banks | FVCB FVCBankcorp | HIGH 0.73 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064850 | 에프앤가이드 | Software | GTM ZoomInfo Technologies | MEDIUM 0.7135 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 064900 | 교보메리츠퍼스트기업구조조정부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 064960 | SNT모티브 | Automobiles | GPI Group 1 Automotive | HIGH 0.753 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065060 | 지엔코 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 065130 | 탑엔지니어링 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6241 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065150 | 대산F&B | Food and Beverage | FLO Flowers Foods | HIGH 0.81 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065160 | 라임 | Listed Operating Company | AMTX Aemetis | LOW 0.1824 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 065170 | 비엘팜텍 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065180 | 해피드림 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065270 | 플렉스컴 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065310 | 더스텔라 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065340 | 쓰리디월드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065350 | 신성델타테크 | Software | REZI Resideo Technologies | MEDIUM 0.6631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065370 | 위세아이텍 | Software | LX LexinFintech Holdings | MEDIUM 0.5581 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065410 | 지엔텍홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 065420 | 에스아이리소스 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065440 | 이루온 | Software | LX LexinFintech Holdings | MEDIUM 0.5986 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065450 | 빅텍 | Software | AIRS AirSculpt Technologies | MEDIUM 0.647 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 065500 | 오리엔트정공 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6821 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065510 | 휴비츠 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065530 | 와이어블 | Telecommunications | OPTU Optimum Communications, . Class A | HIGH 0.7263 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 065560 | 녹원씨엔아이 | Listed Operating Company | VFC V.F | LOW 0.1869 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 065570 | 삼영이엔씨 | Software | LX LexinFintech Holdings | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065610 | 폴리플러스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065620 | 제낙스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065650 | 하이퍼코퍼레이션 | Software | LSAK Lesaka Technologies | MEDIUM 0.5387 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065660 | 안트로젠 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6302 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065680 | 우주일렉트로 | Semiconductors | KE Kimball Electronics | HIGH 0.7326 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065690 | 파커스 | Software | ARRY Array Technologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065710 | 서호전기 | Electrical Equipment | POR Portland General Electric | HIGH 0.8142 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065770 | CS | Software | LSAK Lesaka Technologies | MEDIUM 0.5375 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 065810 | 유씨아이콜스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065910 | 피더블유제네틱스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 065940 | 바이오빌 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 065950 | 웰크론 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6662 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066060 | 휴먼텍코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066110 | 한프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066130 | 하츠 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6625 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066200 | 이노블루 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066270 | 네이트커뮤니케이션즈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066300 | 샤인시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 066310 | 큐에스아이 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6938 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066330 | 세이프아시아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066340 | 케이에스리소스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066350 | 티엔아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066360 | 체리부로 | Food and Beverage | FLO Flowers Foods | HIGH 0.8125 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066410 | 버킷스튜디오 | Software | PAR PAR Technology | MEDIUM 0.6783 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066430 | 아이로보틱스 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.728 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066480 | 휘튼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066570 | LG전자 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.8639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066590 | 스모트로닉 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6735 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066620 | 국보디자인 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6784 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066670 | 디티씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.654 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066690 | 보광티에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066700 | 테라젠이텍스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6684 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066790 | 씨씨에스 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7701 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 066830 | 제노텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066850 | 아이드림 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 066900 | 디에이피 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 066910 | 손오공 | Hotels, Restaurants, and Leisure | PK Park Hotels & Resorts | MEDIUM 0.5295 | industry | not_low_confidence | partial_direct_similarity |
| 066930 | 한국애보트진단 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 066970 | 엘앤에프 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5985 | industry | not_low_confidence | us_market_relative_proxy |
| 066980 | 한성크린텍 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067000 | 조이시티 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.6916 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067010 | 이씨에스 | Software | ARRY Array Technologies | MEDIUM 0.5659 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067080 | 대화제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7184 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067130 | 클루넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 067160 | SOOP | Software | SIGA SIGA Technologies | MEDIUM 0.64 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067170 | 오텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7179 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067250 | 케이조선 | Shipbuilding | HZO MarineMax, . (FL) | MEDIUM 0.6374 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 067280 | 멀티캠퍼스 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5819 | industry | not_low_confidence | us_market_relative_proxy |
| 067290 | JW신약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7061 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067310 | 하나마이크론 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7164 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067370 | 선바이오 | Biotechnology | SBC SBC Medical Group Holdings Incorporated | MEDIUM 0.5412 | industry | not_low_confidence | us_market_relative_proxy |
| 067390 | 아스트 | Software | AIRS AirSculpt Technologies | HIGH 0.7406 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067570 | 엔브이에이치코리아 | Automobiles | F Ford Motor | MEDIUM 0.5675 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067630 | HLB생명과학 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5959 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067730 | 로지시스 | Software | DXC DXC Technology | MEDIUM 0.555 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 067770 | 세진티에스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 067830 | 세이브존I&C | Retail | CBRL Cracker Barrel Old Country Store | MEDIUM 0.7176 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067850 | 바이나믹 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 067900 | 와이엔텍 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8248 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067910 | 코크렙제1호기업구조조정부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 067920 | 이글루 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 067950 | 티이씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 067990 | 도이치모터스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7275 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068050 | 팬엔터테인먼트 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068060 | 케이씨더블류 | Listed Operating Company | CNC Centene | LOW 0.1992 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 068100 | 케이웨더 | Software | LSAK Lesaka Technologies | MEDIUM 0.6204 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068150 | 케이엔씨글로벌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 068240 | 다원시스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.577 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068270 | 셀트리온 | Biotechnology | BIIB Biogen | MEDIUM 0.6986 | industry | not_low_confidence | direct_financial_similarity |
| 068290 | 삼성출판사 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7746 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 068330 | 일신바이오 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6582 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068400 | 에스케이렌터카 | Listed Operating Company | G Genpact | LOW 0.2075 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 068420 | 엔터미디어 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | HIGH 0.8246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068630 | 에피밸리 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 068760 | 셀트리온제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7625 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068770 | 선우중공업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 068790 | DMS | Semiconductors | KE Kimball Electronics | MEDIUM 0.6778 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 068870 | LG생명과학 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 068930 | 디지털대성 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.6044 | industry | not_low_confidence | us_market_relative_proxy |
| 068940 | 셀피글로벌 | Software | GOTU Gaotu Techedu | MEDIUM 0.5757 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069080 | 웹젠 | Interactive Entertainment | BYD Boyd Gaming | HIGH 0.7584 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069110 | 유한코스메틱 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.7184 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069140 | 누리플랜 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069260 | 티케이지휴켐스 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7546 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069330 | 유아이디 | Semiconductors | KE Kimball Electronics | MEDIUM 0.573 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069410 | 엔텔스 | Software | LX LexinFintech Holdings | MEDIUM 0.5818 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069460 | 대호에이엘 | Metals and Materials | OI O-I Glass | HIGH 0.7207 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069470 | 제로원인터랙티브 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 069510 | 에스텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.532 | industry | not_low_confidence | us_market_relative_proxy |
| 069540 | 빛과전자 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6741 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069620 | 대웅제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069640 | 한세엠케이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6247 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 069730 | DSR제강 | Metals and Materials | KRT Karat Packaging | MEDIUM 0.6983 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069920 | 엑시온그룹 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5715 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 069960 | 현대백화점 | Retail | EVCM EverCommerce | HIGH 0.7729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 070080 | 삼보오토 | Automobiles | AN AutoNation | HIGH 0.8202 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 070300 | 엑스큐어 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6345 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 070480 | 신비앤텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 070540 | 코크렙제2호기업구조조정부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 070590 | 인티큐브 | Software | LX LexinFintech Holdings | MEDIUM 0.5621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 070960 | 모나용평 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6627 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071050 | 한국금융지주 | Banks | MTB M&T Bank | MEDIUM 0.7176 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071090 | 하이스틸 | Metals and Materials | OI O-I Glass | MEDIUM 0.6703 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071200 | 인피니트헬스케어 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5646 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071280 | 로체시스템즈 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6689 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071320 | 지역난방공사 | Energy Infrastructure | CVI CVR Energy | HIGH 0.7637 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071360 | 나노하이텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 071460 | 위니아 | Listed Operating Company | IVVD Invivyd | LOW 0.1816 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 071530 | 유에이블 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 071660 | 에스에스씨피 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 071670 | 에이테크솔루션 | Software | LX LexinFintech Holdings | MEDIUM 0.6152 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071840 | 롯데하이마트 | Retail | NEGG Newegg Commerce, . Common Shares | HIGH 0.7358 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 071850 | 캐스텍코리아 | Automobiles | F Ford Motor | MEDIUM 0.5813 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 071930 | 에이스하이텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 071950 | 코아스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6279 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 071970 | HD현대마린엔진 | Software | AIT Applied Industrial Technologies | MEDIUM 0.6737 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072020 | 중앙백신 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6967 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072130 | 유엔젤 | Software | DXC DXC Technology | MEDIUM 0.6232 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 072430 | 아이레보 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 072450 | 리얼티코리아제1호기업구조조정부동산투자 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 072470 | 우리산업홀딩스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6321 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072520 | 제넨바이오 | Biotechnology | BBIO BridgeBio Pharma | MEDIUM 0.6988 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072530 | 나이스메탈 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 072710 | 농심홀딩스 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8481 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072770 | 멤레이비티 | Software | LSAK Lesaka Technologies | MEDIUM 0.605 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 072870 | 메가스터디 | Energy Infrastructure | HPK HighPeak Energy | MEDIUM 0.5901 | industry | not_low_confidence | us_market_relative_proxy |
| 072950 | 빛샘전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5164 | industry | not_low_confidence | us_market_relative_proxy |
| 072990 | 에이치시티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.4851 | industry | not_low_confidence | us_market_relative_proxy |
| 073010 | 케이에스피 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6074 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073070 | 에이팸 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 073110 | 엘엠에스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6192 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073130 | 인스프리트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 073190 | 듀오백 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 073240 | 금호타이어 | Automobiles | GPI Group 1 Automotive | HIGH 0.7773 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073470 | 유레스메리츠제1호 | Real Estate | CTRE CareTrust REIT | MEDIUM 0.6828 | industry_and_business_model | not_low_confidence | not_available |
| 073490 | LIG아큐버 | Software | LSAK Lesaka Technologies | MEDIUM 0.6784 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073530 | 코크렙제3호CR리츠 | Real Estate | CTRE CareTrust REIT | MEDIUM 0.6828 | industry_and_business_model | not_low_confidence | not_available |
| 073540 | 에프알텍 | Software | LX LexinFintech Holdings | MEDIUM 0.5648 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073560 | 우리손에프앤지 | Food and Beverage | FLO Flowers Foods | HIGH 0.8353 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073570 | 리튬포어스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6078 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073640 | 테라사이언스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6526 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 073710 | 씨디네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 073780 | 케이디세코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 073930 | 제너시스템즈 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 074000 | 에스지피엠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 074130 | 디아이디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 074140 | 엑스로드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 074150 | 엠제이비 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 074430 | 아미노로직스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7007 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 074600 | 원익QnC | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6939 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 074610 | 이엔플러스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6546 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 075130 | 플랜티넷 | Software | DXC DXC Technology | MEDIUM 0.5799 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 075180 | 새론오토모티브 | Automobiles | F Ford Motor | MEDIUM 0.6209 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 075580 | 세진중공업 | Software | AIT Applied Industrial Technologies | MEDIUM 0.6527 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 075970 | 동국알앤에스 | Metals and Materials | OI O-I Glass | MEDIUM 0.6491 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 076080 | 웰크론한텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6371 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 076090 | 테이크시스템즈 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 076170 | 지비에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 076340 | 지에이이노더스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 076610 | 해성옵틱스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6771 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 076850 | 맥쿼리센트럴오피스기업구조조정부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 077280 | 한컴지엠디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 077360 | 덕산하이메탈 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.626 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 077500 | 유니퀘스트 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.6862 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 077960 | 케이이엔지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 077970 | STX엔진 | Software | AIT Applied Industrial Technologies | MEDIUM 0.6597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078000 | 텔코웨어 | Software | DXC DXC Technology | MEDIUM 0.6517 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 078020 | LS증권 | Banks | FVCB FVCBankcorp | HIGH 0.7443 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078070 | 유비쿼스홀딩스 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6806 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078130 | 국일제지 | Machinery and Industrial Equipment | ALTG Alta Equipment Group . Class A | MEDIUM 0.7049 | industry | not_low_confidence | partial_direct_similarity |
| 078140 | 대봉엘에스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6908 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078150 | HB테크놀러지 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6976 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078160 | 메디포스트 | Biotechnology | BNTC Benitec Biopharma | MEDIUM 0.634 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078340 | 컴투스 | Interactive Entertainment | GME GameStop | MEDIUM 0.6975 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078350 | 한양디지텍 | Semiconductors | KE Kimball Electronics | HIGH 0.7225 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078420 | 동북아1호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 078520 | 에이블씨엔씨 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.76 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078590 | 휴림에이텍 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6264 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078600 | 대주전자재료 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6186 | industry | not_low_confidence | us_market_relative_proxy |
| 078610 | 도움 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 078650 | 지나인제약 | Biotechnology | BBIO BridgeBio Pharma | MEDIUM 0.6977 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078670 | 아구스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 078700 | 신지소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 078780 | 아이디에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 078860 | 아이오케이이엔엠 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | HIGH 0.7282 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078890 | 가온그룹 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6139 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 078930 | GS | Energy Infrastructure | NOG Northern Oil and Gas | MEDIUM 0.6798 | industry | not_low_confidence | us_market_relative_proxy |
| 078940 | 퀀타피아 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1893 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 079000 | 와토스코리아 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.6945 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 079160 | CJ CGV | Media and Entertainment | TSQ Townsquare Media, . Class A | HIGH 0.7528 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079170 | 한창산업 | Metals and Materials | WS Worthington Steel, . Common Shares | MEDIUM 0.6217 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079190 | 케스피온 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5834 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079340 | 하이럭스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 079370 | 제우스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7162 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079430 | 현대리바트 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.72 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079440 | 오렌지라이프생명보험 | Insurance | SIGI Selective Insurance Group | MEDIUM 0.6348 | industry_and_business_model | not_low_confidence | not_available |
| 079550 | LIG디펜스앤에어로스페이스 | Software | REZI Resideo Technologies | MEDIUM 0.7007 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079560 | 시노펙스멤브레인 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 079650 | 서산 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6871 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079660 | 사조해표 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 079810 | APS이노베이션 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5658 | industry | not_low_confidence | us_market_relative_proxy |
| 079870 | 산양전기 | Electrical Equipment | EMR Emerson Electric | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | not_available |
| 079900 | 전진건설로봇 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7346 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079940 | 가비아 | Software | PRTH Priority Technology Holdings | MEDIUM 0.7072 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079950 | 인베니아 | Semiconductors | MEI Methode Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079960 | 동양이엔피 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.5799 | industry | not_low_confidence | us_market_relative_proxy |
| 079970 | 투비소프트 | Software | LX LexinFintech Holdings | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 079980 | 휴비스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.699 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080000 | 에스엔유프리시젼 | Listed Operating Company | MCK McKesson | LOW 0.2039 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 080010 | 이상네트웍스 | Listed Operating Company | TRAK ReposiTrak | LOW 0.2507 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 080030 | 동북아2호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 080140 | 디보스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 080160 | 모두투어 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.7053 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080180 | 아시아퍼시픽1호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 080220 | 제주반도체 | Semiconductors | ARW Arrow Electronics | HIGH 0.7352 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080410 | 동북아6호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 080420 | 모다이노칩 | Retail | NEGG Newegg Commerce, . Common Shares | HIGH 0.7337 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 080440 | 에스제이케이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 080470 | 성창오토텍 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6574 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080520 | 오디텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5782 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 080530 | 코디 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080570 | 국제개발 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 080580 | 오킨스전자 | Semiconductors | KE Kimball Electronics | HIGH 0.7286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080720 | 한국유니온제약 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 080960 | 동북아3호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 080970 | 동북아4호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 080980 | 동북아5호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 081000 | 일진다이아 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.706 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 081090 | 씨모텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 081150 | 티플랙스 | Metals and Materials | OI O-I Glass | MEDIUM 0.6844 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 081180 | 쎄크 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4954 | industry | not_low_confidence | us_market_relative_proxy |
| 081190 | 아시아퍼시픽2호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 081200 | 아시아퍼시픽3호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 081210 | 아시아퍼시픽4호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 081220 | 세미텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 081500 | 엑스씨이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 081580 | 성우전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 081660 | 미스토홀딩스 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.8272 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 081930 | 아시아퍼시픽8호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 081940 | 아시아퍼시픽9호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 081970 | 케이엑스넥스지 | Listed Operating Company | AMZN Amazon.com | LOW 0.2168 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 082110 | 동북아8호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 082210 | 옵트론텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4884 | industry | not_low_confidence | us_market_relative_proxy |
| 082220 | 프렉코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 082240 | 아시아퍼시픽5호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 082250 | 아시아퍼시픽6호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 082260 | 아시아퍼시픽7호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 082270 | 젬백스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.664 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 082390 | 피엘에이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 082640 | 동양생명 | Insurance | THG Hanover Insurance Group | HIGH 0.8336 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 082660 | 코스나인 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 082740 | 한화엔진 | Software | AIT Applied Industrial Technologies | HIGH 0.7218 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 082800 | 비보존 제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5533 | industry | not_low_confidence | us_market_relative_proxy |
| 082850 | 우리바이오 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5024 | industry | not_low_confidence | us_market_relative_proxy |
| 082920 | 비츠로셀 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6164 | industry | not_low_confidence | us_market_relative_proxy |
| 082930 | 실리콘화일 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 083120 | 동북아9호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083160 | 현대경매부동산일호투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 083310 | 엘오티베큠 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7042 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083350 | 동북아10호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083360 | 동북아11호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083370 | 동북아12호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083380 | 동북아13호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083390 | 동북아14호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083420 | 그린케미칼 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7133 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083450 | GST | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6904 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083470 | 이엠앤아이 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5982 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083500 | 에프엔에스테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6634 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083550 | 케이엠 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.608 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 083570 | 아시아퍼시픽10호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083580 | 아시아퍼시픽11호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083590 | 아시아퍼시픽12호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083600 | 아시아퍼시픽13호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083610 | 아시아퍼시픽14호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083620 | 아시아퍼시픽15호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 083640 | 인콘 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 083650 | 비에이치아이 | Battery and Energy Storage | TDG Transdigm Group Incorporated | HIGH 0.7465 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083660 | CSA 코스믹 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 083790 | CG인바이츠 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.5696 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 083930 | 아바코 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5911 | industry | not_low_confidence | us_market_relative_proxy |
| 084010 | 대한제강 | Metals and Materials | IIIN Insteel Industries | HIGH 0.7266 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084110 | 휴온스글로벌 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7095 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084160 | 골든브릿지더블유엠경매부동산일호투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 084180 | 수성웹툰 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7367 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084240 | 동북아15호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 084370 | 유진테크 | Semiconductors | ARW Arrow Electronics | HIGH 0.7258 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084440 | 유비온 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 084450 | 세실 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 084650 | 랩지노믹스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084670 | 동양고속 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8389 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084680 | 이월드 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6268 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 084690 | 대상홀딩스 | Food and Beverage | BGS B&G Foods | HIGH 0.8514 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084730 | 팅크웨어 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5296 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 084810 | 아이알디 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 084850 | 아이티엠반도체 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5561 | industry | not_low_confidence | us_market_relative_proxy |
| 084870 | 티비에이치글로벌 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7007 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 084990 | 헬릭스미스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.612 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085310 | 엔케이 | Software | LSAK Lesaka Technologies | MEDIUM 0.5738 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085370 | 루트로닉 | Listed Operating Company | SSTK Shutterstock | LOW 0.1914 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 085450 | 굿앤리치부동산공경매투자회사1호 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 085620 | 미래에셋생명 | Insurance | SAFT Safety Insurance Group | HIGH 0.8094 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 085660 | 차바이오텍 | Biotechnology | TH Target Hospitality | MEDIUM 0.6149 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085670 | 뉴프렉스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5373 | industry | not_low_confidence | us_market_relative_proxy |
| 085680 | 모빌탑 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 085810 | 알티캐스트 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5852 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085910 | 네오티스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7558 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 085980 | 세화피앤씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 085990 | 영찬테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 086040 | 바이오톡스텍 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.4964 | industry | not_low_confidence | us_market_relative_proxy |
| 086060 | 진바이오텍 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086080 | 다이노나 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 086200 | 제이앤유글로벌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 086220 | 광동헬스바이오 | Biotechnology | ALHC Alignment Healthcare | MEDIUM 0.6392 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086250 | 화신테크 | Software | RXT Rackspace Technology | MEDIUM 0.6864 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 086280 | 현대글로비스 | Logistics and Transportation | GXO GXO Logistics | HIGH 0.7527 | industry | not_low_confidence | us_market_relative_proxy |
| 086390 | 유니테스트 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7112 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086450 | 동국제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7409 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086460 | 큐러블 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 086520 | 에코프로 | Energy Infrastructure | MAN ManpowerGroup | MEDIUM 0.6693 | industry | not_low_confidence | us_market_relative_proxy |
| 086670 | 비엠티 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6985 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086710 | 선진뷰티사이언스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.739 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086720 | 코크렙제7호위탁관리부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 086790 | 하나금융지주 | Banks | C Citigroup | HIGH 0.7426 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086820 | 바이오솔루션 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6127 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 086830 | 신양오라컴디스플레이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 086890 | 이수앱지스 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6889 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086900 | 메디톡스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6053 | industry | not_low_confidence | us_market_relative_proxy |
| 086960 | MDS테크 | Software | ACTG Acacia Research | MEDIUM 0.664 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 086980 | 쇼박스 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7716 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 087010 | 펩트론 | Biotechnology | SRPT Sarepta Therapeutics | MEDIUM 0.6626 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 087220 | 스틸플라워 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 087260 | 모바일어플라이언스 | Automobiles | F Ford Motor | MEDIUM 0.524 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 087600 | 픽셀플러스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6395 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 087730 | 이엠네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 088010 | 동북아21호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 088020 | 네이쳐글로벌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 088130 | 동아엘텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6037 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088260 | 이리츠코크렙 | Real Estate | NNN NNN REIT | HIGH 0.7776 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088280 | 쏘닉스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088290 | 이원컴포텍 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6227 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088340 | 유라클 | Software | PAR PAR Technology | MEDIUM 0.596 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088350 | 한화생명 | Insurance | HIG The Hartford Insurance Group | HIGH 0.8336 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088390 | 이녹스 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.6607 | industry | not_low_confidence | us_market_relative_proxy |
| 088510 | 굿앤리치부동산공경매투자회사2호 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 088700 | 마이스코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 088790 | 진도 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7087 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088800 | 에이스테크 | Software | GOTU Gaotu Techedu | MEDIUM 0.6773 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088810 | 맥스브로 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 088910 | 동우팜투테이블 | Food and Beverage | FLO Flowers Foods | HIGH 0.8276 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 088960 | 씨티엘테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 088980 | 맥쿼리인프라 | Electrical Equipment | EMR Emerson Electric | HIGH 0.7684 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 089010 | 켐트로닉스 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5299 | industry | not_low_confidence | us_market_relative_proxy |
| 089030 | 테크윙 | Semiconductors | BHE Benchmark Electronics | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089140 | 넥스턴앤롤코리아 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 089150 | 케이씨티 | Software | GTM ZoomInfo Technologies | MEDIUM 0.5981 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089170 | 동북아27호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 089180 | 동북아28호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 089190 | 동북아29호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 089200 | 동북아30호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 089230 | THE E&M | Software | LOT Lotus Technology | MEDIUM 0.6284 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089240 | 네오세미테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 089470 | HDC현대EP | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7044 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089480 | 평산 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 089530 | 에이티세미콘 | Listed Operating Company | AMTX Aemetis | LOW 0.1818 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 089590 | 제주항공 | Aerospace and Defense | JBLU JetBlue Airways | HIGH 0.7925 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089600 | KT나스미디어 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7931 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089790 | 제이티 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6581 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089850 | 유비벨록스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 089860 | 롯데렌탈 | Logistics and Transportation | GXO GXO Logistics | HIGH 0.843 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089890 | 코세스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6811 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089970 | 브이엠 | Semiconductors | BHE Benchmark Electronics | HIGH 0.7327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 089980 | 상아프론테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5992 | industry | not_low_confidence | us_market_relative_proxy |
| 090080 | 평화산업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6507 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090090 | 디앤샵 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 090120 | 잘만테크 | Software | UBER Uber Technologies | HIGH 0.7578 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090150 | 아이윈 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6548 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090350 | 노루페인트 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7422 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090360 | 로보스타 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6643 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 090370 | 메타랩스 | Software | GOTU Gaotu Techedu | MEDIUM 0.5388 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090410 | 덕신이피씨 | Metals and Materials | IIIN Insteel Industries | MEDIUM 0.6292 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090430 | 아모레퍼시픽 | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.7992 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090460 | 비에이치 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.572 | industry | not_low_confidence | us_market_relative_proxy |
| 090470 | 제이스로보틱스 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 090540 | 코크렙제8호위탁관리부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 090710 | 휴림로봇 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6683 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 090730 | 심팩메탈 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 090740 | 와이앤넥스트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 090850 | 현대이지웰 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 090970 | 코리아퍼시픽01호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 090980 | 코리아퍼시픽02호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 090990 | 코리아퍼시픽03호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 091000 | 코리아퍼시픽04호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 091090 | 세원이앤씨 | Listed Operating Company | ACH Accendra Health | LOW 0.1868 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 091120 | 이엠텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6818 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091270 | 유디피 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 091340 | S&K폴리텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 091440 | 한울소재과학 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.5696 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091580 | 상신이디피 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6209 | industry | not_low_confidence | us_market_relative_proxy |
| 091590 | 남화토건 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6943 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091690 | 디지텍시스템스 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 091700 | 파트론 | Semiconductors | FEIM Frequency Electronics | HIGH 0.7336 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091810 | 트리니티항공 | Aerospace and Defense | JBLU JetBlue Airways | HIGH 0.7823 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091970 | 나노캠텍 | Specialty Chemicals | DOW Dow | MEDIUM 0.6162 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 091990 | 셀트리온헬스케어 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 092040 | 아미코젠 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092070 | 디엔에프 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6481 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 092130 | 이크레더블 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6388 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092190 | 서울바이오시스 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.6036 | industry | not_low_confidence | us_market_relative_proxy |
| 092200 | 디아이씨 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.707 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092220 | KEC | Semiconductors | MEI Methode Electronics | MEDIUM 0.7019 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092230 | KPX홀딩스 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092300 | 현우산업 | Semiconductors | KE Kimball Electronics | MEDIUM 0.4944 | industry | not_low_confidence | us_market_relative_proxy |
| 092440 | 기신정기 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092460 | 한라IMS | Software | GTM ZoomInfo Technologies | MEDIUM 0.6501 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092590 | 럭스피아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 092600 | 앤씨앤 | Semiconductors | MEI Methode Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 092630 | 바다로3호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 092730 | 네오팜 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7453 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092780 | DYP | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6735 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092790 | 넥스틸 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7656 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092870 | 엑시콘 | Semiconductors | KE Kimball Electronics | HIGH 0.7234 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 092970 | 거북선1호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 093050 | LF | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7908 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093190 | 빅솔론 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6269 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093230 | 이아이디 | Listed Operating Company | NSP Insperity | LOW 0.2006 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 093240 | 형지엘리트 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6457 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 093320 | 케이아이엔엑스 | Software | HDSN Hudson Technologies | MEDIUM 0.7122 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093370 | 후성 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7895 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093380 | 풍강 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6574 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093400 | 코리아퍼시픽05호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 093410 | 코리아퍼시픽06호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 093510 | 엔지브이아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 093520 | 매커스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.71 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093640 | 케이알엠 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6391 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 093730 | 동북아31호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 093820 | 한국베트남15-1유전해외자원개발투자회사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 093920 | 서원인텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6962 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094170 | 동운아나텍 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7138 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094190 | 이엘케이 | Listed Operating Company | CNC Centene | LOW 0.2164 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 094280 | 효성 ITX | Software | ACTG Acacia Research | MEDIUM 0.5806 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094360 | 칩스앤미디어 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6911 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094480 | 갤럭시아머니트리 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094520 | 미래에셋맵스오퍼튜니티베트남주식혼합형투자회사1호 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 094700 | 미성포리테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 094800 | 맵스리얼티 | Real Estate | ACRE Ares Commercial Real Estate | HIGH 0.7948 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 094820 | 일진파워 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6912 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094840 | 슈프리마에이치큐 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5473 | industry | not_low_confidence | us_market_relative_proxy |
| 094850 | 참좋은여행 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6268 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094860 | 네오리진 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.5958 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 094940 | 푸른로보틱스 | Software | LSAK Lesaka Technologies | MEDIUM 0.6236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 094950 | GB블루오션베트남주식혼합형투자회사1호 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 094970 | 제이엠티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.619 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095190 | 신화프리텍 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095270 | 웨이브일렉트로 | Software | LX LexinFintech Holdings | MEDIUM 0.5716 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095300 | 엔에스브이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 095340 | ISC | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7118 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095500 | 미래나노텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6869 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095570 | AJ네트웍스 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8476 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095610 | 테스 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7118 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095660 | 네오위즈 | Interactive Entertainment | GME GameStop | MEDIUM 0.7139 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095700 | 제넥신 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 095720 | 웅진씽크빅 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5362 | industry | not_low_confidence | us_market_relative_proxy |
| 095910 | 에스에너지 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7241 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096040 | 이트론 | Listed Operating Company | CHRS Coherus Oncology | LOW 0.1776 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 096240 | 크레버스 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5716 | industry | not_low_confidence | us_market_relative_proxy |
| 096250 | 와이즈넛 | Software | LX LexinFintech Holdings | MEDIUM 0.6552 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096300 | 한국월드와이드베트남부동산개발특별자산1호투자회사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 096350 | 대창솔루션 | Software | LSAK Lesaka Technologies | MEDIUM 0.6028 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096530 | 씨젠 | Biotechnology | GEHC GE HealthCare Technologies | MEDIUM 0.6746 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096610 | 알에프세미 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6756 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096630 | 에스코넥 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6399 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096640 | 멜파스 | Listed Operating Company | CHRS Coherus Oncology | LOW 0.1818 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 096690 | 에이루트 | Software | PAR PAR Technology | MEDIUM 0.5246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096760 | JW홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6971 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 096770 | SK이노베이션 | Energy Infrastructure | MAN ManpowerGroup | MEDIUM 0.6756 | industry | not_low_confidence | us_market_relative_proxy |
| 096870 | 엘디티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6151 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 097230 | HJ중공업 | Software | AIT Applied Industrial Technologies | HIGH 0.7243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 097520 | 엠씨넥스 | Semiconductors | FEIM Frequency Electronics | HIGH 0.7485 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 097780 | 에코볼트 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.634 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 097800 | 윈팩 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6511 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 097870 | 효성오앤비 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7136 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 097950 | CJ제일제당 | Food and Beverage | BGS B&G Foods | HIGH 0.8579 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 098070 | 한텍 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.7063 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 098120 | 마이크로컨텍솔 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6858 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 098150 | 한국월드와이드아시아태평양특별자산1호투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 098400 | 엔스퍼트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 098460 | 고영 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6281 | industry | not_low_confidence | us_market_relative_proxy |
| 098660 | 에스티오 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6294 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 099190 | 아이센스 | Biotechnology | SMTI Sanara MedTech | MEDIUM 0.5798 | industry | not_low_confidence | us_market_relative_proxy |
| 099210 | 코리아퍼시픽07호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 099220 | SDN | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 099320 | 쎄트렉아이 | Software | REZI Resideo Technologies | MEDIUM 0.6723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 099340 | 하나유비에스암바토비니켈해외자원개발1호 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 099350 | 하나유비에스암바토비니켈해외자원개발2호 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 099390 | 브레인즈컴퍼니 | Software | DXC DXC Technology | MEDIUM 0.5797 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 099410 | 동방선기 | Software | GTM ZoomInfo Technologies | MEDIUM 0.5713 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 099430 | 바이오플러스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5854 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 099440 | 스맥 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7572 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 099520 | DGI | Software | GOTU Gaotu Techedu | MEDIUM 0.6157 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 099660 | 신텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 099750 | 이지케어텍 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 099830 | 씨그널엔터테인먼트그룹 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 100030 | 인지소프트 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6245 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100090 | SK오션플랜트 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.713 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100120 | 뷰웍스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100130 | 동국S&C | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6454 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 100220 | 비상교육 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5349 | industry | not_low_confidence | us_market_relative_proxy |
| 100250 | 진양홀딩스 | Automobiles | GPI Group 1 Automotive | HIGH 0.7305 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100590 | 머큐리 | Software | LSAK Lesaka Technologies | MEDIUM 0.5961 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100660 | 서암기계공업 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6445 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100700 | 세운메디칼 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.5312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100790 | 미래에셋벤처투자 | Financial Services | GNW Genworth Financial | HIGH 0.7272 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 100840 | SNT에너지 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.7137 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101000 | KS인더스트리 | Software | GOTU Gaotu Techedu | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101060 | SBS미디어홀딩스 | Media and Entertainment | AMC AMC Entertainment Holdings, . Class A | MEDIUM 0.6671 | industry_and_business_model | not_low_confidence | not_available |
| 101140 | 인바이오젠 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 101160 | 월덱스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6599 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101170 | 우림피티에스 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6983 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101240 | 씨큐브 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101330 | 모베이스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6811 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101360 | 에코앤드림 | Specialty Chemicals | DOW Dow | MEDIUM 0.7116 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101380 | 거북선2호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 101390 | 아이엠 | Semiconductors | MEI Methode Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101400 | 엔시트론 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6124 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101490 | 에스앤에스텍 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6996 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101530 | 해태제과식품 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8525 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101670 | 하이드로리튬 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.4926 | industry | not_low_confidence | us_market_relative_proxy |
| 101680 | 한국정밀기계 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6175 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101730 | 위메이드맥스 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.6282 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 101790 | 케이알제2호개발전문위탁관리부동산투자회사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 101930 | 인화정공 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6578 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 101970 | 우양에이치씨 | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6963 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 101990 | 파브코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 102000 | 거북선3호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 102120 | 어보브반도체 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7133 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 102210 | 트레스 | Listed Operating Company | T AT&T | LOW 0.2154 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 102260 | 동성케미컬 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7212 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 102280 | 쌍방울 | Listed Operating Company | CNC Centene | LOW 0.1931 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 102370 | 케이옥션 | Listed Operating Company | XGN Exagen | LOW 0.1699 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 102460 | 이연제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.6216 | industry | not_low_confidence | us_market_relative_proxy |
| 102710 | 이엔에프테크놀로지 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6717 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 102940 | 코오롱생명과학 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7416 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 102950 | 아하 | Listed Operating Company | CNC Centene | LOW 0.1926 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 103130 | 웅진에너지 | Energy Infrastructure | MPC Marathon Petroleum | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 103140 | 풍산 | Metals and Materials | KMT Kennametal | HIGH 0.7898 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 103150 | 하이트맥주 | Food and Beverage | BGS B&G Foods | HIGH 0.7297 | industry_and_business_model | not_low_confidence | not_available |
| 103160 | 풀무원식품 | Food and Beverage | FLO Flowers Foods | HIGH 0.8751 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 103230 | 에스앤더블류 | Software | LX LexinFintech Holdings | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 103590 | 일진전기 | Electrical Equipment | LECO Lincoln Electric Holdings, . Common Shares | HIGH 0.7632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 103650 | 에이치앤아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 103660 | 씨앗 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 103840 | 우양 | Food and Beverage | FLO Flowers Foods | HIGH 0.8191 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104040 | 디에스엠 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.5744 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 104110 | 신성이엔지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1262 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 104120 | 신성에프에이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 104200 | NHN벅스 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7592 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104460 | 디와이피엔에프 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6606 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104480 | 티케이케미칼 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7216 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104540 | 코렌텍 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104620 | 노랑풍선 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6464 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104700 | 한국철강 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.7167 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 104830 | 원익머트리얼즈 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7947 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105070 | 금강제강 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 105330 | 케이엔더블유 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6868 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105380 | 다산자기관리부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 105550 | 엣지파운드리 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.5281 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 105560 | KB금융 | Banks | C Citigroup | HIGH 0.7608 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 105630 | 한세실업 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7603 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105740 | 디케이락 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105760 | 포스뱅크 | Software | LX LexinFintech Holdings | MEDIUM 0.5459 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 105840 | 우진 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 106080 | 케이이엠텍 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 106190 | 하이텍팜 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6955 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 106240 | 파인테크닉스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5856 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 106520 | 노블엠앤비 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 107590 | 미원홀딩스 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7011 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 107600 | 새빗켐 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5623 | industry | not_low_confidence | us_market_relative_proxy |
| 107640 | 한중엔시에스 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7662 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 108070 | 삼성디지털이미징 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 108230 | 톱텍 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 108320 | LX세미콘 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.5985 | industry | not_low_confidence | us_market_relative_proxy |
| 108380 | 대양전기공업 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 108490 | 로보티즈 | Construction and Engineering | ROAD Construction Partners | HIGH 0.7327 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 108670 | LX하우시스 | Metals and Materials | OI O-I Glass | HIGH 0.758 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 108790 | 인터파크 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 108860 | 셀바스AI | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5576 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 108890 | 거북선4호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 109070 | 주성코퍼레이션 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8379 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109080 | 옵티시스 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6135 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109610 | 에스와이 | Metals and Materials | OI O-I Glass | MEDIUM 0.6604 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 109670 | 씨싸이트 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.5939 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 109740 | 디에스케이 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5084 | industry | not_low_confidence | us_market_relative_proxy |
| 109820 | 진매트릭스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109860 | 동일금속 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6679 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 109960 | 앱토크롬 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5055 | industry | not_low_confidence | us_market_relative_proxy |
| 110020 | 전진바이오팜 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 110310 | 모린스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 110500 | 유니드코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 110570 | 넥솔론 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 110660 | 툴코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 110790 | 크리스에프앤씨 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 110990 | 디아이티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111110 | 호전실업 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7067 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111380 | 동인기연 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111610 | 세왕 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 111710 | 남화산업 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6742 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111770 | 영원무역 | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.8018 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 111820 | 지유온 | Listed Operating Company | CNC Centene | LOW 0.1865 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 111870 | 케이에이치미래물산 | Listed Operating Company | CNC Centene | LOW 0.1878 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 112040 | 위메이드 | Interactive Entertainment | GME GameStop | MEDIUM 0.6802 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 112190 | KC산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 112240 | 에스에프씨 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1905 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 112290 | 와이씨켐 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6579 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 112610 | 씨에스윈드 | Battery and Energy Storage | TDG Transdigm Group Incorporated | HIGH 0.7448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 113810 | 디젠스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6479 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114090 | GKL | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7446 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114120 | 크루셜텍 | Listed Operating Company | CNC Centene | LOW 0.188 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 114130 | 거북선5호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 114140 | 거북선6호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 114190 | 강원에너지 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5719 | industry | not_low_confidence | us_market_relative_proxy |
| 114410 | 현대푸드시스템 | Software | UBER Uber Technologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 114450 | 그린생명과학 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6598 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114570 | 지스마트글로벌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 114630 | 폴라리스우노 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6979 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114810 | 한솔아이원스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7154 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114840 | 아이패밀리에스씨 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7405 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 114920 | 대주이엔티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 115160 | 휴맥스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115180 | 큐리언트 | Biotechnology | ARCT Arcturus Therapeutics Holdings | HIGH 0.7298 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115310 | 인포바인 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6841 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115390 | 락앤락 | Listed Operating Company | MCK McKesson | LOW 0.1942 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 115440 | 우리넷 | Software | LX LexinFintech Holdings | MEDIUM 0.6115 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115450 | HLB테라퓨틱스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.6004 | industry | not_low_confidence | us_market_relative_proxy |
| 115480 | 씨유메디칼 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115500 | 케이씨에스 | Software | DXC DXC Technology | MEDIUM 0.6649 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 115530 | 씨엔플러스 | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 115570 | 스타플렉스 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6387 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115610 | 이미지스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6331 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 115960 | 연우 | Listed Operating Company | MCK McKesson | LOW 0.1986 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 116100 | 태양기계 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 117580 | 대성에너지 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.617 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 117670 | 알파칩스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6557 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 117730 | 티로보틱스 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7507 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 117930 | 한진해운 | Logistics and Transportation | GXO GXO Logistics | MEDIUM 0.6978 | industry_and_business_model | not_low_confidence | not_available |
| 118000 | 메타케어 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.5938 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 118990 | 모트렉스 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7127 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119250 | 에프지엔개발전문자기관리부동산투자회사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 119500 | 포메탈 | Metals and Materials | WS Worthington Steel, . Common Shares | MEDIUM 0.6871 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119610 | 인터로조 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5479 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119650 | KC코트렐 | Software | LSAK Lesaka Technologies | MEDIUM 0.6375 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119830 | 아이텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7053 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119850 | 지엔씨에너지 | Electrical Equipment | POR Portland General Electric | HIGH 0.7593 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 119860 | 커넥트웨이브 | Listed Operating Company | MCK McKesson | LOW 0.1934 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 120030 | 조선선재 | Metals and Materials | KMT Kennametal | MEDIUM 0.6925 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 120110 | 코오롱인더 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7921 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 120240 | 대정화금 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7247 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 120780 | 전우정밀 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 121060 | 유니포인트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 121440 | 골프존홀딩스 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.6978 | industry | not_low_confidence | us_market_relative_proxy |
| 121550 | 코크렙제15호기업구조조정부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 121600 | 나노신소재 | Metals and Materials | KMT Kennametal | MEDIUM 0.6944 | industry | not_low_confidence | us_market_relative_proxy |
| 121800 | 비덴트 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.858 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 121850 | 코이즈 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 121890 | 에스디시스템 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7265 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 121910 | 대우증권그린코리아기업인수목적회사 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 121950 | 미래에셋제1호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 122050 | 아이엘사이언스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 122290 | 동양밸류오션기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 122310 | 제노레이 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 122350 | 삼기 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6656 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122450 | KX | Investment Holding Companies | BXC Bluelinx Holdings | MEDIUM 0.6913 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122640 | 예스티 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7174 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122690 | 서진오토모티브 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.5934 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 122750 | 우리기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 122800 | 썬테크놀로지스 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 122830 | 원포유 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1262 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 122870 | 와이지엔터테인먼트 | Media and Entertainment | INSE Inspired Entertainment | HIGH 0.802 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122900 | 아이마켓코리아 | Software | ACTG Acacia Research | MEDIUM 0.6463 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 122990 | 와이솔 | Semiconductors | MEI Methode Electronics | MEDIUM 0.712 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123010 | 알엔티엑스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6339 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 123040 | 엠에스오토텍 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6619 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 123100 | 원익테라세미콘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 123160 | 히든챔피언제1호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 123260 | 파인넥스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 123290 | 한국투자신성장1호기업인수목적회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 123300 | 부국퓨쳐스타즈기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 123330 | 제닉 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.742 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123410 | 코리아에프티 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7147 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123420 | 위메이드플레이 | Interactive Entertainment | GME GameStop | MEDIUM 0.6451 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123550 | 대신증권그로쓰알파기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 123570 | 이엠넷 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7559 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123690 | 한국화장품 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7401 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123700 | 에스제이엠 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.688 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123750 | 알톤 | Hotels, Restaurants, and Leisure | XHR Xenia Hotels & Resorts | MEDIUM 0.5966 | industry | not_low_confidence | us_market_relative_proxy |
| 123840 | 뉴온 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123860 | 아나패스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6574 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 123890 | 한국자산신탁 | Real Estate | PINE Alpine Income Property Trust | HIGH 0.776 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 123910 | 에스비아이앤솔로몬드림기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 124050 | 한화에스브이명장제1호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 124500 | 아이티센글로벌 | Software | HDSN Hudson Technologies | HIGH 0.7283 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 124560 | 태웅로직스 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.7947 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 125020 | 티씨머티리얼즈 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7454 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 125210 | 아모그린텍 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.722 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 125490 | 한라캐스트 | Automobiles | GPI Group 1 Automotive | HIGH 0.7547 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126340 | 비나텍 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7498 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 126560 | 현대퓨처넷 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7619 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126600 | BGF에코머티리얼즈 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7274 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126640 | 화신정공 | Automobiles | GPI Group 1 Automotive | HIGH 0.7278 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126680 | 아이비케이에스스마트에스엠이기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 126700 | 하이비젼시스템 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7091 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126720 | 수산인더스트리 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.6786 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 126730 | 코칩 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6166 | industry | not_low_confidence | us_market_relative_proxy |
| 126870 | 앤에스 | Listed Operating Company | MCK McKesson | LOW 0.2174 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 126880 | 제이엔케이글로벌 | Energy Infrastructure | OIS Oil States International | MEDIUM 0.6425 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 127120 | 제이에스링크 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.6967 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 127160 | 매직마이크로 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 127710 | 아시아경제 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7903 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 127980 | 화인써키트 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 128540 | 에코캡 | Automobiles | F Ford Motor | MEDIUM 0.5812 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 128660 | 피제이메탈 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.7 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 128820 | 대성산업 | Energy Infrastructure | MAN ManpowerGroup | MEDIUM 0.5912 | industry | not_low_confidence | us_market_relative_proxy |
| 128910 | 동부티에스블랙펄기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 128940 | 한미약품 | Biotechnology | ZBH Zimmer Biomet Holdings | HIGH 0.7399 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 129260 | 인터지스 | Logistics and Transportation | RLGT Radiant Logistics | HIGH 0.8284 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 129890 | 앱코 | Software | LX LexinFintech Holdings | MEDIUM 0.5568 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 129920 | 대성하이텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.7182 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 130500 | GH신소재 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6374 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 130580 | 나이스디앤비 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6048 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 130660 | 한전산업 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.789 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 130740 | 티피씨글로벌 | Automobiles | F Ford Motor | MEDIUM 0.5687 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 130960 | 씨제이이앤엠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 131030 | 옵투스제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7039 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131090 | 시큐브 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6035 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131100 | 티엔엔터테인먼트 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7379 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131180 | 딜리 | Software | LX LexinFintech Holdings | MEDIUM 0.541 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131220 | 대한과학 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.5532 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131290 | 티에스이 | Semiconductors | BHE Benchmark Electronics | HIGH 0.7314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131370 | 알서포트 | Software | DXC DXC Technology | MEDIUM 0.6278 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 131390 | 원익피앤이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 131400 | 이브이첨단소재 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5196 | industry | not_low_confidence | us_market_relative_proxy |
| 131760 | 파인텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5646 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 131970 | 두산테스나 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6662 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 133750 | 메가엠디 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5093 | industry | not_low_confidence | us_market_relative_proxy |
| 133820 | 화인베스틸 | Metals and Materials | OI O-I Glass | MEDIUM 0.6507 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 134000 | 거북선7호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 134060 | 이퓨쳐 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5049 | industry | not_low_confidence | us_market_relative_proxy |
| 134380 | 미원화학 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7508 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 134580 | 탑코미디어 | Software | DXC DXC Technology | MEDIUM 0.6038 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 134780 | 에스엠화진 | Listed Operating Company | VFC V.F | LOW 0.1944 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 134790 | 시디즈 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6318 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 135160 | 무송지오씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 135270 | 세종머티리얼즈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 136150 | 원일티엔아이 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7306 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136410 | 아셈스 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7516 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136480 | 하림 | Food and Beverage | FLO Flowers Foods | HIGH 0.8461 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136490 | 선진 | Food and Beverage | FLO Flowers Foods | HIGH 0.8397 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136510 | 스마트솔루션즈 | Software | TTGT TechTarget | HIGH 0.7616 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136540 | 윈스테크넷 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6809 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 136660 | 큐엠씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 137080 | 나래나노텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5599 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 137310 | 에스디바이오센서 | Biotechnology | TH Target Hospitality | MEDIUM 0.6149 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 137400 | 피엔티 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5917 | industry | not_low_confidence | us_market_relative_proxy |
| 137940 | 넥스트아이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 137950 | 제이씨케미칼 | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6423 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 138040 | 메리츠금융지주 | Banks | CFR Cullen/Frost Bankers | MEDIUM 0.6964 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 138070 | 신진에스엠 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6595 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 138080 | 오이솔루션 | Software | PAR PAR Technology | MEDIUM 0.6815 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 138250 | 엔에스쇼핑 | Retail | BURL Burlington Stores | MEDIUM 0.5588 | industry_and_business_model | not_low_confidence | not_available |
| 138290 | 지성이씨에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 138360 | 앤로보틱스 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7266 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 138440 | 이코리아자기관리부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 138490 | 코오롱이앤피 | Listed Operating Company | SSTK Shutterstock | LOW 0.1911 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 138580 | 비즈니스온커뮤니케이션 | Listed Operating Company | T AT&T | LOW 0.2128 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 138610 | 나이벡 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5825 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 138690 | 엘아이에스 | Listed Operating Company | CNC Centene | LOW 0.2308 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 138930 | BNK금융지주 | Banks | PEBO Peoples Bancorp | HIGH 0.7473 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 139050 | 비에프랩스 | Listed Operating Company | CNC Centene | LOW 0.2027 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 139130 | iM금융지주 | Banks | NBHC National Bank Holdings | HIGH 0.7234 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 139170 | 퓨얼셀파워 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 139200 | 하이골드오션2호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 139480 | 이마트 | Retail | SPSC SPS Commerce | HIGH 0.7701 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 139670 | 키네마스터 | Software | DXC DXC Technology | MEDIUM 0.5748 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 139990 | 아주스틸 | Metals and Materials | OI O-I Glass | MEDIUM 0.6529 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 140070 | 서플러스글로벌 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 140290 | 청광건설 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 140410 | 메지온 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8384 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 140430 | 카티스 | Software | LSAK Lesaka Technologies | MEDIUM 0.5489 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 140520 | 대창스틸 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.6795 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 140610 | 엔솔바이오사이언스 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 140660 | 위월드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 140670 | 알에스오토메이션 | Automobiles | F Ford Motor | MEDIUM 0.6835 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 140860 | 파크시스템스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.5904 | industry | not_low_confidence | us_market_relative_proxy |
| 140890 | 트러스와이제7호위탁관리부동산투자회사 | Real Estate | GOOD Gladstone Commercial Real Estate Investment Trust | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | not_available |
| 140910 | 에이리츠 | Real Estate | NXDT NexPoint Diversified Real Estate Trust | HIGH 0.8448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 141000 | 비아트론 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6596 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 141020 | 디에스앤엘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 141070 | 맥스로텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 141080 | 리가켐바이오 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6539 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 142210 | 유니트론텍 | Semiconductors | FEIM Frequency Electronics | MEDIUM 0.6801 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 142280 | 녹십자엠에스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 142760 | 모아라이프플러스 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 143160 | 아이디스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5602 | industry | not_low_confidence | us_market_relative_proxy |
| 143210 | 핸즈코퍼레이션 | Automobiles | FNGR FingerMotion | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 143240 | 사람인 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6277 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 143540 | 영우디에스피 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6216 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 144510 | 지씨셀 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.6281 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 144620 | 코오롱머티리얼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 144630 | 씨아이에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 144740 | 피엠디아카데미 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 144960 | 뉴파워프라즈마 | Semiconductors | KE Kimball Electronics | HIGH 0.7208 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145020 | 휴젤 | Biotechnology | UTHR United Therapeutics | MEDIUM 0.6215 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145170 | 노브랜드 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6975 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145210 | 다이나믹디자인 | Automobiles | F Ford Motor | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145270 | 케이탑리츠 | Real Estate | NNN NNN REIT | HIGH 0.7215 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145720 | 덴티움 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.6118 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 145990 | 삼양사 | Food and Beverage | BGS B&G Foods | HIGH 0.8148 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 146060 | 율촌 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6659 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 146320 | 비씨엔씨 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7023 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 147760 | 피엠티 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5901 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 147830 | 제룡산업 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7335 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 148140 | 비디아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 148150 | 세경하이테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6994 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 148250 | 알엔투테크놀로지 | Software | GOTU Gaotu Techedu | MEDIUM 0.5976 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 148780 | 비큐AI | Software | LSAK Lesaka Technologies | MEDIUM 0.5818 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 148930 | 에이치와이티씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 149010 | 아이케이세미콘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 149130 | 케이비부국제1호개발전문위탁관리부동산투자회사 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 149300 | 아퓨어스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 149940 | 모다 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 149950 | 아바텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6786 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 149980 | 하이로닉 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5809 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 150440 | 피노텍 | Listed Operating Company | VFC V.F | LOW 0.1955 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 150840 | 인트로메딕 | Listed Operating Company | CNC Centene | LOW 0.21 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 150900 | 파수AI | Software | DXC DXC Technology | MEDIUM 0.5852 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 151750 | 테라텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 151860 | KG에코솔루션 | Automobiles | SMP Standard Motor Products | HIGH 0.7368 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 151910 | 퓨처코어 | Listed Operating Company | ACH Accendra Health | LOW 0.1868 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 152330 | 코리아오토글라스 | Automobiles | F Ford Motor | MEDIUM 0.5944 | industry_and_business_model | not_low_confidence | not_available |
| 152550 | 한국투자ANKOR유전해외자원개발특별자산투자회사1호(지분증권) | Financial Services | LPLA LPL Financial Holdings | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 153360 | 하이골드오션3호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 153460 | 네이블 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6098 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 153490 | 우리이앤엘하루틴 | Semiconductors | KE Kimball Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 153710 | 옵티팜 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.564 | industry | not_low_confidence | us_market_relative_proxy |
| 154030 | 아시아종묘 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 154040 | 다산솔루에타 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5411 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 155650 | 와이엠씨 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6421 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 155660 | DSR | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.6933 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 155900 | 바다로19호선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 155960 | 지디 | Listed Operating Company | CNC Centene | LOW 0.2088 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 156100 | 엘앤케이바이오 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5488 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 156170 | 비앤에스미디어 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 158300 | 에스에이티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 158310 | 참존글로벌 | Listed Operating Company | CNC Centene | LOW 0.227 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 158380 | 삼목강업 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 158430 | 아톤 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6637 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 159010 | 아스플로 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7539 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 159580 | 제로투세븐 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6993 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 159650 | 하이골드오션8호국제선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 159910 | 에코글로우 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6239 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 160190 | 하이젠알앤엠 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6416 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 160350 | 웹솔루스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 160550 | NEW | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7469 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 160600 | 이큐셀 | Listed Operating Company | CNC Centene | LOW 0.1867 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 160980 | 싸이맥스 | Semiconductors | KE Kimball Electronics | HIGH 0.7301 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 161000 | 애경케미칼 | Specialty Chemicals | DOW Dow | HIGH 0.7231 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 161390 | 한국타이어앤테크놀로지 | Automobiles | PAG Penske Automotive Group | HIGH 0.7745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 161570 | 더미동 | Listed Operating Company | CNC Centene | LOW 0.2031 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 161580 | 필옵틱스 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.5255 | industry | not_low_confidence | us_market_relative_proxy |
| 161890 | 한국콜마 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.8113 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 162120 | 루켄테크놀러지스 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 162300 | 신스틸 | Metals and Materials | FLXS Flexsteel Industries | MEDIUM 0.708 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 163280 | 에어레인 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7191 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 163430 | 디피코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 163560 | 동일고무벨트 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6884 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 163730 | 핑거 | Software | ACTG Acacia Research | MEDIUM 0.6546 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 164060 | 이루다 | Listed Operating Company | ACH Accendra Health | LOW 0.1873 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 165270 | 금오하이텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 166090 | 하나머티리얼즈 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7018 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 166480 | 코아스템켐온 | Biotechnology | BNTC Benitec Biopharma | MEDIUM 0.5407 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 167380 | 나무기술 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 168330 | 내츄럴엔도텍 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 168360 | 펨트론 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.512 | industry | not_low_confidence | partial_direct_similarity |
| 168490 | 한국투자패러랠유전해외자원개발특별자산투자회사1호(지분증권) | Financial Services | LPLA LPL Financial Holdings | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 169330 | 엠브레인 | Software | LSAK Lesaka Technologies | MEDIUM 0.6094 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 169670 | 코스텍시스템 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 170030 | 현대공업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6858 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 170790 | 파이오링크 | Software | LX LexinFintech Holdings | MEDIUM 0.5719 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 170900 | 동아에스티 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6975 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 170920 | 엘티씨 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6803 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 171010 | 램테크놀러지 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6344 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 171090 | 선익시스템 | Biotechnology | NAGE Niagen Bioscience | MEDIUM 0.5612 | industry | not_low_confidence | us_market_relative_proxy |
| 171120 | 라이온켐텍 | Metals and Materials | KRT Karat Packaging | MEDIUM 0.6796 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 172580 | 하이골드오션12호국제선박투자회사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 172670 | 에이엘티 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6861 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 173130 | 오파스넷 | Software | ACTG Acacia Research | MEDIUM 0.642 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 173940 | 에프엔씨엔터 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7634 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 174880 | 장원테크 | Software | UBER Uber Technologies | HIGH 0.7571 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 174900 | 앱클론 | Biotechnology | LAB Standard BioTools | MEDIUM 0.6437 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 175140 | 휴먼테크놀로지 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5925 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 175250 | 아이큐어 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 175330 | JB금융지주 | Banks | GBFH GBank Financial Holdings | MEDIUM 0.7138 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 176440 | 미래오토스 | Automobiles | F Ford Motor | MEDIUM 0.5944 | industry_and_business_model | not_low_confidence | not_available |
| 176560 | 포인트엔지니어링 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5823 | industry_and_business_model | not_low_confidence | not_available |
| 176590 | 코나솔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 176750 | 듀켐바이오 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7175 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 177350 | 베셀 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.5315 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 177830 | 파버나인 | Semiconductors | KE Kimball Electronics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 177900 | 쓰리에이로직스 | Software | GOTU Gaotu Techedu | MEDIUM 0.6049 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 178320 | 서진시스템 | Electrical Equipment | LECO Lincoln Electric Holdings, . Common Shares | MEDIUM 0.6877 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 178600 | 대동고려삼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 178780 | 일월지엠엘 | Retail | CBRL Cracker Barrel Old Country Store | HIGH 0.7424 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 178920 | PI첨단소재 | Metals and Materials | KMT Kennametal | MEDIUM 0.6678 | industry | not_low_confidence | us_market_relative_proxy |
| 179280 | 스탠다드펌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 179290 | 엠아이텍 | Biotechnology | ACHC Acadia Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 179440 | 비지스틸 | Metals and Materials | CMC Commercial Metals | MEDIUM 0.6259 | industry_and_business_model | not_low_confidence | not_available |
| 179530 | 애드바이오텍 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5574 | industry | not_low_confidence | us_market_relative_proxy |
| 179720 | 머니무브 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1265 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 179900 | 유티아이 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.623 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 180060 | 탑선 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 180400 | DXVX | Biotechnology | BNTC Benitec Biopharma | MEDIUM 0.5521 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 180640 | 한진칼 | Aerospace and Defense | AAL American Airlines Group | HIGH 0.7505 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 181340 | 이즈미디어 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | HIGH 0.8167 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 181710 | NHN | Software | REZI Resideo Technologies | HIGH 0.731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 181980 | 자원메디칼 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 182360 | 큐브엔터 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7823 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 182400 | 엔케이젠바이오텍코리아 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.6649 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 182690 | 테라셈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 183190 | 아세아시멘트 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7674 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 183300 | 코미코 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7067 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 183350 | 엘피케이로보틱스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 183410 | 골프존클라우드 | Hotels, Restaurants, and Leisure | H Hyatt Hotels Class A | HIGH 0.7476 | industry_and_business_model | not_low_confidence | not_available |
| 183490 | 엔지켐생명과학 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5406 | industry | not_low_confidence | us_market_relative_proxy |
| 184230 | SGA솔루션즈 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6174 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 185190 | 수프로 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 185280 | 이푸른 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 185490 | 아이진 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5323 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 185750 | 종근당 | Biotechnology | SEM Select Medical Holdings | HIGH 0.764 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 186230 | 그린플러스 | Metals and Materials | OI O-I Glass | MEDIUM 0.6304 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 187220 | 디티앤씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 187270 | 신화콘텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.645 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 187420 | HLB제넥스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 187660 | 페니트리움바이오 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.7094 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 187770 | 판타지오 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 187790 | 나노 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.73 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 187870 | 디바이스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6616 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 188040 | 바이오포트 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 188260 | 세니젠 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 189300 | 인텔리안테크 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6873 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 189330 | 씨이랩 | Software | PAR PAR Technology | MEDIUM 0.668 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 189350 | 코셋 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 189540 | 씨티네트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 189690 | 포시에스 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6079 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 189700 | 디피앤케이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 189860 | 서전기전 | Electrical Equipment | HE Hawaiian Electric Industries | MEDIUM 0.617 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 189980 | 흥국에프엔비 | Food and Beverage | FLO Flowers Foods | HIGH 0.8158 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 190510 | 나무가 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7122 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 190650 | 코리아에셋투자증권 | Banks | GBFH GBank Financial Holdings | MEDIUM 0.6822 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 191410 | 육일씨엔에쓰 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.8335 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 191420 | 테고사이언스 | Biotechnology | RGNX REGENXBIO | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 191600 | 블루탑 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 192080 | 더블유게임즈 | Interactive Entertainment | BYD Boyd Gaming | HIGH 0.7602 | industry | not_low_confidence | us_market_relative_proxy |
| 192240 | 나이코 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 192250 | 케이사인 | Software | DXC DXC Technology | MEDIUM 0.6067 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 192390 | 윈하이텍 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.5922 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 192400 | 쿠쿠홀딩스 | Software | RCMT RCM Technologies | MEDIUM 0.6491 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 192410 | 오늘이엔엠 | Software | GOTU Gaotu Techedu | MEDIUM 0.6478 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 192440 | 슈피겐코리아 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7092 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 192520 | 경남은행 | Banks | USB U.S. Bancorp | HIGH 0.7528 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 192530 | 광주은행 | Banks | USB U.S. Bancorp | HIGH 0.7527 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 192650 | 드림텍 | Semiconductors | FEIM Frequency Electronics | HIGH 0.7429 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 192820 | 코스맥스 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.8033 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 193250 | 링크드 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.571 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194370 | 제이에스코퍼레이션 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7631 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194480 | 데브시스터즈 | Interactive Entertainment | GME GameStop | MEDIUM 0.6943 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194510 | 넥스쳐 | Listed Operating Company | T AT&T | LOW 0.2108 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 194610 | 우성아이비 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 194700 | 노바렉스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5996 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 194860 | 에스와이이노베이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 195440 | 퓨전 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 195500 | 마니커에프앤지 | Food and Beverage | FLO Flowers Foods | HIGH 0.8128 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 195870 | 해성디에스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7067 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 195940 | HK이노엔 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7446 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 195990 | 에이비프로바이오 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 196170 | 알테오젠 | Biotechnology | HALO Halozyme Therapeutics | HIGH 0.8106 | industry_and_business_model | not_low_confidence | not_available |
| 196300 | HLB펩 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 196450 | 코아시아씨엠 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6423 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 196490 | 디에이테크놀로지 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5564 | industry | not_low_confidence | us_market_relative_proxy |
| 196700 | 웹스 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6438 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 197140 | 디지캡 | Software | LSAK Lesaka Technologies | MEDIUM 0.5928 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 197210 | 리드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 198080 | 캐프 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6549 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 198440 | 강동씨앤엘 | Metals and Materials | OI O-I Glass | MEDIUM 0.707 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 198940 | 한주라이트메탈 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199150 | 데이터스트림즈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 199290 | 바이오프로테크 | Biotechnology | TECH Bio-Techne | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 199430 | 케이엔알시스템 | Software | PAR PAR Technology | MEDIUM 0.6503 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199480 | 뱅크웨어글로벌 | Software | LSAK Lesaka Technologies | MEDIUM 0.604 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199550 | 레이저옵텍 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199730 | 바이오인프라 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199800 | 툴젠 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6539 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199820 | 제일일렉트릭 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.752 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 199870 | 배터리솔루션즈 | Battery and Energy Storage | TSLA Tesla | MEDIUM 0.6035 | industry_and_business_model | not_low_confidence | not_available |
| 200130 | 콜마비앤에이치 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5949 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200230 | 텔콘RF제약 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6052 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200350 | 아티스트스튜디오 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7527 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200470 | 에이팩트 | Semiconductors | KE Kimball Electronics | HIGH 0.7293 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200580 | 메디쎄이 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 200670 | 휴메딕스 | Biotechnology | HRMY Harmony Biosciences Holdings | HIGH 0.7231 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200710 | 에이디테크놀로지 | Semiconductors | KE Kimball Electronics | HIGH 0.7344 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200780 | 비씨월드제약 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6144 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 200880 | 서연이화 | Automobiles | GPI Group 1 Automotive | HIGH 0.7331 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 201490 | 미투온 | Interactive Entertainment | GME GameStop | MEDIUM 0.6492 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 202960 | 판도라티비 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 203400 | 에이비온 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.7159 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 203450 | 유니온바이오메트릭스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 203650 | 드림시큐리티 | Software | PRTH Priority Technology Holdings | MEDIUM 0.648 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 203690 | 아크솔루션스 | Software | GWAV Greenwave Technology Solutions | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 204020 | 그리티 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7004 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204210 | JK리버스톤리츠 | Real Estate | FVR FrontView REIT | HIGH 0.8394 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204270 | 제이앤티씨 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.7042 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204320 | HL만도 | Automobiles | GPI Group 1 Automotive | HIGH 0.7832 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204440 | 대우기업인수목적2호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 204610 | 티쓰리 | Interactive Entertainment | BYD Boyd Gaming | HIGH 0.7321 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204620 | 글로벌텍스프리 | Banks | FVCB FVCBankcorp | HIGH 0.7745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204630 | 스튜디오산타클로스엔터테인먼트 | Media and Entertainment | PENN PENN Entertainment | HIGH 0.8382 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204650 | 케이티비기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 204690 | 다린 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 204760 | 현대에이블기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 204840 | 지엘팜텍 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6873 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 204990 | 코썬바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 205100 | 엑셈 | Software | DXC DXC Technology | MEDIUM 0.6412 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 205290 | 케미메디 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 205470 | 휴마시스 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.5246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 205500 | 넥써쓰 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.7136 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 206400 | 베노티앤알 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.5759 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 206560 | 덱스터 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7398 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 206640 | 바디텍메드 | Biotechnology | PBYI Puma Biotechnology | HIGH 0.732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 206650 | 유바이오로직스 | Biotechnology | RIGL Rigel Pharmaceuticals | MEDIUM 0.6251 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 206660 | 골든브릿지제2호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 206950 | 볼빅 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 207230 | 디와이엘엔제이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 207490 | 에이펙스인텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 207720 | 엔에이치에스엘기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 207760 | 미스터블루 | Software | LSAK Lesaka Technologies | MEDIUM 0.5745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 207930 | 에스케이제1호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 207940 | 삼성바이오로직스 | Biotechnology | TMO Thermo Fisher Scientific | MEDIUM 0.6493 | industry | not_low_confidence | direct_financial_similarity |
| 208140 | 정다운 | Food and Beverage | FLO Flowers Foods | HIGH 0.833 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 208340 | 파멥신 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1856 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 208350 | 지란지교시큐리티 | Software | DXC DXC Technology | MEDIUM 0.5635 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 208370 | 셀바스헬스케어 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 208640 | 썸에이지 | Interactive Entertainment | SEGG Sports Entertainment Gaming Global | MEDIUM 0.62 | industry | not_low_confidence | direct_financial_similarity |
| 208710 | 포톤 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6046 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 208850 | 이비테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 208860 | 다산디엠씨 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6351 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 208870 | 하나머스트3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 208890 | 미래엔에듀파트너 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 209640 | 와이제이링크 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5574 | industry | not_low_confidence | us_market_relative_proxy |
| 210120 | 캔버스엔 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7362 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 210540 | 디와이파워 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6753 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 210610 | 소프트캠프 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 210980 | SK디앤디 | Real Estate | WSR Whitestone REIT Common Shares | HIGH 0.7642 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 211050 | 인카금융서비스 | Insurance | THG Hanover Insurance Group | HIGH 0.7908 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 211270 | AP위성 | Software | GOTU Gaotu Techedu | MEDIUM 0.6536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 212310 | 오건에코텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 212560 | 네오오토 | Automobiles | GPI Group 1 Automotive | HIGH 0.7321 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 212710 | 아이에스티이 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6808 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 213090 | 미래테크놀로지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 213420 | 덕산네오룩스 | Biotechnology | HRMY Harmony Biosciences Holdings | MEDIUM 0.5827 | industry | not_low_confidence | us_market_relative_proxy |
| 213500 | 한솔제지 | Machinery and Industrial Equipment | TITN Titan Machinery | MEDIUM 0.7031 | industry | not_low_confidence | us_market_relative_proxy |
| 214150 | 클래시스 | Biotechnology | UTHR United Therapeutics | MEDIUM 0.6306 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214180 | 헥토이노베이션 | Software | PRTH Priority Technology Holdings | MEDIUM 0.676 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214260 | 라파스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 214270 | FSN | Software | DXC DXC Technology | MEDIUM 0.6292 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214310 | 로아앤코 | Listed Operating Company | CHRS Coherus Oncology | LOW 0.1811 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 214320 | 이노션 | Media and Entertainment | INSE Inspired Entertainment | HIGH 0.7996 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214330 | 금호에이치티 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6569 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214370 | 케어젠 | Biotechnology | THC Tenet Healthcare | MEDIUM 0.6508 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214390 | 경보제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6934 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214420 | 토니모리 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7385 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214430 | 아이쓰리시스템 | Software | HDSN Hudson Technologies | MEDIUM 0.6913 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214450 | 파마리서치 | Biotechnology | ADMA ADMA Biologics | MEDIUM 0.625 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 214610 | 롤링스톤 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214680 | 디알텍 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5383 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 214870 | 한울비앤씨 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1871 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 215000 | 골프존 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.669 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215050 | 비엔디생활건강 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 215090 | 솔디펜스 | Software | AIRS AirSculpt Technologies | MEDIUM 0.6044 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 215100 | 로보로보 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5996 | industry | not_low_confidence | us_market_relative_proxy |
| 215200 | 메가스터디교육 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.6253 | industry | not_low_confidence | us_market_relative_proxy |
| 215360 | 우리산업 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6667 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215380 | 우정바이오 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5132 | industry | not_low_confidence | us_market_relative_proxy |
| 215480 | 토박스코리아 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.5979 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 215570 | 크로넥스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 215580 | 대우기업인수목적3호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 215600 | 신라젠 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7293 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 215750 | 미래에셋제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 215790 | 이노인스트루먼트 | Software | GOTU Gaotu Techedu | MEDIUM 0.57 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 216050 | 인크로스 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 216080 | 제테마 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 216280 | 원텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.126 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 216400 | 인바이츠바이오코아 | Biotechnology | ALHC Alignment Healthcare | MEDIUM 0.6622 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217190 | 제너셈 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6839 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217270 | 넵튠 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.6978 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217320 | 썬테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 217330 | 싸이토젠 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217480 | 에스디생명공학 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 217500 | 러셀 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6612 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217590 | 티엠씨 | Software | DXC DXC Technology | MEDIUM 0.6759 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217600 | 켐온 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 217620 | 선샤인푸드 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8715 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217730 | 강스템바이오텍 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6201 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 217810 | 엔에이치기업인수목적7호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 217820 | 원익피앤이 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5615 | industry | not_low_confidence | us_market_relative_proxy |
| 217880 | 틸론 | Listed Operating Company | CNC Centene | LOW 0.2186 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 217910 | 에스제이켐 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 217950 | 파마리서치바이오 | Biotechnology | UTHR United Therapeutics | MEDIUM 0.6808 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 218150 | 미래생명자원 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8197 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 218410 | RFHIC | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.705 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 218710 | 키움제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 219130 | 타이거일렉 | Semiconductors | KE Kimball Electronics | HIGH 0.7302 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 219420 | 링크제니시스 | Software | DXC DXC Technology | MEDIUM 0.6145 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 219550 | 디와이디 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6303 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 219580 | 골든브릿지제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 219750 | 한국비티비 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 219860 | 한화에이스기업인수목적2호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 219960 | 유안타제2호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 220100 | 퓨쳐켐 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6119 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 220110 | 드림티엔터테인먼트 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 220180 | 핸디소프트 | Software | ARRY Array Technologies | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 220250 | 카이노스메드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 220260 | 켐트로스 | Specialty Chemicals | DOW Dow | MEDIUM 0.7125 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 220630 | 맘스터치앤컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 221200 | 유진기업인수목적3호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 221610 | 자안바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 221670 | 주노콜렉션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 221800 | 지구홀딩스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5754 | industry | not_low_confidence | us_market_relative_proxy |
| 221840 | 하이즈항공 | Software | AIRS AirSculpt Technologies | MEDIUM 0.6046 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 221950 | 케이비드림투게더제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 221980 | 케이디켐 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6915 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222040 | 코스맥스엔비티 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5288 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222080 | 씨아이에스 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5953 | industry | not_low_confidence | us_market_relative_proxy |
| 222110 | 팬젠 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.555 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222160 | NPX | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222390 | 케이비제8호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 222420 | 쎄노텍 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.7108 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 222520 | 솔트웍스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 222670 | 플럼라인생명과학 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 222800 | 심텍 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5857 | industry | not_low_confidence | partial_direct_similarity |
| 222810 | 세토피아 | Listed Operating Company | CNC Centene | LOW 0.1846 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 222980 | 한국맥널티 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8073 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 223040 | 교보5호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 223220 | 로지스몬 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 223250 | 드림씨아이에스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6963 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 223310 | 사토시홀딩스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 224020 | 에스케이씨에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 224060 | 더코디 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4884 | industry | not_low_confidence | us_market_relative_proxy |
| 224090 | 정다운 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 224110 | 에이텍모빌리티 | Software | DXC DXC Technology | MEDIUM 0.5644 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 224760 | 엔에스컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 224810 | 엄지하우스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 224880 | 에스지에이클라우드서비스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 225190 | LK삼양 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 225220 | 제놀루션 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 225330 | 씨엠에스에듀 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 225430 | 케이엠제약 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 225440 | 이베스트기업인수목적3호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 225530 | HC보광산업 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6749 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 225570 | 넥슨게임즈 | Interactive Entertainment | GME GameStop | MEDIUM 0.5518 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 225590 | 패션플랫폼 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6702 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 225650 | 쿠첸 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 225850 | 미애부 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 225860 | 엠앤씨생명과학 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 226320 | 잇츠한불 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.757 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226330 | 신테카바이오 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226340 | 본느 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 226350 | 아이엠텍 | Listed Operating Company | CNC Centene | LOW 0.1984 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 226360 | 케이에이치건설 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7716 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226400 | 오스테오닉 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.5237 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226440 | 시스네오텍 | Listed Operating Company | MCK McKesson | LOW 0.2165 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 226590 | 엠디바이스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6913 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 226610 | 한국비엔씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 226850 | 키움제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 226950 | 올릭스 | Biotechnology | VIR Vir Biotechnology | HIGH 0.7457 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 227100 | 프로브잇 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 227420 | 도부 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 227610 | 아우딘퓨쳐스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 227840 | 현대코퍼레이션홀딩스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.5869 | industry | not_low_confidence | us_market_relative_proxy |
| 227950 | 엔투텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5992 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 228180 | 비엘사이언스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 228340 | 동양파일 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6754 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 228670 | 레이 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 228760 | 지노믹트리 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6359 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 228850 | 레이언스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5432 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 229000 | 젠큐릭스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 229480 | 줌인터넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 229500 | 노브메타파마 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 229640 | LS에코에너지 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7875 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 230240 | 에치에프알 | Software | LSAK Lesaka Technologies | MEDIUM 0.6903 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 230360 | 에코마케팅 | Listed Operating Company | HLLY Holley | LOW 0.2604 | generic_or_mismatch | source_profile_generic_or_legacy | direct_financial_similarity |
| 230400 | 자비스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 230490 | 동부제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 230980 | 비유테크놀러지 | Software | LUMN Lumen Technologies | HIGH 0.7665 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 232140 | 와이씨 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7157 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 232270 | 케이비제9호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 232290 | 에스지에이시스템즈 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 232330 | 에스케이제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 232360 | 아스팩오일 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 232530 | 이엠티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 232680 | 라온로보틱스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7049 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 232830 | 아이티센피엔에스 | Software | LSAK Lesaka Technologies | MEDIUM 0.611 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 233190 | 미래자원엠엘 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 233250 | 메디안디노스틱 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 233990 | 질경이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1235 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 234030 | 싸이닉솔루션 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6816 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234070 | 에이원큐브텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 234080 | JW생명과학 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.703 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234100 | 폴라리스세원 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6709 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234300 | 에스트래픽 | Software | ACTG Acacia Research | MEDIUM 0.647 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234340 | 헥토파이낸셜 | Software | ACTG Acacia Research | MEDIUM 0.7016 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234690 | 녹십자웰빙 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7036 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 234920 | 자이글 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5342 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 235010 | 하이에이아이1호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 235090 | 태경피엔에스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 235980 | 메드팩토 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.7002 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 236030 | 씨알푸드 | Food and Beverage | BGS B&G Foods | HIGH 0.7297 | industry_and_business_model | not_low_confidence | not_available |
| 236200 | 슈프리마 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5564 | industry | not_low_confidence | us_market_relative_proxy |
| 236340 | 메디젠휴먼케어 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 236810 | 엔비티 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.724 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 237690 | 에스티팜 | Biotechnology | AVAH Aveanna Healthcare Holdings | HIGH 0.7263 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 237720 | 케이엠제약 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 237750 | 피앤씨테크 | Electrical Equipment | HE Hawaiian Electric Industries | MEDIUM 0.6121 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 237820 | 플레이디 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7519 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 237880 | 클리오 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7443 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238090 | 앤디포스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6939 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238120 | 얼라인드 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6728 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238170 | 엔에스엠 | Listed Operating Company | CNC Centene | LOW 0.2064 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 238200 | 비피도 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238490 | 힘스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5865 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 238500 | 솔루믹스 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1971 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 239340 | 이스트에이드 | Banks | GBFH GBank Financial Holdings | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 239610 | 에이치엘사이언스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 239890 | 피엔에이치테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6204 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 240340 | 인터코스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 240540 | 한국제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 240550 | 동방메디컬 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 240600 | 유진테크놀로지 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 240810 | 원익IPS | Semiconductors | ARW Arrow Electronics | HIGH 0.7442 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241510 | 이에스산업 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 241520 | DSC인베스트먼트 | Financial Services | JCAP Jefferson Capital | HIGH 0.7203 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241560 | 두산밥캣 | Construction and Engineering | ROAD Construction Partners | HIGH 0.7645 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 241590 | 화승엔터프라이즈 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6856 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 241690 | 유니테크노 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6721 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241710 | 코스메카코리아 | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.7664 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241770 | 메카로 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6789 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241790 | 티이엠씨씨엔에스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241820 | 피씨엘 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.5642 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 241840 | 에이스토리 | Media and Entertainment | STRZ Starz Entertainment . Common Shares | HIGH 0.732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 242040 | 나무기술 | Software | DXC DXC Technology | MEDIUM 0.7033 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 242350 | 피엔아이컴퍼니 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 242420 | 본느 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 242850 | 영현무역 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 243070 | 휴온스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7174 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 243840 | 신흥에스이씨 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5504 | industry | not_low_confidence | partial_direct_similarity |
| 243870 | 아이티센코어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 244460 | 올리패스 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6218 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 244880 | 나눔테크 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 244920 | 에이플러스에셋 | Insurance | AII American Integrity Insurance Group | HIGH 0.7983 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 245030 | 스페이스솔루션 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 245450 | 씨앤에스링크 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 245620 | EDGC | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.5993 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 246250 | 에스엘에스바이오 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6429 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 246690 | TS인베스트먼트 | Financial Services | JCAP Jefferson Capital | MEDIUM 0.6567 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 246710 | 티앤알바이오팹 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5475 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 246720 | 아스타 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5848 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 246830 | 시냅스엠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 246960 | SCL사이언스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5243 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 247300 | 인프라웨어테크놀러지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 247540 | 에코프로비엠 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.633 | industry | not_low_confidence | us_market_relative_proxy |
| 247660 | 나노씨엠에스 | Specialty Chemicals | DOW Dow | MEDIUM 0.5691 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 248020 | 젬 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 248070 | 솔루엠 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.5776 | industry | not_low_confidence | us_market_relative_proxy |
| 248170 | 샘표식품 | Food and Beverage | FLO Flowers Foods | HIGH 0.8467 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 249420 | 일동제약 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7352 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 250000 | 보라티알 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.5147 | industry | not_low_confidence | us_market_relative_proxy |
| 250030 | 진코스텍 | Listed Operating Company | MCK McKesson | LOW 0.2086 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 250060 | 모비스 | Software | LOT Lotus Technology | MEDIUM 0.6543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 250300 | 제이에스피브이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 250930 | 예선테크 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 251120 | 바이오에프디엔씨 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 251270 | 넷마블 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.6995 | industry | not_low_confidence | partial_direct_similarity |
| 251280 | 안지오랩 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 251370 | 와이엠티 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7464 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 251540 | 에스와이제이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 251630 | 브이원텍 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6871 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 251960 | 엠에프엠코리아 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1259 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 251970 | 펌텍코리아 | Software | SIGA SIGA Technologies | MEDIUM 0.5816 | industry | not_low_confidence | us_market_relative_proxy |
| 252370 | 유쎌 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 252500 | 세화피앤씨 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6668 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 252940 | 에스엠로보틱스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 252990 | 샘씨엔에스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7009 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 253450 | 스튜디오드래곤 | Media and Entertainment | INSE Inspired Entertainment | HIGH 0.7983 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 253590 | 네오셈 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7091 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 253610 | 루트락 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 253840 | 수젠텍 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5284 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 254120 | 자비스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 254160 | 제이엠멀티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 254490 | 미래반도체 | Semiconductors | KE Kimball Electronics | HIGH 0.7235 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 255220 | SG | Metals and Materials | OI O-I Glass | HIGH 0.7621 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 255440 | 야스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6611 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 256090 | 패션플랫폼 | Software | UBER Uber Technologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 256150 | 한독크린텍 | Software | LX LexinFintech Holdings | MEDIUM 0.6563 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 256630 | 포인트엔지니어링 | Semiconductors | KE Kimball Electronics | MEDIUM 0.574 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 256840 | 한국비엔씨 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.572 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 256940 | 킵스파마 | Metals and Materials | OI O-I Glass | HIGH 0.7554 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 257370 | 피엔티엠에스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5243 | industry | not_low_confidence | us_market_relative_proxy |
| 257720 | 실리콘투 | Retail | SPSC SPS Commerce | HIGH 0.8227 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 257730 | 신한제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 257990 | 나우코스 | Listed Operating Company | MCK McKesson | LOW 0.2092 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 258050 | 테크트랜스 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 258250 | 셀젠텍 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 258540 | 에스엘테라퓨틱스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 258610 | 케일럼 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6409 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 258790 | 소프트캠프 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5435 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 258830 | 세종메디칼 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 259630 | 엠플러스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5845 | industry | not_low_confidence | us_market_relative_proxy |
| 259960 | 크래프톤 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.6642 | industry | not_low_confidence | direct_financial_similarity |
| 260490 | 캐로스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 260660 | 알리코제약 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6139 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 260870 | SK시그넷 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 260930 | 씨티케이 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 260970 | 에스앤디 | Food and Beverage | FLO Flowers Foods | HIGH 0.8351 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 261200 | 덴티스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 261520 | 이지스 | Software | PAR PAR Technology | MEDIUM 0.6143 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 261780 | 아리바이오LAB | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7286 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 262260 | 에이프로 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4903 | industry | not_low_confidence | us_market_relative_proxy |
| 262760 | 엔케이맥스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 262830 | 대신밸런스제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 262840 | 아이퀘스트 | Software | DXC DXC Technology | MEDIUM 0.5797 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 263020 | 디케이앤디 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7177 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263050 | 유틸렉스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263540 | 어스앤에어로스페이스 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1867 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 263600 | 덕우전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6842 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263690 | 디알젬 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263700 | 케어랩스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 263720 | 디앤씨미디어 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.8116 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263750 | 펄어비스 | Interactive Entertainment | GME GameStop | MEDIUM 0.6353 | industry | not_low_confidence | partial_direct_similarity |
| 263770 | 유에스티 | Metals and Materials | WS Worthington Steel, . Common Shares | MEDIUM 0.6729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263800 | 데이타솔루션 | Software | ACTG Acacia Research | MEDIUM 0.6388 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263810 | 상신전자 | Semiconductors | KE Kimball Electronics | MEDIUM 0.4853 | industry | not_low_confidence | us_market_relative_proxy |
| 263860 | 지니언스 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6493 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 263920 | 휴엠앤씨 | Software | LX LexinFintech Holdings | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 264290 | 한화에이스기업인수목적3호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 264450 | 유비쿼스 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6411 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 264660 | 씨앤지하이테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6874 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 264850 | 이랜시스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5677 | industry | not_low_confidence | us_market_relative_proxy |
| 264900 | 크라운제과 | Food and Beverage | FLO Flowers Foods | HIGH 0.8354 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 265480 | 미래에셋대우기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 265520 | AP시스템 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6379 | industry | not_low_confidence | us_market_relative_proxy |
| 265560 | 영화테크 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6861 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 265740 | 엔에프씨 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7167 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 265920 | 한화수성기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 266170 | 레드우즈 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.2781 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 266350 | 팡스카이 | Listed Operating Company | ACH Accendra Health | LOW 0.1982 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 266470 | 바이오인프라생명과학 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 266870 | 파워풀엑스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 267060 | 명진홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 267080 | 세븐브로이맥주 | Food and Beverage | TAP Molson Coors Beverage Class B | HIGH 0.8652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267250 | HD현대 | Software | ACMR ACM Research, . Class A | MEDIUM 0.6973 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267260 | HD현대일렉트릭 | Electrical Equipment | POR Portland General Electric | HIGH 0.7897 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267270 | HD건설기계 | Construction and Engineering | ROAD Construction Partners | MEDIUM 0.6722 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 267290 | 경동도시가스 | Energy Infrastructure | CVI CVR Energy | MEDIUM 0.5771 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267320 | 나인테크 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5884 | industry | not_low_confidence | us_market_relative_proxy |
| 267790 | 배럴 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6965 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267810 | 앙츠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 267850 | 아시아나IDT | Software | ACTG Acacia Research | MEDIUM 0.6577 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 267980 | 매일유업 | Food and Beverage | FLO Flowers Foods | HIGH 0.8546 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 268280 | 미원에스씨 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7612 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 268600 | 셀리버리 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1827 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 269620 | 시스웍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5756 | industry | not_low_confidence | us_market_relative_proxy |
| 270020 | 이십일스토어 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 270210 | 에스알바이오텍 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 270520 | 앱튼 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7518 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 270660 | 에브리봇 | Software | KC Kingsoft Cloud Holdings | MEDIUM 0.6725 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 270870 | 뉴트리 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271400 | 알로이스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1255 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 271560 | 오리온 | Food and Beverage | FLO Flowers Foods | HIGH 0.8444 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271740 | 한국제5호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 271780 | 비엔에프머티리얼즈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 271830 | 팸텍 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6588 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271850 | 다이오진 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 271940 | 일진하이솔루스 | Automobiles | F Ford Motor | MEDIUM 0.7071 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 271980 | 제일약품 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.694 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 272110 | 케이엔제이 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6867 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 272210 | 한화시스템 | Software | TTEK Tetra Tech | MEDIUM 0.7172 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 272290 | 이녹스첨단소재 | Biotechnology | NAGE Niagen Bioscience | MEDIUM 0.5729 | industry | not_low_confidence | us_market_relative_proxy |
| 272420 | 극동자동화 | Machinery and Industrial Equipment | GIC Global Industrial | MEDIUM 0.6644 | industry_and_business_model | not_low_confidence | not_available |
| 272450 | 진에어 | Aerospace and Defense | JBLU JetBlue Airways | HIGH 0.7567 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 272550 | 삼양패키징 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5411 | industry | not_low_confidence | us_market_relative_proxy |
| 273060 | 와이즈버즈 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7536 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 273640 | 와이엠텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5752 | industry | not_low_confidence | us_market_relative_proxy |
| 274090 | 켄코아에어로스페이스 | Software | GOTU Gaotu Techedu | MEDIUM 0.6427 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 274400 | 이노시뮬레이션 | Software | PAR PAR Technology | MEDIUM 0.5953 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 275630 | 에스에스알 | Software | DXC DXC Technology | MEDIUM 0.6144 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 276040 | 스코넥 | Software | LOT Lotus Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 276240 | 엘리비젼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 276730 | 한울앤제주 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8117 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 276920 | 아이비케이에스제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 277070 | 린드먼아시아 | Financial Services | JCAP Jefferson Capital | MEDIUM 0.6587 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 277410 | 인산가 | Food and Beverage | FLO Flowers Foods | HIGH 0.8208 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 277480 | 신한제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 277810 | 레인보우로보틱스 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7361 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 277880 | 티에스아이 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5164 | industry | not_low_confidence | us_market_relative_proxy |
| 278280 | 천보 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5396 | industry | not_low_confidence | partial_direct_similarity |
| 278380 | 원바이오젠 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 278470 | 에이피알 | Household and Personal Products | ELF e.l.f. Beauty | HIGH 0.7993 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 278650 | HLB바이오스텝 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.508 | industry | not_low_confidence | us_market_relative_proxy |
| 278990 | EMB | Listed Operating Company | CNC Centene | LOW 0.1946 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 279060 | 이노벡스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 279410 | 한화에이스기업인수목적4호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 279570 | 케이뱅크 | Banks | NBHC National Bank Holdings | MEDIUM 0.7102 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 279600 | 미디어젠 | Software | LSAK Lesaka Technologies | MEDIUM 0.5745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 280360 | 롯데웰푸드 | Food and Beverage | FIZZ National Beverage | HIGH 0.8526 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 281310 | 바이오시네틱스 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 281410 | 한국제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 281740 | 레이크머티리얼즈 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7864 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 281820 | 케이씨텍 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.7133 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 282330 | BGF리테일 | Retail | SPSC SPS Commerce | HIGH 0.7745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 282690 | 동아타이어공업 | Automobiles | ROK Rockwell Automation | HIGH 0.8151 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 282720 | 금양그린파워 | Battery and Energy Storage | ABAT American Battery Technology | MEDIUM 0.6371 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 282880 | 코윈테크 | Software | PAR PAR Technology | MEDIUM 0.6821 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 283100 | 노보믹스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 284420 | 휴럼 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1259 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 284610 | 티에스트릴리온 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 284620 | 카이노스메드 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6661 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 284740 | 쿠쿠홈시스 | Software | RCMT RCM Technologies | MEDIUM 0.6623 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 285130 | SK케미칼 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7357 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 285490 | 노바텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7076 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 285770 | 라이프사이언스테크놀로지 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 285800 | 진영 | Specialty Chemicals | DOW Dow | MEDIUM 0.5839 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 286000 | 씨엔티드림 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 286750 | 나노실리칸첨단소재 | Metals and Materials | RYAM Rayonier Advanced Materials | MEDIUM 0.5086 | industry | not_low_confidence | partial_direct_similarity |
| 286940 | 롯데이노베이트 | Software | ACTG Acacia Research | MEDIUM 0.71 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 287410 | 제이시스메디칼 | Biotechnology | THC Tenet Healthcare | MEDIUM 0.666 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 287840 | 인투셀 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 288180 | 케이피항공산업 | Software | AIRS AirSculpt Technologies | MEDIUM 0.5962 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 288330 | 파라택시스코리아 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7387 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 288490 | 나라소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 288620 | 에스프리즘 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 288980 | 모아데이타 | Software | PAR PAR Technology | MEDIUM 0.5881 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 289010 | 아이스크림에듀 | Energy Infrastructure | MAN ManpowerGroup | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 289080 | SV인베스트먼트 | Financial Services | GLIBK Liberty Capital Series C GCI Group | MEDIUM 0.6627 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 289170 | 바이오텐 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 289220 | 자이언트스텝 | Software | LOT Lotus Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 289860 | 지슨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1261 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 289930 | 웨이비스 | Software | AIRS AirSculpt Technologies | MEDIUM 0.669 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 290090 | 트윔 | Software | PAR PAR Technology | MEDIUM 0.6108 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290120 | DH오토리드 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6807 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290270 | 휴네시온 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5639 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290380 | 대유 | Listed Operating Company | MCK McKesson | LOW 0.2137 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 290510 | 코리아센터 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 290520 | 신도기연 | Semiconductors | KE Kimball Electronics | MEDIUM 0.603 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290550 | 디케이티 | Semiconductors | KE Kimball Electronics | HIGH 0.7488 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290560 | 파라택시스이더리움 | Software | GTM ZoomInfo Technologies | MEDIUM 0.608 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290650 | 엘앤씨바이오 | Biotechnology | ALHC Alignment Healthcare | MEDIUM 0.6671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290660 | 다이나믹솔루션 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.6246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290670 | 대보마그네틱 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 290690 | 소룩스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7051 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290720 | 푸드나무 | Food and Beverage | BJRI BJ's Restaurants | HIGH 0.8347 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 290740 | 액트로 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6987 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 291210 | 한국제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 291230 | 엔피 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7371 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 291650 | 압타머사이언스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6077 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 291810 | 핀텔 | Software | LOT Lotus Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 293480 | 하나제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.7051 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 293490 | 카카오게임즈 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.5528 | industry | not_low_confidence | us_market_relative_proxy |
| 293580 | 나우IB | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.6998 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 293780 | 압타바이오 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5837 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 293940 | 신한알파리츠 | Real Estate | STRW Strawberry Fields REIT | HIGH 0.8235 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294090 | 이오플로우 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5477 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294140 | 레몬 | Specialty Chemicals | DOW Dow | MEDIUM 0.5515 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294570 | 쿠콘 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6916 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294630 | 서남 | Electrical Equipment | IE Ivanhoe Electric | MEDIUM 0.6459 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 294870 | IPARK현대산업개발 | Construction and Engineering | ROAD Construction Partners | HIGH 0.7418 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 295310 | 에이치브이엠 | Metals and Materials | KMT Kennametal | HIGH 0.7718 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 296160 | 프로젠 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 296520 | 가이아코퍼레이션 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 296640 | 이노에이엑스 | Software | LX LexinFintech Holdings | MEDIUM 0.5821 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 297090 | 씨에스베어링 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6901 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 297570 | 알로이스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5574 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 297890 | HB솔루션 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6741 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298000 | 효성화학 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6476 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 298020 | 효성티앤씨 | Retail | SPSC SPS Commerce | HIGH 0.8046 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298040 | 효성중공업 | Electrical Equipment | FELE Franklin Electric | HIGH 0.7837 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298050 | HS효성첨단소재 | Metals and Materials | KMT Kennametal | MEDIUM 0.6903 | industry | not_low_confidence | us_market_relative_proxy |
| 298060 | 풍전약품 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 298380 | 에이비엘바이오 | Biotechnology | AMN AMN Healthcare Services | MEDIUM 0.5985 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298540 | 더네이쳐홀딩스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298690 | 에어부산 | Aerospace and Defense | JBLU JetBlue Airways | HIGH 0.7453 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298830 | 슈어소프트테크 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6831 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 298870 | 우리벤처파트너스 | Listed Operating Company | T AT&T | LOW 0.2163 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 299030 | 하나기술 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5275 | industry | not_low_confidence | us_market_relative_proxy |
| 299170 | 더블유에스아이 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6528 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 299480 | 지앤이헬스케어 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 299660 | 셀리드 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 299670 | 에스엠비나 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 299900 | 위지윅스튜디오 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7582 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 299910 | 애닉 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.1987 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 300080 | 플리토 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6321 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 300120 | 라온피플 | Software | LSAK Lesaka Technologies | MEDIUM 0.5895 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 300720 | 한일시멘트 | Metals and Materials | KMT Kennametal | HIGH 0.7843 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 301300 | 바이브컴퍼니 | Software | PAR PAR Technology | MEDIUM 0.5507 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 302430 | 이노메트리 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5564 | industry | not_low_confidence | us_market_relative_proxy |
| 302440 | SK바이오사이언스 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.6912 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 302550 | 리메드 | Biotechnology | AKBA Akebia Therapeutics | MEDIUM 0.5376 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 302920 | 더콘텐츠온 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 303030 | 지니틱스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 303360 | 프로티아 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 303530 | 이노뎁 | Software | LSAK Lesaka Technologies | MEDIUM 0.5825 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 303810 | 동국생명과학 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5264 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 304100 | 솔트룩스 | Software | PAR PAR Technology | MEDIUM 0.6917 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 304360 | 에스바이오메딕스 | Biotechnology | VNDA Vanda Pharmaceuticals | MEDIUM 0.5816 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 304840 | 피플바이오 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 305090 | 마이크로디지탈 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 306040 | 에스제이그룹 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 306200 | 세아제강 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7537 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 306620 | 지아이에스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6509 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 307070 | 에스케이에이씨피씨제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 307160 | 하나머스트제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 307180 | 아이엘 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6832 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 307280 | 원바이오젠 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 307750 | 국전 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.5581 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 307870 | 비투엔 | Software | PAR PAR Technology | MEDIUM 0.6335 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 307930 | 컴퍼니케이 | Financial Services | JCAP Jefferson Capital | MEDIUM 0.6764 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 307950 | 현대오토에버 | Software | TTEK Tetra Tech | HIGH 0.7444 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 308080 | 바이젠셀 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7563 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 308100 | 형지글로벌 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 308170 | 씨티알모빌리티 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6266 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 308430 | 셀비온 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7327 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 308700 | 테크엔 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 309710 | 아이티켐 | Biotechnology | AVAH Aveanna Healthcare Holdings | MEDIUM 0.623 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 309900 | 티티씨디펜스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 309930 | 조이웍스앤코 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 309960 | LB인베스트먼트 | Financial Services | ECPG Encore Capital Group | MEDIUM 0.6752 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 310200 | 애니플러스 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7663 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 310210 | 보로노이 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.7131 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 310840 | 엔에이치기업인수목적13호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 310870 | 디와이씨 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6675 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311060 | 엘에이티 | Listed Operating Company | MCK McKesson | LOW 0.2202 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 311270 | 키움제5호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 311320 | 지오엘리먼트 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6999 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311390 | 네오크레마 | Food and Beverage | FLO Flowers Foods | HIGH 0.8179 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311690 | CJ 바이오사이언스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.5916 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 311840 | 대원모방 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 311960 | 인터로이드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 312610 | 에이에프더블류 | Automobiles | EVTV Envirotech Vehicles | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 313750 | 유안타제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 313760 | 캐리 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 314130 | 지놈앤컴퍼니 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6922 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 314140 | 알피바이오 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6595 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 314930 | 바이오다인 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.6581 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 315640 | 딥노이드 | Software | LOT Lotus Technology | MEDIUM 0.6321 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 316140 | 우리금융지주 | Banks | CFR Cullen/Frost Bankers | MEDIUM 0.7148 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317030 | 케이비제17호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 317120 | 라닉스 | Software | LOT Lotus Technology | MEDIUM 0.5638 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317240 | TS트릴리온 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 317320 | 한화에스비아이기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 317330 | 덕산테코피아 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6906 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317400 | 자이에스앤디 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6509 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317450 | 명인제약 | Biotechnology | HRMY Harmony Biosciences Holdings | HIGH 0.7416 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317530 | 에피소드컴퍼니 | Software | LOT Lotus Technology | MEDIUM 0.5893 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317690 | 퀀타매트릭스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6165 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317770 | 엑스페릭스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5575 | industry | not_low_confidence | us_market_relative_proxy |
| 317830 | 에스피시스템스 | Software | LSAK Lesaka Technologies | MEDIUM 0.6321 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317850 | 대모 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6728 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 317860 | 노드메이슨 | Listed Operating Company | CNC Centene | LOW 0.2045 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 317870 | 엔바이오니아 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 318000 | KBG | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6862 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 318010 | 팜스빌 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 318020 | 포인트모바일 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 318060 | 그래피 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 318160 | 셀바이오휴먼텍 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 318410 | 비비씨 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7139 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 318660 | 타임기술 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 319400 | 현대무벡스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6701 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 319660 | 피에스케이 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.7175 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 320000 | 한울반도체 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5316 | industry | not_low_confidence | us_market_relative_proxy |
| 321260 | 프로이천 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 321370 | 센서뷰 | Software | LOT Lotus Technology | MEDIUM 0.6058 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 321550 | 티움바이오 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6942 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 321820 | 아티스트컴퍼니 | Media and Entertainment | IHRT iHeartMedia, . Class A | MEDIUM 0.7055 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 322000 | HD현대에너지솔루션 | Battery and Energy Storage | TDG Transdigm Group Incorporated | HIGH 0.741 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 322180 | LS티라유텍 | Software | LSAK Lesaka Technologies | MEDIUM 0.6688 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 322190 | 베른 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 322310 | 오로스테크놀로지 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7086 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 322510 | 제이엘케이 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5593 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 322780 | 코퍼스코리아 | Media and Entertainment | IHRT iHeartMedia, . Class A | MEDIUM 0.7054 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 322970 | 무진메디 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 323210 | 이베스트이안기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 323230 | 엠에프엠코리아 | Listed Operating Company | CNC Centene | LOW 0.1892 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 323280 | 태성 | Semiconductors | AAOI Applied Optoelectronics | MEDIUM 0.5304 | industry | not_low_confidence | us_market_relative_proxy |
| 323350 | 다원넥스뷰 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6842 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 323410 | 카카오뱅크 | Banks | MTB M&T Bank | MEDIUM 0.7104 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 323940 | 케이비제18호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 323990 | 박셀바이오 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.7001 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 326030 | 에스케이바이오팜 | Biotechnology | ZBH Zimmer Biomet Holdings | HIGH 0.736 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 327260 | RF머트리얼즈 | Software | HDSN Hudson Technologies | MEDIUM 0.6852 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 327610 | 펨토바이오메드 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 327970 | 케어룸의료산업 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.46 | industry | not_low_confidence | not_available |
| 328130 | 루닛 | Biotechnology | LYEL Lyell Immunopharma | MEDIUM 0.5995 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 328380 | 솔트웨어 | Software | LX LexinFintech Holdings | MEDIUM 0.5468 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 329020 | 오션스톤 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 329050 | 구스앤홈 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 329180 | HD현대중공업 | Software | DELL Dell Technologies . Class C | MEDIUM 0.6993 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 329560 | 상상인이안제2호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 330350 | 위더스제약 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6988 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 330590 | 롯데리츠 | Real Estate | NNN NNN REIT | HIGH 0.8255 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 330730 | 스톤브릿지벤처스 | Financial Services | JCAP Jefferson Capital | MEDIUM 0.6742 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 330860 | 네패스아크 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6994 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 330990 | 케이비제19호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 331380 | 포커스에이아이 | Semiconductors | MEI Methode Electronics | MEDIUM 0.481 | industry | not_low_confidence | us_market_relative_proxy |
| 331520 | 밸로프 | Interactive Entertainment | GME GameStop | MEDIUM 0.5926 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 331660 | 한국미라클피플사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 331740 | 아우토크립트 | Automobiles | F Ford Motor | MEDIUM 0.599 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 331920 | 셀레믹스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5391 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 332190 | 오션스바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 332290 | 누보 | Specialty Chemicals | EMN Eastman Chemical | MEDIUM 0.6645 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 332370 | 아이디피 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6284 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 332570 | PS일렉트로닉스 | Semiconductors | KE Kimball Electronics | HIGH 0.729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 332710 | 하나금융14호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 333050 | 이노테나 | Software | DXC DXC Technology | MEDIUM 0.5832 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 333430 | 일승 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6204 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 333620 | 엔시스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5069 | industry | not_low_confidence | us_market_relative_proxy |
| 334890 | 이지스밸류플러스리츠 | Real Estate | NNN NNN REIT | HIGH 0.7831 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 334970 | 프레스티지바이오로직스 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.7045 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 335810 | 프리시젼바이오 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 335870 | 윙스풋 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6346 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 335890 | 비올메디컬 | Biotechnology | UTHR United Therapeutics | MEDIUM 0.6735 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 336040 | 타스컴 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 336060 | 웨이버스 | Software | LX LexinFintech Holdings | MEDIUM 0.5655 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 336260 | 두산퓨얼셀 | Battery and Energy Storage | ABAT American Battery Technology | HIGH 0.7749 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 336370 | 솔루스첨단소재 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.5552 | industry | not_low_confidence | us_market_relative_proxy |
| 336570 | 원텍 | Biotechnology | HRMY Harmony Biosciences Holdings | MEDIUM 0.5927 | industry | not_low_confidence | us_market_relative_proxy |
| 336680 | 탑런토탈솔루션 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.7021 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 337450 | 에스케이제5호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 337840 | 유엑스엔 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 337930 | 젝시믹스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.74 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 338100 | NH프라임리츠 | Real Estate | NTST NetSTREIT | HIGH 0.767 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 338220 | 뷰노 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 338840 | 와이바이오로직스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6173 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 339770 | 교촌에프앤비 | Food and Beverage | LWAY Lifeway Foods | HIGH 0.8418 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 339950 | 아이비김영 | Energy Infrastructure | HPK HighPeak Energy | MEDIUM 0.5637 | industry | not_low_confidence | us_market_relative_proxy |
| 340120 | 하이제5호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 340350 | 에스케이제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 340360 | 다보링크 | Software | LSAK Lesaka Technologies | MEDIUM 0.6086 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 340440 | 세림B&G | Software | LX LexinFintech Holdings | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 340450 | 지씨지놈 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 340570 | 티앤엘 | Biotechnology | HRMY Harmony Biosciences Holdings | MEDIUM 0.5912 | industry | not_low_confidence | us_market_relative_proxy |
| 340810 | 시선AI | Software | LOT Lotus Technology | MEDIUM 0.6159 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 340930 | 유일에너테크 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4943 | industry | not_low_confidence | us_market_relative_proxy |
| 341160 | 하나금융15호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 341170 | 퓨쳐메디신 | Biotechnology | AMN AMN Healthcare Services | MEDIUM 0.527 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 341310 | 이앤에치 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 342550 | 케이비제20호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 342870 | 오아 | Software | PRTH Priority Technology Holdings | MEDIUM 0.5861 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 343090 | 에이치엘비사이언스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 343510 | 하나금융16호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 344050 | 신영해피투모로우제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 344820 | 케이씨씨글라스 | Metals and Materials | AMR Alpha Metallurgical Resources | HIGH 0.7308 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 344860 | 이노진 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6786 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 346010 | 타이드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 347000 | 센코 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5295 | industry | not_low_confidence | us_market_relative_proxy |
| 347140 | 케이프이에스제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 347700 | 스피어 | Software | REZI Resideo Technologies | MEDIUM 0.6887 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 347740 | 피엔케이피부임상연구센타 | Biotechnology | PBYI Puma Biotechnology | MEDIUM 0.6696 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 347770 | 핌스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 347850 | 디앤디파마텍 | Biotechnology | SRPT Sarepta Therapeutics | MEDIUM 0.6704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 347860 | 알체라 | Software | LOT Lotus Technology | MEDIUM 0.629 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 347890 | 엠엑스온 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5229 | industry | not_low_confidence | us_market_relative_proxy |
| 348030 | 모비릭스 | Interactive Entertainment | CRSR Corsair Gaming | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 348080 | 큐라티스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 348150 | 고바이오랩 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5208 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 348210 | 넥스틴 | Semiconductors | MX Magnachip Semiconductor | HIGH 0.7231 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 348340 | 뉴로메카 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.62 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 348350 | 위드텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6785 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 348370 | 엔켐 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.5853 | industry | not_low_confidence | us_market_relative_proxy |
| 348840 | 데이드림엔터테인먼트 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 348950 | 제이알글로벌리츠 | Real Estate | NNN NNN REIT | HIGH 0.7695 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 349720 | 이베스트기업인수목적5호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 350520 | 이지스레지던스리츠 | Real Estate | NNN NNN REIT | HIGH 0.7542 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 351020 | 미쥬 | Listed Operating Company | MCK McKesson | LOW 0.2177 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 351320 | 넥사다이내믹스 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5699 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 351330 | 이삭엔지니어링 | Software | LSAK Lesaka Technologies | MEDIUM 0.6052 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 351340 | 아이비케이에스제13호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 351870 | 차이커뮤니케이션 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7312 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352090 | 스톰테크 | Software | LX LexinFintech Holdings | MEDIUM 0.6989 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352480 | 씨앤씨인터내셔널 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7626 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352700 | 씨앤투스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6595 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 352770 | 셀레스트라 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352820 | 하이브 | Media and Entertainment | LUCK Lucky Strike Entertainment Class A | HIGH 0.7583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352910 | 오비고 | Software | LSAK Lesaka Technologies | MEDIUM 0.6323 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 352940 | 인바이오 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.4916 | industry | not_low_confidence | us_market_relative_proxy |
| 353060 | 에이치엠씨아이비제5호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 353070 | 에이치엠씨아이비제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 353190 | 휴럼 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 353200 | 대덕전자 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6597 | industry | not_low_confidence | us_market_relative_proxy |
| 353490 | 미래에셋대우기업인수목적5호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 353590 | 오토앤 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6399 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 353810 | 이지바이오 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.579 | industry | not_low_confidence | us_market_relative_proxy |
| 354200 | 엔젠바이오 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 354230 | 폭스소프트 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 354320 | 알멕 | Automobiles | GT The Goodyear Tire & Rubber | HIGH 0.7253 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 354390 | 바스칸바이오제약 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 355150 | 코스텍시스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.694 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 355390 | 크라우드웍스 | Software | LOT Lotus Technology | MEDIUM 0.5892 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 355690 | 에이텀 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4865 | industry | not_low_confidence | us_market_relative_proxy |
| 356680 | 엑스게이트 | Software | HDSN Hudson Technologies | HIGH 0.7366 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 356860 | 티엘비 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6998 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 356890 | 싸이버원 | Software | DXC DXC Technology | MEDIUM 0.6377 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357120 | 코람코라이프인프라리츠 | Real Estate | NNN NNN REIT | HIGH 0.7981 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357230 | 에이치피오 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5316 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357250 | 미래에셋맵스리츠 | Real Estate | NNN NNN REIT | HIGH 0.7459 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357430 | 마스턴프리미어리츠 | Real Estate | NNN NNN REIT | MEDIUM 0.7095 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357550 | 석경에이티 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7989 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357580 | 아모센스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.687 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357780 | 솔브레인 | Semiconductors | BHE Benchmark Electronics | HIGH 0.7236 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 357880 | SKAI | Software | PAR PAR Technology | MEDIUM 0.6936 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 358570 | 지아이이노베이션 | Biotechnology | LAB Standard BioTools | MEDIUM 0.6314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 359090 | 씨엔알리서치 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6448 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 360070 | 탑머티리얼 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 360350 | 코셈 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5198 | industry | not_low_confidence | us_market_relative_proxy |
| 361390 | 제노코 | Software | LSAK Lesaka Technologies | MEDIUM 0.641 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 361570 | 알비더블유 | Media and Entertainment | GTN Gray Media | HIGH 0.7641 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 361610 | SK아이이테크놀로지 | Semiconductors | NVTS Navitas Semiconductor | MEDIUM 0.5568 | industry | not_low_confidence | us_market_relative_proxy |
| 361670 | 삼영에스앤씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 362320 | 청담글로벌 | Retail | EVCM EverCommerce | HIGH 0.7496 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 362990 | 드림인사이트 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.744 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 363250 | 진시스템 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6671 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 363260 | 모비데이즈 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7425 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 363280 | 티와이홀딩스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6455 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 364950 | 에이아이코리아 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 365270 | 큐라클 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7723 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 365330 | 에스와이스틸텍 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6896 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 365340 | 성일하이텍 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.5922 | industry | not_low_confidence | us_market_relative_proxy |
| 365550 | ESR켄달스퀘어리츠 | Real Estate | STRW Strawberry Fields REIT | HIGH 0.7859 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 365590 | 하이딥 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5879 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 365900 | 브이씨 | Hotels, Restaurants, and Leisure | PK Park Hotels & Resorts | MEDIUM 0.5896 | industry | not_low_confidence | us_market_relative_proxy |
| 366030 | 공구우먼 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7466 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 366330 | 신한제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 367000 | 플래티어 | Software | LSAK Lesaka Technologies | MEDIUM 0.5953 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 367340 | 디비금융제8호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 367360 | 디비금융제9호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 367460 | 유안타제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 367480 | 유안타제8호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 368030 | 창대정밀 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 368600 | 아이씨에이치 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 368770 | 파이버프로 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.5461 | industry | not_low_confidence | us_market_relative_proxy |
| 368970 | 오에스피 | Food and Beverage | UNFI United Natural Foods | HIGH 0.797 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 369370 | 블리츠웨이엔터테인먼트 | Media and Entertainment | IHRT iHeartMedia, . Class A | MEDIUM 0.7173 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 370090 | 퓨런티어 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 371950 | 풍원정밀 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6318 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 372170 | 윤성에프앤씨 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5225 | industry | not_low_confidence | us_market_relative_proxy |
| 372290 | 하나머스트7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 372320 | 큐로셀 | Biotechnology | ANIK Anika Therapeutics | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 372800 | 아이티아이즈 | Software | LSAK Lesaka Technologies | MEDIUM 0.5399 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 372910 | 한컴라이프케어 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 373110 | 엑셀세라퓨틱스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 373160 | 데이원컴퍼니 | Energy Infrastructure | RNGR Ranger Energy Services, . Class A | MEDIUM 0.5021 | industry | not_low_confidence | us_market_relative_proxy |
| 373170 | 엠아이큐브솔루션 | Software | ACTG Acacia Research | MEDIUM 0.6036 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 373200 | 엑스플러스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 373220 | LG에너지솔루션 | Battery and Energy Storage | TSLA Tesla | HIGH 0.8402 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 373340 | 유진기업인수목적6호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 375500 | DL이앤씨 | Software | HLIO Helios Technologies | HIGH 0.728 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376180 | 피코그램 | Software | LX LexinFintech Holdings | MEDIUM 0.5867 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 376190 | 엘비루셈 | Listed Operating Company | NSP Insperity | LOW 0.2017 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 376270 | HEM파마 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6066 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376290 | 씨유테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376300 | 디어유 | Software | HDSN Hudson Technologies | MEDIUM 0.6091 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376900 | 로킷헬스케어 | Biotechnology | ALHC Alignment Healthcare | MEDIUM 0.6297 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376930 | 노을 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 376980 | 원티드랩 | Software | LX LexinFintech Holdings | MEDIUM 0.5352 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377030 | 비트맥스 | Software | PAR PAR Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377190 | 디앤디플랫폼리츠 | Software | CCSI Consensus Cloud Solutions | MEDIUM 0.622 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377220 | 프롬바이오 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377300 | 카카오페이 | Software | AMKR Amkor Technology | HIGH 0.7382 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377330 | 이지트로닉스 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 377400 | 하이제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 377450 | 리파인 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6314 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377460 | 큐에이드 | Software | LX LexinFintech Holdings | MEDIUM 0.6581 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377480 | 마음AI | Software | LOT Lotus Technology | MEDIUM 0.6501 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 377630 | 삼성기업인수목적4호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 377740 | 바이오노트 | Biotechnology | KROS Keros Therapeutics | MEDIUM 0.5854 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 378340 | 필에너지 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5707 | industry | not_low_confidence | us_market_relative_proxy |
| 378800 | 샤페론 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6848 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 378850 | 화승알앤에이 | Automobiles | GPI Group 1 Automotive | MEDIUM 0.6732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 379390 | 이성씨엔아이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 380320 | 삼성머스트기업인수목적5호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 380440 | 엔에이치기업인수목적19호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 380540 | 옵티코어 | Software | GOTU Gaotu Techedu | MEDIUM 0.6622 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 380550 | 뉴로핏 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5715 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 381620 | 제닉스로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.68 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 381970 | 케이카 | Automobiles | GPI Group 1 Automotive | HIGH 0.7566 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 382150 | 온코크로스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6564 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 382480 | 지아이텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5865 | industry | not_low_confidence | us_market_relative_proxy |
| 382800 | 지앤비에스 에코 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6701 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 382840 | 원준 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5154 | industry | not_low_confidence | partial_direct_similarity |
| 382900 | 범한퓨얼셀 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6336 | industry | not_low_confidence | us_market_relative_proxy |
| 383220 | F&F | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.8011 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 383310 | 에코프로에이치엔 | Software | REZI Resideo Technologies | MEDIUM 0.6744 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 383800 | LX홀딩스 | Retail | SPSC SPS Commerce | MEDIUM 0.7135 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 383930 | 디티앤씨알오 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 384470 | 코어라인소프트 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 386580 | 한화플러스제2호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 387310 | 대신밸런스제10호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 387570 | 파인메딕스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 388050 | 지투파워 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7542 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 388210 | 씨엠티엑스 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6301 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 388220 | 하나금융19호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 388610 | 지에프씨생명과학 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 388720 | 유일로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.634 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 388790 | 라이콤 | Software | LX LexinFintech Holdings | MEDIUM 0.6583 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 388800 | 유진기업인수목적7호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 388870 | 파로스아이바이오 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389020 | 자람테크놀로지 | Software | LOT Lotus Technology | MEDIUM 0.6693 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389030 | 지니너스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5363 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389140 | 포바이포 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7635 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389260 | 대명에너지 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.7014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389470 | 인벤티지랩 | Biotechnology | ARCT Arcturus Therapeutics Holdings | HIGH 0.754 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389500 | 에스비비테크 | Software | LOT Lotus Technology | MEDIUM 0.7068 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389650 | 넥스트바이오메디컬 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.6575 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 389680 | 유디엠텍 | Software | LOT Lotus Technology | MEDIUM 0.5686 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 390110 | 애니메디솔루션 | Biotechnology | TECH Bio-Techne | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 391060 | 엔에이치기업인수목적20호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 391710 | 코닉오토메이션 | Software | LSAK Lesaka Technologies | MEDIUM 0.6522 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 393210 | 토마토시스템 | Software | LSAK Lesaka Technologies | MEDIUM 0.6527 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 393360 | 신한제8호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 393890 | 더블유씨피 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5255 | industry | not_low_confidence | us_market_relative_proxy |
| 393970 | 대진첨단소재 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5054 | industry | not_low_confidence | us_market_relative_proxy |
| 394280 | 오픈엣지테크놀로지 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6722 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 394420 | 리센스메디컬 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.615 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 394800 | 쓰리빌리언 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5535 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 395400 | SK리츠 | Real Estate | NNN NNN REIT | HIGH 0.822 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 396270 | 넥스트칩 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 396300 | 세아메카닉스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 396470 | 워트 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6838 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 396690 | 미래에셋글로벌리츠 | Real Estate | FVR FrontView REIT | HIGH 0.7958 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 396770 | 엔에이치기업인수목적22호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 397030 | 에이프릴바이오 | Biotechnology | ARCT Arcturus Therapeutics Holdings | HIGH 0.7431 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 397500 | 대신밸런스제11호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 397810 | 애드포러스 | Media and Entertainment | GTN Gray Media | HIGH 0.7704 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 397880 | 교보11호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 398120 | 에스지헬스케어 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 399720 | 가온칩스 | Semiconductors | MX Magnachip Semiconductor | HIGH 0.738 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 400560 | 하나금융20호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 400760 | NH올원리츠 | Real Estate | NNN NNN REIT | HIGH 0.775 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 400840 | 하이제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 402030 | 코난테크놀로지 | Software | PAR PAR Technology | MEDIUM 0.6872 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 402340 | SK스퀘어 | Semiconductors | MU Micron Technology | MEDIUM 0.558 | industry | not_low_confidence | us_market_relative_proxy |
| 402420 | 켈스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 402490 | 그린리소스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7026 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 403360 | 라피치 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 403490 | 우듬지팜 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8137 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 403550 | 쏘카 | Logistics and Transportation | GXO GXO Logistics | HIGH 0.8087 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 403810 | 아이엘로보틱스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 403850 | 더핑크퐁컴퍼니 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.7674 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 403870 | HPSP | Semiconductors | ARW Arrow Electronics | MEDIUM 0.6967 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 404950 | 디비금융제10호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 404990 | 신한서부티엔디리츠 | Real Estate | NNN NNN REIT | HIGH 0.7806 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 405000 | 플라즈맵 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 405100 | 큐알티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7066 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 405350 | 아이비케이에스제17호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 405640 | 신한제9호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 405920 | 나라셀라 | Food and Beverage | BGS B&G Foods | HIGH 0.8065 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 406760 | 하나금융21호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 406820 | 뷰티스킨 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6451 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 407400 | 꿈비 | Software | LX LexinFintech Holdings | MEDIUM 0.5582 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 408470 | 한패스 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6189 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 408900 | 스튜디오미르 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 408920 | 메쎄이상 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6079 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 409570 | 한국제10호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 411080 | 샌즈랩 | Software | PAR PAR Technology | MEDIUM 0.6659 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 412350 | 레이저쎌 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6233 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 412540 | 제일엠앤에스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5591 | industry | not_low_confidence | us_market_relative_proxy |
| 412930 | 미래에셋비전기업인수목적1호 | Electrical Equipment | EMR Emerson Electric | HIGH 0.8104 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 413300 | 티엘엔지니어링 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.5778 | industry_and_business_model | not_low_confidence | not_available |
| 413390 | 엠오티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5645 | industry | not_low_confidence | us_market_relative_proxy |
| 413600 | 키움제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 413630 | 씨피시스템 | Software | PRTH Priority Technology Holdings | MEDIUM 0.668 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 413640 | 비아이매트릭스 | Software | LX LexinFintech Holdings | MEDIUM 0.6119 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 415380 | 스튜디오삼익 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.76 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 415580 | 상상인제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 415640 | KB발해인프라 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7766 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 416180 | 신성에스티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6139 | industry | not_low_confidence | us_market_relative_proxy |
| 417010 | 나노팀 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 417180 | 핑거스토리 | Software | LX LexinFintech Holdings | MEDIUM 0.5216 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417200 | LS머트리얼즈 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.5369 | industry | not_low_confidence | us_market_relative_proxy |
| 417310 | 코람코더원리츠 | Real Estate | NNN NNN REIT | HIGH 0.8086 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417500 | 제이아이테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6626 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417790 | 트루엔 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 417840 | 저스템 | Semiconductors | KE Kimball Electronics | HIGH 0.7304 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417860 | 오브젠 | Software | DXC DXC Technology | MEDIUM 0.6511 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 417970 | 모델솔루션 | Software | PRTH Priority Technology Holdings | MEDIUM 0.625 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 418170 | 하나금융22호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 418210 | 신한제10호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 418250 | 시큐레터 | Software | LOT Lotus Technology | MEDIUM 0.6547 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 418420 | 라온텍 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6793 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 418470 | KT밀리의서재 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.801 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 418550 | 제이오 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7386 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 418620 | E8 | Software | LOT Lotus Technology | MEDIUM 0.5851 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 419050 | 삼기에너지솔루션즈 | Automobiles | GT The Goodyear Tire & Rubber | MEDIUM 0.6125 | industry | not_low_confidence | us_market_relative_proxy |
| 419080 | 엔젯 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5281 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 419120 | 산돌 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6309 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 419270 | 신영해피투모로우제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 419530 | SAMG엔터 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.794 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 419540 | 비스토스 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 419700 | 이브이파킹서비스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 420570 | 제이투케이바이오 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5246 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 420770 | 기가비스 | Semiconductors | BHE Benchmark Electronics | HIGH 0.7346 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 421800 | 교보12호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 422040 | 엔에이치기업인수목적23호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 424140 | 케이비제21호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 424760 | 벨로크 | Software | LX LexinFintech Holdings | MEDIUM 0.5655 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 424870 | 이뮨온시아 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.7632 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 424960 | 스마트레이더시스템 | Automobiles | F Ford Motor | MEDIUM 0.5981 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 424980 | 마이크로투나노 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6687 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 425040 | 티이엠씨 | Semiconductors | KE Kimball Electronics | HIGH 0.72 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 425290 | 삼성기업인수목적6호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 425420 | 티에프이 | Semiconductors | BHE Benchmark Electronics | MEDIUM 0.6861 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 426550 | 아이비케이에스제19호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 426670 | 대신밸런스제12호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 427950 | 하나금융23호기업인수목적 | Financial Services | COF Capital One Financial | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 429270 | 시지트로닉스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5737 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 430220 | 신영해피투모로우제8호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 430230 | 하나금융24호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 430460 | 한화플러스제3호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 430690 | 한싹 | Software | LSAK Lesaka Technologies | MEDIUM 0.6059 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 430700 | 유안타제9호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 431190 | 케이쓰리아이 | Software | PAR PAR Technology | MEDIUM 0.5768 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 432320 | KB스타리츠 | Real Estate | FVR FrontView REIT | HIGH 0.7575 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 432430 | 와이랩 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7862 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 432470 | 케이엔에스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5599 | industry | not_low_confidence | us_market_relative_proxy |
| 432720 | 퀄리타스반도체 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 432980 | 엠에프씨 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6522 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 433530 | 키움제7호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 434190 | 탈로스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 434480 | 모니터랩 | Software | DXC DXC Technology | MEDIUM 0.5892 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 435380 | 유안타제10호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 435570 | 에르코스 | Food and Beverage | BGS B&G Foods | HIGH 0.8508 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 435620 | 하나금융25호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6903 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 435870 | 에스케이증권제8호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6903 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 436530 | 케이비제22호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 436610 | 한국제11호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 437730 | 삼현 | Automobiles | GPI Group 1 Automotive | HIGH 0.7784 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 437780 | 엔에이치기업인수목적24호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 438220 | 대신밸런스제13호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 438580 | 엔에이치기업인수목적25호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 438700 | 버넥트 | Software | LOT Lotus Technology | MEDIUM 0.6039 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 439090 | 마녀공장 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7597 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 439250 | 삼성기업인수목적7호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 439260 | 대한조선 | Software | PAYC Paycom Software | MEDIUM 0.6501 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 439410 | 엔에이치기업인수목적26호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 439580 | 블루엠텍 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.5285 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 439730 | 아이비케이에스제20호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 439960 | 코스모로보틱스 | Construction and Engineering | ROAD Construction Partners | MEDIUM 0.6308 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 440110 | 파두 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.6837 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 440200 | 케이비제23호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 440290 | HB인베스트먼트 | Financial Services | ECPG Encore Capital Group | MEDIUM 0.6386 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 440320 | 오픈놀 | Consumer Electronics and Appliances | WHR Whirlpool | HIGH 0.8041 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 440790 | 교보13호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 440820 | 엔에이치기업인수목적27호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 441270 | 파인엠텍 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6895 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 442130 | 유진기업인수목적9호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 442310 | 대신밸런스제14호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 442770 | 아이비케이에스제21호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 442900 | 미래에셋드림기업인수목적1호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 443060 | HD현대마린솔루션 | Software | AIT Applied Industrial Technologies | HIGH 0.7422 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 443250 | 레뷰코퍼레이션 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6118 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 443670 | 에스피소프트 | Software | DXC DXC Technology | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 444530 | 심플랫폼 | Software | PAR PAR Technology | MEDIUM 0.6475 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 444920 | 유안타제11호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 445090 | 에이직랜드 | Semiconductors | MEI Methode Electronics | MEDIUM 0.7021 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 445180 | 퓨릿 | Semiconductors | KE Kimball Electronics | MEDIUM 0.7032 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 445360 | 비엔케이제1호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 445680 | 큐리옥스바이오시스템즈 | Biotechnology | FBIO Fortress Biotech | HIGH 0.7493 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 445970 | 신영해피투모로우제9호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 446070 | 유니드비티플러스 | Metals and Materials | OI O-I Glass | MEDIUM 0.625 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 446150 | 유안타제12호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 446190 | 미래에셋비전기업인수목적2호 | Electrical Equipment | EMR Emerson Electric | HIGH 0.8091 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 446440 | 에피바이오텍 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 446540 | 메가터치 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5814 | industry | not_low_confidence | us_market_relative_proxy |
| 446600 | 카이바이오텍 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 446750 | 하나26호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 446840 | 지슨 | Software | LOT Lotus Technology | MEDIUM 0.6124 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 447690 | 아이오바이오 | Biotechnology | HCA HCA Healthcare | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 448280 | 에코아이 | Software | LX LexinFintech Holdings | MEDIUM 0.66 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 448370 | 하나27호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 448710 | 코츠테크놀로지 | Software | AIRS AirSculpt Technologies | MEDIUM 0.631 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 448730 | 삼성FN리츠 | Real Estate | STRW Strawberry Fields REIT | HIGH 0.8298 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 448740 | 삼성기업인수목적8호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 448760 | 아이비케이에스제22호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 448780 | 마이크로엔엑스 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 448830 | 미래에셋비전기업인수목적3호 | Electrical Equipment | EMR Emerson Electric | HIGH 0.8104 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 448900 | 한국피아이엠 | Automobiles | GT The Goodyear Tire & Rubber | HIGH 0.7439 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 449020 | 유안타제13호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 450050 | 하이제8호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 450080 | 에코프로머티 | Semiconductors | ARW Arrow Electronics | MEDIUM 0.5754 | industry | not_low_confidence | partial_direct_similarity |
| 450140 | 코오롱모빌리티그룹 | Automobiles | AN AutoNation | HIGH 0.7803 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 450330 | 하스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5207 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 450410 | 엔에이치기업인수목적28호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 450520 | 인스웨이브 | Software | LSAK Lesaka Technologies | MEDIUM 0.5931 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 450940 | 유안타제14호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 450950 | 아스테라시스 | Biotechnology | AMPH Amphastar Pharmaceuticals | MEDIUM 0.5864 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 451220 | 아이엠티 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6999 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 451250 | 삐아 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.731 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 451700 | 엔에이치스팩29호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 451760 | 컨텍 | Software | GOTU Gaotu Techedu | MEDIUM 0.6306 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 451800 | 한화리츠 | Real Estate | STRW Strawberry Fields REIT | HIGH 0.8235 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452160 | 제이엔비 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6094 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 452190 | 한빛레이저 | Semiconductors | KE Kimball Electronics | MEDIUM 0.601 | industry | not_low_confidence | us_market_relative_proxy |
| 452200 | 민테크 | Semiconductors | MEI Methode Electronics | MEDIUM 0.4929 | industry | not_low_confidence | us_market_relative_proxy |
| 452260 | 한화갤러리아 | Retail | EVCM EverCommerce | HIGH 0.7635 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452280 | 한선엔지니어링 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7231 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452300 | 캡스톤파트너스 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.6443 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452400 | 이닉스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 452430 | 사피엔반도체 | Semiconductors | MEI Methode Electronics | HIGH 0.732 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452450 | 피아이이 | Software | PAR PAR Technology | MEDIUM 0.6559 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 452670 | 상상인제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 452980 | 신한제11호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 453340 | 현대그린푸드 | Food and Beverage | FIZZ National Beverage | HIGH 0.8445 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 453450 | 그리드위즈 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7745 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 453860 | 에이에스텍 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6647 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 454640 | 하나29호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 454750 | 하나28호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 454910 | 두산로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6467 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 455180 | 케이지에이 | Semiconductors | MEI Methode Electronics | MEDIUM 0.48 | industry | not_low_confidence | us_market_relative_proxy |
| 455250 | 케이비제25호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 455310 | 한화플러스제4호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 455900 | 엔젤로보틱스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6364 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 455910 | 에스케이증권제9호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6903 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 456010 | 아이씨티케이 | Software | LOT Lotus Technology | MEDIUM 0.6822 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 456040 | OCI | Specialty Chemicals | DOW Dow | HIGH 0.7381 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 456070 | 이엔셀 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | MEDIUM 0.6876 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 456160 | 지투지바이오 | Biotechnology | ARCT Arcturus Therapeutics Holdings | HIGH 0.7656 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 456190 | 큐라켐 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 456440 | 디비금융제11호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6902 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 456490 | 교보14호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 456570 | 아이엠지티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 456700 | 길교이앤씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 457190 | 이수스페셜티케미컬 | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7938 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 457370 | 한켐 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6535 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 457390 | 대신밸런스제15호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 457550 | 우진엔텍 | Battery and Energy Storage | TDG Transdigm Group Incorporated | MEDIUM 0.6795 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 457600 | 벡트 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5063 | industry | not_low_confidence | us_market_relative_proxy |
| 457630 | 대신밸런스제16호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 457940 | 에스케이증권제10호기업인수목적 | Financial Services | JEF Jefferies Financial Group | MEDIUM 0.6904 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 458320 | 케이비제26호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 458350 | 에스팀 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7543 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 458610 | 한국제12호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.166 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 458650 | 성우 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5985 | industry | not_low_confidence | us_market_relative_proxy |
| 458870 | 씨어스 | Biotechnology | HRMY Harmony Biosciences Holdings | MEDIUM 0.626 | industry | not_low_confidence | us_market_relative_proxy |
| 459100 | 위츠 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6824 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 459510 | 나우로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.714 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 459550 | 알트 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6358 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 460470 | 아이빔테크놀로지 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6122 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 460850 | 동국씨엠 | Metals and Materials | AMR Alpha Metallurgical Resources | MEDIUM 0.6793 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 460860 | 동국제강 | Metals and Materials | KMT Kennametal | HIGH 0.7435 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 460870 | 에스엠씨지 | Software | PRTH Priority Technology Holdings | MEDIUM 0.4877 | industry | not_low_confidence | us_market_relative_proxy |
| 460930 | 현대힘스 | Software | HDSN Hudson Technologies | MEDIUM 0.6616 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 460940 | 피앤에스로보틱스 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.5843 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 461030 | 아이엠비디엑스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6042 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 461300 | 아이스크림미디어 | Energy Infrastructure | HPK HighPeak Energy | MEDIUM 0.5993 | industry | not_low_confidence | us_market_relative_proxy |
| 462020 | 에이치엠씨아이비제6호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 462310 | 뉴키즈온 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6325 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 462350 | 이노스페이스 | Software | LOT Lotus Technology | MEDIUM 0.6736 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 462510 | 라메디텍 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 462520 | 조선내화 | Metals and Materials | FLXS Flexsteel Industries | HIGH 0.7313 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 462860 | 더즌 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6884 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 462870 | 시프트업 | Interactive Entertainment | BYD Boyd Gaming | MEDIUM 0.7092 | industry | not_low_confidence | us_market_relative_proxy |
| 462980 | 아이지넷 | Software | DXC DXC Technology | MEDIUM 0.575 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 463020 | 뉴엔AI | Software | LSAK Lesaka Technologies | MEDIUM 0.6729 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 463480 | 모티브링크 | Automobiles | F Ford Motor | MEDIUM 0.6274 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 464080 | 에스오에스랩 | Semiconductors | INDI indie Semiconductor, . Class A | MEDIUM 0.5082 | industry | not_low_confidence | us_market_relative_proxy |
| 464280 | 티디에스팜 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6614 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 464440 | 한국제13호스팩 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 464490 | 쿼드메디슨 | Biotechnology | OFIX Orthofix Medical | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 464500 | 아이언디바이스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5894 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 464580 | 닷밀 | Media and Entertainment | AMCX AMC Global Media . Class A | HIGH 0.7366 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 464680 | KB제27호스팩 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 465320 | 교보15호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 465480 | 인스피언 | Software | PRTH Priority Technology Holdings | MEDIUM 0.6102 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 465770 | STX그린로지스 | Logistics and Transportation | HTLD Heartland Express | HIGH 0.7625 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 466100 | 클로봇 | Construction and Engineering | BLDR Builders FirstSource | MEDIUM 0.6845 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 466410 | 사이냅소프트 | Software | GTM ZoomInfo Technologies | MEDIUM 0.6237 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 466690 | 키움히어로제1호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 466910 | 엔에이치기업인수목적30호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 467930 | IBKS제23호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 468510 | 삼성기업인수목적9호 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 468530 | 프로티나 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.6401 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 468760 | 유진스팩10호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 469480 | IBKS제24호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 469610 | 이노테크 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6675 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 469750 | 아이비젼웍스 | Semiconductors | MEI Methode Electronics | MEDIUM 0.5145 | industry | not_low_confidence | us_market_relative_proxy |
| 469880 | 하나30호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 469900 | 하나31호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 471050 | 대신밸런스제17호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 471820 | 셀로맥스사이언스 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6844 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 472220 | 신영스팩10호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 472230 | SK증권제11호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 472850 | 폰드그룹 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7618 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 473000 | SK증권제12호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 473050 | 유안타제15호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 473370 | 비엔케이제2호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 473950 | SK증권제13호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 473980 | 노머스 | Media and Entertainment | PLAY Dave & Buster's Entertainment | HIGH 0.765 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 474170 | 루미르 | Software | ARRY Array Technologies | MEDIUM 0.652 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 474490 | 유안타제16호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 474610 | RF시스템즈 | Software | AIRS AirSculpt Technologies | MEDIUM 0.6739 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 474650 | 링크솔루션 | Software | LOT Lotus Technology | MEDIUM 0.6676 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 474660 | 신한제12호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 474930 | 신한제13호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 475150 | SK이터닉스 | Battery and Energy Storage | TDG Transdigm Group Incorporated | HIGH 0.7594 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475230 | 엔알비 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.6355 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 475240 | 하나32호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 475250 | 하나33호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 475400 | 씨메스로보틱스 | Construction and Engineering | MEC Mayville Engineering | MEDIUM 0.681 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475430 | 키스트론 | Electrical Equipment | HE Hawaiian Electric Industries | HIGH 0.7486 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475460 | 미트박스 | Retail | CBRL Cracker Barrel Old Country Store | MEDIUM 0.7 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475560 | 더본코리아 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7615 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475580 | 에이럭스 | Energy Infrastructure | SXC SunCoke Energy | MEDIUM 0.5776 | industry | not_low_confidence | us_market_relative_proxy |
| 475660 | 에스켐 | Semiconductors | MEI Methode Electronics | MEDIUM 0.6182 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475830 | 오름테라퓨틱 | Biotechnology | ARCT Arcturus Therapeutics Holdings | HIGH 0.769 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 475960 | 토모큐브 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.6828 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 476040 | 오가노이드사이언스 | Biotechnology | EDIT Editas Medicine | MEDIUM 0.5523 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 476060 | 온코닉테라퓨틱스 | Biotechnology | HRMY Harmony Biosciences Holdings | HIGH 0.7511 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 476080 | M83 | Media and Entertainment | IHRT iHeartMedia, . Class A | HIGH 0.7338 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 476470 | 케이비제28호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 476710 | 타조이엔터테인먼트 | Media and Entertainment | LYV Live Nation Entertainment | MEDIUM 0.6324 | industry_and_business_model | not_low_confidence | not_available |
| 476830 | 알지노믹스 | Biotechnology | LAB Standard BioTools | MEDIUM 0.633 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 477340 | 에이치엠씨제7호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 477380 | 미래에셋비전스팩4호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 477470 | 미래에셋비전스팩5호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 477530 | 한국제14호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 477760 | 디비금융스팩12호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 477850 | 마키나락스 | Software | LX LexinFintech Holdings | MEDIUM 0.628 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 478110 | 이베스트스팩6호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 478340 | 나라스페이스테크놀로지 | Software | GOTU Gaotu Techedu | MEDIUM 0.649 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 478390 | KB제29호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 478440 | 미래에셋비전스팩6호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 478560 | 블랙야크아이앤씨 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.6742 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 478780 | 대신밸런스제18호기업인수목적 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1659 | generic_or_mismatch | source_profile_generic_or_legacy | domain_first_proxy |
| 479880 | 한국제15호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 479960 | 위너스일렉 | Electrical Equipment | HE Hawaiian Electric Industries | MEDIUM 0.7135 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 480370 | 씨케이솔루션 | Software | GOTU Gaotu Techedu | MEDIUM 0.6117 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 481070 | 에이유브랜즈 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7577 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 481850 | 신한글로벌액티브리츠 | Real Estate | PINE Alpine Income Property Trust | HIGH 0.7408 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 481890 | 엔에이치스팩31호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 482520 | 교보16호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 482630 | 삼양엔씨켐 | Semiconductors | KE Kimball Electronics | HIGH 0.7218 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 482680 | 미래에셋비전스팩7호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 482690 | 대신밸런스제19호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 483650 | 달바글로벌 | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.7888 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 484120 | 도우인시스 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6933 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 484130 | 하나34호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 484590 | 삼양컴텍 | Software | AIRS AirSculpt Technologies | MEDIUM 0.6841 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 484810 | 티엑스알로보틱스 | Construction and Engineering | MEC Mayville Engineering | HIGH 0.7496 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 484870 | 엠앤씨솔루션 | Software | AIRS AirSculpt Technologies | MEDIUM 0.7085 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 486630 | KB제30호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 486990 | 노타 | Software | TTGT TechTarget | HIGH 0.7727 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 487360 | 신한제14호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 487570 | HS효성 | Investment Holding Companies | BXC Bluelinx Holdings | MEDIUM 0.7014 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 487580 | 폴레드 | Software | LX LexinFintech Holdings | MEDIUM 0.6325 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 487720 | 키움제10호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 487830 | 신한제15호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 488060 | 유진스팩11호 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 488280 | 에스투더블유 | Software | LOT Lotus Technology | MEDIUM 0.666 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 488900 | 비츠로넥스텍 | Software | GOTU Gaotu Techedu | MEDIUM 0.6633 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 489210 | 교보17호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 489460 | 바이오비쥬 | Biotechnology | EBS Emergent BioSolutions | MEDIUM 0.582 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 489480 | 키움제11호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 489500 | 엘케이켐 | Semiconductors | KE Kimball Electronics | MEDIUM 0.6899 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 489730 | 디비금융제13호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 489790 | 한화비전 | Semiconductors | BHE Benchmark Electronics | HIGH 0.7356 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 490470 | 세미파이브 | Semiconductors | MX Magnachip Semiconductor | MEDIUM 0.6936 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 491000 | 리브스메드 | Biotechnology | TH Target Hospitality | MEDIUM 0.5902 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 492220 | KB제31호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 493280 | 아이엠바이오로직스 | Biotechnology | SEM Select Medical Holdings | HIGH 0.7593 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 493330 | 지에프아이 | Semiconductors | KE Kimball Electronics | MEDIUM 0.48 | industry | not_low_confidence | partial_direct_similarity |
| 493790 | 유안타제17호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 494120 | 큐리오시스 | Biotechnology | VIR Vir Biotechnology | MEDIUM 0.6736 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 495810 | 유비씨 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 495900 | 에이엠시지 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 496070 | 신한제16호스팩 | Financial Services | DDT Dillard's Capital Trust I | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 496320 | 본시스템즈 | Software | AMKR Amkor Technology | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 498390 | 한화플러스제5호스팩 | Financial Services | BRSP BrightSpire Capital, . Class A | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 499790 | GS피앤엘 | Construction and Engineering | BLDR Builders FirstSource | HIGH 0.7367 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900010 | 3노드디지탈그룹유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900020 | 코웰이홀딩스유한공사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 900030 | 연합과기공고유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900040 | 차이나그레이트스타인터내셔널리미티드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900050 | 중국원양자원유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900060 | 중국식품포장유한공사 | Food and Beverage | TSN Tyson Foods | MEDIUM 0.6028 | industry | not_low_confidence | not_available |
| 900070 | 글로벌에스엠 | Automobiles | GPI Group 1 Automotive | HIGH 0.7555 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900080 | 에스앤씨엔진그룹리미티드 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900090 | 차이나하오란리사이클링유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900100 | 파이온엑스 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6576 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 900110 | 딥커머스 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | HIGH 0.7419 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900120 | 씨엑스아이 | Biotechnology | SEM Select Medical Holdings | MEDIUM 0.6532 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900130 | 웨이포트유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 900140 | 엘브이엠씨 | Automobiles | GPI Group 1 Automotive | HIGH 0.7935 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900150 | 성융광전투자유한공사 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 900180 | 완리인터내셔널홀딩스 | Investment Holding Companies | INGM Ingram Micro Holding | MEDIUM 0.52 | industry_and_business_model | not_low_confidence | not_available |
| 900250 | 크리스탈신소재 | Metals and Materials | OI O-I Glass | HIGH 0.7615 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900260 | 로스웰 | Software | LX LexinFintech Holdings | MEDIUM 0.6572 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900270 | 헝셩그룹 | Hotels, Restaurants, and Leisure | PK Park Hotels & Resorts | MEDIUM 0.6662 | industry | not_low_confidence | us_market_relative_proxy |
| 900280 | 케이만금세기차륜집단유한공사 | Listed Operating Company | ALIT Alight, . Class A | LOW 0.2054 | generic_or_mismatch | source_profile_generic_or_legacy | us_market_relative_proxy |
| 900290 | GRT | Specialty Chemicals | EMN Eastman Chemical | HIGH 0.7859 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 900300 | 오가닉티코스메틱 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.6698 | industry_and_business_model | not_low_confidence | direct_financial_similarity |
| 900310 | 컬러레이 | Household and Personal Products | SBH Sally Beauty Holdings, . (Name to be changed from Sally Holdings, .) | MEDIUM 0.7115 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 900340 | 윙입푸드 | Food and Beverage | FLO Flowers Foods | HIGH 0.8457 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950010 | 평산차업집단유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 950030 | 네프로아이티 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 950070 | 중국고섬공고유한공사 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 950100 | 아루히 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 950110 | SBI핀테크솔루션즈 | Software | REZI Resideo Technologies | HIGH 0.7722 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950130 | 엑세스바이오 | Biotechnology | VIR Vir Biotechnology | HIGH 0.7257 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950140 | 잉글우드랩 | Household and Personal Products | ULTA Ulta Beauty | HIGH 0.7869 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950160 | 코오롱티슈진 | Biotechnology | BBIO BridgeBio Pharma | MEDIUM 0.7118 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950170 | JTC | Retail | SPSC SPS Commerce | HIGH 0.7683 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950180 | 에스앤케이 | Listed Operating Company | SPGI.V S&P Global . When-Issued | LOW 0.1258 | generic_or_mismatch | source_profile_generic_or_legacy | not_available |
| 950190 | 고스트스튜디오 | Interactive Entertainment | GME GameStop | HIGH 0.7486 | industry | not_low_confidence | us_market_relative_proxy |
| 950200 | 소마젠 | Biotechnology | ADPT Adaptive Biotechnologies | MEDIUM 0.6523 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950210 | 프레스티지바이오파마 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.757 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
| 950220 | 네오이뮨텍 | Biotechnology | DNA Ginkgo Bioworks Holdings, . Class A | HIGH 0.767 | industry_and_business_model | not_low_confidence | us_market_relative_proxy |
| 950250 | 테라뷰 | Semiconductors | KE Kimball Electronics | MEDIUM 0.5563 | industry_and_business_model | not_low_confidence | partial_direct_similarity |
