# Building Lunar OS

This document provides detailed instructions for building Lunar OS from source.

## Prerequisites

### Operating System

Lunar OS must be built on a Debian-based system. Recommended options:

- **Debian 12 (Bookworm)** - Recommended
- **Ubuntu 22.04 LTS or later**
- **Linux Mint 21 or later**
- **Other Debian-based distributions**

Building on non-Debian systems (e.g., Fedora, Arch) is possible but requires additional configuration and is not documented here.

### System Requirements for Building

- **Disk Space**: At least 10 GB free space (for build artifacts and ISO)
- **RAM**: 2 GB minimum, 4 GB recommended
- **Network**: Internet connection required for downloading packages
- **CPU**: x86_64 architecture

### Required Packages

Install the following packages:

```bash
sudo apt-get update
sudo apt-get install -y \
    live-build \
    debootstrap \
    syslinux-utils \
    grub-pc-bin \
    grub-common \
    xorriso \
    mtools \
    squashfs-tools \
    wget \
    curl \
    git
```

### Optional Packages (for asset generation)

If you want to regenerate the visual assets:

```bash
sudo apt-get install -y python3 python3-pip
pip3 install Pillow --user
```

## Build Steps

### 1. Obtain the Source Code

Clone the repository or download the source:

```bash
git clone <repository-url> lunar-os
cd lunar-os
```

Or download and extract the source archive.

### 2. Generate Visual Assets

Generate the wallpaper, logos, and icons:

```bash
./scripts/generate-assets.sh
```

This will create:
- Desktop wallpaper (lunar-os/assets/desktop/wallpaper.png)
- Application logos in multiple sizes
- Welcome window icon
- Plymouth boot screen assets

If the script fails, ensure Python 3 and Pillow are installed:

```bash
python3 --version
python3 -c "from PIL import Image; print('Pillow OK')"
```

### 3. Build the ISO

The build process requires root privileges. Run:

```bash
sudo ./scripts/build.sh
```

The build script will:

1. Check for required dependencies
2. Clean any previous build
3. Create the build directory
4. Copy configuration files
5. Copy assets to the chroot
6. Run `lb build` to create the ISO
7. Report the location of the resulting ISO

#### Build Time

The build process typically takes:
- **30-60 minutes** on a modern system with fast internet
- **60-90 minutes** on older systems or slower internet

#### Build Output

On success, you'll see:

```
=== Build successful! ===
ISO file location: /path/to/lunar-os/build/*.iso
```

The ISO file will be named something like `lunar-os-amd64.iso`.

### 4. Verify the ISO

Check that the ISO was created:

```bash
ls -lh build/*.iso
```

You should see a file of approximately 1-2 GB.

Optionally, verify the ISO checksum:

```bash
sha256sum build/*.iso > build/sha256sum.txt
```

## Build Configuration

### Modifying the Configuration

Image options are the `lb config` flags in `scripts/build.sh`. Package lists, hooks and included files live under `config/`.

### Adding Packages

Edit `config/package-lists/lunar.list.chroot`, one package per line, then rebuild.

### Customizing Hooks

Hooks are in `config/hooks/normal/` and run in numeric order. See `docs/PROJECT_STRUCTURE.md` for what each one does. Hook `0900-verify-desktop` fails the build when required packages or Lunar files are missing.

## Troubleshooting Build Issues

### "lb: command not found"

Install live-build:

```bash
sudo apt-get install live-build
```

### Permission Denied

Ensure you're running the build script with sudo:

```bash
sudo ./scripts/build.sh
```

### Build Fails During Package Download

Check your internet connection and mirror configuration in `config/build/config`:

```
LB_MIRROR_BOOTSTRAP="http://deb.debian.org/debian"
LB_MIRROR_CHROOT="http://deb.debian.org/debian"
```

### Build Fails with "Space on device"

Ensure you have at least 10 GB free disk space. Clean previous builds:

```bash
sudo rm -rf build/
```

### Plymouth Theme Not Applied

Check that the Plymouth hook has execute permissions:

```bash
chmod +x config/packages.hook/0001-install-plymouth-theme.hook.chroot
```

### Assets Not Copied

Verify assets were generated:

```bash
ls -la assets/desktop/
ls -la assets/boot/plymouth/
```

Regenerate if missing:

```bash
./scripts/generate-assets.sh
```

## Building Variants

### Building for Different Architectures

Edit `config/build/config`:

```bash
LB_ARCHITECTURE="i386"  # For 32-bit systems
```

### Building with Different Desktop Environments

Lunar OS targets LXDE. Another desktop needs different packages in `config/package-lists/lunar.list.chroot` and rewritten hooks `0002`, `0005`, `0006` and `0007`, the panel config and the verification hook.

### Building with Additional Software

Add one package name per line to `config/package-lists/lunar.list.chroot`, for example `vlc`, `gimp` or `libreoffice`. Everything installed this way also uses RAM at run time.

## Reproducible Builds

To ensure reproducible builds:

1. Use the same base system (Debian 12)
2. Use the same package versions (pin them in config if needed)
3. Use the same mirror for package downloads
4. Set the same timezone during build

## Advanced: Custom Kernel

To use a custom kernel:

1. Build the kernel modules
2. Add them to `config/includes.chroot/lib/modules/`
3. Update the bootloader configuration in `config/bootloaders/`

## Clean Build

To completely clean and rebuild:

```bash
sudo rm -rf build/
sudo ./scripts/build.sh
```

## Performance Tips

### Use a Local Mirror

Edit `config/build/config` to use a local Debian mirror:

```bash
LB_MIRROR_BOOTSTRAP="http://localhost/debian"
LB_MIRROR_CHROOT="http://localhost/debian"
```

### Cache Packages

live-build caches packages in `/var/cache/live-build`. Preserve this cache between builds.

### Parallelize

Live-build can use multiple CPU cores. Ensure `lb config` is set appropriately.

## Next Steps

After building:

1. Test the ISO in a virtual machine (see docs/TESTING.md)
2. Write to a USB drive for physical testing
3. Customize further if needed
4. Share the ISO with others

## Additional Resources

- [Debian Live Manual](https://live-team.pages.debian.net/live-manual/)
- [LXDE](https://www.lxde.org/)
- [Plymouth Themes](https://www.freedesktop.org/software/plymouth/doc/)
