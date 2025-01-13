#!/usr/bin/env bash
# This script should continue on errors
# set -e
set -u

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

if command -v kwallet-query &> /dev/null; then
  kwallet-query -l kdewallet > /dev/null
fi

# Run the pre-startup script again to ensure that the SSH agent is available
. "${SCRIPT_DIR}/agx-user-pre-startup.sh"

echo "Starting SSH agent configuration script."
SETUP_AGENT="${REPO_DIR}/ssh/setup_agent.sh"
if [ -f "${SETUP_AGENT}" ]; then
  "${SETUP_AGENT}" private-scripts
fi

# This should be before other applications just in case, since this configures audio settings for them.
if command -v pactl >/dev/null 2>&1; then
  echo "Configuring PipeWire"
  pactl load-module module-combine-sink
fi

if command -v syncthing  >/dev/null 2>&1; then
  syncthing &
fi

ACTIVITYWATCH="${HOME}/Downloads/activitywatch/aw-qt"
if [ -f "${ACTIVITYWATCH}" ]; then
  echo "Starting ActivityWatch"
  "${ACTIVITYWATCH}" &
fi

if command -v flatpak >/dev/null 2>&1; then
  echo "Starting Slack"
  flatpak run com.slack.Slack &
  echo "Starting Mattermost"
  flatpak run com.mattermost.Desktop &
fi

if command -v telegram-desktop  >/dev/null 2>&1; then
  echo "Starting Telegram"
  telegram-desktop &
fi
