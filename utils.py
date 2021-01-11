"""
Utility methods for scripts
"""

import typing as tp
import logging
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
        logger.info(text)
        print(text)


def run(
        command: tp.List[str],
        check: bool = True,
        get_output: bool = False,
        print_output: bool = True,
        stderr: bool = True) -> tp.Union[int, tp.Tuple[int, tp.List[str]]]:
    """
    Run an external command as a subprocess
    :param command: command and its arguments
    :param check: whether to check the return code and raise an error accordingly
    :param get_output: whether to extract output to Python
    :param print_output: print command output to console
    :return: return code of the command
    """
    logger.info(f"Running {command}")
    kwargs = {}
    if stderr:
        kwargs["stderr"] = sp.PIPE
    process = sp.Popen(command, stdout=sp.PIPE, bufsize=1, **kwargs)
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
