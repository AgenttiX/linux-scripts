"""Parsers for the output of GPU tools and the GPU driver interfaces."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import typing as tp
import xml.etree.ElementTree as ET

from sysinfo.common import normalize_pci_address, parse_int, read_text, run_cmd


def parse_amd_smi() -> dict[str, dict[str, str]]:
    """Get the AMD GPU names and VRAM types with amd-smi.

    :return: dictionary from PCI address to properties
    """
    exe = shutil.which("amd-smi") or ("/opt/rocm/bin/amd-smi" if Path("/opt/rocm/bin/amd-smi").exists() else None)
    if exe is None:
        return {}
    output = run_cmd([exe, "static", "--asic", "--vram", "--bus", "--json"], timeout=30)
    if not output:
        return {}
    try:
        data = json.loads(output[output.find("["):])
    except json.JSONDecodeError:
        return {}
    if isinstance(data, dict):
        data = data.get("gpu_data", [])
    result: dict[str, dict[str, str]] = {}
    for gpu in data:
        bdf = str(gpu.get("bus", {}).get("bdf", "")).lower()
        if not bdf:
            continue
        props: dict[str, str] = {}
        name = gpu.get("asic", {}).get("market_name")
        if name and name != "N/A":
            props["name"] = name
        vram = gpu.get("vram", {})
        if vram.get("type") not in (None, "N/A", "UNKNOWN"):
            props["vram_type"] = vram["type"]
        if vram.get("vendor") not in (None, "N/A", "UNKNOWN"):
            props["vram_vendor"] = str(vram["vendor"]).capitalize()
        result[bdf] = props
    return result


def parse_kfd() -> dict[str, dict[str, str]]:
    """Get the AMD GPU LLVM targets from the KFD (ROCm kernel driver) topology.

    :return: dictionary from PCI address to properties
    """
    result: dict[str, dict[str, str]] = {}
    for node in Path("/sys/class/kfd/kfd/topology/nodes").glob("*"):
        props: dict[str, int] = {}
        for line in (read_text(node / "properties") or "").splitlines():
            key, _, value = line.partition(" ")
            if (num := parse_int(value)) is not None:
                props[key] = num
        version = props.get("gfx_target_version")
        location = props.get("location_id")
        if not version or location is None:
            continue
        major, minor, step = version // 10000, version // 100 % 100, version % 100
        addr = f"{props.get('domain', 0):04x}:{location >> 8:02x}:{(location >> 3) & 0x1F:02x}.{location & 0x7}"
        result[addr] = {"gfx_target": f"gfx{major}{minor:x}{step:x}"}
    return result


def parse_nvidia_smi() -> dict[str, dict[str, str]]:
    """Get the NVIDIA GPU details with nvidia-smi.

    :return: dictionary from PCI address (e.g. "0000:01:00.0") to properties
    """
    if shutil.which("nvidia-smi") is None:
        return {}
    output = run_cmd(["nvidia-smi", "-q", "-x"], timeout=30)
    if not output:
        return {}
    try:
        # The output of a local trusted program. Python 3.7.1+ does not resolve external entities.
        root = ET.fromstring(output)
    except ET.ParseError:
        return {}
    caps: dict[str, str] = {}
    csv = run_cmd(["nvidia-smi", "--query-gpu=pci.bus_id,compute_cap", "--format=csv,noheader"])
    for line in (csv or "").splitlines():
        bus_id, _, cap = line.partition(",")
        caps[normalize_pci_address(bus_id)] = cap.strip()
    driver_version = root.findtext("driver_version")
    result: dict[str, dict[str, str]] = {}
    for gpu in root.findall("gpu"):
        addr = normalize_pci_address(gpu.findtext("pci/pci_bus_id") or gpu.get("id", ""))
        # Newer drivers use gpu_power_readings, older ones power_readings.
        power = gpu.find("gpu_power_readings")
        if power is None:
            power = gpu.find("power_readings")

        def power_value(*tags: str, readings: ET.Element | None = power) -> str | None:
            if readings is None:
                return None
            for tag in tags:
                value = readings.findtext(tag)
                if value and value != "N/A":
                    return value
            return None

        props = {
            "name": gpu.findtext("product_name"),
            "architecture": gpu.findtext("product_architecture"),
            "vram": gpu.findtext("fb_memory_usage/total"),
            "ecc": gpu.findtext("ecc_mode/current_ecc"),
            "vbios_version": gpu.findtext("vbios_version"),
            "driver_version": driver_version,
            "compute_capability": caps.get(addr),
            "power_limit": power_value("current_power_limit", "enforced_power_limit", "power_limit"),
            "power_limit_default": power_value("default_power_limit"),
            "power_limit_min": power_value("min_power_limit"),
            "power_limit_max": power_value("max_power_limit"),
        }
        result[addr] = {key: value for key, value in props.items() if value and value != "N/A"}
    return result


def parse_vulkaninfo(text: str | None = None) -> list[dict[str, tp.Any]]:
    """Get the Vulkan devices with vulkaninfo --summary.

    :param text: output of vulkaninfo --summary, run if not given
    :return: list of device properties
    """
    if text is None:
        text = run_cmd(["vulkaninfo", "--summary"], timeout=60)
    if not text or "Devices:" not in text:
        return []
    devices: list[dict[str, tp.Any]] = []
    current: dict[str, tp.Any] | None = None
    for line in text[text.index("Devices:"):].splitlines():
        if re.match(r"^GPU\d+:", line):
            current = {}
            devices.append(current)
        elif current is not None and "=" in line:
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            current[key] = parse_int(value) if key in ("vendorID", "deviceID") else value
    return devices


def strip_vulkan_name(name: str | None) -> str | None:
    """Remove the driver suffix from a Vulkan device name, e.g. "AMD Radeon VII (RADV VEGA20)".

    :param name: Vulkan device name
    :return: GPU name
    """
    if not name:
        return None
    return re.sub(r"\s*\((RADV|Turnip|NVK|DXVK)[^)]*\)$", "", name, flags=re.IGNORECASE) or None


def vulkan_driver(vk: dict[str, tp.Any]) -> str | None:
    """Format the Vulkan driver of a device.

    :param vk: vulkaninfo device properties
    :return: e.g. "radv, Mesa 26.0.8, Vulkan 1.4.335"
    """
    if not vk:
        return None
    parts = [vk.get("driverName"), vk.get("driverInfo")]
    if vk.get("apiVersion"):
        parts.append(f"Vulkan {vk['apiVersion']}")
    return ", ".join(str(part) for part in parts if part) or None
