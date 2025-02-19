#!/usr/bin/env python3

"""
Configuration script for drawing tablets.
This script is based on X11 utilities and will unfortunately not yet work on Wayland.
To run this script automatically when plugging in the tablet, please run "install_wacom.sh".

This script works on X11 only, and not on Wayland.
OpenTabletDriver supports Wayland as well, and it's a lot more comprehensive.
Please use it instead.
https://opentabletdriver.net/

Based on a similar script by Alpi Tolvanen
https://gitlab.com/tolvanea/linux_utility_scripts/-/blob/master/wacom_intuos

Useful links
https://wiki.archlinux.org/index.php/Wacom_tablet

"""

import enum
import logging
from logging.handlers import RotatingFileHandler
import os
import os.path
import shlex
import sys
import time
import typing as tp

from Xlib import display
from Xlib.ext import randr
from Xlib.protocol.rq import DictWrapper

# Add linux-scripts folder to PATH
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIR)

import misc_utils as utils

XSETWACOM: str = "/usr/bin/xsetwacom"

LOG_DIR = os.path.join(REPO_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(module)-16s %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            filename=os.path.join(LOG_DIR, "wacom.txt"),
            maxBytes=10**5,
            backupCount=5
        )
    ]
)


@enum.unique
class Rotation(str, enum.Enum):
    NONE = "none"
    HALF = "half"
    CW = "cw"
    CCW = "ccw"


@enum.unique
class DevType(str, enum.Enum):
    CURSOR = "CURSOR"
    ERASER = "ERASER"
    PAD = "PAD"
    STYLUS = "STYLUS"


class Device:
    """An individual xsetwacom device such as the stylus or pad"""
    def __init__(
            self,
            name: str,
            dev_id: int,
            dev_type: DevType):
        self.name = name
        self.dev_id = dev_id
        self.dev_type = dev_type
        if name.startswith("Wacom Co.,Ltd. Intuos BT M"):
            logger.warning(
                f"Found device \"{name}\" in Android mode. Only a part of the tablet surface will be usable. "
                "Holding the left- and rightmost keys at the same time may switch the tablet to PC mode. "
                f"ID = {dev_id}, type = {dev_type}."
            )

    @classmethod
    def create_by_names(cls, names: tp.List[str]) -> "Device":
        devices = cls.get_devices()
        for name in names:
            found = next((dev for dev in devices if dev.name == name), None)
            if found is not None:
                return found
        raise IndexError(f"Device not found with the names: {names}")

    @staticmethod
    def get_devices() -> tp.List["Device"]:
        ret_code, lst = utils.run([XSETWACOM, "--list", "devices"], get_output=True, print_output=False)
        props = [[elem.strip() for elem in line.split("\t")] for line in lst]
        return [Device(
            name=line[0],
            dev_id=line[1],
            dev_type=DevType(line[2].split(":")[1].strip())
        ) for line in props]

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
        self.set_value("Rotate", rotation.value)

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
        # print(params)
        if not params.crtc:
            continue
        crtc = d.xrandr_get_crtc_info(params.crtc, res.config_timestamp)
        # Available modes
        # modes = {find_mode(mode, res.modes) for mode in params.modes}
        monitors[params.name] = (crtc.width, crtc.height)

    return monitors


def set_x11_environment_variables() -> None:
    """Configure the X11 session for a script started by an udev rule or Cron."""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    if "XAUTHORITY" not in os.environ:
        os.environ["XAUTHORITY"] = f"{os.environ['HOME']}/.Xauthority"
    logger.debug("DISPLAY=%s", os.environ["DISPLAY"])
    logger.debug("XAUTHORITY=%s", os.environ["XAUTHORITY"])


def script(use_big: bool = True):
    logger.info("Running Wacom script")
    utils.alert_if_root(fail=True)
    set_x11_environment_variables()

    # Add the name of your tablet here.
    stylus = Device.create_by_names([
        "Wacom Intuos BT M Pen stylus",
        "Wacom Co.,Ltd. Intuos BT M stylus"
    ])
    # pad = Device("Wacom Intuos BT M Pad pad")

    # This sleep is necessary to ensure that the settings don't get overwritten by other applications
    time.sleep(0.5)

    # stylus.print_all_settings()
    stylus.set_suppress(False)
    stylus.set_raw_sample(True)
    # pad.set_raw_sample(True)
    stylus.set_threshold(128)
    # pad.set_threshold(128)

    monitors = get_display_info()
    monitor_names = list(monitors.keys())
    logger.info("Found monitors: %s", monitor_names)
    resolutions = list(monitors.values())
    try:
        big_monitor = monitor_names[resolutions.index((3440, 1440))]
    except ValueError:
        big_monitor = None

    tablet_resolution = (21600, 13500)
    tablet_aspect_ratio = tablet_resolution[0] / tablet_resolution[1]
    logger.info(f"Tablet aspect ratio: {tablet_aspect_ratio}")
    # if big_monitor is not None:
    #     print(big_monitor)
    #     stylus.rotate(Rotation.CW)
    #     area_x = int(1440/tablet_aspect_ratio)
    #     area_y = 1440
    #     print(area_x, area_y)
    #     stylus.set_output(area_x, area_y, 1920+180, 0)

    # If the ultrawide monitor is connected
    if big_monitor is not None:
        if use_big:
            area_y = 1440
            area_x = int(tablet_aspect_ratio * 1440)
            logger.info(f"Tablet area: ({area_x}, {area_y})")
            # If the left-most monitor is connected
            if any([name in monitor_names for name in ["DisplayPort-2", "DP-2", "HDMI-1"]]):
                stylus.set_output(area_x, area_y, 1920, 0)
            else:
                stylus.set_output(area_x, area_y, 0, 0)
        else:
            # Use the left-most monitor
            stylus.set_output(1920, 1080, 0, 0)
    # For laptop
    # The ports in ThinkPad T480 are
    # eDP-1 = internal monitor
    # HDMI-2 = HDMI
    # DP-1 = Thunderbolt (USB-c with the Thunderbolt logo)
    # DP-2 = USB-c with the charging logo
    elif "eDP-1" in monitors.keys():
        area_x, area_y = monitors["eDP-1"]
        # If there is a secondary monitor
        for port in monitors.keys():
            if port != "eDP-1":
                logger.info("External monitor detected at %s. Using internal display.", port)
                # TODO: configure this so that it recognizes the arrangement of the displays
                # TODO: ensure, that relative position would not get enabled from the system settings
                # stylus.set_output(area_x, area_y, monitors[port][0], 0)
                # stylus.set_output(area_x, area_y, 0, 0)
                stylus.set_output(monitors[port][0], monitors[port][1], 1920, 0)
                break
        else:
            stylus.set_output(area_x, area_y, 0, 0)

    logger.info("Wacom script ready.")


def main():
    try:
        script(use_big=True)
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == "__main__":
    main()
