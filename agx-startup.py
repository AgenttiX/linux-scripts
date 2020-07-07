#!/usr/bin/env python3

"""
Startup configuration
Created by Mika Mäki, 2019-2020

To enable this script, run agx-startup-enabler.sh
"""

import enum
import glob
import os
import subprocess
import typing as tp


# Code required for configuration

class ALPM_LevelOptions(enum.Enum):
    MAX_PERFORMANCE = "max_powerformance"
    MEDIUM_POWER = "medium_power"
    MED_POWER_WITH_DIPM = "med_power_with_dipm"
    MIN_POWER = "min_power"     # Warning: possible data loss


# Configuration

ALPM_LEVELS: tp.Dict[str, ALPM_LevelOptions] = {
    "334729G": ALPM_LevelOptions.MED_POWER_WITH_DIPM,
    "X58A-UD7": ALPM_LevelOptions.MED_POWER_WITH_DIPM,
    "0B4Ch": ALPM_LevelOptions.MED_POWER_WITH_DIPM,
    "ROG ZENITH II EXTREME": ALPM_LevelOptions.MED_POWER_WITH_DIPM
}

CUSTOM_COMMANDS: tp.Dict[str, tp.List[tp.List[str]]] = {
    "0B4Ch": [
        ["ethtool", "-s", "enp1s0", "wol", "d"]
    ]
}

CUSTOM_WRITES: tp.Dict[str, tp.Dict[str, str]] = {
    "334729G": {
        "/proc/sys/kernel/nmi_watchdog": "0"
    },
    "0B4Ch": {
        "/sys/module/snd_hda_intel/parameters/power_save": "1"
    },
    "ROG ZENITH II EXTREME": {
        "/sys/class/net/enp71s0/device/power/wakeup": "disabled",
        "/sys/bus/usb/devices/9-3.2.1/power/wakeup": "disabled"
    },
}

HDPARM_PARAMS: tp.Dict[str, tp.Dict[str, tp.Dict[str, int]]] = {
    "0B4Ch": {
        "ata-TOSHIBA_THNSNF128GCSS_Z2IS10NMT8KY": {
            "-B": 127,
            "-S": 241
        },
        "ata-ST4000DM000-1F2168_S301LPS3": {
            "-B": 127,
            "-S": 241
        },
        "ata-ST4000DM000-1F2168_Z3018Q9G": {
            "-B": 127,
            "-S": 241
        },
        "ata-ST4000DM000-1F2168_Z30199N4": {
            "-B": 127,
            "-S": 241
        },
        "ata-ST4000DM000-1F2168_Z302HEFX": {
            "-B": 127,
            "-S": 241
        },
        "ata-ST4000DM000-1F2168_Z303ZLPZ": {
            "-B": 127,
            "-S": 241
        }
    }
}

