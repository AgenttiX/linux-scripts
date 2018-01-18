# Created by Mika Mäki, 2017-2018

import os
import subprocess


def main():
    running = os.uname().release

    process = subprocess.run(["dpkg", "--list", "linux-image-*"], stdout=subprocess.PIPE)
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

    print("Which kernels would you like to remove?")
    remove_input = input()

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
    continue_str = input()
    if continue_str == "y":
        print("Removing old kernels")
        subprocess.run(["apt-get", "purge"] + purge_these)
        print("Old kernels removed. Updating.")
        subprocess.run(["apt-get", "update"])
        subprocess.run(["apt-get", "dist-upgrade"])
        subprocess.run(["apt-get", "autoremove"])
        print("Update complete")

main()
