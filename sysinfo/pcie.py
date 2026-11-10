"""PCIe link information."""

from __future__ import annotations

from pathlib import Path
import re

from sysinfo.common import PCI_ADDRESS, read_int, read_text

#: PCIe link speeds in GT/s and the corresponding PCIe versions
PCIE_GENERATIONS: dict[float, int] = {2.5: 1, 5.0: 2, 8.0: 3, 16.0: 4, 32.0: 5, 64.0: 6, 128.0: 7}


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
