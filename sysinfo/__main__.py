#!/usr/bin/env python3
"""Print the hardware and OS information needed for a performance testing report.

Usage: ``./sysinfo/__main__.py [--json] [output_file]``, or ``python3 -m sysinfo [--json] [output_file]``
in the repository directory.
See the ``sysinfo`` package docstring for details.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import logging
import os
from pathlib import Path
import sys

# Allow running this file directly as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sysinfo.cpu import get_cpu_info
from sysinfo.gpu import get_gpus, get_kernel_log
from sysinfo.memory import get_memory_info
from sysinfo.models import SystemInfo
from sysinfo.npu import get_npus
from sysinfo.output import format_text
from sysinfo.system import get_board_info, get_os_info, get_software_info


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
