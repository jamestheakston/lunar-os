#!/usr/bin/env python3
import configparser
import os
import shutil
import subprocess
from datetime import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

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

LAUNCHER_PAGES = (
    ("display", "Display", "Change resolution, orientation and monitor layout.", "Open display settings", ("lxrandr",)),
    ("sound", "Sound", "Choose output and input devices and adjust volume.", "Open sound settings", ("pavucontrol",)),
    ("network", "Network", "Manage wired, wireless and VPN connections.", "Open network connections", ("nm-connection-editor",)),
    ("input", "Keyboard and Mouse", "Keyboard layout, repeat rate, pointer speed and acceleration.", "Open keyboard and mouse settings", ("lxinput",)),
    ("startup", "Startup Applications", "Choose which applications start with the desktop.", "Open session settings", ("lxsession-edit",)),
    ("themes", "Advanced Themes", "Pick GTK themes, icons, cursors and fonts.", "Open appearance tool", ("lxappearance",)),
    ("bluetooth", "Bluetooth", "Manage Bluetooth devices and connections.", "Open Bluetooth settings", ("blueman-manager",)),
    ("power", "Power Management", "Configure power saving, battery, and sleep settings.", "Open power settings", ("xfce4-power-manager-settings",)),
    ("accessibility", "Accessibility", "Screen reader, magnifier, and accessibility features.", "Open accessibility settings", ("onboard",)),
    ("datetime", "Date & Time", "Set time zone, date, and time configuration.", "Open date and time settings", ("lxappearance",)),
    ("firewall", "Firewall", "Configure firewall rules and security settings.", "Open firewall settings", ("gufw",)),
    ("users", "Users", "Manage user accounts and permissions.", "Open user settings", ("lxsession-edit",)),
    ("printers", "Printers", "Add and configure printers.", "Open printer settings", ("system-config-printer",)),
    ("disks", "Disks", "Manage disk partitions and storage.", "Open disk utility", ("gparted",)),
    ("system", "System Info", "View system information and hardware details.", "Open system info", ("hardinfo",)),
    ("terminal", "Terminal", "Configure terminal emulator settings.", "Open terminal settings", ("lxterminal",)),
)

