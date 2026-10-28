# Lunar OS Project Structure

This document describes the complete project structure of Lunar OS.

## Directory Tree

```
lunar-os/
├── assets/                          # Visual assets and resources
│   ├── boot/                       # Boot screen assets
│   │   └── plymouth/              # Plymouth boot screen theme
│   │       ├── lunar-os.plymouth  # Plymouth theme configuration
│   │       ├── lunar-os.script    # Plymouth animation script
│   │       └── logo.svg           # Moon logo (SVG)
│   ├── desktop/                    # Desktop assets
│   │   ├── wallpaper.png          # Desktop wallpaper
│   │   ├── welcome.py             # Welcome window application
│   │   ├── welcome-icon.png       # Welcome window icon
│   │   ├── shutdown-dialog.py     # Shutdown dialog application
│   │   ├── xfce4-panel.xml        # XFCE panel configuration
│   │   ├── xfce4-xfconf.xml       # XFCE desktop configuration
│   │   ├── xfce4-appearance.xml   # XFCE appearance settings
│   │   ├── generate-wallpaper.py  # Wallpaper generation script
│   │   └── generate-logo.py       # Logo generation script
│   └── icons/                      # Application icons (if present)
│       └── (various icon files)
│
├── config/                         # Debian Live configuration
│   ├── build/                     # Live-build configuration
│   │   └── config                 # Main build configuration
│   ├── includes.chroot/           # Files to add to the live system
│   │   └── etc/
│   │       ├── live/
│   │       │   └── config.conf.d/
│   │       │       ├── 0000-lunar-live.conf
│   │       │       └── 0001-disposable-storage.conf
│   │       └── skel/
│   │           └── .config/
│   │               └── xfce4/
│   │                   ├── panel/
│   │                   │   └── whiskermenu-1.rc
│   │                   └── xfconf/
│   │                       └── xfce-perchannel-xml/
│   │                           ├── xfce4-keyboard-shortcuts.xml
│   │                           └── (other XFCE configs)
│   ├── includes.binary/          # Files to add to the ISO (empty by default)
│   ├── packages.hook/            # Build hooks
│   │   ├── 0000-copy-assets.hook.chroot
│   │   ├── 0001-install-plymouth-theme.hook.chroot
│   │   ├── 0002-configure-xfce.hook.chroot
│   │   ├── 0003-install-welcome-app.hook.chroot
│   │   ├── 0004-configure-shutdown.hook.chroot
│   │   ├── 0005-configure-user.hook.chroot
│   │   └── 0006-configure-applications.hook.chroot
│   ├── bootloaders/              # Bootloader configuration
│   │   └── grub/
│   │       └── live.cfg          # GRUB boot menu
│   └── packages.list             # List of packages to install
│
├── scripts/                       # Build and utility scripts
│   ├── build.sh                  # Main ISO build script
│   └── generate-assets.sh        # Asset generation script
│
├── docs/                          # Documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── BUILDING.md               # Detailed build instructions
│   ├── TESTING.md                # Testing procedures
│   ├── ARCHITECTURE.md           # Technical architecture
│   └── PROJECT_STRUCTURE.md      # This file
│
├── build/                         # Build output directory (created during build)
│   └── *.iso                     # Generated ISO file
│
├── README.md                      # Main project README
└── LICENSE                        # License information
```

## Directory Descriptions

### assets/

Contains all visual assets and resources for Lunar OS.

#### assets/boot/plymouth/

Plymouth boot screen theme files:
- **lunar-os.plymouth**: Theme configuration file
- **lunar-os.script**: Animation script (Plymouth script language)
- **logo.svg**: SVG moon logo for boot screen

These files create the minimalist boot screen with the moon logo and loading animation.

#### assets/desktop/

Desktop-specific assets:
- **wallpaper.png**: Main desktop wallpaper (lunar gradient with moon)
- **welcome.py**: Python GTK3 application for the welcome window
- **welcome-icon.png**: Icon for the welcome window
- **shutdown-dialog.py**: Python GTK3 application for shutdown dialog
- **xfce4-panel.xml**: XFCE panel configuration
- **xfce4-xfconf.xml**: XFCE desktop settings
- **xfce4-appearance.xml**: XFCE appearance/theme settings
- **generate-wallpaper.py**: Script to generate the wallpaper
- **generate-logo.py**: Script to generate logo files

#### assets/icons/

Application icons in various sizes (populated by generate-logo.py).

### config/

Debian Live configuration files that control the ISO build process.

#### config/build/

Live-build configuration:
- **config**: Main configuration file with distribution, architecture, package selections, and build options

Key settings:
- Distribution: Debian 12 (bookworm)
- Desktop: XFCE
- Architecture: amd64
- ISO metadata

#### config/includes.chroot/

Files that will be copied into the live system's filesystem:

