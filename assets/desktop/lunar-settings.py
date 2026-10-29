#!/usr/bin/env python3
import configparser
import os
import shutil
import subprocess
from datetime import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

HOME = os.path.expanduser("~")
GTK3_SETTINGS = os.path.join(HOME, ".config", "gtk-3.0", "settings.ini")
GTK2_RC = os.path.join(HOME, ".gtkrc-2.0")
LXSESSION_USER = os.path.join(HOME, ".config", "lxsession", "LXDE", "desktop.conf")
LXSESSION_SYSTEM = "/etc/xdg/lxsession/LXDE/desktop.conf"
LIGHT_THEME = "Adwaita"
DARK_THEME = "Adwaita-dark"
CURRENT_YEAR = datetime.now().year
AUTHOR = "James Theakston"
LICENSE = "MIT"

SETTINGS_GRID = [
    # General
    {"name": "Appearance", "icon": "preferences-desktop-theme", "page": "appearance", "desc": "Dark mode, wallpaper"},
    {"name": "Display", "icon": "preferences-desktop-display", "page": "display", "desc": "Resolution, monitors"},
    {"name": "Sound", "icon": "preferences-desktop-sound", "page": "sound", "desc": "Volume, devices"},
    {"name": "Network", "icon": "preferences-desktop-network", "page": "network", "desc": "Wi-Fi, VPN"},
    
    # Internet
    {"name": "Bluetooth", "icon": "bluetooth", "page": "bluetooth", "desc": "Devices, connections"},
    {"name": "Users", "icon": "system-users", "page": "users", "desc": "Accounts, permissions"},
    
    # Hardware
    {"name": "Keyboard", "icon": "input-keyboard", "page": "input", "desc": "Layout, repeat rate"},
    {"name": "Mouse", "icon": "input-mouse", "page": "input", "desc": "Speed, acceleration"},
    {"name": "Printers", "icon": "printer", "page": "printers", "desc": "Add, configure"},
    {"name": "Power", "icon": "battery", "page": "power", "desc": "Battery, sleep"},
    
    # System
    {"name": "Startup", "icon": "system-run", "page": "startup", "desc": "Autostart apps"},
    {"name": "Themes", "icon": "preferences-desktop-wallpaper", "page": "themes", "desc": "GTK, icons, fonts"},
    {"name": "Firewall", "icon": "security-high", "page": "firewall", "desc": "Security rules"},
    {"name": "Disks", "icon": "drive-harddisk", "page": "disks", "desc": "Partitions, storage"},
    {"name": "System Info", "icon": "computer", "page": "system", "desc": "Hardware details"},
    {"name": "About", "icon": "help-about", "page": "about", "desc": "Version, license"},
]

CHANGELOG = """Version 1.0.0 (2026)
- Initial release of Lunar OS Home Edition
- Disposable session architecture with RAM-based storage
- LXDE desktop environment with Lunar OS branding
- Built-in VPN support (WireGuard)
- Browser selection (Firefox ESR, Tor Browser)
- Custom shutdown and restart dialogs
- Welcome window with session information
"""

