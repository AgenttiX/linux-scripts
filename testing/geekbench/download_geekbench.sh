#!/bin/bash -e

VERSIONS=("5.4.4" "4.4.4" "3.4.4" "2.4.3")
for VERSION in "${VERSIONS[@]}"; do
  echo "Downloading Geekbench ${VERSION}"
  FILENAME="Geekbench-${VERSION}-Linux.tar.gz"
  wget "https://cdn.geekbench.com/${FILENAME}" -O "${FILENAME}"
  tar -xzf "${FILENAME}"
  rm "${FILENAME}"
done
mv ./dist/* .
rm ./dist -r
