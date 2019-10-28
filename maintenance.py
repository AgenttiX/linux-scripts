#!/usr/bin/env python3

"""
Routine GNU/Linux maintenance

Created by Mika Mäki 2019

TODO: work in progress!
"""

import os
import subprocess as sp
import typing as tp


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
    "deepscan.ds_store",
    "deepscan.thumbs_db",
    "deepscan.tmp",
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
    "system.desktop_entry",
    "system.rotated_logs",
    "system.tmp",
    "system.trash",
    "thumbnails.*",
    "thunderbird.cache",
    "thunderbird.cookies",
    "thunderbird.index",
    "thunderbird.vacuum",
    "tremulous.cache",
    "vim.*",
    "vlc.*",
    "vuze.*",
    "warzone2100.*",
    "wine.*",
    "winetricks.*",
    "x11.*",
    "xchat.*",
    "xine.*",
    "yum.*"
]


def apt() -> None:
    print("Running apt")
    sp.run(["apt-get", "update"], check=True)
    # sp.run(["apt-get", "autoremove", "-y"], check=True)
    sp.run(["apt-get", "dist-upgrade", "-y"], check=True)
    # sp.run(["apt-get", "upgrade", "-y"], check=True)
    sp.run(["apt-get", "autoremove", "-y"], check=True)
    sp.run(["apt-get", "autoclean", "-y"], check=True)


def bleachbit() -> None:
    if os.path.exists("/usr/bin/bleachbit"):
        print("Running Bleachbit")
        sp.run(["bleachbit", "--clean"] + BLEACHBIT_FEATURES, check=True)
    else:
        print("Bleachbit not found")


def docker() -> None:
    if os.path.exists("/usr/bin/docker"):
        print("Pruning Docker")
        sp.run(["docker", "system", "prune", "-f"], check=True)
    else:
        print("Docker not found")


def security() -> None:
    if os.path.exists("/usr/bin/freshclam"):
        print("Running freshclam")
        sp.run(["freshclam", "-d"], check=True)
    else:
        print("freshclam not found")

    if os.path.exists("/usr/sbin/chkrootkit"):
        print("Running chkrootkit")
        sp.run(["chkrootkit", "-q"], check=True)
    else:
        print("chkrootkit not found")

    if os.path.exists("/usr/bin/rkhunter"):
        print("Running rkhunter")
        sp.run(["rkhunter", "--update", "-q"])
        sp.run(["rkhunter", "-c", "-q"])


def trim() -> None:
    if os.path.exists("/sbin/fstrim"):
        print("Running fstrim")
        sp.run(["fstrim", "-a", "-v"], check=True)
        # sp.run(["fstrim", "/", "-v"], check=True)
    else:
        print("fstrim not found")


if __name__ == "__main__":
    print("Running maintenance script")
    apt()
    print()
    security()
    print()
    docker()
    # bleachbit()
    # print()
    trim()
