# Lunar OS Architecture

This document describes the technical architecture of Lunar OS.

## Overview

Lunar OS is a Linux-based operating system designed for disposable sessions. It uses Debian Live as the base, customized with a lightweight desktop environment (XFCE), custom branding, and a RAM-based overlay filesystem for complete data disposability.

## System Components

### Base System

**Distribution**: Debian 12 (Bookworm)
- Stable, well-supported
- Extensive package repository
- Security updates available
- Long-term support

**Architecture**: x86_64 (amd64)
- Modern 64-bit processors
- Widespread hardware support
- Good performance

**Kernel**: Linux (from Debian)
- linux-image-amd64
- Non-free firmware included for hardware support

### Live System Framework

**Live-Boot**: Provides live system functionality
- Boot from ISO/USB without installation
- Overlay filesystem support
- Network configuration
- Hardware detection

**Live-Config**: Configures the live system
- Auto-login setup
- Hostname configuration
- User creation
- System settings

**Live-Build**: Build system for creating the ISO
- Automates ISO creation
- Package management
- Hook system for customization
- Reproducible builds

### Desktop Environment

**XFCE**: Lightweight desktop environment
- Fast and responsive
- Low resource usage
- Highly customizable
- Traditional desktop metaphor

**Components**:
- xfce4-panel: Taskbar/dock
- xfce4-terminal: Terminal emulator
- thunar: File manager
- xfdesktop: Desktop manager
- xfwm4: Window manager
- xfsettings: Settings manager
- whiskermenu-plugin: Application launcher

### Boot Process

```
1. BIOS/UEFI
   ↓
2. GRUB Bootloader
   - Loads kernel
   - Loads initramfs
   - Passes boot parameters
   ↓
3. Linux Kernel
   - Initializes hardware
   - Mounts root filesystem
   - Starts init system
   ↓
4. Plymouth Boot Screen
   - Displays Lunar OS branding
   - Shows loading animation
   - Hides kernel messages
   ↓
5. Live-Boot Scripts
   - Detects live media
   - Sets up overlayfs
   - Configures tmpfs
   - Mounts filesystems
   ↓
6. Systemd Init System
   - Starts services
   - Configures system
   - Initializes hardware
   ↓
7. LightDM Display Manager
   - Auto-login to user account
   - Starts X server
   ↓
8. XFCE Desktop Session
   - Loads desktop environment
   - Applies settings
   - Starts panel
   ↓
9. Welcome Window
   - Python GTK3 application
   - Displays automatically
   - Introduces disposable concept
   ↓
10. Ready-to-use Desktop
```

## Disposable Session Architecture

### Filesystem Layout

```
/ (root)
├── /bin, /sbin, /lib          - Read-only from ISO (squashfs)
├── /usr                      - Read-only from ISO (squashfs)
├── /etc                      - Read-only from ISO (squashfs)
├── /ro (read-only)           - Base system from ISO
├── /rw (read-write)          - tmpfs overlay in RAM
└── overlayfs                 - Union of /ro and /rw
```

### OverlayFS Implementation

Lunar OS uses overlayfs to combine the read-only base system with a writable overlay:

**Lower Layer** (Read-only):
- Source: squashfs from ISO
- Location: /ro (mounted during boot)
- Contains: Base system, applications, configurations
- Properties: Cannot be modified, persists across reboots

**Upper Layer** (Writeable):
- Source: tmpfs (RAM)
- Location: /rw
- Contains: User data, settings, caches, temporary files
- Properties: Can be modified, discarded on shutdown

**Merged Layer**:
- Source: overlayfs union
- Location: / (root filesystem)
- Properties: Read from lower, write to upper
- Behavior: Appears as normal filesystem

### Boot Parameters

The system boots with these key parameters:

```
boot=live              - Enable live-boot
components             - Load all live components
noprompt               - Don't prompt for input
quiet                  - Suppress kernel messages
splash                 - Enable Plymouth boot screen
overlay=tmpfs          - Use tmpfs for overlay (RAM-based)
noeject                - Don't require media eject before shutdown
```

### RAM Usage

**Base System**: ~500-800 MB (compressed in squashfs)
**Overlay**: Variable, depending on usage
  - Minimum: ~200 MB for basic usage
  - Typical: 500 MB - 2 GB
  - Maximum: Limited by available RAM

**Total RAM Requirements**:
- Minimum: 2 GB (tight)
- Recommended: 4 GB (comfortable)
- Optimal: 8 GB (plenty of headroom)

### Data Flow

