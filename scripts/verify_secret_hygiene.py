import re
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TRACKED_FILES = {
    ".env",
    "secrets.local.env",
}
FORBIDDEN_TRACKED_SUFFIXES = (
    ".pem",
    ".key",
    ".p12",
    ".pfx",
)
FORBIDDEN_ASSIGNMENT_PATTERNS = (
    re.compile(r"\bNAVER_NEWS_CLIENT_ID\s*=\s*\S+"),
    re.compile(r"\bNAVER_NEWS_CLIENT_SECRET\s*=\s*\S+"),
    re.compile(r"\bOPEN_DART_API_KEY\s*=\s*\S+"),
    re.compile(r"\bKRX_API_KEY\s*=\s*\S+"),
    re.compile(r"\bOMNILENS_API_KEY\s*=\s*\S+"),
    re.compile(r"\bX-HANNAH-AI-SERVICE-TOKEN\s*=\s*\S+"),
)
TEXT_FILE_SUFFIXES = {
    ".env",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}


def main() -> None:
    tracked_files = git_tracked_files()
    violations = [
        *tracked_secret_file_violations(tracked_files),
        *tracked_secret_assignment_violations(tracked_files),
    ]
    if violations:
        raise SystemExit("\n".join(violations))
    print("Secret hygiene check passed.")


def git_tracked_files() -> list[Path]:
    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git executable is required")
    # git 경로는 shutil.which로 확인하고 인자는 고정한다.
    output = subprocess.run(  # noqa: S603
        [git_path, "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [PROJECT_ROOT / line for line in output.splitlines() if line]


def tracked_secret_file_violations(paths: list[Path]) -> list[str]:
    violations = []
    for path in paths:
        relative_path = path.relative_to(PROJECT_ROOT).as_posix()
        if relative_path in FORBIDDEN_TRACKED_FILES:
            violations.append(f"Forbidden secret file is tracked: {relative_path}")
        if path.suffix in FORBIDDEN_TRACKED_SUFFIXES:
            violations.append(f"Forbidden key material file is tracked: {relative_path}")
    return violations


def tracked_secret_assignment_violations(paths: list[Path]) -> list[str]:
    violations = []
    for path in paths:
        if path.suffix not in TEXT_FILE_SUFFIXES or not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_ASSIGNMENT_PATTERNS:
            if pattern.search(content):
                relative_path = path.relative_to(PROJECT_ROOT).as_posix()
                violations.append(f"Forbidden credential assignment found: {relative_path}")
    return violations


if __name__ == "__main__":
    main()
