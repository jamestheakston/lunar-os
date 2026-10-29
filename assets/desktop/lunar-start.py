#!/usr/bin/env python3
import os
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk, GLib, Pango

HOME = os.path.expanduser("~")
BROWSER_CONFIG = os.path.join(HOME, ".config", "lunar-os/browser")

CSS = b"""
window.lunar-start {
    background-color: #f0f0f0;
    border: 1px solid #888;
    border-radius: 8px;
}
window.lunar-start entry {
    background-color: #ffffff;
    border: 1px solid #888;
    border-radius: 0;
    padding: 8px;
    margin: 8px;
}
window.lunar-start .sidebar {
    background-color: #e8e8e8;
    border-right: 1px solid #ccc;
}
window.lunar-start .sidebar-item {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
}
window.lunar-start .sidebar-item:hover {
    background-color: #d0d0d0;
}
window.lunar-start .sidebar-item.active {
    background-color: #a8d0f0;
}
window.lunar-start .content {
    background-color: #ffffff;
}
window.lunar-start .program-item {
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
}
window.lunar-start .program-item:hover {
    background-color: #e8f4ff;
}
window.lunar-start .program-icon {
    margin-right: 12px;
}
window.lunar-start .folder-item {
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
}
window.lunar-start .folder-item:hover {
    background-color: #e8f4ff;
}
window.lunar-start .folder-icon {
    margin-right: 12px;
}
window.lunar-start .power-button {
    background-color: #d32f2f;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    margin: 8px;
}
window.lunar-start .power-button:hover {
    background-color: #b71c1c;
}
"""

COMMON_PROGRAMS = [
    ("Orbit Explorer", "system-file-manager", "pcmanfm"),
    ("Web Browser", "web-browser", None),  # Will be set based on browser config
    ("Terminal", "utilities-terminal", "lxterminal"),
    ("Lunar Settings", "preferences-system", "/usr/share/lunar-os/lunar-settings.py"),
    ("WireGuard VPN", "network-vpn", "nm-connection-editor"),
    ("Calculator", "accessories-calculator", "galculator"),
    ("Text Editor", "accessories-text-editor", "mousepad"),
]

FOLDERS = [
    ("Documents", "folder-documents", "~/Documents"),
    ("Pictures", "folder-pictures", "~/Pictures"),
    ("Music", "folder-music", "~/Music"),
    ("Videos", "folder-videos", "~/Videos"),
    ("Downloads", "folder-downloads", "~/Downloads"),
    ("Temporary Files", "folder-temp", "/tmp"),
]


