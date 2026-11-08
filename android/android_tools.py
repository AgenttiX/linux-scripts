"""Utilities for downloading Android apps."""

# import argparse
import os.path

import requests

# Python-ADB may require additional packages described in requirements.txt.
# from adb.sign_m2crypto import M2CryptoSigner as Signer
# from gplaycli import gplaycli
# from gplaydl import gplaydl

SCRIPT_FOLDER: str = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER: str = os.path.join(SCRIPT_FOLDER, "apps")
# SIGNER = Signer(os.path.expanduser("~/.android/adbkey"))

os.makedirs(APP_FOLDER, exist_ok=True)


def download(url: str, path: str) -> None:
    """Download a file.

    :param url: URL of the file
    :param path: path to which the file is saved
    """
    data = requests.get(url, allow_redirects=True)
    with open(path, "wb") as file:
        file.write(data.content)


def download_multi(urls_names: dict[str, str], folder: str = APP_FOLDER) -> None:
    """Download multiple files.

    :param urls_names: dictionary of URLs and the corresponding file names
    :param folder: folder to which the files are saved
    """
    for url, name in urls_names.items():
        print(f"Downloading: {name}")
        download(url, os.path.join(folder, name))


def download_play(
        package_id: str,  # noqa: ARG001
        folder: str = APP_FOLDER,  # noqa: ARG001
        device: str | None = None,  # noqa: ARG001  # = gplaydl.devicecode,
        expansionfiles: bool = True,  # noqa: ARG001
        splits: bool = True  # noqa: ARG001
) -> None:
    """Download an apk from Google Play.

    This is currently a stub, as the gplaydl backend is broken.
    The arguments are kept for when a replacement backend is implemented.

    :param package_id: package ID of the app
    :param folder: folder to which the apk is saved
    :param device: device code to download the apk for
    :param expansionfiles: whether to download expansion files
    :param splits: whether to download split apks
    """
    # parser = argparse.ArgumentParser()
    # if args is None:
    #     args = []
    # args2: argparse.Namespace = parser.parse_args(["--download", url, *args])
    # gplaycli.GPlaycli(args2)

    # TODO: gplaydl is broken and should be replaced with something else.
    # gplaydl.args.storagepath = folder
    # gplaydl.args.device = device
    # gplaydl.args.expansionfiles = "y" if expansionfiles else "n"
    # gplaydl.args.splits = "y" if splits else "n"
    # gplaydl.downloadapp(package_id)
    print("Gplaydl is broken. Cannot download apk.")


def download_play_multi(apps: list[str]) -> None:
    """Download multiple apks from Google Play.

    :param apps: package IDs of the apps
    """
    for url in apps:
        download_play(url)