POWER_CONTROL_DEVICES: tp.Dict[str, tp.List[str]] = {
    # HP Z400 Workstation
    "0B4Ch": [
        # GPU
        "/sys/bus/i2c/devices/i2c-0/device",
        "/sys/bus/i2c/devices/i2c-12/device",

        # Audio
        "/sys/bus/pci/devices/0000:00:1b.0",

        # LAN
        "/sys/bus/pci/devices/0000:01:00.0",

        # USB
        "/sys/bus/usb/devices/1-4",
        "/sys/bus/pci/devices/0000:00:1a.0",
        "/sys/bus/pci/devices/0000:00:1a.2",
        "/sys/bus/pci/devices/0000:00:1d.2",
        "/sys/bus/pci/devices/0000:00:1a.7",
        "/sys/bus/pci/devices/0000:00:1d.0",
        "/sys/bus/pci/devices/0000:03:00.0",
        "/sys/bus/pci/devices/0000:00:1d.1",
        "/sys/bus/pci/devices/0000:00:1d.7",

        # CPU, motherboard & memory
        "/sys/bus/pci/devices/0000:00:15.0",
        "/sys/bus/pci/devices/0000:3f:04.1",
        "/sys/bus/pci/devices/0000:00:10.1",
        "/sys/bus/pci/devices/0000:3f:03.1",
        "/sys/bus/pci/devices/0000:00:14.2",
        "/sys/bus/pci/devices/0000:00:11.0",
        "/sys/bus/pci/devices/0000:00:00.0",
        "/sys/bus/pci/devices/0000:3f:05.0",
        "/sys/bus/pci/devices/0000:3f:05.2",
        "/sys/bus/pci/devices/0000:00:1e.0",
        "/sys/bus/pci/devices/0000:3f:04.3",
        "/sys/bus/pci/devices/0000:3f:05.1",
        "/sys/bus/pci/devices/0000:3f:03.4",
        "/sys/bus/pci/devices/0000:3f:02.1",
        "/sys/bus/pci/devices/0000:3f:04.0",
        "/sys/bus/pci/devices/0000:3f:05.3",
        "/sys/bus/pci/devices/0000:3f:04.2",
        "/sys/bus/pci/devices/0000:00:14.1",
        "/sys/bus/pci/devices/0000:00:14.0",
        "/sys/bus/pci/devices/0000:3f:00.1",
        "/sys/bus/pci/devices/0000:37:05.0",
        "/sys/bus/pci/devices/0000:3f:00.0",
        "/sys/bus/pci/devices/0000:00:1f.2",
        "/sys/bus/pci/devices/0000:3f:06.2",
        "/sys/bus/pci/devices/0000:3f:03.0",
        "/sys/bus/pci/devices/0000:3f:06.0",
        "/sys/bus/pci/devices/0000:00:10.0",
        "/sys/bus/pci/devices/0000:00:11.1",
        "/sys/bus/pci/devices/0000:00:1f.0",
        "/sys/bus/pci/devices/0000:3f:02.0",
        "/sys/bus/pci/devices/0000:00:1c.0",
        "/sys/bus/pci/devices/0000:3f:06.3",
        "/sys/bus/pci/devices/0000:00:1c.5",
        "/sys/bus/pci/devices/0000:00:1a.1",
        "/sys/bus/pci/devices/0000:3f:06.1",
    ],
    # ThinkPad T480
    "20L5CTO1WW": [
        # PCIe
        "/sys/bus/pci/devices/0000:00:1d.0",

        # Nvidia MX 150
        "/sys/bus/pci/devices/0000:01:00.0",
    ],
    # ThinkPad S230u
    "334729G": [
        # I2C
        "/sys/bus/i2c/devices/i2c-0/device",

        # Atmel maXTouch Digitizer
        "/sys/bus/usb/devices/1-1.1",

        # STM32 eMotion2
        "/sys/bus/usb/devices/2-1.5",

        # H5321 gw
        "/sys/bus/usb/devices/1-1.2",

        # Chipset
        "/sys/bus/pci/devices/0000:00:1f.0",
        "/sys/bus/pci/devices/0000:00:1c.3",
        "/sys/bus/pci/devices/0000:00:1f.3",
        "/sys/bus/pci/devices/0000:00:00.0",
        "/sys/bus/pci/devices/0000:00:1c.1",
        "/sys/bus/pci/devices/0000:02:00.0",
        "/sys/bus/pci/devices/0000:00:16.0",

        # GPU
        "/sys/bus/pci/devices/0000:00:02.0",

        # USB
        "/sys/bus/pci/devices/0000:00:1d.0",
        "/sys/bus/pci/devices/0000:00:1a.0",
        "/sys/bus/pci/devices/0000:00:14.0",

        # Ethernet
        "/sys/bus/pci/devices/0000:04:00.0",

        # SATA
        "/sys/bus/pci/devices/0000:00:1f.2",

        # WiFi
        "/sys/bus/pci/devices/0000:03:00.0",

        # Audio
        "/sys/bus/pci/devices/0000:00:1b.0",
    ],
    "ROG ZENITH II EXTREME": [
        # Chipset
        "/sys/bus/i2c/devices/i2c-1/device",
        "/sys/bus/pci/devices/0000:20:08.0",
        "/sys/bus/pci/devices/0000:60:08.0",
        "/sys/bus/pci/devices/0000:00:18.2",
        "/sys/bus/pci/devices/0000:60:05.0",
        "/sys/bus/pci/devices/0000:42:02.0",
        "/sys/bus/pci/devices/0000:40:03.0",
        "/sys/bus/pci/devices/0000:05:00.0",
        "/sys/bus/pci/devices/0000:00:18.0",
        "/sys/bus/pci/devices/0000:40:00.0",
        "/sys/bus/pci/devices/0000:00:03.0",
        "/sys/bus/pci/devices/0000:23:00.0",
        "/sys/bus/pci/devices/0000:60:02.0",
        "/sys/bus/pci/devices/0000:20:05.0",
        "/sys/bus/pci/devices/0000:40:00.2",
        "/sys/bus/pci/devices/0000:00:00.0",
        "/sys/bus/pci/devices/0000:00:18.4",
        "/sys/bus/pci/devices/0000:00:14.0",
        "/sys/bus/pci/devices/0000:21:00.0",
        "/sys/bus/pci/devices/0000:00:18.7",
        "/sys/bus/pci/devices/0000:22:00.0",
        "/sys/bus/pci/devices/0000:62:00.0",
        "/sys/bus/pci/devices/0000:4e:00.0",
        "/sys/bus/pci/devices/0000:00:18.1",
        "/sys/bus/pci/devices/0000:00:18.3",
        "/sys/bus/pci/devices/0000:49:00.0",
        "/sys/bus/pci/devices/0000:00:18.5",
        "/sys/bus/pci/devices/0000:00:18.6",
        "/sys/bus/pci/devices/0000:24:00.0",
        "/sys/bus/pci/devices/0000:00:14.3",

        # Crypto
        "/sys/bus/pci/devices/0000:24:00.1",

        # IOMMU
        "/sys/bus/pci/devices/0000:20:00.2",
        "/sys/bus/pci/devices/0000:00:08.0",
        "/sys/bus/pci/devices/0000:60:00.2",
        
        # PCIe
        "/sys/bus/pci/devices/0000:40:07.0",
        "/sys/bus/pci/devices/0000:61:00.0",
        "/sys/bus/pci/devices/0000:40:02.0",
        "/sys/bus/pci/devices/0000:4d:00.0",
        "/sys/bus/pci/devices/0000:00:05.0",
        "/sys/bus/pci/devices/0000:60:04.0",
        "/sys/bus/pci/devices/0000:20:07.0",
        "/sys/bus/pci/devices/0000:00:02.0",
        "/sys/bus/pci/devices/0000:04:00.0",
        "/sys/bus/pci/devices/0000:60:01.0",
        "/sys/bus/pci/devices/0000:40:08.0",
        "/sys/bus/pci/devices/0000:20:03.0",
        "/sys/bus/pci/devices/0000:00:01.0",
        "/sys/bus/pci/devices/0000:40:05.0",
        "/sys/bus/pci/devices/0000:60:03.0",
        "/sys/bus/pci/devices/0000:20:02.0",
        "/sys/bus/pci/devices/0000:00:00.2",
        "/sys/bus/pci/devices/0000:20:01.0",
        "/sys/bus/pci/devices/0000:00:04.0",
        "/sys/bus/pci/devices/0000:40:04.0",
        "/sys/bus/pci/devices/0000:00:07.0",
        "/sys/bus/pci/devices/0000:40:01.0",
        "/sys/bus/pci/devices/0000:60:07.0",

        # SATA
        "/sys/bus/pci/devices/0000:00:18.0",
        "/sys/bus/pci/devices/0000:45:00.0",
        "/sys/bus/pci/devices/0000:45:00.0/ata1",
        "/sys/bus/pci/devices/0000:45:00.0/ata2",
        "/sys/bus/pci/devices/0000:46:00.0",
        "/sys/bus/pci/devices/0000:46:00.0/ata3",
        "/sys/bus/pci/devices/0000:46:00.0/ata4",
        "/sys/bus/pci/devices/0000:4a:00.0/ata5",
        "/sys/bus/pci/devices/0000:4b:00.0",
        "/sys/bus/pci/devices/0000:4b:00.0/ata6",

        # Radeon VII
        "/sys/bus/i2c/devices/i2c-3/device",

        # GTX Titan
        "/sys/bus/i2c/devices/i2c-12/device",

        # LAN
        "/sys/bus/pci/devices/0000:44:00.0",
        "/sys/bus/pci/devices/0000:47:00.0",

        # Wi-Fi
        "/sys/bus/pci/devices/0000:48:00.0",

        # Audio
        "/sys/bus/pci/devices/0000:24:00.4",
        "/sys/bus/usb/devices/9-5",
        "/sys/bus/usb/devices/9-6",

        # Aura LED
        "/sys/bus/usb/devices/7-5.3",
        "/sys/bus/usb/devices/7-5.4",

        # USB
        "/sys/bus/pci/devices/0000:49:00.1",
        "/sys/bus/pci/devices/0000:49:00.3",
        "/sys/bus/pci/devices/0000:05:00.3",
        "/sys/bus/pci/devices/0000:24:00.3",
    ],
    # "X58A-UD7": [
    #     # Nvidia GPU
    #     "/sys/bus/i2c/devices/i2c-1/device",
    #     # NVIDIA Corporation GK104 HDMI Audio Controller
    #     "/sys/bus/pci/devices/0000:03:00.1",
    #
    #     # Texas Instruments TSB43AB23 IEEE-1394a-2000 Controller (PHY/Link)
    #     "/sys/bus/pci/devices/0000:0a:06.0",
    #
    #     # JMicron Technology Corp. JMB363 SATA/IDE Controller
    #     "/sys/bus/pci/devices/0000:06:00.0",
    #     "/sys/bus/pci/devices/0000:06:00.1",
    #     "/sys/bus/pci/devices/0000:07:00.0",
    #     "/sys/bus/pci/devices/0000:07:00.1",
    #
    #     # Marvell Technology Group Ltd. 88SE9128 PCIe SATA 6 Gb/s RAID controller
    #     "/sys/bus/pci/devices/0000:01:00.0",
    #
    #
    #     # Intel
    #
    #     # Intel Corporation 7500/5520/5500 Routing & Protocol Layer Register Port 1
    #     "/sys/bus/pci/devices/0000:00:11.1",
    #
    #     # Intel Corporation 5520/5500/X58 I/O Hub to ESI Port
    #     "/sys/bus/pci/devices/0000:00:00.0",
    #     # Intel Corporation 7500/5520/5500/X58 I/O Hub I/OxAPIC Interrupt Controller
    #     "/sys/bus/pci/devices/0000:00:13.0",
    #     # Intel Corporation 7500/5520/5500/X58 I/O Hub System Management Registers
    #     "/sys/bus/pci/devices/0000:00:14.0",
    #     # Intel Corporation 7500/5520/5500/X58 I/O Hub GPIO and Scratch Pad Registers
    #     "/sys/bus/pci/devices/0000:00:14.1",
    #
    #     # Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 1
    #     "/sys/bus/pci/devices/0000:00:01.0",
    #     # Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 2
    #     "/sys/bus/pci/devices/0000:00:02.0",
    #     # Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 3
    #     "/sys/bus/pci/devices/0000:00:03.0",
    #     # Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 7
    #     "/sys/bus/pci/devices/0000:00:07.0",
    #
    #     # Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 1
    #     "/sys/bus/pci/devices/0000:00:1c.0",
    #     # Intel Corporation 82801JI (ICH10 Family) PCI Express Port 2
    #     "/sys/bus/pci/devices/0000:00:1c.1",
    #     # Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 4
    #     "/sys/bus/pci/devices/0000:00:1c.3",
    #     # Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 5
    #     "/sys/bus/pci/devices/0000:00:1c.4",
    #     # Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 6
    #     "/sys/bus/pci/devices/0000:00:1c.5",
    #     # Intel Corporation 82801JI (ICH10 Family) SMBus Controller
    #     "/sys/bus/pci/devices/0000:00:1f.3",
    #
    #     # Intel Corporation 82801 PCI Bridge
    #     "/sys/bus/pci/devices/0000:00:1e.0",
    #
    #     # Intel Corporation SATA Controller [RAID mode]
    #     "/sys/bus/pci/devices/0000:00:1f.2",
    #
    #     # Intel Corporation 82801JIR (ICH10R) LPC Interface Controller
    #     "/sys/bus/pci/devices/0000:00:1f.0",
    #
    #     # Intel Corporation 7500/5520/5500 Physical and Link Layer Registers Port 1
    #     "/sys/bus/pci/devices/0000:00:11.0",
    #     # Intel Corporation 7500/5520/5500/X58 Physical and Link Layer Registers Port 0
    #     "/sys/bus/pci/devices/0000:00:10.0",
    #
    #     # Intel Corporation 7500/5520/5500/X58 Routing and Protocol Layer Registers Port 0
    #     "/sys/bus/pci/devices/0000:00:10.1",
    #     # Intel Corporation 7500/5520/5500/X58 I/O Hub Control Status and RAS Registers
    #     "/sys/bus/pci/devices/0000:00:14.2",
    #     # Intel Corporation 7500/5520/5500/X58 Trusted Execution Technology Registers
    #     "/sys/bus/pci/devices/0000:00:15.0",
    #
    #     # Intel Corporation Xeon 5500/Core i7 QPI Physical 0
    #     "/sys/bus/pci/devices/0000:3f:02.1",
    #     # Intel Corporation Xeon 5500/Core i7 QPI Link 0
    #     "/sys/bus/pci/devices/0000:3f:02.0",
    #     # Intel Corporation Xeon 5500/Core i7 QuickPath Architecture Generic Non-Core Registers
    #     "/sys/bus/pci/devices/0000:3f:00.0",
    #     # Intel Corporation Xeon 5500/Core i7 QuickPath Architecture System Address Decoder
    #     "/sys/bus/pci/devices/0000:3f:00.1",
    #
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller
    #     "/sys/bus/pci/devices/0000:3f:03.0",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Target Address Decoder
    #     "/sys/bus/pci/devices/0000:3f:03.1",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 0 Control Registers
    #     "/sys/bus/pci/devices/0000:3f:04.0",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 1 Control Registers
    #     "/sys/bus/pci/devices/0000:3f:05.0",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 2 Control Registers
    #     "/sys/bus/pci/devices/0000:3f:06.0",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 0 Thermal Control Registers
    #     "/sys/bus/pci/devices/0000:3f:04.3",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 1 Thermal Control Registers
    #     "/sys/bus/pci/devices/0000:3f:05.3",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 2 Thermal Control Registers
    #     "/sys/bus/pci/devices/0000:3f:06.3",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 0 Address Registers
    #     "/sys/bus/pci/devices/0000:3f:04.1",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 1 Address Registers
    #     "/sys/bus/pci/devices/0000:3f:05.1",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 2 Address Registers
    #     "/sys/bus/pci/devices/0000:3f:06.1",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 0 Rank Registers
    #     "/sys/bus/pci/devices/0000:3f:04.2",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 1 Rank Registers
    #     "/sys/bus/pci/devices/0000:3f:05.2",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Channel 2 Rank Registers
    #     "/sys/bus/pci/devices/0000:3f:06.2",
    #     # Intel Corporation Xeon 5500/Core i7 Integrated Memory Controller Test Registers
    #     "/sys/bus/pci/devices/0000:3f:03.4",
    # ],
}


