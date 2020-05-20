#!/usr/bin/env python3

"""
Routine GNU/Linux maintenance

Created by Mika Mäki 2019-2020

TODO: work in progress!
"""

import argparse
import logging
import os
import subprocess as sp
import time
import typing as tp

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


def run(command: tp.List[str], check: bool = True) -> int:
    logger.info(f"Running {command}")
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
    while True:
        stdout = process.stdout.readline().decode("utf-8").rstrip("\r|\n")
        stderr = process.stderr.readline().decode("utf-8").rstrip("\r|\n")
        if not stdout and not stderr and process.poll() is not None:
            break
        if stdout:
            print(stdout)
            logger.info(stdout)
        if stderr:
            print(stderr)
            logger.error(stderr)
    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()
    if check and return_code:
        raise sp.CalledProcessError(return_code, command)
    return return_code


def apt() -> None:
    print("Running apt")
    run(["apt-get", "update"])
    # run(["apt-get", "autoremove", "-y"])
    while True:
        apt_ret = run(["apt-get", "dist-upgrade", "-y"], check=False)
        if apt_ret == 0:
            break
        elif apt_ret == 100:
            pass
        else:
            raise ValueError(f"Got unknown APT return code: {apt_ret}")
        print("Waiting for APT lock to be freed")
        time.sleep(APT_WAIT_TIME)

    # run(["apt-get", "upgrade", "-y"])
    run(["apt-get", "autoremove", "-y"])
    run(["apt-get", "autoclean", "-y"])


def bleachbit(deep: bool = False, firefox: bool = False, thunderbird: bool = False) -> None:
    if os.path.exists("/usr/bin/bleachbit"):
        print("Running Bleachbit")
        args = ["bleachbit", "--clean"] + BLEACHBIT_FEATURES
        if deep:
            print("Using deep scan. This will take a while.")
            logger.info("Using deep scan. This will take a while.")
            args += BLEACHBIT_DEEP
        if firefox:
            args += BLEACHBIT_FIREFOX
        if thunderbird:
            args += BLEACHBIT_THUNDERBIRD
        # Bleachbit does not run with the run() function for some reason
        sp.run(args, check=True)
    else:
        print("Bleachbit not found")


def docker(all_unused_images: bool = False) -> None:
    if os.path.exists("/usr/bin/docker"):
        print("Pruning Docker")
        args = ["docker", "system", "prune", "-f"]
        if all_unused_images:
            args.append("-a")
        run(args)
    else:
        print("Docker not found")


def security() -> None:
    if os.path.exists("/usr/bin/freshclam"):
        print("Running freshclam")
        freshclam_ret = run(["freshclam", "-d"], check=False)
        if freshclam_ret in [2, 62]:
            print("Freshclam is already running")
        elif freshclam_ret != 0:
            raise ValueError(f"Got unknown freshclam return code: {freshclam_ret}")
    else:
        print("freshclam not found")

    if os.path.exists("/usr/sbin/chkrootkit"):
        print("Running chkrootkit")
        run(["chkrootkit", "-q"])
    else:
        print("chkrootkit not found")

    if os.path.exists("/usr/bin/rkhunter"):
        print("Running rkhunter")
        run(["rkhunter", "--update", "-q"])
        run(["rkhunter", "-c", "-q"])


def trim() -> None:
    if os.path.exists("/sbin/fstrim"):
        print("Running fstrim")
        run(["fstrim", "-a", "-v"])
        # run(["fstrim", "/", "-v"])
    else:
        print("fstrim not found")


def main():
    parser = argparse.ArgumentParser(description="Maintenance script")
    parser.add_argument("--deep", help="Deep-clean all", action="store_true")
    parser.add_argument("--docker", help="Deep-clean Docker", action="store_true")
    parser.add_argument("--firefox", help="Deep-clean Firefox", action="store_true")
    parser.add_argument("--thunderbird", help="Deep-clean Thunderbird", action="store_true")
    args = parser.parse_args()
    logger.info(f"Args: {args}")

    if args.deep:
        print("Deep scan has been selected. Some processes may take a long time.")
        logger.info("Deep scan has been selected. Some processes may take a long time.")

    print("Running maintenance script")
    apt()
    print()
    security()
    print()
    docker(args.deep or args.docker)
    print()
    bleachbit(deep=args.deep, firefox=(args.deep or args.firefox), thunderbird=(args.deep or args.thunderbird))
    print()
    trim()


if __name__ == "__main__":
    main()
