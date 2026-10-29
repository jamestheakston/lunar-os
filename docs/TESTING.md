# Testing Lunar OS

This document describes how to test Lunar OS after building the ISO.

## Testing in Virtual Machines

### Using QEMU (Linux/Unix)

#### Installation

On Debian/Ubuntu:
```bash
sudo apt-get install qemu-kvm qemu-utils
```

On Fedora:
```bash
sudo dnf install qemu-kvm qemu-tools
```

#### Basic Test

```bash
cd lunar-os
qemu-system-x86_64 -m 2048 -cdrom build/*.iso -boot d
```

#### With KVM (Better Performance)

```bash
qemu-system-x86_64 -enable-kvm -m 2048 -cdrom build/*.iso -boot d
```

#### With More Options

```bash
qemu-system-x86_64 \
    -enable-kvm \
    -m 4096 \
    -smp 2 \
    -cdrom build/*.iso \
    -boot d \
    -net nic,model=virtio \
    -net user \
    -vga virtio \
    -display gtk
```

Options:
- `-m 4096`: 4 GB RAM
- `-smp 2`: 2 CPU cores
- `-net nic,model=virtio`: Virtio network driver
- `-vga virtio`: Virtio graphics

### Using VirtualBox

#### Create VM

1. Open VirtualBox
2. Click "New"
3. Name: "Lunar OS Test"
4. Type: Linux
5. Version: Debian (64-bit)
6. RAM: 2048 MB or more
7. Create a virtual disk (you can skip this for live boot)
8. Settings → Storage → Controller: IDE → Empty → Choose disk
9. Select the Lunar OS ISO file
10. Start the VM

#### VirtualBox Settings

For better performance:
- System → Motherboard → Enable I/O APIC
- System → Processor → 2+ CPUs
- System → Acceleration → Enable VT-x/AMD-V
- Display → Graphics Controller: VMSVGA
- Display → Video Memory: 128 MB

### Using VMware

#### Create VM

1. Create new VM
2. Select "Linux" as guest OS
3. Version: Debian 12 64-bit
4. RAM: 2048 MB or more
5. Disk: 20 GB (not used for live boot, but required)
6. Mount ISO as CD/DVD
7. Start VM

## Testing Checklist

### Boot Test

- [ ] ISO boots successfully
- [ ] GRUB menu appears with Lunar OS options
- [ ] Plymouth boot screen displays with moon logo
- [ ] Loading animation is visible
- [ ] No kernel panics or error messages
- [ ] System reaches graphical login

### Welcome Window Test

- [ ] Desktop loads automatically
- [ ] Welcome window appears automatically
- [ ] Welcome window displays correct title: "Welcome to Lunar OS"
- [ ] Moon logo/icon is visible
- [ ] Description text is correct
- [ ] "Start Session" button is present
- [ ] Clicking "Start Session" closes the window
- [ ] Desktop is revealed after closing welcome window
- [ ] No applications crash on startup

### Desktop Environment Test

- [ ] Wallpaper displays correctly (lunar gradient with moon)
- [ ] Taskbar appears at bottom
- [ ] Application launcher (moon icon) is visible
- [ ] System tray is visible
- [ ] Clock displays correct time
- [ ] Desktop shortcuts are present
- [ ] Right-click context menu works
- [ ] Windows can be dragged
- [ ] Windows can be resized
- [ ] Windows can be minimized
- [ ] Windows can be maximized
- [ ] Windows can be closed

### Application Tests

#### File Manager (PCManFM)

- [ ] File manager opens from launcher
- [ ] Home directory is displayed
- [ ] Desktop folder is accessible
- [ ] Documents folder is accessible
- [ ] Downloads folder is accessible
- [ ] Pictures folder is accessible
- [ ] Music folder is accessible
- [ ] Videos folder is accessible
- [ ] Can create new folder
- [ ] Can create new file
- [ ] Can rename files/folders
- [ ] Can copy files
- [ ] Can move files
- [ ] Can delete files
- [ ] Search function works
- [ ] Breadcrumb navigation works

#### Terminal

- [ ] Terminal opens from launcher
- [ ] Command prompt is visible
- [ ] Can execute commands
- [ ] Can navigate directories
- [ ] Can create files
- [ ] Can edit files with vim/nano
- [ ] Copy/paste works

#### Web Browser (Firefox)

- [ ] Firefox opens from launcher
- [ ] Private browsing mode is active
- [ ] Can navigate to websites
- [ ] Can download files
- [ ] Downloads go to Downloads folder
- [ ] Bookmarks work during session
- [ ] History is not saved (test after restart)

#### Text Editor (Mousepad)

- [ ] Text editor opens from launcher
- [ ] Can create new document
- [ ] Can type text
- [ ] Can save file
- [ ] Can open existing file
- [ ] Can edit file
- [ ] Font rendering is correct

#### Calculator (Galculator)

- [ ] Calculator opens from launcher
- [ ] Basic arithmetic works
- [ ] Clear button works
- [ ] Display shows correct results

#### Image Viewer (GPicView)

- [ ] Image viewer opens from launcher
- [ ] Can open image files
- [ ] Can zoom in/out
- [ ] Can navigate images in folder
- [ ] Fullscreen mode works

#### System Monitor

- [ ] System monitor opens from launcher
- [ ] CPU usage is displayed
- [ ] Memory usage is displayed
- [ ] Process list is visible
- [ ] Can end processes

#### Settings

- [ ] Settings manager opens
- [ ] Can change wallpaper
- [ ] Can change theme
- [ ] Can change fonts
- [ ] Can configure network
- [ ] Can configure sound
- [ ] Can configure power management

