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
        self.safety_ignores = [p.rstrip("/") for p in safety_ignores]

        self._pathspec: pathspec.PathSpec | None
        if gitignore_patterns:
            self._pathspec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, gitignore_patterns
            )
        else:
            self._pathspec = None

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

            for si in self.safety_ignores:
                if f"/{si}/" in f"/{rel_path_str}":
                    return True
                if rel_path_str.startswith(f"{si}/") or rel_path_str == si:
                    return True

            if self._pathspec:
                return self._pathspec.match_file(rel_path_str)

            return False
        except (ValueError, OSError):
            return False

    def should_descend(self, dir_path: Path) -> bool:
        """
        Check if the scanner should descend into a directory.

        Args:
            dir_path: The directory path.

        Returns:
            True if the directory should be entered, False if ignored.
        """
        return not self.should_ignore(dir_path, is_dir=True)
