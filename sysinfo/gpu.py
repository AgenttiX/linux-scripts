"""GPU information."""

from __future__ import annotations

from pathlib import Path
import platform
import re
import shutil

from sysinfo.common import (
    PCI_ADDRESS,
    driver_name,
    format_bytes,
    parse_int,
    parse_lspci,
    parse_size,
    read_int,
    read_text,
    run_cmd,
    split_pci_name,
)
from sysinfo.gpu_tools import (
    parse_amd_smi,
    parse_kfd,
    parse_nvidia_smi,
    parse_vulkaninfo,
    strip_vulkan_name,
    vulkan_driver,
)
from sysinfo.models import GPUInfo
from sysinfo.pcie import pcie_link

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


def nvidia_vram_type(name: str) -> str | None:
    """Get the VRAM type of an NVIDIA GPU from its name, as the driver does not report it.

    :param name: GPU name
    :return: VRAM type
    """
    for pattern, vram_type in NVIDIA_VRAM_TYPES:
        if re.search(pattern, name):
            return f"{vram_type} (inferred from the model)"
    return None


def soc_gpu_driver() -> str | None:
    """Get the kernel driver of a non-PCI (SoC) GPU."""
    for card in sorted(Path("/sys/class/drm").glob("card[0-9]")):
        dev = (card / "device").resolve()
        if not PCI_ADDRESS.match(dev.name):
            return driver_name(dev)
    return None
