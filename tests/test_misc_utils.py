"""Tests for ./utils/misc_utils.py."""

import subprocess
import sys
import unittest

import pytest

from utils import misc_utils as utils


class UtilsTestCase(unittest.TestCase):
    """Smoke tests for the miscellaneous utilities."""

    @staticmethod
    def test_print_info() -> None:
        """Check that printing info does not fail."""
        utils.print_info("test")

    @staticmethod
    def test_run() -> None:
        """Check that running a command does not fail."""
        utils.run(["echo", "test"])

    def test_run_check(self) -> None:
        """Check that a failing command raises an error only when checked."""
        with pytest.raises(subprocess.CalledProcessError):
            utils.run(["false"])
        assert utils.run(["false"], check=False) == 1

    def test_run_interactive(self) -> None:
        """Check that running a command interactively returns its return code."""
        assert utils.run_interactive(["true"]) == 0
        assert utils.run_interactive(["false"], check=False) == 1

    def test_run_large_output(self) -> None:
        """Check that a command with more output than fits in a pipe buffer does not deadlock."""
        script = "import sys\nfor i in range(20000): print('x' * 20)\nprint('err', file=sys.stderr)"
        ret, output = utils.run(
            [sys.executable, "-c", script], get_output=True, print_output=False)
        assert ret == 0
        assert len(output) == 20001
        assert "err" in output

    def test_run_output(self) -> None:
        """Check that the output of a command is captured."""
        ret, output = utils.run(["echo", "test"], get_output=True, print_output=False)
        assert ret == 0
        assert output == ["test"]
