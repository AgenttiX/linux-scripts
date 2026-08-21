#!/usr/bin/env zsh

# TODO: Think whether to use hyphens or underscores in the names.
# Hyphens are probably better, since they're easire to write.
# https://unix.stackexchange.com/a/168222/

apt-rdepends-installed() {
  # Find installed apt packages which depend on argument(s)
  # From:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
	apt-cache rdepends "$@" | grep "  " | xargs apt list --installed
}

clear-history() {
  "${HOME}/Git/linux-scripts/security/clear_history.sh"
}

fix-kde() {
  killall plasmashell -9
  sleep 1
  kstart plasmashell
}

fix-kde-hard() {
  rm -rf "${HOME}/.cache/"*plasma*
  kwin_wayland --replace &
}

# function nvidia-smi {
#   # This fix is no longer needed and won't work with the latest Nvidia drivers (570->).
#   # https://forums.developer.nvidia.com/t/nvidia-smi-uses-all-of-ram-and-swap/295639/3
#   valgrind nvidia-smi "$@" 2> /dev/null
# }

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
	if [ "$2" = "" ]; then
		echo "Usage: $0 sleeptime command"
	fi

	local sleeptime="$1"
	shift

	until $@
	do
		sleep "$sleeptime"
	done
}

# For those familiar with Vim
alias :q="exit"

# Analyze the contents of a Docker image
# https://github.com/wagoodman/dive
alias dive="docker run -ti --rm  -v /var/run/docker.sock:/var/run/docker.sock docker.io/wagoodman/dive"

# Calculate checksum for current directory INCLUDING filenames and permissions. It takes no arguments
alias dirsum1="tar c . | md5sum"

# Calculate checksum for current directory NOT INCLUDING filenames and permissions. It takes no arguments
alias dirsum2="find . -type f -name '*' -exec md5sum {} + | awk '{print $1}' | sort | md5sum"

# Scan wifi networks. This also refreshes the wifi-list, so if device was not connected,
# it makes auto-connection quicker
alias fix-wifi="sudo iwlist scan | grep 'Cell\|ESSID:\|Quality='"

# shellcheck disable=SC2139
alias modem="sudo ${HOME}/Git/linux-scripts/modem.py"

# if ! command -v nvim &> /dev/null && command -v flatpak; then
#   alias nvim="flatpak run io.neovim.nvim"
# fi

# A joke for typoing the command "apt".
# The "; :" discards any additional arguments.
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

# RTFM = Read The Fucking Manual :D
alias rtfm="man"

alias screeni="screen -rD || screen"

# Fun sudo aliases
alias fuck="sudo"
alias fucking="sudo"
alias please="sudo"

# Google Translate
alias translate="ddg \!translate ${@}"

alias yoink="git pull"
alias yeet="git push"
