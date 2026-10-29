#!/bin/bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Error: this script must be run as root: sudo $0"
    exit 1
fi

apt-get update
apt-get install -y \
    live-build \
    debootstrap \
    xorriso \
    squashfs-tools \
    mtools \
    dosfstools \
    syslinux-utils \
    grub-pc-bin \
    grub-efi-amd64-bin \
    grub-common \
    rsync \
    python3 \
    python3-pil

echo "Dependencies installed. Optional for testing: apt-get install qemu-system-x86"
