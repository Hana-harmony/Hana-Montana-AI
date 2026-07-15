# Responsible NLP 및 제출 자체 점검

기준: ACL Rolling Review 장문 익명 심사 형식과 Responsible NLP Research checklist.

## 과학적 주장

- [x] 동일 Test ID의 기준선과 후보만 통계 비교했다.
- [x] Test는 모델·threshold·prior 선택에 사용하지 않았다.
- [x] 세 seed 평균과 표본표준편차를 보고했다.
- [x] 거래일 cluster bootstrap과 exact McNemar를 함께 보고했다.
- [x] v3 공유 모델의 공시 회귀와 v4 출처별 전문가의 제거 결과를 모두 공개했다.
- [x] 시장반응을 의미 중요도·인과효과·수익 신호와 분리했다.
- [x] 과제가 다른 FNSPID·KRX Bench·FINKRX와 성능 수치를 직접 비교하지 않았다.
- [x] 모델 단독 결과와 코드북 안전 floor 결과를 분리했다.
- [ ] 금융전문가 2인 이상 독립 재주석과 합의도 측정이 필요하다.

## 데이터 및 윤리

- [x] 원천, 수집 편향, 전문 커버리지, 삭제·버전 정책을 datasheet에 기록했다.
- [x] 시세는 DB가 아닌 `prices_daily.parquet`로 동결했다.
- [x] weak label과 Gold를 schema에서 구분했다.
- [x] Gold URL을 학습 후보에서 제외했다.
- [x] API key·credential·사용자 개인정보를 데이터와 원고에서 제외했다.
- [x] 투자 조언·자동 주문·인과 추론 용도가 아님을 명시했다.
- [x] 생성형 AI의 코드·주석·원고 작성 참여와 단일 판정 한계를 공개했다.

## 익명화 및 재현성

- [x] 심사 PDF에서 저자·소속·공개 저장소 URL을 제거했다.
- [x] 저자 공개 영문본과 한글본에 최성현의 공식 국문·영문 소속과 학부생 신분을 표기했다.
- [x] 익명본과 저자 공개 영문본이 같은 본문 원천을 사용하도록 구성했다.
- [x] 저자 이메일·ORCID를 임의 생성하지 않고 미입력 메타데이터로 기록했다.
- [x] 제품명 외에 저자를 역추적할 조직 식별자를 넣지 않았다.
- [x] Python·lockfile·base revision·seed·LoRA·optimizer·scheduler를 기록했다.
- [x] Parquet byte size와 SHA-256 manifest를 제공한다.
- [x] baseline과 각 Transformer seed의 prediction 파일을 제공한다.
- [x] 원고의 핵심 수치를 동결 JSON과 자동 대조한다.
- [x] 공식 ACL style을 고정 upstream commit에서 사용한다.
- [x] 익명 심사용·저자 공개 영문·한글 PDF 총 18쪽을 모두 렌더링해 검수한다.
- [ ] 실제 제출 직전 익명 supplementary archive의 메타데이터·파일명을 다시 검사한다.

## PDF QA

- [x] 본문은 장문 기준 8쪽 이내이며 Limitations/Ethics가 뒤따른다(본문 5쪽, 전체 7쪽).
- [x] 초록은 200단어 이하다(177단어).
- [x] A4 2단, 11pt 공식 ACL review style과 줄 번호를 사용한다.
- [x] 13개 폰트가 모두 내장되어 있다.
- [x] 표·수식·참고문헌에 잘림이나 겹침이 없다.
- [x] 세 PDF 총 18개 페이지를 140 DPI PNG로 렌더링해 시각 검수했다.
