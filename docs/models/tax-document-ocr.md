# 세무 문서 OCR 검증

## 목적과 API

`POST /api/v1/tax/documents/verify`에서 거주자 증명서, 아포스티유, 제한세율 적용신청서의 진위 위험과 필수 정보를 검증한다.

## 파이프라인

1. base64를 제한 크기로 decode하고 이미지/PDF signature, MIME과 파일 유형을 검증한다.
2. Tesseract `kor+eng` OCR로 텍스트와 confidence를 추출한다.
3. 문서별 parser가 성명, 거주국, 발급일·유효기간, 인증·세율 신청 필드를 정규화한다.
4. reviewer가 필수 필드, 날짜, 예상 거주국, 문서 간 일관성과 위변조 신호를 검사한다.
5. `VERIFIED`, `REVIEW_REQUIRED`, `REJECTED`, 누락 필드, 거절 사유, 위험도와 `hanah-tax-ocr-e2e-review-v2`를 반환한다.

OCR이 불가능하거나 신뢰도가 낮은 입력을 임의 승인하지 않는다. 원본 파일은 이 서버에 영구 저장하지 않으며 사용자 식별자를 OCR 요청에 포함하지 않는다.

## 지원과 한계

- 이미지와 PDF를 지원한다. PDF renderer 또는 OCR runtime이 없으면 명시적 검수 상태로 종료한다.
- 판독 결과는 서류 접수 전 검증 보조이며 법적 진위 확인이나 정부 승인을 대체하지 않는다.
- 실제 표본 확장, 언어·서식 drift, 위변조 adversarial set은 지속 평가 대상이다.

## 검증

- `tests/test_tax_ocr_engine.py`
- `src/hanah_tax_ocr/evaluation.py`
- `docs/adr/ADR-002-tax-document-ocr.md`
