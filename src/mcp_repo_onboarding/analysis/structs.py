from pathlib import Path

import pathspec


class IgnoreMatcher:
    """Matches paths against a set of ignore patterns."""

    def __init__(
        self,
        repo_root: Path,
        safety_ignores: list[str],
        gitignore_patterns: list[str],
    ) -> None:
        """
        Initialize the IgnoreMatcher.

        Args:
            repo_root: The root directory of the repository.
            safety_ignores: List of patterns to always ignore for safety.
            gitignore_patterns: List of patterns from .gitignore.
        """
        self.repo_root = repo_root.resolve()
        self.safety_ignores = list(safety_ignores)

        self._pathspec: pathspec.PathSpec | None
        if gitignore_patterns:
            self._pathspec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, gitignore_patterns
            )
        else:
            self._pathspec = None

    def is_safety_ignored(self, rel_path: str) -> bool:
        """
        Check if a repo-relative path is in the safety ignore list.
        Bypasses gitignore entirely.
        """
        # Normalize separators and strip leading/trailing slashes for comparison
        clean_rel_path = rel_path.replace("\\", "/").strip("/")

        for si in self.safety_ignores:
            si_clean = si.strip("/")

            if si.endswith("/"):
                # Directory match anywhere in the path (e.g. site-packages/ or tests/fixtures/)
                if f"/{si_clean}/" in f"/{clean_rel_path}/":
                    return True
            else:
                # File-like match (e.g. .coverage)
                # Matches exact name, matching as a filename at any level, or as a substring with /
                if (
                    clean_rel_path == si_clean
                    or Path(clean_rel_path).name == si_clean
                    or f"/{si_clean}" in f"/{clean_rel_path}"
                ):
                    return True

        return False

    def should_ignore(self, path: Path, is_dir: bool = False) -> bool:
        """
        Check if a path should be ignored.

        Args:
            path: The path to check.
            is_dir: Whether the path matches a directory.

        Returns:
            True if the path should be ignored, False otherwise.
        """
        try:
            resolved_path = path.resolve()
            rel_path = resolved_path.relative_to(self.repo_root)
            rel_path_str = str(rel_path.as_posix())

            if is_dir and not rel_path_str.endswith("/"):
                rel_path_str += "/"

            if self.is_safety_ignored(rel_path_str):
                return True

            if self._pathspec:
                return self._pathspec.match_file(rel_path_str)

            return False
        except (ValueError, OSError):
            # If path resolution fails or is outside the repository root, ignore it for safety.
            return True

    def should_descend(self, dir_path: Path) -> bool:
        """
        Check if the scanner should descend into a directory.

        Args:
            dir_path: The directory path.

        Returns:
            True if the directory should be entered, False if ignored.
        """
        return not self.should_ignore(dir_path, is_dir=True)