class StartMenu(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_default_size(600, 450)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        self.set_type_hint(Gdk.WindowTypeHint.MENU)
        self.get_style_context().add_class("lunar-start")
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_key_press)
        
        self.load_browser_config()
        self.build()
        self.show_all()

    def load_browser_config(self):
        if os.path.exists(BROWSER_CONFIG):
            with open(BROWSER_CONFIG, "r") as f:
                self.browser = f.read().strip()
        else:
            self.browser = "firefox-esr"

    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)

        # Search bar
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.set_margin_top(8)
        search_box.set_margin_start(8)
        search_box.set_margin_end(8)
        
        search_entry = Gtk.Entry()
        search_entry.set_placeholder_text("Search programs and files")
        search_entry.connect("activate", self.on_search)
        search_entry.connect("changed", self.on_search_changed)
        self.search_entry = search_entry
        search_box.pack_start(search_entry, True, True, 0)
        
        main_box.pack_start(search_box, False, False, 0)
        
        # Search results (hidden by default)
        self.search_results = Gtk.ListBox()
        self.search_results.set_visible(False)
        self.search_results.connect("row-activated", self.on_search_result_activated)
        scrolled_search = Gtk.ScrolledWindow()
        scrolled_search.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_search.set_min_content_height(150)
        scrolled_search.add(self.search_results)
        main_box.pack_start(scrolled_search, True, True, 0)

        # Main content with sidebar
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(content_box, True, True, 0)

        # Sidebar - pinned programs
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.get_style_context().add_class("sidebar")
        sidebar.set_size_request(200, -1)
        
        scrolled_sidebar = Gtk.ScrolledWindow()
        scrolled_sidebar.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sidebar_list = Gtk.ListBox()
        sidebar_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_sidebar.add(sidebar_list)
        sidebar.pack_start(scrolled_sidebar, True, True, 0)
        
        for name, icon, command in COMMON_PROGRAMS:
            if command and (name == "Web Browser" and command is None):
                # Set browser command based on config
                browser_commands = {
                    "firefox-esr": "firefox-esr",
                    "tor-browser": "torbrowser-launcher"
                }
                command = browser_commands.get(self.browser, "firefox-esr")
            
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.set_margin_top(2)
            row.set_margin_bottom(2)
            
            icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
            row.pack_start(icon_img, False, False, 0)
            
            label = Gtk.Label(label=name)
            label.set_halign(Gtk.Align.START)
            row.pack_start(label, True, True, 0)
            
            item = Gtk.ListBoxRow()
            item.add(row)
            item.get_style_context().add_class("sidebar-item")
            item.connect("activate", lambda _w, c=command: self.launch(c))
            sidebar_list.add(item)
        
        content_box.pack_start(sidebar, False, False, 0)

        # Right pane - programs and folders
        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_pane.get_style_context().add_class("content")
        right_pane.set_size_request(400, -1)
        
        # Programs section
        programs_label = Gtk.Label()
        programs_label.set_markup('<span weight="bold">Programs</span>')
        programs_label.set_halign(Gtk.Align.START)
        programs_label.set_margin_top(8)
        programs_label.set_margin_start(12)
        right_pane.pack_start(programs_label, False, False, 0)
        
        programs_list = Gtk.ListBox()
        programs_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_programs = Gtk.ScrolledWindow()
        scrolled_programs.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_programs.set_min_content_height(120)
        scrolled_programs.add(programs_list)
        right_pane.pack_start(scrolled_programs, True, True, 0)
        
        for name, icon, command in COMMON_PROGRAMS:
            if command and (name == "Web Browser" and command is None):
                browser_commands = {
                    "firefox-esr": "firefox-esr",
                    "tor-browser": "torbrowser-launcher"
                }
                command = browser_commands.get(self.browser, "firefox-esr")
            
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
            row.pack_start(icon_img, False, False, 0)
            
            label = Gtk.Label(label=name)
            label.set_halign(Gtk.Align.START)
            row.pack_start(label, True, True, 0)
            
            item = Gtk.ListBoxRow()
            item.add(row)
            item.get_style_context().add_class("program-item")
            item.connect("activate", lambda _w, c=command: self.launch(c))
            programs_list.add(item)
        
        # Folders section
        folders_label = Gtk.Label()
        folders_label.set_markup('<span weight="bold">Folders</span>')
        folders_label.set_halign(Gtk.Align.START)
        folders_label.set_margin_top(8)
        folders_label.set_margin_start(12)
        right_pane.pack_start(folders_label, False, False, 0)
        
        folders_list = Gtk.ListBox()
        folders_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_folders = Gtk.ScrolledWindow()
        scrolled_folders.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_folders.set_min_content_height(120)
        scrolled_folders.add(folders_list)
        right_pane.pack_start(scrolled_folders, True, True, 0)
        
        for name, icon, path in FOLDERS:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
            row.pack_start(icon_img, False, False, 0)
            
            label = Gtk.Label(label=name)
            label.set_halign(Gtk.Align.START)
            row.pack_start(label, True, True, 0)
            
            item = Gtk.ListBoxRow()
            item.add(row)
            item.get_style_context().add_class("folder-item")
            item.connect("activate", lambda _w, p=path: self.launch_file_manager(p))
            folders_list.add(item)
        
        # Power button
        power_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        power_box.set_margin_top(8)
        power_box.set_margin_start(12)
        power_box.set_margin_bottom(8)
        
        power_button = Gtk.Button(label="Shut Down")
        power_button.get_style_context().add_class("power-button")
        power_button.set_halign(Gtk.Align.START)
        power_button.connect("clicked", self.on_shutdown)
        power_box.pack_start(power_button, False, False, 0)
        
        right_pane.pack_start(power_box, False, False, 0)
        
        content_box.pack_start(right_pane, True, True, 0)

    def launch(self, command):
        if command.startswith("/"):
            # It's a script
            try:
                subprocess.Popen([command])
            except OSError:
                pass
        else:
            # It's a command with args
            try:
                subprocess.Popen(command.split())
            except OSError:
                pass
        self.destroy()

    def launch_file_manager(self, path):
        expanded = os.path.expanduser(path)
        try:
            subprocess.Popen(["pcmanfm", expanded])
        except OSError:
            pass
        self.destroy()

    def on_search(self, entry):
        query = entry.get_text().strip()
        if query:
            self.launch(query)
        self.destroy()

    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()
        
        self.search_results.remove_all()
        
        if query:
            self.search_results.set_visible(True)
            
            # Search in programs
            for name, icon, command in COMMON_PROGRAMS:
                if query in name.lower():
                    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
                    row.pack_start(icon_img, False, False, 0)
                    label = Gtk.Label(label=name)
                    row.pack_start(label, True, True, 0)
                    item = Gtk.ListBoxRow()
                    item.add(row)
                    item.command = command
                    self.search_results.add(item)
            
            # Search in folders
            for name, icon, path in FOLDERS:
                if query in name.lower():
                    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    icon_img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
                    row.pack_start(icon_img, False, False, 0)
                    label = Gtk.Label(label=name)
                    row.pack_start(label, True, True, 0)
                    item = Gtk.ListBoxRow()
                    item.add(row)
                    item.is_folder = True
                    item.path = path
                    self.search_results.add(item)
        else:
            self.search_results.set_visible(False)

    def on_search_result_activated(self, listbox, row):
        if hasattr(row, 'is_folder'):
            self.launch_file_manager(row.path)
        elif hasattr(row, 'command'):
            self.launch(row.command)
        self.destroy()

    def on_shutdown(self, button):
        try:
            subprocess.Popen(["/usr/local/bin/lunar-shutdown"])
        except OSError:
            pass
        self.destroy()

    def on_focus_out(self, widget, event):
        self.destroy()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    StartMenu()
    Gtk.main()


if __name__ == "__main__":
    main()
