#!/usr/bin/env python3
import os
import subprocess
import sys
import threading
import traceback

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk, Pango

ERROR_LOG = "/tmp/lunar-store-error.log"

CSS = b"""
window.lunar-store { background-color: #1a1a2e; }
window.lunar-store label { color: #e8e8f0; }
box.store-sidebar { background-color: #14142a; border-right: 1px solid #2d2d4d; }
label.store-title { font-size: 20px; font-weight: bold; color: #ffffff; }
label.store-note { font-size: 12px; color: #9a9ab8; }
label.app-name { font-size: 15px; font-weight: bold; color: #ffffff; }
label.app-description { font-size: 12px; color: #b0b0c8; }
label.app-status { font-size: 12px; color: #9a9ab8; }
list.store-categories, list.store-apps { background-color: transparent; }
list.store-categories row { padding: 11px 18px; color: #d0d0e4; border-radius: 8px; margin: 2px 8px; }
list.store-categories row:hover { background-color: rgba(108, 92, 231, 0.25); }
list.store-categories row:selected { background-color: #6c5ce7; color: #ffffff; }
list.store-apps row { background-color: transparent; padding: 0; }
box.app-card {
    background-color: #232340;
    border: 1px solid #2f2f55;
    border-radius: 10px;
    padding: 14px;
    margin: 6px 14px;
}
box.app-card:hover { border-color: #6c5ce7; }
entry.store-search {
    background-image: none;
    background-color: #14142a;
    color: #e8e8f0;
    border: 1px solid #3a3a5c;
    border-radius: 16px;
    padding: 7px 14px;
}
button.install-button {
    background-image: none;
    background-color: #6c5ce7;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
}
button.install-button:hover { background-color: #7d6ff0; }
button.install-button:disabled { background-color: #3a3a5c; color: #a0a0b8; }
button.install-button.installed { background-color: #1e8e5a; color: #ffffff; }
progressbar trough { min-height: 8px; border-radius: 4px; background-color: #14142a; }
progressbar progress { min-height: 8px; border-radius: 4px; background-color: #6c5ce7; }
textview.install-log, textview.install-log text { background-color: #0e0e1c; color: #c8c8d8; }
"""

CATEGORIES = (
    ("all", "All Applications"),
    ("internet", "Internet"),
    ("multimedia", "Multimedia"),
    ("office", "Office"),
    ("graphics", "Graphics"),
    ("games", "Games"),
    ("system", "System"),
    ("accessories", "Accessories"),
)

PACKAGES = (
    ("Chromium", "chromium", "internet", "Open-source web browser", "chromium"),
    ("Thunderbird", "thunderbird", "internet", "Email client", "thunderbird"),
    ("Transmission", "transmission-gtk", "internet", "BitTorrent client", "transmission"),
    ("FileZilla", "filezilla", "internet", "FTP and SFTP client", "filezilla"),
    ("VLC Media Player", "vlc", "multimedia", "Plays almost any audio or video file", "vlc"),
    ("Audacity", "audacity", "multimedia", "Audio recorder and editor", "audacity"),
    ("Blender", "blender", "multimedia", "3D creation suite", "blender"),
    ("GIMP", "gimp", "graphics", "Image editor", "gimp"),
    ("Inkscape", "inkscape", "graphics", "Vector graphics editor", "inkscape"),
    ("LibreOffice", "libreoffice", "office", "Full office suite", "libreoffice-startcenter"),
    ("Evince", "evince", "office", "PDF and document viewer", "evince"),
    ("Steam", "steam-installer", "games", "Steam gaming platform", "steam"),
    ("Lutris", "lutris", "games", "Open gaming platform", "lutris"),
    ("GParted", "gparted", "system", "Partition editor", "gparted"),
    ("BleachBit", "bleachbit", "system", "System cleaner", "bleachbit"),
    ("Geany", "geany", "accessories", "Lightweight code editor", "geany"),
    ("Vim", "vim", "accessories", "Terminal text editor", "vim"),
)


def log_error(text):
    try:
        with open(ERROR_LOG, "a") as handle:
            handle.write(text + "\n")
    except OSError:
        pass


def installed_packages():
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Package} ${Status}\n"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return set()
    names = set()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[-1] == "installed":
            names.add(parts[0])
    return names


