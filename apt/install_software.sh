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

apt-get update
apt-get install \
  apt-transport-https autojump bleachbit build-essential ca-certificates cifs-utils clamtk cmake curl cutecom \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
  filelight filezilla gfortran gimp git git-gui gparted htop inkscape kde-config-flatpak keepassxc ktorrent \
  libreoffice libreoffice-help-fi lm-sensors mumble network-manager-openvpn openssh-server optipng powertop \
  python3-dev python3-venv \
  s-tui signal-desktop stress synaptic texlive-full texmaker ufw vlc wget wireguard yt-dlp zsh

if [ "$(hostnamectl chassis)" = "laptop" ]; then
  apt-get install tlp touchegg
fi

snap install pycharm-professional --classic
snap install telegram-desktop

flatpak install flathub \
  com.discordapp.Discord \
  com.github.iwalton3.jellyfin-media-player \
  com.github.xournalpp.xournalpp \
  com.mastermindzh.tidal-hifi \
  com.mattermost.Desktop \
  com.obsproject.Studio \
  com.plexamp.Plexamp \
  com.skype.Client \
  com.slack.Slack \
  com.spotify.Client \
  com.vscodium.codium \
  md.obsidian.Obsidian \
  org.blender.Blender \
  org.chromium.Chromium \
  org.ferdium.Ferdium \
  org.zotero.Zotero \
  tv.plex.PlexDesktop
