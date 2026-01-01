"""
Canonical blueprint module (engine-backed, versionless entrypoint).

Production code should import from this module, not version-specific variants.
"""

from __future__ import annotations

# Re-export engine API (provides stable versionless import path)
from mcp_repo_onboarding.analysis.onboarding_blueprint_engine import (  # noqa: F401
    BULLET,
    NO_COMMANDS,
    NO_CONFIG,
    NO_DEPS,
    NO_DOCS,
    Context,
    build_context,
    compile_blueprint_v2,
    render_blueprint_to_markdown,
)

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint_v2",
    "render_blueprint_to_markdown",
    "BULLET",
    "NO_COMMANDS",
    "NO_CONFIG",
    "NO_DEPS",
    "NO_DOCS",
]
