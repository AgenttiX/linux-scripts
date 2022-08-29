#!/bin/bash -e
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

# Reattach GPU to the host
virsh nodedev-reattach pci_0000_4c_00_0
virsh nodedev-reattach pci_0000_4c_00_1

# Reload Nvidia drivers
modprobe nvidia_drm
modprobe nvidia_modeset
modprobe nvidia_uvm
modprobe nvidia

# Disable hugpages
echo 0 > /proc/sys/vm/nr_hugepages

# Set CPU governor to "ondemand"
for file in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo "ondemand" > $file; done
