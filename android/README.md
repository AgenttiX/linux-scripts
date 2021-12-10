# Android tools
This folder contains some tools for working with Android devices.

## Links

### OnePlus 6 (enchilada)
- [LineageOS](https://download.lineageos.org/enchilada)
- [TWRP](https://twrp.me/oneplus/oneplus6.html)
- [Stock ROM](https://www.oneplus.com/global/support/softwareupgrade/details?code=PM1574156173727)

### Samsung Galaxy Note 3 LTE (SM-N9005, hlte)
- [LineageOS](https://download.lineageos.org/hlte)
- [TWRP](https://twrp.me/samsung/samsunggalaxynote3qualcomm.html)
- [Lolz kernel](https://forum.xda-developers.com/t/clang-13-lolz-kernel-v16-android-9-10-11-stable.3812469/) ([download](https://www.pling.com/p/1410846/))
- [Stock ROM](https://sfirmware.com/samsung-sm-n9005/)

### Samsung Galaxy Note 2 LTE (GT-N7105, t0lte)
- [LineageOS](https://forum.xda-developers.com/t/rom-eol-7-1-2-official-lineageos-for-t0lte.3538310/) ([download](https://androidfilehost.com/?fid=1395089523397906488))
- [TWRP](https://twrp.me/samsung/samsunggalaxynote2n7105.html)
- [Stock ROM](https://sfirmware.com/samsung-gt-n7105/)

### Samsung Galaxy Tab 3 10.1 (GT-P5220)
- [LineageOS](https://forum.xda-developers.com/t/rom-gt-p52xx-unofficial-7-1-2-lineageos-14-1.3587761/)
- [TWRP](https://forum.xda-developers.com/t/recovery-gt-p52xx-unofficial-twrp-3-x-for-samsung-galaxy-tab-3-10-1.3340938/)

### Google Apps
- [LineageOS](https://wiki.lineageos.org/gapps.html)
- [OpenGApps](https://opengapps.org/)

### Root
- [Magisk](https://github.com/topjohnwu/Magisk) (preferred)
- [SuperSU](https://supersuroot.org/)

## Installation order
- Upgrade of stock ROM for firmware upgrades (if possible)
  - The stock ROM may contain newer firmware for the modem, bluetooth etc., which improves security and reliability
  - Please ensure, though, that the newer stock ROM doesn't lock the bootloader or introduce other additional restrictions
- Recovery (TWRP)
- Firmware from the stock ROM (if not already upgraded)
  - This can be done with the scripts of this repository
- ROM (LineageOS)
- Google Apps
- Kernel (if available)
- Root (Magisk)

([XDA discussion](https://forum.xda-developers.com/t/what-is-the-proper-order-of-flashing-rom-kernel-root-gapps-and-anti-throttle.3651521/))
