"""Cleaning of caches and unnecessary files."""

import pathlib
import shutil

from utils.misc_utils import get_user, print_info, run

#: Files that some programs leave in the home directory
CUSTOM_HOME_FILES: tuple[str, ...] = (
    "client_state.xml",
    "coproc_info.xml",
    "lockfile",
    "stderrgpudetect.txt",
    "stdoutgpudetect.txt",
    "time_stats_log",
)


def apptainer() -> None:
    """Clean the Apptainer cache of the current user."""
    if shutil.which("apptainer") is None:
        print_info("Apptainer not found")
        return
    print_info("Cleaning Apptainer cache")
    run(["apptainer", "cache", "clean", "--force"])


def docker(all_unused_images: bool = False) -> None:
    """Prune unused Docker data.

    :param all_unused_images: whether to remove all unused images and not just dangling ones
    """
    if shutil.which("docker") is None:
        print_info("Docker not found")
        return
    print_info("Pruning Docker")
    args = ["docker", "system", "prune", "-f"]
    if all_unused_images:
        args.append("-a")
    run(args, sudo=True)


def remove_custom_files(home: pathlib.Path | None = None) -> None:
    """Remove files that some programs leave in the home directory.

    :param home: home directory, defaults to that of the user who ran the script (also with sudo)
    """
    if home is None:
        home = pathlib.Path("/home") / get_user()
    print_info(f"Removing custom files from {home}")
    for name in CUSTOM_HOME_FILES:
        path = home / name
        # Don't follow symlinks, as this may be run as root.
        if path.is_file() and not path.is_symlink():
            print_info(f"Removing \"{path}\"")
            path.unlink()
