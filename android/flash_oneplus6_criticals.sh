#!/usr/bin/env bash
set -e

# This script is for flashing the additional critical partitions with TWRP.
# This should not be done, unless you want to completely wipe
# the device from any possible malware, or have recently re-flashed the device with MSM.

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root to ensure that adb works correctly."
  exit 1
fi

# https://stackoverflow.com/a/246128/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
ADB="$SCRIPT_DIR/platform-tools/adb"

TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/flash_oneplus6_criticals_${TIMESTAMP}.txt"

echo "Starting OnePlus 6 critical partition flasher script." |& tee "${LOG_PATH}"

# https://forum.xda-developers.com/t/rom-stock-fastboot-op6-stock-fastboot-roms-for-oneplus-6.3796665/
$ADB push abl.img /sdcard/abl.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/abl.img of=/dev/block/bootdevice/by-name/abl_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/abl.img of=/dev/block/bootdevice/by-name/abl_b |& tee -a "${LOG_PATH}"
$ADB push cmnlib.img /sdcard/cmnlib.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/cmnlib.img of=/dev/block/bootdevice/by-name/cmnlib_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/cmnlib.img of=/dev/block/bootdevice/by-name/cmnlib_b |& tee -a "${LOG_PATH}"
$ADB push cmnlib64.img /sdcard/cmnlib64.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/cmnlib64.img of=/dev/block/bootdevice/by-name/cmnlib64_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/cmnlib64.img of=/dev/block/bootdevice/by-name/cmnlib64_b |& tee -a "${LOG_PATH}"
$ADB push devcfg.img /sdcard/devcfg.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/devcfg.img of=/dev/block/bootdevice/by-name/devcfg_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/devcfg.img of=/dev/block/bootdevice/by-name/devcfg_b |& tee -a "${LOG_PATH}"
$ADB push hyp.img /sdcard/hyp.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/hyp.img of=/dev/block/bootdevice/by-name/hyp_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/hyp.img of=/dev/block/bootdevice/by-name/hyp_b |& tee -a "${LOG_PATH}"
$ADB push keymaster.img /sdcard/keymaster.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/keymaster.img of=/dev/block/bootdevice/by-name/keymaster_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/keymaster.img of=/dev/block/bootdevice/by-name/keymaster_b |& tee -a "${LOG_PATH}"
$ADB push xbl.img /sdcard/xbl.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/xbl.img of=/dev/block/bootdevice/by-name/xbl_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/xbl.img of=/dev/block/bootdevice/by-name/xbl_b |& tee -a "${LOG_PATH}"
$ADB push xbl_config.img /sdcard/xbl_config.img |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/xbl_config.img of=/dev/block/bootdevice/by-name/xbl_config_a |& tee -a "${LOG_PATH}"
$ADB shell dd if=/sdcard/xbl_config.img of=/dev/block/bootdevice/by-name/xbl_config_b |& tee -a "${LOG_PATH}"

echo "OnePlus 6 critical partition flasher script ready." |& tee -a "${LOG_PATH}"
