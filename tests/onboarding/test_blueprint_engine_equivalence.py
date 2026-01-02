"""
Equivalence gate tests for blueprint engine.

Tests that engine produces byte-for-byte identical output vs v2 reference.
Tests are synthetic only (no analyzer calls, no fixtures).
"""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint_engine import (
    build_context as engine_build_context,
)
from mcp_repo_onboarding.analysis.onboarding_blueprint_engine import (
    compile_blueprint_v2 as engine_compile_blueprint_v2,
)
from mcp_repo_onboarding.analysis.onboarding_blueprint_reference import (
    build_context as ref_build_context,
)
from mcp_repo_onboarding.analysis.onboarding_blueprint_reference import (
    compile_blueprint_v2 as ref_compile_blueprint_v2,
)


def test_equivalence_minimal_repo() -> None:
    """Minimal repo: no commands, no deps."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {"pythonVersionHints": [], "envSetupInstructions": []},
        "scripts": {},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]


def test_equivalence_with_python_pin() -> None:
    """Python pin present: no generic venv snippet."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {
            "pythonVersionHints": ["Python 3.9+"],
            "envSetupInstructions": [],
        },
        "scripts": {},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]


def test_equivalence_with_venv_marker() -> None:
    """Env instructions include venv marker → inserts `(Generic suggestion)`."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": ["python3 -m venv .venv", "source .venv/bin/activate"],
        },
        "scripts": {},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]


def test_equivalence_duplicate_pip_install_r() -> None:
    """Two `pip install -r` → only one emitted."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
            "installInstructions": [
                "pip install -r requirements.txt",
                "pip install -r requirements-dev.txt",
            ],
        },
        "scripts": {"install": []},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]
    # Verify only one pip install -r is in the markdown
    assert engine_blueprint["render"]["markdown"].count("pip install -r") == 1


def test_equivalence_sanitization_nonascii() -> None:
    """Sanitization: non-ASCII characters removed."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
        },
        "scripts": {
            "install": [{"command": "pip install", "description": "Install Вас garbage mixed in."}]
        },
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]


def test_equivalence_sanitization_double_periods() -> None:
    """Sanitization: double periods normalized to single."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
        },
        "scripts": {"test": [{"command": "pytest", "description": "Run tests.. with pytest."}]},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]


def test_equivalence_analyzer_notes_frameworks() -> None:
    """Analyzer notes: framework detection logic."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {"pythonVersionHints": [], "envSetupInstructions": []},
        "scripts": {},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [
            {"name": "Django", "detectionReason": "Detected via classifiers"},
            {"name": "Flask", "detectionReason": "Detected via Poetry deps"},
        ],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]
    assert "Django, Flask" in engine_blueprint["render"]["markdown"]


def test_equivalence_analyzer_notes_notebooks() -> None:
    """Analyzer notes: notebook detection logic."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {"pythonVersionHints": [], "envSetupInstructions": []},
        "scripts": {},
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": ["notebooks/examples/", "."],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]
    assert "Notebooks found in: notebooks/examples/, ./" in engine_blueprint["render"]["markdown"]


def test_equivalence_make_install_precedence() -> None:
    """`make install` takes precedence over other install commands."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
        },
        "scripts": {
            "install": [
                {"command": "make install", "description": "Install deps"},
                {"command": "pip install -r requirements.txt", "description": "Pip"},
            ]
        },
        "configurationFiles": [],
        "dependencyFiles": [],
        "docs": [],
        "notes": [],
        "notebooks": [],
        "frameworks": [],
    }
    commands: dict[str, Any] = {}

    ref_ctx = ref_build_context(analyze, commands)
    engine_ctx = engine_build_context(analyze, commands)

    ref_blueprint = ref_compile_blueprint_v2(ref_ctx)
    engine_blueprint = engine_compile_blueprint_v2(engine_ctx)

    assert ref_blueprint["render"]["markdown"] == engine_blueprint["render"]["markdown"]
    assert ref_blueprint["sections"] == engine_blueprint["sections"]
    assert "* `make install`" in engine_blueprint["render"]["markdown"]
    assert "pip install" not in engine_blueprint["render"]["markdown"]
