#!/usr/bin/env bash
set -e

# # Based on the script by Joona Halonen
# https://github.com/JoonaHa/Single-GPU-VFIO-Win10/blob/main/hooks/win10-vfio/release/end/revert.sh
# set -x

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

# Unload VFIO-PCI Kernel Driver
# modprobe -r vfio-pci
# modprobe -r vfio_iommu_type1
# modprobe -r vfio

echo "Reattaching PCIe devices to the host."
virsh nodedev-reattach pci_0000_4c_00_0
virsh nodedev-reattach pci_0000_4c_00_1
virsh nodedev-reattach pci_0000_24_00_3

# Uncomment this if you don't use the any other Nvidia GPU on the host.
# echo "Reloading Nvidia drivers."
# set +e
# modprobe nvidia_drm
# odprobe nvidia_modeset
# modprobe nvidia_uvm
# modprobe nvidia
# set -e

echo "Disabling hugepages."
echo 0 > /proc/sys/vm/nr_hugepages

echo "Setting CPU governor to \"ondemand\"."
for file in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo "ondemand" > $file; done

echo "Re-enabling all CPU cores."
HOST_CPUS="0-63"
systemctl set-property --runtime -- user.slice AllowedCPUs="${HOST_CPUS}"
systemctl set-property --runtime -- system.slice AllowedCPUs="${HOST_CPUS}"
systemctl set-property --runtime -- init.slice AllowedCPUs="${HOST_CPUS}"
