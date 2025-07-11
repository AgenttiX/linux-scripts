#!/usr/bin/env bash
set -e
# LibreNMS client installation

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Plase give the LibreNMS server IP as the only parameter."
  exit 1
fi

apt update
if ! command -v wget &> /dev/null; then
    echo "Wget was not found. Installing it now."
    apt install wget -y
fi

if ! [ -f /etc/snmp/snmpd.conf ]; then
    echo "SNMP installation was not found. Installing it now."
    apt install snmpd -y
fi

if command -v ufw &> /dev/null; then
  echo "Creating firewall rule for SNMP"
  ufw allow from "$1" to any port snmp comment "LibreNMS SNMP"
  echo "Creating firewall rule for check_mk"
  ufw allow from "$1" to any port 6556 comment "LibreNMS check_mk"
else
  echo "Could not create firewall rules, as ufw was not found."
fi

# check_mk agent
# https://docs.librenms.org/Extensions/Agent-Setup/
echo "Downloading check_mk agent"
if [ -d /opt/librenms-agent ]; then
    echo "LibreNMS agent appears to be already downloaded. If you have run this script previously, check afterwards that there are no duplicate lines in /etc/snmp/snmpd.conf."
    cd /opt/librenms-agent
    git pull
else
    cd /opt/
    git clone https://github.com/librenms/librenms-agent.git
    cd /opt/librenms-agent
fi
echo "Installing check_mk agent"
cp check_mk_agent /usr/bin/check_mk_agent
chown root:root /usr/bin/check_mk_agent
chmod 755 /usr/bin/check_mk_agent
cp check_mk@.service check_mk.socket /etc/systemd/system/
mkdir -p /usr/lib/check_mk_agent/plugins /usr/lib/check_mk_agent/local

# dmi
echo "Installing check_mk dmi"
cp /opt/librenms-agent/agent-local/dmi /usr/lib/check_mk_agent/local/
chown root:root /usr/lib/check_mk_agent/local/dmi
chmod 755 /usr/lib/check_mk_agent/local/dmi

# dpkg
echo "Installing check_mk dpkg"
cp /opt/librenms-agent/agent-local/dpkg /usr/lib/check_mk_agent/local/
chown root:root /usr/lib/check_mk_agent/local/dpkg
chmod 755 /usr/lib/check_mk_agent/local/dpkg

echo "Enabling check_mk service"
systemctl enable check_mk.socket
systemctl start check_mk.socket


# SNMP extend
echo "Installing SNMP extensions"

# Entropy
echo "Installing entropy support"
wget https://raw.githubusercontent.com/librenms/librenms-agent/master/snmp/entropy.sh -O /etc/snmp/entropy.sh
chown root:root /etc/snmp/entropy.sh
chmod 755 /etc/snmp/entropy.sh
echo "extend entropy /etc/snmp/entropy.sh" >> /etc/snmp/snmpd.conf

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
if [ -f /proc/device-tree/model ] && [[ $(cat /proc/device-tree/model) != Raspberry* ]]; then
    echo "Raspberry pi detected. Installing support."
    wget https://raw.githubusercontent.com/librenms/librenms-agent/master/snmp/raspberry.sh -O /etc/snmp/raspberry.sh
    chown root:root /etc/snmp/raspberry.sh
    chmod 755 /etc/snmp/raspberry.sh
    echo "extend raspberry sudo /etc/snmp/raspberry.sh" >> /etc/snmp/snmpd.conf
    echo "NOTE! Run visudo and add the following:"
    echo "Debian-snmp ALL=(ALL) NOPASSWD: /etc/snmp/raspberry.sh, /usr/bin/vcgencmd"
fi

# SMART
echo "Do you want to install SMART support?"
select yn in "Yes" "No"; do
    case $yn in
        Yes)
            INSTALL_SMART=1
            break
            ;;
        No)
            INSTALL_SMART=0
            break
            ;;
        *)
            echo "Please use a number for the selection"
            ;;
    esac
done
if [ $INSTALL_SMART -eq 1 ]; then
    apt install -y smartmontools
    wget https://github.com/librenms/librenms-agent/raw/master/snmp/smart -O /etc/snmp/smart
    chown root:root /etc/snmp/smart
    chmod 755 /etc/snmp/smart
    # The default config is not useful
    # cp ./smart.config /etc/snmp/smart.config
    /etc/snmp/smart -g > /etc/snmp/smart.config
    echo "extend smart /etc/snmp/smart" >> /etc/snmp/snmpd.conf
    echo "NOTE! Run visudo and add the following:"
    echo "Debian-snmp ALL=(ALL) NOPASSWD: /etc/snmp/smart, /usr/bin/env smartctl"
    echo "Also run \"sudo crontab -e\" and add the following:"
    echo "*/3 * * * * /etc/snmp/smart -u"
fi

echo "Starting snmpd to see that it works."
systemctl restart snmpd
systemctl status snmpd
echo "Stopping snmpd to allow configuring."
systemctl stop snmpd
systemctl status snmpd
# https://stackoverflow.com/questions/13538307/net-snmp-reloading-working-in-strange-way
echo "Do not edit the snmpd config while it's running! You may run into bizarre issues with SNMPv3 user settings not being applied."
echo "SNMPv3 SHA-512 and AES-256 have been verified to work with LibreNMS."
