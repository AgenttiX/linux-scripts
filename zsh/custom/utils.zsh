#!/usr/bin/env zsh

# TODO: Think whether to use hyphens or underscores in the names.
# https://unix.stackexchange.com/a/168222/

compress_7z() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
    return 1
  fi
  # https://stackoverflow.com/a/965072/
  FILENAME=$(basename -- "$1")
  NAME="${FILENAME%.*}"
  # https://superuser.com/a/742034/
  7zr a -t7z -mx=9 "${NAME}.7z" "${FILENAME}"
  7zr t "${NAME}.7z"
  echo "Computing SHA-256 checksum."
  sha256sum "${NAME}.7z" > "${NAME}.7z.sha256"
}

compress_zip() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
    return 1
  fi
  # https://stackoverflow.com/a/965072/
  FILENAME=$(basename -- "$1")
  NAME="${FILENAME%.*}"
  # https://superuser.com/a/742034/
  7z a -mm=Deflate -mfb=258 -mpass=15 "${NAME}.zip" "${FILENAME}"
  7z t "${NAME}.zip"
  echo "Computing SHA-256 checksum."
  sha256sum "${NAME}.zip" > "${NAME}.zip.sha256"
}

findit() {
    # https://unix.stackexchange.com/questions/42841/how-to-skip-permission-denied-errors-when-running-find-in-linux
    if [ $# -ne 2 ]; then
        echo "findit: Search files and directories recursively. Unlike 'find', it does not pollute output with errors."
        echo "Usage:    findit <path> <some part of filename>"
        echo "Example:  findit / 'some_library'"
    else
        find "$1" -name "*$2*"  2>&1 | grep -v "Permission denied" | grep -v "No such file or directory" | grep -v "Invalid argument"
    fi
}

# This does not work, since zsh functions are not available in the KDE Alt+F2 prompt
# fix-kde() {
#   killall plasmashell
#   sleep 1
#   kstart plasmashell
# }

pdfsearch() {
    # https://stackoverflow.com/questions/4643438/how-to-search-contents-of-multiple-pdf-files
    if [ $# -ne 2 ]; then
        echo "pdfsearch: Search content from multiple pdfs recursively. For example, search some word from directory of books."
        echo "Usage:    pdfsearch <path> <text snippet>"
        echo "Example:  pdfsearch . 'citation'"
    else
        find "$1" -name '*.pdf' -exec sh -c "pdftotext \"{}\" - | grep -nH -B 1 -A 1 --label=\"{}\" --color \"$2\"" \;
    fi
}

replacerec() {
    # https://superuser.com/questions/422459/substitution-in-text-file-without-regular-expressions
    # https://stackoverflow.com/questions/1583219/how-to-do-a-recursive-find-replace-of-a-string-with-awk-or-sed
    if [ $# -ne 3 ]; then
        echo "replacerec: Find and replace text recursicely. Unlike 'sed' it does not try to match special symbols with regex."
        echo "Usage:    replacerec <old-text> <new-text> <filter>"
        echo "Example:  replacerec '(^_^)' ':D' '*.txt'"
    else
        export FINDTHIS="$1"
        export REPLACE="$2"
        find . \( -type d -name .git -prune \) -o -type f -name "$3" -exec echo {} \;  -exec \
            ruby -p -i -e "gsub(ENV['FINDTHIS'], ENV['REPLACE'])" {} \;
    fi
}

# Chats
start-chats() {
  # Start chat clients
  # The "&!" is zsh-specific
  # https://askubuntu.com/a/10557/
  if (command -v discord &> /dev/null); then
    if pgrep -x "Discord" > /dev/null; then :; else
      echo "Starting Discord"
      discord &> /dev/null &!
    fi
  fi
  # The "telegram-deskto" is not a typo.
  if command -v flatpak &> /dev/null; then
    if pgrep -x "telegram-deskto" > /dev/null; then :; else
      echo "Starting Telegram"
      flatpak run org.telegram.desktop &!
    fi
  fi
  if command -v signal-desktop &> /dev/null; then
    if pgrep -x "signal-desktop" > /dev/null; then :; else
      echo "Starting Signal"
      signal-desktop --start-in-tray &> /dev/null &!
    fi
  fi
}

close-chats() {
  # Close chat clients
  killall --signal TERM Discord
  # The "telegram-deskto" is not a typo.
  killall --signal TERM telegram-deskto
  killall --signal TERM signal-desktop
  killall --signal TERM walc
}

update() {
  if (command -v apt-get &> /dev/null); then
    echo "Updating apt-get packages"
    sudo apt-get update
    # Remove unused packages before upgrading to prevent unnecessary upgrades
    sudo apt-get autoremove
    sudo apt-get dist-upgrade
    sudo apt-get autoremove
  fi
  if (command -v snap &> /dev/null); then
    echo "Updating Snap packages"
    sudo snap refresh
  fi
  if (command -v flatpak &> /dev/null); then
    echo "Updating Flatpak packages"
    # Remove unused packages before updating to prevent unnecessary updates
    flatpak uninstall --unused
    flatpak update
    flatpak uninstall --unused
  fi
  if (command -v zgen &> /dev/null); then
    echo "Updating zgen"
    zgen update
  fi

  # Git repositories
  PWD_BEFORE_UPDATE="${PWD}"
  if [ -d "${HOME}/Git/linux-scripts" ]; then
    echo "Updating linux-scripts"
    cd "${HOME}/Git/linux-scripts"
    git pull
  fi
  if [ -d "${HOME}/Git/windows-scripts" ]; then
    echo "Updating windows-scripts"
    cd "${HOME}/Git/windows-scripts"
    git pull
  fi
  if [ -d "${HOME}/Git/private-scripts" ]; then
    echo "Updating private-scripts"
    cd "${HOME}/Git/private-scripts"
    git pull
  fi
  if [ -d "${HOME}/Git/vxl-scripts" ]; then
    echo "Updating vxl-scripts"
    cd "${HOME}/Git/vxl-scripts"
    git pull
  fi
  cd "${PWD_BEFORE_UPDATE}"
}

# Calculate checksum for current directory INCLUDING filenames and permissions. It takes no arguments
alias dirsum1="tar c . | md5sum"

# Calculate checksum for current directory NOT INCLUDING filenames and permissions. It takes no arguments
alias dirsum2="find . -type f -name '*' -exec md5sum {} + | awk '{print $1}' | sort | md5sum"

# Find text recursively. Print line numbers and rows above and below match.
# It takes one argument, which is text. For examble: eti some_text
alias eti="grep -rnI -B 1 -A 1"

# Reload broken audio devices
alias fixaudio="pulseaudio -k && sudo alsa force-reload"

# Scan wifi networks. This also refreshes the wifi-list, so if device was not connected,
# it makes auto-connection quicker
alias fixwifi="sudo iwlist scan | grep 'Cell\|ESSID:\|Quality='"

# shellcheck disable=SC2139
alias modem="sudo ${HOME}/Git/linux-scripts/modem.py"

# Easy pinging
alias pingu="ping -c 4 google.com"
alias pingu6="ping6 -c 4 google.com"

# Protontricks
# https://github.com/Matoking/protontricks
alias protontricks="flatpak run com.github.Matoking.protontricks"

if ! command -v rocm-smi &> /dev/null && [ -f "/opt/rocm/bin/rocm-smi" ]; then
  alias rocm-smi="/opt/rocm/bin/rocm-smi"
fi

# Print most recently modified files in current directory. It takes no arguments
alias vikat="find ${1} -type f | xargs stat --format '%Y :%y: %n' 2>/dev/null | sort -nr | cut -d: -f2,3,5 | head"
