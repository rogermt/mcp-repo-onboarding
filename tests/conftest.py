import pytest
import shutil
import tempfile
from pathlib import Path

@pytest.fixture
def fixtures_root():
    """Returns the path to the static fixtures directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def temp_repo(fixtures_root):
    """
    Factory fixture.
    Usage: repo_path = temp_repo("fixture_name")
    Returns a Path object to a temporary copy of the fixture.
    """
    created_dirs = []

    def _create_temp_repo(fixture_name):
        source = fixtures_root / fixture_name
        if not source.exists():
            raise FileNotFoundError(f"Fixture {fixture_name} not found at {source}")
        
        # Create a temp dir
        temp_dir = tempfile.mkdtemp(prefix="mcp-test-")
        created_dirs.append(temp_dir)
        
        # Copy fixture content into temp dir
        shutil.copytree(source, temp_dir, dirs_exist_ok=True)
        
        return Path(temp_dir)

    yield _create_temp_repo

    # Cleanup
    for d in created_dirs:
        shutil.rmtree(d, ignore_errors=True)
