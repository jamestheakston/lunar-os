#!/usr/bin/env python3
import os
import subprocess
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

HOME = os.path.expanduser("~")

CSS = b"""
window {
    background-color: #f5f5f5;
}
.sidebar {
    background-color: #e8e8e8;
    border-right: 1px solid #ccc;
}
.category-item {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
}
.category-item:hover {
    background-color: #d0d0d0;
}
.category-item.active {
    background-color: #a8d0f0;
}
.app-item {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    margin: 8px;
}
.app-item:hover {
    background-color: #f8f8ff;
    border-color: #a8d0f0;
}
.app-name {
    font-size: 14px;
    font-weight: bold;
}
.app-description {
    font-size: 12px;
    color: #666;
}
.install-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}
.install-button:hover {
    background-color: #7d6ff0;
}
.install-button.installed {
    background-color: #27ae60;
}
.progress-bar {
    margin-top: 8px;
}
.terminal-toggle {
    margin-top: 8px;
}
"""

CATEGORIES = {
    "all": "All Applications",
    "internet": "Internet",
    "multimedia": "Multimedia",
    "office": "Office",
    "graphics": "Graphics",
    "games": "Games",
    "system": "System",
    "accessories": "Accessories",
}

PACKAGES = [
    {"name": "Firefox ESR", "package": "firefox-esr", "category": "internet", "description": "Extended Support Release web browser"},
    {"name": "Chromium", "package": "chromium", "category": "internet", "description": "Open-source web browser"},
    {"name": "Thunderbird", "package": "thunderbird", "category": "internet", "description": "Email client"},
    {"name": "Transmission", "package": "transmission-gtk", "category": "internet", "description": "BitTorrent client"},
    {"name": "FileZilla", "package": "filezilla", "category": "internet", "description": "FTP client"},
    {"name": "VLC Media Player", "package": "vlc", "category": "multimedia", "description": "Media player"},
    {"name": "Audacity", "package": "audacity", "category": "multimedia", "description": "Audio editor"},
    {"name": "GIMP", "package": "gimp", "category": "graphics", "description": "Image editor"},
    {"name": "Inkscape", "package": "inkscape", "category": "graphics", "description": "Vector graphics editor"},
    {"name": "Blender", "package": "blender", "category": "multimedia", "description": "3D creation suite"},
    {"name": "LibreOffice", "package": "libreoffice", "category": "office", "description": "Full office suite"},
    {"name": "Evince", "package": "evince", "category": "office", "description": "PDF viewer"},
    {"name": "Steam", "package": "steam-installer", "category": "games", "description": "Steam gaming platform"},
    {"name": "Lutris", "package": "lutris", "category": "games", "description": "Open gaming platform"},
    {"name": "GParted", "package": "gparted", "category": "system", "description": "Partition editor"},
    {"name": "BleachBit", "package": "bleachbit", "category": "system", "description": "System cleaner"},
    {"name": "Htop", "package": "htop", "category": "system", "description": "Process viewer"},
    {"name": "Vim", "package": "vim", "category": "accessories", "description": "Text editor"},
    {"name": "Nano", "package": "nano", "category": "accessories", "description": "Simple text editor"},
    {"name": "Geany", "package": "geany", "category": "accessories", "description": "IDE/Text editor"},
]


