"""
Blueprint engine: registry-driven blueprint compilation.

Exports the core API for building onboarding blueprints.
"""

from __future__ import annotations

from .compile import compile_blueprint_v2, render_blueprint_to_markdown
from .context import Context, build_context

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint_v2",
    "render_blueprint_to_markdown",
]
