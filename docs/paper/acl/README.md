# K-FNSPID 논문 패키지

이 디렉터리는 `K-FNSPID`의 ACL Rolling Review 영문 원고와 한국정보과학회 논문지 형식을 따른 한글 원고를 함께 관리한다. 공개 시스템명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`로 고정한다.

저자는 최성현(Sunghyun Choi)이며, 소속은 한국공학대학교 컴퓨터공학부 소프트웨어학과다. 영문 소속은 `Department of Software, School of Computer Engineering, Tech University of Korea`로 표기한다.

## 구성

- `k-fnspid-v4-arr-review.tex`: 익명 심사용 영문 원고
- `k-fnspid-v4-author-preprint.tex`: 같은 영문 본문을 사용하는 저자 공개본 진입점
- `k-fnspid-v4-ko.tex`: 한국정보과학회 계열 판형과 2단 편집을 적용한 한글 원고
- `author-metadata.json`: 국문·영문 저자와 소속 메타데이터
- `references.bib`: 1차 출처 중심 BibTeX
- `responsible-nlp-checklist.md`: 책임 있는 NLP·익명화·재현성 자체 점검
- `scripts/paper/verify_k_fnspid_submission.py`: 논문 수치와 동결 JSON 보고서 대조
- `scripts/paper/verify_paper_artifacts.py`: 세 PDF의 크기·쪽수·SHA-256과 제출 manifest 대조
- `scripts/paper/build_acl_submission.sh`: 세 원고의 검증·재현 빌드
- `output/pdf/k-fnspid-v4-arr-review.pdf`: 형식 검수를 마친 잠금 전 익명 심사본
- `output/pdf/k-fnspid-v4-author-preprint.pdf`: 형식 검수를 마친 잠금 전 저자 공개본
- `output/pdf/k-fnspid-v4-ko.pdf`: 전체 쪽 렌더링을 검수한 한글 PDF
- `output/docx/k-fnspid-kiise-ko.docx`: 동일 구조의 편집 가능한 한글 Word 원고

## 재현

```bash
bash scripts/paper/build_acl_submission.sh
```

영문 원고는 ACL 공식 스타일 저장소의 커밋 `d5adc823ff0f80f98c80405ca0ab66c68e684409`을 사용한다. 한글 원고는 182×257mm 판형, 첫 쪽 단일 단, 본문 2단과 번호식 절 구성을 적용한다. 감성 수치는 one-shot 정본 `reports/korean-finance-sentiment-benchmark-v4.json`과 대조하며, 층화가중 1차 지표와 비가중 기술통계를 구분한다.

## 제출본 구분

- ARR 심사에는 `k-fnspid-v4-arr-review.pdf`만 제출한다. 저자명·소속·공개 저장소 URL을 PDF와 익명 supplement에 넣지 않는다.
- 저자 정보는 OpenReview 제출 메타데이터에 입력하되, 심사 PDF의 익명성을 깨지 않는다.
- 개인 웹·사전공개·내부 검수에는 `k-fnspid-v4-author-preprint.pdf`를 사용한다.
- `k-fnspid-v4-ko.pdf`와 `k-fnspid-kiise-ko.docx`는 국내 학회 제출 준비용 저자 원고다. 대상 학회의 배포 양식이 확정되면 여백과 머리말만 해당 양식으로 치환한다.
- 채택 후 camera-ready에는 학회 요구 형식에 맞춰 저자·소속·공개 artifact URL을 복구한다.
- 제출 시스템이 필수로 요구하면 저자 이메일과 ORCID를 `author-metadata.json`에 추가한다. 현재 값은 제공되지 않아 `null`이다.

현재 한글 원고의 서식과 문장 교정은 완료했다. `논의`와 `결론`을 분리하고 연구의 한계는 `논의`에 통합했다. 감성분류의 KR-FinBERT-SC 동일 조건 3회 반복평가가 끝나면 표 2와 초록의 관련 문장만 실제 수치로 갱신한다. 독립 금융전문가 주석과 더 미래 기간의 외부 평가는 후속 연구 범위로 명시한다.
