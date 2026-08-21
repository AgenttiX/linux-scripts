#!/usr/bin/env zsh

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
        echo "pdfsearch: Search content from multiple pdfs recursively. For example, search some word from a directory of books."
        echo "Usage:    pdfsearch <path> <text snippet>"
        echo "Example:  pdfsearch . 'citation'"
        return 1
    fi
    echo "Searching $1 for \"$2\""
    find "$1/" -name '*.pdf' -exec sh -c "pdftotext \"{}\" - 2> /dev/null | grep -nH -B 1 -A 1 --label=\"{}\" --color \"$2\"" \;
}

replacerec() {
    # https://superuser.com/questions/422459/substitution-in-text-file-without-regular-expressions
    # https://stackoverflow.com/questions/1583219/how-to-do-a-recursive-find-replace-of-a-string-with-awk-or-sed
    if [ $# -ne 3 ]; then
        echo "replacerec: Find and replace text recursively. Unlike 'sed' it does not try to match special symbols with regex."
        echo "Usage:    replacerec <old-text> <new-text> <filter>"
        echo "Example:  replacerec '(^_^)' ':D' '*.txt'"
        return 1
    fi
    export FINDTHIS="$1"
    export REPLACE="$2"
    find . \( -type d -name .git -prune \) -o -type f -name "$3" -exec echo {} \;  -exec \
        ruby -p -i -e "gsub(ENV['FINDTHIS'], ENV['REPLACE'])" {} \;
}

zotsearch() {
  if [ $# -ne 1 ]; then
    echo "zotsearch: Search content from Zotero PDFs."
    echo "Usage:    zotsearch <text snippet>"
    echo "Example:  zotsearch 'citation'"
    return 1
  fi
  pdfsearch "${HOME}/Zotero/storage" "$1"
}

# Find text recursively. Print line numbers and rows above and below match.
# It takes one argument, which is text. For examble: eti some_text
alias eti="grep -rnI -B 1 -A 1"

# Print most recently modified files in current directory. It takes no arguments
alias vikat="find ${1} -type f | xargs stat --format '%Y :%y: %n' 2>/dev/null | sort -nr | cut -d: -f2,3,5 | head"
