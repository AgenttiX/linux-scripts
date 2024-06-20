#!/usr/bin/env sh
set -eu

# Ubuntu 22.04 installs Firefox as snap by default,
# and the deb package is merely a wrapper for the snap.
# To get some extensions such as KeePassXC working,
# one has to install Firefox from the Mozilla PPA.

# Source:
# https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04

echo "Creating a backup of the existing Firefox profile"
cp -r "${HOME}/snap/firefox" "${HOME}/snap/firefox-backup-$(date +%s)"

echo "Removing the Firefox snap"
sudo snap remove firefox
sudo apt-get remove firefox

echo "Adding the Mozilla PPA"
sudo add-apt-repository ppa:mozillateam/ppa

echo "Altering Firefox package priority to prefer the PPA version"
echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' | sudo tee /etc/apt/preferences.d/mozilla-firefox

echo "Configuring unattended upgrades"
# shellcheck disable=SC2016
echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' | sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-firefox

echo "Installing Firefox from the PPA"
sudo apt install firefox
