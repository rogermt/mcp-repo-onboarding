from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import build_context, compile_blueprint


def _base_analyze() -> dict[str, Any]:
    return {
        "repoPath": "/test/repo",
        "python": None,  # important for "Python not detected"
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
        # Optional: show that other tooling can exist, but we still do not suggest commands
        "otherTooling": [
            {"name": "Node.js", "evidenceFiles": ["package.json", "yarn.lock"]},
        ],
    }


def _base_commands() -> dict[str, Any]:
    return {"devCommands": [], "testCommands": [], "buildCommands": []}


def test_python_only_scope_message_shown_when_python_not_detected() -> None:
    analyze = _base_analyze()
    commands = _base_commands()

    md = compile_blueprint(build_context(analyze, commands))["render"]["markdown"]

    assert "## Analyzer notes" in md
    assert (
        "* Python tooling not detected; this release generates Python-focused onboarding only."
        in md
    )

    low = md.lower()
    assert "npm " not in low
    assert "yarn " not in low
    assert "pnpm " not in low


def test_python_only_scope_message_not_shown_when_python_detected() -> None:
    analyze = _base_analyze()
    analyze["python"] = {
        "pythonVersionHints": [],
        "packageManagers": [],
        "dependencyFiles": [{"path": "requirements.txt", "type": "requirements.txt"}],
        "envSetupInstructions": [],
        "installInstructions": [],
    }

    md = compile_blueprint(build_context(analyze, _base_commands()))["render"]["markdown"]

    assert (
        "Python tooling not detected; this release generates Python-focused onboarding only."
        not in md
    )
