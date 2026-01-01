from __future__ import annotations

from pathlib import Path


def test_prioritization_not_if_elif_ladder() -> None:
    p = Path("src/mcp_repo_onboarding/analysis/prioritization.py")
    src = p.read_text(encoding="utf-8")

    # Very effective anti-regression check for huge ladders
    elif_count = src.count("\nelif ")
    assert elif_count <= 6, f"prioritization.py has too many elif branches ({elif_count})"
