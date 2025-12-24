from pathlib import Path


def get_config_priority(path: str) -> int:
    """
    Determine the priority of a configuration file for display.

    Args:
        path: Path to the configuration file.

    Returns:
        Priority score (higher is better).
    """
    name = Path(path).name.lower()
    if name == "makefile":
        return 100
    if name in ["pyproject.toml", "setup.cfg", "setup.py"]:
        return 90
    if name in ["tox.ini", "noxfile.py"]:
        return 80
    if name in [".pre-commit-config.yaml", ".pre-commit-config.yml"]:
        return 70
    if path.startswith(".github/workflows/"):
        return 60
    return 10


def get_doc_priority(path: str) -> int:
    """
    Determine the priority of a documentation file.

    Args:
        path: Path to the doc file.

    Returns:
        Priority score (higher is better).
    """
    name = Path(path).name.lower()
    if name.startswith("readme"):
        return 100
    if name.startswith("contributing"):
        return 100
    if (
        "getting_started" in path.lower()
        or "quickstart" in path.lower()
        or "install" in name
        or "setup" in name
    ):
        return 90
    if "admin" in path.lower():
        return 40
    return 50
