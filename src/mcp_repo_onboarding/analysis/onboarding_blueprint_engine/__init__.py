"""
Blueprint engine package.

Registry-driven blueprint compilation with modular section builders.
"""

from __future__ import annotations

from .compile import compile_blueprint_v2, render_blueprint_to_markdown
from .context import Context, build_context
from .registry import (
    BULLET,
    NO_COMMANDS,
    NO_CONFIG,
    NO_DEPS,
    NO_DOCS,
    get_section_registry,
)

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint_v2",
    "render_blueprint_to_markdown",
    "get_section_registry",
    "BULLET",
    "NO_COMMANDS",
    "NO_CONFIG",
    "NO_DEPS",
    "NO_DOCS",
]
