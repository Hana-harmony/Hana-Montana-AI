import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/verify_message_conventions.py"
SPEC = importlib.util.spec_from_file_location("verify_message_conventions", SCRIPT_PATH)
assert SPEC is not None
verify_message_conventions = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verify_message_conventions)

_validate_commit_subject = verify_message_conventions._validate_commit_subject
_validate_pr_body = verify_message_conventions._validate_pr_body
_validate_pr_title = verify_message_conventions._validate_pr_title


def test_pr_title_requires_korean_text() -> None:
    assert _validate_pr_title("Add live news evaluation and feature contracts")
    assert _validate_pr_title("기능정의서 모델 계약 추가") == []


def test_pr_body_requires_korean_template_fields() -> None:
    body = """
- 배경: 기능정의서 계약을 CI에서 검증해야 함
- 변경 사항: 메시지 컨벤션 검사 추가
- 검증 결과: 테스트 통과
- 영향 범위: PR 검증
- 롤백 방법: 검사 단계 제거
- 체크리스트:
  - [x] CI 통과
  - [x] 보안/민감정보 점검
  - [x] 문서 업데이트
"""

    assert _validate_pr_body("## Summary\n- add checks")
    assert _validate_pr_body(body) == []


def test_pr_body_rejects_empty_template_placeholders() -> None:
    empty_template = """
- 배경:
- 변경 사항:
- 검증 결과:
- 영향 범위:
- 롤백 방법:
- 체크리스트:
  - [ ] CI 통과
  - [ ] 보안/민감정보 점검
  - [ ] 문서 업데이트
"""

    errors = _validate_pr_body(empty_template)

    assert "PR 본문 템플릿 항목 내용 누락: - 배경:" in errors
    assert "PR 본문 템플릿 항목 내용 누락: - 변경 사항:" in errors


def test_commit_subject_requires_conventional_commit_and_korean_title() -> None:
    assert _validate_commit_subject("Add live news evaluation batch")
    assert _validate_commit_subject("feat(model): Add live news evaluation batch")
    assert _validate_commit_subject("feat(model): 기능정의서 모델 계약 추가") == ""
