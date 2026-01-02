"""Tests for other tooling detection (Phase 8 - #81)."""

from __future__ import annotations

from pathlib import Path

from mcp_repo_onboarding.analysis.tooling import (
    TOOLING_EVIDENCE_REGISTRY,
    ToolingDetection,
    detect_other_tooling,
)


class TestToolingRegistry:
    """Tests for tooling evidence registry."""

    def test_registry_has_node_js(self) -> None:
        """Node.js is registered for #12."""
        assert "Node.js" in TOOLING_EVIDENCE_REGISTRY
        node = TOOLING_EVIDENCE_REGISTRY["Node.js"]
        assert "package.json" in node["files"]
        assert ".nvmrc" in node["files"]

    def test_registry_has_docker(self) -> None:
        """Docker is registered."""
        assert "Docker" in TOOLING_EVIDENCE_REGISTRY
        docker = TOOLING_EVIDENCE_REGISTRY["Docker"]
        assert "Dockerfile" in docker["files"]

    def test_registry_entries_have_required_fields(self) -> None:
        """All registry entries have required structure."""
        for name, config in TOOLING_EVIDENCE_REGISTRY.items():
            assert "files" in config, f"{name} missing 'files'"
            assert isinstance(config["files"], tuple), f"{name} 'files' must be tuple"
            assert len(config["files"]) > 0, f"{name} has empty files list"


