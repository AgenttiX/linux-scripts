#!/usr/bin/env python3

"""
Script for removing old kernel versions
to free up space on the boot partition.

This is necessary on some old encrypted Ubuntu installations,
which have a too small boot partition by default.
"""

import os
import subprocess


def main():
    running = os.uname().release

    process = subprocess.run(["dpkg", "--list", "linux-image-*"], stdout=subprocess.PIPE, check=True)
    dpkg_output = process.stdout.decode("utf-8")

    kernels = []

    lines = dpkg_output.split("\n")
    for line in lines:
        columns = line.split()

        if len(columns) > 5:
            version = columns[1][12:]

            if version != "generic" and version[:5] != "extra":
                status = columns[0]
                kernels.append([version, status])

    running_index = -1

    print("Installed kernels")
    for index, kernel in enumerate(kernels):
        if kernel[0] == running:
            running_index = index
            print(index, kernel[0], "running")
        else:
            print(index, kernel[0], kernel[1])

    if running_index == -1:
        raise RuntimeError("The running kernel appears not to be installed")

    print("Which kernels would you like to remove? (Separate the numbers by spaces)")
    # Input is safe in Python 3
    remove_input = input()  # nosec

    remove_indexes = []
    for index in remove_input.split():
        index_int = int(index)
        if index_int == running_index:
            print("Running kernel cannot be removed")
            return
        remove_indexes.append(index_int)

    print("You chose")
    purge_these = []
    for index in remove_indexes:
        print(kernels[index][0])
        purge_these.append("linux-image-" + kernels[index][0])
        purge_these.append("linux-image-extra-" + kernels[index][0])
    print(purge_these)

    print("Is this ok?")
    # Input is safe in Python 3
    continue_str = input()  # nosec
    if continue_str == "y":
        print("Removing old kernels")
        subprocess.run(["apt-get", "purge"] + purge_these, check=True)
        print("Old kernels removed. Updating.")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "dist-upgrade"], check=True)
        subprocess.run(["apt-get", "autoremove"], check=True)
        print("Update complete")


if __name__ == "__main__":
    main()
