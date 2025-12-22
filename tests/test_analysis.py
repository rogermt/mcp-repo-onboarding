from mcp_repo_onboarding.analysis import analyze_repo


def _notes_str(analysis) -> str:
    notes = analysis.notes or []
    return " ".join(notes)


def _paths_config(analysis) -> set[str]:
    return {c.path for c in (analysis.configurationFiles or [])}


def _paths_docs(analysis) -> set[str]:
    return {d.path for d in (analysis.docs or [])}


def _paths_deps(analysis) -> set[str]:
    if analysis.python is None or analysis.python.dependencyFiles is None:
        return set()
    return {d.path for d in (analysis.python.dependencyFiles or [])}


def _commands(group) -> list[str]:
    if not group:
        return []
    return [c.command for c in group]


def test_caps_docs_and_config(temp_repo):
    repo_path = temp_repo("excessive-docs-configs")
    analysis = analyze_repo(repo_path=str(repo_path))

    assert len(analysis.docs) <= 10
    assert len(analysis.configurationFiles) <= 15

    ns = _notes_str(analysis)
    assert "docs list truncated to 10 entries" in ns
    assert "configurationFiles list truncated to 15 entries" in ns

    config_paths = [c.path for c in analysis.configurationFiles]
    assert "Makefile" in config_paths


def test_makefile_targets_only_no_recipe_internals(temp_repo):
    repo_path = temp_repo("makefile-with-recipes")
    analysis = analyze_repo(repo_path=str(repo_path))

    test_cmds = _commands(analysis.scripts.test)
    assert "make test" in test_cmds

    joined = "\n".join(test_cmds)
    assert "$(" not in joined
    assert "\\n" not in joined
    assert "utils/" not in joined
    assert "container/" not in joined


def test_shell_script_extraction_and_description(temp_repo):
    repo_path = temp_repo("repo-with-scripts")
    # Overwrite the file to ensure a safe description exists for the base test
    (repo_path / "scripts" / "run.sh").write_text(
        "#!/bin/bash\n# Safe description.\necho 'running'"
    )
    (repo_path / "scripts" / "setup.sh").write_text(
        "#!/bin/bash\n# Safe description.\necho 'running'"
    )
    (repo_path / "scripts" / "test.sh").write_text(
        "#!/bin/bash\n# Safe description.\necho 'running'"
    )

    analysis = analyze_repo(repo_path=str(repo_path))

    dev_cmds = analysis.scripts.dev or []
    test_cmds = analysis.scripts.test or []

    dev_cmd_strs = [c.command for c in dev_cmds]
    test_cmd_strs = [c.command for c in test_cmds]

    assert "bash scripts/run.sh" in dev_cmd_strs
    assert "bash scripts/setup.sh" in dev_cmd_strs
    assert "bash scripts/test.sh" in test_cmd_strs

    for c in dev_cmds + test_cmds:
        assert c.description is not None
        assert isinstance(c.description, str)
        assert c.description.strip() != ""
        assert "Safe description" in c.description


def test_dependency_files_do_not_appear_in_configuration_files(temp_repo):
    repo_path = temp_repo("phase3-2-tox-nox-make")
    analysis = analyze_repo(repo_path=str(repo_path))

    deps = _paths_deps(analysis)
    configs = _paths_config(analysis)

    assert "requirements.txt" in deps
    assert "requirements.txt" not in configs

    docs = _paths_docs(analysis)

    assert deps.isdisjoint(configs)
    assert deps.isdisjoint(docs)
    assert configs.isdisjoint(docs)


def test_tox_and_tox_lint_commands_are_emitted(temp_repo):
    repo_path = temp_repo("imgix-python-tox-lint")
    analysis = analyze_repo(repo_path=str(repo_path))

    test_cmds = _commands(analysis.scripts.test)
    lint_cmds = _commands(analysis.scripts.lint)

    assert "tox" in test_cmds
    assert "tox -e flake8" in lint_cmds

    for cmd in (analysis.scripts.test or []) + (analysis.scripts.lint or []):
        assert cmd.description is not None
        assert isinstance(cmd.description, str)
        assert cmd.description.strip() != ""


def test_weak_pytest_repo_does_not_emit_pytest_command(temp_repo):
    repo_path = temp_repo("repo-with-weak-pytest")
    analysis = analyze_repo(repo_path=str(repo_path))

    all_cmds = []
    for grp in [
        analysis.scripts.dev,
        analysis.scripts.start,
        analysis.scripts.test,
        analysis.scripts.lint,
        analysis.scripts.format,
        analysis.scripts.other,
    ]:
        if grp:
            all_cmds.extend([c.command for c in grp])

    assert "pytest" not in all_cmds


def test_site_packages_never_leaks_into_output(temp_repo):
    repo_path = temp_repo("repo-with-site-packages")
    analysis = analyze_repo(repo_path=str(repo_path))

    for p in _paths_docs(analysis):
        assert "site-packages" not in p
    for p in _paths_config(analysis):
        assert "site-packages" not in p
    for p in _paths_deps(analysis):
        assert "site-packages" not in p


def test_python_pin_detected_from_workflow_env(temp_repo):
    repo_path = temp_repo("workflow-python-pin-env")
    analysis = analyze_repo(repo_path=str(repo_path))

    assert analysis.python is not None
    hints = analysis.python.pythonVersionHints or []
    assert "3.14" in hints


