#!/usr/bin/env bash
set -u

# https://kcore.org/2022/05/18/ssh-passphrases-kde/

export SSH_ASKPASS="/usr/bin/ksshaskpass"
export SSH_ASKPASS_REQUIRE=prefer

if ! pgrep -u "${USER}" ssh-agent > /dev/null; then
    ssh-agent > ~/.ssh-agent-info
fi
if [[ "${SSH_AGENT_PID}" == "" ]]; then
    eval "$(<~/.ssh-agent-info)"
fi
