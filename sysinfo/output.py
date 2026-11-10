"""Formatting of the collected information as text."""

from __future__ import annotations

import dataclasses
import typing as tp

from sysinfo.models import SystemInfo

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


#: Fields that are only included in the JSON output, as the text output has a summary of them
JSON_ONLY_FIELDS: frozenset[str] = frozenset({"modules"})


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


def label(key: str) -> str:
    """Convert a snake_case key to a human-readable label.

    :param key: dataclass field name
    :return: label
    """
    words = [ACRONYMS.get(word, word) for word in key.split("_")]
    if words and words[0] == words[0].lower():
        words[0] = words[0].capitalize()
    return " ".join(words)
