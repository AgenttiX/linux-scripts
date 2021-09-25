#!/bin/bash

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

apt-get update
apt-get install iperf iperf3
cp ./iperf.service /etc/systemd/system/iperf.service
cp ./iperf3.service /etc/systemd/system/iperf3.service
chmod 644 /etc/systemd/system/iperf.service
chmod 644 /etc/systemd/system/iperf3.service
systemctl start iperf
systemctl start iperf3
systemctl status iperf
systemctl status iperf3
