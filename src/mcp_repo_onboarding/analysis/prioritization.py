from pathlib import Path

__all__ = ["get_config_priority", "get_doc_priority", "get_dep_priority"]


def get_config_priority(path: str) -> int:
    """
    Determine the priority of a configuration file for display.

    Args:
        path: Path to the configuration file.

    Returns:
        Priority score (higher is better).
    """
    name = Path(path).name.lower()
    score = 10
    if name == "makefile" or name == "justfile":
        score = 300
    elif name in [
        "tox.ini",
        "noxfile.py",
        ".pre-commit-config.yaml",
        ".pre-commit-config.yml",
        "pytest.ini",
    ]:
        score = 200
    elif path.startswith(".github/workflows/"):
        score = 150

    # V9: Root Priority (+100)
    if "/" not in path:
        score += 100

    return score


def get_doc_priority(path: str) -> int:
    """
    Determine the priority of a documentation file.

    Args:
        path: Path to the doc file.

    Returns:
        Priority score (higher is better).
    """
    name = Path(path).name.lower()
    score = 50

    # 3.1 Buckets
    if "/" not in path:
        if name.startswith(("readme", "contributing", "license", "security")):
            score = 300

    if score < 300:
        if path.startswith("docs/") and "/" not in path[5:]:
            score = 250
        elif any(kw in path.lower() for kw in ["quickstart", "install", "setup", "tutorial"]):
            score = 200
        elif path.startswith("docs/"):
            score = 150

    # Penalties
    if "admin" in path.lower():
        score -= 20

    if any(p in path.lower() for p in ["tests/", "test/", "examples/", "scripts/", "src/"]):
        score -= 200

    return score


def get_dep_priority(path: str) -> int:
    """
    Determine the priority of a dependency file.

    Args:
        path: Path to the dependency file.

    Returns:
        Priority score (higher is better).
    """
    name = Path(path).name.lower()
    score = 100

    # root manifests
    if "/" not in path:
        if name == "pyproject.toml" or name.startswith("requirements"):
            score = 300
    elif name == "pyproject.toml" or name.startswith("requirements"):
        score = 150

    # Penalties
    if any(p in path.lower() for p in ["tests/", "test/", "examples/", "scripts/"]):
        score -= 200

    return score
