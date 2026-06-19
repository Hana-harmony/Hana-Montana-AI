# 기능정의서 구현 계약

## 적용 범위
- 이 서비스는 AI/계산/패킹 계층이다. KIS, KRX, Papago, DeepL, 국세청, 현지 MTS의 실제 계정·주문·세무 제출 실행은 외부 백엔드 어댑터가 담당한다.
- 본 구현은 외부 어댑터가 넘긴 검증된 입력값을 기준으로 국내주식 주문 상태, 뉴스·공시 인텔리전스 이벤트, 세무 환급 선지급 상태를 계산하고 단일 JSON 계약으로 반환한다.
- API는 내부 네트워크용이며 별도 사용자 토큰을 검증하지 않는다.

## 1. 한국 주식 주문
- endpoint: `POST /api/v1/stocks/order-status`
- 입력: KIS/KRX/PredictEngine에서 동기화된 종목 마스터, 현재가, 상·하한가, VI 플래그, 외국인 보유수량, 외국인 한도율, 장중 외국인 순매수 추정량.
- 파서:
  - `parse_kis_master_csv`: KIS 종목 마스터 파일의 종목코드, 국문명, 영문명, 시장, 발행주식수, 상·하한가 기준가를 정규화한다.
  - `parse_kis_realtime_packet`: KIS 실시간 현재가/VI/단일가 패킷을 정규화한다.
  - `parse_krx_foreign_holding_row`: KRX 전일 확정 외국인 보유수량, 보유율, 한도소진율을 정규화한다.
  - `build_stock_order_status_request`: 세 provider row의 종목코드 일치성을 검증하고 모델 입력을 생성한다.
- 계산:
  - 외국인 보유율 = `foreign_owned_quantity / issued_shares * 100`
  - 외국인 한도소진율 = `foreign_owned_quantity / foreign_limit_quantity * 100`
  - 당일 예측 지분율 구간 = 장중 순매수 반영 중심값 ± `prediction_confidence_interval_percent`
  - 외국인 한도 잔여 수량 = `foreign_limit_quantity - foreign_owned_quantity`
  - 외국인 한도 사용 상태 = 예측 최대치가 한도에 도달하면 `LIMIT_REACHED`, 1%p 이내 접근 시 `CAUTION`
  - VI 상태 = 동적 VI, 정적 VI, 단일가 세션 중 하나라도 있으면 `Y`
  - 제한가격 상태 = 현재가가 상한가 이상이면 `UPPER`, 하한가 이하이면 `LOWER`
  - 주문 가능 여부 = 실시간 체결 가능 상태와 외국인 한도 사용 상태를 합성해 매수/매도 가능 여부와 제한 사유 코드를 산출
- 모델:
  - `ForeignOwnershipBoundaryModel`: 외국인 지분율 및 당일 예측 boundary 산출
  - `TradingStateModel`: VI, 단일가, 상·하한가, 즉시체결 가능 여부 판정
- 출력 핵심 필드:
  - `fx_predicted_rate_min`, `fx_predicted_rate_max`
  - `foreign_limit_remaining_quantity`, `foreign_limit_usage_status`
  - `vi_activation_status`
  - `price_limit_status`
  - `immediate_execution_available`
  - `buy_order_available`, `sell_order_available`
  - `order_availability_indicator`, `order_restriction_reasons`
  - `order_guidance_message`
  - `prediction_model_version`, `trading_state_model_version`
  - `data_source="KIS/KRX/PredictEngine"`

## 2. 한국 주식 정보 취득 및 분석
- endpoint: `POST /api/v1/intelligence/events`
- 입력: Naver News/OpenDART가 수집한 제목, snippet, 원문 링크, 발행시각, 언론사, 종목 후보.
- 파서:
  - `parse_naver_news_row`: Naver News Search API row의 제목, snippet, 원문 링크, 발행시각, 언론사, 종목 후보를 정규화한다.
  - `parse_opendart_disclosure_row`: OpenDART 공시검색 row의 접수번호, 공시 제목, 회사명, 종목코드, 제출일자를 정규화하고 DART 원문 링크를 구성한다.
  - `build_intelligence_event_request`: provider row를 `IntelligenceEventRequest`로 변환한다.
  - `build_omnilens_websocket_event`: 분석·번역 완료 응답을 협력사/종목 단위 WebSocket 이벤트 JSON으로 패킹한다.
  - provider 파서는 유효하지 않은 원문 URL과 잘못된 종목코드를 거부한다.
