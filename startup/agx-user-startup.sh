#!/usr/bin/env bash
# set -e

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
