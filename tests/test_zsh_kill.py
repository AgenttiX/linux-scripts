"""Tests for zsh process killer.

The tests of the process killing spawn dummy processes of their own,
so that no real program has to be killed.
"""

import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
import unittest
import uuid

from tests.utils import UTILS_ZSH


@unittest.skipIf(shutil.which("zsh") is None, "Zsh is not installed")
class KillUserProcessesTestCase(unittest.TestCase):
    """Tests for the "kill-user-processes" Zsh function."""

    marker: str

    def setUp(self) -> None:
        """Create a unique marker for the dummy processes."""
        # The marker is part of the command line of the dummy processes,
        # which makes them findable with a pattern that can't match anything else.
        self.marker = f"kill-user-processes-test-{uuid.uuid4().hex}"

    def spawn(self) -> subprocess.Popen[bytes]:
        """Start a dummy process that has the marker in its command line."""
        # The marker is passed as an argument, so that it ends up in the command line
        # that "pgrep -f" reads.
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(300)", self.marker]
        )
        self.addCleanup(self.terminate, process)
        # Wait until the process is visible to pgrep.
        for _ in range(50):
            if subprocess.run(["pgrep", "-f", self.marker], capture_output=True, check=False).returncode == 0:
                break
            time.sleep(0.1)
        else:
            self.fail("The dummy process did not start.")
        return process

    @staticmethod
    def terminate(process: subprocess.Popen[bytes]) -> None:
        """Clean up a dummy process that the tested function did not kill."""
        if process.poll() is None:
            process.send_signal(signal.SIGKILL)
        process.wait()

    @staticmethod
    def run_zsh(*args: str) -> subprocess.CompletedProcess[str]:
        """Run "kill-user-processes" with the given arguments.

        :param args: arguments for the function
        :return: the completed process
        """
        script = textwrap.dedent(
            f"""\
            source {UTILS_ZSH}
            kill-user-processes {" ".join(args)}
            """
        )
        return subprocess.run(["zsh", "-f", "-c", script], capture_output=True, check=False, text=True)

    def test_no_matching_processes(self) -> None:
        """A pattern without matches must not be an error."""
        process = self.run_zsh("Dummy", f"'{self.marker}'", "--yes")
        assert process.returncode == 0, process.stderr
        assert "No Dummy processes" in process.stdout

    def test_kill(self) -> None:
        """Check that a matching process is listed and killed."""
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'", "--yes")
        assert result.returncode == 0, result.stderr
        assert str(process.pid) in result.stdout
        assert process.poll() is not None, "The dummy process was not killed."

    def test_dry_run(self) -> None:
        """Check that a dry run lists a matching process without killing it."""
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'", "--dry-run")
        assert result.returncode == 0, result.stderr
        assert str(process.pid) in result.stdout
        assert process.poll() is None, "The dry run killed the dummy process."

    def test_no_terminal_aborts(self) -> None:
        """Without "--yes" and without a terminal to ask from, nothing may be killed."""
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'")
        assert result.returncode == 1
        assert "Aborted" in result.stdout
        assert process.poll() is None, "The dummy process was killed without a confirmation."

    def test_unknown_option(self) -> None:
        """Check that an unknown option is an error and kills nothing."""
        process = self.spawn()
        result = self.run_zsh("Dummy", f"'{self.marker}'", "--force")
        assert result.returncode == 2
        assert "Unknown option" in result.stderr
        assert process.poll() is None, "An unknown option killed the dummy process."

    def test_missing_arguments(self) -> None:
        """Check that missing arguments print the usage."""
        result = self.run_zsh("Dummy")
        assert result.returncode != 0
        assert "Usage" in result.stderr

    def test_only_the_processes_of_the_current_user_are_found(self) -> None:
        """A pattern that matches every process may still list only the own processes."""
        self.spawn()
        # The dot matches the command line of every process.
        result = self.run_zsh("Dummy", "'.'", "--dry-run")
        assert result.returncode == 0, result.stderr

        pids = []
        for line in result.stdout.splitlines():
            fields = line.split()
            if fields and fields[0].isdigit():
                pids.append(int(fields[0]))
        assert pids, "No processes were found."

        for pid in pids:
            try:
                owner = os.stat(f"/proc/{pid}").st_uid
            except FileNotFoundError:
                # The process has exited since the listing was made.
                continue
            assert os.getuid() == owner, f"Process {pid} belongs to another user."


if __name__ == "__main__":
    unittest.main()
