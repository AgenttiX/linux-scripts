"""Shared code for the user and root parts of the maintenance script."""

import argparse
from collections.abc import Callable, Iterable
import logging
import pathlib
import time

PACKAGE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
REPO_DIR: pathlib.Path = PACKAGE_DIR.parent
LOG_DIR: pathlib.Path = REPO_DIR / "logs"
#: The root part is run with the system Python instead of e.g. a virtual environment of the user.
SYSTEM_PYTHON: str = "/usr/bin/python3"


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add the arguments shared by the user and root parts.

    :param parser: argument parser to add the arguments to
    """
    parser.add_argument("--bleachbit-only", help="Run only BleachBit", action="store_true")
    parser.add_argument("--deep", help="Deep-clean all", action="store_true")
    parser.add_argument("--docker", help="Deep-clean Docker", action="store_true")
    parser.add_argument("--firefox", help="Deep-clean Firefox", action="store_true")
    parser.add_argument("--thunderbird", help="Deep-clean Thunderbird", action="store_true")


def run_steps(steps: Iterable[Callable[[], None]]) -> None:
    """Run maintenance steps, separating their outputs with empty lines.

    :param steps: the steps to run
    """
    for i, step in enumerate(steps):
        if i:
            print()
        step()


def setup_logging(name: str) -> pathlib.Path:
    """Configure logging to a timestamped file in the log directory.

    :param name: prefix of the log file name
    :return: path of the log file
    """
    LOG_DIR.mkdir(exist_ok=True)
    path = LOG_DIR / f"{name}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    logging.basicConfig(
        handlers=[logging.FileHandler(path)],
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    return path
