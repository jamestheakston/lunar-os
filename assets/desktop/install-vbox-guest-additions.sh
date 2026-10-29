#!/bin/bash
set -e

echo "Installing VirtualBox Guest Additions..."
echo "This may take a few minutes..."

# Check if VBoxGuestAdditions.iso is mounted
if ! mount | grep -q "VBoxGuestAdditions"; then
    echo "Please insert VirtualBox Guest Additions CD image from the VirtualBox menu:"
    echo "Devices -> Insert Guest Additions CD image"
    echo ""
    read -p "Press Enter after inserting the CD image..."
fi

# Find the mounted ISO
VBOX_MOUNT=$(find /media -name "VBox*" -type d 2>/dev/null | head -n 1)
if [ -z "$VBOX_MOUNT" ]; then
    VBOX_MOUNT=$(find /mnt -name "VBox*" -type d 2>/dev/null | head -n 1)
fi

if [ -z "$VBOX_MOUNT" ]; then
    echo "Error: VirtualBox Guest Additions CD not found."
    echo "Please insert it from the VirtualBox menu: Devices -> Insert Guest Additions CD image"
    exit 1
fi

echo "Found VirtualBox Guest Additions at: $VBOX_MOUNT"

# Install required packages
echo "Installing required build packages..."
sudo apt-get update
sudo apt-get install -y build-essential dkms linux-headers-amd64

# Run the installer
echo "Running VirtualBox Guest Additions installer..."
cd "$VBOX_MOUNT"
sudo sh ./VBoxLinuxAdditions.run

# Add user to vboxsf group
if id "lunar" &>/dev/null; then
    sudo usermod -aG vboxsf lunar
fi

echo ""
echo "VirtualBox Guest Additions installation complete!"
echo "Please reboot to apply all changes."
