# ADR-002 세무 서류 OCR 검증 경계

## 상태
Accepted

## 맥락
세무 서류 업로드 흐름은 거래소 FE, Stock-exchange-BE, Hana-OmniLens-API, Hannah-Montana-AI가 함께 처리한다. FE와 거래소 BE는 최종투자자 파일 저장, 계좌 권한, 제출 상태를 담당하지만 OCR 모델과 문서별 검증 규칙은 AI 서비스 경계에 있어야 한다.

기존 `/api/v1/tax/documents/verify`는 외부에서 전달한 OCR 텍스트와 confidence를 검증하는 계약이었다. 이 방식은 MTS upload gateway가 별도 OCR을 수행할 때는 유효하지만, 거래소 BE가 파일 bytes를 직접 전달하는 경우 실제 OCR 실행 없이 임의 confidence를 넣을 위험이 있다.

## 결정
Hannah-Montana-AI가 세무 서류 OCR 검증 API의 모델 경계를 가진다.

- `document_content_base64` 이미지/PDF payload는 Hannah가 임시 파일로 격리하고 하네스와 공유하는 `TaxDocumentPipeline`에서 Tesseract 전체·영역 OCR을 실행한다.
- OCR 결과는 `hanah_tax_ocr` parser/reviewer로 필드 추출, 문서별 규칙, 수동검수 필요 여부를 판단한다.
- `extracted_text`만 전달되는 기존 협력사 경로는 호환용 rule gate로 유지한다.
- `paddleocr`, `paddlepaddle`, `opencv-python-headless`는 API 컨테이너 런타임 의존성에 포함한다.
- OCR 엔진이 없거나 파일을 읽을 수 없으면 임의 승인하지 않고 manual review/rejection reason을 반환한다.
- Stock-exchange-BE와 Hana-OmniLens-API는 OCR confidence와 fraud score를 만들어내지 않고 파일 payload와 기대 식별자만 전달한다.

## 보안 및 운영
- 파일 bytes는 Hannah 프로세스의 임시 파일로만 저장하고 요청 처리 후 삭제한다.
- 협력사 API key나 최종투자자 credential은 Hannah에 저장하지 않는다.
- OCR confidence는 모델 산출값으로만 응답하며, upstream이 임의로 제공한 값은 파일 payload 검증 경로에서 통과 조건으로 사용하지 않는다.
- OCR 엔진 장애는 성공 fallback이 아니라 관측 가능한 실패/수동검수 상태로 노출한다.

## 결과
거래소 앱의 세무 제출 버튼은 세 문서가 모두 `HANNAH_MONTANA_AI_TAX_OCR` 출처로 `VERIFIED`되고 manual review가 false일 때만 제출 완료로 진행한다.
