from mcp_repo_onboarding.analysis import analyze_repo
# Note: These imports will fail because we haven't written the source code yet.
# This is intentional TDD.
from mcp_repo_onboarding.schema import RepoAnalysis

def test_caps_docs_and_config(temp_repo):
    """
    Asserts that docs are capped at 10 and configs at 15.
    """
    repo_path = temp_repo("excessive-docs-configs")
    
    # This function call will fail (ImportError/NameError)
    analysis = analyze_repo(repo_path=str(repo_path))
    
    assert isinstance(analysis, RepoAnalysis)
    
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
    
    # Should find 'make test'
    test_cmds = [cmd.command for cmd in analysis.scripts.test]
    assert "make test" in test_cmds
    
    # Should NOT find internal shell commands (e.g., 'python -m pytest')
    assert "python -m pytest" not in test_cmds
