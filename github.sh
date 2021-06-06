#!/usr/bin/sh -e

get_latest_release() {
  if [ $# -ne 1 ]; then
    echo "get_latest_release: Get the Git tag name of the latest GitHub release."
    echo "Usage: get_latest_release <user_name/repository_name>"
    exit 1
  fi
  # https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

get_download_url() {
  if [ $# -ne 2 ]; then
    echo "get_download_url: Get the download URL of the latest GitHub release."
    echo "Usage: get_download_url <user_name/repository_name> <file_search_string>"
    exit 1
  fi
  # https://gist.github.com/steinwaywhw/a4cd19cda655b8249d908261a62687f8#gistcomment-2758561
	wget -q -nv -O- "https://api.github.com/repos/$1/releases/latest" 2>/dev/null |  jq -r '.assets[] | select(.browser_download_url | contains("'"$2"'")) | .browser_download_url'
}

download_latest_release() {
  if [ $# -ne 3 ]; then
    echo "download_latest_release: Download the latest release of a GitHub repository."
    echo "Usage: "
    exit 1
  fi
  wget "$(get_download_url "$1" "$2")" -O "$3"
}
