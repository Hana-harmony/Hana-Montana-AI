import argparse
import os
import re
import shutil
import subprocess
import sys

ALLOWED_WORK_TYPES = (
    "feat",
    "fix",
    "hotfix",
    "refactor",
    "chore",
    "docs",
    "test",
    "security",
    "release",
)
PROTECTED_BRANCHES = {"main", "feature"}
WORK_BRANCH_PATTERN = re.compile(
    rf"^({'|'.join(ALLOWED_WORK_TYPES)})/[a-z0-9]+(?:-[a-z0-9]+)*$"
)
GIT_REF_PATTERN = re.compile(r"^[0-9A-Za-z._/\-]+$")


def main() -> None:
    args = _parse_args()
    errors: list[str] = []

    current_branch = _git(["branch", "--show-current"])
    base_ref = args.base_ref
    expected_pr_base = args.expected_pr_base
    actual_pr_base = args.pr_base or os.getenv("GITHUB_BASE_REF") or os.getenv("PR_BASE_REF")

    errors.extend(_validate_work_branch(current_branch))
    errors.extend(_validate_ref("base ref", base_ref))
    errors.extend(_validate_base_ancestry(base_ref))
    errors.extend(_validate_pr_base(actual_pr_base, expected_pr_base))

    if errors:
        print("하네스 Git 흐름 검증 실패")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("하네스 Git 흐름 검증 통과")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify repository harness Git flow.")
    parser.add_argument("--base-ref", default="origin/feature")
    parser.add_argument("--expected-pr-base", default="feature")
    parser.add_argument("--pr-base", default="")
    return parser.parse_args()


def _validate_work_branch(branch: str) -> list[str]:
    if not branch:
        return ["현재 HEAD가 브랜치에 있지 않음"]
    if branch in PROTECTED_BRANCHES:
        return [f"보호 브랜치에서 직접 작업하면 안 됨: {branch}"]
    if not WORK_BRANCH_PATTERN.fullmatch(branch):
        allowed = ", ".join(f"{work_type}/..." for work_type in ALLOWED_WORK_TYPES)
        return [f"작업 브랜치 형식 오류: {branch} (허용: {allowed})"]
    return []


def _validate_ref(label: str, ref: str) -> list[str]:
    if not GIT_REF_PATTERN.fullmatch(ref) or ref.startswith("-") or ".." in ref:
        return [f"허용되지 않은 {label}: {ref}"]
    return []


def _validate_base_ancestry(base_ref: str) -> list[str]:
    errors: list[str] = []
    if _run_git(["rev-parse", "--verify", "--quiet", base_ref]).returncode != 0:
        return [f"기준 브랜치를 찾을 수 없음: {base_ref}"]
    result = _run_git(["merge-base", "--is-ancestor", base_ref, "HEAD"])
    if result.returncode != 0:
        errors.append(f"작업 브랜치가 최신 {base_ref}를 포함하지 않음")
    return errors


def _validate_pr_base(actual_pr_base: str, expected_pr_base: str) -> list[str]:
    if not actual_pr_base:
        return []
    if actual_pr_base != expected_pr_base:
        return [f"PR base 오류: actual={actual_pr_base}, expected={expected_pr_base}"]
    return []


def _git(args: list[str]) -> str:
    result = _run_git(args, check=True)
    return result.stdout.strip()


def _run_git(args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git 실행 파일을 찾을 수 없음")
    return subprocess.run(  # noqa: S603
        [git_path, *args],
        check=check,
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    main()
