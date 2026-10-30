#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import time
import traceback

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk, Pango

HOME = os.path.expanduser("~")
PID_FILE = "/tmp/.lunar-start7.pid"
CLOSED_FILE = "/tmp/.lunar-start7.closed"
ERROR_LOG = "/tmp/lunar-start7-error.log"
APP_DIR = "/usr/share/lunar-os"
WIDTH = 480
HEIGHT = 580
REOPEN_GUARD_SECONDS = 0.45

PINNED = (
    "pcmanfm.desktop",
    "firefox-esr.desktop",
    "lxterminal.desktop",
    "mousepad.desktop",
    "galculator.desktop",
    "gpicview.desktop",
    "lunar-store.desktop",
    "lunar-settings.desktop",
)

PLACES = (
    ("Documents", "folder-documents", os.path.join(HOME, "Documents")),
    ("Pictures", "folder-pictures", os.path.join(HOME, "Pictures")),
    ("Music", "folder-music", os.path.join(HOME, "Music")),
    ("Downloads", "folder-download", os.path.join(HOME, "Downloads")),
    ("Temporary Files", "folder-temp", "/tmp"),
)

TOOLS = (
    ("Lunar Settings", "preferences-system", (os.path.join(APP_DIR, "lunar-settings.py"),)),
    ("Lunar Store", "lunar-store", (os.path.join(APP_DIR, "lunar-store.py"),)),
    ("Wallpapers", "preferences-desktop-wallpaper", (os.path.join(APP_DIR, "lunar-wallpaper.py"),)),
    ("Task Manager", "utilities-system-monitor", ("lxtask",)),
    ("About Lunar OS", "help-about", (os.path.join(APP_DIR, "lunar-about.py"),)),
)

CSS = b"""
window.lunar-start {
    background-color: rgba(22, 22, 40, 0.97);
    border: 1px solid rgba(108, 92, 231, 0.6);
    border-radius: 10px;
}
box.start-left {
    background-color: rgba(34, 34, 60, 0.95);
    border-radius: 8px;
    margin: 8px 0 8px 8px;
    padding: 8px;
}
box.start-right { padding: 10px 10px 10px 14px; }
button.program-row, button.place-row {
    background-image: none;
    background-color: transparent;
    border: none;
    box-shadow: none;
    border-radius: 6px;
    padding: 6px 8px;
    color: #e8e8f0;
}
button.program-row:hover, button.place-row:hover { background-color: rgba(108, 92, 231, 0.45); }
button.place-row { color: #f2f2fa; font-size: 13px; }
label.start-user { font-size: 17px; font-weight: bold; color: #ffffff; }
label.start-empty { color: #9a9ab8; padding: 16px; }
label.start-heading { color: #9a9ab8; font-size: 11px; padding: 6px 8px 2px 8px; }
button.all-programs {
    background-image: none;
    background-color: transparent;
    border: none;
    box-shadow: none;
    border-radius: 6px;
    padding: 6px 8px;
    color: #ffffff;
    font-weight: bold;
}
button.all-programs:hover { background-color: rgba(108, 92, 231, 0.45); }
entry.start-search {
    background-image: none;
    background-color: #14142a;
    color: #e8e8f0;
    border: 1px solid #3a3a5c;
    border-radius: 16px;
    padding: 7px 14px;
    box-shadow: none;
}
entry.start-search:focus { border-color: #6c5ce7; }
button.shutdown {
    background-image: none;
    background-color: #34345a;
    color: #ffffff;
    border: 1px solid #44446e;
    border-radius: 6px 0 0 6px;
    padding: 7px 16px;
    box-shadow: none;
}
button.shutdown:hover { background-color: #c0392b; border-color: #c0392b; }
button.shutdown-arrow {
    background-image: none;
    background-color: #34345a;
    color: #ffffff;
    border: 1px solid #44446e;
    border-left: none;
    border-radius: 0 6px 6px 0;
    padding: 7px 9px;
    box-shadow: none;
}
button.shutdown-arrow:hover { background-color: #44446e; }
separator.start-separator { background-color: rgba(255, 255, 255, 0.12); margin: 6px 4px; }
scrolledwindow { background-color: transparent; }
"""


def log_error(text):
    try:
        with open(ERROR_LOG, "a") as handle:
            handle.write(text + "\n")
    except OSError:
        pass


def spawn(command):
    try:
        subprocess.Popen(command, start_new_session=True)
    except OSError as error:
        log_error(f"could not start {command}: {error}")


