#!/bin/bash
# Lunar OS Build Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Lunar OS Build Script ==="
echo "Project root: $PROJECT_ROOT"

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo $0"
    exit 1
fi

if ! command -v lb &> /dev/null; then
    echo "Error: 'lb' not found. Please install live-build:"
    echo "  apt-get install live-build"
    exit 1
fi

if [ -d "$PROJECT_ROOT/build" ]; then
    echo "Cleaning previous build..."
    rm -rf "$PROJECT_ROOT/build"
fi

mkdir -p "$PROJECT_ROOT/build"
cd "$PROJECT_ROOT/build"

echo "Initializing live-build..."
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
    --bootappend-live "boot=live components quiet splash" \
    --debian-installer none \
    --binary-images iso-hybrid

echo "Syncing configuration files..."
for dir in package-lists hooks includes.chroot includes.binary bootloaders; do
    if [ -d "$PROJECT_ROOT/config/$dir" ]; then
        mkdir -p "config/$dir"
        if [ -d "config/$dir" ]; then
            rsync -a "$PROJECT_ROOT/config/$dir/" "config/$dir/"
        else
            cp -a "$PROJECT_ROOT/config/$dir" config/
        fi
    fi
done

echo "Copying assets to includes.chroot..."
mkdir -p config/includes.chroot/tmp/lunar-assets/desktop
mkdir -p config/includes.chroot/tmp/lunar-assets/plymouth
mkdir -p config/includes.chroot/tmp/lunar-assets/icons

if [ -d "$PROJECT_ROOT/assets/desktop" ]; then
    rsync -a "$PROJECT_ROOT/assets/desktop/" config/includes.chroot/tmp/lunar-assets/desktop/
fi

if [ -d "$PROJECT_ROOT/assets/boot/plymouth" ]; then
    rsync -a "$PROJECT_ROOT/assets/boot/plymouth/" config/includes.chroot/tmp/lunar-assets/plymouth/
fi

if [ -d "$PROJECT_ROOT/assets/icons" ] && [ "$(ls -A "$PROJECT_ROOT/assets/icons" 2>/dev/null)" ]; then
    rsync -a "$PROJECT_ROOT/assets/icons/" config/includes.chroot/tmp/lunar-assets/icons/
fi

echo "=== Building Lunar OS ISO ==="
lb build

echo "=== Build successful! ==="
echo "ISO file location: $PROJECT_ROOT/build/*.iso"
echo ""
echo "To test the ISO:"
echo "  qemu-system-x86_64 -m 2048 -cdrom $PROJECT_ROOT/build/*.iso -boot d"
echo ""
echo "To write to USB:"
echo "  dd if=$PROJECT_ROOT/build/*.iso of=/dev/sdX bs=4M status=progress"
