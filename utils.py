"""
Utility methods for scripts
"""

import typing as tp
import logging
import subprocess as sp

logger = logging.getLogger(__name__)


def run(command: tp.List[str], check: bool = True) -> int:
    """
    Run an external command as a subprocess
    :param command: command and its arguments
    :param check: whether to check the return code and raise an error accordingly
    :return: return code of the command
    """
    logger.info(f"Running {command}")
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
    while True:
        stdout = process.stdout.readline().decode("utf-8").rstrip("\r|\n")
        stderr = process.stderr.readline().decode("utf-8").rstrip("\r|\n")
        if not stdout and not stderr and process.poll() is not None:
            break
        if stdout:
            print(stdout)
            logger.info(stdout)
        if stderr:
            print(stderr)
            logger.error(stderr)
    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()
    if check and return_code:
        raise sp.CalledProcessError(return_code, command)
    return return_code
