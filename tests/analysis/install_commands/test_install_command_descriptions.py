from __future__ import annotations

from mcp_repo_onboarding.analysis.install_commands import (
    describe_install_command,
    merge_python_install_instructions_into_scripts,
)
from mcp_repo_onboarding.schema import (
    CommandInfo,
    PythonEnvFile,
    PythonInfo,
    RepoAnalysisScriptGroup,
)


def _python_info_with_install(instr: list[str]) -> PythonInfo:
    return PythonInfo(
        packageManagers=["pip"],
        dependencyFiles=[PythonEnvFile(path="pyproject.toml", type="pyproject.toml")],
        envSetupInstructions=[],
        installInstructions=instr,
        pythonVersionHints=[],
    )


def test_describe_pip_install_variants() -> None:
    assert describe_install_command("pip install .") == "Install the project package."
    assert describe_install_command("pip install -e .") == "Install the project in editable mode."
    assert (
        describe_install_command("pip install --editable .")
        == "Install the project in editable mode."
    )
    assert (
        describe_install_command("pip install -r requirements.txt")
        == "Install dependencies from requirements.txt."
    )
    assert (
        describe_install_command("pip install --requirement requirements-dev.txt")
        == "Install dependencies from requirements-dev.txt."
    )
    assert describe_install_command("python -m pip install .") == "Install the project package."
    assert (
        describe_install_command("python3 -m pip install -e .")
        == "Install the project in editable mode."
    )
    assert describe_install_command("pip install --upgrade pip") == "Upgrade pip."
    assert (
        describe_install_command("pip install -U requests") == "Upgrade Python package(s) via pip."
    )


def test_describe_other_install_tools_future_friendly() -> None:
    assert describe_install_command("uv sync") == "Install dependencies using uv."
    assert describe_install_command("poetry install") == "Install dependencies using Poetry."
    assert describe_install_command("pdm install") == "Install dependencies using PDM."
    assert describe_install_command("pipenv install") == "Install dependencies using Pipenv."
    assert describe_install_command("make install") == "Install dependencies via Makefile target."


def test_merge_adds_described_commandinfo_and_periodizes() -> None:
    scripts = RepoAnalysisScriptGroup()
    py = _python_info_with_install(["python -m pip install ."])

    merge_python_install_instructions_into_scripts(scripts, py)

    assert len(scripts.install) == 1
    assert scripts.install[0].command == "python -m pip install ."
    assert scripts.install[0].description == "Install the project package."
    assert scripts.install[0].source == "python.installInstructions"


def test_merge_does_not_add_when_make_install_already_present() -> None:
    scripts = RepoAnalysisScriptGroup()
    scripts.install.append(
        CommandInfo(command="make install", source="Makefile:install", description="Install deps.")
    )

    py = _python_info_with_install(["pip install .", "pip install -r requirements.txt"])
    merge_python_install_instructions_into_scripts(scripts, py)

    assert [c.command for c in scripts.install] == ["make install"]


def test_merge_caps_pip_install_r_to_one() -> None:
    scripts = RepoAnalysisScriptGroup()
    py = _python_info_with_install(
        ["pip install -r requirements.txt", "pip install -r requirements-dev.txt"]
    )

    merge_python_install_instructions_into_scripts(scripts, py)

    cmds = [c.command for c in scripts.install]
    assert sum("pip install -r" in c for c in cmds) == 1
