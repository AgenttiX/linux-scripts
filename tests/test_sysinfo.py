"""Tests for the ./sysinfo package."""

import dataclasses
import json
import pathlib
import tempfile
import textwrap
import typing as tp
import unittest
from unittest import mock

from sysinfo import __main__ as sysinfo_main
from sysinfo import common, cpu, gpu, gpu_tools, memory, output, pcie
from sysinfo.models import MemoryModule

DMIDECODE_OUTPUT: str = textwrap.dedent("""\
    # dmidecode 3.6
    Getting SMBIOS data from sysfs.
    SMBIOS 3.3.0 present.

    Handle 0x0010, DMI type 16, 23 bytes
    Physical Memory Array
    \tLocation: System Board Or Motherboard
    \tUse: System Memory
    \tError Correction Type: Multi-bit ECC
    \tMaximum Capacity: 512 GB
    \tNumber Of Devices: 2

    Handle 0x0012, DMI type 17, 92 bytes
    Memory Device
    \tTotal Width: 72 bits
    \tData Width: 64 bits
    \tSize: 32 GB
    \tForm Factor: DIMM
    \tLocator: DIMM 0
    \tBank Locator: P0 CHANNEL A
    \tType: DDR4
    \tType Detail: Synchronous Registered (Buffered)
    \tSpeed: 3200 MT/s
    \tManufacturer: Micron Technology
    \tSerial Number: 12345678
    \tPart Number: 36ASF4G72PZ-3G2R1
    \tRank: 2
    \tConfigured Memory Speed: 2933 MT/s

    Handle 0x0013, DMI type 17, 92 bytes
    Memory Device
    \tTotal Width: Unknown
    \tData Width: Unknown
    \tSize: No Module Installed
    \tForm Factor: DIMM
    \tLocator: DIMM 1
    \tBank Locator: P0 CHANNEL B
    \tType: Unknown
""")

VULKANINFO_OUTPUT: str = textwrap.dedent("""\
    ==========
    VULKANINFO
    ==========

    Devices:
    ========
    GPU0:
    \tapiVersion         = 1.4.335
    \tdriverVersion      = 26.0.8
    \tvendorID           = 0x1002
    \tdeviceID           = 0x66af
    \tdeviceType         = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
    \tdeviceName         = AMD Radeon VII (RADV VEGA20)
    \tdriverName         = radv
    \tdriverInfo         = Mesa 26.0.8
    GPU1:
    \tvendorID           = 0x10005
    \tdeviceID           = 0x0000
    \tdeviceType         = PHYSICAL_DEVICE_TYPE_CPU
    \tdeviceName         = llvmpipe (LLVM 21.1.8, 256 bits)
""")


def module(locator: str, bank_locator: str, **kwargs: int | str | None) -> MemoryModule:
    """Create a MemoryModule with default values."""
    defaults: dict[str, tp.Any] = {
        "size_bytes": 16 * 1024**3, "mem_type": "DDR5", "type_detail": "Synchronous Unbuffered (Unregistered)",
        "form_factor": "DIMM", "speed": 5600, "configured_speed": 5600, "manufacturer": "Kingston",
        "part_number": "KF556C40-16", "rank": 1, "total_width": 64, "data_width": 64,
    }
    defaults.update(kwargs)
    return memory.memory_module(locator=locator, bank_locator=bank_locator, **defaults)


class TestFormatting(unittest.TestCase):
    """Tests for the formatting helpers."""

    def test_compress_ranges(self) -> None:
        """Consecutive numbers are compressed to ranges."""
        assert common.compress_ranges([5, 0, 1, 2, 6, 9]) == "0-2,5-6,9"
        assert common.compress_ranges([]) == ""

    def test_format_bytes(self) -> None:
        """Sizes are formatted with binary units."""
        assert common.format_bytes(16 * 1024**3) == "16 GiB"
        assert common.format_bytes(1536 * 1024**2) == "1.5 GiB"
        assert common.format_bytes(512) == "512 B"

    def test_label(self) -> None:
        """Field names are converted to labels with the correct acronyms."""
        assert output.label("pcie_link_max") == "PCIe link max"
        assert output.label("vram_type") == "VRAM type"
        assert output.label("gpus") == "GPUs"

    def test_parse_cpu_list(self) -> None:
        """CPU lists are expanded."""
        assert common.parse_cpu_list("0-2,5,7-8\n") == [0, 1, 2, 5, 7, 8]
        assert common.parse_cpu_list("") == []

    def test_parse_size(self) -> None:
        """Sizes in decimal and binary units are parsed as binary units."""
        assert common.parse_size("16 GB") == 16 * 1024**3
        assert common.parse_size("24576 MiB") == 24 * 1024**3
        assert common.parse_size("No Module Installed") is None

    def test_split_pci_name(self) -> None:
        """The lspci device name is split into the codename and the product name."""
        assert common.split_pci_name("GA102 [GeForce RTX 3090]") == ("GA102", "GeForce RTX 3090")
        assert common.split_pci_name("Vega 20 [Radeon VII] [66af]") == ("Vega 20", "Radeon VII")
        assert common.split_pci_name("Some device") == (None, "Some device")
        assert common.split_pci_name(None) == (None, None)


