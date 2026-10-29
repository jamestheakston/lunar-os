# Project Structure

```
lunar-os/
├── .github/workflows/build-iso.yml   CI build, desktop verification, artifacts
├── assets/
│   ├── boot/
│   │   ├── generate-bootsplash.py    Writes boot menu splash images
│   │   └── plymouth/                 Boot screen theme (script, logo, dot)
│   └── desktop/                      Wallpaper, logos, Python applications,
│                                     Openbox keybindings
├── config/
│   ├── package-lists/lunar.list.chroot   Packages installed in the image
│   ├── hooks/normal/                 Chroot hooks, run in numeric order
│   ├── includes.chroot/              Files copied into the image
│   ├── includes.binary/              Files copied onto the ISO
│   └── bootloaders/                  syslinux and grub splash overrides
├── docs/
├── scripts/
│   ├── install-deps.sh               Installs build dependencies
│   ├── generate-assets.sh            Generates wallpaper, logos, splash images
│   └── build.sh                      Configures and runs live-build
└── README.md
```

## Hooks

| Hook | Purpose |
|---|---|
| 0000-copy-assets | Installs wallpaper, applications, logos and Plymouth theme |
| 0001-install-plymouth-theme | Selects the Lunar theme and rebuilds the initramfs |
| 0002-configure-desktop | LightDM, LXDE session and GTK theme defaults |
| 0003-install-welcome-app | Welcome autostart and Settings launcher |
| 0004-configure-shutdown | Shutdown wrappers; routes logout through the Lunar dialog |
| 0005-configure-user | Home folders and desktop shortcuts in `/etc/skel` |
| 0006-configure-applications | Firefox, LXTerminal and PCManFM defaults |
| 0007-configure-openbox | Lunar window theme and keyboard shortcuts |
| 0008-harden-session | Disables swap and hibernation |
| 0900-verify-desktop | Fails the build if the desktop or Lunar files are missing |

## Customising

- Panel: `config/includes.chroot/etc/xdg/lxpanel/LXDE/panels/panel`
- Window theme: `config/includes.chroot/usr/share/themes/Lunar/openbox-3/themerc`
- Shortcuts: `assets/desktop/openbox-keybinds.xml`
- Notifications: `config/includes.chroot/etc/xdg/dunst/dunstrc`
- Packages: `config/package-lists/lunar.list.chroot`
