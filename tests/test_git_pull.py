"""Tests for ./git/pull.py

The tests use local repositories, so that no network connection is needed.
"""

import contextlib
import importlib.util
import io
import pathlib
import subprocess
import tempfile
import unittest

from tests.utils import REPO_PATH

SPEC = importlib.util.spec_from_file_location("git_pull", REPO_PATH / "git" / "pull.py")
git_pull = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(git_pull)


def git(*args: str, cwd: pathlib.Path) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=cwd, check=True, capture_output=True,
    )


class GitPullTestCase(unittest.TestCase):
    def setUp(self) -> None:
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
        self._tmp.cleanup()

    def test_find_repos(self):
        repos = git_pull.find_repos([self.root, self.tmp / "nonexistent"])
        self.assertEqual([repo.name for repo in repos], ["a-repo", "b-repo"])

    def test_find_repos_deduplicates(self):
        link = self.tmp / "git"
        link.symlink_to(self.root)
        repos = git_pull.find_repos([self.root, link])
        self.assertEqual(len(repos), 2)

    def test_pull_all(self):
        (self.upstream / "file.txt").write_text("2\n")
        git("commit", "-am", "Update", cwd=self.upstream)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            returncode = git_pull.main(["-j", "2", str(self.root)])
        self.assertEqual(returncode, 0)
        for name in ("a-repo", "b-repo"):
            self.assertEqual((self.root / name / "file.txt").read_text(), "2\n")
        output = stdout.getvalue()
        # The outputs must be in order.
        self.assertLess(output.index("a-repo"), output.index("b-repo"))
        self.assertIn("2/2", output)

    def test_diverged_repo_fails(self):
        (self.upstream / "file.txt").write_text("2\n")
        git("commit", "-am", "Upstream", cwd=self.upstream)
        repo = self.root / "a-repo"
        (repo / "file.txt").write_text("3\n")
        git("commit", "-am", "Local", cwd=repo)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            returncode = git_pull.main([str(self.root)])
        self.assertEqual(returncode, 1)
        self.assertIn("1/2", stdout.getvalue())
        # The local commit must not have been merged or rebased.
        self.assertEqual((repo / "file.txt").read_text(), "3\n")


if __name__ == "__main__":
    unittest.main()
