#!/usr/bin/env python3

"""
Modem control based on mmcli. For
- Lenovo ThinkPad T480
- Lenovo ThinkPad Twist S230u

https://manpages.ubuntu.com/manpages/trusty/man8/mmcli.8.html
https://manpages.debian.org/jessie/modemmanager/mmcli.8
"""

import subprocess
import time
import typing as tp

PIN_PATH = "modem-pin.txt"


def read_pin(path: str) -> str:
    with open(path) as f:
        pin = f.read().rstrip()
    if not pin.isnumeric():
        raise ValueError("PIN should be numeric")
    return pin


def modem_number() -> int:
    # Note: capture_output=True can be used instead of Pipe in Python 3.7 ->
    modem_search = subprocess.run(["mmcli", "-L"], check=True, stdout=subprocess.PIPE)
    rows = str(modem_search.stdout, encoding="ascii").strip("\n").split("\n")
    if len(rows) > 1 and rows[0] != "Found 1 modems:":
        raise RuntimeError("Got invalid response from mmcli:", modem_search.stdout)
    if len(rows) > 1:
        row_ind = 1
    else:
        row_ind = 0
    modem_path = rows[row_ind].strip("\t").split()[0]
    try:
        number = int(modem_path.split("/")[-1])
    except ValueError:
        raise ValueError("Invalid modem path")
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
        ["mmcli", "-m", str(modem), "--delete-bearer={}".format(bearer)],
        check=True, stdout=subprocess.PIPE
    )


def create_bearer(modem: int, apn="internet", ip_type="ipv4", number="*99#") -> tp.Tuple[int, str]:
    output = subprocess.run([
        "mmcli", "-m", str(modem),
        "--create-bearer=apn={},ip-type={},number={}".format(apn, ip_type, number)
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
    subprocess.run(
        ["mmcli", "-m", str(modem), "--location-enable-3gpp"],
        check=True, stdout=subprocess.PIPE
    )


def send_pin(modem: int, pin: str) -> None:
    subprocess.run(
        ["mmcli", "-i", str(modem), "--pin={}".format(pin)],
        check=True, stdout=subprocess.PIPE
    )


def connect(bearer: int):
    subprocess.run(
        ["mmcli", "-b", str(bearer), "--connect"]
    )


def main():
    pin = read_pin(PIN_PATH)
    modem = modem_number()

    disable_modem(modem)
    send_pin(modem, pin)
    time.sleep(1)

    # old_bearer_int, old_bearer_str = get_bearer(modem)
    # delete_bearer(modem, old_bearer_str)
    # new_bearer_int, new_bearer_str = create_bearer(modem)
    # connect(new_bearer_int)

    try:
        enable(modem)
    except subprocess.CalledProcessError:
        print(f"Could not enable modem: {e}")
    enable_location(modem)


if __name__ == "__main__":
    main()