**etc/live/config.conf.d/**:
- **0000-lunar-live.conf**: Live-boot configuration
- **0001-disposable-storage.conf**: Disposable storage configuration (overlayfs with tmpfs)

**etc/skel/**: Default user configuration
- **.config/xfce4/**: XFCE desktop settings for new users

These files are copied to the live system during the build.

#### config/includes.binary/

Files to add directly to the ISO filesystem (currently empty).

#### config/packages.hook/

Build hooks that execute during the build process (in numerical order):

1. **0000-copy-assets.hook.chroot**: Copies visual assets to the chroot
2. **0001-install-plymouth-theme.hook.chroot**: Installs and configures Plymouth theme
3. **0002-configure-xfce.hook.chroot**: Configures XFCE desktop environment
4. **0003-install-welcome-app.hook.chroot**: Installs welcome window application
5. **0004-configure-shutdown.hook.chroot**: Configures custom shutdown dialog
6. **0005-configure-user.hook.chroot**: Configures user home directory and shortcuts
7. **0006-configure-applications.hook.chroot**: Configures application defaults

Hooks are shell scripts that execute at specific points during the build process.

#### config/bootloaders/

Bootloader configuration:
- **grub/live.cfg**: GRUB boot menu configuration with Lunar OS options

#### config/packages.list

List of Debian packages to install in the live system, including:
- Linux kernel
- Live system tools
- XFCE desktop
- Applications (Firefox, Thunar, etc.)
- System utilities

### scripts/

Executable scripts for building and asset generation.

#### scripts/build.sh

Main build script that:
- Checks dependencies
- Cleans previous builds
- Copies configuration
- Copies assets
- Runs live-build
- Reports results

Must be run as root.

#### scripts/generate-assets.sh

Generates visual assets:
- Runs Python scripts to create wallpaper and logos
- Creates SVG logo for Plymouth
- Copies assets to appropriate locations

Requires Python 3 and Pillow.

### docs/

Documentation files:
- **QUICKSTART.md**: Quick start guide for users
- **BUILDING.md**: Detailed build instructions
- **TESTING.md**: Testing procedures and checklist
- **ARCHITECTURE.md**: Technical architecture documentation
- **PROJECT_STRUCTURE.md**: This file

### build/

Build output directory (created during build):
- Contains the generated ISO file
- Temporary build artifacts
- Can be safely deleted and rebuilt

### Root Files

- **README.md**: Main project documentation
- **LICENSE**: MIT License for Lunar OS custom components

## File Purposes

### Configuration Files

**config/build/config**: Controls the entire build process
- Distribution and architecture
- Package selections
- Build options
- ISO metadata

**config/packages.list**: Defines software to install
- Core system packages
- Desktop environment
- Applications
- Utilities

### Custom Components

**assets/desktop/welcome.py**: First-boot welcome window
- Python GTK3 application
- Explains disposable concept
- Auto-starts on login

**assets/desktop/shutdown-dialog.py**: Custom shutdown dialog
- Python GTK3 application
- Warns about data loss
- Handles shutdown/restart

**assets/boot/plymouth/**: Boot screen
- Custom Plymouth theme
- Moon logo
- Loading animation

### Build System

**scripts/build.sh**: Orchestrates the build
- Validates environment
- Prepares build directory
- Executes live-build
- Reports results

**config/packages.hook/**: Customization hooks
- Execute during build
- Install custom components
- Configure system
- Apply settings

## Build Flow

1. **Asset Generation** (scripts/generate-assets.sh)
   - Creates wallpaper, logos, icons
   - Outputs to assets/

2. **Build Preparation** (scripts/build.sh)
   - Copies config/build/config
   - Copies packages.list
   - Copies includes.chroot/
   - Copies hooks
   - Copies assets to chroot_local-includes/

3. **Live-Build Execution** (lb build)
   - Runs debootstrap
   - Installs packages
   - Executes hooks (in order)
   - Creates squashfs
   - Generates initramfs
   - Configures GRUB
   - Creates ISO

4. **Output**
   - ISO file in build/
   - Ready to test or distribute

## Customization Guide

### Changing Visuals

1. **Wallpaper**: Edit assets/desktop/wallpaper.png or regenerate with modified generate-wallpaper.py
2. **Logo**: Edit assets/desktop/generate-logo.py and regenerate
3. **Boot Screen**: Edit assets/boot/plymouth/lunar-os.script

### Changing Software

1. **Add packages**: Edit config/packages.list
2. **Remove packages**: Remove from config/packages.list
3. **Configure apps**: Edit or add hooks in config/packages.hook/

### Changing Desktop

1. **Panel**: Edit assets/desktop/xfce4-panel.xml
2. **Settings**: Edit assets/desktop/xfce4-*.xml
3. **Shortcuts**: Edit config/includes.chroot/etc/skel/.config/xfce4/

### Changing Behavior

1. **Storage**: Edit config/includes.chroot/etc/live/config.conf.d/0001-disposable-storage.conf
2. **Boot**: Edit config/bootloaders/grub/live.cfg
3. **Auto-start**: Edit or add autostart entries in hooks

## File Formats

### Configuration Files

- **config/build/config**: Shell variable assignments
- **config/packages.list**: Plain text package list
- **XML files**: XFCE and GRUB configurations
- **Live config**: Key-value pairs

### Scripts

- **Shell scripts** (.sh): Bash scripts
- **Python scripts** (.py): Python 3 with GTK3
- **Plymouth script**: Plymouth-specific language

### Assets

- **PNG**: Raster images (wallpaper, icons)
- **SVG**: Vector graphics (boot logo)
- **Font files**: If custom fonts are added

## Dependencies

### Build-Time Dependencies

- **live-build**: Build system
- **debootstrap**: Debian bootstrap tool
- **Python 3**: For asset generation
- **Pillow**: Python image library

### Runtime Dependencies

- **linux-image-amd64**: Linux kernel
- **live-boot**: Live system support
- **xfce4**: Desktop environment
- **python3-gi**: Python GTK bindings
- **plymouth**: Boot screen

## Version Control

### What to Track

- All configuration files
- All scripts
- All source code
- Documentation
- Asset generation scripts

### What NOT to Track

- Generated assets (regenerate from scripts)
- build/ directory (generated during build)
- Binary files (except assets)
- Temporary files

### Git Ignore Example

```
build/
*.iso
assets/desktop/*.png
assets/desktop/logo-*.png
assets/boot/plymouth/*.png
.DS_Store
*~
```