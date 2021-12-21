"""Script for quickly installing Android apps over ADB

TODO: Work in progress
"""

from adb import adb_commands

import android_tools as tools


COMMUNICATION_APPS = [
    "com.whatsapp",
    "org.thoughtcrime.securesms",
    "org.telegram.messenger",
]
UTILITY_APPS = [
    "com.authy.authy",
    "com.lonelycatgames.Xplore",
    # SD Maid
    "eu.thedarken.sdm",
    "net.sourceforge.opencamera",
    "org.zwanoo.android.speedtest",
]
DIRECT_APPS = {
    "https://f-droid.org/F-Droid.apk": "F-Droid.apk",
    "https://github.com/YTVanced/VancedManager/releases/latest/download/manager.apk": "Vanced_manager.apk"
}
TESTING_APPS = [
    "com.futuremark.dmandroid.application",
    "com.futuremark.pcmark.android.benchmark",
    "com.glbenchmark.glbenchmark27",
    "com.primatelabs.banff",
    "com.primatelabs.geekbench",
    "com.primatelabs.geekbench4",
    "com.primatelabs.geekbench5",
    "de.srlabs.snoopsnitch",
    "org.ogre.browser",
    "org.zwanoo.android.speedtest",
]


def install_default_apps(device: adb_commands.AdbCommands):
    pass
    # TODO:
    # - split the apps to categories
    # - add settings configuration
    # https://stackoverflow.com/questions/14432706/adb-command-to-open-settings-and-change-them


def main():
    # tools.download_multi(DIRECT_APPS)
    tools.download_play_multi(UTILITY_APPS)
    tools.download_play_multi(TESTING_APPS)
    # device = adb_commands.AdbCommands()
    # device.ConnectDevice(rsa_keys=[tools.SIGNER])
    # install_default_apps(device)


if __name__ == "__main__":
    main()
