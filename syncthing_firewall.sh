#!/bin/bash -e

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

ufw allow 22000/tcp comment "Syncthing"
ufw allow 21027/udp comment "Syncthing Discovery"

while true; do
  read -p "Do you want to allow remote GUI access? (y/n) " yn

  case $yn in
    [yY] ) echo "Enabling remote GUI access"
      ufw allow 8384 comment "Syncthing GUI"
      break;;
    [nN] ) echo "Skipping remote GUI access"
      exit;;
    * ) echo "Invalid response";;
  esac
done
