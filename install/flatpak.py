#!/usr/bin/env python3
"""Install Flatpak packages from Flathub.

Before running this script on Kubuntu, enable the Flatpak backend:
https://flatpak.org/setup/Kubuntu
"""

import argparse
import logging
import pathlib
import sys

# Allow running this file directly as a script.
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import utils

logger = logging.getLogger(__name__)

BASE_PACKAGES = (
    "com.mastermindzh.tidal-hifi",
    "com.vscodium.codium",
    "md.obsidian.Obsidian",
    "org.chromium.Chromium",
    "org.jellyfin.JellyfinDesktop",
    "org.zotero.Zotero",
    "tv.plex.PlexDesktop",
)
DESKTOP_PACKAGES = (
    "app.eduroam.geteduroam",
    "cc.arduino.IDE2",
    "com.discordapp.Discord",
    "com.github.IsmaelMartinez.teams_for_linux",
    "com.github.tchx84.Flatseal",
    "com.github.xournalpp.xournalpp",
    "com.mattermost.Desktop",
    # "com.plexamp.Plexamp",
    "com.slack.Slack",
    "com.spotify.Client",
    "net.lutris.Lutris",
    "org.blender.Blender",
    "org.ferdium.Ferdium",
    "org.telegram.desktop",
)
STEAMOS_PACKAGES = (
    "org.keepassxc.KeePassXC",
    # "org.signal.Signal",
)


def get_packages(info: utils.SystemInfo) -> list[str]:
    """Get the Flatpak packages to install.

    :param info: system information
    :return: Flatpak application IDs
    """
    if info.os_release.get("NAME") == "SteamOS":
        return [*BASE_PACKAGES, *STEAMOS_PACKAGES]
    if not info.is_desktop:
        return []
    return [*BASE_PACKAGES, *DESKTOP_PACKAGES]


def install_packages(info: utils.SystemInfo, assume_yes: bool = False) -> None:
    """Install the Flatpak packages.

    :param info: system information
    :param assume_yes: whether to skip the confirmations
    """
    if not utils.command_exists("flatpak"):
        logger.warning("Flatpak was not found. Skipping the installation of Flatpak packages.")
        return
    packages = get_packages(info)
    if not packages:
        logger.info("This seems to be a headless device. Skipping the installation of Flatpak packages.")
        return
    logger.info("Installing Flatpak packages.")
    utils.run(["flatpak", "install", *(["--assumeyes"] if assume_yes else []), "flathub", *packages])


def main() -> None:
    """Install the Flatpak packages."""
    parser = argparse.ArgumentParser(description=__doc__)
    utils.add_common_args(parser)
    args = parser.parse_args()
    utils.setup_logging()
    install_packages(utils.SystemInfo.detect(args.desktop_env), assume_yes=args.yes)


if __name__ == "__main__":
    main()