class TestDetectOtherTooling:
    """Tests for detect_other_tooling function."""

    def test_empty_file_list_returns_empty(self) -> None:
        """No files → no detections."""
        result = detect_other_tooling([])
        assert result == []

    def test_python_only_repo_returns_empty(self) -> None:
        """Pure Python repo → no other tooling."""
        files = [
            "pyproject.toml",
            "requirements.txt",
            "src/main.py",
            "tests/test_main.py",
        ]
        result = detect_other_tooling(files)
        assert result == []

    def test_detects_node_from_package_json(self) -> None:
        """package.json → Node.js detected."""
        files = ["package.json", "src/index.ts"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"
        assert "package.json" in result[0].evidence_files

    def test_detects_node_from_nvmrc(self) -> None:
        """.nvmrc → Node.js detected."""
        files = [".nvmrc"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        assert result[0].name == "Node.js"
        assert ".nvmrc" in result[0].evidence_files

    def test_detects_node_from_multiple_evidence(self) -> None:
        """Multiple Node.js evidence files."""
        files = ["package.json", "yarn.lock", ".nvmrc"]
        result = detect_other_tooling(files)

        assert len(result) == 1
        node = result[0]
        assert node.name == "Node.js"
        assert len(node.evidence_files) == 3

    def test_detects_docker(self) -> None:
        """Dockerfile → Docker detected."""
        files = ["Dockerfile", "docker-compose.yml"]
        result = detect_other_tooling(files)

        docker = next((d for d in result if d.name == "Docker"), None)
        assert docker is not None
        assert "Dockerfile" in docker.evidence_files

    def test_detects_go(self) -> None:
        """go.mod → Go detected."""
        files = ["go.mod", "main.go"]
        result = detect_other_tooling(files)

        go = next((d for d in result if d.name == "Go"), None)
        assert go is not None
        assert "go.mod" in go.evidence_files

    def test_detects_rust(self) -> None:
        """Cargo.toml → Rust detected."""
        files = ["Cargo.toml", "src/main.rs"]
        result = detect_other_tooling(files)

        rust = next((d for d in result if d.name == "Rust"), None)
        assert rust is not None
        assert "Cargo.toml" in rust.evidence_files

    def test_detects_multiple_tooling(self) -> None:
        """Mixed repo → multiple detections."""
        files = [
            "pyproject.toml",
            "package.json",
            "Dockerfile",
            "go.mod",
        ]
        result = detect_other_tooling(files)

        names = {d.name for d in result}
        assert "Node.js" in names
        assert "Docker" in names
        assert "Go" in names

    def test_results_sorted_by_name(self) -> None:
        """Results are deterministically sorted."""
        files = ["go.mod", "package.json", "Dockerfile", "Cargo.toml"]
        result = detect_other_tooling(files)

        names = [d.name for d in result]
        assert names == sorted(names)

    def test_case_insensitive_matching(self) -> None:
        """File matching is case-insensitive."""
        files = ["DOCKERFILE", "Package.JSON"]
        result = detect_other_tooling(files)

        names = {d.name for d in result}
        assert "Docker" in names
        assert "Node.js" in names

    def test_nested_files_detected(self) -> None:
        """Files in subdirectories are detected."""
        files = ["frontend/package.json", "backend/go.mod"]
        result = detect_other_tooling(files)

        names = {d.name for d in result}
        assert "Node.js" in names
        assert "Go" in names

    def test_detection_includes_note(self) -> None:
        """Detection includes neutral note."""
        files = ["package.json"]
        result = detect_other_tooling(files)

        assert result[0].note is not None
        assert "Node.js" in result[0].note
        # Note should NOT contain commands
        assert "npm install" not in result[0].note.lower()
        assert "yarn" not in result[0].note.lower()


class TestAnalyzeRepoIntegration:
    """Integration tests for tooling detection in analyze_repo."""

    def test_analyze_repo_includes_other_tooling(self, tmp_path: Path) -> None:
        """analyze_repo populates otherTooling field."""
        from mcp_repo_onboarding.analysis import analyze_repo

        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0.0.0'\n")
        (repo / "package.json").write_text('{"name": "x", "version": "1.0.0"}')

        result = analyze_repo(str(repo))

        assert hasattr(result, "otherTooling")
        assert len(result.otherTooling) == 1
        assert result.otherTooling[0].name == "Node.js"
        assert "package.json" in result.otherTooling[0].evidenceFiles

    def test_pure_python_repo_has_empty_other_tooling(self, tmp_path: Path) -> None:
        """Pure Python repo has empty otherTooling."""
        from mcp_repo_onboarding.analysis import analyze_repo

        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0.0.0'\n")
        (repo / "src").mkdir()
        (repo / "src" / "main.py").write_text("print('hello')")

        result = analyze_repo(str(repo))

        assert result.otherTooling == []

    def test_mixed_repo_detects_multiple(self, tmp_path: Path) -> None:
        """Mixed repo detects multiple tooling."""
        from mcp_repo_onboarding.analysis import analyze_repo

        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0.0.0'\n")
        (repo / "package.json").write_text('{"name": "x"}')
        (repo / "Dockerfile").write_text("FROM python:3.11")

        result = analyze_repo(str(repo))

        names = {t.name for t in result.otherTooling}
        assert "Node.js" in names
        assert "Docker" in names


class TestNoCommandsGenerated:
    """Safety tests: tooling detection must NOT generate commands."""

    def test_detection_note_has_no_commands(self) -> None:
        """Detection notes must not suggest commands."""
        command_patterns = [
            "npm install",
            "npm run",
            "yarn install",
            "yarn add",
            "pnpm install",
            "go build",
            "go run",
            "cargo build",
            "cargo run",
            "docker build",
            "docker run",
            "bundle install",
        ]

        for name, config in TOOLING_EVIDENCE_REGISTRY.items():
            note = config.get("note", "")
            for pattern in command_patterns:
                assert pattern not in note.lower(), (
                    f"{name} note contains command pattern '{pattern}'"
                )

    def test_tooling_detection_has_no_commands_field(self) -> None:
        """ToolingDetection has no 'commands' field."""
        from dataclasses import fields

        field_names = {f.name for f in fields(ToolingDetection)}

        assert "commands" not in field_names
        assert "install_command" not in field_names
        assert "run_command" not in field_names

    def test_schema_tooling_evidence_has_no_commands_field(self) -> None:
        """ToolingEvidence schema has no commands field."""
        from mcp_repo_onboarding.schema import ToolingEvidence

        field_names = set(ToolingEvidence.model_fields.keys())

        assert "commands" not in field_names
        assert "installCommand" not in field_names
        assert "runCommand" not in field_names
