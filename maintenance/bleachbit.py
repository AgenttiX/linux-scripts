"""System cleaning with BleachBit."""

import argparse
import os
import shutil

from utils.misc_utils import print_info, run_interactive

BLEACHBIT_DEEP: list[str] = [
    "deepscan.backup",
    "deepscan.ds_store",
    "deepscan.thumbs_db",
    "deepscan.tmp"
]

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

BLEACHBIT_FIREFOX: list[str] = [
    "firefox.*"
]

BLEACHBIT_ROOT: list[str] = [
    "apt.*",
]

BLEACHBIT_THUNDERBIRD: list[str] = [
    "thunderbird.cache",
    "thunderbird.index",
]


def bleachbit(deep: bool = False, firefox: bool = False, thunderbird: bool = False) -> None:
    """Clean the system with BleachBit.

    When run as root, the system-wide cleaners are run as well.
    BleachBit cleans the home directory of the user running it,
    so it should be run both as a normal user and as root.

    :param deep: whether to run the slow deep scan
    :param firefox: whether to clean all Firefox data
    :param thunderbird: whether to clean the Thunderbird cache and index
    """
    if shutil.which("bleachbit") is None:
        print_info("BleachBit not found")
        return
    print_info(f"Running BleachBit as {'root' if os.geteuid() == 0 else 'the current user'}")
    if deep:
        print_info("Using deep scan. This will take a while.")
    # BleachBit does not work with run() for some reason.
    run_interactive(bleachbit_command(deep=deep, firefox=firefox, thunderbird=thunderbird, root=os.geteuid() == 0))


def bleachbit_args(args: argparse.Namespace) -> None:
    """Clean the system with BleachBit according to the command-line arguments.

    :param args: command-line arguments
    """
    bleachbit(deep=args.deep, firefox=args.deep or args.firefox, thunderbird=args.deep or args.thunderbird)


def bleachbit_command(deep: bool, firefox: bool, thunderbird: bool, root: bool) -> list[str]:
    """Create the BleachBit command.

    :param deep: whether to run the slow deep scan
    :param firefox: whether to clean all Firefox data
    :param thunderbird: whether to clean the Thunderbird cache and index
    :param root: whether to include the cleaners that require root privileges
    :return: BleachBit command and its arguments
    """
    command = ["bleachbit", "--clean", *BLEACHBIT_FEATURES]
    if deep:
        command += BLEACHBIT_DEEP
    if firefox:
        command += BLEACHBIT_FIREFOX
    if thunderbird:
        command += BLEACHBIT_THUNDERBIRD
    if root:
        command += BLEACHBIT_ROOT
    return command
