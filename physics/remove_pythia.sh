#!/usr/bin/bash -e

if [ "$EUID" -ne 0 ]; then
  echo "This script should be run as root."
  exit
fi

rm -rf /usr/local/include/Pythia8
rm -rf /usr/local/include/Pythia8Plugins
rm -rf /usr/local/share/Pythia8
rm -f /usr/local/bin/pythia8-config
rm -f /usr/local/lib/_pythia8.so
rm -f /usr/local/lib/libpythia8.a
rm -f /usr/local/lib/libpythia8*.so
rm -f /usr/local/lib/pythia8.*
