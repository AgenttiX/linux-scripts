#!/usr/bin/env python3

"""
Routine maintenance script for GNU/Linux-based systems
"""

import argparse
import logging
import os
import subprocess as sp
import time
import typing as tp

from utils import print_info, run

logger = logging.getLogger(__name__)
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_path):
    os.mkdir(log_path)

logging.basicConfig(
    handlers=[
        logging.FileHandler(os.path.join(log_path, "maintenance_{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S"))))
    ],
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s"
)

APT_WAIT_TIME: int = 1

BLEACHBIT_FEATURES: tp.List[str] = [
    "adobe_reader.*",
    "amsn.*",
    "amule.*",
    "apt.*",
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
    "firefox.download_history",
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

BLEACHBIT_DEEP: tp.List[str] = [
    "deepscan.backup",
    "deepscan.ds_store",
    "deepscan.thumbs_db",
    "deepscan.tmp"
]

BLEACHBIT_FIREFOX: tp.List[str] = [
    "firefox.*"
]

BLEACHBIT_THUNDERBIRD: tp.List[str] = [
    "thunderbird.cache",
    "thunderbird.index",
]


def apt() -> None:
    print_info("Running apt")
    run(["apt-get", "update"], sudo=True)
    # run(["apt-get", "autoremove", "-y"])
    while True:
        apt_ret = run(["apt-get", "dist-upgrade", "-y"], check=False, sudo=True)
        if apt_ret == 0:
            break
        if apt_ret != 100:
            error_text = f"Got unknown APT return code: {apt_ret}"
            logger.error(error_text)
            raise ValueError(error_text)
        print_info("Waiting for APT lock to be freed")
        time.sleep(APT_WAIT_TIME)

    # run(["apt-get", "upgrade", "-y"])
    run(["apt-get", "autoremove", "-y"], sudo=True)
    run(["apt-get", "autoclean", "-y"], sudo=True)


def bleachbit(deep: bool = False, firefox: bool = False, thunderbird: bool = False) -> None:
    if not os.path.exists("/usr/bin/bleachbit"):
        print_info("Bleachbit not found")
        return
    print_info("Running Bleachbit")
    args = ["bleachbit", "--clean"] + BLEACHBIT_FEATURES
    if deep:
        print_info("Using deep scan. This will take a while.")
        args += BLEACHBIT_DEEP
    if firefox:
        args += BLEACHBIT_FIREFOX
    if thunderbird:
        args += BLEACHBIT_THUNDERBIRD
    # Bleachbit does not run with the run() function for some reason
    if os.geteuid() != 0:
        args.insert(0, "sudo")
    sp.run(args, check=True)


def docker(all_unused_images: bool = False) -> None:
    if not os.path.exists("/usr/bin/docker"):
        print_info("Docker not found")
        return
    print_info("Pruning Docker")
    args = ["docker", "system", "prune", "-f"]
    if all_unused_images:
        args.append("-a")
    run(args)


def fwupdmgr() -> None:
    if not os.path.exists("/usr/bin/fwupdmgr"):
        print_info("fwupdmgr is not installed")
        return
    print_info("Checking for firmware updates")
    ret = run(["fwupdmgr", "refresh"], check=False)
    # Return code 2 = no updates available
    if ret > 0 and ret != 2:
        print_info(f"Got return code {ret}. Is this an error?")

    ret = run(["fwupdmgr", "get-updates"], check=False)
    if ret > 0 and ret != 2:
        print_info(f"Got return code {ret}. Is this an error?")


def security() -> None:
    if os.path.exists("/usr/bin/freshclam"):
        print_info("Running freshclam")
        freshclam_ret = run(["freshclam", "-d"], check=False, sudo=True)
        if freshclam_ret in [2, 62]:
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


def trim() -> None:
    if os.path.exists("/sbin/fstrim"):
        print_info("Running fstrim")
        run(["fstrim", "-a", "-v"], sudo=True)
        # run(["fstrim", "/", "-v"])
    else:
        print_info("fstrim not found")


def main():
    parser = argparse.ArgumentParser(description="Maintenance script")
    parser.add_argument("--deep", help="Deep-clean all", action="store_true")
    parser.add_argument("--docker", help="Deep-clean Docker", action="store_true")
    parser.add_argument("--firefox", help="Deep-clean Firefox", action="store_true")
    parser.add_argument("--thunderbird", help="Deep-clean Thunderbird", action="store_true")
    args = parser.parse_args()
    logger.info("Args: %s", args)

    if args.deep:
        print_info("Deep scan has been selected. Some processes may take a long time.")

    print_info("Running maintenance script")
    apt()
    print()
    security()
    print()
    docker(args.deep or args.docker)
    print()
    bleachbit(deep=args.deep, firefox=(args.deep or args.firefox), thunderbird=(args.deep or args.thunderbird))
    print()
    trim()
    print()
    fwupdmgr()


if __name__ == "__main__":
    main()
