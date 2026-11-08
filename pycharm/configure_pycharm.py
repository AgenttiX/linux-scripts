#!/usr/bin/env python3

"""Set the JVM options of the latest PyCharm version that has a config directory.

The IDE has to be restarted for the changes to take effect.
"""

import os
import pathlib
import re
import sys
import tempfile

CONFIG_DIR_PATTERN: re.Pattern[str] = re.compile(r"PyCharm(\d+)\.(\d+)")
MAX_HEAP_MIB = 16384
# The indexing workers run in the same thread pool as the remote development protocol of the IDE.
# If they all get stuck, then the remote sessions hang in "Connecting" even though the SSH connection is fine.
# This has happened on a 64-core server with TeXiFy-IDEA, where each worker gets blocked when running a command.
# Therefore, keep at least half of the CPU cores free of indexing, since the size of the pool is based on them.
MAX_INDEXER_THREADS = 16


def heap_size_mib(mem_bytes: int) -> int:
    """Get the largest allowed heap size, which is a power of two and at most half of the RAM.

    :param mem_bytes: total RAM in bytes
    :return: heap size in MiB
    """
    heap_mib = MAX_HEAP_MIB
    while heap_mib * 1024 ** 2 * 2 > mem_bytes:
        heap_mib //= 2
    return heap_mib


def indexer_threads(cpu_count: int) -> int:
    """Get the number of indexing threads.

    :param cpu_count: number of available CPU cores
    :return: number of threads
    """
    return max(1, min(cpu_count // 2, MAX_INDEXER_THREADS))


def latest_config_dir(jetbrains_dir: pathlib.Path) -> pathlib.Path | None:
    """Get the config directory of the latest PyCharm version. This excludes e.g. PyCharm2026.3-backup.

    :param jetbrains_dir: directory of the JetBrains configs
    :return: config directory, or None if there are none
    """
    if not jetbrains_dir.is_dir():
        return None
    versions: dict[tuple[int, int], pathlib.Path] = {}
    for path in jetbrains_dir.iterdir():
        match = CONFIG_DIR_PATTERN.fullmatch(path.name)
        if match and path.is_dir():
            versions[(int(match[1]), int(match[2]))] = path
    return versions[max(versions)] if versions else None


def set_option(lines: list[str], prefix: str, value: str) -> list[str]:
    """Replace the existing values of an option, or append the option if there are none.

    :param lines: lines of the vmoptions file
    :param prefix: start of the option, e.g. "-Xmx"
    :param value: new value of the option
    :return: updated lines
    """
    option = f"{prefix}{value}"
    updated: list[str] = []
    done = False
    for line in lines:
        if not line.startswith(prefix):
            updated.append(line)
        elif not done:
            updated.append(option)
            done = True
    if not done:
        updated.append(option)
    return updated


def write_atomically(path: pathlib.Path, content: str) -> None:
    """Replace the content of an existing file atomically, while retaining its permissions.

    :param path: path of the file
    :param content: new content
    """
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(content)
        os.chmod(tmp_name, path.stat().st_mode)
        os.replace(tmp_name, path)
    except BaseException:
        os.unlink(tmp_name)
        raise


def main() -> int:
    """Update the vmoptions file.

    :return: exit code
    """
    config_home = os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
    config_dir = latest_config_dir(pathlib.Path(config_home) / "JetBrains")
    if config_dir is None:
        print("No PyCharm config directory was found.", file=sys.stderr)
        return 1

    heap_mib = heap_size_mib(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    threads = indexer_threads(len(os.sched_getaffinity(0)))

    vmoptions = config_dir / "pycharm64.vmoptions"
    vmoptions.touch()
    # The file may be a symlink, which should not be replaced with a regular file.
    vmoptions = vmoptions.resolve()

    old_content = vmoptions.read_text(encoding="utf-8")
    lines = set_option(old_content.splitlines(), "-Xmx", f"{heap_mib}m")
    lines = set_option(lines, "-Dcaches.indexerThreadsCount=", str(threads))
    new_content = "\n".join(lines) + "\n"

    if new_content == old_content:
        print(f"{vmoptions} is already up to date: -Xmx{heap_mib}m, {threads} indexing threads.")
    else:
        write_atomically(vmoptions, new_content)
        print(f"Updated {vmoptions}: -Xmx{heap_mib}m, {threads} indexing threads. Restart PyCharm to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
