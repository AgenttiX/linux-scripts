#!/usr/bin/env python3
"""Configure the apt repositories. Must be run as root."""

import argparse
from dataclasses import dataclass
import logging
import pathlib
import sys
import tempfile

# Allow running this file directly as a script.
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import utils

logger: logging.Logger = logging.getLogger(__name__)

APT_KEYRINGS_DIR: pathlib.Path = pathlib.Path("/etc/apt/keyrings")
APT_SOURCES_DIR: pathlib.Path = pathlib.Path("/etc/apt/sources.list.d")
PREREQUISITES = (
    "apt-transport-https", "ca-certificates",
    "software-properties-common",  # Provides add-apt-repository
    "ubuntu-dbgsym-keyring",
)
SHARE_KEYRINGS_DIR: pathlib.Path = pathlib.Path("/usr/share/keyrings")


@dataclass(frozen=True, slots=True)
class AptSource:
    """An apt repository in the deb822 format."""

    #: Name of the .sources file without the extension
    name: str
    uris: str
    suites: str
    components: str
    signed_by: pathlib.Path
    #: URL of the signing key. If None, the key is assumed to be installed by a package.
    key_url: str | None = None
    architectures: str | None = None

    @property
    def path(self) -> pathlib.Path:
        """Path of the .sources file."""
        return APT_SOURCES_DIR / f"{self.name}.sources"

    def render(self) -> str:
        """Render the source in the deb822 format.

        :return: contents of the .sources file
        """
        lines = [
            "Types: deb",
            f"URIs: {self.uris}",
            f"Suites: {self.suites}",
            f"Components: {self.components}",
            f"Signed-By: {self.signed_by}",
        ]
        if self.architectures:
            lines.append(f"Architectures: {self.architectures}")
        return "\n".join(lines) + "\n"

    def install(self) -> None:
        """Download the signing key and write the .sources file."""
        logger.info("Configuring the %s repository.", self.name)
        if self.key_url is not None:
            utils.download_gpg_key(self.key_url, self.signed_by)
        utils.write_file(self.path, self.render())


def get_ppas(info: utils.SystemInfo) -> list[str]:
    """Get the PPAs to enable.

    :param info: system information
    :return: PPA names
    """
    ppas = []
    if info.is_desktop:
        # For OpenTabletDriver dotnet-runtime-6.0 dependency
        # https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#register-the-ubuntu-net-backports-package-repository
        # ppas.append("ppa:dotnet/backports")
        # ppas.append("ppa:linuxuprising/java")
        # ppas.append("ppa:obsproject/obs-studio")
        ppas.append("ppa:phoerious/keepassxc")
        # ppas.append("ppa:thopiekar/openrgb")
        if info.is_laptop:
            ppas.append("ppa:touchegg/stable")
    if info.is_laptop:
        ppas.append("ppa:linrunner/tlp")
    return ppas


