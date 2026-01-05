from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import build_context, compile_blueprint


def test_no_venv_snippet_when_python_not_detected() -> None:
    analyze: dict[str, Any] = {
        "repoPath": "/test/repo",
        "python": None,
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
    commands: dict[str, Any] = {"devCommands": [], "testCommands": [], "buildCommands": []}

    md = compile_blueprint(build_context(analyze, commands))["render"]["markdown"]

    assert "python3 -m venv .venv" not in md
    assert "python -m venv .venv" not in md
    assert "(Generic suggestion)" not in md
