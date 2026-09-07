"""Test zsh utilities"""

import pathlib
import subprocess
import unittest

from tests.utils import UTILS_ZSH

class ZshCustomUtilsTestCase(unittest.TestCase):
    @staticmethod
    def _run_function(name: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["zsh", "-c", f"source {UTILS_ZSH} && {name}"],
            capture_output=True,
            check=True,
            text=True,
        )

    def test_per_user_usage(self):
        result = self._run_function("per-user-usage")
        lines = result.stdout.splitlines()
        self.assertGreaterEqual(len(lines), 1)
        self.assertEqual(lines[0].split(), ["USER", "%CPU", "%MEM"])
        # The current user should always have at least one running process.
        self.assertIn(pathlib.Path.home().name, result.stdout)
