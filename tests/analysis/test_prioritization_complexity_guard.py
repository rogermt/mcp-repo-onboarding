from pathlib import Path


def test_prioritization_not_if_elif_ladder() -> None:
    src = Path("src/mcp_repo_onboarding/analysis/prioritization.py").read_text(encoding="utf-8")
    assert src.count("\nelif ") <= 6
