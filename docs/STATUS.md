# Project Status

Last updated 2026-10-28.

The ISO has not been built or booted by the author. Nothing below is marked as tested unless it says so.

## Verified so far

- Shell scripts and hooks pass `bash -n` syntax checks.
- Python applications parse and compile.
- `scripts/build.sh` ran end to end against a stand-in `lb`: configuration sync, asset copying and hook permissions behaved as intended.
- A GitHub Actions run reached the package-list stage of live-build before the fixes in this version.

## Implemented, not yet tested on a real ISO

| Requirement | Implementation |
|---|---|
| Disposable session | live-boot RAM overlay; swap, hibernate and persistent journal disabled in `0008` hook |
| Boot screen | Plymouth script theme `lunar-os`; boot menu splash for syslinux and grub |
| Desktop | LXDE, Openbox theme `Lunar`, lxpanel panel config, picom shadows and rounded corners |
| Welcome window | `welcome.py`, autostarted, remembers dismissal per boot |
| Shutdown dialog | `shutdown-dialog.py`, wired to the panel button, menu logout and Super+Q |
| Notifications | dunst with Lunar styling |
| Settings app | `lunar-settings.py` |
| Session status and low-RAM warnings | `lunar-session-monitor.py` |
| File manager, editor, terminal, calculator, image viewer, system monitor, browser | PCManFM, Mousepad, LXTerminal, Galculator, GPicView, LXTask, Firefox ESR |
| Dark default and light mode | GTK Adwaita-dark by default; toggle in Lunar Settings |

## Not yet run

The ten checks from the project brief: graphical boot, welcome window on every boot, Start session, file operations, application launch, settings, shutdown discards data, restart gives a clean session, VM resource use, no writes to the base system.

## Known risks to check first

- Plymouth script syntax and font rendering inside the initramfs.
- Whether the syslinux and grub splash images replace the defaults.
- lxpanel plugin names and options on bookworm.
- Whether `picom` starts in the target VM.
- Theme changes only affect newly opened windows.

## Boot speed and boot screen (2026-10-29)

First real ISO booted to the desktop. Boot was slow and the Plymouth screen did not show. Changes made in response, not yet tested: zstd squashfs compression, only selected firmware packages instead of the full set, smaller font package, slow wait services masked, Plymouth installed with `plymouth-set-default-theme`, shorter device timeout and `plymouth.use-simpledrm` on the kernel command line.

## Desktop tidy-up (2026-10-29)

Changes made after the first boot test, not yet tested: Firefox always launches in a private window and is the only browser, desktop shortcuts launch without the "Execute File?" prompt (libfm `quick_exec`), the desktop shows five shortcuts including Lunar Settings, the Lunar wallpaper is set in the user profile, the original distribution's artwork packages and branding text are removed or replaced.

## Login screen (2026-10-29)

Boot autologins straight to the desktop. After logging out, `lunar-greeter.py` (a LightDM greeter) shows one Log In button; if it fails to start, `lunar-greeter` falls back to the standard GTK greeter. Not yet tested.

## Start menu, apps and file manager (2026-10-29)

Changes made after the first boot tests, not yet tested on a real ISO:

- `lunar-start7.py` is a new Windows 7 style start menu: pinned programs, All Programs, live search, places and tools on the right, and a Shut down button with a Restart and Log off menu. A start orb button replaces the old LXDE menu in the panel, and Ctrl+Esc opens it. Earlier it was never installed or added to the panel.
- Lunar Store was crashing on startup (it read the installed package list before it existed and used the wrong widget index). It is rewritten with a dark theme, background installs with an `apt-get update` first, and an installation details panel.
- Lunar Settings, Lunar Store and the Start menu write start-up errors to `/tmp/lunar-*-error.log`.
- `shutdown-dialog.py` was missing the `GLib` import.
- File manager look: Arc-Dark theme, Papirus-Dark icons, larger icons, breadcrumb path bar, status bar and roomier lists.
