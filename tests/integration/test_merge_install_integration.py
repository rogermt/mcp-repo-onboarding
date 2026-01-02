from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_analyze_repo_merges_python_install_instructions(temp_repo: Callable[[str], Path]) -> None:
    # Use a fixture that triggers python install instructions inference
    # pyproject.toml without makefile usually triggers pip install .
    repo_path = temp_repo("pyproject-rich")

    analysis = analyze_repo(repo_path=str(repo_path))

    assert analysis.python is not None
    assert "pip install ." in analysis.python.installInstructions

    # Check if it's merged into scripts.install
    install_cmds = [c.command for c in analysis.scripts.install]
    assert "pip install ." in install_cmds

    # Check for description (this is what the new module provides)
    cmd_info = next(c for c in analysis.scripts.install if c.command == "pip install .")
    assert cmd_info.description == "Install the project package."
    assert cmd_info.source == "python.installInstructions"
