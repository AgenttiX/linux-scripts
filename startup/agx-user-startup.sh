#!/usr/bin/env bash
# This script should continue on errors
# set -e
set -u

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

echo "Starting SSH agent configuration script."
SETUP_AGENT="${REPO_DIR}/ssh/setup_agent.sh"
if [ -f "${SETUP_AGENT}" ]; then
  "${SETUP_AGENT}" private-scripts
fi

ACTIVITYWATCH="${HOME}/Downloads/activitywatch/aw-qt"
if [ -f "${ACTIVITYWATCH}" ]; then
  echo "Starting ActivityWatch"
  "${ACTIVITYWATCH}" &
fi

if command -v pactl >/dev/null 2>&1; then
  echo "Configuring PipeWire"
  pactl load-module module-combine-sink
fi

if command -v flatpak >/dev/null 2>&1; then
  echo "Starting Slack"
  flatpak run com.slack.Slack
  echo "Starting Mattermost"
  flatpak run com.mattermost.Desktop
fi
