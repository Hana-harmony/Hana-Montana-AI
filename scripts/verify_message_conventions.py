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


def main() -> None:
    args = _parse_args()
    errors: list[str] = []

    if not args.skip_pr:
        errors.extend(_validate_pr_title(args.pr_title or os.getenv("PR_TITLE", "")))
        errors.extend(_validate_pr_body(args.pr_body or os.getenv("PR_BODY", "")))

    if args.base and args.head:
        subjects = _commit_subjects(args.base, args.head)
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


def _validate_pr_title(title: str) -> list[str]:
    normalized = title.strip()
    errors: list[str] = []
    if not normalized:
        return ["PR 제목이 비어 있음"]
    if not HANGUL_PATTERN.search(normalized):
        errors.append("PR 제목은 한글을 포함해야 함")
    if _looks_like_english_sentence(normalized):
        errors.append("PR 제목은 영어 문장형으로 작성하면 안 됨")
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
    return errors


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


def _commit_subjects(base: str, head: str) -> list[str]:
    _validate_git_ref(base)
    _validate_git_ref(head)
    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git 실행 파일을 찾을 수 없음")
    result = subprocess.run(  # noqa: S603
        [git_path, "log", "--format=%s", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


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
