"""
Tests for canonical module (#87 refactoring).

The canonical module (onboarding_blueprint.py) should be a stable, versionless
entrypoint that re-exports the engine API. These tests ensure:

1. All expected exports are present
2. Output format is correct ("onboarding_blueprint_v2")
3. Behavior matches engine
"""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis import onboarding_blueprint


def _mk_analyze(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build minimal analyze dict."""
    base: dict[str, Any] = {
        "repoPath": "/test/repo",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
            "installInstructions": [],
            "dependencyFiles": [],
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
    if overrides:
        for k, v in overrides.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k].update(v)
            else:
                base[k] = v
    return base


def _mk_cmds(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build minimal commands dict."""
    base: dict[str, Any] = {"devCommands": [], "testCommands": [], "buildCommands": []}
    if overrides:
        base.update(overrides)
    return base


class TestCanonicalModuleExports:
    """Test that canonical module exports all required APIs."""

    def test_canonical_exports_context(self) -> None:
        """Canonical module should export Context class."""
        assert hasattr(onboarding_blueprint, "Context")

    def test_canonical_exports_build_context(self) -> None:
        """Canonical module should export build_context function."""
        assert hasattr(onboarding_blueprint, "build_context")
        assert callable(onboarding_blueprint.build_context)

    def test_canonical_exports_compile_blueprint_v2(self) -> None:
        """Canonical module should export compile_blueprint_v2 function."""
        assert hasattr(onboarding_blueprint, "compile_blueprint_v2")
        assert callable(onboarding_blueprint.compile_blueprint_v2)

    def test_canonical_exports_render_blueprint_to_markdown(self) -> None:
        """Canonical module should export render_blueprint_to_markdown function."""
        assert hasattr(onboarding_blueprint, "render_blueprint_to_markdown")
        assert callable(onboarding_blueprint.render_blueprint_to_markdown)

    def test_canonical_exports_constants(self) -> None:
        """Canonical module should export constants."""
        assert hasattr(onboarding_blueprint, "BULLET")
        assert hasattr(onboarding_blueprint, "NO_COMMANDS")
        assert hasattr(onboarding_blueprint, "NO_DEPS")
        assert hasattr(onboarding_blueprint, "NO_CONFIG")
        assert hasattr(onboarding_blueprint, "NO_DOCS")


class TestCanonicalModuleConstants:
    """Test that constants have expected values."""

    def test_bullet_constant(self) -> None:
        """BULLET should be "* "."""
        assert onboarding_blueprint.BULLET == "* "

    def test_no_commands_constant(self) -> None:
        """NO_COMMANDS should match reference."""
        assert onboarding_blueprint.NO_COMMANDS == "No explicit commands detected."

    def test_no_deps_constant(self) -> None:
        """NO_DEPS should match reference."""
        assert onboarding_blueprint.NO_DEPS == "No dependency files detected."

    def test_no_config_constant(self) -> None:
        """NO_CONFIG should match reference."""
        assert onboarding_blueprint.NO_CONFIG == "No useful configuration files detected."

    def test_no_docs_constant(self) -> None:
        """NO_DOCS should match reference."""
        assert onboarding_blueprint.NO_DOCS == "No useful docs detected."


class TestCanonicalModuleBehavior:
    """Test that canonical module produces correct output."""

    def test_canonical_produces_v2_format(self) -> None:
        """Output format should be "onboarding_blueprint_v2"."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result = onboarding_blueprint.compile_blueprint_v2(ctx)

        assert result["format"] == "onboarding_blueprint_v2"

    def test_canonical_produces_verbatim_mode(self) -> None:
        """Render mode should be "verbatim"."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result = onboarding_blueprint.compile_blueprint_v2(ctx)

        assert result["render"]["mode"] == "verbatim"

    def test_canonical_has_markdown_output(self) -> None:
        """Markdown output should exist and be a string."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result = onboarding_blueprint.compile_blueprint_v2(ctx)

        assert "markdown" in result["render"]
        assert isinstance(result["render"]["markdown"], str)

    def test_canonical_has_sections(self) -> None:
        """Sections should be a list."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result = onboarding_blueprint.compile_blueprint_v2(ctx)

        assert "sections" in result
        assert isinstance(result["sections"], list)

    def test_canonical_context_creation(self) -> None:
        """build_context should create a Context object."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)

        assert ctx is not None
        assert hasattr(ctx, "analyze")
        assert hasattr(ctx, "commands")

    def test_canonical_sections_have_required_fields(self) -> None:
        """Each section should have id, heading, and lines."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result = onboarding_blueprint.compile_blueprint_v2(ctx)

        for section in result["sections"]:
            assert "id" in section
            assert "heading" in section
            assert "lines" in section
            assert isinstance(section["lines"], list)

    def test_canonical_rendering_consistency(self) -> None:
        """Rendering the same blueprint twice should produce same markdown."""
        analyze = _mk_analyze()
        commands = _mk_cmds()

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result1 = onboarding_blueprint.compile_blueprint_v2(ctx)
        rendered = onboarding_blueprint.render_blueprint_to_markdown(result1)

        # Should equal the original markdown
        assert rendered == result1["render"]["markdown"]

    def test_canonical_with_content(self) -> None:
        """Canonical module should handle repos with content."""
        analyze = _mk_analyze(
            overrides={
                "python": {
                    "pythonVersionHints": ["3.11"],
                    "envSetupInstructions": ["python3 -m venv venv"],
                    "installInstructions": ["pip install -r requirements.txt"],
                    "dependencyFiles": [{"path": "requirements.txt", "description": ""}],
                }
            }
        )
        commands = _mk_cmds(
            overrides={
                "devCommands": [{"command": "uvicorn main:app", "description": "Run API server."}]
            }
        )

        ctx = onboarding_blueprint.build_context(analyze, commands)
        result = onboarding_blueprint.compile_blueprint_v2(ctx)

        # Should have output
        assert result["render"]["markdown"]
        assert len(result["sections"]) > 0

        # Should contain Python version
        assert "3.11" in result["render"]["markdown"]

        # Should contain commands
        assert "uvicorn" in result["render"]["markdown"]
