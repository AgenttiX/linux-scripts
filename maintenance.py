#!/usr/bin/env python3

"""
Routine GNU/Linux maintenance

Created by Mika Mäki 2019

TODO: work in progress!
"""

import os
import subprocess as sp


BLEACHBIT_FEATURES = [
    "adobe_reader.*",
    "amsn.*",
    "amule.*",
    "apt.*",
    "audacious.*",
    "bash.*",
    "beagle.*",
    "chromium.*",
    "d4x.*",
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
    "firefox.cache",
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
    sp.run(["apt-get", "update"], check=True)
    # sp.run(["apt-get", "autoremove", "-y"], check=True)
    sp.run(["apt-get", "dist-upgrade", "-y"], check=True)
    # sp.run(["apt-get", "upgrade", "-y"], check=True)
    sp.run(["apt-get", "autoremove", "-y"], check=True)
    sp.run(["apt-get", "autoclean", "-y"], check=True)


def bleachbit() -> None:
    if os.path.exists("/usr/bin/bleachbit"):
        sp.run(["bleachbit", "--clean"] + BLEACHBIT_FEATURES, check=True)
    else:
        print("bleachbit not found")


def security() -> None:
    if os.path.exists("/usr/bin/freshclam"):
        sp.run(["freshclam", "-d"], check=True)
    else:
        print("freshclam not found")

    if os.path.exists("/usr/sbin/chkrootkit"):
        sp.run(["chkrootkit", "-q"], check=True)
    else:
        print("chkrootkit not found")

    if os.path.exists("/usr/bin/rkhunter"):
        sp.run(["rkhunter", "--update", "-q"])
        sp.run(["rkhunter", "-c", "-q"])


def trim() -> None:
    if os.path.exists("/sbin/fstrim"):
        sp.run(["fstrim", "-a", "-v"], check=True)
        # sp.run(["fstrim", "/", "-v"], check=True)
    else:
        print("fstrim not found")


if __name__ == "__main__":
    apt()
    security()
    # bleachbit()
    trim()
