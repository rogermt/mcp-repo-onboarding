from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_pyproject_metadata_extraction(temp_repo: Callable[[str], Path]) -> None:
    """Verify that pyproject.toml metadata is extracted correctly (Issue #10)."""
    repo_path = temp_repo("pyproject-rich")

    analysis = analyze_repo(str(repo_path))

    assert analysis.python is not None
    # Verify Python version hint from requires-python
    assert ">=3.11" in analysis.python.pythonVersionHints

    # Verify package manager detection (Hatch)
    assert "hatch" in analysis.python.packageManagers


def test_pyproject_malformed_toml(temp_repo: Callable[[str], Path]) -> None:
    """Verify that malformed pyproject.toml doesn't crash the analysis."""
    repo_path = temp_repo("pyproject-rich")
    (repo_path / "pyproject.toml").write_text("[project\nname = 'broken'")

    # Should not raise exception
    analysis = analyze_repo(str(repo_path))
    assert analysis is not None
    # Should still find Python files if they exist (none in this fixture yet)
    # but packageManagers and version hints might be empty or partial
