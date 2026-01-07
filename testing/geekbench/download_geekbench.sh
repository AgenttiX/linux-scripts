#!/bin/bash -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

VERSIONS=("6.5.0" "5.4.5" "4.4.4" "3.4.4" "2.4.3")
for VERSION in "${VERSIONS[@]}"; do
  FOLDER_NAME="Geekbench-${VERSION}-Linux"
  if [ -d "${SCRIPT_DIR}/${FOLDER_NAME}" ]; then
    echo "Geekbench ${VERSION} seems to be already downloaded."
  else
    echo "Downloading Geekbench ${VERSION}"
    FILENAME="${FOLDER_NAME}.tar.gz"
    wget "https://cdn.geekbench.com/${FILENAME}" -O "${SCRIPT_DIR}/${FILENAME}"
    tar -xzf "${FILENAME}"
    rm "${FILENAME}"
  fi
done
mv -f "${SCRIPT_DIR}/dist/"* "${SCRIPT_DIR}"
rm -rf "${SCRIPT_DIR}/dist"