def process_is_start_menu(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as handle:
            return b"lunar-start7" in handle.read()
    except OSError:
        return False


def toggle_existing():
    try:
        with open(PID_FILE) as handle:
            pid = int(handle.read().strip())
    except (OSError, ValueError):
        return False
    if pid != os.getpid() and process_is_start_menu(pid):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return False
        return True
    return False


def closed_recently():
    try:
        with open(CLOSED_FILE) as handle:
            return time.time() - float(handle.read().strip()) < REOPEN_GUARD_SECONDS
    except (OSError, ValueError):
        return False


def list_apps():
    seen = set()
    apps = []
    for app in Gio.AppInfo.get_all():
        if not app.should_show():
            continue
        name = app.get_display_name() or ""
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        apps.append(app)
    apps.sort(key=lambda item: item.get_display_name().lower())
    return apps


def app_keywords(app):
    words = [app.get_display_name() or "", app.get_description() or ""]
    if isinstance(app, Gio.DesktopAppInfo):
        words.extend(app.get_keywords() or [])
    return " ".join(words).lower()


def icon_image(icon, size):
    if icon is not None:
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DND)
    else:
        image = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DND)
    image.set_pixel_size(size)
    return image


def named_icon_image(name, size):
    image = Gtk.Image.new_from_icon_name(name, Gtk.IconSize.DND)
    image.set_pixel_size(size)
    return image


