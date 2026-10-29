# Architecture

## Base

Debian 12 (bookworm) Live built with live-build. The kernel and bootloader come from Debian. BIOS boots through syslinux and UEFI through grub-efi.

## Disposable storage

live-boot mounts the compressed system image read-only and stacks a writable overlay in RAM. No persistence is configured. Nothing written during a session reaches the ISO or local disks.

Additional measures in hook `0008-harden-session`:

- GPT swap auto-detection disabled and `swap.target` masked
- Hibernate and hybrid-sleep targets masked
- `/etc/fstab` swap entries removed

Journald uses volatile storage and core dumps are disabled.

Session storage is bounded by RAM. The tray session monitor reports usage and warns when storage passes 85 percent or available memory falls below about 150 MB.

## Boot

1. syslinux or grub-efi loads the kernel and initramfs (menu splash from `config/bootloaders`)
2. Plymouth shows the Lunar boot screen, relaying real boot messages
3. live-boot assembles the overlay
4. live-config creates the `lunar` user from `/etc/skel` and enables autologin
5. LightDM starts the LXDE session
6. Autostart launches picom, dunst, the session monitor and the welcome window

## Desktop

LXDE session with Openbox, lxpanel and PCManFM. picom provides shadows and rounded corners. The Lunar Openbox theme and the Adwaita-dark GTK theme with a violet accent give the visual identity.

## Shutdown

`lxsession-logout` and `lxde-logout` are diverted to a wrapper that opens the Lunar dialog, so the panel, menu and shortcuts all use it. Shut down and restart call `systemctl`, and polkit rules allow them for the live user. Logging out ends the login session only.

## Applications

`welcome.py`, `shutdown-dialog.py`, `lunar-settings.py` and `lunar-session-monitor.py` are GTK 3 programs installed in `/usr/share/lunar-os`.

## Build

`scripts/build.sh` runs `lb config`, copies the project's `config/` directories into the build tree, copies assets into `includes.chroot/tmp/lunar-assets` and runs `lb build`. Hook `0900` fails the build if the desktop is missing.
