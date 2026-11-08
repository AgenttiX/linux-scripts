"""Disk maintenance: RAID scrubbing, TRIM and zeroing of free space."""

import pathlib
import shutil

from maintenance.common import REPO_DIR
from utils.misc_utils import is_virtual, print_info, run, yes_or_no

MDSTAT_PATH: pathlib.Path = pathlib.Path("/proc/mdstat")
#: The directory /var/tmp is used instead of /tmp, as the latter may be on a ramdisk or a separate partition.
ZEROFREE_PATH: pathlib.Path = pathlib.Path("/var/tmp/bigemptyfile")


def mdadm() -> None:
    """Start mdadm scrubbing.

    https://wiki.archlinux.org/title/RAID#Scrubbing
    """
    if shutil.which("mdadm") is None:
        print_info("mdadm not found")
        return
    endpoints = sorted(pathlib.Path("/sys/block").glob("md*/md/sync_action"))
    if not endpoints:
        print_info("No mdadm arrays found")
        return
    print_info(
        "Starting mdadm scrubbing. "
        "You can monitor the progress with \"cat /proc/mdstat\". "
        "Rebooting will restart the scrubbing from the beginning.")
    for path in endpoints:
        path.write_text("check")
    print(MDSTAT_PATH.read_text())


def should_zero_free_space(requested: bool) -> bool:
    """Determine whether free disk space should be zeroed, asking the user if necessary.

    :param requested: whether zeroing was requested with a command-line argument
    :return: whether to zero free disk space
    """
    if is_virtual():
        if requested:
            print("Virtual machine detected. Enabling zeroing of free space as requested.")
            return True
        print("This seems to be a virtual machine. Do you want to zero free space?")
        print("THIS IS FOR VIRTUALBOX GUESTS ONLY")
        return yes_or_no()
    if requested:
        print("This does not seem to be a virtual machine. Are you sure you want to zero free space regardless?")
        print("THIS IS FOR VIRTUALBOX GUESTS ONLY")
        return yes_or_no()
    return False


def trim() -> None:
    """Trim all mounted file systems."""
    if shutil.which("fstrim") is None:
        print_info("fstrim not found")
        return
    print_info("Running fstrim")
    run(["fstrim", "-a", "-v"], sudo=True)


def virtualbox_host() -> None:
    """Run the VirtualBox host maintenance script.

    This does not work yet, as it does not capture output.
    """
    if shutil.which("virtualbox") is None:
        print_info("VirtualBox not found")
        return
    print_info("Running VirtualBox maintenance script.")
    run([str(REPO_DIR / "virtualbox" / "vbox_host_maintenance.sh")])


def zero_free_space() -> None:
    """Zero free disk space on the root partition."""
    print_info("Zeroing free disk space on /")
    # dd exits with an error once the disk is full, which is the expected outcome.
    run(["dd", "if=/dev/zero", f"of={ZEROFREE_PATH}", "bs=4096k", "status=progress"], check=False, sudo=True)
    print_info("Removing temporary file.")
    run(["rm", "-f", str(ZEROFREE_PATH)], sudo=True)
    print_info("Zeroing ready.")
