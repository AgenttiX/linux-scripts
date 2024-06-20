#!/usr/bin/env sh
# set -eu

[ -z "$SSH_AGENT_PID" ] || eval "$(ssh-agent -k)"