class TestHardware(unittest.TestCase):
    """Tests for the hardware identification helpers."""

    def test_amd_architecture(self) -> None:
        """AMD GPU architectures are identified from the LLVM target or the codename."""
        assert gpu.amd_architecture("gfx906", None) == "GCN 5 (Vega)"
        assert gpu.amd_architecture("gfx90a", None) == "CDNA 2"
        assert gpu.amd_architecture("gfx1100", None) == "RDNA 3"
        assert gpu.amd_architecture("gfx1151", None) == "RDNA 3.5"
        assert gpu.amd_architecture("gfx1201", None) == "RDNA 4"
        assert gpu.amd_architecture(None, "Navi 21") == "RDNA 2"

    def test_amd_microarchitecture(self) -> None:
        """AMD CPU microarchitectures are identified from the family and model."""
        assert cpu.amd_microarchitecture(0x17, 0x31) == "Zen 2"
        assert cpu.amd_microarchitecture(0x17, 0x08) == "Zen+"
        assert cpu.amd_microarchitecture(0x19, 0x21) == "Zen 3"
        assert cpu.amd_microarchitecture(0x19, 0x61) == "Zen 4"
        assert cpu.amd_microarchitecture(0x1A, 0x44) == "Zen 5"
        assert cpu.amd_microarchitecture(0x10, 0x00) is None

    def test_arm_core_name(self) -> None:
        """ARM cores are identified from /proc/cpuinfo."""
        assert cpu.arm_core_name({"CPU implementer": "0x41", "CPU part": "0xd82"}) == "Cortex-X4"
        assert cpu.arm_core_name({"CPU implementer": "0x51", "CPU part": "0x001"}) == "Qualcomm part 0x1"
        assert cpu.arm_core_name({}) is None

    def test_nvidia_vram_type(self) -> None:
        """NVIDIA VRAM types are inferred from the model name."""
        assert gpu.nvidia_vram_type("NVIDIA GeForce RTX 3090") == "GDDR6X (inferred from the model)"
        assert gpu.nvidia_vram_type("NVIDIA RTX A4000") == "GDDR6 (inferred from the model)"
        assert gpu.nvidia_vram_type("NVIDIA GeForce RTX 5090") == "GDDR7 (inferred from the model)"
        assert gpu.nvidia_vram_type("Unknown GPU") is None

    def test_pcie(self) -> None:
        """PCIe link speeds are converted to versions."""
        assert pcie.pcie_generation("16.0 GT/s PCIe") == 4
        assert pcie.pcie_generation("2.5 GT/s PCIe") == 1
        assert pcie.pcie_generation("Unknown") is None
        assert pcie.pcie_text("8.0 GT/s PCIe", 16) == "PCIe 3.0 x16"
        assert common.normalize_pci_address("00000000:01:00.0") == "0000:01:00.0"

    def test_x86_64_isa_level(self) -> None:
        """The x86-64 microarchitecture level is determined from the CPU flags."""
        v2 = {"cx16", "lahf_lm", "popcnt", "sse4_1", "sse4_2", "ssse3"}
        v3 = v2 | {"avx", "avx2", "bmi1", "bmi2", "f16c", "fma", "abm", "movbe", "xsave"}
        v4 = v3 | {"avx512f", "avx512bw", "avx512cd", "avx512dq", "avx512vl"}
        assert cpu.x86_64_isa_level(set()) == "x86-64"
        assert cpu.x86_64_isa_level(v2) == "x86-64-v2"
        assert cpu.x86_64_isa_level(v3) == "x86-64-v3"
        assert cpu.x86_64_isa_level(v4) == "x86-64-v4"
        assert cpu.x86_64_isa_level(v4 - {"avx2"}) == "x86-64-v2"


