#!/usr/bin/env bash
# Start Steam so that it uses only the GPU(s) that run the desktop.
#
# On multi-GPU systems Steam's PipeWire desktop capture (Remote Play, Steam Link, Steam Frame)
# picks the first GPU returned by libdrm, which may not be the one running the desktop.
# This makes the capture fall back from DMA-BUF to a slow CPU copy.
# This script builds and preloads steam_drm_filter.c, which hides GPUs of the given PCI vendors from Steam.
#
# Usage: start_steam.sh [steam arguments]
# Environment:
#   AGX_DRM_HIDE_VENDORS: comma-separated PCI vendor IDs to hide. Default: 0x1002 (AMD).
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE="${SCRIPT_DIR}/steam_drm_filter.c"
LIB_NAME="libagx-drm-filter.so"
LIB_ROOT="${HOME}/.local/lib"

# Build the library for one architecture if it is missing or outdated.
build_filter() {
  local arch_flag="$1"
  local multiarch="$2"
  local out_dir="${LIB_ROOT}/${multiarch}"
  local out="${out_dir}/${LIB_NAME}"
  if [ -f "${out}" ] && [ "${out}" -nt "${SOURCE}" ]; then
    return 0
  fi
  if [ ! -e "/usr/lib/${multiarch}/libdrm.so.2" ]; then
    echo "libdrm for ${multiarch} not found. Skipping the ${multiarch} DRM filter." >&2
    return 1
  fi
  mkdir -p "${out_dir}"
  local tmp
  tmp="$(mktemp "${out_dir}/.${LIB_NAME}.XXXXXX")"
  if gcc "${arch_flag}" -shared -fPIC -O2 -Wall -Wextra -I/usr/include/libdrm \
      -o "${tmp}" "${SOURCE}" -ldl "-l:libdrm.so.2" -L"/usr/lib/${multiarch}"; then
    chmod 0755 "${tmp}"
    mv -f "${tmp}" "${out}"
    echo "Built ${out}"
  else
    rm -f "${tmp}"
    echo "Failed to build ${out}" >&2
    return 1
  fi
}

if ! command -v steam >/dev/null 2>&1; then
  echo "Steam is not installed." >&2
  exit 1
fi

FILTER_OK=true
if command -v gcc >/dev/null 2>&1; then
  # The Steam client is 32-bit. The 64-bit build covers its 64-bit helper processes.
  build_filter -m32 i386-linux-gnu || FILTER_OK=false
  build_filter -m64 x86_64-linux-gnu || FILTER_OK=false
else
  echo "gcc not found. Cannot build the DRM filter." >&2
  FILTER_OK=false
fi

if [ "${FILTER_OK}" = true ]; then
  export AGX_DRM_HIDE_VENDORS="${AGX_DRM_HIDE_VENDORS:-0x1002}"
  # The dynamic linker expands $LIB to e.g. lib/i386-linux-gnu or lib/x86_64-linux-gnu,
  # so each process loads the library of its own architecture.
  export LD_PRELOAD="${HOME}/.local/\$LIB/${LIB_NAME}${LD_PRELOAD:+:${LD_PRELOAD}}"
  echo "Starting Steam with GPUs of PCI vendors ${AGX_DRM_HIDE_VENDORS} hidden."
else
  echo "Starting Steam without the DRM filter." >&2
fi

exec steam "$@"
