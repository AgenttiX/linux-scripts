#!/usr/bin/env zsh

# TODO: Think whether to use hyphens or underscores in the names.
# https://unix.stackexchange.com/a/168222/

apt-rdepends-installed () {
  # Find installed apt packages which depend on argument(s)
  # From:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
	apt-cache rdepends "$@" | grep "  " | xargs apt list --installed
}

compress_7z() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
    return 1
  fi
  # https://stackoverflow.com/a/965072/
  local FILENAME=$(basename -- "$1")
  local NAME="${FILENAME%.*}"
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
  local FILENAME=$(basename -- "$1")
  local NAME="${FILENAME%.*}"
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

fix-kde() {
  killall plasmashell -9
  sleep 1
  kstart plasmashell
}

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

function nvidia-smi {
  # https://forums.developer.nvidia.com/t/nvidia-smi-uses-all-of-ram-and-swap/295639/3
  valgrind nvidia-smi "$@" 2> /dev/null
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
  if command -v flatpak &> /dev/null; then
    if pgrep -x "ferdium" > /dev/null; then :; else
      echo "Starting Ferdium"
      flatpak run org.ferdium.Ferdium &!
    fi
    if pgrep -f "mattermost-desktop" > /dev/null; then :; else
      echo "Starting Mattermost"
      flatpak run org.mattermost.Desktop &!
    fi
    if pgrep -f "telegram-desktop" > /dev/null; then :; else
      echo "Starting Telegram"
      flatpak run org.telegram.desktop &!
    fi
  fi
  if command -v signal-desktop &> /dev/null; then
    if pgrep -f "signal-desktop" > /dev/null; then :; else
      echo "Starting Signal"
      signal-desktop --start-in-tray &> /dev/null &!
    fi
  fi
}

close-chats() {
  # Close chat clients
  # Ferdium may require two signals to fully close.
  # Therefore it's the first to give it as much time as possible to close cleanly.
  killall --signal TERM ferdium 2> /dev/null
  killall --signal TERM Discord 2> /dev/null
  # The "telegram-deskto" is not a typo.
  killall --signal TERM telegram-deskto 2> /dev/null
  killall --signal TERM signal-desktop 2> /dev/null
  killall --signal TERM walc 2> /dev/null
  # Second attempt to close Ferdium
  killall --signal TERM ferdium 2> /dev/null
}

retry_until() {
  # From:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
	if [ "$2" = "" ]
	then
		echo "Usage: $0 sleeptime command"
	fi

	local sleeptime="$1"
	shift

	until $@
	do
		sleep "$sleeptime"
	done
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

  # Git repositories
  local PWD_BEFORE_UPDATE="${PWD}"
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

  # This should be after the Git repo pulling,
  # since the repos can have an updated zsh config.
  if (command -v zgen &> /dev/null); then
    echo "Updating zgen"
    zgen update
  fi

  # zsh completions using zsh-manpage-completion-generator
  # Based on:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
  if command -v fish &> /dev/null; then
    local FISH_COMPLETION_DIR="${XDG_DATA_HOME-$HOME}/.local/share/fish/generated_completions"

    echo "Downloading zsh-manpage-completion-generator."
    cd "${ZSH_CUSTOM}"
    curl -sSL "https://github.com/umlx5h/zsh-manpage-completion-generator/releases/latest/download/zsh-manpage-completion-generator_$(uname -s)_$(uname -m).tar.gz" \
      | tar xz "zsh-manpage-completion-generator"
    chmod a+x "${ZSH_CUSTOM}/zsh-manpage-completion-generator"

    echo "Creating fish completions."
    fish -c "fish_update_completions"

    echo "Converting fish completions to zsh completions."
    ./zsh-manpage-completion-generator
    cd "${PWD_BEFORE_UPDATE}"

    # You can disable the completions for specific commands by deleting the files here.
    # rm "${FISH_COMPLETION_DIR}/_git*"
  else
      echo "Please install fish for zsh-manpage-completion-generator" > /dev/stderr
  fi
}

# For those familiar with Vim
alias :q="exit"

# Calculate checksum for current directory INCLUDING filenames and permissions. It takes no arguments
alias dirsum1="tar c . | md5sum"

# Calculate checksum for current directory NOT INCLUDING filenames and permissions. It takes no arguments
alias dirsum2="find . -type f -name '*' -exec md5sum {} + | awk '{print $1}' | sort | md5sum"

# Find text recursively. Print line numbers and rows above and below match.
# It takes one argument, which is text. For examble: eti some_text
alias eti="grep -rnI -B 1 -A 1"

# Scan wifi networks. This also refreshes the wifi-list, so if device was not connected,
# it makes auto-connection quicker
alias fix-wifi="sudo iwlist scan | grep 'Cell\|ESSID:\|Quality='"

# shellcheck disable=SC2139
alias modem="sudo ${HOME}/Git/linux-scripts/modem.py"

# if ! command -v nvim &> /dev/null && command -v flatpak; then
#   alias nvim="flatpak run io.neovim.nvim"
# fi

# The "; :" discards any additional arguments
alias pat="image headpat; :"

# Easy pinging
alias pingu="ping -c 4 google.com"
alias pingu6="ping6 -c 4 google.com"

# Protontricks
# https://github.com/Matoking/protontricks
alias protontricks="flatpak run com.github.Matoking.protontricks"

if ! command -v rocm-smi &> /dev/null && [ -f "/opt/rocm/bin/rocm-smi" ]; then
  alias rocm-smi="/opt/rocm/bin/rocm-smi"
fi

alias rtfm="man"

# Print most recently modified files in current directory. It takes no arguments
alias vikat="find ${1} -type f | xargs stat --format '%Y :%y: %n' 2>/dev/null | sort -nr | cut -d: -f2,3,5 | head"

alias screeni="screen -rD || screen"

# Fun sudo aliases
alias fuck="sudo"
alias fucking="sudo"
alias please="sudo"

# Google Translate
alias translate="ddg \!translate ${@}"

alias yoink="git pull"
alias yeet="git push"
