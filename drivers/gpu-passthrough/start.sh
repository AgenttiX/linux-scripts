#!/usr/bin/env bash
set -e

# Based on the script by Joona Halonen
# https://github.com/JoonaHa/Single-GPU-VFIO-Win10/blob/main/hooks/win10-vfio/prepare/begin/start.sh
# set -x

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

## Calculate number of hugepages to allocate from memory (in MB)
MEMORY=16384
HUGEPAGES="$(($MEMORY/$(($(grep Hugepagesize /proc/meminfo | awk '{print $2}')/1024))))"

echo "Allocating hugepages."
echo $HUGEPAGES > /proc/sys/vm/nr_hugepages
ALLOC_PAGES=$(cat /proc/sys/vm/nr_hugepages)

TRIES=0
while (( $ALLOC_PAGES != $HUGEPAGES && $TRIES < 1000 ))
do
    echo 1 > /proc/sys/vm/compact_memory            ## defrag ram
    echo $HUGEPAGES > /proc/sys/vm/nr_hugepages
    ALLOC_PAGES=$(cat /proc/sys/vm/nr_hugepages)
    echo "Succesfully allocated $ALLOC_PAGES / $HUGEPAGES"
    let TRIES+=1
done

if [ "$ALLOC_PAGES" -ne "$HUGEPAGES" ]
then
    echo "Not able to allocate all hugepages. Reverting."
    echo 0 > /proc/sys/vm/nr_hugepages
    exit 1
fi

echo "Setting CPU governor to \"performance\"."
for file in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo "performance" > $file; done

# Uncomment this if you don't use the any other Nvidia GPU on the host.
# echo "Unloading Nvidia drivers."
# modprobe -r nvidia_drm
# modprobe -r nvidia_modeset
# modprobe -r nvidia_uvm
# modprobe -r nvidia

echo "Unloading PCIe devices from the host OS."
# You can use the IOMMU script to find the PCIe IDs
set +e  # If the VM is already running, these can't be detached
virsh nodedev-detach pci_0000_4c_00_0
virsh nodedev-detach pci_0000_4c_00_1
# Unload USB controller as well
virsh nodedev-detach pci_0000_24_00_3
set -e

echo "Loading VFIO kernel module."
modprobe vfio-pci

echo "Isolating pinned CPUs."
HOST_CPUS="0-23,32-55"
# VM_CPUS="24-31,56-63"
systemctl set-property --runtime -- user.slice AllowedCPUs="${HOST_CPUS}"
systemctl set-property --runtime -- system.slice AllowedCPUs="${HOST_CPUS}"
systemctl set-property --runtime -- init.slice AllowedCPUs="${HOST_CPUS}"
