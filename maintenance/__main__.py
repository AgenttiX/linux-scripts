#!/usr/bin/env python3
"""Routine maintenance script for GNU/Linux-based systems.

Should be run as a normal user. Pulls this repository, runs the maintenance steps of the current user,
and then runs the steps that require root privileges with sudo by calling ``sudo.py``.

Usage: ``./maintenance/__main__.py [arguments]``, or ``python3 -m maintenance [arguments]`` in the repository directory.
"""

import argparse
import logging
import os
import pathlib
import sys

# Allow running this file directly as a script.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from git import pull
from maintenance import bleachbit, cleanup, common, disks, packages
from utils.misc_utils import alert_if_root, print_info, run_interactive

logger: logging.Logger = logging.getLogger(__name__)


def git_pull() -> None:
    """Pull the latest version of this repository.

    :raises SystemExit: if the pull fails, as the root part should not be run with an unexpected version
    """
    print_info("Updating the linux-scripts repository")
    result = pull.pull(common.REPO_DIR)
    logger.info("git pull returned %s with output:\n%s", result.returncode, result.output)
    pull.print_result(result, color=sys.stdout.isatty() and "NO_COLOR" not in os.environ)
    if result.returncode:
        raise SystemExit(f"Pulling the repository failed with code {result.returncode}. Use --no-pull to skip it.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command-line arguments.

    :param argv: command-line arguments, defaults to ``sys.argv[1:]``
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common.add_common_args(parser)
    power = parser.add_mutually_exclusive_group()
    power.add_argument("--reboot", help="Reboot once the script is ready", action="store_true")
    power.add_argument("--shutdown", help="Shut down once the script is ready", action="store_true")
    parser.add_argument("--no-pull", help="Do not pull the linux-scripts repository", action="store_true")
    parser.add_argument("--skip-sudo", help="Skip the steps that require root privileges", action="store_true")
    parser.add_argument("--virtualbox", help="Optimize VirtualBox disk images on the host", action="store_true")
    parser.add_argument("--zerofree", help="Zero free disk space", action="store_true")
    return parser.parse_args(argv)


def sudo_command(args: argparse.Namespace, zerofree: bool) -> list[str]:
    """Create the command for running the root part with sudo.

    :param args: command-line arguments of the user part
    :param zerofree: whether to zero free disk space
    :return: command and its arguments
    """
    flags = {
        "--bleachbit-only": args.bleachbit_only,
        "--deep": args.deep,
        "--docker": args.docker,
        "--firefox": args.firefox,
        "--reboot": args.reboot,
        "--shutdown": args.shutdown,
        "--thunderbird": args.thunderbird,
        "--zerofree": zerofree,
    }
    return [
        "sudo", common.SYSTEM_PYTHON, str(common.PACKAGE_DIR / "sudo.py"),
        *(flag for flag, enabled in flags.items() if enabled),
    ]


def main(argv: list[str] | None = None) -> None:
    """Run the maintenance script.

    :param argv: command-line arguments, defaults to ``sys.argv[1:]``
    :raises NotImplementedError: if VirtualBox maintenance is selected
    """
    args = parse_args(argv)
    alert_if_root(fail=True)
    log_path = common.setup_logging("maintenance")
    logger.info("Args: %s", args)
    if args.virtualbox:
        raise NotImplementedError("VirtualBox support does not work yet.")
    if args.deep:
        print_info("Deep scan has been selected. Some processes may take a long time.")

    if args.bleachbit_only:
        steps = [lambda: bleachbit.bleachbit_args(args)]
        zerofree = False
    else:
        # Ask this before starting, so that the rest can be run unattended.
        zerofree = False if args.skip_sudo else disks.should_zero_free_space(args.zerofree)
        print_info(f"Running maintenance script. Logging to {log_path}")
        steps = [
            *([] if args.no_pull else [git_pull]),
            packages.zgen,
            cleanup.apptainer,
            lambda: bleachbit.bleachbit_args(args),
        ]
    common.run_steps(steps)

    if args.skip_sudo:
        return
    print()
    # The root part is run interactively, so that e.g. APT can ask questions.
    run_interactive(sudo_command(args, zerofree=zerofree))


if __name__ == "__main__":
    main()
