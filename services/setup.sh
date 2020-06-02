#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

cp ./iperf.service /usr/systemd/system/iperf.service
cp ./iperf3.service /usr/systemd/system/iperf3.service
chmod 644 /etc/systemd/system/iperf.service
chmod 644 /etc/systemd/system/iperf3.service
