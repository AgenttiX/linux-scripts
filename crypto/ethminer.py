#!/usr/bin/env python3

"""
Ethereum mining script

TODO: this script has problems with redirecting the ethminer output, such as:
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe2 in position 110: invalid continuation byte
"""

import configparser
import logging
from logging.handlers import RotatingFileHandler
import os.path
import sys

# Add linux-scripts folder to PATH
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
LOG_DIR = os.path.join(REPO_DIR, "logs")
sys.path.append(REPO_DIR)
import misc_utils as utils

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(module)-16s %(message)s",
    handlers=[
        # logging.StreamHandler(),
        RotatingFileHandler(filename=os.path.join(REPO_DIR, "logs", "ethminer.txt"))
    ]
)


def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(SCRIPT_DIR, "ethminer.txt"))
    eth = config["Ethminer"]

    pool = f'{eth["Scheme"]}://{eth["Address"]}@{eth["Hostname"]}:{eth["Port"]}'
    # TODO: the device listing output does not get redirected properly
    utils.print_info("Ethminer devices:")
    utils.run([os.path.join(SCRIPT_DIR, "ethminer", "ethminer"), "--list-devices"])
    utils.print_info("Starting ethminer")
    utils.run([os.path.join(SCRIPT_DIR, "ethminer", "ethminer"), "-P", pool])


if __name__ == "__main__":
    main()
