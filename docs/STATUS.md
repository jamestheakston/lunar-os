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
