#!/usr/bin/env bash
set -eu

# This script is for flashing the partitions manually using images extracted
# from an official OxygenOS zip, which you can get here:
# https://www.oneplus.com/global/support/softwareupgrade

# https://wiki.lineageos.org/devices/lemonadep/fw_update/

# Enable factory reset if doing a clean install!
FACTORY_RESET=true
FLASH_FIRMWARE=false

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root to ensure that fastboot works correctly."
  exit 1
fi


# https://stackoverflow.com/a/246128/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
FASTBOOT="${SCRIPT_DIR}/platform-tools/fastboot"
CWD="${PWD}"

TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/flash_oneplus9pro_${TIMESTAMP}.txt"

echo "Starting OnePlus 9 Pro fastboot flash script." |& tee "${LOG_PATH}"

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
  # This device does not seem to support "fastboot -w", but instead results in
  # "remote: 'unknown command'" and "fastboot: error: Command failed", so these have to be used instead.
  # $FASTBOOT erase data |& tee -a "${LOG_PATH}"
  # $FASTBOOT erase cache |& tee -a "${LOG_PATH}"
  echo "Error: factory resetting does not seem to be supported by this device."
  echo "You have to do the factory reset in the recovery."
fi

if [ "${FLASH_FIRMWARE}" = true ]; then
  echo "Flashing OTA images to all slots" |& tee -a "${LOG_PATH}"

  # This feature is manually disabled,
  # since the latest OTA firmware is much newer than the one available on the OnePlus website.
  echo "Warning! This feature is dangerous and therefore disabled."
  echo "Run the script again with the OTA firmware flashing disabled."
  exit 1

  $FASTBOOT flash --slot=all abl "${OTA_DIR}/abl.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all aop "${OTA_DIR}/aop.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all bluetooth "${OTA_DIR}/bluetooth.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all cpucp "${OTA_DIR}/cpucp.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all devcfg "${OTA_DIR}/devcfg.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all dsp "${OTA_DIR}/dsp.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all engineering_cdt "${OTA_DIR}/engineering_cdt.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all featenabler "${OTA_DIR}/featenabler.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all hyp "${OTA_DIR}/hyp.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all imagefv "${OTA_DIR}/imagefv.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all keymaster "${OTA_DIR}/keymaster.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all modem "${OTA_DIR}/modem.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all multiimgoem "${OTA_DIR}/multiimgoem.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all oplus_sec "${OTA_DIR}/oplus_sec.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all oplusstanvbk "${OTA_DIR}/oplusstanvbk.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all qupfw "${OTA_DIR}/qupfw.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all qweslicstore "${OTA_DIR}/qweslicstore.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all shrm "${OTA_DIR}/shrm.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all splash "${OTA_DIR}/splash.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all tz "${OTA_DIR}/tz.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all uefisecapp "${OTA_DIR}/uefisecapp.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all xbl_config "${OTA_DIR}/xbl_config.img" |& tee -a "${LOG_PATH}"
  $FASTBOOT flash --slot=all xbl "${OTA_DIR}/xbl.img" |& tee -a "${LOG_PATH}"
fi

# https://source.android.com/docs/core/ota/dynamic_partitions/implement
echo "Wiping the super partition using the LineageOS template"
$FASTBOOT wipe-super "${LINEAGEOS_DIR}/super_empty.img" |& tee -a "${LOG_PATH}"

echo "Flashing LineageOS images to all slots"
$FASTBOOT flash dtbo "${LINEAGEOS_DIR}/dtbo.img" |& tee -a "${LOG_PATH}"
$FASTBOOT flash vbmeta "${LINEAGEOS_DIR}/vbmeta.img" |& tee -a "${LOG_PATH}"
$FASTBOOT flash vendor_boot "${LINEAGEOS_DIR}/vendor_boot.img" |& tee -a "${LOG_PATH}"

# Rebooting back to the bootloader just in case to ensure that all changes have been applied
echo "Rebooting the device to the bootloader" |& tee -a "${LOG_PATH}"
$FASTBOOT reboot bootloader |& tee -a "${LOG_PATH}"

echo "Flashing the LineageOS boot image."
$FASTBOOT flash boot "${LINEAGEOS_DIR}/boot.img" |& tee -a "${LOG_PATH}"

echo "Booting the device to TWRP" |& tee -a "${LOG_PATH}"
$FASTBOOT boot "${TWRP_IMG}" |& tee -a "${LOG_PATH}"

echo "Flashing script ready." |& tee -a "${LOG_PATH}"
