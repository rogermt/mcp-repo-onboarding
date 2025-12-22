# This test file is for the unit tests of the MetadataDescriber strategies.

from mcp_repo_onboarding.describers import MakefileDescriber
from mcp_repo_onboarding.schema import ConfigFileInfo

def test_makefile_describer():
    """
    Tests the MakefileDescriber strategy.
    This test will FAIL until the describers are implemented.
    """
    describer = MakefileDescriber()
    mock_file = ConfigFileInfo(path="Makefile", type="makefile")
    described_file = describer.describe(mock_file)
    assert described_file.description == "Primary task runner for development and build orchestration."
