"""Tests for ./pycharm/configure_pycharm.py."""

import os
import pathlib
import re
import stat
import subprocess
import sys
import tempfile
import types
import unittest

from tests.utils import REPO_PATH, load_module

SCRIPT = REPO_PATH / "pycharm" / "configure_pycharm.py"
configure_pycharm: types.ModuleType = load_module("configure_pycharm", SCRIPT)


class ConfigurePycharmFunctionsTestCase(unittest.TestCase):
    """Tests for the PyCharm configuration helper functions."""

    def test_heap_size(self) -> None:
        """Check that the heap is half of the RAM, rounded down to a power of two and capped."""
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
                assert configure_pycharm.heap_size_mib(mem_bytes) == expected

    def test_indexer_threads(self) -> None:
        """Check that the indexer gets half of the CPUs, at least one and capped."""
        for cpu_count, expected in ((1, 1), (3, 1), (14, 7), (32, 16), (64, 16)):
            with self.subTest(cpu_count=cpu_count):
                assert configure_pycharm.indexer_threads(cpu_count) == expected

    def test_set_option(self) -> None:
        """Check that an option replaces all its previous values or is appended."""
        assert configure_pycharm.set_option(["-Xmx1m", "-Da=1", "-Xmx2m"], "-Xmx", "4m") == ["-Xmx4m", "-Da=1"]
        assert configure_pycharm.set_option(["-Da=1"], "-Xmx", "4m") == ["-Da=1", "-Xmx4m"]


class ConfigurePycharmScriptTestCase(unittest.TestCase):
    """Tests for running the PyCharm configuration script in a fake home directory."""

    home: pathlib.Path
    jetbrains: pathlib.Path

    def setUp(self) -> None:
        """Create a temporary home directory."""
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = pathlib.Path(self._tmp.name)
        self.jetbrains = self.home / ".config" / "JetBrains"

    def _config_dir(self, name: str) -> pathlib.Path:
        path = self.jetbrains / name
        path.mkdir(parents=True)
        return path

    def _run_script(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            check=False,
            env={"HOME": str(self.home), "PATH": os.environ["PATH"]},
            text=True,
        )

    def test_no_config_dir(self) -> None:
        """Check that a missing config directory is an error."""
        result = self._run_script()
        assert result.returncode == 1
        assert "No PyCharm config directory" in result.stderr

    def test_only_latest_version_is_updated(self) -> None:
        """Check that only the newest PyCharm version is configured."""
        old = self._config_dir("PyCharm2025.3")
        previous = self._config_dir("PyCharm2026.9")
        latest = self._config_dir("PyCharm2026.10")
        self._config_dir("PyCharm2026.10-backup")
        self._config_dir("RustRover2027.1")

        assert self._run_script().returncode == 0

        assert list(old.iterdir()) == []
        assert list(previous.iterdir()) == []
        assert (latest / "pycharm64.vmoptions").is_file()
        assert list((self.jetbrains / "PyCharm2026.10-backup").iterdir()) == []

    def test_options_are_replaced_and_others_kept(self) -> None:
        """Check that the managed options are replaced in place and the file mode is kept."""
        vmoptions = self._config_dir("PyCharm2026.3") / "pycharm64.vmoptions"
        vmoptions.write_text(
            "-Xmx2048m\n-Dide.managed.by.toolbox=\n-Dcaches.indexerThreadsCount=99\n-Xmx4096m\n-Dlast.line=1"
        )
        vmoptions.chmod(0o640)

        assert self._run_script().returncode == 0

        lines = vmoptions.read_text().splitlines()
        assert lines[1] == "-Dide.managed.by.toolbox="
        assert lines[3] == "-Dlast.line=1"
        assert len(lines) == 4
        assert re.search(r"^-Xmx\d+m$", lines[0])
        heap_mib = int(lines[0][4:-1])
        assert heap_mib & heap_mib - 1 == 0
        assert heap_mib <= 16384
        assert re.search(r"^-Dcaches\.indexerThreadsCount=\d+$", lines[2])
        assert stat.S_IMODE(vmoptions.stat().st_mode) == 416

    def test_is_idempotent(self) -> None:
        """Check that a second run changes nothing and leaves no backup files."""
        vmoptions = self._config_dir("PyCharm2026.3") / "pycharm64.vmoptions"

        assert self._run_script().returncode == 0
        first = vmoptions.read_text()
        result = self._run_script()

        assert result.returncode == 0
        assert "already up to date" in result.stdout
        assert vmoptions.read_text() == first
        assert [path.name for path in vmoptions.parent.iterdir()] == ["pycharm64.vmoptions"]

    def test_symlink_is_kept(self) -> None:
        """Check that a symlinked vmoptions file is edited through the link."""
        target = self.home / "pycharm64.vmoptions"
        target.write_text("-Xmx2048m\n")
        vmoptions = self._config_dir("PyCharm2026.3") / "pycharm64.vmoptions"
        vmoptions.symlink_to(target)

        assert self._run_script().returncode == 0

        assert vmoptions.is_symlink()
        assert "-Dcaches.indexerThreadsCount=" in target.read_text()
