"""Data classes for the collected information."""

from __future__ import annotations

import dataclasses


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
