"""
Backward compatibility shim for onboarding_blueprint_v2.

This shim allows old code importing onboarding_blueprint_v2 to continue working.
Prefer importing from onboarding_blueprint (canonical module) in new code.
"""

from __future__ import annotations

# Re-export canonical module (which is engine-backed)
from mcp_repo_onboarding.analysis.onboarding_blueprint import (  # noqa: F401
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
