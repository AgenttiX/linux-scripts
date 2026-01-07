#!/usr/bin/env bash
set -eu

# This is Mika's reporting script
# https://github.com/AgenttiX/linux-scripts

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

REPORT=true
SECURITY=true

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-report)
      REPORT=false
      shift
      ;;
    --no-security)
      SECURITY=false
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

OLDPWD="${PWD}"
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &> /dev/null && pwd )"
GIT_DIR="$(dirname "$(dirname "${SCRIPT_DIR}")")"
DIR="${SCRIPT_DIR}/report"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"

if [ -z "${DIR}" ]; then
  echo "Could not configure directory variable: ${DIR}"
  exit 1
fi

# Detect if lm-sensors was already installed
if command -v sensors &> /dev/null; then
  LM_SENSORS_INSTALLED=true
else
  LM_SENSORS_INSTALLED=false
fi

# Install dependencies
echo "Updating package lists."
sudo apt update
echo "Installing dependencies."
sudo apt install 7zip acpi clinfo dmidecode git i2c-tools lm-sensors lshw lsscsi vainfo vdpauinfo vulkan-tools wget

# Install security scanners
if [ "${SECURITY}" = true ]; then
  echo "Downloading LinPEAS."
  wget "https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh" -O "${SCRIPT_DIR}/linpeas.sh"
  chmod +x "${SCRIPT_DIR}/linpeas.sh"

  LYNIS_DIR="${GIT_DIR}/lynis"
  if [ -d "${LYNIS_DIR}" ]; then
    echo "Lynis was found. Updating."
    cd "${LYNIS_DIR}"
    git pull
  else
    echo "Lynis was not found. Downloading."
    cd "${GIT_DIR}"
    git clone "https://github.com/CISOfy/lynis"
  fi
  cd "${OLDPWD}"
fi

# Load kernel modules for decode-dimms
# https://superuser.com/a/1499521/
if command -v decode-dimms &> /dev/null; then
  echo "Loading kernel modules for decode-dimms."
  sudo modprobe at24
  sudo modprobe ee1004
  sudo modprobe i2c-i801
  sudo modprobe i2c-amd-mp2-pci
  # The eeprom module may not be present on all systems.
  # https://bbs.archlinux.org/viewtopic.php?id=292830
  set +e
  sudo modprobe eeprom
  set -e
fi

# It's not clear whether this should be before or after loading the kernel modules.
# As this is after loading them, it could detect more devices, but on the other hand
# it might access some devices that it shouldn't.
# TODO: test that this works
if (command -v sensors &> /dev/null) && [ "${LM_SENSORS_INSTALLED}" = false ]; then
  echo "lm-sensors was installed with this run of the script."
  echo "Therefore the sensors haven't been configured yet and should be configured now."
  sudo sensors-detect
fi

