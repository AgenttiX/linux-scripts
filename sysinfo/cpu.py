"""CPU information."""

from __future__ import annotations

import json
from pathlib import Path
import platform
import typing as tp

from sysinfo.common import compress_ranges, parse_cpu_list, parse_int, read_int, read_text, run_cmd
from sysinfo.models import CoreGroup, CPUInfo

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


#: x86 CPU flags that are relevant for performance, especially for AI inference
X86_FEATURES: tuple[str, ...] = (
    "sse4_2", "avx", "avx2", "fma", "f16c", "avx_vnni", "avx_vnni_int8", "avx_ne_convert",
    "avx512f", "avx512bw", "avx512vl", "avx512_vnni", "avx512_bf16", "avx512_fp16", "avx10",
    "amx_tile", "amx_bf16", "amx_int8", "amx_fp16", "aes", "sha_ni",
)


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
