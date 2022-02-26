#!/usr/bin/bash -e

# This script is for flashing the partitions manually using images extracted
# from an official OxygenOS zip, which you can get here:
# https://www.oneplus.com/global/support/softwareupgrade
# Use this payload dumper to extract the files from the OTA zip:
# https://github.com/vm03/payload_dumper
# It supports running directly from a pre-built Docker container.

# After you have run this script, you may want to run the additional
# script for flashing the critical partitions.

# If you get an error saying that the boot images are bigger than the corresponding
# partitions, you should first OTA update the device with official firmware,
# or flash it with MSM directly to a relatively new OxygenOS.
# (OxygenOS 10 worked, but 8 did not.)
# You can find some MSM images here:
# https://www.thecustomdroid.com/oneplus-6-6t-unbrick-guide/

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root to ensure that fastboot works correctly."
  exit 1
fi

# Enable factory reset if doing a clean install!
FACTORY_RESET=false
FLASH_A=true
FLASH_B=true

# https://stackoverflow.com/a/246128/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FASTBOOT="$SCRIPT_DIR/platform-tools/fastboot"

# Factory reset
if [ "${FACTORY_RESET}" = true ]; then
  echo "Factory resetting the device"
  $FASTBOOT -w
fi

# The partition list below is based on these instructions
# https://forum.xda-developers.com/t/rom-stock-fastboot-op6-stock-fastboot-roms-for-oneplus-6.3796665/
# https://www.droidwin.com/restore-oneplus-6-stock-via-fastboot-commands/
if [ "${FLASH_A}" = true ]; then
  echo "Flashing slot A"
  $FASTBOOT flash aop_a aop.img
  $FASTBOOT flash bluetooth_a bluetooth.img
  $FASTBOOT flash boot_a boot.img
  $FASTBOOT flash dsp_a dsp.img
  $FASTBOOT flash dtbo_a dtbo.img
  $FASTBOOT flash fw_4j1ed_a fw_4j1ed.img
  $FASTBOOT flash fw_4u1ea_a fw_4u1ea.img
  $FASTBOOT flash modem_a modem.img
  $FASTBOOT flash oem_stanvbk oem_stanvbk.img
  $FASTBOOT flash qupfw_a qupfw.img
  $FASTBOOT flash storsec_a storsec.img
  $FASTBOOT flash system_a system.img
  $FASTBOOT flash vbmeta_a vbmeta.img
  $FASTBOOT flash vendor_a vendor.img
  $FASTBOOT flash LOGO_a LOGO.img
fi
if [ "${FLASH_B}" = true ]; then
  echo "Flashing slot B"
  $FASTBOOT flash aop_b aop.img
  $FASTBOOT flash bluetooth_b bluetooth.img
  $FASTBOOT flash boot_b boot.img
  $FASTBOOT flash dsp_b dsp.img
  $FASTBOOT flash dtbo_b dtbo.img
  $FASTBOOT flash fw_4j1ed_b fw_4j1ed.img
  $FASTBOOT flash fw_4u1ea_b fw_4u1ea.img
  $FASTBOOT flash modem_b modem.img
  $FASTBOOT flash qupfw_b qupfw.img
  $FASTBOOT flash storsec_b storsec.img
  $FASTBOOT flash system_b system.img
  $FASTBOOT flash vbmeta_b vbmeta.img
  $FASTBOOT flash vendor_b vendor.img
  $FASTBOOT flash LOGO_b LOGO.img
fi

# This would overwrite sensor calibrations and some other unique data
# $FASTBOOT flash persist persist.img

# Rebooting back to the bootloader just in case to ensure that all changes have been applied
echo "Rebooting the device to the bootloader"
$FASTBOOT reboot bootloader
