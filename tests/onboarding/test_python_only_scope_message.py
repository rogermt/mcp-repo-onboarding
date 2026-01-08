from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import build_context, compile_blueprint


def _mk_node_only_analyze() -> dict[str, Any]:
    # Minimal payload to replicate nanobanana-like "no python" case.
    # Has Node.js evidence but no Python evidence.
    return {
        "repoPath": "/test/repo",
        "primaryTooling": "Node.js",  # Node-primary, so no scope note
        "python": None,  # <- key condition
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
        # Optional: show other tooling exists (still no commands should be suggested)
        "otherTooling": [
            {
                "name": "Node.js",
                "evidenceFiles": ["package.json", "yarn.lock"],
                "confidence": "detected",
            }
        ],
    }


def _mk_commands() -> dict[str, Any]:
    return {"devCommands": [], "testCommands": [], "buildCommands": []}


def test_scope_note_for_node_only_repo_is_not_rendered() -> None:
    """Node-primary repos should NOT show the scope note (primaryTooling = Node.js)."""
    analyze = _mk_node_only_analyze()
    md = compile_blueprint(build_context(analyze, _mk_commands()))["render"]["markdown"]

    # Node-primary repos should NOT show the scope note
    assert (
        "Python/Node.js tooling not detected; this release generates onboarding for Python and Node.js repos only."
        not in md
    )

    low = md.lower()
    assert "npm " not in low
    assert "yarn " not in low
    assert "pnpm " not in low


def test_scope_note_absent_when_python_evidence_present() -> None:
    """Scope note not shown when Python evidence is present."""
    analyze = _mk_node_only_analyze()
    analyze["python"] = {
        "pythonVersionHints": [],
        "packageManagers": [],
        "dependencyFiles": [{"path": "requirements.txt", "type": "requirements.txt"}],
        "envSetupInstructions": [],
        "installInstructions": [],
    }

    md = compile_blueprint(build_context(analyze, _mk_commands()))["render"]["markdown"]
    assert (
        "Python/Node.js tooling not detected; this release generates onboarding for Python and Node.js repos only."
        not in md
    )
