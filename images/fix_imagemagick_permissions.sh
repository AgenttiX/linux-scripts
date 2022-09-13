#!/usr/bin/env bash
set -e

# Fix pdf creation for ImageMagick
# https://askubuntu.com/a/1081907/

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

sed -i 's/^  <policy domain="coder" rights="none" pattern="PDF" \/>$/  <policy domain="coder" rights="read\|write" pattern="PDF" \/>/g' "/etc/ImageMagick-6/policy.xml"
