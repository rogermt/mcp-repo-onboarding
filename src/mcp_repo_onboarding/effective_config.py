from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .config import SAFETY_IGNORES

# Safety invariant: these ignores MUST always apply and MUST NOT be disable-able.
REQUIRED_SAFETY_IGNORES: tuple[str, ...] = (
    "tests/fixtures/",
    "test/fixtures/",
)


def _dedupe_preserve_order(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        s = str(raw)
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return tuple(out)


@dataclass(frozen=True, slots=True)
class EffectiveConfig:
    """
    Internal config layering scaffold (defaults ⊕ overrides).

    Important: this is additive-only scaffolding.
    There is intentionally no mechanism to remove/negate safety ignores.

    Future: parse .onboardingrc / pyproject.toml into these fields.
    """

    # Additive ignore patterns (cannot disable REQUIRED_SAFETY_IGNORES)
    additional_safety_ignores: tuple[str, ...] = ()

    # Future seam: targeted scan / pinned paths (not used yet)
    additional_targeted_paths: tuple[str, ...] = ()

    # Future seam: prioritization adjustments (not used yet)
    # Keep as placeholder so the pipeline seam exists without behavior change.
    prioritization_adjustments: tuple[tuple[str, int], ...] = ()

    @property
    def safety_ignores(self) -> tuple[str, ...]:
        """
        Resolved safety ignores: defaults + REQUIRED + additive overrides.
        Deterministic order, de-duped.
        """
        return _dedupe_preserve_order(
            tuple(SAFETY_IGNORES) + REQUIRED_SAFETY_IGNORES + tuple(self.additional_safety_ignores)
        )
