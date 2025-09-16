#!/usr/bin/env bash
set -eu

# Before running this script on Kubuntu, enable Flatpak backend here:
# https://flatpak.org/setup/Kubuntu

# These have to be installed manually:
# TeamViewer

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

set +u
if [ ! -z "${XDG_CURRENT_DESKTOP}" ]; then
  IS_DESKTOP=true
else
  IS_DESKTOP=false
fi
set -u

echo "Configuring apt/dpkg architectures."
ARCH="$(uname -i)"
FOREIGN_ARCHS="$(dpkg --print-foreign-architectures)}"
if [ "${ARCH}" = "x86_64" ] && [[ "${FOREIGN_ARCHS}" != *"i386"* ]]; then
  echo "Detected x86_64 architecture where i386 is not enabled. Enabling i386."
  dpkg --add-architecture i386
fi

echo "Updating apt repositories."
apt update

echo "Constructing the list of apt packages to install."
BASE_PACKAGES=(
  # Servers should have git-gui too for X11 forwarding.
  "apt-transport-https" "bleachbit" "ca-certificates" "git" "git-gui" "htop" "mosh" "openssh-server" "screen" "ufw"
)
DEV_PACKAGES=(
  "build-essential" "cloc" "cmake" "gcc-multilib" "g++-multilib" "gfortran"
)
DOCKER_PACKAGES=(
  "docker-ce" "docker-ce-cli" "containerd.io" "docker-buildx-plugin" "docker-compose-plugin"
)
PYTHON_PACKAGES=(
  "python3-dev" "python3-setuptools" "python3-venv" "python3-wheel"
)
UTILS_PACKAGES=(
  "autojump" "autossh" "cifs-utils" "curl" "fastfetch" "git-delta" "gpg-agent" "links"
  "mtr-tiny" "optipng" "pandoc" "texlive-full" "traceroute" "wget" "wireguard" "xindy" "yt-dlp" "zsh"
)
APT_PACKAGES=("${BASE_PACKAGES[@]}" "${DEV_PACKAGES[@]}" "${DOCKER_PACKAGES[@]}" "${GUI_PACKAGES[@]}" "${PYTHON_PACKAGES[@]}" "${UTILS_PACKAGES[@]}")

# If running in a desktop environment. All GUI programs should go here.
if [ "${IS_DESKTOP}" = true ]; then
  APT_PACKAGES+=(
    "clamtk" "filelight" "filezilla" "gimp" "inkscape"
    "keepassxc" "ktorrent" "libenchant-2-voikko"
    "libreoffice" "libreoffice-help-en-us" "libreoffice-help-fi" "libreoffice-voikko"
    "mumble" "network-manager-openvpn" "remmina" "signal-desktop" "steam"
    "synaptic" "texmaker" "tikzit" "tmispell-voikko" "vlc"
  )
  if [ "${XDE_CURRENT_DESKTOP}" = "KDE" ]; then
    APT_PACKAGES+=("kde-config-flatpak" "remmina-plugin-kwallet")
  fi
  if [ "${XDE_SESSION_TYPE}" = "wayland" ]; then
    APT_PACKAGES+=("freerdp2-wayland")
  fi
  if dpkg -s google-chrome-stable &> /dev/null; then
    echo "Google Chrome is already installed."
  else
    echo "Adding Google Chrome to the installation list."
    CHROME_DEB="google-chrome-stable_current_amd64.deb"
    CHROME_DEB_PATH="${SCRIPT_DIR}/${CHROME_DEB}"
    wget "https://dl.google.com/linux/direct/${CHROME_DEB}" -O "${CHROME_DEB_PATH}"
    APT_PACKAGES+=("${CHROME_DEB_PATH}")
  fi
fi

# If running on physical hardware
if ! grep -q "hypervisor" /proc/cpuinfo; then
  APT_PACKAGES+=(
    "bluetooth" "boinc-client-opencl" "clinfo" "clpeak" "exfatprogs" "gdisk"
    "lm-sensors" "pocl-opencl-icd" "powertop" "s-tui" "stress" "usbtop"
  )
  if [ "${IS_DESKTOP}" = true ]; then
    APT_PACKAGES+=("boinc" "cutecom" "gnome-disk-utility" "gparted" "obs-studio" "pipewire-audio" "rpi-imager")
  fi
fi
# If running on a laptop
if [ "$(hostnamectl chassis)" = "laptop" ]; then
  APT_PACKAGES+=("tlp" "touchegg")
fi
# If the system has an Intel CPU
if grep -q "Intel" /proc/cpuinfo; then
  APT_PACKAGES+=("intel-media-va-driver" "intel-microcode" "intel-opencl-icd")
fi
# If the system has an Nvidia GPU
if command -v nvidia-smi &> /dev/null; then
  APT_PACKAGES+=("boinc-client-nvidia-cuda")
fi

echo "Installing apt packages."
apt install "${APT_PACKAGES[@]}"

if [ "${IS_DESKTOP}" = true ]; then
  echo "Installing Snap packages."
  snap install pycharm-professional --classic
  # Telegram snap does not work on Kubuntu 25.04
  # https://github.com/telegramdesktop/tdesktop/issues/29437#issuecomment-3131627645
  # snap install telegram-desktop

  echo "Installing Flatpak packages."
  flatpak install flathub \
    cc.arduino.IDE2 \
    com.discordapp.Discord \
    com.github.tchx84.Flatseal \
    com.github.iwalton3.jellyfin-media-player \
    com.github.xournalpp.xournalpp \
    com.mastermindzh.tidal-hifi \
    com.mattermost.Desktop \
    com.plexamp.Plexamp \
    com.slack.Slack \
    com.spotify.Client \
    com.vscodium.codium \
    md.obsidian.Obsidian \
    net.lutris.Lutris \
    org.blender.Blender \
    org.chromium.Chromium \
    org.ferdium.Ferdium \
    org.telegram.desktop \
    org.zotero.Zotero \
    tv.plex.PlexDesktop

  if command -v asdf &> /dev/null; then
    # https://github.com/GloriousEggroll/proton-ge-custom
    echo "Installing ProtonGE using asdf."
    asdf plugin add protonge
    asdf install protonge latest
  else
    echo "asdf was not found. Skipping ProtonGE installation."
  fi
fi

echo "Software installed."
