"""Shared utilities for the installation scripts.

The scripts in this directory can be run directly (e.g. ``./install/install.py``).
They add the repository directory to ``sys.path`` before importing this module as ``install.utils``.
Only the Python standard library is used, as these scripts are run with the system Python, also as root.
"""

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
import logging
import os
import pathlib
import platform
import shutil
import subprocess
import tempfile
import typing
import urllib.error
import urllib.parse
import urllib.request

from pgp import pgp

logger: logging.Logger = logging.getLogger(__name__)

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
#: Mapping from kernel machine names to Debian architecture names
ARCHITECTURES = {
    "aarch64": "arm64",
    "armv7l": "armhf",
    "i386": "i386",
    "i686": "i386",
    "ppc64le": "ppc64el",
    "riscv64": "riscv64",
    "s390x": "s390x",
    "x86_64": "amd64",
}
#: Mapping from SMBIOS chassis types to the chassis names used by hostnamectl
CHASSIS_TYPES = {
    3: "desktop", 4: "desktop", 6: "desktop", 7: "desktop", 13: "desktop", 35: "desktop", 36: "desktop",
    8: "laptop", 9: "laptop", 10: "laptop", 14: "laptop",
    11: "handset",
    17: "server", 28: "server", 29: "server",
    30: "tablet",
    31: "convertible", 32: "convertible",
}
CPUINFO_PATH: pathlib.Path = pathlib.Path("/proc/cpuinfo")
DMI_CHASSIS_TYPE_PATH: pathlib.Path = pathlib.Path("/sys/class/dmi/id/chassis_type")
DOWNLOAD_TIMEOUT = 60
MACHINE_INFO_PATH: pathlib.Path = pathlib.Path("/etc/machine-info")
OS_RELEASE_PATH: pathlib.Path = pathlib.Path("/etc/os-release")
USER_AGENT = "linux-scripts-installer"


@dataclass(frozen=True, slots=True)
class SystemInfo:
    """Information about the system that affects what software is installed."""

    arch: str
    chassis: str
    #: Value of ``XDG_CURRENT_DESKTOP``, or an empty string for headless systems
    desktop_env: str
    has_intel_cpu: bool
    has_nvidia_gpu: bool
    is_physical: bool
    os_release: dict[str, str]

    @property
    def is_desktop(self) -> bool:
        """Whether the system has a desktop environment."""
        return bool(self.desktop_env)

    @property
    def is_laptop(self) -> bool:
        """Whether the system is a laptop."""
        return self.chassis == "laptop"

    @classmethod
    def detect(cls, desktop_env: str | None = None) -> SystemInfo:
        """Detect the information of the current system.

        :param desktop_env: Desktop environment override.
            This is needed when running with sudo, as sudo does not preserve ``XDG_CURRENT_DESKTOP``.
        :return: system information
        """
        cpuinfo = _read_text(CPUINFO_PATH)
        is_physical = "hypervisor" not in cpuinfo
        if desktop_env is None:
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "")
        machine = platform.machine()
        return cls(
            arch=ARCHITECTURES.get(machine, machine),
            chassis=detect_chassis(
                machine_info=_read_text(MACHINE_INFO_PATH),
                dmi_chassis_type=_read_text(DMI_CHASSIS_TYPE_PATH),
                is_physical=is_physical,
            ),
            desktop_env=desktop_env,
            has_intel_cpu="GenuineIntel" in cpuinfo,
            has_nvidia_gpu=command_exists("nvidia-smi"),
            is_physical=is_physical,
            os_release=parse_os_release(_read_text(OS_RELEASE_PATH)),
        )


