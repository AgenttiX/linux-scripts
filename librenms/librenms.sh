#!/bin/bash -e
# LibreNMS installation

# check_mk agent
# https://docs.librenms.org/Extensions/Agent-Setup/
ufw allow 6556 comment "LibreNMS check_mk"
cd /opt/
git clone https://github.com/librenms/librenms-agent.git
cd /opt/librenms-agent
cp check_mk_agent /usr/bin/check_mk_agent
chown root:root /usr/bin/check_mk_agent
chmod 755 /usr/bin/check_mk_agent
cp check_mk@.service check_mk.socket /etc/systemd/system/
mkdir -p /usr/lib/check_mk_agent/plugins /usr/lib/check_mk_agent/local

# dmi
cp /opt/librenms-agent/agent-local/dmi /usr/lib/check_mk_agent/local/
chown root:root /usr/lib/check_mk_agent/local/dmi
chmod 755 /usr/lib/check_mk_agent/local/dmi

# dpkg
cp /opt/librenms-agent/agent-local/dpkg /usr/lib/check_mk_agent/local/
chown root:root /usr/lib/check_mk_agent/local/dpkg
chmod 755 /usr/lib/check_mk_agent/local/dpkg

systemctl enable check_mk.socket
systemctl start check_mk.socket


# SNMP extend

# Nvidia
if command -v nvidia-smi &> /dev/null; then
    echo "Nvidia driver found. Installing Nvidia GPU support."
    wget https://github.com/librenms/librenms-agent/raw/master/snmp/nvidia -O /etc/snmp/nvidia
    chown root:root /etc/snmp/nvidia
    chmod 755 /etc/snmp/nvidia
    echo "extend nvidia /etc/snmp/nvidia" >> /etc/snmp/snmpd.conf
fi

# OS Updates
echo "Installing OS update support"
wget https://raw.githubusercontent.com/librenms/librenms-agent/master/snmp/osupdate -O /etc/snmp/osupdate
chown root:root /etc/snmp/osupdate
chmod 755 /etc/snmp/osupdate
echo "extend osupdate /etc/snmp/osupdate" >> /etc/snmp/snmpd.conf

# Raspberry Pi
if [ -f /proc/device-tree/model ] && [[ $(cat /proc/device-tree/model) != Raspberry* ]]
    echo "Raspberry pi detected. Installing support."
    wget https://raw.githubusercontent.com/librenms/librenms-agent/master/snmp/raspberry.sh -O /etc/snmp/raspberry.sh
    chown root:root /etc/snmp/raspberry.sh
    chmod 755 /etc/snmp/raspberry.sh
    echo "extend raspberry sudo /etc/snmp/raspberry.sh" >> /etc/snmp/snmpd.conf
    echo "NOTE! Run visudo and add the following:"
    echo "Debian-snmp ALL=(ALL) NOPASSWD: /etc/snmp/raspberry.sh, /usr/bin/vcgencmd"
fi

# SMART
# echo "Installing SMART support"
# apt-get install -y smartmontools
# wget https://github.com/librenms/librenms-agent/raw/master/snmp/smart -O /etc/snmp/smart
# chown root:root /etc/snmp/smart
# chmod 755 /etc/snmp/smart
# echo "extend smart /etc/snmp/smart" >> /etc/snmp/snmpd.conf
# echo "NOTE! Run visudo and add the following:"
# echo "snmp ALL=(ALL) NOPASSWD: /etc/snmp/smart, /usr/bin/env smartctl"


