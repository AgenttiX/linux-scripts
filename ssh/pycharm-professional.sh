#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ -f "${HOME}/.ssh-agent-info" ]; then
  eval "$(<"${HOME}/.ssh-agent-info")" > /dev/null
fi

export BAMF_DESKTOP_FILE_HINT=/var/lib/snapd/desktop/applications/pycharm-professional_pycharm-professional.desktop
/snap/bin/pycharm-professional "$@"