# Actual program

# Support functions

def board_name() -> str:
    with open("/sys/class/dmi/id/board_name") as name_file:
        return name_file.read().rstrip("\n")


def write_to_virtual_file(path: str, data: str) -> None:
    try:
        with open(path, "w") as file:
            print(data, file=file)
    except PermissionError:
        print("Could not write to", path, "Are you running without root?")


# Features

def alpm() -> None:
    board = board_name()

    if board not in ALPM_LEVELS:
        return

    alpm_level = ALPM_LEVELS[board]

    devices = glob.glob("/sys/class/scsi_host/*")
    for device in devices:
        alpm_path = os.path.join(device, "link_power_management_policy")
        if os.path.exists(alpm_path):
            write_to_virtual_file(alpm_path, str(alpm_level.value))


def custom_writes() -> None:
    board = board_name()

    if board not in CUSTOM_WRITES:
        return

    for path, data in CUSTOM_WRITES[board].items():
        write_to_virtual_file(path, data)


def custom_commands() -> None:
    board = board_name()

    if board not in CUSTOM_COMMANDS:
        return

    for command in CUSTOM_COMMANDS[board]:
        subprocess.run(command)


def disable_wakeups() -> None:
    wakeup_file_path = "/proc/acpi/wakeup"

    # Read the file and close it as quickly as possible
    with open(wakeup_file_path) as file:
        lines = file.readlines()

    line_iter = iter(lines)
    next(line_iter)
    sources = [line.strip().split() for line in line_iter]

    for source in sources:
        if len(source) >= 3 and source[2] == "*enabled":
            write_to_virtual_file(wakeup_file_path, source[0])


def hdparm() -> None:
    board = board_name()

    if board not in HDPARM_PARAMS:
        return

    for drive, params in HDPARM_PARAMS[board].items():
        drive_path = os.path.join("/dev/disk/by-id", drive)

        for param, value in params.items():
            subprocess.run(["hdparm", param, str(value), drive_path])


def power_control() -> None:
    board = board_name()

    if board not in POWER_CONTROL_DEVICES.keys():
        print("Computer has not been configured for power control:", board)
        return

    devices = POWER_CONTROL_DEVICES[board]

    for device in devices:
        if os.path.exists(device):
            control_path = os.path.join(device, "power/control")
            if os.path.exists(control_path):
                write_to_virtual_file(control_path, "auto")
            else:
                print("Device power control path", control_path, "not found")
        else:
            print("Device", device, "not found")


if __name__ == "__main__":
    disable_wakeups()
    power_control()
    alpm()
    hdparm()
    custom_writes()
    custom_commands()
