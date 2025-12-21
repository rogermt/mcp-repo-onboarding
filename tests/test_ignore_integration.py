from pathlib import Path
from mcp_repo_onboarding.analysis import analyze_repo

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ignore_handling"

def flatten_files(analysis):
    """Helper to get a set of all file paths found in analysis."""
    files = set()
    for doc in analysis.docs:
        files.add(doc.path)
    for config in analysis.configurationFiles:
        files.add(config.path)
    if analysis.python:
        for dep in analysis.python.dependencyFiles:
            files.add(dep.path)
    return files

def test_integration_repo_basic_gitignore():
    """
    Test that analyze_repo respects .gitignore.
    Currently expected to FAIL because analyze_repo ignores .gitignore.
    
    Fixture:
    - .gitignore has: build/, .env
    - file: .env (should be ignored)
    - file: build/out.txt (should be ignored)
    """
    repo_root = FIXTURES_DIR / "repo_basic_gitignore"
    analysis = analyze_repo(str(repo_root))
    
    found_files = flatten_files(analysis)
    
    # These should be ignored by .gitignore
    assert ".env" not in found_files
    # Note: build/ is in SKIP_DIRS currently, so build/out.txt might be ignored by hardcoded logic, 
    # but .env is NOT in SKIP_DIRS.

def test_integration_repo_nested_ignores():
    """
    Test nested ignore patterns in .gitignore.
    
    Fixture:
    - .gitignore has: docs/_build/
    - file: docs/_build/html/index.html (should be ignored)
    """
    repo_root = FIXTURES_DIR / "repo_nested_ignores"
    analysis = analyze_repo(str(repo_root))
    
    found_files = flatten_files(analysis)
    
    # docs/_build/ is NOT in SKIP_DIRS, so currently this will be found
    # expecting failure here
    assert "docs/_build/html/index.html" not in found_files
    assert "docs/index.md" in found_files
