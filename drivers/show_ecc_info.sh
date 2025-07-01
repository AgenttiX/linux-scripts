#!/usr/bin/env sh
set -eu

# https://www.setphaserstostun.org/posts/monitoring-ecc-memory-on-linux-with-rasdaemon/

if ! command -v ras-mc-ctl 2>&1 >/dev/null; then
  echo "Rasdaemon seems not to be installed. Installing."
  apt update
  apt install rasdaemon
  systemctl enable rasdaemon
  systemctl start rasdaemon
fi

# "To identify which DIMM slot corresponds to which EDAC path
# you will have to reboot your system with only one DIMM inserted,
# write down the name of the slot you insterted it in and then printing out the paths with ras-mc-ctl --error-count."
ras-mc-ctl --print-labels

ras-mc-ctl --error-count
