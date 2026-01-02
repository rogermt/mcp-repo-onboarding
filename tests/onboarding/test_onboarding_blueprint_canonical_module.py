"""
Tests for canonical (versionless) onboarding_blueprint module.

Ensures canonical exports and behavior match engine.
"""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis import onboarding_blueprint


def test_canonical_exports() -> None:
    """Canonical module exports required API."""
    assert hasattr(onboarding_blueprint, "Context")
    assert hasattr(onboarding_blueprint, "build_context")
    assert hasattr(onboarding_blueprint, "compile_blueprint_v2")
    assert hasattr(onboarding_blueprint, "render_blueprint_to_markdown")


def test_canonical_context_minimal() -> None:
    """Canonical Context works with minimal data."""
    ctx = onboarding_blueprint.build_context({}, {})
    assert ctx.analyze == {}
    assert ctx.commands == {}


def test_canonical_context_with_data() -> None:
    """Canonical Context preserves data."""
    analyze: dict[str, Any] = {"repoPath": "/foo"}
    commands: dict[str, Any] = {"devCommands": []}

    ctx = onboarding_blueprint.build_context(analyze, commands)
    assert ctx.analyze == analyze
    assert ctx.commands == commands


def test_canonical_compile_produces_valid_blueprint() -> None:
    """Canonical compile produces valid blueprint structure."""
    ctx = onboarding_blueprint.build_context(
        {
            "repoPath": ".",
            "python": {"pythonVersionHints": [], "envSetupInstructions": []},
            "scripts": {},
            "configurationFiles": [],
            "dependencyFiles": [],
            "docs": [],
            "notes": [],
            "notebooks": [],
            "frameworks": [],
        },
        {},
    )

    blueprint = onboarding_blueprint.compile_blueprint_v2(ctx)

    assert isinstance(blueprint, dict)
    assert "format" in blueprint
    assert blueprint["format"] == "onboarding_blueprint_v2"
    assert "sections" in blueprint
    assert "render" in blueprint
    assert isinstance(blueprint["sections"], list)
    assert isinstance(blueprint["render"], dict)
    assert "markdown" in blueprint["render"]


def test_canonical_render_produces_markdown() -> None:
    """Canonical render produces markdown output."""
    blueprint: dict[str, Any] = {
        "sections": [
            {"heading": "# Title", "lines": []},
            {"heading": "## Section", "lines": ["* Item"]},
        ]
    }

    markdown = onboarding_blueprint.render_blueprint_to_markdown(blueprint)

    assert isinstance(markdown, str)
    assert "# Title" in markdown
    assert "## Section" in markdown
    assert "* Item" in markdown
