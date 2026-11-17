#!/usr/bin/env bash
# This script should continue on errors
# set -e
set -u

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

# if command -v kwallet-query &> /dev/null; then
#   kwallet-query -l kdewallet > /dev/null
# fi

# Run the pre-startup script again to ensure that the SSH agent is available
. "${SCRIPT_DIR}/agx-user-pre-startup.sh"

echo "Starting SSH agent configuration script."
SETUP_AGENT="${REPO_DIR}/ssh/setup_agent.sh"
if [ -f "${SETUP_AGENT}" ]; then
  "${SETUP_AGENT}" private-scripts
fi

# This should be before other applications just in case, since this configures audio settings for them.
if command -v pactl >/dev/null 2>&1; then
  echo "Configuring PipeWire."
  pactl load-module module-combine-sink
fi

if command -v displaycal-apply-profiles >/dev/null 2>&1; then
  displaycal-apply-profiles &
fi

# Syncthing and cloud services should be started as early as possible to ensure
# that the user does not modify files before they are synced.
if command -v syncthing >/dev/null 2>&1; then
  syncthing &
fi

if command -v dropbox >/dev/null 2>&1; then
  dropbox start -i &
fi

# RescueTime no longer supports Linux.
#if command -v rescuetime >/dev/null 2>&1; then
#  rescuetime &
#fi

# ActivityWatch does not work on Wayland.
# https://docs.activitywatch.net/en/latest/faq.html#why-is-the-active-window-logged-as-unknown-when-using-wayland
# https://github.com/ActivityWatch/activitywatch/issues/92
#ACTIVITYWATCH="${HOME}/Downloads/activitywatch/aw-qt"
#if [ -f "${ACTIVITYWATCH}" ]; then
#  echo "Starting ActivityWatch."
#  "${ACTIVITYWATCH}" &
#fi

# Electron and Qt apps register their tray icons only once at startup.
# If the system tray (StatusNotifierWatcher) is not yet available,
# the tray icon will be missing, and e.g. Mattermost may open a window instead.
# Therefore, wait for the tray before starting the apps that should start in the tray.
wait_for_system_tray() {
  local timeout=60
  if ! command -v busctl >/dev/null 2>&1; then
    echo "busctl not found. Cannot check whether the system tray is available."
    return 1
  fi
  for ((i = 0; i < timeout; i++)); do
    if busctl --user status org.kde.StatusNotifierWatcher >/dev/null 2>&1; then
      echo "System tray is available."
      return 0
    fi
    sleep 1
  done
  echo "System tray did not become available in ${timeout} s. Starting the apps anyway."
  return 1
}
wait_for_system_tray

if command -v flatpak >/dev/null 2>&1; then
  FLATPAKS="$(flatpak list --app --columns=application)"
  has_flatpak() { grep -qxF "$1" <<< "${FLATPAKS}"; }
  if has_flatpak "com.mattermost.Desktop"; then
    echo "Starting Mattermost."
    flatpak run com.mattermost.Desktop --hidden &
  fi
  if has_flatpak "com.slack.Slack"; then
    echo "Starting Slack."
    flatpak run com.slack.Slack --startup &
  fi
  if has_flatpak "org.telegram.desktop"; then
    echo "Starting Telegram."
    flatpak run org.telegram.desktop -startintray &
  fi
  if has_flatpak "com.github.IsmaelMartinez.teams_for_linux"; then
    echo "Starting Teams."
    flatpak run com.github.IsmaelMartinez.teams_for_linux &
  fi
fi

if command -v signal-desktop >/dev/null 2>&1; then
  echo "Starting Signal."
  signal-desktop --start-in-tray &
fi

# Telegram snap does not work on Kubuntu 25.04
# https://github.com/telegramdesktop/tdesktop/issues/29437#issuecomment-3131627645
# if command -v telegram-desktop >/dev/null 2>&1; then
#   echo "Starting Telegram"
#   # The environment variable fixes compatibility with Kubuntu 25.04
#   # https://github.com/telegramdesktop/tdesktop/issues/29437#issuecomment-2981043225
#   QT_QPA_PLATFORM=xcb telegram-desktop -startintray &
# fi

if [ "$(hostname)" = "agx-z2e-kubuntu" ]; then
  echo "Starting Discord."
  flatpak run com.discordapp.Discord --start-minimized &
  echo "Starting Steam."
  # -pipewire enables desktop capture on Wayland for Remote Play and Steam Frame / Steam Link.
  # Without it, the streamed desktop is black.
  # start_steam.sh hides the Radeon VII from Steam so that the capture uses the GPU running the desktop.
  # STEAM_FORCE_CLIENT=steamrt64 selects the 64-bit Steam client, whose desktop capture uses
  # SIMD-optimized color conversion. The 32-bit client's conversion is too slow for 3440x1440 at 60 FPS.
  STEAM_FORCE_CLIENT=steamrt64 "${REPO_DIR}/games/steam/start_steam.sh" -nochatui -nofriendsui -pipewire -silent &
fi
