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
    "tests/fixtures/",
    "test/fixtures/",
    ".git/",
    ".hg/",
    ".svn/",
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

# Configuration files — NO overlap with DEPENDENCY_FILE_TYPES per §2
# NOTE: pyproject.toml, setup.py, setup.cfg are classified as DEPS, not configs
CONFIG_FILE_TYPES = {
    "makefile",
    "tox.ini",
    "noxfile.py",
    ".pre-commit-config.yaml",
    ".pre-commit-config.yml",
    "pytest.ini",
    "pytest.cfg",
}

# Dependency files — canonical list per EXTRACT_OUTPUT_RULES.md §2
DEPENDENCY_FILE_TYPES = {
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-server.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "pipfile",
    "environment.yml",
    "environment.yaml",
}
# Extensions to exclude from documentation entirely
DOC_EXCLUDED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".mp4",
    ".mov",
    ".mp3",
    ".css",
    ".js",
    ".map",
}

# Extensions considered "human documentation" under docs/ directory
DOC_HUMAN_EXTENSIONS = {
    ".md",
    ".rst",
    ".txt",
    ".adoc",
}

# Mapping of tool keys and build backend identifiers to package manager names
KNOWN_PACKAGE_MANAGERS = {
    "poetry": "poetry",
    "hatch": "hatch",
    "pdm": "pdm",
    "flit": "flit",
}
