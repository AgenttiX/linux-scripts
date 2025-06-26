#!/usr/bin/env bash
set -eu

# Before running this script on Kubuntu, enable Flatpak backend here:
# https://flatpak.org/setup/Kubuntu

# These have to be installed manually:
# Google Chrome, Steam, TeamViewer

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

echo "Installing apt packages."
apt-get update
APT_PACKAGES=(
  "apt-transport-https" "autojump" "bleachbit" "bluetooth" "build-essential" "ca-certificates"
  "cifs-utils" "clamtk" "cloc" "cmake" "curl" "cutecom"
  "docker-ce" "docker-ce-cli" "containerd.io" "docker-buildx-plugin" "docker-compose-plugin"
  "exfatprogs" "filelight" "filezilla" "freerdp2-wayland"
  "gcc-multilib" "g++-multilib" "gdisk" "gfortran" "gimp" "git" "git-delta" "git-gui" "gparted" "htop"
  "inkscape" "kde-config-flatpak" "keepassxc" "ktorrent" "libenchant-2-voikko"
  "libreoffice" "libreoffice-help-fi" "libreoffice-voikko"
  "links" "lm-sensors" "mumble" "network-manager-openvpn" "openssh-server" "optipng"
  "pipewire-audio" "powertop"
  "python3-dev" "python3-venv"
  "remmina" "remmina-plugin-kwallet" "s-tui" "screen" "signal-desktop" "stress" "synaptic" "tmispell-voikko"
  "texlive-full" "texmaker" "tikzit" "ufw" "usbtop" "vlc" "wget" "wireguard" "xindy" "yt-dlp" "zsh"
)
if [ "$(hostnamectl chassis)" = "laptop" ]; then
  APT_PACKAGES+=("tlp" "touchegg")
fi
apt-get install "${PACKAGES[@]}"

echo "Installing Snap packages."
snap install pycharm-professional --classic
snap install telegram-desktop

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
  org.blender.Blender \
  org.chromium.Chromium \
  org.ferdium.Ferdium \
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

echo "Software installed."
