from collections.abc import Callable
from pathlib import Path

import pytest

from mcp_repo_onboarding.analysis.utils import classify_python_version


@pytest.mark.parametrize(
    "hint, expected_pin, expected_comment",
    [
        ("==3.11.0", "3.11.0", None),
        (">=3.11", None, "Requires Python >=3.11"),
        ("~=3.10.0", None, "Compatible with 3.10.x"),
        (">=3.9, !=3.9.7, <4", None, "Requires Python >=3.9, !=3.9.7, <4"),
        ("3.10", "3.10", None),
        ("*", None, "Any Python version"),
        ("", None, "Any Python version"),
        (None, None, "Any Python version"),
        # Malformed but starting with digit
        ("3.x", "3.x", None),
    ],
)
def test_classify_python_version(
    hint: str | None, expected_pin: str | None, expected_comment: str | None
) -> None:
    pin, comment = classify_python_version(hint)  # type: ignore[arg-type]
    assert pin == expected_pin
    assert comment == expected_comment


def test_integration_version_classification(temp_repo: Callable[[str], Path]) -> None:
    """Verify that analyze_repo correctly populates pin and comment fields."""
    repo_path = temp_repo("version-ranges")
    from mcp_repo_onboarding.analysis import analyze_repo

    analysis = analyze_repo(str(repo_path))

    assert analysis.python is not None
    assert analysis.python.pythonVersionPin is None
    assert analysis.python.pythonVersionComments == "Requires Python >=3.11"
