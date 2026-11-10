"""Shared helpers for reading files, running commands and parsing their output."""

from __future__ import annotations

from collections.abc import Iterable
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess as sp

logger: logging.Logger = logging.getLogger(__name__)


#: Placeholder values that some manufacturers leave in the DMI tables
DMI_RUBBISH: frozenset[str] = frozenset({
    "", "default string", "none", "not applicable", "not specified", "o.e.m.", "oem", "sku",
    "system manufacturer", "system product name", "system serial number", "system version",
    "to be filled by o.e.m.", "unknown",
})


#: PCI device address format
PCI_ADDRESS: re.Pattern[str] = re.compile(r"^[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7]$")


def compress_ranges(numbers: Iterable[int]) -> str:
    """Format a list of integers as ranges, e.g. "0-3,8-11".

    :param numbers: integers
    :return: compressed representation
    """
    nums = sorted(set(numbers))
    parts: list[str] = []
    i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ",".join(parts)


def dmi_value(value: str | None) -> str | None:
    """Filter out placeholder values from DMI fields.

    :param value: raw value
    :return: the value, or None if it's a placeholder
    """
    if value is None:
        return None
    value = value.strip()
    if value.lower() in DMI_RUBBISH:
        return None
    return value


def driver_name(dev: Path) -> str | None:
    """Get the name of the kernel driver bound to a device.

    :param dev: sysfs device directory
    :return: driver name
    """
    driver = dev / "driver"
    if not driver.exists():
        return None
    return Path(os.readlink(driver)).name


def format_bytes(num: int) -> str:
    """Format a number of bytes with binary units.

    :param num: number of bytes
    :return: human-readable size
    """
    size = float(num)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":  # noqa: PLR2004
            return f"{size:.0f} {unit}" if size == int(size) else f"{size:.1f} {unit}"
        size /= 1024
    raise AssertionError("Unreachable")


def normalize_pci_address(address: str) -> str:
    """Convert a PCI address such as "00000000:01:00.0" to the sysfs format "0000:01:00.0".

    :param address: PCI address
    :return: normalized address
    """
    address = address.strip().lower()
    if match := re.match(r"^([0-9a-f]+):([0-9a-f]{2}):([0-9a-f]{2})\.([0-7])$", address):
        return f"{int(match.group(1), 16):04x}:{match.group(2)}:{match.group(3)}.{match.group(4)}"
    return address


def parse_cpu_list(text: str) -> list[int]:
    """Parse a CPU list such as "0-3,8-11".

    :param text: CPU list
    :return: CPU numbers
    """
    cpus: list[int] = []
    for part in text.strip().split(","):
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-")
            cpus.extend(range(int(start), int(end) + 1))
        else:
            cpus.append(int(part))
    return cpus


def parse_int(text: str | None) -> int | None:
    """Parse an integer in decimal or hexadecimal format.

    :param text: text
    :return: integer, or None if the text is not an integer
    """
    if text is None:
        return None
    try:
        return int(text.strip(), 0)
    except ValueError:
        return None


def parse_lspci(address: str) -> dict[str, str]:
    """Get the lspci fields of a PCI device.

    :param address: PCI address
    :return: fields, e.g. {"Vendor": "NVIDIA Corporation", "Device": "GA102 [GeForce RTX 3090]"}
    """
    output = run_cmd(["lspci", "-vmm", "-D", "-s", address])
    if not output:
        return {}
    fields: dict[str, str] = {}
    for line in output.splitlines():
        key, sep, value = line.partition(":")
        if sep and key not in fields:
            fields[key.strip()] = value.strip()
    return fields


def parse_size(text: str | None) -> int | None:
    """Parse a size such as "16 GB" or "16 GiB" to bytes. Both are interpreted as binary units.

    :param text: size text
    :return: number of bytes
    """
    if not text:
        return None
    match = re.match(r"^([\d.]+)\s*([KMGT]i?B|B)$", text.strip())
    if not match:
        return None
    factor = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}[match.group(2)[0]]
    return int(float(match.group(1)) * factor)


def read_int(path: str | Path) -> int | None:
    """Read an integer from a file.

    :param path: file path
    :return: integer, or None if the file cannot be read or does not contain an integer
    """
    return parse_int(read_text(path))


def read_text(path: str | Path) -> str | None:
    """Read a text file.

    :param path: file path
    :return: stripped contents, or None if the file cannot be read
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as file:
            return file.read().strip()
    except OSError:
        return None


def run_cmd(command: list[str], timeout: float = 15) -> str | None:
    """Run a command and get its output.

    :param command: command and its arguments
    :param timeout: timeout in seconds
    :return: stdout, or None if the command is not available or fails
    """
    if shutil.which(command[0]) is None:
        logger.debug("Command not found: %s", command[0])
        return None
    try:
        result = sp.run(
            command, capture_output=True, text=True, timeout=timeout, check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, sp.SubprocessError) as e:
        logger.debug("Running %s failed: %s", command, e)
        return None
    if result.returncode != 0:
        logger.debug("%s returned %d: %s", command, result.returncode, result.stderr.strip())
        return None
    return result.stdout


def split_pci_name(device: str | None) -> tuple[str | None, str | None]:
    """Split an lspci device name into the codename and the product name.

    :param device: e.g. "GA102 [GeForce RTX 3090]"
    :return: e.g. ("GA102", "GeForce RTX 3090")
    """
    if not device:
        return None, None
    device = re.sub(r"\s*\[[0-9a-f]{4}\]$", "", device)
    if match := re.match(r"^(.*?)\s*\[(.+)\]$", device):
        return match.group(1) or None, match.group(2)
    return None, device
