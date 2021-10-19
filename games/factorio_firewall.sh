#!/bin/bash -e

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

ufw allow 34197/udp comment Factorio
ufw allow 27015/tcp comment Factorio
