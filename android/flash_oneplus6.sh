#!/usr/bin/env bash
set -e

# This script is for flashing the partitions manually using images extracted
# from an official OxygenOS zip, which you can get here:
# https://www.oneplus.com/global/support/softwareupgrade

# You can use this payload dumper to extract the files from the OTA zip:
# https://github.com/tobyxdd/android-ota-payload-extractor
# Or alternatively this:
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
FACTORY_RESET=true
FLASH_A=true
FLASH_B=true

# https://stackoverflow.com/a/246128/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
FASTBOOT="${SCRIPT_DIR}/platform-tools/fastboot"
CWD="${PWD}"

TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/flash_oneplus6_${TIMESTAMP}.txt"

echo "Starting OnePlus 6 fastboot flash script." |& tee "${LOG_PATH}"

# Directory checks

OTA_DIR="${CWD}/OTA"
if [ -d "${OTA_DIR}" ]; then
  echo "OTA directory found."
else
  echo "OTA directory was not found. Please put the img files to the subdirectory \"OTA\"."
  exit 1
fi

LINEAGEOS_DIR="${CWD}/LineageOS"
if [ -d "${LINEAGEOS_DIR}" ]; then
  echo "LineageOS directory found."
else
  echo "LineageOS directory was not found. Please put the img files and signatures to the subdirectory \"LineageOS\"."
  exit 1
fi

TWRP_DIR="${CWD}/TWRP"
if [ -d "${TWRP_DIR}" ]; then
  echo "TWRP directory found."
else
  echo "TWRP directory was not found. Please put the TWRP img file and signatures to the subdirectory \"TWRP\"."
fi

# File checks

cd "${LINEAGEOS_DIR}"
sha256sum -c "./imgs.sha256"
# "${CWD}"

cd "${TWRP_DIR}"
TWRP_PATTERN="${TWRP_DIR}/*.img"
TWRP_FILES=($TWRP_PATTERN)
TWRP_IMG="${TWRP_FILES[0]}"
sha256sum -c "${TWRP_IMG}.sha256"
wget "https://eu.dl.twrp.me/public.asc" -O "${TWRP_DIR}/public.asc"
gpg --import "${TWRP_DIR}/public.asc"
gpg --verify "${TWRP_IMG}.asc" "${TWRP_IMG}"
cd "${CWD}"

# Factory reset
if [ "${FACTORY_RESET}" = true ]; then
  echo "Factory resetting the device" |& tee -a "${LOG_PATH}"
  $FASTBOOT -w |& tee -a "${LOG_PATH}"
fi

# The partition list below is based on these instructions
# https://forum.xda-developers.com/t/rom-stock-fastboot-op6-stock-fastboot-roms-for-oneplus-6.3796665/
# https://www.droidwin.com/restore-oneplus-6-stock-via-fastboot-commands/
if [ "${FLASH_A}" = true ]; then
  echo "Flashing OTA images to slot A" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash aop_a "${OTA_DIR}/aop.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash bluetooth_a "${OTA_DIR}/bluetooth.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash boot_a "${OTA_DIR}/boot.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash dsp_a "${OTA_DIR}/dsp.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash dtbo_a "${OTA_DIR}/dtbo.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash fw_4j1ed_a "${OTA_DIR}/fw_4j1ed.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash fw_4u1ea_a "${OTA_DIR}/fw_4u1ea.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash modem_a "${OTA_DIR}/modem.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash oem_stanvbk "${OTA_DIR}/oem_stanvbk.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash qupfw_a "${OTA_DIR}/qupfw.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash storsec_a "${OTA_DIR}/storsec.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash system_a "${OTA_DIR}/system.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash vbmeta_a "${OTA_DIR}/vbmeta.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash vendor_a "${OTA_DIR}/vendor.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash LOGO_a "${OTA_DIR}/LOGO.img" |& tee -a "${LOG_PATH}"
fi
if [ "${FLASH_B}" = true ]; then
  echo "Flashing OTA images to slot B" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash aop_b "${OTA_DIR}/aop.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash bluetooth_b "${OTA_DIR}/bluetooth.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash boot_b "${OTA_DIR}/boot.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash dsp_b "${OTA_DIR}/dsp.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash dtbo_b "${OTA_DIR}/dtbo.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash fw_4j1ed_b "${OTA_DIR}/fw_4j1ed.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash fw_4u1ea_b "${OTA_DIR}/fw_4u1ea.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash modem_b "${OTA_DIR}/modem.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash qupfw_b "${OTA_DIR}/qupfw.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash storsec_b "${OTA_DIR}/storsec.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash system_b "${OTA_DIR}/system.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash vbmeta_b "${OTA_DIR}/vbmeta.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash vendor_b "${OTA_DIR}/vendor.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash LOGO_b "${OTA_DIR}/LOGO.img" |& tee -a "${LOG_PATH}"
fi

if [ "${FLASH_A}" = true ]; then
  echo "Flashing LineageOS to slot A"
  $FASTBOOT flash boot_a "${LINEAGEOS_DIR}/boot.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash dtbo_a "${LINEAGEOS_DIR}/dtbo.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash vbmeta_a "${LINEAGEOS_DIR}/vbmeta.img" |& tee -a "${LOG_PATH}"
fi
if [ "${FLASH_B}" = true ]; then
  echo "Flashing LineageOS to slot B"
  $FASTBOOT flash boot_b "${LINEAGEOS_DIR}/boot.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash dtbo_b "${LINEAGEOS_DIR}/dtbo.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash vbmeta_b "${LINEAGEOS_DIR}/vbmeta.img" |& tee -a "${LOG_PATH}"
fi

# This would overwrite sensor calibrations and some other unique data
# $FASTBOOT flash persist persist.img |& tee -a "${LOG_PATH}"

# Rebooting back to the bootloader just in case to ensure that all changes have been applied
echo "Rebooting the device to the bootloader" |& tee -a "${LOG_PATH}"
$FASTBOOT reboot bootloader |& tee -a "${LOG_PATH}"

echo "Booting the device to TWRP" |& tee -a "${LOG_PATH}"
$FASTBOOT boot "${TWRP_IMG}" |& tee -a "${LOG_PATH}"

echo "Flashing script ready." |& tee -a "${LOG_PATH}"
