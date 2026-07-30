#!/usr/bin/env bash
set -euo pipefail

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

ARCH="$(dpkg --print-architecture)"
CHASSIS="$(hostnamectl chassis)"
FOREIGN_ARCHS="$(dpkg --print-foreign-architectures)}"
# This is a newline-separated string, not an array.
INSTALLED="$(dpkg-query --show --showformat='${Package} ${db:Status-Status}\n' | awk '$2 == "installed" {print $1}')"

echo "Configuring apt/dpkg architectures."
if [ "${ARCH}" = "amd64" ] && [[ "${FOREIGN_ARCHS}" != *"i386"* ]]; then
  echo "Detected amd64 architecture where i386 is not enabled. Enabling i386."
  dpkg --add-architecture i386
fi

echo "Updating apt repositories."
apt update

echo "Constructing the list of apt packages to install."
BASE_PACKAGES=(
  # Servers should have git-gui too for X11 forwarding.
  # Screen has been replaced with tmux.
  "7zip" "apt-transport-https" "ca-certificates" "git" "git-gui"
  "htop" "mosh" "openssh-server" "rsync" "tmux" "ufw"
)
DEV_PACKAGES=(
  "build-essential" "cloc" "cmake" "gcc-multilib" "g++-multilib" "gfortran"
)
DOCKER_PACKAGES=(
  "docker-ce" "docker-ce-cli" "containerd.io" "docker-buildx-plugin" "docker-compose-plugin"
)
FUN_PACKAGES=(
  "cmatrix" "cowsay" "fortune-mod"
)
PYTHON_PACKAGES=(
  "python3-dev" "python3-setuptools" "python3-venv" "python3-wheel"
)
UTILS_PACKAGES=(
  "autojump" "autossh" "bleachbit" "cifs-utils" "curl" "dislocker" "fastfetch" "git-delta"
  "gocryptfs" "gpg" "gpg-agent" "links" "mtr-tiny" "nmap" "optipng" "pandoc" "pdftk" "rclone" "ssh-tools"
  "texlive-full" "traceroute" "wget" "wireguard" "xindy"
  # The yt-dlp apt package may not be up to date. In this case, use pip to install the latest version.
  "yt-dlp"
  "zsh"
)

# If running in a desktop environment. All GUI programs should go here.
if [ "${IS_DESKTOP}" = true ]; then
  DESKTOP_PACKAGES=(
    "clamtk" "claude-desktop" "eduvpn-client" "filelight" "filezilla" "gimp" "haruna" "inkscape"
    "keepassxc" "krdc" "ktorrent" "libenchant-2-voikko"
    "libreoffice" "libreoffice-help-en-us" "libreoffice-help-fi" "libreoffice-voikko"
    "mumble" "network-manager-openvpn" "remmina" "signal-desktop" "steam"
    "synaptic" "texmaker" "tikzit" "tmispell-voikko" "vlc"
  )
  if [ "${XDG_CURRENT_DESKTOP}" = "KDE" ]; then
    DESKTOP_PACKAGES+=("kde-config-flatpak" "remmina-plugin-kwallet")
  fi
  # XDG_SESSION_TYPE is not set properly when running with sudo.
  # if [ "${XDG_SESSION_TYPE}" = "wayland" ]; then
  #   APT_PACKAGES+=("freerdp2-wayland")
  # fi
  if dpkg -s google-chrome-stable &> /dev/null; then
    echo "Google Chrome is already installed."
  else
    echo "Adding Google Chrome to the installation list."
    CHROME_DEB="google-chrome-stable_current_amd64.deb"
    CHROME_DEB_PATH="${SCRIPT_DIR}/${CHROME_DEB}"
    wget "https://dl.google.com/linux/direct/${CHROME_DEB}" -O "${CHROME_DEB_PATH}"
    DESKTOP_PACKAGES+=("${CHROME_DEB_PATH}")
  fi
  if dpkg -s zoom &> /dev/null; then
    echo "Zoom is already installed."
  else
    echo "Adding Zoom to the installation list."
    ZOOM_DEB="zoom_amd64.deb"
    ZOOM_DEB_PATH="${SCRIPT_DIR}/${ZOOM_DEB}"
    wget "https://zoom.us/client/latest/${ZOOM_DEB}" -O "${ZOOM_DEB_PATH}"
    DESKTOP_PACKAGES+=("${ZOOM_DEB_PATH}")
  fi
  # Install debug symbols for these packages.
  # These are installed already here before any crashes occur to ensure that if a crash occurs,
  # the debug symbols are immediately available for debugging.
  DEBUGGABLE_PACKAGES=(
    "kinit" "kscreen" "kwin-wayland"
    "libkwin6"
    "libqt6core6t64" "libqt6dbus6" "libqt6qml6" "libqt6quick6"
    # "libsystemd0" "libtbb12" "libxcb-randr0"
  )
  DEBUG_PACKAGES=()
  for PKG in "${DEBUGGABLE_PACKAGES[@]}"; do
    if grep -q "^${PKG}$" <<< "${INSTALLED}"; then
      DEBUG_PACKAGES+=("${PKG}-dbgsym")
    fi
  done
  DESKTOP_PACKAGES+=("${DEBUG_PACKAGES[@]}")
else
  DESKTOP_PACKAGES=()
fi

# If running on physical hardware
if ! grep -q "hypervisor" /proc/cpuinfo; then
  PHYSICAL_PACKAGES=(
    "bluetooth" "boinc-client-opencl" "clinfo" "clpeak" "exfatprogs" "gdisk"
    "lm-sensors" "pocl-opencl-icd" "powertop" "s-tui" "stress" "usbtop"
  )
  if [ "${IS_DESKTOP}" = true ]; then
    PHYSICAL_PACKAGES+=(
      "boinc" "cutecom" "gnome-disk-utility" "gparted" "obs-studio" "pipewire-audio" "rpi-imager" "solaar" "virt-viewer"
      )
    # If running on a laptop
    if [ "${CHASSIS}" = "laptop" ]; then
      PHYSICAL_PACKAGES+=("gnome-network-displays" "touchegg")
    fi
  fi
  # If running on a laptop
  if [ "${CHASSIS}" = "laptop" ]; then
    PHYSICAL_PACKAGES+=("tlp")
  fi
else
  PHYSICAL_PACKAGES=()
fi

DRIVER_PACKAGES=()
# If the system has an Intel CPU
if grep -q "Intel" /proc/cpuinfo; then
  DRIVER_PACKAGES+=("intel-gpu-tools" "intel-media-va-driver" "intel-microcode" "intel-opencl-icd")
fi

# If the system has an Nvidia GPU
if command -v nvidia-smi &> /dev/null; then
  DRIVER_PACKAGES+=("boinc-client-nvidia-cuda")
fi

APT_PACKAGES=(
  "${BASE_PACKAGES[@]}" "${DEV_PACKAGES[@]}" "${DOCKER_PACKAGES[@]}" "${FUN_PACKAGES[@]}"
  "${GUI_PACKAGES[@]}" "${PYTHON_PACKAGES[@]}" "${UTILS_PACKAGES[@]}"
  "${DESKTOP_PACKAGES[@]}" "${PHYSICAL_PACKAGES[@]}" "${DRIVER_PACKAGES[@]}"
)
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
    app.eduroam.geteduroam \
    cc.arduino.IDE2 \
    com.discordapp.Discord \
    com.github.IsmaelMartinez.teams_for_linux \
    com.github.tchx84.Flatseal \
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
    org.jellyfin.JellyfinDesktop \
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