class _HTTPSOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Redirect handler that refuses redirects to insecure URLs."""

    @typing.override
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Refuse the redirect if the new URL does not use HTTPS."""
        if urllib.parse.urlparse(newurl).scheme != "https":
            raise urllib.error.HTTPError(newurl, code, f"Refusing an insecure redirect to {newurl}", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _read_text(path: pathlib.Path) -> str:
    """Read a text file, or return an empty string if it cannot be read.

    :param path: path of the file
    :return: contents of the file
    """
    try:
        return path.read_text()
    except OSError:
        return ""


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add the arguments shared by all the installation scripts.

    :param parser: argument parser to add the arguments to
    """
    parser.add_argument(
        "--desktop-env",
        default=None,
        help="Desktop environment (XDG_CURRENT_DESKTOP). An empty string means a headless system. "
             "Defaults to the value of XDG_CURRENT_DESKTOP.",
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Do not ask for confirmations")


def command_exists(command: str) -> bool:
    """Check whether a command is available in PATH.

    :param command: name of the command
    :return: whether the command exists
    """
    return shutil.which(command) is not None


def detect_chassis(machine_info: str, dmi_chassis_type: str, is_physical: bool) -> str:
    """Detect the chassis type similarly to ``hostnamectl chassis``.

    :param machine_info: contents of ``/etc/machine-info``
    :param dmi_chassis_type: contents of ``/sys/class/dmi/id/chassis_type``
    :param is_physical: whether the system is running on physical hardware
    :return: chassis type, or an empty string if it could not be detected
    """
    chassis = parse_os_release(machine_info).get("CHASSIS")
    if chassis:
        return chassis
    if not is_physical:
        return "vm"
    try:
        return CHASSIS_TYPES.get(int(dmi_chassis_type), "")
    except ValueError:
        return ""


def download(url: str) -> bytes:
    """Download a file over HTTPS.

    :param url: URL of the file
    :return: content of the file
    :raises ValueError: if the URL does not use HTTPS
    """
    if urllib.parse.urlparse(url).scheme != "https":
        raise ValueError(f"Refusing to download over an insecure connection: {url}")
    logger.info("Downloading %s", url)
    # The default SSL context verifies the certificates.
    opener = urllib.request.build_opener(_HTTPSOnlyRedirectHandler)
    # Some servers reject the default Python-urllib user agent.
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=DOWNLOAD_TIMEOUT) as response:
        return response.read()


def download_file(url: str, path: pathlib.Path, mode: int = 0o644) -> pathlib.Path:
    """Download a file over HTTPS and save it.

    :param url: URL of the file
    :param path: path to save the file to
    :param mode: file permissions
    :return: path of the saved file
    """
    write_file(path, download(url), mode=mode)
    return path


def download_gpg_key(url: str, path: pathlib.Path) -> None:
    """Download a GPG key and save it in the binary format.

    Keys that are already binary are saved as-is, and ASCII-armored keys are dearmored.

    :param url: URL of the key
    :param path: path to save the key to
    """
    data = download(url)
    if pgp.is_armored(data):
        data = pgp.dearmor(data)
    write_file(path, data)


def is_root() -> bool:
    """Check whether the script is run as root.

    :return: whether the effective user is root
    """
    return os.geteuid() == 0


def parse_os_release(text: str) -> dict[str, str]:
    """Parse the contents of ``/etc/os-release``.

    :param text: contents of the file
    :return: the key-value pairs of the file
    """
    values = {}
    for line in text.splitlines():
        line = line.strip()  # noqa: PLW2901
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":  # noqa: PLR2004
            value = value[1:-1]
        values[key] = value
    return values


def require_not_root() -> None:
    """Exit if the script is run as root."""
    if is_root():
        raise SystemExit("This script should not be run as root.")


def require_root() -> None:
    """Exit if the script is not run as root."""
    if not is_root():
        raise SystemExit("This script should be run as root.")


def run(
        command: Sequence[str | os.PathLike[str]],
        capture: bool = False,
        check: bool = True,
        **kwargs: typing.Any) -> str:
    """Run a command.

    :param command: command and its arguments
    :param capture: whether to capture and return the standard output
    :param check: whether to raise an exception if the command fails
    :param kwargs: additional arguments for :func:`subprocess.run`
    :return: the standard output with surrounding whitespace removed if captured, otherwise an empty string
    """
    logger.debug("Running: %s", " ".join(str(part) for part in command))
    result = subprocess.run(command, capture_output=capture, check=check, text=True, **kwargs)
    return result.stdout.strip() if capture else ""


def setup_logging() -> None:
    """Configure logging for the installation scripts."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def write_file(path: pathlib.Path, content: str | bytes, mode: int = 0o644) -> None:
    """Write a file atomically with the given permissions.

    :param path: path of the file
    :param content: content of the file
    :param mode: file permissions
    """
    data = content.encode() if isinstance(content, str) else content
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(data)
        os.chmod(temp_path, mode)
        os.replace(temp_path, path)
    except BaseException:
        pathlib.Path(temp_path).unlink(missing_ok=True)
        raise
