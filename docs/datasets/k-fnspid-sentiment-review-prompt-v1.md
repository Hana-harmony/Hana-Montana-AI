# K-FNSPID 감성 Gold 독립 검수 프롬프트 v1

- 식별자: `k-fnspid-sentiment-review-prompt/v1`
- 적용 코드북: `k-fnspid-sentiment-codebook/v1`
- 판정 라벨: `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- 검수 유형: 사람 전문가가 아닌 분리된 Codex AI 세션

## 시작 전 계약

이 검수는 새로 생성한 독립 context에서 수행한다. 다음 정보를 context, 프롬프트, 첨부 파일, 도구 출력 또는 이전 대화로 제공받았다면 검수를 시작하지 않고 실패로 보고한다.

- 후보 모델의 라벨, 확률, logit, 설명, 오분류 이력
- Qwen 등 teacher의 라벨, 확률, 근거
- 기존 Gold와 다른 검수자의 판정
- 발표 후 주가·거래량·초과수익률과 평가 gate

검수 세션은 검수 packet, 이 문서, 고정된 감성 코드북만 읽는다. 외부 검색, 후속 기사 조회, 시세 조회, 다른 검수 run의 산출물 조회는 금지한다.

## 판정 절차

1. `item_id`와 대상 종목을 확인한다.
2. 제공된 제목·전문 또는 제목·스니펫에서 대상 기업에 직접 연결된 명제만 찾는다.
3. 코드북의 1단계에 따라 `NEUTRAL`과 `DIRECTIONAL`을 구분한다.
4. `DIRECTIONAL`일 때만 2단계에서 `POSITIVE`와 `NEGATIVE`를 구분한다.
5. 대상·부정어·조건절·인용 주체·혼합 근거를 우선순위대로 적용한다.
6. 입력만으로 책임 있는 판정이 불가능하면 임의로 클래스를 맞추지 않고 별도 제외 절차로 보낸다.

## 독립 reviewer 출력

각 행은 다음 필드만 갖는 JSON 객체로 저장한다.

```json
{
  "item_id": "document::security",
  "final_sentiment": "POSITIVE | NEUTRAL | NEGATIVE",
  "review_note": "대상 기업에 연결된 입력 내 근거와 적용 규칙",
  "reviewer_id": "가명 reviewer ID",
  "reviewed_at": "timezone이 있는 ISO-8601 시각",
  "review_status": "CODEX_REVIEW_APPROVED"
}
```

receipt에는 이 packet의 SHA-256, 코드북 SHA-256, 이 프롬프트의 SHA-256, 사용한 모델명·버전, 독립 run UUID, context UUID, 입력 행 범위, decision SHA-256를 기록한다.

## adjudicator 추가 계약

adjudicator는 두 reviewer가 불일치한 항목만 받는 새 run·새 context에서 실행한다. adjudication packet은 원본 문서와 item ID만 포함하고 두 reviewer의 라벨·근거를 노출하지 않는다. adjudicator의 독립 판정과 receipt를 먼저 봉인한 뒤에만 dual merge가 앞선 두 판정과 비교해 최종 결정을 구성한다. 후보 모델·teacher·시장 반응도 여전히 금지한다. 코드북으로 해소할 수 없으면 `UNRESOLVED`로 제외한다.

## 해석 제한

이 계약은 파일 해시와 자체 신고된 run provenance를 통해 **절차적 분리**를 감사 가능하게 한다. 동일 모델 계열의 오류 상관을 제거하거나, 사람 금융전문가 다중 주석을 대체하는 증거는 아니다.
