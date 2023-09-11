#!/usr/bin/env python3

"""
Control script for the integrated WWAN (3G, LTE etc.) modem of the following laptops:
- Lenovo ThinkPad T480
- Lenovo ThinkPad Twist S230u
This script is based on the use of mmcli.

This script was developed, since the integrated modem utilities of Kubuntu have
a lot of room for improvement in their usability.

https://manpages.ubuntu.com/manpages/trusty/man8/mmcli.8.html
https://manpages.debian.org/jessie/modemmanager/mmcli.8
"""

import os.path
import subprocess
import time
import typing as tp

# import utils

PIN_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modem-pin.txt")


def read_pin(path: str) -> str:
    with open(path) as file:
        pin = file.read().rstrip()
    if not pin.isnumeric():
        raise ValueError("PIN should be numeric")
    return pin


def modem_number() -> int:
    # Note: capture_output=True can be used instead of Pipe in Python 3.7 ->
    modem_search = subprocess.run(["mmcli", "-L"], check=True, stdout=subprocess.PIPE)
    rows = str(modem_search.stdout, encoding="ascii").strip("\n").split("\n")
    if rows[0] == "No modems were found":
        raise RuntimeError("No modems found. Please try again or reboot.")
    if len(rows) > 1 and rows[0] != "Found 1 modems:":
        raise RuntimeError("Got invalid response from mmcli:", modem_search.stdout)
    if len(rows) > 1:
        row_ind = 1
    else:
        row_ind = 0
    modem_path = rows[row_ind].strip("\t").split()[0]
    try:
        number = int(modem_path.split("/")[-1])
    except ValueError as e:
        raise ValueError(f"Invalid modem path \"{modem_path}\" on row \"{rows[row_ind]}\"") from e
    return number


def disable_modem(modem: int) -> None:
    subprocess.run(["mmcli", "-m", str(modem), "--disable"], check=True, stdout=subprocess.PIPE)


def get_bearer(modem: int) -> tp.Tuple[int, str]:
    bearer_search = subprocess.run(
        ["mmcli", "-m", str(modem), "--list-bearers"],
        check=True, stdout=subprocess.PIPE
    )
    rows = str(bearer_search.stdout, encoding="ascii").strip("\n").split("\n")
    if rows[0] != "Found 1 bearers:" or len(rows) < 3:
        raise RuntimeError("Got invalid response from mmcli:", bearer_search.stdout)
    bearer_str = rows[2].strip("\t")
    bearer_num = int(bearer_str.split("/")[-1])
    return bearer_num, bearer_str


def delete_bearer(modem: int, bearer: str):
    subprocess.run(
        ["mmcli", "-m", str(modem), f"--delete-bearer={bearer}"],
        check=True, stdout=subprocess.PIPE
    )


def create_bearer(modem: int, apn="internet", ip_type="ipv4", number="*99#") -> tp.Tuple[int, str]:
    output = subprocess.run([
        "mmcli", "-m", str(modem),
        f"--create-bearer=apn={apn},ip-type={ip_type},number={number}"
    ], check=True, stdout=subprocess.PIPE)
    rows = str(output.stdout, encoding="ascii").split("\n")
    if rows[0] != "Successfully created new bearer in modem:":
        raise RuntimeError("Got invalid response from mmcli:", output.stdout)
    bearer_str = rows[1].strip("\t")
    bearer_num = int(bearer_str.split("/")[-1])
    return bearer_num, bearer_str


def enable(modem: int):
    subprocess.run(
        ["mmcli", "-m", str(modem), "--enable"],
        check=True, stdout=subprocess.PIPE
    )


def enable_location(modem: int) -> None:
    try:
        subprocess.run(
            ["mmcli", "-m", str(modem), "--location-enable-3gpp"],
            check=True, stdout=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        if e.stderr is not None and b"modem in initializing state" in e.stderr:
            print("Cannot enable location: the modem is still initializing. Try increasing the delay.")
        else:
            raise e


def send_pin(modem: int, pin: str, retry: bool = True) -> None:
    try:
        subprocess.run(
            ["mmcli", "-i", str(modem), f"--pin={pin}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        # If the device is already open we don't need to do anything
        if e.stderr is not None and b"Cannot send PIN: device is not SIM-PIN locked" in e.stderr:
            print("SIM was already unlocked")
        elif e.stderr is not None and retry and b"error: couldn't find sim at" in e.stderr and modem != 0:
            print("SIM was not found at the modem address. Retrying with address 0.")
            send_pin(0, pin, retry=False)
        else:
            raise e


def connect(bearer: int):
    subprocess.run(
        ["mmcli", "-b", str(bearer), "--connect"],
        check=True
    )


def main():
    # utils.alert_if_not_root()
    pin = read_pin(PIN_PATH)
    modem = modem_number()

    disable_modem(modem)
    send_pin(modem, pin)
    time.sleep(2)

    # old_bearer_int, old_bearer_str = get_bearer(modem)
    # delete_bearer(modem, old_bearer_str)
    # new_bearer_int, new_bearer_str = create_bearer(modem)
    # connect(new_bearer_int)

    try:
        enable(modem)
    except subprocess.CalledProcessError as e:
        print(f"Could not enable modem: {e}")

    # The modem will take a while to initialize
    time.sleep(1)
    enable_location(modem)


if __name__ == "__main__":
    main()
