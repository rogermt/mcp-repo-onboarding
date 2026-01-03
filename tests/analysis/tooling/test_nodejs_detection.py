"""Tests for Node.js detection (Issue #12)."""

from __future__ import annotations

from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo
from mcp_repo_onboarding.analysis.tooling import detect_other_tooling


class TestNodeJsDetection:
    """Node.js-specific detection tests."""

    def test_nvmrc_triggers_detection(self) -> None:
        """.nvmrc alone triggers Node.js detection."""
        files = [".nvmrc"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"
        assert ".nvmrc" in result[0].evidence_files

    def test_node_version_triggers_detection(self) -> None:
        """.node-version triggers Node.js detection."""
        files = [".node-version"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"

    def test_package_json_triggers_detection(self) -> None:
        """package.json triggers Node.js detection."""
        files = ["package.json"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"

    def test_yarn_lock_triggers_detection(self) -> None:
        """yarn.lock triggers Node.js detection."""
        files = ["yarn.lock"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"

    def test_pnpm_lock_triggers_detection(self) -> None:
        """pnpm-lock.yaml triggers Node.js detection."""
        files = ["pnpm-lock.yaml"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"

    def test_package_lock_triggers_detection(self) -> None:
        """package-lock.json triggers Node.js detection."""
        files = ["package-lock.json"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"

    def test_npmrc_triggers_detection(self) -> None:
        """.npmrc triggers Node.js detection."""
        files = [".npmrc"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"

    def test_multiple_node_evidence_combined(self) -> None:
        """Multiple Node.js files result in single detection with all evidence."""
        files = ["package.json", "yarn.lock", ".nvmrc"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        node = result[0]
        assert node.name == "Node.js"
        assert len(node.evidence_files) == 3
        assert "package.json" in node.evidence_files
        assert "yarn.lock" in node.evidence_files
        assert ".nvmrc" in node.evidence_files

    def test_nested_package_json_detected(self) -> None:
        """package.json in subdirectory is detected."""
        files = ["frontend/package.json"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"
        assert "frontend/package.json" in result[0].evidence_files

    def test_note_is_neutral(self) -> None:
        """Node.js note contains no commands."""
        files = ["package.json"]
        result = detect_other_tooling(files)

        note = result[0].note
        assert note is not None
        assert "npm install" not in note.lower()
        assert "yarn" not in note.lower()
        assert "pnpm" not in note.lower()
        assert "npx" not in note.lower()


class TestNodeJsIntegration:
    """Integration tests for Node.js detection in analyze_repo."""

    def test_python_node_mixed_repo(self, tmp_path: Path) -> None:
        """Mixed Python + Node.js repo detects both."""
        repo = tmp_path / "repo"
        repo.mkdir()

        # Python files
        (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0.0.0'\n")
        (repo / "src").mkdir()
        (repo / "src" / "main.py").write_text("print('hello')")

        # Node.js files
        (repo / "package.json").write_text('{"name": "frontend", "version": "1.0.0"}')
        (repo / ".nvmrc").write_text("18.17.0")

        result = analyze_repo(str(repo))

        # Should have Python detected
        assert result.python is not None

        # Should have Node.js in otherTooling
        assert len(result.otherTooling) == 1
        assert result.otherTooling[0].name == "Node.js"
        assert "package.json" in result.otherTooling[0].evidenceFiles
        assert ".nvmrc" in result.otherTooling[0].evidenceFiles

    def test_monorepo_with_frontend(self, tmp_path: Path) -> None:
        """Monorepo with frontend/ subdirectory."""
        repo = tmp_path / "repo"
        repo.mkdir()

        # Python backend
        (repo / "pyproject.toml").write_text("[project]\nname='backend'\n")
        (repo / "backend").mkdir()
        (repo / "backend" / "app.py").write_text("print('backend')")

        # Node.js frontend
        (repo / "frontend").mkdir()
        (repo / "frontend" / "package.json").write_text('{"name": "frontend"}')

        result = analyze_repo(str(repo))

        assert len(result.otherTooling) == 1
        assert result.otherTooling[0].name == "Node.js"

    def test_nvmrc_only_repo(self, tmp_path: Path) -> None:
        """Repo with only .nvmrc (no package.json)."""
        repo = tmp_path / "repo"
        repo.mkdir()

        (repo / "pyproject.toml").write_text("[project]\nname='x'\n")
        (repo / ".nvmrc").write_text("20.0.0")

        result = analyze_repo(str(repo))

        # Should still detect Node.js
        assert len(result.otherTooling) == 1
        assert result.otherTooling[0].name == "Node.js"
        assert ".nvmrc" in result.otherTooling[0].evidenceFiles


class TestNodeJsBlueprint:
    """Tests for Node.js in blueprint output."""

    def test_blueprint_includes_other_tooling_section(self, tmp_path: Path) -> None:
        """Blueprint includes other tooling section when Node.js detected."""
        from mcp_repo_onboarding.analysis import analyze_repo
        from mcp_repo_onboarding.analysis.onboarding_blueprint import (
            build_context,
            compile_blueprint,
        )

        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "pyproject.toml").write_text("[project]\nname='x'\n")
        (repo / "package.json").write_text('{"name": "x"}')

        analysis = analyze_repo(str(repo))
        ctx = build_context(analysis.model_dump(), {})
        blueprint = compile_blueprint(ctx)

        md = blueprint["render"]["markdown"]

        assert "## Other tooling detected" in md
        assert "Node.js" in md
        assert "package.json" in md

    def test_blueprint_excludes_section_for_pure_python(self, tmp_path: Path) -> None:
        """Blueprint excludes other tooling section for pure Python repo."""
        from mcp_repo_onboarding.analysis import analyze_repo
        from mcp_repo_onboarding.analysis.onboarding_blueprint import (
            build_context,
            compile_blueprint,
        )

        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "pyproject.toml").write_text("[project]\nname='x'\n")

        analysis = analyze_repo(str(repo))
        ctx = build_context(analysis.model_dump(), {})
        blueprint = compile_blueprint(ctx)

        md = blueprint["render"]["markdown"]

        assert "## Other tooling detected" not in md
