import argparse
import os.path
import requests
import typing as tp

# Python-ADB may require additional packages described in requirements.txt.
from adb.sign_m2crypto import M2CryptoSigner as Signer
# from gplaycli import gplaycli
from gplaydl import gplaydl

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER = os.path.join(SCRIPT_FOLDER, "apps")
SIGNER = Signer(os.path.expanduser("~/.android/adbkey"))

os.makedirs(APP_FOLDER, exist_ok=True)


def download(url: str, path: str):
    data = requests.get(url, allow_redirects=True)
    with open(path, "wb") as file:
        file.write(data.content)


def download_multi(urls_names: tp.Dict[str, str], folder: str = APP_FOLDER):
    for url, name in urls_names.items():
        download(url, os.path.join(folder, name))


def download_play(
        package_id: str,
        folder: str = APP_FOLDER,
        device: str = gplaydl.devicecode,
        expansionfiles: bool = True,
        splits: bool = True
):
    # parser = argparse.ArgumentParser()
    # if args is None:
    #     args = []
    # args2: argparse.Namespace = parser.parse_args(["--download", url, *args])
    # gplaycli.GPlaycli(args2)

    gplaydl.args.storagepath = folder
    gplaydl.args.device = device
    gplaydl.args.expansionfiles = "y" if expansionfiles else "n"
    gplaydl.args.splits = "y" if splits else "n"
    gplaydl.downloadapp(package_id)


def download_play_multi(apps: tp.List[str]):
    for url in apps:
        download_play(url)
