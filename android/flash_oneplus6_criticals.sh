#!/usr/bin/bash -e

# This script is for flashing the additional critical partitions with TWRP.
# This should not be done, unless you want to completely wipe
# the device from any possible malware, or have recently re-flashed the device with MSM.

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root to ensure that adb works correctly."
  exit 1
fi

# https://stackoverflow.com/a/246128/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ADB="$SCRIPT_DIR/platform-tools/adb"

# https://forum.xda-developers.com/t/rom-stock-fastboot-op6-stock-fastboot-roms-for-oneplus-6.3796665/
$ADB push abl.img /sdcard/abl.img
$ADB shell dd if=/sdcard/abl.img of=/dev/block/bootdevice/by-name/abl_a
$ADB shell dd if=/sdcard/abl.img of=/dev/block/bootdevice/by-name/abl_b
$ADB push cmnlib.img /sdcard/cmnlib.img
$ADB shell dd if=/sdcard/cmnlib.img of=/dev/block/bootdevice/by-name/cmnlib_a
$ADB shell dd if=/sdcard/cmnlib.img of=/dev/block/bootdevice/by-name/cmnlib_b
$ADB push cmnlib64.img /sdcard/cmnlib64.img
$ADB shell dd if=/sdcard/cmnlib64.img of=/dev/block/bootdevice/by-name/cmnlib64_a
$ADB shell dd if=/sdcard/cmnlib64.img of=/dev/block/bootdevice/by-name/cmnlib64_b
$ADB push devcfg.img /sdcard/devcfg.img
$ADB shell dd if=/sdcard/devcfg.img of=/dev/block/bootdevice/by-name/devcfg_a
$ADB shell dd if=/sdcard/devcfg.img of=/dev/block/bootdevice/by-name/devcfg_b
$ADB push hyp.img /sdcard/hyp.img
$ADB shell dd if=/sdcard/hyp.img of=/dev/block/bootdevice/by-name/hyp_a
$ADB shell dd if=/sdcard/hyp.img of=/dev/block/bootdevice/by-name/hyp_b
$ADB push keymaster.img /sdcard/keymaster.img
$ADB shell dd if=/sdcard/keymaster.img of=/dev/block/bootdevice/by-name/keymaster_a
$ADB shell dd if=/sdcard/keymaster.img of=/dev/block/bootdevice/by-name/keymaster_b
$ADB push xbl.img /sdcard/xbl.img
$ADB shell dd if=/sdcard/xbl.img of=/dev/block/bootdevice/by-name/xbl_a
$ADB shell dd if=/sdcard/xbl.img of=/dev/block/bootdevice/by-name/xbl_b
$ADB push xbl_config.img /sdcard/xbl_config.img
$ADB shell dd if=/sdcard/xbl_config.img of=/dev/block/bootdevice/by-name/xbl_config_a
$ADB shell dd if=/sdcard/xbl_config.img of=/dev/block/bootdevice/by-name/xbl_config_b
