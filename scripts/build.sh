#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
ASSETS_DEST="config/includes.chroot/tmp/lunar-assets"
LOG_FILE="$PROJECT_ROOT/lunar-build.log"

exec > >(tee "$LOG_FILE") 2>&1
trap 'echo "Build failed near line $LINENO. Full log: $LOG_FILE" >&2' ERR

if [ "$EUID" -ne 0 ]; then
    echo "Error: this script must be run as root: sudo $0"
    exit 1
fi

if ! command -v lb > /dev/null 2>&1; then
    echo "Error: 'lb' not found. Install live-build: apt-get install live-build"
    exit 1
fi

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "=== Configuring live-build ==="
lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --mirror-bootstrap "http://deb.debian.org/debian" \
    --mirror-chroot "http://deb.debian.org/debian" \
    --mirror-binary "http://deb.debian.org/debian" \
    --mirror-chroot-security "http://security.debian.org/debian-security" \
    --mirror-binary-security "http://security.debian.org/debian-security" \
    --parent-mirror-bootstrap "http://deb.debian.org/debian" \
    --parent-mirror-chroot "http://deb.debian.org/debian" \
    --parent-mirror-binary "http://deb.debian.org/debian" \
    --bootappend-live "boot=live components quiet splash plymouth.use-simpledrm" \
    --chroot-squashfs-compression-type zstd \
    --firmware-chroot false \
    --firmware-binary false \
    --debian-installer none \
    --binary-images iso-hybrid \
    --memtest none \
    --iso-application "Lunar OS" \
    --iso-preparer "Lunar OS Team" \
    --iso-publisher "Lunar OS Project" \
    --iso-volume "LUNAR_OS"

echo "=== Syncing project configuration ==="
for dir in package-lists hooks includes.chroot includes.binary bootloaders; do
    if [ -d "$PROJECT_ROOT/config/$dir" ]; then
        mkdir -p "config/$dir"
        cp -a --remove-destination "$PROJECT_ROOT/config/$dir/." "config/$dir/"
    fi
done

find config/hooks -type f -name '*.hook.*' -exec chmod +x {} +

copy_assets() {
    local src="$1" dest="$2"
    if [ -d "$src" ] && [ -n "$(ls -A "$src")" ]; then
        mkdir -p "$dest"
        cp -a "$src/." "$dest/"
    fi
}

copy_assets "$PROJECT_ROOT/assets/desktop" "$ASSETS_DEST/desktop"
copy_assets "$PROJECT_ROOT/assets/boot/plymouth" "$ASSETS_DEST/plymouth"
copy_assets "$PROJECT_ROOT/assets/icons" "$ASSETS_DEST/icons"

if ! ls config/package-lists/*.list.chroot > /dev/null 2>&1; then
    echo "Error: no package list found in config/package-lists"
    exit 1
fi

echo "=== Package lists ==="
ls -l config/package-lists
echo "=== Hooks ==="
ls config/hooks/normal | grep -E '^0[0-9]{3}-'

echo "=== Building Lunar OS ISO ==="
lb build

echo "=== Build successful ==="
ls -lh "$BUILD_DIR"/*.iso