class StartMenu(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.menu_open = False
        self.closing = False
        self.show_all_programs = False
        self.first_result = None
        self.apps = list_apps()
        self.all_built = False

        self.get_style_context().add_class("lunar-start")
        self.set_title("Start")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(WIDTH, HEIGHT)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)
            self.set_app_paintable(True)

        self.connect("key-press-event", self.on_key)
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("destroy", self.on_destroy)

        self.build()
        self.place()
        self.show_all()
        self.present()
        self.search.grab_focus()

    def build(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(outer)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        left.get_style_context().add_class("start-left")
        left.set_size_request(290, -1)
        outer.pack_start(left, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(120)
        left.pack_start(self.stack, True, True, 0)

        self.pinned_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.stack.add_named(self.pinned_box, "pinned")
        self.fill_pinned()

        self.all_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.stack.add_named(self.scrolled(self.all_box), "all")

        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.stack.add_named(self.scrolled(self.results_box), "results")

        self.toggle_button = Gtk.Button(label="All Programs  \u25B8")
        self.toggle_button.get_style_context().add_class("all-programs")
        self.toggle_button.set_halign(Gtk.Align.FILL)
        self.toggle_button.get_child().set_halign(Gtk.Align.START)
        self.toggle_button.connect("clicked", self.on_toggle_programs)
        left.pack_start(self.toggle_button, False, False, 0)

        self.search = Gtk.Entry()
        self.search.set_placeholder_text("Search programs")
        self.search.get_style_context().add_class("start-search")
        self.search.connect("changed", self.on_search_changed)
        self.search.connect("activate", self.on_search_activate)
        left.pack_start(self.search, False, False, 2)

        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        right.get_style_context().add_class("start-right")
        outer.pack_start(right, True, True, 0)

        user = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        user.pack_start(named_icon_image("avatar-default", 48), False, False, 0)
        real_name = GLib.get_real_name()
        name = Gtk.Label(label=real_name if real_name not in ("", "Unknown") else GLib.get_user_name())
        name.get_style_context().add_class("start-user")
        name.set_halign(Gtk.Align.START)
        user.pack_start(name, True, True, 0)
        user.set_margin_bottom(10)
        right.pack_start(user, False, False, 0)

        for label, icon, path in PLACES:
            right.pack_start(self.place_button(label, icon, lambda _b, p=path: self.open_path(p)), False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.get_style_context().add_class("start-separator")
        right.pack_start(separator, False, False, 4)

        for label, icon, command in TOOLS:
            right.pack_start(self.place_button(label, icon, lambda _b, c=command: self.run_command(c)), False, False, 0)

        right.pack_start(Gtk.Box(), True, True, 0)

        power = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        power.set_halign(Gtk.Align.START)
        shutdown = Gtk.Button(label="Shut down")
        shutdown.get_style_context().add_class("shutdown")
        shutdown.connect("clicked", lambda _b: self.power_action("--shutdown"))
        power.pack_start(shutdown, False, False, 0)
        arrow = Gtk.Button(label="\u25B8")
        arrow.get_style_context().add_class("shutdown-arrow")
        arrow.connect("clicked", self.on_power_menu)
        power.pack_start(arrow, False, False, 0)
        right.pack_start(power, False, False, 4)

    def scrolled(self, child):
        view = Gtk.ScrolledWindow()
        view.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        view.add(child)
        return view

    def program_button(self, app):
        button = Gtk.Button()
        button.get_style_context().add_class("program-row")
        button.set_relief(Gtk.ReliefStyle.NONE)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.pack_start(icon_image(app.get_icon(), 28), False, False, 0)
        label = Gtk.Label(label=app.get_display_name())
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(26)
        row.pack_start(label, True, True, 0)
        button.add(row)
        button.set_tooltip_text(app.get_description())
        button.connect("clicked", lambda _b, a=app: self.launch_app(a))
        return button

    def place_button(self, label_text, icon_name, callback):
        button = Gtk.Button()
        button.get_style_context().add_class("place-row")
        button.set_relief(Gtk.ReliefStyle.NONE)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.pack_start(named_icon_image(icon_name, 22), False, False, 0)
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        row.pack_start(label, True, True, 0)
        button.add(row)
        button.connect("clicked", callback)
        return button

    def fill_pinned(self):
        by_id = {app.get_id(): app for app in self.apps}
        count = 0
        for desktop_id in PINNED:
            app = by_id.get(desktop_id)
            if app is None:
                app = Gio.DesktopAppInfo.new(desktop_id)
            if app is None:
                continue
            self.pinned_box.pack_start(self.program_button(app), False, False, 0)
            count += 1
        if count == 0:
            self.pinned_box.pack_start(Gtk.Label(label="No pinned programs"), False, False, 0)

    def fill_all(self):
        if self.all_built:
            return
        for app in self.apps:
            self.all_box.pack_start(self.program_button(app), False, False, 0)
        self.all_box.show_all()
        self.all_built = True

    def place(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        area = monitor.get_workarea()
        self.move(area.x + 4, area.y + area.height - HEIGHT - 2)

    def show_page(self):
        if self.search.get_text().strip():
            self.stack.set_visible_child_name("results")
        elif self.show_all_programs:
            self.fill_all()
            self.stack.set_visible_child_name("all")
        else:
            self.stack.set_visible_child_name("pinned")

    def on_toggle_programs(self, _button):
        self.show_all_programs = not self.show_all_programs
        self.toggle_button.set_label("\u25C2  Back" if self.show_all_programs else "All Programs  \u25B8")
        self.search.set_text("")
        self.show_page()

    def on_search_changed(self, entry):
        text = entry.get_text().strip().lower()
        for child in self.results_box.get_children():
            self.results_box.remove(child)
        self.first_result = None
        if text:
            matches = [app for app in self.apps if text in app_keywords(app)]
            matches.sort(key=lambda app: (not app.get_display_name().lower().startswith(text), app.get_display_name().lower()))
            for app in matches[:40]:
                self.results_box.pack_start(self.program_button(app), False, False, 0)
            if matches:
                self.first_result = matches[0]
            else:
                empty = Gtk.Label(label="No matching programs")
                empty.get_style_context().add_class("start-empty")
                self.results_box.pack_start(empty, False, False, 0)
            self.results_box.show_all()
        self.show_page()

    def on_search_activate(self, _entry):
        if self.first_result is not None:
            self.launch_app(self.first_result)

    def launch_app(self, app):
        try:
            context = Gdk.Display.get_default().get_app_launch_context()
            app.launch([], context)
        except GLib.Error as error:
            log_error(f"could not launch {app.get_id()}: {error}")
        self.close_menu()

    def open_path(self, path):
        if path.startswith(HOME):
            os.makedirs(path, exist_ok=True)
        spawn(["pcmanfm", path])
        self.close_menu()

    def run_command(self, command):
        spawn(list(command))
        self.close_menu()

    def power_action(self, flag):
        spawn([os.path.join(APP_DIR, "shutdown-dialog.py"), flag])
        self.close_menu()

    def on_power_menu(self, button):
        menu = Gtk.Menu()
        for label, flag in (("Restart", "--restart"), ("Log off", "--logout")):
            item = Gtk.MenuItem(label=label)
            item.connect("activate", lambda _i, f=flag: self.power_action(f))
            menu.append(item)
        menu.show_all()
        self.menu_open = True
        menu.connect("deactivate", self.on_menu_deactivate)
        menu.popup_at_widget(button, Gdk.Gravity.NORTH_EAST, Gdk.Gravity.NORTH_WEST, None)

    def on_menu_deactivate(self, _menu):
        GLib.timeout_add(200, self.release_menu)

    def release_menu(self):
        self.menu_open = False
        return False

    def on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close_menu()
            return True
        return False

    def on_focus_out(self, _widget, _event):
        GLib.timeout_add(150, self.check_focus)
        return False

    def check_focus(self):
        if not self.closing and not self.menu_open and not self.is_active():
            self.close_menu()
        return False

    def close_menu(self, *_args):
        if self.closing:
            return False
        self.closing = True
        try:
            with open(CLOSED_FILE, "w") as handle:
                handle.write(str(time.time()))
        except OSError:
            pass
        self.destroy()
        return False

    def on_destroy(self, _widget):
        try:
            os.remove(PID_FILE)
        except OSError:
            pass
        Gtk.main_quit()


def main():
    if closed_recently() or toggle_existing():
        return
    with open(PID_FILE, "w") as handle:
        handle.write(str(os.getpid()))

    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    menu = StartMenu()
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, menu.close_menu)
    Gtk.main()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log_error(traceback.format_exc())
        try:
            os.remove(PID_FILE)
        except OSError:
            pass
        sys.exit(1)
