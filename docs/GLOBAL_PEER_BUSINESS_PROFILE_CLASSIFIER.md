# 글로벌 피어 Business Profile ML 분류기

## 목적
- 한국 종목의 `sector`, `industry`, `business_model`, `business_tags`가 generic fallback에 머무르면 글로벌 피어 매칭 confidence가 낮아진다.
- 이번 모델은 한국 전종목에 적용 가능한 business profile ML classifier를 학습해, 실제 사업 설명이 있는 종목을 구체 업종으로 승격한다.
- confidence를 강제로 올리지 않고, 원천 business profile이 구체화된 경우에만 피어 매칭 결과가 개선되도록 한다.

## 모델 구조
- 분류기: `FeatureUnion(TfidfVectorizer(char_wb 2-5), TfidfVectorizer(word 1-2)) + LogisticRegression(class_weight=balanced)`
- 강한 라벨: Naver 업종 비교군에서 이미 구체 sector/industry가 잡힌 한국 종목 2,639개
- 약지도 라벨: WiseReport 사업개요에서 고신뢰 사업 태그가 추출된 generic 후보 20개
- 약지도 가중치: 8.0
- 주요 입력 feature: 종목명, alias, Naver 업종/비교군, OpenDART 회사 업종코드, WiseReport 사업개요, 재무 규모 토큰

## 학습 및 평가
- 전체 한국 universe: 3,967개
- 전체 미국 universe: 12,916개
- business profile classifier 학습 샘플: 2,659개
- 라벨 수: 27개
- holdout 평가 표본: 528개
- holdout accuracy: 0.973485
- holdout macro F1: 0.967205
- holdout weighted F1: 0.974094
- 회사 프로필 캐시: 2,881개
- 사업개요 캐시: 2,565개

## 전종목 피어 성능
- 전종목 추론: 3,967 / 3,967 성공
- 전체 LOW confidence: 878개, 22.1326%
- specific profile 종목: 3,089개
- specific profile LOW confidence: 0개
- 동일회사 중복 노이즈: 0개
- full coverage gate: pass
- all-results quality gate: pass

## 기존 LOW 후보 12개 개선 결과
| 종목코드 | 종목명 | 최종 세부 분야 | primary peer | confidence | root cause |
| --- | --- | --- | --- | --- | --- |
| 003580 | HLB글로벌 | Food and Beverage | UNFI United Natural Foods | HIGH 0.8205 | not_low_confidence |
| 007720 | 소노스퀘어 | Retail | NEGG Newegg Commerce | MEDIUM 0.4945 | not_low_confidence |
| 009810 | 플레이그램 | Software | LSAK Lesaka Technologies | MEDIUM 0.5854 | not_low_confidence |
| 019660 | 글로본 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | not_low_confidence |
| 032860 | 더라미 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | not_low_confidence |
| 051160 | 지어소프트 | Software | ACTG Acacia Research | MEDIUM 0.6231 | not_low_confidence |
| 051390 | YW | Retail | CBRL Cracker Barrel Old Country Store | MEDIUM 0.5264 | not_low_confidence |
| 052020 | 에스티큐브 | Biotechnology | LAB Standard BioTools | MEDIUM 0.6332 | not_low_confidence |
| 063170 | 서울옥션 | Art and Collectibles Marketplace | ACVA ACV Auctions | HIGH 0.901 | not_low_confidence |
| 064090 | 인크레더블버즈 | Household and Personal Products | LVLU Lulu's Fashion Lounge Holdings | MEDIUM 0.62 | not_low_confidence |
| 080010 | 이상네트웍스 | Machinery and Industrial Equipment | TITN Titan Machinery | HIGH 0.7455 | not_low_confidence |
| 102370 | 케이옥션 | Art and Collectibles Marketplace | ACVA ACV Auctions | HIGH 0.8993 | not_low_confidence |

## 남은 한계
- 남은 LOW 878개는 모두 `source_profile_generic_or_legacy`다.
- 이들은 WiseReport/OpenDART/Naver 데이터만으로 아직 구체 사업 프로필이 충분히 확보되지 않은 종목이거나, 상장폐지·합병·스팩·비일반 거래 종목이 섞인 legacy universe 후보일 수 있다.
- 운영에서는 전종목 추론은 유지하되, 일반 거래가능 종목 universe를 별도 필터링해 남은 generic 후보를 계속 줄인다.
