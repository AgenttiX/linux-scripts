#!/usr/bin/bash -e

if ! (command -v f3read &> /dev/null); then
  echo "F3 seems not to be installed. Installing."
  sudo apt-get install f3
fi

f3write "$1"
f3read "$1"
