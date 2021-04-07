#!/usr/bin/bash -e

if [ "$EUID" -ne 0 ]; then
  echo "This script should be run as root."
  exit
fi

rm /usr/local/bin/pythia8-config
rm /usr/local/share/Pythia8 -r
rm /usr/local/lib/_pythia8.so
rm /usr/local/lib/libpythia8.a
rm /usr/local/lib/libpythia8*.so
rm /usr/local/lib/pythia8.*
