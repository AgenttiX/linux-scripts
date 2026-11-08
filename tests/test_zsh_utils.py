"""Test zsh utilities."""

import pathlib
import subprocess
import unittest

from tests.utils import UTILS_ZSH


class ZshCustomUtilsTestCase(unittest.TestCase):
    """Tests for the Zsh utility functions."""

    @staticmethod
    def _run_function(name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["zsh", "-c", f"source {UTILS_ZSH} && {name}"],
            capture_output=True,
            check=True,
            text=True,
        )

    def test_per_user_usage(self) -> None:
        """Check that the per-user resource usage has a header and the current user."""
        result = self._run_function("per-user-usage")
        lines = result.stdout.splitlines()
        assert len(lines) >= 1
        assert lines[0].split() == ["USER", "%CPU", "%MEM"]
        # The current user should always have at least one running process.
        assert pathlib.Path.home().name in result.stdout
