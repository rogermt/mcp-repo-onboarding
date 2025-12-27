"""Test type hints for analysis module functions.

This test file verifies that all public functions have proper type hints
as part of our code quality standards.
"""

from typing import get_type_hints

from mcp_repo_onboarding.analysis import (
    extract_makefile_commands,
    extract_shell_scripts,
    extract_tox_commands,
)


def test_extract_shell_scripts_has_proper_type_hints() -> None:
    """Verify extract_shell_scripts has proper return type hint.

    The function should return Dict[str, List[CommandInfo]], not just 'dict'.
    """
    hints = get_type_hints(extract_shell_scripts)
    assert "return" in hints, "extract_shell_scripts missing return type hint"

    # Check that it's a Dict type (not just 'dict')
    return_type = hints["return"]
    assert hasattr(
        return_type, "__origin__"
    ), "Return type should be a generic Dict, not plain dict"
    assert return_type.__origin__ == dict, "Return type should be Dict"


def test_extract_tox_commands_has_proper_type_hints() -> None:
    """Verify extract_tox_commands has proper return type hint.

    The function should return Dict[str, List[CommandInfo]], not just 'dict'.
    """
    hints = get_type_hints(extract_tox_commands)
    assert "return" in hints, "extract_tox_commands missing return type hint"

    # Check that it's a Dict type (not just 'dict')
    return_type = hints["return"]
    assert hasattr(
        return_type, "__origin__"
    ), "Return type should be a generic Dict, not plain dict"
    assert return_type.__origin__ == dict, "Return type should be Dict"


def test_extract_makefile_commands_has_proper_type_hints() -> None:
    """Verify extract_makefile_commands has proper return type hint.

    This should already be correct, but we test it for completeness.
    """
    hints = get_type_hints(extract_makefile_commands)
    assert "return" in hints, "extract_makefile_commands missing return type hint"

    # Check that it's a Dict type
    return_type = hints["return"]
    assert hasattr(
        return_type, "__origin__"
    ), "Return type should be a generic Dict, not plain dict"
    assert return_type.__origin__ == dict, "Return type should be Dict"