class LunarStore(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lunar Store")
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("lunar-store")
        self.connect("destroy", Gtk.main_quit)
        
        self.current_category = "all"
        self.installing = None
        self.terminal_window = None
        self.terminal_process = None
        
        self.build()
        self.show_all()
        
        # Check installed packages in background
        threading.Thread(target=self.check_installed, daemon=True).start()
    
    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        # Sidebar with categories
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.get_style_context().add_class("sidebar")
        sidebar.set_size_request(200, -1)
        
        scrolled_sidebar = Gtk.ScrolledWindow()
        scrolled_sidebar.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.category_list = Gtk.ListBox()
        self.category_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.category_list.connect("row-activated", self.on_category_changed)
        scrolled_sidebar.add(self.category_list)
        sidebar.pack_start(scrolled_sidebar, True, True, 0)
        
        for cat_id, cat_name in CATEGORIES.items():
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=cat_name)
            label.set_halign(Gtk.Align.START)
            row.add(label)
            row.get_style_context().add_class("category-item")
            row.category_id = cat_id
            self.category_list.add(row)
        
        main_box.pack_start(sidebar, False, False, 0)
        
        # Main content area
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(content, True, True, 0)
        
        # Search bar
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.set_margin_top(8)
        search_box.set_margin_start(8)
        search_box.set_margin_end(8)
        
        search_entry = Gtk.Entry()
        search_entry.set_placeholder_text("Search applications...")
        search_entry.connect("changed", self.on_search_changed)
        self.search_entry = search_entry
        search_box.pack_start(search_entry, True, True, 0)
        
        content.pack_start(search_box, False, False, 0)
        
        # Apps list
        scrolled_apps = Gtk.ScrolledWindow()
        scrolled_apps.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.apps_list = Gtk.ListBox()
        self.apps_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_apps.add(self.apps_list)
        content.pack_start(scrolled_apps, True, True, 0)
        
        # Populate apps
        self.populate_apps()
    
    def check_installed(self):
        installed = set()
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\n"],
                capture_output=True,
                text=True,
                check=False
            )
            installed = set(result.stdout.strip().split("\n"))
        except Exception:
            pass
        
        self.installed_packages = installed
        GLib.idle_add(self.update_install_buttons)
    
    def update_install_buttons(self):
        for row in self.apps_list.get_children():
            widget = row.get_child()
            install_button = widget.get_children()[2]
            package_name = install_button.package_name
            
            if package_name in self.installed_packages:
                install_button.set_label("Installed")
                install_button.get_style_context().add_class("installed")
                install_button.set_sensitive(False)
    
    def populate_apps(self):
        # Clear existing
        for row in self.apps_list.get_children():
            self.apps_list.remove(row)
        
        for app in PACKAGES:
            if self.current_category != "all" and app["category"] != self.current_category:
                continue
            
            search_text = self.search_entry.get_text().lower()
            if search_text and search_text not in app["name"].lower() and search_text not in app["description"].lower():
                continue
            
            app_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            app_box.get_style_context().add_class("app-item")
            
            # Name and button row
            top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            name_label = Gtk.Label(label=app["name"])
            name_label.get_style_context().add_class("app-name")
            name_label.set_halign(Gtk.Align.START)
            top_row.pack_start(name_label, True, True, 0)
            
            install_button = Gtk.Button(label="Install")
            install_button.get_style_context().add_class("install-button")
            install_button.package_name = app["package"]
            install_button.connect("clicked", self.on_install_clicked, app)
            top_row.pack_start(install_button, False, False, 0)
            
            app_box.pack_start(top_row, False, False, 0)
            
            # Description
            desc_label = Gtk.Label(label=app["description"])
            desc_label.get_style_context().add_class("app-description")
            desc_label.set_line_wrap(True)
            desc_label.set_max_width_chars(60)
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_xalign(0)
            app_box.pack_start(desc_label, False, False, 0)
            
            # Progress bar (hidden by default)
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_show_text(True)
            progress_bar.set_visible(False)
            progress_bar.get_style_context().add_class("progress-bar")
            app_box.pack_start(progress_bar, False, False, 0)
            
            # Terminal toggle (hidden by default)
            terminal_toggle = Gtk.CheckButton(label="Show terminal")
            terminal_toggle.set_visible(False)
            terminal_toggle.get_style_context().add_class("terminal-toggle")
            terminal_toggle.connect("toggled", self.on_terminal_toggled, app["package"])
            app_box.pack_start(terminal_toggle, False, False, 0)
            
            row = Gtk.ListBoxRow()
            row.add(app_box)
            self.apps_list.add(row)
        
        self.apps_list.show_all()
        self.update_install_buttons()
    
    def on_category_changed(self, listbox, row):
        self.current_category = row.category_id
        self.populate_apps()
    
    def on_search_changed(self, entry):
        self.populate_apps()
    
    def on_install_clicked(self, button, app):
        if self.installing:
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.CLOSE,
                text="Installation in Progress",
            )
            dialog.format_secondary_text("Another application is currently being installed. Please wait.")
            dialog.run()
            dialog.destroy()
            return
        
        self.installing = app["package"]
        button.set_sensitive(False)
        button.set_label("Installing...")
        
        # Find the progress bar and terminal toggle
        app_box = button.get_parent().get_parent()
        progress_bar = app_box.get_children()[2]
        terminal_toggle = app_box.get_children()[3]
        
        progress_bar.set_visible(True)
        progress_bar.set_text("Preparing...")
        progress_bar.set_fraction(0.0)
        terminal_toggle.set_visible(True)
        
        # Start installation in background thread
        threading.Thread(
            target=self.install_package,
            args=(app["package"], progress_bar, terminal_toggle, button),
            daemon=True
        ).start()
    
    def on_terminal_toggled(self, toggle, package_name):
        if toggle.get_active():
            self.show_terminal(package_name)
        else:
            self.hide_terminal()
    
    def show_terminal(self, package_name):
        if self.terminal_window:
            self.terminal_window.present()
            return
        
        self.terminal_window = Gtk.Window(title=f"Installing {package_name}")
        self.terminal_window.set_default_size(600, 400)
        self.terminal_window.set_position(Gtk.WindowPosition.CENTER)
        
        terminal = Gtk.VBox()
        self.terminal_window.add(terminal)
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.get_buffer().set_text("Installation terminal output will appear here...\n")
        self.terminal_text = text_view.get_buffer()
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(text_view)
        terminal.pack_start(scrolled, True, True, 0)
        
        close_button = Gtk.Button(label="Close Terminal")
        close_button.connect("clicked", self.hide_terminal)
        terminal.pack_start(close_button, False, False, 8)
        
        self.terminal_window.connect("destroy", self.on_terminal_closed)
        self.terminal_window.show_all()
    
    def hide_terminal(self, button=None):
        if self.terminal_window:
            self.terminal_window.destroy()
            self.terminal_window = None
    
    def on_terminal_closed(self, window):
        self.terminal_window = None
    
    def install_package(self, package_name, progress_bar, terminal_toggle, button):
        try:
            # Update progress
            GLib.idle_add(lambda: progress_bar.set_text("Downloading..."))
            GLib.idle_add(lambda: progress_bar.set_fraction(0.3))
            
            # Run apt-get install with sudo
            process = subprocess.Popen(
                ["sudo", "apt-get", "install", "-y", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                if self.terminal_window and self.terminal_text:
                    GLib.idle_add(lambda l=line: self.terminal_text.insert(self.terminal_text.get_end_iter(), l))
                    GLib.idle_add(lambda: self.terminal_text.scroll_mark_onscreen(self.terminal_text.get_insert()))
                
                # Update progress based on output
                if "Unpacking" in line:
                    GLib.idle_add(lambda: progress_bar.set_text("Installing..."))
                    GLib.idle_add(lambda: progress_bar.set_fraction(0.6))
                elif "Setting up" in line:
                    GLib.idle_add(lambda: progress_bar.set_text("Configuring..."))
                    GLib.idle_add(lambda: progress_bar.set_fraction(0.8))
            
            process.wait()
            
            if process.returncode == 0:
                GLib.idle_add(lambda: progress_bar.set_text("Complete!"))
                GLib.idle_add(lambda: progress_bar.set_fraction(1.0))
                GLib.idle_add(lambda: button.set_label("Installed"))
                GLib.idle_add(lambda: button.get_style_context().add_class("installed"))
                GLib.idle_add(lambda: self.installed_packages.add(package_name))
            else:
                GLib.idle_add(lambda: progress_bar.set_text("Failed"))
                GLib.idle_add(lambda: progress_bar.set_fraction(0.0))
                GLib.idle_add(lambda: button.set_sensitive(True))
                GLib.idle_add(lambda: button.set_label("Retry"))
        
        except Exception as e:
            GLib.idle_add(lambda: progress_bar.set_text("Error"))
            GLib.idle_add(lambda: progress_bar.set_fraction(0.0))
            GLib.idle_add(lambda: button.set_sensitive(True))
            GLib.idle_add(lambda: button.set_label("Retry"))
        
        finally:
            self.installing = None
            GLib.idle_add(lambda: terminal_toggle.set_visible(False))


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    LunarStore()
    Gtk.main()


if __name__ == "__main__":
    main()
