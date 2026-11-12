#!/usr/bin/env python3
"""Install the software that requires root privileges.

This is called by install.py with sudo. As sudo does not preserve XDG_CURRENT_DESKTOP,
the desktop environment should be given with --desktop-env.
"""

import argparse
import logging
import pathlib
import sys

# Allow running this file directly as a script.
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import (
    apt_packages,
    apt_sources,
    utils,
)

logger: logging.Logger = logging.getLogger(__name__)

APPARMOR_USERNS_SYSCTL: pathlib.Path = pathlib.Path("/proc/sys/kernel/apparmor_restrict_unprivileged_userns")
BWRAP_APPARMOR_PROFILE = """abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
"""
BWRAP_APPARMOR_PROFILE_PATH: pathlib.Path = pathlib.Path("/etc/apparmor.d/bwrap")
SNAP_PACKAGES = (
    # ("lua-language-server", True),
    ("pycharm-professional", True),
    # Telegram snap does not work on Kubuntu 25.04
    # https://github.com/telegramdesktop/tdesktop/issues/29437#issuecomment-3131627645
    # ("telegram-desktop", False),
)


def fix_bwrap_apparmor() -> None:
    """Allow bubblewrap to create user namespaces, as required by the Claude Code sandbox.

    https://code.claude.com/docs/en/sandboxing#ubuntu-24-04-and-later-allow-bubblewrap-to-create-user-namespaces
    """
    if not APPARMOR_USERNS_SYSCTL.exists() or APPARMOR_USERNS_SYSCTL.read_text().strip() == "0":
        return
    if BWRAP_APPARMOR_PROFILE_PATH.exists() and BWRAP_APPARMOR_PROFILE_PATH.read_text() == BWRAP_APPARMOR_PROFILE:
        return
    logger.info("Fixing bubblewrap permissions for Claude Code.")
    utils.write_file(BWRAP_APPARMOR_PROFILE_PATH, BWRAP_APPARMOR_PROFILE)
    utils.run(["systemctl", "reload", "apparmor"])


def install_snaps(info: utils.SystemInfo) -> None:
    """Install the Snap packages.

    :param info: system information
    """
    if not info.is_desktop:
        return
    if not utils.command_exists("snap"):
        logger.warning("Snap was not found. Skipping the installation of Snap packages.")
        return
    logger.info("Installing Snap packages.")
    for package, classic in SNAP_PACKAGES:
        utils.run(["snap", "install", package, *(["--classic"] if classic else [])])


def main() -> None:
    """Install the software that requires root privileges."""
    parser = argparse.ArgumentParser(description=__doc__)
    utils.add_common_args(parser)
    parser.add_argument("--sources", action="store_true", help="Configure the apt repositories first")
    args = parser.parse_args()
    utils.setup_logging()
    utils.require_root()

    info = utils.SystemInfo.detect(args.desktop_env)
    if utils.command_exists("apt"):
        if args.sources:
            apt_sources.setup_sources(info, assume_yes=args.yes)
        apt_packages.install_packages(info, assume_yes=args.yes)
    install_snaps(info)
    fix_bwrap_apparmor()


if __name__ == "__main__":
    main()
