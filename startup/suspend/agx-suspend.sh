#!/usr/bin/env bash
set -eu

USERNAME="$(id -nu 1000)"
# After resume
if [[ "${1}" == "post" ]]; then
    sudo -u "${USERNAME}" -i "/home/${USERNAME}/Git/linux-scripts/startup/suspend/agx-resume-user.sh"
fi
