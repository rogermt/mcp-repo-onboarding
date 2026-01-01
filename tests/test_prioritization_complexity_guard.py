from pathlib import Path


def test_prioritization_not_if_elif_ladder() -> None:
    """
    Enforce that prioritization.py does not regress into deep if/elif ladders.

    This test is deterministic and file-specific, catching "ladder regressions"
    that global Ruff thresholds might miss. The threshold of 6 elif blocks is
    a reasonable ceiling for the registry-driven refactoring in Issue #77.

    If this test fails, prioritization.py likely needs refactoring to use
    registries (dicts + rules) instead of chained if/elif logic.
    """
    src = Path("src/mcp_repo_onboarding/analysis/prioritization.py").read_text(encoding="utf-8")
    elif_count = src.count("\nelif ")
    assert elif_count <= 6, (
        f"prioritization.py has {elif_count} elif blocks (threshold: 6). Refactor to registry pattern."
    )
