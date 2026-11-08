#!/usr/bin/env python3

"""Routine maintenance script for GNU/Linux-based systems."""

import argparse
import glob
import logging
import os
import shutil
import subprocess as sp
import time

import misc_utils as utils
from misc_utils import print_info, run

SCRIPT_PATH: str = os.path.dirname(os.path.abspath(__file__))
LOG_PATH: str = os.path.join(SCRIPT_PATH, "logs")
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(
    handlers=[
        logging.FileHandler(os.path.join(LOG_PATH, "maintenance_{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S"))))
    ],
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)

APT_WAIT_TIME: int = 1
#: APT return code when the APT lock is held by another process
APT_RET_LOCKED: int = 100

BLEACHBIT_FEATURES: list[str] = [
    "adobe_reader.*",
    "amsn.*",
    "amule.*",
    "audacious.*",
    "bash.*",
    "beagle.*",
    "chromium.*",
    # "chromium.cache",
    # "chromium.cookies",
    # "chromium.current_session",
    # "chromium.dom",
    # "chromium.form_history",
    # "chromium.history",
    # "chromium.passwords",
    # "chromium.search_engines",
    # "chromium.vacuum"
    "d4x.*",
    # "deepscan.backup",
    # "deepscan.ds_store",
    # "deepscan.thumbs_db",
    # "deepscan.tmp",
    "easytag.*",
    "elinks.*",
    "emesene.*",
    "epiphany.*",
    "evolution.*",
    "exaile.*",
    "filezilla.*",
    # "firefox.*",
    # "firefox.backup",
    "firefox.cache",
    # "firefox.cookies",
    "firefox.crash_reports",
    "firefox.dom",
    # "firefox.download_history",
    "firefox.forms",
    # "firefox.passwords",
    "firefox.session_restore",
    "firefox.site_preferences",
    "firefox.url_history",
    "firefox.vacuum",
    "flash.*",
    "gedit.*",
    "gftp.*",
    "gimp.*",
    "gl-117.*",
    "gnome.*",
    "google_chrome.*",
    "google_earth.*",
    "google_toolbar.*",
    "gpodder.*",
    "gwenview.*",
    "hexchat.*",
    "hippo_opensim_viewer.*",
    "java.*",
    "kde.*",
    "konqueror.*",
    "libreoffice.*",
    "liferea.*",
    "links2.*",
    "midnightcommander.*",
    "miro.*",
    "nautilus.*",
    "nexuiz.*",
    "octave.*",
    "openofficeorg.*",
    "opera.*",
    "pidgin.*",
    "realplayer.*",
    "recoll.*",
    "rhythmbox.*",
    "screenlets.*",
    "seamonkey.*",
    "secondlife_viewer.*",
    "skype.*",
    "sqlite3.*",
    "system.cache",
    "system.clipboard",
    # "system.custom",
    "system.desktop_entry",
    # "system.free_disk_space",
    # "system.localizations",
    # "system.memory",
    "system.recent_documents",
    "system.rotated_logs",
    "system.tmp",
    "system.trash",
    "thumbnails.*",
    # "thunderbird.cache",
    "thunderbird.cookies",
    # "thunderbird.index",
    # "thunderbird.passwords",
    "thunderbird.vacuum",
    # "transmission.blocklists",
    "transmission.history",
    # "transmission.torrents",
    "tremulous.*",
    "vim.*",
    "vlc.*",
    "vuze.*",
    "warzone2100.*",
    "wine.*",
    "winetricks.*",
    "x11.*",
    "xine.*",
    "yum.*"
]

BLEACHBIT_ROOT: list[str] = [
    "apt.*",
]

BLEACHBIT_DEEP: list[str] = [
    "deepscan.backup",
    "deepscan.ds_store",
    "deepscan.thumbs_db",
    "deepscan.tmp"
]

BLEACHBIT_FIREFOX: list[str] = [
    "firefox.*"
]

#: freshclam return codes when freshclam is already running
FRESHCLAM_RET_RUNNING: tuple[int, ...] = (2, 62)
#: fwupdmgr return code when no updates are available
FWUPDMGR_RET_NO_UPDATES: int = 2

BLEACHBIT_THUNDERBIRD: list[str] = [
    "thunderbird.cache",
    "thunderbird.index",
]


def apptainer() -> None:
    """Clean the Apptainer cache."""
    if shutil.which("apptainer") is None:
        print_info("Apptainer not found")
        return
    print_info("Cleaning Apptainer cache")
    run(["apptainer", "cache", "clean"])


def apt() -> None:
    """Upgrade APT packages.

    This does not print output properly while the process is being run,
    which makes it impossible to answer prompts.

    :raises ValueError: if APT returns an unknown return code
    """
    print_info("Running apt")
    run(["apt-get", "update"], sudo=True)
    # run(["apt-get", "autoremove", "-y"])
    while True:
        apt_ret = run(["apt-get", "dist-upgrade", "-y"], check=False, sudo=True)
        if apt_ret == 0:
            break
        if apt_ret != APT_RET_LOCKED:
            error_text = f"Got unknown APT return code: {apt_ret}"
            logger.error(error_text)
            raise ValueError(error_text)
        print_info("Waiting for APT lock to be freed")
        time.sleep(APT_WAIT_TIME)

    # run(["apt-get", "upgrade", "-y"])
    run(["apt-get", "autoremove", "-y"], sudo=True)
    run(["apt-get", "autoclean", "-y"], sudo=True)