# Create the report directory
mkdir -p "${DIR}"
# Remove old results
if [ "$(ls -A $DIR)" ]; then
  echo "Cleaning the report directory."
  rm -r "${DIR:?}"/*
fi
mkdir -p "${DIR}/hdparm" "${DIR}/smartctl"
cp "${SCRIPT_PATH}" "${DIR}"
sed "s/HOST/$(hostname)/g; s/TIMESTAMP/${TIMESTAMP}/g" "${SCRIPT_DIR}/report_readme_template.txt" > "${DIR}/README.txt"

# Basic info
echo "Basic info:"
echo -n "Hostname: "
hostname |& tee "${DIR}/basic.txt"
echo -n "Uname: "
uname -a |& tee -a "${DIR}/basic.txt"
echo "HDDs" |& tee -a "${DIR}/basic.txt"
if command -v smartctl &> /dev/null; then
  smartctl --scan |& tee -a "${DIR}/basic.txt"
else
  echo "The command \"smartctl\" was not found."
fi

function report_command () {
  if [ "${1}" = "sudo" ]; then
    if command -v "${2}" &> /dev/null; then
      echo "Running the command \"${*}\"."
      # shellcheck disable=SC2024
      if sudo "${@:2}" &> "${DIR}/${2}.txt"; then :; else
        echo "Running the command \"${*}\" failed."
      fi
    else
      echo "The command \"${2}\" was not found."
    fi
  else
    if command -v "${1}" &> /dev/null; then
      echo "Running the command \"${*}\"."
      if ${1} "${@:2}" &> "${DIR}/${1}.txt"; then :; else
        echo "Running the command \"${*}\" failed."
      fi
    else
      echo "The command \"${1}\" was not found."
    fi
  fi
}

# -----
# Root info
# -----
# These should be first so that the probability of having to ask sudo password again is minimized.

echo "Running the reporting commands that require sudo access."
echo "If these take a while, then you may be asked to input your sudo password again."

report_command sudo dmesg
report_command sudo dmidecode
if command -v docker &> /dev/null; then
  {
    sudo docker -v
    sudo docker system info
    sudo docker image ls
    sudo docker container ls
  } &> "${DIR}/docker.txt"
else
  echo "The command \"docker\" was not found."
fi

report_command sudo fdisk -l

if command -v lshw &> /dev/null; then
  # shellcheck disable=SC2024
  sudo lshw -html > "${DIR}/lshw.html"
else
  echo "The command \"lshw\" was not found."
fi

# Storage devices
if command -v smartctl &> /dev/null; then
  echo "Scanning storage devices with hdparm and smartctl."
  mapfile -t SMARTCTL_SCAN < <(smartctl --scan)
  for LINE in "${SMARTCTL_SCAN[@]}"; do
    IFS=", " read -r -a ARR <<< "${LINE}"
    DISK="${ARR[0]}"
    DISK_NAME="$(basename "${DISK}")"
    # shellcheck disable=SC2024
    sudo hdparm -I "${DISK}" &> "${DIR}/hdparm/${DISK_NAME}.txt"
    # shellcheck disable=SC2024
    if sudo smartctl --all "${DISK}" &> "${DIR}/smartctl/${DISK_NAME}.txt"; then :; else
      echo "Checking smartctl data for ${DISK} failed. Either the drive does not support smartctl or it's failing."
    fi
  done
else
  echo "The command \"smartctl\" was not found."
fi

# RAID devices
# This should be after regular HDD/SSD checks so that the individual drives are checked before the higher-level features.
if command -v mdadm &> /dev/null; then
  echo "Scanning RAID devices with mdadm."
  mapfile -t MDADM_SCAN < <(sudo mdadm --detail --scan)
  echo "${MDADM_SCAN[@]}"
  for LINE in "${MDADM_SCAN[@]}"; do
    IFS=" " read -r -a ARR <<< "${LINE}"
    # shellcheck disable=SC2024
    sudo mdadm --detail "${ARR[1]}" &>> "${DIR}/mdadm.txt"
  done
else
  echo "The command \"mdadm\" was not found."
fi

if command -v cpupower &> /dev/null; then
  echo "Scanning CPU info with cpupower"
  {
    sudo cpupower info
    cpupower frequency-info
    cpupower idle-info
    sudo cpupower powercap-info
    sudo cpupower monitor
  } &> "${DIR}/cpupower.txt"
else
  echo "The command \"cpupower\" was not found."
fi

# Security scanners
if [ "${SECURITY}" = true ]; then
  echo "Running security scanners."
  # Lynis security scan
  # This can take quite a while and should therefore be the last command to be run with sudo.
  echo "Starting Lynis as root. If you see a warning about file permissions, press enter to continue."
  sudo "${LYNIS_DIR}/lynis" audit system |& tee "${DIR}/lynis.txt"

  # LinPEAS security scan
  echo "Starting LinPEAS security scanner."
  "${SCRIPT_DIR}/linpeas.sh" |& tee "${DIR}/linpeas.txt"
fi


# -----
# Non-root info
# -----

echo "Running the reporting commands that do not require sudo access."
echo "You should no longer be asked for your sudo password."

cat "/proc/acpi/wakeup" > "${DIR}/wakeup.txt"
cat "/proc/cpuinfo" > "${DIR}/cpuinfo.txt"
cat "/proc/mdstat" > "${DIR}/mdstat.txt"
cat "/sys/power/mem_sleep" > "${DIR}/mem_sleep.txt"
cat "/var/log/syslog" > "${DIR}/syslog.txt"

if command -v fwupdmgr &> /dev/null; then
  fwupdmgr get-devices > "${DIR}/fwupdmgr_devices.txt"
  # fwupdmgr returns exit code 2 when no updates are found.
  set +e
  fwupdmgr get-updates > "${DIR}/fwupdmgr_updates.txt"
  set -e
else
  echo "The command \"fwupdmgr\" was not found."
fi

if command -v systemd-analyze &> /dev/null; then
  systemd-analyze plot > "${DIR}/systemd-analyze-plot.svg"
  {
    echo -e '$ systemd-analyze has-tpm2'
    systemd-analyze has-tpm2
    echo -e '$ systemd-analyze critical-chain'
    systemd-analyze critical-chain
    echo -e '\n$ systemd-analyze blame'
    systemd-analyze blame
    echo -e '\n$ systemd-analyze architectures'
    systemd-analyze architectures
    echo -e '\n$ systemd-analyze security'
    systemd-analyze security
    echo -e '\n$ systemd-analyze unit-paths'
    systemd-analyze unit-paths
    echo -e '\n$ systemd-analyze unit-files'
    systemd-analyze unit-files
    # This is long and therefore the last.
    echo e '\n$ systemd-analyze dump'
    systemd-analyze dump
  } &> "${DIR}/systemd-analyze.txt"
else
  echo "The command \"systemd-analyze\" was not found."
fi

report_command acpi --everything --details
report_command arp
report_command clinfo
report_command decode-dimms
report_command df --human-readable
report_command dpkg --list
report_command fastfetch
report_command glxinfo -t
report_command intel_gpu_top -L
report_command lsblk
report_command lsb_release -a
report_command lscpu
report_command lsmod
report_command lspci
report_command lsscsi
# lsusb seems to return 1 on virtual servers.
set +e
report_command lsusb
set -e
report_command numba --sysinfo
report_command nvidia-smi

if command -v pip &> /dev/null; then
  {
    pip -V
    pip list
  } &> "${DIR}/pip.txt"
else
  echo "Python pip was not found."
fi

if command -v pip3 &> /dev/null; then
  {
    pip3 -V
    pip3 list
  } &> "${DIR}/pip3.txt"
else
  echo "Python pip3 was not found."
fi

if command -v ras-mc-ctl &> /dev/null; then
  {
    ras-mc-ctl --print-labels
    ras-mc-ctl --error-count
  } &> "${DIR}/ras-mc-ctl.txt"
else
  echo "The command \"ras-mc-ctl\" was not found."
fi

report_command rocminfo
report_command rocm-smi --showallinfo
report_command sensors

# Battery info
if command -v upower &> /dev/null; then
  echo "Scanning battery info with upower."
  {
    upower --enumerate
    upower --dump
    # This no longer works on Kubuntu 25.04
    # upower --wakeups
  } &> "${DIR}/upower.txt"
else
  echo "The command \"upower\" was not found."
fi

report_command vainfo
report_command vdpauinfo
report_command vulkaninfo
report_command xinput list
report_command xrandr
report_command zpool status

if [ -d "/var/log/samba" ] && command -v rsync &> /dev/null; then
  # The cores folder would require root access, so let's skip it.
  rsync -av --progress "/var/log/samba" "${DIR}" --exclude "cores"
fi

if [ "${REPORT}" = true ]; then
  # Packaging
  7zr a -mx=9 "${DIR}_${TIMESTAMP}.7z" "${DIR}"
  echo "The report is ready."
fi
