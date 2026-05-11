#!/usr/bin/env bash
set -euo pipefail
# Enable automatic WireGuard connection when not at the LAN.

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi
if [ $# -ne 2 ]; then
  echo "Arguments: WireGuard connection name, LAN gateway IP"
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WG_NAME="$1"
LAN_GW_IP="$2"

if [ ! -f "/etc/wireguard/${WG_NAME}.conf" ]; then
  echo "WireGuard config not found at /etc/wireguard/${WG_NAME}.conf"
  exit 1
fi
if nmcli connection show "${WG_NAME}" &>/dev/null; then
  echo "The WireGuard nmcli config already exists. Deleting."
  nmcli connection delete "${WG_NAME}"
fi

sed "s/WG_CON_NAME/${WG_NAME}/g; s/LAN_GW_IP/${LAN_GW_IP}/g" \
  "${SCRIPT_DIR}/99-wireguard-autoconnect.sh" > "/etc/NetworkManager/dispatcher.d/99-wireguard-autoconnect.sh"
chmod 755 /etc/NetworkManager/dispatcher.d/99-wireguard-autoconnect.sh

nmcli connection import type wireguard file "/etc/wireguard/${WG_NAME}.conf"
nmcli connection modify "${WG_NAME}" connection.id "${WG_NAME}" ipv4.dns-priority -100 connection.autoconnect no
echo "nmcli connection:"
nmcli --terse connection show "${WG_NAME}"
echo "resolvectl status:"
resolvectl status --no-pager

echo "WireGuard VPN configured."
