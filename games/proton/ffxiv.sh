#!/bin/sh -e
FFXIV_CFG="FFXIV.cfg"
FFXIV_CFG_ORIGINAL="FFXIV-original.cfg"
FFXIV_BOOT_CFG="FFXIV_BOOT.cfg"
FFXIV_BOOT_CFG_ORIGINAL="FFXIV_BOOT-original.cfg"

DEMO_ID=312060
FULL_ID=39210

echo "Do you have the demo or the full version? Answer d for demo or f for full."
read GAME_TYPE
case $GAME_TYPE in
    d) ID=$DEMO_ID;;
    f) ID=$FULL_ID;;
    *) echo "Invalid option" && exit;;
esac

cd "${HOME}/.steam/debian-installation/steamapps/compatdata/${ID}/pfx/drive_c/users/steamuser/My Documents/My Games/FINAL FANTASY XIV - A Realm Reborn/"

# Backup the original configuration
if [ ! -f $FFXIV_BOOT_CFG_ORIGINAL ]; then
    cp $FFXIV_BOOT_CFG $FFXIV_BOOT_CFG_ORIGINAL
fi

# Set Browser and StartupCompleted to 1
sed -i "s/Browser	2/Browser	1/g" $FFXIV_BOOT_CFG
sed -i "s/StartupCompleted	0/StartupCompleted	1/g" $FFXIV_BOOT_CFG
echo "Launcher settings have been configured successfully."

if [ -f $FFXIV_CFG ]; then
    if [ ! -f $FFXIV_CFG_ORIGINAL ]; then
        cp $FFXIV_CFG $FFXIV_CFG_ORIGINAL
    fi
    # Set CutsceneMovieOpening to 1
    sed -i "s/CutsceneMovieOpening	0/CutsceneMovieOpening	1/g" $FFXIV_CFG
else
    echo "The game has not been launched yet, so the in-game settings could not yet be configured. Please run this script again when you have launched the game at least once."
fi

# TODO: Add the dxvk.conf here
