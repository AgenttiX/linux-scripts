#!/usr/bin/env python3

"""Configure Git to use the shared config of this directory and a private config.

Links ``~/.config/git`` to this directory:
a symbolic link on Linux and a directory junction on Windows,
neither of which requires administrator privileges.
An existing ``~/.config/git`` directory is moved to a backup next to it.

The shared config includes ``~/.config/git/config_private``,
so the private config is made available as ``config_private`` in this directory.
On Linux it is a symbolic link to the private config.
On Windows it is a copy, since a symbolic link to a file requires administrator privileges or Developer Mode,
so rerun this script after editing the private config.
``config_private`` is in ``.gitignore``.

Usage: ``python3 -m git <path to the private Git config>`` in the repository directory.
"""

import argparse
from collections.abc import Sequence
import datetime
import pathlib
import shutil
import sys

if sys.platform == "win32":
    import _winapi

GIT_DIR = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = pathlib.Path.home() / ".config" / "git"
PRIVATE_CONFIG_NAME = "config_private"


def backup_path(path: pathlib.Path) -> pathlib.Path:
    """Get a path for a backup of the given path.

    :param path: path to back up
    :return: path with a timestamp suffix in the same directory
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return path.with_name(f"{path.name}.backup_{timestamp}")


def create_dir_link(link: pathlib.Path, target: pathlib.Path) -> None:
    """Create a link to a directory without administrator privileges.

    :param link: path of the link to create
    :param target: existing directory that the link points to
    """
    if sys.platform == "win32":
        # Unlike symbolic links, directory junctions can be created without administrator privileges.
        _winapi.CreateJunction(str(target.resolve()), str(link))
    else:
        link.symlink_to(target.resolve(), target_is_directory=True)


def install_private_config(
        source: pathlib.Path,
        target_dir: pathlib.Path = GIT_DIR,
        copy: bool = sys.platform == "win32") -> pathlib.Path:
    """Make the private config available as ``config_private`` in the target directory.

    :param source: private config file
    :param target_dir: directory of the shared config
    :param copy: copy the file instead of creating a symbolic link
    :return: path of the installed private config
    :raises FileNotFoundError: if the private config does not exist
    :raises ValueError: if the private config is the installed file itself
    """
    source = source.resolve(strict=True)
    if not source.is_file():
        msg = f"The private Git config is not a file: {source}"
        raise FileNotFoundError(msg)
    dest = target_dir / PRIVATE_CONFIG_NAME
    if dest.exists() and not dest.is_symlink() and dest.samefile(source):
        msg = f"The private Git config must be outside of {target_dir}: {source}"
        raise ValueError(msg)
    # Remove the old file or link first, so that copying cannot write through a link to the private config.
    dest.unlink(missing_ok=True)
    if copy:
        shutil.copyfile(source, dest)
    else:
        dest.symlink_to(source)
    return dest


def is_link(path: pathlib.Path) -> bool:
    """Check whether the path is a symbolic link or a directory junction.

    :param path: path to check
    :return: whether the path is a link
    """
    return path.is_symlink() or path.is_junction()


def link_config_dir(config_dir: pathlib.Path = CONFIG_DIR, target: pathlib.Path = GIT_DIR) -> pathlib.Path | None:
    """Link the Git config directory to the target directory.

    An existing link elsewhere is replaced, and an existing file or directory is moved to a backup.

    :param config_dir: path of the link, usually ``~/.config/git``
    :param target: directory containing the shared config
    :return: path of the backup, if one was created
    """
    backup = None
    if is_link(config_dir):
        if config_dir.resolve() == target.resolve():
            print(f"{config_dir} already links to {target}.")
            return None
        print(f"Replacing the link {config_dir} -> {config_dir.resolve()}")
        remove_link(config_dir)
    elif config_dir.exists():
        backup = backup_path(config_dir)
        config_dir.rename(backup)
        print(f"Moved the existing {config_dir} to {backup}")
    config_dir.parent.mkdir(parents=True, exist_ok=True)
    create_dir_link(config_dir, target)
    print(f"Linked {config_dir} -> {target}")
    return backup


def remove_link(path: pathlib.Path) -> None:
    """Remove a symbolic link or a directory junction without touching its target.

    :param path: link to remove
    """
    if path.is_junction():
        # A junction is removed like an empty directory.
        path.rmdir()
    else:
        path.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    """Configure Git with the shared config and the given private config.

    :param argv: command-line arguments, or None to use sys.argv
    :return: exit code
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("private_config", type=pathlib.Path, help="path to the private Git config")
    args = parser.parse_args(argv)

    private_config: pathlib.Path = args.private_config
    if not private_config.is_file():
        print(f"The private Git config does not exist: {private_config}", file=sys.stderr)
        return 1
    try:
        install_private_config(private_config)
    except (FileNotFoundError, ValueError) as e:
        print(e, file=sys.stderr)
        return 1
    action = "Copied" if sys.platform == "win32" else "Linked"
    print(f"{action} the private config {private_config.resolve()} to {GIT_DIR / PRIVATE_CONFIG_NAME}")
    backup = link_config_dir()
    if backup is not None:
        print(f"Check {backup} for files that should be moved to the new config directory.")

    gitconfig = pathlib.Path.home() / ".gitconfig"
    if gitconfig.exists():
        print(f"Note: {gitconfig} exists, and its settings override the ones in {CONFIG_DIR}.")
    print("Git configured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
