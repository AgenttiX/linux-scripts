#!/usr/bin/env sh
set -eu

# This does not seem to fix the Plasma crash on Kubuntu 24.10
# if pgrep -x "plasmashell" > /dev/null; then
#   sleep 1
#   killall plasmashell -9
#   sleep 1
#   kstart plasmashell
# fi
