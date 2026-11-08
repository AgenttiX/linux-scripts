"""Security scanners."""

import shutil

from utils.misc_utils import print_info, run

#: freshclam return codes when freshclam is already running
FRESHCLAM_RET_RUNNING: tuple[int, ...] = (2, 62)


def chkrootkit() -> None:
    """Scan for rootkits with chkrootkit."""
    if shutil.which("chkrootkit") is None:
        print_info("chkrootkit not found")
        return
    print_info("Running chkrootkit")
    run(["chkrootkit", "-q"], sudo=True)


def freshclam() -> None:
    """Update the ClamAV virus database.

    :raises ValueError: if freshclam returns an unknown return code
    """
    if shutil.which("freshclam") is None:
        print_info("freshclam not found")
        return
    print_info("Running freshclam")
    ret = run(["freshclam", "-d"], check=False, sudo=True)
    if ret in FRESHCLAM_RET_RUNNING:
        print_info("freshclam is already running")
    elif ret != 0:
        raise ValueError(f"Got unknown freshclam return code: {ret}")


def rkhunter() -> None:
    """Scan for rootkits with rkhunter."""
    if shutil.which("rkhunter") is None:
        print_info("rkhunter not found")
        return
    print_info("Running rkhunter")
    run(["rkhunter", "--update", "-q"], check=False, sudo=True)
    run(["rkhunter", "-c", "-q"], check=False, sudo=True)


def scan() -> None:
    """Run all the security scanners."""
    freshclam()
    chkrootkit()
    rkhunter()