def bleachbit(deep: bool = False, firefox: bool = False, thunderbird: bool = False) -> None:
    """Clean the system with BleachBit.

    :param deep: whether to run the slow deep scan
    :param firefox: whether to clean all Firefox data
    :param thunderbird: whether to clean the Thunderbird cache and index
    """
    if not os.path.exists("/usr/bin/bleachbit"):
        print_info("Bleachbit not found")
        return
    print_info("Running Bleachbit")
    args = ["bleachbit", "--clean", *BLEACHBIT_FEATURES]
    if deep:
        print_info("Using deep scan. This will take a while.")
        args += BLEACHBIT_DEEP
    if firefox:
        args += BLEACHBIT_FIREFOX
    if thunderbird:
        args += BLEACHBIT_THUNDERBIRD
    # Bleachbit does not run with the run() function for some reason.
    # Run both as root and as the current user.
    if os.geteuid() != 0:
        args2 = ["sudo", *args, *BLEACHBIT_ROOT]
        sp.run(args2, check=True)
    else:
        args += BLEACHBIT_ROOT
    sp.run(args, check=True)


def docker(all_unused_images: bool = False) -> None:
    """Prune unused Docker data.

    :param all_unused_images: whether to remove all unused images and not just dangling ones
    """
    if not os.path.exists("/usr/bin/docker"):
        print_info("Docker not found")
        return
    print_info("Pruning Docker")
    args = ["docker", "system", "prune", "-f"]
    if all_unused_images:
        args.append("-a")
    run(args)


def flatpak() -> None:
    """Update Flatpak apps and remove unused ones."""
    if os.path.exists("/usr/bin/flatpak"):
        print_info("Removing unused Flatpak apps (so that unnecessary apps are not updated)")
        run(["flatpak", "remove", "--unused"])
        print_info("Updating Flatpak apps")
        # Flatpak may return a non-zero exit code even when it's capable of installing the updates.
        run(["flatpak", "update"], check=False)
        print_info("Removing unused Flatpak apps (if some apps have become unused due to the update)")
        # Especially different Nvidia driver versions come as separate packages, and upgrades may leave old
        # versions dangling on the system.
        run(["flatpak", "remove", "--unused"])
    else:
        print_info("flatpak not found")


def fwupdmgr() -> None:
    """Check for firmware updates."""
    if not os.path.exists("/usr/bin/fwupdmgr"):
        print_info("fwupdmgr is not installed")
        return
    print_info("Checking for firmware updates")
    ret = run(["fwupdmgr", "refresh"], check=False)
    if ret > 0 and ret != FWUPDMGR_RET_NO_UPDATES:
        print_info(f"Got return code {ret}. Is this an error?")

    ret = run(["fwupdmgr", "get-updates"], check=False)
    if ret > 0 and ret != FWUPDMGR_RET_NO_UPDATES:
        print_info(f"Got return code {ret}. Is this an error?")


def get_zerofree_status(args: argparse.Namespace) -> bool:
    """Determine whether free disk space should be zeroed, asking the user if necessary.

    :param args: command-line arguments
    :return: whether to zero free disk space
    """
    if utils.is_virtual():
        if args.zerofree:
            print("Virtual machine detected. Enabling zeroing of free space as requested.")
            return True
        print("This seems to be a virtual machine. Do you want to zero free space?")
        print("THIS IS FOR VIRTUALBOX GUESTS ONLY")
        return utils.yes_or_no()
    if args.zerofree:
        print("This does not seem to be a virtual machine. Are you sure you want to zero free space regardless?")
        print("THIS IS FOR VIRTUALBOX GUESTS ONLY")
        return utils.yes_or_no()
    return False


def mdadm() -> None:
    """Run mdadm scrubbing.

    https://wiki.archlinux.org/title/RAID#Scrubbing
    """
    if os.path.exists("/sbin/mdadm"):
        print_info(
            "Starting mdadm scrubbing. "
            "You can monitor the progress with \"cat /proc/mdstat\". "
            "Rebooting will restart the scrubbing from the beginning.")
        endpoints = glob.glob("/sys/block/md*/md/sync_action")
        for path in endpoints:
            with open(path, "w") as endpoint:
                endpoint.write("check")
        with open("/proc/mdstat") as file:
            print(file.read())


def remove_custom_files() -> None:
    """Remove custom files from the home directory."""
    print("Removing custom files")
    home = os.path.join("/home", utils.get_user())
    home_files = [
        "client_state.xml",
        "coproc_info.xml",
        "lockfile",
        "stderrgpudetect.txt",
        "stdoutgpudetect.txt",
        "time_stats_log"
    ]
    for file in home_files:
        full_path = os.path.join(home, file)
        if os.path.exists(full_path):
            print(f"Removing \"{full_path}\"")
            os.remove(full_path)


