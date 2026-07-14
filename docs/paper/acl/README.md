# K-FNSPID v3 ARR 제출 패키지

이 디렉터리는 `K-FNSPID v3`의 ACL Rolling Review 장문 익명 심사용 원고다. 공개 시스템명은 `Hana Montana AI(KF-DeBERTa + K-FNSPID)`로 고정한다.

## 구성

- `k-fnspid-v3-arr-review.tex`: 익명 심사용 영문 원고
- `references.bib`: 1차 출처 중심 BibTeX
- `responsible-nlp-checklist.md`: 책임 있는 NLP·익명화·재현성 자체 점검
- `scripts/paper/verify_k_fnspid_submission.py`: 논문 수치와 동결 JSON 보고서 대조
- `scripts/paper/build_acl_submission.sh`: 공식 ACL 스타일 고정 커밋으로 PDF 생성
- `output/pdf/k-fnspid-v3-arr-review.pdf`: 렌더링·검수된 제출 PDF

## 재현

```bash
bash scripts/paper/build_acl_submission.sh
```

빌드는 ACL 공식 스타일 저장소의 커밋 `d5adc823ff0f80f98c80405ca0ab66c68e684409`을 사용한다. 원고 수치는 먼저 동결 manifest와 연구 평가 JSON에 대조하며 불일치 시 PDF를 만들지 않는다.

## 제출 전 교체 항목

현재 파일은 익명 심사용이다. 실제 ARR 제출 시에는 OpenReview가 발급한 submission ID와 익명 supplementary archive만 연결한다. 공개 GitHub Release URL, 조직명, 저자명은 심사 PDF에 넣지 않는다. 채택 후 카메라레디에서만 저자·소속·공개 artifact URL을 복구한다.

현재 상태는 형식·실험·재현성 기준의 학회 제출본이다. 독립 금융전문가 다중 주석이 없으므로 외부 Gold 타당성이나 공시 가격반응 SOTA를 주장하지 않는다.
