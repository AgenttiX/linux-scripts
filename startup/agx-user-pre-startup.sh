#!/usr/bin/env bash
# This should not be set, as it would cause an error when checking if SSH_AGENT_PID is set
# set -u

# https://kcore.org/2022/05/18/ssh-passphrases-kde/

# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# REPO_DIR="$(dirname "${SCRIPT_DIR}")"
# LOG_PATH="${REPO_DIR}/logs/agx-user-pre-startup.txt"

# echo "Running agx-user-pre-startup.sh at $(date +%F_%H-%M-%S)" >> "${LOG_PATH}"

export SSH_ASKPASS="/usr/bin/ksshaskpass"
export SSH_ASKPASS_REQUIRE=prefer

# Wait for kwallet
# This is necessary on Wayland, but not on X11
# if command -v kwallet-query &> /dev/null; then
#   kwallet-query -l kdewallet > /dev/null
# fi

# SSH_AGENT_UPDATED=false
# Pgrep finds regexes, and without the specification for the start and end of the line,
# it could find e.g. the gcr-ssh-agent provided by the package gcr,
# and not start the correct SSH agent.
# if ! pgrep -u "${USER}" '^ssh-agent$' > /dev/null; then
  # echo "SSH agent seems not to be started. Starting, and saving its configuration."
  # ssh-agent > "${HOME}/.ssh-agent-info"
  # SSH_AGENT_UPDATED=true
# fi
# if [ "${SSH_AGENT_UPDATED}" = true ] || [[ "${SSH_AGENT_PID}" == "" ]]; then
#   echo "SSH agent configuration seems not to be loaded. Loading."
#   eval "$(<"${HOME}/.ssh-agent-info")" > /dev/null
# fi

# echo "SSH_AUTH_SOCK=${SSH_AUTH_SOCK}" >> "${LOG_PATH}"
# echo "SSH_AGENT_PID=${SSH_AGENT_PID}" >> "${LOG_PATH}"
# echo "Finished agx-user-pre-startup.sh at $(date +%F_%H-%M-%S)" >> "${LOG_PATH}"
