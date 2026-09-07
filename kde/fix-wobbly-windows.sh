#!/usr/bin/env sh
set -eu

# Kubuntu ships /usr/share/kubuntu-default-settings/kf5-settings/kwinrc with
# "wobblywindowsEnabled=true", and that directory is part of XDG_CONFIG_DIRS.
#
# When the Wobbly Windows effect is unticked in
# System Settings -> Window Management -> Desktop Effects,
# the KCM assumes the effect's built-in default is "disabled" and, instead of
# writing "false", it writes the KConfig revert-to-default marker:
#
#   [Plugins]
#   wobblywindowsEnabled[$d]
#
# KConfig then resolves that entry through the cascade, where it picks up the
# Kubuntu default of "true", so the effect comes back on the next KWin start.
#
# The fix is to write an explicit "false" into ~/.config/kwinrc, which overrides
# the distribution default instead of deferring to it.

# Overridable so that the script can be unit tested against a temporary file.
KWINRC="${KWINRC:-kwinrc}"

if command -v kwriteconfig6 > /dev/null 2>&1; then
  KWRITECONFIG=kwriteconfig6
elif command -v kwriteconfig5 > /dev/null 2>&1; then
  KWRITECONFIG=kwriteconfig5
else
  echo "Neither kwriteconfig6 nor kwriteconfig5 was found."
  exit 1
fi

echo "Disabling the Wobbly Windows effect in ${KWINRC}"
"${KWRITECONFIG}" --file "${KWINRC}" --group Plugins --key wobblywindowsEnabled false

# Apply the change to the running session, if there is one.
if command -v qdbus6 > /dev/null 2>&1; then
  if qdbus6 org.kde.KWin /KWin org.kde.KWin.reconfigure > /dev/null 2>&1; then
    echo "Reloaded the KWin configuration"
  fi
fi
