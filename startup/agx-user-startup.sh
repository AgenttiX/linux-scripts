#!/usr/bin/env bash
# set -e
set -u

echo "Configuring SSH agent"
SETUP_AGENT="${HOME}/Git/private-scripts/ssh/setup_agent.sh"
if [ -f "${SETUP_AGENT}" ]; then
  "${SETUP_AGENT}"
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
