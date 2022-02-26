#!/usr/bin/env zsh

compress_7z() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
  fi
  # https://stackoverflow.com/a/965072/
  FILENAME=$(basename -- "$1")
  NAME="${FILENAME%.*}"
  # https://superuser.com/a/742034/
  7zr a -t7z -mx=9 "${NAME}.7z" "${FILENAME}"
}

compress_zip() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
  fi
  # https://stackoverflow.com/a/965072/
  FILENAME=$(basename -- "$1")
  NAME="${FILENAME%.*}"
  # # https://superuser.com/a/742034/
  7z a -mm=Deflate -mfb=258 -mpass=15 "${NAME}.zip" "${FILENAME}"
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

# Easy pinging
alias pingu="ping -c 4 google.com"
alias pingu6="ping6 -c 4 google.com"

# Protontricks
# https://github.com/Matoking/protontricks
alias protontricks="flatpak run com.github.Matoking.protontricks"

if ! command -v rocm-smi &> /dev/null && [ -f "/opt/rocm/bin/rocm-smi" ]; then
  alias rocm-smi="/opt/rocm/bin/rocm-smi"
fi

# Easy upgrading
alias sagdu="sudo apt-get update && sudo apt-get dist-upgrade && sudo snap refresh && flatpak update"

# Print most recently modified files in current directory. It takes no arguments
alias vikat="find ${1} -type f | xargs stat --format '%Y :%y: %n' 2>/dev/null | sort -nr | cut -d: -f2,3,5 | head"
