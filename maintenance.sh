#!/bin/bash

# GNU/Linux maintenance script developed by Mika Mäki

# Check if running as root
if [ "$EUID" -ne 0 ]; then
	echo "Please run as root"
	exit
fi

# Update list of available packages
apt-get update

# Update packages
apt-get dist-upgrade -y
apt-get upgrade -y

# Remove unnecessary packages
apt-get autoremove -y
apt-get autoclean

# Update ClamAV virus definitions
if [ -f /usr/bin/freshclam ]; then
	freshclam -d
fi

# Clean unnecessary files using BleachBit
if [ -f /usr/bin/bleachbit ]; then
	bleachbit --clean adobe_reader.* amsn.* amule.* apt.* audacious.* bash.* beagle.* chromium.* d4x.* deepscan.ds_store deepscan.thumbs_db deepscan.tmp easytag.* elinks.* emesene.* epiphany.* evolution.* exaile.* filezilla.* firefox.cache firefox.crash_reports firefox.dom firefox.download_history firefox.forms firefox.session_restore firefox.site_preferences firefox.url_history firefox.vacuum flash.* gedit.* gftp.* gimp.* gl-117.* gnome.* google_chrome.* google_earth.* gpodder.* gwenview.* hippo_opensim_viewer.* java.* kde.* konqueror.* libreoffice.* liferea.* links2.* midnightcommander.* miro.* nautilus.* nexuiz.* octave.* openofficeorg.* opera.* pidgin.* realplayer.* recoll.* rhythmbox.* screenlets.* seamonkey.* secondlife_viewer.* skype.* sqlite3.* system.cache system.clipboard system.desktop_entry system.rotated_logs system.tmp system.trash thumbnails.* thunderbird.cache thunderbird.cookies thunderbird.index thunderbird.vacuum tremulous.cache vim.* vlc.* vuze.* warzone2100.* wine.* winetricks.* x11.* xchat.* xine.* yum.*
fi

# Run chkrootkit
if [ -f /usr/sbin/chkrootkit ]; then
	chkrootkit -q
fi


if [ -f /usr/bin/rkhunter ]; then
	# Update rkhunter
	rkhunter --update -q

	# Run rkhunter
	rkhunter -c -q
fi

# Trim SSD disks
if [ -f /sbin/fstrim ]; then
	fstrim -a -v
	fstrim / -v
fi

