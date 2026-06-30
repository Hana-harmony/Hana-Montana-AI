import argparse
import os
import re
import shutil
import subprocess
import sys

ALLOWED_COMMIT_TYPES = {
    "feat",
    "fix",
    "refactor",
    "test",
    "docs",
    "chore",
    "security",
    "perf",
    "build",
    "ci",
    "revert",
}
HANGUL_PATTERN = re.compile(r"[가-힣]")
GIT_REF_PATTERN = re.compile(r"^[0-9A-Za-z._/\-]+$")
COMMIT_SUBJECT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?:\([a-z0-9-]+\))?: (?P<title>.+)$"
)
PR_TEMPLATE_REQUIRED_FIELDS = (
    "- 배경:",
    "- 변경 사항:",
    "- 검증 결과:",
    "- 영향 범위:",
    "- 롤백 방법:",
    "- 체크리스트:",
)
PR_CHECKLIST_REQUIRED_ITEMS = (
    "CI 통과",
    "보안/민감정보 점검",
    "문서 업데이트",
)
LEGACY_COMMIT_VALIDATION_CUTOFFS = (
    "ci(git): PR 메시지 컨벤션 검사 추가",
)


def main() -> None:
    args = _parse_args()
    errors: list[str] = []
    subjects = _commit_subjects(args.base, args.head) if args.base and args.head else []

    if not args.skip_pr:
        errors.extend(_validate_pr_title(args.pr_title or os.getenv("PR_TITLE", ""), subjects))
        errors.extend(_validate_pr_body(args.pr_body or os.getenv("PR_BODY", "")))

    if subjects:
        errors.extend(_validate_commit_subject(subject) for subject in subjects)

    errors = [error for error in errors if error]
    if errors:
        print("메시지 컨벤션 검증 실패")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("메시지 컨벤션 검증 통과")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Korean PR and commit conventions.")
    parser.add_argument("--pr-title", default="")
    parser.add_argument("--pr-body", default="")
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    parser.add_argument("--skip-pr", action="store_true")
    return parser.parse_args()


def _validate_pr_title(title: str, commit_subjects: list[str] | None = None) -> list[str]:
    normalized = title.strip()
    errors: list[str] = []
    if not normalized:
        return ["PR 제목이 비어 있음"]
    subject_error = _validate_commit_subject(normalized)
    if subject_error:
        errors.append(f"PR 제목 형식 오류: {subject_error}")
    if _looks_like_english_sentence(normalized):
        errors.append("PR 제목은 영어 문장형으로 작성하면 안 됨")
    expected_title = _expected_pr_title_from_commits(commit_subjects or [])
    if expected_title and normalized != expected_title:
        errors.append(
            f"PR 제목은 대표 커밋 제목과 일치해야 함: expected={expected_title}"
        )
    return errors


def _validate_pr_body(body: str) -> list[str]:
    normalized = body.strip()
    errors: list[str] = []
    if not normalized:
        return ["PR 본문이 비어 있음"]
    if not HANGUL_PATTERN.search(normalized):
        errors.append("PR 본문은 한글을 포함해야 함")
    for field in PR_TEMPLATE_REQUIRED_FIELDS:
        if field not in normalized:
            errors.append(f"PR 본문 템플릿 항목 누락: {field}")
        elif field != "- 체크리스트:" and not _field_has_content(normalized, field):
            errors.append(f"PR 본문 템플릿 항목 내용 누락: {field}")
    for item in PR_CHECKLIST_REQUIRED_ITEMS:
        if not re.search(rf"- \[[ xX]\] {re.escape(item)}", normalized):
            errors.append(f"PR 체크리스트 항목 누락: {item}")
    return errors


def _field_has_content(body: str, field: str) -> bool:
    start = body.find(field)
    if start < 0:
        return False
    content_start = start + len(field)
    following_starts = [
        position
        for other_field in PR_TEMPLATE_REQUIRED_FIELDS
        if other_field != field
        if (position := body.find(other_field, content_start)) >= 0
    ]
    content_end = min(following_starts) if following_starts else len(body)
    return bool(body[content_start:content_end].strip())


def _validate_commit_subject(subject: str) -> str:
    match = COMMIT_SUBJECT_PATTERN.fullmatch(subject.strip())
    if not match:
        return f"커밋 제목 형식 오류: {subject}"
    commit_type = match.group("type")
    title = match.group("title")
    if commit_type not in ALLOWED_COMMIT_TYPES:
        return f"허용되지 않은 커밋 type: {commit_type}"
    if not HANGUL_PATTERN.search(title):
        return f"커밋 제목은 한글을 포함해야 함: {subject}"
    return ""


def _expected_pr_title_from_commits(subjects: list[str]) -> str:
    if len(subjects) != 1:
        return ""
    return subjects[0].strip()


def _commit_subjects(base: str, head: str) -> list[str]:
    _validate_git_ref(base)
    _validate_git_ref(head)
    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git 실행 파일을 찾을 수 없음")
    result = subprocess.run(  # noqa: S603
        [
            git_path,
            "log",
            "--first-parent",
            "--reverse",
            "--no-merges",
            "--format=%s",
            f"{base}..{head}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subjects = [line for line in result.stdout.splitlines() if line.strip()]
    return _subjects_after_legacy_cutoff(subjects)


def _subjects_after_legacy_cutoff(subjects: list[str]) -> list[str]:
    for index, subject in enumerate(subjects):
        if any(subject.startswith(cutoff) for cutoff in LEGACY_COMMIT_VALIDATION_CUTOFFS):
            return subjects[index:]
    return subjects


def _looks_like_english_sentence(text: str) -> bool:
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return False
    ascii_letters = [character for character in letters if character.isascii()]
    return len(ascii_letters) / len(letters) > 0.8


def _validate_git_ref(ref: str) -> None:
    if not GIT_REF_PATTERN.fullmatch(ref) or ref.startswith("-") or ".." in ref:
        raise ValueError(f"허용되지 않은 git ref: {ref}")


if __name__ == "__main__":
    main()
