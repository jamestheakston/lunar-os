#!/usr/bin/env python3
import configparser
import os
import shutil
import subprocess

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

LAUNCHER_PAGES = (
    ("display", "Display", "Change resolution, orientation and monitor layout.", "Open display settings", ("lxrandr",)),
    ("sound", "Sound", "Choose output and input devices and adjust volume.", "Open sound settings", ("pavucontrol",)),
    ("network", "Network", "Manage wired, wireless and VPN connections.", "Open network connections", ("nm-connection-editor",)),
    ("input", "Keyboard and Mouse", "Keyboard layout, repeat rate, pointer speed and acceleration.", "Open keyboard and mouse settings", ("lxinput",)),
    ("startup", "Startup Applications", "Choose which applications start with the desktop.", "Open session settings", ("lxsession-edit",)),
    ("themes", "Advanced Themes", "Pick GTK themes, icons, cursors and fonts.", "Open appearance tool", ("lxappearance",)),
)


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
        for name, title, description, button, command in LAUNCHER_PAGES[:5]:
            self.add_page(name, title, self.build_launcher(title, description, button, command))
        self.add_page("session", "Session", self.build_session())
        self.add_page(LAUNCHER_PAGES[5][0], LAUNCHER_PAGES[5][1], self.build_launcher(*LAUNCHER_PAGES[5][1:4], LAUNCHER_PAGES[5][4]))
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

    def build_about(self):
        box = self.page("About Lunar OS")
        box.pack_start(
            self.text(
                "Lunar OS is a disposable desktop built on Debian Live. The base system is read-only and "
                "all session changes are stored in RAM. Disposable storage reduces persistence but cannot "
                "remove data you copied to external drives, sent over a network or that hardware retained."
            ),
            False, False, 0,
        )
        return box


def main():
    SettingsWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
