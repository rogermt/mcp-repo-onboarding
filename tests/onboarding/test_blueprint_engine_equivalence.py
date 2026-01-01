"""
Equivalence gate tests for #87 blueprint refactoring.

These tests compare output from the reference (frozen v2) and the new engine.
They SHOULD FAIL until the engine is fully implemented and byte-for-byte identical
to the reference.

Core assertion: engine output == reference output (render.markdown + sections).
"""

from __future__ import annotations

from typing import Any

import pytest

from mcp_repo_onboarding.analysis.onboarding_blueprint_engine.compile import (
    compile_blueprint_v2 as compile_eng,
)

# Import engine (new implementation - these will fail until engine exists)
from mcp_repo_onboarding.analysis.onboarding_blueprint_engine.context import (
    build_context as build_ctx_eng,
)

# Import reference (frozen v2 baseline)
from mcp_repo_onboarding.analysis.onboarding_blueprint_reference import (
    build_context as build_ctx_ref,
)
from mcp_repo_onboarding.analysis.onboarding_blueprint_reference import (
    compile_blueprint_v2 as compile_ref,
)


def _mk(
    analyze_overrides: dict[str, Any] | None = None,
    commands_overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build minimal but complete analyze and commands dicts for testing."""
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
        # Shallow merge for nested dicts
        for key, value in analyze_overrides.items():
            if isinstance(value, dict) and isinstance(analyze.get(key), dict):
                analyze[key].update(value)
            else:
                analyze[key] = value

    if commands_overrides:
        commands.update(commands_overrides)

    return analyze, commands


def _assert_equivalent(analyze: dict[str, Any], commands: dict[str, Any]) -> None:
    """
    Core equivalence gate: engine and reference must produce identical output.

    Assertions:
    1. render.markdown byte-for-byte equal (non-negotiable)
    2. sections list equal
    3. format string is "onboarding_blueprint_v2"
    4. render.mode is "verbatim"
    """
    ref = compile_ref(build_ctx_ref(analyze, commands))
    eng = compile_eng(build_ctx_eng(analyze, commands))

    # Non-negotiable gate: byte-for-byte markdown equality
    assert eng["render"]["markdown"] == ref["render"]["markdown"], (
        "Engine markdown differs from reference.\n"
        f"Expected:\n{ref['render']['markdown']}\n"
        f"Got:\n{eng['render']['markdown']}"
    )

    # Stronger gate: sections must match exactly
    assert eng["sections"] == ref["sections"], (
        "Engine sections differ from reference.\n"
        f"Expected: {ref['sections']}\n"
        f"Got: {eng['sections']}"
    )

    # Schema invariants
    assert eng["format"] == "onboarding_blueprint_v2"
    assert eng["render"]["mode"] == "verbatim"


class TestEquivalenceMinimal:
    """Minimal repo with no content."""

    def test_equivalence_minimal_repo(self) -> None:
        """Empty analyze + commands should produce identical output."""
        analyze, commands = _mk()
        _assert_equivalent(analyze, commands)


class TestEquivalencePythonVersioning:
    """Python version pinning behavior."""

    def test_equivalence_no_pin_includes_generic_venv_lines(self) -> None:
        """No Python version pin → include generic venv snippet."""
        analyze, commands = _mk(
            analyze_overrides={
                "python": {
                    "pythonVersionHints": [],
                    "envSetupInstructions": [],
                    "installInstructions": [],
                    "dependencyFiles": [],
                }
            }
        )
        _assert_equivalent(analyze, commands)

        # Verify behavior: generic venv should be present
        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        assert "python3 -m venv .venv" in out

    def test_equivalence_pin_present_no_env_no_generic_venv(self) -> None:
        """With Python version pin and no explicit env instructions → no generic venv."""
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
        _assert_equivalent(analyze, commands)

        # Verify behavior: no generic venv when pin exists and no explicit env
        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        assert "python3 -m venv .venv" not in out


class TestEquivalenceEnvInstructions:
    """Environment setup instruction handling."""

    def test_equivalence_env_instructions_with_venv_marker(self) -> None:
        """Env instructions with venv marker → insert (Generic suggestion) before marker."""
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
        _assert_equivalent(analyze, commands)

        # Verify behavior: (Generic suggestion) inserted before venv
        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        assert "(Generic suggestion)" in out
        assert out.index("(Generic suggestion)") < out.index("python3 -m venv .venv")


class TestEquivalenceInstallCommands:
    """Install command filtering and deduplication."""

    def test_equivalence_v7_single_pip_install_r(self) -> None:
        """Multiple pip install -r commands → only one emitted (V7 behavior)."""
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
        _assert_equivalent(analyze, commands)

        # Verify behavior: only one "pip install -r" remains
        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        pip_r_count = out.count("pip install -r")
        assert pip_r_count == 1, f"Expected 1 'pip install -r', found {pip_r_count}"


class TestEquivalenceDescriptionSanitization:
    """Description sanitization: non-ASCII, provenance, punctuation."""

    @pytest.mark.parametrize(
        "junk_desc",
        [
            "hello..",  # double period
            "source: hi",  # provenance marker
            "evidence: hi",  # provenance marker
            "hi \t  there   ",  # whitespace normalization
            "bad \u0412\u0430\u0441",  # non-ascii (Cyrillic) should be stripped
        ],
    )
    def test_equivalence_description_sanitization(self, junk_desc: str) -> None:
        """Descriptions are sanitized (non-ASCII removed, provenance stripped, single period)."""
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
        _assert_equivalent(analyze, commands)


class TestEquivalenceScriptCommands:
    """Script command formatting and deduplication."""

    def test_equivalence_dev_commands_with_description(self) -> None:
        """Dev commands with descriptions are formatted correctly."""
        analyze, commands = _mk(
            commands_overrides={
                "devCommands": [{"command": "uv run dev", "description": "Run dev server."}]
            }
        )
        _assert_equivalent(analyze, commands)

    def test_equivalence_test_commands(self) -> None:
        """Test commands are formatted correctly."""
        analyze, commands = _mk(
            analyze_overrides={
                "scripts": {
                    "test": [{"command": "pytest", "description": "Run pytest tests."}],
                }
            }
        )
        _assert_equivalent(analyze, commands)

    def test_equivalence_deduplication_same_command_twice(self) -> None:
        """Duplicate commands are deduplicated."""
        analyze, commands = _mk(
            analyze_overrides={
                "scripts": {
                    "test": [
                        {"command": "pytest", "description": "Run pytest."},
                        {"command": "pytest", "description": "Run pytest again."},
                    ]
                }
            }
        )
        _assert_equivalent(analyze, commands)


class TestEquivalenceConfigAndDocs:
    """Configuration files and docs handling."""

    def test_equivalence_configuration_files(self) -> None:
        """Configuration files are listed with descriptions."""
        analyze, commands = _mk(
            analyze_overrides={
                "configurationFiles": [
                    {"path": "pyproject.toml", "description": "Python project config."}
                ]
            }
        )
        _assert_equivalent(analyze, commands)

    def test_equivalence_docs_files(self) -> None:
        """Docs files are listed."""
        analyze, commands = _mk(
            analyze_overrides={
                "docs": [
                    {"path": "docs/index.md"},
                    {"path": "docs/contributing.md"},
                ]
            }
        )
        _assert_equivalent(analyze, commands)


class TestEquivalenceNotebooksAndFrameworks:
    """Notebook and framework detection."""

    def test_equivalence_notebooks_detected(self) -> None:
        """Notebooks detected → includes notebook-centric note."""
        analyze, commands = _mk(
            analyze_overrides={
                "notebooks": ["notebooks/", "analysis/"],
            }
        )
        _assert_equivalent(analyze, commands)

        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        assert "Notebook-centric repo detected" in out

    def test_equivalence_frameworks_detected(self) -> None:
        """Frameworks detected → included in analyzer notes."""
        analyze, commands = _mk(
            analyze_overrides={
                "frameworks": [{"name": "FastAPI", "detectionReason": "Found in imports."}]
            }
        )
        _assert_equivalent(analyze, commands)

        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        assert "FastAPI" in out


class TestEquivalenceAnalyzerNotes:
    """Analyzer notes handling."""

    def test_equivalence_analyzer_notes_with_text(self) -> None:
        """Analyzer notes are included with sanitization."""
        analyze, commands = _mk(
            analyze_overrides={
                "notes": [
                    "Note 1: Important.",
                    "Note 2: Another note.",
                ]
            }
        )
        _assert_equivalent(analyze, commands)

        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        assert "Note 1" in out
        assert "Note 2" in out

    def test_equivalence_analyzer_notes_sanitized(self) -> None:
        """Analyzer notes with provenance markers are sanitized."""
        analyze, commands = _mk(
            analyze_overrides={
                "notes": [
                    "source: this is a note",
                    "evidence: another note",
                ]
            }
        )
        _assert_equivalent(analyze, commands)

        out = compile_eng(build_ctx_eng(analyze, commands))["render"]["markdown"]
        # Provenance markers should be removed
        assert "source:" not in out
        assert "evidence:" not in out


class TestEquivalenceComplexScenario:
    """Full scenario with multiple sections."""

    def test_equivalence_complex_repo(self) -> None:
        """Complex repo with dependencies, scripts, frameworks."""
        analyze, commands = _mk(
            analyze_overrides={
                "repoPath": "/home/user/project",
                "python": {
                    "pythonVersionHints": ["3.11"],
                    "envSetupInstructions": [
                        "python3 -m venv venv",
                        "source venv/bin/activate",
                    ],
                    "installInstructions": ["pip install -r requirements.txt"],
                    "dependencyFiles": [
                        {"path": "requirements.txt", "description": "Core dependencies."},
                        {
                            "path": "requirements-dev.txt",
                            "description": "Dev dependencies.",
                        },
                    ],
                },
                "scripts": {
                    "dev": [{"command": "uv run dev", "description": "Run dev server."}],
                    "test": [{"command": "pytest", "description": "Run all tests."}],
                    "lint": [{"command": "ruff check .", "description": "Lint code."}],
                    "format": [{"command": "ruff format .", "description": "Format code."}],
                },
                "configurationFiles": [
                    {"path": "pyproject.toml", "description": "Python config."},
                    {"path": "ruff.toml", "description": "Ruff config."},
                ],
                "docs": [
                    {"path": "README.md"},
                    {"path": "docs/"},
                ],
                "frameworks": [{"name": "FastAPI", "detectionReason": "Found FastAPI in imports."}],
                "notes": [
                    "Uses async/await extensively.",
                ],
            },
            commands_overrides={
                "devCommands": [{"command": "uv run dev", "description": "Dev server (uv)."}],
                "testCommands": [{"command": "pytest", "description": "Test runner (pytest)."}],
            },
        )
        _assert_equivalent(analyze, commands)
