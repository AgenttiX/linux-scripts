"""Test KDE scripts"""

import configparser
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tests.utils import REPO_PATH

FIX_WOBBLY_WINDOWS = REPO_PATH / "kde" / "fix-wobbly-windows.sh"

@unittest.skipIf(
    shutil.which("kwriteconfig6") is None and shutil.which("kwriteconfig5") is None,
    "kwriteconfig is not installed",
)
class FixWobblyWindowsTestCase(unittest.TestCase):
    @staticmethod
    def _run(kwinrc: pathlib.Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["sh", str(FIX_WOBBLY_WINDOWS)],
            capture_output=True,
            check=True,
            env={**os.environ, "KWINRC": str(kwinrc)},
            text=True,
        )

    @staticmethod
    def _read(kwinrc: pathlib.Path) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        parser.read(kwinrc)
        return parser

    def test_writes_explicit_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            kwinrc = pathlib.Path(temp_dir) / "kwinrc"
            self._run(kwinrc)
            self.assertEqual(self._read(kwinrc)["Plugins"]["wobblywindowsenabled"], "false")

    def test_replaces_revert_to_default_marker(self):
        """The KCM writes a revert-to-default marker, which the distro default then overrides."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kwinrc = pathlib.Path(temp_dir) / "kwinrc"
            kwinrc.write_text("[Plugins]\nwobblywindowsEnabled[$d]\n")
            self._run(kwinrc)
            contents = kwinrc.read_text()
            self.assertNotIn("[$d]", contents)
            self.assertEqual(self._read(kwinrc)["Plugins"]["wobblywindowsenabled"], "false")

    def test_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            kwinrc = pathlib.Path(temp_dir) / "kwinrc"
            self._run(kwinrc)
            first = kwinrc.read_text()
            self._run(kwinrc)
            self.assertEqual(kwinrc.read_text(), first)

    def test_preserves_other_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            kwinrc = pathlib.Path(temp_dir) / "kwinrc"
            kwinrc.write_text("[Plugins]\nblurEnabled=true\n")
            self._run(kwinrc)
            plugins = self._read(kwinrc)["Plugins"]
            self.assertEqual(plugins["blurenabled"], "true")
            self.assertEqual(plugins["wobblywindowsenabled"], "false")