def get_sources(info: utils.SystemInfo) -> list[AptSource]:
    """Get the deb822 apt sources to configure.

    :param info: system information
    :return: apt sources
    """
    codename = info.os_release["VERSION_CODENAME"]
    sources = [
        # Debug symbols
        # https://documentation.ubuntu.com/server/explanation/debugging/debug-symbol-packages/
        AptSource(
            name="ddebs",
            uris="http://ddebs.ubuntu.com/",
            suites=f"{codename} {codename}-updates {codename}-proposed",
            components="main restricted universe multiverse",
            signed_by=SHARE_KEYRINGS_DIR / "ubuntu-dbgsym-keyring.gpg",
        ),
        # Custom repos in alphabetical order
        # Docker
        # https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
        AptSource(
            name="docker",
            uris="https://download.docker.com/linux/ubuntu",
            suites=codename,
            components="stable",
            signed_by=APT_KEYRINGS_DIR / "docker.gpg",
            key_url="https://download.docker.com/linux/ubuntu/gpg",
            architectures=info.arch,
        ),
        # GitHub CLI
        AptSource(
            name="github-cli",
            uris="https://cli.github.com/packages",
            suites="stable",
            components="main",
            signed_by=APT_KEYRINGS_DIR / "githubcli-archive-keyring.gpg",
            key_url="https://cli.github.com/packages/githubcli-archive-keyring.gpg",
            architectures=info.arch,
        ),
        # Intel oneAPI
        # https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc-toolkit-download.html
        AptSource(
            name="oneAPI",
            uris="https://apt.repos.intel.com/oneapi",
            suites="all",
            components="main",
            signed_by=SHARE_KEYRINGS_DIR / "oneapi-archive-keyring.gpg",
            key_url="https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB",
        ),
        # Syncthing
        # https://apt.syncthing.net/
        AptSource(
            name="syncthing",
            uris="https://apt.syncthing.net/",
            suites="syncthing",
            components="stable-v2",
            signed_by=APT_KEYRINGS_DIR / "syncthing-archive-keyring.gpg",
            key_url="https://syncthing.net/release-key.gpg",
        ),
    ]
    if info.is_desktop:
        sources += [
            # eduVPN
            AptSource(
                name="eduvpn-v4",
                uris="https://app.eduvpn.org/linux/v4/deb",
                suites="resolute",
                components="main",
                signed_by=SHARE_KEYRINGS_DIR / "eduvpn-v4.gpg",
                key_url="https://app.eduvpn.org/linux/v4/deb/app+linux@eduvpn.org.asc",
                architectures=info.arch,
            ),
            # Google Antigravity
            AptSource(
                name="antigravity",
                uris="https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev",
                suites="antigravity-debian",
                components="main",
                signed_by=APT_KEYRINGS_DIR / "antigravity-repo-key.gpg",
                key_url="https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg",
                architectures=info.arch,
            ),
            # Signal
            # https://signal.org/download/
            # The distro name has been "xenial" for quite a while.
            AptSource(
                name="signal-xenial",
                uris="https://updates.signal.org/desktop/apt",
                suites="xenial",
                components="main",
                signed_by=SHARE_KEYRINGS_DIR / "signal-desktop-keyring.gpg",
                key_url="https://updates.signal.org/desktop/apt/keys.asc",
                architectures=info.arch,
            ),
        ]
    return sources


def setup_claude_desktop() -> None:
    """Configure the Claude Desktop repository.

    The claude-desktop package installs its own claude-desktop.list file,
    which would conflict with a .sources file, so the .list format is used here as well.
    """
    logger.info("Configuring the Claude Desktop repository.")
    key_path = SHARE_KEYRINGS_DIR / "claude-desktop-archive-keyring.asc"
    utils.download_file("https://downloads.claude.ai/claude-desktop/key.asc", key_path)
    utils.write_file(
        APT_SOURCES_DIR / "claude-desktop.list",
        f"deb [arch=amd64,arm64 signed-by={key_path}] "
        "https://downloads.claude.ai/claude-desktop/apt/stable stable main\n",
    )


def setup_sources(info: utils.SystemInfo, assume_yes: bool = False) -> None:
    """Configure all the apt repositories.

    :param info: system information
    :param assume_yes: whether to skip the confirmations
    """
    yes = ["--yes"] if assume_yes else []
    APT_KEYRINGS_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)
    utils.run(["apt", "update"])
    utils.run(["apt", "install", *yes, *PREREQUISITES])

    for source in get_sources(info):
        source.install()
    setup_claude_desktop()

    # Nvidia CUDA
    utils.run([utils.REPO_DIR / "drivers" / "setup_nvidia_repos.sh"])

    # Speedtest
    # curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash

    if info.is_desktop and utils.command_exists("teamviewer"):
        utils.run(["teamviewer", "repo", "default"])

    for ppa in get_ppas(info):
        utils.run(["add-apt-repository", "--yes", ppa])

    # The Microsoft repository is configured by a package.
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        # Allow the unprivileged _apt user to read the package.
        temp_path.chmod(0o755)
        version_id = info.os_release["VERSION_ID"]
        deb_path = utils.download_file(
            f"https://packages.microsoft.com/config/ubuntu/{version_id}/packages-microsoft-prod.deb",
            temp_path / "packages-microsoft-prod.deb",
        )
        utils.run(["apt", "install", *yes, deb_path])

    utils.run(["apt", "update"])


def main() -> None:
    """Configure the apt repositories."""
    parser = argparse.ArgumentParser(description=__doc__)
    utils.add_common_args(parser)
    args = parser.parse_args()
    utils.setup_logging()
    utils.require_root()
    setup_sources(utils.SystemInfo.detect(args.desktop_env), assume_yes=args.yes)


if __name__ == "__main__":
    main()
