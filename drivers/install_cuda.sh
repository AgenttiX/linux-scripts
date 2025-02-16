#!/bin/bash -e
# CUDA installer
# From
# https://developer.nvidia.com/cuda-downloads

# You can find cuDNN at
# https://developer.nvidia.com/rdp/cudnn-download

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Delete old signing key
apt-key del 7fa2af80

if [ "${1}" = "--fix" ]; then
  apt purge "^cuda.*$" "^libnvidia.*$" "^nvidia.*$"
  apt autoremove
  apt clean
fi

. "${SCRIPT_DIR}/setup_nvidia_repos.sh"

apt-get update
# https://www.reddit.com/r/linux_gaming/comments/1dnccoq/ubuntu_2404_wayland_on_nvidia_troubleshoot_guide/
# https://askubuntu.com/questions/1514352/ubuntu-24-04-with-nvidia-driver-libegl-warning-egl-failed-to-create-dri2-scre
apt-get install cuda nvidia-container-toolkit  # libnvidia-egl-wayland1

echo "Fixing suspend."
# https://bbs.archlinux.org/viewtopic.php?id=288181
systemctl enable nvidia-suspend.service nvidia-hibernate.service nvidia-resume.service
echo "Installation ready."
