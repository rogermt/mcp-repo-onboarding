from pathlib import Path
from mcp_repo_onboarding.analysis import IgnoreMatcher

# Pure Unit Tests - No Filesystem Access

def test_safety_ignores_only():
    """Test that safety ignores work without any gitignore patterns."""
    repo_root = Path("/tmp/repo")
    matcher = IgnoreMatcher(
        repo_root=repo_root,
        safety_ignores=[".git/", ".venv/", "build/"],
        gitignore_patterns=[]
    )
    
    # Should be ignored (Safety)
    assert matcher.should_ignore(repo_root / ".git")
    assert matcher.should_ignore(repo_root / ".venv/lib.py")
    assert matcher.should_ignore(repo_root / "build/output.txt")
    
    # Should be included
    assert not matcher.should_ignore(repo_root / "src/main.py")
    assert not matcher.should_ignore(repo_root / "README.md")

def test_gitignore_patterns():
    """Test that gitignore patterns are respected."""
    repo_root = Path("/tmp/repo")
    matcher = IgnoreMatcher(
        repo_root=repo_root,
        safety_ignores=[],
        gitignore_patterns=[
            "*.log",
            "temp/",
            "!temp/keep.txt"
        ]
    )
    
    # Ignored by pattern
    assert matcher.should_ignore(repo_root / "error.log")
    assert matcher.should_ignore(repo_root / "temp/trash.tmp")
    
    # Whitelisted
    assert not matcher.should_ignore(repo_root / "temp/keep.txt")
    
    # Included
    assert not matcher.should_ignore(repo_root / "src/app.py")

def test_safety_overrides_gitignore_whitelist():
    """Test that safety ignores cannot be overridden by gitignore whitelist."""
    repo_root = Path("/tmp/repo")
    matcher = IgnoreMatcher(
        repo_root=repo_root,
        safety_ignores=[".venv/"],
        gitignore_patterns=["!.venv/"]
    )
    
    # Safety wins
    assert matcher.should_ignore(repo_root / ".venv")
    assert matcher.should_ignore(repo_root / ".venv/bin/python")

def test_should_descend_optimization():
    """Test should_descend returns False for ignored directories."""
    repo_root = Path("/tmp/repo")
    matcher = IgnoreMatcher(
        repo_root=repo_root,
        safety_ignores=["node_modules/"],
        gitignore_patterns=["dist/"]
    )
    
    assert not matcher.should_descend(repo_root / "node_modules")
    assert not matcher.should_descend(repo_root / "dist")
    assert matcher.should_descend(repo_root / "src")