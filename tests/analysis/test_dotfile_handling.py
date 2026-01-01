from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_dotfile_config_is_detected(temp_repo: Callable[[str], Path]) -> None:
    """
    Regression test to ensure dotfiles like .pre-commit-config.yaml are
    correctly categorized as configuration files and not missed due to
    incorrect path stripping.
    """
    repo_path = temp_repo("edge-cases")
    (repo_path / ".pre-commit-config.yaml").write_text("repos: []")

    analysis = analyze_repo(repo_path=str(repo_path))

    config_paths = {c.path for c in analysis.configurationFiles}
    assert ".pre-commit-config.yaml" in config_paths, (
        f"Expected to find .pre-commit-config.yaml in configurationFiles, "
        f"but it was missing. Found: {config_paths}"
    )
