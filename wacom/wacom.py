#!/usr/bin/env python3

"""
Configuration script for drawing tablets

Based on a similar script by Alpi Tolvanen
https://gitlab.com/tolvanea/linux_utility_scripts/-/blob/master/wacom_intuos

Useful links
https://wiki.archlinux.org/index.php/Wacom_tablet

"""

import enum
import os.path
import shlex
import sys
import typing as tp

from Xlib import display
from Xlib.ext import randr
from Xlib.protocol.rq import DictWrapper

# Add linux-scripts folder to PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils

XSETWACOM: str = "/usr/bin/xsetwacom"


@enum.unique
class Rotation(str, enum.Enum):
    NONE = "none"
    HALF = "half"
    CW = "cw"
    CCW = "ccw"


class Device:
    """An individual xsetwacom device such as the stylus or pad"""
    def __init__(self, name: str):
        self.name = name

    def set_value(self, *args):
        utils.run([XSETWACOM, "set", self.name] + [str(arg) for arg in args])

    def get_all_settings(self) -> tp.List[tp.List[str]]:
        return [
            shlex.split(line)[3:] for line in
            utils.run(
                [XSETWACOM, "-s", "get", self.name, "all"],
                get_output=True, print_output=False)[1]
            if not line.endswith("does not exist on device.")
        ]

    def print_all_settings(self):
        settings = self.get_all_settings()
        for setting in settings:
            values = " ".join([f"\"{value}\"" for value in setting[1:]])
            print(f"{setting[0]}: {values}")

    def rotate(self, rotation: Rotation):
        self.set_value("Rotate", rotation)

    def set_button(self, button: int, command: str):
        self.set_value("Button", str(button), command)

    def set_output_monitor(self, name: str):
        self.set_value("MapToOutput", name)

    def set_output(self, width: int, height: int, x: int = 0, y: int = 0):
        self.set_value("MapToOutput", f"{width}x{height}+{x}+{y}")

    def set_raw_sample(self, status: bool):
        """By default the input is averaged over several data points.
        Enabling raw sampling decreases the latency.
        """
        self.set_value("RawSample", int(status))

    def set_suppress(self, status: bool):
        """By default the pen has to be moved at least two pixels to be registered.
        By disabling suppression even single points will be registered.
        """
        self.set_value("Suppress", int(status))

    def set_threshold(self, threshold: int):
        self.set_value("Threshold", threshold)


def find_mode(mode_id: int, modes: DictWrapper) -> tp.Optional[tp.Tuple[int, int]]:
    """Adapted from
    https://stackoverflow.com/a/64502961/
    """
    for mode in modes:
        if mode_id == mode.id:
            return mode.width, mode.height


def get_devices():
    return utils.run([XSETWACOM, "--list"], get_output=True, print_output=False)[1]


def get_display_info(name: str = ":0") -> tp.Dict[str, tp.Tuple[int, int]]:
    """Adapted from
    https://stackoverflow.com/a/64502961/
    """
    d = display.Display(name)
    # screen_count = d.screen_count()
    default_screen = d.get_default_screen()
    monitors = {}
    info = d.screen(default_screen)
    window = info.root

    res = randr.get_screen_resources(window)
    # print(res)
    for output in res.outputs:
        params = d.xrandr_get_output_info(output, res.config_timestamp)
        print(params)
        if not params.crtc:
            continue
        crtc = d.xrandr_get_crtc_info(params.crtc, res.config_timestamp)
        # Available modes
        modes = {find_mode(mode, res.modes) for mode in params.modes}
        monitors[params.name] = (crtc.width, crtc.height)

    return monitors


def main():
    utils.alert_if_root(fail=True)
    stylus = Device("Wacom Intuos BT M Pen stylus")
    pad = Device("Wacom Intuos BT M Pad pad")

    # stylus.print_all_settings()
    stylus.set_suppress(False)
    stylus.set_raw_sample(True)
    pad.set_raw_sample(True)
    stylus.set_threshold(128)
    pad.set_threshold(128)

    monitors = get_display_info()
    monitor_names = list(monitors.keys())
    resolutions = list(monitors.values())
    try:
        big_monitor = monitor_names[resolutions.index((3440, 1440))]
    except ValueError:
        big_monitor = None

    if big_monitor is not None:
        # stylus.rotate(Rotation.CW)
        print(big_monitor)


if __name__ == "__main__":
    main()
