#!/usr/bin/env python3
"""Install apt packages. Must be run as root, after the repositories have been configured."""

import argparse
import logging
import pathlib
import sys
import tempfile

# Allow running this file directly as a script.
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import dpkg, utils

logger = logging.getLogger(__name__)

BASE_PACKAGES = (
    # Servers should have git-gui too for X11 forwarding.
    # Screen has been replaced with tmux.
    "7zip", "apt-transport-https", "ca-certificates", "git", "git-gui",
    "htop", "mosh", "openssh-server", "rsync", "tmux", "ufw",
)
#: Install debug symbols for these packages.
#: These are installed already before any crashes occur to ensure that if a crash occurs,
#: the debug symbols are immediately available for debugging.
DEBUGGABLE_PACKAGES = (
    "kinit", "kscreen", "kwin-wayland",
    "libkwin6",
    "libqt6core6t64", "libqt6dbus6", "libqt6qml6", "libqt6quick6",
    # "libsystemd0", "libtbb12", "libxcb-randr0",
)
#: All GUI programs should go here.
DESKTOP_PACKAGES = (
    "clamtk", "claude-desktop", "eduvpn-client", "filelight", "filezilla", "gimp", "haruna", "inkscape",
    "keepassxc", "krdc", "ktorrent",
    "libdrm-dev",  # Required for compiling steam_drm_filter.c
    "libenchant-2-voikko",
    "libreoffice", "libreoffice-help-en-us", "libreoffice-help-fi", "libreoffice-voikko",
    "mumble", "network-manager-openvpn", "remmina", "signal-desktop", "steam",
    "synaptic", "texmaker", "tikzit", "tmispell-voikko", "vlc",
)
DEV_PACKAGES = (
    "build-essential", "cloc", "cmake", "gcc-multilib", "g++-multilib", "gfortran", "shellcheck",
)
DOCKER_PACKAGES = (
    "docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin",
)
#: .deb packages that are not available from repositories: (package name, download URL)
EXTERNAL_DEBS = (
    ("google-chrome-stable", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"),
    ("zoom", "https://zoom.us/client/latest/zoom_amd64.deb"),
)
FUN_PACKAGES = ("cmatrix", "cowsay", "fortune-mod")
INTEL_PACKAGES = ("intel-gpu-tools", "intel-media-va-driver", "intel-microcode", "intel-opencl-icd")
KDE_PACKAGES = ("kde-config-flatpak", "remmina-plugin-kwallet")
NVIDIA_PACKAGES = ("boinc-client-nvidia-cuda",)
PHYSICAL_DESKTOP_PACKAGES = (
    "boinc", "cutecom", "gnome-disk-utility", "gparted", "obs-studio", "pipewire-audio", "rpi-imager", "solaar",
    "virt-viewer",
)
PHYSICAL_LAPTOP_DESKTOP_PACKAGES = ("gnome-network-displays", "touchegg")
PHYSICAL_LAPTOP_PACKAGES = ("tlp",)
PHYSICAL_PACKAGES = (
    "bluetooth", "boinc-client-opencl", "clinfo", "clpeak", "exfatprogs", "gdisk",
    "lm-sensors", "pocl-opencl-icd", "powertop", "s-tui", "stress", "usbtop",
)
PYTHON_PACKAGES = (
    "python3-dev", "python3-wheel",
    # I have switched to using uv instead of pip, so these are no longer needed.
    # "python3-setuptools", "python3-venv",
)
UTILS_PACKAGES = (
    "autojump",
    "autossh",
    "bleachbit",
    "bubblewrap",  # Required by Claude Code sandbox
    "cifs-utils",
    "curl",  # Required by asdf-nodejs
    "dirmngr",  # Required by asdf-nodejs
    "dislocker",
    "fastfetch",
    "gawk",  # Required by asdf-nodejs
    "gh",  # GitHub CLI
    "git-delta",
    "gocryptfs",
    "gpg",  # Required by asdf-nodejs
    "gpg-agent", "links", "mtr-tiny", "nmap", "optipng", "pandoc", "pdftk", "rclone",
    # From the Microsoft repository. However, it seems to have been removed from there, and is available as a snap only.
    # "powershell",
    "socat",  # Required by Claude Code sandbox
    "ssh-tools",
    "texlive-full", "traceroute", "wget", "wireguard", "xindy",
    # The yt-dlp apt package may not be up to date. In this case, use pip to install the latest version.
    "yt-dlp",
    "zsh",
)

# Steam Frame streaming with the 32-bit Steam client.
# The 64-bit Steam client (STEAM_FORCE_CLIENT=steamrt64) runs in the Steam Runtime container,
# which bundles its own PipeWire libraries, so no host packages are needed for it.
# if info.arch == "amd64":
#     packages += ["libpipewire-0.3-0t64:i386", "libpipewire-0.3-modules:i386", "libspa-0.2-modules:i386"]

# XDG_SESSION_TYPE is not set properly when running with sudo.
# if XDG_SESSION_TYPE == "wayland":
#     packages.append("freerdp2-wayland")


def download_external_debs(
        info: utils.SystemInfo, installed: set[str], directory: pathlib.Path) -> list[pathlib.Path]:
    """Download the .deb packages that are not available from repositories.

    :param info: system information
    :param installed: names of the installed packages
    :param directory: directory to download the packages to
    :return: paths of the downloaded packages
    """
    paths = []
    for package, url in get_external_debs(info, installed):
        logger.info("Adding %s to the installation list.", package)
        paths.append(utils.download_file(url, directory / url.rsplit("/", 1)[-1]))
    return paths


def get_external_debs(info: utils.SystemInfo, installed: set[str]) -> list[tuple[str, str]]:
    """Get the external .deb packages that should be installed.

    :param info: system information
    :param installed: names of the installed packages
    :return: (package name, download URL) pairs
    """
    if not info.is_desktop or info.arch != "amd64":
        return []
    return [(package, url) for package, url in EXTERNAL_DEBS if package not in installed]


def get_packages(info: utils.SystemInfo, installed: set[str]) -> list[str]:
    """Get the apt packages to install from the repositories.

    :param info: system information
    :param installed: names of the installed packages, used for selecting the debug symbol packages
    :return: package names
    """
    packages = [
        *BASE_PACKAGES, *DEV_PACKAGES, *DOCKER_PACKAGES, *FUN_PACKAGES, *PYTHON_PACKAGES, *UTILS_PACKAGES,
    ]
    if info.is_desktop:
        packages += DESKTOP_PACKAGES
        if info.desktop_env == "KDE":
            packages += KDE_PACKAGES
        packages += [f"{package}-dbgsym" for package in DEBUGGABLE_PACKAGES if package in installed]

    if info.is_physical:
        packages += PHYSICAL_PACKAGES
        if info.is_desktop:
            packages += PHYSICAL_DESKTOP_PACKAGES
            if info.is_laptop:
                packages += PHYSICAL_LAPTOP_DESKTOP_PACKAGES
        if info.is_laptop:
            packages += PHYSICAL_LAPTOP_PACKAGES

    if info.has_intel_cpu:
        packages += INTEL_PACKAGES
    if info.has_nvidia_gpu:
        packages += NVIDIA_PACKAGES
    return packages


def install_packages(info: utils.SystemInfo, assume_yes: bool = False) -> None:
    """Install the apt packages.

    :param info: system information
    :param assume_yes: whether to skip the confirmations
    """
    logger.info("Configuring apt/dpkg architectures.")
    dpkg.enable_i386(info)
    logger.info("Updating apt repositories.")
    utils.run(["apt", "update"])

    logger.info("Constructing the list of apt packages to install.")
    installed = dpkg.get_installed_packages()
    packages: list[str | pathlib.Path] = list(get_packages(info, installed))
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        # Allow the unprivileged _apt user to read the packages.
        temp_path.chmod(0o755)
        packages += download_external_debs(info, installed, temp_path)
        logger.info("Installing apt packages.")
        utils.run(["apt", "install", *(["--yes"] if assume_yes else []), *packages])


def main() -> None:
    """Install the apt packages."""
    parser = argparse.ArgumentParser(description=__doc__)
    utils.add_common_args(parser)
    args = parser.parse_args()
    utils.setup_logging()
    utils.require_root()
    install_packages(utils.SystemInfo.detect(args.desktop_env), assume_yes=args.yes)


if __name__ == "__main__":
    main()