MIT_LICENSE_TEXT = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""".format(year=CURRENT_YEAR, author=AUTHOR)


def launch(*command):
    try:
        subprocess.Popen(command)
    except OSError as error:
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=f"Could not start {command[0]}",
        )
        dialog.format_secondary_text(str(error))
        dialog.run()
        dialog.destroy()


def new_parser():
    parser = configparser.RawConfigParser(interpolation=None)
    parser.optionxform = str
    return parser


def current_dark():
    parser = new_parser()
    parser.read(["/etc/gtk-3.0/settings.ini", GTK3_SETTINGS])
    value = parser.get("Settings", "gtk-application-prefer-dark-theme", fallback="true")
    return value.strip().lower() in ("1", "true", "yes")


def apply_theme(dark):
    theme = DARK_THEME if dark else LIGHT_THEME

    os.makedirs(os.path.dirname(GTK3_SETTINGS), exist_ok=True)
    parser = new_parser()
    parser.read(GTK3_SETTINGS)
    if not parser.has_section("Settings"):
        parser.add_section("Settings")
    parser.set("Settings", "gtk-theme-name", theme)
    parser.set("Settings", "gtk-application-prefer-dark-theme", "true" if dark else "false")
    with open(GTK3_SETTINGS, "w") as handle:
        parser.write(handle, space_around_delimiters=False)

    with open(GTK2_RC, "w") as handle:
        handle.write(f'gtk-theme-name="{theme}"\n')

    os.makedirs(os.path.dirname(LXSESSION_USER), exist_ok=True)
    if not os.path.exists(LXSESSION_USER) and os.path.exists(LXSESSION_SYSTEM):
        shutil.copy(LXSESSION_SYSTEM, LXSESSION_USER)
    session = new_parser()
    session.read(LXSESSION_USER)
    if not session.has_section("GTK"):
        session.add_section("GTK")
    session.set("GTK", "sNet/ThemeName", theme)
    with open(LXSESSION_USER, "w") as handle:
        session.write(handle, space_around_delimiters=False)

    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-theme-name", theme)
    settings.set_property("gtk-application-prefer-dark-theme", dark)


class SettingsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lunar Settings")
        self.set_default_size(900, 650)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("preferences-system")
        self.connect("destroy", Gtk.main_quit)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)

        # Header with user profile
        header = self.build_header()
        main_box.pack_start(header, False, False, 0)

        # Settings grid
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        grid_box.set_border_width(20)
        
        # Add section headers and icon grids
        self.add_category(grid_box, "General", 
            [s for s in SETTINGS_GRID if s["page"] in ["appearance", "display", "sound", "network"]])
        self.add_category(grid_box, "Internet", 
            [s for s in SETTINGS_GRID if s["page"] in ["bluetooth", "users"]])
        self.add_category(grid_box, "Hardware", 
            [s for s in SETTINGS_GRID if s["page"] in ["input", "printers", "power"]])
        self.add_category(grid_box, "System", 
            [s for s in SETTINGS_GRID if s["page"] in ["startup", "themes", "firewall", "disks", "system", "about"]])
        
        scrolled.add(grid_box)
        main_box.pack_start(scrolled, True, True, 0)

        self.show_all()
    
    def build_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header.set_border_width(20)
        header.get_style_context().add_class("header")
        
        # User avatar
        avatar = Gtk.Image.new_from_icon_name("avatar-default", Gtk.IconSize.DIALOG)
        avatar.set_pixel_size(64)
        header.pack_start(avatar, False, False, 0)
        
        # User info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        username = os.environ.get("USER", "Lunar User")
        hostname = os.environ.get("HOSTNAME", "lunar-os")
        
        name_label = Gtk.Label()
        name_label.set_markup(f'<span size="x-large" weight="bold">{username}</span>')
        name_label.set_halign(Gtk.Align.START)
        info_box.pack_start(name_label, False, False, 0)
        
        host_label = Gtk.Label(label=f"{hostname} • Lunar OS Home Edition")
        host_label.set_halign(Gtk.Align.START)
        info_box.pack_start(host_label, False, False, 0)
        
        header.pack_start(info_box, True, True, 0)
        
        return header
    
    def add_category(self, parent, title, items):
        # Category label
        cat_label = Gtk.Label()
        cat_label.set_markup(f'<span weight="bold" size="large">{title}</span>')
        cat_label.set_halign(Gtk.Align.START)
        cat_label.set_margin_top(16)
        cat_label.set_margin_bottom(8)
        parent.pack_start(cat_label, False, False, 0)
        
        # Icon grid
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)
        grid.set_margin_bottom(24)
        
        col = 0
        row = 0
        for item in items:
            icon_button = self.create_icon_button(item)
            grid.attach(icon_button, col, row, 1, 1)
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        parent.pack_start(grid, False, False, 0)
    
    def create_icon_button(self, item):
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("icon-button")
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name(item["icon"], Gtk.IconSize.DIALOG)
        icon.set_pixel_size(48)
        box.pack_start(icon, False, False, 0)
        
        # Name
        name_label = Gtk.Label(label=item["name"])
        name_label.get_style_context().add_class("icon-name")
        box.pack_start(name_label, False, False, 0)
        
        # Description
        desc_label = Gtk.Label(label=item["desc"])
        desc_label.get_style_context().add_class("icon-desc")
        desc_label.set_max_width_chars(15)
        desc_label.set_ellipsize(Pango.EllipsizeMode.END)
        box.pack_start(desc_label, False, False, 0)
        
        button.add(box)
        button.connect("clicked", lambda b: self.open_setting(item))
        
        return button
    
    def open_setting(self, item):
        page = item["page"]
        
        if page == "appearance":
            self.show_appearance_dialog()
        elif page == "about":
            self.show_about_dialog()
        elif page == "session":
            self.show_session_dialog()
        else:
            # Launch external tool
            commands = {
                "display": ("lxrandr",),
                "sound": ("pavucontrol",),
                "network": ("nm-connection-editor",),
                "input": ("lxinput",),
                "startup": ("lxsession-edit",),
                "themes": ("lxappearance",),
                "bluetooth": ("blueman-manager",),
                "power": ("xfce4-power-manager-settings",),
                "firewall": ("gufw",),
                "printers": ("system-config-printer",),
                "disks": ("gparted",),
                "system": ("hardinfo",),
            }
            if page in commands:
                launch(*commands[page])
    
    def show_appearance_dialog(self):
        dialog = Gtk.Dialog(title="Appearance", parent=self, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        
        box = dialog.get_content_area()
        box.set_border_width(20)
        box.set_spacing(12)
        
        # Dark mode toggle
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.pack_start(Gtk.Label(label="Dark mode"), False, False, 0)
        switch = Gtk.Switch()
        switch.set_active(current_dark())
        switch.connect("notify::active", lambda s, _p: apply_theme(s.get_active()))
        row.pack_start(switch, False, False, 0)
        box.pack_start(row, False, False, 0)
        
        # Wallpaper button
        wallpaper = Gtk.Button(label="Choose wallpaper\u2026")
        wallpaper.connect("clicked", self.choose_wallpaper)
        box.pack_start(wallpaper, False, False, 0)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def show_about_dialog(self):
        dialog = Gtk.Dialog(title="About Lunar OS", parent=self, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        
        box = dialog.get_content_area()
        box.set_border_width(20)
        box.set_spacing(16)
        
        # Header with logo and title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        logo_path = "/usr/share/lunar-os/logo-128x128.png"
        if os.path.exists(logo_path):
            logo = Gtk.Image.new_from_file(logo_path)
            header_box.pack_start(logo, False, False, 0)
        else:
            logo_label = Gtk.Label(label="\U0001F319")
            logo_label.set_markup('<span size="xx-large">\U0001F319</span>')
            header_box.pack_start(logo_label, False, False, 0)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_label = Gtk.Label()
        title_label.set_markup('<span size="x-large" weight="bold">LunarOS Home Edition</span>')
        title_label.set_halign(Gtk.Align.START)
        title_box.pack_start(title_label, False, False, 0)
        
        copyright_label = Gtk.Label(label=f"\u00A9 {CURRENT_YEAR} {AUTHOR}")
        copyright_label.set_halign(Gtk.Align.START)
        title_box.pack_start(copyright_label, False, False, 0)
        
        header_box.pack_start(title_box, True, True, 0)
        box.pack_start(header_box, False, False, 0)
        
        # Version info
        version_label = Gtk.Label(label="You are updated to the latest version of LunarOS Home")
        version_label.set_halign(Gtk.Align.START)
        box.pack_start(version_label, False, False, 8)
        
        # License button
        license_button = Gtk.Button(label="View License")
        license_button.set_halign(Gtk.Align.START)
        license_button.connect("clicked", self.show_license)
        box.pack_start(license_button, False, False, 8)
        
        # Changelog
        changelog_label = Gtk.Label()
        changelog_label.set_markup('<span weight="bold">Changelog</span>')
        changelog_label.set_halign(Gtk.Align.START)
        changelog_label.set_margin_top(16)
        box.pack_start(changelog_label, False, False, 0)
        
        changelog_text = Gtk.TextView()
        changelog_text.set_editable(False)
        changelog_text.set_wrap_mode(Gtk.WrapMode.WORD)
        changelog_text.set_left_margin(0)
        changelog_text.set_right_margin(0)
        changelog_text.set_top_margin(0)
        changelog_text.set_bottom_margin(0)
        
        buffer = changelog_text.get_buffer()
        buffer.set_text(CHANGELOG)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.add(changelog_text)
        box.pack_start(scrolled, True, True, 0)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def show_license(self, button):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text="License",
        )
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = text_view.get_buffer()
        buffer.set_text(MIT_LICENSE_TEXT)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(300)
        scrolled.set_min_content_width(500)
        scrolled.add(text_view)
        
        dialog.get_content_area().pack_start(scrolled, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def show_session_dialog(self):
        dialog = Gtk.Dialog(title="Session", parent=self, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        
        box = dialog.get_content_area()
        box.set_border_width(20)
        box.set_spacing(12)
        
        box.pack_start(Gtk.Label(label="This is a temporary session. Files live in memory and are discarded at shutdown."), False, False, 0)
        
        for label, command in (
            ("Shut Down\u2026", "/usr/local/bin/lunar-shutdown"),
            ("Restart\u2026", "/usr/local/bin/lunar-restart"),
            ("Log Out\u2026", "/usr/local/bin/lunar-logout"),
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", lambda _b, c=command: launch(c))
            box.pack_start(button, False, False, 0)
        
        files = Gtk.Button(label="Open Temporary Files")
        files.connect("clicked", lambda _b: launch("pcmanfm", "/tmp"))
        box.pack_start(files, False, False, 8)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def choose_wallpaper(self, _button):
        dialog = Gtk.FileChooserDialog(
            title="Choose wallpaper",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Apply", Gtk.ResponseType.OK)
        images = Gtk.FileFilter()
        images.set_name("Images")
        images.add_pixbuf_formats()
        dialog.add_filter(images)
        dialog.set_current_folder("/usr/share/backgrounds/lunar-os")
        if dialog.run() == Gtk.ResponseType.OK:
            launch("pcmanfm", "--set-wallpaper=" + dialog.get_filename(), "--wallpaper-mode=crop")
        dialog.destroy()


def main():
    # Apply macOS-like styling
    CSS = b"""
window {
    background-color: #ffffff;
}
.header {
    background-color: #f5f5f7;
    border-bottom: 1px solid #d1d1d6;
}
.icon-button {
    background-color: #f5f5f7;
    border-radius: 12px;
    padding: 16px;
}
.icon-button:hover {
    background-color: #e8e8ea;
}
.icon-name {
    font-size: 13px;
    font-weight: 500;
}
.icon-desc {
    font-size: 11px;
    color: #86868b;
}
"""
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    
    SettingsWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