def security() -> None:
    """Run security scanners.

    :raises ValueError: if freshclam returns an unknown return code
    """
    if os.path.exists("/usr/bin/freshclam"):
        print_info("Running freshclam")
        freshclam_ret = run(["freshclam", "-d"], check=False, sudo=True)
        if freshclam_ret in FRESHCLAM_RET_RUNNING:
            print_info("Freshclam is already running")
        elif freshclam_ret != 0:
            raise ValueError(f"Got unknown freshclam return code: {freshclam_ret}")
    else:
        print_info("freshclam not found")

    if os.path.exists("/usr/sbin/chkrootkit"):
        print_info("Running chkrootkit")
        run(["chkrootkit", "-q"], sudo=True)
    else:
        print_info("chkrootkit not found")

    if os.path.exists("/usr/bin/rkhunter"):
        print_info("Running rkhunter")
        run(["rkhunter", "--update", "-q"], check=False, sudo=True)
        run(["rkhunter", "-c", "-q"], check=False, sudo=True)


def snap() -> None:
    """Update snaps."""
    if os.path.exists("/usr/bin/snap"):
        print_info("Updating snaps")
        run(["snap", "refresh"], sudo=True)
    else:
        print_info("snap not found")


def trim() -> None:
    """Trim all mounted file systems."""
    if os.path.exists("/sbin/fstrim"):
        print_info("Running fstrim")
        run(["fstrim", "-a", "-v"], sudo=True)
        # run(["fstrim", "/", "-v"])
    else:
        print_info("fstrim not found")


def virtualbox_host() -> None:
    """Run the VirtualBox host maintenance script.

    This does not work, as it does not capture output.
    """
    if os.path.exists("/usr/bin/virtualbox"):
        print_info("Running VirtualBox maintenance script.")
        run([os.path.join(SCRIPT_PATH, "virtualbox", "vbox_host_maintenance.sh")])
    else:
        print_info("VirtualBox not found")


def zerofree() -> None:
    """Zero free disk space on the root partition."""
    print_info("Zeroing free disk space on /")
    # The directory /var/tmp is used instead of /tmp, as the latter may be on a ramdisk or a separate partition.
    run(["dd", "if=/dev/zero", "of=/var/tmp/bigemptyfile", "bs=4096k", "status=progress"], sudo=True)
    print_info("Removing temporary file.")
    run(["rm", "/var/tmp/bigemptyfile"], sudo=True)
    print_info("Zeroing ready.")


def zgen() -> None:
    """Run zgen."""
    if shutil.which("zgen") is not None:
        print_info("Running zgen")
        run(["zgen"])
    else:
        print_info("zgen not found.")


def main() -> None:
    """Run the maintenance script.

    :raises ValueError: if both reboot and shutdown are selected
    :raises NotImplementedError: if VirtualBox maintenance is selected
    """
    parser = argparse.ArgumentParser(description="Maintenance script")
    parser.add_argument("--bleachbit-only", help="Run only Bleachbit", action="store_true")
    parser.add_argument("--deep", help="Deep-clean all", action="store_true")
    parser.add_argument("--docker", help="Deep-clean Docker", action="store_true")
    parser.add_argument("--firefox", help="Deep-clean Firefox", action="store_true")
    parser.add_argument("--reboot", help="Reboot once the script is ready", action="store_true")
    parser.add_argument("--shutdown", help="Shutdown once the script is ready", action="store_true")
    parser.add_argument("--thunderbird", help="Deep-clean Thunderbird", action="store_true")
    parser.add_argument("--virtualbox", help="Optimize VirtualBox disk images on the host", action="store_true")
    parser.add_argument("--zerofree", help="Zero free disk space", action="store_true")
    args = parser.parse_args()
    logger.info("Args: %s", args)

    if args.reboot and args.shutdown:
        raise ValueError("Both reboot and shutdown cannot be selected simultaneously.")
    if args.deep:
        print_info("Deep scan has been selected. Some processes may take a long time.")
    if args.virtualbox:
        raise NotImplementedError("VirtualBox support does not work yet.")

    if args.bleachbit_only:
        bleachbit(deep=args.deep, firefox=(args.deep or args.firefox), thunderbird=(args.deep or args.thunderbird))
        return

    zero = get_zerofree_status(args)

    print_info("Running maintenance script")
    # apt()
    # print()
    snap()
    print()
    flatpak()
    print()
    zgen()
    print()
    security()
    print()
    apptainer()
    print()
    docker(args.deep or args.docker)
    print()
    bleachbit(
        deep=args.deep,
        firefox=args.deep or args.firefox,
        thunderbird=args.deep or args.thunderbird
    )
    print()
    remove_custom_files()
    print()
    trim()
    print()
    fwupdmgr()
    if zero:
        zerofree()
    mdadm()

    if args.reboot:
        run(["reboot", "now"])
    if args.shutdown:
        run(["shutdown", "now"])


if __name__ == "__main__":
    main()
