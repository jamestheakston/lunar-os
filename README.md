# Lunar OS

A disposable desktop operating system built on Debian 12 (bookworm) Live. Every boot starts a fresh session. Files, settings and downloads live in RAM and are discarded when the computer shuts down or restarts.

**Status:** all source, configuration and build scripts are in place. The ISO has not been built or booted by the author yet. See `docs/STATUS.md` for exactly what has and has not been tested.

## Features

- Debian Live base with a read-only system image and a RAM-backed writable layer
- Custom Plymouth boot screen: moon logo, LUNAR OS title, animated indicator and live boot messages
- LXDE desktop with Openbox, a dark Lunar theme, a violet accent and optional light mode
- Bottom panel with launcher menu, quick-launch buttons, taskbar, system tray (network, sound, battery, session status), date and clock, and a Shut Down button
- Window dragging, resizing, minimising, maximising and closing, with compositor shadows and rounded corners
- Right-click desktop menu and desktop shortcuts
- Notifications (dunst)
- Welcome window on every boot with a "Start session" button
- Custom shutdown dialog: Shut Down and Discard Session, Restart and Start Fresh, Log Out, Cancel
- Lunar Settings: dark/light mode, wallpaper, and shortcuts to display, sound, network, keyboard, mouse and startup tools
- Applications: PCManFM (files), Mousepad (text editor), LXTerminal, Firefox ESR, Galculator, GPicView, LXTask (system monitor)

## Keyboard shortcuts

| Keys | Action |
|---|---|
| Super+T or Ctrl+Alt+T | Terminal |
| Super+B | Web browser |
| Super+E | File manager (LXDE default) |
| Super+I | Lunar Settings |
| Super+C | Calculator |
| Ctrl+Shift+Esc | System monitor |
| Super+Q | Shut down dialog |
| Super+D | Show desktop |
| Super+Up / Super+Down | Maximise / minimise |
| Alt+F4 | Close window |

## System requirements

- Build machine: Debian 12 or a Debian container, root access, 15 GB free disk, internet connection
- Run: 64-bit x86 computer or VM, BIOS or UEFI (Secure Boot not supported), 2 GB RAM minimum and 4 GB recommended

## Building the ISO

### GitHub Actions

Push to `main` or run the **Build Lunar OS ISO** workflow manually. The workflow builds the ISO, checks that the desktop is inside the image and uploads the ISO and checksum as artifacts.

### Local build

```bash
sudo ./scripts/install-deps.sh
./scripts/generate-assets.sh
sudo ./scripts/build.sh
```

The ISO is written to `build/live-image-amd64.hybrid.iso` and the log to `lunar-build.log`.

## Testing

```bash
qemu-system-x86_64 -m 4096 -enable-kvm -cdrom build/live-image-amd64.hybrid.iso -boot d
```

In VirtualBox create a Debian 64-bit VM with at least 2 GB RAM, no virtual disk, and attach the ISO. See `docs/TESTING.md` for the full checklist.

## Writing to a USB drive

```bash
lsblk
sudo dd if=build/live-image-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

Replace `/dev/sdX` with the USB device. This erases it. On Windows use Rufus in DD mode or balenaEtcher.

## How the disposable session works

- live-boot mounts the compressed system image read-only and layers a RAM filesystem (overlayfs on tmpfs) on top. Every write goes to RAM.
- The ISO and any disk in the computer are never written by normal use.
- Power loss or a crash leaves the ISO unchanged, because nothing was ever committed to it.
- Boot hardening: swap and hibernation targets and GPT swap auto-detection are disabled, the journal is kept in memory and core dumps are disabled.
- The session status icon in the tray shows RAM and session storage use and warns when memory runs low.
- **Shut down and restart** discard the session. **Log out** keeps session files in RAM until the next shutdown or restart, and the login screen signs you straight back in.

## Limitations

- Session storage is limited by RAM. A system with 2 GB can hold little beyond the desktop and a browser.
- Disposable storage reduces persistence. It cannot remove data you copied to external drives or cloud services, data sent over a network, data retained by hardware, or RAM contents that linger briefly after power-off. It is not forensic-grade secure erasure.
- Theme changes in Lunar Settings apply to windows opened afterwards.
- No installer and no persistence by design.
- Non-free firmware is included for hardware support.

## Project layout

See `docs/PROJECT_STRUCTURE.md`. Architecture notes are in `docs/ARCHITECTURE.md`.

## License

See `LICENSE`.
