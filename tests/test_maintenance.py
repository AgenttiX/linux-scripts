"""Tests for ./maintenance/."""

import pathlib
import tempfile
import unittest
from unittest import mock

import pytest

from git import pull
from maintenance import __main__ as maintenance_main
from maintenance import bleachbit, cleanup, common, disks, sudo


class BleachbitTestCase(unittest.TestCase):
    """Tests for the BleachBit command."""

    def test_command_default(self) -> None:
        """Check that only the default cleaners are used by default."""
        command = bleachbit.bleachbit_command(deep=False, firefox=False, thunderbird=False, root=False)
        assert command == ["bleachbit", "--clean", *bleachbit.BLEACHBIT_FEATURES]

    def test_command_all(self) -> None:
        """Check that all the optional cleaners are added when requested."""
        command = bleachbit.bleachbit_command(deep=True, firefox=True, thunderbird=True, root=True)
        for feature in (
                *bleachbit.BLEACHBIT_DEEP, *bleachbit.BLEACHBIT_FIREFOX,
                *bleachbit.BLEACHBIT_ROOT, *bleachbit.BLEACHBIT_THUNDERBIRD):
            assert feature in command


class CleanupTestCase(unittest.TestCase):
    """Tests for the cleanup steps."""

    def test_remove_custom_files(self) -> None:
        """Check that only the listed regular files are removed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            home = pathlib.Path(temp_dir)
            target = home / "target"
            target.write_text("keep")
            (home / cleanup.CUSTOM_HOME_FILES[0]).write_text("remove")
            (home / cleanup.CUSTOM_HOME_FILES[1]).symlink_to(target)
            (home / "other").write_text("keep")
            cleanup.remove_custom_files(home)
            remaining = sorted(path.name for path in home.iterdir())
            assert remaining == sorted([cleanup.CUSTOM_HOME_FILES[1], "other", "target"])


class CommonTestCase(unittest.TestCase):
    """Tests for the shared code."""

    def test_run_steps(self) -> None:
        """Check that the steps are run in order."""
        calls: list[int] = []
        common.run_steps([lambda: calls.append(1), lambda: calls.append(2)])
        assert calls == [1, 2]


class MainTestCase(unittest.TestCase):
    """Tests for the user part."""

    def test_git_pull(self) -> None:
        """Check that the repository is pulled and that a failed pull stops the script."""
        for returncode in (0, 1):
            result = pull.PullResult(common.REPO_DIR, returncode, "output\n")
            with mock.patch.object(pull, "pull", return_value=result) as pull_mock, mock.patch("builtins.print"):
                if returncode:
                    with pytest.raises(SystemExit):
                        maintenance_main.git_pull()
                else:
                    maintenance_main.git_pull()
            pull_mock.assert_called_once_with(common.REPO_DIR)

    def test_sudo_command(self) -> None:
        """Check that the relevant arguments are passed to the root part."""
        args = maintenance_main.parse_args(["--deep", "--firefox", "--reboot", "--no-pull"])
        command = maintenance_main.sudo_command(args, zerofree=True)
        assert command[:3] == ["sudo", common.SYSTEM_PYTHON, str(common.PACKAGE_DIR / "sudo.py")]
        assert command[3:] == ["--deep", "--firefox", "--reboot", "--zerofree"]
        # The root part must accept all the arguments.
        sudo_args = sudo.parse_args(command[3:])
        assert sudo_args.deep
        assert sudo_args.reboot
        assert sudo_args.zerofree

    def test_reboot_and_shutdown(self) -> None:
        """Check that reboot and shutdown cannot be selected simultaneously."""
        with pytest.raises(SystemExit), mock.patch("sys.stderr"):
            maintenance_main.parse_args(["--reboot", "--shutdown"])


class ZerofreeTestCase(unittest.TestCase):
    """Tests for deciding whether to zero free disk space."""

    def test_not_requested_physical(self) -> None:
        """Check that physical machines are not zeroed by default and the user is not asked."""
        with mock.patch.object(disks, "is_virtual", return_value=False), \
                mock.patch.object(disks, "yes_or_no") as yes_or_no:
            assert not disks.should_zero_free_space(requested=False)
            yes_or_no.assert_not_called()

    def test_requested_virtual(self) -> None:
        """Check that virtual machines are zeroed without asking when requested."""
        with mock.patch.object(disks, "is_virtual", return_value=True), \
                mock.patch.object(disks, "yes_or_no") as yes_or_no, mock.patch("builtins.print"):
            assert disks.should_zero_free_space(requested=True)
            yes_or_no.assert_not_called()

    def test_not_requested_virtual_asks(self) -> None:
        """Check that the user is asked whether to zero a virtual machine."""
        with mock.patch.object(disks, "is_virtual", return_value=True), \
                mock.patch.object(disks, "yes_or_no", return_value=False), mock.patch("builtins.print"):
            assert not disks.should_zero_free_space(requested=False)
