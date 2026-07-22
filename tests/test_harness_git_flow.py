from scripts.verify_harness_git_flow import _validate_flow, _validate_ref


def test_work_branch_must_target_feature() -> None:
    assert _validate_flow("feat/improve-model", "feature") == []
    assert _validate_flow("feat/improve-model", "main")
    assert _validate_flow("feature", "feature")


def test_release_pr_must_be_feature_to_main() -> None:
    assert _validate_flow("feature", "main") == []
    assert _validate_flow("fix/not-feature", "main")


def test_unknown_base_and_unsafe_ref_are_rejected() -> None:
    assert _validate_flow("feat/improve-model", "develop")
    assert _validate_ref("head ref", "feat/improve-model") == []
    assert _validate_ref("head ref", "../feature")
