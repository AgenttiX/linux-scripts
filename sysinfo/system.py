"""Operating system, motherboard and software information."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import platform
import re
import shutil

from sysinfo.common import dmi_value, read_text, run_cmd
from sysinfo.models import BoardInfo, GPUInfo, OSInfo, SoftwareInfo


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
