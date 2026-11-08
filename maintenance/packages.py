"""Software and firmware updates."""

import shutil

from utils.misc_utils import print_info, run, run_interactive

#: How long APT should wait for the dpkg lock to be freed, in seconds
APT_LOCK_TIMEOUT: int = 600
#: fwupdmgr return code when no updates are available
FWUPDMGR_RET_NO_UPDATES: int = 2


def apt() -> None:
    """Upgrade APT packages and remove the unnecessary ones.

    APT is run interactively, so that it can ask e.g. about configuration file conflicts.
    """
    if shutil.which("apt-get") is None:
        print_info("apt-get not found")
        return
    print_info("Running APT")
    for args in (["update"], ["dist-upgrade", "-y"], ["autoremove", "-y"], ["autoclean", "-y"]):
        run_interactive(["apt-get", "-o", f"DPkg::Lock::Timeout={APT_LOCK_TIMEOUT}", *args], sudo=True)


def flatpak() -> None:
    """Update Flatpak apps and remove unused ones."""
    if shutil.which("flatpak") is None:
        print_info("Flatpak not found")
        return
    print_info("Removing unused Flatpak apps (so that unnecessary apps are not updated)")
    run(["flatpak", "remove", "--unused", "-y"])
    print_info("Updating Flatpak apps")
    # Flatpak may return a non-zero exit code even when it's capable of installing the updates.
    run(["flatpak", "update", "-y"], check=False)
    print_info("Removing unused Flatpak apps (if some apps have become unused due to the update)")
    # Especially different Nvidia driver versions come as separate packages, and upgrades may leave old
    # versions dangling on the system.
    run(["flatpak", "remove", "--unused", "-y"])


def fwupdmgr() -> None:
    """Check for firmware updates."""
    if shutil.which("fwupdmgr") is None:
        print_info("fwupdmgr not found")
        return
    print_info("Checking for firmware updates")
    for command in ("refresh", "get-updates"):
        ret = run(["fwupdmgr", command], check=False)
        if ret > 0 and ret != FWUPDMGR_RET_NO_UPDATES:
            print_info(f"Got return code {ret}. Is this an error?")


def snap() -> None:
    """Update snaps."""
    if shutil.which("snap") is None:
        print_info("Snap not found")
        return
    print_info("Updating snaps")
    run(["snap", "refresh"], sudo=True)


def zgen() -> None:
    """Run zgen."""
    if shutil.which("zgen") is None:
        print_info("zgen not found")
        return
    print_info("Running zgen")
    run(["zgen"])
