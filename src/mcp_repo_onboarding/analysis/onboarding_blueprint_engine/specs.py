"""
Section specification for blueprint registry.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .context import Context


@dataclass
class SectionSpec:
    """Specification for a blueprint section.

    Fields:
    - section_id: unique section identifier
    - heading: markdown heading string (e.g., "## Install dependencies")
    - order: relative ordering in registry
    - build_lines: callable that returns list of lines for this section
    - include_if: optional predicate to conditionally include section
    """

    section_id: str
    heading: str
    order: int
    build_lines: Callable[[Context], list[str]]
    include_if: Callable[[Context], bool] | None = None

    def build(self, ctx: Context) -> dict[str, Any]:
        """Build a section dict from this spec."""
        lines = self.build_lines(ctx)
        return {"id": self.section_id, "heading": self.heading, "lines": lines}

    def should_include(self, ctx: Context) -> bool:
        """Check if section should be included."""
        if self.include_if is None:
            return True
        return self.include_if(ctx)
