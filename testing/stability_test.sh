#!/bin/sh -e
# TODO: Work in progress
# - Fix memtester
# - Add CPU stress testing

sudo apt update


sudo apt install memtester stress-ng

# flatpak install flathub com.geeks3d.furmark

# NPROC=$(nproc)
FREE_RAM="$(free -m | grep Mem | awk '{print $4}')"
MEMTESTER_RAM=$((FREE_RAM / 2))
MEMTESTER_ITERATIONS=10
# echo "Available CPU cores: ${NPROC}"
echo "Free RAM: ${FREE_RAM} MB, using for memtester: ${MEMTESTER_RAM} MB"

echo "Running stress-ng."
# Running as root enables e.g. process memory priority in low memory situations
sudo stress-ng --matrix -1 --timeout 1m --metrics --perf --times --tz

echo "Running memtester."
# http://pyropus.ca/software/memtester/
# Memtester should be run as root so that it can mlock the memory it tests.
sudo memtester "${MEMTESTER_RAM}" "${MEMTESTER_ITERATIONS}"
