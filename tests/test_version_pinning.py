from pathlib import Path

import pytest

from mcp_repo_onboarding.analysis.core import analyze_repo


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def test_python_pin_range_rejection(fixtures_dir: Path) -> None:
    """Verify that version ranges like >=3.10 are rejected and hints are empty."""
    repo_path = fixtures_dir / "python-pin-range"
    analysis = analyze_repo(str(repo_path))
    # The current implementation might return ["3.10"] or [">=3.10"] depending on parsing
    # We want it to be empty if only ranges are available.
    assert analysis.python is not None
    assert not analysis.python.pythonVersionHints


def test_workflow_python_pin_env_success(fixtures_dir: Path) -> None:
    """Verify that exact pins in workflows are still detected."""
    repo_path = fixtures_dir / "workflow-python-pin-env"
    analysis = analyze_repo(str(repo_path))
    assert analysis.python is not None
    assert analysis.python.pythonVersionHints == ["3.14"]


@pytest.mark.parametrize(
    "version,expected",
    [
        ("3.14", True),
        ("3.14.0", True),
        ("31.1", True),
        (">=3.10", False),
        ("^3.11", False),
        ("~=3.12", False),
        ("!=3.10.*", False),
        ("3.x", False),
        ("3.*", False),
        ("3", False),
        ("python-3.14", False),
        ("", False),
    ],
)
def test_is_exact_version_logic(version: str, expected: bool) -> None:
    """This will test the helper function once implemented or just the logic."""
    from mcp_repo_onboarding.analysis.core import _is_exact_version

    assert _is_exact_version(version) == expected
