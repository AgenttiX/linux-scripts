#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "$(dirname "${SCRIPT_DIR}")")"

. "${REPO_DIR}/utils.sh"

# This does not seem to fix the Plasma crash on Kubuntu 24.10
# if pgrep -x "plasmashell" > /dev/null; then
#   sleep 1
#   killall plasmashell -9
#   sleep 1
#   kstart plasmashell
# fi

# Wait for the laptop to connect to Wi-Fi.
echo "Waiting to ensure that Wi-Fi will be available."
sleep 3
SSID="$(get-ssid)"
if [ "${SSID}" = "eduroam" ]; then
  echo "Eduroam connection detected. Closing personal apps and starting work apps."
  # Close personal messaging apps.
  if pgrep -x "discord" > /dev/null 2>&1; then
    killall discord
  fi
  if pgrep -x "ferdium" > /dev/null 2>&1; then
    killall ferdium
  fi
  if pgrep -f "signal-desktop" > /dev/null 2>&1; then
    killall signal-desktop
  fi
  if pgrep -f "telegram-desktop" > /dev/null 2>&1; then
    killall telegram-desktop
  fi
  # Start work messaging apps.
  if pgrep -f "mattermost-desktop" > /dev/null 2>&1; then :; else
    flatpak run com.mattermost.Desktop --hidden &
  fi
  if pgrep -x "slack" > /dev/null 2>&1; then :; else
    flatpak run com.slack.Slack --startup &
  fi
elif [ "${SSID}" = "Agnet" ]; then
  echo "Agnet connection detected. Starting personal apps."
  if pgrep -f "signal-desktop" > /dev/null 2>&1; then :; else
    signal-desktop --start-in-tray &
  fi
  if pgrep -f "telegram-desktop" > /dev/null 2>&1; then :; else
    telegram-desktop -startintray &
  fi
fi
