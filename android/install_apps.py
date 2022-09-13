"""Script for quickly installing Android apps over ADB"""

# from adb import adb_commands
# from gplaydl import gplaydl

import android_tools as tools

ADVANCED_APPS = [
    "com.termux",
    "com.teslacoilsw.launcher",  # Nova launcher
]
BACKUP_APPS = [
    "com.keramidas.TitaniumBackup",
    "com.keramidas.TitaniumBackupPro",
    "org.swiftapps.swiftbackup",
]
COMMUNICATION_APPS = [
    "com.whatsapp",
    "org.thoughtcrime.securesms",
    "org.telegram.messenger",
]
MEDIA_APPS = [
    "com.mxtech.videoplayer.ad",
    "com.netflix.mediaclient",
    "com.plexapp.android",
    "org.videolan.vlc",
]
TV_APPS = [
    "com.google.android.apps.tv.launcherx",
    "com.google.android.leanbacklauncher",
    "com.google.android.youtube.tv",
]
UTILITY_APPS = [
    "com.androidfung.drminfo",
    "com.authy.authy",
    "com.jami.tool.hiddensetting",
    "com.lonelycatgames.Xplore",
    "com.rescuetime.android",
    "eu.thedarken.sdm",  # SD Maid
    "io.homeassistant.companion.android",
    "keepass2android.keepass2android",
    "net.sourceforge.opencamera",
    "org.mozilla.firefox",
]
MAGISK_VERSION = "25.2"
DIRECT_APPS = {
    f"https://github.com/topjohnwu/Magisk/releases/download/v{MAGISK_VERSION}/Magisk-v{MAGISK_VERSION}.apk": f"Magisk-v{MAGISK_VERSION}.apk",
    "https://f-droid.org/F-Droid.apk": "F-Droid.apk",
    # YouTube Vanced has been discontinued
    # https://vancedapp.com/
    # "https://github.com/YTVanced/VancedManager/releases/latest/download/manager.apk": "Vanced_manager.apk",
    # It's still available from APKMirror, but that page does not support automatic downloads
    # https://www.apkmirror.com/apk/team-vanced/vanced-manager/vanced-manager-2-6-2-crimson-release/vanced-manager-2-6-2-crimson-android-apk-download/
    # https://www.apkmirror.com/apk/team-vanced/youtube-vanced/youtube-vanced-17-03-38-release/
}
TESTING_APPS = [
    "com.cpuid.cpu_z",
    "com.futuremark.dmandroid.application",
    "com.futuremark.pcmark.android.benchmark",
    "com.glbenchmark.glbenchmark27",
    "com.primatelabs.banff",
    "com.primatelabs.geekbench",
    "com.primatelabs.geekbench4",
    "com.primatelabs.geekbench5",
    "de.srlabs.snoopsnitch",
    "org.ogre.browser",
    "org.zwanoo.android.speedtest",
]


# def install_default_apps(device: adb_commands.AdbCommands):
#     pass
#     # TODO:
#     # - split the apps to categories
#     # - add settings configuration
#     # https://stackoverflow.com/questions/14432706/adb-command-to-open-settings-and-change-them


def main():
    tools.download_multi(DIRECT_APPS)
    app_types = [
        BACKUP_APPS,
        ADVANCED_APPS,
        MEDIA_APPS,
        UTILITY_APPS,
        TESTING_APPS
    ]
    for apps in app_types:
        tools.download_play_multi(apps)

    # device = gplaydl.devicecode
    # gplaydl.devicecode = "BRAVIA_ATV2"
    # tools.download_play_multi(TV_APPS)
    # gplaydl.devicecode = device

    # TODO: The app installation has not been tested yet
    # device = adb_commands.AdbCommands()
    # device.ConnectDevice(rsa_keys=[tools.SIGNER])
    # install_default_apps(device)


if __name__ == "__main__":
    main()
