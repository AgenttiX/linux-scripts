#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  return 1
fi

DISK=$1
if ! [ -e "${DISK}" ]; then
  echo "Please supply a valid disk as the first argument."
  return 1
fi
if [ $# -gt 2 ]; then
  echo "Too many arguments."
  return 1
fi

echo "If you encounter any issues, check your UEFI/BIOS settings and disable the \"Block SID Authentication\" setting."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="$(dirname "${SCRIPT_DIR}")/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="${LOG_DIR}/erase_nvme_ssd_${TIMESTAMP}.txt"
mkdir -p "${LOG_DIR}"

apt update
apt install nvme-cli smartmontools tar wget

nvme --version
nvme list

# https://stackoverflow.com/a/1885534/
read -p "Are you sure this is the right disk? " -n 1 -r
echo  # newline
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    return 1
fi

ID_CTRL=$(nvme id-ctrl "${DISK}" --human-readable)
echo "${ID_CTRL}" &>> "${LOG_FILE}"

if [ $# -eq 1 ]; then
  nvme sanitize-log "${DISK}"
  SANITIZE=$(nvme sanitize "${DISK}" --sanact=start-block-erase)
  if ! (grep "Access Denied" <<< "${SANITIZE}") then
    nvme sanitize-log "${DISK}"
    echo "Sanitizing started."
    return 0
  fi

  echo "Could not sanitize the drive. Suspending the computer to fix this. "
  echo "Start the computer again to continue."
  sleep 2
  # https://pcpartpicker.com/forums/topic/460000-an-ssd-that-cant-be-formatted-leads-to-solving-an-8-year-old-bug
  # https://superuser.com/a/1574593
  systemctl suspend
  read -p "Did the computer suspend? " -n 1 -r
  echo  # newline
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      return 1
  fi

  # Attempt sanitize again
  SANITIZE=$(nvme sanitize "${DISK}" --sanact=start-block-erase)
  if ! (grep "Access Denied" <<< "${SANITIZE}"); then
    nvme sanitize-log "${DISK}"
    echo "Sanitizing started."
    return 0
  fi
  echo "Suspending did not unlock the disk. Unlocking the disk requires sedutil."
else
  echo "PSID was provided. Using sedutil to erase the drive."
fi

if (grep "SecureBoot enabled" <<< "$(mokutil --sb-state)"); then
  echo "Secure Boot seems to be enabled. You need to disable it to use sedutil."
  return 1
fi

# https://github.com/Drive-Trust-Alliance/sedutil/wiki/Executable-Distributions
SEDUTIL="${SCRIPT_DIR}/sedutil/Release_x86_64/sedutil-cli"
if [ ! -f "${SEDUTIL}" ]; then
  wget "https://github.com/Drive-Trust-Alliance/exec/blob/master/sedutil_LINUX.tgz?raw=true" -O "${SCRIPT_DIR}/sedutil_LINUX.tgz"
  tar -xvzf "${SCRIPT_DIR}/sedutil_LINUX.tgz" "${SCRIPT_DIR}/sedutil"
fi
if [ "1" != "$(cat "/sys/module/libata/parameters/allow_tpm")" ]; then
  echo "libata.allow_tpm was not set. Setting it now."
  echo "1" > "/sys/module/libata/parameters/allow_tpm"
fi

$SEDUTIL --scan
$SEDUTIL --isValidSED "${DISK}"
$SEDUTIL --printDefaultPassword "${DISK}"
if [ $# -eq 1 ]; then
  echo "Please run this script again and provide the PSID of the drive as the second argument."
  return 0
fi
SEDUTIL_OUTPUT=$($SEDUTIL --yesIreallywanttoERASEALLmydatausingthePSID "${2}" "${DISK}")
if (grep "revertTper completed successfully" <<< "${SEDUTIL_OUTPUT}"); then
  echo "Erasing the SSD using the PSID was completed successfully. (${SEDUTIL_OUTPUT})"
else
  echo "${SEDUTIL_OUTPUT}"
  return 1
fi