### Disposable Session Test

#### Create Session Data

- [ ] Create file in home directory
- [ ] Create file on desktop
- [ ] Download file to Downloads
- [ ] Create bookmark in browser
- [ ] Change desktop wallpaper
- [ ] Create terminal command history
- [ ] Change application settings

#### Shutdown Test

- [ ] Shutdown dialog appears
- [ ] "Shut Down and Discard Session" option is present
- [ ] Confirmation message explains data loss
- [ ] Confirming shutdown closes applications
- [ ] System powers off completely

#### Restart Test

- [ ] Restart dialog appears
- [ ] "Restart and Start Fresh" option is present
- [ ] Confirmation message explains data loss
- [ ] System reboots

#### Persistence Test

After shutdown/restart:
- [ ] Welcome window appears again
- [ ] Files created in previous session are gone
- [ ] Downloads are gone
- [ ] Bookmarks are gone
- [ ] Wallpaper is reset to default
- [ ] Settings are reset to defaults
- [ ] Browser history is empty
- [ ] Desktop is clean

### Network Test

- [ ] Network connection is detected
- [ ] Wired network works (if available)
- [ ] Wireless network works (if available)
- [ ] Can access internet
- [ ] Can ping external hosts
- [ ] DNS resolution works

### Audio Test

- [ ] Sound device is detected
- [ ] Volume control works
- [ ] Can play audio files
- [ ] Volume indicator in tray works

### USB Device Test

- [ ] USB drives are detected when plugged in
- [ ] Can mount USB drives
- [ ] Can read from USB drives
- [ ] Can write to USB drives
- [ ] Can copy files to/from USB drives
- [ ] USB drives can be safely ejected

### Performance Test

- [ ] System boots in reasonable time (< 2 minutes)
- [ ] Desktop is responsive
- [ ] Applications open quickly
- [ ] No excessive CPU usage when idle
- [ ] Memory usage is reasonable (check with system monitor)
- [ ] No swap thrashing

### Compatibility Test

Test on different hardware if possible:
- [ ] Works on Intel CPU
- [ ] Works on AMD CPU
- [ ] Works with UEFI firmware
- [ ] Works with BIOS firmware
- [ ] Works with different graphics cards (Intel, AMD, NVIDIA)

## Automated Testing

### Boot Script

Create a script to automate basic tests:

```bash
#!/bin/bash
# Basic Lunar OS test script

echo "=== Lunar OS Test Suite ==="

# Test 1: Check welcome window exists
if [ -f /usr/share/lunar-os/welcome.py ]; then
    echo "PASS: Welcome application exists"
else
    echo "FAIL: Welcome application missing"
fi

# Test 2: Check shutdown dialog exists
if [ -f /usr/share/lunar-os/shutdown-dialog.py ]; then
    echo "PASS: Shutdown dialog exists"
else
    echo "FAIL: Shutdown dialog missing"
fi

# Test 3: Check wallpaper exists
if [ -f /usr/share/backgrounds/lunar-os/wallpaper.png ]; then
    echo "PASS: Wallpaper exists"
else
    echo "FAIL: Wallpaper missing"
fi

# Test 4: Check user home directory
if [ -d /home/lunar ]; then
    echo "PASS: User home directory exists"
else
    echo "FAIL: User home directory missing"
fi

# Test 5: Check overlayfs is in use
if mount | grep overlay; then
    echo "PASS: overlayfs is mounted"
else
    echo "FAIL: overlayfs not mounted"
fi

# Test 6: Check tmpfs is in use
if mount | grep tmpfs; then
    echo "PASS: tmpfs is mounted"
else
    echo "FAIL: tmpfs not mounted"
fi

echo "=== Test Complete ==="
```

Run this script in the terminal after booting Lunar OS.

## Common Issues and Solutions

### Black Screen After Boot

**Cause**: Graphics driver issue

**Solution**: Try the "Safe Graphics" boot option

### Welcome Window Doesn't Appear

**Cause**: Python 3 or GTK3 missing

**Solution**: Check installation in terminal:
```bash
python3 --version
python3 -c "import gi; gi.require_version('Gtk', '3.0')"
```

### System Runs Out of RAM

**Cause**: tmpfs filled up

**Solution**: Increase RAM allocation in VM or reduce usage

### Network Not Working

**Cause**: Driver missing or configuration issue

**Solution**: Check network manager status and try manual configuration

### USB Boot Fails

**Cause**: Corrupted ISO or bad USB write

**Solution**: Rebuild ISO and rewrite to USB using dd

## Reporting Bugs

When reporting bugs, include:

1. System specifications (CPU, RAM, GPU)
2. ISO version/build date
3. Detailed steps to reproduce
4. Expected behavior
5. Actual behavior
6. Screenshots if applicable
7. Logs from `/var/log/`

## Performance Benchmarks

Typical performance metrics (to be verified during testing):

- **Boot time**: 30-60 seconds
- **Idle memory usage**: 400-600 MB
- **Idle CPU usage**: < 5%
- **Time to open file manager**: 1-2 seconds
- **Time to open browser**: 2-3 seconds

## Continuous Integration

For automated CI/CD testing, consider:

1. Using Packer to automate VM creation
2. Using scripts to run automated tests
3. Capturing screenshots and logs
4. Running tests on multiple platforms

## Security Testing

If performing security testing:

- [ ] Verify no data persists after shutdown (check with file recovery tools)
- [ ] Verify swap is disabled
- [ ] Verify no persistent mounts are created
- [ ] Verify tmpfs is actually used for /home
- [ ] Verify network isolation in VM
