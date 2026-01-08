"""
Tests for environment setup when primaryTooling is Unknown.

Issue #166: Make environment setup version-pin line neutral when primaryTooling is Unknown.
When neither Python nor Node.js tooling is detected (e.g., purego), the environment setup
should display a neutral message instead of Python-specific messaging.
"""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import (
    build_context,
    compile_blueprint,
)


def _base_commands() -> dict[str, Any]:
    return {"devCommands": [], "testCommands": [], "buildCommands": []}


def test_unknown_primary_neutral_environment_message() -> None:
    """
    When primaryTooling is Unknown and no Python evidence exists,
    the environment setup should show neutral messaging (not Python-specific),
    and venv snippet should NOT appear.
    """
    analyze: dict[str, Any] = {
        "repoPath": "/test/repo",
        "primaryTooling": "Unknown",
        "python": None,  # no Python evidence
        "scripts": {
            "dev": [],
            "start": [],
            "test": [],
            "lint": [],
            "format": [],
            "install": [],
            "other": [],
        },
        "notes": [],
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
        "testSetup": {"commands": []},
    }

    md = compile_blueprint(build_context(analyze, _base_commands()))["render"]["markdown"]

    # Unknown-primary repos should show neutral message (not Python-specific):
    assert "No Python/Node.js version pin detected." in md
    assert "No Python version pin detected." not in md
    assert "No Node.js version pin file detected." not in md

    # Must NOT show venv snippet or label:
    assert "(Generic suggestion)" not in md
    assert "python3 -m venv .venv" not in md
    assert "python -m venv .venv" not in md
    assert "source .venv/bin/activate" not in md


def test_unknown_primary_missing_primary_tooling_field() -> None:
    """
    When primaryTooling field is missing (None) and no Python evidence exists,
    the environment setup should show the same neutral messaging as Unknown.
    """
    analyze: dict[str, Any] = {
        "repoPath": "/test/repo",
        "primaryTooling": None,  # missing or None
        "python": None,  # no Python evidence
        "scripts": {
            "dev": [],
            "start": [],
            "test": [],
            "lint": [],
            "format": [],
            "install": [],
            "other": [],
        },
        "notes": [],
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
        "testSetup": {"commands": []},
    }

    md = compile_blueprint(build_context(analyze, _base_commands()))["render"]["markdown"]

    # Missing primaryTooling with no Python evidence should also show neutral message:
    assert "No Python/Node.js version pin detected." in md
    assert "No Python version pin detected." not in md
    assert "No Node.js version pin file detected." not in md

    # Must NOT show venv snippet or label:
    assert "(Generic suggestion)" not in md
    assert "python3 -m venv .venv" not in md


def test_python_primary_unchanged_still_shows_python_message() -> None:
    """
    Sanity check: Python-primary repos (with Python evidence) should still show
    Python-specific environment messaging, not the neutral message.
    """
    analyze: dict[str, Any] = {
        "repoPath": "/test/repo",
        "primaryTooling": "Python",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
            "installInstructions": [],
            "dependencyFiles": [{"path": "requirements.txt", "type": "requirements.txt"}],
            "packageManagers": ["pip"],
        },
        "scripts": {
            "dev": [],
            "start": [],
            "test": [],
            "lint": [],
            "format": [],
            "install": [],
            "other": [],
        },
        "notes": [],
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
        "testSetup": {"commands": []},
    }

    md = compile_blueprint(build_context(analyze, _base_commands()))["render"]["markdown"]

    # Python-primary repos should keep Python-specific message:
    assert "No Python version pin detected." in md
    assert "No Python/Node.js version pin detected." not in md
    assert "(Generic suggestion)" in md
    assert "python3 -m venv .venv" in md
