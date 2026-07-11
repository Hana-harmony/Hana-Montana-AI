# 글로벌 피어 Business Profile 분류기

## 목적

- KIS 공식 마스터의 활성 일반주식 전체에 구체적인 `sector`, `industry`, `business_model`, `business_tags`를 제공한다.
- 한국 종목별 정답 peer를 저장하지 않고, 프로필을 미국 상장사 후보와 동적으로 점수화하는 입력으로 사용한다.

## 입력과 모델

- 공식 KIS 종목 코드·시장·업종, Naver 업종 비교군, OpenDART 회사 업종코드, WiseReport 사업개요, 재무 규모를 결합한다.
- KSIC 업종군을 음식료·화학·의약·반도체·자동차·기계·건설·유통·물류·소프트웨어·금융 등 공통 business tag로 변환한다.
- 분류기는 `FeatureUnion(TfidfVectorizer(char_wb 2-5), TfidfVectorizer(word 1-2)) + LogisticRegression(class_weight=balanced)`를 사용한다.
- 우선주는 발행사 본주의 사업 프로필과 재무를 상속하되 종목 식별은 유지한다.

## 2026-07-11 학습 산출물

- 한국 활성 일반주식: 2,752개
- 미국 universe: 12,916개, 서빙 가능 peer: 4,714개
- 한국 업종 profile: 2,742개
- 구체 profile 적용: 2,752개
- business profile classifier 학습 표본: 2,646개, 라벨 27개
- 한국 재무 coverage: 2,656개

## 품질 게이트

- `reports/global-peer-full-coverage-report.json`은 현재 KIS universe 개수와 전체 실행 개수의 일치, 100% 성공률, 비교 3개의 차원·회사 유일성, Key Strength 4개의 근거·유일성을 검증한다.
- 상장폐지·합병 종목은 매 동기화 시점의 KIS 활성 스냅샷에서 제외한다.
