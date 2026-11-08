#!/usr/bin/env python3
"""Run the maintenance steps that require root privileges.

This is called by ``__main__.py`` with sudo, and should not usually be run directly.
"""

import argparse
import functools
import logging
import pathlib
import sys

# Allow running this file directly as a script.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from maintenance import bleachbit, cleanup, common, disks, packages, scanners
from utils.misc_utils import alert_if_not_root, print_info, run

logger: logging.Logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command-line arguments.

    :param argv: command-line arguments, defaults to ``sys.argv[1:]``
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    common.add_common_args(parser)
    power = parser.add_mutually_exclusive_group()
    power.add_argument("--reboot", help="Reboot once the maintenance is done", action="store_true")
    power.add_argument("--shutdown", help="Shut down once the maintenance is done", action="store_true")
    parser.add_argument("--zerofree", help="Zero free disk space without asking", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Run the maintenance steps that require root privileges.

    :param argv: command-line arguments, defaults to ``sys.argv[1:]``
    """
    args = parse_args(argv)
    alert_if_not_root()
    log_path = common.setup_logging("maintenance_sudo")
    logger.info("Args: %s", args)

    if args.bleachbit_only:
        bleachbit.bleachbit_args(args)
        return

    print_info(f"Running the maintenance steps that require root privileges. Logging to {log_path}")
    steps = [
        packages.apt,
        packages.snap,
        packages.flatpak,
        scanners.scan,
        functools.partial(cleanup.docker, all_unused_images=args.deep or args.docker),
        functools.partial(bleachbit.bleachbit_args, args),
        cleanup.remove_custom_files,
        disks.trim,
        packages.fwupdmgr,
    ]
    if args.zerofree:
        steps.append(disks.zero_free_space)
    steps.append(disks.mdadm)
    common.run_steps(steps)

    if args.reboot:
        run(["systemctl", "reboot"])
    elif args.shutdown:
        run(["systemctl", "poweroff"])


if __name__ == "__main__":
    main()
