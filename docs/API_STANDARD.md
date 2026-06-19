# API Standard

모든 비즈니스 REST API는 공통 응답 envelope를 사용한다. `/health`처럼 인프라가 직접 소비하는 운영 endpoint는 예외로 둔다.

## Success Response

```json
{
  "success": true,
  "status": 200,
  "code": "COMMON_000",
  "message": "OK",
  "data": {},
  "timestamp": "2026-06-18T00:00:00Z"
}
```

## Error Response

```json
{
  "success": false,
  "status": 422,
  "code": "COMMON_002",
  "message": "Request validation failed",
  "errors": [
    {
      "field": "body.title",
      "reason": "String should have at least 1 character"
    }
  ],
  "timestamp": "2026-06-18T00:00:00Z"
}
```

## Error Codes

| Code | HTTP | Meaning |
| --- | --- | --- |
| `COMMON_000` | 200 | Success |
| `COMMON_001` | 400 | Invalid request |
| `COMMON_002` | 422 | Validation failed |
| `COMMON_999` | 500 | Internal server error |
| `AI_001` | 503 | AI model unavailable |

## Swagger

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## Tax Document Verification

- `POST /api/v1/tax/documents/verify`
- 외부 OCR/MTS upload gateway가 추출한 텍스트와 위변조 signal을 받아 공통 envelope로 서류 검증 결과를 반환한다.
- 응답 `data.verification_status`는 `VERIFIED`, `PENDING`, `REJECTED` 중 하나이며, `fraud_risk_score`, `risk_level`, `manual_review_required`, `missing_required_fields`, `rejection_reasons`, `document_model_version`을 포함한다.
- 이 endpoint는 원본 파일을 저장하거나 국세청 제출을 수행하지 않는다.
