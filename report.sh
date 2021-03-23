#!/bin/bash -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DIR="${SCRIPT_DIR}/logs/report"

if [ -z "$DIR" ]; then
  echo "Could not configure directory variable: $DIR"
  exit 1
fi

mkdir -p "$DIR"
if [ "$(ls -A $DIR)" ]; then
  rm "${DIR:?}"/*
fi

hostname | tee -a "$DIR/basic.txt"
uname -a | tee -a "$DIR/basic.txt"

lsblk -a > "$DIR/lsblk.txt"
lscpu > "$DIR/lscpu.txt"
lshw -html > "$DIR/lshw.html"
lspci > "$DIR/lspci.txt"
lsusb > "$DIR/lsusb.txt"

vainfo &> "$DIR/vainfo.txt"
vdpauinfo &> "$DIR/vdpauinfo.txt"

xinput list &> "$DIR/xinput.txt"
xrandr &> "$DIR/xrandr.txt"

# TODO
# dmidecode
# hdparm
# lsscsi
