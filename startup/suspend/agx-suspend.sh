#!/usr/bin/env sh
set -eu

USERNAME="$(id -nu 1000)"

if [ "${1}" = "pre" ]; then
  # Laptops should umount all network shares when going to sleep
  if [ "$(hostnamectl chassis)" = "laptop" ]; then
    umount --all --types cifs
  fi
# After resume
elif [ "${1}" = "post" ]; then
  USER_RESUME_SCRIPT="/home/${USERNAME}/Git/linux-scripts/startup/suspend/agx-resume-user.sh"
  if [ -f "${USER_RESUME_SCRIPT}" ]; then
    # Run as user
    sudo -u "${USERNAME}" -i "${USER_RESUME_SCRIPT}"
  else
    echo "User resume script was not found at ${USER_RESUME_SCRIPT}"
  fi
fi