def test_setuptools_files_are_dependencies_not_config(temp_repo):
    repo_path = temp_repo("imgix-python-config-priority")
    analysis = analyze_repo(repo_path=str(repo_path))

    deps = _paths_deps(analysis)
    configs = _paths_config(analysis)

    assert "setup.py" in deps
    assert "setup.py" not in configs
    assert len(deps) > 0


def test_imgix_python_has_dependencies(temp_repo):
    repo_path = temp_repo("imgix-python-tox-lint")
    analysis = analyze_repo(repo_path=str(repo_path))

    deps = _paths_deps(analysis)
    assert len(deps) > 0
    assert "setup.py" in deps


def test_requirements_never_in_config(temp_repo):
    repo_path = temp_repo("phase3-2-tox-nox-make")
    analysis = analyze_repo(repo_path=str(repo_path))

    configs = _paths_config(analysis)
    assert "requirements.txt" not in configs


def test_requirements_prioritized_in_deps(temp_repo):
    repo_path = temp_repo("phase3-2-tox-nox-make")
    (repo_path / "setup.py").write_text("from setuptools import setup; setup()")

    analysis = analyze_repo(repo_path=str(repo_path))

    dep_paths = [d.path for d in analysis.python.dependencyFiles]
    assert "requirements.txt" in dep_paths
    assert "setup.py" in dep_paths

    assert dep_paths[0] == "requirements.txt"


def test_env_install_instructions_separation(temp_repo):
    repo_path = temp_repo("phase3-2-tox-nox-make")

    analysis = analyze_repo(repo_path=str(repo_path))

    assert analysis.python is not None
    assert len(analysis.python.envSetupInstructions) == 0
    assert "pip install -r requirements.txt" in analysis.python.installInstructions
    assert len(analysis.python.installInstructions) > 0


def test_script_description_rejects_command_like_comments(temp_repo):
    repo_path = temp_repo("repo-with-scripts")

    # Scenario 1: Bad comment, then good comment. Should pick the good one.
    script_path = repo_path / "scripts" / "run.sh"
    script_path.write_text(
        "#!/bin/bash\n# export BAD_VAR=true\n# This is a good description.\necho 'running'"
    )

    analysis = analyze_repo(str(repo_path))
    run_cmd = next(
        (c for c in (analysis.scripts.dev or []) if c.name == "run.sh"), None
    )
    assert run_cmd is not None
    assert run_cmd.description == "This is a good description."

    # Scenario 2: Only bad comments. Should use fallback.
    script_path_2 = repo_path / "scripts" / "setup.sh"
    script_path_2.write_text(
        "#!/bin/bash\n# export BAD_VAR=true\n# FOO=bar\necho 'running'"
    )

    analysis = analyze_repo(str(repo_path))
    setup_cmd = next(
        (c for c in (analysis.scripts.dev or []) if c.name == "setup.sh"), None
    )
    assert setup_cmd is not None
    assert setup_cmd.description == "Run repo script entrypoint."


def test_script_description_rejects_decorative_comments(temp_repo):
    repo_path = temp_repo("repo-with-scripts")

    # Scenario 1: Decorative comment, then good comment. Should pick the good one.
    script_path = repo_path / "scripts" / "run.sh"
    script_path.write_text(
        "#!/bin/bash\n# -------- CONFIG --------\n# This is a good description.\necho 'running'"
    )

    analysis = analyze_repo(str(repo_path))
    run_cmd = next(
        (c for c in (analysis.scripts.dev or []) if c.name == "run.sh"), None
    )
    assert run_cmd is not None
    assert run_cmd.description == "This is a good description."

    # Scenario 2: Only decorative comments. Should use fallback.
    script_path_2 = repo_path / "scripts" / "setup.sh"
    script_path_2.write_text(
        "#!/bin/bash\n# -------- CONFIG --------\n# ====================\necho 'running'"
    )

    analysis = analyze_repo(str(repo_path))
    setup_cmd = next(
        (c for c in (analysis.scripts.dev or []) if c.name == "setup.sh"), None
    )
    assert setup_cmd is not None
    assert setup_cmd.description == "Run repo script entrypoint."


def test_script_description_header_only_scan(temp_repo):
    repo_path = temp_repo("repo-with-scripts")

    # Scenario 1: Good comment in header, bad comment after code.
    script_path = repo_path / "scripts" / "test.sh"  # Using test.sh for this new test
    script_path.write_text("""#!/bin/bash
# This is the real description in the header.
set -e
# This comment is after code has started and should be ignored.
echo "running tests"
""")

    analysis = analyze_repo(str(repo_path))
    test_cmd = next(
        (c for c in (analysis.scripts.test or []) if c.name == "test.sh"), None
    )
    assert test_cmd is not None
    assert test_cmd.description == "This is the real description in the header."

    # Scenario 2: Only a decorative comment in the header, then code, then another comment.
    # Should fall back to default and ignore the comment after the code.
    script_path.write_text("""#!/bin/bash
# -------- IGNORE ME --------
set -e
# This comment should also be ignored.
echo "running tests"
""")
    analysis = analyze_repo(str(repo_path))
    test_cmd = next(
        (c for c in (analysis.scripts.test or []) if c.name == "test.sh"), None
    )
    assert test_cmd is not None
    assert test_cmd.description == "Run repo script entrypoint."