class AppCard(Gtk.Box):
    def __init__(self, store, name, package, description, icon_name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.store = store
        self.package = package
        self.get_style_context().add_class("app-card")

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        theme = Gtk.IconTheme.get_default()
        chosen = icon_name if theme.has_icon(icon_name) else "package-x-generic"
        icon = Gtk.Image.new_from_icon_name(chosen, Gtk.IconSize.DIALOG)
        icon.set_pixel_size(48)
        top.pack_start(icon, False, False, 0)

        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title = Gtk.Label(label=name)
        title.get_style_context().add_class("app-name")
        title.set_halign(Gtk.Align.START)
        text.pack_start(title, False, False, 0)
        desc = Gtk.Label(label=description)
        desc.get_style_context().add_class("app-description")
        desc.set_halign(Gtk.Align.START)
        desc.set_xalign(0)
        desc.set_line_wrap(True)
        text.pack_start(desc, False, False, 0)
        top.pack_start(text, True, True, 0)

        self.button = Gtk.Button(label="Install")
        self.button.get_style_context().add_class("install-button")
        self.button.set_valign(Gtk.Align.CENTER)
        self.button.connect("clicked", self.on_clicked)
        top.pack_start(self.button, False, False, 0)
        self.pack_start(top, False, False, 0)

        self.progress = Gtk.ProgressBar()
        self.pack_start(self.progress, False, False, 0)

        self.status = Gtk.Label(label="")
        self.status.get_style_context().add_class("app-status")
        self.status.set_halign(Gtk.Align.START)
        self.pack_start(self.status, False, False, 0)

    def on_clicked(self, _button):
        self.store.start_install(self)

    def mark_installed(self):
        self.button.set_label("Installed")
        self.button.set_sensitive(False)
        self.button.get_style_context().add_class("installed")

    def set_busy(self, busy):
        self.button.set_sensitive(not busy)
        self.progress.set_visible(busy)
        self.status.set_visible(busy)
        if busy:
            self.button.set_label("Installing\u2026")


class LunarStore(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lunar Store")
        self.set_default_size(960, 640)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("lunar-store")
        self.get_style_context().add_class("lunar-store")
        self.connect("destroy", Gtk.main_quit)

        self.installed = set()
        self.cards = []
        self.installing = None
        self.pulse_id = None
        self.category = "all"

        self.build()
        self.show_all()
        self.details.set_visible(False)
        for card in self.cards:
            card.progress.set_visible(False)
            card.status.set_visible(False)
        threading.Thread(target=self.load_installed, daemon=True).start()

    def build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(root)

        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar.get_style_context().add_class("store-sidebar")
        sidebar.set_size_request(220, -1)
        title = Gtk.Label(label="Lunar Store")
        title.get_style_context().add_class("store-title")
        title.set_halign(Gtk.Align.START)
        title.set_margin_start(18)
        title.set_margin_top(18)
        title.set_margin_bottom(8)
        sidebar.pack_start(title, False, False, 0)

        self.category_list = Gtk.ListBox()
        self.category_list.get_style_context().add_class("store-categories")
        self.category_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        for key, label_text in CATEGORIES:
            row = Gtk.ListBoxRow()
            row.category_key = key
            label = Gtk.Label(label=label_text)
            label.set_halign(Gtk.Align.START)
            row.add(label)
            self.category_list.add(row)
        self.category_list.connect("row-selected", self.on_category_selected)
        sidebar.pack_start(self.category_list, True, True, 0)

        note = Gtk.Label(label="Apps you install live in memory and are removed when you shut down.")
        note.get_style_context().add_class("store-note")
        note.set_line_wrap(True)
        note.set_xalign(0)
        note.set_margin_start(18)
        note.set_margin_end(14)
        note.set_margin_bottom(16)
        sidebar.pack_end(note, False, False, 0)
        root.pack_start(sidebar, False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.pack_start(content, True, True, 0)

        self.search = Gtk.Entry()
        self.search.set_placeholder_text("Search applications")
        self.search.get_style_context().add_class("store-search")
        self.search.set_margin_top(16)
        self.search.set_margin_start(20)
        self.search.set_margin_end(20)
        self.search.set_margin_bottom(8)
        self.search.connect("changed", lambda _e: self.apps_list.invalidate_filter())
        content.pack_start(self.search, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.apps_list = Gtk.ListBox()
        self.apps_list.get_style_context().add_class("store-apps")
        self.apps_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.apps_list.set_filter_func(self.filter_row)
        scroller.add(self.apps_list)
        content.pack_start(scroller, True, True, 0)

        for name, package, category, description, icon_name in PACKAGES:
            card = AppCard(self, name, package, description, icon_name)
            card.category = category
            card.search_text = f"{name} {description} {package}".lower()
            row = Gtk.ListBoxRow()
            row.card = card
            row.add(card)
            self.apps_list.add(row)
            self.cards.append(card)

        self.details = Gtk.Expander(label="Installation details")
        self.details.set_margin_start(20)
        self.details.set_margin_end(20)
        self.details.set_margin_bottom(10)
        log_view = Gtk.TextView()
        log_view.get_style_context().add_class("install-log")
        log_view.set_editable(False)
        log_view.set_monospace(True)
        log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_buffer = log_view.get_buffer()
        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_min_content_height(150)
        log_scroll.add(log_view)
        self.log_view = log_view
        self.details.add(log_scroll)
        content.pack_start(self.details, False, False, 0)

        self.category_list.select_row(self.category_list.get_row_at_index(0))

    def filter_row(self, row):
        card = row.card
        if self.category != "all" and card.category != self.category:
            return False
        text = self.search.get_text().strip().lower()
        return not text or text in card.search_text

    def on_category_selected(self, _listbox, row):
        if row is None:
            return
        self.category = row.category_key
        self.apps_list.invalidate_filter()

    def load_installed(self):
        names = installed_packages()
        GLib.idle_add(self.apply_installed, names)

    def apply_installed(self, names):
        self.installed = names
        for card in self.cards:
            if card.package in names:
                card.mark_installed()
        return False

    def start_install(self, card):
        if self.installing is not None:
            dialog = Gtk.MessageDialog(
                parent=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.CLOSE,
                text="Another installation is running",
            )
            dialog.format_secondary_text("Wait for it to finish, then try again.")
            dialog.run()
            dialog.destroy()
            return
        self.installing = card
        card.set_busy(True)
        card.status.set_text("Preparing\u2026")
        self.log_buffer.set_text("")
        self.details.set_visible(True)
        self.pulse_id = GLib.timeout_add(120, self.pulse)
        threading.Thread(target=self.run_install, args=(card,), daemon=True).start()

    def pulse(self):
        if self.installing is None:
            return False
        self.installing.progress.pulse()
        return True

    def append_log(self, text):
        end = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end, text)
        mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
        self.log_view.scroll_mark_onscreen(mark)
        self.log_buffer.delete_mark(mark)
        return False

    def set_status(self, card, text):
        card.status.set_text(text)
        return False

    def stream(self, command, card, label):
        GLib.idle_add(self.set_status, card, label)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        output = []
        for line in process.stdout:
            output.append(line)
            GLib.idle_add(self.append_log, line)
            if "Unpacking" in line:
                GLib.idle_add(self.set_status, card, "Installing\u2026")
            elif "Setting up" in line:
                GLib.idle_add(self.set_status, card, "Configuring\u2026")
        process.wait()
        return process.returncode, "".join(output)

    def run_install(self, card):
        env_prefix = ["sudo", "-n", "env", "DEBIAN_FRONTEND=noninteractive"]
        try:
            code, output = self.stream(env_prefix + ["apt-get", "update"], card, "Refreshing package lists\u2026")
            if code != 0:
                GLib.idle_add(self.finish, card, False, self.explain(output, "Could not refresh package lists."))
                return
            code, output = self.stream(
                env_prefix + ["apt-get", "install", "-y", card.package], card, "Downloading\u2026"
            )
            if code == 0:
                GLib.idle_add(self.finish, card, True, "")
            else:
                GLib.idle_add(self.finish, card, False, self.explain(output, "Installation failed."))
        except Exception:
            log_error(traceback.format_exc())
            GLib.idle_add(self.finish, card, False, "Something went wrong. Open the details for more information.")

    def explain(self, output, fallback):
        lowered = output.lower()
        if "could not resolve" in lowered or "temporary failure" in lowered or "failed to fetch" in lowered:
            return "No internet connection. Connect to a network and try again."
        if "password is required" in lowered:
            return "Administrator access was refused."
        if "unable to locate package" in lowered:
            return "This package is not available from the configured sources."
        return fallback

    def finish(self, card, success, message):
        self.installing = None
        if self.pulse_id is not None:
            GLib.source_remove(self.pulse_id)
            self.pulse_id = None
        card.progress.set_visible(False)
        if success:
            self.installed.add(card.package)
            card.status.set_visible(False)
            card.mark_installed()
        else:
            card.button.set_sensitive(True)
            card.button.set_label("Retry")
            card.status.set_text(message)
            card.status.set_visible(True)
        return False


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    LunarStore()
    Gtk.main()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        text = traceback.format_exc()
        log_error(text)
        print(text, file=sys.stderr)
        sys.exit(1)
