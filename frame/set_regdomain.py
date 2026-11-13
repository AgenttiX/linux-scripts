#!/usr/bin/env python3
"""Set the Wi-Fi regulatory domain for the Steam Frame wireless adapter, both for this boot and persistently.

The driver of the adapter (rtw89) does not set a country by itself,
so the kernel uses the restrictive world regulatory domain "00" for it.
Then all its 6 GHz channels are disabled, and most 5 GHz channels are passive-scan only.
As the network of the headset is hidden, the adapter has to actively probe for it,
and therefore it cannot connect if the headset happens to pick one of those channels.

The country is detected from the other Wi-Fi adapters that set it by themselves (e.g. Intel),
or it can be given with ``--country``.
The script re-runs itself with sudo when the changes require root privileges.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import dataclasses
import logging
import os
import pathlib
import re
import shutil
import sys
import time

# Allow running this file directly as a script.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from utils.misc_utils import print_info, run

logger: logging.Logger = logging.getLogger(__name__)

BAND_5GHZ_MIN_MHZ = 4900
BAND_6GHZ_MIN_MHZ = 5925
CFG80211_PARAM: pathlib.Path = pathlib.Path("/sys/module/cfg80211/parameters/ieee80211_regdom")
COUNTRY_LINE_PATTERN: re.Pattern[str] = re.compile(r"^country (\w{2}):")
COUNTRY_PATTERN: re.Pattern[str] = re.compile(r"^[A-Z]{2}$")
FREQUENCY_LINE_PATTERN: re.Pattern[str] = re.compile(r"^\s*\*\s+(\d+(?:\.\d+)?)\s+MHz\s+\[\d+\](.*)$")
MODPROBE_CONF: pathlib.Path = pathlib.Path("/etc/modprobe.d/cfg80211-regdom.conf")
SYSFS_NET: pathlib.Path = pathlib.Path("/sys/class/net")
VALVE_USB_VENDOR = "28de"
WORLD_REGDOMAIN = "00"


@dataclasses.dataclass(frozen=True, slots=True)
class BandChannels:
    """Channel counts of a frequency band of a Wi-Fi adapter."""

    usable: int = 0
    passive: int = 0
    disabled: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class RegDomains:
    """Regulatory domains reported by ``iw reg get``."""

    global_country: str | None
    self_managed: dict[str, str]


@dataclasses.dataclass(frozen=True, slots=True)
class WirelessInterface:
    """A wireless network interface."""

    name: str
    phy: str
    driver: str | None
    usb_id: str | None

    @property
    def is_steam_frame_adapter(self) -> bool:
        """Whether this is a Valve USB adapter, i.e. the Steam Frame wireless adapter."""
        return self.usb_id is not None and self.usb_id.startswith(f"{VALVE_USB_VENDOR}:")


def band_name(freq_mhz: float) -> str:
    """Get the name of the Wi-Fi band of a frequency.

    :param freq_mhz: frequency in MHz
    :return: band name
    """
    if freq_mhz >= BAND_6GHZ_MIN_MHZ:
        return "6 GHz"
    if freq_mhz >= BAND_5GHZ_MIN_MHZ:
        return "5 GHz"
    return "2.4 GHz"


def channel_counts(phy_info: str) -> dict[str, BandChannels]:
    """Count the usable, passive-scan only and disabled channels of each band.

    :param phy_info: output of ``iw phy <phy> info``
    :return: channel counts by band name
    """
    counts: dict[str, list[int]] = {}
    for line in phy_info.splitlines():
        match = FREQUENCY_LINE_PATTERN.match(line)
        if match is None:
            continue
        band = counts.setdefault(band_name(float(match.group(1))), [0, 0, 0])
        flags = match.group(2)
        if "disabled" in flags:
            band[2] += 1
        elif "no IR" in flags:
            band[1] += 1
        else:
            band[0] += 1
    return {name: BandChannels(*values) for name, values in counts.items()}


def detect_country(reg: RegDomains) -> str | None:
    """Detect the country from the regulatory domains that the drivers or the user have set.

    :param reg: current regulatory domains
    :return: country code, or None if it could not be detected
    """
    countries = {country for country in reg.self_managed.values() if country != WORLD_REGDOMAIN}
    if len(countries) == 1:
        return countries.pop()
    if len(countries) > 1:
        logger.warning("The self-managed adapters report multiple countries: %s", sorted(countries))
        return None
    if reg.global_country not in (None, WORLD_REGDOMAIN):
        return reg.global_country
    return None


def get_reg_domains() -> RegDomains:
    """Get the current regulatory domains with ``iw reg get``.

    :return: current regulatory domains
    """
    return parse_reg_get("\n".join(run(["iw", "reg", "get"], get_output=True, print_output=False)[1]))


def list_wireless_interfaces(sysfs_net: pathlib.Path = SYSFS_NET) -> list[WirelessInterface]:
    """List the wireless network interfaces.

    :param sysfs_net: path to ``/sys/class/net``
    :return: wireless interfaces sorted by name
    """
    interfaces: list[WirelessInterface] = []
    for phy_name_path in sorted(sysfs_net.glob("*/phy80211/name")):
        iface = phy_name_path.parent.parent
        device = iface / "device"
        driver_path = device / "driver"
        driver = driver_path.resolve().name if driver_path.exists() else None
        # For USB devices, the device symlink points to the USB interface,
        # and the vendor and product IDs are in the parent USB device.
        vendor_path = device / ".." / "idVendor"
        product_path = device / ".." / "idProduct"
        usb_id = None
        if vendor_path.is_file() and product_path.is_file():
            usb_id = f"{vendor_path.read_text().strip()}:{product_path.read_text().strip()}"
        interfaces.append(WirelessInterface(
            name=iface.name,
            phy=phy_name_path.read_text().strip(),
            driver=driver,
            usb_id=usb_id,
        ))
    return interfaces


def modprobe_conf_content(country: str) -> str:
    """Get the content of the modprobe config file that sets the regulatory domain at boot.

    :param country: ISO 3166-1 alpha-2 country code
    :return: file content
    """
    return (
        "# Set the Wi-Fi regulatory domain at boot.\n"
        "# Created by linux-scripts/frame/set_regdomain.py\n"
        f"options cfg80211 ieee80211_regdom={country}\n"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command-line arguments.

    :param argv: command-line arguments, defaults to ``sys.argv[1:]``
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--country",
        help="ISO 3166-1 alpha-2 country code, e.g. FI. Detected from the other Wi-Fi adapters by default.",
    )
    parser.add_argument("--status", help="Only print the current status without changing anything", action="store_true")
    return parser.parse_args(argv)


def parse_reg_get(output: str) -> RegDomains:
    """Parse the output of ``iw reg get``.

    :param output: output of ``iw reg get``
    :return: regulatory domains
    """
    global_country: str | None = None
    self_managed: dict[str, str] = {}
    section: str | None = None
    for line in output.splitlines():
        if line == "global":
            section = "global"
        elif line.startswith("phy#"):
            # Only self-managed phys have their own section.
            section = line.split()[0].replace("#", "")
        elif (match := COUNTRY_LINE_PATTERN.match(line)) and section is not None:
            if section == "global":
                global_country = match.group(1)
            else:
                self_managed[section] = match.group(1)
            section = None
    return RegDomains(global_country=global_country, self_managed=self_managed)


def print_status(interfaces: Sequence[WirelessInterface], conf_path: pathlib.Path = MODPROBE_CONF) -> None:
    """Print the regulatory domain configuration and the channel availability of the wireless interfaces.

    :param interfaces: wireless interfaces
    :param conf_path: path to the persistent modprobe config
    """
    print_info("Regulatory domains (iw reg get):")
    run(["iw", "reg", "get"])

    if CFG80211_PARAM.is_file():
        print_info(f"\ncfg80211 boot-time regulatory domain of this boot: {CFG80211_PARAM.read_text().strip()}")
    if conf_path.is_file():
        print_info(f"Persistent config in {conf_path}:\n{conf_path.read_text().rstrip()}")
    else:
        print_info(f"Persistent config {conf_path} does not exist.")

    reg = get_reg_domains()
    for iface in interfaces:
        label = " (Steam Frame wireless adapter)" if iface.is_steam_frame_adapter else ""
        regdomain = reg.self_managed.get(iface.phy, f"{reg.global_country} (global)")
        print_info(
            f"\n{iface.name}{label}: {iface.phy}, driver {iface.driver}, "
            f"USB ID {iface.usb_id or '-'}, regulatory domain {regdomain}"
        )
        phy_info = "\n".join(run(["iw", "phy", iface.phy, "info"], get_output=True, print_output=False)[1])
        for band, counts in channel_counts(phy_info).items():
            print_info(
                f"  {band}: {counts.usable} usable, {counts.passive} passive-scan only, {counts.disabled} disabled"
            )
        if iface.is_steam_frame_adapter and shutil.which("nmcli"):
            run(["nmcli", "-f", "GENERAL.STATE,GENERAL.CONNECTION", "device", "show", iface.name], check=False)

    if not any(iface.is_steam_frame_adapter for iface in interfaces):
        print_info("\nThe Steam Frame wireless adapter was not found. Is it plugged in?")


def set_runtime(country: str, timeout: float = 5) -> bool:
    """Set the global regulatory domain for this boot.

    :param country: ISO 3166-1 alpha-2 country code
    :param timeout: how long to wait for the kernel to apply the change, in seconds
    :return: whether the change was applied within the timeout
    """
    print_info(f"Setting the regulatory domain to {country} for this boot.")
    run(["iw", "reg", "set", country])
    # The kernel applies the change asynchronously.
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if get_reg_domains().global_country == country:
            return True
        time.sleep(0.2)
    print_info(f"Warning: the global regulatory domain did not change to {country} within {timeout} s.")
    return False


def update_initramfs_if_needed() -> None:
    """Update the initramfs if it contains cfg80211, as then the modprobe config is read from the initramfs."""
    initrd = pathlib.Path(f"/boot/initrd.img-{os.uname().release}")
    if not (shutil.which("lsinitramfs") and shutil.which("update-initramfs") and initrd.is_file()):
        return
    files = run(["lsinitramfs", str(initrd)], get_output=True, print_output=False)[1]
    if any(file.endswith(("/cfg80211.ko", "/cfg80211.ko.zst", "/cfg80211.ko.xz")) for file in files):
        print_info("The initramfs contains cfg80211. Updating it.")
        run(["update-initramfs", "-u"])


def validate_country(country: str) -> str:
    """Validate and normalize a country code.

    :param country: ISO 3166-1 alpha-2 country code
    :return: the country code in upper case
    :raises ValueError: if the country code is invalid
    """
    normalized = country.strip().upper()
    if not COUNTRY_PATTERN.match(normalized) or normalized == WORLD_REGDOMAIN:
        msg = f"Invalid country code: {country!r}. Give an ISO 3166-1 alpha-2 code such as FI."
        raise ValueError(msg)
    return normalized


def write_persistent(country: str, path: pathlib.Path = MODPROBE_CONF) -> bool:
    """Write the modprobe config that sets the regulatory domain at boot.

    :param country: ISO 3166-1 alpha-2 country code
    :param path: path to the config file
    :return: whether the file was changed
    """
    content = modprobe_conf_content(country)
    if path.is_file() and path.read_text() == content:
        print_info(f"{path} is already up to date.")
        return False
    print_info(f"Writing {path}")
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(content)
    tmp_path.chmod(0o644)
    tmp_path.replace(path)
    return True


def main(argv: Sequence[str] | None = None) -> None:
    """Set the regulatory domain and print the related information.

    :param argv: command-line arguments, defaults to ``sys.argv[1:]``
    """
    args = parse_args(argv)
    interfaces = list_wireless_interfaces()
    if args.status:
        print_status(interfaces)
        return

    if args.country:
        country = validate_country(args.country)
    else:
        detected = detect_country(get_reg_domains())
        if detected is None:
            print_info("Could not detect the country. Please give it with --country, e.g. --country FI.")
            sys.exit(1)
        country = validate_country(detected)
        print_info(f"Detected country: {country}")

    if os.geteuid() != 0:
        print_info("Root privileges are required. Re-running with sudo.")
        os.execvp("sudo", ["sudo", sys.executable, str(pathlib.Path(__file__).resolve()), "--country", country])

    set_runtime(country)
    if write_persistent(country):
        update_initramfs_if_needed()
    print()
    print_status(interfaces)
    print_info("\nIf the adapter is still not connected, reconnect the headset or run:")
    print_info("nmcli connection up 'Steam Frame Wireless Adapter'")


if __name__ == "__main__":
    main()
