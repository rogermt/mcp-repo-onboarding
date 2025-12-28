from abc import ABC, abstractmethod
from typing import Any

from .schema import CommandInfo, ConfigFileInfo, PythonEnvFile


# Base Class for the Strategy Pattern
class MetadataDescriber(ABC):
    """Abstract base class for a metadata description strategy."""

    @abstractmethod
    def describe(self, target: Any) -> Any:
        """
        Enrich the target object with a description.

        Args:
            target: The object to describe (CommandInfo, ConfigFileInfo, etc.).

        Returns:
            The modified object with the description field populated.
        """
        pass


# --- Concrete Strategy Implementations ---


# Configuration File Describers
class MakefileDescriber(MetadataDescriber):
    """Describer for Makefiles."""

    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        """Add description for Makefile."""
        target.description = "Primary task runner for development and build orchestration."
        return target


class GitHubWorkflowDescriber(MetadataDescriber):
    """Describer for GitHub Actions workflows."""

    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        """Add description for GitHub workflow files."""
        target.description = "CI/CD automation workflow."
        return target


class ToxIniDescriber(MetadataDescriber):
    """Describer for tox.ini files."""

    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        """Add description for tox.ini."""
        target.description = "Test environment orchestrator (tox)."
        return target


class NoxfileDescriber(MetadataDescriber):
    """Describer for noxfile.py."""

    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        """Add description for noxfile.py."""
        target.description = "Test automation sessions (nox)."
        return target


class PreCommitDescriber(MetadataDescriber):
    """Describer for .pre-commit-config.yaml."""

    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        """Add description for pre-commit config."""
        target.description = "Pre-commit hooks configuration (code quality automation)."
        return target


class SetuptoolsDescriber(MetadataDescriber):
    """Describer for setuptools configuration files."""

    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        """Add description for setup.py/cfg."""
        target.description = "Packaging/build configuration (setuptools)."
        return target


# Dependency File Describers
class RequirementsTxtDescriber(MetadataDescriber):
    """Describer for requirements.txt files."""

    def describe(self, target: PythonEnvFile) -> PythonEnvFile:
        """Add description for requirements.txt."""
        target.description = "Python dependency manifest."
        return target


class PyprojectTomlDescriber(MetadataDescriber):
    """Describer for pyproject.toml."""

    def describe(self, target: PythonEnvFile) -> PythonEnvFile:
        """Add description for pyproject.toml."""
        target.description = "Project configuration and dependency management (PEP 518/621)."
        return target


# Command Describers
class MakeTestDescriber(MetadataDescriber):
    """Describer for 'make test' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        """Add description for make test command."""
        target.description = "Run the test suite via Makefile target."
        return target


class MakeFormatDescriber(MetadataDescriber):
    """Describer for 'make format' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        """Add description for make format command."""
        target.description = "Run formatting via Makefile target."
        return target


class MakeRunDescriber(MetadataDescriber):
    """Describer for 'make run' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        """Add description for make run command."""
        target.description = "Run the application via Makefile target."
        return target


class MakeInstallDescriber(MetadataDescriber):
    """Describer for 'make install' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Install dependencies via Makefile target."
        return target


class MakeLintDescriber(MetadataDescriber):
    """Describer for 'make lint' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run linting via Makefile target."
        return target


class ToxDescriber(MetadataDescriber):
    """Describer for 'tox' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        """Add description for tox command."""
        target.description = "Run tests via tox."
        return target


class ToxEnvDescriber(MetadataDescriber):
    """Describer for 'tox -e' command."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        """Add description for tox environment command."""
        target.description = "Run specific tox environment."
        return target


class BashScriptDescriber(MetadataDescriber):
    """Describer for bash scripts."""

    def describe(self, target: CommandInfo) -> CommandInfo:
        """Add description for bash script."""
        target.description = "Run repo script entrypoint."
        return target


# --- Central Registry ---

# Using filename/command string as keys for the lookup
FILE_DESCRIBER_REGISTRY: dict[str, MetadataDescriber] = {
    "makefile": MakefileDescriber(),
    "tox.ini": ToxIniDescriber(),
    "noxfile.py": NoxfileDescriber(),
    ".pre-commit-config.yaml": PreCommitDescriber(),
    "setup.py": SetuptoolsDescriber(),
    "setup.cfg": SetuptoolsDescriber(),
    ".github/workflows": GitHubWorkflowDescriber(),
    "requirements.txt": RequirementsTxtDescriber(),
    "pyproject.toml": PyprojectTomlDescriber(),
}

COMMAND_DESCRIBER_REGISTRY: dict[str, MetadataDescriber] = {
    "make test": MakeTestDescriber(),
    "make format": MakeFormatDescriber(),
    "make run": MakeRunDescriber(),
    "make install": MakeInstallDescriber(),
    "make lint": MakeLintDescriber(),
    "tox": ToxDescriber(),
    "tox -e": ToxEnvDescriber(),  # Prefix for tox environments
    "bash scripts/": BashScriptDescriber(),  # Prefix for shell scripts
}
