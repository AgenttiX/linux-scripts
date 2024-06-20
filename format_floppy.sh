#!/usr/bin/env bash
set -eu

if [ "$1" == "" ]; then
  echo "Please add a device name as an argument."
  exit 1;
fi

echo "Formatting $1"
if [[ "$1" =~ ^/dev/sd.* ]]; then
  echo "This is a USB device. Formatting with ufiformat."
  ufiformat --inquire "$1"
  ufiformat --verify "$1"
elif [[ "$1" == ^/dev/fd.* ]]; then
  echo "This is a true floppy drive. Formatting with fdformat."
  fdformat fdformat --repair 10 "$1"
else
  echo "Unknown device type!"
fi

echo "Testing $1"
badblocks -wsv "$1"

echo "Creating file system"
mkfs.vfat -c -v "$1"
