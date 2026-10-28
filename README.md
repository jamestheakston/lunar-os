# Lunar OS

A completely disposable operating system designed for temporary sessions. Every time you boot Lunar OS, you enter a fresh desktop session. Files, settings, downloads, and other user-created data are stored in temporary storage and discarded when you shut down.

## Features

- **Disposable Sessions**: All session data is stored in RAM and discarded on shutdown
- **Lunar Aesthetic**: Modern, minimalist design with a moon-inspired color scheme
- **Lightweight**: Based on Debian Linux with XFCE desktop environment
- **Privacy-Focused**: Private browsing mode by default, no data persistence
- **Bootable ISO**: Can be run from USB drive or in virtual machines
- **No Installation Required**: Runs entirely from the ISO without installation

## System Requirements

### Minimum Requirements
- **CPU**: x86_64 (Intel/AMD 64-bit)
- **RAM**: 2 GB (4 GB recommended for smooth operation)
- **Storage**: 4 GB USB drive (for live boot) or virtual disk space
- **Graphics**: VESA-compatible or better

### Recommended Requirements
- **CPU**: Dual-core 2.0 GHz or better
- **RAM**: 4 GB or more
- **Storage**: 8 GB USB drive
- **Graphics**: Hardware acceleration capable

## Quick Start

For a quick start guide, see [docs/QUICKSTART.md](docs/QUICKSTART.md).

## Building the ISO

### Option 1: GitHub Actions (Recommended)

The easiest way to build Lunar OS is using GitHub Actions:

1. Push this repository to GitHub
2. Go to the "Actions" tab
3. Click "Build Lunar OS ISO"
4. Click "Run workflow"
5. Download the ISO from the artifacts

See [`.github/README.md`](.github/README.md) for details.

### Option 2: Local Build

For a local build, see [docs/BUILDING.md](docs/BUILDING.md).

## Prerequisites for Local Build

```bash
sudo apt-get update
sudo apt-get install live-build debootstrap syslinux-utils grub-pc-bin grub-common xorriso mtools
```

For asset generation, you also need:
```bash
sudo apt-get install python3 python3-pip
pip3 install Pillow --user
```

For detailed local build instructions, see [docs/BUILDING.md](docs/BUILDING.md).

## Testing Lunar OS

### Using QEMU (Linux/Unix)

Install QEMU:
```bash
sudo apt-get install qemu-kvm qemu-utils
```

Test the ISO:
```bash
qemu-system-x86_64 -m 2048 -cdrom build/*.iso -boot d
```

For better performance with KVM:
```bash
qemu-system-x86_64 -enable-kvm -m 2048 -cdrom build/*.iso -boot d
```

### Using VirtualBox

1. Create a new VM
2. Allocate at least 2 GB RAM
3. Set the CD/DVD drive to point to the Lunar OS ISO
4. Start the VM

### Using VMware

1. Create a new VM
2. Select "Linux" as the guest OS
3. Allocate at least 2 GB RAM
4. Mount the ISO as a virtual CD/DVD
5. Start the VM

## Installing to USB Drive

### On Linux

Identify your USB device (e.g., /dev/sdX):
```bash
lsblk
```

