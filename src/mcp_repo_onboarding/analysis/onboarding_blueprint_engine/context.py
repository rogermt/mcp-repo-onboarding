"""
Blueprint context: minimal data structure for blueprint compilation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Context:
    """Minimal context for blueprint compilation.

    Matches reference v2 exactly:
    - analyze: raw analyzer output dict
    - commands: command overrides dict
    """

    analyze: dict[str, Any]
    commands: dict[str, Any]


def build_context(analyze: dict[str, Any], commands: dict[str, Any]) -> Context:
    """Build a Context from analyze and commands dicts."""
    return Context(analyze=analyze or {}, commands=commands or {})
