"""Utilities for dpkg, the low-level package manager of Debian-based systems.

This module contains the functionality that uses only dpkg and not apt.
"""

import logging
import pathlib

from install import utils

logger = logging.getLogger(__name__)

STATUS_PATH = pathlib.Path("/var/lib/dpkg/status")


def add_architecture(arch: str) -> None:
    """Enable a foreign architecture. Must be run as root.

    :param arch: Debian architecture name, e.g. ``i386``
    """
    utils.run(["dpkg", "--add-architecture", arch])


def enable_i386(info: utils.SystemInfo) -> None:
    """Enable the i386 architecture on amd64 systems, as it's needed e.g. by Steam. Must be run as root.

    :param info: system information
    """
    if info.arch != "amd64":
        return
    if "i386" not in get_foreign_architectures():
        logger.info("Detected amd64 architecture where i386 is not enabled. Enabling i386.")
        add_architecture("i386")


def get_foreign_architectures() -> list[str]:
    """Get the enabled foreign architectures.

    :return: Debian architecture names
    """
    return utils.run(["dpkg", "--print-foreign-architectures"], capture=True).split()


def get_installed_packages(status: str | None = None) -> set[str]:
    """Get the names of the installed packages from the dpkg status database.

    :param status: contents of the dpkg status file. If None, the file is read from the system.
    :return: package names
    """
    if status is None:
        status = STATUS_PATH.read_text()
    installed = set()
    for paragraph in status.split("\n\n"):
        fields = {}
        for line in paragraph.splitlines():
            # Continuation lines of multi-line fields start with whitespace.
            if line and not line[0].isspace() and ":" in line:
                key, value = line.split(":", 1)
                fields[key] = value.strip()
        if "Package" in fields and fields.get("Status", "").split()[-1:] == ["installed"]:
            installed.add(fields["Package"])
    return installed
