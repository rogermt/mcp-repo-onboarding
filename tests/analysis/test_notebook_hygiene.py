from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_precommit_hygiene_detected(temp_repo: Callable[[str], Path]) -> None:
    """Test that notebook hygiene markers trigger the specific description."""
    repo = temp_repo("edge-cases")
    config_path = repo / ".pre-commit-config.yaml"
    config_path.write_text("- repo: local\n  hooks:\n    - id: nbstripout", encoding="utf-8")

    analysis = analyze_repo(str(repo))

    config = next(
        (c for c in analysis.configurationFiles if ".pre-commit-config.yaml" in c.path), None
    )
    assert config is not None
    assert (
        config.description
        == "Pre-commit config for cleaning Jupyter notebooks (e.g. stripping outputs) for cleaner diffs."
    )


def test_precommit_hygiene_not_detected(temp_repo: Callable[[str], Path]) -> None:
    """Test that absence of markers results in the generic description."""
    repo = temp_repo("edge-cases")
    config_path = repo / ".pre-commit-config.yaml"
    config_path.write_text("- repo: local\n  hooks:\n    - id: ruff", encoding="utf-8")

    analysis = analyze_repo(str(repo))

    config = next(
        (c for c in analysis.configurationFiles if ".pre-commit-config.yaml" in c.path), None
    )
    assert config is not None
    assert config.description is not None
    assert "Pre-commit hooks" in config.description
    assert "cleaning Jupyter notebooks" not in config.description


def test_precommit_hygiene_case_insensitive(temp_repo: Callable[[str], Path]) -> None:
    """Test that detection is case-insensitive."""
    repo = temp_repo("edge-cases")
    config_path = repo / ".pre-commit-config.yaml"
    config_path.write_text("NBSTRIPOUT", encoding="utf-8")

    analysis = analyze_repo(str(repo))

    config = next(
        (c for c in analysis.configurationFiles if ".pre-commit-config.yaml" in c.path), None
    )
    assert config is not None
    assert config.description is not None
    assert "cleaning Jupyter notebooks" in config.description
