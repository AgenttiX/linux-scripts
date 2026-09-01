"""Tests for the Zsh SSH helpers in ./zsh/custom/ssh.zsh.

The "ssh" and "ssh-add" commands are replaced with stubs, so that the tests
neither need a network connection nor an SSH server.
"""

import os
import pathlib
import shutil
import subprocess
import tempfile
import textwrap
import unittest

SSH_ZSH = pathlib.Path(__file__).resolve().parent.parent / "zsh" / "custom" / "ssh.zsh"

# The stub records its invocations in $STUB_LOG and reads its behavior from the environment:
# - STUB_CHECK_STATUS: exit status of "ssh -O check", 0 when a master connection exists
# - STUB_PROBE_STATUS: exit status of the probe session, non-zero when the master no longer responds
# - STUB_AGENT_STATUS: the "ssh-add -l" exit status that the probe session passes through
# - STUB_FORWARD_AGENT: the value that "ssh -G" reports for "forwardagent"
SSH_STUB = """\
#!/usr/bin/env bash
echo "$*" >> "${STUB_LOG}"

for arg in "$@"; do
  case "${arg}" in
    check) exit "${STUB_CHECK_STATUS:-0}" ;;
    stop|exit) exit 0 ;;
  esac
done

if [ "$1" = "-G" ]; then
  echo "forwardagent ${STUB_FORWARD_AGENT:-yes}"
  echo "hostname example.invalid"
  exit 0
fi

# The probe session. ssh passes the exit status of the remote command through,
# and uses 255 when it can't reach the server itself.
if [ "${STUB_PROBE_STATUS:-0}" -ne 0 ]; then
  exit "${STUB_PROBE_STATUS}"
fi
exit "${STUB_AGENT_STATUS:-1}"
"""


@unittest.skipIf(shutil.which("zsh") is None, "Zsh is not installed")
class SSHRefreshMasterTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = pathlib.Path(self.temp_dir.name)

        self.bin_dir = temp_path / "bin"
        self.bin_dir.mkdir()
        stub_path = self.bin_dir / "ssh"
        stub_path.write_text(SSH_STUB)
        stub_path.chmod(0o755)

        self.log_path = temp_path / "stub.log"
        self.log_path.touch()

        self.addCleanup(self.temp_dir.cleanup)

    def refresh(self, **stub_env: str) -> str:
        """Run "ssh-refresh-master" against the stub and return the commands it ran."""
        env = dict(os.environ)
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env['PATH']}"
        env["STUB_LOG"] = str(self.log_path)
        env.update(stub_env)

        script = textwrap.dedent(
            f"""\
            source {SSH_ZSH}
            ssh-refresh-master test-host
            """
        )
        process = subprocess.run(
            ["zsh", "-f", "-c", script],
            capture_output=True,
            check=True,
            env=env,
            text=True,
        )
        self.assertEqual("", process.stderr)
        return self.log_path.read_text()

    def test_no_master_connection(self):
        """Without a master connection there is nothing to probe or to close."""
        commands = self.refresh(STUB_CHECK_STATUS="1")
        self.assertIn("-O check", commands)
        self.assertNotIn("-O stop", commands)

    def test_healthy_master_connection(self):
        """A responding master connection with a working agent must be kept."""
        commands = self.refresh(STUB_AGENT_STATUS="0")
        self.assertNotIn("-O stop", commands)

    def test_healthy_master_connection_without_keys(self):
        """An agent that is reachable but has no keys loaded exits with 1, which is not a failure."""
        commands = self.refresh(STUB_AGENT_STATUS="1")
        self.assertNotIn("-O stop", commands)

    def test_master_connection_without_ssh_add(self):
        """Servers that don't have "ssh-add" installed exit with 127, which is not a failure either."""
        commands = self.refresh(STUB_AGENT_STATUS="127")
        self.assertNotIn("-O stop", commands)

    def test_unresponsive_master_connection(self):
        """This is the case after the client computer has been suspended."""
        commands = self.refresh(STUB_PROBE_STATUS="255")
        self.assertIn("-O stop", commands)

    def test_broken_agent_forwarding(self):
        """A forwarded agent socket that can't be reached makes "ssh-add -l" exit with 2."""
        commands = self.refresh(STUB_AGENT_STATUS="2")
        self.assertIn("-O stop", commands)

    def test_broken_agent_forwarding_without_forward_agent(self):
        """Without agent forwarding there is no forwarded agent to check.

        The master connection must therefore not be closed because of a missing agent.
        """
        commands = self.refresh(STUB_AGENT_STATUS="2", STUB_FORWARD_AGENT="no")
        self.assertNotIn("-O stop", commands)

    def test_probe_does_not_reserve_an_x11_display(self):
        """The probe must not take the display number that the actual session should get.

        It must not run the tmux RemoteCommand either.
        """
        commands = self.refresh()
        self.assertIn("-o ForwardX11=no", commands)
        self.assertIn("-o RemoteCommand=none", commands)


if __name__ == "__main__":
    unittest.main()