class TestGPUUnlock(unittest.TestCase):
    """Tests for the NVIDIA GPU unlock check."""

    ADDR = "0000:01:00.0"

    def check(self, log: list[str] | None, module_loaded: bool = True) -> str:
        """Run the check with a mocked gpu_unlock module status."""
        with mock.patch.object(pathlib.Path, "exists", return_value=module_loaded):
            return gpu.check_gpu_unlock(self.ADDR, log)

    def test_unlocked(self) -> None:
        """An unlock message for the GPU is detected, including the resumes."""
        log = [
            f"pci {self.ADDR}: gpu_unlock: stage=claim device=0x2204",
            f"pci {self.ADDR}: gpu_unlock: unlocked",
            f"nvidia {self.ADDR}: gpu_unlock: pass=1/2 attempt=1 ret=0",
            f"nvidia {self.ADDR}: gpu_unlock: unlocked again after resume",
        ]
        assert self.check(log) == "yes (re-applied after 1 resume(s))"

    def test_failed_pass(self) -> None:
        """A failed unlock pass is reported."""
        log = [f"pci {self.ADDR}: gpu_unlock: unlocked", f"nvidia {self.ADDR}: gpu_unlock: pass=1/2 ret=-5"]
        assert "failed" in self.check(log)

    def test_other_gpu(self) -> None:
        """An unlock message of another GPU is not counted."""
        log = ["pci 0000:02:00.0: gpu_unlock: unlocked"]
        assert self.check(log).startswith("no")
        assert "not loaded" in self.check(log, module_loaded=False)

    def test_unreadable_log(self) -> None:
        """An unreadable kernel log gives an unknown status if the module is loaded."""
        assert self.check(None).startswith("unknown")


class TestMemory(unittest.TestCase):
    """Tests for the RAM information."""

    def test_dmidecode(self) -> None:
        """The dmidecode output is parsed, and serial numbers are left out."""
        with mock.patch.object(memory, "run_cmd", return_value=DMIDECODE_OUTPUT):
            modules, array_ecc, slots = memory.memory_from_dmidecode()
        assert array_ecc == "Multi-bit ECC"
        assert slots == 2
        assert modules[0].size == "32 GiB"
        assert modules[0].speed_mts == 3200
        assert modules[0].configured_speed_mts == 2933
        assert modules[0].rank == 2
        assert modules[0].ecc_width
        assert memory.memory_type(modules[:1]) == "DDR4 registered"
        assert modules[1].size == "none"
        assert modules[1].type is None
        assert "12345678" not in json.dumps([dataclasses.asdict(m) for m in modules])

    def test_memory_channels(self) -> None:
        """Memory channels are counted from the different locator formats."""
        amd = [module("DIMM 0", "P0 CHANNEL A"), module("DIMM 1", "P0 CHANNEL A"), module("DIMM 0", "P0 CHANNEL B")]
        assert memory.memory_channels(amd) == 2
        intel = [module("Controller0-ChannelA-DIMM0", "BANK 0"), module("Controller1-ChannelA-DIMM0", "BANK 0")]
        assert memory.memory_channels(intel) == 2
        lenovo = [module("DIMM_A1", "BANK 0"), module("DIMM_B1", "BANK 1"), module("DIMM_A2", "BANK 2")]
        assert memory.memory_channels(lenovo) == 2
        assert memory.memory_channels([module("DIMM 0", "BANK 0")]) is None

    def test_module_summary(self) -> None:
        """Identical modules are grouped."""
        modules = [module("DIMM 0", "P0 CHANNEL A"), module("DIMM 0", "P0 CHANNEL B")]
        expected = "2 x 16 GiB Kingston KF556C40-16, DDR5-5600, DIMM, single-rank, non-ECC"
        assert memory.memory_module_summary(modules) == [expected]


class TestParsers(unittest.TestCase):
    """Tests for the parsers of tool output."""

    def test_parse_cpuinfo(self) -> None:
        """/proc/cpuinfo is parsed per processor."""
        entries = cpu.parse_cpuinfo("processor\t: 0\nmodel name\t: CPU A\n\nprocessor\t: 1\nmodel name\t: CPU B\n")
        assert [entry["model name"] for entry in entries] == ["CPU A", "CPU B"]

    def test_parse_vulkaninfo(self) -> None:
        """The Vulkan devices are parsed from vulkaninfo --summary."""
        devices = gpu_tools.parse_vulkaninfo(VULKANINFO_OUTPUT)
        assert len(devices) == 2
        assert devices[0]["vendorID"] == 0x1002
        assert gpu_tools.strip_vulkan_name(devices[0]["deviceName"]) == "AMD Radeon VII"
        assert gpu_tools.vulkan_driver(devices[0]) == "radv, Mesa 26.0.8, Vulkan 1.4.335"


class TestCollect(unittest.TestCase):
    """Smoke tests for collecting the information on the machine that runs the tests."""

    def test_collect_and_format(self) -> None:
        """Collecting and formatting the information does not fail."""
        info = sysinfo_main.collect()
        text = output.format_text(info)
        assert "CPU:" in text
        assert "Memory:" in text
        data = json.loads(json.dumps(dataclasses.asdict(info)))
        assert data["cpu"]["threads"] >= 1

    def test_main_output_file(self) -> None:
        """The output is saved to a file as JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "sysinfo.json"
            with mock.patch("sys.argv", ["sysinfo.py", "--json", str(path)]), mock.patch("sys.stderr"):
                sysinfo_main.main()
            assert "cpu" in json.loads(path.read_text())


if __name__ == "__main__":
    unittest.main()
