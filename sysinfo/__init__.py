"""Collect the hardware and OS information needed for a performance testing report.

The information is collected from sysfs, procfs, the udev database and common tools
(lscpu, lspci, nvidia-smi, amd-smi, vulkaninfo, journalctl), whichever are available.
Most of it is available without root access.
When run with sudo, dmidecode is used to fill in the RAM module details that the udev database may lack.
Serial numbers are deliberately left out, so that the output can be published.

Run with ``python3 -m sysinfo`` or ``./sysinfo/__main__.py``.
This package uses only the Python standard library and does not import anything else from this repository,
so that this directory can be copied to and run on any Linux system with Python 3.12+.
"""
