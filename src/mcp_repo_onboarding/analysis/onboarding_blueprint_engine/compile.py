"""
Blueprint compiler: compiles sections from registry into blueprint.
"""

from __future__ import annotations

from typing import Any

from .context import Context
from .registry import get_section_registry


def compile_blueprint(ctx: Context) -> dict[str, Any]:
    """Compile a blueprint from context using the registry.

    Produces output identical to v2 format.
    """
    registry = get_section_registry()

    sections: list[dict[str, Any]] = []
    for spec in registry:
        if spec.should_include(ctx):
            sections.append(spec.build(ctx))

    blueprint: dict[str, Any] = {
        "format": "onboarding_blueprint_v2",  # API contract - keep this
        "render": {"mode": "verbatim", "markdown": ""},
        "sections": sections,
    }

    blueprint["render"]["markdown"] = render_blueprint_to_markdown(blueprint)
    return blueprint


def render_blueprint_to_markdown(blueprint: dict[str, Any]) -> str:
    """Render blueprint sections to markdown string.

    Copied verbatim from v2 reference.
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
