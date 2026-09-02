"""Tests for the Zsh utilities in ./zsh/custom/utils.zsh.

The tests of the process killing spawn dummy processes of their own,
so that no real program has to be killed.
"""

import os
import pathlib
import shutil
import signal
import subprocess
import sys
import textwrap
import time
import unittest
import uuid

UTILS_ZSH = pathlib.Path(__file__).resolve().parent.parent / "zsh" / "custom" / "utils.zsh"


@unittest.skipIf(shutil.which("zsh") is None, "Zsh is not installed")
class KillUserProcessesTestCase(unittest.TestCase):
    def setUp(self):
        # The marker is part of the command line of the dummy processes,
        # which makes them findable with a pattern that can't match anything else.
        self.marker = f"kill-user-processes-test-{uuid.uuid4().hex}"

    def spawn(self) -> subprocess.Popen:
        """Start a dummy process that has the marker in its command line."""
        # The marker is passed as an argument, so that it ends up in the command line
        # that "pgrep -f" reads.
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(300)", self.marker]
        )
        self.addCleanup(self.terminate, process)
        # Wait until the process is visible to pgrep.
        for _ in range(50):
            if subprocess.run(["pgrep", "-f", self.marker], capture_output=True).returncode == 0:
                break
            time.sleep(0.1)
        else:
            self.fail("The dummy process did not start.")
        return process

    @staticmethod
    def terminate(process: subprocess.Popen):
        """Clean up a dummy process that the tested function did not kill."""
        if process.poll() is None:
            process.send_signal(signal.SIGKILL)
        process.wait()

    @staticmethod
    def run_zsh(*args: str) -> subprocess.CompletedProcess:
        script = textwrap.dedent(
            f"""\
            source {UTILS_ZSH}
            kill-user-processes {" ".join(args)}
            """
        )
        return subprocess.run(["zsh", "-f", "-c", script], capture_output=True, text=True)

    def test_no_matching_processes(self):
        """A pattern without matches must not be an error."""
        process = self.run_zsh("Dummy", f"'{self.marker}'", "--yes")
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertIn("No Dummy processes", process.stdout)

    def test_kill(self):
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'", "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(str(process.pid), result.stdout)
        self.assertIsNotNone(process.poll(), "The dummy process was not killed.")

    def test_dry_run(self):
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'", "--dry-run")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(str(process.pid), result.stdout)
        self.assertIsNone(process.poll(), "The dry run killed the dummy process.")

    def test_no_terminal_aborts(self):
        """Without "--yes" and without a terminal to ask from, nothing may be killed."""
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'")
        self.assertEqual(1, result.returncode)
        self.assertIn("Aborted", result.stdout)
        self.assertIsNone(process.poll(), "The dummy process was killed without a confirmation.")

    def test_unknown_option(self):
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'", "--force")
        self.assertEqual(2, result.returncode)
        self.assertIn("Unknown option", result.stderr)
        self.assertIsNone(process.poll(), "An unknown option killed the dummy process.")

    def test_missing_arguments(self):
        result = self.run_zsh("Dummy")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Usage", result.stderr)

    def test_only_the_processes_of_the_current_user_are_found(self):
        """A pattern that matches every process may still list only the own processes."""
        self.spawn()
        # The dot matches the command line of every process.
        result = self.run_zsh("Dummy", "'.'", "--dry-run")
        self.assertEqual(0, result.returncode, result.stderr)

        pids = []
        for line in result.stdout.splitlines():
            fields = line.split()
            if fields and fields[0].isdigit():
                pids.append(int(fields[0]))
        self.assertTrue(pids, "No processes were found.")

        for pid in pids:
            try:
                owner = os.stat(f"/proc/{pid}").st_uid
            except FileNotFoundError:
                # The process has exited since the listing was made.
                continue
            self.assertEqual(os.getuid(), owner, f"Process {pid} belongs to another user.")


if __name__ == "__main__":
    unittest.main()
