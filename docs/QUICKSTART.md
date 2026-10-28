# Lunar OS Quick Start Guide

This guide will help you get started with Lunar OS quickly.

## What is Lunar OS?

Lunar OS is a completely disposable operating system. Every time you boot it, you get a fresh, clean desktop. All your files, settings, and changes are discarded when you shut down. It's perfect for:

- Temporary work sessions
- Private browsing
- Testing software
- Kiosk computers
- Secure computing environments

## Quick Start

### Option 1: Download and Run (If Available)

If a pre-built ISO is available:

1. Download the ISO file
2. Write it to a USB drive (see below)
3. Boot from the USB drive
4. Click "Start Session" in the welcome window
5. Use the system
6. Shut down when done (all data is discarded)

### Option 2: Build from Source

If you want to build Lunar OS yourself:

```bash
# On Debian 12 or compatible system
sudo apt-get install live-build debootstrap syslinux-utils grub-pc-bin grub-common xorriso mtools python3 python3-pip
pip3 install Pillow --user

# Clone or download the source
cd lunar-os

# Generate assets
./scripts/generate-assets.sh

# Build the ISO (requires root)
sudo ./scripts/build.sh

# The ISO will be in build/*.iso
```

See [BUILDING.md](BUILDING.md) for detailed instructions.

## Writing to USB Drive

### Linux

```bash
# Identify your USB drive
lsblk

# Write the ISO (replace /dev/sdX with your device)
sudo dd if=build/*.iso of=/dev/sdX bs=4M status=progress conv=fsync

# Sync and eject
sync
sudo eject /dev/sdX
```

### macOS

```bash
# Identify your USB drive
diskutil list

# Unmount the disk
diskutil unmountDisk /dev/diskN

# Write the ISO (replace N with your disk number)
sudo dd if=build/*.iso of=/dev/diskN bs=4m
```

### Windows

Use [Rufus](https://rufus.ie/) or [Etcher](https://www.balena.io/etcher/).

## Booting Lunar OS

1. Insert the USB drive
2. Restart your computer
3. Press the boot menu key (F12, F2, Del, etc.)
4. Select the USB drive
5. Wait for the boot screen
6. Click "Start Session" when prompted

## First Boot

When you first boot Lunar OS:

1. **Boot Screen**: You'll see the Lunar OS logo with a loading animation
2. **Welcome Window**: A window will appear explaining the disposable concept
3. **Start Session**: Click the button to begin using the system
4. **Desktop**: The desktop will load with the lunar wallpaper

## Using Lunar OS

### Desktop Basics

- **Application Launcher**: Click the moon icon in the bottom-left corner
- **Taskbar**: Shows running applications at the bottom
- **System Tray**: Network, sound, and other indicators on the right
- **Clock**: Date and time display

### Built-in Applications

- **File Manager**: Thunar - manage your files
- **Terminal**: XFCE Terminal - command line
- **Web Browser**: Firefox ESR - private browsing mode
- **Text Editor**: Mousepad - edit text files
- **Calculator**: Galculator - perform calculations
- **Image Viewer**: Ristretto - view images
- **System Monitor**: Monitor system resources

### File Management

Your files are stored in:
- **Home Directory**: `/home/lunar`
- **Desktop**: `/home/lunar/Desktop`
- **Documents**: `/home/lunar/Documents`
- **Downloads**: `/home/lunar/Downloads`
- **Pictures**: `/home/lunar/Pictures`
- **Music**: `/home/lunar/Music`
- **Videos**: `/home/lunar/Videos`

**Important**: All files in these locations will be deleted when you shut down!

### Saving Files

To save files permanently:

1. Plug in a USB drive or external storage
2. Open the File Manager
3. Copy files to the external drive
4. Safely eject the drive before removing it

### Shutting Down

1. Click the power icon in the system tray
2. Select "Shut Down and Discard Session"
3. Confirm the shutdown
4. All your data will be discarded

**To restart**: Select "Restart and Start Fresh" instead.

## Testing in a Virtual Machine

If you want to test without writing to USB:

### Using QEMU (Linux)

```bash
qemu-system-x86_64 -m 2048 -cdrom build/*.iso -boot d
```

### Using VirtualBox

1. Create a new VM
2. Set RAM to 2048 MB or more
3. Mount the ISO as a virtual CD/DVD
4. Start the VM

## System Requirements

### Minimum
- **RAM**: 2 GB
- **CPU**: x86_64 (Intel/AMD 64-bit)
- **Storage**: 4 GB USB drive

### Recommended
- **RAM**: 4 GB or more
- **CPU**: Dual-core 2.0 GHz or better
- **Storage**: 8 GB USB drive

## Important Notes

### Data Persistence

**Discarded on Shutdown**:
- Files in your home directory
- Downloads
- Browser history and cookies
- Application settings
- Desktop files
- Terminal history

**NOT Discarded**:
- Files on external USB drives
- Files uploaded to cloud services
- Files sent over the network

### Limitations

- **RAM-based**: All your files are stored in RAM. With 2 GB RAM, you have limited space.
- **No persistence**: Cannot save files to the system (by design).
- **Hardware support**: Limited to hardware supported by Debian 12.

### Privacy

Lunar OS provides disposable storage, but:
- Your ISP can see your network traffic
- Websites can track you during the session
- Use a VPN or Tor for additional privacy
- This is not forensic-grade security

## Keyboard Shortcuts

- **Super (Windows key)**: Open application launcher
- **Alt + Tab**: Switch between windows
- **Alt + F4**: Close window
- **Super + T**: Open terminal
- **Super + E**: Open file manager
- **Print Screen**: Take screenshot

## Troubleshooting

### Won't Boot

- Try the "Safe Graphics" boot option
- Ensure your USB drive is written correctly
- Check that your system meets requirements

### No Network

- Check the network manager in the system tray
- Try connecting manually
- Check if your Wi-Fi adapter is supported

### Out of RAM

- Close unused applications
- Move large files to external storage
- Increase RAM allocation in VM settings

### Welcome Window Doesn't Appear

- Open terminal and run: `/usr/share/lunar-os/welcome.py`
- Check that Python 3 and GTK3 are installed

## Getting Help

- Check the documentation in the `docs/` directory
- Review the configuration files in `config/`
- Look at the build scripts in `scripts/`
- Report issues via the project issue tracker

## Next Steps

- Read the full [README.md](../README.md) for detailed information
- See [BUILDING.md](BUILDING.md) for build instructions
- See [TESTING.md](TESTING.md) for testing procedures
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

## Enjoy Lunar OS!

Remember: everything is temporary. Explore freely without worrying about leaving traces behind.
