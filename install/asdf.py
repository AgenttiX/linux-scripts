#!/usr/bin/env python3
"""Install tools with the asdf version manager. Should be run as a normal user."""

import argparse
import logging
import pathlib
import sys

# Allow running this file directly as a script.
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import utils

logger: logging.Logger = logging.getLogger(__name__)

BASE_PLUGINS = ("actionlint",)
DESKTOP_PLUGINS = (
    # https://github.com/GloriousEggroll/proton-ge-custom
    "protonge",
)


def get_plugins(info: utils.SystemInfo) -> list[str]:
    """Get the asdf plugins to install.

    :param info: system information
    :return: plugin names
    """
    plugins = list(BASE_PLUGINS)
    if info.is_desktop:
        plugins += DESKTOP_PLUGINS
    return plugins


def install_plugins(info: utils.SystemInfo) -> None:
    """Install the latest versions of the asdf plugins.

    :param info: system information
    """
    if not utils.command_exists("asdf"):
        logger.warning("asdf was not found. Skipping the installation of asdf plugins.")
        return
    for plugin in get_plugins(info):
        logger.info("Installing %s with asdf.", plugin)
        # Some asdf versions return a non-zero exit code if the plugin has already been added.
        utils.run(["asdf", "plugin", "add", plugin], check=False)
        utils.run(["asdf", "install", plugin, "latest"])


def main() -> None:
    """Install the asdf plugins."""
    parser = argparse.ArgumentParser(description=__doc__)
    utils.add_common_args(parser)
    args = parser.parse_args()
    utils.setup_logging()
    utils.require_not_root()
    install_plugins(utils.SystemInfo.detect(args.desktop_env))


if __name__ == "__main__":
    main()
