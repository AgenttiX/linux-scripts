"""NPU information."""

from __future__ import annotations

from pathlib import Path

from sysinfo.common import PCI_ADDRESS, driver_name, parse_lspci, read_text, split_pci_name
from sysinfo.models import NPUInfo

#: Kernel drivers of NPUs
NPU_DRIVERS: frozenset[str] = frozenset({"amdxdna", "intel_vpu", "qaic", "rknpu", "rocket"})


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
