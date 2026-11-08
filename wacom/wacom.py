#!/usr/bin/env python3

"""Configuration script for drawing tablets.

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

from collections.abc import Iterable
import enum
import logging
from logging.handlers import RotatingFileHandler
import os
import os.path
import shlex
import sys
import time

from Xlib import display
from Xlib.ext import randr
from Xlib.protocol.rq import DictWrapper

# Add linux-scripts folder to PATH
REPO_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_DIR)

from utils import misc_utils as utils  # noqa: E402

XSETWACOM: str = "/usr/bin/xsetwacom"

LOG_DIR: str = os.path.join(REPO_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logger: logging.Logger = logging.getLogger(__name__)
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
class Rotation(enum.StrEnum):
    """Tablet rotation options of xsetwacom."""

    NONE = "none"
    HALF = "half"
    CW = "cw"
    CCW = "ccw"


@enum.unique
class DevType(enum.StrEnum):
    """Device types reported by xsetwacom."""

    CURSOR = "CURSOR"
    ERASER = "ERASER"
    PAD = "PAD"
    STYLUS = "STYLUS"


class Device:
    """An individual xsetwacom device such as the stylus or pad."""

    def __init__(
            self,
            name: str,
            dev_id: int,
            dev_type: DevType) -> None:
        """Create a device object.

        :param name: xsetwacom device name
        :param dev_id: xsetwacom device ID
        :param dev_type: device type
        """
        self.name: str = name
        self.dev_id: int = dev_id
        self.dev_type: DevType = dev_type
        if name.startswith("Wacom Co.,Ltd. Intuos BT M"):
            logger.warning(
                f"Found device \"{name}\" in Android mode. Only a part of the tablet surface will be usable. "
                "Holding the left- and rightmost keys at the same time may switch the tablet to PC mode. "
                f"ID = {dev_id}, type = {dev_type}."
            )

    @classmethod
    def create_by_names(cls, names: list[str]) -> Device:
        """Find the first connected device that matches one of the given names.

        :param names: device names in the order of preference
        :return: the first matching device
        :raises IndexError: if none of the devices is found
        """
        devices = cls.get_devices()
        for name in names:
            found = next((dev for dev in devices if dev.name == name), None)
            if found is not None:
                return found
        raise IndexError(f"Device not found with the names: {names}")

    @staticmethod
    def get_devices() -> list[Device]:
        """Get the devices listed by xsetwacom.

        :return: list of devices
        """
        _ret_code, lst = utils.run([XSETWACOM, "--list", "devices"], get_output=True, print_output=False)
        props = [[elem.strip() for elem in line.split("\t")] for line in lst]
        return [Device(
            name=line[0],
            # The ID column is of the form "id: 9".
            dev_id=int(line[1].split(":")[1]),
            dev_type=DevType(line[2].split(":")[1].strip())
        ) for line in props]

    def set_value(self, *args: object) -> None:
        """Set a setting of the device.

        :param args: setting name and values, which will be converted to strings
        """
        utils.run([XSETWACOM, "set", self.name] + [str(arg) for arg in args])

    def get_all_settings(self) -> list[list[str]]:
        """Get all settings of the device.

        :return: list of settings, each consisting of the setting name and its values
        """
        return [
            shlex.split(line)[3:] for line in
            utils.run(
                [XSETWACOM, "-s", "get", self.name, "all"],
                get_output=True, print_output=False)[1]
            if not line.endswith("does not exist on device.")
        ]

    def print_all_settings(self) -> None:
        """Print all settings of the device."""
        settings = self.get_all_settings()
        for setting in settings:
            values = " ".join([f"\"{value}\"" for value in setting[1:]])
            print(f"{setting[0]}: {values}")

    def rotate(self, rotation: Rotation) -> None:
        """Set the rotation of the device.

        :param rotation: rotation
        """
        self.set_value("Rotate", rotation.value)

    def set_button(self, button: int, command: str) -> None:
        """Map a button to a command.

        :param button: button number
        :param command: xsetwacom button command
        """
        self.set_value("Button", str(button), command)

    def set_output_monitor(self, name: str) -> None:
        """Map the device to a monitor.

        :param name: monitor (output) name
        """
        self.set_value("MapToOutput", name)

    def set_output(self, width: int, height: int, x: int = 0, y: int = 0) -> None:
        """Map the device to an area of the screen.

        :param width: area width in pixels
        :param height: area height in pixels
        :param x: horizontal offset in pixels
        :param y: vertical offset in pixels
        """
        self.set_value("MapToOutput", f"{width}x{height}+{x}+{y}")

    def set_raw_sample(self, status: bool) -> None:
        """Enable or disable raw sampling.

        By default the input is averaged over several data points.
        Enabling raw sampling decreases the latency.

        :param status: whether to enable raw sampling
        """
        self.set_value("RawSample", int(status))

    def set_suppress(self, status: bool) -> None:
        """Enable or disable movement suppression.

        By default the pen has to be moved at least two pixels to be registered.
        By disabling suppression even single points will be registered.

        :param status: whether to enable suppression
        """
        self.set_value("Suppress", int(status))

    def set_threshold(self, threshold: int) -> None:
        """Set the pressure threshold for a click.

        :param threshold: pressure threshold
        """
        self.set_value("Threshold", threshold)


def find_mode(mode_id: int, modes: Iterable[DictWrapper]) -> tuple[int, int] | None:
    """Find the resolution of an XRandR mode.

    Adapted from
    https://stackoverflow.com/a/64502961/

    :param mode_id: XRandR mode ID
    :param modes: XRandR mode infos
    :return: width and height of the mode, or None if not found
    """
    for mode in modes:
        if mode_id == mode.id:
            return mode.width, mode.height
    return None


def get_devices() -> list[str]:
    """Get the xsetwacom device list.

    :return: output lines of xsetwacom
    """
    return utils.run([XSETWACOM, "--list"], get_output=True, print_output=False)[1]


def get_display_info(name: str = ":0") -> dict[str, tuple[int, int]]:
    """Get the names and resolutions of the active monitors.

    Adapted from
    https://stackoverflow.com/a/64502961/

    :param name: X11 display name
    :return: dictionary of monitor names and their resolutions
    """
    d = display.Display(name)
    # screen_count = d.screen_count()
    default_screen = d.get_default_screen()
    monitors: dict[str, tuple[int, int]] = {}
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


def script(use_big: bool = True) -> None:
    """Configure the tablet.

    :param use_big: whether to map the tablet to the ultrawide monitor if it's connected
    """
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
            if any(name in monitor_names for name in ["DisplayPort-2", "DP-2", "HDMI-1"]):
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
    elif "eDP-1" in monitors:
        area_x, area_y = monitors["eDP-1"]
        # If there is a secondary monitor
        for port in monitors:
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


def main() -> None:
    """Run the script and log any exceptions."""
    try:
        script(use_big=True)
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == "__main__":
    main()
