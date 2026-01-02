"""
Canonical onboarding blueprint module (versionless).

Entrypoint for blueprint generation, backed by the registry engine.
Re-exports engine API for production use.
"""

from __future__ import annotations

from .onboarding_blueprint_engine import (
    Context,
    build_context,
    compile_blueprint,
    render_blueprint_to_markdown,
)
from .onboarding_blueprint_engine.registry import (
    BULLET,
    NO_COMMANDS,
    NO_CONFIG,
    NO_DEPS,
    NO_DOCS,
)

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint",
    "render_blueprint_to_markdown",
    "BULLET",
    "NO_COMMANDS",
    "NO_CONFIG",
    "NO_DEPS",
    "NO_DOCS",
]