**Writing Data**:
1. Application writes to filesystem
2. overlayfs intercepts write
3. Data goes to upper layer (tmpfs)
4. Data stored in RAM
5. Lower layer unchanged

**Reading Data**:
1. Application reads from filesystem
2. overlayfs checks upper layer first
3. If data exists in upper, return it
4. If not, read from lower layer
5. Data from lower layer unchanged

**Shutdown**:
1. System receives shutdown signal
2. Applications are closed
3. Filesystems are unmounted
4. tmpfs is cleared (RAM released)
5. No data written to disk
6. System powers off

## Custom Components

### Plymouth Boot Screen

**Location**: `/usr/share/plymouth/themes/lunar-os/`

**Files**:
- `lunar-os.plymouth` - Theme configuration
- `lunar-os.script` - Animation script
- `logo.svg` - Moon logo

**Features**:
- Minimalist design
- Moon logo centered
- Animated loading indicator
- Status messages
- Lunar color scheme

**Implementation**:
- Plymouth script language
- Draws to framebuffer
- Runs before X server
- Replaced by X server when ready

### Welcome Window

**Location**: `/usr/share/lunar-os/welcome.py`

**Technology**: Python 3 + GTK3

**Features**:
- Automatic display on login
- Modal dialog window
- Lunar OS branding
- Explanation of disposable concept
- "Start Session" button
- Dark theme styling

**Integration**:
- Autostart via `/etc/xdg/autostart/lunar-welcome.desktop`
- Runs after XFCE loads
- Closes on button click
- Does not restart the system

### Shutdown Dialog

**Location**: `/usr/share/lunar-os/shutdown-dialog.py`

**Technology**: Python 3 + GTK3

**Features**:
- Custom shutdown dialog
- Session discard warning
- List of data to be discarded
- Restart and shutdown options
- Confirmation required

**Integration**:
- Wrapper scripts in `/usr/local/bin/`
- Polkit policy for no-password shutdown
- Replaces default XFCE logout dialog

### Desktop Configuration

**XFCE Panel**: `/etc/xdg/xfce4/panel/default.xml`
- Bottom position
- Whisker menu launcher
- Task list
- System tray
- Clock

**Desktop Settings**: `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/`
- Lunar OS wallpaper
- Dark theme (Adwaita-dark)
- Custom fonts
- Window decorations

**User Settings**: `/etc/skel/`
- Default user configuration
- Desktop shortcuts
- Keyboard shortcuts
- Application preferences

## Application Configuration

### Firefox

**Configuration**: `/etc/firefox-esr/syspref.js`

**Settings**:
- Private browsing mode enabled
- Tracking protection enabled
- No disk cache (RAM only)
- Downloads to /home/lunar/Downloads
- No session restore

**Privacy Benefits**:
- No browsing history saved
- No cookies persisted
- No cache on disk
- Isolated session

### Thunar (File Manager)

**Configuration**: `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/thunar.xml`

**Settings**:
- Icon view by default
- 100% zoom level
- Specific column widths
- Show hidden files off

### XFCE Terminal

**Configuration**: `/etc/xdg/xfce4/terminal/terminalrc`

**Settings**:
- Monospace font
- 80x24 default size
- Cursor shape: block
- No toolbar by default

## Security Architecture

### Data Disposability

**What IS Discarded**:
- Files in /home/lunar
- Desktop files
- Downloads
- Application settings
- Browser history/cookies
- Terminal history
- Temporary files
- Caches

**What IS NOT Discarded**:
- Base system files (in ISO)
- System libraries
- Built-in applications
- Hardware state (CPU memory)
- Network logs (on router)
- Files copied to external media

### Persistence Prevention

**Mechanisms**:
1. **tmpfs overlay**: All writes go to RAM
2. **No swap**: Swap disabled to prevent disk writes
3. **No persistent mounts**: No disk partitions mounted
4. **Live-boot configuration**: Explicitly sets no persistence
5. **Overlay size limit**: Prevents filling disk

**Verification**:
```bash
mount | grep overlay    # Should show overlayfs
mount | grep tmpfs      # Should show tmpfs
swapon -s               # Should be empty
```

### Limitations

**NOT Secure Against**:
- Physical memory extraction (cold boot attacks)
- Hypervisor snooping (in VMs)
- Network traffic interception
- Screen capture
- Physical inspection
- Forensic recovery of RAM

**Security Level**:
- Disposable storage: YES
- Anti-forensic: NO
- Network privacy: NO (use VPN/Tor)
- Anti-virus: NO (use at your own risk)

## Build Architecture

### Build Process

