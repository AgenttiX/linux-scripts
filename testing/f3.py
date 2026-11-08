#!/usr/bin/env python3

"""Flash memory testing script, based on f3."""

import argparse
import logging
import os.path
import sys
import time

# Add linux-scripts folder to PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import misc_utils as utils

logger: logging.Logger = logging.getLogger(__name__)
log_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_path):
    os.mkdir(log_path)

logging.basicConfig(
    handlers=[
        logging.FileHandler(os.path.join(log_path, "f3_{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S"))))
    ],
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s"
)


def main() -> None:
    """Write and verify test data on the given mount point with f3."""
    parser = argparse.ArgumentParser(description="F3 script")
    parser.add_argument("path", type=str, help="Mount point path")
    args = parser.parse_args()
    path = args.path
    if not os.path.isdir(path):
        print("The path should be to a directory")

    mount_info = utils.MountInfo(path)
    device_info = utils.DiskInfo(mount_info.device)
    device_info.print()
    device_info.lsblk()
    # For some reason f3 does not output stderr properly
    # TODO: getting live output from the progress does not work either
    utils.run(["f3write", path], stderr=False)
    utils.run(["f3read", path], stderr=False)


if __name__ == "__main__":
    main()
