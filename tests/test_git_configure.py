"""Tests for ./git/configure.py.

The tests use temporary directories instead of the real ``~/.config/git`` and ``./git``.
"""

import contextlib
import io
import pathlib
import sys
import tempfile
import types
import unittest

import pytest

from tests.utils import REPO_PATH, load_module

git_configure: types.ModuleType = load_module("git_configure", REPO_PATH / "git" / "configure.py")


def can_create_file_symlinks(tmp: pathlib.Path) -> bool:
    """Check whether file symbolic links can be created, which on Windows requires privileges.

    :param tmp: temporary directory for the check
    :return: whether symbolic links can be created
    """
    link = tmp / "symlink-check"
    try:
        link.symlink_to(tmp / "nonexistent")
    except OSError:
        return False
    link.unlink()
    return True


class GitConfigureTestCase(unittest.TestCase):
    """Tests for linking the Git config directory and installing the private config."""

    config_dir: pathlib.Path
    private: pathlib.Path
    shared: pathlib.Path
    tmp: pathlib.Path

    def setUp(self) -> None:
        """Create a shared config directory and a private config in a temporary directory."""
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.shared = self.tmp / "linux-scripts" / "git"
        self.shared.mkdir(parents=True)
        (self.shared / "config").write_text("[include]\n    path = ~/.config/git/config_private\n")
        self.private = self.tmp / "private-scripts" / "git" / "config_work"
        self.private.parent.mkdir(parents=True)
        self.private.write_text("[user]\n    name = Test\n")
        self.config_dir = self.tmp / "home" / ".config" / "git"

    def tearDown(self) -> None:
        """Remove the temporary directories, without following the links."""
        if git_configure.is_link(self.config_dir):
            git_configure.remove_link(self.config_dir)
        self._tmp.cleanup()

    def link(self) -> pathlib.Path | None:
        """Link the config directory to the shared directory without printing.

        :return: path of the backup, if one was created
        """
        with contextlib.redirect_stdout(io.StringIO()):
            return git_configure.link_config_dir(self.config_dir, self.shared)

    def test_link_config_dir(self) -> None:
        """Check that the config directory is linked and that relinking is a no-op."""
        assert self.link() is None
        assert git_configure.is_link(self.config_dir)
        assert self.config_dir.resolve() == self.shared.resolve()
        assert (self.config_dir / "config").is_file()
        assert self.link() is None
        assert self.config_dir.resolve() == self.shared.resolve()

    def test_link_config_dir_backs_up_existing_dir(self) -> None:
        """Check that an existing config directory is moved to a backup with its contents."""
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "ignore").write_text("*.swp\n")
        backup = self.link()
        assert backup is not None
        assert (backup / "ignore").read_text() == "*.swp\n"
        assert self.config_dir.resolve() == self.shared.resolve()

    def test_link_config_dir_replaces_other_link(self) -> None:
        """Check that a link elsewhere is replaced without touching its old target."""
        other = self.tmp / "other"
        other.mkdir()
        (other / "config").write_text("old\n")
        self.config_dir.parent.mkdir(parents=True)
        git_configure.create_dir_link(self.config_dir, other)
        assert self.link() is None
        assert self.config_dir.resolve() == self.shared.resolve()
        assert (other / "config").read_text() == "old\n"

    def test_copy_private_config(self) -> None:
        """Check that the private config is copied, and that a rerun updates the copy."""
        dest = git_configure.install_private_config(self.private, self.shared, copy=True)
        assert dest == self.shared / git_configure.PRIVATE_CONFIG_NAME
        assert not dest.is_symlink()
        assert dest.read_text() == self.private.read_text()
        self.private.write_text("[user]\n    name = Changed\n")
        git_configure.install_private_config(self.private, self.shared, copy=True)
        assert dest.read_text() == "[user]\n    name = Changed\n"

    def test_copy_does_not_write_through_old_link(self) -> None:
        """Check that copying over an old link replaces the link instead of overwriting its target."""
        if not can_create_file_symlinks(self.tmp):
            self.skipTest("Creating symbolic links is not permitted.")
        old_target = self.tmp / "old_private"
        old_target.write_text("old\n")
        (self.shared / git_configure.PRIVATE_CONFIG_NAME).symlink_to(old_target)
        dest = git_configure.install_private_config(self.private, self.shared, copy=True)
        assert not dest.is_symlink()
        assert old_target.read_text() == "old\n"

    def test_link_private_config(self) -> None:
        """Check that the private config is linked with an absolute path."""
        if not can_create_file_symlinks(self.tmp):
            self.skipTest("Creating symbolic links is not permitted.")
        dest = git_configure.install_private_config(self.private, self.shared, copy=False)
        assert dest.is_symlink()
        assert dest.readlink().is_absolute()
        assert dest.resolve() == self.private.resolve()

    def test_private_config_errors(self) -> None:
        """Check that a missing private config and the installed file itself are rejected."""
        with pytest.raises(FileNotFoundError):
            git_configure.install_private_config(self.tmp / "missing", self.shared, copy=True)
        dest = git_configure.install_private_config(self.private, self.shared, copy=True)
        with pytest.raises(ValueError, match="must be outside"):
            git_configure.install_private_config(dest, self.shared, copy=True)

    def test_main_missing_private_config(self) -> None:
        """Check that a missing private config fails before anything is changed."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            assert git_configure.main([str(self.tmp / "missing")]) == 1
        assert "does not exist" in stderr.getvalue()

    @unittest.skipUnless(sys.platform == "win32", "Directory junctions exist only on Windows.")
    def test_junction_on_windows(self) -> None:
        """Check that a directory junction is used on Windows."""
        self.link()
        assert self.config_dir.is_junction()
        assert not self.config_dir.is_symlink()


if __name__ == "__main__":
    unittest.main()
