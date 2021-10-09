#!/usr/bin/sh -e
# https://github.com/PCSX2/pcsx2/wiki/Installing-on-Linux
# https://launchpad.net/%7Epcsx2-team/+archive/ubuntu/pcsx2-daily

sudo dpkg --add-architecture i386
sudo add-apt-repository ppa:pcsx2-team/pcsx2-daily
sudo apt-get update
sudo apt-get install pcsx2
