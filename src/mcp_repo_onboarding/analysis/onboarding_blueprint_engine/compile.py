"""
Blueprint compilation logic and markdown rendering.

Orchestrates section builders from registry and renders to markdown.
"""

from __future__ import annotations

from typing import Any

from .context import Context
from .registry import get_section_registry


def compile_blueprint_v2(ctx: Context) -> dict[str, Any]:
    """Compile analysis context into a blueprint.

    Iterates through section registry, calls each builder, and collects sections.

    Args:
        ctx: Blueprint compilation context

    Returns:
        Blueprint dict with format, sections, and rendered markdown
    """
    sections: list[dict[str, Any]] = []

    # Iterate through registry and build sections
    for spec in get_section_registry():
        sec = spec.builder(ctx)
        if sec is not None:
            sections.append(sec)

    # Assemble blueprint structure
    blueprint: dict[str, Any] = {
        "format": "onboarding_blueprint_v2",
        "render": {"mode": "verbatim", "markdown": ""},
        "sections": sections,
    }

    # Render sections to markdown
    blueprint["render"]["markdown"] = render_blueprint_to_markdown(blueprint)
    return blueprint


def render_blueprint_to_markdown(blueprint: dict[str, Any]) -> str:
    """Render blueprint sections to markdown.

    Iterates through sections, combines headings and lines, and joins with blank lines.

    Args:
        blueprint: Blueprint dict with sections

    Returns:
        Markdown string
    """
    secs = blueprint.get("sections")
    if not isinstance(secs, list):
        return ""

    blocks: list[str] = []
    for sec in secs:
        if not isinstance(sec, dict):
            continue

        heading = sec.get("heading")
        if not isinstance(heading, str) or not heading.strip():
            continue

        lines = sec.get("lines")
        if not isinstance(lines, list):
            lines = []

        clean_lines: list[str] = []
        for ln in lines:
            if isinstance(ln, str):
                clean_lines.append(ln.rstrip())
            else:
                clean_lines.append(str(ln).rstrip())

        block = heading.rstrip()
        if clean_lines:
            block += "\n" + "\n".join(clean_lines)
        blocks.append(block)

    out = "\n\n".join(blocks).rstrip()
    return (out + "\n") if out else ""
