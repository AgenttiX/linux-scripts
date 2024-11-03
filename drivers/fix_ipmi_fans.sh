#!/usr/bin/env bash
set -eu

# Fix for fans ramping up and down on Supermicro server motherboards.
# https://www.truenas.com/community/threads/fans-ramping-up-and-down-and-fan-mode-option-not-visible-in-ipmi-supermicro-x9scm-f.70826/
# https://www.truenas.com/community/resources/how-to-change-ipmi-sensor-thresholds-using-ipmitool.35/

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SENSORS=$(ipmitool sensor list all)
FANS=$(grep '^FAN' <<< "${SENSORS}")

while IFS= read -r LINE; do
  NAME="${LINE%% *}"
  echo "Configuring ${NAME}"
  # The three numbers are lnr, lcr, lnc
  # nr = non-recoverable
  # cr = critical
  # nc = non-critical
  # My home server has Noctua NF-A12x25 PWM fans, which are rated for 450 - 2000 RPM.
  # https://www.amazon.de/-/en/gp/product/B07C5VG64V/
  # And Arctic Freezer 4U SP3, which is rated for 400 - 2300 RPM.
  # https://www.arctic.de/en/Freezer-4U-SP3/ACFRE00081A
  # These values will be rounded by the motherboard to 140, 140 and ???.
  ipmitool sensor thresh "${NAME}" lower 100 200 450
  # ipmitool sensor thresh "${NAME}" upper
done <<< "${FANS}"
