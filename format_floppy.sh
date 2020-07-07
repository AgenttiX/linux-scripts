#!/bin/bash
echo "Shredding & formatting $1"
badblocks -wsv "$1"
if [[ "$1" =~ ^/dev/sd.* ]]; then
  echo "This is a USB device. Formatting with ubiformat."
  ufiformat --verify "$1"
elif [[ "$1" == ^/dev/fd.* ]]; then
  echo "This is a true floppy drive. Formatting with fdformat."
  fdformat fdformat --repair 10 "$1"
else
  echo "Unknown device type!"
fi
