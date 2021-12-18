#!/usr/bin/sh -e
# This does not work on new Ubuntu versions due to library conflicts.
# The preferred way to install is from a snap:
# sudo snap install epsxe

sudo apt-get install libsdl-ttf2.0-0

wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5.7_amd64.deb
wget http://archive.ubuntu.com/ubuntu/pool/universe/c/curl3/libcurl3_7.58.0-2ubuntu2_amd64.deb
sudo dpkg -i sudo libssl1.0.0_1.0.2n-1ubuntu5.7_amd64.deb

# libcurl3 cannot be installed with dpkg, as it conflicts with the existing libcurl4
# sudo dpkg -i libcurl3_7.58.0-2ubuntu2_amd64.deb
dpkg -x libcurl3_7.58.0-2ubuntu2_amd64.deb ./libcurl
# mv
