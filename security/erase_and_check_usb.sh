#!/usr/bin/env bash
set -euo pipefail

# -----
# Initial checks
# -----

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

if command -v f3probe &> /dev/null; then :; else
  echo "F3 seems not to be installed. Installing."
  apt update
  apt install f3
fi

# -----
# Environment variables
# -----

DISK=$1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="$(dirname "${SCRIPT_DIR}")/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${LOG_DIR}/usb_${TIMESTAMP}.txt"
mkdir -p "${LOG_DIR}"

# -----
# Disk validation
# -----

if [[ ! -b "${DISK}" ]]; then
  echo "Error: ${DISK} is not a block device."
  exit 1
fi
if [[ "${DISK}" =~ [0-9]$ ]]; then
  echo "Error: Provide the whole disk (e.g. /dev/sda), not a partition (e.g. /dev/sda1)."
  exit 1
fi

# Verify it's removable if possible (USB sticks usually have RM=1, but not always)
RM="$(lsblk -dn -o RM "${DISK}" 2>/dev/null || echo "")"
TRAN="$(lsblk -dn -o TRAN "${DISK}" 2>/dev/null || echo "")"
MODEL="$(lsblk -dn -o MODEL "${DISK}" 2>/dev/null || echo "")"
SIZE="$(lsblk -dn -o SIZE "${DISK}" 2>/dev/null || echo "")"

echo "Target: ${DISK} size=${SIZE} tran=${TRAN} rm=${RM} model=${MODEL:-unknown}" | tee "${LOG_PATH}"
if [[ "${RM:-0}" != "1" ]]; then
  echo "WARNING: lsblk does not report this as removable (RM != 1)."
  echo "If this is your system disk, STOP NOW."
fi

if mount | grep -qE "^${DISK}|^${DISK}[0-9]"; then
  echo "Error: Something on ${DISK} is mounted. Unmount it first."
  mount | grep -E "^${DISK}|^${DISK}[0-9]" || true
  exit 1
fi

# -----
# Run the tests
# -----

# TRIM is unlikely to be supported by USB flash drives, but there's no harm in trying.
blkdiscard -f "${DISK}" || true

# Documentation for the --reset-type argument:
# https://github.com/AltraMayor/f3/issues/79
f3probe --destructive --time-ops "${DISK}" | tee -a "${LOG_PATH}"

blkdiscard -f "${DISK}" 2>/dev/null || true

# type=c = FAT32
# type=83 = Linux filesystem, e.g. ext4
# 1 sector = 512 bytes -> 2048 sectors = 1 MB -> correctly aligned for modern drives
sfdisk --wipe always --wipe-partitions always "${DISK}" <<'EOF'
label: dos
unit: sectors

1 : start=2048, type=c, bootable
EOF

# Inform the kernel of the partition
partprobe "${DISK}" || true

# Create a FAT32 filesystem
mkfs.vfat -F 32 -n USB-TEST "${DISK}1"
partprobe "${DISK}" || true

# Mount the drive
MOUNT="$(mktemp -d /mnt/test-XXXXXX)"
mount "${DISK}1" "${MOUNT}"

# Unmount the drive at script exit
cleanup() {
  set +e
  sync
  umount "${MOUNT}" 2>/dev/null
  rmdir "${MOUNT}" 2>/dev/null
}
trap cleanup EXIT

f3write "${MOUNT}" | tee -a "${LOG_PATH}"
f3read "${MOUNT}" | tee -a "${LOG_PATH}"

fstrim "${MOUNT}" 2>/dev/null || true

echo "USB drive erased and tested. You can now safely remove the drive."
