# K-FNSPID v3 논문 패키지

이 디렉터리는 `K-FNSPID v3`의 ACL Rolling Review 장문 익명 심사용 원고, 저자 공개 영문본과 한글 참고본을 함께 관리한다. 공개 시스템명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`로 고정한다.

저자는 최성현(Sunghyun Choi), 한국공학대학교 SW대학 컴퓨터공학부 소프트웨어전공 4학년 학부생이다. 학교 공식 영문 표기는 `College of SW, Computer Engineering (Major in Software), Tech University of Korea`를 사용한다.

## 구성

- `k-fnspid-v3-arr-review.tex`: 익명 심사용 영문 원고
- `k-fnspid-v3-author-preprint.tex`: 같은 영문 본문을 사용하는 저자 공개본 진입점
- `k-fnspid-v3-ko.tex`: 같은 실험·한계·윤리 내용을 반영한 한글 논문
- `author-metadata.json`: 국문·영문 저자와 소속 메타데이터
- `references.bib`: 1차 출처 중심 BibTeX
- `responsible-nlp-checklist.md`: 책임 있는 NLP·익명화·재현성 자체 점검
- `scripts/paper/verify_k_fnspid_submission.py`: 논문 수치와 동결 JSON 보고서 대조
- `scripts/paper/verify_paper_artifacts.py`: 세 PDF의 크기·쪽수·SHA-256과 제출 manifest 대조
- `scripts/paper/build_acl_submission.sh`: 세 원고의 검증·재현 빌드
- `output/pdf/k-fnspid-v3-arr-review.pdf`: 렌더링·검수된 제출 PDF
- `output/pdf/k-fnspid-v3-author-preprint.pdf`: 저자 공개 영문 PDF
- `output/pdf/k-fnspid-v3-ko.pdf`: 한글 PDF

## 재현

```bash
bash scripts/paper/build_acl_submission.sh
```

빌드는 ACL 공식 스타일 저장소의 커밋 `d5adc823ff0f80f98c80405ca0ab66c68e684409`을 사용한다. 원고 수치는 먼저 동결 manifest와 연구 평가 JSON에 대조하며 불일치 시 PDF를 만들지 않는다. 익명본과 저자 공개본은 같은 영문 본문을 입력해 수치 drift를 막는다.

## 제출본 구분

- ARR 심사에는 `k-fnspid-v3-arr-review.pdf`만 제출한다. 저자명·소속·공개 저장소 URL을 PDF와 익명 supplement에 넣지 않는다.
- 저자 정보는 OpenReview 제출 메타데이터에 입력하되, 심사 PDF의 익명성을 깨지 않는다.
- 개인 웹·사전공개·내부 검수에는 `k-fnspid-v3-author-preprint.pdf`를 사용한다.
- `k-fnspid-v3-ko.pdf`는 국내 검토와 내용 확인을 위한 저자 공개 참고본이며 ACL 심사 언어를 대체하지 않는다.
- 채택 후 camera-ready에는 학회 요구 형식에 맞춰 저자·소속·공개 artifact URL을 복구한다.
- 제출 시스템이 필수로 요구하면 저자 이메일과 ORCID를 `author-metadata.json`에 추가한다. 현재 값은 제공되지 않아 `null`이다.

현재 상태는 형식·실험·재현성 기준의 학회 제출 패키지다. 독립 금융전문가 다중 주석이 없으므로 외부 Gold 타당성이나 공시 가격반응 SOTA를 주장하지 않는다.
