# Responsible NLP 및 제출 자체 점검

기준: ACL Rolling Review 장문 익명 심사 형식과 Responsible NLP Research checklist.

## 과학적 주장

- [x] 공개 감성 Test를 과거 반복 조회된 진단 자료로 명시했다.
- [x] Checkpoint/Calibration/Selection을 group-disjoint 50/25/25로 분리했다.
- [x] 데이터 seed `20260715`와 모델 seed `17/42/73`을 분리했다.
- [x] 공정 KR-FinBERT-SC 기준선을 동일 원천행·split·seed·epoch·update 일정의 전체 fine-tuning으로 정의했다.
- [x] NEWS·DISCLOSURE별 세 기준선 비교 6개와 Holm 보정을 사전 지정했다.
- [x] paired stratified SRSWOR·FPC·delete-one jackknife와 bootstrap 2,000회의 역할을 구분했다.
- [x] 가중 Macro-F1의 plug-in 성격과 Holm p값/개별 CI의 해석 한계를 명시했다.
- [x] one-shot 확증 수치와 `KEEP_CURRENT_MODEL` 판정을 정본 보고서에 맞춰 반영했다.
- [x] 시장반응을 의미 중요도·인과효과·수익 신호와 분리했다.
- [x] 과제가 다른 FNSPID·KRX Bench·FINKRX와 성능 수치를 직접 비교하지 않았다.
- [x] 모델 단독 결과와 코드북 안전 floor 결과를 분리했다.
- [x] 학습·개발 Gold packet의 receipt-bound 재검수와 미해결 제외를 완료했다.
- [x] 원격 Git lock attestation 뒤 예약한 NEWS·DISCLOSURE 확증 packet을 판정하고 one-shot 평가 receipt를 생성했다.
- [ ] 금융전문가 2인 이상 독립 재주석과 합의도 측정이 필요하다.

## 데이터 및 윤리

- [x] 원천, 수집 편향, 전문 커버리지, 삭제·버전 정책을 datasheet에 기록했다.
- [x] 시세는 DB가 아닌 `prices_daily.parquet`로 동결했다.
- [x] weak label과 Gold를 schema에서 구분했다.
- [x] Gold URL을 학습 후보에서 제외했다.
- [x] API key·credential·사용자 개인정보를 데이터와 원고에서 제외했다.
- [x] 투자 조언·자동 주문·인과 추론 용도가 아님을 명시했다.
- [x] 과거 로그의 뉴스 보조 600건·재심 38건·미해결 2건 기록과 reviewer receipt 부재를 함께 공개했다.
- [x] receipt가 없는 기존 AI 라벨을 `LEGACY_UNVERIFIED`로 fail-close했다.
- [x] 후보·teacher·시장 반응 비노출 새 context에서 5개 packet 전체를 재검수하고 reviewer별 receipt를 완성했다.
- [x] 생성형 AI의 코드·주석·원고 작성 참여와 모델 계열 상관오류 한계를 공개했다.

## 익명화 및 재현성

- [x] 심사 PDF에서 저자·소속·공개 저장소 URL을 제거했다.
- [x] 저자 공개 영문본과 한글본에 최성현(Sunghyun Choi)과 한국공학대학교 컴퓨터공학부 소프트웨어학과 소속을 표기했다.
- [x] 익명본과 저자 공개 영문본이 같은 본문 원천을 사용하도록 구성했다.
- [x] 저자 이메일·ORCID를 임의 생성하지 않고 미입력 메타데이터로 기록했다.
- [x] 제품명 외에 저자를 역추적할 조직 식별자를 넣지 않았다.
- [x] Python·lockfile·base revision·data/model seed·all-12 LoRA r16·optimizer·scheduler를 기록했다.
- [x] Apple MPS와 다른 accelerator 사이의 bitwise 비결정 가능성을 명시하고 실제 device·global step·runtime 기록을 요구했다.
- [x] Parquet byte size와 SHA-256 manifest를 제공한다.
- [x] baseline과 각 Transformer seed의 prediction 파일을 제공한다.
- [x] 원고의 핵심 수치를 동결 JSON과 대조했다.
- [x] 공식 ACL style을 고정 upstream commit에서 사용한다.
- [ ] 변경 원고의 익명 심사용·저자 공개 영문·한글 PDF를 다시 렌더링해 검수해야 한다.
- [ ] 실제 제출 직전 익명 supplementary archive의 메타데이터·파일명을 다시 검사한다.

## PDF QA

- [x] `LOCKED_RESULT_PENDING`을 실제 one-shot 결과로 대체했다.
- [ ] 영문 초록 200단어 제한을 빌드에서 다시 확인한다.
- [ ] A4 2단, 11pt 공식 ACL review style과 줄 번호를 확인한다.
- [ ] 모든 폰트 내장 여부를 확인한다.
- [ ] 표·수식·참고문헌의 잘림·겹침을 세 PDF 전체 페이지에서 시각 검수한다.
