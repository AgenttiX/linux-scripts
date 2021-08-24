#!/bin/bash -e
# This script optimizes all VirtualBox disk images on the host.
# This requires that the free space in the guests has already been zeroed.

OUTPUT="$(vboxmanage list hdds)"
IMG_PATHS=()
while read -r LINE; do
  if [[ "$LINE" == "Location:"* ]]; then
    # echo "$LINE"
    IMG_PATH=$(awk -F '[[:blank:]:]+' '{print $2}' <<< "$LINE")
    IMG_PATHS+=("$IMG_PATH")
  fi
done <<< "$OUTPUT"

echo "Found the following images:"
for IMG_PATH in "${IMG_PATHS[@]}"; do
  echo "${IMG_PATH}"
done

read -p "Do you want to optimize these? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Optimizing. Don't interrupt the procedure!"
  for IMG_PATH in "${IMG_PATHS[@]}"; do
    echo "Optimizing ${IMG_PATH}"
    vboxmanage modifymedium disk "$IMG_PATH" --compact
  done
fi
