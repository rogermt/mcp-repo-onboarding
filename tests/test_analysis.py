from mcp_repo_onboarding.analysis import analyze_repo

def test_caps_docs_and_config(temp_repo):
    """
    Asserts that docs are capped at 10 and configs at 15.
    """
    repo_path = temp_repo("excessive-docs-configs")
    
    analysis = analyze_repo(repo_path=str(repo_path))
    
    # Check Caps
    assert len(analysis.docs) <= 10
    assert len(analysis.configurationFiles) <= 15
    
    # Check Truncation Notes
    notes_str = " ".join(analysis.notes)
    assert "docs list truncated to 10" in notes_str
    assert "configurationFiles list truncated to 15" in notes_str

    # Check Prioritization (Makefile should be kept despite truncation)
    config_names = [c.path for c in analysis.configurationFiles]
    assert "Makefile" in config_names

def test_makefile_parsing_cleanliness(temp_repo):
    """
    Asserts that we extract targets but ignore recipe internals.
    """
    repo_path = temp_repo("phase3-2-tox-nox-make")
    
    analysis = analyze_repo(repo_path=str(repo_path))
    
    test_cmds = [cmd.command for cmd in analysis.scripts.test]
    assert "make test" in test_cmds
    # Should NOT find internal shell commands inside recipes
    assert "python -m pytest" not in test_cmds

def test_shell_script_extraction(temp_repo):
    """
    Asserts that scripts/*.sh are detected and added to commands.
    """
    # This fixture should have scripts/run.sh, setup.sh, test.sh
    repo_path = temp_repo("repo-with-scripts")
    
    analysis = analyze_repo(repo_path=str(repo_path))
    
    # Check dev commands (run.sh, setup.sh)
    dev_cmds = [c.command for c in analysis.scripts.dev]
    assert "bash scripts/run.sh" in dev_cmds
    assert "bash scripts/setup.sh" in dev_cmds
    
    # Check test commands (test.sh)
    test_cmds = [c.command for c in analysis.scripts.test]
    assert "bash scripts/test.sh" in test_cmds

def test_python_env_derivation(temp_repo):
    """
    Asserts that requirements.txt triggers signal, but NOT derived commands.
    """
    # phase3-2-tox-nox-make has requirements.txt
    repo_path = temp_repo("phase3-2-tox-nox-make")
    
    analysis = analyze_repo(repo_path=str(repo_path))
    
    assert analysis.python is not None
    
    # Check Dependency Files detected
    dep_paths = [d.path for d in analysis.python.dependencyFiles]
    assert "requirements.txt" in dep_paths
    
    # Check that NO env instructions are generated (Issue #15 fix)
    assert len(analysis.python.envSetupInstructions) == 0
    
    # Check that NO derived Install Scripts are created (Issue #15 fix)
    # searxng has no Makefile 'install' target, so scripts.install should be empty
    # Wait, the fixture might have Makefile with install target? 
    # phase3-2-tox-nox-make HAS a Makefile with test/lint but NO install.
    install_cmds = [c.command for c in analysis.scripts.install]
    assert "pip install -r requirements.txt" not in install_cmds
    assert len(analysis.scripts.install) == 0

def test_config_priority_and_detection(temp_repo):
    """
    Asserts that pre-commit and specific workflows are detected and prioritized.
    """
    repo_path = temp_repo("imgix-python-config-priority")
    
    analysis = analyze_repo(repo_path=str(repo_path))
    
    config_paths = [c.path for c in analysis.configurationFiles]
    
    # Check Detection of .pre-commit-config.yaml
    assert ".pre-commit-config.yaml" in config_paths
    
    # Check Priority Sorting:
    # Makefile (100) > .pre-commit-config.yaml (70) > labeler.yml (5 - automation)
    if "Makefile" in config_paths and ".pre-commit-config.yaml" in config_paths:
        makefile_idx = config_paths.index("Makefile")
        precommit_idx = config_paths.index(".pre-commit-config.yaml")
        assert makefile_idx < precommit_idx