Write the ISO to the USB drive (WARNING: This will erase all data on the USB drive):
```bash
sudo dd if=build/*.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

Sync and eject:
```bash
sync
sudo eject /dev/sdX
```

### On macOS

Identify your USB device (e.g., /dev/disk2):
```bash
diskutil list
```

Unmount the disk:
```bash
diskutil unmountDisk /dev/disk2
```

Write the ISO (replace N with the correct disk number):
```bash
sudo dd if=build/*.iso of=/dev/diskN bs=4m
```

### On Windows

Use a tool like [Rufus](https://rufus.ie/) or [Etcher](https://www.balena.io/etcher/) to write the ISO to a USB drive.

## Using Lunar OS

### First Boot

1. Boot from the USB drive or ISO
2. Wait for the Lunar OS boot screen with the loading animation
3. The desktop will load automatically
4. A "Welcome to Lunar OS" window will appear
5. Click "Start Session" to begin using the system

### Desktop Environment

Lunar OS uses the XFCE desktop environment with custom theming:

- **Taskbar**: Located at the bottom with application launcher, task list, system tray, and clock
- **Application Launcher**: Click the moon icon or press the Super key
- **File Manager**: Thunar with custom settings
- **Terminal**: XFCE Terminal with Monospace font
- **Web Browser**: Firefox ESR in private browsing mode

### Built-in Applications

- **File Manager**: Thunar
- **Text Editor**: Mousepad
- **Terminal**: XFCE Terminal
- **Web Browser**: Firefox ESR (private mode)
- **Calculator**: Galculator
- **Image Viewer**: Ristretto
- **System Monitor**: GNOME System Monitor
- **Settings**: XFCE Settings Manager

### Shutting Down

To shut down Lunar OS:

1. Click the power icon in the system tray or use the application launcher
2. Select "Shut Down and Discard Session"
3. Confirm the shutdown
4. All session data will be discarded

To restart:
1. Select "Restart and Start Fresh"
2. Confirm the restart
3. The system will reboot with a clean session

## Project Structure

```
lunar-os/
├── assets/                  # Visual assets
│   ├── boot/               # Boot screen assets (Plymouth)
│   ├── desktop/            # Desktop assets (wallpaper, Python apps)
│   └── icons/              # Application icons
├── config/                  # Debian Live configuration
│   ├── build/              # Live-build config files
│   ├── includes.chroot/    # Files to add to the live system
│   ├── includes.binary/    # Files to add to the ISO
│   ├── packages.hook/      # Build hooks
│   └── bootloaders/       # Bootloader configuration
├── scripts/                 # Build and utility scripts
│   ├── build.sh           # Main ISO build script
│   └── generate-assets.sh  # Asset generation script
└── docs/                   # Documentation
```

## Technical Details

### Disposable Session Architecture

Lunar OS uses overlayfs with tmpfs for disposable storage:

- **Base System**: Read-only squashfs filesystem from the ISO
- **Writable Layer**: tmpfs (RAM-based overlay)
- **Union**: overlayfs combines the two layers
- **Result**: All writes go to RAM and are discarded on shutdown

This ensures:
- No data persistence after shutdown
- Fast read performance (from ISO)
- Fast write performance (to RAM)
- No wear on USB drives
- No accidental data persistence

### Boot Process

1. **GRUB**: Loads the kernel and initramfs
2. **Plymouth**: Displays the Lunar OS boot screen
3. **live-boot**: Sets up the overlayfs with tmpfs
4. **systemd**: Initializes services
5. **LightDM**: Auto-login to the XFCE desktop
6. **Welcome Window**: Displays automatically on first boot

### Custom Components

- **Plymouth Theme**: Custom boot screen with moon logo and animation
- **Welcome Window**: GTK3 Python application introducing the disposable concept
- **Shutdown Dialog**: Custom GTK3 Python application with session discard confirmation
- **Desktop Configuration**: Custom XFCE settings for Lunar OS branding
- **Application Settings**: Firefox private mode, Thunar defaults, etc.

## Known Limitations

- **RAM Requirements**: The entire writable layer is stored in RAM. With 2 GB RAM, you may experience issues with large files or many applications.
- **No Persistence**: Session data cannot be saved (by design). To save files, copy them to external media.
- **Hardware Support**: Limited to hardware supported by Debian 12 and the included firmware packages.
- **Network Configuration**: Requires manual setup for some network hardware.
- **Battery/Power Management**: Basic power management is included, but advanced features may be limited.

## Security Considerations

Lunar OS is designed for privacy and disposability, but:

- **Not Forensically Secure**: Data may persist in hardware caches, network logs, or other systems.
- **Network Privacy**: Your ISP and network can still see your network traffic. Use a VPN if needed.
- **External Media**: Files copied to external drives will persist.
- **Virtual Machines**: The hypervisor may have access to your session data.

## Troubleshooting

### Build Fails

- Ensure you're running on Debian 12 or compatible
- Check that you have root permissions
- Verify all dependencies are installed
- Check internet connectivity (build downloads packages)

### Boot Fails

- Try the "Safe Graphics" boot option
- Increase RAM allocation in VM settings
- Check that your hardware meets minimum requirements
- Try writing the ISO to a different USB drive

### Desktop Doesn't Load

- Try the "Verbose" boot option to see errors
- Ensure you have at least 2 GB RAM allocated
- Check for graphics driver issues (try Safe Graphics)

### Welcome Window Doesn't Appear

- Check that Python 3 and GTK3 are installed
- Look for errors in `/var/log/Xorg.0.log`
- Manually run: `/usr/share/lunar-os/welcome.py`

## Contributing

Lunar OS is open source. Contributions are welcome in the form of:

- Bug reports
- Feature requests
- Code improvements
- Documentation updates
- Translation support

## License

Lunar OS is based on Debian Linux and uses open source software. The Lunar OS custom components are released under the MIT License.

## Support

For issues, questions, or contributions:
- Report bugs via the project issue tracker
- Check the documentation in the `docs/` directory
- Review the configuration files in `config/`

## Acknowledgments

- Debian Project for the excellent base system
- XFCE for the lightweight desktop environment
- Debian Live team for the live system tools
- All contributors to the open source projects used
