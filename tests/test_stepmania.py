"""Test StepMania installer"""

import os
import pathlib
import socket
import subprocess
import tempfile
import unittest

from tests.utils import REPO_PATH

INSTALL_STEPMANIA = REPO_PATH / "games" / "stepmania" / "install_stepmania.sh"

# Fake executables that are placed first in PATH
FAKE_SUDO = "#!/bin/sh\nexit 0\n"
FAKE_CURL = """#!/bin/sh
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--output" ]; then
    echo "tampered" > "$2"
  fi
  shift
done
"""
FAKE_STEPMANIA = """#!/bin/sh
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}"
echo "PWD=$(pwd)"
echo "ARGS=$*"
"""


def _has_network() -> bool:
    try:
        with socket.create_connection(("archive.ubuntu.com", 443), timeout=5):
            return True
    except OSError:
        return False


class StepManiaInstallerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp_path = pathlib.Path(self._tmp.name)
        self.bin_dir = tmp_path / "bin"
        self.bin_dir.mkdir()
        self._write_executable(self.bin_dir / "sudo", FAKE_SUDO)
        self.game_dir = tmp_path / "stepmania-5.0"
        self.game_dir.mkdir()
        self._write_executable(self.game_dir / "stepmania", FAKE_STEPMANIA)

    def tearDown(self):
        self._tmp.cleanup()

    @staticmethod
    def _write_executable(path: pathlib.Path, content: str) -> None:
        path.write_text(content)
        path.chmod(0o755)

    def _run_installer(self, game_dir: pathlib.Path) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}:{env['PATH']}"
        return subprocess.run(
            ["bash", str(INSTALL_STEPMANIA), str(game_dir)],
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )

    def test_missing_executable(self):
        result = self._run_installer(self.game_dir / "nonexistent")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("StepMania executable was not found", result.stdout)

    def test_checksum_mismatch(self):
        self._write_executable(self.bin_dir / "curl", FAKE_CURL)
        result = self._run_installer(self.game_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.game_dir / "lib" / "libpcre.so.3").exists())
        self.assertFalse((self.game_dir / "stepmania.sh").exists())

    @unittest.skipUnless(_has_network(), "No network connection to archive.ubuntu.com")
    def test_install(self):
        result = self._run_installer(self.game_dir)
        self.assertEqual(result.returncode, 0, result.stderr)

        pcre = self.game_dir / "lib" / "libpcre.so.3"
        self.assertTrue(pcre.is_file())
        self.assertFalse(pcre.is_symlink())
        self.assertEqual(pcre.read_bytes()[:4], b"\x7fELF")
        libva = self.game_dir / "lib" / "libva.so.1"
        self.assertTrue(libva.is_symlink())
        self.assertEqual(os.readlink(libva), "/lib/x86_64-linux-gnu/libva.so.2")

        # Running the installer again should succeed.
        result = self._run_installer(self.game_dir)
        self.assertEqual(result.returncode, 0, result.stderr)

        launcher = self.game_dir / "stepmania.sh"
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "/existing"
        output = subprocess.run(
            [str(launcher), "--foo", "bar"],
            capture_output=True,
            check=True,
            cwd="/",
            env=env,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(output, [
            f"LD_LIBRARY_PATH={self.game_dir}/lib:/existing",
            f"PWD={self.game_dir}",
            "ARGS=--foo bar",
        ])
