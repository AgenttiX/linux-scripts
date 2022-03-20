"""
Utility methods for scripts
"""

import getpass
import typing as tp
import logging
import os
import pwd
import subprocess as sp

logger = logging.getLogger(__name__)


class MountInfo:
    def __init__(self, path: str):
        line = run(["findmnt", "--target", path], get_output=True, print_output=False)[1][1]
        data = line.split()
        self.mountpoint = data[0]
        self.partition = data[1]
        self.partition_type = data[2]
        options = data[3].split(",")
        self.options = {}
        for opt in options:
            if "=" in opt:
                split = opt.split("=")
                self.options[split[0]] = split[1]
            else:
                self.options[opt] = True

    @property
    def device(self):
        return run(["lsblk", "-no", "pkname", self.partition], get_output=True, print_output=False)[1][0]


class DiskInfo:
    def __init__(self, device: str):
        if device.startswith("/dev/"):
            self.device = device[5:]
        self.device = device

    @property
    def model(self):
        with open(f"/sys/block/{self.device}/device/model") as file:
            return file.read().rstrip()

    @property
    def vendor(self):
        with open(f"/sys/block/{self.device}/device/vendor") as file:
            return file.read().rstrip()

    def lsblk(self):
        run(["lsblk", f"/dev/{self.device}"])

    def print(self):
        text = f"Vendor: {self.vendor}, model: {self.model}"
        print_info(text)


def alert_if_root(fail: bool = False):
    if os.geteuid() == 0:
        text = "Warning! This script should not be run as root for security reasons!"
        if fail:
            logger.error(text)
            raise RuntimeError(text)
        print(text)
        logger.warning(text)


def alert_if_not_root(fail: bool = True):
    if os.geteuid() != 0:
        text = "This script should be run as root."
        if fail:
            logger.error(text)
            raise PermissionError(text)
        print(text)
        logger.warning(text)


def get_user() -> str:
    """Get the name of the user that executed this process, even if sudo was used.
    Based on https://unix.stackexchange.com/a/626389/"""
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


def is_virtual():
    with open("/proc/cpuinfo", "r") as file:
        return "hypervisor" in file.read()


def print_info(text: str):
    print(text)
    logger.info(text)


def run(
        command: tp.List[str],
        check: bool = True,
        get_output: bool = False,
        print_output: bool = True,
        stderr: bool = True,
        sudo: bool = False) -> tp.Union[int, tp.Tuple[int, tp.List[str]]]:
    """
    Run an external command as a subprocess
    :param command: command and its arguments
    :param check: whether to check the return code and raise an error accordingly
    :param get_output: whether to extract output to Python
    :param print_output: print command output to console
    :param stderr: whether to capture stderr output as well
    :param sudo: run the command as sudo if not already root
    :return: return code of the command
    """
    logger.info("Running %s", command)
    kwargs = {}
    if stderr:
        kwargs["stderr"] = sp.PIPE
    if sudo and os.geteuid() != 0:
        command = ["sudo"] + command
    # Setting bufsize=1 would result in
    # RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
    process = sp.Popen(command, stdout=sp.PIPE, **kwargs)
    output = []
    stderr_line = ""
    while True:
        stdout_line = process.stdout.readline().decode("utf-8").rstrip("\r|\n")
        if stderr:
            stderr_line = process.stderr.readline().decode("utf-8").rstrip("\r|\n")
        if not stdout_line and not stderr_line and process.poll() is not None:
            break
        if stdout_line:
            logger.info(stdout_line)
            if get_output:
                output.append(stdout_line)
            if print_output:
                print(stdout_line)
        if stderr and stderr_line:
            logger.error(stderr_line)
            if get_output:
                output.append(stderr_line)
            if print_output:
                print(stderr_line)
    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()
    if check and return_code:
        raise sp.CalledProcessError(return_code, command)
    if get_output:
        return return_code, output
    return return_code


def yes_or_no() -> bool:
    return "y" == choice(["y", "n"])


def choice(choices: tp.List[str]) -> str:
    while True:
        reply = str(input(f"({'/'.join(choices)})")).lower().strip()
        if reply in choices:
            return reply
        print("Invalid answer. Did you make a typo?")
