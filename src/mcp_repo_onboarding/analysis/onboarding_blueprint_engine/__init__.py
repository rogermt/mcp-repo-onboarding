"""
Blueprint engine: registry-driven blueprint compilation.

Internal implementation. Prefer importing from `analysis.onboarding_blueprint`.
"""

from __future__ import annotations

from .compile import compile_blueprint, render_blueprint_to_markdown
from .context import Context, build_context

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint",
    "render_blueprint_to_markdown",
]