CHANGELOG = """Version 1.0.0 (2026)
- Initial release of Lunar OS Home Edition
- Disposable session architecture with RAM-based storage
- LXDE desktop environment with Lunar OS branding
- Built-in VPN support (OpenVPN)
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
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
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
        self.set_default_size(760, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("preferences-system")
        self.connect("destroy", Gtk.main_quit)

        layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(layout)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(self.stack)
        sidebar.set_size_request(210, -1)
        layout.pack_start(sidebar, False, False, 0)
        layout.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        layout.pack_start(self.stack, True, True, 0)

        self.add_page("appearance", "Appearance", self.build_appearance())
        for name, title, description, button, command in LAUNCHER_PAGES:
            self.add_page(name, title, self.build_launcher(title, description, button, command))
        self.add_page("session", "Session", self.build_session())
        self.add_page("about", "About", self.build_about())
        self.show_all()

    def add_page(self, name, title, widget):
        self.stack.add_titled(widget, name, title)

    def page(self, title):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(28)
        heading = Gtk.Label()
        heading.set_markup(f'<span size="x-large" weight="bold">{title}</span>')
        heading.set_halign(Gtk.Align.START)
        box.pack_start(heading, False, False, 0)
        return box

    def text(self, content):
        label = Gtk.Label(label=content)
        label.set_line_wrap(True)
        label.set_halign(Gtk.Align.START)
        label.set_xalign(0)
        label.set_max_width_chars(70)
        return label

    def build_launcher(self, title, description, button_label, command):
        box = self.page(title)
        box.pack_start(self.text(description), False, False, 0)
        button = Gtk.Button(label=button_label)
        button.set_halign(Gtk.Align.START)
        button.connect("clicked", lambda _b: launch(*command))
        box.pack_start(button, False, False, 0)
        return box

    def build_appearance(self):
        box = self.page("Appearance")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.pack_start(Gtk.Label(label="Dark mode"), False, False, 0)
        switch = Gtk.Switch()
        switch.set_active(current_dark())
        switch.connect("notify::active", lambda s, _p: apply_theme(s.get_active()))
        row.pack_start(switch, False, False, 0)
        box.pack_start(row, False, False, 0)
        box.pack_start(
            self.text("The theme applies to applications you open from now on. Reopen running applications to update them."),
            False, False, 0,
        )

        wallpaper = Gtk.Button(label="Choose wallpaper\u2026")
        wallpaper.set_halign(Gtk.Align.START)
        wallpaper.connect("clicked", self.choose_wallpaper)
        box.pack_start(wallpaper, False, False, 8)
        return box

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

    def build_session(self):
        box = self.page("Session")
        box.pack_start(
            self.text(
                "This is a temporary session. Files, settings and downloads live in memory and are "
                "discarded when the computer shuts down or restarts. Logging out keeps them until then."
            ),
            False, False, 0,
        )
        
        # Storage button with chevron
        storage_button = Gtk.Button(label="Storage \u203A")
        storage_button.set_halign(Gtk.Align.START)
        storage_button.connect("clicked", self.show_storage_page)
        box.pack_start(storage_button, False, False, 8)
        
        for label, command in (
            ("Shut Down and Discard Session\u2026", "/usr/local/bin/lunar-shutdown"),
            ("Restart and Start Fresh\u2026", "/usr/local/bin/lunar-restart"),
            ("Log Out\u2026", "/usr/local/bin/lunar-logout"),
        ):
            button = Gtk.Button(label=label)
            button.set_halign(Gtk.Align.START)
            button.connect("clicked", lambda _b, c=command: launch(c))
            box.pack_start(button, False, False, 0)
        files = Gtk.Button(label="Open Temporary Files")
        files.set_halign(Gtk.Align.START)
        files.connect("clicked", lambda _b: launch("pcmanfm", "/tmp"))
        box.pack_start(files, False, False, 8)
        return box

    def check_updates(self, button):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Check for Updates",
        )
        dialog.format_secondary_text(
            "To check for the latest version of Lunar OS Home Edition, please visit the GitHub repository:\n\n"
            "https://github.com/jamestheakston/lunar-os\n\n"
            "The built-in update check feature is not currently implemented. "
            "Please check the repository manually for new releases and changes."
        )
        dialog.run()
        dialog.destroy()

    def build_about(self):
        box = self.page("About Lunar OS")
        
        # Header with logo and title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header_box.set_margin_bottom(16)
        
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
        copyright_label.get_style_context().add_class("note")
        title_box.pack_start(copyright_label, False, False, 0)
        
        header_box.pack_start(title_box, True, True, 0)
        box.pack_start(header_box, False, False, 0)
        
        # Version info
        version_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        version_label = Gtk.Label(label="You are updated to the latest version of LunarOS Home")
        version_label.set_halign(Gtk.Align.START)
        version_box.pack_start(version_label, False, False, 0)
        
        check_button = Gtk.Button(label="Check for Updates")
        check_button.connect("clicked", self.check_updates)
        version_box.pack_start(check_button, False, False, 0)
        box.pack_start(version_box, False, False, 8)
        
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
        
        return box

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

    def show_storage_page(self, button):
        storage_page = self.build_storage()
        storage_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        storage_box.pack_start(storage_page, True, True, 0)
        
        dialog = Gtk.Dialog(
            title="Storage",
            parent=self,
            flags=0,
        )
        dialog.add_button("Back", Gtk.ResponseType.CLOSE)
        dialog.get_content_area().pack_start(storage_box, True, True, 0)
        dialog.set_default_size(600, 500)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def build_storage(self):
        box = self.page("Storage")
        
        # Storage info
        storage_info = self.get_storage_info()
        info_label = Gtk.Label(label=storage_info)
        info_label.set_halign(Gtk.Align.START)
        box.pack_start(info_label, False, False, 0)
        
        # Storage graph
        storage_graph = self.build_storage_graph()
        box.pack_start(storage_graph, True, True, 16)
        
        # Non-disposable toggle
        non_disposable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        non_disposable_box.set_margin_top(16)
        
        non_disposable_label = Gtk.Label(label="Non-disposable mode")
        non_disposable_label.set_halign(Gtk.Align.START)
        non_disposable_box.pack_start(non_disposable_label, False, False, 0)
        
        non_disposable_switch = Gtk.Switch()
        non_disposable_switch.set_active(self.is_non_disposable())
        non_disposable_switch.connect("notify::active", self.toggle_non_disposable)
        non_disposable_box.pack_start(non_disposable_switch, False, False, 0)
        
        box.pack_start(non_disposable_box, False, False, 0)
        
        warning_label = Gtk.Label()
        warning_label.set_markup('<span foreground="red" size="small">Warning: Non-disposable mode will keep files on disk. Only enable if you understand the risks.</span>')
        warning_label.set_line_wrap(True)
        warning_label.set_halign(Gtk.Align.START)
        warning_label.set_max_width_chars(70)
        box.pack_start(warning_label, False, False, 8)
        
        return box

    def get_storage_info(self):
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            used_percent = (used / total) * 100
            return f"Session storage: {self.human_size(used)} used of {self.human_size(total)} ({used_percent:.1f}%)"
        except Exception:
            return "Session storage: unavailable"

    def human_size(self, size):
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}"
            size /= 1024

    def build_storage_graph(self):
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            used_percent = (used / total) * 100
        except Exception:
            used_percent = 0
        
        graph = Gtk.ProgressBar()
        graph.set_fraction(used_percent / 100)
        graph.set_text(f"{used_percent:.1f}% used")
        graph.set_show_text(True)
        return graph

    def is_non_disposable(self):
        config_file = os.path.join(HOME, ".config", "lunar-os", "non-disposable")
        return os.path.exists(config_file)

    def toggle_non_disposable(self, switch, param):
        if switch.get_active():
            # Ask for confirmation
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Enable Non-Disposable Mode?"
            )
            dialog.format_secondary_text(
                "Non-disposable mode will keep files on disk instead of discarding them at shutdown.\n\n"
                "This means:\n"
                "- Files will persist across reboots\n"
                "- Data may be left on the system\n"
                "- Privacy benefits of disposable mode are lost\n\n"
                "Only enable this if you understand the risks and want persistent storage.\n\n"
                "Are you sure you want to continue?"
            )
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                config_dir = os.path.join(HOME, ".config", "lunar-os")
                os.makedirs(config_dir, exist_ok=True)
                config_file = os.path.join(config_dir, "non-disposable")
                with open(config_file, "w") as f:
                    f.write("enabled")
            else:
                switch.set_active(False)
        else:
            config_file = os.path.join(HOME, ".config", "lunar-os", "non-disposable")
            if os.path.exists(config_file):
                os.remove(config_file)


def main():
    SettingsWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
