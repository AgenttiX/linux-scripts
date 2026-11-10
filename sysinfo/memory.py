"""RAM information."""

from __future__ import annotations

from collections.abc import Sequence
import os
from pathlib import Path
import re

from sysinfo.common import dmi_value, format_bytes, parse_int, parse_size, read_text, run_cmd
from sysinfo.models import MemoryInfo, MemoryModule


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
