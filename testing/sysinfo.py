#!/usr/bin/env python3
"""Print the hardware and OS information needed for a performance testing report.

The information is collected from sysfs, procfs, the udev database and common tools
(lscpu, lspci, nvidia-smi, amd-smi, vulkaninfo, journalctl), whichever are available.
Most of it is available without root access.
When run with sudo, dmidecode is used to fill in the RAM module details that the udev database may lack.
Serial numbers are deliberately left out, so that the output can be published.

Usage: ``./testing/sysinfo.py [--json] [output_file]``

This script uses only the Python standard library and does not import anything from this repository,
so that it can be copied to and run on any Linux system with Python 3.12+.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import dataclasses
import datetime
import json
import logging
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess as sp
import sys
import typing as tp
import xml.etree.ElementTree as ET

logger: logging.Logger = logging.getLogger(__name__)

#: Words that are written in a specific case in the text output
ACRONYMS: dict[str, str] = {
    "bios": "BIOS",
    "cpu": "CPU",
    "cpus": "CPUs",
    "cuda": "CUDA",
    "ecc": "ECC",
    "edac": "EDAC",
    "gfx": "GFX",
    "gpu": "GPU",
    "gpus": "GPUs",
    "id": "ID",
    "isa": "ISA",
    "mhz": "MHz",
    "mts": "MT/s",
    "npu": "NPU",
    "npus": "NPUs",
    "nvidia": "NVIDIA",
    "numa": "NUMA",
    "os": "OS",
    "pci": "PCI",
    "pcie": "PCIe",
    "ram": "RAM",
    "rocm": "ROCm",
    "simd": "SIMD",
    "smbios": "SMBIOS",
    "sve": "SVE",
    "vbios": "VBIOS",
    "vram": "VRAM",
}
#: CPU parts of the "CPU implementer" 0x41 (Arm Ltd.) in /proc/cpuinfo
ARM_CPU_PARTS: dict[int, str] = {
    0xD03: "Cortex-A53",
    0xD04: "Cortex-A35",
    0xD05: "Cortex-A55",
    0xD07: "Cortex-A57",
    0xD08: "Cortex-A72",
    0xD09: "Cortex-A73",
    0xD0A: "Cortex-A75",
    0xD0B: "Cortex-A76",
    0xD0C: "Neoverse-N1",
    0xD0D: "Cortex-A77",
    0xD40: "Neoverse-V1",
    0xD41: "Cortex-A78",
    0xD44: "Cortex-X1",
    0xD46: "Cortex-A510",
    0xD47: "Cortex-A710",
    0xD48: "Cortex-X2",
    0xD49: "Neoverse-N2",
    0xD4B: "Cortex-A78C",
    0xD4D: "Cortex-A715",
    0xD4E: "Cortex-X3",
    0xD4F: "Neoverse-V2",
    0xD80: "Cortex-A520",
    0xD81: "Cortex-A720",
    0xD82: "Cortex-X4",
    0xD84: "Neoverse-V3",
    0xD85: "Cortex-X925",
    0xD87: "Cortex-A725",
    0xD8E: "Neoverse-N3",
}
#: Other "CPU implementer" values in /proc/cpuinfo
ARM_CPU_IMPLEMENTERS: dict[int, str] = {
    0x41: "Arm",
    0x42: "Broadcom",
    0x43: "Cavium",
    0x46: "Fujitsu",
    0x48: "HiSilicon",
    0x4E: "NVIDIA",
    0x51: "Qualcomm",
    0x61: "Apple",
    0x6D: "Microsoft",
    0xC0: "Ampere",
}
#: CPU flags that are relevant for performance, especially for AI inference
ARM_FEATURES: tuple[str, ...] = (
    "asimd", "asimddp", "asimdhp", "fphp", "i8mm", "bf16", "sve", "sve2", "svei8mm", "svebf16", "sme", "sme2",
)
#: Names of the ARM features in the output
ARM_FEATURE_NAMES: dict[str, str] = {
    "asimd": "NEON", "asimddp": "dotprod", "asimdhp": "fp16 (SIMD)", "fphp": "fp16", "i8mm": "i8mm", "bf16": "bf16",
    "sve": "SVE", "sve2": "SVE2", "svei8mm": "SVE i8mm", "svebf16": "SVE bf16", "sme": "SME", "sme2": "SME2",
}
#: Placeholder values that some manufacturers leave in the DMI tables
DMI_RUBBISH: frozenset[str] = frozenset({
    "", "default string", "none", "not applicable", "not specified", "o.e.m.", "oem", "sku",
    "system manufacturer", "system product name", "system serial number", "system version",
    "to be filled by o.e.m.", "unknown",
})
#: Fields that are only included in the JSON output, as the text output has a summary of them
JSON_ONLY_FIELDS: frozenset[str] = frozenset({"modules"})
#: Kernel drivers of NPUs
NPU_DRIVERS: frozenset[str] = frozenset({"amdxdna", "intel_vpu", "qaic", "rknpu", "rocket"})
#: NVIDIA GPU codename prefixes
NVIDIA_ARCHITECTURES: dict[str, str] = {
    "GF": "Fermi",
    "GK": "Kepler",
    "GM": "Maxwell",
    "GP": "Pascal",
    "GV": "Volta",
    "TU": "Turing",
    "GA": "Ampere",
    "AD": "Ada Lovelace",
    "GH": "Hopper",
    "GB": "Blackwell",
}
#: NVIDIA VRAM types that cannot be queried from the driver: (product name regex, VRAM type)
NVIDIA_VRAM_TYPES: tuple[tuple[str, str], ...] = (
    (r"RTX PRO \d+ Blackwell|RTX 50\d0", "GDDR7"),
    (r"RTX 40(80|90)|RTX 3070 Ti|RTX 30(80|90)", "GDDR6X"),
    (r"RTX 40[67]0|RTX 30[56]0|RTX 3070\b|RTX 20\d0|GTX 16\d0", "GDDR6"),
    (r"RTX A\d{4}|RTX \d{4} Ada|Quadro RTX|\bL4\b|\bL40", "GDDR6"),
    (r"GTX 10(80|80 Ti)|TITAN Xp?\b", "GDDR5X"),
    (r"GTX 10[567]0|GTX 9\d0|GTX 7\d0|GTX TITAN\b|GTX TITAN (Black|Z)", "GDDR5"),
    (r"\bH100|\bH200|\bGH200", "HBM3"),
    (r"\bA100|\bA30\b", "HBM2e"),
    (r"\bV100|TITAN V|\bP100", "HBM2"),
    (r"\bB200|\bB300|\bGB200", "HBM3e"),
)
#: PCIe link speeds in GT/s and the corresponding PCIe versions
PCIE_GENERATIONS: dict[float, int] = {2.5: 1, 5.0: 2, 8.0: 3, 16.0: 4, 32.0: 5, 64.0: 6, 128.0: 7}
#: PCI device address format
PCI_ADDRESS: re.Pattern[str] = re.compile(r"^[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7]$")
#: x86 CPU flags that are relevant for performance, especially for AI inference
X86_FEATURES: tuple[str, ...] = (
    "sse4_2", "avx", "avx2", "fma", "f16c", "avx_vnni", "avx_vnni_int8", "avx_ne_convert",
    "avx512f", "avx512bw", "avx512vl", "avx512_vnni", "avx512_bf16", "avx512_fp16", "avx10",
    "amx_tile", "amx_bf16", "amx_int8", "amx_fp16", "aes", "sha_ni",
)
#: Intel family 6 CPU models
INTEL_MODELS: dict[int, str] = {
    0x3C: "Haswell", 0x3F: "Haswell", 0x45: "Haswell", 0x46: "Haswell",
    0x3D: "Broadwell", 0x47: "Broadwell", 0x4F: "Broadwell", 0x56: "Broadwell",
    0x4E: "Skylake", 0x5E: "Skylake", 0x55: "Skylake/Cascade Lake/Cooper Lake",
    0x8E: "Kaby Lake/Coffee Lake/Whiskey Lake/Amber Lake", 0x9E: "Kaby Lake/Coffee Lake",
    0xA5: "Comet Lake", 0xA6: "Comet Lake", 0x66: "Cannon Lake",
    0x7D: "Ice Lake", 0x7E: "Ice Lake", 0x6A: "Ice Lake-SP", 0x6C: "Ice Lake-SP",
    0x8C: "Tiger Lake", 0x8D: "Tiger Lake", 0xA7: "Rocket Lake",
    0x97: "Alder Lake", 0x9A: "Alder Lake", 0xBE: "Alder Lake-N",
    0xB7: "Raptor Lake", 0xBA: "Raptor Lake", 0xBF: "Raptor Lake",
    0x8F: "Sapphire Rapids", 0xCF: "Emerald Rapids", 0xAD: "Granite Rapids", 0xAE: "Granite Rapids",
    0xAF: "Sierra Forest", 0xDD: "Clearwater Forest",
    0xAA: "Meteor Lake", 0xAC: "Meteor Lake", 0xBD: "Lunar Lake",
    0xB5: "Arrow Lake", 0xC5: "Arrow Lake", 0xC6: "Arrow Lake", 0xCC: "Panther Lake",
    0x5C: "Goldmont (Apollo Lake)", 0x7A: "Goldmont Plus (Gemini Lake)", 0x96: "Tremont (Elkhart Lake)",
    0x9C: "Tremont (Jasper Lake)",
}


@dataclasses.dataclass(frozen=True, slots=True)
class BoardInfo:
    """Information about the computer and its motherboard."""

    computer: str | None
    motherboard: str | None
    bios: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class CoreGroup:
    """A group of identical CPU cores."""

    core_type: str
    cpus: str
    cores: int
    threads: int
    max_frequency_mhz: int | None


@dataclasses.dataclass(frozen=True, slots=True)
class CPUInfo:
    """Information about the CPU(s)."""

    model: str | None
    vendor: str | None
    architecture: str
    microarchitecture: str | None
    compiler_march: str | None
    sockets: int
    cores: int
    threads: int
    core_groups: list[CoreGroup]
    max_frequency_mhz: int | None
    min_frequency_mhz: int | None
    caches: list[str]
    features: list[str]
    isa_level: str | None
    sve_vector_length_bits: int | None
    numa_nodes: int | None
    virtual_machine: bool


@dataclasses.dataclass(frozen=True, slots=True)
class GPUInfo:
    """Information about a GPU."""

    name: str
    vendor: str | None
    codename: str | None
    architecture: str | None
    gfx_target: str | None
    compute_capability: str | None
    integrated: bool | None
    vram: str | None
    vram_type: str | None
    vram_ecc: str | None
    kernel_driver: str | None
    driver_version: str | None
    vulkan_driver: str | None
    vbios_version: str | None
    power_limit: str | None
    power_limit_default: str | None
    power_limit_min: str | None
    power_limit_max: str | None
    pci_address: str | None
    pcie_link_max: str | None
    pcie_link_current: str | None
    gpu_unlock: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class MemoryModule:
    """Information about a RAM module (DIMM)."""

    locator: str | None
    bank_locator: str | None
    size: str
    type: str | None
    type_detail: str | None
    form_factor: str | None
    speed_mts: int | None
    configured_speed_mts: int | None
    manufacturer: str | None
    part_number: str | None
    rank: int | None
    ecc_width: bool | None


@dataclasses.dataclass(frozen=True, slots=True)
class MemoryInfo:
    """Information about the system RAM."""

    total_visible_to_os: str | None
    total_installed: str | None
    type: str | None
    speed: str | None
    channels: int | None
    slots_populated: str | None
    module_summary: list[str]
    ranks: str | None
    ecc: str | None
    modules: list[MemoryModule]
    source: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class NPUInfo:
    """Information about an NPU."""

    name: str
    kernel_driver: str | None
    pci_address: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class OSInfo:
    """Information about the operating system."""

    name: str | None
    version: str | None
    build: str | None
    variant: str | None
    kernel: str
    hostname: str


@dataclasses.dataclass(frozen=True, slots=True)
class SoftwareInfo:
    """Versions of the GPU compute software stacks."""

    nvidia_driver: str | None
    cuda: str | None
    rocm: str | None
    mesa: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class SystemInfo:
    """All the collected information."""

    generated: str
    run_as_root: bool
    os: OSInfo
    board: BoardInfo
    cpu: CPUInfo
    memory: MemoryInfo
    gpus: list[GPUInfo]
    npus: list[NPUInfo]
    software: SoftwareInfo
    notes: list[str]


def amd_architecture(gfx_target: str | None, codename: str | None) -> str | None:
    """Get the architecture of an AMD GPU.

    :param gfx_target: LLVM target, e.g. "gfx906"
    :param codename: PCI codename, e.g. "Vega 20" or "Navi 31"
    :return: architecture name
    """
    if gfx_target:
        exact = {"gfx908": "CDNA 1", "gfx90a": "CDNA 2", "gfx950": "CDNA 4"}
        if gfx_target in exact:
            return exact[gfx_target]
        prefixes = (
            ("gfx94", "CDNA 3"), ("gfx90", "GCN 5 (Vega)"), ("gfx8", "GCN 3/4"), ("gfx7", "GCN 2"),
            ("gfx101", "RDNA 1"), ("gfx103", "RDNA 2"), ("gfx115", "RDNA 3.5"), ("gfx11", "RDNA 3"),
            ("gfx12", "RDNA 4"),
        )
        for prefix, arch in prefixes:
            if gfx_target.startswith(prefix):
                return arch
    if codename:
        if match := re.search(r"Navi (\d)\d", codename):
            return f"RDNA {match.group(1)}"
        if "Vega" in codename:
            return "GCN 5 (Vega)"
        if re.search(r"Ellesmere|Polaris|Baffin|Lexa", codename):
            return "GCN 4 (Polaris)"
    return None


def amd_microarchitecture(family: int, model: int) -> str | None:  # noqa: PLR0911
    """Get the microarchitecture of an AMD CPU.

    :param family: CPU family
    :param model: CPU model
    :return: microarchitecture name
    """
    if family == 0x15:  # noqa: PLR2004
        return "Bulldozer family"
    if family == 0x17:  # noqa: PLR2004
        if model in (0x08, 0x18):
            return "Zen+"
        return "Zen" if model < 0x30 else "Zen 2"  # noqa: PLR2004
    if family == 0x19:  # noqa: PLR2004
        ranges = (
            (0x00, 0x0F, "Zen 3"), (0x10, 0x1F, "Zen 4"), (0x20, 0x3F, "Zen 3"), (0x40, 0x4F, "Zen 3+"),
            (0x50, 0x5F, "Zen 3"), (0x60, 0x7F, "Zen 4"), (0xA0, 0xAF, "Zen 4c"),
        )
        for start, end, name in ranges:
            if start <= model <= end:
                return name
        return "Zen 3/4"
    if family == 0x1A:  # noqa: PLR2004
        return "Zen 5"
    return None


def amd_vram_type(codename: str | None, gfx_target: str | None) -> str | None:
    """Guess the VRAM type of an AMD GPU when amd-smi is not available.

    :param codename: PCI codename
    :param gfx_target: LLVM target
    :return: VRAM type
    """
    if codename and re.search(r"Vega 10|Vega 20|Arcturus", codename):
        return "HBM2"
    if codename and "Fiji" in codename:
        return "HBM"
    if gfx_target in ("gfx908", "gfx90a"):
        return "HBM2e"
    if gfx_target and gfx_target.startswith("gfx94"):
        return "HBM3"
    return None


def check_gpu_unlock(pci_address: str, kernel_log: list[str] | None) -> str:
    """Check whether an NVIDIA GPU has been unlocked by the gpu_unlock kernel module.

    :param pci_address: PCI address of the GPU, e.g. "0000:01:00.0"
    :param kernel_log: kernel log lines of the current boot, or None if not readable
    :return: description of the unlock status
    """
    module_loaded = Path("/sys/module/gpu_unlock").exists()
    if kernel_log is None:
        if module_loaded:
            return "unknown: the gpu_unlock module is loaded, but the kernel log is not readable (run with sudo)"
        return "no (the gpu_unlock module is not loaded)"
    lines = [line for line in kernel_log if pci_address in line and "gpu_unlock:" in line]
    unlocks = [line for line in lines if "gpu_unlock: unlocked" in line]
    failures = [line for line in lines if (match := re.search(r"\bret=(-?\d+)", line)) and match.group(1) != "0"]
    if unlocks:
        resumes = sum("after resume" in line for line in unlocks)
        text = "yes" + (f" (re-applied after {resumes} resume(s))" if resumes else "")
        if failures:
            text += f", but {len(failures)} unlock pass(es) failed with a non-zero ret"
        return text
    if module_loaded:
        return "no: the gpu_unlock module is loaded, but there is no unlock message for this GPU"
    return "no (the gpu_unlock module is not loaded)"


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


def format_text(info: SystemInfo) -> str:
    """Format the information as indented text.

    :param info: collected information
    :return: text output
    """
    data = dataclasses.asdict(info)
    lines = [f"System information (generated {data.pop('generated')}, run as root: {data.pop('run_as_root')})"]
    notes = data.pop("notes")
    for key, value in data.items():
        if value in (None, [], {}):
            continue
        lines.append("")
        lines.append(f"{label(key)}:")
        if isinstance(value, list):
            for i, item in enumerate(value):
                lines.append(f"  [{i}]")
                lines.extend(format_text_value(item, 2))
        else:
            lines.extend(format_text_value(value, 1))
    if notes:
        lines.append("")
        lines.append("Notes:")
        lines.extend(f"  - {note}" for note in notes)
    return "\n".join(lines) + "\n"


def format_text_value(value: tp.Any, indent: int) -> list[str]:
    """Format a dictionary as indented "key: value" lines, skipping empty values.

    :param value: dictionary from dataclasses.asdict
    :param indent: indentation level
    :return: lines
    """
    pad = "  " * indent
    lines: list[str] = []
    for key, val in value.items():
        if val in (None, [], {}, "") or key in JSON_ONLY_FIELDS:
            continue
        if isinstance(val, list) and val and isinstance(val[0], dict):
            lines.append(f"{pad}{label(key)}:")
            for i, item in enumerate(val):
                lines.append(f"{pad}  [{i}]")
                lines.extend(format_text_value(item, indent + 2))
        elif isinstance(val, list):
            lines.append(f"{pad}{label(key)}: {', '.join(str(v) for v in val)}")
        elif isinstance(val, bool):
            lines.append(f"{pad}{label(key)}: {'yes' if val else 'no'}")
        else:
            lines.append(f"{pad}{label(key)}: {val}")
    return lines


def get_board_info() -> BoardInfo:
    """Get the computer and motherboard models from DMI or the device tree."""
    dmi = Path("/sys/class/dmi/id")
    if not dmi.exists():
        model = read_text("/sys/firmware/devicetree/base/model")
        return BoardInfo(computer=model.rstrip("\x00") if model else None, motherboard=None, bios=None)

    def field(name: str) -> str | None:
        return dmi_value(read_text(dmi / name))

    def join(*parts: str | None) -> str | None:
        unique: list[str] = []
        for part in parts:
            if part and part not in unique:
                unique.append(part)
        return " ".join(unique) or None

    product_name = field("product_name")
    product_version = field("product_version")
    if not product_name and not product_version:
        # Only the vendor is not informative. This is typical of custom-built desktops.
        product_name = "(no product name, probably a custom-built computer)"
    # Lenovo uses the product name for the machine type and the version for the model name.
    if product_name and product_version and field("sys_vendor") == "LENOVO":
        computer = join(field("sys_vendor"), product_version, f"({product_name})")
    else:
        computer = join(field("sys_vendor"), product_name, product_version)
    motherboard = join(field("board_vendor"), field("board_name"))
    board_version = field("board_version")
    if motherboard and board_version:
        motherboard += f" (version {board_version})"
    bios_version = field("bios_version")
    bios_date = field("bios_date")
    bios = join(field("bios_vendor"), bios_version, f"({bios_date})" if bios_date else None)
    return BoardInfo(computer=computer, motherboard=motherboard, bios=bios)


def get_cpu_info() -> CPUInfo:  # noqa: PLR0912, PLR0915
    """Get information about the CPU(s)."""
    cpuinfo = parse_cpuinfo()
    first = cpuinfo[0] if cpuinfo else {}
    lscpu = parse_lscpu()
    machine = platform.machine()
    is_arm = machine in ("aarch64", "arm64") or machine.startswith("arm")

    online = parse_cpu_list(read_text("/sys/devices/system/cpu/online") or "0")
    cpu_dir = Path("/sys/devices/system/cpu")
    p_cores = set(parse_cpu_list(read_text("/sys/devices/cpu_core/cpus") or ""))
    e_cores = set(parse_cpu_list(read_text("/sys/devices/cpu_atom/cpus") or ""))
    cpuinfo_by_cpu = {int(entry["processor"]): entry for entry in cpuinfo if entry.get("processor", "").isdigit()}

    core_ids: set[tuple[str | None, ...]] = set()
    packages: set[str | None] = set()
    groups: dict[tuple[str, int | None], list[tuple[int, tuple[str | None, ...]]]] = {}
    max_freqs: list[int] = []
    min_freqs: list[int] = []
    for cpu in online:
        topo = cpu_dir / f"cpu{cpu}" / "topology"
        package = read_text(topo / "physical_package_id")
        core_key = (package, read_text(topo / "cluster_id") if is_arm else None, read_text(topo / "core_id"))
        core_ids.add(core_key)
        packages.add(package)
        max_freq = read_int(cpu_dir / f"cpu{cpu}" / "cpufreq" / "cpuinfo_max_freq")
        min_freq = read_int(cpu_dir / f"cpu{cpu}" / "cpufreq" / "cpuinfo_min_freq")
        if max_freq:
            max_freqs.append(max_freq // 1000)
        if min_freq:
            min_freqs.append(min_freq // 1000)
        if cpu in p_cores:
            core_type = "P-core"
        elif cpu in e_cores:
            core_type = "E-core"
        elif is_arm:
            core_type = arm_core_name(cpuinfo_by_cpu.get(cpu, {})) or "unknown"
        else:
            core_type = first.get("model name", "unknown")
        # x86 CPUs may report slightly different maximum frequencies for the preferred cores,
        # so they are grouped only by the core type.
        group_key = (core_type, max_freq // 1000 if (is_arm and max_freq) else None)
        groups.setdefault(group_key, []).append((cpu, core_key))

    core_groups: list[CoreGroup] = []
    if len(groups) > 1:
        for (core_type, freq), members in groups.items():
            freqs = [
                f // 1000 for cpu, _ in members
                if (f := read_int(cpu_dir / f"cpu{cpu}" / "cpufreq" / "cpuinfo_max_freq"))
            ]
            core_groups.append(CoreGroup(
                core_type=core_type,
                cpus=compress_ranges(cpu for cpu, _ in members),
                cores=len({key for _, key in members}),
                threads=len(members),
                max_frequency_mhz=freq if freq is not None else (max(freqs) if freqs else None),
            ))
        core_groups.sort(key=lambda group: -(group.max_frequency_mhz or 0))

    flags = set((first.get("flags") or first.get("Features") or "").split())
    if is_arm:
        features = [ARM_FEATURE_NAMES[flag] for flag in ARM_FEATURES if flag in flags]
        isa_level = None
    else:
        features = [flag for flag in X86_FEATURES if flag in flags]
        isa_level = x86_64_isa_level(flags) if machine == "x86_64" else None
    sve_length = read_int("/proc/sys/abi/sve_default_vector_length")

    model = first.get("model name") or lscpu.get("Model name")
    vendor = first.get("vendor_id") or lscpu.get("Vendor ID")
    microarch: str | None = None
    if is_arm:
        names = list(dict.fromkeys(group[0] for group in groups))
        if not model:
            implementer = parse_int(first.get("CPU implementer"))
            vendor = ARM_CPU_IMPLEMENTERS.get(implementer, vendor) if implementer is not None else vendor
            soc = read_text("/sys/firmware/devicetree/base/model")
            model = ", ".join(names) + (f" ({soc.rstrip(chr(0))})" if soc else "")
        microarch = ", ".join(names)
    elif "family" in lscpu or "cpu family" in first:
        family = parse_int(first.get("cpu family"))
        cpu_model = parse_int(first.get("model"))
        if family is not None and cpu_model is not None:
            if vendor in ("AuthenticAMD", "HygonGenuine"):
                microarch = amd_microarchitecture(family, cpu_model)
            elif vendor == "GenuineIntel" and family == 6:  # noqa: PLR2004
                microarch = INTEL_MODELS.get(cpu_model)

    numa_dirs = list(Path("/sys/devices/system/node").glob("node[0-9]*"))
    return CPUInfo(
        model=model,
        vendor=vendor,
        architecture=machine,
        microarchitecture=microarch,
        compiler_march=gcc_march(),
        sockets=len(packages),
        cores=len(core_ids),
        threads=len(online),
        core_groups=core_groups,
        max_frequency_mhz=max(max_freqs) if max_freqs else None,
        min_frequency_mhz=min(min_freqs) if min_freqs else None,
        caches=get_caches(),
        features=features,
        isa_level=isa_level,
        sve_vector_length_bits=sve_length * 8 if sve_length else None,
        numa_nodes=len(numa_dirs) or None,
        virtual_machine="hypervisor" in flags,
    )


def arm_core_name(entry: dict[str, str]) -> str | None:
    """Get the name of an ARM CPU core from its /proc/cpuinfo entry.

    :param entry: /proc/cpuinfo fields of the core
    :return: core name
    """
    implementer = parse_int(entry.get("CPU implementer"))
    part = parse_int(entry.get("CPU part"))
    if implementer is None or part is None:
        return None
    if implementer == 0x41 and part in ARM_CPU_PARTS:  # noqa: PLR2004
        return ARM_CPU_PARTS[part]
    return f"{ARM_CPU_IMPLEMENTERS.get(implementer, hex(implementer))} part {part:#x}"


def gcc_march() -> str | None:
    """Get the CPU target that GCC selects with -march=native (or -mcpu=native on ARM)."""
    output = run_cmd(["gcc", "-march=native", "-Q", "--help=target"])
    if output is None:
        output = run_cmd(["gcc", "-mcpu=native", "-Q", "--help=target"])
    if output is None:
        return None
    for key in ("-march=", "-mcpu="):
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == key and parts[1] not in ("native", "[default]"):  # noqa: PLR2004
                return parts[1]
    return None


def get_caches() -> list[str]:
    """Get the CPU cache sizes with lscpu."""
    output = run_cmd(["lscpu", "-J", "-C"])
    if not output:
        return []
    try:
        caches = json.loads(output).get("caches", [])
    except json.JSONDecodeError:
        return []
    result: list[str] = []
    for cache in caches:
        name = cache.get("name")
        all_size = cache.get("all-size")
        one_size = cache.get("one-size")
        if not name or not all_size:
            continue
        text = f"{name} {all_size}"
        if one_size and one_size != all_size:
            text += f" ({one_size} each)"
        result.append(text)
    return result


def get_gpus(kernel_log: list[str] | None, notes: list[str]) -> list[GPUInfo]:  # noqa: PLR0912, PLR0915
    """Get information about the GPUs.

    :param kernel_log: kernel log lines of the current boot, or None if not readable
    :param notes: list to which notes about missing information are appended
    :return: GPUs
    """
    nvidia = parse_nvidia_smi()
    amd_smi = parse_amd_smi()
    kfd = parse_kfd()
    vulkan = parse_vulkaninfo()
    gpus: list[GPUInfo] = []

    for dev in sorted(Path("/sys/bus/pci/devices").iterdir()):
        pci_class = read_text(dev / "class") or ""
        if not pci_class.startswith("0x03"):
            continue
        addr = dev.name
        vendor_id = parse_int(read_text(dev / "vendor"))
        device_id = parse_int(read_text(dev / "device"))
        lspci = parse_lspci(addr)
        vendor = lspci.get("Vendor") or (f"{vendor_id:#06x}" if vendor_id is not None else None)
        codename, pci_name = split_pci_name(lspci.get("Device"))
        driver = driver_name(dev)
        vk = next((v for v in vulkan if v.get("vendorID") == vendor_id and v.get("deviceID") == device_id), {})
        nv = nvidia.get(addr.lower(), {})
        amd = amd_smi.get(addr.lower(), {})
        kfd_node = kfd.get(addr.lower(), {})

        name = nv.get("name") or amd.get("name") or strip_vulkan_name(vk.get("deviceName")) or pci_name
        name = name or codename or f"{vendor} {device_id:#06x}"
        integrated = None
        if vk.get("deviceType"):
            integrated = "INTEGRATED" in vk["deviceType"]

        gfx_target = kfd_node.get("gfx_target")
        architecture: str | None = None
        compute_capability = nv.get("compute_capability")
        vram: str | None = None
        vram_type: str | None = None
        vram_ecc: str | None = None
        driver_version: str | None = None
        unlock: str | None = None
        power = hwmon_power_limits(dev)
        if vendor_id == 0x10DE:  # noqa: PLR2004
            architecture = nv.get("architecture")
            if not architecture and codename:
                architecture = NVIDIA_ARCHITECTURES.get(codename[:2])
            vram_bytes = parse_size(nv.get("vram"))
            vram = format_bytes(vram_bytes) if vram_bytes else nv.get("vram")
            vram_type = nvidia_vram_type(name)
            vram_ecc = nv.get("ecc")
            driver_version = nv.get("driver_version") or read_text("/sys/module/nvidia/version")
            if driver != "nvidia":
                driver_version = None
            unlock = check_gpu_unlock(addr, kernel_log)
            power = {key: nv[key] for key in ("power_limit", "power_limit_default", "power_limit_min",
                                              "power_limit_max") if key in nv} or power
        elif vendor_id == 0x1002:  # noqa: PLR2004
            architecture = amd_architecture(gfx_target, codename)
            vram_bytes = read_int(dev / "mem_info_vram_total")
            if vram_bytes:
                vram = format_bytes(vram_bytes)
            vram_type = amd.get("vram_type") or amd_vram_type(codename, gfx_target)
            if amd.get("vram_vendor"):
                vram_type = f"{vram_type or 'unknown type'} ({amd['vram_vendor']})"
            if driver:
                driver_version = f"{driver} (kernel {platform.release()})"
        elif driver:
            driver_version = f"{driver} (kernel {platform.release()})"
        if integrated and not vram:
            vram = "shared with the system RAM"
        elif integrated and vram:
            vram = f"{vram} carve-out, shared with the system RAM"

        if driver is None:
            notes.append(f"The GPU {name} ({addr}) has no kernel driver loaded, so most of its details are missing.")
        gpus.append(GPUInfo(
            name=name,
            vendor=vendor,
            codename=codename,
            architecture=architecture,
            gfx_target=gfx_target,
            compute_capability=compute_capability,
            integrated=integrated,
            vram=vram,
            vram_type=vram_type,
            vram_ecc=vram_ecc,
            kernel_driver=driver,
            driver_version=driver_version,
            vulkan_driver=vulkan_driver(vk),
            vbios_version=nv.get("vbios_version") or read_text(dev / "vbios_version"),
            power_limit=power.get("power_limit"),
            power_limit_default=power.get("power_limit_default"),
            power_limit_min=power.get("power_limit_min"),
            power_limit_max=power.get("power_limit_max"),
            pci_address=addr,
            pcie_link_max=pcie_link(dev, current=False),
            pcie_link_current=pcie_link(dev, current=True),
            gpu_unlock=unlock,
        ))

    # Non-PCI GPUs, e.g. Qualcomm Adreno in ARM SoCs
    for vk in vulkan:
        if vk.get("deviceType", "").endswith("_CPU"):
            continue
        if any(gpu.integrated is not None and gpu.name == strip_vulkan_name(vk.get("deviceName")) for gpu in gpus):
            continue
        pci_device_ids = {read_int(Path("/sys/bus/pci/devices", gpu.pci_address, "device"))
                          for gpu in gpus if gpu.pci_address}
        if vk.get("deviceID") in pci_device_ids:
            continue
        gpus.append(GPUInfo(
            name=strip_vulkan_name(vk.get("deviceName")) or "unknown",
            vendor=None, codename=None, architecture=None, gfx_target=None, compute_capability=None,
            integrated="INTEGRATED" in vk.get("deviceType", ""),
            vram="shared with the system RAM" if "INTEGRATED" in vk.get("deviceType", "") else None,
            vram_type=None, vram_ecc=None, kernel_driver=soc_gpu_driver(), driver_version=None,
            vulkan_driver=vulkan_driver(vk), vbios_version=None,
            power_limit=None, power_limit_default=None, power_limit_min=None, power_limit_max=None, pci_address=None,
            pcie_link_max=None, pcie_link_current=None, gpu_unlock=None,
        ))
    if not vulkan and shutil.which("vulkaninfo") is None:
        notes.append("vulkaninfo is not installed (apt install vulkan-tools), so the Vulkan drivers are missing.")
    return gpus


def get_kernel_log() -> list[str] | None:
    """Get the kernel log of the current boot.

    :return: log lines, or None if the log is not readable
    """
    output = run_cmd(["journalctl", "-k", "-b", "--no-pager", "-q", "-o", "cat"], timeout=60)
    if output:
        return output.splitlines()
    output = run_cmd(["dmesg"])
    if output:
        return output.splitlines()
    return None


def get_memory_info(notes: list[str]) -> MemoryInfo:
    """Get information about the system RAM.

    :param notes: list to which notes about missing information are appended
    :return: RAM information
    """
    meminfo = read_text("/proc/meminfo") or ""
    match = re.search(r"^MemTotal:\s+(\d+) kB", meminfo, re.MULTILINE)
    visible = format_bytes(int(match.group(1)) * 1024) if match else None

    modules, array_ecc, slots = memory_from_udev()
    source = "udev database (SMBIOS)" if modules else None
    if not modules and os.geteuid() == 0:
        modules, array_ecc, slots = memory_from_dmidecode()
        source = "dmidecode (SMBIOS)" if modules else None
    if not modules:
        if os.geteuid() == 0:
            notes.append("No RAM module information is available in the SMBIOS tables.")
        else:
            notes.append("The RAM module details are not available without root access. Run with sudo to get them.")

    installed = [m for m in modules if m.size != "none"]
    installed_bytes = sum(parse_size(m.size) or 0 for m in installed)
    types = sorted({m.type for m in installed if m.type})
    speeds = sorted({speed for m in installed if (speed := m.configured_speed_mts or m.speed_mts)})
    rated = sorted({m.speed_mts for m in installed if m.speed_mts})
    speed: str | None = None
    if speeds:
        speed = ", ".join(f"{t}-{s}" if len(types) == 1 else str(s) for s in speeds for t in types[:1]) + " MT/s"
        if rated and rated != speeds:
            speed += f" (rated {', '.join(str(r) for r in rated)} MT/s)"
    ranks = sorted({m.rank for m in installed if m.rank})
    rank_names = {1: "single-rank", 2: "dual-rank", 4: "quad-rank", 8: "octal-rank"}
    edac = edac_status()
    ecc_parts: list[str] = []
    if array_ecc:
        ecc_parts.append(f"motherboard: {array_ecc}")
    widths = {m.ecc_width for m in installed if m.ecc_width is not None}
    if widths:
        ecc_parts.append("modules: " + ("ECC" if widths == {True} else "non-ECC" if widths == {False} else "mixed"))
    if edac:
        ecc_parts.append(edac)

    return MemoryInfo(
        total_visible_to_os=visible,
        total_installed=format_bytes(installed_bytes) if installed_bytes else None,
        type=memory_type(installed),
        speed=speed,
        channels=memory_channels(installed) if installed else None,
        slots_populated=f"{len(installed)} of {slots}" if slots else None,
        module_summary=memory_module_summary(installed),
        ranks=", ".join(rank_names.get(r, f"{r}-rank") for r in ranks) or None,
        ecc="; ".join(ecc_parts) or None,
        modules=installed,
        source=source,
    )


def get_npus() -> list[NPUInfo]:
    """Get information about NPUs (neural processing units)."""
    npus: list[NPUInfo] = []
    seen: set[str] = set()
    candidates = [(accel / "device").resolve() for accel in sorted(Path("/sys/class/accel").glob("accel*"))]
    candidates.extend(
        dev.resolve() for dev in sorted(Path("/sys/bus/pci/devices").iterdir())
        if (read_text(dev / "class") or "").startswith("0x1200") or driver_name(dev) in NPU_DRIVERS
    )
    for dev in candidates:
        if str(dev) in seen:
            continue
        seen.add(str(dev))
        driver = driver_name(dev)
        if PCI_ADDRESS.match(dev.name):
            lspci = parse_lspci(dev.name)
            codename, pci_name = split_pci_name(lspci.get("Device"))
            vendor = lspci.get("Vendor")
            name = " ".join(part for part in (vendor, pci_name or codename) if part) or dev.name
            npus.append(NPUInfo(name=name, kernel_driver=driver, pci_address=dev.name))
        else:
            npus.append(NPUInfo(name=dev.name, kernel_driver=driver, pci_address=None))
    # Qualcomm Hexagon DSP, which is exposed as a remote processor
    for rproc in sorted(Path("/sys/class/remoteproc").glob("remoteproc*")):
        name = read_text(rproc / "name") or ""
        if "cdsp" in name.lower():
            state = read_text(rproc / "state")
            npus.append(NPUInfo(
                name=f"Qualcomm Hexagon (CDSP, {name}, state: {state})",
                kernel_driver=driver_name(rproc / "device") if (rproc / "device").exists() else None,
                pci_address=None,
            ))
    return npus


def get_os_info() -> OSInfo:
    """Get information about the operating system."""
    try:
        release = platform.freedesktop_os_release()
    except OSError:
        release = {}
    return OSInfo(
        name=release.get("PRETTY_NAME") or release.get("NAME"),
        version=release.get("VERSION") or release.get("VERSION_ID"),
        build=release.get("BUILD_ID"),
        variant=release.get("VARIANT") or release.get("VARIANT_ID"),
        kernel=f"Linux {platform.release()} ({platform.machine()})",
        hostname=platform.node(),
    )


def get_software_info(gpus: Sequence[GPUInfo]) -> SoftwareInfo:
    """Get the versions of the GPU compute software stacks.

    :param gpus: GPUs, from which the Mesa version is taken
    :return: software versions
    """
    cuda: str | None = None
    if shutil.which("nvidia-smi"):
        output = run_cmd(["nvidia-smi", "-q"])
        if output and (match := re.search(r"CUDA (?:UMD )?Version\s*:\s*([\d.]+)", output)):
            cuda = match.group(1)
    rocm = read_text("/opt/rocm/.info/version")
    if rocm is None:
        for path in sorted(Path("/opt").glob("rocm-*/.info/version")):
            rocm = read_text(path)
    mesa: str | None = None
    for gpu in gpus:
        if gpu.vulkan_driver and (match := re.search(r"Mesa ([\w.~+-]+)", gpu.vulkan_driver)):
            mesa = match.group(1)
            break
    return SoftwareInfo(
        nvidia_driver=read_text("/sys/module/nvidia/version"),
        cuda=cuda,
        rocm=rocm,
        mesa=mesa,
    )


def collect(notes: list[str] | None = None) -> SystemInfo:
    """Collect all the information.

    :param notes: initial notes
    :return: collected information
    """
    notes = notes if notes is not None else []
    kernel_log = get_kernel_log()
    gpus = get_gpus(kernel_log, notes)
    return SystemInfo(
        generated=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        run_as_root=os.geteuid() == 0,
        os=get_os_info(),
        board=get_board_info(),
        cpu=get_cpu_info(),
        memory=get_memory_info(notes),
        gpus=gpus,
        npus=get_npus(),
        software=get_software_info(gpus),
        notes=notes,
    )


def driver_name(dev: Path) -> str | None:
    """Get the name of the kernel driver bound to a device.

    :param dev: sysfs device directory
    :return: driver name
    """
    driver = dev / "driver"
    if not driver.exists():
        return None
    return Path(os.readlink(driver)).name


def edac_status() -> str | None:
    """Get the ECC status from the kernel EDAC subsystem."""
    mcs = sorted(Path("/sys/devices/system/edac/mc").glob("mc[0-9]*"))
    if not mcs:
        return None
    modes: set[str] = set()
    for mc in mcs:
        for dimm in [*mc.glob("dimm[0-9]*"), *mc.glob("rank[0-9]*")]:
            mode = read_text(dimm / "dimm_edac_mode")
            if mode:
                modes.add(mode)
    modes.discard("Unknown")
    if not modes or modes == {"None"}:
        return f"EDAC driver {read_text(mcs[0] / 'mc_name')} loaded, but ECC is not active"
    return f"active ({', '.join(sorted(modes))}, EDAC driver {read_text(mcs[0] / 'mc_name')})"


def hwmon_power_limits(dev: Path) -> dict[str, str]:
    """Get the GPU power limits from hwmon, which e.g. amdgpu provides.

    :param dev: sysfs device directory
    :return: power limits with the same keys as the GPUInfo fields
    """
    files = {
        "power_limit": "power1_cap",
        "power_limit_default": "power1_cap_default",
        "power_limit_min": "power1_cap_min",
        "power_limit_max": "power1_cap_max",
    }
    for hwmon in sorted(dev.glob("hwmon/hwmon*")):
        result: dict[str, str] = {}
        for key, name in files.items():
            microwatts = read_int(hwmon / name)
            if microwatts is not None:
                result[key] = f"{microwatts / 1e6:.2f} W"
        if result:
            return result
    return {}


def label(key: str) -> str:
    """Convert a snake_case key to a human-readable label.

    :param key: dataclass field name
    :return: label
    """
    words = [ACRONYMS.get(word, word) for word in key.split("_")]
    if words and words[0] == words[0].lower():
        words[0] = words[0].capitalize()
    return " ".join(words)


def memory_channels(modules: Sequence[MemoryModule]) -> int | None:
    """Count the memory channels from the DIMM locators.

    Different vendors use different formats, e.g. "P0 CHANNEL A", "ChannelA-DIMM0" and "CPU0_DIMM_A1".

    :param modules: installed modules
    :return: number of populated channels, or None if they cannot be determined
    """
    channels: set[tuple[str, ...]] = set()
    for module in modules:
        text = f"{module.bank_locator or ''} {module.locator or ''}"
        socket = re.search(r"\b(?:P|CPU|Node)\s*(\d+)", text, re.IGNORECASE)
        controller = re.search(r"Controller\s*(\d+)", text, re.IGNORECASE)
        channel = re.search(r"Channel\s*([A-Z0-9]+)", text, re.IGNORECASE)
        if channel is None:
            channel = re.search(r"DIMM[_ ]?([A-Z])\d", text, re.IGNORECASE)
        if channel is None:
            return None
        channels.add((
            socket.group(1) if socket else "",
            controller.group(1) if controller else "",
            channel.group(1).upper(),
        ))
    return len(channels) or None


def memory_from_dmidecode() -> tuple[list[MemoryModule], str | None, int | None]:
    """Get the RAM module information with dmidecode (requires root).

    :return: modules (including empty slots), ECC type of the memory array, number of slots
    """
    output = run_cmd(["dmidecode", "-t", "16", "-t", "17"])
    if not output:
        return [], None, None
    modules: list[MemoryModule] = []
    array_ecc: str | None = None
    slots = 0
    for block in re.split(r"\n\s*\n", output):
        fields: dict[str, str] = {}
        for line in block.splitlines():
            if ":" in line and line.startswith("\t") and not line.startswith("\t\t"):
                key, _, value = line.strip().partition(":")
                fields[key.strip()] = value.strip()
        if "DMI type 16," in block:
            array_ecc = array_ecc or fields.get("Error Correction Type")
        elif "DMI type 17," in block:
            slots += 1
            size_bytes = parse_size(fields.get("Size", ""))
            modules.append(memory_module(
                locator=fields.get("Locator"),
                bank_locator=fields.get("Bank Locator"),
                size_bytes=size_bytes,
                mem_type=fields.get("Type"),
                type_detail=fields.get("Type Detail"),
                form_factor=fields.get("Form Factor"),
                speed=parse_int((fields.get("Speed") or "").split(" ")[0]),
                configured_speed=parse_int((fields.get("Configured Memory Speed") or "").split(" ")[0]),
                manufacturer=fields.get("Manufacturer"),
                part_number=fields.get("Part Number"),
                rank=parse_int(fields.get("Rank")),
                total_width=parse_int((fields.get("Total Width") or "").split(" ")[0]),
                data_width=parse_int((fields.get("Data Width") or "").split(" ")[0]),
            ))
    return modules, dmi_value(array_ecc), slots or None


def memory_from_udev() -> tuple[list[MemoryModule], str | None, int | None]:
    """Get the RAM module information from the udev database, which is readable without root.

    systemd-udevd stores the SMBIOS memory device information in the properties of the DMI device
    (systemd 250 or newer).

    :return: modules (including empty slots), ECC type of the memory array, number of slots
    """
    props: dict[str, str] = {}
    data = read_text("/run/udev/data/+dmi:id")
    if data:
        for line in data.splitlines():
            if line.startswith("E:"):
                key, _, value = line[2:].partition("=")
                props[key] = value
    if not any(key.startswith("MEMORY_DEVICE_") for key in props):
        output = run_cmd(["udevadm", "info", "--query=property", "--path=/devices/virtual/dmi/id"])
        if output:
            for line in output.splitlines():
                key, _, value = line.partition("=")
                props[key] = value
    indices = sorted({
        int(match.group(1)) for key in props if (match := re.match(r"MEMORY_DEVICE_(\d+)_", key))
    })
    modules: list[MemoryModule] = []
    for i in indices:
        def prop(name: str, idx: int = i) -> str | None:
            return props.get(f"MEMORY_DEVICE_{idx}_{name}")
        present = prop("PRESENT")
        size_bytes = parse_int(prop("SIZE")) if present != "0" else None
        modules.append(memory_module(
            locator=prop("LOCATOR"),
            bank_locator=prop("BANK_LOCATOR"),
            size_bytes=size_bytes,
            mem_type=prop("TYPE"),
            type_detail=prop("TYPE_DETAIL"),
            form_factor=prop("FORM_FACTOR"),
            speed=parse_int(prop("SPEED_MTS")),
            configured_speed=parse_int(prop("CONFIGURED_SPEED_MTS")),
            manufacturer=prop("MANUFACTURER"),
            part_number=prop("PART_NUMBER"),
            rank=parse_int(prop("RANK")),
            total_width=parse_int(prop("TOTAL_WIDTH")),
            data_width=parse_int(prop("DATA_WIDTH")),
        ))
    return modules, dmi_value(props.get("MEMORY_ARRAY_EC_TYPE")), len(indices) or None


def memory_module_summary(modules: Sequence[MemoryModule]) -> list[str]:
    """Group identical memory modules, e.g. "8 x 16 GiB Kingston 9965745-002.A00G, DDR4-2666, dual-rank, ECC".

    :param modules: installed modules
    :return: one line per group of identical modules
    """
    groups: dict[str, int] = {}
    for m in modules:
        parts = [" ".join(p for p in (m.size, m.manufacturer, m.part_number) if p)]
        if m.type:
            parts.append(f"{m.type}-{m.speed_mts}" if m.speed_mts else m.type)
        if m.form_factor:
            parts.append(m.form_factor)
        if m.rank:
            parts.append({1: "single-rank", 2: "dual-rank", 4: "quad-rank"}.get(m.rank, f"{m.rank}-rank"))
        if m.ecc_width is not None:
            parts.append("ECC" if m.ecc_width else "non-ECC")
        key = ", ".join(parts)
        groups[key] = groups.get(key, 0) + 1
    return [f"{count} x {key}" for key, count in groups.items()]


def memory_type(modules: Sequence[MemoryModule]) -> str | None:
    """Describe the memory type, e.g. "DDR4 registered".

    :param modules: installed modules
    :return: memory type
    """
    types = sorted({m.type for m in modules if m.type})
    if not types:
        return None
    details = {m.type_detail for m in modules if m.type_detail}
    registered = any("Registered" in d and "Unregistered" not in d for d in details)
    unbuffered = any("Unbuffered" in d or "Unregistered" in d for d in details)
    suffix = " registered" if registered else " unbuffered" if unbuffered else ""
    return ", ".join(f"{t}{suffix}" if t.startswith("DDR") else t for t in types)


def memory_module(  # noqa: PLR0913
        *,
        locator: str | None,
        bank_locator: str | None,
        size_bytes: int | None,
        mem_type: str | None,
        type_detail: str | None,
        form_factor: str | None,
        speed: int | None,
        configured_speed: int | None,
        manufacturer: str | None,
        part_number: str | None,
        rank: int | None,
        total_width: int | None,
        data_width: int | None) -> MemoryModule:
    """Create a MemoryModule object, filtering out placeholder values.

    :return: memory module
    """
    ecc_width = None
    if total_width and data_width:
        ecc_width = total_width > data_width
    return MemoryModule(
        locator=dmi_value(locator),
        bank_locator=dmi_value(bank_locator),
        size=format_bytes(size_bytes) if size_bytes else "none",
        type=dmi_value(mem_type),
        type_detail=dmi_value(type_detail),
        form_factor=dmi_value(form_factor),
        speed_mts=speed or None,
        configured_speed_mts=configured_speed or None,
        manufacturer=dmi_value(manufacturer),
        part_number=dmi_value(part_number),
        rank=rank or None,
        ecc_width=ecc_width,
    )


def nvidia_vram_type(name: str) -> str | None:
    """Get the VRAM type of an NVIDIA GPU from its name, as the driver does not report it.

    :param name: GPU name
    :return: VRAM type
    """
    for pattern, vram_type in NVIDIA_VRAM_TYPES:
        if re.search(pattern, name):
            return f"{vram_type} (inferred from the model)"
    return None


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


def parse_cpuinfo(text: str | None = None) -> list[dict[str, str]]:
    """Parse /proc/cpuinfo.

    :param text: contents of /proc/cpuinfo, read from the file if not given
    :return: list of dictionaries, one per processor
    """
    if text is None:
        text = read_text("/proc/cpuinfo") or ""
    entries: list[dict[str, str]] = []
    for block in text.strip().split("\n\n"):
        entry: dict[str, str] = {}
        for line in block.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                entry[key.strip()] = value.strip()
        if entry:
            entries.append(entry)
    return entries


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


def parse_lscpu() -> dict[str, str]:
    """Get the lscpu fields as a flat dictionary."""
    output = run_cmd(["lscpu", "-J"])
    if not output:
        return {}
    try:
        data = json.loads(output).get("lscpu", [])
    except json.JSONDecodeError:
        return {}
    result: dict[str, str] = {}

    def walk(items: list[dict[str, tp.Any]]) -> None:
        for item in items:
            key = str(item.get("field", "")).rstrip(":")
            if key and key not in result and item.get("data") is not None:
                result[key] = str(item["data"])
            walk(item.get("children", []))

    walk(data)
    return result


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


def pcie_link(dev: Path, current: bool) -> str | None:
    """Get the PCIe link version and width of a device.

    The maximum is the lowest maximum of all the links between the device and the root port,
    as e.g. a GPU in a chipset slot cannot exceed the chipset uplink.
    The current link is that of the slot, i.e. the topmost link below the root port,
    as GPUs such as the Radeon VII have an internal PCIe switch.

    :param dev: sysfs device directory
    :param current: whether to get the current instead of the maximum link
    :return: e.g. "PCIe 4.0 x16"
    """
    chain = [part for part in dev.resolve().parts if PCI_ADDRESS.match(part)]
    if not chain:
        return None
    root = dev.resolve()
    while root.name != chain[0]:
        root = root.parent
    paths = [root]
    for part in chain[1:]:
        paths.append(paths[-1] / part)
    if current:
        slot = paths[1] if len(paths) > 1 else paths[0]
        speed = read_text(slot / "current_link_speed")
        width = read_int(slot / "current_link_width")
        text = pcie_text(speed, width)
        if text and pcie_text(read_text(dev / "current_link_speed"), read_int(dev / "current_link_width")) != text:
            text += (
                f" (device side: "
                f"{pcie_text(read_text(dev / 'current_link_speed'), read_int(dev / 'current_link_width'))})"
            )
        return f"{text} (an idle GPU may lower the link speed)" if text else None
    gens: list[int] = []
    widths: list[int] = []
    for path in paths:
        speed = read_text(path / "max_link_speed")
        width = read_int(path / "max_link_width")
        gen = pcie_generation(speed)
        if gen:
            gens.append(gen)
        if width:
            widths.append(width)
    if not gens or not widths:
        return None
    return f"PCIe {min(gens)}.0 x{min(widths)}"


def pcie_generation(speed: str | None) -> int | None:
    """Convert a PCIe link speed such as "16.0 GT/s PCIe" to the PCIe version.

    :param speed: link speed from sysfs
    :return: PCIe version
    """
    if not speed:
        return None
    match = re.match(r"([\d.]+)\s*GT/s", speed)
    if not match:
        return None
    return PCIE_GENERATIONS.get(float(match.group(1)))


def pcie_text(speed: str | None, width: int | None) -> str | None:
    """Format a PCIe link.

    :param speed: link speed from sysfs
    :param width: link width
    :return: e.g. "PCIe 4.0 x16"
    """
    gen = pcie_generation(speed)
    if gen is None or not width:
        return None
    return f"PCIe {gen}.0 x{width}"


def normalize_pci_address(address: str) -> str:
    """Convert a PCI address such as "00000000:01:00.0" to the sysfs format "0000:01:00.0".

    :param address: PCI address
    :return: normalized address
    """
    address = address.strip().lower()
    if match := re.match(r"^([0-9a-f]+):([0-9a-f]{2}):([0-9a-f]{2})\.([0-7])$", address):
        return f"{int(match.group(1), 16):04x}:{match.group(2)}:{match.group(3)}.{match.group(4)}"
    return address


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


def soc_gpu_driver() -> str | None:
    """Get the kernel driver of a non-PCI (SoC) GPU."""
    for card in sorted(Path("/sys/class/drm").glob("card[0-9]")):
        dev = (card / "device").resolve()
        if not PCI_ADDRESS.match(dev.name):
            return driver_name(dev)
    return None


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


def x86_64_isa_level(flags: set[str]) -> str:
    """Get the x86-64 microarchitecture level (psABI) supported by the CPU.

    :param flags: CPU flags from /proc/cpuinfo
    :return: e.g. "x86-64-v3"
    """
    levels = (
        ("x86-64-v4", {"avx512f", "avx512bw", "avx512cd", "avx512dq", "avx512vl"}),
        ("x86-64-v3", {"avx", "avx2", "bmi1", "bmi2", "f16c", "fma", "abm", "movbe", "xsave"}),
        ("x86-64-v2", {"cx16", "lahf_lm", "popcnt", "sse4_1", "sse4_2", "ssse3"}),
    )
    level = "x86-64"
    for name, required in reversed(levels):
        if not required <= flags:
            break
        level = name
    return level


def main() -> None:
    """Parse the arguments and print or save the information."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("output", nargs="?", type=Path, help="save the output to this file instead of printing it")
    parser.add_argument("--json", action="store_true", help="output JSON instead of text")
    parser.add_argument("--verbose", "-v", action="store_true", help="log failed commands to stderr")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    info = collect()
    text = json.dumps(dataclasses.asdict(info), indent=2) + "\n" if args.json else format_text(info)
    if args.output is None:
        sys.stdout.write(text)
        return
    args.output.write_text(text, encoding="utf-8")
    # Give the file to the user who ran sudo.
    if os.geteuid() == 0 and "SUDO_UID" in os.environ and "SUDO_GID" in os.environ:
        os.chown(args.output, int(os.environ["SUDO_UID"]), int(os.environ["SUDO_GID"]))
    print(f"Saved the system information to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
