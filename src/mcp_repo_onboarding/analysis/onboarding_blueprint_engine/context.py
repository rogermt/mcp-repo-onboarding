"""
Context builder for blueprint engine.

Minimal context: wraps raw analyze + commands dicts (no transformation in #87).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Context:
    """Blueprint compilation context.

    Holds raw analyzer output and commands for section builders.
    No transformation or type conversion in #87 (kept minimal for equivalence safety).
    """

    analyze: dict[str, Any]
    commands: dict[str, Any]


def build_context(analyze: dict[str, Any], commands: dict[str, Any]) -> Context:
    """Build context from analyzer output and commands.

    Args:
        analyze: Raw analyzer output dict
        commands: Commands dict

    Returns:
        Context object for use in compilation
    """
    return Context(analyze=analyze or {}, commands=commands or {})
