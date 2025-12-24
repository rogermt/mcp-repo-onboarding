"""
Configuration constants for the repository analysis module.
"""

# Maximum number of documentation files to include in the analysis report
MAX_DOCS_CAP = 10

# Maximum number of configuration files to include in the analysis report
MAX_CONFIG_CAP = 15

# Default maximum number of files to scan if not specified
DEFAULT_MAX_FILES = 5000

# Patterns to always ignore for safety and noise reduction
SAFETY_IGNORES = [
    ".git/",
    ".venv/",
    "venv/",
    "env/",
    "__pycache__/",
    "node_modules/",
    "site-packages/",
    "dist/",
    "build/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".coverage",
]

# Set of file names known to be configuration files
CONFIG_FILE_TYPES = {
    "makefile",
    "tox.ini",
    "noxfile.py",
    ".pre-commit-config.yaml",
    ".pre-commit-config.yml",
    "pytest.ini",
    "pytest.cfg",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
}

# Set of file names known to define dependencies
DEPENDENCY_FILE_TYPES = {
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-server.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
}
