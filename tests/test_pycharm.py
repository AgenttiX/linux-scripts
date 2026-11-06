"""Tests for ./pycharm/configure_pycharm.py"""

import importlib.util
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

from tests.utils import REPO_PATH

SCRIPT = REPO_PATH / "pycharm" / "configure_pycharm.py"
SPEC = importlib.util.spec_from_file_location("configure_pycharm", SCRIPT)
configure_pycharm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(configure_pycharm)


class ConfigurePycharmFunctionsTestCase(unittest.TestCase):
    def test_heap_size(self):
        gib = 1024 ** 3
        for mem_bytes, expected in (
            (2 * gib, 1024),
            (8 * gib, 4096),
            # Exactly half of the RAM is allowed.
            (16 * gib, 8192),
            # A 32 GB system reports slightly less than 32 GiB of total memory.
            (33131143168, 8192),
            (32 * gib, 16384),
            (188 * gib, 16384),
        ):
            with self.subTest(mem_bytes=mem_bytes):
                self.assertEqual(configure_pycharm.heap_size_mib(mem_bytes), expected)

    def test_indexer_threads(self):
        for cpu_count, expected in ((1, 1), (3, 1), (14, 7), (32, 16), (64, 16)):
            with self.subTest(cpu_count=cpu_count):
                self.assertEqual(configure_pycharm.indexer_threads(cpu_count), expected)

    def test_set_option(self):
        self.assertEqual(
            configure_pycharm.set_option(["-Xmx1m", "-Da=1", "-Xmx2m"], "-Xmx", "4m"),
            ["-Xmx4m", "-Da=1"],
        )
        self.assertEqual(configure_pycharm.set_option(["-Da=1"], "-Xmx", "4m"), ["-Da=1", "-Xmx4m"])


class ConfigurePycharmScriptTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = pathlib.Path(self._tmp.name)
        self.jetbrains = self.home / ".config" / "JetBrains"

    def _config_dir(self, name: str) -> pathlib.Path:
        path = self.jetbrains / name
        path.mkdir(parents=True)
        return path

    def _run_script(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            env={"HOME": str(self.home), "PATH": os.environ["PATH"]},
            text=True,
        )

    def test_no_config_dir(self):
        result = self._run_script()
        self.assertEqual(result.returncode, 1)
        self.assertIn("No PyCharm config directory", result.stderr)

    def test_only_latest_version_is_updated(self):
        old = self._config_dir("PyCharm2025.3")
        previous = self._config_dir("PyCharm2026.9")
        latest = self._config_dir("PyCharm2026.10")
        self._config_dir("PyCharm2026.10-backup")
        self._config_dir("RustRover2027.1")

        self.assertEqual(self._run_script().returncode, 0)

        self.assertEqual(list(old.iterdir()), [])
        self.assertEqual(list(previous.iterdir()), [])
        self.assertTrue((latest / "pycharm64.vmoptions").is_file())
        self.assertEqual(list((self.jetbrains / "PyCharm2026.10-backup").iterdir()), [])

    def test_options_are_replaced_and_others_kept(self):
        vmoptions = self._config_dir("PyCharm2026.3") / "pycharm64.vmoptions"
        vmoptions.write_text(
            "-Xmx2048m\n-Dide.managed.by.toolbox=\n-Dcaches.indexerThreadsCount=99\n-Xmx4096m\n-Dlast.line=1"
        )
        vmoptions.chmod(0o640)

        self.assertEqual(self._run_script().returncode, 0)

        lines = vmoptions.read_text().splitlines()
        self.assertEqual(lines[1], "-Dide.managed.by.toolbox=")
        self.assertEqual(lines[3], "-Dlast.line=1")
        self.assertEqual(len(lines), 4)
        self.assertRegex(lines[0], r"^-Xmx\d+m$")
        heap_mib = int(lines[0][4:-1])
        self.assertEqual(heap_mib & (heap_mib - 1), 0)
        self.assertLessEqual(heap_mib, 16384)
        self.assertRegex(lines[2], r"^-Dcaches\.indexerThreadsCount=\d+$")
        self.assertEqual(stat.S_IMODE(vmoptions.stat().st_mode), 0o640)

    def test_is_idempotent(self):
        vmoptions = self._config_dir("PyCharm2026.3") / "pycharm64.vmoptions"

        self.assertEqual(self._run_script().returncode, 0)
        first = vmoptions.read_text()
        result = self._run_script()

        self.assertEqual(result.returncode, 0)
        self.assertIn("already up to date", result.stdout)
        self.assertEqual(vmoptions.read_text(), first)
        self.assertEqual([path.name for path in vmoptions.parent.iterdir()], ["pycharm64.vmoptions"])

    def test_symlink_is_kept(self):
        target = self.home / "pycharm64.vmoptions"
        target.write_text("-Xmx2048m\n")
        vmoptions = self._config_dir("PyCharm2026.3") / "pycharm64.vmoptions"
        vmoptions.symlink_to(target)

        self.assertEqual(self._run_script().returncode, 0)

        self.assertTrue(vmoptions.is_symlink())
        self.assertIn("-Dcaches.indexerThreadsCount=", target.read_text())
