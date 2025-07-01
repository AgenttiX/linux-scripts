#!/usr/bin/env bash
set -e
# Flash memory testing script, based on f3

if [ ! $# -eq 1 ]; then
    echo "Give the path of the mounted partition as an argument"
    exit 1
fi
if [ ! -d $1 ]; then
    echo "The given argument should be a directory"
    exit 2
fi
if ! (command -v f3read &> /dev/null); then
  echo "F3 seems not to be installed. Installing."
  sudo apt install f3
fi
f3write $1
f3read $1
