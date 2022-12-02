# Virtualized Windows 11 with GPU passthrough

[Arch Wiki: PCI passthrough via OVMF](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF)

Big thanks to Joona Halonen for
[his instructions](https://github.com/JoonaHa/Single-GPU-VFIO-Win10/)!

Install the necessary software on the host
- QEMU is the emulator
- OVFM is the UEFI firmware for the VM
- Virt-manager is the GUI for configuring the VM
``` bash
sudo apt install qemu ovmf virt-manager
```

Create the VM using virt-manager.
For the best performance the disk should not be a file on the host filesystem,
but instead a separate LVM volume as instructed
[here](https://bashtheshell.com/guide/configuring-lvm-storage-for-qemukvm-vms-using-virt-manager-on-centos-7/).
Using a ZFS zvol is also possible,
but creating snapshots
[is not practical](https://www.reddit.com/r/zfs/comments/4oa4xb/comment/d4bofw9/),
as they consume the same amount of space as the original zvol.

### VM installation
Virt-manager settings
- Chipset
  - Q35 is for modern quests with PCIe
  - i440FX is for legacy quests
- Firmware
  - `OVMF_CODE_4M.ms.fd` or similar has support for Secure Boot with the
    Microsoft Windows keys
- Boot Options: ensure that the SATA CDROM drive is enabled in the boot device order
- Disk bus
  - Select VirtIO, as it's significantly faster
  - [Installing VirtIO drivers during Windows installation](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Virtio_disk)
    requires,
    that you add a second SATA CDROM drive using the Add Hardware button.
  - Download the
    [VirtIO Windows drivers](https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md)
    and attach it to the second SATA CDROM drive.
    Please note that the drivers may not be WHQL signed and may therefore cause issues with Secure Boot
    as described later.
    This is a [known issue](https://bugzilla.redhat.com/show_bug.cgi?id=1844726),
    as fully WHQL signed drivers are only provided for Red Hat enterprise customers.
- Add a TPM
  - Model: CRB (it's a
    [newer and simpler](https://kevinlocke.name/bits/2021/12/10/windows-11-guest-virtio-libvirt/)
    implementation than TIS)
  - CRB only supports TPM >= 2.0, so the version choice should not matter.

Once the settings are configured, start the VM.
Don't close the settings window instead, as your settings are not saved until you start the installation.
Start the Windows installation.
When prompted for the storage drivers, select "Load driver", click OK and select "E:\amd64\w11\viostor.inf".
When you reboot after the installation, you may get the bluescreen error "Kernel security check failure".
If this happens, just let Windows to fix it on its own, and reboot the virtual machine.
This is likely caused by the signing issues of the VirtIO storage driver.
Don't log in with your Microsoft account during the installation,
and instead skip it using the
[instructions on my website](https://agx.fi/it/checklists.html#windows-installation).

Shut down the VM.

### GPU setup
- Attach the GPU PCIe devices in the virt-manager VM settings
- Boot the VM
- If the driver does not load due to e.g. Code 43, follow the
  [Arch Wiki instructions](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Video_card_driver_virtualisation_detection)
  to hide the virtualization from the driver

### Performance tuning
- Add a network controller with "Device model: virtio"'
  - This may give you the aforementioned blue screen, but Windows will fix it on its own by disabling the device.
- CPU pinning: follow the
  [Arch Wiki instructions](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#CPU_pinning)
  - Use fixed cores in the XML
  - Disable these cores for the host
  - Use IO threads for the VirtIO disk
- If using an AMD CPU, enable the TOPOEXT flag with the
  [Arch Wiki instructions](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Improving_performance_on_AMD_CPUs)
- Configure huge pages
  - Enable huge pages in the VM settings
  - Use the scripts from this repo to reserve the memory or use your own configs

### Issues
Nvidia dmesg spam
- This can cause lag spikes! (Based on my personal experience.)
- [Reddit](https://www.reddit.com/r/VFIO/comments/dhdkiv/stop_modprobe_spam/)
- [Reddit 2](https://www.reddit.com/r/VFIO/comments/90tg4h/comment/e2tppqv/)
- [Launchpad](https://bugs.launchpad.net/ubuntu/+source/casper/+bug/1824177)
- [Launchpad 2](https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1655584)

Add this to your `/etc/modprobe/some-nvidia-script.conf`.
Replace the version number with the one you're using.
```
blacklist nvidia
blacklist nvidia_drm
blacklist nvidia_modeset
blacklist nvidia_uvm

blacklist nvidia_370
blacklist nvidia_370_drm
blacklist nvidia_370_modeset
blacklist nvidia_370_uvm

alias nvidia off
alias nvidia-uvm off
alias nvidia-modeset off
alias nvidia-drm off
```
You may also have to add the GPU UIDs to the kernel parameters to prevent the Nvidia driver from grabbing the device.
