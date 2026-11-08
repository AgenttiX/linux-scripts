#!/usr/bin/env python3
"""Install all the software.

First runs install_sudo.py with sudo, and then installs the software that does not require root privileges.
Should be run as a normal user.

These have to be installed manually:
- TeamViewer
"""

import argparse
import logging
import os
import pathlib
import sys

# Allow running this file directly as a script.
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import (
    asdf,
    flatpak,
    utils,
)

logger = logging.getLogger(__name__)

#: The root part is run with the system Python instead of e.g. a virtual environment of the user.
SYSTEM_PYTHON = "/usr/bin/python3"


def run_sudo_part(desktop_env: str, assume_yes: bool = False, sources: bool = False) -> None:
    """Run install_sudo.py with sudo.

    :param desktop_env: desktop environment to pass to the script, as sudo does not preserve it
    :param assume_yes: whether to skip the confirmations
    :param sources: whether to configure the apt repositories
    """
    logger.info("Running the installation steps that require root privileges.")
    utils.run([
        "sudo", SYSTEM_PYTHON, utils.SCRIPT_DIR / "install_sudo.py",
        f"--desktop-env={desktop_env}",
        *(["--yes"] if assume_yes else []),
        *(["--sources"] if sources else []),
    ])


def main() -> None:
    """Install all the software."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    utils.add_common_args(parser)
    parser.add_argument("--skip-sudo", action="store_true", help="Skip the steps that require root privileges")
    parser.add_argument("--sources", action="store_true", help="Configure the apt repositories first")
    args = parser.parse_args()
    if args.skip_sudo and args.sources:
        parser.error("--sources requires root privileges and cannot be used with --skip-sudo")
    utils.setup_logging()
    utils.require_not_root()

    desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "") if args.desktop_env is None else args.desktop_env
    if not args.skip_sudo:
        run_sudo_part(desktop_env, assume_yes=args.yes, sources=args.sources)

    # The system information is detected only after the root part, as it may have installed e.g. Nvidia drivers.
    info = utils.SystemInfo.detect(desktop_env)
    flatpak.install_packages(info, assume_yes=args.yes)
    asdf.install_plugins(info)

    # Installing uv requires piping an external script to a shell, so it's left for the user to do manually.
    # if not utils.command_exists("uv"):
    #     curl -LsSf https://astral.sh/uv/install.sh | sh
    logger.info("Software installed.")


if __name__ == "__main__":
    main()
