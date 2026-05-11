#!/usr/bin/env bash
set -euo pipefail
# Auto-connect WireGuard only when not on the home LAN

IFACE="$1"
EVENT="$2"

WG_CON="WG_CON_NAME"
LAN_GW="LAN_GW_IP"

# Ignore WireGuard interface events to prevent loops
[[ "${IFACE}" == "${WG_CON}" ]] && exit 0

is_on_lan() {
    ping -c 2 -W 2 -q "${LAN_GW}" &>/dev/null
}

case "${EVENT}" in
    up|connectivity-change)
        if is_on_lan; then
            nmcli --fields GENERAL.STATE connection show "${WG_CON}" 2>/dev/null \
                | grep -q activated && nmcli connection down "${WG_CON}"
        else
            # Only bring up if we have actual connectivity
            if nmcli -t -f CONNECTIVITY general | grep -qE "full|limited"; then
                nmcli connection up "${WG_CON}" 2>/dev/null
            fi
        fi
        ;;
    down)
        nmcli connection down "${WG_CON}" 2>/dev/null
        ;;
esac
