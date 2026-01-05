"""
Tests for environment setup when primaryTooling is Node.js with no Python evidence.

Issue #126: Suppress venv snippet when Python is not detected (e.g., Node.js-primary repos).
Ensure Python repos still emit generic venv suggestion when no pin/env is detected.
"""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import (
    build_context,
    compile_blueprint,
)


def _base_commands() -> dict[str, Any]:
    return {"devCommands": [], "testCommands": [], "buildCommands": []}


def test_node_primary_no_python_evidence_suppresses_venv_snippet() -> None:
    """
    When primaryTooling is Node.js and python=None (no Python evidence),
    the venv snippet should NOT appear in the markdown output.
    """
    analyze: dict[str, Any] = {
        "repoPath": "/test/repo",
        "primaryTooling": "Node.js",
        "python": None,  # key condition: no python evidence
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

    # When python is not detected, venv snippet and label must NOT appear:
    assert "(Generic suggestion)" not in md
    assert "python3 -m venv .venv" not in md
    assert "python -m venv .venv" not in md
    assert "source .venv/bin/activate" not in md


def test_python_repo_unchanged_generic_venv_still_emitted_when_no_pin_no_env() -> None:
    """
    When primaryTooling is Python and python object exists but has no version pin
    or envSetupInstructions, the generic venv suggestion should still appear.
    This ensures backward compatibility for Python-primary repos.
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

    # Existing Python behavior stays intact:
    assert "No Python version pin detected." in md
    assert "(Generic suggestion)" in md
    assert "python3 -m venv .venv" in md
    assert "source .venv/bin/activate" in md