- 처리:
  - 기존 ML 분석 엔진으로 종목 매핑, 중복키, 이벤트, 감성, 중요도, holder/watchlist target을 산출한다.
  - 현재 로컬 하네스에서는 `FinancialTranslationModel`의 `local-financial-glossary` 번역 보조 모델을 사용한다.
  - 금융 용어집은 종목명, 공시 이벤트, 재무 지표, 세무 용어의 alias를 canonical term으로 정규화하고 긴 용어부터 번역해 부분 치환 오류를 줄인다.
  - 번역 결과에는 적용된 `glossary_terms`와 `translation_quality_flags`를 포함해 현지 거래소가 품질 검수나 fallback 표시 여부를 판단할 수 있게 한다.
  - 실제 Papago/DeepL 호출은 `PapagoDeepLAdapter` 어댑터 자리로 명시하고, 계약 필드는 동일하게 유지한다.
- 출력 핵심 필드:
  - `alert_id`, `duplicate_key`, `stock_code`, `news_disclosure_type`
  - `original_title`, `translated_title`
  - `summary`, `translated_summary`
  - `sentiment`, `importance`, `event_tag`, `event_tags`
  - `is_holder_target`, `is_watchlist_target`
  - `glossary_terms`, `translation_quality_flags`
  - `translation_provider`, `translation_model_version`, `translation_status`
  - `data_source="Naver/OpenDART/NLP/PapagoDeepLAdapter"`

## 3. 최종 투자자별 세무 전산화 및 환급금 선지급
- endpoint: `POST /api/v1/tax/refund-status`
- 입력: 투자자 ID, 거주지 국가, 과세연도, OCR/위변조 검증 완료 서류, 배당·매도 거래 원장.
- 파서:
  - `parse_tax_document_rows`: MTS 업로드/OCR 결과 row를 서류 검증 모델 입력으로 정규화한다.
  - `parse_tax_transaction_rows`: 옴니버스 하위 계좌 거래 원장을 배당·매도 세무 거래 입력으로 정규화한다.
- CASE_01 판정:
  - 거주지 국가가 `HK`
  - 모든 거래가 상장주식 장내거래
  - 직전 5년 및 당해 지분율 입력값이 25% 미만
  - 거주자증명서와 제한세율신청서가 모두 `VERIFIED`, OCR 신뢰도 0.8 이상, 위변조 위험 0.2 이하
- 환급 계산:
  - 배당 환급 = 총 배당금 × 7%
  - 양도세 환급 = `min(총 매도지급액 × 11%, 양도차익 × 22%)`
  - 최종 환급 가능액 = `min(총 기납부 원천세, 배당 환급 + 양도세 환급)`
  - 국세/지방세 표시용 분해 = 환급 가능액의 10%를 지방세 환급액, 나머지를 국세 환급액으로 패킹
  - 즉시 선지급 수수료 = 환급 가능액 × `instant_payout_fee_rate`
  - 환급 진행 상태 = 서류 대기, 수동 검토, 환급 없음, 즉시 선지급 가능, 분기 환급 가능 중 하나로 산출
- 모델:
  - `TaxRefundAdvanceModel`: CASE_01 판정, 서류 검증 gate, 환급 가능액, 선지급액, 사후 환수 플래그 산출
- 출력 핵심 필드:
  - `tax_case_type`
  - `tax_year`, `refund_workflow_status`, `government_verification_ref`
  - `total_withheld_tax`
  - `eligible_refund_amount`
  - `national_tax_refund_amount`, `local_tax_refund_amount`
  - `instant_payout_fee_rate`
  - `instant_payout_amount`
  - `compliance_sandbox_flag`
  - `clawback_required_if_rejected`
  - `required_next_actions`, `risk_disclosure_message`
  - `tax_model_version`, `document_model_version`

## 하네스 보강
- `tests/test_feature_definition_contracts.py`가 기능정의서의 세 도메인 계약을 직접 검증한다.
- 주문 하네스는 외국인 한도 잔여 수량, 한도 사용 상태, 매수/매도 가능 여부, 제한 사유, VI, 상한가, 현지통화 환산, 즉시체결 제한 문구를 검증한다.
- provider parser 하네스는 KIS 마스터, KIS 실시간 패킷, KRX 외국인 보유 row를 모델 입력으로 합성하고 종목코드 불일치를 거부하는지 검증한다.
- 인텔리전스 하네스는 Naver/OpenDART provider row 파싱, API/WebSocket 중복키 생성, 종목·출처별 중복키 경계, 번역 제목, 요약, 이벤트 태그, 감성, 중요도, holder/watchlist target, WebSocket 이벤트 패킷, 데이터 출처를 검증한다.
- 세무 하네스는 CASE_01 판정, 서류 검증, 배당 7%, 양도세 `min(11%, 22%)`, 국세/지방세 분해, 진행 상태, 다음 조치, 3% 선지급 수수료, 사후 환수 플래그와 세무 provider row 파싱을 검증한다.
