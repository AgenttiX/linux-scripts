"""Utility methods for scripts.

Import this as ``from utils import misc_utils``.
Scripts outside the repository root have to add the repository directory to the beginning of ``sys.path`` first,
so that this package is not shadowed by other packages named ``utils``.
Only the Python standard library is used, as this is also run with the system Python as root.
"""

from collections.abc import Sequence
import getpass
import logging
import os
import pwd
import subprocess as sp
import threading
import typing as tp

logger: logging.Logger = logging.getLogger(__name__)


class MountInfo:
    """Information about the filesystem mount that contains a given path."""

    def __init__(self, path: str) -> None:
        """Get the mount information with findmnt.

        :param path: path within the mount
        """
        line = run(["findmnt", "--target", path], get_output=True, print_output=False)[1][1]
        data = line.split()
        self.mountpoint: str = data[0]
        self.partition: str = data[1]
        self.partition_type: str = data[2]
        options = data[3].split(",")
        self.options: dict[str, str | bool] = {}
        for opt in options:
            if "=" in opt:
                split = opt.split("=")
                self.options[split[0]] = split[1]
            else:
                self.options[opt] = True

    @property
    def device(self) -> str:
        """Name of the parent block device of the mounted partition."""
        return run(["lsblk", "-no", "pkname", self.partition], get_output=True, print_output=False)[1][0]


class DiskInfo:
    """Information about a block device."""

    def __init__(self, device: str) -> None:
        """Create a disk info object.

        :param device: device name with or without the "/dev/" prefix
        """
        self.device: str = device.removeprefix("/dev/")

    @property
    def model(self) -> str:
        """Model name of the device."""
        with open(f"/sys/block/{self.device}/device/model") as file:
            return file.read().rstrip()

    @property
    def vendor(self) -> str:
        """Vendor name of the device."""
        with open(f"/sys/block/{self.device}/device/vendor") as file:
            return file.read().rstrip()

    def lsblk(self) -> None:
        """Print the device information with lsblk."""
        run(["lsblk", f"/dev/{self.device}"])

    def print(self) -> None:
        """Print the vendor and model of the device."""
        text = f"Vendor: {self.vendor}, model: {self.model}"
        print_info(text)


def alert_if_root(fail: bool = False) -> None:
    """Warn if the script is run as root.

    :param fail: whether to raise an error instead of only warning
    :raises RuntimeError: if run as root and fail is True
    """
    if os.geteuid() == 0:
        text = "Warning! This script should not be run as root for security reasons!"
        if fail:
            logger.error(text)
            raise RuntimeError(text)
        print(text)
        logger.warning(text)


def alert_if_not_root(fail: bool = True) -> None:
    """Warn if the script is not run as root.

    :param fail: whether to raise an error instead of only warning
    :raises PermissionError: if not run as root and fail is True
    """
    if os.geteuid() != 0:
        text = "This script should be run as root."
        if fail:
            logger.error(text)
            raise PermissionError(text)
        print(text)
        logger.warning(text)


def get_user() -> str:
    """Get the name of the user that executed this process, even if sudo was used.

    Based on https://unix.stackexchange.com/a/626389/
    """
    try:
        return os.getlogin()
    except OSError:
        # Some Ubuntu installations and systemd services don't support os.getlogin()
        pass

    if "USER" not in os.environ:
        # Possibly a systemd service, but no sudo was used.
        return getpass.getuser()
    user = os.environ["USER"]

    if user == "root":
        if "SUDO_USER" in os.environ:
            return os.environ["SUDO_USER"]

        if "PKEXEC_UID" in os.environ:
            pkexec_uid = int(os.environ["PKEXEC_UID"])
            return pwd.getpwuid(pkexec_uid).pw_name

    return user


def is_virtual() -> bool:
    """Check whether the system is a virtual machine."""
    with open("/proc/cpuinfo") as file:
        return "hypervisor" in file.read()


def print_info(text: str) -> None:
    """Print the text and log it at the info level."""
    print(text)
    logger.info(text)


@tp.overload
def run(
        command: list[str],
        *,
        check: bool = True,
        get_output: tp.Literal[False] = False,
        print_output: bool = True,
        stderr: bool = True,
        sudo: bool = False) -> int: ...


@tp.overload
def run(
        command: list[str],
        *,
        check: bool = True,
        get_output: tp.Literal[True],
        print_output: bool = True,
        stderr: bool = True,
        sudo: bool = False) -> tuple[int, list[str]]: ...


def run(  # noqa: PLR0913
        command: list[str],
        *,
        check: bool = True,
        get_output: bool = False,
        print_output: bool = True,
        stderr: bool = True,
        sudo: bool = False) -> int | tuple[int, list[str]]:
    """Run an external command as a subprocess.

    :param command: command and its arguments
    :param check: whether to check the return code and raise an error accordingly
    :param get_output: whether to extract output to Python
    :param print_output: print command output to console
    :param stderr: whether to capture stderr output as well
    :param sudo: run the command as sudo if not already root
    :return: return code of the command, and the output lines if get_output is True
    :raises CalledProcessError: if check is True and the command fails
    """
    logger.info("Running %s", command)
    if sudo and os.geteuid() != 0:
        command = ["sudo", *command]
    # Setting bufsize=1 would result in
    # RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE if stderr else None)
    if process.stdout is None:
        raise RuntimeError("Failed to capture the output of the process.")
    output: list[str] = []
    lock = threading.Lock()

    def handle_stream(stream: tp.IO[bytes], is_stderr: bool) -> None:
        with stream:
            for raw_line in stream:
                line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                if not line:
                    continue
                with lock:
                    if is_stderr:
                        logger.error(line)
                    else:
                        logger.info(line)
                    if get_output:
                        output.append(line)
                    if print_output:
                        print(line)

    # The streams have to be read concurrently.
    # Otherwise the process could block on writing to a full pipe, while this process waits for the other pipe.
    stderr_thread: threading.Thread | None = None
    if process.stderr is not None:
        stderr_thread = threading.Thread(target=handle_stream, args=(process.stderr, True), daemon=True)
        stderr_thread.start()
    handle_stream(process.stdout, is_stderr=False)
    if stderr_thread is not None:
        stderr_thread.join()
    return_code = process.wait()
    if check and return_code:
        raise sp.CalledProcessError(return_code, command)
    if get_output:
        return return_code, output
    return return_code


def run_interactive(command: Sequence[str], check: bool = True, sudo: bool = False) -> int:
    """Run a command so that it uses the terminal directly.

    The output is not logged, but the command can prompt the user, and its output is shown without delays.

    :param command: command and its arguments
    :param check: whether to check the return code and raise an error accordingly
    :param sudo: run the command as sudo if not already root
    :return: return code of the command
    :raises CalledProcessError: if check is True and the command fails
    """
    command = list(command)
    if sudo and os.geteuid() != 0:
        command = ["sudo", *command]
    logger.info("Running interactively %s", command)
    return_code = sp.run(command, check=check).returncode
    logger.info("Return code: %s", return_code)
    return return_code


def yes_or_no() -> bool:
    """Ask the user a yes/no question.

    :return: whether the user answered yes
    """
    return choice(["y", "n"]) == "y"


def choice(choices: list[str]) -> str:
    """Ask the user to select one of the given choices.

    :param choices: the allowed answers in lower case
    :return: the selected choice
    """
    while True:
        reply = input(f"({'/'.join(choices)})").lower().strip()
        if reply in choices:
            return reply
        print("Invalid answer. Did you make a typo?")
