"""Tests for canonical onboarding blueprint module."""

from __future__ import annotations

from typing import Any

import pytest

from mcp_repo_onboarding.analysis.onboarding_blueprint import (
    build_context,
    compile_blueprint,
)


def _mk(
    analyze_overrides: dict[str, Any] | None = None,
    commands_overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    analyze: dict[str, Any] = {
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
    commands: dict[str, Any] = {
        "devCommands": [],
        "testCommands": [],
        "buildCommands": [],
    }

    if analyze_overrides:
        analyze.update(analyze_overrides)
    if commands_overrides:
        commands.update(commands_overrides)

    return analyze, commands


def _compile(analyze: dict[str, Any], commands: dict[str, Any]) -> dict[str, Any]:
    return compile_blueprint(build_context(analyze, commands))


class TestBlueprintStructure:
    """Tests for blueprint output structure."""

    def test_output_has_expected_keys(self) -> None:
        """Blueprint has format, render, sections."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)

        assert result["format"] == "onboarding_blueprint_v2"
        assert result["render"]["mode"] == "verbatim"
        assert isinstance(result["render"]["markdown"], str)
        assert isinstance(result["sections"], list)

    def test_markdown_ends_with_single_newline(self) -> None:
        """Markdown ends with exactly one newline."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert md.endswith("\n")
        assert not md.endswith("\n\n")

    def test_sections_have_required_fields(self) -> None:
        """Each section has id, heading, lines."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)

        for section in result["sections"]:
            assert "id" in section
            assert "heading" in section
            assert "lines" in section


class TestEnvironmentSetup:
    """Tests for environment setup section."""

    def test_no_pin_includes_generic_venv(self) -> None:
        """No Python pin → includes generic venv snippet."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "python3 -m venv .venv" in md
        assert "(Generic suggestion)" in md

    def test_pin_present_no_generic_venv(self) -> None:
        """Python pin present + no env instructions → no generic venv."""
        analyze, commands = _mk(
            analyze_overrides={
                "python": {
                    "pythonVersionHints": ["3.12"],
                    "envSetupInstructions": [],
                    "installInstructions": [],
                    "dependencyFiles": [],
                }
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "python3 -m venv .venv" not in md
        assert "python -m venv .venv" not in md

    def test_env_instructions_insert_generic_label_before_venv(self) -> None:
        """Env instructions with venv marker get generic label inserted."""
        analyze, commands = _mk(
            analyze_overrides={
                "python": {
                    "pythonVersionHints": ["3.11"],
                    "envSetupInstructions": [
                        "python3 -m venv .venv",
                        "source .venv/bin/activate",
                    ],
                    "installInstructions": [],
                    "dependencyFiles": [],
                }
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "(Generic suggestion)" in md
        assert md.index("(Generic suggestion)") < md.index("python3 -m venv .venv")


class TestInstallSection:
    """Tests for install dependencies section."""

    def test_v7_single_pip_install_r(self) -> None:
        """Only one pip install -r command appears (V7 rule)."""
        analyze, commands = _mk(
            analyze_overrides={
                "python": {
                    "pythonVersionHints": [],
                    "envSetupInstructions": [],
                    "installInstructions": [
                        "pip install -r requirements.txt",
                        "pip install -r requirements-dev.txt",
                    ],
                    "dependencyFiles": [],
                }
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert md.count("pip install -r") == 1

    def test_make_install_takes_precedence(self) -> None:
        """make install is sole install command when present."""
        analyze, commands = _mk(
            analyze_overrides={
                "scripts": {
                    "dev": [],
                    "start": [],
                    "test": [],
                    "lint": [],
                    "format": [],
                    "install": [
                        {"command": "make install", "description": "Install deps"},
                        {"command": "pip install -r requirements.txt", "description": "Pip"},
                    ],
                    "other": [],
                },
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "make install" in md
        assert "pip install -r" not in md

    def test_no_commands_shows_fallback(self) -> None:
        """No install commands shows fallback message."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "No explicit commands detected." in md


class TestCommandFormatting:
    """Tests for command bullet formatting."""

    def test_command_bullet_format(self) -> None:
        """Commands are formatted as * `cmd` (Description.)."""
        analyze, commands = _mk(
            analyze_overrides={
                "scripts": {
                    "dev": [],
                    "start": [],
                    "test": [{"command": "pytest", "description": "Run tests."}],
                    "lint": [],
                    "format": [],
                    "install": [],
                    "other": [],
                }
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "* `pytest` (Run tests.)" in md

    def test_no_provenance_strings(self) -> None:
        """No 'source:' or 'evidence:' strings in output."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "source:" not in md
        assert "evidence:" not in md


class TestBulletStyle:
    """Tests for bullet style consistency."""

    def test_all_bullets_are_asterisk(self) -> None:
        """All bullets must be * (never -)."""
        analyze, commands = _mk(
            analyze_overrides={
                "configurationFiles": [{"path": "pyproject.toml", "description": "Config"}],
                "docs": [{"path": "README.md"}],
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        for line in md.split("\n"):
            if line.startswith("- "):
                pytest.fail(f"Found dash bullet: {line}")


class TestSanitization:
    """Tests for description sanitization."""

    @pytest.mark.parametrize(
        "junk_desc",
        [
            "hello..",
            "source: hi",
            "evidence: hi",
            "hi \t  there   ",
            "bad \u0412\u0430\u0441",
        ],
    )
    def test_description_sanitization(self, junk_desc: str) -> None:
        """Descriptions are sanitized (non-ASCII, provenance, double periods)."""
        analyze, commands = _mk(
            analyze_overrides={
                "python": {
                    "pythonVersionHints": [],
                    "envSetupInstructions": [],
                    "installInstructions": [],
                    "dependencyFiles": [{"path": "requirements.txt", "description": junk_desc}],
                }
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert ".." not in md
        assert "source:" not in md
        assert "evidence:" not in md
        assert "\u0412" not in md


class TestAnalyzerNotes:
    """Tests for analyzer notes section."""

    def test_empty_notes_section_excluded(self) -> None:
        """Analyzer notes section excluded when empty."""
        analyze, commands = _mk(
            analyze_overrides={
                "notes": [],
                "notebooks": [],
                "frameworks": [],
                "python": {
                    "pythonVersionHints": ["3.11"],
                    "envSetupInstructions": [],
                    "installInstructions": [],
                    "dependencyFiles": [{"path": "requirements.txt", "type": "requirements.txt"}],
                    "packageManagers": ["pip"],
                },
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "## Analyzer notes" not in md

    def test_frameworks_included(self) -> None:
        """Frameworks are included in analyzer notes."""
        analyze, commands = _mk(
            analyze_overrides={
                "frameworks": [{"name": "Flask", "detectionReason": "Found in pyproject.toml"}],
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "## Analyzer notes" in md
        assert "Flask" in md

    def test_notebooks_included(self) -> None:
        """Notebook paths are included in analyzer notes."""
        analyze, commands = _mk(
            analyze_overrides={
                "notebooks": ["notebooks", "examples"],
            }
        )
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "Notebooks found in:" in md


class TestRequiredHeadings:
    """Tests for required headings and order."""

    def test_all_required_headings_present(self) -> None:
        """All required headings are present in output."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        required = [
            "# ONBOARDING.md",
            "## Overview",
            "## Environment setup",
            "## Install dependencies",
            "## Run / develop locally",
            "## Run tests",
            "## Lint / format",
            "## Dependency files detected",
            "## Useful configuration files",
            "## Useful docs",
        ]

        for heading in required:
            assert heading in md, f"Missing required heading: {heading}"

    def test_headings_in_order(self) -> None:
        """Required headings appear in correct order."""
        analyze, commands = _mk()
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        required = [
            "# ONBOARDING.md",
            "## Overview",
            "## Environment setup",
            "## Install dependencies",
            "## Run / develop locally",
            "## Run tests",
            "## Lint / format",
            "## Dependency files detected",
            "## Useful configuration files",
            "## Useful docs",
        ]

        indices = [md.index(h) for h in required]
        assert indices == sorted(indices), "Headings are out of order"

    def test_repo_path_in_overview(self) -> None:
        """Repo path appears in Overview section."""
        analyze, commands = _mk(analyze_overrides={"repoPath": "/my/test/repo"})
        result = _compile(analyze, commands)
        md = result["render"]["markdown"]

        assert "Repo path: /my/test/repo" in md
