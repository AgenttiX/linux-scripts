"""Script for quickly installing Android apps over ADB

TODO: Work in progress
"""

import argparse
import os.path
import requests
import typing as tp

# python-adb may require the following to work:
# sudo apt-get install gcc libssl-dev python3-dev swig
from adb import adb_commands
from adb.sign_m2crypto import M2CryptoSigner as Signer
from gplaycli import gplaycli

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER = os.path.join(SCRIPT_FOLDER, "apps")
SIGNER = Signer(os.path.expanduser("~/.android/adbkey"))

os.makedirs(APP_FOLDER, exist_ok=True)


def download_play(url: str, args: tp.List[str] = None):
    parser = argparse.ArgumentParser()
    args: argparse.Namespace = parser.parse_args(["--download", url, *args])
    gplaycli.GPlaycli(args)


def download(url: str, path: str):
    data = requests.get(url, allow_redirects=True)
    with open(path, "wb") as file:
        file.write(data.content)


def download_apps_play(apps: tp.List[str]):
    for url in apps:
        download_play(url)


def install_default_apps(device: adb_commands.AdbCommands):
    communication_apps = [
        "com.whatsapp",
        "org.thoughtcrime.securesms",
        "org.telegram.messenger",
    ]
    utility_apps = [
        "com.authy.authy",
        "com.lonelycatgames.Xplore",
        # SD Maid
        "eu.thedarken.sdm",
        "net.sourceforge.opencamera",
        "org.zwanoo.android.speedtest",
    ]
    direct_apps = {
        "https://f-droid.org/F-Droid.apk": "F-Droid.apk",
        "https://github.com/YTVanced/VancedManager/releases/latest/download/manager.apk": "Vanced_manager.apk"
    }

    # TODO:
    # - split the apps to categories
    # - add settings configuration
    # https://stackoverflow.com/questions/14432706/adb-command-to-open-settings-and-change-them


def testing(device: adb_commands.AdbCommands):
    testing_apps = [
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


def main():
    device = adb_commands.AdbCommands()
    device.ConnectDevice(rsa_keys=[SIGNER])
    install_default_apps(device)
    testing(device)


if __name__ == "__main__":
    main()
