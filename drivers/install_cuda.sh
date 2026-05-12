#!/bin/bash -e
# CUDA installer
# https://developer.nvidia.com/cuda-downloads

# You can find cuDNN at
# https://developer.nvidia.com/rdp/cudnn-download

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
NVIDIA_PACKAGES=(
    "^cuda.*$" \
    "^libcublas.*$" "^libcufft.*$" "^libcufile.*$" "^libcurand.*$" "^libcusolver.*$" "^libcusparse.*$" \
    "^libnpp.*$" "^libnvfatbin.*$" "^libnvidia.*$" "^libnvjitlink.*$" "^libnvjpeg.*$" "^libnvvm.*$" \
    "^nvidia.*$" "^xserver-xorg-video-nvidia.*$"
)

if [ "${1}" = "--hold" ]; then
  apt-mark hold "${NVIDIA_PACKAGES[@]}"
  return 0
fi

# Delete old signing key
if command -v apt-key &> /dev/null; then
  echo "Removing old apt key."
  apt-key del 7fa2af80
fi

if [ "${1}" = "--fix" ]; then
  apt purge "${NVIDIA_PACKAGES[@]}"
  apt autoremove
fi

. "${SCRIPT_DIR}/setup_nvidia_repos.sh"

# https://www.reddit.com/r/linux_gaming/comments/1dnccoq/ubuntu_2404_wayland_on_nvidia_troubleshoot_guide/
# https://askubuntu.com/questions/1514352/ubuntu-24-04-with-nvidia-driver-libegl-warning-egl-failed-to-create-dri2-scre
if lshw -C display | grep "GeForce MX150"; then
  echo "Old MX150 GPU detected. Installing driver version 580."
  echo "If you get a black screen after installing, add \"modprobe.blacklist=nvidia_drm\" to GRUB_CMDLINE_LINUX_DEFAULT in /etc/default/grub"
  # The driver pinning has to be installed before other packages so that the pinning is effective.
  apt install nvidia-driver-pinning-580
  apt install --upgrade cuda-13-0 cuda-drivers-580 nvidia-container-toolkit
else
  apt install --upgrade cuda nvidia-container-toolkit  # libnvidia-egl-wayland1
fi
apt autoremove

echo "Fixing suspend."
# https://bbs.archlinux.org/viewtopic.php?id=288181
systemctl enable nvidia-suspend.service nvidia-hibernate.service nvidia-resume.service
echo "Installation ready."
