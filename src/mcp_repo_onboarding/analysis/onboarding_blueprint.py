"""
Canonical onboarding blueprint module (versionless).

Entrypoint for blueprint generation, backed by the registry engine.
Re-exports engine API for production use.

NOTE: This module still needs to support the old v1 API during transition.
Legacy imports for build_onboarding_blueprint_v1 are NOT supported yet (Phase 8).
"""

from __future__ import annotations

from typing import Any

from .onboarding_blueprint_engine import (
    Context,
    build_context,
    compile_blueprint_v2,
    render_blueprint_to_markdown,
)


# Temporary stub for v1 API compatibility (Phase 8)
def build_onboarding_blueprint_v1(analyze: dict[str, Any]) -> dict[str, Any]:
    """
    Build v1 blueprint from analyze dict.

    NOTE: This is a stub. The actual v1 implementation is in onboarding_blueprint.py
    on master (not yet migrated). This is returned for compatibility.
    """
    raise NotImplementedError(
        "build_onboarding_blueprint_v1 not yet ported to canonical module. "
        "This is scheduled for Phase 9."
    )


__all__ = [
    "Context",
    "build_context",
    "compile_blueprint_v2",
    "render_blueprint_to_markdown",
    "build_onboarding_blueprint_v1",
]
