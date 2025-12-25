import logging

from packaging.specifiers import SpecifierSet

logger = logging.getLogger(__name__)


def classify_python_version(version_hint: str) -> tuple[str | None, str | None]:
    """
    Classify a Python version hint as an exact pin or a range.

    Args:
        version_hint: The version string (e.g., ">=3.11", "==3.11.0").

    Returns:
        A tuple of (pin, comment).
    """
    if not version_hint or version_hint == "*":
        return None, "Any Python version"

    # Handle implicit pins (e.g., "3.10")
    if version_hint[0].isdigit():
        return version_hint, None

    try:
        specifiers = SpecifierSet(version_hint)

        # Check for exact pin (==)
        pin = None
        for spec in specifiers:
            if spec.operator == "==":
                pin = spec.version
                break

        if pin:
            return pin, None

        # If no pin, create a readable comment
        # We simplify the specifiers for the comment
        comment = f"Requires Python {version_hint}"

        # Special case for compatible release ~=
        if "~=" in version_hint:
            # e.g. ~=3.10.0 -> Compatible with 3.10.x
            base_version = version_hint.replace("~=", "").strip()
            parts = base_version.split(".")
            if len(parts) >= 2:
                comment = f"Compatible with {'.'.join(parts[:-1])}.x"

        return None, comment

    except Exception as e:
        logger.debug(f"Failed to parse version specifier '{version_hint}': {e}")
        # If it's not a valid specifier but starts with digits, assume it's a version
        if version_hint and version_hint[0].isdigit():
            return version_hint, None
        return None, f"Version requirement: {version_hint}"