```
1. Asset Generation
   - Python scripts generate wallpaper, logos
   - SVG and PNG files created
   ↓
2. Configuration Setup
   - Live-build config files copied
   - Package lists defined
   - Hooks configured
   ↓
3. Chroot Setup
   - debootstrap creates base system
   - Packages installed
   - Custom files added
   ↓
4. Hook Execution
   - Assets copied
   - Plymouth configured
   - XFCE configured
   - Applications configured
   ↓
5. Image Creation
   - squashfs created from chroot
   - initramfs generated
   - GRUB configured
   ↓
6. ISO Assembly
   - All components combined
   - ISO file created
   - Checksum generated
```

### Hook System

Live-build hooks allow customization at specific points:

**Hooks in Lunar OS**:
1. `0000-copy-assets.hook.chroot` - Copy visual assets
2. `0001-install-plymouth-theme.hook.chroot` - Configure boot screen
3. `0002-configure-xfce.hook.chroot` - Configure desktop
4. `0003-install-welcome-app.hook.chroot` - Install welcome window
5. `0004-configure-shutdown.hook.chroot` - Configure shutdown dialog
6. `0005-configure-user.hook.chroot` - Configure user home
7. `0006-configure-applications.hook.chroot` - Configure applications

**Hook Execution Order**:
- Numerical prefix determines order
- Chroot hooks run inside the chroot
- Binary hooks run outside the chroot

### Package Management

**Sources**:
- Debian main repository
- Debian contrib repository
- Debian non-free repository
- Debian non-free-firmware repository

**Package Selection**:
- Lightweight by default
- Essential functionality only
- No bloatware
- Well-maintained packages

## Performance Characteristics

### Boot Performance

**Typical Times**:
- BIOS/UEFI: 5-10 seconds
- GRUB: 2-3 seconds
- Kernel init: 10-15 seconds
- Plymouth animation: 10-20 seconds
- Service startup: 10-15 seconds
- Desktop load: 5-10 seconds
- **Total**: 40-70 seconds

**Optimizations**:
- Minimal service set
- Parallel service startup
- Fast filesystem (squashfs)
- Minimal boot parameters

### Runtime Performance

**Memory Usage**:
- Base system: 400-500 MB
- XFCE desktop: 100-150 MB
- Applications: Variable
- **Idle total**: 500-700 MB

**CPU Usage**:
- Idle: < 5%
- Light usage: 10-20%
- Heavy usage: 50-80%

**Disk I/O**:
- Reads: From ISO (cached in RAM)
- Writes: To RAM (tmpfs)
- No disk writes after boot

### Scalability

**Concurrent Users**: Not designed for multi-user
**Network Load**: Typical desktop usage
**Application Load**: Limited by RAM
**File I/O**: Limited by RAM

## Customization Points

### Easy Customizations

1. **Wallpaper**: Replace `assets/desktop/wallpaper.png`
2. **Logo**: Replace generated logos in `assets/desktop/`
3. **Packages**: Edit `config/packages.list`
4. **Desktop settings**: Edit XFCE XML configs
5. **Welcome text**: Edit `assets/desktop/welcome.py`

### Advanced Customizations

1. **Kernel**: Custom kernel in chroot
2. **Boot screen**: Modify Plymouth scripts
3. **Desktop environment**: Switch to GNOME/KDE
4. **Applications**: Add/remove as needed
5. **Storage architecture**: Different overlay options

## Troubleshooting Architecture

### Debug Information Locations

**Boot Logs**:
- `/var/log/boot.log` - Boot process
- `/var/log/dmesg` - Kernel messages
- `/var/log/syslog` - System logs

**Desktop Logs**:
- `~/.xsession-errors` - X session errors
- `/var/log/Xorg.0.log` - X server logs

**Application Logs**:
- Application-specific log files
- System journal (systemd)

### Common Failure Points

1. **Overlay setup**: tmpfs initialization
2. **Graphics driver**: Plymouth/X startup
3. **User creation**: Live-config
4. **Desktop load**: XFCE configuration
5. **Application launch**: Python/GTK dependencies

## Future Architecture Considerations

### Potential Improvements

1. **Compression**: zstd for faster squashfs
2. **ZRAM**: Compressed RAM for overlay
3. **Caching**: Persistent package cache
4. **Persistence**: Optional persistence layer
5. **Updates**: Live system updates
6. **Security**: Hardening measures

### Expansion Possibilities

1. **Different architectures**: ARM support
2. **Different desktops**: MATE, Cinnamon
3. **Cloud images**: For cloud platforms
4. **Container version**: For Docker/Podman
5. **Headless version**: For servers
