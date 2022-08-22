#!/usr/bin/env bash
set -e

if [ -f /var/run/reboot-required ]; then
        echo "$(date) Rebooting, as system restart is required by: $(cat /var/run/reboot-required.pkgs)"
        reboot now
fi
