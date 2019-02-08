#!/usr/bin/env python3

"""Created by Mika"""


def write_to_virtual_file(data: str, path: str) -> None:
    try:
        with open(path, "w") as file:
            print(data, file=file)
    except PermissionError:
        print("Could not open", path, "Are you running without root?")


def disable_wakeups() -> None:
    wakeup_file_path = "/proc/acpi/wakeup"

    # Read the file and close it as quickly as possible
    with open(wakeup_file_path) as file:
        lines = file.readlines()

    sources = []

    line_iter = iter(lines)
    next(line_iter)
    for line in line_iter:
        data = line.strip().split()
        sources.append(data)

    # print(sources)

    for source in sources:
        if len(source) >= 3 and source[2] == "*enabled":
            write_to_virtual_file(source[0], wakeup_file_path)


def set_power_control() -> None:
    devices = [
        # I2C
        "/sys/bus/i2c/devices/i2c-0/device/power/control",

        # Atmel maXTouch Digitizer
        "/sys/bus/usb/devices/1-1.1/power/control",

        # STM32 eMotion2
        "/sys/bus/usb/devices/2-1.5/power/control",

        # H5321 gw
        "/sys/bus/usb/devices/1-1.2/power/control",

        # Chipset
        "/sys/bus/pci/devices/0000:00:1f.0/power/control",
        "/sys/bus/pci/devices/0000:00:1c.3/power/control",
        "/sys/bus/pci/devices/0000:00:1f.3/power/control",
        "/sys/bus/pci/devices/0000:00:00.0/power/control",
        "/sys/bus/pci/devices/0000:00:1c.1/power/control",
        "/sys/bus/pci/devices/0000:02:00.0/power/control",
        "/sys/bus/pci/devices/0000:00:16.0/power/control",

        # GPU
        "/sys/bus/pci/devices/0000:00:02.0/power/control",

        # USB
        "/sys/bus/pci/devices/0000:00:1d.0/power/control",
        "/sys/bus/pci/devices/0000:00:1a.0/power/control",
        "/sys/bus/pci/devices/0000:00:14.0/power/control",

        # Ethernet
        "/sys/bus/pci/devices/0000:04:00.0/power/control",

        # SATA
        "/sys/bus/pci/devices/0000:00:1f.2/power/control",

        # WiFi
        "/sys/bus/pci/devices/0000:03:00.0/power/control",

        # Audio
        "/sys/bus/pci/devices/0000:00:1b.0/power/control"
    ]

    for device in devices:
        write_to_virtual_file("auto", device)


if __name__ == "__main__":
    disable_wakeups()
    set_power_control()
