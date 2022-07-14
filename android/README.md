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

## Installation steps
These instructions look very complicated, but they are actually quite straightforward,
unless you have a device with the A/B partition scheme or without a separate recovery partition.

- Upgrade of stock ROM for firmware upgrades (if doing a clean install and if it's possible)
  - The stock ROM may contain newer firmware for the modem, bluetooth etc., which improves security and reliability.
  - Please ensure, though, that the newer stock ROM doesn't lock the bootloader or introduce other additional restrictions.
- Install fastboot-installable official firmware from the stock ROM (if not already upgraded)
  - This can be done with the scripts of this repository.
- Select the boot slot you want to install to
  - `sudo fastboot --set-active=a` (or b)
- Boot to recovery (TWRP)
  - Try these in this order until one of them works
    - Samsung devices
       1) `sudo heimdall flash --RECOVERY <TWRP image>.img`
       2) Use Odin
    - Fastboot devices
      1) `sudo fastboot install recovery <TWRP image>.img` and boot from the on-device menu
      2) `sudo fastboot boot <TWRP image>.img`
      3) `sudo fastboot install boot <TWRP image>.img` and boot from the on-device menu
  - If TWRP gets stuck at the logo, try an older version.
- ADB-installable firmware from the stock ROM (if doing a clean install)
  - This can be done with the scripts of this repository.
- ROM (LineageOS)
  - Select the boot slot you want to install to.
  - Wipe the system and cache partitions
    - On devices without a separate recovery partition TWRP cannot be booted without a working OS installation,
      so don't reboot after wiping system before LineageOS is installed.
  - Select the boot slot you don't want to install to.
  - Install LineageOS (This will install to the slot that is not active at the moment.)
  - Select "reboot to recovery"
- If the device boots to the LineageOS recovery, ensure that the active slot is the slot you want to install to.
  - Then you have to use `adb sideload <file>.zip` to install the rest.
  - Install regardless of the signature warnings. They merely warn that the additional zips aren't provided by LineageOS.
- Google Apps
- Kernel (if available)
- TWRP zip (on devices without a recovery partition)
  - This will install to both slots.
- Root (Magisk)
  - The Magisk .apk has to be renamed to a .zip for it to work.
  - TWRP wiped this, so you have to do this for both slots when upgrading.
- Reboot to system

([XDA discussion of proper installation order](https://forum.xda-developers.com/t/what-is-the-proper-order-of-flashing-rom-kernel-root-gapps-and-anti-throttle.3651521/))

## Root installation steps
- Install Magisk when installing the ROM as above
- Install [Magisk Manager](https://github.com/topjohnwu/Magisk)
- Go to Magisk Manager settings and set these:
  - Hide Magisk app
  - Enable Zygisk
  - Enable Zygisk DenyList
  - [Show system and OS apps in Zygisk DenyList](https://i.imgur.com/jsu2Xsm.jpg)
- Add these apps to the DenyList
  - Google Pay
  - Google Play services
  - Google Play Store
  - All other apps that refuse to work on rooted phones
- Install [Universal SafetyNet Fix](https://github.com/kdrag0n/safetynet-fix)
- Install [MagiskHide Props Config](https://github.com/Magisk-Modules-Repo/MagiskHidePropsConf)
- (Install [Google Pay SQlite Fix Module](https://forum.xda-developers.com/t/working-magisk-with-google-pay-as-of-gms-17-1-22-on-pie.3929950/page-9#post-79643248))
- Reboot
- Delete app data and cache for the aforementioned Google apps
- Install and run [SafetyNet Test](https://play.google.com/store/apps/details?id=org.freeandroidtools.safetynettest)
  - Your device should now pass the check
- Delete app data and cache for the apps that still refuse to work
