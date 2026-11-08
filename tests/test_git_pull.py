"""Tests for ./git/pull.py.

The tests use local repositories, so that no network connection is needed.
"""

import contextlib
import io
import pathlib
import subprocess
import tempfile
import types
import unittest

from tests.utils import REPO_PATH, load_module

git_pull: types.ModuleType = load_module("git_pull", REPO_PATH / "git" / "pull.py")


def git(*args: str, cwd: pathlib.Path) -> None:
    """Run a Git command with a test identity.

    :param args: arguments for git
    :param cwd: directory to run the command in
    """
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=cwd, check=True, capture_output=True,
    )


class GitPullTestCase(unittest.TestCase):
    """Tests for pulling all the repositories in a directory."""

    root: pathlib.Path
    tmp: pathlib.Path
    upstream: pathlib.Path

    def setUp(self) -> None:
        """Create an upstream repository and a directory with two clones and a non-repository."""
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.upstream = self.tmp / "upstream"
        self.upstream.mkdir()
        git("init", "-b", "main", cwd=self.upstream)
        (self.upstream / "file.txt").write_text("1\n")
        git("add", "file.txt", cwd=self.upstream)
        git("commit", "-m", "Initial", cwd=self.upstream)

        self.root = self.tmp / "Git"
        self.root.mkdir()
        for name in ("b-repo", "a-repo"):
            git("clone", str(self.upstream), name, cwd=self.root)
        (self.root / "not-a-repo").mkdir()

    def tearDown(self) -> None:
        """Remove the temporary repositories."""
        self._tmp.cleanup()

    def test_find_repos(self) -> None:
        """Check that only Git repositories are found, sorted by name, and missing roots are skipped."""
        repos = git_pull.find_repos([self.root, self.tmp / "nonexistent"])
        assert [repo.name for repo in repos] == ["a-repo", "b-repo"]

    def test_find_repos_deduplicates(self) -> None:
        """Check that a root reached through a symlink does not list its repositories twice."""
        link = self.tmp / "git"
        link.symlink_to(self.root)
        repos = git_pull.find_repos([self.root, link])
        assert len(repos) == 2

    def test_pull_all(self) -> None:
        """Check that all repositories are updated and their outputs are printed in order."""
        (self.upstream / "file.txt").write_text("2\n")
        git("commit", "-am", "Update", cwd=self.upstream)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            returncode = git_pull.main(["-j", "2", str(self.root)])
        assert returncode == 0
        for name in ("a-repo", "b-repo"):
            assert (self.root / name / "file.txt").read_text() == "2\n"
        output = stdout.getvalue()
        # The outputs must be in order.
        assert output.index("a-repo") < output.index("b-repo")
        assert "2/2" in output

    def test_diverged_repo_fails(self) -> None:
        """Check that a diverged repository fails the run and its local commit is kept."""
        (self.upstream / "file.txt").write_text("2\n")
        git("commit", "-am", "Upstream", cwd=self.upstream)
        repo = self.root / "a-repo"
        (repo / "file.txt").write_text("3\n")
        git("commit", "-am", "Local", cwd=repo)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            returncode = git_pull.main([str(self.root)])
        assert returncode == 1
        assert "1/2" in stdout.getvalue()
        # The local commit must not have been merged or rebased.
        assert (repo / "file.txt").read_text() == "3\n"


if __name__ == "__main__":
    unittest.main()
